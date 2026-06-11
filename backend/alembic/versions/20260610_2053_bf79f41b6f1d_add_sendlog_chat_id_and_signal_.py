"""add_sendlog_chat_id_and_signal_deliveries_created_at

Revision ID: bf79f41b6f1d
Revises: 0f1099d21801
Create Date: 2026-06-10 20:53:38.013480

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "bf79f41b6f1d"
down_revision: Union[str, Sequence[str], None] = "0f1099d21801"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # DISC-3: Add chat_id to send_log for audit tracking of actual recipients.
    op.add_column("send_log", sa.Column("chat_id", sa.String(length=50), nullable=True))

    # DISC-7: Add created_at to signal_deliveries; separate row creation time
    # from delivery confirmation time (sent_at).
    op.add_column(
        "signal_deliveries",
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
    )
    # Remove server_default from sent_at so new rows don't auto-populate it;
    # code now sets sent_at explicitly when delivery is confirmed.
    op.alter_column(
        "signal_deliveries",
        "sent_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=None,
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "signal_deliveries",
        "sent_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("now()"),
        existing_nullable=True,
    )
    op.drop_column("signal_deliveries", "created_at")
    op.drop_column("send_log", "chat_id")
