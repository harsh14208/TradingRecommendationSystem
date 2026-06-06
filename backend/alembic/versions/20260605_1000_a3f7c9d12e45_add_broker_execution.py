"""add broker execution — credentials on users + broker_orders table

Revision ID: a3f7c9d12e45
Revises: d507c85676a1
Create Date: 2026-06-05 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "a3f7c9d12e45"
down_revision = "d507c85676a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("auto_execute_qty_dollars", sa.Float(), nullable=True))
    op.add_column("users", sa.Column("alpaca_key_enc", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("alpaca_secret_enc", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("alpaca_account_type", sa.String(10), nullable=True))

    op.create_table(
        "broker_orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("signal_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("broker", sa.String(20), nullable=False),
        sa.Column("account_type", sa.String(10), nullable=False),
        sa.Column("alpaca_order_id", sa.String(50), nullable=True),
        sa.Column("symbol", sa.String(10), nullable=False),
        sa.Column("notional", sa.Float(), nullable=False),
        sa.Column("side", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="submitted"),
        sa.Column("error_msg", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_broker_orders_user_id", "broker_orders", ["user_id"])
    op.create_index("ix_broker_orders_signal_id", "broker_orders", ["signal_id"])
    op.create_index("ix_broker_orders_symbol", "broker_orders", ["symbol"])


def downgrade() -> None:
    op.drop_table("broker_orders")
    op.drop_column("users", "alpaca_account_type")
    op.drop_column("users", "alpaca_secret_enc")
    op.drop_column("users", "alpaca_key_enc")
    op.drop_column("users", "auto_execute_qty_dollars")
