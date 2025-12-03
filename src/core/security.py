"""Security dependencies for FastAPI."""

from typing import Annotated
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.jwt import JWTService
from src.core.jwt import TokenPayload
from src.core.redis import get_redis
from src.domains.auth.repositories import UserRepository
from src.domains.auth.services import AuthService
from src.exceptions import AuthorizationException


# Bearer token security scheme for OpenAPI docs
bearer_scheme = HTTPBearer()


async def get_jwt_service(
    redis: Annotated[aioredis.Redis, Depends(get_redis)],
) -> JWTService:
    """Provide a JWTService instance.

    Args:
        redis: Redis a client from dependency injection.

    Returns:
        Configured JWTService instance.
    """
    return JWTService(redis)


async def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
) -> AuthService:
    """Provide an AuthService instance with dependencies.

    Args:
        session: Database session from dependency injection.
        jwt_service: JWT service from dependency injection.

    Returns:
        Configured AuthService instance.
    """
    user_repo = UserRepository(session)
    return AuthService(user_repo, jwt_service)


async def _get_token_payload(
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> TokenPayload:
    """Extract and verify token payload from Authorization header.

    Args:
        jwt_service: JWT service for token verification.
        credentials: Bearer token credentials from HTTPBearer security scheme.

    Returns:
        TokenPayload with user information.

    Raises:
        InvalidTokenException: If token is invalid.
        ExpiredTokenException: If token has expired.
        RevokedTokenException: If token is revoked.
    """
    return await jwt_service.verify_access_token(credentials.credentials)


async def get_current_user(
    payload: Annotated[TokenPayload, Depends(_get_token_payload)],
) -> UUID:
    """Get current user ID from Authorization header.

    Args:
        payload: Token payload from dependency injection.

    Returns:
        User ID as UUID.
    """
    return payload.sub


async def get_staff_user(
    payload: Annotated[TokenPayload, Depends(_get_token_payload)],
) -> UUID:
    """Get current user ID, verifying the user is a staff member.

    Args:
        payload: Token payload from dependency injection.

    Returns:
        User ID as UUID if user is staff.

    Raises:
        AuthorizationException: If user is not staff.
    """
    if not payload.is_staff:
        raise AuthorizationException()

    return payload.sub


# Type aliases for cleaner endpoint signatures
UserID = Annotated[UUID, Depends(get_current_user)]
StaffID = Annotated[UUID, Depends(get_staff_user)]
