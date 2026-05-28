import logging
import os
from pathlib import Path

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent / ".env", override=False)
except ImportError:
    pass

logger = logging.getLogger(__name__)

# ── Database URL — PostgreSQL in production, SQLite for tests/local dev ──────
# Set DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname in .env.
_DB_URL = os.getenv("DATABASE_URL", "")
if _DB_URL.startswith("postgresql://"):
    _DB_URL = _DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# SQLite fallback is intentionally kept for the test suite (conftest.py sets
# DATABASE_URL=sqlite+aiosqlite:///./test_db.sqlite). Production always uses
# DATABASE_URL from the environment.
DATABASE_URL = _DB_URL or "sqlite+aiosqlite:///./data/trading.db"
_IS_POSTGRES = DATABASE_URL.startswith("postgresql")

# SQLite WAL mode configuration for better concurrency
_SQLITE_PRAGMAS = [
    "PRAGMA journal_mode=WAL",
    "PRAGMA synchronous=NORMAL",
    "PRAGMA cache_size=-64000",
    "PRAGMA temp_store=MEMORY",
    "PRAGMA mmap_size=268435456",
    "PRAGMA busy_timeout=5000",
    "PRAGMA wal_autocheckpoint=1000",
]


def _setup_sqlite_connection(dbapi_conn, _):
    """Configure SQLite connection with concurrency-optimized pragmas."""
    try:
        cursor = dbapi_conn.cursor()
        for pragma in _SQLITE_PRAGMAS:
            cursor.execute(pragma)
        cursor.close()
        dbapi_conn.commit()
        logger.debug("SQLite pragmas applied for concurrency optimization")
    except Exception as e:
        logger.warning(f"Failed to set SQLite pragmas: {e}")


if _IS_POSTGRES:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # test connection health before checkout
        pool_recycle=3600,  # recycle connections after 1 hr to avoid server-side timeout drops
        pool_timeout=5,  # fail fast (5s) vs default 30s; prevents cascade hangs at market-open spikes
    )
    logger.info(f"[db] Using PostgreSQL: {DATABASE_URL.split('@')[-1]}")
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    event.listen(engine.sync_engine, "connect", _setup_sqlite_connection)
    logger.info("[db] Using SQLite (WAL mode)")

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Additive column migrations — kept for environments that have never run
        # Alembic (e.g. local dev clones, CI test DBs).  For production schema
        # changes use Alembic instead:
        #
        #   # New deployment against empty DB — apply all migrations:
        #   alembic upgrade head
        #
        #   # Existing production DB (schema already current) — stamp it so
        #   # Alembic knows the starting revision without re-running DDL:
        #   alembic stamp head
        #
        #   # After adding a new column / table to models.py:
        #   alembic revision --autogenerate -m "add_foo_column"
        #   alembic upgrade head
        #
        # WARNING: never remove columns via this init_db block — that requires a
        # proper Alembic migration with a downgrade() to be safely reversible.
        _migrations: list[tuple[str, str]] = [
            # users table
            ("users", "ALTER TABLE users ADD COLUMN min_confidence_override REAL"),
            ("users", "ALTER TABLE users ADD COLUMN referred_by INTEGER REFERENCES users(id) ON DELETE SET NULL"),
            ("users", "ALTER TABLE users ADD COLUMN referral_rewarded INTEGER DEFAULT 0"),
            ("users", "ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(20)"),
            ("users", "ALTER TABLE users ADD COLUMN oauth_sub VARCHAR(255)"),
            ("users", "ALTER TABLE users ADD COLUMN discord_webhook_url VARCHAR(500)"),
            ("users", "ALTER TABLE users ADD COLUMN webhook_url VARCHAR(500)"),
            # signals table
            ("signals", "ALTER TABLE signals ADD COLUMN expires_at DATETIME"),
            # performance_snapshots table
            ("performance_snapshots", "ALTER TABLE performance_snapshots ADD COLUMN alpha REAL"),
        ]
        for _tbl, sql in _migrations:
            try:
                await conn.execute(text(sql))
            except Exception:
                pass  # column already exists — safe to ignore
