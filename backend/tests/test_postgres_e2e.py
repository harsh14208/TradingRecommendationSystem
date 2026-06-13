"""R10-18: true end-to-end test against a REAL PostgreSQL backend.

The rest of the suite runs on SQLite (conftest + the DISC-5 guard force it),
which is fast and hermetic but cannot catch Postgres-only behavior — most
importantly the production ``json`` column that rejects NaN/Infinity tokens
(the exact bug ``feature_store._json_safe`` exists to prevent). SQLite stores
JSON as TEXT and silently accepts NaN, so that bug is invisible there.

This module builds its OWN async engine from ``TEST_POSTGRES_URL`` — it never
touches the global ``database.engine`` (which is SQLite under pytest), so prod
safety and the DISC-5 guard are untouched. All objects live in a throwaway
schema that is dropped on teardown, so it is safe to point at a dev database.

Run it by exporting a reachable Postgres URL, e.g.::

    TEST_POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/postgres \
        pytest tests/test_postgres_e2e.py -v

It auto-skips when the variable is unset or the server is unreachable, so the
default SQLite suite and current CI stay green. To exercise it in CI, add a
`postgres` service container and set `TEST_POSTGRES_URL`.
"""

import math
import os
import uuid
from datetime import datetime

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

_RAW_URL = os.getenv("TEST_POSTGRES_URL", "")

pytestmark = pytest.mark.skipif(
    not _RAW_URL,
    reason="TEST_POSTGRES_URL not set — skipping real-Postgres E2E (SQLite suite covers the rest)",
)


def _asyncpg_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


@pytest.mark.asyncio
async def test_postgres_end_to_end_round_trip_and_json_nan_rejection():
    from database import Base
    import models  # noqa: F401 — registers every table on Base.metadata
    from models import FeatureSnapshot, Instrument, Signal
    from services.feature_store import save_feature_snapshot

    url = _asyncpg_url(_RAW_URL)
    schema = f"pytest_e2e_{uuid.uuid4().hex[:12]}"

    # 1. Bootstrap the isolation schema with a plain engine (default search_path).
    admin_engine = create_async_engine(url, poolclass=NullPool)
    try:
        try:
            async with admin_engine.begin() as conn:
                await conn.execute(text(f'CREATE SCHEMA "{schema}"'))
        except Exception as exc:  # unreachable server / bad creds → skip, don't fail
            pytest.skip(f"TEST_POSTGRES_URL set but Postgres unreachable: {type(exc).__name__}: {exc}")

        # 2. Main engine pins every connection to the throwaway schema.
        engine = create_async_engine(
            url,
            poolclass=NullPool,
            connect_args={"server_settings": {"search_path": schema}},
        )
        SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        try:
            # Confirm we are really on Postgres, not a fallback.
            async with engine.connect() as conn:
                backend = (await conn.execute(text("SELECT version()"))).scalar_one()
                assert "PostgreSQL" in backend, f"expected PostgreSQL, got: {backend}"

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # ── 3. Multi-table round trip: Instrument ← Signal ← FeatureSnapshot ──
            async with SessionLocal() as db:
                sig = Signal(
                    ticker="PGAAPL",
                    action="BUY",
                    confidence=57.5,
                    price=190.25,
                    headline="E2E round-trip signal",
                    is_sent=True,
                )
                db.add(sig)
                await db.flush()

                # NaN/Inf in the feature dict — the production crash case. On real
                # Postgres json this only survives because _json_safe sanitizes it.
                snap = await save_feature_snapshot(
                    db=db,
                    ticker="PGAAPL",
                    ts=datetime.utcnow(),
                    features={
                        "rsi": 38.0,
                        "bb_pct_b": float("nan"),
                        "deep": {"x": float("inf")},
                        "quality_score": 55.0,
                        "hasMr": True,
                    },
                    signal_id=sig.id,
                )
                await db.commit()
                snap_id = snap.id

            async with SessionLocal() as db:
                row = (await db.execute(select(FeatureSnapshot).where(FeatureSnapshot.id == snap_id))).scalar_one()
                # Sanitized: non-finite values nulled, finite values preserved.
                assert row.features["bb_pct_b"] is None
                assert row.features["deep"]["x"] is None
                assert row.features["rsi"] == 38.0
                assert row.bb_pct_b is None
                assert row.rsi == 38.0
                assert row.feature_vector_hash is not None

                # Instrument was auto-created and linked.
                inst = (await db.execute(select(Instrument).where(Instrument.ticker == "PGAAPL"))).scalar_one()
                assert row.instrument_id == inst.id

                # Signal round-tripped with its server_default created_at.
                live = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one()
                assert live.is_sent is True
                assert live.created_at is not None

            # ── 4. Negative control: RAW NaN into the json column MUST fail on PG ──
            # This is the assertion SQLite physically cannot make — it proves the
            # _json_safe guard is load-bearing on the real backend.
            async with SessionLocal() as db:
                inst = (await db.execute(select(Instrument).where(Instrument.ticker == "PGAAPL"))).scalar_one()
                bad = FeatureSnapshot(
                    instrument_id=inst.id,
                    ts=datetime.utcnow(),
                    features={"unsanitized": float("nan")},  # bypasses _json_safe on purpose
                )
                db.add(bad)
                with pytest.raises(Exception) as exc_info:
                    await db.flush()
                # Postgres rejects the bare NaN token at the json boundary.
                assert "NaN" in str(exc_info.value) or "invalid" in str(exc_info.value).lower()
                await db.rollback()

            # Sanity: the bad row never landed; the good one is still the only snapshot.
            async with SessionLocal() as db:
                count = (await db.execute(select(FeatureSnapshot))).scalars().all()
                assert len(count) == 1
                assert math.isfinite(190.25)  # guard against accidental import pruning
        finally:
            await engine.dispose()
    finally:
        # 5. Drop the throwaway schema and everything in it.
        drop_engine = create_async_engine(url, poolclass=NullPool)
        async with drop_engine.begin() as conn:
            await conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        await drop_engine.dispose()
        await admin_engine.dispose()
