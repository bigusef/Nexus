"""Base exception for all application exceptions."""

from src.core.i18n import lazy_gettext as _lazy


class BaseAppException(Exception):
    """Base exception for all application exceptions."""

    default_message = _lazy("An error occurred")

    def __init__(
        self,
        message: str | None = None,
        status_code: int = 500,
    ) -> None:
        self.message = message if message is not None else self.default_message
        self.status_code = status_code
        super().__init__(str(self.message))

    def __str__(self) -> str:
        """Return the translated message."""
        return str(self.message)
