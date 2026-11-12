import os
from datetime import datetime
from typing import Self

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
            raise DriveFileError(f"Could not upload {self.name}") from e

    def download(self) -> Self:
        pass

    def delete(self) -> None:
        pass


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

    @property
    def newest_file(self) -> DriveFile | None:
        if self.file_count == 0:
            return None
        return self.files[0]

    @property
    def oldest_file(self) -> DriveFile | None:
        if self.file_count == 0:
            return None
        return self.files[-1]

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
            raise DriveFileManagerError("Could not load Google Drive folder data") from e

    @staticmethod
    def get_app_files(gd_api: DriveApi, app_folder: dict) -> list[dict]:
        try:
            return gd_api.list_files(
                query=f"'{app_folder["id"]}' in parents and trashed=false",
                orderBy="modifiedTime desc"
            )
        except DriveApiError as e:
            raise DriveFileManagerError(f"Could not load Google Drive files in folder {app_folder["name"]}") from e

    def sync(self, zip_file: str | os.PathLike[str]) -> None:
        if 0 < self.file_count < config.MAX_BACKUPS:
            new_file = DriveFile.from_src(zip_file)
            new_file.parent_id = self.folder.file_id
            new_file.upload()
        else:
            pass
