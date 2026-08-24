import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.modules.tasks.schemas import TaskResponse


class SearchFacetsResponse(BaseModel):
    """Aggregated facet metrics for search results."""

    status_counts: dict[str, int]
    priority_counts: dict[str, int]


class TaskSearchResponse(BaseModel):
    """Paginated search response with faceted metadata."""

    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
    pages: int
    facets: SearchFacetsResponse


class SavedViewCreate(BaseModel):
    """Request payload to create a saved search view."""

    name: str = Field(..., min_length=1, max_length=100)
    project_id: uuid.UUID | None = None
    filters: dict[str, Any] = Field(default_factory=dict)
    is_default: bool = False


class SavedViewUpdate(BaseModel):
    """Request payload to update an existing saved search view."""

    name: str | None = Field(None, min_length=1, max_length=100)
    filters: dict[str, Any] | None = None
    is_default: bool | None = None


class SavedViewResponse(BaseModel):
    """Response payload for a saved search view."""

    id: uuid.UUID
    user_id: uuid.UUID
    project_id: uuid.UUID | None
    name: str
    filters: dict[str, Any]
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SavedViewListResponse(BaseModel):
    """Response payload for a list of saved views."""

    items: list[SavedViewResponse]
    total: int
