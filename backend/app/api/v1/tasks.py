import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenException
from app.core.permissions import Permission, has_permission
from app.modules.auth.dependencies import CurrentActiveUserDep
from app.modules.projects.dependencies import (
    get_project_member,
    require_project_permission,
)
from app.modules.projects.models import ProjectMember
from app.modules.tasks.models import TaskPriority, TaskStatus
from app.modules.tasks.schemas import (
    TaskCreate,
    TaskListResponse,
    TaskReorderRequest,
    TaskResponse,
    TaskUpdate,
)
from app.modules.tasks.service import (
    create_task,
    delete_task,
    get_task_by_id,
    list_project_tasks,
    reorder_task,
    update_task,
)

router = APIRouter(tags=["Tasks"])


# 1. Project-scoped task endpoints
@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a task in the project. Requires TASK_CREATE permission.",
)
async def create_project_task(
    project_id: Annotated[uuid.UUID, Path(description="Project UUID")],
    task_in: TaskCreate,
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    _member: Annotated[
        ProjectMember, Depends(require_project_permission(Permission.TASK_CREATE))
    ],
) -> TaskResponse:
    """Create a new task in the specified project."""
    return await create_task(db, project_id, current_user, task_in)


@router.get(
    "/projects/{project_id}/tasks",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="List and filter project tasks",
    description="Retrieve paginated tasks with filtering and sorting support.",
)
async def list_tasks(
    project_id: Annotated[uuid.UUID, Path(description="Project UUID")],
    _current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    _member: Annotated[
        ProjectMember, Depends(require_project_permission(Permission.PROJECT_VIEW))
    ],
    task_status: Annotated[
        TaskStatus | None, Query(alias="status", description="Filter by status")
    ] = None,
    priority: Annotated[
        TaskPriority | None, Query(description="Filter by priority")
    ] = None,
    assignee_id: Annotated[
        uuid.UUID | None, Query(description="Filter by assignee UUID")
    ] = None,
    unassigned: Annotated[
        bool, Query(description="Filter unassigned tasks only")
    ] = False,
    label_id: Annotated[
        uuid.UUID | None, Query(description="Filter by attached label UUID")
    ] = None,
    q: Annotated[
        str | None, Query(description="Search keyword in title or description")
    ] = None,
    due_date_from: Annotated[
        datetime | None, Query(description="Filter due date from (ISO-8601)")
    ] = None,
    due_date_to: Annotated[
        datetime | None, Query(description="Filter due date to (ISO-8601)")
    ] = None,
    sort_by: Annotated[
        str,
        Query(description="Sort column (position, created_at, due_date, priority)"),
    ] = "position",
    order: Annotated[
        str, Query(pattern="^(asc|desc)$", description="Sort order (asc or desc)")
    ] = "asc",
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 50,
) -> TaskListResponse:
    """List and filter tasks for a given project."""
    return await list_project_tasks(
        db,
        project_id,
        status=task_status,
        priority=priority,
        assignee_id=assignee_id,
        unassigned=unassigned,
        label_id=label_id,
        query=q,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )


# 2. Direct task-scoped endpoints
@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get task details",
    description="Retrieve task by UUID. Caller must be a member of the project.",
)
async def get_task(
    task_id: Annotated[uuid.UUID, Path(description="Task UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    """Retrieve full task details."""
    task = await get_task_by_id(db, task_id)
    # Check user project membership
    await get_project_member(task.project_id, current_user, db)
    return task


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update task",
    description="Update task fields. Requires TASK_EDIT permission or task assignment.",
)
async def patch_task(
    task_id: Annotated[uuid.UUID, Path(description="Task UUID")],
    task_in: TaskUpdate,
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    """Update task metadata, status, priority, or assignee."""
    task = await get_task_by_id(db, task_id)
    member = await get_project_member(task.project_id, current_user, db)

    # Permission check: OWNER/ADMIN, or creator/assignee MEMBER
    if not current_user.is_superuser:
        if not has_permission(member.role, Permission.TASK_EDIT):
            if current_user.id not in (task.creator_id, task.assignee_id):
                raise ForbiddenException(
                    message="You do not have permission to edit this task."
                )

    return await update_task(db, task, task_in, actor_id=current_user.id)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Permanently delete a task. Requires TASK_DELETE permission.",
)
async def remove_task(
    task_id: Annotated[uuid.UUID, Path(description="Task UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete task from project."""
    task = await get_task_by_id(db, task_id)
    member = await get_project_member(task.project_id, current_user, db)

    if not current_user.is_superuser:
        if not has_permission(member.role, Permission.TASK_DELETE):
            raise ForbiddenException(
                message="Action requires TASK_DELETE permission (OWNER or ADMIN)."
            )

    await delete_task(db, task, actor_id=current_user.id)


@router.patch(
    "/tasks/{task_id}/reorder",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Reorder task on board",
    description="Update task position and optional status for Kanban ordering.",
)
async def reorder_board_task(
    task_id: Annotated[uuid.UUID, Path(description="Task UUID")],
    reorder_in: TaskReorderRequest,
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    """Update board position or column status of a task."""
    task = await get_task_by_id(db, task_id)
    member = await get_project_member(task.project_id, current_user, db)

    if not current_user.is_superuser:
        if not has_permission(member.role, Permission.TASK_EDIT):
            raise ForbiddenException(
                message="Action requires TASK_EDIT permission to reorder tasks."
            )

    return await reorder_task(db, task, reorder_in, actor_id=current_user.id)
