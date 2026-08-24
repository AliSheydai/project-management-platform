"""Add labels, task_labels tables and custom_fields column to tasks

Revision ID: 0005_labels_and_metadata
Revises: 0004_comments_and_activity
Create Date: 2026-08-24 22:50:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005_labels_and_metadata"
down_revision: str | None = "0004_comments_and_activity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create labels table
    op.create_table(
        "labels",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column(
            "color",
            sa.String(length=20),
            server_default="#6B7280",
            nullable=False,
        ),
        sa.Column("description", sa.String(length=200), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_project_label_name"),
    )
    op.create_index(op.f("ix_labels_id"), "labels", ["id"], unique=False)
    op.create_index(
        op.f("ix_labels_project_id"), "labels", ["project_id"], unique=False
    )
    op.create_index(op.f("ix_labels_name"), "labels", ["name"], unique=False)

    # 2. Create task_labels association table
    op.create_table(
        "task_labels",
        sa.Column("task_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("label_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["label_id"], ["labels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("task_id", "label_id"),
    )
    op.create_index(
        op.f("ix_task_labels_task_id"),
        "task_labels",
        ["task_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_task_labels_label_id"),
        "task_labels",
        ["label_id"],
        unique=False,
    )

    # 3. Add custom_fields column to tasks table
    op.add_column(
        "tasks",
        sa.Column("custom_fields", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tasks", "custom_fields")

    op.drop_index(op.f("ix_task_labels_label_id"), table_name="task_labels")
    op.drop_index(op.f("ix_task_labels_task_id"), table_name="task_labels")
    op.drop_table("task_labels")

    op.drop_index(op.f("ix_labels_name"), table_name="labels")
    op.drop_index(op.f("ix_labels_project_id"), table_name="labels")
    op.drop_index(op.f("ix_labels_id"), table_name="labels")
    op.drop_table("labels")
