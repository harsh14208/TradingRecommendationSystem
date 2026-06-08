import asyncio
import time
import logging
import ssl
import certifi
from datetime import datetime, timezone
from database import AsyncSessionLocal
from models import SignalDelivery, User, AppSettings
from sqlalchemy import select

log = logging.getLogger("signal.trade.delivery")

_SSL_CTX = ssl.create_default_context(cafile=certifi.where())


def is_in_quiet_hours(now_utc: datetime, tz_str: str, start_str: str, end_str: str) -> bool:
    if not tz_str or not start_str or not end_str:
        return False
    try:
        import pytz
        from datetime import time as dt_time

        tz = pytz.timezone(tz_str)
        local_now = now_utc.astimezone(tz)
        local_time = local_now.time()

        # Parse start and end times
        sh, sm = map(int, start_str.split(":"))
        eh, em = map(int, end_str.split(":"))
        start_time = dt_time(sh, sm)
        end_time = dt_time(eh, em)

        if start_time <= end_time:
            return start_time <= local_time <= end_time
        else:  # Overrides midnight, e.g. 22:00 to 08:00
            return local_time >= start_time or local_time <= end_time
    except Exception as e:
        log.warning(f"[delivery] Error checking quiet hours: {e}")
        return False


def seconds_until_quiet_hours_end(now_utc: datetime, tz_str: str, end_str: str) -> float:
    try:
        import pytz
        import datetime as dt

        tz = pytz.timezone(tz_str)
        local_now = now_utc.astimezone(tz)

        eh, em = map(int, end_str.split(":"))
        local_end = local_now.replace(hour=eh, minute=em, second=0, microsecond=0)

        for day_offset in range(3):
            candidate = local_end + dt.timedelta(days=day_offset)
            if candidate > local_now:
                return (candidate - local_now).total_seconds()
        return 0.0
    except Exception as e:
        log.warning(f"[delivery] Error calculating quiet hours end: {e}")
        return 0.0


async def queue_delivery(signal_id: int, user_id: int, channel: str, payload: dict, max_retries: int = 5):
    """
    Queue a delivery attempt in the background (TSYS-3b).
    """
    asyncio.create_task(deliver_with_retry(signal_id, user_id, channel, payload, max_retries))


async def deliver_with_retry(signal_id: int, user_id: int, channel: str, payload: dict, max_retries: int = 5):
    """
    Delivers a message to a user on a given channel with exponential backoff retries.
    Acts as a unified retry queue and handles dead-letter receipts (TSYS-3b).
    Enforces quiet hours and timezone checks (TSYS-3c).
    """
    from services.http_client import shared_session
    from config import get_settings

    # Generate dedupe key
    if signal_id:
        dedupe_key = f"{signal_id}:{user_id}:{channel}"
    else:
        dedupe_key = f"system:{user_id}:{channel}:{int(time.time() * 1000)}"

    # 1. Check duplicate
    if signal_id:
        async with AsyncSessionLocal() as db:
            existing = (
                await db.execute(select(SignalDelivery).where(SignalDelivery.dedupe_key == dedupe_key))
            ).scalar_one_or_none()
            if existing:
                log.info(f"[delivery] Duplicate delivery blocked for key={dedupe_key}")
                return

    # Check quiet hours & timezone (TSYS-3c)
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        if not user:
            log.warning(f"[delivery] User {user_id} not found. Skipping delivery.")
            return

        from routers.me import _user_pref_key, _NOTIF_PREF_DEFAULTS

        app_row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
        stored = ((app_row.data or {}).get(_user_pref_key(user_id)) or {}) if app_row else {}
        prefs = {**_NOTIF_PREF_DEFAULTS, **stored}

    tz_str = prefs.get("timezone") or "America/New_York"
    q_start = prefs.get("quiet_hours_start")
    q_end = prefs.get("quiet_hours_end")

    in_quiet = False
    now_utc = datetime.now(timezone.utc)
    if q_start and q_end:
        in_quiet = is_in_quiet_hours(now_utc, tz_str, q_start, q_end)

    # 2. Create initial delivery receipt in DB
    initial_status = "deferred" if in_quiet else "pending"
    async with AsyncSessionLocal() as db:
        from services.provider_telemetry import current_cycle_id

        receipt = SignalDelivery(
            signal_id=signal_id,
            user_id=user_id,
            channel=channel,
            status=initial_status,
            retry_count=0,
            dedupe_key=dedupe_key,
            cycle_id=current_cycle_id.get(),
        )
        db.add(receipt)
        await db.commit()
        receipt_id = receipt.id

    if in_quiet:
        sleep_sec = seconds_until_quiet_hours_end(now_utc, tz_str, q_end)
        if sleep_sec > 0:
            log.info(
                f"[delivery] TSYS-3c Quiet Hours active for user={user_id} ({tz_str}): "
                f"{q_start}-{q_end}. Deferring delivery for {sleep_sec:.1f}s until quiet hours end."
            )
            await asyncio.sleep(sleep_sec)

        # Reset to pending before beginning delivery loop
        async with AsyncSessionLocal() as db:
            db_receipt = await db.get(SignalDelivery, receipt_id)
            if db_receipt:
                db_receipt.status = "pending"
                await db.commit()

    backoff = 1.0
    status = "failed"
    error_code = None
    provider_msg_id = None
    latency_ms = None

    for attempt in range(max_retries):
        if attempt > 0:
            # Update receipt to retrying
            async with AsyncSessionLocal() as db:
                db_receipt = await db.get(SignalDelivery, receipt_id)
                if db_receipt:
                    db_receipt.status = "retrying"
                    db_receipt.retry_count = attempt
                    await db.commit()

            await asyncio.sleep(backoff)
            backoff *= 2.0  # exponential backoff

        start_time = time.monotonic()
        try:
            success = False
            err = None
            msg_id = None

            if channel == "telegram":
                s = get_settings()
                url = f"https://api.telegram.org/bot{s.telegram_bot_token}/sendMessage"
                async with shared_session() as session:
                    async with session.post(url, json=payload, timeout=5.0) as resp:
                        latency_ms = (time.monotonic() - start_time) * 1000
                        if resp.status == 200:
                            res_data = await resp.json()
                            if res_data.get("ok"):
                                success = True
                                msg_id = str(res_data.get("result", {}).get("message_id", ""))
                            else:
                                err = f"TG error: {res_data.get('description')}"
                        else:
                            err = f"HTTP {resp.status}"

            elif channel == "discord":
                webhook_url = payload.get("webhook_url")
                discord_payload = payload.get("payload")
                if not webhook_url:
                    err = "Missing webhook_url"
                else:
                    async with shared_session() as session:
                        async with session.post(webhook_url, json=discord_payload, timeout=5.0) as resp:
                            latency_ms = (time.monotonic() - start_time) * 1000
                            if resp.status in (200, 204):
                                success = True
                            else:
                                err = f"HTTP {resp.status}"

            elif channel == "push":
                from services.push_svc import send_web_push

                sub_info = payload.get("subscription_info")
                push_payload = payload.get("payload")
                if not sub_info:
                    err = "Missing subscription_info"
                else:
                    # Run blocking call in thread
                    await asyncio.to_thread(send_web_push, sub_info, push_payload)
                    latency_ms = (time.monotonic() - start_time) * 1000
                    success = True

            elif channel == "webhook":
                webhook_url = payload.get("webhook_url")
                sig_data = payload.get("signal_data")
                if not webhook_url:
                    err = "Missing webhook_url"
                else:
                    import hashlib
                    import hmac
                    import json

                    # Get user's webhook_secret or default to jwt_secret
                    async with AsyncSessionLocal() as db:
                        user = await db.get(User, user_id)
                        secret = (user.webhook_secret or get_settings().jwt_secret or "").encode()

                    payload_bytes = json.dumps(sig_data, default=str).encode()
                    sig_hdr = "sha256=" + hmac.new(secret, payload_bytes, hashlib.sha256).hexdigest()

                    async with shared_session() as session:
                        async with session.post(
                            webhook_url,
                            data=payload_bytes,
                            headers={"Content-Type": "application/json", "X-Signal-Trade-Signature": sig_hdr},
                            ssl=_SSL_CTX,
                            timeout=5.0,
                        ) as resp:
                            latency_ms = (time.monotonic() - start_time) * 1000
                            if resp.status in (200, 201, 202, 204):
                                success = True
                            else:
                                err = f"HTTP {resp.status}"

            if success:
                status = "sent"
                error_code = None
                provider_msg_id = msg_id
                break
            else:
                error_code = err
                log.warning(f"[delivery] Attempt {attempt + 1} failed for {channel} to user {user_id}: {err}")

        except Exception as e:
            latency_ms = (time.monotonic() - start_time) * 1000
            error_code = str(e)
            log.warning(f"[delivery] Attempt {attempt + 1} exception for {channel} to user {user_id}: {e}")

    # 3. Record final result (dead-letter logging if status is still 'failed')
    async with AsyncSessionLocal() as db:
        db_receipt = await db.get(SignalDelivery, receipt_id)
        if db_receipt:
            db_receipt.status = status
            db_receipt.error_code = error_code[:50] if error_code else None
            db_receipt.provider_message_id = provider_msg_id
            db_receipt.latency_ms = latency_ms
            if status == "failed":
                log.error(
                    f"[delivery] TSYS-3b Dead-letter triggered: delivery {channel} failed for user={user_id} after {max_retries} attempts. Error: {error_code}"
                )
            await db.commit()
