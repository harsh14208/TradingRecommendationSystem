"""add_auto_execute_fields_to_users

Revision ID: 05fadc671532
Revises: 7a9277e42dc3
Create Date: 2026-05-26 08:55:36.083698

Tables password_reset_tokens, stripe_events, and signal_alerts are created by
the initial migration (7a9277e42dc3). This migration only adds the three
auto_execute columns to users and alpha to performance_snapshots.
"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "05fadc671532"
down_revision: Union[str, Sequence[str], None] = "7a9277e42dc3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_column_if_missing(table: str, col: sa.Column) -> None:
    """Add column only if it doesn't already exist in a dialect-safe way."""
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "sqlite":
        cols = {r[1] for r in bind.execute(sa.text(f"PRAGMA table_info({table})"))}
        if col.name not in cols:
            op.add_column(table, col)
    elif dialect == "postgresql":
        # PostgreSQL: query information_schema
        result = bind.execute(
            sa.text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name = :table AND column_name = :col"
            ),
            {"table": table, "col": col.name},
        )
        if result.scalar() is None:
            op.add_column(table, col)
    else:
        # Best-effort: add and let the DB raise if it already exists
        op.add_column(table, col)


def upgrade() -> None:
    """Upgrade schema."""
    _add_column_if_missing("performance_snapshots", sa.Column("alpha", sa.Float(), nullable=True))
    _add_column_if_missing("users", sa.Column("auto_execute", sa.Boolean(), server_default="0", nullable=False))
    _add_column_if_missing("users", sa.Column("auto_execute_min_conf", sa.Float(), nullable=True))
    _add_column_if_missing("users", sa.Column("auto_execute_broker", sa.String(length=50), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "auto_execute_broker")
    op.drop_column("users", "auto_execute_min_conf")
    op.drop_column("users", "auto_execute")
    op.drop_column("performance_snapshots", "alpha")
