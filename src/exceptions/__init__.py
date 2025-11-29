"""Custom exceptions for the application.

All exception messages support i18n translation using lazy translation.
Messages are translated at the time the exception is converted to string,
using the current request's language context.
"""

from .auth import AuthenticationException
from .auth import AuthorizationException
from .auth import ExpiredTokenException
from .auth import InvalidTokenException
from .auth import RevokedTokenException
from .base import BaseAppException
from .http import BadRequestException
from .http import GoneException
from .http import RateLimitException
from .http import ServiceUnavailableException
from .resource import ConflictException
from .resource import NotFoundException
from .validation import BusinessRuleException
from .validation import ValidationException


__all__ = [
    "BaseAppException",
    # Auth
    "AuthenticationException",
    "AuthorizationException",
    "InvalidTokenException",
    "ExpiredTokenException",
    "RevokedTokenException",
    # Resource
    "NotFoundException",
    "ConflictException",
    # Validation
    "ValidationException",
    "BusinessRuleException",
    # HTTP
    "BadRequestException",
    "RateLimitException",
    "ServiceUnavailableException",
    "GoneException",
]
