"""Request context management using context variables

Provides async-safe global access to request-scoped data (platform, language).
Context variables are automatically isolated per async request, ensuring
concurrent requests don't interfere with each other.
"""

from contextvars import ContextVar

from src.utilities.enums import Language
from src.utilities.enums import Platform


# Context variables for request-scoped data (async-safe)
_language: ContextVar[Language] = ContextVar("language", default=Language.EN)
_platform: ContextVar[Platform] = ContextVar("platform")


# ─── Language Context ─────────────────────────────────────────────────────


def set_language(language: Language) -> None:
    """Set the language for the current async context.

    Args:
        language: The parsed language from Accept-Language header.
    """
    _language.set(language)


def get_language() -> Language:
    """Get the language for the current async context.

    Returns:
        Language enum, defaults to EN if not set.

    Example:
        lang = get_language()
        if lang == Language.AR:
            # Arabic-specific logic
    """
    return _language.get()


# ─── Platform Context ─────────────────────────────────────────────────────


def set_platform(platform: Platform) -> None:
    """Set the platform for the current async context.

    Args:
        platform: The validated platform from X-Source header.
    """
    _platform.set(platform)


def get_platform() -> Platform:
    """Get the platform for the current async context.

    Returns:
        Platform enum.

    Raises:
        LookupError: If platform hasn't been set (middleware didn't run).

    Example:
        platform = get_platform()
        if platform == Platform.ADMIN:
            # Admin dashboard logic
    """
    return _platform.get()
