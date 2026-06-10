"""dedup provider_health_scorecards + unique (provider, endpoint)

Fixes the 23k/day "Multiple rows were found when one or none was required"
error flood: record_endpoint_call() did a select-then-insert with no unique
constraint, so concurrent calls for a hot endpoint (polygon /v2/aggs) raced
and created duplicate rows. Every subsequent scalar_one_or_none() then raised.

This migration collapses each (provider, endpoint) group to its lowest id and
adds uq_provider_endpoint so duplicates can never reappear.

Revision ID: a1b2c3d4e5f6
Revises: b6605ce75bd9
Create Date: 2026-06-08 08:00:00.000000

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "b6605ce75bd9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Drop duplicate rows, keeping the lowest id per (provider, endpoint).
    # Use dialect-specific syntax to support both PostgreSQL and SQLite.
    if dialect == "postgresql":
        op.execute(
            """
            DELETE FROM provider_health_scorecards a
            USING provider_health_scorecards b
            WHERE a.provider = b.provider
              AND a.endpoint = b.endpoint
              AND a.id > b.id
            """
        )
    else:
        # SQLite / other: use a correlated subquery
        op.execute(
            sa.text(
                """
                DELETE FROM provider_health_scorecards
                WHERE id > (
                    SELECT MIN(b.id)
                    FROM provider_health_scorecards b
                    WHERE b.provider = provider_health_scorecards.provider
                      AND b.endpoint = provider_health_scorecards.endpoint
                )
                """
            )
        )

    op.create_unique_constraint(
        "uq_provider_endpoint",
        "provider_health_scorecards",
        ["provider", "endpoint"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_provider_endpoint",
        "provider_health_scorecards",
        type_="unique",
    )
