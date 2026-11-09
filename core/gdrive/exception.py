class GoogleAuthError(Exception):
    pass

class ClientFileNotFoundError(GoogleAuthError):
    pass

class AuthTimeoutError(GoogleAuthError):
    pass

class UserCredentialsFileError(GoogleAuthError):
    pass

class AuthUserAccessDeniedError(GoogleAuthError):
    pass