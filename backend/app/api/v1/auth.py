from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.modules.auth.dependencies import CurrentActiveUserDep
from app.modules.auth.schemas import (
    AuthResponse,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.modules.auth.service import (
    authenticate_user,
    logout_user,
    refresh_tokens,
    register_user,
)
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Create a new user account, hash their password, and return "
        "authentication tokens with user profile."
    ),
)
@limiter.limit(settings.RATE_LIMIT_AUTH_REGISTER)
async def register(
    request: Request,
    register_in: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    """Register a new user and generate access/refresh token pair."""
    tokens, user = await register_user(db, register_in)
    return AuthResponse(
        tokens=tokens,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and obtain tokens",
    description=(
        "Verify email and password credentials, returning a signed "
        "JWT access token and refresh token."
    ),
)
@limiter.limit(settings.RATE_LIMIT_AUTH_LOGIN)
async def login(
    request: Request,
    login_in: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    """Authenticate credentials and generate token pair."""
    tokens, user = await authenticate_user(db, login_in)
    return AuthResponse(
        tokens=tokens,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description=(
        "Rotate the provided refresh token and receive a brand new "
        "access and refresh token pair."
    ),
)
@limiter.limit(settings.RATE_LIMIT_AUTH_REFRESH)
async def refresh(
    request: Request,
    refresh_in: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Rotate refresh token and issue new token pair."""
    return await refresh_tokens(db, refresh_in.refresh_token)


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Log out user",
    description="Revoke the provided refresh token to terminate the session.",
)
async def logout(
    logout_in: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Revoke active refresh token on logout."""
    await logout_user(db, logout_in.refresh_token)
    return MessageResponse(message="Successfully logged out")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description=(
        "Retrieve the authenticated user's profile information using "
        "the Bearer access token."
    ),
)
async def get_me(
    current_user: CurrentActiveUserDep,
) -> User:
    """Return profile of currently authenticated active user."""
    return current_user
