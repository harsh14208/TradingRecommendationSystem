"""
Per-ticker, per-source accuracy tracking.
Queries resolved signals and computes win rates grouped by source combinations.
"""
import logging
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Signal
from services.auth_svc import get_current_user

log = logging.getLogger("signal.trade.accuracy")
router = APIRouter(prefix="/api/accuracy", tags=["accuracy"])


@router.get("/sources")
async def source_accuracy(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Win rate per signal source across all resolved signals."""
    rows = (await db.execute(
        select(Signal).where(Signal.is_sent == True)
    )).scalars().all()

    stats: dict[str, dict] = defaultdict(lambda: {"wins": 0, "total": 0, "avg_ret": 0.0})

    for sig in rows:
        # Best available outcome
        outcome = sig.outcome_pct or sig.outcome_3d or sig.outcome_1d or sig.outcome_14d
        if outcome is None:
            continue
        sources = sig.sources or []
        if isinstance(sources, str):
            import json
            try: sources = json.loads(sources)
            except: sources = []
        win = 1 if outcome > 0 else 0
        for src in sources:
            s = stats[src]
            s["total"] += 1
            s["wins"]  += win
            s["avg_ret"] = round((s["avg_ret"] * (s["total"] - 1) + outcome) / s["total"], 2)

    result = []
    for src, s in sorted(stats.items(), key=lambda x: -x[1]["total"]):
        if s["total"] >= 3:
            result.append({
                "source":   src,
                "total":    s["total"],
                "wins":     s["wins"],
                "win_rate": round(s["wins"] / s["total"] * 100, 1),
                "avg_ret":  s["avg_ret"],
            })
    return result


@router.get("/tickers")
async def ticker_accuracy(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Win rate per ticker across all resolved signals."""
    rows = (await db.execute(
        select(Signal).where(Signal.is_sent == True)
    )).scalars().all()

    stats: dict[str, dict] = defaultdict(lambda: {"wins": 0, "total": 0, "avg_ret": 0.0, "sources_freq": defaultdict(int)})

    for sig in rows:
        outcome = sig.outcome_pct or sig.outcome_3d or sig.outcome_1d or sig.outcome_14d
        if outcome is None:
            continue
        t = sig.ticker
        s = stats[t]
        s["total"] += 1
        if outcome > 0: s["wins"] += 1
        s["avg_ret"] = round((s["avg_ret"] * (s["total"] - 1) + outcome) / s["total"], 2)
        for src in (sig.sources or []):
            s["sources_freq"][src] += 1

    result = []
    for ticker, s in sorted(stats.items(), key=lambda x: -x[1]["total"]):
        if s["total"] >= 2:
            top_srcs = sorted(s["sources_freq"].items(), key=lambda x: -x[1])[:4]
            result.append({
                "ticker":    ticker,
                "total":     s["total"],
                "wins":      s["wins"],
                "win_rate":  round(s["wins"] / s["total"] * 100, 1),
                "avg_ret":   s["avg_ret"],
                "top_sources": [s for s, _ in top_srcs],
            })
    return result
