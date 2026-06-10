"""add_signal_raw_confidence

Revision ID: abc123def456
Revises: 8dab442e6933
Create Date: 2026-06-10 00:00:00.000000

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "abc123def456"
down_revision: Union[str, Sequence[str], None] = "8dab442e6933"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add raw_confidence column to signals table."""
    op.add_column("signals", sa.Column("raw_confidence", sa.Float(), nullable=True))


def downgrade() -> None:
    """Remove raw_confidence column from signals table."""
    op.drop_column("signals", "raw_confidence")
