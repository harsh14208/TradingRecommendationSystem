"""
Tests for the extracted fetch_market_context() function in scanner.py.
Verifies: best-effort error handling, dict keys present, buy_saturated logic.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ── helpers ───────────────────────────────────────────────────────────────────

def _settings(**kw):
    m = MagicMock()
    m.tickers = kw.get("tickers", ["AAPL", "MSFT"])
    m.alpaca_api_key    = kw.get("alpaca_api_key", None)
    m.alpaca_api_secret = kw.get("alpaca_api_secret", None)
    return m


def _run(coro):
    return asyncio.run(coro)


# ── basic smoke — all sub-fetches fail gracefully ─────────────────────────────

@patch("services.scanner.get_fear_greed",     new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_macro_context",  new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_put_call_ratio", new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_market_breadth", new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_aaii_sentiment", new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_cot_signal",     new_callable=AsyncMock, return_value=None)
@patch("services.scanner._compute_adaptive_weights", new_callable=AsyncMock, return_value={})
@patch("services.scanner._load_db_settings",  new_callable=AsyncMock, return_value={})
@patch("services.scanner.AsyncSessionLocal")
def test_market_context_all_null(mock_session, *_mocks):
    """fetch_market_context returns a dict even when every data source is None."""
    from services.scanner import fetch_market_context

    # BUY:SELL query: return (0, 0)
    db_cm = MagicMock()
    db_cm.__aenter__ = AsyncMock(return_value=db_cm)
    db_cm.__aexit__  = AsyncMock(return_value=False)
    row_mock = MagicMock()
    row_mock.__getitem__ = lambda self, i: 0
    db_cm.execute = AsyncMock(return_value=MagicMock(fetchone=MagicMock(return_value=(0, 0))))
    mock_session.return_value = db_cm

    ctx = _run(fetch_market_context(["AAPL"], _settings()))
    assert isinstance(ctx, dict)
    assert "buy_saturated" in ctx
    assert ctx["buy_saturated"] is False


@patch("services.scanner.get_fear_greed",     new_callable=AsyncMock, return_value={"score": 55, "label": "greed"})
@patch("services.scanner.get_macro_context",  new_callable=AsyncMock, return_value={"vix": 18.2, "macro_score": 2})
@patch("services.scanner.get_put_call_ratio", new_callable=AsyncMock, return_value=0.85)
@patch("services.scanner.get_market_breadth", new_callable=AsyncMock, return_value={"pct_above_200d": 60})
@patch("services.scanner.get_aaii_sentiment", new_callable=AsyncMock, return_value={"spread": 10, "signal": "bullish"})
@patch("services.scanner.get_cot_signal",     new_callable=AsyncMock, return_value={"signal": "bullish"})
@patch("services.scanner._compute_adaptive_weights", new_callable=AsyncMock, return_value={"news": 1.1})
@patch("services.scanner._load_db_settings",  new_callable=AsyncMock, return_value={"weight_overrides": {}})
@patch("services.scanner.AsyncSessionLocal")
def test_market_context_happy_path(mock_session, *_mocks):
    """fetch_market_context populates all core keys when data sources succeed."""
    from services.scanner import fetch_market_context

    db_cm = MagicMock()
    db_cm.__aenter__ = AsyncMock(return_value=db_cm)
    db_cm.__aexit__  = AsyncMock(return_value=False)
    db_cm.execute = AsyncMock(return_value=MagicMock(fetchone=MagicMock(return_value=(8, 3))))
    mock_session.return_value = db_cm

    ctx = _run(fetch_market_context(["AAPL"], _settings()))

    assert ctx.get("fear_greed", {}).get("score") == 55
    assert ctx.get("macro", {}).get("vix") == 18.2
    assert "buy_sell_ratio" in ctx
    assert ctx["buy_sell_ratio"] == round(8 / 3, 2)
    assert ctx["buy_saturated"] is False


@patch("services.scanner.get_fear_greed",     new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_macro_context",  new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_put_call_ratio", new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_market_breadth", new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_aaii_sentiment", new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_cot_signal",     new_callable=AsyncMock, return_value=None)
@patch("services.scanner._compute_adaptive_weights", new_callable=AsyncMock, return_value={})
@patch("services.scanner._load_db_settings",  new_callable=AsyncMock, return_value={})
@patch("services.scanner.AsyncSessionLocal")
def test_buy_saturated_activated_when_ratio_exceeds_4(mock_session, *_mocks):
    """buy_saturated is True when 7-day BUY:SELL ratio > 4.0."""
    from services.scanner import fetch_market_context

    db_cm = MagicMock()
    db_cm.__aenter__ = AsyncMock(return_value=db_cm)
    db_cm.__aexit__  = AsyncMock(return_value=False)
    # 25 BUYs, 5 SELLs → ratio 5.0 > 4.0
    db_cm.execute = AsyncMock(return_value=MagicMock(fetchone=MagicMock(return_value=(25, 5))))
    mock_session.return_value = db_cm

    ctx = _run(fetch_market_context(["AAPL"], _settings()))
    assert ctx["buy_saturated"] is True
    assert ctx["buy_sell_ratio"] == 5.0


@patch("services.scanner.get_fear_greed",     new_callable=AsyncMock, side_effect=RuntimeError("network"))
@patch("services.scanner.get_macro_context",  new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_put_call_ratio", new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_market_breadth", new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_aaii_sentiment", new_callable=AsyncMock, return_value=None)
@patch("services.scanner.get_cot_signal",     new_callable=AsyncMock, return_value=None)
@patch("services.scanner._compute_adaptive_weights", new_callable=AsyncMock, return_value={})
@patch("services.scanner._load_db_settings",  new_callable=AsyncMock, return_value={})
@patch("services.scanner.AsyncSessionLocal")
def test_market_context_survives_gather_exception(mock_session, *_mocks):
    """fetch_market_context handles exceptions from asyncio.gather without crashing."""
    from services.scanner import fetch_market_context

    db_cm = MagicMock()
    db_cm.__aenter__ = AsyncMock(return_value=db_cm)
    db_cm.__aexit__  = AsyncMock(return_value=False)
    db_cm.execute = AsyncMock(return_value=MagicMock(fetchone=MagicMock(return_value=(0, 1))))
    mock_session.return_value = db_cm

    # Should not raise — errors are best-effort
    ctx = _run(fetch_market_context(["AAPL"], _settings()))
    assert isinstance(ctx, dict)
    assert "buy_saturated" in ctx
