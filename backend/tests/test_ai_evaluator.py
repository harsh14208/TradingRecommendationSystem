"""Tests for services/ai_evaluator.py — AI pre-execution trade gate."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest


@pytest.fixture
def _reset_settings_cache():
    """Clear the cached settings singleton so env overrides are re-read."""
    with patch("config._settings_cache", None):
        yield


def _mock_session(response_text: str, status: int = 200, raise_for_status: bool = True):
    """Build an async context manager that mimics an aiohttp response."""
    resp = AsyncMock()
    resp.status = status
    resp.json = AsyncMock(return_value={"choices": [{"message": {"content": response_text}}]})
    resp.raise_for_status = MagicMock()
    if not raise_for_status:
        resp.raise_for_status.side_effect = aiohttp.ClientResponseError(
            request_info=MagicMock(),
            history=(),
            status=500,
            message="Internal Server Error",
            headers={},
        )

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=resp)
    cm.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock()
    session.post = MagicMock(return_value=cm)
    return session


def _sample_signal():
    return {
        "ticker": "AAPL",
        "action": "BUY",
        "confidence": 82.0,
        "price": 175.0,
        "entry": 175.0,
        "stop": 170.0,
        "target": 185.0,
        "style": "swing",
        "rationale": [{"src": "mr", "head": "Mean reversion bounce", "body": "Oversold on daily RSI."}],
        "sources": ["mr", "breadth"],
    }


@pytest.mark.asyncio
async def test_disabled_returns_approved(_reset_settings_cache):
    from services.ai_evaluator import evaluate_trade

    with patch("services.ai_evaluator.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(ai_eval_enabled=False)
        result = await evaluate_trade(_sample_signal())

    assert result.approved is True
    assert "disabled" in result.reasoning.lower()


@pytest.mark.asyncio
async def test_enabled_by_default_with_no_key_fail_open(_reset_settings_cache):
    from services.ai_evaluator import evaluate_trade

    with patch("services.ai_evaluator.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            ai_eval_enabled=True,
            ai_eval_provider="openai",
            ai_eval_model="gpt-4o-mini",
            ai_eval_timeout=15,
            ai_eval_fail_open_on_error=True,
            ai_eval_base_url="",
            openai_api_key="",
        )
        result = await evaluate_trade(_sample_signal())

    assert result.approved is True
    assert result.risk_flag == "config_error"


@pytest.mark.asyncio
async def test_openai_approve(_reset_settings_cache):
    from services.ai_evaluator import evaluate_trade

    ai_response = json.dumps(
        {"decision": "approve", "reasoning": "Clean setup.", "risk_flag": "none", "confidence": 0.85}
    )
    session = _mock_session(ai_response)

    with (
        patch("services.ai_evaluator.get_settings") as mock_settings,
        patch("services.ai_evaluator.get_session", return_value=session),
    ):
        mock_settings.return_value = MagicMock(
            ai_eval_enabled=True,
            ai_eval_provider="openai",
            ai_eval_model="gpt-4o-mini",
            ai_eval_timeout=15,
            ai_eval_fail_open_on_error=True,
            ai_eval_base_url="",
            openai_api_key="sk-test",
        )
        result = await evaluate_trade(_sample_signal())

    assert result.approved is True
    assert result.reasoning == "Clean setup."
    assert result.risk_flag is None
    assert result.confidence == pytest.approx(0.85)

    # Verify the official OpenAI endpoint was used and response_format was set.
    call_args = session.post.call_args
    assert call_args[0][0] == "https://api.openai.com/v1/chat/completions"
    assert call_args[1]["json"]["response_format"] == {"type": "json_object"}


@pytest.mark.asyncio
async def test_anthropic_block(_reset_settings_cache):
    from services.ai_evaluator import evaluate_trade

    ai_response = json.dumps(
        {
            "decision": "block",
            "reasoning": "Earnings tomorrow creates unacceptable event risk.",
            "risk_flag": "earnings",
            "confidence": 0.92,
        }
    )

    resp = AsyncMock()
    resp.status = 200
    resp.json = AsyncMock(return_value={"content": [{"text": ai_response}]})
    resp.raise_for_status = MagicMock()

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=resp)
    cm.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock()
    session.post = MagicMock(return_value=cm)

    with (
        patch("services.ai_evaluator.get_settings") as mock_settings,
        patch("services.ai_evaluator.get_session", return_value=session),
    ):
        mock_settings.return_value = MagicMock(
            ai_eval_enabled=True,
            ai_eval_provider="anthropic",
            ai_eval_model="claude-3-5-haiku-20241022",
            ai_eval_timeout=15,
            ai_eval_fail_open_on_error=True,
            ai_eval_base_url="",
            anthropic_api_key="sk-ant-test",
        )
        result = await evaluate_trade(_sample_signal())

    assert result.approved is False
    assert result.risk_flag == "earnings"
    assert result.confidence == pytest.approx(0.92)

    call_args = session.post.call_args
    assert call_args[0][0] == "https://api.anthropic.com/v1/messages"
    assert call_args[1]["headers"]["x-api-key"] == "sk-ant-test"


@pytest.mark.asyncio
async def test_openai_compatible_no_response_format(_reset_settings_cache):
    from services.ai_evaluator import evaluate_trade

    ai_response = json.dumps(
        {"decision": "approve", "reasoning": "Looks good.", "risk_flag": "none", "confidence": 0.7}
    )
    session = _mock_session(ai_response)

    with (
        patch("services.ai_evaluator.get_settings") as mock_settings,
        patch("services.ai_evaluator.get_session", return_value=session),
    ):
        mock_settings.return_value = MagicMock(
            ai_eval_enabled=True,
            ai_eval_provider="openai-compatible",
            ai_eval_model="local-model",
            ai_eval_timeout=15,
            ai_eval_fail_open_on_error=True,
            ai_eval_base_url="http://localhost:1234/v1",
            openai_api_key="not-needed",
        )
        result = await evaluate_trade(_sample_signal())

    assert result.approved is True
    call_args = session.post.call_args
    assert call_args[0][0] == "http://localhost:1234/v1/chat/completions"
    assert "response_format" not in call_args[1]["json"]


@pytest.mark.asyncio
async def test_kimi_approve(_reset_settings_cache):
    from services.ai_evaluator import evaluate_trade

    ai_response = json.dumps(
        {"decision": "approve", "reasoning": "Setup looks clean.", "risk_flag": "none", "confidence": 0.8}
    )
    session = _mock_session(ai_response)

    with (
        patch("services.ai_evaluator.get_settings") as mock_settings,
        patch("services.ai_evaluator.get_session", return_value=session),
    ):
        mock_settings.return_value = MagicMock(
            ai_eval_enabled=True,
            ai_eval_provider="kimi",
            ai_eval_model="kimi-latest",
            ai_eval_timeout=15,
            ai_eval_fail_open_on_error=True,
            ai_eval_base_url="",
            kimi_api_key="kimi-test-key",
        )
        result = await evaluate_trade(_sample_signal())

    assert result.approved is True
    assert result.reasoning == "Setup looks clean."

    call_args = session.post.call_args
    assert call_args[0][0] == "https://api.moonshot.cn/v1/chat/completions"
    assert call_args[1]["headers"]["Authorization"] == "Bearer kimi-test-key"


@pytest.mark.asyncio
async def test_malformed_response_fail_open(_reset_settings_cache):
    from services.ai_evaluator import evaluate_trade

    session = _mock_session("not json")

    with (
        patch("services.ai_evaluator.get_settings") as mock_settings,
        patch("services.ai_evaluator.get_session", return_value=session),
    ):
        mock_settings.return_value = MagicMock(
            ai_eval_enabled=True,
            ai_eval_provider="openai",
            ai_eval_model="gpt-4o-mini",
            ai_eval_timeout=15,
            ai_eval_fail_open_on_error=True,
            ai_eval_base_url="",
            openai_api_key="sk-test",
        )
        result = await evaluate_trade(_sample_signal())

    assert result.approved is True
    assert result.risk_flag == "parse_error"


@pytest.mark.asyncio
async def test_http_error_fail_closed(_reset_settings_cache):
    from services.ai_evaluator import evaluate_trade

    session = _mock_session("", status=500, raise_for_status=False)

    with (
        patch("services.ai_evaluator.get_settings") as mock_settings,
        patch("services.ai_evaluator.get_session", return_value=session),
    ):
        mock_settings.return_value = MagicMock(
            ai_eval_enabled=True,
            ai_eval_provider="openai",
            ai_eval_model="gpt-4o-mini",
            ai_eval_timeout=15,
            ai_eval_fail_open_on_error=False,
            ai_eval_base_url="",
            openai_api_key="sk-test",
        )
        result = await evaluate_trade(_sample_signal())

    assert result.approved is False
    assert result.risk_flag == "api_error"


@pytest.mark.asyncio
async def test_missing_key_returns_config_error(_reset_settings_cache):
    from services.ai_evaluator import evaluate_trade

    with patch("services.ai_evaluator.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            ai_eval_enabled=True,
            ai_eval_provider="openai",
            ai_eval_model="gpt-4o-mini",
            ai_eval_timeout=15,
            ai_eval_fail_open_on_error=True,
            ai_eval_base_url="",
            openai_api_key="",
        )
        result = await evaluate_trade(_sample_signal())

    assert result.approved is True
    assert result.risk_flag == "config_error"
