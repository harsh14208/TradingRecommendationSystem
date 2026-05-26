"""
Public (unauthenticated) endpoints — used by the public track record page.
No PII is exposed. All stats are aggregate and anonymised.
"""
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Signal
from routers.signals import _best_outcome

router = APIRouter(prefix="/api/public", tags=["public"])


def _utcnow_naive() -> datetime:
    """UTC timestamp compatible with existing naive SQLAlchemy DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("/track-record")
async def public_track_record(db: AsyncSession = Depends(get_db)):
    """
    Aggregate win-rate stats with no PII — safe to expose without auth.
    Powers the public /track-record.html page.
    """
    rows = (await db.execute(
        select(Signal).where(
            Signal.is_sent == True,
            Signal.outcome_1d.isnot(None)   # at least 1 resolved outcome
        )
    )).scalars().all()

    if not rows:
        return {"no_data": True}

    def _stats(returns):
        if not returns:
            return None
        wins   = [r for r in returns if r > 0]
        losses = [r for r in returns if r <= 0]
        n      = len(returns)
        mean   = sum(returns) / n
        std    = math.sqrt(sum((r - mean) ** 2 for r in returns) / max(n - 1, 1)) if n > 1 else 0
        sharpe = round((mean / std) * math.sqrt(52), 2) if std > 0 and n >= 5 else None
        return {
            "n":          n,
            "win_rate":   round(len(wins) / n * 100, 1),
            "avg_return": round(mean, 2),
            "avg_win":    round(sum(wins) / len(wins), 2) if wins else None,
            "avg_loss":   round(sum(losses) / len(losses), 2) if losses else None,
            "sharpe":     sharpe,
        }

    all_returns = [_best_outcome(r) for r in rows if _best_outcome(r) is not None]
    overall     = _stats(all_returns)

    # By action
    action_buckets: dict = defaultdict(list)
    for r in rows:
        v = _best_outcome(r)
        if v is not None:
            action_buckets[r.action].append(v)
    by_action = [{"action": k, **(_stats(v) or {})} for k, v in sorted(action_buckets.items())]

    # By ticker (top 10 by signal count, min 3 signals)
    ticker_buckets: dict = defaultdict(list)
    for r in rows:
        v = _best_outcome(r)
        if v is not None:
            ticker_buckets[r.ticker].append(v)
    ticker_stats = []
    for ticker, returns in ticker_buckets.items():
        if len(returns) < 2:
            continue
        s = _stats(returns)
        if s:
            ticker_stats.append({"ticker": ticker, **s})
    ticker_stats.sort(key=lambda x: -x["n"])
    top_tickers = ticker_stats[:15]

    # By month (last 6 months)
    month_buckets: dict = defaultdict(list)
    for r in rows:
        v = _best_outcome(r)
        if v is not None and r.created_at:
            key = r.created_at.strftime("%Y-%m")
            month_buckets[key].append(v)
    by_month = []
    for month in sorted(month_buckets)[-6:]:
        s = _stats(month_buckets[month])
        if s:
            by_month.append({"month": month, **s})

    # Best and worst signals (ticker+action only, no user data)
    scored = [(r, _best_outcome(r)) for r in rows if _best_outcome(r) is not None]
    sorted_scored = sorted(scored, key=lambda x: x[1], reverse=True)

    def _brief(r, v):
        return {
            "ticker":     r.ticker,
            "action":     r.action,
            "confidence": round(r.confidence, 0),
            "return_pct": round(v, 2),
            "date":       r.created_at.strftime("%b %d, %Y") if r.created_at else "—",
            "sources":    r.sources or [],
        }

    top5    = [_brief(r, v) for r, v in sorted_scored[:5]]
    worst5  = [_brief(r, v) for r, v in sorted_scored[-5:] if v < 0]

    # Signal cadence (signals per week over last 4 weeks)
    four_weeks_ago = _utcnow_naive() - timedelta(weeks=4)
    recent = [r for r in rows if r.created_at and r.created_at >= four_weeks_ago]
    signals_per_week = round(len(recent) / 4, 1) if recent else 0

    return {
        "overall":           overall,
        "by_action":         by_action,
        "top_tickers":       top_tickers,
        "by_month":          by_month,
        "top_signals":       top5,
        "worst_signals":     worst5,
        "total_signals":     len(rows),
        "signals_per_week":  signals_per_week,
        "data_since":        min((r.created_at for r in rows if r.created_at), default=None),
    }
