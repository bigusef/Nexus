"""HTTP-related exceptions."""

from src.core.i18n import lazy_gettext as _lazy

from .base import BaseAppException


class BadRequestException(BaseAppException):
    """Exception raised for malformed or invalid requests."""

    default_message = _lazy("Bad request")

    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=400)


class RateLimitException(BaseAppException):
    """Exception raised when rate limit is exceeded."""

    default_message = _lazy("Too many requests")

    def __init__(self, message: str | None = None, retry_after: int | None = None):
        super().__init__(message=message, status_code=429)
        self.retry_after = retry_after


class ServiceUnavailableException(BaseAppException):
    """Exception raised when an external service is unavailable."""

    default_message = _lazy("Service temporarily unavailable")

    def __init__(self, message: str | None = None, service_name: str | None = None):
        super().__init__(message=message, status_code=503)
        self.service_name = service_name


class GoneException(BaseAppException):
    """Exception raised when a resource has been permanently deleted."""

    default_message = _lazy("Resource no longer available")

    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=410)
