import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LabelBase(BaseModel):
    """Base schema for label attributes."""

    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#6B7280", max_length=20)
    description: str | None = Field(default=None, max_length=200)


class LabelCreate(LabelBase):
    """Payload for creating a project label."""

    pass


class LabelUpdate(BaseModel):
    """Payload for updating a project label."""

    name: str | None = Field(default=None, min_length=1, max_length=50)
    color: str | None = Field(default=None, max_length=20)
    description: str | None = Field(default=None, max_length=200)


class LabelResponse(LabelBase):
    """Public representation of a label."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class LabelListResponse(BaseModel):
    """List of labels within a project."""

    items: list[LabelResponse]
    total: int
