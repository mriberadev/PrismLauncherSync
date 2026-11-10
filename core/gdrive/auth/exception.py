class AppAuthError(Exception):
    pass

class ClientFileNotFoundError(AppAuthError):
    pass

class AuthTimeoutError(AppAuthError):
    pass

class UserCredentialsFileError(AppAuthError):
    pass

class AuthUserAccessDeniedError(AppAuthError):
    pass