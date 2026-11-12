import colorlog
from logging import Logger
from typing import Self

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from prism_launcher_sync import config
from . import auth


class DriveApiError(Exception):
    pass


class DriveApi:
    __service: str = config.G_API_SERVICE
    __version: str = config.G_API_VERSION
    __logger: Logger = colorlog.getLogger(__name__)

    def __init__(
            self,
            resource: build.Resource
    ):
        self.__resource = resource

    @classmethod
    def build(cls) -> Self:
        try:
            credentials = auth.get_credentials()
            resource = build(cls.__service, cls.__version, credentials=credentials, cache_discovery=False)
            return cls(resource)
        except auth.AuthError as e:
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

    def upload_file(
            self,
            name: str,
            src: str,
            parent_id: str | None = None,
            chunked: bool = False,
            max_attempts: int = 10
    ) -> dict:
        try:
            request = (
                self.__resource.files()
                .create(
                    body={"name": name, "parents": [parent_id] if parent_id else []},
                    media_body=MediaFileUpload(src, resumable=chunked, chunksize=config.UPLOAD_CHUNK_SIZE)
                )
            )
            self.__logger.info(f"Starting upload for {name}...")
            if not chunked:
                new_file = request.execute()

            else:
                # Chunk uploads work progressively and will show status updates in console
                while True:
                    status, response = request.next_chunk(num_retries=max_attempts)
                    pbar_max = 50
                    if status:
                        progress = int(status.progress() * 100)
                        pbar_len = int(status.progress() * pbar_max)
                        progress_bar = ("#" * pbar_len) + ("-" * (pbar_max - pbar_len))
                        self.__logger.info(f"Upload progress {progress}% [{progress_bar}]")
                    if response is not None:
                        self.__logger.info(f"Upload progress 100% [{"#" * pbar_max}]")
                        new_file = response
                        break

            self.__logger.info(f"Upload complete for {name}")
            return new_file

        except HttpError as e:
            self.__logger.error(e)
            raise DriveApiError(f"Could not upload {name}") from e

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
