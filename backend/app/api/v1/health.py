from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import check_db_health
from app.core.redis import check_redis_health

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str


class DependencyStatus(BaseModel):
    postgres: str
    redis: str


class ReadinessResponse(BaseModel):
    status: str
    dependencies: DependencyStatus


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness Health Check",
    description="Returns 200 OK if the FastAPI service is alive and accepting traffic.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Readiness Health Check",
    description=(
        "Verifies operational connectivity to critical dependencies "
        "(PostgreSQL and Redis)."
    ),
    responses={
        200: {"description": "All dependencies are healthy"},
        503: {"description": "One or more dependencies are unhealthy"},
    },
)
async def readiness_check(response: Response) -> ReadinessResponse:
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()

    status_str = "healthy" if (db_ok and redis_ok) else "unhealthy"

    if status_str == "unhealthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status=status_str,
        dependencies=DependencyStatus(
            postgres="connected" if db_ok else "disconnected",
            redis="connected" if redis_ok else "disconnected",
        ),
    )
