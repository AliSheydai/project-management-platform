import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.users.schemas import UserResponse


class CommentBase(BaseModel):
    """Base schema for comment content."""

    content: str = Field(..., min_length=1, max_length=5000)


class CommentCreate(CommentBase):
    """Payload for creating a task comment."""

    pass


class CommentUpdate(CommentBase):
    """Payload for editing a task comment."""

    pass


class CommentResponse(CommentBase):
    """Public representation of a comment."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    author: UserResponse


class CommentListResponse(BaseModel):
    """Paginated list of task comments."""

    items: list[CommentResponse]
    total: int
    page: int
    page_size: int
    pages: int
