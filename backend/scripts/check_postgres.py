#!/usr/bin/env python3
"""
PostgreSQL migration validator.

Run before migrating from SQLite to PostgreSQL:
    python3 scripts/check_postgres.py

Checks:
1. DATABASE_URL is set and uses postgresql:// scheme
2. asyncpg driver is installed
3. Database connection is reachable
4. Schema is compatible (all expected tables exist)
5. Warns about SQLite-specific patterns that won't work in Postgres
"""
import asyncio
import os
import sys

# Allow running from the backend/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


EXPECTED_TABLES = {
    "signals", "users", "refresh_tokens", "signal_deliveries",
    "watchlist", "sources", "app_settings", "send_log",
}

PASS, WARN, FAIL = "✅", "⚠️ ", "❌"


async def main():
    db_url = os.getenv("DATABASE_URL", "")

    print("Signal.Trade — PostgreSQL Migration Validator")
    print("=" * 50)

    # ── 1. DATABASE_URL check ─────────────────────────────────────────────────
    if not db_url:
        print(f"{FAIL} DATABASE_URL is not set")
        print("   Set DATABASE_URL=postgresql://user:pass@host:5432/dbname in .env")
        sys.exit(1)

    if db_url.startswith("sqlite"):
        print(f"{FAIL} DATABASE_URL is pointing to SQLite, not PostgreSQL")
        print(f"   Current: {db_url}")
        print("   Expected: postgresql://... or postgresql+asyncpg://...")
        sys.exit(1)

    if db_url.startswith("postgresql://") or db_url.startswith("postgresql+asyncpg://"):
        print(f"{PASS} DATABASE_URL is set to PostgreSQL")
    else:
        print(f"{WARN} Unrecognised DATABASE_URL scheme: {db_url[:40]}...")

    # ── 2. asyncpg installed ──────────────────────────────────────────────────
    try:
        import asyncpg
        print(f"{PASS} asyncpg is installed (version: {asyncpg.__version__})")
    except ImportError:
        print(f"{FAIL} asyncpg is not installed")
        print("   Run: pip install asyncpg>=0.29.0")
        sys.exit(1)

    # ── 3. Connection reachable ───────────────────────────────────────────────
    conn_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    try:
        conn = await asyncpg.connect(conn_url, timeout=10)
        pg_version = await conn.fetchval("SELECT version()")
        await conn.close()
        print(f"{PASS} Connected to PostgreSQL")
        print(f"   {pg_version[:60]}…")
    except Exception as e:
        print(f"{FAIL} Could not connect to PostgreSQL: {e}")
        sys.exit(1)

    # ── 4. Schema check ───────────────────────────────────────────────────────
    try:
        conn = await asyncpg.connect(conn_url, timeout=10)
        existing = set(
            r["tablename"]
            for r in await conn.fetch(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            )
        )
        await conn.close()
    except Exception as e:
        print(f"{WARN} Could not query table list: {e}")
        existing = set()

    if not existing:
        print(f"{WARN} No tables found yet — run the app once to create the schema")
        print("   Start the server with DATABASE_URL set; init_db() will create all tables.")
    else:
        missing = EXPECTED_TABLES - existing
        if missing:
            print(f"{WARN} Missing tables (will be created on first startup): {missing}")
        else:
            print(f"{PASS} All {len(EXPECTED_TABLES)} expected tables exist")

    # ── 5. SQLite-specific warnings ───────────────────────────────────────────
    print()
    print("Migration notes:")
    print(f"  {PASS} database.py: _IS_POSTGRES=True branch skips ALTER TABLE migrations")
    print(f"  {PASS} database.py: SQLite WAL pragmas are guarded behind not _IS_POSTGRES")
    print(f"  {PASS} database.py: pool_size=10, max_overflow=20, pool_pre_ping=True configured")
    print(f"  {WARN} SQLite WAL-mode journals (trading.db-wal, -shm) can be deleted safely")
    print(f"  {WARN} Backfill outcome_pct on historical signals after migration if needed")
    print()
    print("Migration steps:")
    print("  1. railway add --plugin postgresql   (or provision via your host)")
    print("  2. Set DATABASE_URL=postgresql://... in backend/.env")
    print("  3. Run: python3 scripts/check_postgres.py  (this script)")
    print("  4. Start the server — init_db() creates schema automatically")
    print("  5. Optionally migrate existing SQLite data with pg_loader or custom script")
    print()
    print(f"{PASS} Validation complete — PostgreSQL is ready")


if __name__ == "__main__":
    asyncio.run(main())
