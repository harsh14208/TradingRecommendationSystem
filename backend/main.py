import asyncio
import logging
import logging.handlers
import os
import resource
from datetime import datetime, timedelta
from pathlib import Path

import certifi
import pytz

# ── Sentry ──────────────────────────────────────────────────────────────────
# Initialise as early as possible so import-time crashes are captured.
_sentry_dsn = os.environ.get("SENTRY_DSN", "").strip()
if _sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=_sentry_dsn,
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,  # 10% of requests profiled — adjust up/down by cost
        profiles_sample_rate=0.05,
        environment="production" if not os.environ.get("DEBUG") else "development",
        release=os.environ.get("GIT_SHA", "unknown"),
    )

# Raise the per-process open-file limit early so long-running scan cycles
# (which accumulate sockets + SQLite WAL handles) don't hit the OS default
# (256 on macOS, 1024 on Linux).  We request 65536; cap at the hard limit.
try:
    _soft, _hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    _target = min(_hard, 65536)
    if _target > _soft:
        resource.setrlimit(resource.RLIMIT_NOFILE, (_target, _hard))
except Exception:
    pass

import json as _json


class _StructuredFormatter(logging.Formatter):
    """BE-2: Emit JSON log lines when LOG_FORMAT=json (set in production env)."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return _json.dumps(payload)


_LOG_FORMAT = os.environ.get("LOG_FORMAT", "text").lower()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
if _LOG_FORMAT == "json":
    _json_fmt = _StructuredFormatter()
    for _h in logging.root.handlers:
        _h.setFormatter(_json_fmt)

# ── Rotating file handler for scanner logs (DISC-2) ──────────────────────────
# Prevents Alpaca WS reconnect spam from drowning scanner logs in stderr.log.
_log_dir = Path(__file__).parent / "logs"
_log_dir.mkdir(exist_ok=True)
_scanner_handler = logging.handlers.RotatingFileHandler(
    _log_dir / "scanner.log",
    maxBytes=10 * 1024 * 1024,  # 10 MB per file
    backupCount=5,
)
_scanner_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(name)s  %(message)s"))
logging.getLogger("scanner").addHandler(_scanner_handler)

# Silence noisy third-party loggers
logging.getLogger("yfinance").setLevel(logging.WARNING)
logging.getLogger("peewee").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("signal.trade")

# Point both requests (yfinance) and ssl (aiohttp) at the certifi bundle.
# Must happen before any network library is imported.
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
os.environ.setdefault("CURL_CA_BUNDLE", certifi.where())

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

from config import get_settings
from database import init_db
from models import User
from routers.accuracy import router as accuracy_router
from routers.admin import router as admin_router
from routers.broker import router as broker_router
from routers.me import router as me_router
from routers.auth import router as auth_router
from routers.billing import router as billing_router
from routers.delivery_router import router as delivery_router
from routers.market import router as market_router
from routers.ml import router as ml_router
from routers.oauth import router as oauth_router
from routers.paper_router import router as paper_router
from routers.price_alerts import router as price_alerts_router
from routers.public import router as public_router
from routers.quotes import router as quotes_router
from routers.screener import router as screener_router
from routers.settings_router import router as settings_router
from routers.signal_alerts import router as signal_alerts_router
from routers.signals import router as signals_router
from routers.sources import router as sources_router
from routers.telegram_webhook import router as telegram_webhook_router
from routers.watchlist_router import router as watchlist_router
from routers.websocket_router import manager
from routers.websocket_router import router as ws_router
from services import alpaca_ws
from services.auth_svc import get_current_user
from services.scanner import _alert_telegram, _data_quality, get_scan_status, run_scan

ROOT = Path(__file__).parent.parent  # project root (one level up from backend/)
settings = get_settings()

# ── PostgreSQL production warning ─────────────────────────────────────────────
from database import _IS_POSTGRES as _USING_POSTGRES

if not _USING_POSTGRES and settings.app_url.startswith("https"):
    log.warning(
        "⚠️  PRODUCTION RISK: Running SQLite in a deployed HTTPS environment. "
        "SQLite WAL mode serialises all writes — SQLITE_BUSY errors are likely "
        "under concurrent load (>50 users or multiple scanner cycles). "
        "Set DATABASE_URL=postgresql://... to migrate. "
        "Run: python3 scripts/check_postgres.py"
    )
elif not _USING_POSTGRES:
    log.info("[db] SQLite (dev mode). Set DATABASE_URL=postgresql://... for production.")
else:
    log.info("[db] PostgreSQL — production-ready concurrency.")

# ── Security startup checks ────────────────────────────────────────────────────
_is_prod = settings.app_url.startswith("https")

if _is_prod and not settings.jwt_secret:
    raise RuntimeError(
        "FATAL: JWT_SECRET not set — using deterministic dev secret in production. "
        "Any attacker who reads the source can forge valid JWTs for any user. "
        "Set JWT_SECRET=<64+ random chars> in .env immediately."
    )

if _is_prod and not settings.stripe_webhook_secret:
    log.critical(
        "🔴 CRITICAL: STRIPE_WEBHOOK_SECRET not configured in production. "
        "Stripe webhook endpoint will reject all events (500). "
        "Register the webhook in the Stripe Dashboard and add whsec_... to .env."
    )

if _is_prod and not settings.owner_password:
    log.critical(
        "🔴 CRITICAL: OWNER_PASSWORD not set — owner account uses empty password. "
        "Set OWNER_PASSWORD=<16+ chars> in .env before first paid signup."
    )

_scan_task: asyncio.Task | None = None
# Supervised background tasks: name → (task, coroutine_factory, started_at)
_bg_tasks: dict[str, dict] = {}


_scan_fail_streak = 0


async def _periodic_scan():
    """Continuous market-hours scanner (Mon–Fri, 09:30–16:00 ET).

    Fires at 09:30 sharp on market open, then every scan_interval_min minutes
    until close. One final scan fires at 16:02 to catch any close-of-day prints.
    Sleeps overnight and on weekends until the next 09:30 open.

    Legacy fixed-slot behaviour is preserved when scan_interval_min == 0 and
    scan_times is non-empty in settings.
    """
    global _scan_fail_streak
    ET = pytz.timezone("America/New_York")

    def _is_trading_day(dt: datetime) -> bool:
        return dt.weekday() < 5  # Mon–Fri (basic; no holiday calendar)

    def _next_market_open() -> datetime:
        now = datetime.now(ET)
        for offset in range(7):
            candidate = now + timedelta(days=offset)
            if not _is_trading_day(candidate):
                continue
            open_dt = candidate.replace(hour=9, minute=30, second=0, microsecond=0)
            if open_dt > now + timedelta(seconds=10):
                return open_dt
        return now + timedelta(hours=24)  # fallback

    # ── Legacy fixed-slot path (scan_interval_min == 0) ──────────────────────
    cfg = get_settings()
    if getattr(cfg, "scan_interval_min", 15) == 0 and cfg.scan_times.strip():

        def _next_fire() -> datetime:
            slots: list[tuple[int, int]] = []
            for part in cfg.scan_times.split(","):
                part = part.strip()
                if not part:
                    continue
                try:
                    h, m = part.split(":")
                    slots.append((int(h), int(m)))
                except ValueError:
                    pass
            if not slots:
                slots = [(9, 30), (11, 0), (13, 0), (14, 30), (15, 45)]
            slots.sort()
            now = datetime.now(ET)
            for day_offset in range(7):
                candidate_day = now + timedelta(days=day_offset)
                if candidate_day.weekday() >= 5:
                    continue
                for h, m in slots:
                    fire = candidate_day.replace(hour=h, minute=m, second=0, microsecond=0)
                    if fire > now + timedelta(seconds=5):
                        return fire
            return now + timedelta(hours=24)

        while True:
            try:
                fire_at = _next_fire()
            except Exception as e:
                log.warning("[scanner] _next_fire failed (%s: %s); retrying in 60s", type(e).__name__, e)
                await asyncio.sleep(60)
                continue
            wait_s = (fire_at - datetime.now(ET)).total_seconds()
            log.info("[scanner] next fixed-slot scan: %s ET (%.0fs)", fire_at.strftime("%a %H:%M"), wait_s)
            await asyncio.sleep(max(0, wait_s))
            try:
                await run_scan(broadcast_fn=manager.broadcast)
                _scan_fail_streak = 0
            except asyncio.CancelledError:
                raise
            except BaseException as e:
                _scan_fail_streak += 1
                print(f"[scanner] periodic error (streak {_scan_fail_streak}): {type(e).__name__}: {e}")
                if _scan_fail_streak == 1 or _scan_fail_streak % 5 == 0:
                    await _alert_telegram(
                        f"⚠️ Scanner error (streak {_scan_fail_streak})\n{type(e).__name__}: {str(e)[:200]}"
                    )
            await asyncio.sleep(60)
        return  # unreachable but satisfies linter

    # ── Continuous market-hours path ──────────────────────────────────────────
    while True:
        now = datetime.now(ET)
        interval_min = getattr(get_settings(), "scan_interval_min", 15) or 15

        if not _is_trading_day(now):
            next_open = _next_market_open()
            wait_s = (next_open - now).total_seconds()
            log.info("[scanner] weekend — sleeping until %s ET (%.1fh)", next_open.strftime("%a %H:%M"), wait_s / 3600)
            await asyncio.sleep(wait_s)
            continue

        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        post_close = now.replace(hour=16, minute=2, second=0, microsecond=0)

        if now < market_open:
            wait_s = (market_open - now).total_seconds()
            log.info("[scanner] pre-market — sleeping %.1fmin until 09:30 ET open", wait_s / 60)
            await asyncio.sleep(wait_s)
            continue

        if now > post_close:
            next_open = _next_market_open()
            wait_s = (next_open - now).total_seconds()
            log.info(
                "[scanner] after-hours — sleeping until %s ET (%.1fh)", next_open.strftime("%a %H:%M"), wait_s / 3600
            )
            await asyncio.sleep(wait_s)
            continue

        # Fire scan
        log.info("[scanner] firing continuous scan at %s ET", now.strftime("%H:%M:%S"))
        try:
            await run_scan(broadcast_fn=manager.broadcast)
            _scan_fail_streak = 0
        except asyncio.CancelledError:
            raise
        except BaseException as e:
            _scan_fail_streak += 1
            print(f"[scanner] error (streak {_scan_fail_streak}): {type(e).__name__}: {e}")
            if _scan_fail_streak == 1 or _scan_fail_streak % 5 == 0:
                await _alert_telegram(
                    f"⚠️ Scanner error (streak {_scan_fail_streak})\n{type(e).__name__}: {str(e)[:200]}"
                )

        # After close: one final scan at 16:02, then EOD batch at 16:10, then sleep
        now_after = datetime.now(ET)
        if now_after >= market_close:
            if now_after < post_close:
                await asyncio.sleep((post_close - now_after).total_seconds())
                try:
                    await run_scan(broadcast_fn=manager.broadcast)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    log.warning("[scanner] post-close scan failed: %s: %s", type(e).__name__, e)

            # EOD batch: deliver any BUY/SELL that weren't sent in real-time
            eod_batch_time = now_after.replace(hour=16, minute=10, second=0, microsecond=0)
            wait_eod = (eod_batch_time - datetime.now(ET)).total_seconds()
            if wait_eod > 0:
                await asyncio.sleep(wait_eod)
            try:
                from services.scanner import eod_batch_send

                await eod_batch_send()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.warning("[scanner] EOD batch send failed: %s: %s", type(e).__name__, e)

            next_open = _next_market_open()
            wait_s = (_next_market_open() - datetime.now(ET)).total_seconds()
            log.info("[scanner] EOD batch done — sleeping until %s ET", next_open.strftime("%a %H:%M"))
            await asyncio.sleep(max(0, wait_s))
        else:
            await asyncio.sleep(interval_min * 60)


async def _nightly_signal_cleanup():
    """Deactivate signals that have passed their expires_at timestamp. Runs at 4:15am ET daily."""
    ET = pytz.timezone("America/New_York")
    while True:
        now_et = datetime.now(ET)
        target = now_et.replace(hour=4, minute=15, second=0, microsecond=0)
        if now_et >= target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now_et).total_seconds())
        try:
            from datetime import timezone as _tz

            from database import AsyncSessionLocal
            from models import Signal
            from sqlalchemy import select, update

            cutoff = datetime.now(_tz.utc).replace(tzinfo=None)
            async with AsyncSessionLocal() as db:
                # 1. Deactivate expired signals
                result = await db.execute(
                    update(Signal)
                    .where(Signal.is_active == True)
                    .where(Signal.expires_at <= cutoff)
                    .values(is_active=False)
                )
                expired_count = result.rowcount

                # 2. Confidence decay — active signals older than 3 days lose
                #    3pp per additional day beyond day 3, capped at −15pp total.
                #    An RSI oversold from 4 days ago is no longer actionable.
                day3_cutoff = cutoff - timedelta(days=3)
                stale_rows = (
                    (
                        await db.execute(
                            select(Signal)
                            .where(Signal.is_active == True)
                            .where(Signal.outcome_pct.is_(None))  # not yet resolved
                            .where(Signal.created_at <= day3_cutoff)
                            .where(Signal.action.in_(["BUY", "SELL"]))
                        )
                    )
                    .scalars()
                    .all()
                )

                decayed = 0
                for sig in stale_rows:
                    age_days = (cutoff - sig.created_at).total_seconds() / 86400
                    extra_days = max(0, age_days - 3)
                    decay_pp = min(15.0, extra_days * 3.0)
                    new_conf = round(max(35.0, sig.confidence - decay_pp), 1)
                    if new_conf != sig.confidence:
                        sig.confidence = new_conf
                        decayed += 1

                await db.commit()
            log.info(f"[cleanup] deactivated {expired_count} expired | decayed {decayed} stale signals")
        except Exception as e:
            log.warning(f"[cleanup] nightly cleanup failed: {e}")


async def _nightly_stripe_reconciliation():
    """Run Stripe subscription reconciliation daily at 4:30am ET (TSYS-2a)."""
    import pytz

    ET = pytz.timezone("America/New_York")
    while True:
        now_et = datetime.now(ET)
        target = now_et.replace(hour=4, minute=30, second=0, microsecond=0)
        if now_et >= target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now_et).total_seconds())
        try:
            from database import AsyncSessionLocal
            from services.billing_reconciliation import reconcile_stripe_subscriptions

            async with AsyncSessionLocal() as db:
                await reconcile_stripe_subscriptions(db)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.warning(
                "[main] Nightly Stripe reconciliation failed: %s: %s",
                type(e).__name__,
                e,
            )


async def _nightly_outcome_resolution():
    """
    Resolve pending outcomes + MAE/MFE + refresh calibration nightly at 2:00am ET.

    Runs AFTER markets close (and after the 4:15am cleanup) to ensure all intraday
    prices are final.  Without this, calibration.json goes stale, adaptive weights
    freeze, and the Platt correction stops improving.
    """
    ET = pytz.timezone("America/New_York")
    while True:
        now_et = datetime.now(ET)
        target = now_et.replace(hour=2, minute=0, second=0, microsecond=0)
        if now_et >= target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now_et).total_seconds())
        try:
            log.info("[nightly] running outcome resolution + calibration refresh…")
            # Reuse validate_predictions logic without starting a separate process
            import os
            import sys

            sys.path.insert(0, os.path.dirname(__file__))
            from validate_predictions import fix_phantom_wins, resolve_mae_mfe, resolve_outcomes

            updated = await resolve_outcomes()
            mae_updated = await resolve_mae_mfe()
            phantom_fixed = await fix_phantom_wins(apply=True)
            log.info(
                f"[nightly] resolved {updated} outcomes, {mae_updated} MAE/MFE records, "
                f"{phantom_fixed} phantom wins corrected"
            )
            # Refresh Platt + isotonic calibration now that outcomes are up-to-date
            from services.calibration import run_calibration

            cal = await run_calibration()
            log.info(f"[nightly] calibration refreshed — {len(cal)} bins")
            try:
                from routers.signals import clear_analytics_cache

                clear_analytics_cache()
                log.info("[nightly] analytics cache cleared")
            except Exception as ce:
                log.warning(f"[nightly] failed to clear analytics cache: {ce}")
            # Refresh Polygon short-volume alt-data for the live watchlist so the
            # SVR gate stays current and short_volume_daily accrues for forward
            # re-validation of the alpha (currently provisional at N=25).
            try:
                from sqlalchemy import select as _sel

                from database import AsyncSessionLocal as _ASL
                from models import WatchlistItem
                from scripts.backfill_short_volume import backfill_ticker

                async with _ASL() as _svdb:
                    _wl = (
                        (await _svdb.execute(_sel(WatchlistItem.ticker).where(WatchlistItem.is_active.is_(True))))
                        .scalars()
                        .all()
                    )
                    _sv_rows = 0
                    for _t in _wl:
                        try:
                            _sv_rows += await backfill_ticker(_svdb, _t)
                        except Exception:
                            await _svdb.rollback()
                log.info(
                    f"[nightly] short-volume refreshed for {len(_wl)} watchlist tickers ({_sv_rows} rows upserted)"
                )
            except Exception as _sve:
                log.warning(f"[nightly] short-volume refresh failed: {_sve}")
        except Exception as e:
            log.warning(f"[nightly] outcome resolution failed: {e}")


async def _nightly_cboe_options_snapshot():
    """§110 — Snapshot CBOE delayed options chain into options_chain_daily at 6:30pm ET.

    Runs after market close once CBOE's delayed quotes have accumulated the full
    session's volume and open interest. The table accrues the self-grown IV-rank
    series that later forward tests will need.
    """
    ET = pytz.timezone("America/New_York")
    while True:
        now_et = datetime.now(ET)
        target = now_et.replace(hour=18, minute=30, second=0, microsecond=0)
        if now_et >= target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now_et).total_seconds())
        try:
            from sqlalchemy import select as _sel

            from database import AsyncSessionLocal as _ASL
            from models import WatchlistItem
            from scripts.snapshot_cboe_options import snapshot_ticker

            async with _ASL() as _odb:
                _wl = (
                    (await _odb.execute(_sel(WatchlistItem.ticker).where(WatchlistItem.is_active.is_(True))))
                    .scalars()
                    .all()
                )
                _ok = 0
                _empty = 0
                for _t in _wl:
                    try:
                        _success = await snapshot_ticker(_odb, _t, __import__("datetime").date.today())
                    except Exception:
                        await _odb.rollback()
                        _empty += 1
                        continue
                    if _success:
                        _ok += 1
                    else:
                        _empty += 1
                log.info(
                    f"[nightly] CBOE options snapshot complete: {_ok} populated, {_empty} empty for {len(_wl)} tickers"
                )
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.warning("[nightly] CBOE options snapshot failed: %s: %s", type(e).__name__, e)


async def _intraday_stop_monitor():
    """
    Check active sent signals for stop/target hits every 30 minutes during market hours.
    Fires Telegram notification when a stop or target is breached and deactivates the signal.
    """
    from services.stop_monitor import check_stop_targets_and_notify

    ET = pytz.timezone("America/New_York")
    # Startup delay — let the first scan cycle complete before checking stops
    await asyncio.sleep(120)
    while True:
        now_et = datetime.now(ET)
        is_market_hours = (
            now_et.weekday() < 5
            and now_et.time() >= __import__("datetime").time(9, 30)
            and now_et.time() <= __import__("datetime").time(16, 15)
        )
        if is_market_hours:
            try:
                await check_stop_targets_and_notify()
            except Exception as e:
                log.warning(f"[stop_monitor] failed: {e}")
        await asyncio.sleep(1800)  # 30-minute interval


async def _nightly_reflection_learning():
    """
    Automated Reflection & Learning — runs nightly at 4:30am ET alongside cleanup.
    Reads resolved LOSS signals from the last 7 days, asks the local LLM why each
    failed, and stores the lesson in the vector store so future scans can avoid
    the same mistake.  Gracefully skips if LLM is unavailable.
    """
    ET = pytz.timezone("America/New_York")
    while True:
        now_et = datetime.now(ET)
        target = now_et.replace(hour=4, minute=30, second=0, microsecond=0)
        if now_et >= target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now_et).total_seconds())
        try:
            from services.local_llm import get_llm_client

            llm = get_llm_client()
            if not llm:
                continue  # LLM not available — skip reflection

            from datetime import timezone as _tz

            from database import AsyncSessionLocal
            from models import Signal
            from services.vector_store import store_reflection
            from sqlalchemy import select

            cutoff = datetime.now(_tz.utc).replace(tzinfo=None) - timedelta(days=7)
            async with AsyncSessionLocal() as db:
                losses = (
                    (
                        await db.execute(
                            select(Signal)
                            .where(Signal.outcome_pct.isnot(None))
                            .where(Signal.outcome_pct <= 0)
                            .where(Signal.is_sent == True)
                            .where(Signal.created_at >= cutoff)
                            .order_by(Signal.created_at.desc())
                            .limit(10)
                        )
                    )
                    .scalars()
                    .all()
                )

            reflected = 0
            for sig in losses:
                try:
                    rationale_heads = (
                        "; ".join(r.get("head", "") for r in (sig.rationale or [])[:5] if r.get("head"))
                        or "no rationale stored"
                    )
                    prompt = (
                        f"Signal: {sig.action} {sig.ticker} at {sig.confidence:.0f}% confidence. "
                        f"Outcome: {sig.outcome_pct:+.1f}% (LOSS). "
                        f"Key signals that fired: {rationale_heads}. "
                        f"In 2 sentences: why did this signal likely fail, and what should be "
                        f"checked next time before acting on a similar setup?"
                    )
                    lesson = llm.generate(
                        prompt,
                        system_prompt=(
                            "You are a quantitative trading risk analyst. Be specific, concise, and actionable."
                        ),
                    )
                    if lesson and len(lesson) > 30:
                        features = {
                            "confidence": sig.confidence / 100,
                            "outcome_pct": sig.outcome_pct,
                        }
                        store_reflection(sig.ticker, sig.action, sig.outcome_pct, features, lesson[:500])
                        reflected += 1
                except Exception:
                    pass

            if reflected:
                log.info(f"[reflection] Stored {reflected} loss lessons in vector store")
        except Exception as e:
            log.debug(f"[reflection] nightly reflection failed: {e}")


async def _weekly_ml_retrain():
    """Retrain XGBoost model Sunday 11:00am ET — runs after factor mining."""
    ET = pytz.timezone("America/New_York")
    await asyncio.sleep(3600)  # offset: start checking 1 hour after boot
    while True:
        now_et = datetime.now(ET)
        days_until_sunday = (6 - now_et.weekday()) % 7
        if days_until_sunday == 0 and now_et.hour >= 11:
            days_until_sunday = 7
        next_run = now_et.replace(hour=11, minute=0, second=0, microsecond=0)
        next_run = next_run + timedelta(days=days_until_sunday)
        await asyncio.sleep((next_run - now_et).total_seconds())
        try:
            from services.signal_ml import train_model

            result = await asyncio.to_thread(train_model)
            if result:
                log.info(
                    f"[ml] retrain OK: OOS AUC={result.get('oos_auc') or '?'}  n_train={result.get('n_train', '?')}"
                )
            else:
                log.info("[ml] retrain skipped (insufficient resolved signals).")
        except Exception as e:
            log.warning(f"[ml] retrain failed: {e}")


async def _weekly_factor_mining():
    """Re-mine factor weights every Sunday after the weekly digest runs."""
    ET = pytz.timezone("America/New_York")
    # Stagger 2 hours after the digest (10am ET Sunday)
    await asyncio.sleep(7200)  # let the app warm up first
    while True:
        now_et = datetime.now(ET)
        days_until_sunday = (6 - now_et.weekday()) % 7
        if days_until_sunday == 0 and now_et.hour >= 10:
            days_until_sunday = 7
        next_run = now_et.replace(hour=10, minute=0, second=0, microsecond=0)
        next_run = next_run + timedelta(days=days_until_sunday)
        await asyncio.sleep((next_run - now_et).total_seconds())
        try:
            from services.factor_miner import run_factor_mining

            result = await run_factor_mining()
            n = result.get("combinations_tested", 0)
            promoted = result.get("promoted_count", 0)
            log.info(f"[factor_miner] Weekly run done: {n} combos tested, {promoted} promoted.")
        except Exception as e:
            log.warning(f"[factor_miner] weekly run failed: {e}")
        try:
            from services.calibration import run_calibration

            await run_calibration()
        except Exception as e:
            log.warning(f"[calibration] weekly run failed: {e}")


async def _run_weekly_digest(force: bool = False):
    ET = pytz.timezone("America/New_York")
    try:
        from database import AsyncSessionLocal
        from models import BackgroundJobRun, Signal
        from sqlalchemy import select

        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)

        # ── Once-per-week idempotency guard ──────────────────────────────────────
        # The digest must fire at most once per week no matter how many times this
        # coroutine is reached (server restarts, an accidental admin click, a future
        # cron). We persist a marker row on every successful send and skip if one
        # was written in the last 6 days. force=True (manual admin trigger) bypasses
        # the read check but still records the marker so it shifts the weekly window.
        digest_week = now.strftime("%Y-%W")
        if not force:
            async with AsyncSessionLocal() as db_guard:
                already = (
                    await db_guard.execute(
                        select(BackgroundJobRun.id)
                        .where(BackgroundJobRun.job_name == "weekly_digest_sent")
                        .where(BackgroundJobRun.start_time >= now - timedelta(days=6))
                        .limit(1)
                    )
                ).first()
            if already:
                log.info("[digest] already sent within the last 6 days — skipping (weekly idempotency guard)")
                return

        # Atomic marker insert: if another instance already inserted this week,
        # the unique constraint on (job_name, digest_week) will raise IntegrityError
        # and we skip sending. This closes the TOCTOU race when the distributed
        # lock TTL is shorter than the sleep period.
        try:
            async with AsyncSessionLocal() as db_lock:
                db_lock.add(
                    BackgroundJobRun(
                        job_name="weekly_digest_sent",
                        start_time=now,
                        end_time=datetime.utcnow(),
                        status="completed",
                        digest_week=digest_week,
                    )
                )
                await db_lock.commit()
        except Exception:
            log.info("[digest] weekly marker already present for this week — skipping (atomic guard)")
            return

        async with AsyncSessionLocal() as db:
            sent_this_week = (
                (await db.execute(select(Signal).where(Signal.is_sent == True).where(Signal.sent_at >= week_ago)))
                .scalars()
                .all()
            )

            resolved_past_week = (
                (
                    await db.execute(
                        select(Signal)
                        .where(Signal.is_sent == True)
                        .where(Signal.sent_at >= two_weeks_ago)
                        .where(Signal.sent_at < week_ago)
                    )
                )
                .scalars()
                .all()
            )

        def get_best_outcome(sig):
            for f in ("outcome_pct", "outcome_14d", "outcome_3d", "outcome_1d"):
                v = getattr(sig, f, None)
                if v is not None:
                    return v
            return None

        resolved_with_outcomes = [
            (r, get_best_outcome(r)) for r in resolved_past_week if get_best_outcome(r) is not None
        ]
        sent = len(sent_this_week)
        resolved_count = len(resolved_with_outcomes)
        wins = [r for r, out in resolved_with_outcomes if out > 0]
        win_rate = round(len(wins) / resolved_count * 100) if resolved_count else None
        avg_ret = round(sum(out for r, out in resolved_with_outcomes) / resolved_count, 2) if resolved_count else None
        best_tup = max(resolved_with_outcomes, key=lambda x: x[1]) if resolved_count else None
        worst_tup = min(resolved_with_outcomes, key=lambda x: x[1]) if resolved_count else None
        best, best_ret = best_tup if best_tup else (None, None)
        worst, worst_ret = worst_tup if worst_tup else (None, None)

        # Fetch SPY benchmark for comparison
        import yfinance as yf

        spy_ret = None
        try:

            def _fetch_spy():
                return yf.Ticker("SPY").history(period="5d")

            spy_data = await asyncio.to_thread(_fetch_spy)
            if not spy_data.empty and len(spy_data) >= 2:
                spy_ret = (spy_data["Close"].iloc[-1] / spy_data["Close"].iloc[0] - 1) * 100
        except Exception:
            pass

        lines = [
            "📊 *Signal.Trade — Weekly Digest*",
            f"Week ending {datetime.now(ET).strftime('%b %d, %Y')}",
            "———",
            f"📤 Signals sent: *{sent}*",
        ]
        if win_rate is not None:
            lines.append(f"🎯 Win rate: *{win_rate}%* ({len(wins)}/{resolved_count} resolved)")
        if avg_ret is not None:
            spy_str = f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else ""
            lines.append(f"📈 Avg return: *{avg_ret:+.2f}%*{spy_str}")
        if best:
            lines.append(f"🏆 Best: *{best.ticker}* {best.action} +{best_ret:.1f}%")
        if worst:
            lines.append(f"💔 Worst: *{worst.ticker}* {worst.action} {worst_ret:.1f}%")
        if not resolved_count:
            lines.append("_No resolved outcomes yet — check back next week._")

        # ── Telegram and Email digest to owner + all active subscribers ──────────────
        try:
            import aiohttp
            from config import TIERS, get_settings
            from models import User
            from services.email_svc import send_weekly_digest
            from sqlalchemy import select as _sel

            week_ending_str = datetime.now(ET).strftime("%b %d, %Y")
            s = get_settings()

            async with AsyncSessionLocal() as db2:
                users = (await db2.execute(_sel(User).where(User.is_active == True))).scalars().all()

            recipients = [u.email for u in users if u.is_owner or u.subscription_status == "active"]

            recipients_tg = [
                u.telegram_chat_id
                for u in users
                if u.telegram_chat_id
                and (
                    u.is_owner
                    or (u.subscription_status == "active" and TIERS.index(u.subscription_tier) >= TIERS.index("basic"))
                )
            ]

            # Send to Telegram subscribers
            if s.telegram_bot_token:
                url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
                message_text = "\n".join(lines)
                async with aiohttp.ClientSession() as session:
                    # Fallback to owner's .env chat_id if no subscribers have linked Telegram
                    chats_to_notify = set(recipients_tg)
                    if not chats_to_notify and s.telegram_chat_id:
                        chats_to_notify.add(s.telegram_chat_id)

                    if not chats_to_notify:
                        log.warning(
                            "[digest] No Telegram recipients — owner has no telegram_chat_id linked and TELEGRAM_CHAT_ID env var is not set"
                        )

                    for chat_id in chats_to_notify:
                        try:
                            resp = await session.post(
                                url,
                                json={
                                    "chat_id": chat_id,
                                    "text": message_text,
                                    "parse_mode": "Markdown",
                                },
                            )
                            result = await resp.json()
                            if not result.get("ok"):
                                # Retry without Markdown if parse error
                                log.warning(
                                    f"[digest] telegram to {chat_id} rejected (parse_mode=Markdown): {result.get('description')} — retrying plain"
                                )
                                resp2 = await session.post(
                                    url,
                                    json={"chat_id": chat_id, "text": message_text},
                                )
                                result2 = await resp2.json()
                                if not result2.get("ok"):
                                    log.warning(
                                        f"[digest] telegram to {chat_id} failed (plain): {result2.get('description')}"
                                    )
                        except Exception as e_tg:
                            log.warning(f"[digest] telegram to {chat_id} failed: {e_tg}")
                log.info(f"[digest] Weekly digest sent via Telegram to {len(chats_to_notify)} chats")

            for email in recipients:
                try:
                    await send_weekly_digest(
                        to=email,
                        week_ending=week_ending_str,
                        sent=sent,
                        win_rate=win_rate,
                        wins=len(wins),
                        resolved=resolved_count,
                        avg_ret=avg_ret,
                        best_ticker=best.ticker if best else None,
                        best_ret=best_ret,
                        worst_ticker=worst.ticker if worst else None,
                        worst_ret=worst_ret,
                        spy_ret=spy_ret,
                    )
                except Exception as e_mail:
                    log.warning(f"[digest] email to {email} failed: {e_mail}")
        except Exception as e_email:
            log.warning(f"[digest] email digest error: {e_email}")

        # ── Auto performance snapshot (weekly baseline) ───────────────────────
        try:
            from scripts.calc_tbd_metrics import analyze_db as _metrics_analyze

            week_label = datetime.now(ET).strftime("weekly-%Y-%m-%d")
            await _metrics_analyze(snapshot_tag=week_label)
            log.info(f"[digest] performance snapshot saved: {week_label}")
        except Exception as e_snap:
            log.warning(f"[digest] snapshot failed (non-critical): {e_snap}")

    except Exception as e:
        log.error(f"[digest] fatal error in weekly digest: {e}", exc_info=True)


async def _weekly_digest():
    """Send a Sunday morning Telegram summary of the week's signals and win rate."""
    ET = pytz.timezone("America/New_York")
    while True:
        now_et = datetime.now(ET)
        # Wait until next Sunday 08:00 ET
        days_until_sunday = (6 - now_et.weekday()) % 7
        if days_until_sunday == 0 and now_et.hour >= 8:
            days_until_sunday = 7  # already past this Sunday's 8am
        next_sunday = now_et.replace(hour=8, minute=0, second=0, microsecond=0)
        next_sunday = next_sunday + timedelta(days=days_until_sunday)
        wait_secs = (next_sunday - now_et).total_seconds()
        await asyncio.sleep(wait_secs)
        await _run_weekly_digest()


async def _ensure_default_watchlist():
    """
    Seed the watchlist with ~200 tickers on first startup (or whenever fewer than
    20 are present, to recover from an accidental wipe).

    Organised into five thematic tiers:
      1. Mega-cap / S&P 100 core
      2. AI infrastructure & semiconductors (second-wave)
      3. Industrial rotation, commodities, real assets
      4. High-growth software / next-gen tech
      5. Leveraged & inverse-leveraged ETFs (3× and 2×)
    """
    DEFAULT_TICKERS: list[str] = [
        # ── Mega-cap / S&P 100 core ──────────────────────────────────────────
        "AAPL",
        "MSFT",
        "NVDA",
        "AMZN",
        "GOOGL",
        "META",
        "TSLA",
        "BRK-B",
        "AVGO",
        "JPM",
        "LLY",
        "V",
        "UNH",
        "XOM",
        "MA",
        "COST",
        "HD",
        "PG",
        "JNJ",
        "WMT",
        "BAC",
        "ABBV",
        "CRM",
        "AMD",
        "NFLX",
        "KO",
        "ACN",
        "MRK",
        "CVX",
        "TMO",
        "ORCL",
        "WFC",
        "ABT",
        "CSCO",
        "AXP",
        "BX",
        "MCD",
        "PEP",
        "PM",
        "GE",
        "INTU",
        "CAT",
        "QCOM",
        "GS",
        "TXN",
        "NOW",
        "IBM",
        "MS",
        "LIN",
        "DHR",
        "NEE",
        "RTX",
        "UNP",
        "HON",
        "SYK",
        "AMGN",
        "BMY",
        "UBER",
        "AMAT",
        "UPS",
        "T",
        "PANW",
        "LOW",
        "BKNG",
        "DE",
        "MDT",
        "VRTX",
        "LMT",
        "MU",
        "C",
        "REGN",
        "SBUX",
        "BA",
        "NKE",
        "CVS",
        "ISRG",
        "PLD",
        "GILD",
        "SO",
        "TJX",
        "MMC",
        "ETN",
        "CME",
        "CI",
        "BSX",
        "PGR",
        "AON",
        "MCO",
        "HCA",
        "GM",
        "SNOW",
        "PLTR",
        "MO",
        "TGT",
        "GD",
        "CB",
        "AIG",
        "COF",
        "SPGI",
        "ZTS",
        # ── Established tech & semi ──────────────────────────────────────────
        "SMCI",
        "ARM",
        "MRVL",
        "KLAC",
        "LRCX",
        "ADI",
        "CDNS",
        "SNPS",
        "ICE",
        "ADP",
        # ── AI Infrastructure (second-wave): FPGAs, packaging, optics, storage
        "ALTR",
        "AMKR",
        "COHR",
        "LATT",
        "POWI",
        "PSTG",
        "KEYS",
        # ── Industrial rotation & infrastructure ─────────────────────────────
        "PWR",
        "TT",
        "URI",
        "AME",
        "EMR",
        "ITW",
        "APH",
        # ── Commodities / real assets ────────────────────────────────────────
        "FCX",
        "SCCO",
        "HBM",
        "AEM",
        "NEM",
        "GLD",
        "GDX",
        "GDXJ",
        "SLV",
        "SIL",
        "COPX",
        "PALL",
        "PPLT",
        "SLB",
        "EOG",
        # ── Software / next-gen tech ─────────────────────────────────────────
        "MDB",
        "DDOG",
        "NET",
        # ── Broad market & sector ETFs ───────────────────────────────────────
        "SPY",
        "QQQ",
        "IWM",
        "TQQQ",
        "XLK",
        "XLF",
        "XLE",
        "XLI",
        "XLV",
        "XLC",
        "XLP",
        "XLRE",
        "XLU",
        "XLB",
        # ── 3× Bull leveraged ETFs ───────────────────────────────────────────
        "UPRO",
        "SPXL",
        "SOXL",
        "TECL",
        "FAS",
        "TNA",
        "LABU",
        "WEBL",
        "FNGU",
        "NAIL",
        "DPST",
        "YINN",
        "DRN",
        "TMF",
        "HIBL",
        "MIDU",
        "GUSH",
        "NUGT",
        "JNUG",
        # ── 3× Bear / inverse leveraged ETFs ────────────────────────────────
        "SQQQ",
        "SPXS",
        "SPXU",
        "SOXS",
        "TECS",
        "FAZ",
        "TZA",
        "LABD",
        "FNGD",
        "YANG",
        "DRV",
        "TMV",
        "HIBS",
        "SRTY",
        "DRIP",
        "DUST",
        "JDST",
        # ── 2× leveraged (popular liquid pairs) ─────────────────────────────
        "SSO",
        "SDS",
        "QLD",
        "QID",
        "UCO",
        "SCO",
        "ROM",
        "UWM",
        "TWM",
        # ── Previously-active custom ─────────────────────────────────────────
        "BLK",
        "ELV",
        "EBAY",
        "PNC",
        "USB",
        "WM",
    ]

    try:
        from database import AsyncSessionLocal
        from models import WatchlistItem
        from sqlalchemy import func, select

        async with AsyncSessionLocal() as db:
            existing_count = (
                await db.execute(select(func.count()).select_from(WatchlistItem).where(WatchlistItem.is_active == True))
            ).scalar_one()

            if existing_count >= 20:
                return  # watchlist already populated — don't overwrite user edits

            existing_tickers = set(r.ticker for r in (await db.execute(select(WatchlistItem.ticker))).scalars().all())

            added = 0
            for ticker in DEFAULT_TICKERS:
                if ticker not in existing_tickers:
                    db.add(WatchlistItem(ticker=ticker, company=ticker, is_active=True))
                    existing_tickers.add(ticker)
                    added += 1

            if added:
                await db.commit()
                log.info(f"[startup] default watchlist seeded: {added} tickers added ({existing_count + added} total)")
    except Exception as e:
        log.warning(f"[startup] default watchlist seed failed: {e}")


async def _ensure_owner_account():
    """Create the owner account on first startup if OWNER_EMAIL / OWNER_PASSWORD are set."""
    s = get_settings()
    if not s.owner_email or not s.owner_password:
        return
    from database import AsyncSessionLocal
    from models import User
    from services.auth_svc import generate_link_code, hash_password
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(User).where(User.email == s.owner_email.lower()))).scalar_one_or_none()
        if existing:
            if not existing.is_owner:
                existing.is_owner = True
                await db.commit()
            return
        owner = User(
            email=s.owner_email.lower(),
            password_hash=hash_password(s.owner_password.get_secret_value()),
            full_name="Owner",
            is_owner=True,
            is_active=True,
            subscription_tier="pro",
            subscription_status="active",
            telegram_chat_id=s.telegram_chat_id or None,
            telegram_link_code=generate_link_code(),
        )
        db.add(owner)
        await db.commit()
        log.info(f"[startup] owner account created: {s.owner_email}")


async def _prewarm_news_batch():
    """Run one bulk news fetch right after startup so the first scan hits cache."""
    await asyncio.sleep(10)  # let the app finish booting
    try:
        from services.benzinga_news import prefetch_news_batch
        from services.scanner import _get_scan_tickers

        tickers = await _get_scan_tickers(get_settings())
        await prefetch_news_batch(tickers)
        log.info(f"[startup] news batch pre-warmed for {len(tickers)} tickers")
    except Exception as e:
        log.debug(f"[startup] news batch prewarm failed: {e}")


async def _warm_indicator_cache():
    """
    Pre-fetch Polygon indicators for all watchlist tickers at startup.
    Runs 10 tickers concurrently (unlimited Polygon calls on Starter plan).
    Completes in ~30 seconds instead of the old 60-minute free-tier throttle.
    """
    await asyncio.sleep(15)  # let first scan start first
    try:
        from services.polygon_indicators import get_indicators
        from services.scanner import _get_scan_tickers

        tickers = await _get_scan_tickers(get_settings())
        log.info(f"[startup] warming indicator cache for {len(tickers)} tickers (10 concurrent)")
        sem = asyncio.Semaphore(10)  # 10 concurrent — well within unlimited plan

        async def _fetch_one(t: str):
            async with sem:
                try:
                    await get_indicators(t)
                except Exception:
                    pass

        await asyncio.gather(*[_fetch_one(t) for t in tickers])
        log.info("[startup] indicator cache warm complete (%d tickers)", len(tickers))
    except Exception as e:
        log.debug(f"[startup] indicator cache warm failed: {e}")


async def _weekly_ticker_screener():
    """
    Sunday 10am ET — suggest 5-10 new tickers based on sector momentum,
    ETF flows, and Polygon reference data. Writes suggestions to app_settings.
    """
    ET = pytz.timezone("America/New_York")
    while True:
        now_et = datetime.now(ET)
        days_until_sunday = (6 - now_et.weekday()) % 7
        if days_until_sunday == 0 and now_et.hour >= 10:
            days_until_sunday = 7
        next_run = now_et.replace(hour=10, minute=30, second=0, microsecond=0)
        next_run = next_run + timedelta(days=days_until_sunday)
        await asyncio.sleep((next_run - now_et).total_seconds())
        try:
            api_key = get_settings().polygon_api_key or get_settings().massive_api_key or ""
            if not api_key:
                continue
            import ssl

            import aiohttp
            import certifi

            _ssl = ssl.create_default_context(cafile=certifi.where())
            candidates = []
            async with aiohttp.ClientSession() as sess:
                # Fetch active common stocks sorted by primary exchange
                async with sess.get(
                    "https://api.polygon.io/v3/reference/tickers",
                    params={
                        "market": "stocks",
                        "type": "CS",
                        "active": "true",
                        "sort": "primary_exchange",
                        "order": "asc",
                        "limit": 50,
                        "apiKey": api_key,
                    },
                    ssl=_ssl,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        candidates = [t.get("ticker", "") for t in (data.get("results") or []) if t.get("ticker")]
            if candidates:
                from database import AsyncSessionLocal
                from models import AppSettings
                from sqlalchemy import select

                async with AsyncSessionLocal() as db:
                    row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
                    if row and row.data is not None:
                        row.data = {
                            **row.data,
                            "screener_suggestions": candidates[:10],
                            "screener_updated": datetime.now(__import__("datetime").timezone.utc).isoformat(),
                        }
                        await db.commit()
                        log.info(f"[screener] {len(candidates[:10])} suggestions written to app_settings")
        except Exception as e:
            log.debug(f"[screener] weekly run failed: {e}")


async def _scan_watchdog():
    """Restart _periodic_scan if it ever exits unexpectedly."""
    global _scan_task
    await asyncio.sleep(120)  # let startup settle before watching
    while True:
        await asyncio.sleep(30)
        if _scan_task is None or _scan_task.done():
            exc = _scan_task.exception() if (_scan_task and not _scan_task.cancelled()) else None
            print(f"[watchdog] scanner task dead (exc={exc}), restarting")
            await _alert_telegram(f"⚠️ Scanner task died, restarting. exc={exc}")
            _scan_task = asyncio.create_task(_periodic_scan())


def _supervise(name: str, coro_fn, restart: bool = True):
    """Start a named background task and keep a handle for health reporting.

    If restart=True, the task is automatically restarted on unexpected exit
    (but not on CancelledError, which is a clean shutdown signal).
    """
    from datetime import timezone as _tz

    async def _wrapper():
        import os
        import socket
        import uuid
        import time as _time
        from database import AsyncSessionLocal
        from models import BackgroundJobRun
        from services.redis_cache import cache_acquire_lock, cache_release_lock

        locked_jobs = {
            "weekly_digest",
            "weekly_factor_mining",
            "weekly_ml_retrain",
            "nightly_outcome_resolution",
        }

        # Per-job lock TTLs: weekly_digest sleeps for days, so its lock must
        # outlast the sleep or multiple instances will all fire on Sunday.
        _lock_ttls = {
            "weekly_digest": 691200,  # 8 days
            "weekly_factor_mining": 14400,  # 4 hours
            "weekly_ml_retrain": 14400,  # 4 hours
            "nightly_outcome_resolution": 14400,  # 4 hours
        }

        worker_id = f"{socket.gethostname()}:{os.getpid()}"

        while True:
            started = datetime.now(_tz.utc).replace(tzinfo=None)
            task = asyncio.current_task()
            _bg_tasks[name]["started_at"] = started
            _bg_tasks[name]["task"] = task
            _bg_tasks[name]["status"] = "running"

            # Check if this job needs distributed locking
            lock_token = None
            if name in locked_jobs:
                try:
                    lock_ttl = _lock_ttls.get(name, 7200)
                    lock_token = await cache_acquire_lock(f"lock:job:{name}", ttl=lock_ttl)
                    if not lock_token:
                        log.info(f"[bg:{name}] Lock lock:job:{name} already held. Skipping execution.")
                        _bg_tasks[name]["status"] = "skipped_lock"
                        if not restart:
                            break
                        await asyncio.sleep(60)
                        continue
                except Exception as le:
                    log.warning(f"[bg:{name}] Error acquiring lock: {le}. Proceeding anyway.")

            cycle_id = f"bg:{name}:{int(_time.time())}:{uuid.uuid4().hex[:6]}"

            # Log start of run to DB
            run_id = None
            try:
                async with AsyncSessionLocal() as db:
                    run_rec = BackgroundJobRun(
                        job_name=name,
                        cycle_id=cycle_id,
                        start_time=started,
                        status="running",
                        worker_id=worker_id,
                    )
                    db.add(run_rec)
                    await db.commit()
                    run_id = run_rec.id
            except Exception as dbe:
                log.warning(f"[bg:{name}] Failed to log job run start: {dbe}")

            status = "completed"
            err_msg = None
            try:
                await coro_fn()
                _bg_tasks[name]["status"] = "done"
            except asyncio.CancelledError:
                _bg_tasks[name]["status"] = "cancelled"
                status = "cancelled"
                raise
            except Exception as exc:
                _bg_tasks[name]["status"] = f"error: {exc}"
                log.error(f"[bg:{name}] crashed — {exc}", exc_info=True)
                await _alert_telegram(f"⚠️ Background task '{name}' died: {exc}")
                status = "failed"
                err_msg = str(exc)
            finally:
                ended = datetime.now(_tz.utc).replace(tzinfo=None)
                duration = (ended - started).total_seconds()

                # Log end of run to DB
                if run_id:
                    try:
                        async with AsyncSessionLocal() as db:
                            run_rec = await db.get(BackgroundJobRun, run_id)
                            if run_rec:
                                run_rec.status = status
                                run_rec.end_time = ended
                                run_rec.duration_s = duration
                                if err_msg:
                                    run_rec.error = err_msg
                                await db.commit()
                    except Exception as dbe:
                        log.warning(f"[bg:{name}] Failed to log job run end: {dbe}")

                if lock_token:
                    try:
                        await cache_release_lock(f"lock:job:{name}", lock_token)
                    except Exception as le:
                        log.warning(f"[bg:{name}] Error releasing lock: {le}")

            if not restart:
                break
            await asyncio.sleep(5)  # brief pause before restart

    _bg_tasks[name] = {"task": None, "status": "starting", "started_at": None}
    return asyncio.create_task(_wrapper(), name=name)


def _async_exception_handler(loop, context):
    """R10-16: global handler for exceptions in fire-and-forget asyncio tasks.

    Without this, an exception in a task scheduled via create_task() that is
    never awaited (e.g. the startup one-shot run_scan, manual scan triggers)
    surfaces only as Python's default 'Task exception was never retrieved' and
    is otherwise swallowed. Here we log it with the task name and full
    traceback so such failures are always visible (and alertable).
    """
    exc = context.get("exception")
    if isinstance(exc, asyncio.CancelledError):
        return  # normal on shutdown
    task = context.get("future") or context.get("task")
    name = None
    try:
        if task is not None and hasattr(task, "get_name"):
            name = task.get_name()
    except Exception:
        name = None
    if exc is not None:
        log.error(
            "[async] Unhandled exception in task %r: %s: %s",
            name or "<unknown>",
            type(exc).__name__,
            exc,
            exc_info=exc,
        )
    else:
        log.error("[async] Async error in task %r: %s", name or "<unknown>", context.get("message"))


async def lifespan(app: FastAPI):
    # R10-16: never silently swallow fire-and-forget task exceptions.
    try:
        asyncio.get_running_loop().set_exception_handler(_async_exception_handler)
    except Exception as _eh_err:  # pragma: no cover - defensive
        log.warning(f"[startup] Could not install async exception handler: {_eh_err}")
    # ── Security boot checks ──────────────────────────────────────────────────
    _s = get_settings()
    _is_local = _s.app_url.startswith("http://localhost") or _s.app_url.startswith("http://127.")
    if not _s.jwt_secret and not _is_local:
        raise RuntimeError(
            "[startup] SECURITY: JWT_SECRET is not set. Tokens are signed with a static "
            "dev key — all users share the same signing secret. Set JWT_SECRET in .env "
            'to a 64-char random string (python -c "import secrets; print(secrets.token_hex(32))"). '
            "Every container restart with an empty JWT_SECRET is a production security incident."
        )
    _owner_pwd = _s.owner_password.get_secret_value() if _s.owner_password else ""
    if _owner_pwd and len(_owner_pwd) < 16 and not _is_local:
        raise RuntimeError(
            f"[startup] SECURITY: OWNER_PASSWORD is short ({len(_owner_pwd)} chars) — "
            "change it to a strong password before exposing /api/admin/ endpoints. "
            "An unauthorized login grants access to all user emails and Stripe IDs."
        )
    if not _s.stripe_webhook_secret and not _is_local:
        log.critical(
            "[startup] SECURITY: STRIPE_WEBHOOK_SECRET is not set. "
            "The billing webhook (/api/billing/webhook) will reject all Stripe events because "
            "stripe.Webhook.construct_event() requires a non-empty secret to validate signatures. "
            "An attacker can also probe which events fail — set STRIPE_WEBHOOK_SECRET=whsec_... "
            "from the Stripe dashboard → Developers → Webhooks → your endpoint → Signing secret."
        )
    # ─────────────────────────────────────────────────────────────────────────
    await init_db()
    try:
        from services.signal_policy import initialize_policy_and_registry

        await initialize_policy_and_registry()
    except Exception as e:
        log.warning(f"[startup] Failed to initialize policy/registry: {e}")
    await _ensure_owner_account()
    await _ensure_default_watchlist()
    asyncio.create_task(run_scan(broadcast_fn=manager.broadcast))
    global _scan_task
    _scan_task = asyncio.create_task(_periodic_scan())
    asyncio.create_task(_scan_watchdog())
    _supervise("weekly_digest", _weekly_digest, restart=True)
    _supervise("weekly_factor_mining", _weekly_factor_mining, restart=True)
    _supervise("weekly_ml_retrain", _weekly_ml_retrain, restart=True)
    _supervise("nightly_signal_cleanup", _nightly_signal_cleanup, restart=True)
    _supervise("nightly_stripe_reconciliation", _nightly_stripe_reconciliation, restart=True)
    _supervise("nightly_outcome_resolution", _nightly_outcome_resolution, restart=True)
    _supervise("nightly_cboe_options_snapshot", _nightly_cboe_options_snapshot, restart=True)
    _supervise("intraday_stop_monitor", _intraday_stop_monitor, restart=True)
    _supervise("nightly_reflection", _nightly_reflection_learning, restart=True)
    _supervise("weekly_screener", _weekly_ticker_screener, restart=True)

    # Pre-warm sector heatmap cache so first open is instant
    async def _prewarm_sectors():
        try:
            from routers.quotes import sector_heatmap

            await sector_heatmap()
            print("[startup] sector heatmap pre-warmed")
        except Exception as e:
            print(f"[startup] sector prewarm failed: {e}")

    _supervise("prewarm_sectors", _prewarm_sectors, restart=False)
    if settings.alpaca_api_key and settings.alpaca_api_secret:
        alpaca_ws.start(
            settings.alpaca_api_key, settings.alpaca_api_secret.get_secret_value(), settings.tickers, manager.broadcast
        )
    from services.dark_pool import start_dark_pool_stream

    _supervise("dark_pool_stream", start_dark_pool_stream, restart=True)
    _supervise("prewarm_news", _prewarm_news_batch, restart=False)
    _supervise("warm_indicators", _warm_indicator_cache, restart=False)
    yield
    alpaca_ws.stop()
    from services.http_client import close_sessions

    await close_sessions()
    if _scan_task:
        _scan_task.cancel()
    for entry in _bg_tasks.values():
        t = entry.get("task")
        if t and not t.done():
            t.cancel()


app = FastAPI(title="Signal.Trade API", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_cors_origin = get_settings().app_url.rstrip("/")
_allowed_origins = (
    ["*"] if _cors_origin.startswith("http://localhost") or _cors_origin.startswith("http://127.") else [_cors_origin]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── No-cache middleware for JSX/JS so browsers always get the latest code ────
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest


class CacheMiddleware(BaseHTTPMiddleware):
    """
    CDN-aware cache control:
      • App code (HTML, JSX, JS, CSS) — no-store so Cloudflare proxies always
        fetch fresh versions and code deploys are instant.
      • True static assets (fonts, favicons, manifest, sw.js) — 1-year immutable
        cache with content-hashed URLs, dramatically reducing TTFB via CDN edge.
      • API responses — no-store; CDN must not cache dynamic data.
    """

    # Assets that are content-hashed or versioned — safe to cache for 1 year
    _IMMUTABLE_EXTS = (".woff", ".woff2", ".ttf", ".otf", ".eot", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico")
    _IMMUTABLE_PATHS = {"/favicon.svg", "/manifest.json"}
    # App code — never cached (Cloudflare should bypass these too)
    _NO_CACHE_EXTS = (".jsx", ".js", ".html", ".css")
    _NO_CACHE_PATHS = {
        "/",
        "/app",
        "/login",
        "/signup",
        "/mobile",
        "/design",
        "/hub",
        "/track-record",
        "/tos",
        "/privacy",
        "/verify-email",
        "/sw.js",
    }  # sw.js must never be stale

    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        path = request.url.path

        if path.startswith("/api/") or path.startswith("/ws"):
            response.headers["Cache-Control"] = "no-store"
            return response

        if path in self._IMMUTABLE_PATHS or path.endswith(self._IMMUTABLE_EXTS):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            return response

        if path in self._NO_CACHE_PATHS or path.endswith(self._NO_CACHE_EXTS):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response


app.add_middleware(CacheMiddleware)


# ── Data Compliance Middleware ────────────────────────────────────────────────
# Polygon.io and Finnhub free-tier terms prohibit commercial redistribution of
# raw market data. This middleware stamps all API responses with the appropriate
# licensing notice so the data flow is auditable.
class DataComplianceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["X-Data-Policy"] = (
                "Signal.Trade redistributes derived signals (confidence scores, entry/stop/target) "
                "under a commercial subscriber licence. Raw OHLCV and real-time data sourced from "
                "Polygon.io and yfinance is gated behind paid subscriptions per provider terms."
            )
        return response


app.add_middleware(DataComplianceMiddleware)


# ── Security Headers Middleware ───────────────────────────────────────────────
# Adds CSP, HSTS, X-Frame-Options, and related headers to all responses.
# CSP blocks inline eval — esbuild pre-compiled bundle replaces Babel CDN.
# NOTE: update script-src hashes when upgrading React/CDN versions.
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    # esbuild pre-compiles JSX via dist/app-bundle.js — Babel standalone no longer loaded.
    # 'unsafe-eval' removed: no dynamic eval() required in production bundle.
    _SCRIPT_SRC = "'self' https://unpkg.com https://fonts.googleapis.com https://fonts.gstatic.com"
    _STYLE_SRC = "'self' 'unsafe-inline' https://fonts.googleapis.com"
    _FONT_SRC = "'self' https://fonts.gstatic.com data:"
    _IMG_SRC = "'self' data: blob:"
    _CONNECT_SRC = "'self' wss: ws: https://api.stripe.com"

    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        path = request.url.path

        # Only add security headers to HTML page routes and API — not binary assets
        if not path.endswith((".woff", ".woff2", ".png", ".jpg", ".ico", ".svg")):
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        # HSTS only on HTTPS deployments (avoid breaking local dev HTTP)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # CSP on HTML pages (not on API JSON or static assets — they don't exec scripts)
        if not path.startswith("/api/") and not path.startswith("/ws"):
            response.headers["Content-Security-Policy"] = (
                f"default-src 'self'; "
                f"script-src {self._SCRIPT_SRC}; "
                f"style-src {self._STYLE_SRC}; "
                f"font-src {self._FONT_SRC}; "
                f"img-src {self._IMG_SRC}; "
                f"connect-src {self._CONNECT_SRC}; "
                f"frame-ancestors 'none';"
            )

        return response


app.add_middleware(SecurityHeadersMiddleware)

# ── API routers (registered BEFORE the static-file catch-all) ────────────────
app.include_router(accuracy_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(ml_router)
app.include_router(oauth_router)
app.include_router(billing_router)
app.include_router(public_router)
app.include_router(telegram_webhook_router)
app.include_router(signals_router)
app.include_router(me_router)
app.include_router(quotes_router)
app.include_router(sources_router)
app.include_router(settings_router)
app.include_router(delivery_router)
app.include_router(market_router)
app.include_router(watchlist_router)
app.include_router(paper_router)
app.include_router(price_alerts_router)
app.include_router(signal_alerts_router)
app.include_router(ws_router)
app.include_router(screener_router)
app.include_router(broker_router)


# ── Health check (fast — no external calls, just DB ping) ────────────────────────
@app.get("/api/health", tags=["meta"])
async def health_check():
    from database import AsyncSessionLocal
    from sqlalchemy import text

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        from datetime import timezone as _tz

        scan = get_scan_status()
        bg_status = {
            name: {
                "status": entry.get("status", "unknown"),
                "started_at": entry["started_at"].isoformat() if entry.get("started_at") else None,
                "alive": entry.get("task") is not None and not entry["task"].done(),
            }
            for name, entry in _bg_tasks.items()
        }
        degraded = [
            n for n, e in bg_status.items() if not e["alive"] and e["status"] not in ("done", "cancelled", "starting")
        ]
        # Data-quality counters: tickers with consecutive null fetches ≥ 1
        data_quality_alerts = {t: n for t, n in _data_quality.items() if n > 0}
        return {
            "status": "degraded" if degraded else "ok",
            "db": "connected",
            "scan": scan,
            "background_tasks": bg_status,
            "degraded_tasks": degraded,
            "data_quality": {
                "null_streak_by_ticker": data_quality_alerts,
                "degraded_tickers": [t for t, n in data_quality_alerts.items() if n >= 5],
            },
            "ts": datetime.now(_tz.utc).isoformat(),
        }
    except Exception as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail=f"DB unavailable: {e}")


@app.get("/api/health/sentry", tags=["meta"])
async def sentry_health():
    """Return whether Sentry is configured and reachable.

    To verify the integration end-to-end, set SENTRY_DSN and hit this endpoint;
    a test message is sent to Sentry and the event ID is returned.
    """
    if not _sentry_dsn:
        return {"configured": False, "environment": None, "event_id": None}

    import sentry_sdk

    event_id = sentry_sdk.capture_message("Sentry health check", level="info")
    return {
        "configured": True,
        "environment": "production" if not os.environ.get("DEBUG") else "development",
        "event_id": event_id,
    }


@app.get("/api/scan/status", tags=["meta"])
async def scan_status(user: User = Depends(get_current_user)):
    """Return scanner lifecycle status for authenticated users."""
    return get_scan_status()


@app.post("/api/admin/trigger-weekly-digest", tags=["admin"])
async def admin_trigger_weekly_digest(background_tasks: BackgroundTasks, user: User = Depends(get_current_user)):
    """Manually trigger the weekly digest to be sent immediately."""
    if not user.is_owner:
        raise HTTPException(status_code=403, detail="Owner access required.")
    # force=True: a manual owner trigger always sends, bypassing the weekly guard.
    background_tasks.add_task(_run_weekly_digest, force=True)
    return {"status": "ok", "message": "Weekly digest triggered and sending in the background."}


@app.get("/api/admin/weekly-digest/status", tags=["admin"])
async def admin_weekly_digest_status(user: User = Depends(get_current_user)):
    """Owner-only summary of weekly digest schedule and delivery configuration."""
    if not user.is_owner:
        raise HTTPException(status_code=403, detail="Owner access required.")
    return {
        "schedule": "Sunday 08:00 ET",
        "telegram_configured": bool(settings.telegram_bot_token),
        "owner_telegram_linked": bool(user.telegram_chat_id),
        "fallback_chat_configured": bool(settings.telegram_chat_id),
        "email_configured": bool(settings.smtp_host and settings.smtp_user),
    }


# ── Named page routes (must be registered before the static catch-all) ──────────
@app.get("/favicon.ico")
async def serve_favicon_ico():
    return FileResponse(str(ROOT / "favicon.svg"), media_type="image/svg+xml")


@app.get("/favicon.svg")
async def serve_favicon_svg():
    return FileResponse(str(ROOT / "favicon.svg"), media_type="image/svg+xml")


@app.get("/")
async def serve_landing():
    return FileResponse(str(ROOT / "landing.html"))


@app.get("/app")
async def serve_app():
    return FileResponse(str(ROOT / "Trading Recommendation System.html"))


@app.get("/login")
async def serve_login():
    return FileResponse(str(ROOT / "login.html"))


@app.get("/signup")
async def serve_signup():
    return FileResponse(str(ROOT / "signup.html"))


@app.get("/track-record")
async def serve_track_record():
    return FileResponse(str(ROOT / "track-record.html"))


@app.get("/tos")
async def serve_tos():
    return FileResponse(str(ROOT / "tos.html"))


@app.get("/privacy")
async def serve_privacy():
    return FileResponse(str(ROOT / "privacy.html"))


@app.get("/mobile")
async def serve_mobile():
    return FileResponse(str(ROOT / "mobile.html"))


@app.get("/design")
async def serve_design():
    return FileResponse(str(ROOT / "design.html"))


@app.get("/hub")
async def serve_hub():
    return FileResponse(str(ROOT / "hub.html"))


@app.get("/verify-email")
async def serve_verify_email():
    return FileResponse(str(ROOT / "verify-email.html"))


# ── Static files (CSS, JS, etc.) served from project root ────────────────────
app.mount("/", StaticFiles(directory=str(ROOT)), name="static")


if __name__ == "__main__":
    import os

    import uvicorn

    print("\n  Signal.Trade backend starting…")
    print("  Open → http://localhost:8000\n")
    # Auto-reload is a DEV-ONLY feature and must stay OFF on the live server.
    # The running app writes to data/, logs/, and the dist bundle inside the
    # watched tree, so watchfiles fires "change detected" constantly → the child
    # process is killed and respawned many times a minute. That restart storm
    # drops the scanner mid-cycle (signals queue up and breach the ≤5min delivery
    # SLA) and tears down WS feeds and in-memory caches. Opt in for local dev with
    # DEV_RELOAD=1; the launchd service runs without it and therefore stays stable.
    dev_reload = os.getenv("DEV_RELOAD", "").strip().lower() in ("1", "true", "yes")
    # reload_excludes (dev only): also skip research scripts (scripts/) and tests/
    # that parallel sessions/jobs churn. Bare dir names are resolved by uvicorn into
    # recursive directory excludes (covers scripts/research/*).
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=dev_reload,
        reload_excludes=["scripts", "scripts/*", "tests", "tests/*"] if dev_reload else None,
    )
