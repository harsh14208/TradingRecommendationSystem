"""add raw_score to signals

Revision ID: d507c85676a1
Revises: 05fadc671532
Create Date: 2026-05-30 12:00:00.000000

raw_score stores the pre-heuristic alpha score from _assemble_signal().
Keeping it separate from `confidence` prevents the circular dependency where
the live XGBoost model would learn from its own Platt-scaled output.
"""

from alembic import op
import sqlalchemy as sa

revision = "d507c85676a1"
down_revision = "05fadc671532"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("signals", sa.Column("raw_score", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("signals", "raw_score")
