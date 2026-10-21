"""Add email, phone, and multi-factor authentication fields."""

from alembic import op
import sqlalchemy as sa


revision = "2b4f9d8a1c60"
down_revision = ("f54b9f7d14c2", "b730d891a50f")
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("phone_number", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "users",
        sa.Column("phone_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    with op.batch_alter_table("users") as batch_op:
        batch_op.create_unique_constraint("uq_users_phone_number", ["phone_number"])
        batch_op.alter_column("email_verified", server_default=None)
        batch_op.alter_column("phone_verified", server_default=None)

    op.create_table(
        "auth_challenges",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("channel", sa.String(length=8), nullable=False),
        sa.Column("phone_number", sa.String(length=32), nullable=True),
        sa.Column("code_hash", sa.String(length=64), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auth_challenges_expires_at", "auth_challenges", ["expires_at"])


def downgrade():
    op.drop_index("ix_auth_challenges_expires_at", table_name="auth_challenges")
    op.drop_table("auth_challenges")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("uq_users_phone_number", type_="unique")
    op.drop_column("users", "phone_verified")
    op.drop_column("users", "email_verified")
    op.drop_column("users", "phone_number")
