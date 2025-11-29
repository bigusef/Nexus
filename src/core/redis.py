"""Redis configuration and connection management"""

from collections.abc import AsyncGenerator

import redis.asyncio as aioredis

from src.core import settings


# Global Redis connection pool
redis_pool: aioredis.ConnectionPool | None = None


async def init_redis() -> None:
    """Initialize Redis connection pool (called on startup).

    Creates the connection pool and tests the connection with PING.
    """
    global redis_pool
    redis_pool = aioredis.ConnectionPool.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
    )
    # Test connection
    redis_client = aioredis.Redis(connection_pool=redis_pool)
    await redis_client.ping()
    await redis_client.aclose()


async def close_redis() -> None:
    """Close Redis connection pool (called on shutdown)."""
    global redis_pool
    if redis_pool is not None:
        await redis_pool.disconnect()
        redis_pool = None


async def get_redis() -> AsyncGenerator[aioredis.Redis]:
    """Provide Redis client for dependency injection.

    Yields:
        Redis client instance that auto-closes after use.

    Raises:
        RuntimeError: If Redis pool not initialized.

    Example:
        @app.get("/cache")
        async def get_cache(redis: Redis = Depends(get_redis)):
            value = await redis.get("key")
            return {"value": value}
    """
    if redis_pool is None:
        raise RuntimeError("Redis pool not initialized. Call init_redis() first.")

    redis_client = aioredis.Redis(connection_pool=redis_pool)

    try:
        yield redis_client
    finally:
        await redis_client.aclose()
