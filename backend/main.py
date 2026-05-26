import asyncio
import logging
import os
import resource
import ssl
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path

import certifi
import pytz

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
# Silence noisy third-party loggers
logging.getLogger("yfinance").setLevel(logging.WARNING)
logging.getLogger("peewee").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("signal.trade")

# Point both requests (yfinance) and ssl (aiohttp) at the certifi bundle.
# Must happen before any network library is imported.
os.environ.setdefault("SSL_CERT_FILE",        certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE",   certifi.where())
os.environ.setdefault("CURL_CA_BUNDLE",       certifi.where())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, HTTPException, BackgroundTasks
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

from config import get_settings
from database import init_db
from routers.accuracy import router as accuracy_router
from routers.admin import router as admin_router
from routers.auth import router as auth_router
from routers.billing import router as billing_router
from routers.ml import router as ml_router
from routers.screener import router as screener_router
from routers.oauth import router as oauth_router
from routers.public import router as public_router
from routers.market import router as market_router
from routers.quotes import router as quotes_router
from routers.settings_router import router as settings_router
from routers.signals import router as signals_router
from routers.sources import router as sources_router
from routers.paper_router import router as paper_router
from routers.price_alerts import router as price_alerts_router
from routers.telegram_webhook import router as telegram_webhook_router
from routers.watchlist_router import router as watchlist_router
from routers.websocket_router import manager, router as ws_router
from routers.delivery_router import router as delivery_router
from services.scanner import get_scan_status, run_scan, _alert_telegram
from services.auth_svc import get_current_user
from models import User
from services import alpaca_ws

ROOT = Path(__file__).parent.parent  # project root (one level up from backend/)
settings = get_settings()

# ── PostgreSQL production warning ─────────────────────────────────────────────
from database import DATABASE_URL as _DB_URL, _IS_POSTGRES as _USING_POSTGRES
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

_scan_task: asyncio.Task | None = None


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
                        f"⚠️ Scanner error (streak {_scan_fail_streak})\n{type(e).__name__}: {str(e)[:200]}")
            await asyncio.sleep(60)
        return  # unreachable but satisfies linter

    # ── Continuous market-hours path ──────────────────────────────────────────
    while True:
        now = datetime.now(ET)
        interval_min = getattr(get_settings(), "scan_interval_min", 15) or 15

        if not _is_trading_day(now):
            next_open = _next_market_open()
            wait_s = (next_open - now).total_seconds()
            log.info("[scanner] weekend — sleeping until %s ET (%.1fh)",
                     next_open.strftime("%a %H:%M"), wait_s / 3600)
            await asyncio.sleep(wait_s)
            continue

        market_open  = now.replace(hour=9,  minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0,  second=0, microsecond=0)
        post_close   = now.replace(hour=16, minute=2,  second=0, microsecond=0)

        if now < market_open:
            wait_s = (market_open - now).total_seconds()
            log.info("[scanner] pre-market — sleeping %.1fmin until 09:30 ET open", wait_s / 60)
            await asyncio.sleep(wait_s)
            continue

        if now > post_close:
            next_open = _next_market_open()
            wait_s = (next_open - now).total_seconds()
            log.info("[scanner] after-hours — sleeping until %s ET (%.1fh)",
                     next_open.strftime("%a %H:%M"), wait_s / 3600)
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
                    f"⚠️ Scanner error (streak {_scan_fail_streak})\n{type(e).__name__}: {str(e)[:200]}")

        # After close: one final scan at 16:02 then sleep overnight
        now_after = datetime.now(ET)
        if now_after >= market_close:
            if now_after < post_close:
                await asyncio.sleep((post_close - now_after).total_seconds())
                try:
                    await run_scan(broadcast_fn=manager.broadcast)
                except Exception:
                    pass
            next_open = _next_market_open()
            wait_s = (_next_market_open() - datetime.now(ET)).total_seconds()
            log.info("[scanner] post-close scan done — sleeping until %s ET",
                     next_open.strftime("%a %H:%M"))
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
            from database import AsyncSessionLocal
            from models import Signal
            from sqlalchemy import update, select
            from datetime import timezone as _tz
            cutoff = datetime.now(_tz.utc)
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
                stale_rows = (await db.execute(
                    select(Signal)
                    .where(Signal.is_active   == True)
                    .where(Signal.outcome_pct.is_(None))   # not yet resolved
                    .where(Signal.created_at  <= day3_cutoff)
                    .where(Signal.action.in_(["BUY", "SELL"]))
                )).scalars().all()

                decayed = 0
                for sig in stale_rows:
                    age_days = (cutoff - sig.created_at).total_seconds() / 86400
                    extra_days = max(0, age_days - 3)
                    decay_pp   = min(15.0, extra_days * 3.0)
                    new_conf   = round(max(35.0, sig.confidence - decay_pp), 1)
                    if new_conf != sig.confidence:
                        sig.confidence = new_conf
                        decayed += 1

                await db.commit()
            log.info(f"[cleanup] deactivated {expired_count} expired | decayed {decayed} stale signals")
        except Exception as e:
            log.warning(f"[cleanup] nightly cleanup failed: {e}")


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
            import sys, os
            sys.path.insert(0, os.path.dirname(__file__))
            from validate_predictions import resolve_outcomes, resolve_mae_mfe
            updated = await resolve_outcomes()
            mae_updated = await resolve_mae_mfe()
            log.info(f"[nightly] resolved {updated} outcomes, {mae_updated} MAE/MFE records")
            # Refresh Platt + isotonic calibration now that outcomes are up-to-date
            from services.calibration import run_calibration
            cal = await run_calibration()
            log.info(f"[nightly] calibration refreshed — {len(cal)} bins")
        except Exception as e:
            log.warning(f"[nightly] outcome resolution failed: {e}")


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
            now_et.weekday() < 5 and
            now_et.time() >= __import__("datetime").time(9, 30) and
            now_et.time() <= __import__("datetime").time(16, 15)
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

            from database import AsyncSessionLocal
            from models import Signal
            from sqlalchemy import select
            from services.vector_store import store_reflection

            from datetime import timezone as _tz
            cutoff = datetime.now(_tz.utc) - timedelta(days=7)
            async with AsyncSessionLocal() as db:
                losses = (await db.execute(
                    select(Signal)
                    .where(Signal.outcome_pct.isnot(None))
                    .where(Signal.outcome_pct <= 0)
                    .where(Signal.is_sent == True)
                    .where(Signal.created_at >= cutoff)
                    .order_by(Signal.created_at.desc())
                    .limit(10)
                )).scalars().all()

            reflected = 0
            for sig in losses:
                try:
                    rationale_heads = "; ".join(
                        r.get("head", "") for r in (sig.rationale or [])[:5] if r.get("head")
                    ) or "no rationale stored"
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
                            "You are a quantitative trading risk analyst. "
                            "Be specific, concise, and actionable."
                        )
                    )
                    if lesson and len(lesson) > 30:
                        features = {
                            "confidence": sig.confidence / 100,
                            "outcome_pct": sig.outcome_pct,
                        }
                        store_reflection(sig.ticker, sig.action, sig.outcome_pct,
                                         features, lesson[:500])
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
                    f"[ml] retrain OK: OOS AUC={result.get('oos_auc') or '?'}  "
                    f"n_train={result.get('n_train', '?')}"
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


async def _run_weekly_digest():
    ET = pytz.timezone("America/New_York")
    try:
        from database import AsyncSessionLocal
        from models import Signal
        from sqlalchemy import select, desc
        from datetime import timezone as _tz
        now = datetime.now(_tz.utc)
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)

        async with AsyncSessionLocal() as db:
            sent_this_week = (await db.execute(
                select(Signal)
                .where(Signal.is_sent == True)
                .where(Signal.sent_at >= week_ago)
            )).scalars().all()

            resolved_past_week = (await db.execute(
                select(Signal)
                .where(Signal.is_sent == True)
                .where(Signal.sent_at >= two_weeks_ago)
                .where(Signal.sent_at < week_ago)
            )).scalars().all()

        def get_best_outcome(sig):
            for f in ("outcome_pct", "outcome_14d", "outcome_3d", "outcome_1d"):
                v = getattr(sig, f, None)
                if v is not None:
                    return v
            return None

        resolved_with_outcomes = [(r, get_best_outcome(r)) for r in resolved_past_week if get_best_outcome(r) is not None]
        sent     = len(sent_this_week)
        resolved_count = len(resolved_with_outcomes)
        wins     = [r for r, out in resolved_with_outcomes if out > 0]
        win_rate = round(len(wins) / resolved_count * 100) if resolved_count else None
        avg_ret  = round(sum(out for r, out in resolved_with_outcomes) / resolved_count, 2) if resolved_count else None
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
            from services.email_svc import send_weekly_digest
            from models import User
            from sqlalchemy import select as _sel
            import aiohttp
            from config import get_settings, TIERS
            
            week_ending_str = datetime.now(ET).strftime("%b %d, %Y")
            s = get_settings()
            
            async with AsyncSessionLocal() as db2:
                users = (await db2.execute(
                    _sel(User).where(User.is_active == True)
                )).scalars().all()
            
            recipients = [u.email for u in users
                          if u.is_owner or u.subscription_status == "active"]
            
            recipients_tg = [u.telegram_chat_id for u in users
                             if u.telegram_chat_id and (
                                 u.is_owner or (
                                     u.subscription_status == "active" and
                                     TIERS.index(u.subscription_tier) >= TIERS.index("basic")
                                 )
                             )]
            
            # Send to Telegram subscribers
            if s.telegram_bot_token:
                url = f"https://api.telegram.org/bot{s.telegram_bot_token}/sendMessage"
                message_text = "\n".join(lines)
                async with aiohttp.ClientSession() as session:
                    # Fallback to owner's .env chat_id if no subscribers have linked Telegram
                    chats_to_notify = set(recipients_tg)
                    if not chats_to_notify and s.telegram_chat_id:
                        chats_to_notify.add(s.telegram_chat_id)
                        
                    for chat_id in chats_to_notify:
                        try:
                            await session.post(url, json={
                                "chat_id": chat_id,
                                "text": message_text,
                                "parse_mode": "Markdown",
                            })
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
        print(f"[digest] error: {e}")

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
        "AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","BRK-B","AVGO","JPM",
        "LLY","V","UNH","XOM","MA","COST","HD","PG","JNJ","WMT",
        "BAC","ABBV","CRM","AMD","NFLX","KO","ACN","MRK","CVX","TMO",
        "ORCL","WFC","ABT","CSCO","AXP","BX","MCD","PEP","PM","GE",
        "INTU","CAT","QCOM","GS","TXN","NOW","IBM","MS","LIN","DHR",
        "NEE","RTX","UNP","HON","SYK","AMGN","BMY","UBER","AMAT","UPS",
        "T","PANW","LOW","BKNG","DE","MDT","VRTX","LMT","MU","C",
        "REGN","SBUX","BA","NKE","CVS","ISRG","PLD","GILD","SO","TJX",
        "MMC","ETN","CME","CI","BSX","PGR","AON","MCO","HCA","GM",
        "SNOW","PLTR","MO","TGT","GD","CB","AIG","COF","SPGI","ZTS",
        # ── Established tech & semi ──────────────────────────────────────────
        "SMCI","ARM","MRVL","KLAC","LRCX","ADI","CDNS","SNPS","ICE","ADP",
        # ── AI Infrastructure (second-wave): FPGAs, packaging, optics, storage
        "ALTR","AMKR","COHR","LATT","POWI","PSTG","KEYS",
        # ── Industrial rotation & infrastructure ─────────────────────────────
        "PWR","TT","URI","AME","EMR","ITW","APH",
        # ── Commodities / real assets ────────────────────────────────────────
        "FCX","SCCO","HBM","AEM","NEM",
        "GLD","GDX","GDXJ","SLV","SIL","COPX","PALL","PPLT",
        "SLB","EOG",
        # ── Software / next-gen tech ─────────────────────────────────────────
        "MDB","DDOG","NET",
        # ── Broad market & sector ETFs ───────────────────────────────────────
        "SPY","QQQ","IWM","TQQQ","XLK","XLF","XLE","XLI","XLV","XLC","XLP","XLRE","XLU","XLB",
        # ── 3× Bull leveraged ETFs ───────────────────────────────────────────
        "UPRO","SPXL","SOXL","TECL","FAS","TNA","LABU","WEBL","FNGU",
        "NAIL","DPST","YINN","DRN","TMF","HIBL","MIDU","GUSH","NUGT","JNUG",
        # ── 3× Bear / inverse leveraged ETFs ────────────────────────────────
        "SQQQ","SPXS","SPXU","SOXS","TECS","FAZ","TZA","LABD","FNGD",
        "YANG","DRV","TMV","HIBS","SRTY","DRIP","DUST","JDST",
        # ── 2× leveraged (popular liquid pairs) ─────────────────────────────
        "SSO","SDS","QLD","QID","UCO","SCO","ROM","UWM","TWM",
        # ── Previously-active custom ─────────────────────────────────────────
        "BLK","ELV","EBAY","PNC","USB","WM",
    ]

    try:
        from database import AsyncSessionLocal
        from models import WatchlistItem
        from sqlalchemy import select, func

        async with AsyncSessionLocal() as db:
            existing_count = (await db.execute(
                select(func.count()).select_from(WatchlistItem).where(WatchlistItem.is_active == True)
            )).scalar_one()

            if existing_count >= 20:
                return  # watchlist already populated — don't overwrite user edits

            existing_tickers = set(
                r.ticker for r in
                (await db.execute(select(WatchlistItem.ticker))).scalars().all()
            )

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
    from sqlalchemy import select
    from services.auth_svc import generate_link_code, hash_password
    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(User).where(User.email == s.owner_email.lower()))).scalar_one_or_none()
        if existing:
            if not existing.is_owner:
                existing.is_owner = True
                await db.commit()
            return
        owner = User(
            email=s.owner_email.lower(),
            password_hash=hash_password(s.owner_password),
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
            api_key = (get_settings().polygon_api_key or get_settings().massive_api_key or "")
            if not api_key:
                continue
            import ssl, certifi, aiohttp
            _ssl = ssl.create_default_context(cafile=certifi.where())
            candidates = []
            async with aiohttp.ClientSession() as sess:
                # Fetch active common stocks sorted by primary exchange
                async with sess.get(
                    "https://api.polygon.io/v3/reference/tickers",
                    params={"market": "stocks", "type": "CS", "active": "true",
                            "sort": "primary_exchange", "order": "asc",
                            "limit": 50, "apiKey": api_key},
                    ssl=_ssl, timeout=aiohttp.ClientTimeout(total=10)
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        candidates = [t.get("ticker","") for t in (data.get("results") or [])
                                      if t.get("ticker")]
            if candidates:
                from database import AsyncSessionLocal
                from models import AppSettings
                from sqlalchemy import select
                async with AsyncSessionLocal() as db:
                    row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
                    if row and row.data is not None:
                        row.data = {**row.data, "screener_suggestions": candidates[:10],
                                    "screener_updated": datetime.now(__import__('datetime').timezone.utc).isoformat()}
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


async def lifespan(app: FastAPI):
    await init_db()
    await _ensure_owner_account()
    await _ensure_default_watchlist()
    asyncio.create_task(run_scan(broadcast_fn=manager.broadcast))
    global _scan_task
    _scan_task = asyncio.create_task(_periodic_scan())
    asyncio.create_task(_scan_watchdog())
    asyncio.create_task(_weekly_digest())
    asyncio.create_task(_weekly_factor_mining())
    asyncio.create_task(_weekly_ml_retrain())
    asyncio.create_task(_nightly_signal_cleanup())
    asyncio.create_task(_nightly_outcome_resolution())
    asyncio.create_task(_intraday_stop_monitor())
    asyncio.create_task(_nightly_reflection_learning())
    # Pre-warm sector heatmap cache so first open is instant
    async def _prewarm_sectors():
        try:
            from routers.quotes import sector_heatmap
            await sector_heatmap()
            print("[startup] sector heatmap pre-warmed")
        except Exception as e:
            print(f"[startup] sector prewarm failed: {e}")
    asyncio.create_task(_prewarm_sectors())
    if settings.alpaca_api_key and settings.alpaca_api_secret:
        alpaca_ws.start(settings.alpaca_api_key, settings.alpaca_api_secret,
                        settings.tickers, manager.broadcast)
    from services.dark_pool import start_dark_pool_stream
    asyncio.create_task(start_dark_pool_stream())
    # News batch prefetch — warm per-ticker news cache once before first scan
    asyncio.create_task(_prewarm_news_batch())
    # Indicator cache warming — 10 concurrent fetches, completes in ~30s
    asyncio.create_task(_warm_indicator_cache())
    # Weekly ticker screener — suggest new tickers every Sunday
    asyncio.create_task(_weekly_ticker_screener())
    yield
    alpaca_ws.stop()
    if _scan_task:
        _scan_task.cancel()


app = FastAPI(title="Signal.Trade API", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_cors_origin = get_settings().app_url.rstrip("/")
_allowed_origins = (
    ["*"]
    if _cors_origin.startswith("http://localhost") or _cors_origin.startswith("http://127.")
    else [_cors_origin]
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
    _IMMUTABLE_EXTS   = (".woff", ".woff2", ".ttf", ".otf", ".eot",
                         ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico")
    _IMMUTABLE_PATHS  = {"/favicon.svg", "/manifest.json"}
    # App code — never cached (Cloudflare should bypass these too)
    _NO_CACHE_EXTS    = (".jsx", ".js", ".html", ".css")
    _NO_CACHE_PATHS   = {"/", "/app", "/login", "/signup", "/mobile", "/design",
                         "/hub", "/track-record", "/tos", "/privacy", "/verify-email",
                         "/sw.js"}   # sw.js must never be stale

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
            response.headers["Pragma"]        = "no-cache"
            response.headers["Expires"]       = "0"

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
app.include_router(quotes_router)
app.include_router(sources_router)
app.include_router(settings_router)
app.include_router(delivery_router)
app.include_router(market_router)
app.include_router(watchlist_router)
app.include_router(paper_router)
app.include_router(price_alerts_router)
app.include_router(ws_router)
app.include_router(screener_router)


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
        return {
            "status": "ok",
            "db": "connected",
            "scan": scan,
            "ts": datetime.now(_tz.utc).isoformat(),
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"DB unavailable: {e}")


@app.get("/api/scan/status", tags=["meta"])
async def scan_status(user: User = Depends(get_current_user)):
    """Return scanner lifecycle status for authenticated users."""
    return get_scan_status()

@app.post("/api/admin/trigger-weekly-digest", tags=["admin"])
async def admin_trigger_weekly_digest(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
):
    """Manually trigger the weekly digest to be sent immediately."""
    if not user.is_owner:
        raise HTTPException(status_code=403, detail="Owner access required.")
    background_tasks.add_task(_run_weekly_digest)
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
    import uvicorn
    print("\n  Signal.Trade backend starting…")
    print(f"  Open → http://localhost:8000\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
