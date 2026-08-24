import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Path, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.permissions import Permission, has_permission
from app.modules.attachments.schemas import (
    AttachmentListResponse,
    AttachmentResponse,
)
from app.modules.attachments.service import (
    delete_attachment,
    get_attachment_by_id,
    list_task_attachments,
    upload_task_attachment,
)
from app.modules.attachments.storage import storage_service
from app.modules.auth.dependencies import CurrentActiveUserDep
from app.modules.projects.dependencies import get_project_member
from app.modules.tasks.service import get_task_by_id

router = APIRouter(tags=["Attachments"])


# 1. Task-scoped attachment endpoints
@router.post(
    "/tasks/{task_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload task attachment",
    description="Upload a file attachment to a task.",
)
async def upload_attachment(
    task_id: Annotated[uuid.UUID, Path(description="Task UUID")],
    file: Annotated[UploadFile, File(description="File to upload")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AttachmentResponse:
    """Upload and attach a file to a task."""
    task = await get_task_by_id(db, task_id)
    member = await get_project_member(task.project_id, current_user, db)

    if not current_user.is_superuser:
        # Check if user has permission to upload (TASK_EDIT or COMMENT_CREATE)
        can_edit_task = has_permission(member.role, Permission.TASK_EDIT)
        can_comment = has_permission(member.role, Permission.COMMENT_CREATE)
        is_assignee_or_creator = current_user.id in (
            task.creator_id,
            task.assignee_id,
        )

        if not (can_edit_task or can_comment or is_assignee_or_creator):
            raise ForbiddenException(
                message="You do not have permission to attach files to this task."
            )

    return await upload_task_attachment(
        db=db,
        task=task,
        uploader=current_user,
        file=file,
    )


@router.get(
    "/tasks/{task_id}/attachments",
    response_model=AttachmentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List task attachments",
    description="List all file attachments for a task. Requires PROJECT_VIEW.",
)
async def get_task_attachments(
    task_id: Annotated[uuid.UUID, Path(description="Task UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AttachmentListResponse:
    """Retrieve all attachments belonging to a task."""
    task = await get_task_by_id(db, task_id)
    await get_project_member(task.project_id, current_user, db)
    return await list_task_attachments(db, task_id)


# 2. Attachment-scoped download and delete endpoints
@router.get(
    "/attachments/{attachment_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Download attachment file",
    description="Download a file attachment. Requires PROJECT_VIEW.",
)
async def download_attachment_file(
    attachment_id: Annotated[uuid.UUID, Path(description="Attachment UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FileResponse:
    """Stream and download an attachment file."""
    attachment = await get_attachment_by_id(db, attachment_id)
    await get_project_member(attachment.task.project_id, current_user, db)

    file_path = storage_service.get_absolute_path(attachment.file_path)
    if not file_path.is_file():
        raise NotFoundException(message="File not found on storage server")

    return FileResponse(
        path=file_path,
        filename=attachment.file_name,
        media_type=attachment.content_type,
    )


@router.delete(
    "/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete attachment",
    description="Delete attachment and clean up physical file.",
)
async def remove_attachment(
    attachment_id: Annotated[uuid.UUID, Path(description="Attachment UUID")],
    current_user: CurrentActiveUserDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete an attachment."""
    attachment = await get_attachment_by_id(db, attachment_id)
    member = await get_project_member(attachment.task.project_id, current_user, db)

    if not current_user.is_superuser and attachment.uploader_id != current_user.id:
        if not has_permission(member.role, Permission.TASK_EDIT):
            raise ForbiddenException(
                message=(
                    "Action requires TASK_EDIT permission or attachment authorship."
                )
            )

    await delete_attachment(db, attachment, actor_id=current_user.id)
