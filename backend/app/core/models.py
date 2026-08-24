"""Import all models here for Alembic and metadata reflection."""

from app.core.database import Base
from app.core.permissions import ProjectRole
from app.modules.activity.models import ActivityAction, ActivityLog
from app.modules.attachments.models import Attachment
from app.modules.auth.models import RefreshToken
from app.modules.comments.models import Comment
from app.modules.labels.models import Label, task_labels
from app.modules.projects.models import Project, ProjectMember
from app.modules.tasks.models import Task, TaskPriority, TaskStatus
from app.modules.users.models import User

__all__ = [
    "Base",
    "User",
    "RefreshToken",
    "Project",
    "ProjectMember",
    "ProjectRole",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "Comment",
    "ActivityLog",
    "ActivityAction",
    "Label",
    "task_labels",
    "Attachment",
]
