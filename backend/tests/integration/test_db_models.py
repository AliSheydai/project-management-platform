from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.auth.models import RefreshToken
from app.modules.users.models import User


async def test_create_and_query_user(db_session: AsyncSession) -> None:
    """Test persisting a user and querying from database."""
    new_user = User(
        email="john.doe@example.com",
        password_hash="secret_hashed_pw",
        first_name="John",
        last_name="Doe",
        avatar_url="https://example.com/john.jpg",
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    assert new_user.id is not None
    assert new_user.created_at is not None
    assert new_user.updated_at is not None
    assert new_user.is_active is True
    assert new_user.is_superuser is False

    # Query back using select
    stmt = select(User).where(User.email == "john.doe@example.com")
    result = await db_session.execute(stmt)
    fetched_user = result.scalar_one_or_none()

    assert fetched_user is not None
    assert fetched_user.id == new_user.id
    assert fetched_user.full_name == "John Doe"
    assert fetched_user.avatar_url == "https://example.com/john.jpg"


async def test_user_unique_email_constraint(db_session: AsyncSession) -> None:
    """Test that duplicate emails violate unique constraint."""
    user1 = User(
        email="duplicate@example.com",
        password_hash="hash1",
        first_name="First",
        last_name="User",
    )
    db_session.add(user1)
    await db_session.commit()

    user2 = User(
        email="duplicate@example.com",
        password_hash="hash2",
        first_name="Second",
        last_name="User",
    )
    db_session.add(user2)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()


async def test_user_refresh_token_relationship_and_cascade(
    db_session: AsyncSession,
) -> None:
    """Test RefreshToken creation and cascade delete when user is removed."""
    user = User(
        email="token.user@example.com",
        password_hash="secure_hash",
        first_name="Token",
        last_name="User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    expires = datetime.now(UTC) + timedelta(days=7)
    token1 = RefreshToken(
        user_id=user.id,
        token_hash="hash_token_1_abc",
        expires_at=expires,
    )
    token2 = RefreshToken(
        user_id=user.id,
        token_hash="hash_token_2_def",
        expires_at=expires,
    )
    db_session.add_all([token1, token2])
    await db_session.commit()

    # Query user with eager loaded refresh tokens
    stmt = (
        select(User)
        .options(selectinload(User.refresh_tokens))
        .where(User.id == user.id)
    )
    result = await db_session.execute(stmt)
    user_with_tokens = result.scalar_one()

    assert len(user_with_tokens.refresh_tokens) == 2
    token_hashes = {t.token_hash for t in user_with_tokens.refresh_tokens}
    assert "hash_token_1_abc" in token_hashes
    assert "hash_token_2_def" in token_hashes

    # Delete user and verify cascading deletion of refresh tokens
    await db_session.delete(user_with_tokens)
    await db_session.commit()

    # Query tokens table directly to confirm they were deleted
    token_stmt = select(RefreshToken).where(RefreshToken.user_id == user.id)
    token_res = await db_session.execute(token_stmt)
    assert token_res.scalars().all() == []


async def test_refresh_token_unique_hash_constraint(
    db_session: AsyncSession,
) -> None:
    """Test that refresh token hash must be unique."""
    user = User(
        email="unique.token@example.com",
        password_hash="hash",
        first_name="Test",
        last_name="User",
    )
    db_session.add(user)
    await db_session.commit()

    expiry = datetime.now(UTC) + timedelta(days=1)
    token1 = RefreshToken(
        user_id=user.id,
        token_hash="identical_hash_123",
        expires_at=expiry,
    )
    db_session.add(token1)
    await db_session.commit()

    token2 = RefreshToken(
        user_id=user.id,
        token_hash="identical_hash_123",
        expires_at=expiry,
    )
    db_session.add(token2)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()
