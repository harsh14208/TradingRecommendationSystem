from collections import defaultdict
from datetime import datetime, timedelta, timezone
import math
import time as _time

import pytz
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database import get_db
from models import SendLog, Signal, SignalDelivery, User
from services.auth_svc import get_current_user
from services.telegram_svc import format_signal

router = APIRouter(prefix="/api/signals", tags=["signals"])

# ── 5-minute in-memory cache for expensive analytics endpoints ───────────────
# /backtest and /correlation aggregate thousands of rows with GROUP BY and cross
# joins. Caching for 5 minutes prevents concurrent dashboard loads from hammering
# the database with repeated heavy queries.
_analytics_cache: dict[str, dict] = {}
_ANALYTICS_TTL = 300   # 5 minutes


def _utcnow_naive() -> datetime:
    """UTC timestamp compatible with existing naive SQLAlchemy DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _cache_get(key: str):
    entry = _analytics_cache.get(key)
    if entry and _time.time() - entry["ts"] < _ANALYTICS_TTL:
        return entry["data"]
    return None

def _cache_set(key: str, data):
    # Evict expired entries when cache grows large
    if len(_analytics_cache) > 200:
        now = _time.time()
        expired = [k for k, v in _analytics_cache.items() if now - v["ts"] >= _ANALYTICS_TTL]
        for k in expired:
            del _analytics_cache[k]
    _analytics_cache[key] = {"data": data, "ts": _time.time()}


def _to_dict(s: Signal) -> dict:
    return {
        "id":         s.id,
        "ticker":     s.ticker,
        "company":    s.company or s.ticker,
        "action":     s.action,
        "confidence": s.confidence,
        "confidence_warning": bool(s.confidence_warning) if s.confidence_warning is not None else False,
        "price":      s.price,
        "change":     s.change or 0,
        "changePct":  s.change_pct or 0,
        "entry":      s.entry,
        "stop":       s.stop,
        "target":     s.target,
        "rr":         s.rr or "—",
        "headline":   s.headline,
        "sentiment":  s.sentiment or 0,
        "style":      s.style or "swing",
        "sources":    s.sources or [],
        "rationale":  s.rationale or [],
        "ts":         s.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if s.created_at else None,
        "date":       s.created_at.strftime("%Y-%m-%d") if s.created_at else "—",
        "isSent":     s.is_sent,
        "isSkipped":  s.is_skipped,
        "reviewed":   bool(s.reviewed) if s.reviewed is not None else False,
        "notes":      s.notes or "",
        # Engine enrichment — stored at scan time
        "plain_english":    s.plain_english,
        "session":          s.session,
        "daysToEarnings":   s.days_to_earnings,
        "nextEarningsDate": s.next_earnings_date,
        "sectorEtf":        s.sector_etf,
        "rsVsSector":       s.rs_vs_sector,
        # Outcomes
        "outcomePct":  s.outcome_pct,
        "outcome1d":   s.outcome_1d,
        "outcome3d":   s.outcome_3d,
        "outcome14d":  s.outcome_14d,
        "outcomeAt":   s.outcome_at.strftime("%Y-%m-%d") if s.outcome_at else None,
        # Expiry
        "expiresAt":   s.expires_at.strftime("%Y-%m-%dT%H:%M:%SZ") if s.expires_at else None,
    }


@router.get("")
async def list_signals(db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    action_priority = case(
        (Signal.action == "BUY",  0),
        (Signal.action == "SELL", 1),
        else_=2,
    )
    rows = (await db.execute(
        select(Signal)
        .where(Signal.is_active == True)
        .order_by(action_priority, desc(Signal.confidence), desc(Signal.created_at))
        .limit(300)
    )).scalars().all()
    return [_to_dict(r) for r in rows]


@router.get("/history")
async def signal_history(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
    start_date:  Optional[str] = Query(None),
    end_date:    Optional[str] = Query(None),
    ticker:      Optional[str] = Query(None, description="Filter to a specific ticker (case-insensitive)"),
    action:      Optional[str] = Query(None, description="BUY | SELL | HOLD"),
    min_conf:    Optional[float] = Query(None, description="Minimum confidence %"),
    max_conf:    Optional[float] = Query(None, description="Maximum confidence %"),
    outcome:     Optional[str] = Query(None, description="win | loss | open"),
):
    filters = []
    if start_date:
        try:
            filters.append(Signal.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
        except ValueError:
            pass
    if end_date:
        try:
            filters.append(Signal.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        except ValueError:
            pass
    if ticker:
        filters.append(Signal.ticker == ticker.upper().strip())
    if action and action.upper() in ("BUY", "SELL", "HOLD"):
        filters.append(Signal.action == action.upper())
    if min_conf is not None:
        filters.append(Signal.confidence >= min_conf)
    if max_conf is not None:
        filters.append(Signal.confidence <= max_conf)
    if outcome == "win":
        filters.append(Signal.outcome_pct > 0)
    elif outcome == "loss":
        filters.append(Signal.outcome_pct <= 0)
    elif outcome == "open":
        filters.append(Signal.outcome_pct.is_(None))

    stmt = select(Signal).order_by(desc(Signal.created_at)).limit(500)
    for f in filters:
        stmt = stmt.where(f)
    rows = (await db.execute(stmt)).scalars().all()
    return [_to_dict(r) for r in rows]


@router.post("/{signal_id}/send")
async def send_signal(
    signal_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sig = (await db.execute(select(Signal).where(Signal.id == signal_id))).scalar_one_or_none()
    if not sig:
        raise HTTPException(404, "Signal not found")
    if sig.action not in ("BUY", "SELL"):
        raise HTTPException(400, "Only BUY and SELL signals can be sent via Telegram.")

    # Determine the target chat_id for this user
    chat_id = user.telegram_chat_id

    # Owner fallback: if owner has no personal Telegram linked, use the
    # server-level TELEGRAM_CHAT_ID from .env
    if not chat_id and user.is_owner:
        chat_id = get_settings().telegram_chat_id

    if not chat_id:
        raise HTTPException(
            400,
            "Telegram not linked. Go to Account Settings → Telegram Alerts and "
            "follow the instructions to connect your account."
        )

    s = get_settings()
    if not s.telegram_bot_token:
        raise HTTPException(503, "Telegram bot not configured on the server.")

    sig_dict = _to_dict(sig)

    from services.telegram_svc import send_telegram_message
    success, _raw_detail = await send_telegram_message(chat_id, format_signal(sig_dict))
    detail = "" if success else _raw_detail

    _ET = pytz.timezone("America/New_York")
    now    = _utcnow_naive()
    now_et = datetime.now(_ET)
    emoji  = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(sig.action, "⚪")
    status = "sent" if success else "fail"
    log_msg = f"{'✓' if success else '✗'} {emoji} {sig.action} {sig.ticker} @ {sig.price:.2f} (Conf {sig.confidence:.0f}%) → user={user.id}"

    if success:
        sig.is_sent = True
        sig.sent_at = now

    db.add(SendLog(time=now_et.strftime("%H:%M:%S"), status=status, message=log_msg))
    await db.commit()
    return {"success": success, "detail": detail}


@router.post("/{signal_id}/skip")
async def skip_signal(signal_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    if not _user.is_owner:
        raise HTTPException(403, "Owner access required.")
    sig = (await db.execute(select(Signal).where(Signal.id == signal_id))).scalar_one_or_none()
    if not sig:
        raise HTTPException(404, "Signal not found")
    sig.is_skipped = True
    await db.commit()
    return {"success": True}


@router.post("/{signal_id}/review")
async def review_signal(signal_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    if not _user.is_owner:
        raise HTTPException(403, "Owner access required.")
    sig = (await db.execute(select(Signal).where(Signal.id == signal_id))).scalar_one_or_none()
    if not sig:
        raise HTTPException(404, "Signal not found")
    sig.reviewed = True   # mark reviewed — keeps signal in feed, just flags it
    await db.commit()
    return {"success": True, "reviewed": True}


def _best_outcome(r: Signal):
    """Return best available outcome: prefer 7d, then 3d, then 1d, then 14d."""
    return (r.outcome_pct if r.outcome_pct is not None
            else r.outcome_3d if r.outcome_3d is not None
            else r.outcome_1d if r.outcome_1d is not None
            else r.outcome_14d)

def _outcome_horizon(r: Signal) -> str:
    if r.outcome_pct  is not None: return "7d"
    if r.outcome_3d   is not None: return "3d"
    if r.outcome_1d   is not None: return "1d"
    if r.outcome_14d  is not None: return "14d"
    return "?"


@router.get("/backtest")
async def backtest_stats(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
    start_date: Optional[str] = Query(None),
    end_date:   Optional[str] = Query(None),
):
    """Win-rate and return statistics broken down by signal type, source, style, and confidence."""
    _ck = f"backtest:{start_date}:{end_date}"
    _cached = _cache_get(_ck)
    if _cached is not None:
        return _cached

    # ── Check pre-computed summary from scanner post-scan hook ────────────────
    # For unfiltered requests (no date range), the scanner already pre-computed
    # a lightweight summary that can serve as an instant response while the
    # full query runs asynchronously in the background.
    if not start_date and not end_date:
        try:
            from services.redis_cache import cache_get as _rget
            _precomputed = await _rget("analytics:backtest_summary")
            if _precomputed:
                _precomputed["_source"] = "pre-computed"
                _cache_set(_ck, _precomputed)
                return _precomputed
        except Exception:
            pass
    date_filters = []
    if start_date:
        try:
            date_filters.append(Signal.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
        except ValueError:
            pass
    if end_date:
        try:
            date_filters.append(Signal.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        except ValueError:
            pass
    rows = (await db.execute(
        select(Signal).where(
            Signal.is_sent == True,
            or_(
                Signal.outcome_1d.isnot(None),
                Signal.outcome_3d.isnot(None),
                Signal.outcome_pct.isnot(None),
                Signal.outcome_14d.isnot(None),
            ),
            *date_filters
        ).order_by(desc(Signal.created_at))
    )).scalars().all()

    if not rows:
        return {
            "total": 0, "resolved": 0, "win_rate": None, "avg_return": None,
            "by_action": [], "by_source": [], "by_style": [], "by_confidence": [],
            "top_signals": [], "worst_signals": [], "primary_horizon": None,
        }

    def stats(items):
        if not items:
            return {"count": 0, "wins": 0, "losses": 0, "win_rate": None, "avg_return": None, "avg_win": None, "avg_loss": None}
        wins   = [r for r in items if r > 0]
        losses = [r for r in items if r <= 0]
        return {
            "count":      len(items),
            "wins":       len(wins),
            "losses":     len(losses),
            "win_rate":   round(len(wins) / len(items) * 100, 1),
            "avg_return": round(sum(items) / len(items), 2),
            "avg_win":    round(sum(wins)   / len(wins),   2) if wins   else None,
            "avg_loss":   round(sum(losses) / len(losses), 2) if losses else None,
        }

    all_returns = [_best_outcome(r) for r in rows if _best_outcome(r) is not None]
    overall = stats(all_returns)

    # Determine predominant horizon for the UI label
    horizon_counts: dict[str, int] = defaultdict(int)
    for r in rows:
        horizon_counts[_outcome_horizon(r)] += 1
    primary_horizon = max(horizon_counts, key=lambda k: horizon_counts[k]) if horizon_counts else "7d"

    # ── by action ────────────────────────────────────────────────────────────
    action_buckets: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        v = _best_outcome(r)
        if v is not None:
            action_buckets[r.action].append(v)
    by_action = [{"action": k, **stats(v)} for k, v in sorted(action_buckets.items())]

    # ── by source (expand JSON array) ────────────────────────────────────────
    source_buckets: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        v = _best_outcome(r)
        if v is not None:
            for src in (r.sources or []):
                source_buckets[str(src)].append(v)
    by_source = sorted(
        [{"source": k, **stats(v)} for k, v in source_buckets.items()],
        key=lambda x: -(x["win_rate"] or 0),
    )

    # ── by style ─────────────────────────────────────────────────────────────
    style_buckets: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        v = _best_outcome(r)
        if v is not None:
            style_buckets[r.style or "swing"].append(v)
    by_style = [{"style": k, **stats(v)} for k, v in sorted(style_buckets.items())]

    # ── by confidence tier ───────────────────────────────────────────────────
    tiers = [("<50%", lambda c: c < 50), ("50–65%", lambda c: 50 <= c < 65),
             ("65–80%", lambda c: 65 <= c < 80), ("80%+", lambda c: c >= 80)]
    by_confidence = []
    for label, pred in tiers:
        bucket = [_best_outcome(r) for r in rows if pred(r.confidence) and _best_outcome(r) is not None]
        by_confidence.append({"tier": label, **stats(bucket)})

    # ── risk-adjusted metrics ─────────────────────────────────────────────────
    def risk_metrics(returns: list[float]) -> dict:
        if len(returns) < 3:
            return {"sharpe": None, "max_drawdown": None, "calmar": None}
        n = len(returns)
        mean_r = sum(returns) / n
        variance = sum((r - mean_r) ** 2 for r in returns) / (n - 1)
        std_r = math.sqrt(variance) if variance > 0 else 0
        # ~52 signal cycles per year (7-day hold periods)
        sharpe = round((mean_r / std_r) * math.sqrt(52), 2) if std_r > 0 else None

        # Max drawdown assuming 5% position sizing per trade
        capital, peak, max_dd = 10_000.0, 10_000.0, 0.0
        for r in returns:
            capital += capital * 0.05 * (r / 100)
            peak = max(peak, capital)
            max_dd = max(max_dd, (peak - capital) / peak * 100)
        max_dd = round(max_dd, 2)

        ann_return = round(mean_r * 52, 2)  # rough annualisation
        calmar = round((ann_return * 0.05) / max_dd, 2) if max_dd > 0 else None

        return {"sharpe": sharpe, "max_drawdown": round(-max_dd, 2), "calmar": calmar,
                "ann_return": ann_return}

    risk = risk_metrics(all_returns)

    # ── top & worst resolved signals ─────────────────────────────────────────
    scored_rows = [(r, _best_outcome(r)) for r in rows if _best_outcome(r) is not None]
    sorted_rows = sorted(scored_rows, key=lambda x: x[1], reverse=True)
    def _brief(r, v):
        return {
            "id": r.id, "ticker": r.ticker, "action": r.action,
            "confidence": r.confidence, "outcome_pct": round(v, 2),
            "sources": r.sources or [],
            "horizon": _outcome_horizon(r),
            "date": (r.outcome_at or r.created_at).strftime("%Y-%m-%d") if (r.outcome_at or r.created_at) else None,
        }
    top_signals    = [_brief(r, v) for r, v in sorted_rows[:5]]
    worst_signals  = [_brief(r, v) for r, v in sorted_rows[-5:] if v < 0]

    _result = {
        "total":            len(rows),
        "resolved":         len(rows),
        "primary_horizon":  primary_horizon,
        "win_rate":         overall["win_rate"],
        "avg_return":       overall["avg_return"],
        "avg_win":          overall["avg_win"],
        "avg_loss":         overall["avg_loss"],
        "sharpe":           risk["sharpe"],
        "max_drawdown":     risk["max_drawdown"],
        "calmar":           risk["calmar"],
        "ann_return":       risk["ann_return"],
        "by_action":        by_action,
        "by_source":        by_source,
        "by_style":         by_style,
        "by_confidence":    by_confidence,
        "top_signals":      top_signals,
        "worst_signals":    worst_signals,
    }
    _cache_set(_ck, _result)
    return _result


@router.get("/backtest/oos")
async def backtest_oos(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """
    Walk-forward out-of-sample validation.

    Splits resolved signals chronologically into 60/40 train/test.
    For each 30-day test window, computes win rate and Sharpe.
    Returns: windows list + overall OOS stats.
    """
    _ck = "backtest:oos"
    _cached = _cache_get(_ck)
    if _cached is not None:
        return _cached

    # 10-minute TTL for OOS — override module-level TTL locally
    _OOS_TTL = 600
    entry = _analytics_cache.get(_ck)
    if entry and _time.time() - entry["ts"] < _OOS_TTL:
        return entry["data"]

    rows = (await db.execute(
        select(Signal).where(
            Signal.outcome_pct.isnot(None),
            Signal.action.in_(["BUY", "SELL"]),
        ).order_by(Signal.created_at)
    )).scalars().all()

    if not rows:
        return {
            "oos_win_rate": None,
            "oos_avg_return": None,
            "oos_sharpe": None,
            "n_train": 0,
            "n_oos": 0,
            "windows": [],
        }

    # 60/40 chronological split
    split_idx = int(len(rows) * 0.6)
    oos_rows = rows[split_idx:]
    n_train = split_idx
    n_oos = len(oos_rows)

    def _is_win(sig: Signal) -> bool:
        """Win = positive outcome (database already flips SELL outcomes)."""
        return (sig.outcome_pct or 0) > 0

    def _window_stats(sigs) -> dict:
        if not sigs:
            return {"n": 0, "win_rate": None, "avg_return": None}
        rets = [s.outcome_pct for s in sigs]
        wins = [s for s in sigs if _is_win(s)]
        mean_r = sum(rets) / len(rets)
        return {
            "n":          len(sigs),
            "win_rate":   round(len(wins) / len(sigs) * 100, 1),
            "avg_return": round(mean_r, 2),
        }

    # Overall OOS stats
    oos_returns = [s.outcome_pct for s in oos_rows]
    oos_wins = [s for s in oos_rows if _is_win(s)]
    oos_mean = sum(oos_returns) / n_oos if n_oos else 0.0
    oos_variance = (
        sum((r - oos_mean) ** 2 for r in oos_returns) / (n_oos - 1)
        if n_oos > 1 else 0.0
    )
    oos_std = math.sqrt(oos_variance)
    oos_sharpe = round((oos_mean / oos_std) * math.sqrt(52), 2) if oos_std > 0 else 0.0

    # 30-day rolling windows (up to 6)
    windows = []
    if oos_rows:
        window_start = oos_rows[0].created_at
        window_end_limit = oos_rows[-1].created_at
        max_windows = 6
        window_days = timedelta(days=30)

        current_start = window_start
        while current_start <= window_end_limit and len(windows) < max_windows:
            current_end = current_start + window_days
            bucket = [s for s in oos_rows if current_start <= s.created_at < current_end]
            stats = _window_stats(bucket)
            windows.append({
                "start": current_start.strftime("%Y-%m-%d"),
                "end":   current_end.strftime("%Y-%m-%d"),
                **stats,
            })
            current_start = current_end

    _result = {
        "oos_win_rate":   round(len(oos_wins) / n_oos * 100, 1) if n_oos else None,
        "oos_avg_return": round(oos_mean, 2) if n_oos else None,
        "oos_sharpe":     oos_sharpe if n_oos else None,
        "n_train":        n_train,
        "n_oos":          n_oos,
        "windows":        windows,
    }
    _analytics_cache[_ck] = {"data": _result, "ts": _time.time()}
    return _result


@router.get("/{ticker}/spark")
async def get_sparkline(ticker: str, _user: User = Depends(get_current_user)):
    """Return last 30 daily closes for a mini sparkline chart."""
    from services.market_data import get_history
    # Sanitise ticker: only allow alphanumeric + hyphen/dot (valid ticker characters)
    import re as _re
    if not _re.match(r'^[A-Za-z0-9.\-]{1,10}$', ticker):
        raise HTTPException(400, "Invalid ticker symbol.")
    df = await get_history(ticker.upper(), period="1mo", interval="1d")
    if df is None or df.empty:
        return {"ticker": ticker.upper(), "prices": []}
    prices = [round(float(p), 2) for p in df["Close"].tolist()[-30:]]
    return {"ticker": ticker.upper(), "prices": prices}


@router.post("/scan")
async def manual_scan(_user: User = Depends(get_current_user)):
    if not _user.is_owner:
        raise HTTPException(403, "Owner access required.")
    from services.scanner import run_scan
    from routers.websocket_router import manager
    import asyncio
    asyncio.create_task(run_scan(broadcast_fn=manager.broadcast))
    return {"success": True, "message": "Scan triggered"}


@router.get("/{ticker}/confidence-history")
async def confidence_history(ticker: str, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    """Return the confidence trend for a ticker over its last 30 scans."""
    import re as _re
    if not _re.match(r'^[A-Za-z0-9.\-]{1,10}$', ticker):
        raise HTTPException(400, "Invalid ticker symbol.")
    rows = (await db.execute(
        select(Signal.confidence, Signal.action, Signal.created_at)
        .where(Signal.ticker == ticker.upper())
        .order_by(Signal.created_at)
        .limit(30)
    )).all()
    return [
        {
            "ts":         r.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if r.created_at else "",
            "confidence": r.confidence,
            "action":     r.action,
        }
        for r in rows
    ]


from pydantic import BaseModel as _BaseModel, ConfigDict as _ConfigDict

class _NotesIn(_BaseModel):
    model_config = _ConfigDict(str_max_length=2000)

    notes: str = ""

    @classmethod
    def __get_validators__(cls):
        yield cls


@router.patch("/{signal_id}/notes")
async def update_notes(signal_id: int, body: _NotesIn, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    sig = (await db.execute(select(Signal).where(Signal.id == signal_id))).scalar_one_or_none()
    if not sig:
        raise HTTPException(404, "Signal not found")
    notes = (body.notes or "")[:2000]  # enforce max length server-side
    sig.notes = notes
    await db.commit()
    return {"ok": True}


@router.get("/track-record")
async def track_record(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD inclusive start"),
    end_date:   Optional[str] = Query(None, description="YYYY-MM-DD inclusive end"),
):
    """Per-ticker win rate, avg return, Sharpe — optionally filtered by date range."""
    filters = [Signal.outcome_pct.isnot(None), Signal.is_sent == True]
    if start_date:
        try:
            filters.append(Signal.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
        except ValueError:
            pass
    if end_date:
        try:
            # Include entire end day
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            filters.append(Signal.created_at <= end_dt)
        except ValueError:
            pass

    rows = (await db.execute(
        select(Signal).where(*filters).order_by(desc(Signal.outcome_at))
    )).scalars().all()

    if not rows:
        return []

    buckets: dict = defaultdict(list)
    for r in rows:
        buckets[r.ticker].append(r)

    result = []
    for ticker, signals in buckets.items():
        returns = [s.outcome_pct for s in signals]
        wins    = [r for r in returns if r > 0]
        losses  = [r for r in returns if r <= 0]
        n       = len(returns)
        mean_r  = sum(returns) / n
        std_r   = math.sqrt(sum((r - mean_r) ** 2 for r in returns) / max(n - 1, 1)) if n > 1 else 0
        sharpe  = round((mean_r / std_r) * math.sqrt(52), 2) if std_r > 0 and n >= 3 else None
        best    = max(signals, key=lambda s: s.outcome_pct)
        worst   = min(signals, key=lambda s: s.outcome_pct)
        result.append({
            "ticker":     ticker,
            "company":    signals[0].company or ticker,
            "signals":    n,
            "wins":       len(wins),
            "losses":     len(losses),
            "win_rate":   round(len(wins) / n * 100, 1),
            "avg_return": round(mean_r, 2),
            "avg_win":    round(sum(wins) / len(wins), 2) if wins else None,
            "avg_loss":   round(sum(losses) / len(losses), 2) if losses else None,
            "sharpe":     sharpe,
            "best":       round(best.outcome_pct, 2),
            "worst":      round(worst.outcome_pct, 2),
            "last_date":  best.outcome_at.strftime("%Y-%m-%d") if best.outcome_at else None,
        })

    result.sort(key=lambda x: -(x["avg_return"]))
    return result


@router.get("/backtest/simulate")
async def backtest_simulate(
    slippage_pct: float = 0.15,
    commission_per_share: float = 0.0,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """
    Replay historical sent signals with realistic execution:
    - Entry at next-day open ± slippage
    - Exit when stop or target hit on daily High/Low, or 7 trading days elapsed
    - Commission applied both sides
    Returns gross vs net comparison plus per-signal audit trail.
    """
    from services.market_data import get_history
    import asyncio

    rows = (await db.execute(
        select(Signal)
        .where(Signal.is_sent == True)
        .where(Signal.entry.isnot(None))
        .where(Signal.stop.isnot(None))
        .where(Signal.target.isnot(None))
        .where(Signal.created_at.isnot(None))
        .order_by(desc(Signal.created_at))
        .limit(200)
    )).scalars().all()

    if not rows:
        return {"simulated": 0, "signals": []}

    slip = slippage_pct / 100

    async def simulate_one(sig: Signal) -> dict:
        try:
            df = await get_history(sig.ticker, period="2mo", interval="1d")
            if df is None or df.empty:
                return None
            # Find the trading day after signal was created
            sig_date = sig.created_at.date()
            future = df[df.index.date > sig_date].head(12)  # up to 12 trading days
            if future.empty:
                return None

            # Simulate entry at next-day open + slippage
            first_row   = future.iloc[0]
            raw_entry   = float(first_row["Open"])
            is_buy      = sig.action == "BUY"
            actual_entry = raw_entry * (1 + slip) if is_buy else raw_entry * (1 - slip)

            # Recalculate stop/target relative to actual entry
            orig_risk   = abs(sig.entry - sig.stop)
            orig_reward = abs(sig.target - sig.entry)
            if is_buy:
                act_stop   = actual_entry - orig_risk
                act_target = actual_entry + orig_reward
            else:
                act_stop   = actual_entry + orig_risk
                act_target = actual_entry - orig_reward

            # Simulate day-by-day: exit when stop/target hit
            exit_price, exit_day, exit_reason = None, None, None
            for i, (idx, row) in enumerate(future.iloc[1:].iterrows(), start=1):
                day_high = float(row["High"])
                day_low  = float(row["Low"])
                if is_buy:
                    if day_low <= act_stop:
                        exit_price  = act_stop
                        exit_day    = i
                        exit_reason = "stop"
                        break
                    if day_high >= act_target:
                        exit_price  = act_target
                        exit_day    = i
                        exit_reason = "target"
                        break
                else:
                    if day_high >= act_stop:
                        exit_price  = act_stop
                        exit_day    = i
                        exit_reason = "stop"
                        break
                    if day_low <= act_target:
                        exit_price  = act_target
                        exit_day    = i
                        exit_reason = "target"
                        break

            if exit_price is None:
                # Time-based exit at close on day 7
                exit_row    = future.iloc[min(6, len(future) - 1)]
                exit_price  = float(exit_row["Close"])
                exit_day    = min(7, len(future))
                exit_reason = "timeout"

            # Apply exit slippage
            exit_price = exit_price * (1 - slip) if is_buy else exit_price * (1 + slip)

            # Commission (both sides)
            notional    = 1000.0  # standard notional
            shares      = notional / actual_entry if actual_entry > 0 else 1
            comm_total  = commission_per_share * shares * 2

            gross_pct = (exit_price - actual_entry) / actual_entry * 100 * (1 if is_buy else -1)
            comm_pct  = comm_total / notional * 100
            net_pct   = gross_pct - comm_pct

            return {
                "id":           sig.id,
                "ticker":       sig.ticker,
                "action":       sig.action,
                "confidence":   sig.confidence,
                "date":         sig_date.isoformat(),
                "raw_entry":    round(raw_entry, 2),
                "actual_entry": round(actual_entry, 2),
                "exit_price":   round(exit_price, 2),
                "exit_day":     exit_day,
                "exit_reason":  exit_reason,
                "slippage_pct": round(slip * 200, 3),    # both sides
                "commission_pct": round(comm_pct, 3),
                "gross_pct":    round(gross_pct, 2),
                "net_pct":      round(net_pct, 2),
                "raw_outcome":  sig.outcome_pct,
            }
        except Exception:
            return None

    results = await asyncio.gather(*[simulate_one(r) for r in rows])
    signals  = [r for r in results if r is not None]

    if not signals:
        return {"simulated": 0, "signals": []}

    gross_returns = [s["gross_pct"] for s in signals]
    net_returns   = [s["net_pct"]   for s in signals]

    def agg(returns):
        if not returns: return {}
        wins   = [r for r in returns if r > 0]
        losses = [r for r in returns if r <= 0]
        return {
            "count":      len(returns),
            "win_rate":   round(len(wins) / len(returns) * 100, 1),
            "avg_return": round(sum(returns) / len(returns), 2),
            "avg_win":    round(sum(wins)   / len(wins),   2) if wins   else None,
            "avg_loss":   round(sum(losses) / len(losses), 2) if losses else None,
        }

    return {
        "simulated":          len(signals),
        "slippage_pct":       slippage_pct,
        "commission_per_share": commission_per_share,
        "gross":              agg(gross_returns),
        "net":                agg(net_returns),
        "cost_drag_avg":      round(sum(s["gross_pct"] - s["net_pct"] for s in signals) / len(signals), 3),
        "stop_hit_rate":      round(sum(1 for s in signals if s["exit_reason"] == "stop") / len(signals) * 100, 1),
        "target_hit_rate":    round(sum(1 for s in signals if s["exit_reason"] == "target") / len(signals) * 100, 1),
        "timeout_rate":       round(sum(1 for s in signals if s["exit_reason"] == "timeout") / len(signals) * 100, 1),
        "signals":            sorted(signals, key=lambda s: s["net_pct"], reverse=True),
    }


@router.get("/predictive")
async def predictive_confidence(
    action:     str   = "BUY",
    confidence: float = 65.0,
    sources:    str   = "",        # comma-separated source list
    style:      str   = "swing",
    db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user),
):
    """
    Predictive confidence intervals for a new signal.

    Finds historically resolved signals that are similar to the incoming one
    (same action, nearby confidence, overlapping sources) and computes:
      - P(success) at 1d, 3d, 7d horizons with Bayesian smoothing
      - Expected return + 10th/25th/75th/90th percentile bands
      - Calibrated "confidence score" weighting recency and N

    Similarity scoring (0–10):
      • Confidence within ±5  → +4 pts
      • Confidence within ±15 → +2 pts
      • Source overlap ≥ 2    → +3 pts
      • Source overlap ≥ 1    → +1 pt
      • Same style            → +1 pt
    Top 30 similar signals used (min 3 required to report).
    Laplace smoothing α scales with 1/N to avoid overconfidence on small samples.
    """
    req_sources = {s.strip() for s in sources.split(",") if s.strip()}

    # Fetch all sent resolved signals for this action
    rows = (await db.execute(
        select(Signal)
        .where(Signal.action     == action.upper())
        .where(Signal.is_sent   == True)
        .where(Signal.outcome_1d.isnot(None))   # at least 1d must be resolved
        .order_by(desc(Signal.created_at))
        .limit(500)
    )).scalars().all()

    if not rows:
        return {"action": action, "n_similar": 0, "horizons": [],
                "message": "No historical data yet — outcomes accumulate after signals age 1+ day."}

    # ── Similarity scoring ───────────────────────────────────────────────────
    def similarity(sig: Signal) -> float:
        score = 0.0
        conf_diff = abs(sig.confidence - confidence)
        if conf_diff <= 5:   score += 4
        elif conf_diff <= 15: score += 2
        elif conf_diff <= 25: score += 1
        sig_sources = set(sig.sources or [])
        overlap = len(req_sources & sig_sources)
        if overlap >= 2:  score += 3
        elif overlap >= 1: score += 1
        if sig.style == style: score += 1
        return score

    scored = sorted(rows, key=lambda s: -similarity(s))
    # Use top 30, but must have similarity > 0
    pool = [s for s in scored[:30] if similarity(s) > 0]
    if len(pool) < 3:
        # Fall back to all same-action signals
        pool = scored[:30]

    n = len(pool)

    # ── Per-horizon statistics with Laplace smoothing ────────────────────────
    def horizon_stats(values: list[float], label: str) -> dict:
        if not values:
            return None
        k = len(values)
        wins = [v for v in values if v > 0]
        losses = [v for v in values if v <= 0]

        # Bayesian smoothing: α = max(1, 5/k) → weak prior when k ≥ 5
        alpha = max(1.0, 5.0 / k)
        p_success = (len(wins) + alpha) / (k + 2 * alpha)

        mean_r = sum(values) / k
        sorted_v = sorted(values)

        def pct(p):
            idx = (k - 1) * p
            lo, hi = int(idx), min(int(idx) + 1, k - 1)
            return sorted_v[lo] + (sorted_v[hi] - sorted_v[lo]) * (idx - lo)

        ci_10 = pct(0.10) if k >= 5  else None
        ci_25 = pct(0.25) if k >= 5  else None
        ci_75 = pct(0.75) if k >= 5  else None
        ci_90 = pct(0.90) if k >= 5  else None

        # Calibrated confidence in the prediction (0–1): based on sample size
        calibration = min(1.0, k / 20)

        return {
            "horizon":       label,
            "n":             k,
            "p_success":     round(p_success, 3),
            "expected":      round(mean_r, 2),
            "ci_10":         round(ci_10, 2) if ci_10 is not None else None,
            "ci_25":         round(ci_25, 2) if ci_25 is not None else None,
            "ci_75":         round(ci_75, 2) if ci_75 is not None else None,
            "ci_90":         round(ci_90, 2) if ci_90 is not None else None,
            "avg_win":       round(sum(wins)   / len(wins),   2) if wins   else None,
            "avg_loss":      round(sum(losses) / len(losses), 2) if losses else None,
            "calibration":   round(calibration, 2),
        }

    h1  = horizon_stats([s.outcome_1d  for s in pool if s.outcome_1d  is not None], "1d")
    h3  = horizon_stats([s.outcome_3d  for s in pool if s.outcome_3d  is not None], "3d")
    h7  = horizon_stats([s.outcome_pct for s in pool if s.outcome_pct is not None], "7d")
    h14 = horizon_stats([s.outcome_14d for s in pool if s.outcome_14d is not None], "14d")

    horizons = [h for h in [h1, h3, h7, h14] if h is not None]

    # ── Overall "Probability of Success" composite score ─────────────────────
    # Weighted average of available horizons (7d = most weight when available)
    weights = {"1d": 0.2, "3d": 0.35, "7d": 0.35, "14d": 0.10}
    total_w, weighted_p = 0.0, 0.0
    for h in horizons:
        w = weights.get(h["horizon"], 0.1) * h["calibration"]
        weighted_p  += h["p_success"] * w
        total_w     += w
    composite = round(weighted_p / total_w, 3) if total_w > 0 else None

    # ── Insights ─────────────────────────────────────────────────────────────
    insights = []
    resolved_pool = [s for s in pool if s.outcome_pct is not None]

    # 1. Source-combination win rate
    if req_sources and resolved_pool:
        src_wins  = sum(1 for s in resolved_pool if s.outcome_pct > 0)
        src_wr    = round(src_wins / len(resolved_pool) * 100, 1)
        top_srcs  = ", ".join(sorted(req_sources)[:3])
        icon = "bullish" if src_wr >= 60 else "bearish" if src_wr < 45 else "neutral"
        insights.append({
            "type": "source_win_rate", "icon": icon,
            "head": f"{src_wr:.0f}% win rate on matching source combination",
            "body": f"{src_wins} of {len(resolved_pool)} similar {action} signals with {top_srcs} resolved profitably.",
        })

    # 2. Win/loss magnitude (payoff asymmetry)
    h7_data = next((h for h in horizons if h["horizon"] == "7d"), None) or \
              next((h for h in horizons if h["horizon"] == "3d"), None)
    if h7_data and h7_data.get("avg_win") and h7_data.get("avg_loss"):
        avg_win  = h7_data["avg_win"]
        avg_loss = h7_data["avg_loss"]
        ratio    = round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else None
        if ratio:
            icon = "bullish" if ratio >= 1.5 else "bearish" if ratio < 0.8 else "neutral"
            insights.append({
                "type": "payoff_ratio", "icon": icon,
                "head": f"Payoff ratio {ratio:.1f}× (wins {avg_win:+.1f}% vs losses {avg_loss:.1f}%)",
                "body": (
                    f"When similar {action} signals succeed they return +{avg_win:.1f}% on average; "
                    f"when they fail the average loss is {avg_loss:.1f}%. "
                    + ("Asymmetry favours taking this trade." if ratio >= 1.5
                       else "Risk/reward is roughly balanced." if ratio >= 0.9
                       else "Losers outpace winners on average — size position conservatively.")
                ),
            })

    # 3. Best and worst comparable trades
    if resolved_pool:
        best  = max(resolved_pool, key=lambda s: s.outcome_pct)
        worst = min(resolved_pool, key=lambda s: s.outcome_pct)
        best_date  = best.created_at.strftime("%b %d")  if best.created_at  else "?"
        worst_date = worst.created_at.strftime("%b %d") if worst.created_at else "?"
        
        best_path = []
        try:
            from services.market_data import get_history
            df = await get_history(best.ticker, period="3mo", interval="1d")
            if df is not None and not df.empty and best.created_at:
                future = df[df.index.date >= best.created_at.date()].head(15)
                if not future.empty:
                    base_price = float(future.iloc[0]["Close"])
                    best_path = [round((float(row["Close"]) - base_price) / base_price * 100, 2) for _, row in future.iterrows()]
        except Exception:
            pass

        insights.append({
            "type": "best_comparable", "icon": "bullish",
            "head": f"Best comparable: {best.ticker} {best.action} {best.outcome_pct:+.1f}% ({best_date})",
            "body": f"Most similar historical signal: {best.ticker} {best.action} at {best.confidence:.0f}% confidence — "
                    f"returned {best.outcome_pct:+.1f}% at 7-day mark. Sources: {', '.join(best.sources or [])[:80]}.",
            "path": best_path
        })
        if worst.outcome_pct < -2:
            insights.append({
                "type": "worst_comparable", "icon": "bearish",
                "head": f"Worst comparable: {worst.ticker} {worst.action} {worst.outcome_pct:+.1f}% ({worst_date})",
                "body": f"The worst similar signal lost {worst.outcome_pct:.1f}% — "
                        f"illustrates maximum downside when the setup fails.",
            })

    # 4. Confidence-tier calibration
    tier_sigs     = [s for s in rows if abs((s.confidence or 0) - confidence) <= 7 and s.outcome_pct is not None]
    if tier_sigs:
        tier_wr   = round(sum(1 for s in tier_sigs if s.outcome_pct > 0) / len(tier_sigs) * 100, 1)
        tier_icon = "bullish" if tier_wr >= 60 else "bearish" if tier_wr < 45 else "neutral"
        insights.append({
            "type": "tier_calibration", "icon": tier_icon,
            "head": f"Confidence tier {int(confidence-7)}-{int(confidence+7)}%: {tier_wr:.0f}% historical win rate",
            "body": f"Across all {len(tier_sigs)} resolved signals in this confidence range, "
                    f"{tier_wr:.0f}% were profitable. "
                    + ("This tier has been reliable." if tier_wr >= 60
                       else "This tier has been mixed — consider reducing position size." if tier_wr < 50
                       else "This tier performs roughly as expected."),
        })

    # 5. Recency trend (last 5 vs prior 5 similar signals)
    if len(resolved_pool) >= 10:
        recent_wr = sum(1 for s in resolved_pool[:5]  if s.outcome_pct > 0) / 5
        older_wr  = sum(1 for s in resolved_pool[5:10] if s.outcome_pct > 0) / 5
        delta     = round((recent_wr - older_wr) * 100, 0)
        if abs(delta) >= 20:
            icon = "bullish" if delta > 0 else "bearish"
            trend_word = "improving" if delta > 0 else "deteriorating"
            insights.append({
                "type": "recency_trend", "icon": icon,
                "head": f"Recent accuracy {trend_word} ({'+' if delta>0 else ''}{delta:.0f}pp vs older signals)",
                "body": f"The 5 most recent similar signals had a {recent_wr*100:.0f}% win rate vs "
                        f"{older_wr*100:.0f}% for the prior 5. "
                        + ("Momentum is building — signal quality may be rising." if delta > 0
                           else "Recent conditions have been less favourable for this setup."),
            })

    # 6. Sample size warning
    if n < 5:
        insights.append({
            "type": "low_data", "icon": "neutral",
            "head": f"Limited sample: {n} similar signals",
            "body": "Probability estimates are rough with fewer than 5 comparables. "
                    "Accuracy improves as more signals accumulate and resolve over time.",
        })

    # ── Plain-English summary ─────────────────────────────────────────────────
    if composite is not None:
        pct = round(composite * 100)
        if pct >= 70:
            summary = f"Historical data is encouraging: {pct}% of similar signals succeeded."
        elif pct >= 55:
            summary = f"Moderate historical support: {pct}% of similar signals succeeded — proceed with normal sizing."
        elif pct >= 45:
            summary = f"Mixed historical record: {pct}% success rate on similar signals. Consider reducing size."
        else:
            summary = f"Caution: only {pct}% of similar signals succeeded historically. High uncertainty."
    else:
        summary = "Not enough resolved signals yet to compute a reliable probability."

    # Most similar signal for attribution
    similar_desc = None
    if pool:
        rep = pool[0]
        similar_desc = f"{rep.ticker} {rep.action} {rep.confidence:.0f}% ({rep.created_at.strftime('%b %d') if rep.created_at else '?'})"

    return {
        "action":           action,
        "confidence_input": confidence,
        "n_similar":        n,
        "composite_p":      composite,
        "horizons":         horizons,
        "insights":         insights,
        "summary":          summary,
        "similar_example":  similar_desc,
        "message": (
            f"Based on {n} similar {action} signals" if n >= 5
            else f"Limited data ({n} signals) — predictions will improve as outcomes accumulate"
        ),
    }


@router.get("/backtest/horizons")
async def backtest_horizons(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
    start_date: Optional[str] = Query(None),
    end_date:   Optional[str] = Query(None),
):
    """Win rate, avg return and Sharpe at 1d, 3d, 7d, 14d horizons."""
    date_filters = []
    if start_date:
        try:
            date_filters.append(Signal.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
        except ValueError:
            pass
    if end_date:
        try:
            date_filters.append(Signal.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        except ValueError:
            pass
    rows = (await db.execute(
        select(Signal).where(Signal.is_sent == True, *date_filters)
    )).scalars().all()

    def horizon_agg(values, label):
        v = [x for x in values if x is not None]
        if not v:
            return {"horizon": label, "n": 0, "win_rate": None, "avg_return": None,
                    "avg_win": None, "avg_loss": None, "sharpe": None}
        wins   = [x for x in v if x > 0]
        losses = [x for x in v if x <= 0]
        n      = len(v)
        mean_r = sum(v) / n
        std_r  = math.sqrt(sum((x - mean_r)**2 for x in v) / max(n-1, 1)) if n > 1 else 0
        # Annualise: 1d → ×252, 3d → ×84, 7d → ×52, 14d → ×26
        factors = {"1d": 252, "3d": 84, "7d": 52, "14d": 26}
        sharpe  = round((mean_r / std_r) * math.sqrt(factors.get(label, 52)), 2) if std_r > 0 and n >= 5 else None
        return {
            "horizon":    label,
            "n":          n,
            "win_rate":   round(len(wins) / n * 100, 1),
            "avg_return": round(mean_r, 2),
            "avg_win":    round(sum(wins)   / len(wins),   2) if wins   else None,
            "avg_loss":   round(sum(losses) / len(losses), 2) if losses else None,
            "sharpe":     sharpe,
        }

    return [
        horizon_agg([r.outcome_1d  for r in rows], "1d"),
        horizon_agg([r.outcome_3d  for r in rows], "3d"),
        horizon_agg([r.outcome_pct for r in rows], "7d"),
        horizon_agg([r.outcome_14d for r in rows], "14d"),
    ]


@router.get("/correlation")
async def signal_correlation(db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    """
    Source co-occurrence matrix across all sent signals.
    Returns: how often each pair of sources appear together,
    plus the conditional win rate when each pair co-occurs.
    """
    _cached = _cache_get("correlation")
    if _cached is not None:
        return _cached
    rows = (await db.execute(
        select(Signal)
        .where(Signal.is_sent == True)
        .where(Signal.sources.isnot(None))
    )).scalars().all()

    if len(rows) < 5:
        return {"matrix": [], "sources": [], "n_signals": len(rows)}

    # Collect all sources
    all_sources: set = set()
    for r in rows:
        all_sources.update(r.sources or [])
    all_sources = sorted(all_sources)

    # Co-occurrence counts and joint win rates
    co_count: dict = {}
    co_wins:  dict = {}

    for r in rows:
        srcs = sorted(r.sources or [])
        won  = r.outcome_pct is not None and r.outcome_pct > 0
        for i in range(len(srcs)):
            for j in range(i + 1, len(srcs)):
                key = (srcs[i], srcs[j])
                co_count[key] = co_count.get(key, 0) + 1
                if won:
                    co_wins[key] = co_wins.get(key, 0) + 1

    # Build sorted list of pairs by co-occurrence
    pairs = []
    for (a, b), count in sorted(co_count.items(), key=lambda x: -x[1]):
        total_resolved = sum(1 for r in rows
            if a in (r.sources or []) and b in (r.sources or []) and r.outcome_pct is not None)
        win_rate = round(co_wins.get((a, b), 0) / total_resolved * 100, 1) if total_resolved >= 3 else None
        pairs.append({
            "a":          a, "b": b,
            "count":      count,
            "win_rate":   win_rate,
            "resolved":   total_resolved,
            "pct_of_signals": round(count / len(rows) * 100, 1),
        })

    # Single-source win rates
    source_stats = []
    for src in all_sources:
        src_rows     = [r for r in rows if src in (r.sources or [])]
        resolved     = [r for r in src_rows if r.outcome_pct is not None]
        wins         = [r for r in resolved if r.outcome_pct > 0]
        source_stats.append({
            "source":    src,
            "count":     len(src_rows),
            "win_rate":  round(len(wins)/len(resolved)*100, 1) if resolved else None,
        })
    source_stats.sort(key=lambda x: -(x["count"]))

    _corr_result = {
        "n_signals":    len(rows),
        "sources":      source_stats,
        "pairs":        pairs[:30],
    }
    _cache_set("correlation", _corr_result)
    return _corr_result


@router.post("/backtest/backfill")
async def backfill_outcomes(db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    if not _user.is_owner:
        raise HTTPException(403, "Owner access required.")
    """
    Retroactively compute 1d/3d/7d/14d outcomes from yfinance historical prices
    for all sent signals that are missing any outcome values.
    """
    import yfinance as yf
    import logging
    log = logging.getLogger(__name__)

    def _pct(current, entry, action):
        if not current or not entry or entry <= 0:
            return None
        raw = (current - entry) / entry * 100
        return round(raw if action == "BUY" else -raw, 2)

    # All sent signals with an entry price
    rows = (await db.execute(
        select(Signal).where(
            Signal.is_sent == True,
            Signal.entry.isnot(None),
            Signal.entry > 0,
            Signal.created_at.isnot(None),
        )
    )).scalars().all()

    to_fill = [
        s for s in rows
        if s.outcome_1d is None or s.outcome_3d is None
        or s.outcome_pct is None or s.outcome_14d is None
    ]

    if not to_fill:
        return {"updated": 0, "tickers": 0, "errors": [], "message": "All outcomes already resolved."}

    by_ticker: dict = defaultdict(list)
    for sig in to_fill:
        by_ticker[sig.ticker].append(sig)

    updated = 0
    errors = []
    now = _utcnow_naive()

    for ticker, sigs in by_ticker.items():
        try:
            min_dt = min(s.created_at for s in sigs)
            start  = (min_dt - timedelta(days=2)).strftime("%Y-%m-%d")
            # Don't request past today
            end_dt = min(now + timedelta(days=1), min_dt + timedelta(days=40))
            end    = end_dt.strftime("%Y-%m-%d")

            hist = yf.Ticker(ticker).history(start=start, end=end, interval="1d", auto_adjust=True)
            if hist.empty:
                errors.append(f"{ticker}: no history")
                continue

            # List of (date, close) in chronological order
            trading_days = []
            for idx_dt, row in hist.iterrows():
                d = idx_dt.date() if hasattr(idx_dt, "date") else idx_dt
                trading_days.append((d, float(row["Close"])))
            trading_days.sort(key=lambda x: x[0])

            for sig in sigs:
                sig_date = sig.created_at.date()

                # ── Point-in-Time guard 1: never use a future-dated signal ──────
                if sig_date > now.date():
                    errors.append(f"{ticker}: signal {sig.id} dated in the future ({sig_date}) — skipped")
                    continue

                # Find first trading day on or after signal date
                sig_idx = None
                for i, (d, _) in enumerate(trading_days):
                    if d >= sig_date:
                        sig_idx = i
                        break
                if sig_idx is None:
                    continue

                # ── Point-in-Time guard 2: entry price split-detection ───────────
                # If auto_adjust=True rescaled historical prices after a post-signal
                # stock split, the stored entry price will diverge significantly from
                # the adjusted close on the signal date, making outcome calculations
                # wrong (all % returns would be inflated/deflated by the split ratio).
                hist_close_at_signal = trading_days[sig_idx][1]
                if abs(sig.entry - hist_close_at_signal) / sig.entry > 0.25:
                    errors.append(
                        f"{ticker} sig#{sig.id} {sig_date}: entry ${sig.entry:.2f} vs "
                        f"adjusted history ${hist_close_at_signal:.2f} "
                        f"(Δ{abs(sig.entry - hist_close_at_signal)/sig.entry*100:.0f}%) — "
                        f"likely post-signal split; skipping to avoid look-ahead bias"
                    )
                    continue

                def close_at(offset):
                    idx = sig_idx + offset
                    return trading_days[idx][1] if idx < len(trading_days) else None

                changed = False
                if sig.outcome_1d is None:
                    p = close_at(1)
                    if p is not None:
                        sig.outcome_1d = _pct(p, sig.entry, sig.action)
                        changed = True
                if sig.outcome_3d is None:
                    p = close_at(3)
                    if p is not None:
                        sig.outcome_3d = _pct(p, sig.entry, sig.action)
                        changed = True
                if sig.outcome_pct is None:
                    p = close_at(7)
                    if p is not None:
                        sig.outcome_pct = _pct(p, sig.entry, sig.action)
                        sig.outcome_at  = now
                        changed = True
                if sig.outcome_14d is None:
                    p = close_at(14)
                    if p is not None:
                        sig.outcome_14d = _pct(p, sig.entry, sig.action)
                        changed = True

                if changed:
                    updated += 1

        except Exception as e:
            errors.append(f"{ticker}: {e}")
            log.warning(f"backfill {ticker}: {e}")

    await db.commit()
    return {
        "updated":  updated,
        "tickers":  len(by_ticker),
        "errors":   errors[:10],
        "message":  f"Backfilled outcomes for {updated} signals across {len(by_ticker)} tickers.",
    }


@router.get("/backtest/calibration")
async def calibration_curve(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
    start_date: Optional[str] = Query(None),
    end_date:   Optional[str] = Query(None),
):
    """
    Reliability / calibration diagram data.
    Returns confidence buckets vs actual win rate so the UI can plot
    'what we said' vs 'how often we were right'.
    """
    date_filters = []
    if start_date:
        try:
            date_filters.append(Signal.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
        except ValueError:
            pass
    if end_date:
        try:
            date_filters.append(Signal.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        except ValueError:
            pass

    stmt = (
        select(Signal.confidence, Signal.action, Signal.outcome_pct)
        .where(Signal.is_sent == True)
        .where(Signal.outcome_pct.isnot(None))
        .where(Signal.action.in_(["BUY", "SELL"]))
    )
    for f in date_filters:
        stmt = stmt.where(f)
    rows = (await db.execute(stmt)).all()

    # 5-point wide buckets from 40 → 100
    BUCKET_WIDTH = 5
    buckets: dict[int, list[bool]] = {}

    for conf, action, outcome in rows:
        if conf is None:
            continue
        lo = int(conf // BUCKET_WIDTH) * BUCKET_WIDTH
        lo = max(40, min(95, lo))
        win = (outcome > 0)
        buckets.setdefault(lo, []).append(win)

    result = []
    for lo in sorted(buckets):
        wins = buckets[lo]
        n = len(wins)
        if n == 0:
            continue
        actual_wr = round(sum(wins) / n * 100, 1)
        mid = lo + BUCKET_WIDTH / 2
        result.append({
            "bucket":      f"{lo}–{lo + BUCKET_WIDTH}%",
            "predicted":   round(mid, 1),
            "actual":      actual_wr,
            "count":       n,
            "gap":         round(mid - actual_wr, 1),
        })

    return result


@router.get("/factor-mining")
async def factor_mining_results(_user: User = Depends(get_current_user)):
    """Return the most recent factor mining run results (or trigger one if missing)."""
    from services.factor_miner import get_factor_mining_results
    return await get_factor_mining_results()


@router.post("/factor-mining/run")
async def trigger_factor_mining(_user: User = Depends(get_current_user)):
    """Manually trigger a factor mining run (owner only)."""
    if not _user.is_owner:
        raise HTTPException(403, "Owner access required.")
    import asyncio
    from services.factor_miner import run_factor_mining
    asyncio.create_task(run_factor_mining())
    return {"message": "Factor mining run triggered in background."}


@router.get("/history/export")
async def export_signal_history(
    format: str = "xlsx",
    ticker: str = None,
    action: str = None,
    outcome: str = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """
    Export signal history as Excel (.xlsx).
    Columns: ticker, action, confidence, entry, stop, target, rr, outcome_pct, style, created_at, notes.
    Filters: ticker, action (BUY/SELL/HOLD), outcome (wins/losses/open).
    """
    import io
    from fastapi.responses import StreamingResponse
    from sqlalchemy import select, and_

    q = select(Signal).where(Signal.is_sent == True)
    if ticker:
        q = q.where(Signal.ticker == ticker.upper())
    if action:
        q = q.where(Signal.action == action.upper())
    if outcome == "wins":
        q = q.where(Signal.outcome_pct > 0)
    elif outcome == "losses":
        q = q.where(Signal.outcome_pct <= 0)
    elif outcome == "open":
        q = q.where(Signal.outcome_pct.is_(None))
    q = q.order_by(Signal.created_at.desc()).limit(2000)
    rows = (await db.execute(q)).scalars().all()

    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter
    except ImportError:
        from fastapi import HTTPException
        raise HTTPException(500, "openpyxl not installed — run: pip install openpyxl")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Signal History"

    headers = ["Ticker", "Action", "Confidence %", "Entry", "Stop", "Target",
               "R:R", "Outcome %", "7d Outcome %", "Style", "Created At", "Notes"]
    header_fill   = PatternFill("solid", fgColor="1F2937")
    header_font   = Font(bold=True, color="FFFFFF")
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill   = header_fill
        cell.font   = header_font
        cell.alignment = Alignment(horizontal="center")

    for r_idx, sig in enumerate(rows, 2):
        action_color = "D1FAE5" if sig.action == "BUY" else "FEE2E2" if sig.action == "SELL" else "FEF3C7"
        vals = [
            sig.ticker, sig.action,
            round(sig.confidence, 1) if sig.confidence else None,
            round(sig.entry, 2) if sig.entry else None,
            round(sig.stop,  2) if sig.stop  else None,
            round(sig.target,2) if sig.target else None,
            sig.rr,
            round(sig.outcome_pct, 2) if sig.outcome_pct is not None else None,
            round(sig.outcome_pct, 2) if sig.outcome_pct is not None else None,
            sig.style,
            sig.created_at.strftime("%Y-%m-%d %H:%M") if sig.created_at else None,
            sig.notes or "",
        ]
        for col, val in enumerate(vals, 1):
            cell = ws.cell(row=r_idx, column=col, value=val)
            if col == 2:
                cell.fill = PatternFill("solid", fgColor=action_color)
            if col == 8 and val is not None:
                cell.font = Font(color="059669" if val > 0 else "DC2626")

    # Auto-width
    for col in range(1, len(headers) + 1):
        max_len = max(
            len(str(ws.cell(row=r, column=col).value or "")) for r in range(1, len(rows) + 2)
        )
        ws.column_dimensions[get_column_letter(col)].width = min(max_len + 2, 30)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    filename = f"signals_{ticker or 'all'}_{action or 'all'}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/alpha-decay")
async def alpha_decay(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
    min_n: int = Query(3, description="Minimum signals per source to include"),
):
    """
    Alpha decay curve by signal source.

    For each source that fired in resolved signals, returns the win rate and
    average return at 1-day, 3-day, 7-day, and 14-day horizons. Reveals which
    scoring families have short-lived vs durable edge — informs optimal hold time
    per signal type.

    Response shape:
      { source: { n: int, h1d: {n,win_rate,avg_ret}, h3d: ..., h7d: ..., h14d: ... } }
    """
    import json as _json

    _ck = "alpha_decay"
    _cached = _cache_get(_ck)
    if _cached is not None:
        return _cached

    rows = (await db.execute(
        select(
            Signal.sources,
            Signal.action,
            Signal.outcome_1d,
            Signal.outcome_3d,
            Signal.outcome_pct,
            Signal.outcome_14d,
        )
        .where(Signal.is_sent == True)
        .where(Signal.action.in_(["BUY", "SELL"]))
        .where(
            (Signal.outcome_1d.isnot(None))
            | (Signal.outcome_3d.isnot(None))
            | (Signal.outcome_pct.isnot(None))
            | (Signal.outcome_14d.isnot(None))
        )
    )).all()

    # Accumulate per-source stats at each horizon
    from collections import defaultdict
    stats: dict[str, dict] = defaultdict(lambda: {
        "h1d":  {"wins": 0, "total": 0, "sum_ret": 0.0},
        "h3d":  {"wins": 0, "total": 0, "sum_ret": 0.0},
        "h7d":  {"wins": 0, "total": 0, "sum_ret": 0.0},
        "h14d": {"wins": 0, "total": 0, "sum_ret": 0.0},
        "n":    0,
    })

    for sources_raw, action, o1d, o3d, o7d, o14d in rows:
        try:
            srcs = _json.loads(sources_raw) if isinstance(sources_raw, str) else (sources_raw or [])
        except Exception:
            continue
        if not srcs:
            continue

        for src in srcs:
            s = stats[src]
            s["n"] += 1
            for horizon_key, outcome in [("h1d", o1d), ("h3d", o3d), ("h7d", o7d), ("h14d", o14d)]:
                if outcome is None:
                    continue
                h = s[horizon_key]
                h["total"] += 1
                h["sum_ret"] += outcome
                win = (outcome > 0)
                if win:
                    h["wins"] += 1

    # Format output, filter by min_n
    result = {}
    for src, data in sorted(stats.items(), key=lambda x: -x[1]["n"]):
        if data["n"] < min_n:
            continue
        entry: dict = {"n": data["n"]}
        for hk in ("h1d", "h3d", "h7d", "h14d"):
            h = data[hk]
            if h["total"] == 0:
                entry[hk] = None
            else:
                entry[hk] = {
                    "n":        h["total"],
                    "win_rate": round(h["wins"] / h["total"] * 100, 1),
                    "avg_ret":  round(h["sum_ret"] / h["total"], 2),
                }
        result[src] = entry

    _cache_set(_ck, result)
    return result


# ── Execution-confirm webhook ─────────────────────────────────────────────────
# Allows a broker or paper-trade adapter to POST back the actual fill price
# after a signal has been acted on.  The signal's entry_price is updated so
# that future outcome calculations (MAE/MFE, stop-enforced WR) use the real
# fill rather than the signal-generation price.

from pydantic import BaseModel as _BM

class _ExecutionConfirm(_BM):
    signal_id: int
    fill_price: float
    filled_at: Optional[str] = None   # ISO-8601; defaults to now


@router.post("/execution-confirm", tags=["signals"])
async def execution_confirm(
    body: _ExecutionConfirm,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Broker/adapter callback to confirm a trade was filled.

    Updates the signal's `entry` price so downstream P&L calculations
    (MAE/MFE, stop-enforced WR) use the actual fill rather than the
    indicative price at signal generation.
    Only the platform owner or a user who received the signal may confirm.
    """
    sig = await db.get(Signal, body.signal_id)
    if sig is None:
        raise HTTPException(status_code=404, detail="Signal not found")

    # Only the owner or a recipient of this signal may confirm
    delivered_to = (await db.execute(
        select(SignalDelivery.user_id).where(SignalDelivery.signal_id == sig.id)
    )).scalars().all()
    if not user.is_owner and user.id not in delivered_to:
        raise HTTPException(status_code=403, detail="Not authorised to confirm this signal")

    if body.fill_price <= 0:
        raise HTTPException(status_code=400, detail="fill_price must be positive")

    sig.entry = round(body.fill_price, 4)
    if body.filled_at:
        try:
            sig.sent_at = datetime.fromisoformat(body.filled_at.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            raise HTTPException(status_code=400, detail="filled_at must be ISO-8601")

    await db.commit()
    return {
        "ok": True,
        "signal_id": sig.id,
        "ticker": sig.ticker,
        "entry": sig.entry,
        "message": f"Fill confirmed for {sig.ticker} signal at ${sig.entry:.4f}",
    }
