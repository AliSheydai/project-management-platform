import uuid

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.modules.activity.models import ActivityAction
from app.modules.activity.service import record_activity
from app.modules.attachments.models import Attachment
from app.modules.attachments.schemas import (
    AttachmentListResponse,
    AttachmentResponse,
)
from app.modules.attachments.storage import storage_service, validate_file
from app.modules.tasks.models import Task
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse


async def upload_task_attachment(
    db: AsyncSession,
    task: Task,
    uploader: User,
    file: UploadFile,
) -> AttachmentResponse:
    """Upload and attach a file to a project task."""
    file_bytes = await file.read()
    file_size = len(file_bytes)
    content_type = file.content_type or "application/octet-stream"
    original_filename = file.filename or "attachment"

    # Validate size & MIME type
    validate_file(content_type=content_type, file_size=file_size)

    # Save to storage
    stored_path = await storage_service.save_file(file_bytes, original_filename)

    attachment = Attachment(
        task_id=task.id,
        uploader_id=uploader.id,
        file_name=original_filename,
        file_path=stored_path,
        file_size=file_size,
        content_type=content_type,
    )
    db.add(attachment)
    await db.flush()

    # Record activity log
    await record_activity(
        db=db,
        project_id=task.project_id,
        user_id=uploader.id,
        action=ActivityAction.ATTACHMENT_ADDED,
        entity_type="attachment",
        entity_id=attachment.id,
        task_id=task.id,
        details={
            "file_name": attachment.file_name,
            "file_size": attachment.file_size,
            "content_type": attachment.content_type,
        },
    )

    await db.commit()
    await db.refresh(attachment)

    return AttachmentResponse(
        id=attachment.id,
        task_id=attachment.task_id,
        uploader_id=attachment.uploader_id,
        file_name=attachment.file_name,
        file_size=attachment.file_size,
        content_type=attachment.content_type,
        created_at=attachment.created_at,
        uploader=UserResponse.model_validate(uploader),
    )


async def list_task_attachments(
    db: AsyncSession,
    task_id: uuid.UUID,
) -> AttachmentListResponse:
    """Retrieve list of attachments associated with a task."""
    stmt = (
        select(Attachment)
        .options(selectinload(Attachment.uploader))
        .where(Attachment.task_id == task_id)
        .order_by(Attachment.created_at.desc())
    )
    result = await db.execute(stmt)
    attachments = result.scalars().all()

    items = [
        AttachmentResponse(
            id=a.id,
            task_id=a.task_id,
            uploader_id=a.uploader_id,
            file_name=a.file_name,
            file_size=a.file_size,
            content_type=a.content_type,
            created_at=a.created_at,
            uploader=UserResponse.model_validate(a.uploader) if a.uploader else None,
        )
        for a in attachments
    ]
    return AttachmentListResponse(items=items, total=len(items))


async def get_attachment_by_id(
    db: AsyncSession,
    attachment_id: uuid.UUID,
) -> Attachment:
    """Retrieve attachment with task and uploader relationships loaded."""
    stmt = (
        select(Attachment)
        .options(
            selectinload(Attachment.task),
            selectinload(Attachment.uploader),
        )
        .where(Attachment.id == attachment_id)
    )
    result = await db.execute(stmt)
    attachment = result.scalar_one_or_none()
    if not attachment:
        raise NotFoundException(message="Attachment not found")
    return attachment


async def delete_attachment(
    db: AsyncSession,
    attachment: Attachment,
    actor_id: uuid.UUID,
) -> None:
    """Delete an attachment record and remove the physical file from disk."""
    # Remove file from disk
    storage_service.delete_file(attachment.file_path)

    # Record activity log
    await record_activity(
        db=db,
        project_id=attachment.task.project_id,
        user_id=actor_id,
        action=ActivityAction.ATTACHMENT_DELETED,
        entity_type="attachment",
        entity_id=attachment.id,
        task_id=attachment.task_id,
        details={"file_name": attachment.file_name},
    )

    await db.delete(attachment)
    await db.commit()
