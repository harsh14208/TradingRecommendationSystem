"""Mocked-session unit tests for additional data-service fetchers
(market_calendar, massive_ratios, fear_greed)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _mock_session(payload, status=200):
    resp = AsyncMock()
    resp.status = status
    resp.json = AsyncMock(return_value=payload)
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.get = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=resp),
            __aexit__=AsyncMock(return_value=False),
        )
    )
    return session


# ── market_calendar.get_upcoming_holidays ────────────────────────────────────


@pytest.mark.asyncio
async def test_holidays_no_key(monkeypatch):
    import services.market_calendar as mc

    mc._cache["data"] = None
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    monkeypatch.delenv("MASSIVE_API_KEY", raising=False)
    assert await mc.get_upcoming_holidays() == []


@pytest.mark.asyncio
async def test_holidays_parses_nyse_closed(monkeypatch):
    import services.market_calendar as mc

    mc._cache["data"] = None
    monkeypatch.setenv("POLYGON_API_KEY", "k")
    payload = [
        {"status": "closed", "exchange": "NYSE", "date": "2026-07-03", "name": "Independence Day"},
        {"status": "closed", "exchange": "LSE", "date": "2026-07-03", "name": "Foreign"},  # ignored
        {"status": "open", "exchange": "NYSE", "date": "2026-07-06", "name": "Reopen"},  # ignored
    ]
    with patch("services.market_calendar.shared_session", return_value=_mock_session(payload)):
        out = await mc.get_upcoming_holidays()
    assert len(out) == 1 and out[0]["name"] == "Independence Day"
    mc._cache["data"] = None


@pytest.mark.asyncio
async def test_holidays_non_200(monkeypatch):
    import services.market_calendar as mc

    mc._cache["data"] = None
    monkeypatch.setenv("POLYGON_API_KEY", "k")
    with patch("services.market_calendar.shared_session", return_value=_mock_session({}, status=500)):
        assert await mc.get_upcoming_holidays() == []
    mc._cache["data"] = None


# ── massive_ratios.get_ratios ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_ratios_no_key(monkeypatch):
    import services.massive_ratios as mr

    mr._cache.clear()
    monkeypatch.delenv("MASSIVE_API_KEY", raising=False)
    assert await mr.get_ratios("AAPL") == {}


@pytest.mark.asyncio
async def test_get_ratios_non_200(monkeypatch):
    import services.massive_ratios as mr

    mr._cache.clear()
    monkeypatch.setenv("MASSIVE_API_KEY", "k")
    with patch("services.massive_ratios.shared_session", return_value=_mock_session({}, status=500)):
        assert await mr.get_ratios("AAPL") == {}
    mr._cache.clear()


@pytest.mark.asyncio
async def test_get_ratios_computes_margins(monkeypatch):
    import services.massive_ratios as mr

    mr._cache.clear()
    monkeypatch.setenv("MASSIVE_API_KEY", "k")
    fin = {
        "income_statement": {
            "revenues": {"value": 1000.0},
            "gross_profit": {"value": 400.0},
            "income_loss_from_continuing_operations_after_tax": {"value": 100.0},
        },
        "balance_sheet": {
            "assets": {"value": 5000.0},
            "current_assets": {"value": 2000.0},
            "current_liabilities": {"value": 1000.0},
            "long_term_debt": {"value": 500.0},
        },
        "cash_flow_statement": {
            "net_cash_flow_from_operating_activities": {"value": 300.0},
            "net_cash_flow_from_investing_activities": {"value": -100.0},
        },
    }
    prev_fin = {"income_statement": {"revenues": {"value": 800.0}}}
    payload = {"results": [{"financials": fin}, {"financials": prev_fin}]}
    with patch("services.massive_ratios.shared_session", return_value=_mock_session(payload)):
        out = await mr.get_ratios("AAPL")
    assert out["gross_margin"] == 40.0
    assert out["net_margin"] == 10.0
    assert out["revenue_qoq"] == 25.0  # (1000-800)/800*100
    assert out["current_ratio"] == 2.0
    mr._cache.clear()


# ── fear_greed.get_fear_greed ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fear_greed_happy_path():
    import services.fear_greed as fg

    fg._cache["data"] = None
    payload = {
        "fear_and_greed": {
            "score": 25.0,
            "previous_close": 30.0,
            "previous_1_week": 40.0,
            "previous_1_month": 55.0,
        }
    }
    with (
        patch("services.fear_greed.cache_get", new=AsyncMock(return_value=None)),
        patch("services.fear_greed.cache_set", new=AsyncMock(return_value=None)),
        patch("services.fear_greed.aiohttp.ClientSession", return_value=_mock_session(payload)),
    ):
        result = await fg.get_fear_greed()
    assert result["score"] == 25.0
    assert isinstance(result["sentiment"], str) and result["label"]
    assert result["prev_1w"] == 40.0
    fg._cache["data"] = None


@pytest.mark.asyncio
async def test_fear_greed_non_200_returns_neutral():
    import services.fear_greed as fg

    fg._cache["data"] = None
    with (
        patch("services.fear_greed.cache_get", new=AsyncMock(return_value=None)),
        patch("services.fear_greed.aiohttp.ClientSession", return_value=_mock_session({}, status=503)),
    ):
        result = await fg.get_fear_greed()
    assert isinstance(result, dict) and "score" in result
    fg._cache["data"] = None
