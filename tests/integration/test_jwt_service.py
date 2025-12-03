"""Integration tests for JWT service."""

from datetime import timedelta
from uuid import uuid4

import pytest
from freezegun import freeze_time

from src.security import JWTService
from src.exceptions import ExpiredTokenException
from src.exceptions import InvalidTokenException
from src.exceptions import RevokedTokenException


class TestCreateTokenPair:
    """Tests for create_token_pair method."""

    async def test_create_token_pair(self, jwt_service: JWTService):
        """Test creating a token pair."""
        user_id = uuid4()
        tokens = await jwt_service.create_token_pair(
            user_id=user_id,
            email="test@example.com",
            is_staff=False,
        )

        assert tokens.access is not None
        assert tokens.refresh is not None
        assert tokens.access != tokens.refresh

    async def test_create_token_pair_staff_user(self, jwt_service: JWTService):
        """Test creating tokens for staff user."""
        user_id = uuid4()
        tokens = await jwt_service.create_token_pair(
            user_id=user_id,
            email="staff@example.com",
            is_staff=True,
        )

        payload = await jwt_service.verify_access_token(tokens.access)
        assert payload.is_staff is True


class TestVerifyAccessToken:
    """Tests for verify_access_token method."""

    async def test_verify_valid_access_token(self, jwt_service: JWTService):
        """Test verifying a valid access token."""
        user_id = uuid4()
        tokens = await jwt_service.create_token_pair(
            user_id=user_id,
            email="test@example.com",
            is_staff=False,
        )

        payload = await jwt_service.verify_access_token(tokens.access)

        assert payload.sub == user_id
        assert payload.email == "test@example.com"
        assert payload.is_staff is False
        assert payload.type == "access"

    async def test_verify_access_token_invalid(self, jwt_service: JWTService):
        """Test verifying an invalid access token."""
        with pytest.raises(InvalidTokenException):
            await jwt_service.verify_access_token("invalid.token.here")

    async def test_verify_access_token_wrong_type(self, jwt_service: JWTService):
        """Test verifying refresh token as access token."""
        user_id = uuid4()
        tokens = await jwt_service.create_token_pair(
            user_id=user_id,
            email="test@example.com",
            is_staff=False,
        )

        with pytest.raises(InvalidTokenException):
            await jwt_service.verify_access_token(tokens.refresh)

    async def test_verify_access_token_expired(self, jwt_service: JWTService):
        """Test verifying an expired access token."""
        user_id = uuid4()

        with freeze_time("2024-01-01 12:00:00"):
            tokens = await jwt_service.create_token_pair(
                user_id=user_id,
                email="test@example.com",
                is_staff=False,
            )

        # Move time forward past expiration
        with freeze_time("2024-01-01 13:00:00"):
            with pytest.raises(ExpiredTokenException):
                await jwt_service.verify_access_token(tokens.access)


class TestVerifyRefreshToken:
    """Tests for verify_refresh_token method."""

    async def test_verify_valid_refresh_token(self, jwt_service: JWTService):
        """Test verifying a valid refresh token."""
        user_id = uuid4()
        tokens = await jwt_service.create_token_pair(
            user_id=user_id,
            email="test@example.com",
            is_staff=False,
        )

        payload = await jwt_service.verify_refresh_token(tokens.refresh)

        assert payload.sub == user_id
        assert payload.type == "refresh"
        assert payload.jti is not None

    async def test_verify_refresh_token_invalid(self, jwt_service: JWTService):
        """Test verifying an invalid refresh token."""
        with pytest.raises(InvalidTokenException):
            await jwt_service.verify_refresh_token("invalid.token.here")

    async def test_verify_refresh_token_wrong_type(self, jwt_service: JWTService):
        """Test verifying access token as refresh token."""
        user_id = uuid4()
        tokens = await jwt_service.create_token_pair(
            user_id=user_id,
            email="test@example.com",
            is_staff=False,
        )

        with pytest.raises(InvalidTokenException):
            await jwt_service.verify_refresh_token(tokens.access)


class TestRefreshTokenPair:
    """Tests for refresh_token_pair method."""

    async def test_refresh_tokens(self, jwt_service: JWTService):
        """Test refreshing tokens returns valid access token."""
        user_id = uuid4()
        original_tokens = await jwt_service.create_token_pair(
            user_id=user_id,
            email="test@example.com",
            is_staff=False,
        )

        new_tokens = await jwt_service.refresh_token_pair(
            refresh_token=original_tokens.refresh,
            email="test@example.com",
            is_staff=False,
        )

        # Verify new access token is valid
        payload = await jwt_service.verify_access_token(new_tokens.access)
        assert payload.sub == user_id
        assert payload.email == "test@example.com"
        # Note: tokens created in same second may be identical (same iat/exp)

    async def test_refresh_tokens_invalid_refresh(self, jwt_service: JWTService):
        """Test refreshing with invalid refresh token."""
        with pytest.raises(InvalidTokenException):
            await jwt_service.refresh_token_pair(
                refresh_token="invalid.token",
                email="test@example.com",
                is_staff=False,
            )


class TestRevokeRefreshToken:
    """Tests for revoke_refresh_token method."""

    async def test_revoke_refresh_token(self, jwt_service: JWTService):
        """Test revoking a refresh token."""
        user_id = uuid4()
        tokens = await jwt_service.create_token_pair(
            user_id=user_id,
            email="test@example.com",
            is_staff=False,
        )

        # Get the jti from the token
        payload = await jwt_service.verify_refresh_token(tokens.refresh)
        assert payload.jti is not None

        # Revoke the token
        await jwt_service.revoke_refresh_token(payload.jti)

        # Token should now be revoked
        with pytest.raises(RevokedTokenException):
            await jwt_service.verify_refresh_token(tokens.refresh)


class TestRevokeAllUserTokens:
    """Tests for revoke_all_user_tokens method."""

    async def test_revoke_all_user_tokens(self, jwt_service: JWTService):
        """Test revoking all tokens for a user."""
        user_id = uuid4()

        # Create multiple token pairs
        tokens1 = await jwt_service.create_token_pair(
            user_id=user_id,
            email="test@example.com",
            is_staff=False,
        )
        tokens2 = await jwt_service.create_token_pair(
            user_id=user_id,
            email="test@example.com",
            is_staff=False,
        )

        # Revoke all tokens
        await jwt_service.revoke_all_user_tokens(user_id)

        # Both access tokens should be revoked (version mismatch)
        with pytest.raises(RevokedTokenException):
            await jwt_service.verify_access_token(tokens1.access)

        with pytest.raises(RevokedTokenException):
            await jwt_service.verify_access_token(tokens2.access)

    async def test_new_tokens_work_after_revoke_all(self, jwt_service: JWTService):
        """Test that new tokens work after revoking all."""
        user_id = uuid4()

        # Create and revoke
        await jwt_service.create_token_pair(
            user_id=user_id,
            email="test@example.com",
            is_staff=False,
        )
        await jwt_service.revoke_all_user_tokens(user_id)

        # Create new tokens
        new_tokens = await jwt_service.create_token_pair(
            user_id=user_id,
            email="test@example.com",
            is_staff=False,
        )

        # New tokens should work
        payload = await jwt_service.verify_access_token(new_tokens.access)
        assert payload.sub == user_id
