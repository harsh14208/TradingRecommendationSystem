"""Extended tests for services/signal_engine.py — error branches and edge cases."""

from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pandas as pd
import pytest


# ── Helpers ──────────────────────────────────────────────────────────────────


def _make_df(rows: int = 30) -> pd.DataFrame:
    return pd.DataFrame({"Close": [100.0 + i * 0.1 for i in range(rows)]})


def _make_df_1h(rows: int = 20) -> pd.DataFrame:
    return pd.DataFrame({"Close": [100.0 + i * 0.05 for i in range(rows)]})


# Patch group used by most generate_signal tests
_GENERATE_SIGNAL_PATCHES = [
    ("services.signal_engine.get_company_news", AsyncMock),
    ("services.signal_engine.get_scraped_news", AsyncMock),
    ("services.signal_engine.get_insider_activity", AsyncMock),
    ("services.signal_engine.get_analyst_recs", AsyncMock),
    ("services.signal_engine.get_earnings_calendar", AsyncMock),
    ("services.signal_engine.get_earnings_surprise", AsyncMock),
    ("services.signal_engine.get_options_flow", AsyncMock),
    ("services.signal_engine.get_fundamentals", AsyncMock),
    ("services.signal_engine.get_social_sentiment", AsyncMock),
    ("services.signal_engine.get_google_trends", AsyncMock),
    ("services.signal_engine.get_congress_signal", AsyncMock),
    ("services.signal_engine.get_history", AsyncMock),
    ("services.signal_engine.get_info", AsyncMock),
    ("services.signal_engine.get_sector_relative_strength", AsyncMock),
    ("services.signal_engine.calculate_indicators", MagicMock),
]


def _setup_generate_signal_mocks(
    m_news,
    m_snews,
    m_insider,
    m_arecs,
    m_ecal,
    m_esurp,
    m_oflow,
    m_fund,
    m_soc,
    m_trends,
    m_cong,
    m_hist,
    m_info,
    m_sec,
    m_calc,
    *,
    df_daily=None,
    df_1h=None,
):
    """Wire default return values for all generate_signal dependencies."""
    m_news.return_value = []
    m_snews.return_value = []
    m_insider.return_value = {}
    m_arecs.return_value = {}
    m_ecal.return_value = {}
    m_esurp.return_value = {}
    m_oflow.return_value = {}
    m_fund.return_value = {}
    m_soc.return_value = {}
    m_trends.return_value = {}
    m_cong.return_value = {}
    m_hist.side_effect = [
        df_daily if df_daily is not None else _make_df(),
        df_1h if df_1h is not None else _make_df_1h(),
    ]
    m_info.return_value = {"company": "Test Co"}
    m_sec.return_value = {}
    m_calc.return_value = {
        "price": 100.0,
        "atr": 2.0,
        "rsi": 50.0,
        "macd_hist": 0.0,
        "macd_hist_prev": 0.0,
        "sma200": 95.0,
        "sma50": 98.0,
        "volume": 1_000_000,
        "avg_volume": 1_000_000,
    }


# ── _fetch_ticker_data ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fetch_ticker_data_prefetched_path():
    from services.signal_engine import _fetch_ticker_data

    df = _make_df(35)
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_extended_hours_data", new_callable=AsyncMock) as m_ext,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
    ):
        m_news.return_value = []
        m_snews.return_value = []
        m_insider.return_value = {}
        m_arecs.return_value = {}
        m_ecal.return_value = {}
        m_esurp.return_value = {}
        m_oflow.return_value = {}
        m_fund.return_value = {}
        m_soc.return_value = {}
        m_trends.return_value = {}
        m_cong.return_value = {}
        m_hist.return_value = _make_df_1h()
        m_ext.return_value = {}
        m_sec.return_value = {"rs_vs_sector": 2.0, "sector_etf": "XLK"}

        result = await _fetch_ticker_data("AAPL", df, {"company": "Apple"})

    assert result is not None
    assert result.df is df
    assert result.info == {"company": "Apple"}
    assert len(result.data_warnings) == 0
    m_hist.assert_awaited_once_with("AAPL", period="5d", interval="1h")


@pytest.mark.asyncio
async def test_fetch_ticker_data_non_prefetched_path():
    from services.signal_engine import _fetch_ticker_data

    df_daily = _make_df(35)
    df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_extended_hours_data", new_callable=AsyncMock) as m_ext,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
    ):
        m_news.return_value = []
        m_snews.return_value = []
        m_insider.return_value = {}
        m_arecs.return_value = {}
        m_ecal.return_value = {}
        m_esurp.return_value = {}
        m_oflow.return_value = {}
        m_fund.return_value = {}
        m_soc.return_value = {}
        m_trends.return_value = {}
        m_cong.return_value = {}
        m_hist.side_effect = [df_daily, df_1h]
        m_info.return_value = {"company": "Apple"}
        m_ext.return_value = {}
        m_sec.return_value = {}

        result = await _fetch_ticker_data("AAPL", None, None)

    assert result is not None
    assert result.df is df_daily
    assert result.info == {"company": "Apple"}
    assert m_hist.call_count == 2


@pytest.mark.asyncio
async def test_fetch_ticker_data_insufficient_history():
    from services.signal_engine import _fetch_ticker_data

    df = _make_df(10)  # less than 30 rows
    with (
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_extended_hours_data", new_callable=AsyncMock) as m_ext,
    ):
        m_hist.return_value = _make_df_1h()
        m_info.return_value = {}
        m_ext.return_value = {}

        result = await _fetch_ticker_data("AAPL", None, None)

    assert result is None


@pytest.mark.asyncio
async def test_fetch_ticker_data_leveraged_etf():
    from services.signal_engine import _fetch_ticker_data, _LEVERAGED_ETFS

    # Ensure TQQQ is in the leveraged list
    assert "TQQQ" in _LEVERAGED_ETFS

    df = _make_df(35)
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_extended_hours_data", new_callable=AsyncMock) as m_ext,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
    ):
        m_news.return_value = []
        m_snews.return_value = []
        m_insider.return_value = {"filings": 3}  # would be overridden by dummy
        m_arecs.return_value = {}
        m_ecal.return_value = {}
        m_esurp.return_value = {}
        m_oflow.return_value = {}
        m_fund.return_value = {}
        m_soc.return_value = {}
        m_trends.return_value = {}
        m_cong.return_value = {}
        m_hist.return_value = _make_df_1h()
        m_ext.return_value = {}
        m_sec.return_value = {}

        result = await _fetch_ticker_data("TQQQ", df, {})

    assert result is not None
    # Leveraged ETFs get empty dicts for fundamental-sensitive sources
    assert result.insider == {}
    assert result.analyst_recs == {}
    assert result.fundamentals == {}


@pytest.mark.asyncio
async def test_fetch_ticker_data_sector_rs_exception():
    from services.signal_engine import _fetch_ticker_data

    df = _make_df(35)
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_extended_hours_data", new_callable=AsyncMock) as m_ext,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
    ):
        m_news.return_value = []
        m_snews.return_value = []
        m_insider.return_value = {}
        m_arecs.return_value = {}
        m_ecal.return_value = {}
        m_esurp.return_value = {}
        m_oflow.return_value = {}
        m_fund.return_value = {}
        m_soc.return_value = {}
        m_trends.return_value = {}
        m_cong.return_value = {}
        m_hist.return_value = _make_df_1h()
        m_ext.return_value = {}
        m_sec.side_effect = RuntimeError("sector rs failed")

        result = await _fetch_ticker_data("AAPL", df, {})

    assert result is not None
    assert result.sector_rs is None
    assert any(w["source"] == "sector_relative_strength" for w in result.data_warnings)


@pytest.mark.asyncio
async def test_fetch_ticker_data_gather_exceptions():
    from services.signal_engine import _fetch_ticker_data

    df = _make_df(35)
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_extended_hours_data", new_callable=AsyncMock) as m_ext,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
    ):
        m_news.side_effect = RuntimeError("news down")
        m_snews.return_value = []
        m_insider.return_value = {}
        m_arecs.return_value = {}
        m_ecal.return_value = {}
        m_esurp.return_value = {}
        m_oflow.return_value = {}
        m_fund.return_value = {}
        m_soc.return_value = {}
        m_trends.return_value = {}
        m_cong.return_value = {}
        m_hist.return_value = _make_df_1h()
        m_ext.return_value = {}
        m_sec.return_value = {}

        result = await _fetch_ticker_data("AAPL", df, {})

    assert result is not None
    assert result.news is None
    assert any(w["source"] == "company_news" for w in result.data_warnings)


# ── generate_signal early exits ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_signal_fetch_returns_none():
    from services.signal_engine import generate_signal

    with patch("services.signal_engine._fetch_ticker_data", new_callable=AsyncMock) as m_fetch:
        m_fetch.return_value = None
        result = await generate_signal("AAPL")
    assert result is None


@pytest.mark.asyncio
async def test_generate_signal_tech_none():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        m_calc.return_value = None
        result = await generate_signal("AAPL")
    assert result is None


@pytest.mark.asyncio
async def test_generate_signal_tech_no_price():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        m_calc.return_value = {"rsi": 50.0}  # missing price key
        result = await generate_signal("AAPL")
    assert result is None


# ── generate_signal exception branches ───────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_signal_worker_import_fails():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
        patch("services.signal_engine.asyncio.ensure_future", side_effect=Exception("boom")),
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        result = await generate_signal("AAPL")
    assert result is not None
    assert result["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_generate_signal_polygon_indicators_exception():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
        patch("services.polygon_indicators.get_indicators", side_effect=RuntimeError("polygon down")),
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        result = await generate_signal("AAPL")
    assert result is not None


@pytest.mark.asyncio
async def test_generate_signal_weekly_trend_exception():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    # Use a RangeIndex so resample() raises
    mock_df.index = pd.RangeIndex(start=0, stop=len(mock_df))
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        result = await generate_signal("AAPL")
    assert result is not None


@pytest.mark.asyncio
async def test_generate_signal_polygon_weekly_bars_exception():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
        patch("services.polygon_client.get_polygon_weekly_bars", side_effect=RuntimeError("polygon weekly down")),
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        result = await generate_signal("AAPL")
    assert result is not None


@pytest.mark.asyncio
async def test_generate_signal_exdiv_lookup_exception():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
        patch("services.polygon_client.get_polygon_dividends", side_effect=RuntimeError("divs down")),
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        result = await generate_signal("AAPL")
    assert result is not None


@pytest.mark.asyncio
async def test_generate_signal_local_llm_exception():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
        patch("services.local_llm.get_llm_client", side_effect=RuntimeError("llm down")),
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        # Force earnings window so LLM path is reached
        m_ecal.return_value = {"days_to_earnings": 7}
        m_news.return_value = [{"headline": "earnings beat", "sentiment": 0.5, "hours_ago": 1, "source": "Finviz"}]
        result = await generate_signal("AAPL")
    assert result is not None


@pytest.mark.asyncio
async def test_generate_signal_1h_techs_exception():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
        patch("services.signal_engine.asyncio.to_thread", side_effect=RuntimeError("thread pool down")),
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        result = await generate_signal("AAPL")
    assert result is not None


@pytest.mark.asyncio
async def test_generate_signal_massive_ratios_exception():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
        patch("services.massive_ratios.get_ratios", side_effect=RuntimeError("ratios down")),
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        result = await generate_signal("AAPL")
    assert result is not None


@pytest.mark.asyncio
async def test_generate_signal_8k_events_exception():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
        patch("services.eightk_events.get_8k_signals", side_effect=RuntimeError("8k down")),
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        result = await generate_signal("AAPL")
    assert result is not None


@pytest.mark.asyncio
async def test_generate_signal_supply_chain_exception():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
        patch("services.supply_chain.get_supply_chain_score", side_effect=RuntimeError("sc down")),
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        result = await generate_signal("AAPL")
    assert result is not None


@pytest.mark.asyncio
async def test_generate_signal_corp_events_exception():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
        patch("services.corporate_events.get_event_score", side_effect=RuntimeError("ce down")),
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        result = await generate_signal("AAPL")
    assert result is not None


@pytest.mark.asyncio
async def test_generate_signal_etf_flows_exception():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
        patch("services.etf_flows.get_flow_score_for_ticker", side_effect=RuntimeError("etf flow down")),
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        result = await generate_signal("AAPL")
    assert result is not None


# ── Blackout / gate branches ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_signal_pre_earnings_blackout():
    from services.signal_engine import generate_signal

    mock_df = _make_df(35)
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        # Pre-earnings blackout: days_to_earnings=1 forces HOLD
        m_ecal.return_value = {"days_to_earnings": 1, "next_earnings_date": "2026-05-15"}
        result = await generate_signal("AAPL")
    assert result is not None
    assert result["action"] == "HOLD"
    assert any("Earnings Blackout" in r["head"] for r in result["rationale"])


@pytest.mark.asyncio
async def test_generate_signal_sector_downtrend_gate():
    from services.signal_engine import generate_signal

    # Use DatetimeIndex so weekly resample doesn't throw
    mock_df = pd.DataFrame(
        {"Close": [100.0 + i * 0.1 for i in range(35)]},
        index=pd.date_range("2026-01-01", periods=35, freq="D"),
    )
    mock_df_1h = _make_df_1h()
    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
    ):
        _setup_generate_signal_mocks(
            m_news,
            m_snews,
            m_insider,
            m_arecs,
            m_ecal,
            m_esurp,
            m_oflow,
            m_fund,
            m_soc,
            m_trends,
            m_cong,
            m_hist,
            m_info,
            m_sec,
            m_calc,
            df_daily=mock_df,
            df_1h=mock_df_1h,
        )
        # Mild bullish indicators → score > 0 but < 40 so gate fires
        m_calc.return_value = {
            "price": 100.0,
            "atr": 2.0,
            "rsi": 45.0,
            "volume": 1_000_000,
            "avg_volume": 1_000_000,
            "sma200": 95.0,
            "sma50": 98.0,
            "close_streak": 5,
            "gap_pct": 2.0,
        }
        m_sec.return_value = {"sector_etf": "XLK", "sector_1m_ret": -8.0, "rs_vs_sector": 2.0}
        result = await generate_signal("AAPL")
    assert result is not None
    assert result["action"] == "HOLD"
    assert any("Sector Downtrend Gate" in r["head"] for r in result["rationale"])


@pytest.mark.asyncio
async def test_generate_signal_unhandled_exception_returns_none():
    from services.signal_engine import generate_signal

    with patch("services.signal_engine._fetch_ticker_data", new_callable=AsyncMock) as m_fetch:
        m_fetch.side_effect = RuntimeError("unexpected crash")
        result = await generate_signal("AAPL")
    assert result is None


# ── scan_all ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_scan_all_with_tickers():
    from services.signal_engine import scan_all

    with patch("services.signal_engine.generate_signal", new_callable=AsyncMock) as m_gen:
        m_gen.side_effect = [
            {"ticker": "AAPL", "action": "BUY", "confidence": 60.0, "sectorEtf": "XLK", "rationale": [], "sources": []},
            {
                "ticker": "MSFT",
                "action": "HOLD",
                "confidence": 50.0,
                "sectorEtf": "XLK",
                "rationale": [],
                "sources": [],
            },
        ]
        results = await scan_all(["AAPL", "MSFT"])

    assert len(results) == 2
    assert results[0]["ticker"] == "AAPL"
    assert results[1]["ticker"] == "MSFT"


@pytest.mark.asyncio
async def test_scan_all_etf_histories_injected():
    from services.signal_engine import scan_all

    histories = {
        "XLK": pd.DataFrame({"Close": [100.0] * 70}),
        "AAPL": pd.DataFrame({"Close": [100.0] * 70}),
    }
    with patch("services.signal_engine.generate_signal", new_callable=AsyncMock) as m_gen:
        m_gen.return_value = {
            "ticker": "AAPL",
            "action": "BUY",
            "confidence": 60.0,
            "sectorEtf": "XLK",
            "rationale": [],
            "sources": [],
        }
        await scan_all(["AAPL"], market_ctx={}, histories=histories, infos={})

    # Verify market_ctx was augmented with etf_histories
    call_kwargs = m_gen.call_args.kwargs
    assert "market_ctx" in call_kwargs
    assert "etf_histories" in call_kwargs["market_ctx"]
    assert "XLK" in call_kwargs["market_ctx"]["etf_histories"]


@pytest.mark.asyncio
async def test_scan_all_sector_peer_confirmation():
    from services.signal_engine import scan_all

    with patch("services.signal_engine.generate_signal", new_callable=AsyncMock) as m_gen:
        m_gen.side_effect = [
            {"ticker": "AAPL", "action": "BUY", "confidence": 60.0, "sectorEtf": "XLK", "rationale": [], "sources": []},
            {
                "ticker": "MSFT",
                "action": "HOLD",
                "confidence": 50.0,
                "sectorEtf": "XLK",
                "rationale": [],
                "sources": [],
            },
            {
                "ticker": "GOOGL",
                "action": "HOLD",
                "confidence": 50.0,
                "sectorEtf": "XLK",
                "rationale": [],
                "sources": [],
            },
        ]
        results = await scan_all(["AAPL", "MSFT", "GOOGL"])

    aapl = next(r for r in results if r["ticker"] == "AAPL")
    # Lone BUY in sector with <2 bullish peers gets a confidence haircut
    assert aapl["confidence"] < 60.0
    assert any("Sector Peers Not Confirming" in r["head"] for r in aapl["rationale"])


@pytest.mark.asyncio
async def test_scan_all_filters_exceptions():
    from services.signal_engine import scan_all

    with patch("services.signal_engine.generate_signal", new_callable=AsyncMock) as m_gen:
        m_gen.side_effect = [
            RuntimeError("boom"),
            {"ticker": "MSFT", "action": "BUY", "confidence": 60.0, "sectorEtf": "XLK", "rationale": [], "sources": []},
        ]
        results = await scan_all(["AAPL", "MSFT"])

    assert len(results) == 1
    assert results[0]["ticker"] == "MSFT"


# ── _collect_fetch_results edge cases ────────────────────────────────────────

from services.signal_engine import _collect_fetch_results


def test_collect_fetch_results_all_success():
    values, warnings = _collect_fetch_results(
        "TICK",
        ["a", "b", "c"],
        [1, 2, 3],
    )
    assert values == [1, 2, 3]
    assert warnings == []


def test_collect_fetch_results_all_fail():
    values, warnings = _collect_fetch_results(
        "TICK",
        ["a", "b"],
        [RuntimeError("a err"), ValueError("b err")],
    )
    assert values == [None, None]
    assert len(warnings) == 2
    assert warnings[0]["error"] == "RuntimeError"
    assert warnings[1]["error"] == "ValueError"


def test_collect_fetch_results_mixed():
    values, warnings = _collect_fetch_results(
        "TICK",
        ["a", "b", "c"],
        [RuntimeError("a err"), {"ok": True}, ValueError("c err")],
    )
    assert values == [None, {"ok": True}, None]
    assert len(warnings) == 2
    assert warnings[0]["source"] == "a"
    assert warnings[1]["source"] == "c"


# ── _apply_q1_rebalancing edge cases ─────────────────────────────────────────

from services.signal_engine import _apply_q1_rebalancing


def test_q1_rebalancing_unknown_sector():
    with patch("services.signal_engine.datetime") as mock_dt:
        mock_dt.now.return_value = MagicMock(month=2)
        score, rationale = _apply_q1_rebalancing(50.0, [], "Unknown", 15.0)
    assert score == 50.0
    assert rationale == []


def test_q1_rebalancing_empty_sector():
    with patch("services.signal_engine.datetime") as mock_dt:
        mock_dt.now.return_value = MagicMock(month=2)
        score, rationale = _apply_q1_rebalancing(50.0, [], "", 15.0)
    assert score == 50.0
    assert rationale == []


# ── _compute_1h_techs edge cases ─────────────────────────────────────────────

from services.signal_engine import _compute_1h_techs


def test_compute_1h_techs_constant_prices():
    df = pd.DataFrame({"Close": [100.0] * 30})
    result = _compute_1h_techs(df)
    assert "rsi_1h" in result
    assert "macd_1h" in result
    assert "above_ema_1h" in result


def test_compute_1h_techs_with_nan():
    closes = [100.0] * 10 + [np.nan] * 5 + [100.0] * 15
    df = pd.DataFrame({"Close": closes})
    result = _compute_1h_techs(df)
    assert "rsi_1h" in result
    assert "macd_1h" in result
    assert "above_ema_1h" in result
