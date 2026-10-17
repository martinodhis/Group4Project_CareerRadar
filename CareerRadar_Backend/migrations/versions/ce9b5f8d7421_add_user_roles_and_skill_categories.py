"""Add user roles and skill categories.

Revision ID: ce9b5f8d7421
Revises: adb3694cc309
"""

from alembic import op
import sqlalchemy as sa


revision = "ce9b5f8d7421"
down_revision = "adb3694cc309"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), server_default="USER", nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.add_column("skills", sa.Column("category", sa.String(length=100), nullable=True))
    op.add_column(
        "user_skills",
        sa.Column("proficiency_level", sa.String(length=32), server_default="INTERMEDIATE", nullable=False),
    )
    op.add_column(
        "user_skills",
        sa.Column("years_experience", sa.Float(), server_default="0", nullable=False),
    )
    op.add_column(
        "user_skills",
        sa.Column("is_primary", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("role", server_default=None)
        batch_op.alter_column("is_active", server_default=None)
    with op.batch_alter_table("user_skills") as batch_op:
        batch_op.alter_column("proficiency_level", server_default=None)
        batch_op.alter_column("years_experience", server_default=None)
        batch_op.alter_column("is_primary", server_default=None)


def downgrade():
    op.drop_column("user_skills", "is_primary")
    op.drop_column("user_skills", "years_experience")
    op.drop_column("user_skills", "proficiency_level")
    op.drop_column("skills", "category")
    op.drop_column("users", "is_active")
    op.drop_column("users", "role")
