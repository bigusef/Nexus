"""Database configuration and connection management"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.core import settings


# Global database engine and session factory
engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_database() -> None:
    """Initialize database engine and session factory (called on startup).

    Creates the async engine with connection pooling and tests the connection.
    """
    global engine, async_session_factory

    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,  # Log SQL queries in debug mode
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20,
    )

    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Test connection
    async with engine.begin():
        pass


async def close_database() -> None:
    """Close database engine (called on shutdown)."""
    global engine, async_session_factory

    if engine is not None:
        await engine.dispose()
        engine = None
        async_session_factory = None


async def get_session() -> AsyncGenerator[AsyncSession]:
    """Provide async database session for dependency injection.

    Yields:
        AsyncSession instance that auto-closes after use.

    Raises:
        RuntimeError: If database not initialized.

    Example:
        @app.get("/users")
        async def get_users(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(User))
            return result.scalars().all()
    """
    global async_session_factory

    if async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession]:
    """Provide async database session as context manager.

    Use this for ARQ workers and other non-FastAPI contexts where
    dependency injection is not available.

    Yields:
        AsyncSession instance that auto-closes after use.

    Raises:
        RuntimeError: If database not initialized.

    Example:
        async def my_arq_task(ctx: dict, user_id: UUID):
            async with get_session_context() as session:
                repo = UserRepository(session)
                user = await repo.get_one(User.pk == user_id)
                # ... process user
                await session.commit()

    Transaction with multiple repositories:
        async with get_session_context() as session:
            user_repo = UserRepository(session)
            profile_repo = ProfileRepository(session)

            user = await user_repo.create(email="test@example.com")
            await profile_repo.create(user_id=user.pk)

            await session.commit()  # Single transaction
    """
    global async_session_factory

    if async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
