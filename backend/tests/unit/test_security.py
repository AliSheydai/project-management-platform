import uuid
from datetime import timedelta

import pytest

from app.core.exceptions import UnauthorizedException
from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    get_password_hash,
    hash_refresh_token,
    verify_password,
)


def test_password_hashing_and_verification() -> None:
    """Test password hashing produces distinct valid hashes and verifies correctly."""
    plain_password = "mySecretPassword123!"
    hashed = get_password_hash(plain_password)

    assert hashed != plain_password
    assert verify_password(plain_password, hashed) is True
    assert verify_password("wrongPassword", hashed) is False


def test_jwt_token_creation_and_decoding() -> None:
    """Test creating and decoding a JWT access token."""
    user_id = uuid.uuid4()
    token = create_access_token(subject=user_id)

    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_token_expired() -> None:
    """Test decoding an expired JWT token raises UnauthorizedException."""
    user_id = uuid.uuid4()
    # Create token expired 10 seconds ago
    token = create_access_token(
        subject=user_id,
        expires_delta=timedelta(seconds=-10),
    )

    with pytest.raises(UnauthorizedException) as exc_info:
        decode_access_token(token)

    assert "expired" in exc_info.value.message.lower()


def test_jwt_token_invalid_or_tampered() -> None:
    """Test decoding an invalid/tampered token raises UnauthorizedException."""
    with pytest.raises(UnauthorizedException) as exc_info:
        decode_access_token("invalid.jwt.token.string")

    assert "invalid" in exc_info.value.message.lower()


def test_refresh_token_generation_and_hashing() -> None:
    """Test refresh token generation produces secure unique strings."""
    token1 = generate_refresh_token()
    token2 = generate_refresh_token()

    assert len(token1) >= 64
    assert len(token2) >= 64
    assert token1 != token2

    hash1 = hash_refresh_token(token1)
    hash2 = hash_refresh_token(token2)

    assert len(hash1) == 64  # SHA-256 hex string length
    assert hash1 != hash2
    assert hash1 == hash_refresh_token(token1)  # deterministic hashing
