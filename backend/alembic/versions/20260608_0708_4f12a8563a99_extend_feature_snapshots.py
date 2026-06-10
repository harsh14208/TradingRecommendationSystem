"""extend_feature_snapshots

Revision ID: 4f12a8563a99
Revises: 3acee01716f9
Create Date: 2026-06-08 07:08:45.202154

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4f12a8563a99"
down_revision: Union[str, Sequence[str], None] = "3acee01716f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("feature_snapshots", sa.Column("effective_time", sa.DateTime(), nullable=True))
    op.add_column("feature_snapshots", sa.Column("provider_timestamp", sa.DateTime(), nullable=True))
    op.add_column("feature_snapshots", sa.Column("provider", sa.String(length=50), nullable=True))
    op.add_column("feature_snapshots", sa.Column("feature_vector_hash", sa.String(length=64), nullable=True))
    op.add_column("feature_snapshots", sa.Column("signal_policy_version", sa.String(length=20), nullable=True))
    op.create_index(
        op.f("ix_feature_snapshots_feature_vector_hash"), "feature_snapshots", ["feature_vector_hash"], unique=False
    )
    op.create_index(
        op.f("ix_feature_snapshots_signal_policy_version"), "feature_snapshots", ["signal_policy_version"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_feature_snapshots_signal_policy_version"), table_name="feature_snapshots")
    op.drop_index(op.f("ix_feature_snapshots_feature_vector_hash"), table_name="feature_snapshots")
    op.drop_column("feature_snapshots", "signal_policy_version")
    op.drop_column("feature_snapshots", "feature_vector_hash")
    op.drop_column("feature_snapshots", "provider")
    op.drop_column("feature_snapshots", "provider_timestamp")
    op.drop_column("feature_snapshots", "effective_time")
