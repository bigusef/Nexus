"""Tests for custom exceptions."""

import pytest

from src.exceptions import AuthenticationException
from src.exceptions import AuthorizationException
from src.exceptions import BadRequestException
from src.exceptions import BaseAppException
from src.exceptions import BusinessRuleException
from src.exceptions import ConflictException
from src.exceptions import ExpiredTokenException
from src.exceptions import GoneException
from src.exceptions import InvalidTokenException
from src.exceptions import NotFoundException
from src.exceptions import RateLimitException
from src.exceptions import RevokedTokenException
from src.exceptions import ServiceUnavailableException
from src.exceptions import ValidationException


class TestBaseAppException:
    """Tests for BaseAppException."""

    def test_default_message(self):
        """Test exception with default message."""
        exc = BaseAppException()
        assert exc.status_code == 500
        assert "error occurred" in str(exc).lower()

    def test_custom_message(self):
        """Test exception with custom message."""
        exc = BaseAppException(message="Custom error", status_code=400)
        assert exc.status_code == 400
        assert str(exc) == "Custom error"


class TestAuthenticationException:
    """Tests for AuthenticationException."""

    def test_default_message(self):
        """Test exception with default message."""
        exc = AuthenticationException()
        assert exc.status_code == 401
        assert "authentication" in str(exc).lower()

    def test_custom_message(self):
        """Test exception with custom message."""
        exc = AuthenticationException(message="Invalid credentials")
        assert exc.status_code == 401
        assert str(exc) == "Invalid credentials"


class TestAuthorizationException:
    """Tests for AuthorizationException."""

    def test_default_message(self):
        """Test exception with default message."""
        exc = AuthorizationException()
        assert exc.status_code == 403
        assert "permission" in str(exc).lower() or "denied" in str(exc).lower()

    def test_custom_message(self):
        """Test exception with custom message."""
        exc = AuthorizationException(message="Access forbidden")
        assert exc.status_code == 403
        assert str(exc) == "Access forbidden"


class TestInvalidTokenException:
    """Tests for InvalidTokenException."""

    def test_default_message(self):
        """Test exception with default message."""
        exc = InvalidTokenException()
        assert exc.status_code == 401
        assert "invalid" in str(exc).lower() and "token" in str(exc).lower()

    def test_custom_message(self):
        """Test exception with custom message."""
        exc = InvalidTokenException(message="Malformed token")
        assert exc.status_code == 401
        assert str(exc) == "Malformed token"


class TestExpiredTokenException:
    """Tests for ExpiredTokenException."""

    def test_default_message(self):
        """Test exception with default message."""
        exc = ExpiredTokenException()
        assert exc.status_code == 401
        assert "expired" in str(exc).lower()

    def test_custom_message(self):
        """Test exception with custom message."""
        exc = ExpiredTokenException(message="Token validity ended")
        assert exc.status_code == 401
        assert str(exc) == "Token validity ended"


class TestRevokedTokenException:
    """Tests for RevokedTokenException."""

    def test_default_message(self):
        """Test exception with default message."""
        exc = RevokedTokenException()
        assert exc.status_code == 401
        assert "revoked" in str(exc).lower()

    def test_custom_message(self):
        """Test exception with custom message."""
        exc = RevokedTokenException(message="Token was invalidated")
        assert exc.status_code == 401
        assert str(exc) == "Token was invalidated"


class TestNotFoundException:
    """Tests for NotFoundException."""

    def test_with_entity_info(self):
        """Test exception with entity information."""
        exc = NotFoundException(entity_name="User", entity_id=123)
        assert exc.status_code == 404
        assert exc.entity_name == "User"
        assert exc.entity_id == 123
        assert "User" in str(exc)
        assert "123" in str(exc)

    def test_with_string_id(self):
        """Test exception with string entity ID."""
        exc = NotFoundException(entity_name="Order", entity_id="abc-123")
        assert exc.status_code == 404
        assert exc.entity_id == "abc-123"


class TestConflictException:
    """Tests for ConflictException."""

    def test_default_message(self):
        """Test exception with default message."""
        exc = ConflictException()
        assert exc.status_code == 409
        assert "conflict" in str(exc).lower()

    def test_custom_message(self):
        """Test exception with custom message."""
        exc = ConflictException(message="Email already exists")
        assert exc.status_code == 409
        assert str(exc) == "Email already exists"


class TestValidationException:
    """Tests for ValidationException."""

    def test_creates_exception(self):
        """Test exception creation."""
        exc = ValidationException(message="Invalid input")
        assert exc.status_code == 422
        assert str(exc) == "Invalid input"


class TestBusinessRuleException:
    """Tests for BusinessRuleException."""

    def test_creates_exception(self):
        """Test exception creation."""
        exc = BusinessRuleException(message="Cannot process order")
        assert exc.status_code == 400
        assert str(exc) == "Cannot process order"


class TestBadRequestException:
    """Tests for BadRequestException."""

    def test_creates_exception(self):
        """Test exception creation."""
        exc = BadRequestException(message="Malformed request")
        assert exc.status_code == 400
        assert str(exc) == "Malformed request"


class TestRateLimitException:
    """Tests for RateLimitException."""

    def test_creates_exception(self):
        """Test exception creation."""
        exc = RateLimitException()
        assert exc.status_code == 429


class TestServiceUnavailableException:
    """Tests for ServiceUnavailableException."""

    def test_creates_exception(self):
        """Test exception creation."""
        exc = ServiceUnavailableException()
        assert exc.status_code == 503


class TestGoneException:
    """Tests for GoneException."""

    def test_creates_exception(self):
        """Test exception creation."""
        exc = GoneException()
        assert exc.status_code == 410
