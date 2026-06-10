"""add_research_experiment_table

Revision ID: 3acee01716f9
Revises: f1a2b3c4d5e6
Create Date: 2026-06-08 07:04:08.427903

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3acee01716f9"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "research_experiments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("experiment_type", sa.String(length=50), nullable=False),
        sa.Column("hypothesis", sa.Text(), nullable=False),
        sa.Column("universe", sa.JSON(), nullable=True),
        sa.Column("data_version", sa.String(length=50), nullable=False),
        sa.Column("git_sha", sa.String(length=40), nullable=True),
        sa.Column("search_space", sa.JSON(), nullable=True),
        sa.Column("number_of_trials", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_metrics", sa.JSON(), nullable=True),
        sa.Column("oos_metrics", sa.JSON(), nullable=True),
        sa.Column("dsr_pbo", sa.JSON(), nullable=True),
        sa.Column("decision", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("promotion_status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_research_experiments_experiment_type"), "research_experiments", ["experiment_type"], unique=False
    )
    op.create_index(op.f("ix_research_experiments_decision"), "research_experiments", ["decision"], unique=False)
    op.create_index(
        op.f("ix_research_experiments_promotion_status"), "research_experiments", ["promotion_status"], unique=False
    )
    op.create_index(op.f("ix_research_experiments_created_at"), "research_experiments", ["created_at"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_research_experiments_created_at"), table_name="research_experiments")
    op.drop_index(op.f("ix_research_experiments_promotion_status"), table_name="research_experiments")
    op.drop_index(op.f("ix_research_experiments_decision"), table_name="research_experiments")
    op.drop_index(op.f("ix_research_experiments_experiment_type"), table_name="research_experiments")
    op.drop_table("research_experiments")
