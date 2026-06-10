"""Unit tests for services/polygon_client.py — fetchers with a mocked pooled session.

Uses the shared_session() seam (patched per-function) to feed canned Polygon JSON,
exercising the parse paths, the no-API-key short-circuits, and the error branches.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

import services.polygon_client as pc


def _mock_session(payload, status=200):
    """Build an async-CM session whose .get(...) yields a response returning `payload`."""
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


def _patch(session):
    return (
        patch("services.polygon_client.shared_session", return_value=session),
        patch("services.polygon_client._get_api_key", return_value="fake_key"),
    )


@pytest.fixture(autouse=True)
def _clear_caches():
    pc._snapshot_cache.clear()
    pc._div_cache.clear()
    pc._weekly_cache.clear()
    pc._block_print_cache.clear()
    pc._ofi_cache.clear()
    yield
    # Clear again on teardown so module-level caches don't leak into other test files.
    pc._snapshot_cache.clear()
    pc._div_cache.clear()
    pc._weekly_cache.clear()
    pc._block_print_cache.clear()
    pc._ofi_cache.clear()


# ── _get_api_key ─────────────────────────────────────────────────────────────


def test_get_api_key_prefers_polygon(monkeypatch):
    monkeypatch.setenv("POLYGON_API_KEY", "poly")
    monkeypatch.setenv("MASSIVE_API_KEY", "massive")
    assert pc._get_api_key() == "poly"


def test_get_api_key_falls_back_to_massive(monkeypatch):
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    monkeypatch.setenv("MASSIVE_API_KEY", "massive")
    assert pc._get_api_key() == "massive"


def test_get_api_key_empty(monkeypatch):
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    monkeypatch.delenv("MASSIVE_API_KEY", raising=False)
    with patch("config.get_settings", return_value=MagicMock(polygon_api_key="", massive_api_key="")):
        assert pc._get_api_key() == ""


# ── get_polygon_history ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_history_no_key_returns_none():
    with patch("services.polygon_client._get_api_key", return_value=""):
        assert await pc.get_polygon_history("AAPL") is None


@pytest.mark.asyncio
async def test_history_happy_path_returns_dataframe():
    payload = {
        "results": [
            {"t": 1700000000000, "o": 10, "h": 11, "l": 9, "c": 10.5, "v": 1000},
            {"t": 1700086400000, "o": 10.5, "h": 12, "l": 10, "c": 11.5, "v": 2000},
        ]
    }
    session = _mock_session(payload)
    p1, p2 = _patch(session)
    with p1, p2:
        df = await pc.get_polygon_history("AAPL", period="1mo", interval="1d")
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert len(df) == 2
    assert df["Close"].iloc[-1] == 11.5


@pytest.mark.asyncio
async def test_history_empty_results_returns_empty_df():
    session = _mock_session({"results": []})
    p1, p2 = _patch(session)
    with p1, p2:
        df = await pc.get_polygon_history("AAPL")
    assert isinstance(df, pd.DataFrame) and df.empty


@pytest.mark.asyncio
async def test_history_non_200_returns_none():
    session = _mock_session({}, status=403)
    p1, p2 = _patch(session)
    with p1, p2:
        assert await pc.get_polygon_history("AAPL") is None


@pytest.mark.asyncio
@pytest.mark.parametrize("interval", ["1d", "1h", "5m", "weird"])
async def test_history_interval_mapping(interval):
    session = _mock_session({"results": [{"t": 1700000000000, "o": 1, "h": 1, "l": 1, "c": 1, "v": 1}]})
    p1, p2 = _patch(session)
    with p1, p2:
        df = await pc.get_polygon_history("AAPL", interval=interval)
    assert df is not None and len(df) == 1


# ── get_polygon_snapshot_batch / quotes_batch ────────────────────────────────


@pytest.mark.asyncio
async def test_snapshot_batch_no_key_or_empty():
    with patch("services.polygon_client._get_api_key", return_value=""):
        assert await pc.get_polygon_snapshot_batch(["AAPL"]) == {}
    p1, p2 = _patch(_mock_session({}))
    with p1, p2:
        assert await pc.get_polygon_snapshot_batch([]) == {}


@pytest.mark.asyncio
async def test_snapshot_batch_parses_and_caches():
    payload = {"tickers": [{"ticker": "AAPL", "lastTrade": {"p": 150}, "prevDay": {"c": 148}}]}
    p1, p2 = _patch(_mock_session(payload))
    with p1, p2:
        out = await pc.get_polygon_snapshot_batch(["AAPL"])
    assert "AAPL" in out
    assert "AAPL" in pc._snapshot_cache  # cached for extended-hours reuse


@pytest.mark.asyncio
async def test_snapshot_batch_non_200_returns_empty():
    p1, p2 = _patch(_mock_session({}, status=500))
    with p1, p2:
        assert await pc.get_polygon_snapshot_batch(["AAPL"]) == {}


@pytest.mark.asyncio
async def test_quotes_batch_builds_rows():
    payload = {
        "tickers": [
            {"ticker": "AAPL", "lastTrade": {"p": 150.0}, "prevDay": {"c": 148.0}},
            {"ticker": "ZERO", "lastTrade": {"p": 0}, "prevDay": {"c": 0}},  # skipped
        ]
    }
    p1, p2 = _patch(_mock_session(payload))
    with p1, p2:
        quotes = await pc.get_polygon_quotes_batch(["AAPL", "ZERO"])
    assert len(quotes) == 1
    row = quotes[0]
    assert row["t"] == "AAPL" and row["p"] == 150.0
    assert row["c"] == pytest.approx(1.35, abs=0.01)


# ── get_polygon_info / infos_batch ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_info_happy_and_empty():
    payload = {"results": {"name": "Apple Inc", "market_cap": 3e12, "homepage_url": "x"}}
    p1, p2 = _patch(_mock_session(payload))
    with p1, p2:
        info = await pc.get_polygon_info("AAPL")
    assert info["company"] == "Apple Inc" and info["market_cap"] == 3e12

    p1, p2 = _patch(_mock_session({"results": {}}))
    with p1, p2:
        assert await pc.get_polygon_info("AAPL") is None


@pytest.mark.asyncio
async def test_info_no_key_and_non_200():
    with patch("services.polygon_client._get_api_key", return_value=""):
        assert await pc.get_polygon_info("AAPL") is None
    p1, p2 = _patch(_mock_session({}, status=404))
    with p1, p2:
        assert await pc.get_polygon_info("AAPL") is None


@pytest.mark.asyncio
async def test_infos_batch():
    payload = {"results": {"name": "Apple", "market_cap": 1}}
    p1, p2 = _patch(_mock_session(payload))
    with p1, p2:
        out = await pc.get_polygon_infos_batch(["AAPL", "MSFT"])
    assert set(out.keys()) == {"AAPL", "MSFT"}
    with patch("services.polygon_client._get_api_key", return_value=""):
        assert await pc.get_polygon_infos_batch(["AAPL"]) == {}


# ── get_polygon_weekly_bars ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_weekly_bars_parse_and_cache():
    payload = {
        "results": [
            {"t": 1700000000000, "o": 1, "h": 2, "l": 1, "c": 1.5, "v": 10},
            {"t": 1700604800000, "o": 1.5, "h": 3, "l": 1, "c": 2.5, "v": 20},
        ]
    }
    p1, p2 = _patch(_mock_session(payload))
    with p1, p2:
        df = await pc.get_polygon_weekly_bars("AAPL", weeks=5)
    assert list(df.columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert "AAPL" in pc._weekly_cache
    # Second call hits cache (no session needed)
    with patch("services.polygon_client._get_api_key", return_value="fake_key"):
        df2 = await pc.get_polygon_weekly_bars("AAPL", weeks=5)
    assert len(df2) == len(df)


@pytest.mark.asyncio
async def test_weekly_bars_no_key_and_empty():
    with patch("services.polygon_client._get_api_key", return_value=""):
        assert await pc.get_polygon_weekly_bars("AAPL") is None
    p1, p2 = _patch(_mock_session({"results": []}))
    with p1, p2:
        df = await pc.get_polygon_weekly_bars("ZZZ")
    assert df is not None and df.empty


# ── histories_batch ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_histories_batch_empty_and_nokey():
    with patch("services.polygon_client._get_api_key", return_value=""):
        assert await pc.get_polygon_histories_batch(["AAPL"]) == {}
    with patch("services.polygon_client._get_api_key", return_value="k"):
        assert await pc.get_polygon_histories_batch([]) == {}


@pytest.mark.asyncio
async def test_histories_batch_collects_results():
    df = pd.DataFrame({"Open": [1, 2], "High": [1, 2], "Low": [1, 2], "Close": [1, 2], "Volume": [1, 2]})
    with (
        patch("services.polygon_client._get_api_key", return_value="k"),
        patch("services.polygon_client.get_polygon_history", new=AsyncMock(return_value=df)),
    ):
        out = await pc.get_polygon_histories_batch(["AAPL", "MSFT"], concurrency=2)
    assert set(out.keys()) == {"AAPL", "MSFT"}


# ── extended hours (cache reuse) ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_extended_hours_uses_snapshot_cache():
    import time as _t

    pc._snapshot_cache["EXTHRS"] = (
        {"lastTrade": {"p": 152.0}, "prevDay": {"c": 150.0}, "min": {"v": 9000}},
        _t.monotonic(),
    )
    with patch("services.polygon_client._get_api_key", return_value="fake_key"):
        result = await pc.get_polygon_extended_hours("EXTHRS")
    assert result["direction"] == "up"
    assert result["ext_volume"] == 9000


# ── get_polygon_dividends ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_dividends_no_key_returns_empty():
    with patch("services.polygon_client._get_api_key", return_value=""):
        assert await pc.get_polygon_dividends("AAPL") == []


@pytest.mark.asyncio
async def test_dividends_sorted_ascending_and_cached():
    payload = {
        "results": [
            {"ex_dividend_date": "2026-09-01", "cash_amount": 0.25, "pay_date": "2026-09-15", "frequency": 4},
            {"ex_dividend_date": "2026-06-01", "cash_amount": 0.24, "pay_date": "2026-06-15", "frequency": 4},
            {"ex_dividend_date": None, "cash_amount": 0.0},  # dropped
        ]
    }
    p1, p2 = _patch(_mock_session(payload))
    with p1, p2:
        divs = await pc.get_polygon_dividends("AAPL")
    assert [d["ex_dividend_date"] for d in divs] == ["2026-06-01", "2026-09-01"]
    assert "AAPL" in pc._div_cache


@pytest.mark.asyncio
async def test_dividends_non_200_returns_empty():
    p1, p2 = _patch(_mock_session({}, status=500))
    with p1, p2:
        assert await pc.get_polygon_dividends("AAPL") == []


# ── get_recent_block_prints ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_block_prints_no_key_or_no_snapshot():
    with patch("services.polygon_client._get_api_key", return_value=""):
        assert await pc.get_recent_block_prints("AAPL") == {}
    # key present but no snapshot context → {}
    with patch("services.polygon_client._get_api_key", return_value="k"):
        assert await pc.get_recent_block_prints("NOSNAP") == {}


@pytest.mark.asyncio
async def test_block_prints_classifies_buys_and_sells():
    import time as _t

    pc._snapshot_cache["BLK"] = (
        {"day": {"l": 100.0, "h": 110.0}, "lastTrade": {"p": 105.0}},
        _t.monotonic(),
    )
    payload = {
        "results": [
            {"size": 10000, "price": 100.5},  # near low → accumulation
            {"size": 8000, "price": 109.8},  # near high → distribution
            {"size": 100, "price": 100.5},  # below min_block_size → ignored
            {"size": 9000, "price": 105.0},  # mid-range → neither
        ]
    }
    p1, p2 = _patch(_mock_session(payload))
    with p1, p2:
        res = await pc.get_recent_block_prints("BLK", min_block_size=5000)
    assert res["block_buys"] == 1 and res["block_buy_volume"] == 10000
    assert res["block_sells"] == 1 and res["block_sell_volume"] == 8000


# ── get_ofi_signals ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ofi_no_key_and_insufficient_bars():
    with patch("services.polygon_client._get_api_key", return_value=""):
        assert await pc.get_ofi_signals("AAPL") == {}
    p1, p2 = _patch(_mock_session({"results": [{"c": 1, "v": 1}]}))  # <10 bars
    with p1, p2:
        assert await pc.get_ofi_signals("AAPL") == {}


@pytest.mark.asyncio
async def test_ofi_happy_path():
    bars = [{"c": 100 + i, "v": 1000} for i in range(20)]  # steadily rising → buyer-initiated
    p1, p2 = _patch(_mock_session({"results": bars}))
    with p1, p2:
        res = await pc.get_ofi_signals("AAPL")
    assert "ofi_1d" in res and res["ofi_1d"] > 0  # net buying
    assert "AAPL" in pc._ofi_cache
