"""add_orats_daily_features

Revision ID: a6e62f2c6ed3
Revises: 3344e655631f
Create Date: 2026-06-18 12:15:00.000000

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a6e62f2c6ed3"
down_revision: Union[str, Sequence[str], None] = "3344e655631f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "orats_daily_features",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(length=12), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("stk_px", sa.Float(), nullable=True),
        sa.Column("atm_iv_30d", sa.Float(), nullable=True),
        sa.Column("iv_25d_call", sa.Float(), nullable=True),
        sa.Column("iv_25d_put", sa.Float(), nullable=True),
        sa.Column("pc_iv_skew", sa.Float(), nullable=True),
        sa.Column("gex", sa.Float(), nullable=True),
        sa.Column("dex", sa.Float(), nullable=True),
        sa.Column("pc_volume_ratio", sa.Float(), nullable=True),
        sa.Column("pc_oi_ratio", sa.Float(), nullable=True),
        sa.Column("total_opt_volume", sa.Float(), nullable=True),
        sa.Column("total_opt_oi", sa.Float(), nullable=True),
        sa.Column("zero_dte_put_volume", sa.Float(), nullable=True),
        sa.Column("iv_rank_252", sa.Float(), nullable=True),
        sa.Column("iv_pctile_252", sa.Float(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticker", "date", name="uq_orats_daily_features_ticker_date"),
    )
    op.create_index(
        "ix_orats_daily_features_ticker_date",
        "orats_daily_features",
        ["ticker", "date"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_orats_daily_features_ticker_date", table_name="orats_daily_features")
    op.drop_table("orats_daily_features")
