import asyncio
import logging
import ssl
import certifi
from datetime import datetime, timedelta, time as dtime

import pytz

_SSL_CTX = ssl.create_default_context(cafile=certifi.where())

log = logging.getLogger("scanner")

import aiohttp

from database import AsyncSessionLocal
from models import AppSettings, SendLog, Signal, SignalDelivery, User
from services.aaii import get_aaii_sentiment
from services.breadth import get_market_breadth
from services.cot import get_cot_signal
from services.fear_greed import get_fear_greed, get_put_call_ratio
from services.macro import get_macro_context
from services.market_data import get_histories_batch, get_infos_sequential, get_quotes_batch
from services.signal_engine import scan_all
from services.telegram_svc import format_signal, send_telegram
from config import get_settings, TIERS
from sqlalchemy import select, desc, update, func

# ── Data quality monitoring ───────────────────────────────────────────────────
_data_quality: dict[str, int] = {}  # ticker → consecutive_null_count


def _check_data_quality(histories: dict, settings) -> list[str]:
    """
    Check fetched OHLCV histories for data gaps.
    Returns list of tickers with ≥5 consecutive null fetches (for Telegram alert).
    Mutates module-level _data_quality counter.
    """
    degraded = []
    for ticker, df in histories.items():
        if df is None or len(df) < 5 or df["Close"].iloc[-1] == 0:
            _data_quality[ticker] = _data_quality.get(ticker, 0) + 1
            if _data_quality[ticker] == 5:  # only alert on the transition to 5
                degraded.append(ticker)
        else:
            _data_quality[ticker] = 0  # reset on valid data
    return degraded


async def _alert_sla_breach(ticker: str, action: str, latency_s: float, settings):
    """Notify owner when signal delivery exceeds 5-minute SLA."""
    msg = (f"⚠️ SLA breach: {action} {ticker} took {latency_s/60:.1f}min to deliver "
           f"(target ≤5min). Check scanner health.")
    try:
        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        async with aiohttp.ClientSession() as sess:
            await sess.post(url, json={"chat_id": settings.telegram_chat_id,
                                       "text": msg}, ssl=_SSL_CTX,
                            timeout=aiohttp.ClientTimeout(total=5))
    except Exception:
        pass


async def _fanout_to_subscribers(sig_dict: dict, db_row: Signal, db) -> bool:
    """
    Deliver signal to all active subscribers who have Telegram linked.
    Returns True if at least one delivery succeeded.
    """
    s = get_settings()
    if not s.telegram_bot_token:
        return False

    # Fetch users: active subscription (basic or pro) + telegram chat linked
    # Free users don't get Telegram delivery
    subscribers = (await db.execute(
        select(User).where(
            User.telegram_chat_id.isnot(None),
            User.is_active == True,
        )
    )).scalars().all()

    # Filter to those with telegram access (basic+, pro, or owner)
    eligible = [
        u for u in subscribers
        if u.is_owner
        or (u.subscription_status == "active"
            and TIERS.index(u.subscription_tier) >= TIERS.index("basic"))
    ]

    if not eligible:
        return False

    # Check for already-delivered (dedup)
    delivered_user_ids = set()
    if db_row.id:
        rows = (await db.execute(
            select(SignalDelivery.user_id).where(SignalDelivery.signal_id == db_row.id)
        )).scalars().all()
        delivered_user_ids = set(rows)

    message_text = format_signal(sig_dict)
    url = f"https://api.telegram.org/bot{s.telegram_bot_token}/sendMessage"
    any_success = False

    global_min_conf = get_settings().min_confidence
    sent_chat_ids: set[str] = set()  # dedup: never send twice to the same chat
    async with aiohttp.ClientSession() as session:
        for user in eligible:
            if user.id in delivered_user_ids:
                continue
            if user.telegram_chat_id in sent_chat_ids:
                log.info(f" [fanout] skipped user={user.id} — chat {user.telegram_chat_id} already received this signal")
                continue
            # Apply per-user confidence threshold (falls back to global setting)
            user_min = user.min_confidence_override if user.min_confidence_override is not None else global_min_conf
            if sig_dict.get("confidence", 0) < user_min:
                log.info(f" [fanout] user={user.id} threshold {user_min:.0f}% > conf {sig_dict['confidence']:.0f}% — skipped")
                continue
            try:
                resp = await session.post(url, json={
                    "chat_id": user.telegram_chat_id,
                    "text": message_text,
                    "parse_mode": "Markdown",
                })
                data = await resp.json()
                msg_id = str(data.get("result", {}).get("message_id", "")) if data.get("ok") else None
                db.add(SignalDelivery(
                    signal_id=db_row.id,
                    user_id=user.id,
                    telegram_msg_id=msg_id,
                ))
                if data.get("ok"):
                    any_success = True
                    sent_chat_ids.add(user.telegram_chat_id)
                    log.info(f" [fanout] delivered to user={user.id} chat={user.telegram_chat_id}")
                else:
                    log.warning(f" [fanout] failed user={user.id}: {data.get('description')}")
            except Exception as e:
                log.warning(f" [fanout] error user={user.id}: {e}")

    await db.flush()  # persist deliveries before outer commit

    # Discord delivery — alongside Telegram, for users with webhook_url set
    try:
        from services.discord_bot import send_discord_signal
        discord_users = [u for u in eligible if getattr(u, "discord_webhook_url", None)]
        for du in discord_users:
            asyncio.create_task(send_discord_signal(du.discord_webhook_url, sig_dict))
    except Exception:
        pass

    return any_success


_ET = pytz.timezone("America/New_York")

# Tickers whose .info was recently fetched — skip re-fetch if price barely moved
_MOVEMENT_THRESHOLD = 1.0  # % — skip info re-fetch if price moved less than this

# ── Differential Scan state ──────────────────────────────────────────────────
# Persists last known price + volume per ticker across scan cycles.
# Next scan: stable tickers skip generate_signal() entirely, saving ~80/154 API calls.
_diff_state: dict[str, dict] = {}   # {ticker: {price, volume, ts}}
_DIFF_PRICE_THRESHOLD  = 0.5   # % price change that counts as "moved"
_DIFF_VOL_THRESHOLD    = 1.3   # volume ratio above which ticker is "active"
_DIFF_SIGNAL_MAX_AGE_H = 2.0   # skip only if an active signal was created within this window


def _market_session() -> str:
    """Return the current US market session: pre, regular, after, or closed."""
    now_et = datetime.now(_ET)
    if now_et.weekday() >= 5:
        return "closed"
    t = now_et.time()
    if dtime(4, 0) <= t < dtime(9, 30):   return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):  return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):  return "after"
    return "closed"

def _market_hours_ok() -> bool:
    """Return True during NYSE trading hours (9:30–15:55 ET, Mon–Fri only)."""
    now_et = datetime.now(_ET)
    if now_et.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False
    return dtime(9, 30) <= now_et.time() <= dtime(15, 55)


async def _get_scan_tickers(settings) -> list[str]:
    """Return tickers from DB watchlist if populated, otherwise fall back to .env."""
    try:
        from models import WatchlistItem
        async with AsyncSessionLocal() as db:
            rows = (await db.execute(
                select(WatchlistItem).where(WatchlistItem.is_active == True)
            )).scalars().all()
            if rows:
                return [r.ticker for r in rows]
    except Exception:
        pass
    return settings.tickers


def _pct(current, entry, action):
    if not current or not entry or entry <= 0:
        return None
    raw = (current - entry) / entry * 100
    return round(raw if action == "BUY" else -raw, 2)


async def _update_outcomes(quotes: list[dict]):
    """Record % return at 1d, 3d, 7d, and 14d horizons for sent signals."""
    now = datetime.utcnow()
    price_map = {q["t"]: q["p"] for q in quotes}
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(
            select(Signal).where(Signal.is_sent == True)
        )).scalars().all()
        for sig in rows:
            current = price_map.get(sig.ticker)
            if not current or not sig.entry or sig.entry <= 0:
                continue
            age_days = (now - sig.created_at).total_seconds() / 86400 if sig.created_at else 0
            if age_days >= 1  and sig.outcome_1d  is None:
                sig.outcome_1d  = _pct(current, sig.entry, sig.action)
            if age_days >= 3  and sig.outcome_3d  is None:
                sig.outcome_3d  = _pct(current, sig.entry, sig.action)
            if age_days >= 7  and sig.outcome_pct is None:
                sig.outcome_pct = _pct(current, sig.entry, sig.action)
                sig.outcome_at  = now
            if age_days >= 14 and sig.outcome_14d is None:
                sig.outcome_14d = _pct(current, sig.entry, sig.action)
        await db.commit()


# Minimum confidence delta that counts as a "significant" prediction change within a day.
# Below this threshold, the existing signal is silently refreshed (no new row, no re-send).
_CONF_CHANGE_THRESHOLD = 15.0  # percentage points


def _today_start_utc() -> datetime:
    """Return today's 00:00:00 ET expressed in UTC (naive)."""
    ET   = pytz.timezone("America/New_York")
    now  = datetime.now(ET)
    midnight_et = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight_et.astimezone(pytz.utc).replace(tzinfo=None)


async def _maybe_send(sig_dict: dict, db_row: Signal, settings, db, label: str,
                      force_resend: bool = False):
    """Send a Telegram notification for a signal if it qualifies. Mutates db_row on success.

    force_resend=True bypasses the 24h cooldown (used when the signal direction flipped)
    but still enforces a 30-minute anti-spam guard.
    """
    if sig_dict["action"] not in ("BUY", "SELL"):
        return
    if sig_dict["confidence"] < settings.min_confidence:
        log.info(f" {sig_dict['ticker']} skipped ({label}) "
              f"conf {sig_dict['confidence']:.0f}% < {settings.min_confidence:.0f}%")
        return

    # ── Style-based confidence floor ────────────────────────────────────────
    # Validated win rates by style: position 61.4%, swing 38.2%, intraday 30.4%.
    # Swing and intraday signals need higher confidence bars to be worth sending;
    # applying the global min_confidence to all styles is too permissive.
    _style = sig_dict.get("style", "swing")
    _style_floors = {"intraday": 68.0, "swing": 63.0, "position": 0.0}
    _style_floor  = _style_floors.get(_style, 63.0)
    if sig_dict["confidence"] < _style_floor:
        log.info(f" {sig_dict['ticker']} skipped ({label}) "
              f"{_style} conf {sig_dict['confidence']:.0f}% < style floor {_style_floor:.0f}%")
        return

    # ── Pre-earnings hard blackout (2 trading days) ─────────────────────────
    # Sending directional signals within 2 days of earnings exposes users to:
    # (1) IV crush destroying options premium even on correct direction,
    # (2) gap-through-stop risk, (3) analyst pre-positioning distortions.
    # The post-earnings cooldown (days 0–2) gates after; this gates before.
    _dte = sig_dict.get("daysToEarnings")
    if _dte is not None and 0 < _dte <= 2:
        log.info(f" {sig_dict['ticker']} skipped ({label}) "
              f"— {_dte}d to earnings (pre-earnings hard blackout)")
        return

    # ── Sector concentration limit (max 2 BUY sends per sector per 24h) ─────
    # Sending NVDA + AMD + SOXL + MU in one scan is one correlated bet ×4.
    # Cap at 2 signals per SPDR sector ETF per rolling 24h window.
    _sector = sig_dict.get("sectorEtf")
    if _sector and sig_dict["action"] == "BUY":
        _sector_cutoff = datetime.utcnow() - timedelta(hours=24)
        _sector_count = (await db.execute(
            select(func.count()).select_from(Signal)
            .where(Signal.sector_etf == _sector)
            .where(Signal.action     == "BUY")
            .where(Signal.is_sent    == True)
            .where(Signal.sent_at    >= _sector_cutoff)
        )).scalar_one()
        if _sector_count >= 2:
            log.info(f" {sig_dict['ticker']} skipped ({label}) "
                  f"— sector {_sector} already has {_sector_count} BUY sends in 24h (max 2)")
            return

    # ── Ticker-adaptive confidence floor ────────────────────────────────────
    # Global threshold is too blunt: AMD (100% win rate) deserves a lower bar;
    # tickers with <45% win rate need a higher bar to be worth sending.
    # Reads from adaptive_weights pre-computed each scan cycle.
    try:
        from database import AsyncSessionLocal
        from models import AppSettings
        async with AsyncSessionLocal() as _adb:
            _srow = (await _adb.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
        _app_data = (_srow.data or {}) if _srow else {}
        _ticker_wrs = _app_data.get("adaptive_weights", {}).get("ticker_win_rates", {})
        _twr = _ticker_wrs.get(sig_dict["ticker"])
        if _twr is not None:
            if _twr < 0.45 and sig_dict["confidence"] < 68.0:
                log.info(f" {sig_dict['ticker']} skipped ({label}) "
                      f"— hist win rate {_twr*100:.0f}% requires ≥68% conf (got {sig_dict['confidence']:.0f}%)")
                return
            if _twr >= 0.75 and sig_dict["confidence"] < 52.0:
                log.info(f" {sig_dict['ticker']} high-win skip — conf {sig_dict['confidence']:.0f}% < 52% floor even for {_twr*100:.0f}% WR")
                return
    except Exception:
        pass

    # ── Source independence gate ─────────────────────────────────────────────
    # A high-confidence signal driven entirely by correlated technical indicators
    # has much lower real-world win rates than one where multiple independent data
    # pipelines agree. Require at least 2 non-technical source categories for
    # position signals (and at least 1 for swing/intraday) before sending.
    # This prevents "everything is oversold on a crash day" from auto-sending.
    _sources_set  = set(sig_dict.get("sources") or [])
    _non_ta = _sources_set - {
        "Technical", "Technicals", "Risk Gate", "Backtest",
        "Cross-Sectional", "Orthogonalization", "Signal Cluster",
    }
    _min_non_ta = 2 if _style == "position" else 1
    if len(_non_ta) < _min_non_ta:
        log.info(f" {sig_dict['ticker']} skipped ({label}) "
              f"only {len(_non_ta)} non-TA sources for {_style} (need {_min_non_ta}): {_non_ta}")
        return

    # ── Minimum profit filter ───────────────────────────────────────────────
    entry  = sig_dict.get("entry")
    target = sig_dict.get("target")
    if entry and target and entry > 0:
        profit_pct = abs(target - entry) / entry * 100
        if profit_pct < 2.0:
            log.info(f" {sig_dict['ticker']} skipped ({label}) "
                  f"profit {profit_pct:.1f}% < 2.0% min")
            return

    # ── Market Holiday Pre-Signal Warning — -5pp confidence haircut ────────
    # 2 trading days before a 3-day weekend: lower liquidity, wider spreads, gap risk.
    try:
        from services.market_calendar import get_upcoming_holidays, is_pre_long_weekend
        _holidays = await get_upcoming_holidays()
        _is_long_wknd, _holiday_name = is_pre_long_weekend(_holidays)
        if _is_long_wknd:
            sig_dict = dict(sig_dict)  # shallow copy to avoid mutating original
            sig_dict["confidence"] = round(max(35.0, sig_dict["confidence"] - 5.0), 1)
            sig_dict.setdefault("rationale", [])
            sig_dict["rationale"] = list(sig_dict["rationale"]) + [{
                "src": "Risk Gate",
                "head": f"Pre-{_holiday_name} Haircut (−5pp)",
                "body": (f"Signal is 2 trading days before {_holiday_name} (3-day weekend). "
                         "Lower liquidity, wider bid-ask spreads, and gap risk at open after "
                         "the holiday reduce expected return. Confidence reduced by 5pp."),
                "sentiment": "neg",
                "meta": f"holiday={_holiday_name} haircut=-5pp",
            }]
    except Exception:
        pass

    # ── Time-of-day filter ──────────────────────────────────────────────────
    if not _market_hours_ok():
        log.info(f" {sig_dict['ticker']} notification suppressed — outside clean market window")
        return

    # ── Cooldown: 24h normally, 30 min on direction-flip (force_resend) ────
    # ── Hard cap: max 1 send per ticker per trading day ─────────────────────
    # Multiple same-ticker sends within one session count as one market view but
    # inflate the "sent signals" count and the win-rate denominator. Cap at 1
    # regardless of direction flip or confidence changes within the same day.
    _today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    _today_sent  = (await db.execute(
        select(Signal)
        .where(Signal.ticker  == sig_dict["ticker"])
        .where(Signal.is_sent == True)
        .where(Signal.sent_at >= _today_start)
        .limit(1)
    )).scalar_one_or_none()
    if _today_sent:
        log.info(f" {sig_dict['ticker']} skipped — already sent today (1/day cap)")
        return

    if force_resend:
        # Direction flip: only enforce a short anti-spam window (the daily cap above
        # already prevents same-day repeats; this guards cross-day rapid flips)
        cutoff = datetime.utcnow() - timedelta(minutes=30)
        result = await db.execute(
            select(Signal)
            .where(Signal.ticker  == sig_dict["ticker"])
            .where(Signal.is_sent == True)
            .where(Signal.sent_at >= cutoff)
            .limit(1)
        )
        if result.scalar_one_or_none():
            log.info(f" {sig_dict['ticker']} flip-cooldown — sent within 30m")
            return
        log.info(f" {sig_dict['ticker']} direction flip — bypassing 24h cooldown")
    else:
        # Base cooldown: 24h. Extended if the most recent resolved signal for
        # this ticker+action was a loss — prevents piling into losing trades.
        # Loss streak ≥3 → 72h cooldown. Single loss → 48h.
        base_hours = 24
        try:
            recent_resolved = (await db.execute(
                select(Signal.outcome_pct)
                .where(Signal.ticker      == sig_dict["ticker"])
                .where(Signal.action      == sig_dict["action"])
                .where(Signal.is_sent     == True)
                .where(Signal.outcome_pct.isnot(None))
                .order_by(Signal.sent_at.desc())
                .limit(3)
            )).scalars().all()
            if recent_resolved:
                _act = sig_dict["action"]
                # BUY win  = outcome_pct > 0;  BUY loss  = outcome_pct <= 0
                # SELL win = outcome_pct < 0;  SELL loss = outcome_pct >= 0
                losses = sum(
                    1 for o in recent_resolved
                    if (o <= 0 if _act == "BUY" else o >= 0)
                )
                if losses >= 3:
                    base_hours = 72
                elif losses >= 1:
                    base_hours = 48
        except Exception:
            pass

        cutoff = datetime.utcnow() - timedelta(hours=base_hours)
        result = await db.execute(
            select(Signal)
            .where(Signal.ticker  == sig_dict["ticker"])
            .where(Signal.action  == sig_dict["action"])
            .where(Signal.is_sent == True)
            .where(Signal.sent_at >= cutoff)
            .limit(1)
        )
        if result.scalar_one_or_none():
            log.info(f" {sig_dict['ticker']} cooldown — already sent "
                  f"{sig_dict['action']} within {base_hours}h")
            return

    now      = datetime.now()
    now_et   = datetime.now(_ET)           # New York time for display
    et_time  = now_et.strftime("%H:%M:%S") # "20:32:07 ET"
    emoji    = "🟢" if sig_dict["action"] == "BUY" else "🔴"

    # ── Broadcast channel (scale path: 1 API call vs N per-user DMs) ──────────
    # When TELEGRAM_BROADCAST_CHANNEL_ID is set, post once to the channel so all
    # subscribers see the signal without the per-user loop hitting Telegram's 30/sec limit.
    _broadcast_id = settings.telegram_broadcast_channel_id
    if _broadcast_id:
        try:
            _url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
            _msg = format_signal(sig_dict)
            async with aiohttp.ClientSession() as _sess:
                _r = await _sess.post(_url, json={"chat_id": _broadcast_id,
                                                   "text": _msg, "parse_mode": "Markdown"},
                                      ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8))
                _d = await _r.json()
                any_sent = bool(_d.get("ok"))
                if any_sent:
                    log.info(f" [broadcast] {sig_dict['ticker']} → channel {_broadcast_id}")
                else:
                    log.warning(f" [broadcast] {sig_dict['ticker']} failed: {_d.get('description')}")
        except Exception as _e:
            log.warning(f" [broadcast] error: {_e}")
            any_sent = False
    else:
        # ── Multi-user fan-out ──────────────────────────────────────────────────
        any_sent = await _fanout_to_subscribers(sig_dict, db_row, db)

    # ── Legacy single-user fallback (settings.telegram_chat_id) ────────────
    success = any_sent
    detail  = ""
    if not any_sent:
        success, detail = await send_telegram(sig_dict)

    log_msg = (f"{'✓' if success else '✗'} {emoji} "
               f"{sig_dict['action']} {sig_dict['ticker']} @ {sig_dict['price']:.2f} "
               f"(Conf {sig_dict['confidence']:.0f}%)")

    if success:
        db_row.is_sent = True
        db_row.sent_at = now
        # ── Delivery SLA tracking ────────────────────────────────────────────────
        if db_row.created_at:
            latency_s = (now - db_row.created_at).total_seconds()
            if latency_s > 300:  # > 5 minutes
                log.warning(
                    f"[sla] {sig_dict['ticker']} delivery latency {latency_s:.0f}s "
                    f"(created {db_row.created_at.isoformat()}, sent {now.isoformat()})"
                )
                # Fire-and-forget Telegram alert to owner
                try:
                    asyncio.ensure_future(_alert_sla_breach(
                        sig_dict['ticker'], sig_dict['action'], latency_s, settings
                    ))
                except Exception:
                    pass
        log.info(f" ✓ Telegram sent ({label}) — "
              f"{sig_dict['action']} {sig_dict['ticker']} @ {sig_dict['price']:.2f} "
              f"conf {sig_dict['confidence']:.0f}%")
        # Fire web push to all subscribers for high-confidence signals
        if sig_dict["confidence"] >= 70:
            asyncio.create_task(_push_web_notifications(sig_dict, db))
        # Webhook outbound — POST signal JSON to user's webhook_url with HMAC signature
        asyncio.create_task(_send_webhook_outbound(sig_dict, db))
    else:
        log.info(f" ✗ Telegram failed — {sig_dict['ticker']}: {detail}")

    db.add(SendLog(time=et_time,            # ET time
                   status="sent" if success else "fail",
                   message=log_msg))


async def _push_web_notifications(sig_dict: dict, db) -> None:
    """Send web push notifications to all subscribed users for a high-confidence signal."""
    try:
        from models import PushSubscription
        from services.push_svc import send_web_push
        subs = (await db.execute(select(PushSubscription))).scalars().all()
        if not subs:
            return
        emoji = "🟢" if sig_dict["action"] == "BUY" else "🔴"
        push_payload = {
            "title": f"{emoji} {sig_dict['action']} {sig_dict['ticker']} — {sig_dict['confidence']:.0f}% conf",
            "body": sig_dict.get("headline", f"Entry ${sig_dict.get('entry', sig_dict['price']):.2f} · Target ${sig_dict.get('target', 0):.2f}"),
            "tag": f"signal-{sig_dict['ticker']}-{sig_dict['action']}",
            "url": "/",
        }
        for sub in subs:
            sub_info = {"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh, "auth": sub.auth}}
            await asyncio.to_thread(send_web_push, sub_info, push_payload)
        log.info(f"[push] Web push sent to {len(subs)} subscriber(s) for {sig_dict['ticker']}")
    except Exception as e:
        log.warning(f"[push] Web push failed: {e}")


async def _send_webhook_outbound(sig_dict: dict, db) -> None:
    """POST signal JSON to each user's webhook_url (if set) with HMAC-SHA256 signature.
    Lets power users route signals to their own order management systems (e.g. TradingView bots).
    """
    try:
        import hashlib, hmac, json
        from models import User
        from sqlalchemy import select as _sel
        users_with_webhook = (await db.execute(
            _sel(User.webhook_url, User.id)
            .where(User.webhook_url.isnot(None))
            .where(User.is_active == True)
        )).all()
        if not users_with_webhook:
            return

        payload = json.dumps(sig_dict, default=str).encode()
        secret  = (get_settings().jwt_secret or "").encode()
        sig_hdr = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()

        async with aiohttp.ClientSession() as sess:
            for row in users_with_webhook:
                url = row[0]
                try:
                    async with sess.post(
                        url, data=payload,
                        headers={"Content-Type": "application/json",
                                 "X-Signal-Trade-Signature": sig_hdr},
                        ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=5)
                    ) as r:
                        log.debug(f"[webhook] user={row[1]} → {url} status={r.status}")
                except Exception as we:
                    log.debug(f"[webhook] user={row[1]} failed: {we}")
    except Exception as e:
        log.warning(f"[webhook] outbound error: {e}")


async def _compute_adaptive_weights() -> dict:
    """
    Query resolved sent signals to compute:
      - Global BUY/SELL win rates (used by signal_engine to nudge confidence)
      - Per-ticker win rates (used to de-rate cluster boost for historically weak tickers)

    Only kicks in once ≥10 resolved signals exist per action (global),
    and ≥3 resolved signals per ticker (per-ticker).
    """
    try:
        from datetime import timezone as _tz
        import math as _math

        async with AsyncSessionLocal() as db:
            rows = (await db.execute(
                select(Signal.ticker, Signal.action, Signal.outcome_pct, Signal.outcome_at)
                .where(Signal.outcome_pct.isnot(None))
                .where(Signal.is_sent == True)
                .order_by(Signal.outcome_at.asc())   # chronological — needed for streak calc
            )).all()

        if not rows:
            return {}

        from collections import defaultdict
        action_buckets:  dict = defaultdict(list)
        ticker_outcomes: dict = defaultdict(list)  # ticker → [(win_bool, outcome_at)]

        for ticker, action, pct, outcome_at in rows:
            action_buckets[action].append(pct)
            if action == "BUY":
                ticker_outcomes[ticker].append((pct > 0, outcome_at))
            elif action == "SELL":
                ticker_outcomes[ticker].append((pct < 0, outcome_at))

        weights: dict = {}
        now_utc = datetime.utcnow()

        # Global win rates — recency-weighted (exponential decay, halflife 60 days)
        for action, outcomes_raw in action_buckets.items():
            if len(outcomes_raw) < 10:
                continue
            if action not in ("BUY", "SELL"):
                continue
            wr = sum(1 for o in outcomes_raw if (o > 0 if action == "BUY" else o < 0)) / len(outcomes_raw)
            weights[f"{action}_win_rate"] = round(wr, 3)
            log.info(f" {action} historical win rate: {wr*100:.1f}% ({len(outcomes_raw)} signals)")

        # Per-ticker win rates (recency-weighted) + loss-streak tracking
        ticker_win_rates:   dict = {}
        ticker_loss_streaks: dict = {}

        _HALFLIFE_DAYS = 60.0   # outcomes from 60 days ago count at half weight

        for ticker, entries in ticker_outcomes.items():
            if len(entries) < 3:
                continue

            # Recency-weighted win rate
            w_win = 0.0
            w_total = 0.0
            for win_bool, ts in entries:
                age_days = (now_utc - ts).total_seconds() / 86400 if ts else _HALFLIFE_DAYS
                w = _math.exp(-age_days / _HALFLIFE_DAYS * _math.log(2))
                w_total += w
                if win_bool:
                    w_win += w
            if w_total > 0:
                ticker_win_rates[ticker] = round(w_win / w_total, 3)

            # Current consecutive loss streak (count backwards from most recent)
            streak = 0
            for win_bool, _ in reversed(entries):
                if not win_bool:
                    streak += 1
                else:
                    break
            if streak >= 2:
                ticker_loss_streaks[ticker] = streak

        if ticker_win_rates:
            weights["ticker_win_rates"] = ticker_win_rates
            log.debug(f" Per-ticker win rates computed for {len(ticker_win_rates)} tickers")
        if ticker_loss_streaks:
            weights["ticker_loss_streaks"] = ticker_loss_streaks
            log.info(f" Loss streaks: {dict(list(ticker_loss_streaks.items())[:8])}")

        return weights
    except Exception:
        return {}


async def _load_db_settings() -> dict:
    """Load persisted UI settings from DB (theme, auto_paper_trade, etc.)."""
    try:
        async with AsyncSessionLocal() as db:
            row = (await db.execute(
                select(AppSettings).where(AppSettings.id == 1)
            )).scalar_one_or_none()
            if row and row.data:
                return row.data
    except Exception:
        pass
    return {}


async def _maybe_paper_trade(
    sig_dict: dict,
    positions_map: dict,   # { symbol_upper: position_dict } from Alpaca
    settings,
    db_settings: dict,
):
    """
    Place an Alpaca paper trade for a qualifying signal.
    Rules:
      - auto_paper_trade must be True in DB settings
      - BUY/SELL only (HOLD skipped)
      - Confidence >= min_confidence
      - BUY  → skip if we already hold a long position in that ticker
      - SELL → if we hold a long, close it (take profit); else short-sell
      - market hours check
    """
    if not db_settings.get("auto_paper_trade"):
        return

    action = sig_dict.get("action")
    if action not in ("BUY", "SELL"):
        return

    if sig_dict["confidence"] < settings.min_confidence:
        return

    if not _market_hours_ok():
        return

    if not settings.alpaca_api_key or not settings.alpaca_api_secret:
        print("[paper] Alpaca keys not set — auto paper trade skipped")
        return

    from services import alpaca_rest

    ticker   = sig_dict["ticker"]
    price    = sig_dict.get("price") or sig_dict.get("entry") or 1
    notional = float(db_settings.get("paper_trade_notional", 1000.0))
    qty      = max(1, round(notional / price))
    pos      = positions_map.get(ticker.upper())

    # Guard: check buying power before placing BUY orders
    try:
        if action == "BUY":
            acct = await alpaca_rest.get_account(settings.alpaca_api_key, settings.alpaca_api_secret)
            buying_power = float(acct.get("buying_power") or 0)
            if buying_power < notional * 0.5:
                log.info(f" {ticker} BUY skipped — insufficient buying power "
                      f"(${buying_power:.0f} available, ${notional:.0f} needed). "
                      f"Reset your paper account at alpaca.markets.")
                return
    except Exception as e:
        log.info(f" account check failed: {e}")
        return

    try:
        if action == "BUY":
            if pos and pos.get("side") == "long":
                log.info(f" {ticker} BUY skipped — already long {pos['qty']} shares")
                return
            order = await alpaca_rest.place_order(
                settings.alpaca_api_key, settings.alpaca_api_secret,
                ticker, qty, "buy",
            )
            log.info(f" ✓ AUTO BUY  {ticker} {qty}sh @ ~${price:.2f} "
                  f"| order {order.get('id','?')[:8]} status={order.get('status')}")

        else:  # SELL
            if pos and pos.get("side") == "long":
                order = await alpaca_rest.close_position(
                    settings.alpaca_api_key, settings.alpaca_api_secret, ticker
                )
                log.info(f" ✓ AUTO CLOSE long {ticker} — SELL signal received")
            else:
                if pos and pos.get("side") == "short":
                    log.info(f" {ticker} SELL skipped — already short {pos['qty']} shares")
                    return
                order = await alpaca_rest.place_order(
                    settings.alpaca_api_key, settings.alpaca_api_secret,
                    ticker, qty, "sell",
                )
                log.info(f" ✓ AUTO SELL {ticker} {qty}sh @ ~${price:.2f} "
                      f"| order {order.get('id','?')[:8]} status={order.get('status')}")

    except Exception as e:
        log.info(f" ✗ {ticker} {action} failed: {e}")



async def _alert_telegram(text: str):
    """Send a plain alert message via Telegram (best-effort, never raises)."""
    try:
        s = get_settings()
        if not s.telegram_bot_token or not s.telegram_chat_id:
            return
        url = f"https://api.telegram.org/bot{s.telegram_bot_token}/sendMessage"
        async with aiohttp.ClientSession() as sess:
            await sess.post(url, json={"chat_id": s.telegram_chat_id, "text": text},
                            ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=6))
    except Exception:
        pass


_last_analytics_compute: float = 0.0
_ANALYTICS_COMPUTE_INTERVAL = 300  # re-compute at most every 5 minutes


async def _precompute_analytics() -> None:
    """
    Pre-compute and cache the backtest summary after each scan cycle.

    Eliminates expensive GROUP BY queries on every /api/signals/backtest
    request. Results are stored in redis_cache (or in-process dict fallback)
    with a 5-minute TTL. The backtest endpoint checks this cache first.
    """
    global _last_analytics_compute
    import time as _t
    now = _t.monotonic()
    if now - _last_analytics_compute < _ANALYTICS_COMPUTE_INTERVAL:
        return
    _last_analytics_compute = now

    try:
        from services.redis_cache import cache_set
        from sqlalchemy import select, func, case
        from models import Signal

        async with AsyncSessionLocal() as db:
            rows = (await db.execute(
                select(
                    Signal.action,
                    func.count(Signal.id).label("n"),
                    func.avg(Signal.outcome_pct).label("avg_ret"),
                    func.sum(
                        case((Signal.outcome_pct > 0, 1), else_=0)
                    ).label("wins"),
                ).where(
                    Signal.outcome_pct.isnot(None),
                    Signal.action.in_(["BUY", "SELL"]),
                ).group_by(Signal.action)
            )).all()

        if not rows:
            return

        total_n = sum(r.n for r in rows)
        total_wins = sum(r.wins for r in rows)
        summary = {
            "resolved":   total_n,
            "win_rate":   round(total_wins / total_n * 100, 1) if total_n else None,
            "avg_return": round(sum(r.avg_ret * r.n for r in rows) / total_n, 3) if total_n else None,
            "by_action":  [
                {"action": r.action, "count": r.n,
                 "win_rate": round(r.wins / r.n * 100, 1) if r.n else None,
                 "avg_return": round(r.avg_ret, 3) if r.avg_ret is not None else None}
                for r in rows
            ],
            "computed_at": datetime.utcnow().isoformat() + "Z",
        }
        await cache_set("analytics:backtest_summary", summary, ttl=_ANALYTICS_COMPUTE_INTERVAL)
        log.debug(f"[analytics] backtest summary cached (n={total_n})")
    except Exception as e:
        log.debug(f"[analytics] pre-compute failed (non-critical): {e}")


async def run_scan(broadcast_fn=None):
    """
    Full scan cycle:
      1. Fetch market-wide context (F&G + Macro) once.
      2. Batch-download history for active watchlist tickers.
      3. Pre-filter: skip .info re-fetch for stable tickers (< 1% move, recent signal).
      4. Fetch ticker .info sequentially (rate-limited).
      5. Generate signals (news + EDGAR fetched concurrently per ticker).
      6. Persist to SQLite.
      7. Auto-send qualifying signals (time-of-day + cooldown checks).
      8. Update outcomes for old sent signals.
      9. Broadcast via WebSocket.
    """
    settings = get_settings()
    tickers  = await _get_scan_tickers(settings)

    # Clear stale data-quality counters at the start of each cycle
    global _data_quality
    _data_quality = {t: _data_quality.get(t, 0) for t in tickers}  # prune removed tickers

    # Evict tickers no longer in the watchlist to prevent unbounded growth
    global _diff_state
    _diff_state = {t: _diff_state[t] for t in tickers if t in _diff_state}

    stale_cutoff = datetime.utcnow() - timedelta(hours=8)

    # ── Step 1: market-wide context + adaptive weights ───────────────────
    try:
        fg, macro, pc, breadth, aaii, cot = await asyncio.gather(
            get_fear_greed(), get_macro_context(), get_put_call_ratio(), get_market_breadth(),
            get_aaii_sentiment(), get_cot_signal()
        )
        market_ctx = {"fear_greed": fg, "macro": macro, "put_call": pc, "breadth": breadth,
                      "aaii": aaii, "cot": cot}
        fg_label = fg["label"] if fg else "unknown"
        breadth_str = f"{breadth['pct_above_200d']:.0f}% >200d" if breadth else "?"
        aaii_str = f"AAII {aaii['spread']:+.0f}% ({aaii['signal']})" if aaii and aaii.get("spread") is not None else "AAII N/A"
        log.info(f" F&G = {fg['score'] if fg else '?'} ({fg_label}) | "
              f"VIX = {macro.get('vix', '?') if macro else '?'} | "
              f"Macro score = {macro.get('macro_score', 0) if macro else 0} | "
              f"Breadth = {breadth_str} | {aaii_str}")
    except Exception as e:
        log.info(f" market context failed: {e}")
        market_ctx = {}

    try:
        market_ctx["adaptive_weights"] = await _compute_adaptive_weights()
    except Exception:
        pass

    # Load calibration map (fit weekly, applied every scan from disk cache)
    try:
        from services.calibration import load_calibration
        market_ctx["calibration_map"] = load_calibration()
    except Exception:
        pass

    # ── HMM Macro Regime (cached 1h — expensive fit) ─────────────────────────
    try:
        from services.macro_regime import get_macro_regime
        regime_data = await get_macro_regime()
        market_ctx["hmm_regime"] = regime_data
        log.info(f" HMM regime: {regime_data.get('regime','?')} "
                 f"bull={regime_data.get('bull_prob',0):.0%} "
                 f"trans_risk={regime_data.get('transition_risk',0):.0%}")
    except Exception as e:
        log.debug(f" HMM regime failed (non-critical): {e}")

    # ── Supply Chain signals (cached 4h) ──────────────────────────────────────
    try:
        from services.supply_chain import get_supply_chain_signals
        market_ctx["supply_chain"] = await get_supply_chain_signals()
    except Exception as e:
        log.debug(f" Supply chain data failed (non-critical): {e}")

    # ── Step 1b: 13F institutional flow (quarterly, cached 6h) ──────────────
    try:
        from services.institutional import get_institutional_signals
        inst_list = await get_institutional_signals(settings.tickers)
        # Index by ticker for O(1) lookup in signal_engine
        market_ctx["institutional_signals"] = {
            s["ticker"]: s for s in inst_list
        }
        if inst_list:
            log.info(f" 13F: {len(inst_list)} watchlist tickers with institutional activity")
    except Exception as e:
        log.debug(f" 13F fetch failed (non-critical): {e}")

    # ── Step 1g: Dark Pool Block Prints (cached 1h) ──────────────
    try:
        from services.dark_pool import get_dark_pool_flow
        market_ctx["dark_pool"] = await get_dark_pool_flow(settings.tickers)
    except Exception as e:
        log.debug(f" Dark pool fetch failed (non-critical): {e}")

    # ── Step 1h: Corporate Events (Wall Street Horizon, cached 4h) ───────────
    try:
        from services.corporate_events import get_corporate_events
        corp_events = await get_corporate_events()
        market_ctx["corporate_events"] = corp_events
        n_ev = len(corp_events.get("events", []))
        if n_ev:
            log.info(f" Corporate events: {n_ev} upcoming across {len(corp_events.get('by_ticker', {}))} tickers")
    except Exception as e:
        log.debug(f" Corporate events fetch failed (non-critical): {e}")

    # ── Step 1i: ETF Fund Flows (cached 4h) ───────────────────────────────────
    try:
        from services.etf_flows import get_etf_flows
        market_ctx["etf_flows"] = await get_etf_flows()
    except Exception as e:
        log.debug(f" ETF flows fetch failed (non-critical): {e}")

    # ── Step 1j: Economy data from Massive (cached 1h, no FRED key needed) ───
    try:
        from services.massive_economy import get_economy_data
        eco = await get_economy_data()
        if eco:
            market_ctx["massive_economy"] = eco
    except Exception as e:
        log.debug(f" Massive economy fetch failed (non-critical): {e}")

    # ── Step 1k: ETF Constituents preload (cached 24h) ────────────────────────
    try:
        from services.etf_constituents import preload_all
        await preload_all()  # warms the constituent cache silently
    except Exception as e:
        log.debug(f" ETF constituents preload failed (non-critical): {e}")

    # ── Step 1d: Paper portfolio sector exposure (for correlation limits) ────
    if settings.alpaca_api_key and settings.alpaca_api_secret:
        try:
            from services import alpaca_rest
            from services.sector import SECTOR_MAP as SECTOR_ETF_MAP
            positions_list = await alpaca_rest.get_positions(
                settings.alpaca_api_key, settings.alpaca_api_secret
            )
            if positions_list:
                total_mv = sum(
                    abs(float(p.get("market_value") or 0)) for p in positions_list
                )
                sector_exposure: dict[str, float] = {}
                if total_mv > 0:
                    for p in positions_list:
                        sym = p.get("symbol", "").upper()
                        mv  = abs(float(p.get("market_value") or 0))
                        # Map ticker → sector ETF via the static SECTOR_ETF_MAP
                        etf = SECTOR_ETF_MAP.get(sym)
                        if etf:
                            sector_exposure[etf] = sector_exposure.get(etf, 0) + mv / total_mv * 100
                market_ctx["portfolio_ctx"] = {
                    "sector_exposure": sector_exposure,  # {sector_etf: pct_of_portfolio}
                    "total_positions": len(positions_list),
                    "total_mv": round(total_mv, 2),
                }
                log.info(
                    f" Portfolio: {len(positions_list)} open positions, "
                    f"sector exposure: {', '.join(f'{k} {v:.0f}%' for k,v in sector_exposure.items())}"
                )

                # ── PCA Risk Model — detect latent factor concentration ────────────
                # Runs concurrently after basic sector context is set.
                if len(positions_list) >= 3:
                    try:
                        from services.pca_risk import compute_pca_risk
                        pos_values = {
                            p.get("symbol", "").upper(): abs(float(p.get("market_value") or 0))
                            for p in positions_list
                        }
                        pca_result = await compute_pca_risk(pos_values)
                        if pca_result:
                            market_ctx["portfolio_ctx"]["pca_risk"] = pca_result
                            if pca_result.get("concentration_warning"):
                                log.info(
                                    f" PCA: concentrated on '{pca_result['dominant_factor']}' "
                                    f"({pca_result['dominant_exposure']:.0%}) — "
                                    f"haircut={pca_result['haircut_pct']:.0f}%"
                                )
                    except Exception as pca_e:
                        log.debug(f" PCA risk model failed (non-critical): {pca_e}")
        except Exception as e:
            log.debug(f" Portfolio context failed (non-critical): {e}")

    # ── Step 1c: Cointegration / pairs trading signals (cached 2h) ──────────
    try:
        from services.cointegration import get_pairs_signals
        pairs_signals = await get_pairs_signals(settings.tickers)
        market_ctx["pairs_signals"] = pairs_signals
        if pairs_signals:
            log.info(f" Pairs: {len(pairs_signals)} divergence signals detected")
    except Exception as e:
        log.debug(f" Pairs signal fetch failed (non-critical): {e}")

    # ── Step 1e: Weight overrides from app_settings + factor mining output ───
    # weight_overrides lets the owner permanently cap cluster/orthogonality boosts
    # without touching the codebase — survives the Sunday factor mining job.
    # factor_weights gives the engine the mined OOS-Sharpe rankings for source combos.
    try:
        db_settings_now = await _load_db_settings()
        wo = db_settings_now.get("weight_overrides") or {}
        market_ctx["weight_overrides"] = wo
        if wo:
            log.debug(f" Weight overrides active: {wo}")
    except Exception as e:
        log.debug(f" Weight overrides load failed: {e}")

    try:
        from services.factor_miner import load_factor_weights
        fw = load_factor_weights()
        if fw and not fw.get("skipped"):
            market_ctx["factor_weights"] = fw
            log.debug(f" Factor weights loaded: {fw.get('combinations_tested', '?')} combos, top={fw.get('top_factors', [{}])[0].get('label', '?') if fw.get('top_factors') else '?'}")
    except Exception as e:
        log.debug(f" Factor weights load failed: {e}")

    # ── Step 1f: BUY:SELL saturation circuit breaker ────────────────────
    # If the rolling 7-day BUY:SELL ratio exceeds 4:1, the system is in a
    # structurally over-optimistic state. Pass this flag so the signal engine
    # raises its effective BUY threshold to 42 for the current scan cycle,
    # suppressing marginal BUY signals until the ratio normalises.
    try:
        async with AsyncSessionLocal() as db:
            from sqlalchemy import text as _sa_text
            _ratio_row = (await db.execute(_sa_text("""
                SELECT
                    SUM(CASE WHEN action='BUY'  THEN 1 ELSE 0 END) AS buys,
                    SUM(CASE WHEN action='SELL' THEN 1 ELSE 0 END) AS sells
                FROM signals
                WHERE date(created_at) >= date('now', '-7 days')
                  AND action IN ('BUY', 'SELL')
            """))).fetchone()
        _buys  = _ratio_row[0] or 0
        _sells = _ratio_row[1] or 1  # avoid div-by-zero
        _buy_sell_ratio = round(_buys / _sells, 2)
        market_ctx["buy_sell_ratio"]  = _buy_sell_ratio
        market_ctx["buy_saturated"]   = _buy_sell_ratio > 4.0
        if _buy_sell_ratio > 4.0:
            log.info(f" BUY:SELL circuit breaker ACTIVE — 7d ratio {_buy_sell_ratio:.1f}:1 (>4.0 threshold). BUY threshold raised to 42.")
        else:
            log.info(f" BUY:SELL ratio (7d): {_buy_sell_ratio:.1f}:1 — within normal range.")
    except Exception as e:
        log.debug(f" BUY:SELL ratio check failed (non-critical): {e}")
        market_ctx["buy_saturated"] = False

    # ── Step 1l: news batch prefetch (154 tickers → 3 API calls) ────────────────
    try:
        from services.benzinga_news import prefetch_news_batch
        await prefetch_news_batch(tickers)
    except Exception as e:
        log.debug(f" news batch prefetch failed (non-critical): {e}")

    # ── Step 2: batch history ────────────────────────────────────────────
    try:
        histories = await get_histories_batch(tickers, period="1y", interval="1d")
        log.info(f" history batch: {len(histories)}/{len(tickers)} tickers loaded")
    except Exception as e:
        log.info(f" history batch failed: {e}")
        histories = {}

    # ── Data quality check ───────────────────────────────────────────────
    _bad_tickers = _check_data_quality(histories, settings)
    if _bad_tickers:
        _alert_msg = f"⚠️ Data quality alert: {len(_bad_tickers)} ticker(s) have ≥5 consecutive null fetches: {', '.join(_bad_tickers[:10])}"
        log.warning(_alert_msg)
        try:
            await send_telegram({"action": "DATA_ALERT", "ticker": "SYSTEM",
                                 "confidence": 0, "headline": _alert_msg,
                                 "price": 0, "sentiment": 0, "style": "swing",
                                 "sources": [], "rationale": [], "ts": datetime.utcnow().isoformat() + "Z"})
        except Exception:
            pass

    # ── Step 3: quotes batch for pre-filtering + outcome tracking ────────
    try:
        quotes = await get_quotes_batch(tickers)
        quote_map = {q["t"]: q for q in quotes}
    except Exception as e:
        log.info(f" quotes batch failed: {e}")
        quotes, quote_map = [], {}

    # ── Step 4: pre-filtered .info fetch ─────────────────────────────────
    # Skip .info for tickers where price moved < threshold AND a recent active
    # signal already exists — saves significant time on quiet days.
    try:
        async with AsyncSessionLocal() as db:
            recent_sigs = (await db.execute(
                select(Signal.ticker)
                .where(Signal.is_active == True)
                .where(Signal.created_at >= stale_cutoff)  # same 8h window
            )).scalars().all()
        recent_set = set(recent_sigs)

        tickers_needing_info = []
        for t in tickers:
            q = quote_map.get(t)
            if q and abs(q.get("c", 99)) < _MOVEMENT_THRESHOLD and t in recent_set:
                pass  # stable + has recent signal — skip info re-fetch
            else:
                tickers_needing_info.append(t)

        infos = await get_infos_sequential(tickers_needing_info)
        # Extend with empty dicts for skipped tickers (engine handles missing gracefully)
        for t in tickers:
            if t not in infos:
                infos[t] = {}
        log.info(f" info fetch: {len(tickers_needing_info)}/{len(tickers)} tickers "
              f"({len(tickers) - len(tickers_needing_info)} skipped — stable)")
    except Exception as e:
        log.info(f" info fetch failed: {e}")
        infos = {}

    # ── Step 4b: differential scan — identify stable tickers to skip ────────
    # Stable = price moved < 0.5% AND volume < 1.3× avg AND active signal < 2h old.
    # Skipped tickers get their price + timestamp updated in-place in the DB.
    # Expected: skip 80-100 of 154 tickers per cycle → ~5× throughput increase.
    _two_hr_ago = datetime.utcnow() - timedelta(hours=_DIFF_SIGNAL_MAX_AGE_H)
    try:
        async with AsyncSessionLocal() as _diff_db:
            _recent_sig_tickers = set((await _diff_db.execute(
                select(Signal.ticker)
                .where(Signal.is_active == True)
                .where(Signal.created_at >= _two_hr_ago)
            )).scalars().all())
    except Exception:
        _recent_sig_tickers = set()

    stable_tickers: set[str] = set()
    for t in tickers:
        q = quote_map.get(t)
        if not q:
            continue
        prev = _diff_state.get(t)
        if not prev:
            continue  # no baseline yet — must generate
        if t not in _recent_sig_tickers:
            continue  # no active signal — must generate fresh
        price_chg = abs((q["p"] - prev["price"]) / max(prev["price"], 0.01) * 100)
        # Volume ratio — use today vol vs stored avg; skip if we don't have baseline
        vol_ratio = 1.0
        h = histories.get(t)
        if h is not None and len(h) >= 5:
            try:
                import pandas as _pd
                today_vol = float(h["Volume"].iloc[-1])
                avg_vol   = float(h["Volume"].iloc[-21:-1].mean())
                if avg_vol > 0:
                    vol_ratio = today_vol / avg_vol
            except Exception:
                pass
        if price_chg < _DIFF_PRICE_THRESHOLD and vol_ratio < _DIFF_VOL_THRESHOLD:
            stable_tickers.add(t)

    active_tickers = [t for t in tickers if t not in stable_tickers]
    if stable_tickers:
        log.info(f" differential scan: {len(stable_tickers)} tickers skipped "
                 f"(stable <{_DIFF_PRICE_THRESHOLD}% move, vol <{_DIFF_VOL_THRESHOLD}×) "
                 f"| {len(active_tickers)} active")
        # Bulk-update price for stable tickers (no new signal row, no re-send)
        try:
            async with AsyncSessionLocal() as _su_db:
                for t in stable_tickers:
                    q = quote_map.get(t)
                    if q:
                        await _su_db.execute(
                            update(Signal)
                            .where(Signal.ticker == t)
                            .where(Signal.is_active == True)
                            .values(price=q["p"], change_pct=q.get("c", 0))
                        )
                await _su_db.commit()
        except Exception as e:
            log.debug(f" differential price update failed: {e}")

    # Update diff state for all tickers that have a current quote
    for t in tickers:
        q = quote_map.get(t)
        if q:
            _diff_state[t] = {"price": q["p"], "ts": datetime.utcnow()}

    # ── Step 5: generate signals ─────────────────────────────────────────
    try:
        signals = await scan_all(
            active_tickers,
            market_ctx=market_ctx,
            histories={t: histories[t] for t in active_tickers if t in histories},
            infos={t: infos.get(t, {}) for t in active_tickers},
        )
    except Exception as e:
        log.info(f" scan_all failed: {e}")
        return

    # new_signals entries are 3-tuples: (sig_dict, db_row, force_resend)
    new_signals:      list[tuple[dict, Signal, bool]] = []
    refreshed_unsent: list[tuple[dict, Signal, bool]] = []

    # ── Step 6: persist (smart daily deduplication) ──────────────────────
    # Rules (per trading day, midnight ET boundary):
    #   • Same ticker, same direction, conf delta < 15pp → silent refresh
    #     (update price/confidence in place, no new row, no Telegram re-send)
    #   • Same ticker, direction flipped → deactivate old, create new,
    #     bypass 24h Telegram cooldown (force_resend=True)
    #   • Same ticker, same direction, conf delta ≥ 15pp → deactivate old,
    #     create new, normal 24h Telegram cooldown applies
    #   • No active signal from today → deactivate any stale signal, create new
    today_start = _today_start_utc()

    async with AsyncSessionLocal() as db:
        for sig in signals:
            # Find most recent active signal for this ticker (any direction)
            result = await db.execute(
                select(Signal)
                .where(Signal.ticker == sig["ticker"])
                .where(Signal.is_active == True)
                .order_by(desc(Signal.created_at))
                .limit(1)
            )
            existing = result.scalar_one_or_none()

            force_resend = False

            if existing and existing.created_at and existing.created_at >= today_start:
                # ── Same trading day ──────────────────────────────────────
                conf_delta        = abs(sig["confidence"] - (existing.confidence or 0))
                direction_changed = existing.action != sig["action"]

                if not direction_changed and conf_delta < _CONF_CHANGE_THRESHOLD:
                    # Prediction essentially unchanged — silent in-place refresh
                    existing.price              = sig["price"]
                    existing.change             = sig["change"]
                    existing.change_pct         = sig["changePct"]
                    existing.confidence         = sig["confidence"]
                    existing.confidence_warning = bool(sig.get("confidence_warning", False))
                    existing.rationale          = sig["rationale"]
                    existing.sources            = sig["sources"]
                    existing.headline           = sig["headline"]
                    existing.plain_english      = sig.get("plain_english")
                    existing.session            = sig.get("session")
                    existing.days_to_earnings   = sig.get("daysToEarnings")
                    existing.next_earnings_date = sig.get("nextEarningsDate")
                    existing.sector_etf         = sig.get("sectorEtf")
                    existing.rs_vs_sector       = sig.get("rsVsSector")
                    existing.style              = sig.get("style", existing.style)
                    # Still queue for send if never sent (first send of the day)
                    if not existing.is_sent:
                        refreshed_unsent.append((sig, existing, False))
                    continue  # no new row for minor updates

                # Significant change — log it and create a fresh signal
                if direction_changed:
                    force_resend = True
                    log.info(f" {sig['ticker']} direction flip "
                             f"{existing.action}→{sig['action']} "
                             f"(conf {existing.confidence:.0f}%→{sig['confidence']:.0f}%)")
                else:
                    log.info(f" {sig['ticker']} confidence surge "
                             f"{existing.confidence:.0f}%→{sig['confidence']:.0f}% "
                             f"(Δ{conf_delta:.0f}pp)")

            # Deactivate all active signals for this ticker before inserting new
            await db.execute(
                update(Signal)
                .where(Signal.ticker == sig["ticker"])
                .where(Signal.is_active == True)
                .values(is_active=False)
            )

            # Expiry: intraday → today 4pm ET; swing → +10 calendar days; position → +30 days
            _now_et  = datetime.now(_ET)
            _style   = sig.get("style", "swing")
            if _style == "intraday":
                _close_et = _now_et.replace(hour=16, minute=5, second=0, microsecond=0)
                if _now_et >= _close_et:
                    _close_et += timedelta(days=1)
                _expires = _close_et.astimezone(pytz.utc).replace(tzinfo=None)
            elif _style == "position":
                _expires = datetime.utcnow() + timedelta(days=30)
            else:  # swing
                _expires = datetime.utcnow() + timedelta(days=10)

            row = Signal(
                ticker     = sig["ticker"],
                company    = sig.get("company"),
                action     = sig["action"],
                confidence = sig["confidence"],
                confidence_warning = bool(sig.get("confidence_warning", False)),
                price      = sig["price"],
                change     = sig["change"],
                change_pct = sig["changePct"],
                entry      = sig.get("entry"),
                stop       = sig.get("stop"),
                target     = sig.get("target"),
                rr         = sig.get("rr"),
                headline   = sig["headline"],
                sentiment  = sig.get("sentiment", 0),
                style      = sig.get("style", "swing"),
                sources    = sig.get("sources", []),
                rationale  = sig.get("rationale", []),
                plain_english      = sig.get("plain_english"),
                session            = sig.get("session"),
                days_to_earnings   = sig.get("daysToEarnings"),
                next_earnings_date = sig.get("nextEarningsDate"),
                sector_etf         = sig.get("sectorEtf"),
                rs_vs_sector       = sig.get("rsVsSector"),
                expires_at         = _expires,
            )
            db.add(row)
            new_signals.append((sig, row, force_resend))

        await db.commit()

    # ── Step 7: auto-send + auto paper trade ────────────────────────────
    db_settings = await _load_db_settings()

    # Pre-load open positions once so _maybe_paper_trade can deduplicate cheaply
    positions_map: dict = {}
    if db_settings.get("auto_paper_trade") and settings.alpaca_api_key:
        try:
            from services import alpaca_rest
            positions_list = await alpaca_rest.get_positions(
                settings.alpaca_api_key, settings.alpaca_api_secret
            )
            positions_map = {p["symbol"].upper(): p for p in positions_list}
        except Exception as e:
            log.info(f" positions fetch failed: {e}")

    if settings.auto_send_notifications:
        async with AsyncSessionLocal() as db:
            seen = set()
            candidates = []
            new_set = {id(row) for _, row, _ in new_signals}
            for sig, row, force in (new_signals + refreshed_unsent):
                key = (sig["ticker"], sig["action"])
                if key not in seen:
                    seen.add(key)
                    label = "new" if id(row) in new_set else "unsent"
                    candidates.append((sig, row, label, force))

            for sig, row, label, force in candidates:
                merged = await db.merge(row)
                await _maybe_send(sig, merged, settings, db, label, force_resend=force)
                await _maybe_paper_trade(sig, positions_map, settings, db_settings)

            await db.commit()
    elif db_settings.get("auto_paper_trade"):
        # Paper trading on but Telegram off — still run paper trades
        seen = set()
        for sig, row, _force in (new_signals + refreshed_unsent):
            key = (sig["ticker"], sig["action"])
            if key not in seen:
                seen.add(key)
                await _maybe_paper_trade(sig, positions_map, settings, db_settings)

    # ── Step 8: update outcomes ──────────────────────────────────────────
    try:
        await _update_outcomes(quotes)
    except Exception as e:
        log.info(f" outcome update failed: {e}")

    # ── Step 9: price alert evaluation ──────────────────────────────────
    # alert_evaluator already has all current quotes from get_quotes_batch().
    # Crossing a user's target price fires Telegram + Discord notification.
    try:
        from services.alert_evaluator import evaluate_price_alerts
        async with AsyncSessionLocal() as db:
            await evaluate_price_alerts(db)
    except Exception as e:
        log.debug(f" price alert eval failed (non-critical): {e}")

    # ── Step 10: broadcast ───────────────────────────────────────────────
    if broadcast_fn:
        for sig, _, _force in new_signals:
            await broadcast_fn({"type": "new_signal", "signal": sig})

        prices = {q["t"]: {"price": q["p"], "change": q["c"]} for q in quotes}
        await broadcast_fn({"type": "price_update", "quotes": quotes, "prices": prices})

        if market_ctx:
            await broadcast_fn({"type": "market_context", "data": market_ctx})

    log.info(f" {datetime.now().strftime('%H:%M:%S')} — "
          f"scanned {len(tickers)} tickers, {len(new_signals)} new, "
          f"{len(signals) - len(new_signals)} refreshed "
          f"({len(refreshed_unsent)} unsent queued)")

    # ── Step 11: analytics pre-computation ──────────────────────────────
    # Compute backtest summary in background after each scan so heavy GROUP BY
    # queries aren't triggered on every /api/signals/backtest request.
    # Fire-and-forget — never blocks the scan cycle.
    asyncio.ensure_future(_precompute_analytics())
