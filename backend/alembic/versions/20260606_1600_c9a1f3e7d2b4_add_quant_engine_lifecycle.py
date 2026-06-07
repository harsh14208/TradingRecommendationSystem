"""add quant-engine lifecycle tables (additive)

Adds a normalized quant-engine spine layered additively on top of the existing
signal-delivery schema — securities master, point-in-time market data + features,
an execution fill ledger, position accounting, and daily P&L / risk marks. No
existing table is modified.

Tables: instruments, bars, feature_snapshots, fills, positions, pnl_daily,
risk_metrics.

Revision ID: c9a1f3e7d2b4
Revises: b4e8d2f6a91c
Create Date: 2026-06-06 16:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "c9a1f3e7d2b4"
down_revision = "b4e8d2f6a91c"
branch_labels = None
depends_on = None

_NOW = sa.text("CURRENT_TIMESTAMP")


def upgrade() -> None:
    # ── instruments — securities master ──────────────────────────────────────
    op.create_table(
        "instruments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(12), nullable=False),
        sa.Column("name", sa.String(120), nullable=True),
        sa.Column("asset_type", sa.String(16), nullable=False, server_default="equity"),
        sa.Column("sector", sa.String(40), nullable=True),
        sa.Column("industry", sa.String(80), nullable=True),
        sa.Column("sector_etf", sa.String(10), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("market_cap", sa.Float(), nullable=True),
        sa.Column("adv_usd", sa.Float(), nullable=True),
        sa.Column("beta", sa.Float(), nullable=True),
        sa.Column("shares_outstanding", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), server_default=_NOW),
        sa.Column("updated_at", sa.DateTime(), server_default=_NOW),
        sa.PrimaryKeyConstraint("id"),
    )
    # Single unique index — matches Instrument.ticker = Column(unique=True, index=True).
    op.create_index("ix_instruments_ticker", "instruments", ["ticker"], unique=True)

    # ── bars — OHLCV time-series ─────────────────────────────────────────────
    op.create_table(
        "bars",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("instrument_id", sa.Integer(), nullable=False),
        sa.Column("interval", sa.String(4), nullable=False, server_default="1d"),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Float(), nullable=False, server_default="0"),
        sa.Column("vwap", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["instrument_id"], ["instruments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("instrument_id", "interval", "ts", name="uq_bars_instrument_interval_ts"),
    )
    op.create_index("ix_bars_instrument_ts", "bars", ["instrument_id", "ts"])

    # ── feature_snapshots — point-in-time alpha features ─────────────────────
    op.create_table(
        "feature_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("instrument_id", sa.Integer(), nullable=False),
        sa.Column("signal_id", sa.Integer(), nullable=True),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("rsi", sa.Float(), nullable=True),
        sa.Column("bb_pct_b", sa.Float(), nullable=True),
        sa.Column("ibs", sa.Float(), nullable=True),
        sa.Column("vwap_pct", sa.Float(), nullable=True),
        sa.Column("atr_pct", sa.Float(), nullable=True),
        sa.Column("zscore", sa.Float(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("features", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=_NOW),
        sa.ForeignKeyConstraint(["instrument_id"], ["instruments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feature_snapshots_signal_id", "feature_snapshots", ["signal_id"])
    op.create_index("ix_feature_snapshots_instrument_ts", "feature_snapshots", ["instrument_id", "ts"])

    # ── fills — execution ledger (children of broker_orders) ─────────────────
    op.create_table(
        "fills",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("broker_order_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("instrument_id", sa.Integer(), nullable=True),
        sa.Column("side", sa.String(4), nullable=False),
        sa.Column("qty", sa.Float(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("commission", sa.Float(), nullable=False, server_default="0"),
        sa.Column("slippage_bps", sa.Float(), nullable=True),
        sa.Column("broker_fill_id", sa.String(64), nullable=True),
        sa.Column("filled_at", sa.DateTime(), nullable=False, server_default=_NOW),
        sa.ForeignKeyConstraint(["broker_order_id"], ["broker_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["instrument_id"], ["instruments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fills_broker_order_id", "fills", ["broker_order_id"])
    op.create_index("ix_fills_user_id", "fills", ["user_id"])
    op.create_index("ix_fills_instrument_id", "fills", ["instrument_id"])
    op.create_index("ix_fills_filled_at", "fills", ["filled_at"])

    # ── positions — accounting unit ──────────────────────────────────────────
    op.create_table(
        "positions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("instrument_id", sa.Integer(), nullable=False),
        sa.Column("signal_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(8), nullable=False, server_default="open"),
        sa.Column("side", sa.String(5), nullable=False, server_default="long"),
        sa.Column("qty", sa.Float(), nullable=False, server_default="0"),
        sa.Column("avg_entry_price", sa.Float(), nullable=False),
        sa.Column("avg_exit_price", sa.Float(), nullable=True),
        sa.Column("cost_basis", sa.Float(), nullable=False, server_default="0"),
        sa.Column("last_price", sa.Float(), nullable=True),
        sa.Column("market_value", sa.Float(), nullable=True),
        sa.Column("unrealized_pnl", sa.Float(), nullable=True),
        sa.Column("realized_pnl", sa.Float(), nullable=False, server_default="0"),
        sa.Column("stop", sa.Float(), nullable=True),
        sa.Column("target", sa.Float(), nullable=True),
        sa.Column("opened_at", sa.DateTime(), server_default=_NOW),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=_NOW),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["instrument_id"], ["instruments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_positions_user_id", "positions", ["user_id"])
    op.create_index("ix_positions_instrument_id", "positions", ["instrument_id"])
    op.create_index("ix_positions_signal_id", "positions", ["signal_id"])
    op.create_index("ix_positions_opened_at", "positions", ["opened_at"])
    op.create_index("ix_positions_user_status", "positions", ["user_id", "status"])

    # ── pnl_daily — equity curve / drawdown ──────────────────────────────────
    op.create_table(
        "pnl_daily",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("equity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("cash", sa.Float(), nullable=True),
        sa.Column("realized_pnl", sa.Float(), nullable=False, server_default="0"),
        sa.Column("unrealized_pnl", sa.Float(), nullable=False, server_default="0"),
        sa.Column("gross_exposure", sa.Float(), nullable=True),
        sa.Column("net_exposure", sa.Float(), nullable=True),
        sa.Column("drawdown_pct", sa.Float(), nullable=True),
        sa.Column("n_positions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=_NOW),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date", name="uq_pnl_daily_user_date"),
    )
    op.create_index("ix_pnl_daily_user_id", "pnl_daily", ["user_id"])

    # ── risk_metrics — daily portfolio risk ──────────────────────────────────
    op.create_table(
        "risk_metrics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("portfolio_beta", sa.Float(), nullable=True),
        sa.Column("portfolio_vol", sa.Float(), nullable=True),
        sa.Column("var_95", sa.Float(), nullable=True),
        sa.Column("max_sector_pct", sa.Float(), nullable=True),
        sa.Column("avg_pairwise_corr", sa.Float(), nullable=True),
        sa.Column("gross_leverage", sa.Float(), nullable=True),
        sa.Column("net_leverage", sa.Float(), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=_NOW),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date", name="uq_risk_metrics_user_date"),
    )
    op.create_index("ix_risk_metrics_user_id", "risk_metrics", ["user_id"])


def downgrade() -> None:
    op.drop_table("risk_metrics")
    op.drop_table("pnl_daily")
    op.drop_table("positions")
    op.drop_table("fills")
    op.drop_table("feature_snapshots")
    op.drop_table("bars")
    op.drop_table("instruments")
