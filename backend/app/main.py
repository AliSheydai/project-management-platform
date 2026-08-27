from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.v1.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger, setup_logging
from app.core.middleware import SecurityHeadersMiddleware
from app.core.rate_limit import limiter
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
    description=(
        "Production-grade REST API for a project management platform "
        "(auth, projects, tasks, comments, labels, attachments, search, notifications).\n\n"
        "## Try it out\n"
        "1. Use **POST /api/v1/auth/register** or **POST /api/v1/auth/login**.\n"
        "2. Copy `tokens.access_token` from the response.\n"
        "3. Click **Authorize** and paste only the access token "
        "(Swagger adds the `Bearer` prefix).\n"
        "4. Call protected endpoints (projects, tasks, …).\n\n"
        "Interactive docs: `/docs` · ReDoc: `/redoc` · OpenAPI: `/openapi.json`"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


def custom_openapi() -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema["servers"] = [
        {
            "url": "https://project-management-platform-ltzd.vercel.app",
            "description": "Production (Vercel)",
        },
        {"url": "http://localhost:8000", "description": "Local development"},
    ]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]


@app.get("/api/v1/openapi.json", include_in_schema=False)
async def openapi_v1_alias() -> dict:
    """Keep older OpenAPI path working for clients that still request it."""
    return app.openapi()


# Attach SlowAPI limiter state
app.state.limiter = limiter

# Exception handlers
register_exception_handlers(app)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=settings.CORS_EXPOSE_HEADERS,
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
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "health": "/health",
        "version": "0.1.0",
    }
