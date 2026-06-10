"""§93d: Live-vs-IS gap decomposition."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import AsyncSessionLocal
from models import Signal, BrokerOrder


async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(
                Signal.ticker, Signal.created_at, Signal.action,
                Signal.confidence, Signal.outcome_pct, Signal.outcome_14d,
                Signal.extra_data, Signal.sent_at, Signal.sector_etf,
            ).where(Signal.outcome_pct != None, Signal.action.in_(["BUY", "SELL"]))
        )
        signals = pd.DataFrame(res.all(), columns=[
            "ticker", "created_at", "action", "confidence",
            "outcome_pct", "outcome_14d", "extra_data", "sent_at", "sector_etf"
        ])
        signals["created_at"] = pd.to_datetime(signals["created_at"])
        signals["sent_at"] = pd.to_datetime(signals["sent_at"])
        signals["vix"] = signals["extra_data"].apply(lambda x: x.get("vix") if isinstance(x, dict) else None)

        res2 = await db.execute(
            select(
                BrokerOrder.symbol, BrokerOrder.created_at,
                BrokerOrder.avg_fill_price, BrokerOrder.arrival_price, BrokerOrder.spread,
            ).where(BrokerOrder.avg_fill_price != None)
        )
        fills = pd.DataFrame(res2.all(), columns=[
            "symbol", "filled_at", "avg_fill_price", "arrival_price", "spread"
        ])
        fills["filled_at"] = pd.to_datetime(fills["filled_at"])

    print("=" * 60)
    print("§93d: Live-vs-IS Gap Decomposition")
    print("=" * 60)

    print("\n## 1. Regime Mismatch (VIX distribution)\n")
    print(f"Live resolved signals: {len(signals)}")
    print(f"Signals with non-null VIX: {signals['vix'].notna().sum()}/{len(signals)}")

    vix_valid = signals.dropna(subset=["vix"]).copy()
    if len(vix_valid) > 0:
        vix_valid["vix_bucket"] = pd.cut(
            vix_valid["vix"],
            bins=[0, 15, 20, 25, 30, 35, 100],
            labels=["<15", "15-20", "20-25", "25-30", "30-35", ">35"],
        )
        vix_dist = vix_valid.groupby("vix_bucket", observed=False).agg(
            n=("outcome_pct", "count"),
            wr=("outcome_pct", lambda x: (x > 0).mean() * 100),
            avg=("outcome_pct", "mean"),
        )
        print(vix_dist.round(2).to_string())
    else:
        print("No VIX data available.")

    print("\n> Backtest regime split: 100% of trades in VIX 20-30")
    print("> Live VIX distribution shows regime mismatch if significant mass outside 20-30.")

    print("\n## 2. Delivery Latency\n")
    signals["latency_sec"] = (signals["sent_at"] - signals["created_at"]).dt.total_seconds()
    latency = signals["latency_sec"].dropna()
    if len(latency) > 0:
        print(f"Mean latency: {latency.mean():.1f}s")
        print(f"Median latency: {latency.median():.1f}s")
        print(f"P95 latency: {latency.quantile(0.95):.1f}s")
    else:
        print("No delivery timestamps available.")

    print("\n## 3. Spread at Fill\n")
    if fills.empty:
        print("No fill data available.")
    else:
        print(f"Filled orders: {len(fills)}")
        spreads = fills["spread"].dropna()
        if len(spreads) > 0:
            print(f"Mean spread: {spreads.mean():.3f}%")
            print(f"Median spread: {spreads.median():.3f}%")
        fills["slippage_bps"] = (fills["avg_fill_price"] - fills["arrival_price"]) / fills["arrival_price"] * 10000
        slip = fills["slippage_bps"].dropna()
        if len(slip) > 0:
            print(f"Mean slippage: {slip.mean():.1f} bps")
            print(f"Median slippage: {slip.median():.1f} bps")

    print("\n## 4. Session Timing\n")
    signals["hour"] = signals["created_at"].dt.hour
    hour_stats = signals.groupby("hour").agg(
        n=("outcome_pct", "count"),
        wr=("outcome_pct", lambda x: (x > 0).mean() * 100),
        avg=("outcome_pct", "mean"),
    )
    print(hour_stats.round(2).to_string())

    print("\n## 5. Per-Sector Live Performance\n")
    sector_stats = signals.groupby("sector_etf").agg(
        n=("outcome_pct", "count"),
        wr=("outcome_pct", lambda x: (x > 0).mean() * 100),
        avg=("outcome_pct", "mean"),
    ).sort_values("wr", ascending=False)
    print(sector_stats.round(2).to_string())

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    live_wr = (signals["outcome_pct"] > 0).mean() * 100
    live_avg = signals["outcome_pct"].mean()
    print(f"Live WR: {live_wr:.1f}%  |  Live Avg: {live_avg:+.2f}%")
    print(f"IS WR:   69.1%  |  IS Avg:   +0.80%")
    print(f"Gap:     {69.1 - live_wr:.1f}pp  |  Avg gap: {0.80 - live_avg:+.2f}%")

    vix_20_30 = signals[(signals["vix"] >= 20) & (signals["vix"] <= 30)]
    if len(vix_20_30) > 0:
        regime_wr = (vix_20_30["outcome_pct"] > 0).mean() * 100
        print(f"\nLive WR in VIX 20-30 (backtest regime): {regime_wr:.1f}% (N={len(vix_20_30)})")
    outside = signals[(signals["vix"] < 20) | (signals["vix"] > 30)]
    if len(outside) > 0:
        outside_wr = (outside["outcome_pct"] > 0).mean() * 100
        print(f"Live WR outside VIX 20-30: {outside_wr:.1f}% (N={len(outside)})")


if __name__ == "__main__":
    asyncio.run(main())
