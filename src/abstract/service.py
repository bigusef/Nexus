"""Base service class with DI support.

Provides a base class for domain services with auto-generated `.DI`
type alias for FastAPI dependency injection.
"""

from typing import Annotated
from typing import Any

from fastapi import Depends


class Service:
    """Base service with auto-generated .DI for FastAPI dependency injection.

    This class provides:
    - Auto-generated `.DI` type alias for clean FastAPI endpoint signatures
    - Support for both FastAPI DI and manual instantiation (ARQ workers, CLI)

    Usage with FastAPI (automatic dependency injection):
        ```python
        class AuthService(Service):
            def __init__(
                self,
                user_repo: UserRepository.DI,
                jwt_service: JWTService.DI,
            ) -> None:
                self._user_repo = user_repo
                self._jwt_service = jwt_service

        @app.post("/auth/refresh")
        async def refresh(auth_service: AuthService.DI):
            return await auth_service.refresh_tokens(token)
        ```

    Usage with ARQ workers (manual instantiation):
        ```python
        async def process_auth_task(ctx: dict, user_id: UUID):
            async with get_session_context() as session:
                async with get_redis_context() as redis:
                    user_repo = UserRepository(session)
                    jwt_service = JWTService(redis)
                    auth_service = AuthService(user_repo, jwt_service)
                    await auth_service.logout_all_devices(user_id)
        ```

    Attributes:
        DI: Auto-generated type alias for FastAPI dependency injection.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Generate DI type alias when subclass is defined."""
        super().__init_subclass__(**kwargs)
        cls.DI = Annotated[cls, Depends()]
