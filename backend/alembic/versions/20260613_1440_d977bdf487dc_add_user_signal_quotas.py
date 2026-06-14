"""add user signal quotas

Adds a daily per-user signal view quota table used to tier-gate
/api/signals and /api/signals/history.

Revision ID: d977bdf487dc
Revises: 17c3c714fe68
Create Date: 2026-06-13 14:40:00.000000
"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d977bdf487dc"
down_revision: Union[str, Sequence[str], None] = "17c3c714fe68"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NOW = sa.text("CURRENT_TIMESTAMP")


def upgrade() -> None:
    """Create user_signal_quotas table."""
    op.create_table(
        "user_signal_quotas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("window_start", sa.DateTime(), nullable=False),
        sa.Column("views_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=_NOW),
        sa.Column("updated_at", sa.DateTime(), server_default=_NOW),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_user_signal_quotas_user_id"),
    )
    op.create_index("ix_user_signal_quotas_user_id", "user_signal_quotas", ["user_id"], unique=True)


def downgrade() -> None:
    """Drop user_signal_quotas table."""
    op.drop_index("ix_user_signal_quotas_user_id", table_name="user_signal_quotas")
    op.drop_table("user_signal_quotas")
