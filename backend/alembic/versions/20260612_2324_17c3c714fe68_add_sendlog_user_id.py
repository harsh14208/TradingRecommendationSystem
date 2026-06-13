"""add_sendlog_user_id

Revision ID: 17c3c714fe68
Revises: 404971b9f841
Create Date: 2026-06-12 23:24:40.109389

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "17c3c714fe68"
down_revision: Union[str, Sequence[str], None] = "404971b9f841"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add nullable user_id to send_log for per-user delivery log filtering."""
    op.add_column("send_log", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_send_log_user_id"), "send_log", ["user_id"], unique=False)
    op.create_foreign_key(None, "send_log", "users", ["user_id"], ["id"])


def downgrade() -> None:
    """Remove user_id from send_log."""
    op.drop_constraint(None, "send_log", type_="foreignkey")
    op.drop_index(op.f("ix_send_log_user_id"), table_name="send_log")
    op.drop_column("send_log", "user_id")
