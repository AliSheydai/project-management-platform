import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.modules.users.schemas import UserResponse


class ActivityLogResponse(BaseModel):
    """Public representation of an activity audit log."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    task_id: uuid.UUID | None = None
    user_id: uuid.UUID
    action: str
    entity_type: str
    entity_id: uuid.UUID
    details: dict[str, Any] | None = None
    created_at: datetime
    user: UserResponse


class ActivityListResponse(BaseModel):
    """Paginated list of activity logs."""

    items: list[ActivityLogResponse]
    total: int
    page: int
    page_size: int
    pages: int
