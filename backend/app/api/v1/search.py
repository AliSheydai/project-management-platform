import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentActiveUserDep
from app.modules.search.schemas import (
    SavedViewCreate,
    SavedViewListResponse,
    SavedViewResponse,
    SavedViewUpdate,
    TaskSearchResponse,
)
from app.modules.search.service import (
    create_saved_view,
    delete_saved_view,
    get_saved_view_by_id,
    list_user_saved_views,
    search_tasks,
    update_saved_view,
)
from app.modules.tasks.models import TaskPriority, TaskStatus

router = APIRouter(tags=["Search & Saved Views"])


# 1. Search Engine Endpoint
@router.get(
    "/search/tasks",
    response_model=TaskSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Cross-project task search",
    description="Search tasks across accessible projects with filters and facets.",
)
async def execute_task_search(
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    q: Annotated[
        str | None, Query(description="Search keyword in title/description")
    ] = None,
    project_id: Annotated[
        uuid.UUID | None, Query(description="Scope search to single project")
    ] = None,
    task_status: Annotated[
        list[TaskStatus] | None, Query(alias="status", description="Filter statuses")
    ] = None,
    priority: Annotated[
        list[TaskPriority] | None, Query(description="Filter priorities")
    ] = None,
    assignee_id: Annotated[
        uuid.UUID | None, Query(description="Filter by assignee UUID")
    ] = None,
    creator_id: Annotated[
        uuid.UUID | None, Query(description="Filter by creator UUID")
    ] = None,
    label_id: Annotated[
        uuid.UUID | None, Query(description="Filter by attached label UUID")
    ] = None,
    unassigned: Annotated[
        bool, Query(description="Filter unassigned tasks only")
    ] = False,
    due_date_from: Annotated[
        datetime | None, Query(description="Filter due date from")
    ] = None,
    due_date_to: Annotated[
        datetime | None, Query(description="Filter due date to")
    ] = None,
    created_from: Annotated[
        datetime | None, Query(description="Filter created from")
    ] = None,
    created_to: Annotated[
        datetime | None, Query(description="Filter created to")
    ] = None,
    sort_by: Annotated[
        str,
        Query(
            description="Sort column (created_at, due_date, priority, title, position)"
        ),
    ] = "created_at",
    order: Annotated[
        str, Query(pattern="^(asc|desc)$", description="Sort order (asc/desc)")
    ] = "desc",
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
) -> TaskSearchResponse:
    """Execute search across accessible projects."""
    return await search_tasks(
        db=db,
        current_user=current_user,
        project_id=project_id,
        query=q,
        statuses=task_status,
        priorities=priority,
        assignee_id=assignee_id,
        creator_id=creator_id,
        label_id=label_id,
        unassigned=unassigned,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
        created_from=created_from,
        created_to=created_to,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )


# 2. Saved Views Endpoints
@router.post(
    "/saved-views",
    response_model=SavedViewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create saved view",
    description="Save a custom search and filter view configuration.",
)
async def add_saved_view(
    view_in: SavedViewCreate,
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SavedViewResponse:
    """Create a saved search view."""
    return await create_saved_view(db, current_user.id, view_in)


@router.get(
    "/saved-views",
    response_model=SavedViewListResponse,
    status_code=status.HTTP_200_OK,
    summary="List saved views",
    description="List saved search views for the authenticated user.",
)
async def get_saved_views(
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    project_id: Annotated[
        uuid.UUID | None, Query(description="Filter by project")
    ] = None,
) -> SavedViewListResponse:
    """Retrieve saved search views."""
    return await list_user_saved_views(db, current_user.id, project_id)


@router.patch(
    "/saved-views/{view_id}",
    response_model=SavedViewResponse,
    status_code=status.HTTP_200_OK,
    summary="Update saved view",
    description="Update a saved search view.",
)
async def patch_saved_view(
    view_id: Annotated[uuid.UUID, Path(description="Saved View UUID")],
    view_in: SavedViewUpdate,
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SavedViewResponse:
    """Update saved view attributes."""
    view = await get_saved_view_by_id(db, view_id, current_user.id)
    return await update_saved_view(db, view, view_in)


@router.delete(
    "/saved-views/{view_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete saved view",
    description="Delete a saved search view.",
)
async def remove_saved_view(
    view_id: Annotated[uuid.UUID, Path(description="Saved View UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a saved search view."""
    view = await get_saved_view_by_id(db, view_id, current_user.id)
    await delete_saved_view(db, view)
