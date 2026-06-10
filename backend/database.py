import logging
import os
from pathlib import Path

from sqlalchemy import event, text
from sqlalchemy.exc import OperationalError, ProgrammingError
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
        except Exception:
            await session.rollback()
            raise


def _dt_type() -> str:
    return "TIMESTAMP" if _IS_POSTGRES else "DATETIME"


def _bool_default(false_value: str = "FALSE") -> str:
    return f"BOOLEAN DEFAULT {false_value.upper()}" if _IS_POSTGRES else "INTEGER DEFAULT 0"


async def _pg_column_exists(conn, table: str, column: str) -> bool:
    """Check whether a column already exists on a PostgreSQL table."""
    result = await conn.execute(
        text("SELECT 1 FROM information_schema.columns WHERE table_name = :table AND column_name = :column"),
        {"table": table, "column": column},
    )
    return result.scalar() is not None


async def _pg_index_exists(conn, table: str, index: str) -> bool:
    """Check whether an index already exists on a PostgreSQL table."""
    result = await conn.execute(
        text("SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = :table AND indexname = :index"),
        {"table": table, "index": index},
    )
    return result.scalar() is not None


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
        dt = _dt_type()
        bd = _bool_default
        _migrations: list[tuple[str, str, str | None]] = [
            # (table_or_kind, sql, object_name_for_idempotency_check)
            # users table
            ("users", "ALTER TABLE users ADD COLUMN min_confidence_override REAL", "min_confidence_override"),
            (
                "users",
                "ALTER TABLE users ADD COLUMN referred_by INTEGER REFERENCES users(id) ON DELETE SET NULL",
                "referred_by",
            ),
            ("users", f"ALTER TABLE users ADD COLUMN referral_rewarded {bd('FALSE')}", "referral_rewarded"),
            ("users", "ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(20)", "oauth_provider"),
            ("users", "ALTER TABLE users ADD COLUMN oauth_sub VARCHAR(255)", "oauth_sub"),
            ("users", "ALTER TABLE users ADD COLUMN discord_webhook_url VARCHAR(500)", "discord_webhook_url"),
            ("users", "ALTER TABLE users ADD COLUMN webhook_url VARCHAR(500)", "webhook_url"),
            ("users", f"ALTER TABLE users ADD COLUMN trial_consumed_at {dt}", "trial_consumed_at"),
            # oauth_state table
            ("oauth_state", "ALTER TABLE oauth_state ADD COLUMN code_challenge VARCHAR(255)", "code_challenge"),
            ("oauth_state", "ALTER TABLE oauth_state ADD COLUMN code_verifier VARCHAR(255)", "code_verifier"),
            # signals table
            ("signals", f"ALTER TABLE signals ADD COLUMN expires_at {dt}", "expires_at"),
            # performance_snapshots table
            ("performance_snapshots", "ALTER TABLE performance_snapshots ADD COLUMN alpha REAL", "alpha"),
            # indexes for created_at (CREATE INDEX IF NOT EXISTS is idempotent on its own)
            ("signals", "CREATE INDEX IF NOT EXISTS idx_signals_created_at ON signals(created_at)", None),
            ("send_log", "CREATE INDEX IF NOT EXISTS idx_send_log_created_at ON send_log(created_at)", None),
            (
                "broker_orders",
                "CREATE INDEX IF NOT EXISTS idx_broker_orders_created_at ON broker_orders(created_at)",
                None,
            ),
        ]
        for table, sql, obj_name in _migrations:
            try:
                if obj_name and _IS_POSTGRES:
                    if sql.strip().upper().startswith("CREATE INDEX"):
                        if await _pg_index_exists(conn, table, obj_name):
                            continue
                    else:
                        if await _pg_column_exists(conn, table, obj_name):
                            continue
                await conn.execute(text(sql))
            except (OperationalError, ProgrammingError) as exc:
                err = str(exc).lower()
                if any(k in err for k in ("duplicate column", "already exists", "duplicate relation")):
                    continue
                logger.warning(f"Migration operational error ({sql}): {exc}")
            except Exception as exc:
                logger.warning(f"Migration unexpected error ({sql}): {exc}")
