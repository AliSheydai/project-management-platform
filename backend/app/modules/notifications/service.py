import math
import re
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.modules.notifications.models import Notification, NotificationType
from app.modules.notifications.schemas import (
    NotificationListResponse,
    NotificationResponse,
)
from app.modules.projects.models import ProjectMember
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse


async def create_notification(
    db: AsyncSession,
    user_id: uuid.UUID,
    actor_id: uuid.UUID | None,
    notification_type: NotificationType | str,
    title: str,
    message: str,
    entity_type: str,
    entity_id: uuid.UUID,
    payload: dict[str, Any] | None = None,
) -> Notification | None:
    """Create a notification if recipient is not the actor."""
    if actor_id is not None and user_id == actor_id:
        return None

    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        type=str(notification_type),
        title=title,
        message=message,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
    )
    db.add(notification)
    return notification


async def parse_and_notify_mentions(
    db: AsyncSession,
    text: str,
    project_id: uuid.UUID,
    actor: User,
    entity_type: str,
    entity_id: uuid.UUID,
    title: str,
    payload: dict[str, Any] | None = None,
) -> list[Notification]:
    """Find mentioned users by @email or @username and dispatch notifications."""
    if not text:
        return []

    # Find @mentions (e.g. @user@example.com or @username)
    mention_pattern = (
        r"@([a-zA-Z0-9_\.\-]+@[a-zA-Z0-9_\.\-]+\.[a-zA-Z0-9]+|[a-zA-Z0-9_\.\-]+)"
    )
    raw_handles = re.findall(mention_pattern, text)
    if not raw_handles:
        return []

    # Get active project members
    stmt = (
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(ProjectMember.project_id == project_id)
    )
    res = await db.execute(stmt)
    members = res.scalars().all()

    created_notifs = []
    notified_user_ids = set()

    for member in members:
        user = member.user
        if not user.is_active or user.id == actor.id:
            continue

        # Check if handle matches email, first name, last name, or full name
        for handle in raw_handles:
            h_lower = handle.lower()
            if (
                h_lower == user.email.lower()
                or h_lower == user.first_name.lower()
                or h_lower == user.last_name.lower()
                or h_lower == f"{user.first_name.lower()}_{user.last_name.lower()}"
            ):
                if user.id not in notified_user_ids:
                    notified_user_ids.add(user.id)
                    notif = await create_notification(
                        db=db,
                        user_id=user.id,
                        actor_id=actor.id,
                        notification_type=NotificationType.USER_MENTIONED,
                        title=title,
                        message=f"{actor.full_name} mentioned you: {text[:100]}",
                        entity_type=entity_type,
                        entity_id=entity_id,
                        payload=payload,
                    )
                    if notif:
                        created_notifs.append(notif)
                break

    return created_notifs


async def list_user_notifications(
    db: AsyncSession,
    user_id: uuid.UUID,
    unread_only: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> NotificationListResponse:
    """Retrieve paginated notifications for the user."""
    base_filter = [Notification.user_id == user_id]
    if unread_only:
        base_filter.append(Notification.is_read.is_(False))

    # Total Count
    count_stmt = select(func.count(Notification.id)).where(*base_filter)
    count_res = await db.execute(count_stmt)
    total = count_res.scalar() or 0

    # Unread Count
    unread_stmt = select(func.count(Notification.id)).where(
        Notification.user_id == user_id,
        Notification.is_read.is_(False),
    )
    unread_res = await db.execute(unread_stmt)
    unread_count = unread_res.scalar() or 0

    # Query items
    offset = (page - 1) * page_size
    stmt = (
        select(Notification)
        .options(selectinload(Notification.actor))
        .where(*base_filter)
        .order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    notifications = result.scalars().all()

    items = [
        NotificationResponse(
            id=n.id,
            user_id=n.user_id,
            actor_id=n.actor_id,
            type=n.type,
            title=n.title,
            message=n.message,
            entity_type=n.entity_type,
            entity_id=n.entity_id,
            payload=n.payload,
            is_read=n.is_read,
            read_at=n.read_at,
            created_at=n.created_at,
            actor=UserResponse.model_validate(n.actor) if n.actor else None,
        )
        for n in notifications
    ]

    pages = math.ceil(total / page_size) if total > 0 else 1

    return NotificationListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        unread_count=unread_count,
    )


async def get_unread_notification_count(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> int:
    """Retrieve total count of unread notifications for a user."""
    stmt = select(func.count(Notification.id)).where(
        Notification.user_id == user_id,
        Notification.is_read.is_(False),
    )
    res = await db.execute(stmt)
    return res.scalar() or 0


async def mark_notification_read(
    db: AsyncSession,
    notification_id: uuid.UUID,
    user_id: uuid.UUID,
) -> NotificationResponse:
    """Mark a single notification as read."""
    stmt = (
        select(Notification)
        .options(selectinload(Notification.actor))
        .where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )
    res = await db.execute(stmt)
    notif = res.scalar_one_or_none()
    if not notif:
        raise NotFoundException(message="Notification not found")

    if not notif.is_read:
        notif.is_read = True
        notif.read_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(notif)

    return NotificationResponse(
        id=notif.id,
        user_id=notif.user_id,
        actor_id=notif.actor_id,
        type=notif.type,
        title=notif.title,
        message=notif.message,
        entity_type=notif.entity_type,
        entity_id=notif.entity_id,
        payload=notif.payload,
        is_read=notif.is_read,
        read_at=notif.read_at,
        created_at=notif.created_at,
        actor=UserResponse.model_validate(notif.actor) if notif.actor else None,
    )


async def mark_all_notifications_read(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> int:
    """Mark all unread notifications for user as read."""
    now = datetime.now(UTC)
    stmt = (
        update(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .values(is_read=True, read_at=now)
    )
    res = await db.execute(stmt)
    await db.commit()
    return res.rowcount or 0


async def delete_notification(
    db: AsyncSession,
    notification_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    """Permanently delete a notification owned by user."""
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == user_id,
    )
    res = await db.execute(stmt)
    notif = res.scalar_one_or_none()
    if not notif:
        raise NotFoundException(message="Notification not found")

    await db.delete(notif)
    await db.commit()
