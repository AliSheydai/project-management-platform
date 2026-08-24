import math
import uuid
from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestException, NotFoundException
from app.modules.projects.models import ProjectMember
from app.modules.tasks.models import Task, TaskPriority, TaskStatus
from app.modules.tasks.schemas import (
    TaskCreate,
    TaskListResponse,
    TaskReorderRequest,
    TaskResponse,
    TaskUpdate,
)
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse


async def validate_assignee_membership(
    db: AsyncSession,
    project_id: uuid.UUID,
    assignee_id: uuid.UUID,
) -> User:
    """Validate that the assignee is an active member of the specified project."""
    stmt = (
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == assignee_id,
        )
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()

    if member is None:
        raise BadRequestException(
            message="Assignee must be an active member of this project"
        )
    if not member.user.is_active:
        raise BadRequestException(message="Assignee user account is deactivated")
    return member.user


async def create_task(
    db: AsyncSession,
    project_id: uuid.UUID,
    creator: User,
    task_in: TaskCreate,
) -> Task:
    """Create a new task within a project."""
    if task_in.assignee_id:
        await validate_assignee_membership(db, project_id, task_in.assignee_id)

    # Determine initial board position
    if task_in.position is not None:
        position = task_in.position
    else:
        pos_stmt = select(func.max(Task.position)).where(
            Task.project_id == project_id,
            Task.status == task_in.status,
        )
        pos_res = await db.execute(pos_stmt)
        max_pos = pos_res.scalar()
        position = (max_pos + 1000.0) if max_pos is not None else 1000.0

    task = Task(
        project_id=project_id,
        title=task_in.title.strip(),
        description=task_in.description.strip() if task_in.description else None,
        status=task_in.status,
        priority=task_in.priority,
        assignee_id=task_in.assignee_id,
        creator_id=creator.id,
        due_date=task_in.due_date,
        position=position,
    )
    db.add(task)
    await db.commit()

    # Reload with eager loaded relationships
    reload_stmt = (
        select(Task)
        .options(selectinload(Task.creator), selectinload(Task.assignee))
        .where(Task.id == task.id)
    )
    res = await db.execute(reload_stmt)
    return res.scalar_one()


async def list_project_tasks(
    db: AsyncSession,
    project_id: uuid.UUID,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee_id: uuid.UUID | None = None,
    unassigned: bool = False,
    query: str | None = None,
    due_date_from: datetime | None = None,
    due_date_to: datetime | None = None,
    sort_by: str = "position",
    order: str = "asc",
    page: int = 1,
    page_size: int = 50,
) -> TaskListResponse:
    """Retrieve and filter tasks within a project with sorting and pagination."""
    base_filter = [Task.project_id == project_id]

    if status is not None:
        base_filter.append(Task.status == status)
    if priority is not None:
        base_filter.append(Task.priority == priority)
    if unassigned:
        base_filter.append(Task.assignee_id.is_(None))
    elif assignee_id is not None:
        base_filter.append(Task.assignee_id == assignee_id)

    if query and query.strip():
        search_pattern = f"%{query.strip()}%"
        base_filter.append(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern),
            )
        )

    if due_date_from is not None:
        base_filter.append(Task.due_date >= due_date_from)
    if due_date_to is not None:
        base_filter.append(Task.due_date <= due_date_to)

    # Count total
    count_stmt = select(func.count(Task.id)).where(*base_filter)
    count_res = await db.execute(count_stmt)
    total = count_res.scalar() or 0

    # Sort mapping
    sort_map = {
        "position": Task.position,
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
        "due_date": Task.due_date,
        "title": Task.title,
        "priority": Task.priority,
    }
    sort_col = sort_map.get(sort_by, Task.position)
    order_func = sort_col.desc() if order.lower() == "desc" else sort_col.asc()

    # Query items
    offset = (page - 1) * page_size
    stmt = (
        select(Task)
        .options(selectinload(Task.creator), selectinload(Task.assignee))
        .where(*base_filter)
        .order_by(order_func, Task.created_at.asc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    items = [
        TaskResponse(
            id=t.id,
            project_id=t.project_id,
            title=t.title,
            description=t.description,
            status=t.status,
            priority=t.priority,
            assignee_id=t.assignee_id,
            creator_id=t.creator_id,
            due_date=t.due_date,
            position=t.position,
            created_at=t.created_at,
            updated_at=t.updated_at,
            creator=UserResponse.model_validate(t.creator),
            assignee=UserResponse.model_validate(t.assignee) if t.assignee else None,
        )
        for t in tasks
    ]

    pages = math.ceil(total / page_size) if total > 0 else 1

    return TaskListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


async def get_task_by_id(
    db: AsyncSession,
    task_id: uuid.UUID,
) -> Task:
    """Retrieve task with creator, assignee, and project loaded."""
    stmt = (
        select(Task)
        .options(
            selectinload(Task.creator),
            selectinload(Task.assignee),
            selectinload(Task.project),
        )
        .where(Task.id == task_id)
    )
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if task is None:
        raise NotFoundException(message="Task not found")
    return task


async def update_task(
    db: AsyncSession,
    task: Task,
    task_in: TaskUpdate,
) -> Task:
    """Update task fields and enforce membership validation on assignee change."""
    if task_in.title is not None:
        task.title = task_in.title.strip()
    if task_in.description is not None:
        task.description = task_in.description.strip() if task_in.description else None
    if task_in.status is not None:
        task.status = task_in.status
    if task_in.priority is not None:
        task.priority = task_in.priority

    if task_in.unassign:
        task.assignee_id = None
    elif task_in.assignee_id is not None and task_in.assignee_id != task.assignee_id:
        await validate_assignee_membership(db, task.project_id, task_in.assignee_id)
        task.assignee_id = task_in.assignee_id

    if task_in.clear_due_date:
        task.due_date = None
    elif task_in.due_date is not None:
        task.due_date = task_in.due_date

    if task_in.position is not None:
        task.position = task_in.position

    await db.commit()

    # Reload
    stmt = (
        select(Task)
        .options(selectinload(Task.creator), selectinload(Task.assignee))
        .where(Task.id == task.id)
    )
    res = await db.execute(stmt)
    return res.scalar_one()


async def delete_task(
    db: AsyncSession,
    task: Task,
) -> None:
    """Permanently delete a task."""
    await db.delete(task)
    await db.commit()


async def reorder_task(
    db: AsyncSession,
    task: Task,
    reorder_in: TaskReorderRequest,
) -> Task:
    """Update board position and workflow status of a task."""
    task.position = reorder_in.position
    if reorder_in.status is not None:
        task.status = reorder_in.status

    await db.commit()

    stmt = (
        select(Task)
        .options(selectinload(Task.creator), selectinload(Task.assignee))
        .where(Task.id == task.id)
    )
    res = await db.execute(stmt)
    return res.scalar_one()
