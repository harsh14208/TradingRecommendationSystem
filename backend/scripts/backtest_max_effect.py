#!/usr/bin/env python3
"""
Backtest: MAX-effect conditioning (Chen et al., "Maxing Out Short-term Reversals").

Tests whether the trailing 21-day maximum daily return (MAX_21) improves the MR
book when used as an entry gate or sizing factor.  The feature is already
emitted by backtest_technicals.py; this harness evaluates causal filter and size
rules without re-running the 26-year simulation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.backtest_technicals import run_portfolio_simulation

DEFAULT_SLOTS = 5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MAX-effect backtest")
    parser.add_argument(
        "--trades",
        default=str(ROOT / "data" / "backtest_trades_is.csv"),
        help="Path to backtest_trades_is.csv",
    )
    parser.add_argument("--slots", type=int, default=DEFAULT_SLOTS)
    parser.add_argument(
        "--strategy",
        choices=["filter_top", "filter_bottom", "size", "both"],
        default="both",
        help="filter_top = only top percentile; size = linear percentile sizing",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.67,
        help="Percentile threshold for filter strategies (0-1)",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "data" / "backtest_max_effect.csv"),
    )
    return parser.parse_args()


def trade_stats(trades: pd.DataFrame) -> dict:
    r = trades["net_pct"].dropna()
    if r.empty:
        return {"n": 0, "wr": 0.0, "avg": 0.0, "sharpe": 0.0}
    avg = r.mean()
    std = r.std(ddof=0)
    sharpe = (avg / std) * np.sqrt(252 / 5.0) if std > 1e-9 else 0.0
    return {"n": len(r), "wr": (r > 0).mean() * 100.0, "avg": avg, "sharpe": sharpe}


def apply_max_effect(trades: pd.DataFrame, strategy: str, threshold: float) -> pd.DataFrame:
    trades = trades.copy().sort_values("date").reset_index(drop=True)
    # Expanding percentile to avoid look-ahead
    mults = []
    for i in range(len(trades)):
        hist = trades["max21"].iloc[:i]
        current = trades["max21"].iloc[i]
        if len(hist) < 10 or pd.isna(current):
            mults.append(1.0)
            continue
        pct = (hist <= current).mean()
        if strategy == "filter_top":
            mults.append(1.0 if pct >= threshold else 0.0)
        elif strategy == "filter_bottom":
            mults.append(1.0 if pct <= (1 - threshold) else 0.0)
        elif strategy == "size":
            # size in [0.5, 1.5] anchored at median
            mults.append(float(np.clip(0.5 + pct, 0.5, 1.5)))
        elif strategy == "both":
            if pct < threshold:
                mults.append(0.0)
            else:
                mults.append(float(np.clip(0.5 + pct, 0.5, 1.5)))
        else:
            mults.append(1.0)

    trades["max_mult"] = mults
    trades["net_pct_max"] = trades["net_pct"] * trades["max_mult"]
    return trades


def main() -> None:
    args = parse_args()
    trades = pd.read_csv(args.trades)
    if "max21" not in trades.columns:
        raise SystemExit("max21 column missing; re-run backtest_technicals.py with current code.")

    trades["date"] = pd.to_datetime(trades["date"])
    baseline_pm = run_portfolio_simulation(trades, max_concurrent=args.slots, quiet=True) or {}
    baseline_pm = {k: baseline_pm.get(k, 0.0) for k in ("ann_sharpe", "cagr", "max_dd", "skipped")}
    baseline_ts = trade_stats(trades)

    print("=" * 70)
    print("MAX-Effect Conditioning Backtest (Chen et al.)")
    print(f"Trades loaded: {len(trades)}  |  Slots: {args.slots}")
    print("=" * 70)
    print("\nBaseline (all trades)")
    print(f"  Trades: {baseline_ts['n']}")
    print(f"  WR:     {baseline_ts['wr']:.1f}%")
    print(f"  Avg:    {baseline_ts['avg']:+.2f}%")
    print(f"  Trd Sh: {baseline_ts['sharpe']:.2f}")
    print(f"  Port Sh:{baseline_pm['ann_sharpe']:.2f}")
    print(f"  Ann Ret:{baseline_pm['cagr']:+.2f}%")
    print(f"  Max DD: -{baseline_pm['max_dd']:.2f}%")

    best_variant = None
    strategies = ["filter_top", "filter_bottom", "size", "both"] if args.strategy == "both" else [args.strategy]

    for strategy in strategies:
        rc = apply_max_effect(trades.copy(), strategy, args.threshold)
        taken = rc[rc["max_mult"] > 0.0].copy()
        taken["net_pct"] = taken["net_pct_max"]

        pm = run_portfolio_simulation(taken, max_concurrent=args.slots, quiet=True) or {}
        pm = {k: pm.get(k, 0.0) for k in ("ann_sharpe", "cagr", "max_dd", "skipped")}
        ts = trade_stats(taken)
        variant = {
            "strategy": strategy,
            "trades_taken": int(len(taken)),
            "trades_skipped": int(len(rc) - len(taken)),
            "wr": ts["wr"],
            "avg": ts["avg"],
            "trade_sharpe": ts["sharpe"],
            "port_sharpe": pm["ann_sharpe"],
            "ann_return": pm["cagr"],
            "max_dd": pm["max_dd"],
        }

        print(f"\nVariant: {strategy} (thr={args.threshold:.0%})")
        print(f"  Taken:  {variant['trades_taken']}  Skipped: {variant['trades_skipped']}")
        print(f"  WR:     {variant['wr']:.1f}%")
        print(f"  Avg:    {variant['avg']:+.2f}%")
        print(f"  Trd Sh: {variant['trade_sharpe']:.2f}")
        print(f"  Port Sh:{variant['port_sharpe']:.2f}")
        print(f"  Ann Ret:{variant['ann_return']:+.2f}%")
        print(f"  Max DD: -{variant['max_dd']:.2f}%")

        if best_variant is None or variant["port_sharpe"] > best_variant["port_sharpe"]:
            best_variant = variant

    print("\n" + "=" * 70)
    if best_variant:
        print(f"Best variant: {best_variant['strategy']}  Port Sharpe {best_variant['port_sharpe']:.2f}")
        delta_sh = best_variant["port_sharpe"] - baseline_pm["ann_sharpe"]
        delta_dd = abs(best_variant["max_dd"]) - abs(baseline_pm["max_dd"])
        print(f"Δ Sharpe vs baseline: {delta_sh:+.2f}")
        print(f"Δ MaxDD vs baseline: {delta_dd:+.2f}pp")

        if delta_sh > 0.20 and delta_dd <= 1.0 and best_variant["trades_taken"] >= max(50, len(trades) * 0.5):
            print("VERDICT: GRADUATE — integrate into live signal engine / L-stack.")
        elif delta_sh > 0.10 and delta_dd <= 2.0:
            print("VERDICT: PROMISING — refine threshold or combine with other features.")
        elif delta_sh > 0.05:
            print("VERDICT: MARGINAL — weak transfer of published MAX effect.")
        else:
            print("VERDICT: REJECT — no material lift in this dataset.")

    rc = apply_max_effect(trades.copy(), args.strategy, args.threshold)
    rc.to_csv(args.output, index=False)
    print(f"\nWrote per-trade MAX-effect results to {args.output}")


if __name__ == "__main__":
    main()
