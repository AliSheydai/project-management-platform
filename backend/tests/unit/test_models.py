import uuid
from datetime import UTC, datetime

from app.modules.auth.models import RefreshToken
from app.modules.users.models import User


def test_user_model_instantiation() -> None:
    """Test User model instantiation, default values and properties."""
    user = User(
        email="test@example.com",
        password_hash="hashed_pw_secret",
        first_name="Jane",
        last_name="Doe",
    )

    assert user.email == "test@example.com"
    assert user.password_hash == "hashed_pw_secret"
    assert user.first_name == "Jane"
    assert user.last_name == "Doe"
    assert user.full_name == "Jane Doe"
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.avatar_url is None
    assert isinstance(user.id, uuid.UUID)
    assert "<User id=" in repr(user)
    assert "email=test@example.com" in repr(user)


def test_user_custom_avatar_and_superuser() -> None:
    """Test User model with optional fields provided."""
    user = User(
        email="admin@example.com",
        password_hash="hashed_admin_pw",
        first_name="Admin",
        last_name="Super",
        avatar_url="https://example.com/avatar.png",
        is_superuser=True,
    )

    assert user.avatar_url == "https://example.com/avatar.png"
    assert user.is_superuser is True
    assert user.full_name == "Admin Super"


def test_refresh_token_model_instantiation() -> None:
    """Test RefreshToken model instantiation and defaults."""
    user_id = uuid.uuid4()
    expiry = datetime.now(UTC)
    token = RefreshToken(
        user_id=user_id,
        token_hash="sample_token_hash_abc",
        expires_at=expiry,
    )

    assert token.user_id == user_id
    assert token.token_hash == "sample_token_hash_abc"
    assert token.expires_at == expiry
    assert token.is_revoked is False
    assert isinstance(token.id, uuid.UUID)
    assert "<RefreshToken id=" in repr(token)
    assert f"user_id={user_id}" in repr(token)
