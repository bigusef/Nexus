"""Core infrastructure module"""

from .config import get_settings
from .context import get_language
from .context import get_platform
from .middleware import RequestHeadersMiddleware


settings = get_settings()

__all__ = [
    "settings",
    # Context functions
    "get_platform",
    "get_language",
]
