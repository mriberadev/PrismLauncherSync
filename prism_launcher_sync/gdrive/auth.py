from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, WSGITimeoutError, Flow
from pathlib import Path

from oauthlib.oauth2 import AccessDeniedError

class AppAuthError(Exception):
    pass

def get_user_credentials() -> Credentials:
    package_dir_path = Path(__file__).parent
    resource_dir_path = (package_dir_path / "resource").resolve()
    client_file_path = (resource_dir_path / "client_secret.json").resolve()
    user_credentials_path = (resource_dir_path / "user_credentials.json").resolve()

    scopes = ["https://www.googleapis.com/auth/drive.file", ]

    user_credentials = None

    if user_credentials_path.exists():
        try:
            user_credentials = Credentials.from_authorized_user_file(user_credentials_path.__str__(), scopes)
        except ValueError as e:
            e.add_note("User credentials file in unknown format")
            raise

    if user_credentials:
        if not user_credentials.valid and user_credentials.expired and user_credentials.refresh_token:
            user_credentials.refresh(Request())
        return user_credentials

    try:
        auth_flow = get_flow_from_client_file(client_file_path, scopes)
        user_credentials = get_user_credentials_from_flow(auth_flow)
        save_user_credentials_to_file(user_credentials_path, user_credentials)

        return user_credentials

    except (
            TimeoutError,
            AccessDeniedError,
            FileNotFoundError,
            OSError,
    ) as e:
        raise AppAuthError("Could not complete auth process") from e


def get_flow_from_client_file(client_file_path: Path, scopes: list[str]) -> Flow:
    if not client_file_path.exists():
        raise FileNotFoundError("Client file was not found")
    return InstalledAppFlow.from_client_secrets_file(
        client_secrets_file=client_file_path.__str__(),
        scopes=scopes,
        redirect_uri="http://localhost",
        pkce="S256"
    )


def get_user_credentials_from_flow(auth_flow: Flow) -> Credentials:
    try:
        credentials = auth_flow.run_local_server()
        return credentials

    except WSGITimeoutError as e:
        raise TimeoutError("Authentication timed out") from e
    except AccessDeniedError as e:
        e.add_note("Access denied by user")
        raise


def save_user_credentials_to_file(user_credentials_path: Path, user_credentials: Credentials) -> None:
    try:
        with user_credentials_path.open("w") as creds_file:
            creds_file.write(user_credentials.to_json())
    except OSError as e:
        e.add_note("Could not open user credentials file")
        raise
