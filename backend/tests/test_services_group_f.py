"""
backend/tests/test_services_group_f.py

Targeted coverage for uncovered public functions in:
- services/alpha_sleeves.py
- services/calibration.py
- services/institutional.py
"""

import asyncio
import json
import math
import sys
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import numpy as np
import pandas as pd
import pytest

# Ensure backend is on path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers / mocks
# ─────────────────────────────────────────────────────────────────────────────


class _MockSeries:
    def __init__(self, values):
        self._values = np.array(values, dtype=float)

    def astype(self, dtype):
        return self

    @property
    def values(self):
        return self._values

    def __len__(self):
        return len(self._values)


class _MockDF:
    def __init__(self, close_values):
        self._close = _MockSeries(close_values)

    def __getitem__(self, key):
        if key == "Close":
            return self._close
        raise KeyError(key)

    def __len__(self):
        return len(self._close)


def _make_price_series(length, start=100.0, drift=0.1):
    return [start + i * drift for i in range(length)]


class _MockRow:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


# ─────────────────────────────────────────────────────────────────────────────
# services/alpha_sleeves.py
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_compute_etf_residual_stat_arb_empty_tickers():
    from services.alpha_sleeves import compute_etf_residual_stat_arb
    result = await compute_etf_residual_stat_arb([], {})
    assert result == {}


@pytest.mark.asyncio
async def test_compute_etf_residual_stat_arb_missing_etf():
    from services.alpha_sleeves import compute_etf_residual_stat_arb
    with patch("services.alpha_sleeves.get_histories_batch", new=AsyncMock(return_value={})):
        result = await compute_etf_residual_stat_arb(["AAPL"], {"AAPL": "XLK"})
        assert result == {}


@pytest.mark.asyncio
async def test_compute_etf_residual_stat_arb_short_history():
    from services.alpha_sleeves import compute_etf_residual_stat_arb
    histories = {"AAPL": _MockDF([100.0] * 10), "XLK": _MockDF([100.0] * 10)}
    with patch("services.alpha_sleeves.get_histories_batch", new=AsyncMock(return_value=histories)):
        result = await compute_etf_residual_stat_arb(["AAPL"], {"AAPL": "XLK"}, lookback_days=60)
        assert result == {}


@pytest.mark.asyncio
async def test_compute_etf_residual_stat_arb_actions():
    from services.alpha_sleeves import compute_etf_residual_stat_arb

    # Build 61 closes so we get 60 returns
    base = 100.0
    closes = [base + i * 0.01 for i in range(61)]

    # Helper to inject a spike at the end of returns
    def make_hist(spike):
        s_closes = closes.copy()
        s_closes[-1] += spike
        return {"AAPL": _MockDF(s_closes), "XLK": _MockDF(closes)}

    # Patch lstsq so OLS => alpha=0,beta=0 and OU => a_param=0.9 (half-life ~6.6)
    def mock_lstsq(A, b, rcond=None):
        # Distinguish by checking whether second column looks like returns or lagged residuals
        # For our test data, the OU call operates on the residuals which are the same as b here.
        # We'll count calls per module invocation via a closure counter in the patch.
        return np.array([0.0, 0.0]), np.zeros(len(b)), None, None

    def mock_lstsq_ou(A, b, rcond=None):
        return np.array([0.0, 0.9]), np.zeros(len(b)), None, None

    with patch("services.alpha_sleeves.np.linalg.lstsq", side_effect=mock_lstsq):
        # HOLD: small spike → z not extreme
        histories = make_hist(0.001)
        result = await compute_etf_residual_stat_arb(["AAPL"], {"AAPL": "XLK"})
        assert result.get("AAPL", {}).get("action") == "HOLD"

    # For BUY/SELL we need |z| > 2 and half_life < 25.
    # Since alpha=0,beta=0, residual = ret_s.  With mostly flat returns and a big spike,
    # z will be huge.  But half-life fallback is 99 because a_param comes from second lstsq.
    # We'll patch lstsq to alternate: first call OLS, second call OU with a=0.9.
    call_count = 0

    def alt_lstsq(A, b, rcond=None):
        nonlocal call_count
        call_count += 1
        if call_count % 2 == 1:
            return np.array([0.0, 0.0]), np.zeros(len(b)), None, None
        return np.array([0.0, 0.9]), np.zeros(len(b)), None, None

    with patch("services.alpha_sleeves.np.linalg.lstsq", side_effect=alt_lstsq):
        # SELL: big positive spike
        histories = make_hist(5.0)
        with patch("services.alpha_sleeves.get_histories_batch", new=AsyncMock(return_value=histories)):
            result = await compute_etf_residual_stat_arb(["AAPL"], {"AAPL": "XLK"})
            assert result["AAPL"]["action"] == "SELL"
            assert result["AAPL"]["z_score"] > 2.0

        # BUY: big negative spike
        histories = make_hist(-5.0)
        with patch("services.alpha_sleeves.get_histories_batch", new=AsyncMock(return_value=histories)):
            result = await compute_etf_residual_stat_arb(["AAPL"], {"AAPL": "XLK"})
            assert result["AAPL"]["action"] == "BUY"
            assert result["AAPL"]["z_score"] < -2.0


@pytest.mark.asyncio
async def test_compute_etf_residual_stat_arb_exception():
    from services.alpha_sleeves import compute_etf_residual_stat_arb
    with patch("services.alpha_sleeves.get_histories_batch", side_effect=Exception("network")):
        result = await compute_etf_residual_stat_arb(["AAPL"], {"AAPL": "XLK"})
        assert result == {}


@pytest.mark.asyncio
async def test_compute_time_series_momentum_exception():
    from services.alpha_sleeves import compute_time_series_momentum
    with patch("services.alpha_sleeves.get_histories_batch", side_effect=Exception("network")):
        result = await compute_time_series_momentum()
        assert result == {}


@pytest.mark.asyncio
async def test_compute_cross_sectional_factor_scores_empty():
    from services.alpha_sleeves import compute_cross_sectional_factor_scores
    result = await compute_cross_sectional_factor_scores([])
    assert result == {}


@pytest.mark.asyncio
async def test_compute_cross_sectional_factor_scores_missing_data():
    from services.alpha_sleeves import compute_cross_sectional_factor_scores
    histories = {"AAPL": _MockDF(_make_price_series(250)), "MSFT": _MockDF(_make_price_series(50))}
    with patch("services.alpha_sleeves.get_histories_batch", new=AsyncMock(return_value=histories)):
        result = await compute_cross_sectional_factor_scores(["AAPL", "MSFT"])
        # MSFT has <120 days so skipped; only AAPL should appear
        assert "AAPL" in result
        assert "MSFT" not in result


@pytest.mark.asyncio
async def test_compute_cross_sectional_factor_scores_exception():
    from services.alpha_sleeves import compute_cross_sectional_factor_scores
    with patch("services.alpha_sleeves.get_histories_batch", side_effect=Exception("network")):
        result = await compute_cross_sectional_factor_scores(["AAPL"])
        assert result == {}


@pytest.mark.asyncio
async def test_get_dynamic_sleeve_sharpes():
    from services.alpha_sleeves import get_dynamic_sleeve_sharpes

    # Mock DB result for MR Sharpe
    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.all.return_value = [(1.5,), (-0.5,), (0.8,)]
    mock_db.execute.return_value = mock_res

    # Build histories for all tickers used by Trend / StatArb / Factor
    from services.alpha_sleeves import TREND_ETFS
    histories = {}
    for etf in TREND_ETFS:
        histories[etf] = _MockDF(_make_price_series(250, drift=0.2))
    for t in ["AAPL", "MSFT", "XLK", "NVDA", "AMZN", "GOOG"]:
        histories[t] = _MockDF(_make_price_series(250, drift=0.2))

    # Patch datetime.utcnow so cutoff is deterministic
    fixed_now = datetime(2026, 6, 1, 12, 0, 0)

    with patch("services.alpha_sleeves.datetime") as mock_dt:
        mock_dt.utcnow.return_value = fixed_now
        mock_dt.timedelta = timedelta
        with patch("services.alpha_sleeves.get_histories_batch", new=AsyncMock(return_value=histories)):
            sharpes = await get_dynamic_sleeve_sharpes(mock_db, lookback_days=30)

    assert "MR" in sharpes
    assert "StatArb" in sharpes
    assert "Trend" in sharpes
    assert "Factor" in sharpes
    # Non-MR sleeves are forced to 0.0 per code comment
    assert sharpes["StatArb"] == 0.0
    assert sharpes["Trend"] == 0.0
    assert sharpes["Factor"] == 0.0


@pytest.mark.asyncio
async def test_get_dynamic_sleeve_sharpes_db_exception():
    from services.alpha_sleeves import get_dynamic_sleeve_sharpes
    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("db error")
    fixed_now = datetime(2026, 6, 1, 12, 0, 0)
    with patch("services.alpha_sleeves.datetime") as mock_dt:
        mock_dt.utcnow.return_value = fixed_now
        mock_dt.timedelta = timedelta
        sharpes = await get_dynamic_sleeve_sharpes(mock_db, lookback_days=30)
    assert sharpes["MR"] == 1.0  # fallback


def test_allocate_cross_sleeve_capital_no_active():
    from services.alpha_sleeves import allocate_cross_sleeve_capital
    sharpes = {"MR": 0.0, "StatArb": -0.5, "Trend": 0.0}
    alloc = allocate_cross_sleeve_capital(sharpes, 1000.0)
    assert alloc == {"MR": 1000.0 / 3, "StatArb": 1000.0 / 3, "Trend": 1000.0 / 3}


def test_allocate_cross_sleeve_capital_floor_and_ceiling():
    from services.alpha_sleeves import allocate_cross_sleeve_capital
    # MR capped (>50%), Trend floored (<10%), StatArb stays unconstrained
    sharpes = {"MR": 0.8, "StatArb": 0.1, "Trend": 0.05}
    alloc = allocate_cross_sleeve_capital(sharpes, 1000.0)
    assert alloc["MR"] == pytest.approx(500.0)
    assert alloc["Trend"] == pytest.approx(100.0)
    assert alloc["StatArb"] == pytest.approx(400.0)


def test_allocate_cross_sleeve_capital_all_constrained():
    from services.alpha_sleeves import allocate_cross_sleeve_capital
    # Two sleeves, both would be >50% or <10% so they all hit constraints
    sharpes = {"A": 10.0, "B": 9.0}
    alloc = allocate_cross_sleeve_capital(sharpes, 1000.0)
    # A capped at 500, B capped at 500 → total 1000
    assert alloc["A"] == pytest.approx(500.0)
    assert alloc["B"] == pytest.approx(500.0)


# ─────────────────────────────────────────────────────────────────────────────
# services/calibration.py
# ─────────────────────────────────────────────────────────────────────────────


def test_fit_isotonic_exception():
    from services.calibration import _fit_isotonic
    with patch("sklearn.isotonic.IsotonicRegression", side_effect=Exception("sklearn fail")):
        result = _fit_isotonic(list(range(25)), [0] * 25)
        assert result is None


def test_build_spy_regime_cache_bear():
    from services.calibration import _build_spy_regime_cache
    import numpy as np
    dates = pd.date_range("2024-01-01", periods=400, freq="B")
    # SMA200 forms on flat 120, then price drops to 80 → bear
    prices = np.concatenate([np.full(300, 120), np.full(100, 80)])
    df = pd.DataFrame({"Close": prices}, index=dates)
    with patch("yfinance.download", return_value=df):
        result = _build_spy_regime_cache("2024-01-01", "2025-03-01")
    assert isinstance(result, dict)
    values = list(result.values())
    assert "bear" in values


def test_build_spy_regime_cache_neutral():
    from services.calibration import _build_spy_regime_cache
    import numpy as np
    dates = pd.date_range("2024-01-01", periods=400, freq="B")
    # Flat prices → ratio == 1.0 → neutral once SMA200 forms
    prices = np.full(400, 100.0)
    df = pd.DataFrame({"Close": prices}, index=dates)
    with patch("yfinance.download", return_value=df):
        result = _build_spy_regime_cache("2024-01-01", "2025-03-01")
    assert isinstance(result, dict)
    values = list(result.values())
    assert "neutral" in values


def test_build_spy_regime_cache_multiindex():
    from services.calibration import _build_spy_regime_cache
    dates = pd.date_range("2025-06-01", periods=210, freq="B")
    prices = np.linspace(100, 110, 210)
    df = pd.DataFrame({"Close": prices}, index=dates)
    # Simulate MultiIndex columns like yfinance sometimes returns
    df.columns = pd.MultiIndex.from_tuples([("Close", "SPY")])
    with patch("yfinance.download", return_value=df):
        result = _build_spy_regime_cache("2025-06-01", "2026-03-01")
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_run_calibration_no_signals():
    from services.calibration import run_calibration

    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.all.return_value = []
    mock_db.execute.return_value = mock_res

    session_mock = MagicMock()
    session_mock.return_value.__aenter__ = AsyncMock(return_value=mock_db)
    session_mock.return_value.__aexit__ = AsyncMock(return_value=False)

    with patch("database.AsyncSessionLocal", session_mock):
        result = await run_calibration()
    assert result == {}


@pytest.mark.asyncio
async def test_run_calibration_full_flow(tmp_path):
    from services.calibration import run_calibration, _CONF_CEIL, _CONF_FLOOR

    # Build mock signal rows as tuples matching the SELECT order:
    # action, confidence, outcome_14d, outcome_pct, created_at
    rows = [
        ("BUY", 55.0, 2.0, None, datetime(2026, 5, 1, tzinfo=timezone.utc)),
        ("SELL", 60.0, -1.5, None, datetime(2026, 5, 10, tzinfo=timezone.utc)),
        ("BUY", 65.0, None, 1.0, datetime(2026, 5, 15, tzinfo=timezone.utc)),
    ]

    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.all.return_value = rows
    mock_db.execute.return_value = mock_res

    session_mock = MagicMock()
    session_mock.return_value.__aenter__ = AsyncMock(return_value=mock_db)
    session_mock.return_value.__aexit__ = AsyncMock(return_value=False)

    # Mock yfinance SPY download
    import numpy as np
    dates = pd.date_range("2026-01-01", periods=150, freq="B")
    prices = np.linspace(100, 110, 150)
    spy_df = pd.DataFrame({"Close": prices}, index=dates)

    cal_file = tmp_path / "calibration.json"

    with patch("database.AsyncSessionLocal", session_mock):
        with patch("yfinance.download", return_value=spy_df):
            with patch("services.calibration._CAL_FILE", cal_file):
                result = await run_calibration()

    assert isinstance(result, dict)
    assert "_meta" in result
    assert result["_meta"]["n_total"] == 3
    # File should have been written
    assert cal_file.exists()


@pytest.mark.asyncio
async def test_run_calibration_sell_logic_and_brier():
    from services.calibration import run_calibration

    # Need enough samples for isotonic (≥20) and walk-forward validation
    rows = []
    base_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(30):
        action = "BUY" if i % 2 == 0 else "SELL"
        conf = 40.0 + i
        pct = 1.0 if action == "BUY" else -1.0
        rows.append(
            (action, conf, pct, None, base_date + timedelta(days=i))
        )

    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.all.return_value = rows
    mock_db.execute.return_value = mock_res

    session_mock = MagicMock()
    session_mock.return_value.__aenter__ = AsyncMock(return_value=mock_db)
    session_mock.return_value.__aexit__ = AsyncMock(return_value=False)

    dates = pd.date_range("2026-01-01", periods=150, freq="B")
    prices = np.linspace(100, 110, 150)
    spy_df = pd.DataFrame({"Close": prices}, index=dates)

    with patch("database.AsyncSessionLocal", session_mock):
        with patch("yfinance.download", return_value=spy_df):
            result = await run_calibration()

    assert "_meta" in result
    assert result["_meta"]["n_total"] == 30
    # Brier should be computed because validation set exists
    assert "brier_walkforward" in result["_meta"]


@pytest.mark.asyncio
async def test_archive_current_calibration_empty():
    from services.calibration import archive_current_calibration
    mock_db = AsyncMock()
    with patch("services.calibration.load_calibration", return_value={}):
        version = await archive_current_calibration(mock_db)
        assert version == ""


@pytest.mark.asyncio
async def test_archive_current_calibration_existing_version():
    from services.calibration import archive_current_calibration

    mock_db = AsyncMock()
    existing_row = MagicMock()
    mock_scalar = MagicMock()
    mock_scalar.scalar_one_or_none.return_value = existing_row
    mock_db.execute.return_value = mock_scalar

    with patch("services.calibration.load_calibration", return_value={"last_run": "2026-06-01T12:00:00"}):
        version = await archive_current_calibration(mock_db)
        assert version == "2026-06-01T12:00:00"
        # Should not commit because it already exists
        mock_db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_archive_current_calibration_new_version(tmp_path):
    from services.calibration import archive_current_calibration

    mock_db = AsyncMock()
    mock_scalar = MagicMock()
    mock_scalar.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_scalar

    cal_file = tmp_path / "calibration.json"
    cal_data = {"last_run": "2026-06-01T12:00:00", "50": {"win_rate": 0.6}}

    with patch("services.calibration.load_calibration", return_value=cal_data):
        with patch("services.calibration._DATA_DIR", tmp_path):
            with patch("services.calibration._CAL_FILE", cal_file):
                version = await archive_current_calibration(mock_db)
                assert version == "2026-06-01T12:00:00"
                mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_restore_calibration_version_missing():
    from services.calibration import restore_calibration_version
    mock_db = AsyncMock()
    mock_scalar = MagicMock()
    mock_scalar.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_scalar
    result = await restore_calibration_version(mock_db, "v1")
    assert result is False


@pytest.mark.asyncio
async def test_restore_calibration_version_success(tmp_path):
    from services.calibration import restore_calibration_version

    mock_db = AsyncMock()
    row = MagicMock()
    row.calibration_data = {"last_run": "2026-05-01T00:00:00"}
    mock_scalar = MagicMock()
    mock_scalar.scalar_one_or_none.return_value = row
    mock_db.execute.return_value = mock_scalar

    cal_file = tmp_path / "calibration.json"
    with patch("services.calibration._DATA_DIR", tmp_path):
        with patch("services.calibration._CAL_FILE", cal_file):
            result = await restore_calibration_version(mock_db, "2026-05-01T00:00:00")
            assert result is True
            assert cal_file.exists()
            assert json.loads(cal_file.read_text()) == row.calibration_data
            mock_db.commit.assert_awaited_once()
            assert row.is_active is True


# ─────────────────────────────────────────────────────────────────────────────
# services/institutional.py
# ─────────────────────────────────────────────────────────────────────────────


def _aiohttp_session(mock_resp):
    """Return a MagicMock session whose .get() yields an async context manager returning mock_resp."""
    session = MagicMock()
    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=mock_resp)
    cm.__aexit__ = AsyncMock(return_value=False)
    session.get.return_value = cm
    return session


@pytest.fixture(autouse=True)
def _clear_institutional_cache():
    from services.institutional import _CACHE
    _CACHE.clear()
    yield
    _CACHE.clear()


@pytest.mark.asyncio
async def test_get_success():
    from services.institutional import _get
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"foo": "bar"})
    session = _aiohttp_session(mock_resp)
    result = await _get(session, "http://example.com")
    assert result == {"foo": "bar"}


@pytest.mark.asyncio
async def test_get_non_200():
    from services.institutional import _get
    mock_resp = MagicMock()
    mock_resp.status = 404
    session = _aiohttp_session(mock_resp)
    result = await _get(session, "http://example.com")
    assert result is None


@pytest.mark.asyncio
async def test_get_exception():
    from services.institutional import _get
    session = MagicMock()
    session.get.side_effect = Exception("timeout")
    result = await _get(session, "http://example.com")
    assert result is None


@pytest.mark.asyncio
async def test_fetch_latest_13f_holdings_cache_hit():
    from services.institutional import _fetch_latest_13f_holdings, _CACHE
    cik = "0009999999"
    _CACHE[f"13f_{cik}"] = {"ts": __import__("time").time(), "data": [{"ticker": "AAPL"}]}
    session = MagicMock()
    result = await _fetch_latest_13f_holdings(session, cik)
    assert result == [{"ticker": "AAPL"}]


@pytest.mark.asyncio
async def test_fetch_latest_13f_holdings_no_filings():
    from services.institutional import _fetch_latest_13f_holdings
    session = MagicMock()
    with patch("services.institutional._get", new=AsyncMock(return_value={"filings": {"recent": {"form": [], "filingDate": [], "accessionNumber": []}}})):
        result = await _fetch_latest_13f_holdings(session, "0009999998")
        assert result == []


@pytest.mark.asyncio
async def test_fetch_latest_13f_holdings_actions_and_trends():
    from services.institutional import _fetch_latest_13f_holdings

    async def mock_get(session, url):
        if "submissions" in url:
            return {
                "filings": {
                    "recent": {
                        "form": ["13F-HR", "13F-HR", "13F-HR"],
                        "filingDate": ["2026-05-10", "2026-02-10", "2025-11-10"],
                        "accessionNumber": ["000-12345", "000-12344", "000-12343"],
                    }
                }
            }
        if "index.json" in url:
            return {"directory": {"item": [{"name": "infotable.xml"}]}}
        return None

    # Build holdings for three quarters to test all actions/trends
    q0 = [{"name": "Apple", "ticker": "AAPL", "cusip": "037833100", "value_k": 5000, "shares": 10000, "filing_date": "2026-05-10"}]
    q1 = [{"name": "Apple", "ticker": "AAPL", "cusip": "037833100", "value_k": 4500, "shares": 8000, "filing_date": "2026-02-10"}]
    q2 = [{"name": "Apple", "ticker": "AAPL", "cusip": "037833100", "value_k": 4000, "shares": 7000, "filing_date": "2025-11-10"}]

    call_idx = 0
    async def mock_parse(session, url, filing_date):
        nonlocal call_idx
        holdings = [q0, q1, q2][call_idx]
        call_idx += 1
        return holdings

    session = MagicMock()
    with patch("services.institutional._get", side_effect=mock_get):
        with patch("services.institutional._parse_infotable_xml", side_effect=mock_parse):
            result = await _fetch_latest_13f_holdings(session, "0009999997")

    assert len(result) == 1
    assert result[0]["action"] == "increased"  # 10000 > 8000*1.05
    assert result[0]["qoq_trend"] == "rising"  # 8000 > 7000*1.05


@pytest.mark.asyncio
async def test_fetch_latest_13f_holdings_decreased_trends():
    from services.institutional import _fetch_latest_13f_holdings

    async def mock_get(session, url):
        if "submissions" in url:
            return {
                "filings": {
                    "recent": {
                        "form": ["13F-HR", "13F-HR", "13F-HR"],
                        "filingDate": ["2026-05-10", "2026-02-10", "2025-11-10"],
                        "accessionNumber": ["000-12345", "000-12344", "000-12343"],
                    }
                }
            }
        if "index.json" in url:
            return {"directory": {"item": [{"name": "infotable.xml"}]}}
        return None

    # Decreased this quarter, decreased last quarter → falling
    q0 = [{"name": "A", "ticker": "AAPL", "cusip": "037833100", "value_k": 5000, "shares": 6000, "filing_date": "2026-05-10"}]
    q1 = [{"name": "A", "ticker": "AAPL", "cusip": "037833100", "value_k": 4500, "shares": 8000, "filing_date": "2026-02-10"}]
    q2 = [{"name": "A", "ticker": "AAPL", "cusip": "037833100", "value_k": 4000, "shares": 10000, "filing_date": "2025-11-10"}]

    call_idx = 0
    async def mock_parse(session, url, filing_date):
        nonlocal call_idx
        holdings = [q0, q1, q2][call_idx]
        call_idx += 1
        return holdings

    session = MagicMock()
    with patch("services.institutional._get", side_effect=mock_get):
        with patch("services.institutional._parse_infotable_xml", side_effect=mock_parse):
            result = await _fetch_latest_13f_holdings(session, "0009999996")

    assert result[0]["action"] == "decreased"
    # q1(8000) < q2(10000)*0.95=9500 → falling
    assert result[0]["qoq_trend"] == "falling"


@pytest.mark.asyncio
async def test_fetch_latest_13f_holdings_unchanged():
    from services.institutional import _fetch_latest_13f_holdings

    async def mock_get(session, url):
        if "submissions" in url:
            return {
                "filings": {
                    "recent": {
                        "form": ["13F-HR", "13F-HR"],
                        "filingDate": ["2026-05-10", "2026-02-10"],
                        "accessionNumber": ["000-12345", "000-12344"],
                    }
                }
            }
        if "index.json" in url:
            return {"directory": {"item": [{"name": "infotable.xml"}]}}
        return None

    q0 = [{"name": "A", "ticker": "AAPL", "cusip": "037833100", "value_k": 5000, "shares": 10000, "filing_date": "2026-05-10"}]
    q1 = [{"name": "A", "ticker": "AAPL", "cusip": "037833100", "value_k": 4500, "shares": 10000, "filing_date": "2026-02-10"}]

    call_idx = 0
    async def mock_parse(session, url, filing_date):
        nonlocal call_idx
        holdings = [q0, q1][call_idx]
        call_idx += 1
        return holdings

    session = MagicMock()
    with patch("services.institutional._get", side_effect=mock_get):
        with patch("services.institutional._parse_infotable_xml", side_effect=mock_parse):
            result = await _fetch_latest_13f_holdings(session, "0009999995")

    assert result[0]["action"] == "unchanged"
    assert result[0]["qoq_trend"] == "neutral"


@pytest.mark.asyncio
async def test_fetch_latest_13f_holdings_new_position():
    from services.institutional import _fetch_latest_13f_holdings

    async def mock_get(session, url):
        if "submissions" in url:
            return {
                "filings": {
                    "recent": {
                        "form": ["13F-HR", "13F-HR"],
                        "filingDate": ["2026-05-10", "2026-02-10"],
                        "accessionNumber": ["000-12345", "000-12344"],
                    }
                }
            }
        if "index.json" in url:
            return {"directory": {"item": [{"name": "infotable.xml"}]}}
        return None

    q0 = [{"name": "A", "ticker": "AAPL", "cusip": "037833100", "value_k": 5000, "shares": 10000, "filing_date": "2026-05-10"}]
    q1 = []  # no previous holding

    call_idx = 0
    async def mock_parse(session, url, filing_date):
        nonlocal call_idx
        holdings = [q0, q1][call_idx]
        call_idx += 1
        return holdings

    session = MagicMock()
    with patch("services.institutional._get", side_effect=mock_get):
        with patch("services.institutional._parse_infotable_xml", side_effect=mock_parse):
            result = await _fetch_latest_13f_holdings(session, "0009999994")

    assert result[0]["action"] == "new"
    assert result[0]["qoq_trend"] == "neutral"


@pytest.mark.asyncio
async def test_parse_infotable_xml_success():
    from services.institutional import _parse_infotable_xml
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<informationTable xmlns="http://www.sec.gov/edgar/document/thirteenf/informationtable">
  <infoTable>
    <nameOfIssuer>Apple Inc</nameOfIssuer>
    <cusip>037833100</cusip>
    <value>5000</value>
    <sshPrnamt>10000</sshPrnamt>
  </infoTable>
</informationTable>"""
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value=xml)
    session = _aiohttp_session(mock_resp)
    result = await _parse_infotable_xml(session, "http://example.com/infotable.xml", "2026-05-10")
    assert len(result) == 1
    assert result[0]["ticker"] == "AAPL"
    assert result[0]["value_k"] == 5000
    assert result[0]["shares"] == 10000


@pytest.mark.asyncio
async def test_parse_infotable_xml_non_200():
    from services.institutional import _parse_infotable_xml
    mock_resp = MagicMock()
    mock_resp.status = 404
    session = _aiohttp_session(mock_resp)
    result = await _parse_infotable_xml(session, "http://example.com/infotable.xml", "2026-05-10")
    assert result == []


@pytest.mark.asyncio
async def test_parse_infotable_xml_parse_error():
    from services.institutional import _parse_infotable_xml
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value="<<<not xml")
    session = _aiohttp_session(mock_resp)
    result = await _parse_infotable_xml(session, "http://example.com/infotable.xml", "2026-05-10")
    assert result == []


@pytest.mark.asyncio
async def test_get_institutional_signals_sell_and_new():
    from services.institutional import get_institutional_signals

    async def mock_fetch(session, cik):
        if cik == "0001067983":
            # Berkshire: decreased AAPL
            return [
                {
                    "ticker": "AAPL",
                    "value_k": 5000,
                    "shares": 5000,
                    "action": "decreased",
                    "filing_date": "2026-05-10",
                    "qoq_trend": "falling",
                }
            ]
        if cik == "0000102909":
            # Vanguard: new MSFT
            return [
                {
                    "ticker": "MSFT",
                    "value_k": 3000,
                    "shares": 3000,
                    "action": "new",
                    "filing_date": "2026-05-10",
                    "qoq_trend": "neutral",
                }
            ]
        return []

    with patch("services.institutional._fetch_latest_13f_holdings", side_effect=mock_fetch):
        signals = await get_institutional_signals(["AAPL", "MSFT"])

    by_ticker = {s["ticker"]: s for s in signals}
    assert "AAPL" in by_ticker
    assert by_ticker["AAPL"]["score"] < 0
    assert by_ticker["AAPL"]["rationale"]["head"].startswith("Institutional selling")
    assert "MSFT" in by_ticker
    assert by_ticker["MSFT"]["score"] > 0


@pytest.mark.asyncio
async def test_get_institutional_signals_watchlist_filter():
    from services.institutional import get_institutional_signals

    async def mock_fetch(session, cik):
        return [
            {"ticker": "AAPL", "value_k": 5000, "shares": 10000, "action": "increased", "filing_date": "2026-05-10", "qoq_trend": "neutral"},
            {"ticker": "TSLA", "value_k": 2000, "shares": 2000, "action": "increased", "filing_date": "2026-05-10", "qoq_trend": "neutral"},
        ]

    with patch("services.institutional._fetch_latest_13f_holdings", side_effect=mock_fetch):
        signals = await get_institutional_signals(["AAPL"])

    assert len(signals) == 1
    assert signals[0]["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_get_institutional_signals_exception_in_fund_loop():
    from services.institutional import get_institutional_signals

    call_count = 0
    async def mock_fetch(session, cik):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("blow up")
        return [
            {"ticker": "AAPL", "value_k": 5000, "shares": 10000, "action": "increased", "filing_date": "2026-05-10", "qoq_trend": "neutral"},
        ]

    with patch("services.institutional._fetch_latest_13f_holdings", side_effect=mock_fetch):
        signals = await get_institutional_signals(["AAPL"])

    assert len(signals) == 1
    assert signals[0]["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_get_institutional_signals_aggregation_multiple_funds():
    from services.institutional import get_institutional_signals

    async def mock_fetch(session, cik):
        return [
            {"ticker": "AAPL", "value_k": 5000, "shares": 10000, "action": "increased", "filing_date": "2026-05-10", "qoq_trend": "neutral"},
        ]

    with patch("services.institutional._fetch_latest_13f_holdings", side_effect=mock_fetch):
        signals = await get_institutional_signals(["AAPL"])

    # Every tracked fund returns the same holding → score aggregates
    assert len(signals) == 1
    assert signals[0]["ticker"] == "AAPL"
    assert abs(signals[0]["score"]) <= 20  # capped
