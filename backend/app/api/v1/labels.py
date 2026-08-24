import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenException
from app.core.permissions import Permission, has_permission
from app.modules.auth.dependencies import CurrentActiveUserDep
from app.modules.labels.schemas import (
    LabelCreate,
    LabelListResponse,
    LabelResponse,
    LabelUpdate,
)
from app.modules.labels.service import (
    attach_label_to_task,
    create_label,
    delete_label,
    detach_label_from_task,
    get_label_by_id,
    list_project_labels,
    update_label,
)
from app.modules.projects.dependencies import get_project_member
from app.modules.tasks.service import get_task_by_id

router = APIRouter(tags=["Labels"])


# 1. Project-scoped labels endpoints
@router.post(
    "/projects/{project_id}/labels",
    response_model=LabelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project label",
    description="Create a label within a project. Requires PROJECT_EDIT permission.",
)
async def add_project_label(
    project_id: Annotated[uuid.UUID, Path(description="Project UUID")],
    label_in: LabelCreate,
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LabelResponse:
    """Create a new tag label for project tasks."""
    member = await get_project_member(project_id, current_user, db)
    if not current_user.is_superuser:
        if not has_permission(member.role, Permission.PROJECT_EDIT):
            raise ForbiddenException(
                message="Action requires PROJECT_EDIT permission (OWNER or ADMIN)."
            )

    return await create_label(db, project_id, label_in)


@router.get(
    "/projects/{project_id}/labels",
    response_model=LabelListResponse,
    status_code=status.HTTP_200_OK,
    summary="List project labels",
    description="List all labels defined in a project. Requires PROJECT_VIEW.",
)
async def get_project_labels(
    project_id: Annotated[uuid.UUID, Path(description="Project UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LabelListResponse:
    """Retrieve all available labels for a project."""
    await get_project_member(project_id, current_user, db)
    return await list_project_labels(db, project_id)


# 2. Direct label-scoped endpoints
@router.patch(
    "/labels/{label_id}",
    response_model=LabelResponse,
    status_code=status.HTTP_200_OK,
    summary="Update label",
    description="Update label name or color. Requires PROJECT_EDIT.",
)
async def patch_label(
    label_id: Annotated[uuid.UUID, Path(description="Label UUID")],
    label_in: LabelUpdate,
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LabelResponse:
    """Update label attributes."""
    label = await get_label_by_id(db, label_id)
    member = await get_project_member(label.project_id, current_user, db)

    if not current_user.is_superuser:
        if not has_permission(member.role, Permission.PROJECT_EDIT):
            raise ForbiddenException(message="Action requires PROJECT_EDIT permission.")

    return await update_label(db, label, label_in)


@router.delete(
    "/labels/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete label",
    description="Delete a label. Requires PROJECT_EDIT.",
)
async def remove_label(
    label_id: Annotated[uuid.UUID, Path(description="Label UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a label."""
    label = await get_label_by_id(db, label_id)
    member = await get_project_member(label.project_id, current_user, db)

    if not current_user.is_superuser:
        if not has_permission(member.role, Permission.PROJECT_EDIT):
            raise ForbiddenException(message="Action requires PROJECT_EDIT permission.")

    await delete_label(db, label)


# 3. Task-label attachment endpoints
@router.post(
    "/tasks/{task_id}/labels/{label_id}",
    status_code=status.HTTP_200_OK,
    summary="Attach label to task",
    description="Attach label. Requires TASK_EDIT permission.",
)
async def add_label_to_task(
    task_id: Annotated[uuid.UUID, Path(description="Task UUID")],
    label_id: Annotated[uuid.UUID, Path(description="Label UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Attach label to a task."""
    task = await get_task_by_id(db, task_id)
    member = await get_project_member(task.project_id, current_user, db)

    if not current_user.is_superuser:
        if not has_permission(member.role, Permission.TASK_EDIT):
            if current_user.id not in (task.creator_id, task.assignee_id):
                raise ForbiddenException(
                    message="Action requires TASK_EDIT permission."
                )

    await attach_label_to_task(db, task, label_id)
    return {"message": "Label attached successfully"}


@router.delete(
    "/tasks/{task_id}/labels/{label_id}",
    status_code=status.HTTP_200_OK,
    summary="Detach label from task",
    description="Detach label. Requires TASK_EDIT permission.",
)
async def remove_label_from_task(
    task_id: Annotated[uuid.UUID, Path(description="Task UUID")],
    label_id: Annotated[uuid.UUID, Path(description="Label UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Detach label from a task."""
    task = await get_task_by_id(db, task_id)
    member = await get_project_member(task.project_id, current_user, db)

    if not current_user.is_superuser:
        if not has_permission(member.role, Permission.TASK_EDIT):
            if current_user.id not in (task.creator_id, task.assignee_id):
                raise ForbiddenException(
                    message="Action requires TASK_EDIT permission."
                )

    await detach_label_from_task(db, task, label_id)
    return {"message": "Label detached successfully"}
