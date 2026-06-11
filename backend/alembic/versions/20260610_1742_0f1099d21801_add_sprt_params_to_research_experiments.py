"""add_sprt_params_to_research_experiments

Revision ID: 0f1099d21801
Revises: 4a7f6b33eb49
Create Date: 2026-06-10 17:42:00.702440

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0f1099d21801"
down_revision: Union[str, Sequence[str], None] = "4a7f6b33eb49"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("research_experiments", sa.Column("sprt_params", sa.JSON(), nullable=True))
    op.add_column("research_experiments", sa.Column("sprt_state", sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("research_experiments", "sprt_state")
    op.drop_column("research_experiments", "sprt_params")
