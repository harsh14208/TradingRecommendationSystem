#!/usr/bin/env python3
"""§104b — Validate the canonical FRICTION=0.5% assumption against real broker fills.

Queries the QENG-3a fill ledger (``broker_orders`` + ``fills``) and reports
realized round-trip transaction cost per ticker and per ADV bucket. The canonical
0.5% round-trip is a deliberate conservative buffer (R10-8); this script measures
the real number without changing the backtest constant.

Usage:
    cd backend && python scripts/analyze_realized_friction.py [--days 30]
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import sqlalchemy as sa

_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from database import AsyncSessionLocal  # noqa: E402

log = logging.getLogger("signal.analyze_realized_friction")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

CANONICAL_ROUND_TRIP_BPS = 50.0  # 0.50%


@dataclass
class FrictionSummary:
    n_fills: int
    n_tickers: int
    mean_slippage_bps: float
    median_slippage_bps: float
    p90_slippage_bps: float
    mean_commission_bps: float
    mean_round_trip_bps: float


async def _load_fills(days: int) -> pd.DataFrame:
    """Load fills joined to broker_orders from the last ``days`` calendar days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    query = sa.text(
        """
        SELECT
            bo.symbol AS ticker,
            f.side,
            f.qty,
            f.price,
            f.commission,
            f.slippage_bps,
            bo.arrival_price,
            bo.nbbo_mid,
            bo.spread,
            bo.fees,
            bo.broker,
            f.filled_at
        FROM fills f
        JOIN broker_orders bo ON f.broker_order_id = bo.id
        WHERE f.filled_at >= :cutoff
        ORDER BY f.filled_at DESC
        """
    )
    async with AsyncSessionLocal() as db:
        result = await db.execute(query, {"cutoff": cutoff})
        rows = result.mappings().all()
    df = pd.DataFrame([dict(r) for r in rows])
    return df


def _compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived cost columns in bps."""
    notional = df["qty"] * df["price"]
    commission_bps = (df["commission"] / notional.clip(lower=1e-9)) * 10000.0
    fees_bps = (df["fees"].fillna(0.0) / notional.clip(lower=1e-9)) * 10000.0
    return df.assign(
        notional=notional,
        commission_bps=commission_bps,
        fees_bps=fees_bps,
        total_cost_bps=df["slippage_bps"].fillna(0.0) + commission_bps + fees_bps,
    )


def _summarize(df: pd.DataFrame) -> FrictionSummary:
    return FrictionSummary(
        n_fills=len(df),
        n_tickers=df["ticker"].nunique(),
        mean_slippage_bps=df["slippage_bps"].mean(),
        median_slippage_bps=df["slippage_bps"].median(),
        p90_slippage_bps=df["slippage_bps"].quantile(0.90),
        mean_commission_bps=df["commission_bps"].mean(),
        mean_round_trip_bps=df["total_cost_bps"].mean() * 2,  # entry + exit assumption
    )


def _print_summary(summary: FrictionSummary, df: pd.DataFrame) -> None:
    print("\n=== Realized Friction Summary ===")
    print(f"Fill sample: {summary.n_fills} legs across {summary.n_tickers} tickers")
    print(f"Mean slippage:     {summary.mean_slippage_bps:6.2f} bps")
    print(f"Median slippage:   {summary.median_slippage_bps:6.2f} bps")
    print(f"90th pct slippage: {summary.p90_slippage_bps:6.2f} bps")
    print(f"Mean commission:   {summary.mean_commission_bps:6.2f} bps")
    print(f"Implied round-trip (2× all-in leg): {summary.mean_round_trip_bps:6.2f} bps")
    print(f"Canonical assumption:               {CANONICAL_ROUND_TRIP_BPS:6.2f} bps")
    if summary.mean_round_trip_bps:
        ratio = summary.mean_round_trip_bps / CANONICAL_ROUND_TRIP_BPS
        print(f"Realized / canonical ratio:         {ratio:6.2f}x")

    if not df.empty:
        print("\n=== Per-ticker realized cost (bps) ===")
        per_ticker = (
            df.groupby("ticker")
            .agg(
                n=("ticker", "size"),
                mean_slippage_bps=("slippage_bps", "mean"),
                median_slippage_bps=("slippage_bps", "median"),
                mean_total_cost_bps=("total_cost_bps", "mean"),
            )
            .sort_values("mean_total_cost_bps", ascending=False)
        )
        print(per_ticker.to_string())


async def main() -> None:
    ap = argparse.ArgumentParser(description="Analyze realized fill friction")
    ap.add_argument("--days", type=int, default=90, help="Lookback window in calendar days")
    args = ap.parse_args()

    df = await _load_fills(args.days)
    if df.empty:
        print(f"No fills recorded in the last {args.days} days.")
        print("The QENG-3a fill ledger exists but is empty; run auto-execution (paper or live)")
        print("to accumulate data, then re-run this script.")
        return

    df = _compute_metrics(df)
    summary = _summarize(df)
    _print_summary(summary, df)


if __name__ == "__main__":
    asyncio.run(main())
