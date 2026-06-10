"""Tests for services/push_svc.py."""

import sys
from unittest.mock import MagicMock, patch

# pywebpush may not be installed in test env — stub it out
if "pywebpush" not in sys.modules:
    _stub = MagicMock()
    _stub.WebPushException = type("WebPushException", (Exception,), {})
    sys.modules["pywebpush"] = _stub


def _settings(vapid_key=None, vapid_subject="mailto:test@example.com"):
    s = MagicMock()
    s.vapid_private_key = vapid_key
    s.vapid_subject = vapid_subject
    return s


def test_send_web_push_no_vapid_key_returns_false():
    from services.push_svc import send_web_push

    with patch("services.push_svc.get_settings", return_value=_settings(vapid_key=None)):
        result = send_web_push({"endpoint": "https://x.com", "keys": {}}, {"title": "Test"})

    assert result is False


def test_send_web_push_success():
    from services.push_svc import send_web_push

    s = _settings(vapid_key="fake-key")
    with (
        patch("services.push_svc.get_settings", return_value=s),
        patch("services.push_svc.webpush") as mock_wp,
    ):
        mock_wp.return_value = None
        result = send_web_push(
            {"endpoint": "https://push.example.com", "keys": {"p256dh": "abc", "auth": "def"}},
            {"title": "Trade Signal", "body": "BUY AAPL"},
        )

    assert result is True


def test_send_web_push_exception_returns_false():
    from services.push_svc import WebPushException, send_web_push

    s = _settings(vapid_key="fake-key")
    ex = WebPushException("push failed")
    ex.response = None

    with (
        patch("services.push_svc.get_settings", return_value=s),
        patch("services.push_svc.webpush", side_effect=ex),
    ):
        result = send_web_push({"endpoint": "https://push.example.com", "keys": {}}, {"msg": "x"})

    assert result is False


def test_send_web_push_exception_with_response_json():
    from services.push_svc import WebPushException, send_web_push

    s = _settings(vapid_key="fake-key")
    ex = WebPushException("push failed")
    resp = MagicMock()
    resp.json = MagicMock(return_value={"error": "Subscription expired"})
    ex.response = resp

    with (
        patch("services.push_svc.get_settings", return_value=s),
        patch("services.push_svc.webpush", side_effect=ex),
    ):
        result = send_web_push({"endpoint": "https://push.example.com", "keys": {}}, {"msg": "x"})

    assert result is False


def test_send_web_push_uses_default_vapid_subject():
    from services.push_svc import send_web_push

    s = MagicMock()
    s.vapid_private_key = "key"
    # vapid_subject attribute doesn't exist → getattr fallback
    del s.vapid_subject

    with (
        patch("services.push_svc.get_settings", return_value=s),
        patch("services.push_svc.webpush") as mock_wp,
    ):
        mock_wp.return_value = None
        result = send_web_push({"endpoint": "x", "keys": {}}, {})

    assert result is True
