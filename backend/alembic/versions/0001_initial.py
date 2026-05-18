"""Initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-05-18 00:00:00

"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "simulations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("target", sa.String(length=2048), nullable=False),
        sa.Column("charset", sa.String(length=4096), nullable=False),
        sa.Column("update_every", sa.Integer(), nullable=False),
        sa.Column("current", sa.String(length=2048), nullable=False, server_default=""),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("matched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("progress", sa.Float(), nullable=False, server_default="0"),
        sa.Column("elapsed", sa.Float(), nullable=False, server_default="0"),
        sa.Column("speed", sa.Float(), nullable=False, server_default="0"),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("task_id", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_simulations_status", "simulations", ["status"], unique=False)
    op.create_index("ix_simulations_created_at", "simulations", ["created_at"], unique=False)
    op.create_index("ix_simulations_task_id", "simulations", ["task_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_simulations_task_id", table_name="simulations")
    op.drop_index("ix_simulations_created_at", table_name="simulations")
    op.drop_index("ix_simulations_status", table_name="simulations")
    op.drop_table("simulations")
