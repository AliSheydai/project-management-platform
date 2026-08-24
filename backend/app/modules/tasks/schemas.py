import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.tasks.models import TaskPriority, TaskStatus
from app.modules.users.schemas import UserResponse


class TaskBase(BaseModel):
    """Base schema for task attributes."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None


class TaskCreate(TaskBase):
    """Payload for creating a new task."""

    assignee_id: uuid.UUID | None = None
    position: float | None = None


class TaskUpdate(BaseModel):
    """Payload for updating an existing task."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: uuid.UUID | None = None
    unassign: bool = False
    due_date: datetime | None = None
    clear_due_date: bool = False
    position: float | None = None


class TaskResponse(TaskBase):
    """Public representation of a task."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    creator_id: uuid.UUID
    assignee_id: uuid.UUID | None = None
    position: float
    created_at: datetime
    updated_at: datetime
    creator: UserResponse
    assignee: UserResponse | None = None


class TaskListResponse(BaseModel):
    """Paginated list of tasks."""

    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
    pages: int


class TaskReorderRequest(BaseModel):
    """Payload for moving/reordering a task on a Kanban or list view."""

    position: float
    status: TaskStatus | None = None
