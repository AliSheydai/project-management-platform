"""Add saved_views table

Revision ID: 0007_search_and_saved_views
Revises: 0006_attachments_schema
Create Date: 2026-08-24 23:10:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0007_search_and_saved_views"
down_revision: str | None = "0006_attachments_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "saved_views",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("filters", sa.JSON(), nullable=False),
        sa.Column(
            "is_default",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_saved_views_id"), "saved_views", ["id"], unique=False)
    op.create_index(
        op.f("ix_saved_views_user_id"),
        "saved_views",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_saved_views_project_id"),
        "saved_views",
        ["project_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_saved_views_project_id"), table_name="saved_views")
    op.drop_index(op.f("ix_saved_views_user_id"), table_name="saved_views")
    op.drop_index(op.f("ix_saved_views_id"), table_name="saved_views")
    op.drop_table("saved_views")
