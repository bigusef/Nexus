"""Validation and business rule exceptions."""

from src.core.i18n import lazy_gettext as _lazy

from .base import BaseAppException


class ValidationException(BaseAppException):
    """Exception raised when validation fails."""

    default_message = _lazy("Validation error")

    def __init__(self, message: str | None = None, field: str | None = None):
        super().__init__(message=message, status_code=422)
        self.field = field


class BusinessRuleException(BaseAppException):
    """Exception raised when a business rule is violated."""

    default_message = _lazy("Business rule violation")

    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=400)
