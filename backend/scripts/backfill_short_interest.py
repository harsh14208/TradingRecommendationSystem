"""Backfill bi-weekly Polygon FINRA short-interest into short_interest_biweekly.

Re-runnable: upserts on (ticker, date) so re-running only fills gaps / refreshes.
Covers the IS + held-out universe so the backtest alpha check and live gate can
both reuse the data. History available ~2017-12 onward (deeper than short-volume).

    python scripts/backfill_short_interest.py             # full universe
    python scripts/backfill_short_interest.py --ticker NVDA
"""

import asyncio
import sys

sys.path.insert(0, ".")

from sqlalchemy.dialects.postgresql import insert as pg_insert  # noqa: E402

from database import AsyncSessionLocal  # noqa: E402
from models import ShortInterestBiweekly  # noqa: E402
from services.polygon_client import get_polygon_short_interest  # noqa: E402


def _universe() -> list[str]:
    import scripts.backtest_technicals as bt
    syms = set(bt.TICKERS)
    for name in ("HELD_OUT_TICKERS",):
        v = getattr(bt, name, None)
        if v:
            syms |= set(v)
    return sorted(syms)


async def backfill_ticker(db, ticker: str) -> int:
    rows = await get_polygon_short_interest(ticker, limit=1000)
    if not rows:
        return 0
    import datetime as _dt
    payload = [
        {
            "ticker": ticker,
            "date": _dt.date.fromisoformat(r["date"][:10]),
            "short_interest": r.get("short_interest"),
            "days_to_cover": r.get("days_to_cover"),
            "avg_daily_volume": r.get("avg_daily_volume"),
        }
        for r in rows
    ]
    stmt = pg_insert(ShortInterestBiweekly).values(payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=["ticker", "date"],
        set_={
            "short_interest": stmt.excluded.short_interest,
            "days_to_cover": stmt.excluded.days_to_cover,
            "avg_daily_volume": stmt.excluded.avg_daily_volume,
        },
    )
    await db.execute(stmt)
    await db.commit()
    return len(payload)


async def main():
    if "--ticker" in sys.argv:
        universe = [sys.argv[sys.argv.index("--ticker") + 1].upper()]
    else:
        universe = _universe()
    print(f"Backfilling short-interest for {len(universe)} tickers…", flush=True)
    total, ok, empty = 0, 0, 0
    async with AsyncSessionLocal() as db:
        for i, t in enumerate(universe, 1):
            try:
                n = await backfill_ticker(db, t)
            except Exception as e:  # noqa: BLE001
                print(f"[{i}/{len(universe)}] {t}: ERROR {type(e).__name__}: {str(e)[:60]}", flush=True)
                await db.rollback()
                continue
            total += n
            if n:
                ok += 1
            else:
                empty += 1
            if i % 20 == 0 or n == 0:
                print(f"[{i}/{len(universe)}] {t}: {n} rows (ok={ok} empty={empty} total={total})", flush=True)
    print(f"\nDONE. {ok} tickers populated, {empty} empty, {total} rows upserted.", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
