"""Alpha check: does short-interest / days-to-cover at entry predict MR outcome?

Joins data/mr_trades.csv (from a backtest_technicals run) with the backfilled
short_interest_biweekly table using an AS-OF join — each MR trade gets the most
recent FINRA settlement on or before the entry date (point-in-time correct, since
short interest is reported bi-weekly with a settlement lag). Then compares MR
outcomes by days-to-cover (DTC) tercile and by rising-vs-falling short interest.

History constraint: short-interest exists ~2017-12+, so MR trades before then get
no reading — expect moderate N. The same as-of join runs live as data accrues,
so this also seeds a forward gate.

    python scripts/check_short_interest_alpha.py
"""

import asyncio
import sys

sys.path.insert(0, ".")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sqlalchemy import select  # noqa: E402

from database import AsyncSessionLocal  # noqa: E402
from models import ShortInterestBiweekly  # noqa: E402


def _stats(rets: list[float]) -> dict:
    if not rets:
        return {"n": 0, "wr": 0.0, "avg": 0.0, "sharpe": None}
    a = np.array(rets, dtype=float)
    mu = float(a.mean())
    sd = float(a.std(ddof=1)) if len(a) > 1 else 0.0
    return {"n": len(a), "wr": round(float((a > 0).mean()) * 100, 1), "avg": round(mu, 2),
            "sharpe": round(mu / sd, 3) if sd > 0 and len(a) >= 10 else None}


async def _load_si() -> pd.DataFrame:
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(
                ShortInterestBiweekly.ticker,
                ShortInterestBiweekly.date,
                ShortInterestBiweekly.short_interest,
                ShortInterestBiweekly.days_to_cover,
            )
        )
        rows = res.all()
    df = pd.DataFrame(rows, columns=["ticker", "date", "short_interest", "dtc"])
    df["date"] = pd.to_datetime(df["date"])
    return df


def main():
    try:
        trades = pd.read_csv("data/mr_trades.csv")
    except FileNotFoundError:
        print("> Missing data/mr_trades.csv — run `python scripts/backtest_technicals.py --sequential` first.")
        return
    trades["date"] = pd.to_datetime(trades["date"]).dt.normalize()

    si = asyncio.run(_load_si())
    if si.empty:
        print("> short_interest_biweekly is empty — run `python scripts/backfill_short_interest.py` first.")
        return
    si["date"] = si["date"].dt.normalize()

    # Prior-reading delta (rising vs falling short interest) — per ticker, chronological.
    si = si.sort_values(["ticker", "date"])
    si["dtc_prev"] = si.groupby("ticker")["dtc"].shift(1)
    si["si_prev"] = si.groupby("ticker")["short_interest"].shift(1)

    # AS-OF join: each trade gets the latest settlement on/before its entry date.
    trades_s = trades.sort_values("date")
    j = pd.merge_asof(
        trades_s, si.sort_values("date"),
        on="date", by="ticker", direction="backward",
    )
    have = j.dropna(subset=["dtc"])

    print("## Short-Interest / Days-to-Cover Alpha Check vs MR Trade Outcomes\n")
    print(f"> {len(have)}/{len(trades)} MR trades have a short-interest reading at entry "
          f"(as-of join, history ~2017-12+). DTC = short_interest / avg_daily_volume.\n")
    if len(have) < 15:
        print("> Too few overlapping trades for a tercile read — accrue more live trades, "
              "then re-run. Backfill + as-of join are in place for forward use.\n")
        return

    # ── Absolute days-to-cover terciles ───────────────────────────────────────
    q1, q2 = np.percentile(have["dtc"], [33, 67])
    buckets = [
        (f"Low DTC (<{q1:.1f}d)", have[have["dtc"] <= q1]),
        (f"Mid DTC ({q1:.1f}-{q2:.1f}d)", have[(have["dtc"] > q1) & (have["dtc"] <= q2)]),
        (f"High DTC (>{q2:.1f}d)", have[have["dtc"] > q2]),
    ]
    print("| Days-to-cover tercile | N | WR | Avg Ret | Sharpe |")
    print("|:---|---:|---:|---:|---:|")
    for lbl, g in buckets:
        s = _stats(g["net_pct"].tolist())
        print(f"| {lbl} | {s['n']} | {s['wr']:.1f}% | {s['avg']:+.2f}% | {s['sharpe'] if s['sharpe'] is not None else '—'} |")

    # ── Rising vs falling short interest (vs prior bi-weekly reading) ──────────
    rel = have.dropna(subset=["si_prev"]).copy()
    if len(rel) >= 15:
        rel["rising"] = rel["short_interest"] > rel["si_prev"]
        hi = _stats(rel[rel["rising"]]["net_pct"].tolist())
        lo = _stats(rel[~rel["rising"]]["net_pct"].tolist())
        print("\n| Short interest vs prior reading | N | WR | Avg Ret | Sharpe |")
        print("|:---|---:|---:|---:|---:|")
        print(f"| Rising (SI up) | {hi['n']} | {hi['wr']:.1f}% | {hi['avg']:+.2f}% | {hi['sharpe'] if hi['sharpe'] is not None else '—'} |")
        print(f"| Falling (SI down) | {lo['n']} | {lo['wr']:.1f}% | {lo['avg']:+.2f}% | {lo['sharpe'] if lo['sharpe'] is not None else '—'} |")
        _spread = (hi["avg"] or 0) - (lo["avg"] or 0)
        print(f"\n> Rising-minus-falling avg-return spread = {_spread:+.2f}pp. "
              "Positive ⇒ building short interest into an oversold name is squeeze fuel (size up); "
              "negative ⇒ shorts are right / falling-knife (gate down). Directional at this N.\n")


if __name__ == "__main__":
    main()
