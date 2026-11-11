from datetime import datetime
from pathlib import Path
from typing import Self

from .apiwrapper import DriveApi, DriveApiError
from prism_launcher_sync.base import BaseFile
from prism_launcher_sync import config


class DriveFile(BaseFile):

    def __init__(self, file_id: str | None, parent_id: str | None, **kwargs):
        super().__init__(**kwargs)
        self.file_id = file_id
        self.parent_id = parent_id

    @classmethod
    def map_from_drive(cls, drive_file: dict) -> Self:
        return cls(
            file_id=drive_file["id"],
            parent_id=drive_file["parents"][0] if drive_file["parents"] else None,
            name=drive_file["name"],
            last_modified=datetime.fromisoformat(drive_file["modifiedTime"]).replace(tzinfo=None)
        )

    def upload(self) -> str:
        gd_api = DriveApi.build()
        new_drivefile = gd_api.upload_file(
            name=self.name,
            parent=self.parent_id,
            src=self.path.__str__(),
            chunked=True
        )

    def download(self) -> Path:
        pass


class FileManagerError(Exception):
    pass


class DriveFileManager:

    def __init__(
            self,
            folder: DriveFile,
            files: list[DriveFile]
    ):
        self.folder = folder
        self.files = files

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
        return not self.files or self.files[0].last_modified != last_modified

    def sync(self, zip_file: Path, last_modified: datetime) -> None:
        if not self.files or len(self.files) < config.MAX_BACKUPS or self.files[0].last_modified < last_modified:
            new_file = DriveFile(
                file_id=None,
                parent_id=self.folder.file_id,
                name=zip_file.name,
                last_modified=last_modified,
                path=zip_file
            )
            new_file.upload()
        else:
            pass
