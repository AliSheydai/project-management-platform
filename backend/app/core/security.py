import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedException


def get_password_hash(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    # Truncate to 72 bytes as per bcrypt specification
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "access",
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a signed JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            raise UnauthorizedException(message="Invalid token type")
        if not payload.get("sub"):
            raise UnauthorizedException(message="Token missing subject claim")
        return payload
    except jwt.ExpiredSignatureError as e:
        raise UnauthorizedException(message="Access token has expired") from e
    except jwt.InvalidTokenError as e:
        raise UnauthorizedException(message="Invalid authentication token") from e


def generate_refresh_token() -> str:
    """Generate a cryptographically secure random token string."""
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    """Compute SHA-256 hash of a refresh token for secure database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
