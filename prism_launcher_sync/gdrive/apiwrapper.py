import colorlog
from typing import Self

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from . import auth


class DriveApiError(Exception):
    pass


class DriveApi:
    __service: str = "drive"
    __version: str = "v3"
    __logger = colorlog.getLogger(__name__)

    def __init__(
            self,
            resource: build.Resource
    ):
        self.__resource = resource

    @classmethod
    def build(cls) -> Self:
        try:
            credentials = auth.get_user_credentials()
            resource = build(cls.__service, cls.__version, credentials=credentials, cache_discovery=False)
            return cls(resource)
        except auth.AppAuthError as e:
            cls.__logger.error(e)
            raise DriveApiError("Could not complete auth process") from e

    def list_files(self, query: str | None = None, orderBy: str | None = None) -> list[dict]:
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
                        orderBy=orderBy
                    )
                    .execute()
                )
                files.extend(response.get("files", []))
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    return files
        except HttpError as e:
            self.__logger.error(e)
            raise DriveApiError("Could not obtain files") from e

    def create_folder(self, name: str) -> dict:
        try:
            new_folder = (
                self.__resource.files()
                .create(
                    body={"name": name, "mimeType": "application/vnd.google-apps.folder"},
                )
                .execute()
            )
            return new_folder
        except HttpError as e:
            self.__logger.error(e)
            raise DriveApiError(f"Could not create folder '{name}'") from e

    def upload_file(self, name: str, mimetype: str, src: str, chunked: bool = False, max_attempts: int = 10) -> dict:
        try:
            request = (
                self.__resource.files()
                .create(
                    body={"name": name, "mimeType": mimetype},
                    media_body=MediaFileUpload(src, mimetype=mimetype, resumable=chunked)
                )
            )
            if not chunked:
                return request.execute()

            # Chunk uploads work progressively and will show status updates in console
            while True:
                status, response = request.next_chunk(num_retries=max_attempts)
                if status:
                    self.__logger.info(f"Uploaded {int(status.progress() * 100)}%")
                if response is not None:
                    return response

        except HttpError as e:
            self.__logger.error(e)
            raise DriveApiError(f"Could not upload file '{name}'") from e

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
            raise DriveApiError(f"Could not update file with id: '{file_id}'") from e
