import asyncio
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from arq.connections import RedisSettings
from sqlalchemy import delete, func, or_, select

from app.core.config import settings
from app.core.database import async_session_factory, close_db_engine
from app.core.logging import logger, setup_logging
from app.core.queue import get_redis_settings
from app.modules.activity.models import ActivityLog
from app.modules.auth.models import RefreshToken
from app.modules.projects.models import Project
from app.modules.tasks.models import Task
from app.workers.email import render_email_template, send_email


async def send_email_job(
    ctx: dict[str, Any],
    to_email: str,
    template: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Background job to format and send transactional emails."""
    job_id = ctx.get("job_id", "local")
    logger.info("Executing send_email_job [%s] for %s (%s)", job_id, to_email, template)

    try:
        subject, body = render_email_template(template, context)
        delivered = await send_email(to_email=to_email, subject=subject, body=body)
        return {
            "status": "sent" if delivered else "failed",
            "to": to_email,
            "template": template,
            "subject": subject,
        }
    except Exception as e:
        logger.exception("Failed to send email to %s: %s", to_email, e)
        raise e


async def cleanup_expired_sessions_job(
    ctx: dict[str, Any],
) -> dict[str, Any]:
    """Background job to purge expired or revoked refresh tokens."""
    job_id = ctx.get("job_id", "local")
    logger.info("Executing cleanup_expired_sessions_job [%s]...", job_id)

    now = datetime.now(UTC)
    async_session = ctx.get("session_factory", async_session_factory)

    async with async_session() as db:
        stmt = delete(RefreshToken).where(
            or_(
                RefreshToken.expires_at <= now,
                RefreshToken.is_revoked == True,  # noqa: E712
            )
        )
        result = await db.execute(stmt)
        deleted_count = result.rowcount
        await db.commit()

    logger.info(
        "cleanup_expired_sessions_job completed. Purged %d expired/revoked sessions.",
        deleted_count,
    )
    return {"status": "success", "purged_count": deleted_count}


async def aggregate_daily_activity_stats_job(
    ctx: dict[str, Any],
    project_id: str | uuid.UUID | None = None,
) -> dict[str, Any]:
    """Background job to aggregate daily project activity and task distributions."""
    job_id = ctx.get("job_id", "local")
    logger.info(
        "Executing aggregate_daily_activity_stats_job [%s] (project=%s)...",
        job_id,
        project_id or "ALL",
    )

    now = datetime.now(UTC)
    yesterday = now - timedelta(days=1)
    async_session = ctx.get("session_factory", async_session_factory)

    pid_uuid = uuid.UUID(str(project_id)) if project_id else None
    stats: dict[str, Any] = {}

    async with async_session() as db:
        # 1. Total activity entries in past 24h
        act_stmt = select(func.count(ActivityLog.id)).where(
            ActivityLog.created_at >= yesterday
        )
        if pid_uuid:
            act_stmt = act_stmt.where(ActivityLog.project_id == pid_uuid)
        act_res = await db.execute(act_stmt)
        total_activities_24h = act_res.scalar() or 0

        # 2. Total active projects count
        proj_res = await db.execute(select(func.count(Project.id)))
        total_projects = proj_res.scalar() or 0

        # 3. Task counts by status
        task_stmt = select(Task.status, func.count(Task.id)).group_by(Task.status)
        if pid_uuid:
            task_stmt = task_stmt.where(Task.project_id == pid_uuid)
        task_res = await db.execute(task_stmt)
        status_distribution = {
            str(row[0].value if hasattr(row[0], "value") else row[0]): row[1]
            for row in task_res.all()
        }

        stats = {
            "window_start": yesterday.isoformat(),
            "window_end": now.isoformat(),
            "total_activities_24h": total_activities_24h,
            "total_projects": total_projects,
            "task_distribution": status_distribution,
        }

    logger.info("aggregate_daily_activity_stats_job finished with summary: %s", stats)
    return {"status": "success", "summary": stats}


async def startup(ctx: dict[str, Any]) -> None:
    """Worker startup hook."""
    setup_logging()
    logger.info(
        "Initializing ARQ Background Worker for %s in %s...",
        settings.PROJECT_NAME,
        settings.ENVIRONMENT,
    )
    ctx["session_factory"] = async_session_factory


async def shutdown(ctx: dict[str, Any]) -> None:
    """Worker shutdown hook."""
    logger.info("Shutting down ARQ Background Worker...")
    await close_db_engine()


class WorkerSettings:
    """ARQ Worker configuration class."""

    functions = [
        send_email_job,
        cleanup_expired_sessions_job,
        aggregate_daily_activity_stats_job,
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings: RedisSettings = get_redis_settings()
    max_tries = 3
    retry_jobs = True
    job_timeout = 300


if __name__ == "__main__":
    from arq import run_worker

    asyncio.run(run_worker(WorkerSettings))
