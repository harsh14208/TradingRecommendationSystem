import json
import logging

from config import get_settings
from pywebpush import WebPushException, webpush

log = logging.getLogger("signal.trade.push")


def send_web_push(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = getattr(s, "vapid_subject", "mailto:admin@signal.trade")

    if not _vapid_private_key:
        log.warning("VAPID_PRIVATE_KEY not configured. Cannot send web push.")
        return False

    vapid_private_key = (
        _vapid_private_key.get_secret_value()
        if hasattr(_vapid_private_key, "get_secret_value")
        else _vapid_private_key
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
