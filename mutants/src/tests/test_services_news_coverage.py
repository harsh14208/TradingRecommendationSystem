"""Coverage tests for services/news.py."""

from collections import deque
from unittest.mock import MagicMock, patch

import pytest


# ── score_sentiment ────────────────────────────────────────────────────────


def test_score_sentiment_neutral():
    from services.news import score_sentiment

    assert score_sentiment("nothing special here") == 0.0


def test_score_sentiment_positive():
    from services.news import score_sentiment

    assert score_sentiment("strong growth and record profits") > 0


def test_score_sentiment_negative():
    from services.news import score_sentiment

    assert score_sentiment("misses expectations and decline in revenue") < 0


def test_score_sentiment_mixed():
    from services.news import score_sentiment

    # 2 positive words (strong, growth) + 2 negative words (decline, loss) = 4 total
    # (2 - 2) / 4 = 0.0
    assert score_sentiment("strong growth but decline loss") == 0.0


# ── get_api_usage ──────────────────────────────────────────────────────────


def test_get_api_usage_empty():
    from services.news import get_api_usage, _call_times

    _call_times.clear()
    usage = get_api_usage()
    assert usage["used_last_60s"] == 0
    assert usage["limit"] == 60
    assert usage["pct"] == 0


def test_get_api_usage_with_calls():
    from services.news import get_api_usage, _call_times
    import time

    _call_times.clear()
    now = time.time()
    _call_times.extend([now, now - 10, now - 70])
    usage = get_api_usage()
    assert usage["used_last_60s"] == 2
    assert usage["pct"] == pytest.approx(3.33, 0.1)


# ── _fetch_news ────────────────────────────────────────────────────────────


def test_fetch_news_cached():
    from services.news import _fetch_news

    with patch.dict("services.news._cache", {"AAPL": ([{"headline": "cached"}], 9999999999)}, clear=False):
        result = _fetch_news("AAPL", 7)
        assert result == [{"headline": "cached"}]


def test_fetch_news_no_api_key():
    from services.news import _fetch_news

    with patch("services.news._cache", {}):
        with patch("config.get_settings") as mock_settings:
            mock_settings.return_value.finnhub_api_key = None
            result = _fetch_news("AAPL", 7)
            assert result == []


@patch("services.news._track_call")
def test_fetch_news_success(mock_track):
    from services.news import _fetch_news

    mock_news = [{"headline": "h1"}, {"headline": "h2"}]
    mock_client = MagicMock()
    mock_client.company_news.return_value = mock_news

    with patch("services.news._cache", {}):
        with patch("config.get_settings") as mock_settings:
            mock_settings.return_value.finnhub_api_key = "test_key"
            with patch("finnhub.Client", return_value=mock_client):
                result = _fetch_news("AAPL", 7)
                assert len(result) == 2
                assert result[0]["headline"] == "h1"
                mock_track.assert_called()


@patch("services.news._track_call")
def test_fetch_news_exception(mock_track):
    from services.news import _fetch_news

    with patch("services.news._cache", {}):
        with patch("config.get_settings") as mock_settings:
            mock_settings.return_value.finnhub_api_key = "test_key"
            with patch("finnhub.Client", side_effect=Exception("api down")):
                result = _fetch_news("AAPL", 7)
                assert result == []


# ── _fetch_analyst_recs ────────────────────────────────────────────────────


def test_fetch_analyst_recs_cached():
    from services.news import _fetch_analyst_recs

    with patch.dict("services.news._rec_cache", {"AAPL": ({"buy": 5}, 9999999999)}, clear=False):
        result = _fetch_analyst_recs("AAPL")
        assert result == {"buy": 5}


def test_fetch_analyst_recs_no_api_key():
    from services.news import _fetch_analyst_recs

    with patch("services.news._rec_cache", {}):
        with patch("config.get_settings") as mock_settings:
            mock_settings.return_value.finnhub_api_key = None
            result = _fetch_analyst_recs("AAPL")
            assert result == {}


@patch("services.news._track_call")
def test_fetch_analyst_recs_success(mock_track):
    from services.news import _fetch_analyst_recs

    mock_client = MagicMock()
    mock_client.recommendation_trends.return_value = [
        {"period": "2026-01", "strongBuy": 5, "buy": 3, "hold": 2, "sell": 1, "strongSell": 0},
        {"period": "2025-12", "strongBuy": 3, "buy": 3, "hold": 3, "sell": 1, "strongSell": 0},
    ]
    mock_client.company_basic_financials.return_value = {
        "metric": {"13WeekPriceReturnDaily": 5.0, "26WeekPriceReturnDaily": 10.0, "52WeekHigh": 200.0, "52WeekLow": 100.0}
    }

    with patch("services.news._rec_cache", {}):
        with patch("config.get_settings") as mock_settings:
            mock_settings.return_value.finnhub_api_key = "test_key"
            with patch("finnhub.Client", return_value=mock_client):
                result = _fetch_analyst_recs("AAPL")
                assert result["period"] == "2026-01"
                assert result["strong_buy"] == 5
                assert result["revision_pts"] == 4  # (5*2+3) - (3*2+3) = 13-9 = 4
                assert result["momentum_factor"] == pytest.approx(8.33, 0.01)
                assert result["fh_52w_high"] == 200.0
                assert result["fh_52w_low"] == 100.0


@patch("services.news._track_call")
def test_fetch_analyst_recs_empty_raw(mock_track):
    from services.news import _fetch_analyst_recs

    mock_client = MagicMock()
    mock_client.recommendation_trends.return_value = []

    with patch("services.news._rec_cache", {}):
        with patch("config.get_settings") as mock_settings:
            mock_settings.return_value.finnhub_api_key = "test_key"
            with patch("finnhub.Client", return_value=mock_client):
                result = _fetch_analyst_recs("AAPL")
                assert result == {}


@patch("services.news._track_call")
def test_fetch_analyst_recs_exception(mock_track):
    from services.news import _fetch_analyst_recs

    with patch("services.news._rec_cache", {}):
        with patch("config.get_settings") as mock_settings:
            mock_settings.return_value.finnhub_api_key = "test_key"
            with patch("finnhub.Client", side_effect=Exception("api down")):
                result = _fetch_analyst_recs("AAPL")
                assert result == {}


# ── async wrappers ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_company_news_redis_cache():
    from services.news import get_company_news

    with patch("services.news.cache_get", return_value=[{"headline": "redis"}]) as mock_get:
        result = await get_company_news("AAPL", 7)
        assert result == [{"headline": "redis"}]
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_get_company_news_with_items():
    from services.news import get_company_news

    mock_item = {
        "headline": "Test Headline",
        "summary": "Test summary content",
        "datetime": 1700000000,
        "source": "Finnhub",
        "url": "http://example.com",
    }

    with patch("services.news.cache_get", return_value=None):
        with patch("services.news._fetch_news", return_value=[mock_item]):
            with patch("services.news.cache_set") as mock_cache_set:
                result = await get_company_news("AAPL", 7)
                assert len(result) == 1
                assert result[0]["headline"] == "Test Headline"
                assert result[0]["sentiment"] == pytest.approx(0.0, 0.01)
                mock_cache_set.assert_called_once()


@pytest.mark.asyncio
async def test_get_company_news_empty():
    from services.news import get_company_news

    with patch("services.news.cache_get", return_value=None):
        with patch("services.news._fetch_news", return_value=[]):
            result = await get_company_news("AAPL", 7)
            assert result == []


@pytest.mark.asyncio
async def test_get_analyst_recs_redis_cache():
    from services.news import get_analyst_recs

    with patch("services.news.cache_get", return_value={"buy": 5}) as mock_get:
        result = await get_analyst_recs("AAPL")
        assert result == {"buy": 5}
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_get_analyst_recs_from_fetch():
    from services.news import get_analyst_recs

    with patch("services.news.cache_get", return_value=None):
        with patch("services.news._fetch_analyst_recs", return_value={"strong_buy": 3}) as mock_fetch:
            with patch("services.news.cache_set") as mock_cache_set:
                result = await get_analyst_recs("AAPL")
                assert result == {"strong_buy": 3}
                mock_fetch.assert_called_once_with("AAPL")
                mock_cache_set.assert_called_once()


@pytest.mark.asyncio
async def test_get_analyst_recs_empty():
    from services.news import get_analyst_recs

    with patch("services.news.cache_get", return_value=None):
        with patch("services.news._fetch_analyst_recs", return_value={}):
            result = await get_analyst_recs("AAPL")
            assert result == {}
