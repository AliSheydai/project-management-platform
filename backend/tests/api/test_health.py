from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient) -> None:
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"


@pytest.mark.asyncio
async def test_liveness_health_check(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_readiness_health_check_healthy(async_client: AsyncClient) -> None:
    with (
        patch("app.api.v1.health.check_db_health", new_callable=AsyncMock) as mock_db,
        patch(
            "app.api.v1.health.check_redis_health", new_callable=AsyncMock
        ) as mock_redis,
    ):
        mock_db.return_value = True
        mock_redis.return_value = True

        response = await async_client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["dependencies"]["postgres"] == "connected"
        assert data["dependencies"]["redis"] == "connected"


@pytest.mark.asyncio
async def test_readiness_health_check_unhealthy(async_client: AsyncClient) -> None:
    with (
        patch("app.api.v1.health.check_db_health", new_callable=AsyncMock) as mock_db,
        patch(
            "app.api.v1.health.check_redis_health", new_callable=AsyncMock
        ) as mock_redis,
    ):
        mock_db.return_value = False
        mock_redis.return_value = True

        response = await async_client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["dependencies"]["postgres"] == "disconnected"
        assert data["dependencies"]["redis"] == "connected"
