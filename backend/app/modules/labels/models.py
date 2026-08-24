import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Table,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.models import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.modules.projects.models import Project
    from app.modules.tasks.models import Task


task_labels = Table(
    "task_labels",
    Base.metadata,
    Column(
        "task_id",
        Uuid(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
    Column(
        "label_id",
        Uuid(as_uuid=True),
        ForeignKey("labels.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)


class Label(Base, UUIDMixin, TimestampMixin):
    """Label entity for tagging and categorizing tasks within a project."""

    __tablename__ = "labels"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_project_label_name"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    color: Mapped[str] = mapped_column(
        String(20),
        default="#6B7280",
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="labels",
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        secondary=task_labels,
        back_populates="labels",
    )

    def __init__(self, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = uuid.uuid4()
        if "color" not in kwargs:
            kwargs["color"] = "#6B7280"
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Label id={self.id} name={self.name!r} color={self.color}>"
