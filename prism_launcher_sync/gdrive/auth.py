from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, WSGITimeoutError, Flow
from oauthlib.oauth2 import AccessDeniedError

from prism_launcher_sync import config


class AuthError(Exception):
    pass


def get_credentials() -> Credentials:

    scopes = ["https://www.googleapis.com/auth/drive.file", ]

    creds = None

    if config.USER_CREDS_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(config.USER_CREDS_FILE, scopes)
        except ValueError as e:
            e.add_note("User credentials file in unknown format")
            raise

    if creds:
        if not creds.valid and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds

    try:
        creds = request_access(scopes)
        save_to_file(creds)

        return creds

    except (
            TimeoutError,
            AccessDeniedError,
            FileNotFoundError,
            OSError,
    ) as e:
        raise AuthError("Failed to complete auth process") from e


def request_access(scopes: list[str]) -> Credentials:
    if not config.CLIENT_FILE.exists():
        raise FileNotFoundError("Client file was not found")

    try:
        return InstalledAppFlow.from_client_secrets_file(
            client_secrets_file=config.CLIENT_FILE.__str__(),
            scopes=scopes,
            redirect_uri="http://localhost",
            pkce="S256"
        ).run_local_server()

    except WSGITimeoutError as e:
        raise TimeoutError("Authentication timed out") from e
    except AccessDeniedError as e:
        e.add_note("Access denied by user")
        raise


def save_to_file(creds: Credentials) -> None:
    try:
        with config.USER_CREDS_FILE.open("w") as creds_file:
            creds_file.write(creds.to_json())
    except OSError as e:
        e.add_note("Failed to open user credentials file")
        raise
