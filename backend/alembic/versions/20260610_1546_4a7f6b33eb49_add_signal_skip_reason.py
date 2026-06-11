"""add_signal_skip_reason

Revision ID: 4a7f6b33eb49
Revises: abc123def456
Create Date: 2026-06-10 15:46:42.422278

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4a7f6b33eb49"
down_revision: Union[str, Sequence[str], None] = "abc123def456"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("signals", sa.Column("skip_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("signals", "skip_reason")
