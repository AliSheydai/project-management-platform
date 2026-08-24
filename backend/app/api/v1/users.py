import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentActiveUserDep
from app.modules.users.models import User
from app.modules.users.schemas import (
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.modules.users.service import (
    get_user_by_id,
    search_users,
    update_user_profile,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Retrieve the profile data of the currently authenticated user.",
)
async def get_my_profile(
    current_user: CurrentActiveUserDep,
) -> User:
    """Return profile of authenticated user."""
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description=(
        "Update editable profile fields (first name, last name, avatar URL, "
        "or change password)."
    ),
)
async def update_my_profile(
    update_in: UserUpdate,
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Update profile attributes of the authenticated user."""
    return await update_user_profile(db, current_user, update_in)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by UUID",
    description="Retrieve public profile information for a specific user by UUID.",
)
async def get_user_profile(
    user_id: uuid.UUID,
    _current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Retrieve user profile by unique identifier."""
    return await get_user_by_id(db, user_id)


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="Search and list users",
    description=(
        "Search active platform users by name or email with pagination support "
        "for workspace invitations."
    ),
)
async def list_users(
    _current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    q: Annotated[
        str | None, Query(description="Search keyword (name or email)")
    ] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
) -> UserListResponse:
    """Search and paginate platform users."""
    return await search_users(db, query=q, page=page, page_size=page_size)
