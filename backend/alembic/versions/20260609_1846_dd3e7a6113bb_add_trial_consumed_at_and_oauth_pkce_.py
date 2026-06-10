"""add_trial_consumed_at_and_oauth_pkce_columns

Revision ID: dd3e7a6113bb
Revises: d8e9f0a1b2c3
Create Date: 2026-06-09 18:46:06.778941

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dd3e7a6113bb"
down_revision: Union[str, Sequence[str], None] = "d8e9f0a1b2c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add trial_consumed_at to users and PKCE columns to oauth_state."""
    op.add_column("users", sa.Column("trial_consumed_at", sa.DateTime(), nullable=True))
    op.add_column("oauth_states", sa.Column("code_challenge", sa.String(length=255), nullable=True))
    op.add_column("oauth_states", sa.Column("code_verifier", sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Remove columns added in upgrade."""
    op.drop_column("oauth_states", "code_verifier")
    op.drop_column("oauth_states", "code_challenge")
    op.drop_column("users", "trial_consumed_at")
