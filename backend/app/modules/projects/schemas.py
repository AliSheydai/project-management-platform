import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.permissions import ProjectRole
from app.modules.users.schemas import UserResponse


class ProjectBase(BaseModel):
    """Base schema for project fields."""

    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=2000)


class ProjectCreate(ProjectBase):
    """Payload for creating a new project."""

    pass


class ProjectUpdate(BaseModel):
    """Payload for updating project details."""

    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    is_archived: bool | None = None


class ProjectMemberResponse(BaseModel):
    """Member profile within a project."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    role: ProjectRole
    user: UserResponse
    created_at: datetime
    updated_at: datetime


class ProjectResponse(ProjectBase):
    """Project summary representation."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    current_user_role: ProjectRole | None = None
    members_count: int = 0


class ProjectDetailResponse(ProjectResponse):
    """Detailed project representation with owner and members list."""

    owner: UserResponse
    members: list[ProjectMemberResponse] = []


class ProjectListResponse(BaseModel):
    """Paginated list of projects."""

    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ProjectMemberAddRequest(BaseModel):
    """Payload for inviting/adding a member to a project."""

    email: EmailStr | None = None
    user_id: uuid.UUID | None = None
    role: ProjectRole = ProjectRole.MEMBER


class ProjectMemberRoleUpdateRequest(BaseModel):
    """Payload for changing a project member's role."""

    role: ProjectRole
