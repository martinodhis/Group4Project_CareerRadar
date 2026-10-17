"""Add account, profile, and saved-job fields used by the REST API."""

from alembic import op
import sqlalchemy as sa


revision = "f54b9f7d14c2"
down_revision = "ce9b5f8d7421"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("first_name", sa.String(length=120), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(length=120), nullable=True))
    op.add_column("users", sa.Column("last_login", sa.DateTime(timezone=True), nullable=True))
    op.add_column("profiles", sa.Column("current_job_title", sa.String(), nullable=True))
    op.add_column("profiles", sa.Column("career_level", sa.String(), nullable=True))
    op.add_column(
        "profiles",
        sa.Column("years_of_experience", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "profiles",
        sa.Column("profile_completion", sa.Integer(), nullable=False, server_default="0"),
    )
    with op.batch_alter_table("profiles") as batch_op:
        batch_op.alter_column("years_of_experience", server_default=None)
        batch_op.alter_column("profile_completion", server_default=None)
    op.add_column("saved_jobs", sa.Column("notes", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("saved_jobs", "notes")
    op.drop_column("profiles", "profile_completion")
    op.drop_column("profiles", "years_of_experience")
    op.drop_column("profiles", "career_level")
    op.drop_column("profiles", "current_job_title")
    op.drop_column("users", "last_login")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
