"""Database configuration and connection management"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

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
        echo=settings.debug, # Log SQL queries in debug mode
        pool_pre_ping=True, # Verify connections before using
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


async def get_session() -> AsyncGenerator[AsyncSession, None]:
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
