"""Add attachments table

Revision ID: 0006_attachments_schema
Revises: 0005_labels_and_metadata
Create Date: 2026-08-24 23:05:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0006_attachments_schema"
down_revision: str | None = "0005_labels_and_metadata"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "attachments",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("task_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("uploader_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploader_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_attachments_id"), "attachments", ["id"], unique=False)
    op.create_index(
        op.f("ix_attachments_task_id"), "attachments", ["task_id"], unique=False
    )
    op.create_index(
        op.f("ix_attachments_uploader_id"),
        "attachments",
        ["uploader_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attachments_created_at"),
        "attachments",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_attachments_created_at"), table_name="attachments")
    op.drop_index(op.f("ix_attachments_uploader_id"), table_name="attachments")
    op.drop_index(op.f("ix_attachments_task_id"), table_name="attachments")
    op.drop_index(op.f("ix_attachments_id"), table_name="attachments")
    op.drop_table("attachments")
