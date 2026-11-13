import os
import io
from logging import Logger
from pathlib import Path
from typing import Self

import colorlog

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from prism_launcher_sync import config
from . import auth


def make_progress_bar(progress: int | float, max_len: int = 50) -> str:
    percent = int(progress * 100)
    done = int(progress * max_len)
    remaining = int(max_len - done)
    return f"[{"#" * done}{"-" * remaining}] {percent}%"


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
            raise DriveApiError("Failed to complete auth process") from e

    def list(self, query: str | None = None, order_by: str | None = None) -> list[dict]:
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
                        orderBy=order_by
                    )
                    .execute()
                )
                files.extend(response.get("files", []))
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    return files
        except HttpError as e:
            raise DriveApiError("Failed to obtain files") from e

    def get(self, file_id: str) -> dict:
        try:
            return self.__resource.files().get(fileId=file_id).execute()
        except HttpError as e:
            raise DriveApiError(f"Failed to obtain file with id: '{file_id}") from e

    def create(
            self,
            name: str,
            parent_id: str,
            is_folder: bool,
            src: str | os.PathLike[str] | None = None,
            max_attempts: int = config.UPLOAD_MAX_ATTEMPTS
    ) -> dict:
        body = {
            "name": name,
            "parents": [parent_id],
        }
        try:
            if is_folder:
                body["mimeType"] = "application/vnd.google-apps.folder"
                media_body = None
            else:
                if not src:
                    raise ValueError("File upload requires 'src' argument")
                src_path = Path(src)
                if not src_path.exists():
                    raise FileNotFoundError
                media_body = MediaFileUpload(src, resumable=True, chunksize=config.UPLOAD_CHUNK_SIZE)

            request = (
                self.__resource.files()
                .create(
                    body=body,
                    media_body=media_body,
                    fields="id, modifiedTime, webViewLink, webContentLink"
                )
            )
            if is_folder:
                return request.execute()

            self.__logger.info(f"Starting upload...")
            while True:
                status, response = request.next_chunk(num_retries=max_attempts)
                if status:
                    self.__logger.info(f"Upload progress {make_progress_bar(status.progress())}")
                if response is not None:
                    self.__logger.info(f"Upload progress {make_progress_bar(1)}")
                    return response

        except (ValueError, FileNotFoundError, HttpError) as e:
            raise DriveApiError(f"Failed to create {name}") from e

    def download(
            self,
            file_id: str,
            max_attempts: int = config.DOWNLOAD_MAX_ATTEMPTS
    ) -> bytes:
        try:
            request = self.__resource.files().get_media(fileId=file_id)
            downloaded_file = io.BytesIO()
            downloader = MediaIoBaseDownload(downloaded_file, request, chunksize=config.DOWNLOAD_CHUNK_SIZE)
            done = False

            self.__logger.info("Starting download...")
            while done is False:
                status, done = downloader.next_chunk(num_retries=max_attempts)
                if status:
                    self.__logger.info(f"Download progress {make_progress_bar(status.progress())}")

            return downloaded_file.getvalue()

        except HttpError as e:
            raise DriveApiError(f"Failed to download file with id '{file_id}'") from e

    def update(self, file_id: str, updated_fields: dict) -> dict:
        try:
            updated_file = (
                self.__resource.files()
                .update(
                    fileId=file_id,
                    body=updated_fields,
                )
                .execute()
            )
            return updated_file
        except HttpError as e:
            raise DriveApiError(f"Failed to update file with id: '{file_id}'") from e

    def delete(self, file_id: str) -> None:
        try:
            self.__resource.files().delete(fileId=file_id).execute()
        except HttpError as e:
            raise DriveApiError(f"Failed to delete file with id: '{file_id}'") from e
