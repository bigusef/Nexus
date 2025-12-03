"""Authentication domain services."""

from uuid import UUID

from src.core.jwt import JWTService
from src.core.jwt import TokenPair
from src.exceptions import AuthenticationException
from src.exceptions import NotFoundException

from .entities import User
from .repositories import UserRepository


class AuthService:
    """Authentication service handling user authentication and token management.

    This service orchestrates authentication operations:
    - Token refresh with user validation
    - Logout operations (single device / all devices)

    Usage:
        ```python
        auth_service = AuthService(user_repo, jwt_service)

        # Refresh tokens
        new_tokens = await auth_service.refresh_tokens(refresh_token)

        # Logout
        await auth_service.logout(refresh_token)
        await auth_service.logout_all_devices(user_id)
        ```
    """

    def __init__(self, user_repo: UserRepository, jwt_service: JWTService) -> None:
        """Initialize auth service with dependencies.

        Args:
            user_repo: Repository for user operations.
            jwt_service: Service for JWT token operations.
        """
        self._user_repo = user_repo
        self._jwt_service = jwt_service

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """Refresh access token using a valid refresh token.

        This method:
        1. Verifies the refresh token
        2. Validates the user still exists and is active
        3. Creates new token pair (with smart rotation)

        Args:
            refresh_token: Current refresh token.

        Returns:
            New TokenPair with access token and (possibly rotated) refresh token.

        Raises:
            InvalidTokenException: If token is invalid.
            ExpiredTokenException: If token has expired.
            RevokedTokenException: If token is revoked.
            AuthenticationException: If user not found or inactive.
        """
        # Verify refresh token and get payload
        payload = await self._jwt_service.verify_refresh_token(refresh_token)

        # Validate user still exists and is active
        try:
            user = await self._user_repo.get_by_id(payload.sub)

            if not user.is_active:
                raise AuthenticationException("User account is disabled")

            # Create new tokens (JWTService handles smart rotation)
            return await self._jwt_service.refresh_token_pair(
                refresh_token=refresh_token,
                email=user.email,
                is_staff=user.is_staff,
            )
        except NotFoundException:
            raise AuthenticationException("User not found") from None

    async def logout(self, refresh_token: str) -> None:
        """Logout from the current device by revoking the refresh token.

        Args:
            refresh_token: Current refresh token to revoke.

        Raises:
            InvalidTokenException: If token is invalid.
            ExpiredTokenException: If token has expired.
        """
        payload = await self._jwt_service.verify_refresh_token(refresh_token)
        if payload.jti:
            await self._jwt_service.revoke_refresh_token(payload.jti)

    async def logout_all_devices(self, user_id: UUID) -> None:
        """Logout from all devices by invalidating all user tokens.

        Args:
            user_id: User ID to logout.
        """
        await self._jwt_service.revoke_all_user_tokens(user_id)
