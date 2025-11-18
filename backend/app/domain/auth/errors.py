
class AuthError(Exception):
    """Base class for auth domain/application errors."""


class EmailAlreadyUsedError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass


class UserNotFoundError(AuthError):
    pass


class InvalidRefreshTokenError(AuthError):
    pass
