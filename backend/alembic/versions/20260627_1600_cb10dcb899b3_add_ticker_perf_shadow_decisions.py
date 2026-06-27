"""add ticker perf shadow decisions

Revision ID: cb10dcb899b3
Revises: 700fef99ff87
Create Date: 2026-06-27 16:00:00.000000

Dedicated table for the Stage B shadow experiment comparing the legacy static
defensive-ticker blocklist against the new decay-weighted
TickerPerformanceGate.  Outcome columns are backfilled after signals resolve.
"""

from alembic import op
import sqlalchemy as sa

revision = "cb10dcb899b3"
down_revision = "700fef99ff87"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ticker_perf_shadow_decisions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "signal_id", sa.Integer(), sa.ForeignKey("signals.id", ondelete="CASCADE"), nullable=True, index=True
        ),
        sa.Column("ticker", sa.String(10), nullable=False, index=True),
        sa.Column("action", sa.String(4), nullable=False),
        sa.Column("sector_etf", sa.String(10), nullable=True),
        sa.Column("scan_ts", sa.DateTime(), nullable=False, index=True),
        sa.Column("static_blocked", sa.Boolean(), nullable=False),
        sa.Column("dynamic_decision", sa.String(10), nullable=False),
        sa.Column("dynamic_reason", sa.Text(), nullable=True),
        sa.Column("dynamic_n", sa.Integer(), nullable=True),
        sa.Column("dynamic_decay_wr", sa.Float(), nullable=True),
        sa.Column("dynamic_raw_wr", sa.Float(), nullable=True),
        sa.Column("dynamic_size_mult", sa.Float(), nullable=True),
        sa.Column("hold_days", sa.Integer(), nullable=True),
        sa.Column("outcome_pct_7d", sa.Float(), nullable=True),
        sa.Column("outcome_pct_hold", sa.Float(), nullable=True),
        sa.Column("outcome_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("ticker_perf_shadow_decisions")
