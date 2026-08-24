import math
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.activity.models import ActivityAction, ActivityLog
from app.modules.activity.schemas import (
    ActivityListResponse,
    ActivityLogResponse,
)
from app.modules.users.schemas import UserResponse


async def record_activity(
    db: AsyncSession,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    action: ActivityAction | str,
    entity_type: str,
    entity_id: uuid.UUID,
    task_id: uuid.UUID | None = None,
    details: dict[str, Any] | None = None,
) -> ActivityLog:
    """Record an audit log entry within the workspace."""
    action_str = action if isinstance(action, str) else action.value
    log_entry = ActivityLog(
        project_id=project_id,
        task_id=task_id,
        user_id=user_id,
        action=action_str,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(log_entry)
    return log_entry


async def list_project_activity(
    db: AsyncSession,
    project_id: uuid.UUID,
    page: int = 1,
    page_size: int = 50,
) -> ActivityListResponse:
    """Retrieve paginated activity feed for a project."""
    base_filter = [ActivityLog.project_id == project_id]

    count_stmt = select(func.count(ActivityLog.id)).where(*base_filter)
    count_res = await db.execute(count_stmt)
    total = count_res.scalar() or 0

    offset = (page - 1) * page_size
    stmt = (
        select(ActivityLog)
        .options(selectinload(ActivityLog.user))
        .where(*base_filter)
        .order_by(ActivityLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    items = [
        ActivityLogResponse(
            id=log.id,
            project_id=log.project_id,
            task_id=log.task_id,
            user_id=log.user_id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            details=log.details,
            created_at=log.created_at,
            user=UserResponse.model_validate(log.user),
        )
        for log in logs
    ]

    pages = math.ceil(total / page_size) if total > 0 else 1

    return ActivityListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


async def list_task_activity(
    db: AsyncSession,
    task_id: uuid.UUID,
    page: int = 1,
    page_size: int = 50,
) -> ActivityListResponse:
    """Retrieve paginated activity history for a specific task."""
    base_filter = [ActivityLog.task_id == task_id]

    count_stmt = select(func.count(ActivityLog.id)).where(*base_filter)
    count_res = await db.execute(count_stmt)
    total = count_res.scalar() or 0

    offset = (page - 1) * page_size
    stmt = (
        select(ActivityLog)
        .options(selectinload(ActivityLog.user))
        .where(*base_filter)
        .order_by(ActivityLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    items = [
        ActivityLogResponse(
            id=log.id,
            project_id=log.project_id,
            task_id=log.task_id,
            user_id=log.user_id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            details=log.details,
            created_at=log.created_at,
            user=UserResponse.model_validate(log.user),
        )
        for log in logs
    ]

    pages = math.ceil(total / page_size) if total > 0 else 1

    return ActivityListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
