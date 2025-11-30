"""Global test fixtures for Nexus Cortex."""

# ruff: noqa: E402
# Set test environment variables BEFORE importing application modules
import os

os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://nexus:nexus@localhost:5432/nexus")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only-do-not-use-in-production")
os.environ.setdefault("JWT_ACCESS_EXPIRATION", "15m")
os.environ.setdefault("JWT_REFRESH_EXPIRATION", "7d")
os.environ.setdefault("ALLOWED_ORIGINS", "*")

import gettext as gettext_module
from collections.abc import AsyncGenerator
from uuid import uuid4

import fakeredis.aioredis
import pytest
import pytest_asyncio
from httpx import ASGITransport
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from src.abstract.entity import Entity
from src.core import i18n as i18n_module
from src.core import settings
from src.core.database import get_session
from src.core.jwt import JWTService
from src.core.redis import get_redis
from src.domains.auth.entities import User
from src.domains.auth.repositories import UserRepository
from src.domains.auth.services import AuthService
from src.main import app
from src.utilities.enums import Language

# Initialize translations for tests using NullTranslations (returns original strings)
for lang in Language:
    i18n_module._translations[lang.value] = gettext_module.NullTranslations()


# =============================================================================
# DATABASE FIXTURES
# =============================================================================

# Track if tables were created
_tables_created = False


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session for each test.

    Each test runs in a transaction that is rolled back after the test completes,
    ensuring test isolation without needing to recreate tables.
    """
    global _tables_created

    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )

    # Create tables on first use
    if not _tables_created:
        async with engine.begin() as conn:
            await conn.run_sync(Entity.metadata.create_all)
        _tables_created = True

    # Use a connection with a transaction that we can rollback
    async with engine.connect() as conn:
        # Start a transaction
        trans = await conn.begin()

        # Create session bound to this connection
        session = AsyncSession(bind=conn, expire_on_commit=False)

        try:
            yield session
        finally:
            # Always rollback to ensure test isolation
            await trans.rollback()
            await session.close()

    await engine.dispose()


# =============================================================================
# REDIS FIXTURES
# =============================================================================


@pytest.fixture
def fake_redis() -> fakeredis.aioredis.FakeRedis:
    """Provide a fake Redis client for testing."""
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


# =============================================================================
# SERVICE FIXTURES
# =============================================================================


@pytest_asyncio.fixture
async def jwt_service(fake_redis) -> JWTService:
    """Provide a JWTService instance with fake Redis."""
    return JWTService(fake_redis)


@pytest_asyncio.fixture
async def user_repository(db_session) -> UserRepository:
    """Provide a UserRepository instance."""
    return UserRepository(db_session)


@pytest_asyncio.fixture
async def auth_service(user_repository, jwt_service) -> AuthService:
    """Provide an AuthService instance."""
    return AuthService(user_repository, jwt_service)


# =============================================================================
# USER FIXTURES
# =============================================================================


@pytest_asyncio.fixture
async def test_user(db_session) -> User:
    """Create a test user in the database."""
    user = User(
        pk=uuid4(),
        email="test@example.com",
        first_name="Test",
        last_name="User",
        is_staff=False,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def staff_user(db_session) -> User:
    """Create a staff user in the database."""
    user = User(
        pk=uuid4(),
        email="staff@example.com",
        first_name="Staff",
        last_name="User",
        is_staff=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def locked_user(db_session) -> User:
    """Create a locked user in the database."""
    user = User(
        pk=uuid4(),
        email="locked@example.com",
        first_name="Locked",
        last_name="User",
        is_staff=False,
        is_locked=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


# =============================================================================
# API CLIENT FIXTURES
# =============================================================================


@pytest_asyncio.fixture
async def client(db_session, fake_redis) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP client for API testing."""

    async def override_get_session():
        yield db_session

    async def override_get_redis():
        yield fake_redis

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
