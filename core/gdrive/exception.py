class InitAuthError(Exception):
    pass

class ClientFileNotFoundError(Exception):
    pass

class AuthTimeoutError(Exception):
    pass

class UserCredentialsFileError(Exception):
    pass

class AuthUserAccessDeniedError(Exception):
    pass