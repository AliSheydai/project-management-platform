from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logging import logger


def get_client_ip(request: Request) -> str:
    """Extract client IP from request headers or direct connection."""
    # Check X-Forwarded-For header (first entry is the client)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    # Fallback to direct client host
    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"


def get_user_or_ip_key(request: Request) -> str:
    """Extract user identifier if authenticated, otherwise fallback to client IP."""
    # Check if user state exists
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"

    # Fallback to IP address
    return f"ip:{get_client_ip(request)}"


def create_limiter() -> Limiter:
    """Initialize SlowAPI Limiter instance with Redis or in-memory fallback."""
    storage_uri = "memory://"

    if settings.REDIS_HOST:
        try:
            import redis

            r = redis.Redis.from_url(
                settings.REDIS_CONNECTION_URL,
                socket_connect_timeout=0.2,
                socket_timeout=0.2,
            )
            r.ping()
            storage_uri = settings.REDIS_CONNECTION_URL
            logger.info("Rate limiter connected to Redis storage: %s", storage_uri)
        except Exception as e:
            logger.info(
                "Redis storage for rate limiting not available (%s). "
                "Using in-memory storage.",
                e,
            )
            storage_uri = "memory://"

    return Limiter(
        key_func=get_client_ip,
        default_limits=[settings.RATE_LIMIT_DEFAULT],
        storage_uri=storage_uri,
        enabled=settings.RATE_LIMIT_ENABLED,
        headers_enabled=False,
        swallow_errors=True,
    )


limiter = create_limiter()


def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Custom response handler when rate limit is exceeded."""
    retry_after = "60"
    detail_msg = f"Rate limit exceeded: {exc.detail}"

    # Extract retry_after if available in exception detail
    response = JSONResponse(
        status_code=429,
        content={
            "detail": detail_msg,
            "error": "rate_limit_exceeded",
        },
        headers={
            "Retry-After": retry_after,
        },
    )
    return response
