"""
Admin router — owner-only endpoints for setup verification, user management, and MRR.
All endpoints require is_owner=True.
"""

import logging
from datetime import datetime, timedelta

from config import TIER_PRICES_CENTS, get_settings
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from models import AppSettings, PerformanceSnapshot, Signal, SignalDelivery, User
from services.auth_svc import get_current_user
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

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
        s.owner_email and s.owner_password and s.owner_password != "ChangeMe123!" and len(s.owner_password) >= 16
    )
    checks = [
        {
            "key": "JWT_SECRET",
            "label": "JWT Secret",
            "ok": bool(s.jwt_secret),
            "note": "Tokens reset on restart without this. Run stripe_setup.py." if not s.jwt_secret else "Set ✓",
            "critical": True,
        },
        {
            "key": "OWNER_EMAIL",
            "label": "Owner Account",
            "ok": owner_password_ok,
            "note": (
                "Set OWNER_EMAIL and a 16+ char OWNER_PASSWORD; never use ChangeMe123!."
                if not owner_password_ok
                else "Set ✓"
            ),
            "critical": True,
        },
        {
            "key": "TELEGRAM_BOT_TOKEN",
            "label": "Telegram Bot",
            "ok": bool(s.telegram_bot_token),
            "note": "Get from @BotFather on Telegram",
            "critical": True,
        },
        {
            "key": "STRIPE_SECRET_KEY",
            "label": "Stripe Secret Key",
            "ok": bool(s.stripe_secret_key),
            "note": "From dashboard.stripe.com → API keys. Run stripe_setup.py after adding.",
            "critical": True,
        },
        {
            "key": "STRIPE_WEBHOOK_SECRET",
            "label": "Stripe Webhook Secret",
            "ok": bool(s.stripe_webhook_secret),
            "note": "From Stripe → Webhooks → Signing secret (whsec_...)",
            "critical": True,
        },
        {
            "key": "STRIPE_PRICE_BASIC",
            "label": "Stripe Basic Price ID",
            "ok": bool(s.stripe_price_basic) and not s.stripe_price_basic.startswith("price_..."),
            "note": "Run python3 stripe_setup.py to create and auto-fill",
            "critical": True,
        },
        {
            "key": "STRIPE_PRICE_PRO",
            "label": "Stripe Pro Price ID",
            "ok": bool(s.stripe_price_pro) and not s.stripe_price_pro.startswith("price_..."),
            "note": "Run python3 stripe_setup.py to create and auto-fill",
            "critical": True,
        },
        {
            "key": "APP_URL",
            "label": "Public App URL (HTTPS)",
            "ok": s.app_url.startswith("https://"),
            "note": "Required for Stripe redirects + Telegram webhook. Set to your deployed URL.",
            "critical": True,
        },
        {
            "key": "SMTP_HOST",
            "label": "Email (SMTP)",
            "ok": bool(s.smtp_host),
            "note": "Optional — sign-up/receipt emails won't send without this. Use SendGrid free tier.",
            "critical": False,
        },
        {
            "key": "FINNHUB_API_KEY",
            "label": "Finnhub API Key",
            "ok": bool(s.finnhub_api_key),
            "note": "Free at finnhub.io — needed for news sentiment + analyst recs",
            "critical": False,
        },
        {
            "key": "ALPACA_API_KEY",
            "label": "Alpaca Paper Trading",
            "ok": bool(s.alpaca_api_key),
            "note": "Free at alpaca.markets — needed for real-time prices + paper trading",
            "critical": False,
        },
        {
            "key": "FRED_API_KEY",
            "label": "FRED Macro Data",
            "ok": bool(s.fred_api_key),
            "note": "Free at fred.stlouisfed.org — needed for CPI/NFP/FOMC calendar",
            "critical": False,
        },
    ]
    all_critical_ok = all(c["ok"] for c in checks if c["critical"])
    return {
        "checks": checks,
        "all_critical_ok": all_critical_ok,
        "app_url": s.app_url,
        "telegram_webhook_url": f"{s.app_url}/api/telegram/webhook",
        "stripe_webhook_url": f"{s.app_url}/api/billing/webhook",
    }


@router.get("/system-readiness")
async def system_readiness(
    owner: User = Depends(_require_owner),
    db: AsyncSession = Depends(get_db),
):
    """
    Computes system launch readiness by checking:
    1. Critical environment variables
    2. Database connection health and latency
    3. External provider API status (Alpaca, Finnhub, FRED, Polygon)
    4. Webhook settings (Telegram, Stripe)
    5. Background queues (Redis if configured)
    6. System status flags (Kill-switch)
    """
    import time
    import asyncio
    from services.http_client import shared_session
    from services.broker_svc import verify_alpaca_connection

    s = get_settings()

    # 1. Env check (equivalent to setup-status critical check logic)
    owner_password_ok = bool(
        s.owner_email and s.owner_password and s.owner_password != "ChangeMe123!" and len(s.owner_password) >= 16
    )
    env_checks = {
        "jwt_secret": bool(s.jwt_secret),
        "owner_account": owner_password_ok,
        "telegram_bot_token": bool(s.telegram_bot_token),
        "stripe_secret_key": bool(s.stripe_secret_key),
        "stripe_webhook_secret": bool(s.stripe_webhook_secret),
        "stripe_price_basic": bool(s.stripe_price_basic) and not s.stripe_price_basic.startswith("price_..."),
        "stripe_price_pro": bool(s.stripe_price_pro) and not s.stripe_price_pro.startswith("price_..."),
        "app_url": s.app_url.startswith("https://"),
    }
    env_ok = all(env_checks.values())

    # 2. Database Check
    db_ok = True
    db_error = None
    db_start = time.monotonic()
    try:
        await db.execute(select(1))
    except Exception as e:
        db_ok = False
        db_error = str(e)
    db_latency = (time.monotonic() - db_start) * 1000

    # 3. Kill Switch Check
    row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    execution_paused = bool(row and row.data and row.data.get("execution_paused"))

    # Check providers and webhooks
    providers = {}
    webhooks = {}
    queues = {}

    # 5. Background queue / Redis
    redis_ok = True
    redis_error = None
    if s.redis_url:
        try:
            import redis.asyncio as aioredis

            r = aioredis.from_url(s.redis_url)
            await asyncio.wait_for(r.ping(), timeout=3.0)
            await r.close()
        except Exception as e:
            redis_ok = False
            redis_error = str(e)

    queues["redis"] = {
        "configured": bool(s.redis_url),
        "status": "ok" if redis_ok else "error",
        "error": redis_error,
    }

    # Helper function to check an HTTP endpoint
    async def check_endpoint(session, url, name):
        try:
            async with session.get(url, timeout=3.0) as resp:
                if resp.status == 200:
                    return True, None
                else:
                    return False, f"HTTP {resp.status}"
        except Exception as e:
            return False, str(e)

    async with shared_session() as session:
        # Check Alpaca
        alpaca_ok = False
        alpaca_err = None
        if s.alpaca_api_key and s.alpaca_api_secret:
            try:
                # Reuse verify_alpaca_connection
                await asyncio.wait_for(
                    verify_alpaca_connection(s.alpaca_api_key, s.alpaca_api_secret, live=False), timeout=3.0
                )
                alpaca_ok = True
            except Exception as e:
                alpaca_err = str(e)
        else:
            alpaca_err = "Alpaca API keys not set"

        providers["alpaca"] = {"status": "ok" if alpaca_ok else "error", "error": alpaca_err}

        # Check Finnhub
        finnhub_ok = False
        finnhub_err = None
        if s.finnhub_api_key:
            finnhub_ok, finnhub_err = await check_endpoint(
                session, f"https://finnhub.io/api/v1/news?category=general&token={s.finnhub_api_key}", "Finnhub"
            )
        else:
            finnhub_err = "Finnhub API key not set"

        providers["finnhub"] = {"status": "ok" if finnhub_ok else "error", "error": finnhub_err}

        # Check FRED
        fred_ok = False
        fred_err = None
        if s.fred_api_key:
            fred_ok, fred_err = await check_endpoint(
                session,
                f"https://api.stlouisfed.org/fred/series?series_id=VIXCLS&api_key={s.fred_api_key}&file_type=json",
                "FRED",
            )
        else:
            fred_err = "FRED API key not set"

        providers["fred"] = {"status": "ok" if fred_ok else "error", "error": fred_err}

        # Check Polygon
        polygon_ok = False
        polygon_err = None
        if s.polygon_api_key:
            polygon_ok, polygon_err = await check_endpoint(
                session, f"https://api.polygon.io/v1/meta/crypto-exchanges?apiKey={s.polygon_api_key}", "Polygon"
            )
        else:
            polygon_err = "Polygon API key not set"

        providers["polygon"] = {"status": "ok" if polygon_ok else "error", "error": polygon_err}

        # Check Telegram Webhook info
        telegram_ok = False
        telegram_err = None
        telegram_webhook_info = {}
        if s.telegram_bot_token:
            try:
                async with session.get(
                    f"https://api.telegram.org/bot{s.telegram_bot_token}/getWebhookInfo", timeout=3.0
                ) as resp:
                    if resp.status == 200:
                        res_data = await resp.json()
                        if res_data.get("ok"):
                            telegram_webhook_info = res_data.get("result", {})
                            actual_url = telegram_webhook_info.get("url", "")
                            expected_url = f"{s.app_url}/api/telegram/webhook"
                            if actual_url == expected_url:
                                telegram_ok = True
                            else:
                                telegram_err = (
                                    f"Webhook URL mismatch: expected {expected_url}, got {actual_url or 'None'}"
                                )
                        else:
                            telegram_err = "Telegram API error response"
                    else:
                        telegram_err = f"HTTP {resp.status}"
            except Exception as e:
                telegram_err = str(e)
        else:
            telegram_err = "Telegram bot token not set"

        webhooks["telegram"] = {
            "status": "ok" if telegram_ok else "error",
            "webhook_info": telegram_webhook_info,
            "error": telegram_err,
        }

    # Check Stripe Webhook Configuration
    stripe_ok = bool(s.stripe_webhook_secret and s.stripe_webhook_secret.startswith("whsec_"))
    webhooks["stripe"] = {
        "status": "ok" if stripe_ok else "error",
        "error": None if stripe_ok else "Stripe Webhook Secret not configured or invalid format",
    }

    # Overall launch readiness score / status
    ready = env_ok and db_ok and not execution_paused and telegram_ok and stripe_ok and alpaca_ok and redis_ok

    return {
        "ready": ready,
        "kill_switch": {"execution_paused": execution_paused},
        "database": {"status": "ok" if db_ok else "error", "latency_ms": db_latency, "error": db_error},
        "env_vars": {"status": "ok" if env_ok else "error", "checks": env_checks},
        "providers": providers,
        "webhooks": webhooks,
        "queues": queues,
    }


# ── User management ───────────────────────────────────────────────────────────


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(_require_owner),
):
    rows = (await db.execute(select(User).order_by(User.created_at.desc()))).scalars().all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "is_owner": u.is_owner,
            "tier": u.subscription_tier,
            "status": u.subscription_status,
            "telegram_linked": bool(u.telegram_chat_id),
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "last_seen_at": u.last_seen_at.isoformat() if u.last_seen_at else None,
            "period_end": u.subscription_period_end.isoformat() if u.subscription_period_end else None,
        }
        for u in rows
    ]


@router.get("/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(_require_owner),
):
    s = get_settings()
    all_users = (await db.execute(select(func.count()).select_from(User))).scalar()
    active_subs = (
        await db.execute(select(func.count()).select_from(User).where(User.subscription_status == "active"))
    ).scalar()
    basic_count = (
        await db.execute(
            select(func.count())
            .select_from(User)
            .where(User.subscription_tier == "basic", User.subscription_status == "active")
        )
    ).scalar()
    pro_count = (
        await db.execute(
            select(func.count())
            .select_from(User)
            .where(User.subscription_tier == "pro", User.subscription_status == "active")
        )
    ).scalar()
    tg_linked = (
        await db.execute(select(func.count()).select_from(User).where(User.telegram_chat_id.isnot(None)))
    ).scalar()

    # MRR estimate from the same source of truth used by billing/pricing.
    mrr = round(
        (basic_count * TIER_PRICES_CENTS["basic"] + pro_count * TIER_PRICES_CENTS["pro"]) / 100,
        2,
    )

    # Signal stats
    total_signals = (await db.execute(select(func.count()).select_from(Signal))).scalar()
    sent_signals = (await db.execute(select(func.count()).select_from(Signal).where(Signal.is_sent == True))).scalar()
    from datetime import timezone as _tz

    _now_utc = datetime.now(_tz.utc).replace(tzinfo=None)
    deliveries_30d = (
        await db.execute(
            select(func.count())
            .select_from(SignalDelivery)
            .where(SignalDelivery.sent_at >= _now_utc - timedelta(days=30))
        )
    ).scalar()

    # New users last 30 days
    new_users_30d = (
        await db.execute(select(func.count()).select_from(User).where(User.created_at >= _now_utc - timedelta(days=30)))
    ).scalar()

    return {
        "users": {
            "total": all_users,
            "active_subs": active_subs,
            "basic": basic_count,
            "pro": pro_count,
            "telegram_linked": tg_linked,
            "new_30d": new_users_30d,
        },
        "mrr": mrr,
        "arr": round(mrr * 12, 2),
        "signals": {
            "total": total_signals,
            "sent": sent_signals,
            "deliveries_30d": deliveries_30d,
        },
    }


from pydantic import BaseModel as _BaseModel


class _SetTierIn(_BaseModel):
    tier: str = "free"
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
    user.subscription_tier = body.tier
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
        from services.polygon_indicators import _TTL
        from services.polygon_indicators import _cache as _poly_cache

        cached = sum(1 for v in _poly_cache.values() if _time.time() - v["ts"] < _TTL)
        result["polygon_indicator_cache_warm"] = cached
        result["polygon_indicator_cache_total"] = len(_poly_cache)
    except Exception:
        pass

    # OHLCV shared cache stats
    try:
        from services.market_data import _OHLCV_TTL, _ohlcv_cache

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
        from database import AsyncSessionLocal
        from models import AppSettings
        from sqlalchemy import select as _sel

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

    # TSYS-13d: GDPR/CCPA deletion verification report. Count related records and
    # capture third-party identifiers before deletion, then verify cascade after.
    from sqlalchemy import func

    from models import BrokerOrder, RefreshToken, SignalDelivery

    async def _count(model):
        return (await db.execute(select(func.count(model.id)).where(model.user_id == user_id))).scalar() or 0

    before = {
        "signal_deliveries": await _count(SignalDelivery),
        "broker_orders": await _count(BrokerOrder),
        "refresh_tokens": await _count(RefreshToken),
    }
    third_party = {
        "stripe_customer_id": bool(user.stripe_customer_id),
        "telegram_chat_id": bool(user.telegram_chat_id),
        "broker_credentials": bool(user.alpaca_key_enc),
    }

    # TSYS-13c: audit the deletion before the user row (and its FK row) is gone.
    from services.audit_svc import ACTION_ACCOUNT_DELETION, record_action

    await record_action(
        db,
        ACTION_ACCOUNT_DELETION,
        user_id=None,  # user row is about to be deleted; keep the log orphan-safe
        details={"deleted_user_id": user_id, "related": before, "third_party": third_party},
    )

    await db.delete(user)
    await db.commit()

    # Verify the cascade actually removed the child rows.
    after = {
        "signal_deliveries": await _count(SignalDelivery),
        "broker_orders": await _count(BrokerOrder),
        "refresh_tokens": await _count(RefreshToken),
    }
    fully_purged = all(v == 0 for v in after.values())
    log.info(f"[admin] deleted user={user_id} purged={fully_purged} before={before}")
    return {
        "ok": True,
        "deleted_user_id": user_id,
        "records_before": before,
        "records_after": after,
        "third_party_identifiers_cleared": third_party,
        "fully_purged": fully_purged,
    }


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
    from datetime import timezone as _tz

    import numpy as np

    cutoff = datetime.now(_tz.utc).replace(tzinfo=None) - timedelta(hours=24)
    rows = (
        await db.execute(
            select(Signal.created_at, Signal.sent_at)
            .where(Signal.is_sent == True)
            .where(Signal.sent_at >= cutoff)
            .where(Signal.created_at.isnot(None))
        )
    ).all()

    total_sent_24h = len(rows)
    latencies = [(row.sent_at - row.created_at).total_seconds() for row in rows if row.sent_at and row.created_at]

    sla_breaches_24h = sum(1 for s in latencies if s > 300)

    if latencies:
        arr = np.array(latencies)
        p50 = round(float(np.percentile(arr, 50)), 1)
        p95 = round(float(np.percentile(arr, 95)), 1)
        p99 = round(float(np.percentile(arr, 99)), 1)
    else:
        p50 = p95 = p99 = 0.0

    return {
        "p50_latency_s": p50,
        "p95_latency_s": p95,
        "p99_latency_s": p99,
        "sla_breaches_24h": sla_breaches_24h,
        "total_sent_24h": total_sent_24h,
    }


# ── Performance Snapshots ─────────────────────────────────────────────────────


@router.get("/snapshots")
async def list_snapshots(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(_require_owner),
):
    """Return the most recent N performance snapshots (summary fields only)."""
    rows = (
        (await db.execute(select(PerformanceSnapshot).order_by(PerformanceSnapshot.created_at.desc()).limit(limit)))
        .scalars()
        .all()
    )
    return [
        {
            "id": r.id,
            "tag": r.tag,
            "git_sha": r.git_sha,
            "n_trades": r.n_trades,
            "win_rate": r.win_rate,
            "sharpe": r.sharpe,
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
    row = (
        await db.execute(select(PerformanceSnapshot).where(PerformanceSnapshot.id == snapshot_id))
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(404, f"Snapshot {snapshot_id} not found")
    return {
        "id": row.id,
        "tag": row.tag,
        "git_sha": row.git_sha,
        "n_trades": row.n_trades,
        "win_rate": row.win_rate,
        "sharpe": row.sharpe,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "metrics": row.metrics,
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

    rows = (
        (await db.execute(select(PerformanceSnapshot).where(PerformanceSnapshot.id.in_([id_a, id_b])))).scalars().all()
    )

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
        "after": {"id": b.id, "tag": b.tag, "created_at": b.created_at.isoformat() if b.created_at else None},
        "delta": delta,
        "flagged_metrics": flagged,
    }


@router.post("/execution-kill-switch")
async def execution_kill_switch(
    owner: User = Depends(_require_owner),
    db: AsyncSession = Depends(get_db),
):
    """
    Toggle the broker auto-execution kill switch.

    When paused=True, scanner._maybe_auto_execute_for_signal() skips all
    orders without error. Use during circuit breaker events, broker API
    outages, or flash crash conditions.
    Returns the new state.
    """
    row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    if not row:
        row = AppSettings(id=1, data={})
        db.add(row)
    data = dict(row.data or {})
    data["execution_paused"] = not data.get("execution_paused", False)
    row.data = data
    # TSYS-13c: immutable audit of the kill-switch toggle.
    from services.audit_svc import ACTION_KILL_SWITCH, record_action

    await record_action(
        db,
        ACTION_KILL_SWITCH,
        user_id=owner.id,
        details={"execution_paused": data["execution_paused"]},
    )
    await db.commit()
    log.info("kill_switch: execution_paused set to %s by owner=%d", data["execution_paused"], owner.id)
    return {"execution_paused": data["execution_paused"]}


@router.get("/execution-kill-switch")
async def get_kill_switch_status(
    owner: User = Depends(_require_owner),
    db: AsyncSession = Depends(get_db),
):
    """Return the current state of the broker auto-execution kill switch."""
    row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    paused = bool(row and row.data and row.data.get("execution_paused"))
    return {"execution_paused": paused}


import math as _math


def _wilson_ci(wins: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score 95% CI for a proportion. Returns (lower_pct, upper_pct)."""
    if n == 0:
        return 0.0, 100.0
    p = wins / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * _math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return round(max(0.0, centre - margin) * 100, 1), round(min(1.0, centre + margin) * 100, 1)


@router.get("/live-wr-stats")
async def live_wr_stats(
    days: int = 90,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(_require_owner),
):
    """
    OOS-5: Live WR tracking with Wilson 95% CI bands.

    Returns overall and rolling-window WR with confidence intervals.
    Flag is raised when the lower CI bound drops below 55%.
    """
    from datetime import timezone as _tz

    cutoff = datetime.now(_tz.utc).replace(tzinfo=None) - timedelta(days=days)

    all_resolved = (
        (await db.execute(select(Signal).where(Signal.outcome_pct.isnot(None)).where(Signal.is_sent == True)))
        .scalars()
        .all()
    )
    recent = [s for s in all_resolved if s.created_at and s.created_at >= cutoff]

    def _stats(sigs):
        n = len(sigs)
        wins = sum(1 for s in sigs if (s.outcome_pct or 0) > 0)
        wr = round(wins / n * 100, 1) if n else None
        lo, hi = _wilson_ci(wins, n) if n else (None, None)
        avg_ret = round(sum(s.outcome_pct for s in sigs if s.outcome_pct) / n, 3) if n else None
        return {"n": n, "wins": wins, "wr_pct": wr, "ci_lo": lo, "ci_hi": hi, "avg_ret_pct": avg_ret}

    overall = _stats(all_resolved)
    rolling = _stats(recent)

    ci_lo = rolling.get("ci_lo")
    flag = ci_lo is not None and ci_lo < 55.0 and rolling["n"] >= 20

    return {
        "overall": overall,
        f"rolling_{days}d": rolling,
        "flag": flag,
        "flag_reason": f"Rolling lower CI {ci_lo:.1f}% < 55% floor (N={rolling['n']})" if flag else None,
    }


@router.get("/analytics-summary")
async def analytics_summary(
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(_require_owner),
):
    """
    PROD-4: Admin analytics dashboard summary.

    Returns daily/weekly signal volume, tier breakdown, live WR, MRR estimate,
    and calibration Brier score — all from the local DB.
    """
    from datetime import timezone as _tz

    now = datetime.now(_tz.utc).replace(tzinfo=None)
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)

    # Signal counts
    all_signals = (await db.execute(select(Signal))).scalars().all()
    signals_today = [s for s in all_signals if s.created_at and s.created_at >= day_ago]
    signals_week = [s for s in all_signals if s.created_at and s.created_at >= week_ago]
    delivered_week = [s for s in signals_week if s.is_sent]
    resolved = [s for s in all_signals if s.outcome_pct is not None]
    wins = [s for s in resolved if (s.outcome_pct or 0) > 0]

    # User tier breakdown
    all_users = (await db.execute(select(User).where(User.is_active == True))).scalars().all()
    tier_counts: dict[str, int] = {}
    for u in all_users:
        tier = u.subscription_tier or "free"
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    active_paid = sum(1 for u in all_users if u.subscription_status == "active")

    # MRR estimate
    try:
        _prices = {"basic": 29, "pro": 79, "elite": 149}
        mrr = sum(_prices.get(u.subscription_tier or "", 0) for u in all_users if u.subscription_status == "active")
    except Exception:
        mrr = None

    # Calibration Brier score
    brier = None
    if resolved:
        total_sq = sum(
            ((s.confidence or 50.0) / 100.0 - (1.0 if (s.outcome_pct or 0) > 0 else 0.0)) ** 2
            for s in resolved
            if s.confidence is not None
        )
        brier = round(total_sq / len(resolved), 4)

    lo, hi = _wilson_ci(len(wins), len(resolved)) if resolved else (None, None)

    return {
        "signals": {
            "today": len(signals_today),
            "this_week": len(signals_week),
            "delivered_this_week": len(delivered_week),
            "delivery_rate_pct": round(len(delivered_week) / len(signals_week) * 100, 1) if signals_week else None,
            "total_resolved": len(resolved),
            "live_wr_pct": round(len(wins) / len(resolved) * 100, 1) if resolved else None,
            "live_wr_ci": [lo, hi],
            "avg_ret_pct": round(sum(s.outcome_pct for s in resolved) / len(resolved), 3) if resolved else None,
        },
        "users": {
            "total_active": len(all_users),
            "paid": active_paid,
            "tiers": tier_counts,
        },
        "revenue": {"mrr_usd": mrr},
        "calibration": {"brier": brier, "v4_baseline": 0.2641},
    }


def _find_flagged(d: dict, prefix: str = "") -> list[dict]:
    """Recursively collect fields where flag=True."""
    flagged = []
    for k, v in d.items():
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            if v.get("flag"):
                flagged.append(
                    {
                        "metric": path,
                        "before": v.get("before"),
                        "after": v.get("after"),
                        "delta": v.get("delta"),
                        "delta_pct": v.get("delta_pct"),
                    }
                )
            else:
                flagged.extend(_find_flagged(v, path))
    return flagged


@router.get("/provider-reliability")
async def provider_reliability(db: AsyncSession = Depends(get_db), owner: User = Depends(_require_owner)):
    """
    TSYS-5d: Expose provider rate-limit budgets, health scorecards, and degradation states.
    """
    from models import ProviderHealthScorecard, ProviderTelemetry

    # Get all health scorecards
    scorecards = (await db.execute(select(ProviderHealthScorecard))).scalars().all()

    # Get recent telemetry records (e.g. last 20 records)
    telemetry = (
        (await db.execute(select(ProviderTelemetry).order_by(ProviderTelemetry.created_at.desc()).limit(20)))
        .scalars()
        .all()
    )

    return {
        "scorecards": [
            {
                "id": s.id,
                "provider": s.provider,
                "endpoint": s.endpoint,
                "latency_avg_ms": round(s.latency_avg_ms, 2),
                "error_rate": round(s.error_rate, 4),
                "stale_data_rate": round(s.stale_data_rate, 4),
                "schema_drift_count": s.schema_drift_count,
                "health_score": round(s.health_score, 2),
                "is_active": s.is_active,
                "last_updated": s.last_updated.isoformat() if s.last_updated else None,
            }
            for s in scorecards
        ],
        "telemetry": [
            {
                "id": t.id,
                "cycle_id": t.cycle_id,
                "provider": t.provider,
                "api_calls": t.api_calls,
                "cache_hits": t.cache_hits,
                "cache_misses": t.cache_misses,
                "quota_remaining": t.quota_remaining,
                "throttles": t.throttles,
                "fallback_usage": t.fallback_usage,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in telemetry
        ],
    }


# ── TSYS-10 Observability ─────────────────────────────────────────────────────


@router.get("/incident-timeline")
async def incident_timeline(
    limit: int = 100,
    severity: str | None = None,
    owner: User = Depends(_require_owner),
    db: AsyncSession = Depends(get_db),
):
    """TSYS-10a: recent system incidents (scan failures, provider degradations,
    metric-threshold breaches, etc.) newest-first."""
    from models import IncidentTimeline

    stmt = select(IncidentTimeline).order_by(IncidentTimeline.created_at.desc()).limit(min(limit, 500))
    if severity:
        stmt = stmt.where(IncidentTimeline.severity == severity)
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": r.id,
            "event_type": r.event_type,
            "severity": r.severity,
            "message": r.message,
            "details": r.details,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics(owner: User = Depends(_require_owner)):
    """TSYS-10c: export in-process metrics in Prometheus text exposition format."""
    from services.metrics import render_prometheus

    return render_prometheus()


@router.post("/check-alerts")
async def check_alerts(
    owner: User = Depends(_require_owner),
    db: AsyncSession = Depends(get_db),
):
    """TSYS-10d: evaluate metric alert thresholds; record incidents on breach."""
    from services.metrics import check_alert_thresholds

    breaches = await check_alert_thresholds(db)
    await db.commit()
    return {"breaches": breaches, "count": len(breaches)}


# ── TSYS-12 Data retention & schema hygiene ───────────────────────────────────


@router.get("/retention-rules")
async def retention_rules(owner: User = Depends(_require_owner)):
    """TSYS-12b: the per-table retention/anonymization policy registry."""
    from services.retention_svc import default_rules

    return default_rules()


@router.post("/retention/purge")
async def retention_purge(
    dry_run: bool = True,
    owner: User = Depends(_require_owner),
    db: AsyncSession = Depends(get_db),
):
    """TSYS-12b: count (dry_run) or delete expired rows in prunable tables."""
    from services.retention_svc import purge_expired

    report = await purge_expired(db, dry_run=dry_run)
    return {"dry_run": dry_run, "report": report}


@router.get("/index-audit")
async def index_audit(owner: User = Depends(_require_owner)):
    """TSYS-12c: verify hot-path columns are indexed. Returns missing indexes."""
    import models

    # (table, column) pairs that must be indexed for hot query paths.
    required = [
        ("signals", "created_at"),
        ("signals", "is_sent"),
        ("signal_deliveries", "user_id"),
        ("signal_deliveries", "signal_id"),
        ("broker_orders", "user_id"),
        ("broker_orders", "status"),
        ("broker_orders", "created_at"),
        ("action_audit_logs", "user_id"),
        ("provider_response_samples", "created_at"),
    ]
    tables = {m.__tablename__: m.__table__ for m in models.Base.__subclasses__() if hasattr(m, "__tablename__")}
    missing = []
    for table_name, column in required:
        tbl = tables.get(table_name)
        if tbl is None:
            missing.append({"table": table_name, "column": column, "reason": "table not found"})
            continue
        col = tbl.columns.get(column)
        indexed = bool(col is not None and col.index) or any(column in idx.columns for idx in tbl.indexes)
        if not indexed:
            missing.append({"table": table_name, "column": column, "reason": "no index"})
    return {"checked": len(required), "missing": missing, "ok": not missing}
