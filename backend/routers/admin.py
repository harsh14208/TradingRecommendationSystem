"""
Admin router — owner-only endpoints for setup verification, user management, and MRR.
All endpoints require is_owner=True.
"""
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import TIER_PRICES_CENTS, get_settings
from database import get_db
from models import Signal, SignalDelivery, User, PerformanceSnapshot
from services.auth_svc import get_current_user

log = logging.getLogger("signal.trade.admin")
router = APIRouter(prefix="/api/admin", tags=["admin"])


def _require_owner(user: User = Depends(get_current_user)) -> User:
    if not user.is_owner:
        raise HTTPException(403, "Owner access required.")
    return user


# ── Setup health check ────────────────────────────────────────────────────────

@router.get("/setup-status")
async def setup_status(owner: User = Depends(_require_owner)):
    """Returns which critical .env vars are configured — no secrets exposed."""
    s = get_settings()
    owner_password_ok = bool(
        s.owner_email
        and s.owner_password
        and s.owner_password != "ChangeMe123!"
        and len(s.owner_password) >= 16
    )
    checks = [
        {
            "key":     "JWT_SECRET",
            "label":   "JWT Secret",
            "ok":      bool(s.jwt_secret),
            "note":    "Tokens reset on restart without this. Run stripe_setup.py." if not s.jwt_secret else "Set ✓",
            "critical": True,
        },
        {
            "key":     "OWNER_EMAIL",
            "label":   "Owner Account",
            "ok":      owner_password_ok,
            "note":    (
                "Set OWNER_EMAIL and a 16+ char OWNER_PASSWORD; never use ChangeMe123!."
                if not owner_password_ok else "Set ✓"
            ),
            "critical": True,
        },
        {
            "key":     "TELEGRAM_BOT_TOKEN",
            "label":   "Telegram Bot",
            "ok":      bool(s.telegram_bot_token),
            "note":    "Get from @BotFather on Telegram",
            "critical": True,
        },
        {
            "key":     "STRIPE_SECRET_KEY",
            "label":   "Stripe Secret Key",
            "ok":      bool(s.stripe_secret_key),
            "note":    "From dashboard.stripe.com → API keys. Run stripe_setup.py after adding.",
            "critical": True,
        },
        {
            "key":     "STRIPE_WEBHOOK_SECRET",
            "label":   "Stripe Webhook Secret",
            "ok":      bool(s.stripe_webhook_secret),
            "note":    "From Stripe → Webhooks → Signing secret (whsec_...)",
            "critical": True,
        },
        {
            "key":     "STRIPE_PRICE_BASIC",
            "label":   "Stripe Basic Price ID",
            "ok":      bool(s.stripe_price_basic) and not s.stripe_price_basic.startswith("price_..."),
            "note":    "Run python3 stripe_setup.py to create and auto-fill",
            "critical": True,
        },
        {
            "key":     "STRIPE_PRICE_PRO",
            "label":   "Stripe Pro Price ID",
            "ok":      bool(s.stripe_price_pro) and not s.stripe_price_pro.startswith("price_..."),
            "note":    "Run python3 stripe_setup.py to create and auto-fill",
            "critical": True,
        },
        {
            "key":     "APP_URL",
            "label":   "Public App URL (HTTPS)",
            "ok":      s.app_url.startswith("https://"),
            "note":    "Required for Stripe redirects + Telegram webhook. Set to your deployed URL.",
            "critical": True,
        },
        {
            "key":     "SMTP_HOST",
            "label":   "Email (SMTP)",
            "ok":      bool(s.smtp_host),
            "note":    "Optional — sign-up/receipt emails won't send without this. Use SendGrid free tier.",
            "critical": False,
        },
        {
            "key":     "FINNHUB_API_KEY",
            "label":   "Finnhub API Key",
            "ok":      bool(s.finnhub_api_key),
            "note":    "Free at finnhub.io — needed for news sentiment + analyst recs",
            "critical": False,
        },
        {
            "key":     "ALPACA_API_KEY",
            "label":   "Alpaca Paper Trading",
            "ok":      bool(s.alpaca_api_key),
            "note":    "Free at alpaca.markets — needed for real-time prices + paper trading",
            "critical": False,
        },
        {
            "key":     "FRED_API_KEY",
            "label":   "FRED Macro Data",
            "ok":      bool(s.fred_api_key),
            "note":    "Free at fred.stlouisfed.org — needed for CPI/NFP/FOMC calendar",
            "critical": False,
        },
    ]
    all_critical_ok = all(c["ok"] for c in checks if c["critical"])
    return {
        "checks":          checks,
        "all_critical_ok": all_critical_ok,
        "app_url":         s.app_url,
        "telegram_webhook_url": f"{s.app_url}/api/telegram/webhook",
        "stripe_webhook_url":   f"{s.app_url}/api/billing/webhook",
    }


# ── User management ───────────────────────────────────────────────────────────

@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(_require_owner),
):
    rows = (await db.execute(
        select(User).order_by(User.created_at.desc())
    )).scalars().all()
    return [
        {
            "id":                  u.id,
            "email":               u.email,
            "full_name":           u.full_name,
            "is_owner":            u.is_owner,
            "tier":                u.subscription_tier,
            "status":              u.subscription_status,
            "telegram_linked":     bool(u.telegram_chat_id),
            "created_at":          u.created_at.isoformat() if u.created_at else None,
            "last_seen_at":        u.last_seen_at.isoformat() if u.last_seen_at else None,
            "period_end":          u.subscription_period_end.isoformat() if u.subscription_period_end else None,
        }
        for u in rows
    ]


@router.get("/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(_require_owner),
):
    s = get_settings()
    all_users   = (await db.execute(select(func.count()).select_from(User))).scalar()
    active_subs = (await db.execute(
        select(func.count()).select_from(User).where(User.subscription_status == "active")
    )).scalar()
    basic_count = (await db.execute(
        select(func.count()).select_from(User).where(
            User.subscription_tier == "basic", User.subscription_status == "active"
        )
    )).scalar()
    pro_count = (await db.execute(
        select(func.count()).select_from(User).where(
            User.subscription_tier == "pro", User.subscription_status == "active"
        )
    )).scalar()
    tg_linked = (await db.execute(
        select(func.count()).select_from(User).where(User.telegram_chat_id.isnot(None))
    )).scalar()

    # MRR estimate from the same source of truth used by billing/pricing.
    mrr = round(
        (basic_count * TIER_PRICES_CENTS["basic"] + pro_count * TIER_PRICES_CENTS["pro"]) / 100,
        2,
    )

    # Signal stats
    total_signals = (await db.execute(select(func.count()).select_from(Signal))).scalar()
    sent_signals  = (await db.execute(
        select(func.count()).select_from(Signal).where(Signal.is_sent == True)
    )).scalar()
    from datetime import timezone as _tz
    _now_utc = datetime.now(_tz.utc)
    deliveries_30d = (await db.execute(
        select(func.count()).select_from(SignalDelivery).where(
            SignalDelivery.sent_at >= _now_utc - timedelta(days=30)
        )
    )).scalar()

    # New users last 30 days
    new_users_30d = (await db.execute(
        select(func.count()).select_from(User).where(
            User.created_at >= _now_utc - timedelta(days=30)
        )
    )).scalar()

    return {
        "users": {
            "total":         all_users,
            "active_subs":   active_subs,
            "basic":         basic_count,
            "pro":           pro_count,
            "telegram_linked": tg_linked,
            "new_30d":       new_users_30d,
        },
        "mrr":            mrr,
        "arr":            round(mrr * 12, 2),
        "signals": {
            "total":        total_signals,
            "sent":         sent_signals,
            "deliveries_30d": deliveries_30d,
        },
    }


from pydantic import BaseModel as _BaseModel

class _SetTierIn(_BaseModel):
    tier:   str = "free"
    status: str = "active"


@router.post("/users/{user_id}/tier")
async def set_user_tier(
    user_id: int,
    body: _SetTierIn,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(_require_owner),
):
    """Manually override a user's subscription tier (e.g. grant free Pro access)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found.")
    if body.tier not in ("free", "basic", "pro"):
        raise HTTPException(400, "Invalid tier.")
    if body.status not in ("active", "inactive", "past_due", "canceled"):
        raise HTTPException(400, "Invalid status.")
    user.subscription_tier   = body.tier
    user.subscription_status = body.status
    await db.commit()
    log.info(f"[admin] tier override user={user_id} tier={body.tier} by owner")
    return {"ok": True, "tier": body.tier, "status": body.status}


@router.get("/rate-limits", tags=["admin"])
async def rate_limit_dashboard(owner: User = Depends(_require_owner)):
    """
    Owner-only — returns API rate-limit counters and scan cycle duration history.
    Helps diagnose slowdowns without reading server logs.
    """
    import time as _time

    result: dict = {}

    # yfinance circuit breaker state
    try:
        from services.market_data import _yf_backoff_until
        now = _time.time()
        if _yf_backoff_until > now:
            result["yfinance_blocked"] = True
            result["yfinance_unblocked_in_secs"] = round(_yf_backoff_until - now)
        else:
            result["yfinance_blocked"] = False
    except Exception:
        pass

    # Polygon indicator cache hit stats
    try:
        from services.polygon_indicators import _cache as _poly_cache, _TTL
        cached = sum(1 for v in _poly_cache.values() if _time.time() - v["ts"] < _TTL)
        result["polygon_indicator_cache_warm"] = cached
        result["polygon_indicator_cache_total"] = len(_poly_cache)
    except Exception:
        pass

    # OHLCV shared cache stats
    try:
        from services.market_data import _ohlcv_cache, _OHLCV_TTL
        warm = sum(1 for v in _ohlcv_cache.values() if _time.time() - v["ts"] < _OHLCV_TTL)
        result["ohlcv_cache_warm"] = warm
        result["ohlcv_cache_total"] = len(_ohlcv_cache)
    except Exception:
        pass

    # Macro cache age
    try:
        from services.macro import _cache as _macro_cache
        age = round(_time.time() - _macro_cache["ts"])
        result["macro_cache_age_secs"] = age
    except Exception:
        pass

    # News batch cache age
    try:
        from services.benzinga_news import _batch_cache
        age = round(_time.time() - _batch_cache["ts"])
        result["news_batch_cache_age_secs"] = age
    except Exception:
        pass

    # Screener suggestions from app_settings
    try:
        from sqlalchemy import select as _sel
        from models import AppSettings
        from database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            row = (await db.execute(_sel(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
            if row and row.data:
                sugg = row.data.get("screener_suggestions")
                if sugg:
                    result["screener_suggestions"] = sugg
                    result["screener_updated"] = row.data.get("screener_updated")
    except Exception:
        pass

    # Worker bus stats — circuit breaker state per scoring worker
    try:
        from services.signal_workers import ALL_WORKERS
        from services.worker_bus import collect_worker_stats
        result["worker_stats"] = collect_worker_stats(ALL_WORKERS)
        # Redis bus status
        import os
        result["worker_bus_backend"] = "redis" if os.getenv("REDIS_URL") else "asyncio"
        result["redis_url_set"] = bool(os.getenv("REDIS_URL"))
    except Exception:
        pass

    return result


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(_require_owner),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found.")
    if user.is_owner:
        raise HTTPException(400, "Cannot delete owner account.")
    await db.delete(user)
    await db.commit()
    log.info(f"[admin] deleted user={user_id}")
    return {"ok": True}


# ── Signal delivery SLA ───────────────────────────────────────────────────────

@router.get("/delivery-sla")
async def delivery_sla(
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(_require_owner),
):
    """
    Returns signal delivery latency percentiles and SLA breach count for the
    last 24 hours. Latency = sent_at - created_at per signal row.
    """
    import numpy as np

    from datetime import timezone as _tz
    cutoff = datetime.now(_tz.utc) - timedelta(hours=24)
    rows = (await db.execute(
        select(Signal.created_at, Signal.sent_at)
        .where(Signal.is_sent == True)
        .where(Signal.sent_at >= cutoff)
        .where(Signal.created_at.isnot(None))
    )).all()

    total_sent_24h = len(rows)
    latencies = [
        (row.sent_at - row.created_at).total_seconds()
        for row in rows
        if row.sent_at and row.created_at
    ]

    sla_breaches_24h = sum(1 for s in latencies if s > 300)

    if latencies:
        arr = np.array(latencies)
        p50 = round(float(np.percentile(arr, 50)), 1)
        p95 = round(float(np.percentile(arr, 95)), 1)
        p99 = round(float(np.percentile(arr, 99)), 1)
    else:
        p50 = p95 = p99 = 0.0

    return {
        "p50_latency_s":    p50,
        "p95_latency_s":    p95,
        "p99_latency_s":    p99,
        "sla_breaches_24h": sla_breaches_24h,
        "total_sent_24h":   total_sent_24h,
    }


# ── Performance Snapshots ─────────────────────────────────────────────────────

@router.get("/snapshots")
async def list_snapshots(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(_require_owner),
):
    """Return the most recent N performance snapshots (summary fields only)."""
    rows = (await db.execute(
        select(PerformanceSnapshot)
        .order_by(PerformanceSnapshot.created_at.desc())
        .limit(limit)
    )).scalars().all()
    return [
        {
            "id":         r.id,
            "tag":        r.tag,
            "git_sha":    r.git_sha,
            "n_trades":   r.n_trades,
            "win_rate":   r.win_rate,
            "sharpe":     r.sharpe,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/snapshots/{snapshot_id}")
async def get_snapshot(
    snapshot_id: int,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(_require_owner),
):
    """Return the full metrics dict for one snapshot."""
    row = (await db.execute(
        select(PerformanceSnapshot).where(PerformanceSnapshot.id == snapshot_id)
    )).scalar_one_or_none()
    if not row:
        raise HTTPException(404, f"Snapshot {snapshot_id} not found")
    return {
        "id":         row.id,
        "tag":        row.tag,
        "git_sha":    row.git_sha,
        "n_trades":   row.n_trades,
        "win_rate":   row.win_rate,
        "sharpe":     row.sharpe,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "metrics":    row.metrics,
    }


@router.get("/snapshots/diff/{id_a}/{id_b}")
async def diff_snapshots_endpoint(
    id_a: int,
    id_b: int,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(_require_owner),
):
    """
    Compute the metric delta between snapshot id_a (before) and id_b (after).

    Each field in the response has: {before, after, delta, delta_pct, flag}
    where flag=True marks changes exceeding significance thresholds.
    """
    from scripts.calc_tbd_metrics import diff_snapshots

    rows = (await db.execute(
        select(PerformanceSnapshot).where(
            PerformanceSnapshot.id.in_([id_a, id_b])
        )
    )).scalars().all()

    by_id = {r.id: r for r in rows}
    if id_a not in by_id:
        raise HTTPException(404, f"Snapshot {id_a} not found")
    if id_b not in by_id:
        raise HTTPException(404, f"Snapshot {id_b} not found")

    a, b = by_id[id_a], by_id[id_b]
    delta = diff_snapshots(a.metrics, b.metrics)

    flagged = _find_flagged(delta)

    return {
        "before": {"id": a.id, "tag": a.tag, "created_at": a.created_at.isoformat() if a.created_at else None},
        "after":  {"id": b.id, "tag": b.tag, "created_at": b.created_at.isoformat() if b.created_at else None},
        "delta":  delta,
        "flagged_metrics": flagged,
    }


def _find_flagged(d: dict, prefix: str = "") -> list[dict]:
    """Recursively collect fields where flag=True."""
    flagged = []
    for k, v in d.items():
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            if v.get("flag"):
                flagged.append({
                    "metric": path,
                    "before": v.get("before"),
                    "after":  v.get("after"),
                    "delta":  v.get("delta"),
                    "delta_pct": v.get("delta_pct"),
                })
            else:
                flagged.extend(_find_flagged(v, path))
    return flagged
