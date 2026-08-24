import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentActiveUserDep
from app.modules.notifications.schemas import (
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.modules.notifications.service import (
    delete_notification,
    get_unread_notification_count,
    list_user_notifications,
    mark_all_notifications_read,
    mark_notification_read,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List notifications",
    description="Retrieve paginated in-app notifications for the authenticated user.",
)
async def get_notifications(
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    unread_only: Annotated[
        bool, Query(description="Filter unread notifications only")
    ] = False,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
) -> NotificationListResponse:
    """Retrieve notifications feed."""
    return await list_user_notifications(
        db=db,
        user_id=current_user.id,
        unread_only=unread_only,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/unread-count",
    response_model=UnreadCountResponse,
    status_code=status.HTTP_200_OK,
    summary="Get unread notification count",
    description="Get the total count of unread notifications for badge counters.",
)
async def get_unread_count(
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UnreadCountResponse:
    """Retrieve count of unread notifications."""
    count = await get_unread_notification_count(db, current_user.id)
    return UnreadCountResponse(unread_count=count)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark notification as read",
    description="Mark a specific notification as read.",
)
async def mark_single_read(
    notification_id: Annotated[uuid.UUID, Path(description="Notification UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> NotificationResponse:
    """Mark a notification as read."""
    return await mark_notification_read(db, notification_id, current_user.id)


@router.post(
    "/mark-all-read",
    status_code=status.HTTP_200_OK,
    summary="Mark all notifications as read",
    description="Mark all unread notifications as read for current user.",
)
async def mark_all_read(
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Mark all notifications as read."""
    updated = await mark_all_notifications_read(db, current_user.id)
    return {"message": "All notifications marked as read", "updated_count": updated}


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete notification",
    description="Permanently delete a notification.",
)
async def remove_notification(
    notification_id: Annotated[uuid.UUID, Path(description="Notification UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a notification."""
    await delete_notification(db, notification_id, current_user.id)
