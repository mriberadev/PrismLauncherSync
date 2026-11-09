class InitAuthError(Exception):
    pass

class ClientFileNotFoundError(InitAuthError):
    pass

class AuthTimeoutError(InitAuthError):
    pass

class UserCredentialsFileError(InitAuthError):
    pass

class AuthUserAccessDeniedError(InitAuthError):
    pass