from datetime import datetime
from pathlib import Path
from typing import Self

from .apiwrapper import DriveApi, DriveApiError
from prism_launcher_sync.base import BaseFile
from prism_launcher_sync import config


class DriveFile(BaseFile):

    def __init__(self, file_id: str, **kwargs):
        super().__init__(**kwargs)
        self.file_id = file_id

    @classmethod
    def map_from_drive(cls, drive_file: dict) -> Self:
        return cls(
            file_id=drive_file["id"],
            name=drive_file["name"],
            last_modified=datetime.fromisoformat(drive_file["modifiedTime"])
        )

    def upload(self) -> str:
        pass

    def download(self) -> Path:
        pass


class FileManagerError(Exception):
    pass


class DriveFileManager:

    def __init__(
            self,
            folder: DriveFile,
            files: list[DriveFile],
            last_backup: DriveFile | None
    ):
        self.folder = folder
        self.files = files
        self.last_backup = last_backup

    @classmethod
    def load_files(cls) -> Self:
        gd_api = DriveApi.build()

        app_folder = cls.get_app_folder(gd_api, config.DRIVE_FOLDER)
        app_files = cls.get_app_files(gd_api, app_folder)

        return cls(
            DriveFile.map_from_drive(app_folder),
            [DriveFile.map_from_drive(f) for f in app_files],
            DriveFile.map_from_drive(app_files[0]) if app_files else None
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
            raise FileManagerError("Could not load Google Drive folder data") from e

    @staticmethod
    def get_app_files(gd_api: DriveApi, app_folder: dict) -> list[dict]:
        try:
            return gd_api.list_files(
                query=f"'{app_folder["id"]}' in parents and trashed=false",
                orderBy="modifiedTime desc"
            )
        except DriveApiError as e:
            raise FileManagerError(f"Could not load Google Drive files in folder {app_folder["name"]}") from e

    def needs_sync(self, last_modified: datetime) -> bool:
        return self.last_backup is None or self.last_backup.last_modified != last_modified

    def sync(self, zip_file: Path, last_modified: datetime) -> None:
        if not self.last_backup or self.last_backup.last_modified < last_modified:
            pass
        else:
            pass
