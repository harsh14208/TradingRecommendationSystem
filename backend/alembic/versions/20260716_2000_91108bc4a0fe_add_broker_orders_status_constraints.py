"""add broker_orders status CHECK and alpaca_order_id UNIQUE constraints

Revision ID: 91108bc4a0fe
Revises: 743fdc612c4b
Create Date: 2026-07-16 20:00:00.000000

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "91108bc4a0fe"
down_revision: Union[str, Sequence[str], None] = "743fdc612c4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """models.py has declared ck_broker_order_status and
    uq_broker_orders_alpaca_order_id since broker_orders was first added, but
    no prior migration ever created them — the live DB has been running with
    neither constraint. Before adding the CHECK, normalize any raw
    broker-status values (e.g. "pending_new") that predate the
    _normalize_broker_status() fix so the constraint can actually be applied.
    """
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE broker_orders SET status = 'canceled' "
            "WHERE lower(status) IN ('cancelled', 'expired', 'done_for_day')"
        )
    )
    conn.execute(sa.text("UPDATE broker_orders SET status = 'filled' WHERE lower(status) = 'partially_filled'"))
    conn.execute(
        sa.text(
            "UPDATE broker_orders SET status = 'submitted' WHERE lower(status) NOT IN "
            "('submitted', 'filled', 'rejected', 'error', 'orphan', 'canceled')"
        )
    )

    op.create_check_constraint(
        "ck_broker_order_status",
        "broker_orders",
        "status IN ('submitted','filled','rejected','error','orphan','canceled')",
    )
    op.create_unique_constraint("uq_broker_orders_alpaca_order_id", "broker_orders", ["alpaca_order_id"])


def downgrade() -> None:
    op.drop_constraint("uq_broker_orders_alpaca_order_id", "broker_orders", type_="unique")
    op.drop_constraint("ck_broker_order_status", "broker_orders", type_="check")
