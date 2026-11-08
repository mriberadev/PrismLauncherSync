from pydrive2.auth import GoogleAuth, AuthenticationError, AuthenticationRejected
from pydrive2.drive import GoogleDrive

from gdrive_management.exception import InitAuthError


def gdrive_auth() -> GoogleDrive | None:
    try:
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()

        return GoogleDrive(gauth)
    except (AuthenticationError, AuthenticationRejected):
        raise InitAuthError(f"Authentication could not be completed")
