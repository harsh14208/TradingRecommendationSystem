"""Tests for services/discord_bot.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _signal(action="BUY"):
    return {
        "action": action,
        "ticker": "AAPL",
        "headline": "Strong buy signal",
        "confidence": 75.5,
        "price": 150.00,
        "rr": "1:2",
        "entry": 150.0,
        "stop": 145.0,
        "target": 160.0,
        "plain_english": {"summary": "Technical breakout with strong volume."},
    }


@pytest.mark.asyncio
async def test_no_webhook_url_returns_false():
    from services.discord_bot import send_discord_signal

    result = await send_discord_signal("", _signal())
    assert result is False


@pytest.mark.asyncio
async def test_buy_signal_sent_successfully():
    from services.discord_bot import send_discord_signal

    mock_response = AsyncMock()
    mock_response.status = 204

    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session.post = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_response),
                __aexit__=AsyncMock(return_value=False),
            )
        )
        mock_session_cls.return_value = mock_session

        result = await send_discord_signal("https://discord.com/api/webhooks/123/abc", _signal("BUY"))

    assert result is True


@pytest.mark.asyncio
async def test_sell_signal_red_color():
    from services.discord_bot import send_discord_signal

    captured_payload = {}

    resp = AsyncMock()
    resp.status = 200

    post_ctx = AsyncMock()
    post_ctx.__aenter__ = AsyncMock(return_value=resp)
    post_ctx.__aexit__ = AsyncMock(return_value=False)

    def _post(url, json=None, headers=None):
        captured_payload.update(json or {})
        return post_ctx

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.post = _post

    with patch("aiohttp.ClientSession", return_value=mock_session):
        await send_discord_signal("https://discord.com/api/webhooks/123/abc", _signal("SELL"))

    embed = captured_payload.get("embeds", [{}])[0]
    assert embed.get("color") == 0xEF4444


@pytest.mark.asyncio
async def test_hold_signal_yellow_color():
    from services.discord_bot import send_discord_signal

    captured_payload = {}

    resp = AsyncMock()
    resp.status = 200

    post_ctx = AsyncMock()
    post_ctx.__aenter__ = AsyncMock(return_value=resp)
    post_ctx.__aexit__ = AsyncMock(return_value=False)

    def _post(url, json=None, headers=None):
        captured_payload.update(json or {})
        return post_ctx

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.post = _post

    with patch("aiohttp.ClientSession", return_value=mock_session):
        await send_discord_signal("https://discord.com/api/webhooks/123/abc", _signal("HOLD"))

    embed = captured_payload.get("embeds", [{}])[0]
    assert embed.get("color") == 0xF59E0B


@pytest.mark.asyncio
async def test_status_error_returns_false():
    from services.discord_bot import send_discord_signal

    mock_response = AsyncMock()
    mock_response.status = 400

    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session.post = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_response),
                __aexit__=AsyncMock(return_value=False),
            )
        )
        mock_session_cls.return_value = mock_session

        result = await send_discord_signal("https://discord.com/api/webhooks/123/abc", _signal())

    assert result is False


@pytest.mark.asyncio
async def test_exception_returns_false():
    from services.discord_bot import send_discord_signal

    with patch("aiohttp.ClientSession", side_effect=Exception("network error")):
        result = await send_discord_signal("https://discord.com/api/webhooks/123/abc", _signal())

    assert result is False
