"""add broker_order ai_eval_data

Revision ID: f47ac10b58cc
Revises: 91108bc4a0fe
Create Date: 2026-07-18 22:41:00.000000

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f47ac10b58cc"
down_revision: Union[str, Sequence[str], None] = "91108bc4a0fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add AI pre-execution evaluation snapshot to broker_orders."""
    op.add_column("broker_orders", sa.Column("ai_eval_data", sa.JSON(), nullable=True))


def downgrade() -> None:
    """Remove AI evaluation snapshot column."""
    op.drop_column("broker_orders", "ai_eval_data")
