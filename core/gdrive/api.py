import logging
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from . import auth


class ApiError(Exception):
    pass


class Api:
    __service: str = "drive"
    __version: str = "v3"
    __logger = logging.getLogger(__name__)

    def __init__(
            self,
            resource: build.Resource
    ):
        self.__resource = resource

    @classmethod
    def build(cls):
        try:
            credentials = auth.get_user_credentials()
            resource = build(cls.__service, cls.__version, credentials=credentials)
            return cls(resource)
        except auth.AppAuthError as e:
            cls.__logger.error(e)

    def list_files(self, query: str | None = None) -> list[Any]:
        try:
            files = []
            page_token = None
            while True:
                response = (
                    self.__resource.files()
                    .list(
                        q=query,
                        spaces="drive",
                        fields="nextPageToken, files",
                        pageToken=page_token,
                    )
                    .execute()
                )
                files.extend(response.get("files", []))
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    return files
        except HttpError as e:
            self.__logger.error(e)
            raise ApiError("Could not obtain files")

    def create_file(self, name: str, mime_type: str) -> dict:
        try:
            new_file = (
                self.__resource.files()
                .create(
                    body={"name": name, "mimeType": mime_type},
                )
                .execute()
            )
            return new_file
        except HttpError as e:
            self.__logger.error(e)
            raise ApiError(f"Could not create file '{name}'")

    def update_file(self, file_id: str, update_fields: dict) -> dict:
        try:
            updated_file = (
                self.__resource.files()
                .update(
                    fileId=file_id,
                    body=update_fields,
                )
                .execute()
            )
            return updated_file
        except HttpError as e:
            self.__logger.error(e)
            raise ApiError(f"Could not update file with id: '{file_id}'")
