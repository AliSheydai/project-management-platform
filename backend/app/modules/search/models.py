import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.models import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.modules.projects.models import Project
    from app.modules.users.models import User


class SavedView(Base, UUIDMixin, TimestampMixin):
    """User-saved search and filter view configuration."""

    __tablename__ = "saved_views"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    filters: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
    )
    project: Mapped["Project | None"] = relationship(
        "Project",
    )

    def __init__(self, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = uuid.uuid4()
        if "filters" not in kwargs:
            kwargs["filters"] = {}
        if "is_default" not in kwargs:
            kwargs["is_default"] = False
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<SavedView id={self.id} name='{self.name}' user_id={self.user_id}>"
