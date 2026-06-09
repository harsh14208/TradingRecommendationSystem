"""add short_volume_daily (Polygon FINRA short-volume alt-data)

Revision ID: c7d8e9f0a1b2
Revises: a1b2c3d4e5f6
Create Date: 2026-06-09 01:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "c7d8e9f0a1b2"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "short_volume_daily",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(length=12), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("short_volume_ratio", sa.Float(), nullable=True),
        sa.Column("short_volume", sa.Integer(), nullable=True),
        sa.Column("total_volume", sa.Integer(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticker", "date", name="uq_short_volume_ticker_date"),
    )
    op.create_index("ix_short_volume_ticker_date", "short_volume_daily", ["ticker", "date"])


def downgrade() -> None:
    op.drop_index("ix_short_volume_ticker_date", table_name="short_volume_daily")
    op.drop_table("short_volume_daily")
