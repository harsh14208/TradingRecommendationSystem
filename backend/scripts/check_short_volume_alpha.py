"""Alpha check: does short-volume ratio (SVR) at entry predict MR trade outcome?

Joins data/mr_trades.csv (from a backtest_technicals run) with the backfilled
short_volume_daily table on (ticker, date), then compares MR outcomes by SVR tercile
and by SVR vs the ticker's own trailing-20d average (relative short pressure).

History constraint: short-volume only exists ~2024-02+, so only MR trades in that
window get an SVR — expect small N (directional). The same join runs live as data
accrues, so this also seeds a forward gate.

    python scripts/check_short_volume_alpha.py
"""

import asyncio
import sys

sys.path.insert(0, ".")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sqlalchemy import select  # noqa: E402

from database import AsyncSessionLocal  # noqa: E402
from models import ShortVolumeDaily  # noqa: E402


def _stats(rets: list[float]) -> dict:
    if not rets:
        return {"n": 0, "wr": 0.0, "avg": 0.0, "sharpe": None}
    a = np.array(rets, dtype=float)
    mu = float(a.mean())
    sd = float(a.std(ddof=1)) if len(a) > 1 else 0.0
    return {
        "n": len(a),
        "wr": round(float((a > 0).mean()) * 100, 1),
        "avg": round(mu, 2),
        "sharpe": round(mu / sd, 3) if sd > 0 and len(a) >= 10 else None,
    }


async def _load_svr() -> pd.DataFrame:
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(ShortVolumeDaily.ticker, ShortVolumeDaily.date, ShortVolumeDaily.short_volume_ratio)
        )
        rows = res.all()
    df = pd.DataFrame(rows, columns=["ticker", "date", "svr"])
    df["date"] = pd.to_datetime(df["date"])
    return df


def main():
    try:
        trades = pd.read_csv("data/mr_trades.csv")
    except FileNotFoundError:
        print("> Missing data/mr_trades.csv — run `python scripts/backtest_technicals.py --sequential` first.")
        return
    trades["date"] = pd.to_datetime(trades["date"]).dt.normalize()

    svr = asyncio.run(_load_svr())
    if svr.empty:
        print("> short_volume_daily is empty — run `python scripts/backfill_short_volume.py` first.")
        return
    svr["date"] = svr["date"].dt.normalize()

    # Absolute SVR at entry
    j = trades.merge(svr, on=["ticker", "date"], how="left")
    have = j.dropna(subset=["svr"])
    print("## Short-Volume Ratio (SVR) Alpha Check vs MR Trade Outcomes\n")
    print(
        f"> {len(have)}/{len(trades)} MR trades have an SVR at entry "
        f"(short-volume history ~2024-02+). SVR is % of consolidated volume short-marked.\n"
    )
    if len(have) < 15:
        print(
            "> Too few overlapping trades for a tercile read — accrue more live trades, "
            "then re-run. Backfill + join are in place for forward use.\n"
        )
        return

    # Absolute SVR terciles
    q1, q2 = np.percentile(have["svr"], [33, 67])
    buckets = [
        (f"Low SVR (<{q1:.0f}%)", have[have["svr"] <= q1]),
        (f"Mid SVR ({q1:.0f}-{q2:.0f}%)", have[(have["svr"] > q1) & (have["svr"] <= q2)]),
        (f"High SVR (>{q2:.0f}%)", have[have["svr"] > q2]),
    ]
    print("| SVR tercile (absolute) | N | WR | Avg Ret | Sharpe |")
    print("|:---|---:|---:|---:|---:|")
    for lbl, g in buckets:
        s = _stats(g["net_pct"].tolist())
        print(
            f"| {lbl} | {s['n']} | {s['wr']:.1f}% | {s['avg']:+.2f}% | {s['sharpe'] if s['sharpe'] is not None else '—'} |"
        )

    # Relative SVR: entry SVR vs the ticker's trailing-20d mean (elevated short pressure)
    svr_sorted = svr.sort_values(["ticker", "date"])
    svr_sorted["svr_ma20"] = svr_sorted.groupby("ticker")["svr"].transform(
        lambda x: x.rolling(20, min_periods=5).mean()
    )
    j2 = trades.merge(svr_sorted[["ticker", "date", "svr", "svr_ma20"]], on=["ticker", "date"], how="left").dropna(
        subset=["svr", "svr_ma20"]
    )
    if len(j2) >= 15:
        j2 = j2.copy()
        j2["elevated"] = j2["svr"] > j2["svr_ma20"]
        hi = _stats(j2[j2["elevated"]]["net_pct"].tolist())
        lo = _stats(j2[~j2["elevated"]]["net_pct"].tolist())
        print("\n| Entry short pressure vs 20d avg | N | WR | Avg Ret | Sharpe |")
        print("|:---|---:|---:|---:|---:|")
        print(
            f"| Elevated (SVR > 20d avg) | {hi['n']} | {hi['wr']:.1f}% | {hi['avg']:+.2f}% | {hi['sharpe'] if hi['sharpe'] is not None else '—'} |"
        )
        print(
            f"| Subdued (SVR <= 20d avg) | {lo['n']} | {lo['wr']:.1f}% | {lo['avg']:+.2f}% | {lo['sharpe'] if lo['sharpe'] is not None else '—'} |"
        )
        _spread = (hi["avg"] or 0) - (lo["avg"] or 0)
        print(
            f"\n> Elevated-minus-subdued avg-return spread = {_spread:+.2f}pp. "
            "Positive ⇒ short pressure at entry is squeeze fuel (size up); "
            "negative ⇒ falling-knife signal (gate down). Directional at this N.\n"
        )


if __name__ == "__main__":
    main()
