import os
from datetime import datetime
from typing import Self

from prismlauncher import Instance
from .apiwrapper import DriveApi, DriveApiError
from prism_launcher_sync.base import BaseFile
from prism_launcher_sync import config


class DriveFileError(Exception):
    pass


class DriveFile(BaseFile):

    def __init__(
            self,
            file_id: str | None = None,
            parent_id: str | None = None,
            view_link: str | None = None,
            content_link: str | None = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.file_id = file_id
        self.parent_id = parent_id
        self.view_link = view_link
        self.content_link = content_link

    @classmethod
    def map_from_drive(cls, drive_file: dict) -> Self:
        return cls(
            file_id=drive_file["id"],
            parent_id=drive_file["parents"][0] if drive_file["parents"] else None,
            name=drive_file["name"],
            view_link=drive_file["webViewLink"][0] if "webViewLink" in drive_file else None,
            content_link=drive_file["webContentLink"][0] if "webContentLink" in drive_file else None,
            dt_modified=datetime.fromisoformat(drive_file["modifiedTime"]).replace(tzinfo=None)
        )

    def upload(self) -> Self:
        try:
            gd_api = DriveApi.build()
            new_drivefile = gd_api.upload_file(
                name=self.name,
                parent_id=self.parent_id,
                src=self.path.__str__(),
                chunked=True
            )
            self.file_id = new_drivefile["id"]
            return self

        except DriveApiError as e:
            raise DriveFileError(f"Failed to upload {self.name}") from e

    def download(self) -> Self:
        pass

    def delete(self) -> None:
        if not self.file_id:
            raise AttributeError("DriveFile has no id")

        try:
            gd_api = DriveApi.build()
            gd_api.delete_file(file_id=self.file_id)

        except DriveApiError as e:
            raise DriveFileError(f"Failed to delete {self.name}") from e


class DriveFileManagerError(Exception):
    pass


class DriveFileManager:

    def __init__(
            self,
            folder: DriveFile,
            files: list[DriveFile]
    ):
        self.folder = folder
        self.files = files

    @property
    def file_count(self) -> int:
        return len(self.files)

    @classmethod
    def load_files(cls) -> Self:
        gd_api = DriveApi.build()

        app_folder = cls.get_app_folder(gd_api, config.DRIVE_FOLDER)
        app_files = cls.get_app_files(gd_api, app_folder)

        return cls(
            DriveFile.map_from_drive(app_folder),
            [DriveFile.map_from_drive(f) for f in app_files]
        )

    @staticmethod
    def get_app_folder(gd_api: DriveApi, name: str) -> dict:
        try:
            folders = gd_api.list_files(f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder'")

            if not folders:
                return gd_api.create_folder(name)

            app_folder = folders[0]

            if app_folder["trashed"]:
                return gd_api.update_file(app_folder["id"], {"trashed": False})

            return app_folder

        except DriveApiError as e:
            raise DriveFileManagerError("Failed to load Google Drive folder data") from e

    @staticmethod
    def get_app_files(gd_api: DriveApi, app_folder: dict) -> list[dict]:
        try:
            return gd_api.list_files(
                query=f"'{app_folder["id"]}' in parents and trashed=false",
                orderBy="modifiedTime desc"
            )
        except DriveApiError as e:
            raise DriveFileManagerError(f"Failed to load Google Drive files in folder {app_folder["name"]}") from e

    def remove_oldest(self) -> None:
        if self.file_count > 0:
            try:
                self.files[-1].delete()
                self.files.pop()  # Update .files list preserving order
            except AttributeError:
                raise

    def sync_instance(self, instance: Instance) -> None:
        if self.file_count == 0 or self.files[0].dt_modified < instance.dt_modified:
            src = instance.to_zip().path
            gd_file = DriveFile.from_src(src)
            gd_file.parent_id = self.folder.file_id
            self.files.insert(0, gd_file.upload())  # Update .files list preserving order
        else:
            pass

        if self.file_count > config.MAX_BACKUPS:
            try:
                self.remove_oldest()
            except AttributeError as e:
                raise DriveFileManagerError("Failed to remove oldest backup") from e
