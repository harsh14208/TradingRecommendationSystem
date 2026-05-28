#!/usr/bin/env python3
"""
One-shot migration: SQLite → PostgreSQL.

Run from the backend/ directory after starting Postgres:
    docker compose up -d postgres
    source venv/bin/activate
    python scripts/migrate_sqlite_to_postgres.py

The script reads DATABASE_URL from .env (or the environment).
It is safe to re-run — all destination tables are truncated before copy.
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")

# ── Load .env from backend/ ───────────────────────────────────────────────────
_env = Path(__file__).parent.parent / ".env"
if _env.exists():
    from dotenv import load_dotenv

    load_dotenv(_env)

# ── Source ────────────────────────────────────────────────────────────────────
_sqlite = Path("data/trading.db")
if not _sqlite.exists():
    _sqlite = Path("trading.db")
if not _sqlite.exists():
    sys.exit("ERROR: No SQLite database found at data/trading.db or trading.db")

SQLITE_URL = f"sqlite+aiosqlite:///{_sqlite}"

# ── Target ────────────────────────────────────────────────────────────────────
_pg = os.environ.get("DATABASE_URL", "")
if not _pg:
    sys.exit("ERROR: DATABASE_URL is not set. Add it to backend/.env or export it.")
if _pg.startswith("postgresql://"):
    _pg = _pg.replace("postgresql://", "postgresql+asyncpg://", 1)
if not _pg.startswith("postgresql+asyncpg://"):
    sys.exit(f"ERROR: DATABASE_URL must be a PostgreSQL URL, got: {_pg[:40]}")

PG_URL = _pg

# ── Tables — FK parents before children ──────────────────────────────────────
TABLES = [
    "users",
    "signals",
    "send_log",
    "app_settings",
    "watchlist",
    "sources",
    "refresh_tokens",
    "signal_deliveries",
    "price_alerts",
    "push_subscriptions",
]

# Columns that SQLite stores as JSON text — must be parsed before PG insert
_JSON_COLS: dict[str, set[str]] = {
    "signals": {"sources", "rationale", "plain_english"},
    "app_settings": {"data"},
}

# Columns that SQLite stores as 0/1 integers — convert to bool for PG
_BOOL_COLS: dict[str, set[str]] = {
    "signals": {"is_active", "is_sent", "is_skipped", "reviewed", "confidence_warning"},
    "users": {"is_active", "is_owner", "referral_rewarded", "email_verified"},
    "refresh_tokens": {"revoked"},
    "price_alerts": {"is_active"},
    "watchlist": {"is_active"},
    "sources": {"is_on"},
}


def _coerce(table: str, row: dict) -> dict:
    out: dict = {}
    for k, v in row.items():
        if v is None:
            out[k] = None
        elif k in _JSON_COLS.get(table, set()) and isinstance(v, str):
            try:
                out[k] = json.loads(v)
            except (ValueError, TypeError):
                out[k] = v
        elif k in _BOOL_COLS.get(table, set()):
            out[k] = bool(v)
        elif isinstance(v, str) and _DATETIME_RE.match(v):
            try:
                out[k] = datetime.fromisoformat(v)
            except ValueError:
                out[k] = v
        else:
            out[k] = v
    return out


async def main() -> None:
    import sqlalchemy as sa
    from sqlalchemy.ext.asyncio import create_async_engine

    print(f"Source : sqlite:///{_sqlite}")
    print(f"Target : {PG_URL.split('@')[-1]}\n")

    sqlite_eng = create_async_engine(SQLITE_URL, echo=False)
    pg_eng = create_async_engine(PG_URL, echo=False)

    # ── 1. Create schema on PG ────────────────────────────────────────────────
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models import Base  # noqa: E402

    async with pg_eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Schema created.\n")

    # ── 2. Read all rows from SQLite ──────────────────────────────────────────
    data: dict[str, list[dict]] = {}
    async with sqlite_eng.connect() as src:
        for tname in TABLES:
            try:
                res = await src.execute(sa.text(f"SELECT * FROM {tname}"))
                cols = list(res.keys())
                rows = [_coerce(tname, dict(zip(cols, r))) for r in res.fetchall()]
                data[tname] = rows
                print(f"  read  {tname}: {len(rows)} rows")
            except Exception:
                data[tname] = []
                print(f"  skip  {tname} (not in SQLite)")

    # ── 3. Copy into PG ───────────────────────────────────────────────────────
    print()

    # Reflect PG schema so SQLAlchemy handles JSON/datetime serialization for us
    from sqlalchemy import MetaData as SAMeta

    pg_meta = SAMeta()
    async with pg_eng.connect() as c:
        await c.run_sync(pg_meta.reflect)

    async with pg_eng.begin() as dst:
        # Single TRUNCATE CASCADE clears everything
        tables_sql = ", ".join(f'"{t}"' for t in TABLES)
        await dst.execute(sa.text(f"TRUNCATE TABLE {tables_sql} RESTART IDENTITY CASCADE"))

        # Disable RI triggers so we can insert in dependency order freely
        for tname in TABLES:
            await dst.execute(sa.text(f'ALTER TABLE "{tname}" DISABLE TRIGGER ALL'))

        for tname in TABLES:
            rows = data.get(tname, [])
            if not rows:
                print(f"  skip  {tname} (0 rows)")
                continue
            tbl = pg_meta.tables[tname]
            await dst.execute(tbl.insert(), rows)
            print(f"  copy  {tname}: {len(rows)} rows")

        # Re-enable FK triggers
        for tname in TABLES:
            await dst.execute(sa.text(f'ALTER TABLE "{tname}" ENABLE TRIGGER ALL'))

    # ── 4. Reset sequences ────────────────────────────────────────────────────
    async with pg_eng.begin() as conn:
        for tname in TABLES:
            try:
                await conn.execute(
                    sa.text(f"""
                    SELECT setval(
                        pg_get_serial_sequence('{tname}', 'id'),
                        COALESCE((SELECT MAX(id) FROM "{tname}"), 0) + 1,
                        false
                    )
                """)
                )
            except Exception:
                pass  # table has no serial id column

    print("\nDone — sequences reset. PostgreSQL is ready.")


if __name__ == "__main__":
    asyncio.run(main())
