from typing import Any

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.core.config import settings
from app.core.logging import logger

_arq_pool: ArqRedis | None = None


def get_redis_settings() -> RedisSettings:
    """Extract host, port, password from Redis connection URL."""
    url = settings.REDIS_CONNECTION_URL
    return RedisSettings.from_dsn(url)


async def get_arq_pool() -> ArqRedis | None:
    """Obtain or initialize ARQ Redis connection pool."""
    global _arq_pool
    if _arq_pool is None:
        try:
            redis_settings = get_redis_settings()
            _arq_pool = await create_pool(redis_settings)
        except Exception as e:
            logger.debug("ARQ Redis pool creation unavailable: %s", e)
            return None
    return _arq_pool


async def close_arq_pool() -> None:
    """Gracefully close ARQ Redis connection pool."""
    global _arq_pool
    if _arq_pool is not None:
        await _arq_pool.close()
        _arq_pool = None
        logger.info("ARQ Redis connection pool closed.")


async def enqueue_job(
    job_name: str,
    *args: Any,
    **kwargs: Any,
) -> bool:
    """Enqueue an asynchronous background job with graceful fallback."""
    pool = await get_arq_pool()
    if pool is not None:
        try:
            await pool.enqueue_job(job_name, *args, **kwargs)
            logger.debug("Enqueued background job '%s'", job_name)
            return True
        except Exception as e:
            logger.warning(
                "Failed to enqueue job '%s' to Redis: %s. Using direct fallback.",
                job_name,
                e,
            )

    logger.debug(
        "Job '%s' dispatched in fallback execution mode.",
        job_name,
    )
    return False
