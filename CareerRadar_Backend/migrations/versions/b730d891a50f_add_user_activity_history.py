"""Add persisted user activity history.

Revision ID: b730d891a50f
Revises: f54b9f7d14c2
"""

from alembic import op
import sqlalchemy as sa


revision = "b730d891a50f"
down_revision = "f54b9f7d14c2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_activity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("endpoint", sa.String(length=240), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_activity_user_created",
        "user_activity",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_user_activity_action_created",
        "user_activity",
        ["action", "created_at"],
    )


def downgrade():
    op.drop_index("ix_user_activity_action_created", table_name="user_activity")
    op.drop_index("ix_user_activity_user_created", table_name="user_activity")
    op.drop_table("user_activity")
