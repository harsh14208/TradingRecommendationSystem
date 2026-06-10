"""add_weekly_digest_sent_unique_week

Revision ID: 8dab442e6933
Revises: dd3e7a6113bb
Create Date: 2026-06-09 21:58:07.237080

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8dab442e6933"
down_revision: Union[str, Sequence[str], None] = "dd3e7a6113bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add digest_week column and unique constraint to prevent duplicate weekly digest markers."""
    op.add_column("background_job_runs", sa.Column("digest_week", sa.String(10), nullable=True))
    op.create_index(
        "ix_background_job_runs_digest_week",
        "background_job_runs",
        ["digest_week"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_background_job_runs_weekly_digest_week",
        "background_job_runs",
        ["job_name", "digest_week"],
    )


def downgrade() -> None:
    """Remove digest_week column and unique constraint."""
    op.drop_constraint("uq_background_job_runs_weekly_digest_week", "background_job_runs", type_="unique")
    op.drop_index("ix_background_job_runs_digest_week", table_name="background_job_runs")
    op.drop_column("background_job_runs", "digest_week")
