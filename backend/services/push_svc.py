import json
import logging
from urllib.parse import urlparse

from config import get_settings
from models import PushSubscription
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from pywebpush import WebPushException, webpush
except ImportError:  # pragma: no cover - optional dependency
    webpush = None
    WebPushException = Exception

log = logging.getLogger("signal.trade.push")


def send_web_push(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    if webpush is None:
        log.warning("pywebpush not installed. Cannot send web push.")
        return False

    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = getattr(s, "vapid_subject", "mailto:admin@signal.trade")

    if not _vapid_private_key:
        log.warning("VAPID_PRIVATE_KEY not configured. Cannot send web push.")
        return False

    vapid_private_key = (
        _vapid_private_key.get_secret_value() if hasattr(_vapid_private_key, "get_secret_value") else _vapid_private_key
    )

    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(message),
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": vapid_subject},
        )
        return True
    except WebPushException as ex:
        log.error(f"Web push failed: {repr(ex)}")
        if ex.response and ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def _host_allowed(endpoint: str, allowed: set[str]) -> bool:
    if not allowed:
        return True
    parsed = urlparse(endpoint)
    host = (parsed.hostname or "").lower().lstrip(".")
    return any(host == a or host.endswith("." + a) for a in allowed)


async def save_push_subscription(db: AsyncSession, user_id: int, endpoint: str, p256dh: str, auth: str) -> bool:
    """Persist a web-push subscription, enforcing endpoint host allowlist.

    Returns True if a new row was inserted, False if it already existed.
    Commits the session.
    """
    s = get_settings()
    allowed = {h.strip().lower() for h in s.push_allowed_hosts.split(",") if h.strip()}
    if not _host_allowed(endpoint, allowed):
        raise ValueError("Push endpoint host not in allowlist")

    existing = (
        await db.execute(select(PushSubscription).where(PushSubscription.endpoint == endpoint))
    ).scalar_one_or_none()
    if existing:
        return False

    db.add(PushSubscription(user_id=user_id, endpoint=endpoint, p256dh=p256dh, auth=auth))
    await db.commit()
    return True
