"""add confidence ontology columns

Revision ID: 700fef99ff87
Revises: 9682ab65249c
Create Date: 2026-06-27 15:42:00.000000

Splits the overloaded `confidence` field into explicit ontology columns:
- alpha_score: raw composite score
- calibrated_probability: calibrated win probability (immutable after calibration)
- display_confidence: user-facing confidence (may include peer/ranking tilts)
- rank_score / rank_percentile: cross-sectional ordering metadata

Existing `confidence` remains as the backward-compatible alias for display
confidence.  `raw_confidence` is retained for pre-calibration probability.
"""

from alembic import op
import sqlalchemy as sa

revision = "700fef99ff87"
down_revision = "9682ab65249c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("signals", sa.Column("calibrated_probability", sa.Float(), nullable=True))
    op.add_column("signals", sa.Column("display_confidence", sa.Float(), nullable=True))
    op.add_column("signals", sa.Column("alpha_score", sa.Float(), nullable=True))
    op.add_column("signals", sa.Column("rank_score", sa.Float(), nullable=True))
    op.add_column("signals", sa.Column("rank_percentile", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("signals", "rank_percentile")
    op.drop_column("signals", "rank_score")
    op.drop_column("signals", "alpha_score")
    op.drop_column("signals", "display_confidence")
    op.drop_column("signals", "calibrated_probability")
