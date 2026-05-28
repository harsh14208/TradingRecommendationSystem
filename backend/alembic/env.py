import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make backend/ importable (models.py, database.py live here)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

# Import Base so Alembic can autogenerate against all registered models.
# models.py must be imported BEFORE Base.metadata is read so all ORM classes
# register themselves.
import models  # noqa: F401 — side-effect import registers all table metadata
from database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    """
    Return a synchronous (psycopg2) PostgreSQL URL for Alembic.
    asyncpg is the async driver used at runtime; Alembic needs a sync driver.
    Falls back to the raw DATABASE_URL for non-Postgres environments (e.g. SQLite
    in CI), stripping the aiosqlite driver prefix.
    """
    url = os.getenv("DATABASE_URL", "")
    # Convert async drivers to sync equivalents
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    url = url.replace("postgresql://", "postgresql+psycopg2://")
    url = url.replace("sqlite+aiosqlite://", "sqlite://")
    return url or "sqlite:///./data/trading.db"


def run_migrations_offline() -> None:
    """Generate SQL script without a live DB connection (--sql mode)."""
    url = _get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations against a live DB connection."""
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = _get_url()

    connectable = engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
