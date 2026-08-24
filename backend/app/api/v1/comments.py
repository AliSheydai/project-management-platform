import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenException
from app.core.permissions import Permission, has_permission
from app.modules.auth.dependencies import CurrentActiveUserDep
from app.modules.comments.schemas import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
)
from app.modules.comments.service import (
    create_comment,
    delete_comment,
    get_comment_by_id,
    list_task_comments,
    update_comment,
)
from app.modules.projects.dependencies import get_project_member
from app.modules.tasks.service import get_task_by_id

router = APIRouter(tags=["Comments"])


# 1. Task-scoped comments endpoints
@router.post(
    "/tasks/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add comment to task",
    description="Create a comment. Requires COMMENT_CREATE permission on project.",
)
async def add_task_comment(
    task_id: Annotated[uuid.UUID, Path(description="Task UUID")],
    comment_in: CommentCreate,
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CommentResponse:
    """Post a comment on a project task."""
    task = await get_task_by_id(db, task_id)
    member = await get_project_member(task.project_id, current_user, db)

    if not current_user.is_superuser:
        if not has_permission(member.role, Permission.COMMENT_CREATE):
            raise ForbiddenException(
                message="Action requires COMMENT_CREATE permission on project."
            )

    return await create_comment(db, task_id, current_user.id, comment_in)


@router.get(
    "/tasks/{task_id}/comments",
    response_model=CommentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List task comments",
    description="Retrieve comments. Requires PROJECT_VIEW permission.",
)
async def get_task_comments(
    task_id: Annotated[uuid.UUID, Path(description="Task UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 50,
) -> CommentListResponse:
    """List comments on a task with pagination."""
    task = await get_task_by_id(db, task_id)
    await get_project_member(task.project_id, current_user, db)

    return await list_task_comments(db, task_id, page=page, page_size=page_size)


# 2. Direct comment-scoped endpoints
@router.patch(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
    summary="Edit comment",
    description="Edit comment body. Restricted to the original comment author.",
)
async def edit_comment(
    comment_id: Annotated[uuid.UUID, Path(description="Comment UUID")],
    comment_in: CommentUpdate,
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CommentResponse:
    """Edit comment text."""
    comment = await get_comment_by_id(db, comment_id)
    # Check user membership on parent task project
    await get_project_member(comment.task.project_id, current_user, db)

    if not current_user.is_superuser and comment.author_id != current_user.id:
        raise ForbiddenException(message="Only the author can edit their own comment.")

    return await update_comment(db, comment, comment_in)


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete comment",
    description="Delete comment. Allowed for the author or users with COMMENT_DELETE.",
)
async def remove_comment(
    comment_id: Annotated[uuid.UUID, Path(description="Comment UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a comment."""
    comment = await get_comment_by_id(db, comment_id)
    member = await get_project_member(comment.task.project_id, current_user, db)

    if not current_user.is_superuser and comment.author_id != current_user.id:
        if not has_permission(member.role, Permission.COMMENT_DELETE):
            raise ForbiddenException(
                message="Action requires COMMENT_DELETE permission or comment authorship."
            )

    await delete_comment(db, comment, actor_id=current_user.id)
