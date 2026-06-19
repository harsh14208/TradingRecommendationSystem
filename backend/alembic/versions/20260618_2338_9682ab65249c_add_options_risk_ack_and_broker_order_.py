"""add_options_risk_ack_and_broker_order_option_columns

Revision ID: 9682ab65249c
Revises: 119672a8089d
Create Date: 2026-06-18 23:38:23.106919

"""

from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9682ab65249c"
down_revision: Union[str, Sequence[str], None] = "119672a8089d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("broker_orders", sa.Column("option_legs", sa.JSON(), nullable=True))
    op.add_column("broker_orders", sa.Column("realized_pnl", sa.Float(), nullable=True))
    op.add_column("broker_orders", sa.Column("unrealized_pnl", sa.Float(), nullable=True))
    op.add_column("users", sa.Column("options_risk_acknowledged", sa.Boolean(), server_default="0", nullable=False))
    op.add_column("users", sa.Column("options_risk_acknowledged_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "options_risk_acknowledged_at")
    op.drop_column("users", "options_risk_acknowledged")
    op.drop_column("broker_orders", "unrealized_pnl")
    op.drop_column("broker_orders", "realized_pnl")
    op.drop_column("broker_orders", "option_legs")
