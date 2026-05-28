"""
Unit tests for services/telegram_svc.py.

Coverage targets:
  - format_signal: all action emojis, with/without entry+stop+target, None-safe fields
  - send_telegram: unconfigured (no token), unconfigured (no chat_id), success path,
                   Telegram API-level error, network exception
"""

import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _base_signal(**overrides):
    """Return a minimal valid signal dict, overrideable via kwargs."""
    sig = {
        "action": "BUY",
        "ticker": "AAPL",
        "price": 150.00,
        "confidence": 72.5,
        "headline": "Apple hits new highs on AI news",
        "rr": "2.5",
    }
    sig.update(overrides)
    return sig


# ---------------------------------------------------------------------------
# format_signal tests
# ---------------------------------------------------------------------------


class TestFormatSignal:
    """Tests for the pure-function format_signal."""

    def setup_method(self):
        from services.telegram_svc import format_signal

        self.format_signal = format_signal

    def test_buy_action_uses_green_emoji(self):
        sig = _base_signal(action="BUY")
        result = self.format_signal(sig)
        assert "🟢" in result
        assert "*BUY AAPL*" in result

    def test_sell_action_uses_red_emoji(self):
        sig = _base_signal(action="SELL")
        result = self.format_signal(sig)
        assert "🔴" in result
        assert "*SELL AAPL*" in result

    def test_hold_action_uses_yellow_emoji(self):
        sig = _base_signal(action="HOLD")
        result = self.format_signal(sig)
        assert "🟡" in result
        assert "*HOLD AAPL*" in result

    def test_unknown_action_uses_white_emoji(self):
        sig = _base_signal(action="ALERT")
        result = self.format_signal(sig)
        assert "⚪" in result

    def test_confidence_formatted_as_integer_percent(self):
        sig = _base_signal(confidence=72.9)
        result = self.format_signal(sig)
        # 72.9 rounded to 0 decimals → "73%"
        assert "73%" in result

    def test_price_formatted_to_two_decimal_places(self):
        sig = _base_signal(price=150.5)
        result = self.format_signal(sig)
        assert "$150.50" in result

    def test_rr_included_when_present(self):
        sig = _base_signal(rr="3.1")
        result = self.format_signal(sig)
        assert "R:R 3.1" in result

    def test_rr_falls_back_to_em_dash_when_missing(self):
        sig = _base_signal()
        sig.pop("rr", None)
        result = self.format_signal(sig)
        assert "R:R —" in result

    def test_headline_included_as_italic(self):
        sig = _base_signal(headline="Earnings beat expectations")
        result = self.format_signal(sig)
        assert "_Earnings beat expectations_" in result

    def test_entry_stop_target_line_appended_when_all_present(self):
        sig = _base_signal(entry=148.00, stop=144.00, target=158.00)
        result = self.format_signal(sig)
        assert "Entry $148.00" in result
        assert "Stop $144.00" in result
        assert "TP $158.00" in result

    def test_entry_stop_target_line_omitted_when_any_is_missing(self):
        # Only entry + stop, no target
        sig = _base_signal(entry=148.00, stop=144.00)
        result = self.format_signal(sig)
        assert "Entry" not in result

    def test_entry_stop_target_line_omitted_when_entry_is_none(self):
        sig = _base_signal(entry=None, stop=144.00, target=158.00)
        result = self.format_signal(sig)
        assert "Entry" not in result

    def test_disclaimer_always_present(self):
        sig = _base_signal()
        result = self.format_signal(sig)
        assert "_Not financial advice · Signal.Trade_" in result

    def test_output_is_multiline_string(self):
        sig = _base_signal()
        result = self.format_signal(sig)
        assert "\n" in result

    def test_entry_zero_treated_as_falsy_skips_trade_line(self):
        # entry=0 is falsy, so the entry/stop/target block should be skipped
        sig = _base_signal(entry=0, stop=144.00, target=158.00)
        result = self.format_signal(sig)
        assert "Entry" not in result


# ---------------------------------------------------------------------------
# send_telegram tests
# ---------------------------------------------------------------------------


class TestSendTelegram:
    """Tests for the async send_telegram function."""

    @pytest.mark.asyncio
    async def test_returns_false_when_bot_token_missing(self):
        from services.telegram_svc import send_telegram

        fake_settings = types.SimpleNamespace(
            telegram_bot_token="",
            telegram_chat_id="123456",
        )
        with patch("services.telegram_svc.aiohttp"):
            with patch("config.get_settings", return_value=fake_settings):
                ok, msg = await send_telegram(_base_signal())

        assert ok is False
        assert "TELEGRAM_BOT_TOKEN" in msg or "not configured" in msg.lower()

    @pytest.mark.asyncio
    async def test_returns_false_when_chat_id_missing(self):
        from services.telegram_svc import send_telegram

        fake_settings = types.SimpleNamespace(
            telegram_bot_token="bot:TOKEN",
            telegram_chat_id="",
        )
        with patch("config.get_settings", return_value=fake_settings):
            ok, msg = await send_telegram(_base_signal())

        assert ok is False
        assert "not configured" in msg.lower() or "TELEGRAM_CHAT_ID" in msg

    @pytest.mark.asyncio
    async def test_success_path_returns_true_and_message_id(self):
        from services.telegram_svc import send_telegram

        fake_settings = types.SimpleNamespace(
            telegram_bot_token="bot:TOKEN",
            telegram_chat_id="-1001234567890",
        )

        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(
            return_value={
                "ok": True,
                "result": {"message_id": 42},
            }
        )

        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_resp)

        mock_session_ctx = MagicMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("config.get_settings", return_value=fake_settings):
            with patch("aiohttp.ClientSession", return_value=mock_session_ctx):
                ok, detail = await send_telegram(_base_signal())

        assert ok is True
        assert detail == "42"

    @pytest.mark.asyncio
    async def test_api_error_returns_false_with_description(self):
        from services.telegram_svc import send_telegram

        fake_settings = types.SimpleNamespace(
            telegram_bot_token="bot:TOKEN",
            telegram_chat_id="-1001234567890",
        )

        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(
            return_value={
                "ok": False,
                "description": "Bad Request: chat not found",
            }
        )

        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_resp)

        mock_session_ctx = MagicMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("config.get_settings", return_value=fake_settings):
            with patch("aiohttp.ClientSession", return_value=mock_session_ctx):
                ok, detail = await send_telegram(_base_signal())

        assert ok is False
        assert "chat not found" in detail

    @pytest.mark.asyncio
    async def test_api_error_without_description_uses_fallback_message(self):
        from services.telegram_svc import send_telegram

        fake_settings = types.SimpleNamespace(
            telegram_bot_token="bot:TOKEN",
            telegram_chat_id="-1001234567890",
        )

        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value={"ok": False})

        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_resp)

        mock_session_ctx = MagicMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("config.get_settings", return_value=fake_settings):
            with patch("aiohttp.ClientSession", return_value=mock_session_ctx):
                ok, detail = await send_telegram(_base_signal())

        assert ok is False
        assert detail == "Unknown Telegram error"

    @pytest.mark.asyncio
    async def test_network_exception_returns_false_with_error_string(self):
        from services.telegram_svc import send_telegram

        fake_settings = types.SimpleNamespace(
            telegram_bot_token="bot:TOKEN",
            telegram_chat_id="-1001234567890",
        )

        mock_session_ctx = MagicMock()
        mock_session_ctx.__aenter__ = AsyncMock(side_effect=ConnectionError("Network unreachable"))
        mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("config.get_settings", return_value=fake_settings):
            with patch("aiohttp.ClientSession", return_value=mock_session_ctx):
                ok, detail = await send_telegram(_base_signal())

        assert ok is False
        assert "Network unreachable" in detail

    @pytest.mark.asyncio
    async def test_signal_with_full_trade_params_sends_correctly(self):
        """Verify format_signal is called inside send_telegram with entry/stop/target."""
        from services.telegram_svc import send_telegram

        fake_settings = types.SimpleNamespace(
            telegram_bot_token="bot:TOKEN",
            telegram_chat_id="-1001234567890",
        )
        sig = _base_signal(entry=148.00, stop=144.00, target=158.00)

        posted_payloads = []

        async def _fake_post(url, json=None, **kwargs):
            posted_payloads.append(json)
            resp = AsyncMock()
            resp.json = AsyncMock(return_value={"ok": True, "result": {"message_id": 7}})
            return resp

        mock_session = AsyncMock()
        mock_session.post = _fake_post

        mock_session_ctx = MagicMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("config.get_settings", return_value=fake_settings):
            with patch("aiohttp.ClientSession", return_value=mock_session_ctx):
                ok, _ = await send_telegram(sig)

        assert ok is True
        assert len(posted_payloads) == 1
        payload = posted_payloads[0]
        assert "Entry $148.00" in payload["text"]
        assert "Stop $144.00" in payload["text"]
        assert payload["parse_mode"] == "Markdown"
        assert payload["chat_id"] == "-1001234567890"
