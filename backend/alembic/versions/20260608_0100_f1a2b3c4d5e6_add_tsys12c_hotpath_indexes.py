"""add_tsys12c_hotpath_indexes

TSYS-12c index audit: add indexes on frequently-filtered hot-path columns
(signals.is_sent, broker_orders.status, provider_response_samples.created_at).

Revision ID: f1a2b3c4d5e6
Revises: 5864d5cdab47
Create Date: 2026-06-08 01:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "5864d5cdab47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(op.f("ix_signals_is_sent"), "signals", ["is_sent"], unique=False)
    op.create_index(op.f("ix_broker_orders_status"), "broker_orders", ["status"], unique=False)
    op.create_index(
        op.f("ix_provider_response_samples_created_at"),
        "provider_response_samples",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_provider_response_samples_created_at"), table_name="provider_response_samples")
    op.drop_index(op.f("ix_broker_orders_status"), table_name="broker_orders")
    op.drop_index(op.f("ix_signals_is_sent"), table_name="signals")
