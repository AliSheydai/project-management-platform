import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.activity.schemas import ActivityListResponse
from app.modules.activity.service import (
    list_project_activity,
    list_task_activity,
)
from app.modules.auth.dependencies import CurrentActiveUserDep
from app.modules.projects.dependencies import get_project_member
from app.modules.tasks.service import get_task_by_id

router = APIRouter(tags=["Activity & Audit Logs"])


@router.get(
    "/projects/{project_id}/activity",
    response_model=ActivityListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project activity log",
    description="Retrieve paginated activity logs for a project. Requires PROJECT_VIEW.",
)
async def get_project_activity_feed(
    project_id: Annotated[uuid.UUID, Path(description="Project UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 50,
) -> ActivityListResponse:
    """Retrieve activity audit log feed for a given project."""
    await get_project_member(project_id, current_user, db)
    return await list_project_activity(db, project_id, page=page, page_size=page_size)


@router.get(
    "/tasks/{task_id}/activity",
    response_model=ActivityListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get task activity history",
    description="Retrieve paginated activity history for a task. Requires PROJECT_VIEW.",
)
async def get_task_activity_history(
    task_id: Annotated[uuid.UUID, Path(description="Task UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 50,
) -> ActivityListResponse:
    """Retrieve activity audit history for a specific task."""
    task = await get_task_by_id(db, task_id)
    await get_project_member(task.project_id, current_user, db)
    return await list_task_activity(db, task_id, page=page, page_size=page_size)
