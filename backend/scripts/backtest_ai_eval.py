#!/usr/bin/env python3
"""
Backtest the AI pre-execution evaluator against historical signals.

Loads resolved signals from the database, runs each through
services.ai_evaluator.evaluate_trade(), and compares the outcomes of
AI-approved signals vs AI-blocked signals. This estimates whether the
LLM gate would have improved live execution results.

Results are cached on disk so the script can be resumed if interrupted.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import math
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from tqdm.asyncio import tqdm_asyncio

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database import AsyncSessionLocal
from services.ai_evaluator import evaluate_trade
from services.http_client import close_sessions

log = logging.getLogger("backtest_ai_eval")

DEFAULT_OUTPUT = ROOT / "analysis_output" / "ai_eval_backtest.csv"
CACHE_PATH = ROOT / "analysis_output" / "ai_eval_backtest_cache.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backtest AI pre-execution evaluator")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max signals to evaluate (0 = all with outcomes)",
    )
    parser.add_argument(
        "--since",
        type=str,
        default="",
        help="Only evaluate signals created on or after this date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Max concurrent LLM calls",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT),
        help="Path for the per-signal result CSV",
    )
    parser.add_argument(
        "--cache",
        type=str,
        default=str(CACHE_PATH),
        help="Path for the resume cache CSV",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Ignore existing cache and re-evaluate everything",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="",
        help="Override AI_EVAL_PROVIDER (openai | anthropic | kimi)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="",
        help="Override AI_EVAL_MODEL",
    )
    return parser.parse_args()


def _calc_sharpe(returns: pd.Series, ann_factor: float = 252.0) -> float:
    """Annualized Sharpe ratio; returns 0 for insufficient data."""
    if len(returns) < 3 or returns.std() == 0:
        return 0.0
    return (returns.mean() / returns.std()) * math.sqrt(ann_factor)


def _signal_to_dict(row) -> dict:
    """Convert a Signal ORM row into the dict format expected by evaluate_trade."""
    return {
        "ticker": row.ticker,
        "action": row.action,
        "confidence": row.confidence,
        "price": row.price,
        "entry": row.entry,
        "stop": row.stop,
        "target": row.target,
        "style": row.style or "swing",
        "rationale": row.rationale or [],
        "sources": row.sources or [],
        "sectorEtf": row.sector_etf,
        "cohort": (row.extra_data or {}).get("cohort", "") if row.extra_data else "",
    }


async def load_signals(limit: int, since: str):
    """Load resolved historical signals from the database."""
    async with AsyncSessionLocal() as db:
        stmt = (
            select(
                __import__("models").Signal.id,
                __import__("models").Signal.ticker,
                __import__("models").Signal.action,
                __import__("models").Signal.confidence,
                __import__("models").Signal.price,
                __import__("models").Signal.entry,
                __import__("models").Signal.stop,
                __import__("models").Signal.target,
                __import__("models").Signal.style,
                __import__("models").Signal.rationale,
                __import__("models").Signal.sources,
                __import__("models").Signal.sector_etf,
                __import__("models").Signal.extra_data,
                __import__("models").Signal.outcome_pct,
                __import__("models").Signal.outcome_1d,
                __import__("models").Signal.outcome_3d,
                __import__("models").Signal.outcome_14d,
                __import__("models").Signal.hit_stop,
                __import__("models").Signal.hit_target,
                __import__("models").Signal.exit_type,
                __import__("models").Signal.created_at,
            )
            .where(__import__("models").Signal.outcome_pct.isnot(None))
            .order_by(__import__("models").Signal.created_at)
        )
        if since:
            stmt = stmt.where(__import__("models").Signal.created_at >= since)
        if limit > 0:
            stmt = stmt.limit(limit)

        result = await db.execute(stmt)
        rows = result.all()
    return rows


async def evaluate_one(row, semaphore: asyncio.Semaphore):
    """Run a single signal through the AI evaluator."""
    async with semaphore:
        sig = _signal_to_dict(row)
        ai_result = await evaluate_trade(sig)
        return {
            "signal_id": row.id,
            "ticker": row.ticker,
            "action": row.action,
            "confidence": row.confidence,
            "created_at": row.created_at,
            "ai_approved": ai_result.approved,
            "ai_reasoning": ai_result.reasoning,
            "ai_risk_flag": ai_result.risk_flag,
            "ai_confidence": ai_result.confidence,
            "outcome_pct": row.outcome_pct,
            "outcome_1d": row.outcome_1d,
            "outcome_3d": row.outcome_3d,
            "outcome_14d": row.outcome_14d,
            "hit_stop": row.hit_stop,
            "hit_target": row.hit_target,
            "exit_type": row.exit_type,
        }


def print_summary(df: pd.DataFrame) -> None:
    """Print aggregate statistics comparing approved vs blocked signals."""
    total = len(df)
    approved = df[df["ai_approved"]]
    blocked = df[~df["ai_approved"]]

    print("\n=== AI Evaluator Backtest Summary ===")
    print(f"Total signals evaluated: {total}")
    print(f"AI approved: {len(approved)} ({len(approved) / total * 100:.1f}%)")
    print(f"AI blocked: {len(blocked)} ({len(blocked) / total * 100:.1f}%)")

    if len(approved) == 0 or len(blocked) == 0:
        print("\nNot enough data for both groups.")
        return

    def _group_stats(group: pd.DataFrame, label: str):
        returns = group["outcome_pct"].dropna()
        if len(returns) == 0:
            print(f"\n{label}: no returns data")
            return
        wins = (returns > 0).sum()
        print(f"\n{label} (n={len(returns)}):")
        print(f"  Win rate: {wins / len(returns) * 100:.1f}%")
        print(f"  Mean return: {returns.mean() * 100:.2f}%")
        print(f"  Median return: {returns.median() * 100:.2f}%")
        print(f"  Std dev: {returns.std() * 100:.2f}%")
        print(f"  Sharpe (daily, approx): {_calc_sharpe(returns):.2f}")
        print(f"  Hit stop: {group['hit_stop'].sum()} / {group['hit_stop'].notna().sum()}")
        print(f"  Hit target: {group['hit_target'].sum()} / {group['hit_target'].notna().sum()}")

    _group_stats(approved, "AI Approved")
    _group_stats(blocked, "AI Blocked")

    # Confusion-style view: how often was the AI "right"?
    approved_returns = approved["outcome_pct"].dropna()
    blocked_returns = blocked["outcome_pct"].dropna()
    true_positives = (approved_returns > 0).sum()  # approved and won
    false_positives = (approved_returns <= 0).sum()  # approved and lost
    true_negatives = (blocked_returns <= 0).sum()  # blocked and would have lost
    false_negatives = (blocked_returns > 0).sum()  # blocked but would have won

    print("\n=== Confusion-style view ===")
    print(f"Approved & won (TP): {true_positives}")
    print(f"Approved & lost (FP): {false_positives}")
    print(f"Blocked & would have lost (TN): {true_negatives}")
    print(f"Blocked but would have won (FN): {false_negatives}")

    if (true_positives + false_positives + true_negatives + false_negatives) > 0:
        accuracy = (true_positives + true_negatives) / (
            true_positives + false_positives + true_negatives + false_negatives
        )
        print(f"Accuracy (approve=long, block=flat): {accuracy * 100:.1f}%")

    # Value add: what would the approved-only portfolio look like?
    if len(approved_returns) > 0:
        print("\n=== Portfolio impact (naive) ===")
        print(f"Buy-and-hold all signals mean return: {df['outcome_pct'].mean() * 100:.2f}%")
        print(f"Only AI-approved mean return: {approved_returns.mean() * 100:.2f}%")
        print(f"Delta: {(approved_returns.mean() - df['outcome_pct'].mean()) * 100:.2f}% (positive means AI helped)")


async def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    import os

    if args.provider:
        os.environ["AI_EVAL_PROVIDER"] = args.provider
    if args.model:
        os.environ["AI_EVAL_MODEL"] = args.model

    settings_provider = __import__("config").get_settings().ai_eval_provider
    log.info("Using AI provider: %s", settings_provider)

    # Load cache
    done_ids: set[int] = set()
    cache_rows: list[dict] = []
    cache_path = Path(args.cache)
    if cache_path.exists() and not args.no_cache:
        cache_df = pd.read_csv(cache_path)
        done_ids = set(cache_df["signal_id"].tolist())
        cache_rows = cache_df.to_dict("records")
        log.info("Loaded %d cached evaluations from %s", len(done_ids), cache_path)

    rows = await load_signals(args.limit, args.since)
    rows_to_eval = [r for r in rows if r.id not in done_ids]
    log.info("Found %d signals with outcomes; %d already cached", len(rows), len(done_ids))
    log.info("Evaluating %d new signals with concurrency=%d", len(rows_to_eval), args.concurrency)

    semaphore = asyncio.Semaphore(args.concurrency)

    new_results: list[dict] = []
    if rows_to_eval:
        tasks = [evaluate_one(r, semaphore) for r in rows_to_eval]
        new_results = await tqdm_asyncio.gather(*tasks, desc="AI eval backtest")

    all_results = cache_rows + new_results
    df = pd.DataFrame(all_results)

    if new_results:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache_path, index=False)
        log.info("Wrote cache to %s", cache_path)

    if df.empty:
        log.warning("No results to summarize")
        await close_sessions()
        return

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    log.info("Wrote results to %s", output_path)

    print_summary(df)
    await close_sessions()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        # Best-effort cleanup for the synchronous exit path.
        try:
            asyncio.run(close_sessions())
        except Exception:
            pass
