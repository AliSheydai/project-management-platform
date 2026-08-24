import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.models import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.modules.tasks.models import Task
    from app.modules.users.models import User


class Comment(Base, UUIDMixin, TimestampMixin):
    """Comment entity representing discussion and feedback on a task."""

    __tablename__ = "comments"

    task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Relationships
    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="comments",
    )
    author: Mapped["User"] = relationship(
        "User",
        back_populates="comments",
    )

    def __init__(self, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = uuid.uuid4()
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return (
            f"<Comment id={self.id} task_id={self.task_id} author_id={self.author_id}>"
        )
