"""
Integration tests for routers/telegram_webhook.py  POST /api/telegram/webhook

Coverage targets:
  - No message body  → 200 {"ok": True}
  - edited_message body → treated like message
  - /start without a code → 200, sends welcome message
  - Non-/start text → 200, sends usage hint
  - Invalid / expired link code (user not found) → 200, sends error reply
  - Chat already linked to a different account → 200, sends warning reply
  - Successful link: sets telegram_chat_id, clears link_code, returns {"ok": True}
  - Missing JSON body → 400
"""

import pytest
import types
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db

try:
    from routers.telegram_webhook import router
    _ROUTER_OK = True
except ImportError:
    _ROUTER_OK = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_app(db_override):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = db_override
    return app


def _db_with_user_lookup(user_for_code=None, user_for_chat_id=None):
    """
    Build a mock async DB session whose execute() calls return either
    the provided User mock or None, depending on which query runs.

    Call pattern:
      1. select(User).where(User.telegram_link_code == code)   → user_for_code
      2. select(User).where(User.telegram_chat_id == chat_id) → user_for_chat_id
    """
    call_count = [0]

    async def _execute(_stmt):
        call_count[0] += 1
        mock_result = MagicMock()
        if call_count[0] == 1:
            mock_result.scalar_one_or_none.return_value = user_for_code
        else:
            mock_result.scalar_one_or_none.return_value = user_for_chat_id
        return mock_result

    db_mock = AsyncMock()
    db_mock.execute = _execute
    db_mock.commit = AsyncMock()

    async def _get_db_override():
        yield db_mock

    return _get_db_override, db_mock


def _make_user(id_=1, email="alice@example.com", link_code="CODE123",
               chat_id=None, subscription_tier="basic"):
    u = MagicMock()
    u.id = id_
    u.email = email
    u.telegram_link_code = link_code
    u.telegram_chat_id = chat_id
    u.subscription_tier = subscription_tier
    return u


def _webhook_body(text="/start CODE123", chat_id="111222333", username="alice"):
    return {
        "message": {
            "chat": {"id": chat_id},
            "text": text,
            "from": {"username": username},
        }
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _ROUTER_OK, reason="telegram_webhook router import failed")
class TestTelegramWebhook:

    def test_empty_body_no_message_returns_ok(self):
        db_override, _ = _db_with_user_lookup()
        app = _make_app(db_override)

        with patch("routers.telegram_webhook._reply", new=AsyncMock()):
            client = TestClient(app)
            resp = client.post(
                "/api/telegram/webhook",
                json={},
            )

        assert resp.status_code == 200
        assert resp.json() == {"ok": True}

    def test_invalid_json_returns_400(self):
        db_override, _ = _db_with_user_lookup()
        app = _make_app(db_override)

        client = TestClient(app)
        resp = client.post(
            "/api/telegram/webhook",
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )

        assert resp.status_code == 400

    def test_start_without_code_returns_ok_and_sends_welcome(self):
        db_override, _ = _db_with_user_lookup()
        app = _make_app(db_override)

        replied_texts = []

        async def _fake_reply(chat_id, text):
            replied_texts.append(text)

        with patch("routers.telegram_webhook._reply", side_effect=_fake_reply):
            client = TestClient(app)
            resp = client.post(
                "/api/telegram/webhook",
                json=_webhook_body(text="/start"),
            )

        assert resp.status_code == 200
        assert resp.json() == {"ok": True}
        assert any("link" in t.lower() or "code" in t.lower() for t in replied_texts)

    def test_non_start_text_sends_usage_hint(self):
        db_override, _ = _db_with_user_lookup()
        app = _make_app(db_override)

        replied_texts = []

        async def _fake_reply(chat_id, text):
            replied_texts.append(text)

        with patch("routers.telegram_webhook._reply", side_effect=_fake_reply):
            client = TestClient(app)
            resp = client.post(
                "/api/telegram/webhook",
                json=_webhook_body(text="Hello bot"),
            )

        assert resp.status_code == 200
        assert resp.json() == {"ok": True}
        assert any("/start" in t for t in replied_texts)

    def test_invalid_code_user_not_found_returns_ok_with_error_reply(self):
        db_override, _ = _db_with_user_lookup(user_for_code=None)
        app = _make_app(db_override)

        replied_texts = []

        async def _fake_reply(chat_id, text):
            replied_texts.append(text)

        with patch("routers.telegram_webhook._reply", side_effect=_fake_reply):
            client = TestClient(app)
            resp = client.post(
                "/api/telegram/webhook",
                json=_webhook_body(text="/start BADCODE"),
            )

        assert resp.status_code == 200
        assert resp.json() == {"ok": True}
        assert any("invalid" in t.lower() or "expired" in t.lower() for t in replied_texts)

    def test_chat_already_linked_to_different_account_sends_warning(self):
        target_user = _make_user(id_=1, link_code="CODE123")
        other_user  = _make_user(id_=2, link_code="OTHER", chat_id="111222333")

        db_override, _ = _db_with_user_lookup(
            user_for_code=target_user,
            user_for_chat_id=other_user,   # different user already owns this chat_id
        )
        app = _make_app(db_override)

        replied_texts = []

        async def _fake_reply(chat_id, text):
            replied_texts.append(text)

        with patch("routers.telegram_webhook._reply", side_effect=_fake_reply):
            client = TestClient(app)
            resp = client.post(
                "/api/telegram/webhook",
                json=_webhook_body(text="/start CODE123", chat_id="111222333"),
            )

        assert resp.status_code == 200
        assert resp.json() == {"ok": True}
        assert any("already linked" in t.lower() or "unlink" in t.lower() for t in replied_texts)

    def test_successful_link_sets_chat_id_and_clears_code(self):
        user = _make_user(id_=1, link_code="CODE123", chat_id=None)
        # chat_id not yet linked to anyone else
        db_override, db_mock = _db_with_user_lookup(
            user_for_code=user,
            user_for_chat_id=None,
        )
        app = _make_app(db_override)

        replied_texts = []

        async def _fake_reply(chat_id, text):
            replied_texts.append(text)

        with patch("routers.telegram_webhook._reply", side_effect=_fake_reply):
            client = TestClient(app)
            resp = client.post(
                "/api/telegram/webhook",
                json=_webhook_body(text="/start CODE123", chat_id="999888777"),
            )

        assert resp.status_code == 200
        assert resp.json() == {"ok": True}
        assert user.telegram_chat_id == "999888777"
        assert user.telegram_link_code is None
        db_mock.commit.assert_awaited_once()

    def test_successful_link_sends_confirmation_reply_with_email(self):
        user = _make_user(id_=1, email="bob@example.com", link_code="XYZ99",
                          chat_id=None, subscription_tier="pro")
        db_override, _ = _db_with_user_lookup(
            user_for_code=user,
            user_for_chat_id=None,
        )
        app = _make_app(db_override)

        replied_texts = []

        async def _fake_reply(chat_id, text):
            replied_texts.append(text)

        with patch("routers.telegram_webhook._reply", side_effect=_fake_reply):
            client = TestClient(app)
            client.post(
                "/api/telegram/webhook",
                json=_webhook_body(text="/start XYZ99", chat_id="555444333"),
            )

        assert any("bob@example.com" in t for t in replied_texts)

    def test_edited_message_processed_like_regular_message(self):
        """edited_message key should be handled the same as message."""
        db_override, _ = _db_with_user_lookup()
        app = _make_app(db_override)

        replied_texts = []

        async def _fake_reply(chat_id, text):
            replied_texts.append(text)

        with patch("routers.telegram_webhook._reply", side_effect=_fake_reply):
            client = TestClient(app)
            resp = client.post(
                "/api/telegram/webhook",
                json={
                    "edited_message": {
                        "chat": {"id": "777"},
                        "text": "Hello",
                        "from": {"username": "charlie"},
                    }
                },
            )

        assert resp.status_code == 200
        # Non-/start text path should be reached, sending usage hint
        assert any("/start" in t for t in replied_texts)

    def test_same_user_relinks_does_not_trigger_conflict(self):
        """If the same user re-sends /start, existing.id == user.id so no conflict."""
        user = _make_user(id_=5, link_code="MYCODE", chat_id="999")
        # "existing" is the same user object
        db_override, db_mock = _db_with_user_lookup(
            user_for_code=user,
            user_for_chat_id=user,
        )
        app = _make_app(db_override)

        replied_texts = []

        async def _fake_reply(chat_id, text):
            replied_texts.append(text)

        with patch("routers.telegram_webhook._reply", side_effect=_fake_reply):
            client = TestClient(app)
            resp = client.post(
                "/api/telegram/webhook",
                json=_webhook_body(text="/start MYCODE", chat_id="999"),
            )

        assert resp.status_code == 200
        # Should proceed to link (commit called) without the conflict warning
        db_mock.commit.assert_awaited_once()
        assert not any("already linked" in t.lower() for t in replied_texts)
