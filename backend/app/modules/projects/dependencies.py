import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.permissions import (
    Permission,
    ProjectRole,
    has_permission,
    is_role_higher_or_equal,
)
from app.modules.auth.dependencies import CurrentActiveUserDep
from app.modules.projects.models import Project, ProjectMember
from app.modules.users.models import User


async def get_project_member(
    project_id: Annotated[uuid.UUID, Path(description="UUID of the target project")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectMember:
    """Retrieve membership and RBAC role of current user in the requested project."""
    # First verify project exists
    project_stmt = select(Project).where(Project.id == project_id)
    project_res = await db.execute(project_stmt)
    project = project_res.scalar_one_or_none()
    if project is None:
        raise NotFoundException(message="Project not found")

    # Fetch member association
    stmt = (
        select(ProjectMember)
        .options(selectinload(ProjectMember.project), selectinload(ProjectMember.user))
        .where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()

    if member is None:
        # If user is platform superuser, grant full synthesized OWNER access
        if current_user.is_superuser:
            return ProjectMember(
                project_id=project_id,
                user_id=current_user.id,
                role=ProjectRole.OWNER,
            )
        raise ForbiddenException(message="You are not a member of this project")

    return member


def require_project_permission(
    permission: Permission,
) -> Callable[..., ProjectMember]:
    """Dependency factory ensuring user has the required permission in the project."""

    async def dependency(
        member: Annotated[ProjectMember, Depends(get_project_member)],
        current_user: CurrentActiveUserDep,
    ) -> ProjectMember:
        if current_user.is_superuser:
            return member

        if not has_permission(member.role, permission):
            raise ForbiddenException(
                message=(
                    f"Action requires '{permission.value}' permission, "
                    f"but your project role is '{member.role.value}'."
                )
            )
        return member

    return dependency


def require_project_role(
    min_role: ProjectRole,
) -> Callable[..., ProjectMember]:
    """Dependency factory ensuring user has the minimum required project role."""

    async def dependency(
        member: Annotated[ProjectMember, Depends(get_project_member)],
        current_user: CurrentActiveUserDep,
    ) -> ProjectMember:
        if current_user.is_superuser:
            return member

        if not is_role_higher_or_equal(member.role, min_role):
            raise ForbiddenException(
                message=(
                    f"Action requires minimum '{min_role.value}' role, "
                    f"but your project role is '{member.role.value}'."
                )
            )
        return member

    return dependency


async def require_superuser(
    current_user: CurrentActiveUserDep,
) -> User:
    """Verify that authenticated user has platform superuser privileges."""
    if not current_user.is_superuser:
        raise ForbiddenException(message="Platform superuser privileges required")
    return current_user
