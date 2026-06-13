#!/usr/bin/env python3
"""
Run the QENG-3d execution-policy simulator over a backtest trades CSV.

Example:
    python scripts/run_execution_policy_simulation.py \
        --input data/backtest_trades.csv \
        --output-dir data/execution_policy_sim

Output:
    - summary.json   policy-level cost-adjusted comparison
    - per_trade.csv  each trade under each policy
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.execution_policy_simulator import (
    DEFAULT_POLICIES,
    simulate_policies,
)
from services.market_data import get_history

log = logging.getLogger("signal.trade.run_exec_policy_sim")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Execution-policy simulator (QENG-3d)")
    p.add_argument("--input", required=True, type=Path, help="Backtest trades CSV")
    p.add_argument("--output-dir", type=Path, default=Path("data/execution_policy_sim"))
    p.add_argument("--friction-pct", type=float, default=0.50, help="Baseline market-impact + commission (%)")
    p.add_argument("--limit-atr-frac", type=float, default=0.5, help="Limit price offset as fraction of ATR(%)")
    p.add_argument("--passive-friction-discount", type=float, default=0.5, help="Friction multiplier for passive fills")
    p.add_argument(
        "--policies",
        nargs="+",
        choices=DEFAULT_POLICIES,
        default=DEFAULT_POLICIES,
        help="Policies to evaluate",
    )
    p.add_argument("--register-experiment", action="store_true", help="Write a ResearchExperiment row")
    return p.parse_args()


async def _load_price_data(trades: pd.DataFrame) -> dict[str, pd.DataFrame]:
    tickers = trades["ticker"].unique().tolist()
    min_date = pd.to_datetime(trades["entry_date"]).min()
    max_date = pd.to_datetime(trades["exit_date"]).max()
    # Pad a few days so next-bar lookups near the end are safe.
    max_date = max_date + timedelta(days=5)
    period_days = (max_date - min_date).days + 5
    period = f"{max(period_days, 30)}d"

    data: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        try:
            df = await get_history(ticker, period=period, interval="1d")
            if df is None or df.empty:
                log.warning("[exec_sim] no daily data for %s", ticker)
                continue
            df = df.copy()
            df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
            data[ticker] = df
        except Exception as e:
            log.warning("[exec_sim] %s fetch error: %s", ticker, e)
    return data


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    aliases = {
        "entry_date": ["entry_date", "date", "entry_day", "signal_date"],
        "exit_date": ["exit_date", "exit_day"],
        "entry_price": ["entry_price", "entry"],
        "hold_days": ["hold_days", "exit_day", "days_held"],
    }
    df = df.copy()
    for canonical, names in aliases.items():
        for name in names:
            if name in df.columns and canonical not in df.columns:
                df[canonical] = df[name]
                break
    return df


def _trades_to_records(df: pd.DataFrame) -> list[dict]:
    df = _normalise_columns(df)
    required = {"ticker", "action", "entry_date", "entry_price", "exit_price"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Input CSV missing required columns (accepted aliases included): {missing}")
    records = df.to_dict("records")
    for r in records:
        r["entry_date"] = pd.to_datetime(r["entry_date"])
        if "exit_date" in r:
            r["exit_date"] = pd.to_datetime(r["exit_date"])
    return records


def _summary_to_dict(summary):
    return {
        "policy": summary.policy,
        "n_total": summary.n_total,
        "n_filled": summary.n_filled,
        "fill_rate": summary.fill_rate,
        "avg_gross_bps": summary.avg_gross_bps,
        "avg_net_bps": summary.avg_net_bps,
        "win_rate": summary.win_rate,
        "gross_sharpe_annual": summary.gross_sharpe_annual,
        "net_sharpe_annual": summary.net_sharpe_annual,
        "avg_entry_slippage_bps": summary.avg_entry_slippage_bps,
        "notes": summary.notes,
    }


async def _register_experiment(output_dir: Path, args: argparse.Namespace, best_policy_name: str):
    try:
        from database import AsyncSessionLocal
        from models import ResearchExperiment

        async with AsyncSessionLocal() as db:
            exp = ResearchExperiment(
                name="QENG-3d execution-policy simulator",
                hypothesis=f"Best execution policy = {best_policy_name}",
                status="completed",
                metadata_json={
                    "input": str(args.input),
                    "friction_pct": args.friction_pct,
                    "limit_atr_frac": args.limit_atr_frac,
                    "passive_friction_discount": args.passive_friction_discount,
                    "output_dir": str(output_dir),
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            db.add(exp)
            await db.commit()
            log.info("[exec_sim] registered ResearchExperiment id=%s", exp.id)
    except Exception as e:
        log.warning("[exec_sim] could not register experiment: %s", e)


def _print_table(summaries: list):
    header = f"{'Policy':<14} {'N':>5} {'Filled':>6} {'Fill%':>6} {'Gross bps':>10} {'Net bps':>10} {'Win%':>6} {'Net Sharpe':>11}"
    print(header)
    print("-" * len(header))
    for s in summaries:
        print(
            f"{s.policy:<14} {s.n_total:>5} {s.n_filled:>6} {s.fill_rate:>6.2%} "
            f"{s.avg_gross_bps:>10.2f} {s.avg_net_bps:>10.2f} {s.win_rate:>6.2%} "
            f"{s.net_sharpe_annual if s.net_sharpe_annual is not None else '':>11}"
        )


async def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    args = _parse_args()

    if not args.input.exists():
        log.error("[exec_sim] input file not found: %s", args.input)
        return 1

    trades_df = _normalise_columns(pd.read_csv(args.input))
    trades = _trades_to_records(trades_df)
    log.info("[exec_sim] loaded %d trades from %s", len(trades), args.input)

    price_data = await _load_price_data(trades_df)
    log.info("[exec_sim] fetched OHLCV for %d/%d tickers", len(price_data), trades_df["ticker"].nunique())

    result = simulate_policies(
        trades,
        price_data,
        policies=args.policies,  # type: ignore[arg-type]
        friction_pct=args.friction_pct,
        limit_atr_frac=args.limit_atr_frac,
        passive_friction_discount=args.passive_friction_discount,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "summary.json"
    per_trade_path = args.output_dir / "per_trade.csv"

    summary_path.write_text(
        json.dumps(
            {
                "run_at": datetime.now(timezone.utc).isoformat(),
                "input": str(args.input),
                "friction_pct": args.friction_pct,
                "limit_atr_frac": args.limit_atr_frac,
                "passive_friction_discount": args.passive_friction_discount,
                "policies": [s.policy for s in result.summaries],
                "summaries": [_summary_to_dict(s) for s in result.summaries],
            },
            indent=2,
            default=str,
        )
    )

    pd.DataFrame(result.per_trade).to_csv(per_trade_path, index=False)

    _print_table(result.summaries)
    best = max(result.summaries, key=lambda s: s.avg_net_bps)
    print(f"\nBest cost-adjusted policy: {best.policy} (avg net {best.avg_net_bps:.2f} bps)")

    if args.register_experiment:
        await _register_experiment(args.output_dir, args, best.policy)

    log.info("[exec_sim] wrote %s and %s", summary_path, per_trade_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
