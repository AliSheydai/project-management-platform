import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from app.core.exceptions import register_exception_handlers
from app.core.rate_limit import (
    get_client_ip,
    get_user_or_ip_key,
    rate_limit_exceeded_handler,
)


def test_get_client_ip_headers():
    """Verify IP extraction handles X-Forwarded-For, X-Real-IP, and fallbacks."""
    # Test X-Forwarded-For (with proxies chain)
    req_forwarded = Request(
        scope={
            "type": "http",
            "headers": [
                (b"x-forwarded-for", b"203.0.113.195, 70.41.3.18, 150.172.238.178")
            ],
            "client": ("10.0.0.1", 1234),
        }
    )
    assert get_client_ip(req_forwarded) == "203.0.113.195"

    # Test X-Real-IP
    req_real_ip = Request(
        scope={
            "type": "http",
            "headers": [(b"x-real-ip", b"198.51.100.42")],
            "client": ("10.0.0.1", 1234),
        }
    )
    assert get_client_ip(req_real_ip) == "198.51.100.42"

    # Test direct client host fallback
    req_direct = Request(
        scope={
            "type": "http",
            "headers": [],
            "client": ("192.0.2.1", 54321),
        }
    )
    assert get_client_ip(req_direct) == "192.0.2.1"

    # Test missing client scope fallback
    req_empty = Request(scope={"type": "http", "headers": []})
    assert get_client_ip(req_empty) == "127.0.0.1"


def test_get_user_or_ip_key():
    """Verify user key resolution when authenticated or unauthenticated."""
    req = Request(
        scope={
            "type": "http",
            "headers": [(b"x-real-ip", b"198.51.100.42")],
            "client": ("10.0.0.1", 1234),
        }
    )
    # Without authenticated user state
    assert get_user_or_ip_key(req) == "ip:198.51.100.42"

    # With authenticated user state
    req.state.user_id = "test-user-uuid"
    assert get_user_or_ip_key(req) == "user:test-user-uuid"


@pytest.mark.asyncio
async def test_rate_limiting_enforcement_and_429_payload():
    """Test that reaching rate limits triggers 429 with standard JSON payload."""
    test_app = FastAPI()
    test_limiter = Limiter(
        key_func=get_client_ip,
        storage_uri="memory://",
        enabled=True,
    )
    test_app.state.limiter = test_limiter
    register_exception_handlers(test_app)

    @test_app.get("/test-limited")
    @test_limiter.limit("3/minute")
    async def limited_endpoint(request: Request):
        return {"status": "ok"}

    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        # First 3 requests should succeed
        for _ in range(3):
            res = await client.get("/test-limited")
            assert res.status_code == 200
            assert res.json() == {"status": "ok"}

        # 4th request must be throttled with 429
        res_throttled = await client.get("/test-limited")
        assert res_throttled.status_code == 429
        assert "Retry-After" in res_throttled.headers

        body = res_throttled.json()
        assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert "Rate limit exceeded" in body["error"]["message"]


@pytest.mark.asyncio
async def test_direct_rate_limit_exceeded_handler():
    """Verify standalone rate_limit_exceeded_handler behavior."""
    from limits import parse
    from slowapi.wrappers import Limit

    limit_item = parse("5/minute")
    wrapped_limit = Limit(
        limit=limit_item,
        key_func=get_client_ip,
        scope=None,
        per_method=False,
        methods=None,
        error_message="5 per 1 minute",
        exempt_when=None,
        cost=1,
        override_defaults=False,
    )
    req = Request(scope={"type": "http", "headers": []})
    exc = RateLimitExceeded(wrapped_limit)
    response = rate_limit_exceeded_handler(req, exc)
    assert response.status_code == 429
    assert response.headers.get("Retry-After") == "60"
