import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.modules.users.schemas import UserResponse


class NotificationResponse(BaseModel):
    """Schema for a single notification item."""

    id: uuid.UUID
    user_id: uuid.UUID
    actor_id: uuid.UUID | None = None
    type: str
    title: str
    message: str
    entity_type: str
    entity_id: uuid.UUID
    payload: dict[str, Any] | None = None
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime
    actor: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Paginated list of notifications with unread counter."""

    items: list[NotificationResponse]
    total: int
    page: int
    page_size: int
    pages: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    """Response payload for total unread notifications count."""

    unread_count: int
