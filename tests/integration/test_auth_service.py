"""Integration tests for AuthService."""

from uuid import uuid4

import pytest

from src.core.jwt import JWTService
from src.domains.auth.entities import User
from src.domains.auth.repositories import UserRepository
from src.domains.auth.services import AuthService
from src.exceptions import AuthenticationException
from src.exceptions import RevokedTokenException


class TestAuthServiceRefreshTokens:
    """Tests for refresh_tokens method."""

    async def test_refresh_tokens_success(self, db_session, fake_redis, test_user):
        """Test successful token refresh."""
        user_repo = UserRepository(db_session)
        jwt_service = JWTService(fake_redis)
        auth_service = AuthService(user_repo, jwt_service)

        # Create initial tokens
        initial_tokens = await jwt_service.create_token_pair(
            user_id=test_user.pk,
            email=test_user.email,
            is_staff=test_user.is_staff,
        )

        # Refresh tokens
        new_tokens = await auth_service.refresh_tokens(initial_tokens.refresh)

        assert new_tokens.access is not None
        # Note: tokens created in the same second may be identical (same iat/exp)
        # The important thing is that the new token is valid

        # Verify new access token works
        payload = await jwt_service.verify_access_token(new_tokens.access)
        assert payload.sub == test_user.pk
        assert payload.email == test_user.email

    async def test_refresh_tokens_user_not_found(self, db_session, fake_redis):
        """Test refresh fails when user doesn't exist."""
        user_repo = UserRepository(db_session)
        jwt_service = JWTService(fake_redis)
        auth_service = AuthService(user_repo, jwt_service)

        # Create tokens for non-existent user
        non_existent_id = uuid4()
        initial_tokens = await jwt_service.create_token_pair(
            user_id=non_existent_id,
            email="nonexistent@example.com",
            is_staff=False,
        )

        # Refresh should fail
        with pytest.raises(AuthenticationException, match="User not found"):
            await auth_service.refresh_tokens(initial_tokens.refresh)

    async def test_refresh_tokens_user_inactive(self, db_session, fake_redis, locked_user):
        """Test refresh fails when user is inactive (locked)."""
        user_repo = UserRepository(db_session)
        jwt_service = JWTService(fake_redis)
        auth_service = AuthService(user_repo, jwt_service)

        # Create tokens for locked user
        initial_tokens = await jwt_service.create_token_pair(
            user_id=locked_user.pk,
            email=locked_user.email,
            is_staff=locked_user.is_staff,
        )

        # Refresh should fail
        with pytest.raises(AuthenticationException, match="disabled"):
            await auth_service.refresh_tokens(initial_tokens.refresh)


class TestAuthServiceLogout:
    """Tests for logout method."""

    async def test_logout_success(self, db_session, fake_redis, test_user):
        """Test successful logout revokes refresh token."""
        user_repo = UserRepository(db_session)
        jwt_service = JWTService(fake_redis)
        auth_service = AuthService(user_repo, jwt_service)

        # Create tokens
        tokens = await jwt_service.create_token_pair(
            user_id=test_user.pk,
            email=test_user.email,
            is_staff=test_user.is_staff,
        )

        # Logout
        await auth_service.logout(tokens.refresh)

        # Refresh token should be revoked
        with pytest.raises(RevokedTokenException):
            await jwt_service.verify_refresh_token(tokens.refresh)

    async def test_logout_access_token_still_works(self, db_session, fake_redis, test_user):
        """Test that access token still works after logout (until expiry)."""
        user_repo = UserRepository(db_session)
        jwt_service = JWTService(fake_redis)
        auth_service = AuthService(user_repo, jwt_service)

        # Create tokens
        tokens = await jwt_service.create_token_pair(
            user_id=test_user.pk,
            email=test_user.email,
            is_staff=test_user.is_staff,
        )

        # Logout
        await auth_service.logout(tokens.refresh)

        # Access token should still work (it has its own expiry)
        payload = await jwt_service.verify_access_token(tokens.access)
        assert payload.sub == test_user.pk


class TestAuthServiceLogoutAllDevices:
    """Tests for logout_all_devices method."""

    async def test_logout_all_devices(self, db_session, fake_redis, test_user):
        """Test logging out from all devices."""
        user_repo = UserRepository(db_session)
        jwt_service = JWTService(fake_redis)
        auth_service = AuthService(user_repo, jwt_service)

        # Create multiple token pairs (simulating multiple devices)
        tokens1 = await jwt_service.create_token_pair(
            user_id=test_user.pk,
            email=test_user.email,
            is_staff=test_user.is_staff,
        )
        tokens2 = await jwt_service.create_token_pair(
            user_id=test_user.pk,
            email=test_user.email,
            is_staff=test_user.is_staff,
        )

        # Logout all devices
        await auth_service.logout_all_devices(test_user.pk)

        # Both access tokens should be revoked (version mismatch)
        with pytest.raises(RevokedTokenException):
            await jwt_service.verify_access_token(tokens1.access)

        with pytest.raises(RevokedTokenException):
            await jwt_service.verify_access_token(tokens2.access)

    async def test_new_login_after_logout_all(self, db_session, fake_redis, test_user):
        """Test that new login works after logout all devices."""
        user_repo = UserRepository(db_session)
        jwt_service = JWTService(fake_redis)
        auth_service = AuthService(user_repo, jwt_service)

        # Create tokens and logout all
        await jwt_service.create_token_pair(
            user_id=test_user.pk,
            email=test_user.email,
            is_staff=test_user.is_staff,
        )
        await auth_service.logout_all_devices(test_user.pk)

        # New login should work
        new_tokens = await jwt_service.create_token_pair(
            user_id=test_user.pk,
            email=test_user.email,
            is_staff=test_user.is_staff,
        )

        payload = await jwt_service.verify_access_token(new_tokens.access)
        assert payload.sub == test_user.pk
