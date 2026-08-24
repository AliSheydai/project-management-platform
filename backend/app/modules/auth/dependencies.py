import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.modules.users.models import User

# Use auto_error=False to provide consistent AppException response structure
security_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(security_bearer)
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Validate bearer token from Authorization header and return User."""
    if credentials is None:
        raise UnauthorizedException(
            message="Authentication credentials were not provided"
        )

    token = credentials.credentials
    payload = decode_access_token(token)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException(message="Invalid token payload: missing subject")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError as e:
        raise UnauthorizedException(message="Invalid user identifier in token") from e

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedException(message="User not found")

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Verify that current user account is active."""
    if not current_user.is_active:
        raise ForbiddenException(message="User account is deactivated")
    return current_user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
CurrentActiveUserDep = Annotated[User, Depends(get_current_active_user)]
