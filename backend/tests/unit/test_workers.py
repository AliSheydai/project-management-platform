import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.queue import enqueue_job
from app.modules.activity.models import ActivityAction, ActivityLog
from app.modules.auth.models import RefreshToken
from app.modules.projects.models import Project
from app.modules.tasks.models import Task, TaskPriority, TaskStatus
from app.modules.users.models import User
from app.workers.email import render_email_template, send_email
from app.workers.runner import (
    WorkerSettings,
    aggregate_daily_activity_stats_job,
    cleanup_expired_sessions_job,
    send_email_job,
)


def test_render_email_templates() -> None:
    """Test template rendering for all supported transactional email types."""
    # 1. Welcome template
    subj, body = render_email_template("welcome", {"name": "Alice"})
    assert "Welcome" in subj
    assert "Alice" in body

    # 2. Task assigned template
    subj, body = render_email_template(
        "task_assigned",
        {
            "task_title": "Fix Auth Bug",
            "project_name": "Core Platform",
            "assigner_name": "Bob",
        },
    )
    assert "Task Assigned: Fix Auth Bug" in subj
    assert "Bob" in body
    assert "Core Platform" in body

    # 3. User mentioned template
    subj, body = render_email_template(
        "user_mentioned",
        {
            "mentioner_name": "Charlie",
            "task_title": "Database Optimization",
            "comment_text": "Please check @Alice",
        },
    )
    assert "Mentioned in: Database Optimization" in subj
    assert "Charlie" in body
    assert "@Alice" in body

    # 4. Project invited template
    subj, body = render_email_template(
        "project_invited",
        {
            "inviter_name": "Dave",
            "project_name": "New Website",
            "role": "ADMIN",
        },
    )
    assert "Invitation to join project: New Website" in subj
    assert "ADMIN" in body

    # 5. Default/Custom template
    subj, body = render_email_template(
        "custom",
        {"subject": "Custom Alert", "message": "System check passed"},
    )
    assert subj == "Custom Alert"
    assert "System check passed" in body


@pytest.mark.asyncio
async def test_send_email_direct() -> None:
    """Test send_email utility."""
    result = await send_email("test@example.com", "Test Subject", "Test Body")
    assert result is True


@pytest.mark.asyncio
async def test_send_email_job() -> None:
    """Test send_email_job background worker task."""
    ctx = {"job_id": "job-123"}
    res = await send_email_job(
        ctx,
        to_email="worker_test@example.com",
        template="welcome",
        context={"name": "Worker User"},
    )
    assert res["status"] == "sent"
    assert res["to"] == "worker_test@example.com"
    assert res["template"] == "welcome"


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_job(
    db_session: AsyncSession, test_db_engine
) -> None:
    """Test cleanup_expired_sessions_job purges expired/revoked sessions."""
    # Create test user
    user = User(
        id=uuid.uuid4(),
        email=f"worker_user_{uuid.uuid4().hex[:6]}@example.com",
        password_hash="hashed_pw",
        first_name="Session",
        last_name="Test",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    now = datetime.now(UTC)

    # 1. Active valid session
    active_token = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash="active_hash_1",
        expires_at=now + timedelta(days=7),
        is_revoked=False,
    )
    # 2. Expired session
    expired_token = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash="expired_hash_2",
        expires_at=now - timedelta(days=1),
        is_revoked=False,
    )
    # 3. Revoked session
    revoked_token = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash="revoked_hash_3",
        expires_at=now + timedelta(days=5),
        is_revoked=True,
    )

    db_session.add_all([active_token, expired_token, revoked_token])
    await db_session.commit()

    # Create sessionmaker for test DB
    session_factory = async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    ctx = {"session_factory": session_factory, "job_id": "cleanup-job-1"}
    res = await cleanup_expired_sessions_job(ctx)

    assert res["status"] == "success"
    assert res["purged_count"] == 2

    # Verify only active token remains
    remaining = (await db_session.execute(select(RefreshToken))).scalars().all()
    assert len(remaining) == 1
    assert remaining[0].token_hash == "active_hash_1"


@pytest.mark.asyncio
async def test_aggregate_daily_activity_stats_job(
    db_session: AsyncSession,
    test_db_engine,
) -> None:
    """Test activity and task stats aggregation job."""
    # Create test user and project
    user = User(
        id=uuid.uuid4(),
        email=f"stats_user_{uuid.uuid4().hex[:6]}@example.com",
        password_hash="hashed_pw",
        first_name="Stats",
        last_name="User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    project = Project(
        id=uuid.uuid4(),
        name="Stats Project",
        description="Stats Project Description",
        owner_id=user.id,
    )
    db_session.add(project)
    await db_session.flush()

    # Create tasks in various states
    task1 = Task(
        id=uuid.uuid4(),
        project_id=project.id,
        creator_id=user.id,
        title="Stats Task 1",
        status=TaskStatus.TODO,
        priority=TaskPriority.HIGH,
        position=1000,
    )
    task2 = Task(
        id=uuid.uuid4(),
        project_id=project.id,
        creator_id=user.id,
        title="Stats Task 2",
        status=TaskStatus.DONE,
        priority=TaskPriority.LOW,
        position=2000,
    )
    db_session.add_all([task1, task2])

    # Create activity logs
    act1 = ActivityLog(
        id=uuid.uuid4(),
        project_id=project.id,
        user_id=user.id,
        action=ActivityAction.TASK_CREATED,
        entity_type="task",
        entity_id=task1.id,
    )
    db_session.add(act1)
    await db_session.commit()

    session_factory = async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    ctx = {"session_factory": session_factory, "job_id": "stats-job-1"}
    res = await aggregate_daily_activity_stats_job(ctx, project_id=str(project.id))

    assert res["status"] == "success"
    summary = res["summary"]
    assert summary["total_activities_24h"] >= 1
    assert (
        "TaskStatus.TODO" in summary["task_distribution"]
        or "TODO" in summary["task_distribution"]
    )


@pytest.mark.asyncio
async def test_enqueue_job_graceful_fallback() -> None:
    """Test enqueue_job helper handles fallback gracefully without exceptions."""
    result = await enqueue_job("send_email_job", to_email="test@example.com")
    assert result in (True, False)


def test_worker_settings_metadata() -> None:
    """Test WorkerSettings configuration properties."""
    assert len(WorkerSettings.functions) == 3
    assert WorkerSettings.max_tries == 3
    assert WorkerSettings.retry_jobs is True
