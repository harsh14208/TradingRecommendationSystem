"""Coverage-focused unit tests for pure helpers and mockable fetchers across
several data services (news, polygon_indicators, massive_ratios, market_calendar,
etf_flows, etf_constituents)."""

import datetime as _dt
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


# ── news.score_sentiment (pure) ──────────────────────────────────────────────


def test_score_sentiment_neutral_and_polarised():
    from services.news import score_sentiment

    assert score_sentiment("the the the") == 0.0  # no sentiment words
    pos = score_sentiment("strong beat surge upgrade growth rally")
    neg = score_sentiment("weak miss plunge downgrade loss crash")
    assert pos > 0
    assert neg < 0
    assert -1.0 <= neg <= pos <= 1.0


def test_get_api_usage_returns_dict():
    from services.news import get_api_usage

    usage = get_api_usage()
    assert isinstance(usage, dict)


# ── polygon_indicators pure helpers ──────────────────────────────────────────


def test_blend_rsi_variants():
    from services.polygon_indicators import blend_rsi

    assert blend_rsi(None, None) is None
    assert blend_rsi(50.0, None) == 50.0
    assert blend_rsi(None, 30.0) == 30.0
    # 60% polygon / 40% pandas
    assert blend_rsi(40.0, 60.0) == pytest.approx(0.6 * 60 + 0.4 * 40, abs=0.01)


def test_polygon_sma_crossover():
    from services.polygon_indicators import polygon_sma_crossover

    assert polygon_sma_crossover({}, 100.0) == {}
    out = polygon_sma_crossover({"sma200": 90.0, "sma50": 95.0, "sma20": 99.0}, 100.0)
    assert out["above_200"] is True
    assert out["above_50"] is True
    assert out["golden_cross_setup"] is True  # sma50 > sma200*0.99
    assert out["pct_from_200"] == pytest.approx((100 - 90) / 90 * 100, abs=0.01)


# ── massive_ratios.merge_with_yfinance (pure) ────────────────────────────────


def test_merge_with_yfinance_priority():
    from services.massive_ratios import merge_with_yfinance

    yf = {"pe": 20.0, "pb": 3.0, "roe": None}
    massive = {"pe": 18.0, "roe": 0.25, "ev_ebitda": None}
    merged = merge_with_yfinance(yf, massive)
    assert merged["pe"] == 18.0  # massive overrides
    assert merged["pb"] == 3.0  # yfinance retained
    assert merged["roe"] == 0.25  # massive fills gap
    assert "ev_ebitda" not in merged  # None not merged


# ── market_calendar.is_pre_long_weekend (pure, datetime-patched) ─────────────


def test_is_pre_long_weekend_false_paths():
    from services.market_calendar import is_pre_long_weekend

    assert is_pre_long_weekend([]) == (False, "")
    # malformed date is skipped; far-future holiday ignored
    assert is_pre_long_weekend([{"date": "not-a-date", "name": "X"}]) == (False, "")
    assert is_pre_long_weekend([{"date": "2099-01-01", "name": "NewYear"}]) == (False, "")


def test_is_pre_long_weekend_true():
    import services.market_calendar as mc

    # Freeze "today" to Wed 2026-06-03; holiday Fri 2026-06-05 (2 days out, weekday=4)
    with patch.object(mc, "datetime", wraps=_dt.datetime) as mdt:
        mdt.now.return_value = _dt.datetime(2026, 6, 3, tzinfo=_dt.timezone.utc)
        flag, name = mc.is_pre_long_weekend([{"date": "2026-06-05", "name": "Juneteenth-ish"}])
    assert flag is True and name == "Juneteenth-ish"


# ── etf_flows.get_flow_score_for_ticker (pure) ───────────────────────────────


def test_get_flow_score_for_ticker():
    from services.etf_flows import get_flow_score_for_ticker

    assert get_flow_score_for_ticker("AAPL", None) == (0.0, "")
    # Unknown ticker → no sector ETF mapping
    assert get_flow_score_for_ticker("ZZZZ", {"XLK": {"flow_5d_m": 600}}) == (0.0, "")

    with patch.dict("services.sector.SECTOR_MAP", {"AAPL": "XLK"}, clear=False):
        # Below $100M threshold → 0
        assert get_flow_score_for_ticker("AAPL", {"XLK": {"flow_5d_m": 50}}) == (0.0, "")
        pts, reason = get_flow_score_for_ticker("AAPL", {"XLK": {"flow_5d_m": 600}})
        assert pts > 0 and "inflows" in reason
        pts_neg, reason_neg = get_flow_score_for_ticker("AAPL", {"XLK": {"flow_5d_m": -600}})
        assert pts_neg < 0 and "outflows" in reason_neg


# ── etf_constituents weight / amplifier (pure, cache-backed) ─────────────────


def test_constituent_weight_and_amplifier():
    import services.etf_constituents as ec

    ec._cache["XLK"] = {
        "data": [{"ticker": f"T{i}", "weight": round(0.3 - i * 0.01, 3)} for i in range(40)],
        "ts": 0,
    }
    try:
        assert ec.get_constituent_weight("T0", "XLK") == 0.3
        assert ec.get_constituent_weight("NOPE", "XLK") == 0.0
        assert ec.get_flow_amplifier("T0", "XLK") == 1.5  # rank 1 → top 3
        assert ec.get_flow_amplifier("T5", "XLK") == 1.0  # rank 6 → 4-10
        assert ec.get_flow_amplifier("T20", "XLK") == 0.5  # rank 21 → 11-30
        assert ec.get_flow_amplifier("T35", "XLK") == 0.0  # rank 36 → >30
        assert ec.get_flow_amplifier("NOPE", "XLK") == 0.0
    finally:
        ec._cache.pop("XLK", None)


# ── polygon_indicators async fetchers (mocked session) ───────────────────────


@pytest.mark.asyncio
async def test_get_indicators_no_key():
    import services.polygon_indicators as pi

    pi._cache.clear()
    with patch("services.polygon_indicators._get_key", return_value=""):
        assert await pi.get_indicators("AAPL") == {}


@pytest.mark.asyncio
async def test_get_indicators_parses_values():
    import services.polygon_indicators as pi

    pi._cache.clear()
    payload = {"results": {"values": [{"value": 55.0, "signal": 1.0, "histogram": 0.5}]}}
    with (
        patch("services.polygon_indicators._get_key", return_value="k"),
        patch("services.polygon_indicators.shared_session", return_value=_mock_session(payload)),
    ):
        out = await pi.get_indicators("AAPL")
    assert out.get("rsi") == 55.0
    assert out.get("sma20") == 55.0
    assert "AAPL" in pi._cache
    pi._cache.clear()


@pytest.mark.asyncio
async def test_get_indicators_cache_hit():
    import services.polygon_indicators as pi
    import time as _t

    pi._cache["CACHED"] = {"data": {"rsi": 42.0}, "ts": _t.time()}
    with patch("services.polygon_indicators._get_key", return_value="k"):
        out = await pi.get_indicators("CACHED")
    assert out == {"rsi": 42.0}
    pi._cache.clear()


@pytest.mark.asyncio
async def test_get_weekly_indicators_no_key():
    import services.polygon_indicators as pi

    pi._weekly_cache.clear()
    with patch("services.polygon_indicators._get_key", return_value=""):
        assert await pi.get_weekly_indicators("AAPL") == {}
