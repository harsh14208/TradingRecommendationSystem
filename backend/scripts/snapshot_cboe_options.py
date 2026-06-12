"""§110 — Nightly CBOE delayed-quotes options chain snapshot.

Upserts one row per ticker per trading day into ``options_chain_daily``.
Designed to be run once per evening after market close when CBOE's delayed
quotes reflect the full session's volume/OI.

    python scripts/snapshot_cboe_options.py             # full universe
    python scripts/snapshot_cboe_options.py --ticker AAPL
"""

from __future__ import annotations

import asyncio
import logging
import sys
from datetime import date, timedelta

sys.path.insert(0, ".")

from database import AsyncSessionLocal, _IS_POSTGRES  # noqa: E402
from models import OptionsChainDaily  # noqa: E402
from services.options_cboe import build_options_chain_daily_row  # noqa: E402

if _IS_POSTGRES:
    from sqlalchemy.dialects.postgresql import insert as dialect_insert
else:
    from sqlalchemy.dialects.sqlite import insert as dialect_insert

log = logging.getLogger("signal.snapshot_cboe_options")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")


def _universe() -> list[str]:
    import scripts.backtest_technicals as bt

    syms = set(bt.TICKERS)
    for name in ("HELD_OUT_TICKERS",):
        v = getattr(bt, name, None)
        if v:
            syms |= set(v)
    return sorted(syms)


def _today() -> date:
    """Return the most recently completed trading date (skip weekends/holidays simplistically)."""
    d = date.today()
    # Roll back to Friday if today is Saturday/Sunday.
    while d.weekday() >= 5:  # 5=Sat, 6=Sun
        d -= timedelta(days=1)
    return d


async def snapshot_ticker(db, ticker: str, snapshot_date: date) -> bool:
    """Fetch and upsert one ticker's CBOE options snapshot. Returns True on success."""
    try:
        row = await asyncio.to_thread(build_options_chain_daily_row, ticker, snapshot_date)
        if not row:
            log.debug("[cboe snapshot] %s: no data (empty or below volume threshold)", ticker)
            return False

        stmt = dialect_insert(OptionsChainDaily).values(row)
        stmt = stmt.on_conflict_do_update(
            index_elements=["ticker", "date"],
            set_={
                "contract_count": stmt.excluded.contract_count,
                "put_call_ratio": stmt.excluded.put_call_ratio,
                "total_volume": stmt.excluded.total_volume,
                "total_open_interest": stmt.excluded.total_open_interest,
                "avg_iv": stmt.excluded.avg_iv,
                "near_iv": stmt.excluded.near_iv,
                "far_iv": stmt.excluded.far_iv,
                "iv_term_spike": stmt.excluded.iv_term_spike,
                "iv_rank": stmt.excluded.iv_rank,
                "skew_25d": stmt.excluded.skew_25d,
                "max_pain": stmt.excluded.max_pain,
                "net_gex": stmt.excluded.net_gex,
                "spot": stmt.excluded.spot,
                "source": stmt.excluded.source,
                "contracts_snapshot": stmt.excluded.contracts_snapshot,
                "fetched_at": stmt.excluded.fetched_at,
            },
        )
        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as exc:
        log.warning("[cboe snapshot] %s: failed — %s", ticker, exc)
        await db.rollback()
        return False


async def main() -> None:
    if "--ticker" in sys.argv:
        universe = [sys.argv[sys.argv.index("--ticker") + 1].upper()]
    else:
        universe = _universe()

    snapshot_date = _today()
    log.info("CBOE options snapshot for %s tickers on %s", len(universe), snapshot_date)

    ok = 0
    empty = 0
    errors = 0
    async with AsyncSessionLocal() as db:
        for i, ticker in enumerate(universe, 1):
            try:
                success = await snapshot_ticker(db, ticker, snapshot_date)
            except Exception as exc:  # noqa: BLE001
                log.warning("[%s/%s] %s: unhandled error — %s", i, len(universe), ticker, exc)
                errors += 1
                continue
            if success:
                ok += 1
                if ok % 10 == 0:
                    log.info("[%s/%s] %s ok; running ok=%s empty=%s", i, len(universe), ticker, ok, empty)
            else:
                empty += 1

    log.info(
        "CBOE options snapshot complete: ok=%s empty=%s errors=%s",
        ok,
        empty,
        errors,
    )


if __name__ == "__main__":
    asyncio.run(main())
