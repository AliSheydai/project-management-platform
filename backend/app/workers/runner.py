import asyncio
import signal
import sys

from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.core.redis import close_redis_pool, get_redis_client

running = True


def handle_stop_signals(sig: int, frame: object) -> None:
    global running
    logger.info("Received exit signal %s. Shutting down worker gracefully...", sig)
    running = False


async def run_worker() -> None:
    """Main worker event loop."""
    global running
    setup_logging()
    logger.info(
        "Starting background worker for %s in %s mode...",
        settings.PROJECT_NAME,
        settings.ENVIRONMENT,
    )

    # Register signals for clean shutdown (where supported by OS)
    if sys.platform != "win32":
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: handle_stop_signals(s, None))
    else:
        signal.signal(signal.SIGINT, handle_stop_signals)
        signal.signal(signal.SIGTERM, handle_stop_signals)

    try:
        await get_redis_client()
        logger.info(
            "Worker connected to Redis at %s",
            settings.REDIS_CONNECTION_URL,
        )

        while running:
            try:
                # In Phase 1, worker verifies loop and connection
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in worker polling loop: %s", e)
                await asyncio.sleep(2)

    except Exception as e:
        logger.exception("Fatal worker initialization error: %s", e)
    finally:
        logger.info("Worker shutdown complete.")
        await close_redis_pool()


if __name__ == "__main__":
    asyncio.run(run_worker())
