from collections.abc import AsyncGenerator

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import logger

redis_pool: aioredis.ConnectionPool | None = None


def get_redis_pool() -> aioredis.ConnectionPool:
    global redis_pool
    if redis_pool is None:
        redis_pool = aioredis.ConnectionPool.from_url(
            settings.REDIS_CONNECTION_URL,
            max_connections=20,
            decode_responses=True,
        )
    return redis_pool


async def get_redis_client() -> aioredis.Redis:
    pool = get_redis_pool()
    return aioredis.Redis(connection_pool=pool)


async def close_redis_pool() -> None:
    global redis_pool
    if redis_pool is not None:
        await redis_pool.disconnect()
        redis_pool = None
        logger.info("Redis connection pool closed.")


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """FastAPI dependency for accessing the Redis async client."""
    client = await get_redis_client()
    try:
        yield client
    finally:
        await client.aclose()


async def check_redis_health() -> bool:
    """Send PING to Redis to verify connectivity."""
    try:
        client = await get_redis_client()
        res = await client.ping()
        await client.aclose()
        return bool(res)
    except Exception as e:
        logger.error("Redis health check failed: %s", e)
        return False
