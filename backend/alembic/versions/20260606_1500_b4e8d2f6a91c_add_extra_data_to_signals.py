"""add extra_data to signals

Revision ID: b4e8d2f6a91c
Revises: a3f7c9d12e45
Create Date: 2026-06-06 15:00:00.000000

extra_data is a JSON blob of delivery-gate inputs (hasMr, vix,
crossAssetHeadwinds, daysToExDiv) that have no dedicated column. eod_batch_send()
reconstructs the signal dict from the DB row, so without these the EOD delivery
path silently mis-evaluates the BUY gates (ACT-4c): hasMr defaults to False →
every EOD BUY was blocked as "no MR setup", while §54/§55/ex-div no-op'd.
"""

from alembic import op
import sqlalchemy as sa

revision = "b4e8d2f6a91c"
down_revision = "a3f7c9d12e45"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("signals", sa.Column("extra_data", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("signals", "extra_data")
