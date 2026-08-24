import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import Permission
from app.modules.auth.dependencies import CurrentActiveUserDep
from app.modules.auth.schemas import MessageResponse
from app.modules.projects.dependencies import require_project_permission
from app.modules.projects.models import ProjectMember
from app.modules.projects.schemas import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectMemberAddRequest,
    ProjectMemberResponse,
    ProjectMemberRoleUpdateRequest,
    ProjectResponse,
    ProjectUpdate,
)
from app.modules.projects.service import (
    add_project_member,
    create_project,
    delete_project,
    get_project_detail,
    list_project_members,
    list_user_projects,
    remove_project_member,
    update_project,
    update_project_member_role,
)
from app.modules.users.schemas import UserResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Create a project workspace and assign creator as initial OWNER.",
)
async def create_new_project(
    project_in: ProjectCreate,
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectResponse:
    """Create project and assign creator as OWNER."""
    proj = await create_project(db, current_user, project_in)
    return ProjectResponse(
        id=proj.id,
        name=proj.name,
        description=proj.description,
        owner_id=proj.owner_id,
        is_archived=proj.is_archived,
        created_at=proj.created_at,
        updated_at=proj.updated_at,
        current_user_role=proj.members[0].role if proj.members else None,
        members_count=1,
    )


@router.get(
    "",
    response_model=ProjectListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user projects",
    description="List and paginate all projects for the authenticated user.",
)
async def list_projects(
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    q: Annotated[
        str | None, Query(description="Search keyword (name or description)")
    ] = None,
    is_archived: Annotated[
        bool | None, Query(description="Filter by archived status")
    ] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
) -> ProjectListResponse:
    """Retrieve paginated projects for current user."""
    return await list_user_projects(
        db,
        current_user,
        query=q,
        is_archived=is_archived,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project details",
    description="Retrieve full project details, owner profile, and member list.",
)
async def get_project(
    project_id: Annotated[uuid.UUID, Path(description="Project UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    _member: Annotated[
        ProjectMember, Depends(require_project_permission(Permission.PROJECT_VIEW))
    ],
) -> ProjectDetailResponse:
    """Retrieve detailed project information."""
    return await get_project_detail(db, project_id, current_user)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update project details",
    description="Update project details. Requires PROJECT_EDIT permission.",
)
async def patch_project(
    project_in: ProjectUpdate,
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    member: Annotated[
        ProjectMember, Depends(require_project_permission(Permission.PROJECT_EDIT))
    ],
) -> ProjectResponse:
    """Update project metadata."""
    updated = await update_project(db, member.project, project_in)
    return ProjectResponse(
        id=updated.id,
        name=updated.name,
        description=updated.description,
        owner_id=updated.owner_id,
        is_archived=updated.is_archived,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
        current_user_role=member.role,
        members_count=len(updated.members) if updated.members else 1,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Delete project workspace. Requires PROJECT_DELETE permission.",
)
async def remove_project(
    _current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    member: Annotated[
        ProjectMember, Depends(require_project_permission(Permission.PROJECT_DELETE))
    ],
) -> None:
    """Permanently delete project."""
    await delete_project(db, member.project)


@router.get(
    "/{project_id}/members",
    response_model=list[ProjectMemberResponse],
    status_code=status.HTTP_200_OK,
    summary="List project members",
    description="Retrieve all project members. Requires PROJECT_VIEW permission.",
)
async def get_members(
    project_id: Annotated[uuid.UUID, Path(description="Project UUID")],
    _current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    _member: Annotated[
        ProjectMember, Depends(require_project_permission(Permission.PROJECT_VIEW))
    ],
) -> list[ProjectMemberResponse]:
    """List members of the project."""
    members = await list_project_members(db, project_id)
    return [
        ProjectMemberResponse(
            id=m.id,
            project_id=m.project_id,
            user_id=m.user_id,
            role=m.role,
            user=UserResponse.model_validate(m.user),
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        for m in members
    ]


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add / invite member to project",
    description="Add a registered user to project. Requires MEMBER_INVITE permission.",
)
async def add_member(
    member_in: ProjectMemberAddRequest,
    _current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    member: Annotated[
        ProjectMember, Depends(require_project_permission(Permission.MEMBER_INVITE))
    ],
) -> ProjectMemberResponse:
    """Add member to project."""
    new_member = await add_project_member(db, member.project, member_in)
    return ProjectMemberResponse(
        id=new_member.id,
        project_id=new_member.project_id,
        user_id=new_member.user_id,
        role=new_member.role,
        user=UserResponse.model_validate(new_member.user),
        created_at=new_member.created_at,
        updated_at=new_member.updated_at,
    )


@router.patch(
    "/{project_id}/members/{user_id}",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Update project member role",
    description="Update member's role. Requires MEMBER_ROLE_CHANGE permission.",
)
async def update_member_role(
    project_id: Annotated[uuid.UUID, Path(description="Project UUID")],
    user_id: Annotated[uuid.UUID, Path(description="Target User UUID")],
    role_in: ProjectMemberRoleUpdateRequest,
    _current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    _member: Annotated[
        ProjectMember,
        Depends(require_project_permission(Permission.MEMBER_ROLE_CHANGE)),
    ],
) -> ProjectMemberResponse:
    """Update member role in project."""
    updated = await update_project_member_role(db, project_id, user_id, role_in)
    return ProjectMemberResponse(
        id=updated.id,
        project_id=updated.project_id,
        user_id=updated.user_id,
        role=updated.role,
        user=UserResponse.model_validate(updated.user),
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.delete(
    "/{project_id}/members/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove member or leave project",
    description="Remove a member from the project or leave the workspace.",
)
async def remove_member(
    project_id: Annotated[uuid.UUID, Path(description="Project UUID")],
    user_id: Annotated[uuid.UUID, Path(description="Target User UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    caller_member: Annotated[
        ProjectMember, Depends(require_project_permission(Permission.PROJECT_VIEW))
    ],
) -> MessageResponse:
    """Remove member from project or leave project."""
    # If caller is removing someone else, verify MEMBER_REMOVE permission
    if current_user.id != user_id and not current_user.is_superuser:
        from app.core.permissions import has_permission

        if not has_permission(caller_member.role, Permission.MEMBER_REMOVE):
            from app.core.exceptions import ForbiddenException

            raise ForbiddenException(
                message="You do not have permission to remove members from this project"
            )

    await remove_project_member(db, project_id, user_id, current_user)
    return MessageResponse(message="Member removed successfully")
