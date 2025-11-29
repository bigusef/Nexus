"""Authentication and authorization exceptions."""

from src.core.i18n import lazy_gettext as _lazy

from .base import BaseAppException


class AuthenticationException(BaseAppException):
    """Exception raised when authentication fails."""

    default_message = _lazy("Authentication failed")

    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=401)


class AuthorizationException(BaseAppException):
    """Exception raised when authorization fails."""

    default_message = _lazy("Permission denied")

    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=403)


class InvalidTokenException(AuthenticationException):
    """Exception raised when JWT token is invalid or malformed."""

    default_message = _lazy("Invalid token")

    def __init__(self, message: str | None = None):
        super().__init__(message=message)


class ExpiredTokenException(AuthenticationException):
    """Exception raised when JWT token has expired."""

    default_message = _lazy("Token has expired")

    def __init__(self, message: str | None = None):
        super().__init__(message=message)


class RevokedTokenException(AuthenticationException):
    """Exception raised when JWT token has been revoked."""

    default_message = _lazy("Token has been revoked")

    def __init__(self, message: str | None = None):
        super().__init__(message=message)
