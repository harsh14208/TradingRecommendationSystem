"""
Public (unauthenticated) endpoints — used by the public track record page.
No PII is exposed. All stats are aggregate and anonymised.
"""

import asyncio
import math
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from database import get_db
from fastapi import APIRouter, Depends
from models import Signal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from routers.signals import _best_outcome

router = APIRouter(prefix="/api/public", tags=["public"])

# Public track-record stats are aggregate and change only as new outcomes resolve.
# Cache for 60s to avoid re-scanning the entire signals table on every page view.
_TRACK_RECORD_TTL_S = 60.0
_track_record_cache: dict | None = None
_track_record_cache_at = 0.0
_track_record_fetch_lock = asyncio.Lock()


def _clear_track_record_cache() -> None:
    """Test helper: invalidate the public track-record cache."""
    global _track_record_cache, _track_record_cache_at
    _track_record_cache = None
    _track_record_cache_at = 0.0


def _utcnow_naive() -> datetime:
    """UTC timestamp compatible with existing naive SQLAlchemy DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("/version-info")
async def version_info():
    """TSYS-11c: the policy / model / calibration versions behind current signals,
    so analyst-facing views can show explainability badges. No auth or PII."""
    import json
    from pathlib import Path

    data_dir = Path(__file__).resolve().parent.parent / "data"

    def _read_json_field(filename: str, field: str):
        try:
            return json.loads((data_dir / filename).read_text()).get(field)
        except Exception:
            return None

    try:
        from services.signal_policy import get_current_policy_version

        policy_version = get_current_policy_version()
    except Exception:
        policy_version = None

    return {
        "policy_version": policy_version,
        "model_trained_at": _read_json_field("signal_ml_features.json", "trained_at"),
        "calibration_version": _read_json_field("calibration.json", "last_run"),
    }


@router.get("/track-record")
async def public_track_record(db: AsyncSession = Depends(get_db)):
    global _track_record_cache, _track_record_cache_at
    now = time.monotonic()
    if _track_record_cache is not None and (now - _track_record_cache_at) < _TRACK_RECORD_TTL_S:
        return _track_record_cache

    async with _track_record_fetch_lock:
        now = time.monotonic()
        if _track_record_cache is not None and (now - _track_record_cache_at) < _TRACK_RECORD_TTL_S:
            return _track_record_cache

        # Fetch fresh aggregate win-rate stats (no PII).
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.outcome_1d.isnot(None),
                    )
                )
            )
            .scalars()
            .all()
        )

        if not rows:
            return {"no_data": True}

        def _stats(returns):
            if not returns:
                return None
            wins = [r for r in returns if r > 0]
            losses = [r for r in returns if r <= 0]
            n = len(returns)
            mean = sum(returns) / n
            std = math.sqrt(sum((r - mean) ** 2 for r in returns) / max(n - 1, 1)) if n > 1 else 0
            # Require a meaningful sample and cap the ratio so tiny, lucky samples
            # don't produce absurd per-ticker Sharpe figures.
            if n < 15 or std == 0:
                sharpe = None
            else:
                sharpe = round(min((mean / std) * math.sqrt(52), 3.0), 2)
            return {
                "n": n,
                "win_rate": round(len(wins) / n * 100, 1),
                "avg_return": round(mean, 2),
                "avg_win": round(sum(wins) / len(wins), 2) if wins else None,
                "avg_loss": round(sum(losses) / len(losses), 2) if losses else None,
                "sharpe": sharpe,
            }

        all_returns = [_best_outcome(r) for r in rows if _best_outcome(r) is not None]
        overall = _stats(all_returns)

        action_buckets: dict = defaultdict(list)
        for r in rows:
            v = _best_outcome(r)
            if v is not None:
                action_buckets[r.action].append(v)
        by_action = [{"action": k, **(_stats(v) or {})} for k, v in sorted(action_buckets.items())]

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

        scored = [(r, _best_outcome(r)) for r in rows if _best_outcome(r) is not None]
        sorted_scored = sorted(scored, key=lambda x: x[1], reverse=True)

        def _brief(r, v):
            return {
                "ticker": r.ticker,
                "action": r.action,
                "confidence": round(r.confidence, 0),
                "return_pct": round(v, 2),
                "date": r.created_at.strftime("%b %d, %Y") if r.created_at else "—",
                "sources": r.sources or [],
            }

        top5 = [_brief(r, v) for r, v in sorted_scored[:5]]
        worst5 = [_brief(r, v) for r, v in sorted_scored[-5:] if v < 0]

        four_weeks_ago = _utcnow_naive() - timedelta(weeks=4)
        recent = [r for r in rows if r.created_at and r.created_at >= four_weeks_ago]
        signals_per_week = round(len(recent) / 4, 1) if recent else 0

        result = {
            "overall": overall,
            "by_action": by_action,
            "top_tickers": top_tickers,
            "by_month": by_month,
            "top_signals": top5,
            "worst_signals": worst5,
            "total_signals": len(rows),
            "signals_per_week": signals_per_week,
            "data_since": min((r.created_at for r in rows if r.created_at), default=None),
        }
        _track_record_cache = result
        _track_record_cache_at = now
        return result
