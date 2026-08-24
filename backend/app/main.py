from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger, setup_logging
from app.core.redis import close_redis_pool, get_redis_pool


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager for startup and shutdown procedures."""
    setup_logging()
    logger.info(
        "Starting %s in %s mode...", settings.PROJECT_NAME, settings.ENVIRONMENT
    )

    # Initialize Redis connection pool
    try:
        get_redis_pool()
        logger.info("Redis connection pool initialized.")
    except Exception as e:
        logger.warning("Could not initialize Redis connection pool on startup: %s", e)

    yield

    # Teardown database engine and Redis pool
    logger.info("Shutting down %s...", settings.PROJECT_NAME)
    await close_redis_pool()
    await engine.dispose()
    logger.info("Database engine and Redis connections disposed cleanly.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="Production-grade API for Project Management Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Exception handlers
register_exception_handlers(app)

# CORS middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Root-level health endpoints (as requested by specification: /health & /health/ready)
app.include_router(health_router)

# Versioned API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root redirect / welcoming endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "health": "/health",
        "version": "0.1.0",
    }
