import uuid

import pytest

from app.core.exceptions import ForbiddenException
from app.core.permissions import Permission, ProjectRole
from app.modules.projects.dependencies import (
    require_project_permission,
    require_project_role,
    require_superuser,
)
from app.modules.projects.models import ProjectMember
from app.modules.users.models import User


@pytest.mark.asyncio
async def test_require_project_permission_granted() -> None:
    """Test require_project_permission allows action when user role has permission."""
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email="owner@example.com",
        password_hash="hash",
        first_name="Project",
        last_name="Owner",
    )
    member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=ProjectRole.OWNER,
    )

    dep = require_project_permission(Permission.PROJECT_DELETE)
    result = await dep(member=member, current_user=user)
    assert result == member


@pytest.mark.asyncio
async def test_require_project_permission_denied() -> None:
    """Test require_project_permission raises ForbiddenException if denied."""
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email="viewer@example.com",
        password_hash="hash",
        first_name="Project",
        last_name="Viewer",
    )
    member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=ProjectRole.VIEWER,
    )

    dep = require_project_permission(Permission.TASK_CREATE)
    with pytest.raises(ForbiddenException) as exc_info:
        await dep(member=member, current_user=user)

    assert "permission" in exc_info.value.message.lower()


@pytest.mark.asyncio
async def test_require_project_role_granted_and_denied() -> None:
    """Test require_project_role enforces role hierarchy."""
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email="admin@example.com",
        password_hash="hash",
        first_name="Project",
        last_name="Admin",
    )
    admin_member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=ProjectRole.ADMIN,
    )

    # Admin satisfies MEMBER requirement
    dep_member = require_project_role(ProjectRole.MEMBER)
    assert await dep_member(member=admin_member, current_user=user) == admin_member

    # Admin does NOT satisfy OWNER requirement
    dep_owner = require_project_role(ProjectRole.OWNER)
    with pytest.raises(ForbiddenException) as exc_info:
        await dep_owner(member=admin_member, current_user=user)

    assert "minimum" in exc_info.value.message.lower()


@pytest.mark.asyncio
async def test_superuser_bypass() -> None:
    """Test that platform superusers bypass project role and permission checks."""
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()
    superuser = User(
        id=user_id,
        email="super@example.com",
        password_hash="hash",
        first_name="Super",
        last_name="User",
        is_superuser=True,
    )
    viewer_member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=ProjectRole.VIEWER,
    )

    # Superuser can perform delete even if member role is VIEWER
    dep = require_project_permission(Permission.PROJECT_DELETE)
    result = await dep(member=viewer_member, current_user=superuser)
    assert result == viewer_member


@pytest.mark.asyncio
async def test_require_superuser_dependency() -> None:
    """Test require_superuser dependency validation."""
    normal_user = User(
        email="normal@example.com",
        password_hash="hash",
        first_name="Normal",
        last_name="User",
        is_superuser=False,
    )
    super_user = User(
        email="super@example.com",
        password_hash="hash",
        first_name="Super",
        last_name="User",
        is_superuser=True,
    )

    with pytest.raises(ForbiddenException):
        await require_superuser(current_user=normal_user)

    assert await require_superuser(current_user=super_user) == super_user
