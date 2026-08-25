from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    UnauthorizedException,
)
from app.core.queue import enqueue_job
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    get_password_hash,
    hash_refresh_token,
    verify_password,
)
from app.modules.auth.models import RefreshToken
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.modules.users.models import User


async def create_tokens_for_user(
    db: AsyncSession,
    user: User,
) -> TokenResponse:
    """Issue a new JWT access token and store a hashed refresh token."""
    access_token = create_access_token(subject=str(user.id))
    raw_refresh_token = generate_refresh_token()
    token_hash = hash_refresh_token(raw_refresh_token)
    expires_at = datetime.now(UTC) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )

    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        is_revoked=False,
    )
    db.add(refresh_token_record)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def register_user(
    db: AsyncSession,
    register_in: RegisterRequest,
) -> tuple[TokenResponse, User]:
    """Register a new user, hash their password, and issue initial session tokens."""
    normalized_email = register_in.email.strip().lower()

    # Check for existing user
    stmt = select(User).where(User.email == normalized_email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none() is not None:
        raise ConflictException(message="A user with this email already exists")

    # Hash password and persist user
    password_hash = get_password_hash(register_in.password)
    new_user = User(
        email=normalized_email,
        password_hash=password_hash,
        first_name=register_in.first_name.strip(),
        last_name=register_in.last_name.strip(),
        avatar_url=register_in.avatar_url,
        is_active=True,
        is_superuser=False,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    tokens = await create_tokens_for_user(db, new_user)

    # Enqueue welcome email in background
    await enqueue_job(
        "send_email_job",
        to_email=new_user.email,
        template="welcome",
        context={"name": new_user.first_name},
    )

    return tokens, new_user


async def authenticate_user(
    db: AsyncSession,
    login_in: LoginRequest,
) -> tuple[TokenResponse, User]:
    """Authenticate user credentials and issue new tokens."""
    normalized_email = login_in.email.strip().lower()

    stmt = select(User).where(User.email == normalized_email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or not verify_password(login_in.password, user.password_hash):
        raise UnauthorizedException(message="Incorrect email or password")

    if not user.is_active:
        raise ForbiddenException(message="User account is deactivated")

    tokens = await create_tokens_for_user(db, user)
    return tokens, user


async def refresh_tokens(
    db: AsyncSession,
    raw_refresh_token: str,
) -> TokenResponse:
    """Validate a refresh token, rotate it, and return a fresh token pair."""
    token_hash = hash_refresh_token(raw_refresh_token)

    stmt = (
        select(RefreshToken)
        .options(selectinload(RefreshToken.user))
        .where(RefreshToken.token_hash == token_hash)
    )
    result = await db.execute(stmt)
    token_record = result.scalar_one_or_none()

    if token_record is None or token_record.is_revoked:
        raise UnauthorizedException(message="Invalid or revoked refresh token")

    # Check expiration
    now = datetime.now(UTC)
    token_expires_at = token_record.expires_at
    if token_expires_at.tzinfo is None:
        token_expires_at = token_expires_at.replace(tzinfo=UTC)

    if token_expires_at < now:
        token_record.is_revoked = True
        await db.commit()
        raise UnauthorizedException(message="Refresh token has expired")

    user = token_record.user
    if user is None or not user.is_active:
        token_record.is_revoked = True
        await db.commit()
        raise UnauthorizedException(message="User account is inactive or not found")

    # Invalidate previous token (token rotation)
    token_record.is_revoked = True
    await db.commit()

    # Issue new token pair
    new_tokens = await create_tokens_for_user(db, user)
    return new_tokens


async def logout_user(
    db: AsyncSession,
    raw_refresh_token: str,
) -> None:
    """Revoke a refresh token on user logout."""
    token_hash = hash_refresh_token(raw_refresh_token)
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    result = await db.execute(stmt)
    token_record = result.scalar_one_or_none()

    if token_record is not None:
        token_record.is_revoked = True
        await db.commit()
