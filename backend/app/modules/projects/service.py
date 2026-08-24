import math
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.core.permissions import ProjectRole
from app.modules.projects.models import Project, ProjectMember
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
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse


async def create_project(
    db: AsyncSession,
    owner: User,
    project_in: ProjectCreate,
) -> Project:
    """Create a new project and add the creator as OWNER in a single transaction."""
    project = Project(
        name=project_in.name.strip(),
        description=project_in.description.strip() if project_in.description else None,
        owner_id=owner.id,
        is_archived=False,
    )
    db.add(project)
    await db.flush()

    member = ProjectMember(
        project_id=project.id,
        user_id=owner.id,
        role=ProjectRole.OWNER,
    )
    db.add(member)
    await db.commit()

    stmt = (
        select(Project)
        .options(selectinload(Project.members))
        .where(Project.id == project.id)
    )
    res = await db.execute(stmt)
    return res.scalar_one()


async def list_user_projects(
    db: AsyncSession,
    user: User,
    query: str | None = None,
    is_archived: bool | None = None,
    page: int = 1,
    page_size: int = 20,
) -> ProjectListResponse:
    """Retrieve paginated projects where the user is an active member or owner."""
    # Membership filter subquery
    if not user.is_superuser:
        member_subquery = (
            select(ProjectMember.project_id)
            .where(ProjectMember.user_id == user.id)
            .scalar_subquery()
        )
        base_filter = [Project.id.in_(member_subquery)]
    else:
        base_filter = []

    if is_archived is not None:
        base_filter.append(Project.is_archived == is_archived)

    if query and query.strip():
        search_pattern = f"%{query.strip()}%"
        base_filter.append(
            or_(
                Project.name.ilike(search_pattern),
                Project.description.ilike(search_pattern),
            )
        )

    # Count total
    count_stmt = select(func.count(Project.id)).where(*base_filter)
    count_res = await db.execute(count_stmt)
    total = count_res.scalar() or 0

    # Paginated query
    offset = (page - 1) * page_size
    stmt = (
        select(Project)
        .options(selectinload(Project.members))
        .where(*base_filter)
        .order_by(Project.updated_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    projects = result.scalars().all()

    items: list[ProjectResponse] = []
    for proj in projects:
        # Determine user's role in this project
        user_role: ProjectRole | None = None
        for m in proj.members:
            if m.user_id == user.id:
                user_role = m.role
                break
        if user_role is None and user.is_superuser:
            user_role = ProjectRole.OWNER

        items.append(
            ProjectResponse(
                id=proj.id,
                name=proj.name,
                description=proj.description,
                owner_id=proj.owner_id,
                is_archived=proj.is_archived,
                created_at=proj.created_at,
                updated_at=proj.updated_at,
                current_user_role=user_role,
                members_count=len(proj.members),
            )
        )

    pages = math.ceil(total / page_size) if total > 0 else 1

    return ProjectListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


async def get_project_detail(
    db: AsyncSession,
    project_id: uuid.UUID,
    user: User,
) -> ProjectDetailResponse:
    """Retrieve detailed project information including members and owner profile."""
    stmt = (
        select(Project)
        .options(
            selectinload(Project.owner),
            selectinload(Project.members).selectinload(ProjectMember.user),
        )
        .where(Project.id == project_id)
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if project is None:
        raise NotFoundException(message="Project not found")

    user_role: ProjectRole | None = None
    member_responses: list[ProjectMemberResponse] = []
    for m in project.members:
        if m.user_id == user.id:
            user_role = m.role
        member_responses.append(
            ProjectMemberResponse(
                id=m.id,
                project_id=m.project_id,
                user_id=m.user_id,
                role=m.role,
                user=UserResponse.model_validate(m.user),
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
        )

    if user_role is None and user.is_superuser:
        user_role = ProjectRole.OWNER

    return ProjectDetailResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        is_archived=project.is_archived,
        created_at=project.created_at,
        updated_at=project.updated_at,
        current_user_role=user_role,
        members_count=len(project.members),
        owner=UserResponse.model_validate(project.owner),
        members=member_responses,
    )


async def update_project(
    db: AsyncSession,
    project: Project,
    project_in: ProjectUpdate,
) -> Project:
    """Update project metadata."""
    if project_in.name is not None:
        project.name = project_in.name.strip()
    if project_in.description is not None:
        project.description = (
            project_in.description.strip() if project_in.description else None
        )
    if project_in.is_archived is not None:
        project.is_archived = project_in.is_archived

    await db.commit()
    stmt = (
        select(Project)
        .options(selectinload(Project.members))
        .where(Project.id == project.id)
    )
    res = await db.execute(stmt)
    return res.scalar_one()


async def delete_project(
    db: AsyncSession,
    project: Project,
) -> None:
    """Permanently delete a project and cascade deletion to its members and tasks."""
    await db.delete(project)
    await db.commit()


async def add_project_member(
    db: AsyncSession,
    project: Project,
    member_in: ProjectMemberAddRequest,
) -> ProjectMember:
    """Add or invite a registered user to a project with the designated role."""
    # Resolve target user
    if member_in.email:
        target_email = member_in.email.strip().lower()
        stmt = select(User).where(User.email == target_email)
    elif member_in.user_id:
        stmt = select(User).where(User.id == member_in.user_id)
    else:
        raise ConflictException(
            message="Either email or user_id must be provided to add a member"
        )

    result = await db.execute(stmt)
    target_user = result.scalar_one_or_none()
    if target_user is None:
        raise NotFoundException(message="User not found")

    if not target_user.is_active:
        raise ConflictException(message="User account is inactive")

    # Check for existing membership
    existing_stmt = select(ProjectMember).where(
        ProjectMember.project_id == project.id,
        ProjectMember.user_id == target_user.id,
    )
    existing_res = await db.execute(existing_stmt)
    if existing_res.scalar_one_or_none() is not None:
        raise ConflictException(message="User is already a member of this project")

    new_member = ProjectMember(
        project_id=project.id,
        user_id=target_user.id,
        role=member_in.role,
    )
    db.add(new_member)
    await db.commit()

    # Refresh with eager loaded user
    refreshed_stmt = (
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(ProjectMember.id == new_member.id)
    )
    refreshed_res = await db.execute(refreshed_stmt)
    return refreshed_res.scalar_one()


async def list_project_members(
    db: AsyncSession,
    project_id: uuid.UUID,
) -> list[ProjectMember]:
    """Retrieve all members of a project ordered by join date."""
    stmt = (
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(ProjectMember.project_id == project_id)
        .order_by(ProjectMember.created_at.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_project_member_role(
    db: AsyncSession,
    project_id: uuid.UUID,
    target_user_id: uuid.UUID,
    role_in: ProjectMemberRoleUpdateRequest,
) -> ProjectMember:
    """Update a project member's role while enforcing ownership safety."""
    stmt = (
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == target_user_id,
        )
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()
    if member is None:
        raise NotFoundException(message="Project member not found")

    # If member is currently OWNER and being downgraded, verify another OWNER exists
    if member.role == ProjectRole.OWNER and role_in.role != ProjectRole.OWNER:
        owner_count_stmt = select(func.count(ProjectMember.id)).where(
            ProjectMember.project_id == project_id,
            ProjectMember.role == ProjectRole.OWNER,
        )
        owner_count_res = await db.execute(owner_count_stmt)
        owner_count = owner_count_res.scalar() or 0
        if owner_count <= 1:
            raise ConflictException(
                message=(
                    "Cannot demote the sole project owner. "
                    "Assign another owner before changing this role."
                )
            )

    member.role = role_in.role
    await db.commit()
    await db.refresh(member)
    return member


async def remove_project_member(
    db: AsyncSession,
    project_id: uuid.UUID,
    target_user_id: uuid.UUID,
    current_user: User,
) -> None:
    """Remove a member from a project while enforcing ownership constraints."""
    stmt = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == target_user_id,
    )
    result = await db.execute(stmt)
    target_member = result.scalar_one_or_none()
    if target_member is None:
        raise NotFoundException(message="Project member not found")

    # Check sole owner constraint
    if target_member.role == ProjectRole.OWNER:
        owner_count_stmt = select(func.count(ProjectMember.id)).where(
            ProjectMember.project_id == project_id,
            ProjectMember.role == ProjectRole.OWNER,
        )
        owner_count_res = await db.execute(owner_count_stmt)
        owner_count = owner_count_res.scalar() or 0
        if owner_count <= 1:
            raise ConflictException(
                message=(
                    "Cannot remove the sole project owner. "
                    "Transfer ownership or delete the project."
                )
            )

    # If admin is removing someone else, admins cannot remove owners or other admins
    if current_user.id != target_user_id and not current_user.is_superuser:
        caller_member_stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
        caller_res = await db.execute(caller_member_stmt)
        caller_member = caller_res.scalar_one_or_none()
        if caller_member and caller_member.role == ProjectRole.ADMIN:
            if target_member.role in (ProjectRole.OWNER, ProjectRole.ADMIN):
                raise ForbiddenException(
                    message="Admins cannot remove other admins or owners."
                )

    await db.delete(target_member)
    await db.commit()
