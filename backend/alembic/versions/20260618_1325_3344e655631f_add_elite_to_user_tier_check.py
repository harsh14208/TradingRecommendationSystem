"""add_elite_to_user_tier_check

Revision ID: 3344e655631f
Revises: d977bdf487dc
Create Date: 2026-06-18 13:25:43.453495

"""

from typing import Union
from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "3344e655631f"
down_revision: Union[str, Sequence[str], None] = "d977bdf487dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add a check constraint allowing 'elite' on users.subscription_tier."""
    op.create_check_constraint(
        "ck_user_subscription_tier",
        "users",
        "subscription_tier IN ('free', 'basic', 'pro', 'elite')",
    )


def downgrade() -> None:
    """Remove the elite check constraint."""
    op.drop_constraint("ck_user_subscription_tier", "users", type_="check")
