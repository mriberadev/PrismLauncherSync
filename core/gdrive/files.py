import datetime

from . import api
from .api import Api, ApiError


class File:

    def __init__(
            self,
            name: str | None = None,
            parent: str | None = None,
            last_modified: datetime.datetime | None = None
    ):
        self.name = name
        self.parent = parent
        self.last_modified = last_modified


class FileManagerError(Exception):
    pass


class FileManager:
    __app_folder_name = "PrismLauncherSync"

    def __init__(
            self,
            folder: dict | None,
            files: list | None
    ):
        self.folder = folder
        self.files = files

    @classmethod
    def load_files(cls):
        gd_api = Api.build()
        app_folder_name = cls.__app_folder_name

        app_folder = cls.get_app_folder(gd_api, app_folder_name)
        app_files = cls.get_app_files(gd_api, app_folder)

        return cls(
            app_folder,
            app_files
        )


    @staticmethod
    def get_app_folder(gd_api: Api, name: str) -> dict:
        mime_type = "application/vnd.google-apps.folder"
        try:
            files = gd_api.list_files(f"name = '{name}' and mimeType = '{mime_type}'")

            if not files:
                return gd_api.create_file(name, mime_type)

            app_folder = files[0]

            if app_folder["trashed"]:
                return gd_api.update_file(app_folder["id"], {"trashed": False})

            return app_folder

        except ApiError:
            raise FileManagerError("Could not load Google Drive folder data")

    @classmethod
    def get_app_files(cls, gd_api: Api, app_folder: dict) -> list:
        try:
            return gd_api.list_files(query=f"'{app_folder["id"]}' in parents and trashed = false")
        except ApiError:
            raise FileManagerError(f"Could not load Google Drive files in folder {app_folder["name"]}")
