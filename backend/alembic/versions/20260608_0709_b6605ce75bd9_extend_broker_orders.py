"""extend_broker_orders

Revision ID: b6605ce75bd9
Revises: 4f12a8563a99
Create Date: 2026-06-08 07:09:50.596891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6605ce75bd9'
down_revision: Union[str, Sequence[str], None] = '4f12a8563a99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("broker_orders", sa.Column("arrival_price", sa.Float(), nullable=True))
    op.add_column("broker_orders", sa.Column("nbbo_mid", sa.Float(), nullable=True))
    op.add_column("broker_orders", sa.Column("spread", sa.Float(), nullable=True))
    op.add_column("broker_orders", sa.Column("route_order_type", sa.String(length=50), nullable=True))
    op.add_column("broker_orders", sa.Column("requested_qty", sa.Float(), nullable=True))
    op.add_column("broker_orders", sa.Column("filled_qty", sa.Float(), nullable=True))
    op.add_column("broker_orders", sa.Column("avg_fill_price", sa.Float(), nullable=True))
    op.add_column("broker_orders", sa.Column("partial_fills", sa.JSON(), nullable=True))
    op.add_column("broker_orders", sa.Column("fees", sa.Float(), nullable=True))
    op.add_column("broker_orders", sa.Column("reject_reason", sa.Text(), nullable=True))
    op.add_column("broker_orders", sa.Column("stop_child_order_id", sa.String(length=50), nullable=True))
    op.add_column("broker_orders", sa.Column("target_child_order_id", sa.String(length=50), nullable=True))
    op.add_column("broker_orders", sa.Column("final_execution_status", sa.String(length=20), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("broker_orders", "final_execution_status")
    op.drop_column("broker_orders", "target_child_order_id")
    op.drop_column("broker_orders", "stop_child_order_id")
    op.drop_column("broker_orders", "reject_reason")
    op.drop_column("broker_orders", "fees")
    op.drop_column("broker_orders", "partial_fills")
    op.drop_column("broker_orders", "avg_fill_price")
    op.drop_column("broker_orders", "filled_qty")
    op.drop_column("broker_orders", "requested_qty")
    op.drop_column("broker_orders", "route_order_type")
    op.drop_column("broker_orders", "spread")
    op.drop_column("broker_orders", "nbbo_mid")
    op.drop_column("broker_orders", "arrival_price")

