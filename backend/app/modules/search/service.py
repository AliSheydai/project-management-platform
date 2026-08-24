import math
import uuid
from datetime import datetime

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenException, NotFoundException
from app.modules.labels.models import Label
from app.modules.labels.schemas import LabelResponse
from app.modules.projects.models import ProjectMember
from app.modules.search.models import SavedView
from app.modules.search.schemas import (
    SavedViewCreate,
    SavedViewListResponse,
    SavedViewResponse,
    SavedViewUpdate,
    SearchFacetsResponse,
    TaskSearchResponse,
)
from app.modules.tasks.models import Task, TaskPriority, TaskStatus
from app.modules.tasks.schemas import TaskResponse
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse


async def search_tasks(
    db: AsyncSession,
    current_user: User,
    project_id: uuid.UUID | None = None,
    query: str | None = None,
    statuses: list[TaskStatus] | None = None,
    priorities: list[TaskPriority] | None = None,
    assignee_id: uuid.UUID | None = None,
    creator_id: uuid.UUID | None = None,
    label_id: uuid.UUID | None = None,
    unassigned: bool = False,
    due_date_from: datetime | None = None,
    due_date_to: datetime | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> TaskSearchResponse:
    """Execute cross-project or in-project search with multi-filter combinations."""
    base_filter = []

    # Tenancy & Security Scope
    if not current_user.is_superuser:
        member_stmt = select(ProjectMember.project_id).where(
            ProjectMember.user_id == current_user.id
        )
        member_res = await db.execute(member_stmt)
        accessible_project_ids = list(member_res.scalars().all())

        if not accessible_project_ids:
            return TaskSearchResponse(
                items=[],
                total=0,
                page=page,
                page_size=page_size,
                pages=1,
                facets=SearchFacetsResponse(status_counts={}, priority_counts={}),
            )

        if project_id is not None:
            if project_id not in accessible_project_ids:
                raise ForbiddenException(
                    message="You do not have access to search within this project."
                )
            base_filter.append(Task.project_id == project_id)
        else:
            base_filter.append(Task.project_id.in_(accessible_project_ids))
    else:
        if project_id is not None:
            base_filter.append(Task.project_id == project_id)

    # Multi-term full-text search
    if query and query.strip():
        terms = query.strip().split()
        for term in terms:
            pattern = f"%{term}%"
            base_filter.append(
                or_(
                    Task.title.ilike(pattern),
                    Task.description.ilike(pattern),
                )
            )

    # Multi-value Filters
    if statuses:
        base_filter.append(Task.status.in_(statuses))
    if priorities:
        base_filter.append(Task.priority.in_(priorities))

    if unassigned:
        base_filter.append(Task.assignee_id.is_(None))
    elif assignee_id is not None:
        base_filter.append(Task.assignee_id == assignee_id)

    if creator_id is not None:
        base_filter.append(Task.creator_id == creator_id)

    if label_id is not None:
        base_filter.append(Task.labels.any(Label.id == label_id))

    if due_date_from is not None:
        base_filter.append(Task.due_date >= due_date_from)
    if due_date_to is not None:
        base_filter.append(Task.due_date <= due_date_to)

    if created_from is not None:
        base_filter.append(Task.created_at >= created_from)
    if created_to is not None:
        base_filter.append(Task.created_at <= created_to)

    # Facet Computations (status and priority distributions)
    status_facet_stmt = (
        select(Task.status, func.count(Task.id))
        .where(*base_filter)
        .group_by(Task.status)
    )
    status_facet_res = await db.execute(status_facet_stmt)
    status_counts = {str(row[0]): row[1] for row in status_facet_res.all()}

    priority_facet_stmt = (
        select(Task.priority, func.count(Task.id))
        .where(*base_filter)
        .group_by(Task.priority)
    )
    priority_facet_res = await db.execute(priority_facet_stmt)
    priority_counts = {str(row[0]): row[1] for row in priority_facet_res.all()}

    # Total Count
    count_stmt = select(func.count(Task.id.distinct())).where(*base_filter)
    count_res = await db.execute(count_stmt)
    total = count_res.scalar() or 0

    # Sorting
    sort_map = {
        "created_at": Task.created_at,
        "due_date": Task.due_date,
        "priority": Task.priority,
        "title": Task.title,
        "position": Task.position,
        "updated_at": Task.updated_at,
    }
    sort_col = sort_map.get(sort_by, Task.created_at)
    order_func = sort_col.desc() if order.lower() == "desc" else sort_col.asc()

    # Query tasks
    offset = (page - 1) * page_size
    stmt = (
        select(Task)
        .options(
            selectinload(Task.creator),
            selectinload(Task.assignee),
            selectinload(Task.labels),
        )
        .where(*base_filter)
        .order_by(order_func, Task.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    res = await db.execute(stmt)
    tasks = res.scalars().all()

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
            custom_fields=t.custom_fields,
            created_at=t.created_at,
            updated_at=t.updated_at,
            creator=UserResponse.model_validate(t.creator),
            assignee=UserResponse.model_validate(t.assignee) if t.assignee else None,
            labels=[LabelResponse.model_validate(lbl) for lbl in t.labels],
        )
        for t in tasks
    ]

    pages = math.ceil(total / page_size) if total > 0 else 1

    return TaskSearchResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        facets=SearchFacetsResponse(
            status_counts=status_counts,
            priority_counts=priority_counts,
        ),
    )


# Saved Views Service Functions
async def create_saved_view(
    db: AsyncSession,
    user_id: uuid.UUID,
    view_in: SavedViewCreate,
) -> SavedViewResponse:
    """Create a new saved search view."""
    if view_in.is_default:
        # Unset other defaults for this user / project
        await db.execute(
            update(SavedView)
            .where(
                SavedView.user_id == user_id,
                SavedView.project_id == view_in.project_id,
            )
            .values(is_default=False)
        )

    view = SavedView(
        user_id=user_id,
        project_id=view_in.project_id,
        name=view_in.name.strip(),
        filters=view_in.filters,
        is_default=view_in.is_default,
    )
    db.add(view)
    await db.commit()
    await db.refresh(view)
    return SavedViewResponse.model_validate(view)


async def list_user_saved_views(
    db: AsyncSession,
    user_id: uuid.UUID,
    project_id: uuid.UUID | None = None,
) -> SavedViewListResponse:
    """List saved views for the current user."""
    stmt = select(SavedView).where(SavedView.user_id == user_id)
    if project_id is not None:
        stmt = stmt.where(
            or_(
                SavedView.project_id == project_id,
                SavedView.project_id.is_(None),
            )
        )
    stmt = stmt.order_by(SavedView.is_default.desc(), SavedView.name.asc())

    result = await db.execute(stmt)
    views = result.scalars().all()

    items = [SavedViewResponse.model_validate(v) for v in views]
    return SavedViewListResponse(items=items, total=len(items))


async def get_saved_view_by_id(
    db: AsyncSession,
    view_id: uuid.UUID,
    user_id: uuid.UUID,
) -> SavedView:
    """Retrieve saved view ensuring owner authorization."""
    stmt = select(SavedView).where(
        SavedView.id == view_id,
        SavedView.user_id == user_id,
    )
    result = await db.execute(stmt)
    view = result.scalar_one_or_none()
    if not view:
        raise NotFoundException(message="Saved view not found")
    return view


async def update_saved_view(
    db: AsyncSession,
    view: SavedView,
    view_in: SavedViewUpdate,
) -> SavedViewResponse:
    """Update saved view attributes."""
    if view_in.name is not None:
        view.name = view_in.name.strip()
    if view_in.filters is not None:
        view.filters = view_in.filters
    if view_in.is_default is not None:
        if view_in.is_default:
            await db.execute(
                update(SavedView)
                .where(
                    SavedView.user_id == view.user_id,
                    SavedView.project_id == view.project_id,
                    SavedView.id != view.id,
                )
                .values(is_default=False)
            )
        view.is_default = view_in.is_default

    await db.commit()
    await db.refresh(view)
    return SavedViewResponse.model_validate(view)


async def delete_saved_view(
    db: AsyncSession,
    view: SavedView,
) -> None:
    """Permanently delete a saved view."""
    await db.delete(view)
    await db.commit()
