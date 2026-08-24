import math
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.core.websockets import ws_manager
from app.modules.activity.models import ActivityAction
from app.modules.activity.service import record_activity
from app.modules.comments.models import Comment
from app.modules.comments.schemas import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
)
from app.modules.notifications.models import NotificationType
from app.modules.notifications.service import (
    create_notification,
    parse_and_notify_mentions,
)
from app.modules.tasks.models import Task
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse


async def create_comment(
    db: AsyncSession,
    task_id: uuid.UUID,
    author_id: uuid.UUID,
    comment_in: CommentCreate,
) -> Comment:
    """Create a new comment on a task and record activity."""
    # Verify task exists
    task_stmt = select(Task).where(Task.id == task_id)
    task_res = await db.execute(task_stmt)
    task = task_res.scalar_one_or_none()
    if not task:
        raise NotFoundException(message=f"Task {task_id} not found")

    comment = Comment(
        task_id=task_id,
        author_id=author_id,
        content=comment_in.content,
    )
    db.add(comment)
    await db.flush()

    # Record activity log
    await record_activity(
        db=db,
        project_id=task.project_id,
        user_id=author_id,
        action=ActivityAction.COMMENT_ADDED,
        entity_type="comment",
        entity_id=comment.id,
        task_id=task_id,
        details={"content_preview": comment_in.content[:100]},
    )

    # Fetch author user
    user_stmt = select(User).where(User.id == author_id)
    user_res = await db.execute(user_stmt)
    author = user_res.scalar_one_or_none()

    if author:
        # Notify task assignee & creator
        for uid in {task.assignee_id, task.creator_id}:
            if uid and uid != author_id:
                await create_notification(
                    db=db,
                    user_id=uid,
                    actor_id=author_id,
                    notification_type=NotificationType.COMMENT_ADDED,
                    title=f"New comment on: {task.title}",
                    message=f"{author.full_name}: '{comment_in.content[:60]}'",
                    entity_type="comment",
                    entity_id=comment.id,
                    payload={
                        "task_id": str(task_id),
                        "project_id": str(task.project_id),
                    },
                )

        # Parse @mentions
        await parse_and_notify_mentions(
            db=db,
            text=comment_in.content,
            project_id=task.project_id,
            actor=author,
            entity_type="comment",
            entity_id=comment.id,
            title=f"Mentioned in comment on '{task.title}'",
            payload={
                "task_id": str(task_id),
                "project_id": str(task.project_id),
            },
        )

    await db.commit()

    # Re-fetch with eager loaded author
    stmt = (
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.id == comment.id)
    )
    res = await db.execute(stmt)
    created_comment = res.scalar_one()

    # Broadcast real-time comment:added event
    await ws_manager.broadcast_to_project(
        project_id=task.project_id,
        event="comment:added",
        payload={
            "task_id": str(task_id),
            "comment": {
                "id": str(created_comment.id),
                "task_id": str(created_comment.task_id),
                "author_id": str(created_comment.author_id),
                "content": created_comment.content,
                "created_at": created_comment.created_at.isoformat(),
                "updated_at": created_comment.updated_at.isoformat(),
                "author": {
                    "id": str(created_comment.author.id),
                    "email": created_comment.author.email,
                    "first_name": created_comment.author.first_name,
                    "last_name": created_comment.author.last_name,
                    "avatar_url": created_comment.author.avatar_url,
                }
                if created_comment.author
                else None,
            },
        },
    )

    return created_comment


async def list_task_comments(
    db: AsyncSession,
    task_id: uuid.UUID,
    page: int = 1,
    page_size: int = 50,
) -> CommentListResponse:
    """Retrieve paginated comments for a task."""
    base_filter = [Comment.task_id == task_id]

    count_stmt = select(func.count(Comment.id)).where(*base_filter)
    count_res = await db.execute(count_stmt)
    total = count_res.scalar() or 0

    offset = (page - 1) * page_size
    stmt = (
        select(Comment)
        .options(selectinload(Comment.author))
        .where(*base_filter)
        .order_by(Comment.created_at.asc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    comments = result.scalars().all()

    items = [
        CommentResponse(
            id=c.id,
            task_id=c.task_id,
            author_id=c.author_id,
            content=c.content,
            created_at=c.created_at,
            updated_at=c.updated_at,
            author=UserResponse.model_validate(c.author),
        )
        for c in comments
    ]

    pages = math.ceil(total / page_size) if total > 0 else 1

    return CommentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


async def get_comment_by_id(db: AsyncSession, comment_id: uuid.UUID) -> Comment:
    """Retrieve comment with author and task loaded."""
    stmt = (
        select(Comment)
        .options(
            selectinload(Comment.author),
            selectinload(Comment.task),
        )
        .where(Comment.id == comment_id)
    )
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if not comment:
        raise NotFoundException(message=f"Comment {comment_id} not found")
    return comment


async def update_comment(
    db: AsyncSession,
    comment: Comment,
    comment_in: CommentUpdate,
) -> Comment:
    """Update comment body."""
    comment.content = comment_in.content
    await db.commit()

    stmt = (
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.id == comment.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def delete_comment(
    db: AsyncSession,
    comment: Comment,
    actor_id: uuid.UUID,
) -> None:
    """Delete a comment and log deletion."""
    await record_activity(
        db=db,
        project_id=comment.task.project_id,
        user_id=actor_id,
        action=ActivityAction.COMMENT_DELETED,
        entity_type="comment",
        entity_id=comment.id,
        task_id=comment.task_id,
    )
    await db.delete(comment)
    await db.commit()
