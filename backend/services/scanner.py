import asyncio
import logging
import ssl
from datetime import datetime, timedelta, timezone
from datetime import time as dtime
from time import monotonic

import certifi
import pytz

_SSL_CTX = ssl.create_default_context(cafile=certifi.where())

log = logging.getLogger("scanner")

import aiohttp
from config import TIERS, get_settings
from database import AsyncSessionLocal
from models import AppSettings, SendLog, Signal, SignalAlert, SignalDelivery, User, SignalGateTrace, ModelShadowScore
from sqlalchemy import desc, select, update

from services.aaii import get_aaii_sentiment
from services.breadth import get_market_breadth
from services.cot import get_cot_signal
from services.fear_greed import get_fear_greed, get_put_call_ratio
from services.macro import get_macro_context
from services.market_data import get_histories_batch, get_infos_sequential, get_quotes_batch
from services.signal_engine import scan_all
from services.telegram_svc import format_signal, send_telegram

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
        if df is None or len(df) < 5 or float(df["Close"].squeeze().iloc[-1]) == 0:
            _data_quality[ticker] = _data_quality.get(ticker, 0) + 1
            if _data_quality[ticker] == 5:  # only alert on the transition to 5
                degraded.append(ticker)
        else:
            _data_quality[ticker] = 0  # reset on valid data
    return degraded


async def _alert_sla_breach(ticker: str, action: str, latency_s: float, settings):
    """Notify owner when signal delivery exceeds 5-minute SLA."""
    msg = (
        f"⚠️ SLA breach: {action} {ticker} took {latency_s / 60:.1f}min to deliver (target ≤5min). Check scanner health."
    )
    try:
        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        async with aiohttp.ClientSession() as sess:
            await sess.post(
                url,
                json={"chat_id": settings.telegram_chat_id, "text": msg},
                ssl=_SSL_CTX,
                timeout=aiohttp.ClientTimeout(total=5),
            )
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
    subscribers = (
        (
            await db.execute(
                select(User).where(
                    User.telegram_chat_id.isnot(None),
                    User.is_active == True,
                )
            )
        )
        .scalars()
        .all()
    )

    # Filter to those with telegram access (basic+, pro, or owner)
    eligible = [
        u
        for u in subscribers
        if u.is_owner
        or (u.subscription_status == "active" and TIERS.index(u.subscription_tier) >= TIERS.index("basic"))
    ]

    if not eligible:
        return False

    # Check for already-delivered (dedup)
    delivered_user_ids = set()
    if db_row.id:
        rows = (
            (await db.execute(select(SignalDelivery.user_id).where(SignalDelivery.signal_id == db_row.id)))
            .scalars()
            .all()
        )
        delivered_user_ids = set(rows)

    # Load per-ticker signal alert rules for this ticker → {user_id: SignalAlert}
    ticker = sig_dict.get("ticker", "")
    _alert_rows = (
        (
            await db.execute(
                select(SignalAlert).where(
                    SignalAlert.ticker == ticker,
                    SignalAlert.is_active == True,
                )
            )
        )
        .scalars()
        .all()
    )
    ticker_rules: dict[int, SignalAlert] = {a.user_id: a for a in _alert_rows}

    # PROD-3: per-user notification prefs (saved by routers/me.py in AppSettings).
    # Key format mirrors me.py:_user_pref_key. We filter ONLY users who explicitly
    # saved prefs — the defaults are opinionated (actions=["BUY","SELL"], score_min=50), so
    # applying them to users who never configured prefs would silently stop all
    # SELL / low-score delivery. stored=None ⇒ no PROD-3 filtering (legacy behavior).
    _app_row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    _app_data = _app_row.data if (_app_row is not None and isinstance(_app_row.data, dict)) else {}

    def _user_prefs(uid: int) -> dict | None:
        _p = _app_data.get(f"user_{uid}_notification_prefs")
        return _p if isinstance(_p, dict) else None

    message_text = format_signal(sig_dict)
    url = f"https://api.telegram.org/bot{s.telegram_bot_token}/sendMessage"
    any_success = False

    global_min_conf = get_settings().min_confidence
    sent_chat_ids: set[str] = set()  # dedup: never send twice to the same chat
    from services.delivery_manager import queue_delivery

    for user in eligible:
        if user.id in delivered_user_ids:
            continue
        if user.telegram_chat_id in sent_chat_ids:
            log.info(f" [fanout] skipped user={user.id} — chat {user.telegram_chat_id} already received this signal")
            continue
        # PROD-3: telegram master toggle — applies even to ticker-rule matches.
        _prefs = _user_prefs(user.id)
        if _prefs is not None and _prefs.get("telegram") is False:
            log.info(f" [fanout] user={user.id} telegram notifications disabled — skipped")
            continue
        # Per-ticker signal alert rules override the global confidence threshold.
        # If the user has an active rule for this ticker, apply it; otherwise
        # fall back to the user's global override or the system default.
        rule = ticker_rules.get(user.id)
        if rule is not None:
            if sig_dict.get("confidence", 0) < rule.min_confidence:
                log.info(f" [fanout] user={user.id} ticker rule {ticker}>={rule.min_confidence:.0f}% not met — skipped")
                continue
            if rule.action_filter != "any" and sig_dict.get("action") != rule.action_filter:
                log.info(
                    f" [fanout] user={user.id} ticker rule action_filter={rule.action_filter} != {sig_dict.get('action')} — skipped"
                )
                continue
        else:
            # PROD-3: apply explicit per-user sector / score / action filters.
            if _prefs is not None:
                _secs = _prefs.get("sectors") or []
                if _secs and sig_dict.get("sectorEtf") not in _secs:
                    log.info(f" [fanout] user={user.id} sector {sig_dict.get('sectorEtf')} not in {_secs} — skipped")
                    continue
                _smin = _prefs.get("score_min")
                if _smin is not None and (sig_dict.get("raw_score") or 0) < _smin:
                    log.info(f" [fanout] user={user.id} raw_score < score_min {_smin} — skipped")
                    continue
                _acts = _prefs.get("actions") or []
                if _acts and sig_dict.get("action") not in _acts:
                    log.info(f" [fanout] user={user.id} action {sig_dict.get('action')} not in {_acts} — skipped")
                    continue
            # Confidence: prefs.min_conf > user column override > global default.
            if _prefs is not None and _prefs.get("min_conf") is not None:
                user_min = _prefs["min_conf"]
            elif user.min_confidence_override is not None:
                user_min = user.min_confidence_override
            else:
                user_min = global_min_conf
            if sig_dict.get("confidence", 0) < user_min:
                log.info(
                    f" [fanout] user={user.id} threshold {user_min:.0f}% > conf {sig_dict['confidence']:.0f}% — skipped"
                )
                continue

        # TSYS-3c: Check digest preference
        if _prefs is not None and _prefs.get("digest_vs_realtime") == "digest":
            log.info(f" [fanout] user={user.id} digest preference active — skipping realtime delivery")
            continue

        try:
            tg_payload = {
                "chat_id": user.telegram_chat_id,
                "text": message_text,
                "parse_mode": "Markdown",
            }
            await queue_delivery(
                signal_id=db_row.id,
                user_id=user.id,
                channel="telegram",
                payload=tg_payload,
            )
            any_success = True
            sent_chat_ids.add(user.telegram_chat_id)
            log.info(f" [fanout] queued Telegram delivery for user={user.id} chat={user.telegram_chat_id}")
        except Exception as e:
            log.warning(f" [fanout] error queuing Telegram for user={user.id}: {e}")

        # Discord delivery — for users with a webhook configured. Runs inside the
        # per-user loop so it inherits the SAME gating as Telegram (already-delivered
        # dedup, confidence threshold, notification prefs, digest mode). A standalone
        # Discord pass would bypass all of those and double-deliver.
        discord_webhook = getattr(user, "discord_webhook_url", None)
        if discord_webhook:
            try:
                await queue_delivery(
                    signal_id=db_row.id,
                    user_id=user.id,
                    channel="discord",
                    payload={"webhook_url": discord_webhook, "payload": {"embeds": [_build_discord_embed(sig_dict)]}},
                )
                any_success = True
            except Exception as e:
                log.warning(f" [fanout] error queuing Discord for user={user.id}: {e}")

    return any_success


def _build_discord_embed(sig_dict: dict) -> dict:
    """Build the Discord embed payload for a signal."""
    action = sig_dict.get("action", "HOLD")
    color = 0x10B981 if action == "BUY" else 0xEF4444 if action == "SELL" else 0xF59E0B
    return {
        "title": f"{action} {sig_dict.get('ticker')}",
        "description": sig_dict.get("headline", ""),
        "color": color,
        "fields": [
            {"name": "Confidence", "value": f"{sig_dict.get('confidence')}%", "inline": True},
            {"name": "Price", "value": f"${sig_dict.get('price')}", "inline": True},
            {"name": "R:R", "value": str(sig_dict.get("rr", "—")), "inline": True},
            {"name": "Entry", "value": f"${sig_dict.get('entry')}", "inline": True},
            {"name": "Stop", "value": f"${sig_dict.get('stop')}", "inline": True},
            {"name": "Target", "value": f"${sig_dict.get('target')}", "inline": True},
            {"name": "Analysis", "value": sig_dict.get("plain_english", {}).get("summary", ""), "inline": False},
        ],
        "footer": {"text": "NOT FINANCIAL ADVICE. Trade at your own risk."},
    }


_ET = pytz.timezone("America/New_York")

# Tickers whose .info was recently fetched — skip re-fetch if price barely moved
_MOVEMENT_THRESHOLD = 1.0  # % — skip info re-fetch if price moved less than this

# ── Differential Scan state ──────────────────────────────────────────────────
# Persists last known price + volume per ticker across scan cycles.
# Next scan: stable tickers skip generate_signal() entirely, saving ~80/154 API calls.
_diff_state: dict[str, dict] = {}  # {ticker: {price, volume, ts}}
_DIFF_PRICE_THRESHOLD = 0.5  # % price change that counts as "moved"
_DIFF_VOL_THRESHOLD = 1.3  # volume ratio above which ticker is "active"
_DIFF_SIGNAL_MAX_AGE_H = 2.0  # skip only if an active signal was created within this window


def _market_session() -> str:
    """Return the current US market session: pre, regular, after, or closed."""
    now_et = datetime.now(_ET)
    if now_et.weekday() >= 5:
        return "closed"
    t = now_et.time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def _market_hours_ok() -> bool:
    """Return True during NYSE trading hours (9:30–16:05 ET, Mon–Fri only).
    Covers the post-close scan at 16:02 so near-close signals can be sent."""
    now_et = datetime.now(_ET)
    if now_et.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False
    return dtime(9, 30) <= now_et.time() <= dtime(16, 5)


async def _get_scan_tickers(settings) -> list[str]:
    """Return tickers from DB watchlist if populated, otherwise fall back to .env."""
    try:
        from models import WatchlistItem

        async with AsyncSessionLocal() as db:
            rows = (await db.execute(select(WatchlistItem).where(WatchlistItem.is_active == True))).scalars().all()
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
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    price_map = {q["t"]: q["p"] for q in quotes}
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(select(Signal).where(Signal.is_sent == True))).scalars().all()
        for sig in rows:
            current = price_map.get(sig.ticker)
            if not current or not sig.entry or sig.entry <= 0:
                continue
            age_days = (now - sig.created_at).total_seconds() / 86400 if sig.created_at else 0
            if age_days >= 1 and sig.outcome_1d is None:
                sig.outcome_1d = _pct(current, sig.entry, sig.action)
            if age_days >= 3 and sig.outcome_3d is None:
                sig.outcome_3d = _pct(current, sig.entry, sig.action)
            if age_days >= 7 and sig.outcome_pct is None:
                sig.outcome_pct = _pct(current, sig.entry, sig.action)
                sig.outcome_at = now
            if age_days >= 14 and sig.outcome_14d is None:
                sig.outcome_14d = _pct(current, sig.entry, sig.action)
        await db.commit()


# Minimum confidence delta that counts as a "significant" prediction change within a day.
# Below this threshold, the existing signal is silently refreshed (no new row, no re-send).
_CONF_CHANGE_THRESHOLD = 15.0  # percentage points


def _today_start_utc() -> datetime:
    """Return today's 00:00:00 ET expressed in UTC (naive)."""
    ET = pytz.timezone("America/New_York")
    now = datetime.now(ET)
    midnight_et = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight_et.astimezone(pytz.utc).replace(tzinfo=None)


async def _maybe_send(
    sig_dict: dict,
    db_row: Signal,
    settings,
    db,
    label: str,
    force_resend: bool = False,
    scan_started_at: datetime | None = None,
    bypass_market_hours: bool = False,
):
    """Send a Telegram notification for a signal if it qualifies. Mutates db_row on success.

    force_resend=True bypasses the 24h cooldown (used when the signal direction flipped)
    but still enforces a 30-minute anti-spam guard.
    bypass_market_hours=True skips the time-of-day gate (used by EOD batch send).
    scan_started_at is used for SLA tracking — latency is measured from cycle start,
    not from signal created_at (which can be hours old for refreshed-but-unsent signals).
    """
    from services.delivery_gates import check_delivery_gates

    skip_reason, sig_dict = await check_delivery_gates(sig_dict, db, settings)
    if skip_reason:
        log.info(f" {sig_dict['ticker']} skipped ({label}) — {skip_reason}")
        return

    # ── Time-of-day filter ──────────────────────────────────────────────────
    if not bypass_market_hours and not _market_hours_ok():
        log.info(f" {sig_dict['ticker']} notification suppressed — outside clean market window")
        return

    # ── Cooldown: 24h normally, 30 min on direction-flip (force_resend) ────
    # ── Hard cap: max 1 send per ticker per trading day ─────────────────────
    # Multiple same-ticker sends within one session count as one market view but
    # inflate the "sent signals" count and the win-rate denominator. Cap at 1
    # regardless of direction flip or confidence changes within the same day.
    _today_start = datetime.now(timezone.utc).replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0)
    _today_sent = (
        await db.execute(
            select(Signal)
            .where(Signal.ticker == sig_dict["ticker"])
            .where(Signal.is_sent == True)
            .where(Signal.sent_at >= _today_start)
            .limit(1)
        )
    ).scalar_one_or_none()
    if _today_sent:
        log.info(f" {sig_dict['ticker']} skipped — already sent today (1/day cap)")
        return

    if force_resend:
        # Direction flip: only enforce a short anti-spam window (the daily cap above
        # already prevents same-day repeats; this guards cross-day rapid flips)
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=30)
        result = await db.execute(
            select(Signal)
            .where(Signal.ticker == sig_dict["ticker"])
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
            recent_resolved = (
                (
                    await db.execute(
                        select(Signal.outcome_pct)
                        .where(Signal.ticker == sig_dict["ticker"])
                        .where(Signal.action == sig_dict["action"])
                        .where(Signal.is_sent == True)
                        .where(Signal.outcome_pct.isnot(None))
                        .order_by(Signal.sent_at.desc())
                        .limit(3)
                    )
                )
                .scalars()
                .all()
            )
            if recent_resolved:
                _act = sig_dict["action"]
                # BUY win  = outcome_pct > 0;  BUY loss  = outcome_pct <= 0
                # SELL win = outcome_pct < 0;  SELL loss = outcome_pct >= 0
                losses = sum(1 for o in recent_resolved if (o <= 0 if _act == "BUY" else o >= 0))
                if losses >= 3:
                    base_hours = 72
                elif losses >= 1:
                    base_hours = 48
        except Exception:
            pass

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=base_hours)
        result = await db.execute(
            select(Signal)
            .where(Signal.ticker == sig_dict["ticker"])
            .where(Signal.action == sig_dict["action"])
            .where(Signal.is_sent == True)
            .where(Signal.sent_at >= cutoff)
            .limit(1)
        )
        if result.scalar_one_or_none():
            log.info(f" {sig_dict['ticker']} cooldown — already sent {sig_dict['action']} within {base_hours}h")
            return

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    now_et = datetime.now(_ET)  # New York time for display
    et_time = now_et.strftime("%H:%M:%S")  # "20:32:07 ET"
    emoji = "🟢" if sig_dict["action"] == "BUY" else "🔴"

    # ── Broadcast channel (scale path: 1 API call vs N per-user DMs) ──────────
    # When TELEGRAM_BROADCAST_CHANNEL_ID is set, post once to the channel so all
    # subscribers see the signal without the per-user loop hitting Telegram's 30/sec limit.
    _broadcast_id = settings.telegram_broadcast_channel_id
    if _broadcast_id:
        try:
            _url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
            _msg = format_signal(sig_dict)
            async with aiohttp.ClientSession() as _sess:
                _r = await _sess.post(
                    _url,
                    json={"chat_id": _broadcast_id, "text": _msg, "parse_mode": "Markdown"},
                    ssl=_SSL_CTX,
                    timeout=aiohttp.ClientTimeout(total=8),
                )
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
    detail = ""
    if not any_sent:
        success, detail = await send_telegram(sig_dict)

    log_msg = (
        f"{'✓' if success else '✗'} {emoji} "
        f"{sig_dict['action']} {sig_dict['ticker']} @ {sig_dict['price']:.2f} "
        f"(Conf {sig_dict['confidence']:.0f}%)"
    )

    if success:
        db_row.is_sent = True
        db_row.sent_at = now
        # ── Delivery SLA tracking ────────────────────────────────────────────────
        # Measure from scan cycle start (not created_at): refreshed-but-unsent signals
        # carry created_at from hours ago, which would produce false SLA breaches.
        sla_baseline = scan_started_at or db_row.created_at
        if sla_baseline:
            latency_s = (now - sla_baseline).total_seconds()
            if latency_s > 300:  # > 5 minutes from this scan cycle's start
                log.warning(
                    f"[sla] {sig_dict['ticker']} delivery latency {latency_s:.0f}s "
                    f"(scan started {sla_baseline.isoformat()}, sent {now.isoformat()})"
                )
                try:
                    asyncio.ensure_future(
                        _alert_sla_breach(sig_dict["ticker"], sig_dict["action"], latency_s, settings)
                    )
                except Exception:
                    pass
        log.info(
            f" ✓ Telegram sent ({label}) — "
            f"{sig_dict['action']} {sig_dict['ticker']} @ {sig_dict['price']:.2f} "
            f"conf {sig_dict['confidence']:.0f}%"
        )
        # Fire web push to all subscribers for high-confidence signals
        if sig_dict["confidence"] >= 70:
            asyncio.create_task(_push_web_notifications(sig_dict, db, signal_id=db_row.id))
        # Webhook outbound — POST signal JSON to user's webhook_url with HMAC signature
        asyncio.create_task(_send_webhook_outbound(sig_dict, db, signal_id=db_row.id))
    else:
        log.info(f" ✗ Telegram failed — {sig_dict['ticker']}: {detail}")

    from services.provider_telemetry import current_cycle_id

    db.add(
        SendLog(
            time=et_time,  # ET time
            status="sent" if success else "fail",
            message=log_msg,
            cycle_id=current_cycle_id.get(),
        )
    )


async def _push_web_notifications(sig_dict: dict, db, signal_id: int | None = None) -> None:
    """Send web push notifications to all subscribed users for a high-confidence signal."""
    try:
        from models import PushSubscription
        from services.delivery_manager import queue_delivery

        subs = (await db.execute(select(PushSubscription))).scalars().all()
        if not subs:
            return
        # PROD-3: honor the per-user push toggle. Only users who explicitly saved
        # prefs with push=False are skipped (defaults are never applied). Granular
        # sector/score/action filters are enforced on the Telegram fanout path;
        # push only gates the on/off toggle here.
        _app_row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
        _app_data = _app_row.data if (_app_row is not None and isinstance(_app_row.data, dict)) else {}

        def _push_disabled(uid: int) -> bool:
            _p = _app_data.get(f"user_{uid}_notification_prefs")
            return isinstance(_p, dict) and _p.get("push") is False

        emoji = "🟢" if sig_dict["action"] == "BUY" else "🔴"
        push_payload = {
            "title": f"{emoji} {sig_dict['action']} {sig_dict['ticker']} — {sig_dict['confidence']:.0f}% conf",
            "body": sig_dict.get(
                "headline",
                f"Entry ${sig_dict.get('entry', sig_dict['price']):.2f} · Target ${sig_dict.get('target', 0):.2f}",
            ),
            "tag": f"signal-{sig_dict['ticker']}-{sig_dict['action']}",
            "url": "/",
        }
        sent = 0
        for sub in subs:
            if _push_disabled(sub.user_id):
                continue
            sub_info = {"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh, "auth": sub.auth}}
            await queue_delivery(
                signal_id=signal_id,
                user_id=sub.user_id,
                channel="push",
                payload={"subscription_info": sub_info, "payload": push_payload},
            )
            sent += 1
        log.info(f"[push] Web push queued to {sent} subscriber(s) for {sig_dict['ticker']}")
    except Exception as e:
        log.warning(f"[push] Web push queuing failed: {e}")


async def _send_webhook_outbound(sig_dict: dict, db, signal_id: int | None = None) -> None:
    """POST signal JSON to each user's webhook_url (if set) with HMAC-SHA256 signature."""
    try:
        from models import User
        from sqlalchemy import select as _sel
        from services.delivery_manager import queue_delivery

        users_with_webhook = (
            (await db.execute(_sel(User).where(User.webhook_url.isnot(None)).where(User.is_active == True)))
            .scalars()
            .all()
        )

        for u in users_with_webhook:
            await queue_delivery(
                signal_id=signal_id,
                user_id=u.id,
                channel="webhook",
                payload={"signal_data": sig_dict, "webhook_url": u.webhook_url},
            )
    except Exception as e:
        log.warning(f"[webhook] queueing outbound error: {e}")


async def _compute_adaptive_weights() -> dict:
    """
    Query resolved sent signals to compute:
      - Global BUY/SELL win rates (used by signal_engine to nudge confidence)
      - Per-ticker win rates (used to de-rate cluster boost for historically weak tickers)

    Only kicks in once ≥10 resolved signals exist per action (global),
    and ≥3 resolved signals per ticker (per-ticker).
    """
    try:
        import math as _math

        async with AsyncSessionLocal() as db:
            rows = (
                await db.execute(
                    select(Signal.ticker, Signal.action, Signal.outcome_pct, Signal.outcome_at)
                    .where(Signal.outcome_pct.isnot(None))
                    .where(Signal.is_sent == True)
                    .order_by(Signal.outcome_at.asc())  # chronological — needed for streak calc
                )
            ).all()

        if not rows:
            return {}

        from collections import defaultdict

        action_buckets: dict = defaultdict(list)
        ticker_outcomes: dict = defaultdict(list)  # ticker → [(win_bool, outcome_at)]

        for ticker, action, pct, outcome_at in rows:
            action_buckets[action].append(pct)
            if action == "BUY":
                ticker_outcomes[ticker].append((pct > 0, outcome_at))
            elif action == "SELL":
                ticker_outcomes[ticker].append((pct < 0, outcome_at))

        weights: dict = {}
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

        # Global win rates — recency-weighted (exponential decay, halflife 60 days)
        for action, outcomes_raw in action_buckets.items():
            if len(outcomes_raw) < 10:
                continue
            if action not in ("BUY", "SELL"):
                continue
            wr = sum(1 for o in outcomes_raw if (o > 0 if action == "BUY" else o < 0)) / len(outcomes_raw)
            weights[f"{action}_win_rate"] = round(wr, 3)
            log.info(f" {action} historical win rate: {wr * 100:.1f}% ({len(outcomes_raw)} signals)")

        # Per-ticker win rates (recency-weighted) + loss-streak tracking
        ticker_win_rates: dict = {}
        ticker_loss_streaks: dict = {}

        _HALFLIFE_DAYS = 60.0  # outcomes from 60 days ago count at half weight

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
            row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
            if row and row.data:
                return row.data
    except Exception:
        pass
    return {}


async def _maybe_paper_trade(
    sig_dict: dict,
    positions_map: dict,  # { symbol_upper: position_dict } from Alpaca
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

    ticker = sig_dict["ticker"]
    price = sig_dict.get("price") or sig_dict.get("entry") or 1
    notional = float(db_settings.get("paper_trade_notional", 1000.0))
    qty = max(1, round(notional / price))
    pos = positions_map.get(ticker.upper())

    # Guard: check buying power before placing BUY orders
    try:
        if action == "BUY":
            acct = await alpaca_rest.get_account(settings.alpaca_api_key, settings.alpaca_api_secret)
            buying_power = float(acct.get("buying_power") or 0)
            if buying_power < notional * 0.5:
                log.info(
                    f" {ticker} BUY skipped — insufficient buying power "
                    f"(${buying_power:.0f} available, ${notional:.0f} needed). "
                    f"Reset your paper account at alpaca.markets."
                )
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
                settings.alpaca_api_key,
                settings.alpaca_api_secret,
                ticker,
                qty,
                "buy",
            )
            log.info(
                f" ✓ AUTO BUY  {ticker} {qty}sh @ ~${price:.2f} "
                f"| order {order.get('id', '?')[:8]} status={order.get('status')}"
            )

        else:  # SELL
            if pos and pos.get("side") == "long":
                order = await alpaca_rest.close_position(settings.alpaca_api_key, settings.alpaca_api_secret, ticker)
                log.info(f" ✓ AUTO CLOSE long {ticker} — SELL signal received")
            else:
                if pos and pos.get("side") == "short":
                    log.info(f" {ticker} SELL skipped — already short {pos['qty']} shares")
                    return
                order = await alpaca_rest.place_order(
                    settings.alpaca_api_key,
                    settings.alpaca_api_secret,
                    ticker,
                    qty,
                    "sell",
                )
                log.info(
                    f" ✓ AUTO SELL {ticker} {qty}sh @ ~${price:.2f} "
                    f"| order {order.get('id', '?')[:8]} status={order.get('status')}"
                )

    except Exception as e:
        log.info(f" ✗ {ticker} {action} failed: {e}")


async def _maybe_auto_execute_for_signal(sig: dict, signal_id, db) -> None:
    """
    Auto-execute a signal for every Pro user with auto_execute=True and
    a connected Alpaca account.

    Called once per new/unsent signal from _deliver_scan_signals. Never
    raises — any per-user error is logged and skipped.
    """
    action = sig.get("action")
    if action not in ("BUY", "SELL"):
        return

    if not _market_hours_ok():
        return

    db_settings = await _load_db_settings()
    if db_settings.get("execution_paused"):
        log.info("_maybe_auto_execute: broker auto-execution paused (kill switch active)")
        return

    # Load eligible users in a fresh session so we don't dirty the delivery session.
    try:
        async with AsyncSessionLocal() as exec_db:
            from sqlalchemy import select as _sel

            candidates = (
                (
                    await exec_db.execute(
                        _sel(User).where(
                            User.auto_execute == True,
                            User.auto_execute_broker.in_(["alpaca", "ibkr"]),
                            User.alpaca_key_enc.isnot(None),
                            User.is_active == True,
                        )
                    )
                )
                .scalars()
                .all()
            )

            if not candidates:
                return

            conf = float(sig.get("confidence") or 0)

            from services.broker_svc import execute_signal_for_user

            for user in candidates:
                # Require Pro/owner subscription
                if not user.is_owner and not (
                    user.subscription_status == "active" and TIERS.index(user.subscription_tier) >= TIERS.index("pro")
                ):
                    continue

                min_conf = user.auto_execute_min_conf or 75.0
                if conf < min_conf:
                    continue

                await execute_signal_for_user(user, sig, signal_id, exec_db)

            await exec_db.commit()
    except Exception as e:
        log.warning("_maybe_auto_execute_for_signal: unexpected error: %s", e)


async def _maybe_auto_execute_portfolio(delivered_signals: list[tuple[dict, int]], db) -> None:
    """
    REF-5: Auto-execute a portfolio of active signals for all users with auto_execute enabled
    using HRP portfolio allocation weights.
    """
    try:
        from models import User
        from sqlalchemy import select as _sel
        from config import TIERS

        # Create a new async session to avoid mixing with main scan transaction
        async with AsyncSessionLocal() as exec_db:
            candidates = (
                (
                    await exec_db.execute(
                        _sel(User).where(
                            User.auto_execute == True,
                            User.auto_execute_broker.in_(["alpaca", "ibkr"]),
                            User.alpaca_key_enc.isnot(None),
                            User.is_active == True,
                        )
                    )
                )
                .scalars()
                .all()
            )

            if not candidates:
                return

            from services.broker_svc import execute_portfolio_for_user

            for user in candidates:
                # Require Pro/owner subscription
                if not user.is_owner and not (
                    user.subscription_status == "active" and TIERS.index(user.subscription_tier) >= TIERS.index("pro")
                ):
                    continue

                min_conf = user.auto_execute_min_conf or 75.0
                
                # Filter delivered signals that meet the user's min_conf threshold
                user_signals = []
                for sig, signal_id in delivered_signals:
                    enriched_sig = sig.copy()
                    enriched_sig["id"] = signal_id
                    conf = float(enriched_sig.get("confidence") or 0.0)
                    if conf >= min_conf:
                        user_signals.append(enriched_sig)
                        
                if user_signals:
                    # Execute portfolio-level allocation and orders for this user
                    await execute_portfolio_for_user(user, user_signals, exec_db)

            await exec_db.commit()
    except Exception as e:
        log.warning("_maybe_auto_execute_portfolio: unexpected error: %s", e)


async def _alert_telegram(text: str):
    """Send a plain alert message via Telegram (best-effort, never raises)."""
    try:
        s = get_settings()
        if not s.telegram_bot_token or not s.telegram_chat_id:
            return
        url = f"https://api.telegram.org/bot{s.telegram_bot_token}/sendMessage"
        async with aiohttp.ClientSession() as sess:
            await sess.post(
                url,
                json={"chat_id": s.telegram_chat_id, "text": text},
                ssl=_SSL_CTX,
                timeout=aiohttp.ClientTimeout(total=6),
            )
    except Exception:
        pass


_last_analytics_compute: float = 0.0
_ANALYTICS_COMPUTE_INTERVAL = 300  # re-compute at most every 5 minutes

_scan_lock = asyncio.Lock()
_scan_status: dict = {
    "state": "idle",
    "running": False,
    "last_started_at": None,
    "last_finished_at": None,
    "last_success_at": None,
    "last_error": None,
    "last_duration_s": None,
    "last_stage": None,
    "last_stage_at": None,
    "runs": 0,
    "successes": 0,
    "failures": 0,
    "skipped_overlaps": 0,
}


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat() + "Z"


def _mark_scan_stage(stage: str) -> None:
    _scan_status["last_stage"] = stage
    _scan_status["last_stage_at"] = _utc_iso()


def get_scan_status() -> dict:
    """Return a copy of the latest scan lifecycle status for health/admin APIs."""
    return dict(_scan_status)


async def fetch_market_context(tickers: list[str], settings) -> dict:
    """
    Fetch all market-wide signals and context needed for a scan cycle.

    Returns a dict with keys: fear_greed, macro, put_call, breadth, aaii, cot,
    adaptive_weights, calibration_map, hmm_regime, supply_chain, institutional_signals,
    dark_pool, corporate_events, etf_flows, massive_economy, portfolio_ctx, pairs_signals,
    weight_overrides, factor_weights, buy_sell_ratio, buy_saturated.

    All sub-fetches are best-effort; failures are logged and the key is omitted or
    given a safe default. Callers must treat every key as Optional.
    """
    market_ctx: dict = {}

    # ── Core macro / sentiment signals (concurrent) ───────────────────────────
    try:
        fg, macro, pc, breadth, aaii, cot = await asyncio.gather(
            get_fear_greed(),
            get_macro_context(),
            get_put_call_ratio(),
            get_market_breadth(),
            get_aaii_sentiment(),
            get_cot_signal(),
        )
        market_ctx.update(
            {"fear_greed": fg, "macro": macro, "put_call": pc, "breadth": breadth, "aaii": aaii, "cot": cot}
        )
        fg_label = fg["label"] if fg else "unknown"
        breadth_str = f"{breadth['pct_above_200d']:.0f}% >200d" if breadth else "?"
        aaii_str = (
            f"AAII {aaii['spread']:+.0f}% ({aaii['signal']})" if aaii and aaii.get("spread") is not None else "AAII N/A"
        )
        log.info(
            f" F&G = {fg['score'] if fg else '?'} ({fg_label}) | "
            f"VIX = {macro.get('vix', '?') if macro else '?'} | "
            f"Macro score = {macro.get('macro_score', 0) if macro else 0} | "
            f"Breadth = {breadth_str} | {aaii_str}"
        )
    except Exception as e:
        log.info(f" market context failed: {e}")

    try:
        market_ctx["adaptive_weights"] = await _compute_adaptive_weights()
    except Exception:
        pass

    try:
        from services.calibration import load_calibration

        market_ctx["calibration_map"] = load_calibration()
    except Exception:
        pass

    # ── HMM Macro Regime (cached 1h) ─────────────────────────────────────────
    try:
        from services.macro_regime import get_macro_regime

        regime_data = await get_macro_regime()
        market_ctx["hmm_regime"] = regime_data
        log.info(
            f" HMM regime: {regime_data.get('regime', '?')} "
            f"bull={regime_data.get('bull_prob', 0):.0%} "
            f"trans_risk={regime_data.get('transition_risk', 0):.0%}"
        )
    except Exception as e:
        log.debug(f" HMM regime failed (non-critical): {e}")

    # ── Supply Chain signals (cached 4h) ─────────────────────────────────────
    try:
        from services.supply_chain import get_supply_chain_signals

        market_ctx["supply_chain"] = await get_supply_chain_signals()
    except Exception as e:
        log.debug(f" Supply chain data failed (non-critical): {e}")

    # ── 13F institutional flow (quarterly, cached 6h) ────────────────────────
    try:
        from services.institutional import get_institutional_signals

        inst_list = await get_institutional_signals(settings.tickers)
        market_ctx["institutional_signals"] = {s["ticker"]: s for s in inst_list}
        if inst_list:
            log.info(f" 13F: {len(inst_list)} watchlist tickers with institutional activity")
    except Exception as e:
        log.debug(f" 13F fetch failed (non-critical): {e}")

    # ── Dark Pool Block Prints (cached 1h) ───────────────────────────────────
    try:
        from services.dark_pool import get_dark_pool_flow

        market_ctx["dark_pool"] = await get_dark_pool_flow(settings.tickers)
    except Exception as e:
        log.debug(f" Dark pool fetch failed (non-critical): {e}")

    # ── Corporate Events (cached 4h) ─────────────────────────────────────────
    try:
        from services.corporate_events import get_corporate_events

        corp_events = await get_corporate_events()
        market_ctx["corporate_events"] = corp_events
        n_ev = len(corp_events.get("events", []))
        if n_ev:
            log.info(f" Corporate events: {n_ev} upcoming across {len(corp_events.get('by_ticker', {}))} tickers")
    except Exception as e:
        log.debug(f" Corporate events fetch failed (non-critical): {e}")

    # ── ETF Fund Flows (cached 4h) ───────────────────────────────────────────
    try:
        from services.etf_flows import get_etf_flows

        market_ctx["etf_flows"] = await get_etf_flows()
    except Exception as e:
        log.debug(f" ETF flows fetch failed (non-critical): {e}")

    # ── Economy data from Massive (cached 1h) ────────────────────────────────
    try:
        from services.massive_economy import get_economy_data

        eco = await get_economy_data()
        if eco:
            market_ctx["massive_economy"] = eco
    except Exception as e:
        log.debug(f" Massive economy fetch failed (non-critical): {e}")

    # ── ETF Constituents preload (cached 24h) ────────────────────────────────
    try:
        from services.etf_constituents import preload_all

        await preload_all()
    except Exception as e:
        log.debug(f" ETF constituents preload failed (non-critical): {e}")

    # ── Paper portfolio sector exposure + PCA risk ───────────────────────────
    if settings.alpaca_api_key and settings.alpaca_api_secret:
        try:
            from services import alpaca_rest
            from services.sector import SECTOR_MAP as SECTOR_ETF_MAP

            positions_list = await alpaca_rest.get_positions(settings.alpaca_api_key, settings.alpaca_api_secret)
            if positions_list:
                total_mv = sum(abs(float(p.get("market_value") or 0)) for p in positions_list)
                sector_exposure: dict[str, float] = {}
                if total_mv > 0:
                    for p in positions_list:
                        sym = p.get("symbol", "").upper()
                        mv = abs(float(p.get("market_value") or 0))
                        etf = SECTOR_ETF_MAP.get(sym)
                        if etf:
                            sector_exposure[etf] = sector_exposure.get(etf, 0) + mv / total_mv * 100
                market_ctx["portfolio_ctx"] = {
                    "sector_exposure": sector_exposure,
                    "total_positions": len(positions_list),
                    "total_mv": round(total_mv, 2),
                }
                log.info(
                    f" Portfolio: {len(positions_list)} open positions, "
                    f"sector exposure: {', '.join(f'{k} {v:.0f}%' for k, v in sector_exposure.items())}"
                )
                if len(positions_list) >= 3:
                    try:
                        from services.pca_risk import compute_pca_risk

                        pos_values = {
                            p.get("symbol", "").upper(): abs(float(p.get("market_value") or 0)) for p in positions_list
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

    # ── MST dynamic pairs refresh (Sunday only, uses prefetched histories) ─────
    # compute_mst_pairs is CPU-bound (~2s for 154 tickers); run in thread pool.
    try:
        from datetime import datetime as _dt_now

        if _dt_now.now().weekday() == 6:  # Sunday
            from services.market_data import get_histories_batch as _ghb
            from services.mst_cointegration import refresh_mst_pairs as _refresh_mst

            _mst_hists = await _ghb(settings.tickers, period="6mo", interval="1d")
            _n_mst = await _refresh_mst(_mst_hists)
            log.info(f" MST pairs refresh: {_n_mst} dynamic pairs computed")
    except Exception as e:
        log.debug(f" MST pairs refresh failed (non-critical): {e}")

    # ── Cointegration / pairs trading signals (cached 2h) ────────────────────
    try:
        from services.cointegration import get_pairs_signals

        pairs_signals = await get_pairs_signals(settings.tickers)
        market_ctx["pairs_signals"] = pairs_signals
        if pairs_signals:
            log.info(f" Pairs: {len(pairs_signals)} divergence signals detected")
    except Exception as e:
        log.debug(f" Pairs signal fetch failed (non-critical): {e}")

    # ── Weight overrides + factor mining weights ──────────────────────────────
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
            log.debug(f" Factor weights loaded: {fw.get('combinations_tested', '?')} combos")
    except Exception as e:
        log.debug(f" Factor weights load failed: {e}")

    # ── BUY:SELL saturation circuit breaker (7-day ratio) ────────────────────
    try:
        async with AsyncSessionLocal() as db:
            from sqlalchemy import text as _sa_text

            _ratio_row = (
                await db.execute(
                    _sa_text("""
                SELECT
                    SUM(CASE WHEN action='BUY'  THEN 1 ELSE 0 END) AS buys,
                    SUM(CASE WHEN action='SELL' THEN 1 ELSE 0 END) AS sells
                FROM signals
                WHERE date(created_at) >= date('now', '-7 days')
                  AND action IN ('BUY', 'SELL')
            """)
                )
            ).fetchone()
        _buys = _ratio_row[0] or 0
        _sells = _ratio_row[1] or 1
        _buy_sell_ratio = round(_buys / _sells, 2)
        market_ctx["buy_sell_ratio"] = _buy_sell_ratio
        market_ctx["buy_saturated"] = _buy_sell_ratio > 4.0
        if _buy_sell_ratio > 4.0:
            log.info(
                f" BUY:SELL circuit breaker ACTIVE — 7d ratio {_buy_sell_ratio:.1f}:1 (>4.0 threshold). BUY threshold raised to 42."
            )
        else:
            log.info(f" BUY:SELL ratio (7d): {_buy_sell_ratio:.1f}:1 — within normal range.")
    except Exception as e:
        log.debug(f" BUY:SELL ratio check failed (non-critical): {e}")
        market_ctx["buy_saturated"] = False

    # ── News batch prefetch ───────────────────────────────────────────────────
    try:
        from services.benzinga_news import prefetch_news_batch

        await prefetch_news_batch(tickers)
    except Exception as e:
        log.debug(f" news batch prefetch failed (non-critical): {e}")

    return market_ctx


async def run_scan(broadcast_fn=None):
    """Single-flight scan wrapper with status tracking and Redis-aware lock."""
    if _scan_lock.locked():
        _scan_status["skipped_overlaps"] += 1
        _scan_status["state"] = "skipped_overlap"
        return None

    lock_token = None
    try:
        from services.redis_cache import cache_acquire_lock

        lock_token = await cache_acquire_lock("lock:scanner:run", ttl=900)
        if not lock_token:
            _scan_status["skipped_overlaps"] += 1
            _scan_status["state"] = "skipped_distributed_overlap"
            return None
    except Exception:
        # Redis unavailable — fall through to the local asyncio.Lock only.
        log.warning(
            "[scanner] Redis distributed lock unavailable — proceeding with local lock only. "
            "In multi-worker deployments this can cause duplicate scans and API rate-limit bursts."
        )
        lock_token = None

    async with _scan_lock:
        import os
        import socket
        import time as _time
        import uuid
        from database import AsyncSessionLocal
        from models import BackgroundJobRun
        from services.provider_telemetry import (
            current_cycle_id,
            init_cycle_telemetry,
            flush_cycle_telemetry,
        )

        cycle_id = f"scan:{int(_time.time())}:{uuid.uuid4().hex[:6]}"
        token = current_cycle_id.set(cycle_id)
        init_cycle_telemetry(cycle_id)

        started = monotonic()
        start_time_db = datetime.now(timezone.utc).replace(tzinfo=None)
        worker_id = f"{socket.gethostname()}:{os.getpid()}"

        # Insert run row
        job_run_id = None
        try:
            async with AsyncSessionLocal() as db_session:
                job_run = BackgroundJobRun(
                    job_name="run_scan",
                    cycle_id=cycle_id,
                    start_time=start_time_db,
                    status="running",
                    worker_id=worker_id,
                )
                db_session.add(job_run)
                await db_session.commit()
                job_run_id = job_run.id
        except Exception as dbe:
            log.warning(f"[scanner] Failed to log scan run start: {dbe}")

        _scan_status.update(
            {
                "state": "running",
                "running": True,
                "last_started_at": _utc_iso(),
                "last_finished_at": None,
                "last_error": None,
                "last_duration_s": None,
            }
        )
        _scan_status["runs"] += 1
        _mark_scan_stage("start")
        try:
            result = await _run_scan_impl(broadcast_fn=broadcast_fn)
            _scan_status["successes"] += 1
            _scan_status["last_success_at"] = _utc_iso()
            _scan_status["state"] = "success"
            return result
        except Exception as e:
            _scan_status["failures"] += 1
            _scan_status["last_error"] = f"{type(e).__name__}: {e}"
            _scan_status["state"] = "failed"
            raise
        finally:
            _scan_status["running"] = False
            _scan_status["last_finished_at"] = _utc_iso()
            _scan_status["last_duration_s"] = round(monotonic() - started, 3)

            # Update run row
            if job_run_id:
                try:
                    end_time_db = datetime.now(timezone.utc).replace(tzinfo=None)
                    duration = (end_time_db - start_time_db).total_seconds()
                    async with AsyncSessionLocal() as db_session:
                        db_run = await db_session.get(BackgroundJobRun, job_run_id)
                        if db_run:
                            db_run.end_time = end_time_db
                            db_run.duration_s = duration
                            if _scan_status["state"] == "success":
                                db_run.status = "completed"
                            else:
                                db_run.status = "failed"
                                db_run.error = _scan_status.get("last_error")
                            await db_session.commit()
                except Exception as dbe:
                    log.warning(f"[scanner] Failed to log scan run end: {dbe}")

            # Flush provider telemetry
            try:
                await flush_cycle_telemetry(cycle_id)
            except Exception as te:
                log.warning(f"[scanner] Failed to flush telemetry: {te}")

            # Reset ContextVar
            current_cycle_id.reset(token)

            if lock_token:
                try:
                    from services.redis_cache import cache_release_lock

                    await cache_release_lock("lock:scanner:run", lock_token)
                except Exception:
                    pass


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
        from models import Signal
        from sqlalchemy import case, func, select

        from services.redis_cache import cache_set

        async with AsyncSessionLocal() as db:
            rows = (
                await db.execute(
                    select(
                        Signal.action,
                        func.count(Signal.id).label("n"),
                        func.avg(Signal.outcome_pct).label("avg_ret"),
                        func.sum(case((Signal.outcome_pct > 0, 1), else_=0)).label("wins"),
                    )
                    .where(
                        Signal.outcome_pct.isnot(None),
                        Signal.action.in_(["BUY", "SELL"]),
                    )
                    .group_by(Signal.action)
                )
            ).all()

        if not rows:
            return

        total_n = sum(r.n for r in rows)
        total_wins = sum(r.wins for r in rows)
        summary = {
            "resolved": total_n,
            "win_rate": round(total_wins / total_n * 100, 1) if total_n else None,
            "avg_return": round(sum(r.avg_ret * r.n for r in rows) / total_n, 3) if total_n else None,
            "by_action": [
                {
                    "action": r.action,
                    "count": r.n,
                    "win_rate": round(r.wins / r.n * 100, 1) if r.n else None,
                    "avg_return": round(r.avg_ret, 3) if r.avg_ret is not None else None,
                }
                for r in rows
            ],
            "computed_at": datetime.now(timezone.utc).replace(tzinfo=None).isoformat() + "Z",
        }
        await cache_set("analytics:backtest_summary", summary, ttl=_ANALYTICS_COMPUTE_INTERVAL)
        log.debug(f"[analytics] backtest summary cached (n={total_n})")
    except Exception as e:
        log.debug(f"[analytics] pre-compute failed (non-critical): {e}")


async def _persist_scan_signals(
    signals: list[dict],
    today_start: datetime,
) -> tuple[list[tuple], list[tuple]]:
    """
    Deduplicate and persist generated signals for one scan cycle.

    Rules (per trading day, midnight ET boundary):
      • Same ticker + direction, conf delta < 15pp → silent in-place refresh
        (no new row, no re-send unless signal was never sent).
      • Same ticker, direction flipped → deactivate old, create new,
        force_resend=True (bypass 24h Telegram cooldown).
      • Same ticker + direction, conf delta ≥ 15pp → deactivate old, create new,
        normal 24h cooldown applies.
      • No active signal from today → deactivate any stale signal, create new.

    Returns:
        new_signals      — list of (sig_dict, Signal row, force_resend) for new rows
        refreshed_unsent — list of (sig_dict, Signal row, force_resend) for
                           in-place refreshes where the signal was never sent
    """
    new_signals: list[tuple[dict, Signal, bool]] = []
    refreshed_unsent: list[tuple[dict, Signal, bool]] = []

    async with AsyncSessionLocal() as db:
        for sig in signals:
            # ACT-4c: persist BUY-gate inputs that have no dedicated column, so
            # eod_batch_send() can rebuild a sig_dict that the delivery gates
            # evaluate identically to the real-time path.
            _gate_extra = {
                "hasMr": sig.get("hasMr"),
                "vix": sig.get("vix"),
                "crossAssetHeadwinds": sig.get("crossAssetHeadwinds"),
                "daysToExDiv": sig.get("daysToExDiv"),
                "cohort": sig.get("cohort"),
                "cohort_meta": sig.get("cohort_meta"),
            }
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
                conf_delta = abs(sig["confidence"] - (existing.confidence or 0))
                direction_changed = existing.action != sig["action"]

                if not direction_changed and conf_delta < _CONF_CHANGE_THRESHOLD:
                    existing.price = sig["price"]
                    existing.change = sig["change"]
                    existing.change_pct = sig["changePct"]
                    existing.confidence = sig["confidence"]
                    existing.confidence_warning = bool(sig.get("confidence_warning", False))
                    existing.rationale = sig["rationale"]
                    existing.sources = sig["sources"]
                    existing.headline = sig["headline"]
                    existing.plain_english = sig.get("plain_english")
                    existing.session = sig.get("session")
                    existing.days_to_earnings = sig.get("daysToEarnings")
                    existing.next_earnings_date = sig.get("nextEarningsDate")
                    existing.sector_etf = sig.get("sectorEtf")
                    existing.rs_vs_sector = sig.get("rsVsSector")
                    existing.style = sig.get("style", existing.style)
                    existing.extra_data = _gate_extra
                    if not existing.is_sent:
                        refreshed_unsent.append((sig, existing, False))
                    continue

                if direction_changed:
                    force_resend = True
                    log.info(
                        f" {sig['ticker']} direction flip "
                        f"{existing.action}→{sig['action']} "
                        f"(conf {existing.confidence:.0f}%→{sig['confidence']:.0f}%)"
                    )
                else:
                    log.info(
                        f" {sig['ticker']} confidence surge "
                        f"{existing.confidence:.0f}%→{sig['confidence']:.0f}% "
                        f"(Δ{conf_delta:.0f}pp)"
                    )

            await db.execute(
                update(Signal)
                .where(Signal.ticker == sig["ticker"])
                .where(Signal.is_active == True)
                .values(is_active=False)
            )

            _now_et = datetime.now(_ET)
            _style = sig.get("style", "swing")
            if _style == "intraday":
                _close_et = _now_et.replace(hour=16, minute=5, second=0, microsecond=0)
                if _now_et >= _close_et:
                    _close_et += timedelta(days=1)
                _expires = _close_et.astimezone(pytz.utc).replace(tzinfo=None)
            elif _style == "position":
                _expires = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=30)
            else:
                # §34d: use sector-calibrated hold_days (from _SECTOR_MR_CONFIG via
                # signal_engine.recommendedHoldDays) instead of flat 10. Sectors with
                # hold=5 (XLK, XLE, XLB) expire in 5 days; uncalibrated default = 10.
                _swing_hold = sig.get("recommendedHoldDays", 10) or 10
                _expires = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=_swing_hold)

            from services.provider_telemetry import current_cycle_id

            row = Signal(
                ticker=sig["ticker"],
                company=sig.get("company"),
                action=sig["action"],
                raw_score=sig.get("raw_score"),
                confidence=sig["confidence"],
                confidence_warning=bool(sig.get("confidence_warning", False)),
                price=sig["price"],
                change=sig["change"],
                change_pct=sig["changePct"],
                entry=sig.get("entry"),
                stop=sig.get("stop"),
                target=sig.get("target"),
                rr=sig.get("rr"),
                headline=sig["headline"],
                sentiment=sig.get("sentiment", 0),
                style=sig.get("style", "swing"),
                sources=sig.get("sources", []),
                rationale=sig.get("rationale", []),
                plain_english=sig.get("plain_english"),
                session=sig.get("session"),
                days_to_earnings=sig.get("daysToEarnings"),
                next_earnings_date=sig.get("nextEarningsDate"),
                sector_etf=sig.get("sectorEtf"),
                rs_vs_sector=sig.get("rsVsSector"),
                expires_at=_expires,
                extra_data=_gate_extra,
                cycle_id=current_cycle_id.get(),
            )
            db.add(row)
            await db.flush()
            # Save gate traces (TSYS-6a)
            for trace in sig.get("gate_traces", []):
                trace_row = SignalGateTrace(
                    signal_id=row.id,
                    gate_id=trace["gate_id"],
                    version=trace["version"],
                    input_values=trace["input_values"],
                    score_delta=trace["score_delta"],
                    confidence_delta=trace["confidence_delta"],
                    passed=trace["passed"],
                    reason=trace["reason"],
                )
                db.add(trace_row)
            # Save shadow scores (TSYS-7c)
            shadow = sig.get("shadow_scores")
            if shadow:
                shadow_row = ModelShadowScore(
                    signal_id=row.id,
                    model_id=shadow["model_id"],
                    score=shadow["score"],
                    confidence=shadow["confidence"],
                    champion_score=shadow["champion_score"],
                    champion_confidence=shadow["champion_confidence"],
                )
            # Save feature snapshots (QENG-2a)
            if "features" in sig:
                from services.feature_store import save_feature_snapshot
                from services.lineage import DATA_LINEAGE_VERSION
                await save_feature_snapshot(
                    db=db,
                    ticker=sig["ticker"],
                    ts=datetime.utcnow(),
                    features=sig["features"],
                    signal_id=row.id,
                    effective_time=datetime.utcnow(),
                    provider="polygon",
                    signal_policy_version=DATA_LINEAGE_VERSION,
                )

            new_signals.append((sig, row, force_resend))

        await db.commit()

    return new_signals, refreshed_unsent


async def _deliver_scan_signals(
    new_signals: list[tuple],
    refreshed_unsent: list[tuple],
    settings,
    db_settings: dict,
    positions_map: dict,
    scan_cycle_started_at: datetime,
) -> None:
    """
    Send qualifying signals via Telegram/Discord and paper-trade them.

    Deduplicates by (ticker, action) so the same signal is never sent twice
    per cycle even if it appears in both new_signals and refreshed_unsent.
    """
    if settings.auto_send_notifications:
        async with AsyncSessionLocal() as db:
            seen: set = set()
            candidates = []
            new_set = {id(row) for _, row, _ in new_signals}
            for sig, row, force in new_signals + refreshed_unsent:
                key = (sig["ticker"], sig["action"])
                if key not in seen:
                    seen.add(key)
                    label = "new" if id(row) in new_set else "unsent"
                    candidates.append((sig, row, label, force))

            delivered_signals = []
            for sig, row, label, force in candidates:
                cohort = sig.get("cohort", "delivered")
                merged = await db.merge(row)
                
                if cohort == "delivered":
                    await _maybe_send(
                        sig, merged, settings, db, label, force_resend=force, scan_started_at=scan_cycle_started_at
                    )
                    await _maybe_paper_trade(sig, positions_map, settings, db_settings)
                    delivered_signals.append((sig, merged.id))
                elif cohort == "shadow":
                    log.info("Cohort: Ticker %s routed to SHADOW (paper-only). Skipping notifications/live orders.", sig["ticker"])
                    await _maybe_paper_trade(sig, positions_map, settings, db_settings)
                elif cohort == "withheld":
                    log.info("Cohort: Ticker %s routed to WITHHELD (control). Skipping all executions/notifications.", sig["ticker"])

            if delivered_signals:
                await _maybe_auto_execute_portfolio(delivered_signals, db)

            await db.commit()
    elif db_settings.get("auto_paper_trade"):
        seen: set = set()
        for sig, row, _force in new_signals + refreshed_unsent:
            key = (sig["ticker"], sig["action"])
            if key not in seen:
                seen.add(key)
                cohort = sig.get("cohort", "delivered")
                if cohort != "withheld":
                    await _maybe_paper_trade(sig, positions_map, settings, db_settings)


async def eod_batch_send() -> None:
    """
    EOD batch delivery — sends all BUY/SELL signals from today that were never
    delivered in real-time (is_sent=False). Bypasses the market-hours gate so
    after-close scans get delivered. All other delivery gates still apply.

    Called by the scanner loop at 16:10 ET after the post-close scan.
    """
    settings = get_settings()
    if not settings.auto_send_notifications:
        return

    today_start = datetime.now(_ET).replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)

    async with AsyncSessionLocal() as db:
        rows = (
            (
                await db.execute(
                    select(Signal)
                    .where(
                        Signal.is_active == True,
                        Signal.is_sent == False,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.created_at >= today_start,
                    )
                    .order_by(Signal.confidence.desc())
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[eod_batch] no unsent BUY/SELL signals today — nothing to send")
        return

    log.info("[eod_batch] %d unsent signal(s) to process", len(rows))
    sent_count = 0
    batch_started_at = datetime.now(timezone.utc).replace(tzinfo=None)

    async with AsyncSessionLocal() as db:
        for row in rows:
            sig_dict = {
                "ticker": row.ticker,
                "company": row.company or row.ticker,
                "action": row.action,
                "confidence": row.confidence,
                "price": row.price,
                "entry": row.entry,
                "stop": row.stop,
                "target": row.target,
                "rr": row.rr or "—",
                "headline": row.headline or "",
                "style": row.style or "swing",
                "sources": row.sources or [],
                "rationale": row.rationale or [],
                "sectorEtf": row.sector_etf,
                "daysToEarnings": row.days_to_earnings,
            }
            # ACT-4c: restore BUY-gate inputs persisted at creation so the EOD
            # path evaluates §54/§55/ex-div and the MR-setup requirement the same
            # as real-time delivery. Pre-migration rows have extra_data=None →
            # hasMr stays absent and the BUY is conservatively blocked (unchanged).
            _extra = row.extra_data or {}
            for _k in ("hasMr", "vix", "crossAssetHeadwinds", "daysToExDiv"):
                if _extra.get(_k) is not None:
                    sig_dict[_k] = _extra[_k]
            merged = await db.merge(row)
            await _maybe_send(
                sig_dict,
                merged,
                settings,
                db,
                label="eod_batch",
                bypass_market_hours=True,
                scan_started_at=batch_started_at,
            )
            if merged.is_sent:
                sent_count += 1

        await db.commit()

    log.info("[eod_batch] done — %d/%d signals delivered", sent_count, len(rows))


async def _run_scan_impl(broadcast_fn=None):
    """
    Full scan cycle:
      1. Fetch market-wide context (F&G + Macro) once.
      2. Batch-download history for active watchlist tickers.
      3. Pre-filter: skip .info re-fetch for stable tickers (< 1% move, recent signal).
      4. Fetch ticker .info sequentially (rate-limited).
      5. Generate signals (news + EDGAR fetched concurrently per ticker).
      6. Persist signals (smart daily deduplication) via _persist_scan_signals().
      7. Auto-send + auto paper trade via _deliver_scan_signals().
      8. Update outcomes for old sent signals.
      9. Price alert evaluation.
     10. Broadcast via WebSocket.
     11. Pre-compute analytics cache.
    """
    scan_cycle_started_at = datetime.now(timezone.utc).replace(tzinfo=None)  # used for SLA measurement
    settings = get_settings()
    tickers = await _get_scan_tickers(settings)
    _mark_scan_stage("load_tickers")

    # Clear stale data-quality counters at the start of each cycle
    global _data_quality
    _data_quality = {t: _data_quality.get(t, 0) for t in tickers}  # prune removed tickers

    # Evict tickers no longer in the watchlist to prevent unbounded growth
    global _diff_state
    _diff_state = {t: _diff_state[t] for t in tickers if t in _diff_state}

    stale_cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=8)

    # ── Steps 1–1l: market-wide context ─────────────────────────────────
    _mark_scan_stage("market_context")
    market_ctx = await fetch_market_context(tickers, settings)

    # ── Step 2: batch history ────────────────────────────────────────────
    _mark_scan_stage("history_batch")
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
            await send_telegram(
                {
                    "action": "DATA_ALERT",
                    "ticker": "SYSTEM",
                    "confidence": 0,
                    "headline": _alert_msg,
                    "price": 0,
                    "sentiment": 0,
                    "style": "swing",
                    "sources": [],
                    "rationale": [],
                    "ts": datetime.now(timezone.utc).replace(tzinfo=None).isoformat() + "Z",
                }
            )
        except Exception:
            pass

    # ── Step 3: quotes batch for pre-filtering + outcome tracking ────────
    _mark_scan_stage("quotes_batch")
    try:
        quotes = await get_quotes_batch(tickers)
        quote_map = {q["t"]: q for q in quotes}
    except Exception as e:
        log.info(f" quotes batch failed: {e}")
        quotes, quote_map = [], {}

    # ── Step 4: pre-filtered .info fetch ─────────────────────────────────
    _mark_scan_stage("info_fetch")
    # Skip .info for tickers where price moved < threshold AND a recent active
    # signal already exists — saves significant time on quiet days.
    try:
        async with AsyncSessionLocal() as db:
            recent_sigs = (
                (
                    await db.execute(
                        select(Signal.ticker)
                        .where(Signal.is_active == True)
                        .where(Signal.created_at >= stale_cutoff)  # same 8h window
                    )
                )
                .scalars()
                .all()
            )
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
        log.info(
            f" info fetch: {len(tickers_needing_info)}/{len(tickers)} tickers "
            f"({len(tickers) - len(tickers_needing_info)} skipped — stable)"
        )
    except Exception as e:
        log.info(f" info fetch failed: {e}")
        infos = {}

    # ── Step 4b: differential scan — identify stable tickers to skip ────────
    # Stable = price moved < 0.5% AND volume < 1.3× avg AND active signal < 2h old.
    # Skipped tickers get their price + timestamp updated in-place in the DB.
    # Expected: skip 80-100 of 154 tickers per cycle → ~5× throughput increase.
    _two_hr_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=_DIFF_SIGNAL_MAX_AGE_H)
    try:
        async with AsyncSessionLocal() as _diff_db:
            _recent_sig_tickers = set(
                (
                    await _diff_db.execute(
                        select(Signal.ticker).where(Signal.is_active == True).where(Signal.created_at >= _two_hr_ago)
                    )
                )
                .scalars()
                .all()
            )
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
                today_vol = float(h["Volume"].iloc[-1])
                avg_vol = float(h["Volume"].iloc[-21:-1].mean())
                if avg_vol > 0:
                    vol_ratio = today_vol / avg_vol
            except Exception:
                pass
        if price_chg < _DIFF_PRICE_THRESHOLD and vol_ratio < _DIFF_VOL_THRESHOLD:
            stable_tickers.add(t)

    active_tickers = [t for t in tickers if t not in stable_tickers]
    if stable_tickers:
        log.info(
            f" differential scan: {len(stable_tickers)} tickers skipped "
            f"(stable <{_DIFF_PRICE_THRESHOLD}% move, vol <{_DIFF_VOL_THRESHOLD}×) "
            f"| {len(active_tickers)} active"
        )
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
            _diff_state[t] = {"price": q["p"], "ts": datetime.now(timezone.utc).replace(tzinfo=None)}

    # ── Step 5: generate signals ─────────────────────────────────────────
    _mark_scan_stage("signal_generation")
    try:
        signals = await scan_all(
            active_tickers,
            market_ctx=market_ctx,
            histories={t: histories[t] for t in active_tickers if t in histories},
            infos={t: infos.get(t, {}) for t in active_tickers},
        )
        
        # QENG-6a/b/c: Enrich signals with Meta-Label probability and Cohort assignment
        for sig in signals:
            try:
                from services.signal_ml import predict_meta_prob
                from services.cohort_service import build_policy_version_meta
                
                feats = sig.get("features", {})
                entry_prob = sig.get("confidence", 50.0) / 100.0
                hmm_regime = sig.get("hmmRegime", "")
                vix_val = sig.get("vix")
                sector_etf = sig.get("sectorEtf")
                
                meta_prob = predict_meta_prob(
                    tech=feats,
                    entry_prob=entry_prob,
                    hmm_regime=hmm_regime,
                    vix=vix_val,
                    sector_etf=sector_etf
                )
                
                cohort_meta = build_policy_version_meta(
                    ticker=sig["ticker"],
                    ts=datetime.utcnow(),
                    meta_prob=meta_prob
                )
                sig["cohort_meta"] = cohort_meta
                sig["cohort"] = cohort_meta["cohort"]
            except Exception as e_cohort:
                log.warning(f"Failed to enrich signal with cohort/meta metadata: {e_cohort}")
                
    except Exception as e:
        log.info(f" scan_all failed: {e}")
        raise RuntimeError(f"scan_all failed: {e}") from e

    # ── Step 6: persist (smart daily deduplication) ──────────────────────
    _mark_scan_stage("persistence")
    new_signals, refreshed_unsent = await _persist_scan_signals(signals, _today_start_utc())

    # ── Step 7: auto-send + auto paper trade ────────────────────────────
    _mark_scan_stage("delivery")
    db_settings = await _load_db_settings()

    positions_map: dict = {}
    if db_settings.get("auto_paper_trade") and settings.alpaca_api_key:
        try:
            from services import alpaca_rest

            positions_list = await alpaca_rest.get_positions(settings.alpaca_api_key, settings.alpaca_api_secret)
            positions_map = {p["symbol"].upper(): p for p in positions_list}
        except Exception as e:
            log.info(f" positions fetch failed: {e}")

    await _deliver_scan_signals(
        new_signals, refreshed_unsent, settings, db_settings, positions_map, scan_cycle_started_at
    )

    # ── Step 8: update outcomes ──────────────────────────────────────────
    _mark_scan_stage("outcomes")
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
    _mark_scan_stage("broadcast")
    if broadcast_fn:
        for sig, _, _force in new_signals:
            await broadcast_fn({"type": "new_signal", "signal": sig})

        prices = {q["t"]: {"price": q["p"], "change": q["c"]} for q in quotes}
        await broadcast_fn({"type": "price_update", "quotes": quotes, "prices": prices})

        if market_ctx:
            await broadcast_fn({"type": "market_context", "data": market_ctx})

    log.info(
        f" {datetime.now().strftime('%H:%M:%S')} — "
        f"scanned {len(tickers)} tickers, {len(new_signals)} new, "
        f"{len(signals) - len(new_signals)} refreshed "
        f"({len(refreshed_unsent)} unsent queued)"
    )

    # ── Step 11: analytics pre-computation ──────────────────────────────
    _mark_scan_stage("analytics")
    # Compute backtest summary in background after each scan so heavy GROUP BY
    # queries aren't triggered on every /api/signals/backtest request.
    # Fire-and-forget — never blocks the scan cycle.
    asyncio.ensure_future(_precompute_analytics())
