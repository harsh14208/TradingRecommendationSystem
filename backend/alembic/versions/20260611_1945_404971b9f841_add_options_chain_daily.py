"""add_options_chain_daily

Revision ID: 404971b9f841
Revises: bf79f41b6f1d
Create Date: 2026-06-11 19:45:27.751740

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "404971b9f841"
down_revision: Union[str, Sequence[str], None] = "bf79f41b6f1d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "options_chain_daily",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(length=12), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("contract_count", sa.Integer(), nullable=True),
        sa.Column("put_call_ratio", sa.Float(), nullable=True),
        sa.Column("total_volume", sa.Integer(), nullable=True),
        sa.Column("total_open_interest", sa.Integer(), nullable=True),
        sa.Column("avg_iv", sa.Float(), nullable=True),
        sa.Column("near_iv", sa.Float(), nullable=True),
        sa.Column("far_iv", sa.Float(), nullable=True),
        sa.Column("iv_term_spike", sa.Float(), nullable=True),
        sa.Column("iv_rank", sa.Float(), nullable=True),
        sa.Column("skew_25d", sa.Float(), nullable=True),
        sa.Column("max_pain", sa.Float(), nullable=True),
        sa.Column("net_gex", sa.Float(), nullable=True),
        sa.Column("spot", sa.Float(), nullable=True),
        sa.Column("source", sa.String(length=20), server_default="cboe", nullable=True),
        sa.Column("contracts_snapshot", sa.JSON(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticker", "date", name="uq_options_chain_ticker_date"),
    )
    op.create_index("ix_options_chain_ticker_date", "options_chain_daily", ["ticker", "date"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_options_chain_ticker_date", table_name="options_chain_daily")
    op.drop_table("options_chain_daily")
