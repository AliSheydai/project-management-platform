import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.users.schemas import UserResponse


class AttachmentResponse(BaseModel):
    """Schema for returning file attachment metadata."""

    id: uuid.UUID
    task_id: uuid.UUID
    uploader_id: uuid.UUID
    file_name: str
    file_size: int
    content_type: str
    created_at: datetime
    uploader: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class AttachmentListResponse(BaseModel):
    """Schema for paginated/listed attachments on a task."""

    items: list[AttachmentResponse]
    total: int
