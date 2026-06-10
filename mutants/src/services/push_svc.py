import json
import logging

from config import get_settings
from pywebpush import WebPushException, webpush

log = logging.getLogger("signal.trade.push")


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_send_web_push__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_send_web_push__mutmut)
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


def x_send_web_push__mutmut_orig(subscription_info: dict, message: dict):
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


def x_send_web_push__mutmut_1(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = None

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


def x_send_web_push__mutmut_2(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = None
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


def x_send_web_push__mutmut_3(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(None, "vapid_private_key", None)
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


def x_send_web_push__mutmut_4(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, None, None)
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


def x_send_web_push__mutmut_5(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr("vapid_private_key", None)
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


def x_send_web_push__mutmut_6(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, None)
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


def x_send_web_push__mutmut_7(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", )
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


def x_send_web_push__mutmut_8(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "XXvapid_private_keyXX", None)
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


def x_send_web_push__mutmut_9(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "VAPID_PRIVATE_KEY", None)
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


def x_send_web_push__mutmut_10(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = None

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


def x_send_web_push__mutmut_11(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = getattr(None, "vapid_subject", "mailto:admin@signal.trade")

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


def x_send_web_push__mutmut_12(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = getattr(s, None, "mailto:admin@signal.trade")

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


def x_send_web_push__mutmut_13(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = getattr(s, "vapid_subject", None)

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


def x_send_web_push__mutmut_14(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = getattr("vapid_subject", "mailto:admin@signal.trade")

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


def x_send_web_push__mutmut_15(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = getattr(s, "mailto:admin@signal.trade")

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


def x_send_web_push__mutmut_16(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = getattr(s, "vapid_subject", )

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


def x_send_web_push__mutmut_17(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = getattr(s, "XXvapid_subjectXX", "mailto:admin@signal.trade")

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


def x_send_web_push__mutmut_18(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = getattr(s, "VAPID_SUBJECT", "mailto:admin@signal.trade")

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


def x_send_web_push__mutmut_19(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = getattr(s, "vapid_subject", "XXmailto:admin@signal.tradeXX")

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


def x_send_web_push__mutmut_20(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = getattr(s, "vapid_subject", "MAILTO:ADMIN@SIGNAL.TRADE")

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


def x_send_web_push__mutmut_21(subscription_info: dict, message: dict):
    """
    Send a web push notification using pywebpush.
    subscription_info needs: endpoint, keys: {p256dh, auth}
    """
    s = get_settings()

    # You need VAPID keys generated (e.g. `vapid --generate`)
    # Set VAPID_PRIVATE_KEY and VAPID_SUBJECT (mailto:you@example.com) in .env
    _vapid_private_key = getattr(s, "vapid_private_key", None)
    vapid_subject = getattr(s, "vapid_subject", "mailto:admin@signal.trade")

    if _vapid_private_key:
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


def x_send_web_push__mutmut_22(subscription_info: dict, message: dict):
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
        log.warning(None)
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


def x_send_web_push__mutmut_23(subscription_info: dict, message: dict):
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
        log.warning("XXVAPID_PRIVATE_KEY not configured. Cannot send web push.XX")
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


def x_send_web_push__mutmut_24(subscription_info: dict, message: dict):
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
        log.warning("vapid_private_key not configured. cannot send web push.")
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


def x_send_web_push__mutmut_25(subscription_info: dict, message: dict):
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
        log.warning("VAPID_PRIVATE_KEY NOT CONFIGURED. CANNOT SEND WEB PUSH.")
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


def x_send_web_push__mutmut_26(subscription_info: dict, message: dict):
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
        return True

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


def x_send_web_push__mutmut_27(subscription_info: dict, message: dict):
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

    vapid_private_key = None

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


def x_send_web_push__mutmut_28(subscription_info: dict, message: dict):
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
        if hasattr(None, "get_secret_value")
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


def x_send_web_push__mutmut_29(subscription_info: dict, message: dict):
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
        if hasattr(_vapid_private_key, None)
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


def x_send_web_push__mutmut_30(subscription_info: dict, message: dict):
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
        if hasattr("get_secret_value")
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


def x_send_web_push__mutmut_31(subscription_info: dict, message: dict):
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
        if hasattr(_vapid_private_key, )
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


def x_send_web_push__mutmut_32(subscription_info: dict, message: dict):
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
        if hasattr(_vapid_private_key, "XXget_secret_valueXX")
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


def x_send_web_push__mutmut_33(subscription_info: dict, message: dict):
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
        if hasattr(_vapid_private_key, "GET_SECRET_VALUE")
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


def x_send_web_push__mutmut_34(subscription_info: dict, message: dict):
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
            subscription_info=None,
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


def x_send_web_push__mutmut_35(subscription_info: dict, message: dict):
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
            data=None,
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": vapid_subject},
        )
        return True
    except WebPushException as ex:
        log.error(f"Web push failed: {repr(ex)}")
        if ex.response and ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def x_send_web_push__mutmut_36(subscription_info: dict, message: dict):
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
            vapid_private_key=None,
            vapid_claims={"sub": vapid_subject},
        )
        return True
    except WebPushException as ex:
        log.error(f"Web push failed: {repr(ex)}")
        if ex.response and ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def x_send_web_push__mutmut_37(subscription_info: dict, message: dict):
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
            vapid_claims=None,
        )
        return True
    except WebPushException as ex:
        log.error(f"Web push failed: {repr(ex)}")
        if ex.response and ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def x_send_web_push__mutmut_38(subscription_info: dict, message: dict):
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


def x_send_web_push__mutmut_39(subscription_info: dict, message: dict):
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
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": vapid_subject},
        )
        return True
    except WebPushException as ex:
        log.error(f"Web push failed: {repr(ex)}")
        if ex.response and ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def x_send_web_push__mutmut_40(subscription_info: dict, message: dict):
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
            vapid_claims={"sub": vapid_subject},
        )
        return True
    except WebPushException as ex:
        log.error(f"Web push failed: {repr(ex)}")
        if ex.response and ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def x_send_web_push__mutmut_41(subscription_info: dict, message: dict):
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
            )
        return True
    except WebPushException as ex:
        log.error(f"Web push failed: {repr(ex)}")
        if ex.response and ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def x_send_web_push__mutmut_42(subscription_info: dict, message: dict):
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
            data=json.dumps(None),
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": vapid_subject},
        )
        return True
    except WebPushException as ex:
        log.error(f"Web push failed: {repr(ex)}")
        if ex.response and ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def x_send_web_push__mutmut_43(subscription_info: dict, message: dict):
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
            vapid_claims={"XXsubXX": vapid_subject},
        )
        return True
    except WebPushException as ex:
        log.error(f"Web push failed: {repr(ex)}")
        if ex.response and ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def x_send_web_push__mutmut_44(subscription_info: dict, message: dict):
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
            vapid_claims={"SUB": vapid_subject},
        )
        return True
    except WebPushException as ex:
        log.error(f"Web push failed: {repr(ex)}")
        if ex.response and ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def x_send_web_push__mutmut_45(subscription_info: dict, message: dict):
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
        return False
    except WebPushException as ex:
        log.error(f"Web push failed: {repr(ex)}")
        if ex.response and ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def x_send_web_push__mutmut_46(subscription_info: dict, message: dict):
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
        log.error(None)
        if ex.response and ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def x_send_web_push__mutmut_47(subscription_info: dict, message: dict):
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
        log.error(f"Web push failed: {repr(None)}")
        if ex.response and ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def x_send_web_push__mutmut_48(subscription_info: dict, message: dict):
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
        if ex.response or ex.response.json():
            log.error(f"Response: {ex.response.json()}")
        return False


def x_send_web_push__mutmut_49(subscription_info: dict, message: dict):
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
            log.error(None)
        return False


def x_send_web_push__mutmut_50(subscription_info: dict, message: dict):
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
        return True

mutants_x_send_web_push__mutmut['_mutmut_orig'] = x_send_web_push__mutmut_orig # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_1'] = x_send_web_push__mutmut_1 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_2'] = x_send_web_push__mutmut_2 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_3'] = x_send_web_push__mutmut_3 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_4'] = x_send_web_push__mutmut_4 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_5'] = x_send_web_push__mutmut_5 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_6'] = x_send_web_push__mutmut_6 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_7'] = x_send_web_push__mutmut_7 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_8'] = x_send_web_push__mutmut_8 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_9'] = x_send_web_push__mutmut_9 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_10'] = x_send_web_push__mutmut_10 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_11'] = x_send_web_push__mutmut_11 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_12'] = x_send_web_push__mutmut_12 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_13'] = x_send_web_push__mutmut_13 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_14'] = x_send_web_push__mutmut_14 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_15'] = x_send_web_push__mutmut_15 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_16'] = x_send_web_push__mutmut_16 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_17'] = x_send_web_push__mutmut_17 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_18'] = x_send_web_push__mutmut_18 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_19'] = x_send_web_push__mutmut_19 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_20'] = x_send_web_push__mutmut_20 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_21'] = x_send_web_push__mutmut_21 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_22'] = x_send_web_push__mutmut_22 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_23'] = x_send_web_push__mutmut_23 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_24'] = x_send_web_push__mutmut_24 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_25'] = x_send_web_push__mutmut_25 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_26'] = x_send_web_push__mutmut_26 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_27'] = x_send_web_push__mutmut_27 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_28'] = x_send_web_push__mutmut_28 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_29'] = x_send_web_push__mutmut_29 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_30'] = x_send_web_push__mutmut_30 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_31'] = x_send_web_push__mutmut_31 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_32'] = x_send_web_push__mutmut_32 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_33'] = x_send_web_push__mutmut_33 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_34'] = x_send_web_push__mutmut_34 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_35'] = x_send_web_push__mutmut_35 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_36'] = x_send_web_push__mutmut_36 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_37'] = x_send_web_push__mutmut_37 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_38'] = x_send_web_push__mutmut_38 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_39'] = x_send_web_push__mutmut_39 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_40'] = x_send_web_push__mutmut_40 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_41'] = x_send_web_push__mutmut_41 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_42'] = x_send_web_push__mutmut_42 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_43'] = x_send_web_push__mutmut_43 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_44'] = x_send_web_push__mutmut_44 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_45'] = x_send_web_push__mutmut_45 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_46'] = x_send_web_push__mutmut_46 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_47'] = x_send_web_push__mutmut_47 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_48'] = x_send_web_push__mutmut_48 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_49'] = x_send_web_push__mutmut_49 # type: ignore # mutmut generated
mutants_x_send_web_push__mutmut['x_send_web_push__mutmut_50'] = x_send_web_push__mutmut_50 # type: ignore # mutmut generated
