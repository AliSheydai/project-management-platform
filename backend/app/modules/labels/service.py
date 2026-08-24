import uuid

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from app.modules.labels.models import Label, task_labels
from app.modules.labels.schemas import (
    LabelCreate,
    LabelListResponse,
    LabelResponse,
    LabelUpdate,
)
from app.modules.tasks.models import Task


async def create_label(
    db: AsyncSession,
    project_id: uuid.UUID,
    label_in: LabelCreate,
) -> Label:
    """Create a new label in a project."""
    existing_stmt = select(Label).where(
        Label.project_id == project_id,
        Label.name == label_in.name.strip(),
    )
    existing_res = await db.execute(existing_stmt)
    if existing_res.scalar_one_or_none():
        raise ConflictException(
            message=(
                f"Label with name '{label_in.name.strip()}' "
                "already exists in this project."
            )
        )

    label = Label(
        project_id=project_id,
        name=label_in.name.strip(),
        color=label_in.color.strip(),
        description=label_in.description.strip() if label_in.description else None,
    )
    db.add(label)
    await db.commit()
    await db.refresh(label)
    return label


async def list_project_labels(
    db: AsyncSession,
    project_id: uuid.UUID,
) -> LabelListResponse:
    """List all labels in a project."""
    stmt = (
        select(Label).where(Label.project_id == project_id).order_by(Label.name.asc())
    )
    result = await db.execute(stmt)
    labels = result.scalars().all()

    items = [LabelResponse.model_validate(lbl) for lbl in labels]
    return LabelListResponse(items=items, total=len(items))


async def get_label_by_id(db: AsyncSession, label_id: uuid.UUID) -> Label:
    """Retrieve label by UUID."""
    stmt = select(Label).where(Label.id == label_id)
    result = await db.execute(stmt)
    label = result.scalar_one_or_none()
    if not label:
        raise NotFoundException(message=f"Label {label_id} not found")
    return label


async def update_label(
    db: AsyncSession,
    label: Label,
    label_in: LabelUpdate,
) -> Label:
    """Update label attributes."""
    if label_in.name is not None and label_in.name.strip() != label.name:
        check_stmt = select(Label).where(
            Label.project_id == label.project_id,
            Label.name == label_in.name.strip(),
            Label.id != label.id,
        )
        check_res = await db.execute(check_stmt)
        if check_res.scalar_one_or_none():
            raise ConflictException(
                message=(
                    f"Label '{label_in.name.strip()}' already exists in this project."
                )
            )
        label.name = label_in.name.strip()

    if label_in.color is not None:
        label.color = label_in.color.strip()
    if label_in.description is not None:
        label.description = (
            label_in.description.strip() if label_in.description else None
        )

    await db.commit()
    await db.refresh(label)
    return label


async def delete_label(db: AsyncSession, label: Label) -> None:
    """Delete a label from project."""
    await db.delete(label)
    await db.commit()


async def attach_label_to_task(
    db: AsyncSession,
    task: Task,
    label_id: uuid.UUID,
) -> None:
    """Attach a label to a task if it belongs to the same project."""
    label = await get_label_by_id(db, label_id)
    if label.project_id != task.project_id:
        raise BadRequestException(
            message="Label does not belong to the same project as the task"
        )

    check_stmt = select(task_labels).where(
        task_labels.c.task_id == task.id,
        task_labels.c.label_id == label_id,
    )
    check_res = await db.execute(check_stmt)
    if check_res.first() is None:
        insert_stmt = insert(task_labels).values(task_id=task.id, label_id=label_id)
        await db.execute(insert_stmt)
        await db.commit()


async def detach_label_from_task(
    db: AsyncSession,
    task: Task,
    label_id: uuid.UUID,
) -> None:
    """Remove a label association from a task."""
    del_stmt = delete(task_labels).where(
        task_labels.c.task_id == task.id,
        task_labels.c.label_id == label_id,
    )
    await db.execute(del_stmt)
    await db.commit()
