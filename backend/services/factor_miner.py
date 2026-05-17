"""
Automated Factor Mining.

Brute-forces single-source and pairwise-source combinations from resolved signals,
ranks each combination by out-of-sample Sharpe ratio, and promotes the top factors
into a JSON file that signal_engine.py reads to apply adaptive source weights.

Run weekly via `asyncio.create_task(run_factor_mining())`.
Results written to backend/data/factor_weights.json.
"""
import asyncio
import json
import logging
import math
import os
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Optional

log = logging.getLogger("signal.factor_miner")

_DATA_DIR = Path(__file__).parent.parent / "data"
_WEIGHTS_FILE = _DATA_DIR / "factor_weights.json"

# Min signals required for a combination to be considered statistically meaningful
_MIN_SIGNALS = 8
# How much of the timeline to use as training vs test
_TRAIN_SPLIT = 0.70
# Max top factors to persist (kept small to avoid overfitting via too many weights)
_TOP_N = 20


def _sharpe(returns: list[float]) -> Optional[float]:
    """Annualised Sharpe (52 signal cycles/year, 7-day hold assumption)."""
    n = len(returns)
    if n < 3:
        return None
    mean_r = sum(returns) / n
    variance = sum((r - mean_r) ** 2 for r in returns) / (n - 1)
    std_r = math.sqrt(variance) if variance > 0 else 0
    if std_r == 0:
        return None
    return round((mean_r / std_r) * math.sqrt(52), 3)


def _win_rate(returns: list[float]) -> float:
    if not returns:
        return 0.0
    return round(sum(1 for r in returns if r > 0) / len(returns), 3)


async def run_factor_mining() -> dict:
    """
    Main entry point. Reads all resolved sent signals from the DB, brute-forces
    source combinations, and writes factor_weights.json.

    Returns a summary dict: {run_at, combinations_tested, top_factors, promoted_count}.
    """
    log.info("[factor_miner] Starting weekly factor mining run…")
    try:
        rows = await _load_resolved_signals()
    except Exception as e:
        log.warning(f"[factor_miner] DB read failed: {e}")
        return {"error": str(e)}

    if len(rows) < _MIN_SIGNALS * 2:
        log.info(f"[factor_miner] Only {len(rows)} resolved signals — too few to mine.")
        return {"run_at": datetime.utcnow().isoformat(), "rows": len(rows), "skipped": True}

    # Sort by created_at (oldest first) for temporal train/test split
    rows.sort(key=lambda r: r["created_at"])

    all_sources: set[str] = set()
    for r in rows:
        all_sources.update(r["sources"])
    all_sources.discard("")

    results: list[dict] = []

    # ── Single-source factors ──────────────────────────────────────────────────
    for src in all_sources:
        subset = [r for r in rows if src in r["sources"]]
        score = _eval_factor(subset, label=src)
        if score:
            results.append(score)

    # ── Pairwise source combinations ────────────────────────────────────────────
    for src_a, src_b in combinations(sorted(all_sources), 2):
        subset = [r for r in rows if src_a in r["sources"] and src_b in r["sources"]]
        label = f"{src_a}+{src_b}"
        score = _eval_factor(subset, label=label)
        if score:
            results.append(score)

    if not results:
        log.info("[factor_miner] No combinations met the minimum signal threshold.")
        return {"run_at": datetime.utcnow().isoformat(), "combinations_tested": 0}

    # Rank by OOS Sharpe (descending)
    results.sort(key=lambda x: x.get("oos_sharpe") or -99, reverse=True)
    top = results[:_TOP_N]

    summary = {
        "run_at":               datetime.utcnow().isoformat(),
        "signals_used":         len(rows),
        "sources_found":        sorted(all_sources),
        "combinations_tested":  len(results),
        "top_factors":          top,
        "promoted_count":       len([t for t in top if (t.get("oos_sharpe") or 0) > 0.3]),
    }

    # Persist — surface a clear error if the directory is not writable.
    # In Docker the data/ dir must be volume-mounted or created by the Dockerfile
    # with chmod 777; a permissions failure here would silently skip all future
    # weekly runs without this explicit log.
    try:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        _WEIGHTS_FILE.write_text(json.dumps(summary, indent=2))
        log.info(
            f"[factor_miner] Done. {len(results)} combinations tested. "
            f"Top factor: {top[0]['label']} (OOS Sharpe {top[0].get('oos_sharpe')}) "
            f"— results written to {_WEIGHTS_FILE}"
        )
    except OSError as e:
        log.error(
            f"[factor_miner] WRITE FAILED — {_WEIGHTS_FILE}: {e}. "
            "In Docker, ensure the data/ directory is volume-mounted with write "
            "permissions (see docker-compose.yml volumes + Dockerfile RUN chmod 777 /app/data)."
        )
        # Return the summary in-memory so the caller gets results even if disk write failed
    return summary


def _eval_factor(rows: list[dict], label: str) -> Optional[dict]:
    if len(rows) < _MIN_SIGNALS:
        return None

    # Temporal train / test split — never look ahead
    split = max(_MIN_SIGNALS, int(len(rows) * _TRAIN_SPLIT))
    test_rows = rows[split:]
    if len(test_rows) < 3:
        return None

    test_returns = [r["outcome_pct"] for r in test_rows]
    oos_sharpe = _sharpe(test_returns)
    oos_wr = _win_rate(test_returns)
    oos_avg = round(sum(test_returns) / len(test_returns), 3)

    # Also compute in-sample stats for reference (not used for ranking)
    is_returns = [r["outcome_pct"] for r in rows[:split]]
    is_wr = _win_rate(is_returns) if is_returns else None

    return {
        "label":        label,
        "total_signals": len(rows),
        "oos_n":        len(test_rows),
        "oos_sharpe":   oos_sharpe,
        "oos_win_rate": oos_wr,
        "oos_avg_ret":  oos_avg,
        "is_win_rate":  is_wr,
    }


async def _load_resolved_signals() -> list[dict]:
    from database import AsyncSessionLocal
    from models import Signal
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        rows = (await db.execute(
            select(
                Signal.ticker,
                Signal.action,
                Signal.confidence,
                Signal.sources,
                Signal.outcome_pct,
                Signal.created_at,
            )
            .where(Signal.is_sent == True)
            .where(Signal.outcome_pct.isnot(None))
            .order_by(Signal.created_at)
        )).all()

    return [
        {
            "ticker":      r.ticker,
            "action":      r.action,
            "confidence":  r.confidence,
            "sources":     r.sources or [],
            "outcome_pct": r.outcome_pct,
            "created_at":  r.created_at,
        }
        for r in rows
    ]


def load_factor_weights() -> dict:
    """Return the most recently mined factor weights (synchronous, for engine use)."""
    try:
        if _WEIGHTS_FILE.exists():
            return json.loads(_WEIGHTS_FILE.read_text())
    except Exception:
        pass
    return {}


async def get_factor_mining_results() -> dict:
    """Return cached results or trigger a fresh run if no file exists."""
    weights = load_factor_weights()
    if weights and not weights.get("skipped"):
        return weights
    return await run_factor_mining()
