"""add options engine columns

Revision ID: 119672a8089d
Revises: a6e62f2c6ed3
Create Date: 2026-06-18 21:57:55.568461

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "119672a8089d"
down_revision: Union[str, Sequence[str], None] = "a6e62f2c6ed3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Signal payload columns for the options VRP engine.
    op.add_column("signals", sa.Column("option_strategy", sa.String(length=30), nullable=True))
    op.add_column("signals", sa.Column("option_legs", sa.JSON(), nullable=True))
    op.add_column("signals", sa.Column("option_underlying_action", sa.String(length=10), nullable=True))
    op.add_column("signals", sa.Column("option_richness", sa.Float(), nullable=True))
    op.add_column("signals", sa.Column("option_impl_move", sa.Float(), nullable=True))
    op.add_column("signals", sa.Column("option_forecast_move", sa.Float(), nullable=True))
    op.add_column("signals", sa.Column("option_exp_gain", sa.Float(), nullable=True))
    op.add_column("signals", sa.Column("option_max_loss", sa.Float(), nullable=True))
    op.add_column("signals", sa.Column("option_days_to_earnings", sa.Integer(), nullable=True))

    # User-level option execution mode & risk settings.
    op.add_column(
        "users",
        sa.Column("options_mode", sa.String(length=10), server_default="signal", nullable=False),
    )
    op.add_column("users", sa.Column("options_capital", sa.Float(), nullable=True))
    op.add_column("users", sa.Column("options_risk_per_trade", sa.Float(), nullable=True))
    op.add_column("users", sa.Column("options_max_book_risk", sa.Float(), nullable=True))
    op.add_column("users", sa.Column("options_max_positions", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("options_max_iv_sell", sa.Float(), nullable=True))
    op.create_check_constraint(
        "ck_user_options_mode",
        "users",
        sa.text("options_mode IN ('none', 'signal', 'paper', 'live')"),
    )

    # OCC option symbols are ~21 characters; stock tickers fit in the original 10.
    dialect = op.get_bind().dialect.name
    if dialect == "sqlite":
        with op.batch_alter_table("broker_orders") as batch_op:
            batch_op.alter_column(
                "symbol",
                existing_type=sa.String(length=10),
                type_=sa.String(length=24),
                existing_nullable=False,
            )
    else:
        op.alter_column(
            "broker_orders",
            "symbol",
            existing_type=sa.VARCHAR(length=10),
            type_=sa.String(length=24),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema."""
    dialect = op.get_bind().dialect.name
    if dialect == "sqlite":
        with op.batch_alter_table("broker_orders") as batch_op:
            batch_op.alter_column(
                "symbol",
                existing_type=sa.String(length=24),
                type_=sa.String(length=10),
                existing_nullable=False,
            )
    else:
        op.alter_column(
            "broker_orders",
            "symbol",
            existing_type=sa.String(length=24),
            type_=sa.VARCHAR(length=10),
            existing_nullable=False,
        )

    op.drop_constraint("ck_user_options_mode", "users", type_="check")
    op.drop_column("users", "options_max_iv_sell")
    op.drop_column("users", "options_max_positions")
    op.drop_column("users", "options_max_book_risk")
    op.drop_column("users", "options_risk_per_trade")
    op.drop_column("users", "options_capital")
    op.drop_column("users", "options_mode")

    op.drop_column("signals", "option_days_to_earnings")
    op.drop_column("signals", "option_max_loss")
    op.drop_column("signals", "option_exp_gain")
    op.drop_column("signals", "option_forecast_move")
    op.drop_column("signals", "option_impl_move")
    op.drop_column("signals", "option_richness")
    op.drop_column("signals", "option_underlying_action")
    op.drop_column("signals", "option_legs")
    op.drop_column("signals", "option_strategy")
