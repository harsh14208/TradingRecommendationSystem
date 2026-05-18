import asyncio
import logging
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import event, text

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
        pool_pre_ping=True,   # detect stale connections
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
        if _IS_POSTGRES:
            return  # PostgreSQL schema is fully managed by create_all
        # SQLite-only additive migrations — used by the test suite
        _migrations = [
            "ALTER TABLE users ADD COLUMN min_confidence_override REAL",
            "ALTER TABLE users ADD COLUMN referred_by INTEGER REFERENCES users(id) ON DELETE SET NULL",
            "ALTER TABLE users ADD COLUMN referral_rewarded INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(20)",
            "ALTER TABLE users ADD COLUMN oauth_sub VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN discord_webhook_url VARCHAR(500)",
            "ALTER TABLE users ADD COLUMN webhook_url VARCHAR(500)",
            "ALTER TABLE signals ADD COLUMN expires_at DATETIME",
            "ALTER TABLE performance_snapshots ADD COLUMN alpha REAL",
        ]
        for sql in _migrations:
            try:
                await conn.execute(__import__("sqlalchemy").text(sql))
            except Exception:
                pass  # column already exists — ignore
