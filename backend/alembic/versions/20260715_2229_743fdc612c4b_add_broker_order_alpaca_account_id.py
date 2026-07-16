"""add broker_order alpaca_account_id

Revision ID: 743fdc612c4b
Revises: cb10dcb899b3
Create Date: 2026-07-15 22:29:11.783213

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "743fdc612c4b"
down_revision: Union[str, Sequence[str], None] = "cb10dcb899b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Alpaca account id to broker_orders so stale rows can be ignored after a paper-account reset."""
    op.add_column("broker_orders", sa.Column("alpaca_account_id", sa.String(length=50), nullable=True))
    op.create_index(op.f("ix_broker_orders_alpaca_account_id"), "broker_orders", ["alpaca_account_id"], unique=False)


def downgrade() -> None:
    """Remove Alpaca account id column."""
    op.drop_index(op.f("ix_broker_orders_alpaca_account_id"), table_name="broker_orders")
    op.drop_column("broker_orders", "alpaca_account_id")
