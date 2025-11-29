"""Resource-related exceptions."""

from src.core.i18n import gettext as _
from src.core.i18n import lazy_gettext as _lazy

from .base import BaseAppException


class NotFoundException(BaseAppException):
    """Exception raised when an entity is not found."""

    default_message = _lazy("Resource not found")

    def __init__(self, entity_name: str, entity_id: int | str):
        message = _("{entity_name} with id={entity_id} not found").format(
            entity_name=entity_name,
            entity_id=entity_id,
        )
        super().__init__(message=message, status_code=404)
        self.entity_name = entity_name
        self.entity_id = entity_id


class ConflictException(BaseAppException):
    """Exception raised when there's a conflict (e.g., duplicate entry)."""

    default_message = _lazy("Conflict occurred")

    def __init__(self, message: str | None = None):
        super().__init__(message=message, status_code=409)
