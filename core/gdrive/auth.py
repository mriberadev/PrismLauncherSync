from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, WSGITimeoutError, Flow
from pathlib import Path

from oauthlib.oauth2 import AccessDeniedError

from .exception import (InitAuthError, ClientFileNotFoundError, AuthTimeoutError, UserCredentialsFileError,
                        AuthUserAccessDeniedError)


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
        except ValueError:
            raise UserCredentialsFileError("User credentials file in unknown format")

    try:
        if (user_credentials and not user_credentials.valid
                and user_credentials.expired and user_credentials.refresh_token):
            user_credentials.refresh(Request())

        else:
            auth_flow = get_flow_from_client_file(client_file_path, scopes)
            user_credentials = get_user_credentials_from_flow(auth_flow)
            save_user_credentials_to_file(user_credentials_path, user_credentials)

        return user_credentials

    except (
            AuthTimeoutError,
            AuthUserAccessDeniedError,
            ClientFileNotFoundError,
            UserCredentialsFileError,
    ) as e:
        raise InitAuthError(e.__str__())


def get_flow_from_client_file(client_file_path: Path, scopes: list[str]) -> Flow:
    if not client_file_path.exists():
        raise ClientFileNotFoundError("Client file was not found")
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

    except WSGITimeoutError:
        raise AuthTimeoutError("Authentication timed out")
    except AccessDeniedError:
        raise AuthUserAccessDeniedError("Access denied by user")


def save_user_credentials_to_file(user_credentials_path: Path, user_credentials: Credentials) -> str:
    try:
        with open(user_credentials_path.__str__(), "w") as creds_file:
            creds_file.write(user_credentials.to_json())
    except OSError:
        raise UserCredentialsFileError("Could not open user credentials file")
