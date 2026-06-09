"""add short_interest_biweekly (Polygon FINRA short-interest alt-data)

Revision ID: d8e9f0a1b2c3
Revises: c7d8e9f0a1b2
Create Date: 2026-06-09 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "d8e9f0a1b2c3"
down_revision = "c7d8e9f0a1b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "short_interest_biweekly",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(length=12), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("short_interest", sa.Integer(), nullable=True),
        sa.Column("days_to_cover", sa.Float(), nullable=True),
        sa.Column("avg_daily_volume", sa.Integer(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticker", "date", name="uq_short_interest_ticker_date"),
    )
    op.create_index("ix_short_interest_ticker_date", "short_interest_biweekly", ["ticker", "date"])


def downgrade() -> None:
    op.drop_index("ix_short_interest_ticker_date", table_name="short_interest_biweekly")
    op.drop_table("short_interest_biweekly")
