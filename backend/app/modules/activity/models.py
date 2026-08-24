import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.models import UUIDMixin

if TYPE_CHECKING:
    from app.modules.projects.models import Project
    from app.modules.tasks.models import Task
    from app.modules.users.models import User


class ActivityAction(StrEnum):
    """Categorized activity actions."""

    # Project Actions
    PROJECT_CREATED = "project:created"
    PROJECT_UPDATED = "project:updated"
    PROJECT_ARCHIVED = "project:archived"

    # Member Actions
    MEMBER_ADDED = "member:added"
    MEMBER_REMOVED = "member:removed"
    MEMBER_ROLE_UPDATED = "member:role_updated"

    # Task Actions
    TASK_CREATED = "task:created"
    TASK_UPDATED = "task:updated"
    TASK_DELETED = "task:deleted"
    TASK_STATUS_CHANGED = "task:status_changed"
    TASK_ASSIGNED = "task:assigned"
    TASK_REORDERED = "task:reordered"

    # Comment Actions
    COMMENT_ADDED = "comment:added"
    COMMENT_DELETED = "comment:deleted"

    # Attachment Actions
    ATTACHMENT_ADDED = "attachment:added"
    ATTACHMENT_DELETED = "attachment:deleted"


class ActivityLog(Base, UUIDMixin):
    """Audit log entry tracking modifications across the workspace."""

    __tablename__ = "activity_logs"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        index=True,
    )
    details: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="activity_logs",
    )
    task: Mapped["Task | None"] = relationship(
        "Task",
        back_populates="activity_logs",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="activity_logs",
    )

    def __init__(self, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = uuid.uuid4()
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<ActivityLog id={self.id} action={self.action} user_id={self.user_id}>"
