import math
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.security import get_password_hash
from app.modules.users.models import User
from app.modules.users.schemas import UserListResponse, UserResponse, UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User:
    """Fetch user by UUID or raise NotFoundException."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException(message="User not found")
    return user


async def update_user_profile(
    db: AsyncSession,
    user: User,
    update_data: UserUpdate,
) -> User:
    """Update user profile fields and optionally re-hash password."""
    if update_data.first_name is not None:
        user.first_name = update_data.first_name.strip()
    if update_data.last_name is not None:
        user.last_name = update_data.last_name.strip()
    if update_data.avatar_url is not None:
        user.avatar_url = update_data.avatar_url.strip() or None
    if update_data.password is not None:
        user.password_hash = get_password_hash(update_data.password)

    await db.commit()
    await db.refresh(user)
    return user


async def search_users(
    db: AsyncSession,
    query: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> UserListResponse:
    """Search and paginate active users by email or full name."""
    base_filter = [User.is_active.is_(True)]

    if query and query.strip():
        search_pattern = f"%{query.strip()}%"
        base_filter.append(
            or_(
                User.email.ilike(search_pattern),
                User.first_name.ilike(search_pattern),
                User.last_name.ilike(search_pattern),
            )
        )

    # Total count
    count_stmt = select(func.count(User.id)).where(*base_filter)
    count_res = await db.execute(count_stmt)
    total = count_res.scalar() or 0

    # Paginated results
    offset = (page - 1) * page_size
    stmt = (
        select(User)
        .where(*base_filter)
        .order_by(User.first_name.asc(), User.last_name.asc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    users = result.scalars().all()

    pages = math.ceil(total / page_size) if total > 0 else 1

    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
