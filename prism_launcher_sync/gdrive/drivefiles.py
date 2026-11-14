import os
from pathlib import Path
from typing import Self
from datetime import datetime

from prism_launcher_sync import config
from prism_launcher_sync.base import BaseFile
from prism_launcher_sync.prismlauncher import Instance
from prism_launcher_sync.gdrive.apiwrapper import DriveApi, DriveApiError


class DriveFileError(Exception):
    pass


class DriveFile(BaseFile):

    def __init__(
            self,
            name: str,
            dt_modified: datetime | None = None,
            path: str | os.PathLike[str] | None = None,
            file_id: str | None = None,
            parent_id: str = "root",
            is_folder: bool = False,
            view_link: str | None = None,
            content_link: str | None = None,
            children: list[Self] | None = None
    ):
        super().__init__(
            name=name,
            dt_modified=dt_modified,
            path=path
        )
        self.name = name
        self.path = path
        self.dt_modified = dt_modified
        self.file_id = file_id
        self.parent_id = parent_id
        self.is_folder = is_folder
        self.view_link = view_link
        self.content_link = content_link
        self.children = children if children else []

    @property
    def child_count(self) -> int:
        return len(self.children)

    @staticmethod
    def to_datetime(gd_date: str) -> datetime:
        return datetime.fromisoformat(gd_date).astimezone()

    def map_from_drive(self, drive_file: dict) -> None:
        self.file_id = drive_file["id"]
        self.view_link = drive_file["webViewLink"][0] if "webViewLink" in drive_file else None
        self.content_link = drive_file["webContentLink"][0] if "webContentLink" in drive_file else None
        self.dt_modified = DriveFile.to_datetime(drive_file["modifiedTime"])

    def map_to_drive(self) -> dict:
        return {
            "parents": [self.parent_id],
            "name": self.name,
        }

    def get(self, gd_api: DriveApi):
        try:
            if not self.file_id:
                raise AttributeError
            gd_list = gd_api.get(file_id=self.file_id)
            for child in gd_list:
                gd_child = self.__class__(
                    name=child["name"],
                    parent_id=self.parent_id
                )
                gd_child.map_from_drive(child)
                self.children.append(gd_child)
        except (DriveApiError, AttributeError) as e:
            raise DriveFileError(f"Failed to get file") from e

    def get_child(self, file_id: str | None = None, name: str | None = None) -> DriveFile | None:
        return next((child for child in self.children if child.file_id == file_id or child.name == name), None)

    def get_children(self, gd_api: DriveApi):
        try:
            if not self.file_id:
                raise AttributeError
            gd_list = gd_api.list(
                query=f"'{self.file_id}' in parents and trashed=false",
                order_by="modifiedTime"
            )
            for child in gd_list:
                gd_child = self.__class__(
                    name=child["name"],
                    parent_id=self.file_id
                )
                gd_child.map_from_drive(child)
                self.children.append(gd_child)
        except (DriveApiError, AttributeError) as e:
            raise DriveFileError(f"Failed to get children") from e

    def create(
            self,
            gd_api: DriveApi,
            is_folder: bool,
            src: str | os.PathLike[str] | None = None,
    ) -> None:
        try:
            gd_file = gd_api.create(
                name=self.name,
                parent_id=self.parent_id,
                is_folder=is_folder,
                src=src
            )
            self.map_from_drive(gd_file)

        except DriveApiError as e:
            raise DriveFileError(f"Failed to create file") from e

    def update(self, gd_api: DriveApi) -> None:
        try:
            if not self.file_id:
                raise AttributeError

            gd_file = gd_api.update(
                file_id=self.file_id,
                updated_fields=self.map_to_drive()
            )
            self.map_from_drive(gd_file)

        except (AttributeError, DriveApiError) as e:
            raise DriveFileError(f"Failed to create file") from e

    def download(
            self,
            gd_api: DriveApi,
            dst: str | os.PathLike[str]
    ) -> str:
        try:
            if not self.file_id:
                raise AttributeError

            dst = Path(dst)
            if not dst.exists():
                raise FileNotFoundError

            dst = dst.joinpath(self.name).resolve()
            content = gd_api.download(file_id=self.file_id)
            with open(dst, "wb") as f:
                f.write(content)

            return str(dst)

        except (AttributeError, FileNotFoundError, DriveApiError) as e:
            raise DriveFileError(f"Failed to download file") from e

    def delete(self, gd_api: DriveApi) -> None:
        try:
            if not self.file_id:
                raise AttributeError
            gd_api.delete(file_id=self.file_id)

        except (AttributeError, DriveApiError) as e:
            raise DriveFileError(f"Failed to delete file") from e


class DriveFileManagerError(Exception):
    pass


class DriveFileManager:

    def __init__(
            self,
            _root: DriveFile,
            _api: DriveApi
    ):
        self._root = _root
        self._api = _api

    def set_root(self) -> None:
        try:
            gd_list = self._api.list(
                query=f"'root' in parents and name='{config.DRIVE_FOLDER}' and trashed=false"
            )
            if not gd_list:
                self._root = DriveFile(
                    name=config.DRIVE_FOLDER,
                    parent_id="root",
                    dt_modified=datetime.now()
                )
                self._root.create(gd_api=self._api, is_folder=True)
                return None

            if len(gd_list) > 1:
                raise DriveFileManagerError(f"Multiple folders named '{config.DRIVE_FOLDER}' found")

            self._root.map_from_drive(gd_list[0])

        except (DriveApiError, DriveFileError, DriveFileManagerError) as e:
            raise DriveFileManagerError("Failed to retrieve root folder") from e

    def map_from_drive(self) -> None:
        try:
            # Get app root folder in drive
            self.set_root()

            # Get root children
            self._root.get_children(gd_api=self._api)

            # Get children for each folder instance
            for gd_folder in self._root.children:
                gd_folder.get_children(gd_api=self._api)

        except DriveApiError as e:
            raise DriveFileManagerError("Failed to load Google Drive files") from e

    def sync_instance(self, instance: Instance) -> None:
        try:
            if not self._root or not self._root.file_id:
                raise AttributeError("Root dir not set")

            gd_folder = self._root.get_child(name=instance.name)
            if not gd_folder:
                gd_folder = DriveFile(
                    name=instance.name,
                    parent_id=self._root.file_id
                )
                gd_folder.create(gd_api=self._api, is_folder=True)

            if not instance.dt_modified:
                raise AttributeError("No instance date to compare")

            # Indexes for readability
            _latest = -1
            _oldest = 0

            # Upload if backup folder is empty or current instance is newer than last backup, else download
            if gd_folder.child_count == 0 or gd_folder.children[_latest].dt_modified < instance.dt_modified:
                _zip = Path(instance.export_zip())
                gd_file = DriveFile(
                    name=_zip.name,
                    parent_id=gd_folder.file_id
                )
                gd_file.create(gd_api=self._api, is_folder=False, src=_zip)
                gd_folder.children.append(gd_file)
            else:
                _zip = gd_folder.children[_latest].download(gd_api=self._api, dst=config.ZIPFILES_DIR)
                instance.import_zip(_zip)

            if gd_folder.child_count > config.MAX_BACKUPS:
                gd_folder.children[_oldest].delete(gd_api=self._api)

        except (AttributeError, DriveFileError) as e:
            raise DriveFileManagerError(f"Failed to sync instance {instance.name}") from e

    def last_backup_for_instance(self, instance: Instance) -> DriveFile:
        try:
            if not self._root or not self._root.file_id:
                raise AttributeError("Root dir not set")

            gd_folder = self._root.get_child(name=instance.name)
            if gd_folder.child_count > 0:
                return gd_folder.children[-1]
            return None

        except (AttributeError, DriveFileError) as e:
            raise DriveFileManagerError(f"Failed to sync instance {instance.name}") from e