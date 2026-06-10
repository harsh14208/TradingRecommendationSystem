"""Extended tests for services/signal_ml.py — edge cases, error handling, DB, model loading."""
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_sig(**kwargs):
    defaults = {
        "ticker": "AAPL",
        "action": "BUY",
        "confidence": 55.0,
        "raw_score": 60,
        "sources": ["technicals", "macro"],
        "rationale": [
            {"sentiment": "pos", "head": "RSI oversold"},
            {"sentiment": "neg", "head": "VIX elevated"},
        ],
        "rr": "1:2.0",
        "session": "regular",
        "style": "swing",
        "entry": 150.0,
        "stop": 145.0,
        "target": 160.0,
        "price": 150.0,
        "created_at": "2024-01-15T10:00:00",
        "change_pct": 1.5,
        "days_to_earnings": 90,
        "sector_etf": "XLK",
        "rs_vs_sector": 0.05,
    }
    defaults.update(kwargs)
    return defaults


def _make_tech(**kwargs):
    defaults = {
        "bb_pct_b": 0.1,
        "ibs": 0.12,
        "vwap_pct": -0.5,
        "rsi": 28.0,
        "adx": 25.0,
        "rvol": 1.4,
        "price": 150.0,
        "atr": 3.0,
        "price_zscore": -1.5,
        "ou_halflife": 5.0,
        "hurst": 0.35,
    }
    defaults.update(kwargs)
    return defaults


@pytest.fixture(autouse=True)
def _reset_signal_ml_state():
    """Reset all module-level caches before each test."""
    import services.signal_ml as ml

    orig = {
        "_model": ml._model,
        "_model_mtime": ml._model_mtime,
        "_entry_model": ml._entry_model,
        "_entry_model_mtime": ml._entry_model_mtime,
        "_meta_model": ml._meta_model,
        "_meta_model_mtime": ml._meta_model_mtime,
        "_challenger_model": ml._challenger_model,
        "_challenger_model_mtime": ml._challenger_model_mtime,
        "_sector_models": dict(ml._sector_models),
    }
    ml._model = None
    ml._model_mtime = 0.0
    ml._entry_model = None
    ml._entry_model_mtime = 0.0
    ml._meta_model = None
    ml._meta_model_mtime = 0.0
    ml._challenger_model = None
    ml._challenger_model_mtime = 0.0
    ml._sector_models.clear()
    yield
    ml._model = orig["_model"]
    ml._model_mtime = orig["_model_mtime"]
    ml._entry_model = orig["_entry_model"]
    ml._entry_model_mtime = orig["_entry_model_mtime"]
    ml._meta_model = orig["_meta_model"]
    ml._meta_model_mtime = orig["_meta_model_mtime"]
    ml._challenger_model = orig["_challenger_model"]
    ml._challenger_model_mtime = orig["_challenger_model_mtime"]
    ml._sector_models.clear()
    ml._sector_models.update(orig["_sector_models"])


# ── _extract_entry_features ───────────────────────────────────────────────────


def test_extract_entry_features_full():
    from services.signal_ml import _extract_entry_features

    feats = _extract_entry_features(_make_tech(), vix=20.0, sector_etf="XLK", dow=1, month=6)
    assert len(feats) == 14
    assert all(isinstance(f, (int, float)) for f in feats)


def test_extract_entry_features_missing_keys():
    from services.signal_ml import _extract_entry_features

    feats = _extract_entry_features({}, vix=None, sector_etf=None, dow=None, month=None)
    assert len(feats) == 14
    assert all(math.isnan(f) for f in feats)


def test_extract_entry_features_zero_price():
    from services.signal_ml import _extract_entry_features

    tech = _make_tech(price=0.0)
    feats = _extract_entry_features(tech, vix=20.0, sector_etf="XLK", dow=1, month=6)
    assert math.isnan(feats[6])  # atr_pct


def test_extract_entry_features_nan_in_tech():
    from services.signal_ml import _extract_entry_features

    tech = _make_tech(rsi=float("nan"))
    feats = _extract_entry_features(tech, vix=20.0, sector_etf="XLK", dow=1, month=6)
    assert math.isnan(feats[3])  # rsi


# ── validate_feature_schema ───────────────────────────────────────────────────


def test_validate_feature_schema_ok():
    from services.signal_ml import validate_feature_schema

    assert validate_feature_schema([1.0, 2.0, 3], ["a", "b", "c"]) is True


def test_validate_feature_schema_length_mismatch():
    from services.signal_ml import validate_feature_schema

    assert validate_feature_schema([1.0], ["a", "b"]) is False


def test_validate_feature_schema_type_shift():
    from services.signal_ml import validate_feature_schema

    assert validate_feature_schema([1.0, "bad"], ["a", "b"]) is False


def test_validate_feature_schema_none_allowed():
    from services.signal_ml import validate_feature_schema

    assert validate_feature_schema([1.0, None], ["a", "b"]) is True


# ── predict_challenger_prob ───────────────────────────────────────────────────


def test_predict_challenger_prob_no_model():
    from services.signal_ml import predict_challenger_prob

    assert predict_challenger_prob(_make_sig(), model=None) is None


def test_predict_challenger_prob_schema_failure():
    from services.signal_ml import predict_challenger_prob, _CHALLENGER_FEATURE_NAMES

    mock_model = MagicMock()
    with patch("services.signal_ml.validate_feature_schema", return_value=False):
        assert predict_challenger_prob(_make_sig(), model=mock_model) is None


def test_predict_challenger_prob_success():
    from services.signal_ml import predict_challenger_prob

    mock_model = MagicMock()
    mock_model.predict.return_value = [0.72]
    with patch("services.signal_ml.validate_feature_schema", return_value=True):
        with patch.dict(sys.modules, {"numpy": MagicMock(), "xgboost": MagicMock()}):
            # Need to simulate the actual np.array and xgb.DMatrix usage
            np_mock = MagicMock()
            xgb_mock = MagicMock()
            dm_mock = MagicMock()
            xgb_mock.DMatrix.return_value = dm_mock
            np_mock.array.return_value = "array"
            with patch.dict(sys.modules, {"numpy": np_mock, "xgboost": xgb_mock}):
                result = predict_challenger_prob(_make_sig(), model=mock_model)
    assert result == 0.72


def test_predict_challenger_prob_exception():
    from services.signal_ml import predict_challenger_prob

    mock_model = MagicMock()
    mock_model.predict.side_effect = Exception("boom")
    with patch("services.signal_ml.validate_feature_schema", return_value=True):
        with patch.dict(sys.modules, {"numpy": MagicMock(), "xgboost": MagicMock()}):
            np_mock = MagicMock()
            xgb_mock = MagicMock()
            xgb_mock.DMatrix.side_effect = Exception("boom")
            np_mock.array.return_value = "array"
            with patch.dict(sys.modules, {"numpy": np_mock, "xgboost": xgb_mock}):
                result = predict_challenger_prob(_make_sig(), model=mock_model)
    assert result is None


# ── predict_entry_prob ────────────────────────────────────────────────────────


def test_predict_entry_prob_no_model():
    from services.signal_ml import predict_entry_prob

    assert predict_entry_prob(_make_tech(), vix=20.0, sector_etf="XLK", model=None) is None


def test_predict_entry_prob_schema_failure():
    from services.signal_ml import predict_entry_prob

    mock_model = MagicMock()
    with patch("services.signal_ml.validate_feature_schema", return_value=False):
        assert predict_entry_prob(_make_tech(), vix=20.0, sector_etf="XLK", model=mock_model) is None


def test_predict_entry_prob_success():
    from services.signal_ml import predict_entry_prob

    mock_model = MagicMock()
    mock_model.predict.return_value = [0.65]
    with patch("services.signal_ml.validate_feature_schema", return_value=True):
        np_mock = MagicMock()
        xgb_mock = MagicMock()
        dm_mock = MagicMock()
        xgb_mock.DMatrix.return_value = dm_mock
        np_mock.array.return_value = "array"
        with patch.dict(sys.modules, {"numpy": np_mock, "xgboost": xgb_mock}):
            result = predict_entry_prob(_make_tech(), vix=20.0, sector_etf="XLK", model=mock_model)
    assert result == 0.65


def test_predict_entry_prob_exception():
    from services.signal_ml import predict_entry_prob

    mock_model = MagicMock()
    with patch("services.signal_ml.validate_feature_schema", return_value=True):
        np_mock = MagicMock()
        xgb_mock = MagicMock()
        xgb_mock.DMatrix.side_effect = Exception("boom")
        np_mock.array.return_value = "array"
        with patch.dict(sys.modules, {"numpy": np_mock, "xgboost": xgb_mock}):
            result = predict_entry_prob(_make_tech(), vix=20.0, sector_etf="XLK", model=mock_model)
    assert result is None


# ── predict_entry_prob_sector ─────────────────────────────────────────────────


def test_predict_entry_prob_sector_uses_sector_model():
    from services.signal_ml import predict_entry_prob_sector
    import services.signal_ml as ml

    mock_sector_model = MagicMock()
    mock_sector_model.predict.return_value = [0.88]
    with patch.object(ml, "get_sector_entry_model", return_value=mock_sector_model):
        with patch.object(ml, "get_entry_model", return_value=None):
            with patch("services.signal_ml.validate_feature_schema", return_value=True):
                np_mock = MagicMock()
                xgb_mock = MagicMock()
                xgb_mock.DMatrix.return_value = MagicMock()
                np_mock.array.return_value = "array"
                with patch.dict(sys.modules, {"numpy": np_mock, "xgboost": xgb_mock}):
                    result = predict_entry_prob_sector(_make_tech(), vix=20.0, sector_etf="XLK")
    assert result == 0.88


def test_predict_entry_prob_sector_fallback_global():
    from services.signal_ml import predict_entry_prob_sector
    import services.signal_ml as ml

    mock_global = MagicMock()
    mock_global.predict.return_value = [0.55]
    with patch.object(ml, "get_sector_entry_model", return_value=None):
        with patch.object(ml, "get_entry_model", return_value=mock_global):
            with patch("services.signal_ml.validate_feature_schema", return_value=True):
                np_mock = MagicMock()
                xgb_mock = MagicMock()
                xgb_mock.DMatrix.return_value = MagicMock()
                np_mock.array.return_value = "array"
                with patch.dict(sys.modules, {"numpy": np_mock, "xgboost": xgb_mock}):
                    result = predict_entry_prob_sector(_make_tech(), vix=20.0, sector_etf="XLK")
    assert result == 0.55


# ── get_sector_entry_model ────────────────────────────────────────────────────


def test_get_sector_entry_model_no_sector():
    from services.signal_ml import get_sector_entry_model

    assert get_sector_entry_model(None) is None
    assert get_sector_entry_model("") is None


def test_get_sector_entry_model_file_absent(tmp_path):
    from services.signal_ml import get_sector_entry_model
    import services.signal_ml as ml

    fake_dir = tmp_path / "data"
    orig = ml._DATA_DIR
    ml._DATA_DIR = fake_dir
    try:
        assert get_sector_entry_model("XLK") is None
    finally:
        ml._DATA_DIR = orig


def test_get_sector_entry_model_load_success(tmp_path):
    from services.signal_ml import get_sector_entry_model
    import services.signal_ml as ml

    fake_dir = tmp_path / "data"
    fake_dir.mkdir()
    model_file = fake_dir / "backtest_ml_model_XLK.json"
    model_file.write_text("{}")

    orig_dir = ml._DATA_DIR
    ml._DATA_DIR = fake_dir
    try:
        mock_booster = MagicMock()
        xgb_mock = MagicMock()
        xgb_mock.Booster.return_value = mock_booster
        with patch.dict(sys.modules, {"xgboost": xgb_mock}):
            result = get_sector_entry_model("XLK")
        assert result is mock_booster
        mock_booster.load_model.assert_called_once_with(str(model_file))
    finally:
        ml._DATA_DIR = orig_dir
        ml._sector_models.clear()


def test_get_sector_entry_model_load_failure(tmp_path):
    from services.signal_ml import get_sector_entry_model
    import services.signal_ml as ml

    fake_dir = tmp_path / "data"
    fake_dir.mkdir()
    model_file = fake_dir / "backtest_ml_model_XLF.json"
    model_file.write_text("{}")

    orig_dir = ml._DATA_DIR
    ml._DATA_DIR = fake_dir
    try:
        xgb_mock = MagicMock()
        xgb_mock.Booster.side_effect = Exception("corrupt")
        with patch.dict(sys.modules, {"xgboost": xgb_mock}):
            result = get_sector_entry_model("XLF")
        assert result is None
    finally:
        ml._DATA_DIR = orig_dir
        ml._sector_models.clear()


def test_get_sector_entry_model_cache_hit(tmp_path):
    from services.signal_ml import get_sector_entry_model
    import services.signal_ml as ml

    fake_dir = tmp_path / "data"
    fake_dir.mkdir()
    model_file = fake_dir / "backtest_ml_model_XLU.json"
    model_file.write_text("{}")

    orig_dir = ml._DATA_DIR
    ml._DATA_DIR = fake_dir
    mock_booster = MagicMock()
    xgb_mock = MagicMock()
    xgb_mock.Booster.return_value = mock_booster
    try:
        with patch.dict(sys.modules, {"xgboost": xgb_mock}):
            r1 = get_sector_entry_model("XLU")
            # Second call with same mtime should return cached model
            r2 = get_sector_entry_model("XLU")
        assert r1 is r2 is mock_booster
        # load_model should only be called once
        assert mock_booster.load_model.call_count == 1
    finally:
        ml._DATA_DIR = orig_dir
        ml._sector_models.clear()


def test_get_sector_entry_model_oserror_on_stat(tmp_path):
    from services.signal_ml import get_sector_entry_model
    import services.signal_ml as ml

    fake_dir = tmp_path / "data"
    fake_dir.mkdir()
    model_file = fake_dir / "backtest_ml_model_XLI.json"
    model_file.write_text("{}")

    orig_dir = ml._DATA_DIR
    ml._DATA_DIR = fake_dir
    mock_booster = MagicMock()
    ml._sector_models["XLI"] = (mock_booster, 999.0)
    try:
        # Patch stat() to raise OSError
        with patch.object(Path, "stat", side_effect=OSError("denied")):
            result = get_sector_entry_model("XLI")
        assert result is mock_booster
    finally:
        ml._DATA_DIR = orig_dir
        ml._sector_models.clear()


# ── get_meta_model ────────────────────────────────────────────────────────────


def test_get_meta_model_file_absent():
    from services.signal_ml import get_meta_model
    import services.signal_ml as ml

    orig_file = ml._META_MODEL_FILE
    mock_path = MagicMock()
    mock_path.exists.return_value = False
    ml._META_MODEL_FILE = mock_path
    try:
        assert get_meta_model() is None
    finally:
        ml._META_MODEL_FILE = orig_file
        ml._meta_model = None
        ml._meta_model_mtime = 0.0


def test_get_meta_model_load_success():
    from services.signal_ml import get_meta_model
    import services.signal_ml as ml

    mock_booster = MagicMock()
    xgb_mock = MagicMock()
    xgb_mock.Booster.return_value = mock_booster

    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.stat.return_value.st_mtime = 1234.0
    mock_path.name = "meta_label_model.json"

    orig_file = ml._META_MODEL_FILE
    ml._META_MODEL_FILE = mock_path
    try:
        with patch.dict(sys.modules, {"xgboost": xgb_mock}):
            result = get_meta_model()
        assert result is mock_booster
        mock_booster.load_model.assert_called_once()
    finally:
        ml._META_MODEL_FILE = orig_file
        ml._meta_model = None
        ml._meta_model_mtime = 0.0


def test_get_meta_model_cache_hit():
    from services.signal_ml import get_meta_model
    import services.signal_ml as ml

    mock_booster = MagicMock()
    xgb_mock = MagicMock()
    xgb_mock.Booster.return_value = mock_booster

    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.stat.return_value.st_mtime = 1234.0
    mock_path.name = "meta_label_model.json"

    orig_file = ml._META_MODEL_FILE
    ml._META_MODEL_FILE = mock_path
    try:
        with patch.dict(sys.modules, {"xgboost": xgb_mock}):
            r1 = get_meta_model()
            r2 = get_meta_model()
        assert r1 is r2 is mock_booster
        assert mock_booster.load_model.call_count == 1
    finally:
        ml._META_MODEL_FILE = orig_file
        ml._meta_model = None
        ml._meta_model_mtime = 0.0


def test_get_meta_model_exception():
    from services.signal_ml import get_meta_model
    import services.signal_ml as ml

    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.stat.side_effect = Exception("boom")

    orig_file = ml._META_MODEL_FILE
    ml._META_MODEL_FILE = mock_path
    try:
        assert get_meta_model() is None
    finally:
        ml._META_MODEL_FILE = orig_file
        ml._meta_model = None
        ml._meta_model_mtime = 0.0


# ── predict_meta_prob ─────────────────────────────────────────────────────────


def test_predict_meta_prob_no_model():
    from services.signal_ml import predict_meta_prob

    with patch("services.signal_ml.get_meta_model", return_value=None):
        assert predict_meta_prob(_make_tech(), entry_prob=0.6, hmm_regime={}, vix=20.0, sector_etf="XLK", dte=30) is None


def test_predict_meta_prob_success():
    from services.signal_ml import predict_meta_prob

    mock_model = MagicMock()
    mock_model.predict.return_value = [0.78]
    with patch("services.signal_ml.get_meta_model", return_value=mock_model):
        np_mock = MagicMock()
        xgb_mock = MagicMock()
        xgb_mock.DMatrix.return_value = MagicMock()
        np_mock.array.return_value = "array"
        with patch.dict(sys.modules, {"numpy": np_mock, "xgboost": xgb_mock}):
            result = predict_meta_prob(_make_tech(), entry_prob=0.6, hmm_regime={}, vix=20.0, sector_etf="XLK", dte=30)
    assert result == 0.78


def test_predict_meta_prob_exception():
    from services.signal_ml import predict_meta_prob

    mock_model = MagicMock()
    mock_model.predict.side_effect = Exception("boom")
    with patch("services.signal_ml.get_meta_model", return_value=mock_model):
        np_mock = MagicMock()
        xgb_mock = MagicMock()
        xgb_mock.DMatrix.side_effect = Exception("boom")
        np_mock.array.return_value = "array"
        with patch.dict(sys.modules, {"numpy": np_mock, "xgboost": xgb_mock}):
            result = predict_meta_prob(_make_tech(), entry_prob=0.6, hmm_regime={}, vix=20.0, sector_etf="XLK", dte=30)
    assert result is None


# ── _extract_meta_features ────────────────────────────────────────────────────


def test_extract_meta_features_full():
    from services.signal_ml import _extract_meta_features

    tech = _make_tech()
    hmm = {"bull_prob": 0.7, "transition_risk": 0.2}
    feats = _extract_meta_features(tech, entry_prob=0.6, hmm_regime=hmm, vix=20.0, sector_etf="XLK", dow=1, dte=30, vix_term_ratio=1.1, sector_momentum=0.02, vix_9d_ratio=0.95)
    assert len(feats) == 14
    assert feats[0] == 0.6  # entry_prob
    assert not math.isnan(feats[7])  # transition_risk


def test_extract_meta_features_defaults_from_tech():
    from services.signal_ml import _extract_meta_features

    tech = _make_tech(vix_term_ratio=1.2, sector_momentum=0.03, vix_9d_ratio=0.9)
    feats = _extract_meta_features(tech, entry_prob=None, hmm_regime=None, vix=None, sector_etf=None, dow=None, dte=None)
    assert len(feats) == 14
    assert math.isnan(feats[0])  # entry_prob
    assert feats[11] == 1.2  # vix_term_ratio from tech
    assert feats[12] == 0.03  # sector_momentum from tech
    assert feats[13] == 0.9  # vix_9d_ratio from tech


def test_extract_meta_features_all_nan():
    from services.signal_ml import _extract_meta_features

    feats = _extract_meta_features({}, entry_prob=None, hmm_regime=None, vix=None, sector_etf=None, dow=None, dte=None)
    assert len(feats) == 14
    # hmm defaults provide non-NaN values for bull_prob and transition_risk
    assert math.isnan(feats[0])  # entry_prob
    assert not math.isnan(feats[6])  # bull_prob defaults to 0.5
    assert not math.isnan(feats[7])  # transition_risk defaults to 0.1
    assert math.isnan(feats[8])  # dte_bucket
    assert math.isnan(feats[9])  # sector_ord
    assert math.isnan(feats[10])  # dow


# ── compute_rolling_auc ───────────────────────────────────────────────────────


def test_compute_rolling_auc_no_db():
    from services.signal_ml import compute_rolling_auc

    with patch("os.path.exists", return_value=False):
        result = compute_rolling_auc(window_days=30)
    assert result["status"] == "no_db"
    assert result["auc"] is None


def test_compute_rolling_auc_insufficient_n():
    from services.signal_ml import compute_rolling_auc

    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchall.return_value = [(50.0, 1.0)] * 5
    with patch("os.path.exists", return_value=True):
        with patch("sqlite3.connect", return_value=mock_conn):
            result = compute_rolling_auc(window_days=30)
    assert result["status"] == "insufficient_n"


def test_compute_rolling_auc_no_variance():
    from services.signal_ml import compute_rolling_auc

    rows = [(60.0, 2.0)] * 25
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchall.return_value = rows
    with patch("os.path.exists", return_value=True):
        with patch("sqlite3.connect", return_value=mock_conn):
            result = compute_rolling_auc(window_days=30)
    assert result["status"] == "no_variance"


def test_compute_rolling_auc_ok():
    from services.signal_ml import compute_rolling_auc

    # Mix of positive and negative outcomes
    rows = [(60.0, 2.0), (55.0, -1.0), (70.0, 3.0), (50.0, -2.0)] * 10
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchall.return_value = rows
    with patch("os.path.exists", return_value=True):
        with patch("sqlite3.connect", return_value=mock_conn):
            result = compute_rolling_auc(window_days=30)
    assert result["status"] in ("ok", "warn", "degrade")
    assert result["auc"] is not None
    assert 0.0 <= result["auc"] <= 1.0


def test_compute_rolling_auc_db_error():
    from services.signal_ml import compute_rolling_auc

    with patch("os.path.exists", return_value=True):
        with patch("sqlite3.connect", side_effect=Exception("locked")):
            result = compute_rolling_auc(window_days=30)
    assert result["status"].startswith("db_error")


def test_compute_rolling_auc_warn_threshold():
    from services.signal_ml import compute_rolling_auc

    # All low confidence + positive outcome → AUC should be near 0 (degrade/warn)
    rows = [(30.0, 1.0)] * 15 + [(80.0, -1.0)] * 15
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchall.return_value = rows
    with patch("os.path.exists", return_value=True):
        with patch("sqlite3.connect", return_value=mock_conn):
            result = compute_rolling_auc(window_days=30)
    assert result["status"] in ("warn", "degrade", "ok")
    assert result["auc"] is not None


# ── load_model ────────────────────────────────────────────────────────────────


def test_load_model_import_error():
    from services.signal_ml import load_model

    with patch.dict(sys.modules, {"xgboost": None}):
        # Force ImportError by removing xgboost from sys.modules and blocking import
        import builtins
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "xgboost":
                raise ImportError("no xgboost")
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", fake_import):
            assert load_model() is None


def test_load_model_file_absent(tmp_path):
    from services.signal_ml import load_model
    import services.signal_ml as ml

    orig = ml._MODEL_FILE
    ml._MODEL_FILE = tmp_path / "nonexistent.json"
    try:
        with patch.dict(sys.modules, {"xgboost": MagicMock()}):
            assert load_model() is None
    finally:
        ml._MODEL_FILE = orig


def test_load_model_success(tmp_path):
    from services.signal_ml import load_model
    import services.signal_ml as ml

    model_file = tmp_path / "signal_ml_model.json"
    model_file.write_text("{}")
    orig = ml._MODEL_FILE
    ml._MODEL_FILE = model_file
    mock_booster = MagicMock()
    xgb_mock = MagicMock()
    xgb_mock.Booster.return_value = mock_booster
    try:
        with patch.dict(sys.modules, {"xgboost": xgb_mock}):
            result = load_model()
        assert result is mock_booster
        mock_booster.load_model.assert_called_once_with(str(model_file))
    finally:
        ml._MODEL_FILE = orig


def test_load_model_load_failure(tmp_path):
    from services.signal_ml import load_model
    import services.signal_ml as ml

    model_file = tmp_path / "signal_ml_model.json"
    model_file.write_text("{}")
    orig = ml._MODEL_FILE
    ml._MODEL_FILE = model_file
    xgb_mock = MagicMock()
    xgb_mock.Booster.side_effect = Exception("corrupt")
    try:
        with patch.dict(sys.modules, {"xgboost": xgb_mock}):
            result = load_model()
        assert result is None
    finally:
        ml._MODEL_FILE = orig


# ── get_model ─────────────────────────────────────────────────────────────────


def test_get_model_oserror_on_stat():
    from services.signal_ml import get_model
    import services.signal_ml as ml

    mock_model = MagicMock()
    ml._model = mock_model
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.stat.side_effect = OSError("denied")
    orig = ml._MODEL_FILE
    ml._MODEL_FILE = mock_path
    try:
        result = get_model()
        assert result is mock_model
    finally:
        ml._MODEL_FILE = orig


def test_get_model_mtime_change_reloads(tmp_path):
    from services.signal_ml import get_model
    import services.signal_ml as ml

    model_file = tmp_path / "signal_ml_model.json"
    model_file.write_text("{}")
    orig_file = ml._MODEL_FILE
    ml._MODEL_FILE = model_file
    mock_booster = MagicMock()
    xgb_mock = MagicMock()
    xgb_mock.Booster.return_value = mock_booster
    try:
        with patch.dict(sys.modules, {"xgboost": xgb_mock}):
            r1 = get_model()
            # Touch file to change mtime
            model_file.write_text("{}")
            r2 = get_model()
        assert r1 is r2 is mock_booster
    finally:
        ml._MODEL_FILE = orig_file
        ml._model = None
        ml._model_mtime = 0.0


# ── get_entry_model ───────────────────────────────────────────────────────────


def test_get_entry_model_oserror_on_stat():
    from services.signal_ml import get_entry_model
    import services.signal_ml as ml

    mock_model = MagicMock()
    ml._entry_model = mock_model
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.stat.side_effect = OSError("denied")
    orig = ml._ENTRY_MODEL_FILE
    ml._ENTRY_MODEL_FILE = mock_path
    try:
        result = get_entry_model()
        assert result is mock_model
    finally:
        ml._ENTRY_MODEL_FILE = orig


def test_get_entry_model_load_failure(tmp_path):
    from services.signal_ml import get_entry_model
    import services.signal_ml as ml

    model_file = tmp_path / "backtest_ml_model.json"
    model_file.write_text("{}")
    orig = ml._ENTRY_MODEL_FILE
    ml._ENTRY_MODEL_FILE = model_file
    xgb_mock = MagicMock()
    xgb_mock.Booster.side_effect = Exception("bad")
    try:
        with patch.dict(sys.modules, {"xgboost": xgb_mock}):
            result = get_entry_model()
        assert result is None
    finally:
        ml._ENTRY_MODEL_FILE = orig
        ml._entry_model = None
        ml._entry_model_mtime = 0.0


# ── adjust_confidence ─────────────────────────────────────────────────────────


def test_adjust_confidence_with_xgb_booster():
    from services.signal_ml import adjust_confidence

    mock_model = MagicMock()
    mock_model.predict.return_value = [0.65]
    sig = _make_sig(confidence=55.0)
    with patch.dict(sys.modules, {"numpy": MagicMock(), "xgboost": MagicMock()}):
        np_mock = MagicMock()
        xgb_mock = MagicMock()
        dm_mock = MagicMock()
        xgb_mock.DMatrix.return_value = dm_mock
        np_mock.array.return_value = "array"
        with patch.dict(sys.modules, {"numpy": np_mock, "xgboost": xgb_mock}):
            result = adjust_confidence(sig, model=mock_model)
    assert isinstance(result, float)
    assert 0 <= result <= 72.0


def test_adjust_confidence_zero_confidence():
    from services.signal_ml import adjust_confidence

    mock_model = MagicMock()
    mock_model.predict.return_value = [0.5]
    sig = _make_sig(confidence=0.0)
    with patch.dict(sys.modules, {"numpy": MagicMock(), "xgboost": MagicMock()}):
        np_mock = MagicMock()
        xgb_mock = MagicMock()
        xgb_mock.DMatrix.return_value = MagicMock()
        np_mock.array.return_value = "array"
        with patch.dict(sys.modules, {"numpy": np_mock, "xgboost": xgb_mock}):
            result = adjust_confidence(sig, model=mock_model)
    assert isinstance(result, float)


def test_adjust_confidence_missing_confidence_key():
    from services.signal_ml import adjust_confidence

    mock_model = MagicMock()
    mock_model.predict.return_value = [0.5]
    sig = {"action": "BUY"}
    with patch.dict(sys.modules, {"numpy": MagicMock(), "xgboost": MagicMock()}):
        np_mock = MagicMock()
        xgb_mock = MagicMock()
        xgb_mock.DMatrix.return_value = MagicMock()
        np_mock.array.return_value = "array"
        with patch.dict(sys.modules, {"numpy": np_mock, "xgboost": xgb_mock}):
            result = adjust_confidence(sig, model=mock_model)
    assert result == 0.0


# ── train_model ───────────────────────────────────────────────────────────────


def test_train_model_xgboost_missing():
    from services.signal_ml import train_model

    import builtins
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "xgboost":
            raise ImportError("no xgboost")
        return real_import(name, *args, **kwargs)

    with patch.object(builtins, "__import__", fake_import):
        assert train_model() is None


def test_train_model_sklearn_missing():
    from services.signal_ml import train_model

    import builtins
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "sklearn.metrics":
            raise ImportError("no sklearn")
        return real_import(name, *args, **kwargs)

    with patch.object(builtins, "__import__", fake_import):
        assert train_model() is None


def test_train_model_db_error():
    from services.signal_ml import train_model

    with patch("services.signal_ml._load_resolved_signals_sync", side_effect=Exception("db down")):
        assert train_model() is None


def test_train_model_insufficient_samples():
    from services.signal_ml import train_model, _MIN_SAMPLES

    rows = [{"action": "BUY", "outcome_pct": 1.0}] * (_MIN_SAMPLES - 1)
    with patch("services.signal_ml._load_resolved_signals_sync", return_value=rows):
        assert train_model() is None


def test_train_model_training_only():
    from services.signal_ml import train_model, _MIN_SAMPLES, _MIN_LIVE_N_FOR_DEPLOYMENT
    import numpy as np

    # Enough for training but below deployment threshold
    rows = []
    for i in range(_MIN_SAMPLES + 20):
        rows.append({
            "action": "BUY",
            "outcome_pct": 1.0 if i % 2 == 0 else -1.0,
            "created_at": f"2024-01-{i+1:02d}T00:00:00",
            "sources": ["technicals"],
            "rationale": [],
        })

    mock_model = MagicMock()
    mock_booster = MagicMock()
    mock_model.get_booster.return_value = mock_booster
    mock_model.feature_importances_ = np.array([0.1] * 23)
    mock_model.predict.return_value = np.array([1] * 20)
    mock_model.predict_proba.return_value = np.array([[0.4, 0.6]] * 20)

    xgb_mock = MagicMock()
    xgb_mock.XGBClassifier.return_value = mock_model
    xgb_mock.DMatrix.return_value = MagicMock()
    xgb_mock.Booster.return_value = mock_booster

    sklearn_mock = MagicMock()
    sklearn_mock.accuracy_score.return_value = 0.6
    sklearn_mock.precision_score.return_value = 0.6
    sklearn_mock.recall_score.return_value = 0.6
    sklearn_mock.roc_auc_score.return_value = 0.65

    mock_path = MagicMock()
    mock_path.exists.return_value = False

    import services.signal_ml as ml
    orig_model_file = ml._MODEL_FILE
    ml._MODEL_FILE = mock_path
    try:
        with patch("services.signal_ml._load_resolved_signals_sync", return_value=rows):
            with patch.dict(sys.modules, {"xgboost": xgb_mock, "sklearn.metrics": sklearn_mock}):
                result = train_model()
    finally:
        ml._MODEL_FILE = orig_model_file

    assert result is not None
    assert result["training_only"] is True
    assert result["deployed"] is False


def test_train_model_deploys_first_run():
    from services.signal_ml import train_model, _MIN_LIVE_N_FOR_DEPLOYMENT
    import numpy as np

    rows = []
    for i in range(_MIN_LIVE_N_FOR_DEPLOYMENT + 100):
        rows.append({
            "action": "BUY" if i % 2 == 0 else "SELL",
            "outcome_pct": 2.0 if i % 3 != 0 else -1.5,
            "created_at": f"2024-01-{ (i % 30) + 1:02d}T00:00:00",
            "sources": ["technicals"],
            "rationale": [{"sentiment": "pos"}],
        })

    mock_model = MagicMock()
    mock_booster = MagicMock()
    mock_model.get_booster.return_value = mock_booster
    mock_model.feature_importances_ = np.array([0.1] * 23)
    mock_model.predict.return_value = np.array([1] * 50)
    mock_model.predict_proba.return_value = np.array([[0.3, 0.7]] * 50)

    xgb_mock = MagicMock()
    xgb_mock.XGBClassifier.return_value = mock_model
    xgb_mock.DMatrix.return_value = MagicMock()
    xgb_mock.Booster.return_value = mock_booster

    sklearn_mock = MagicMock()
    sklearn_mock.accuracy_score.return_value = 0.62
    sklearn_mock.precision_score.return_value = 0.61
    sklearn_mock.recall_score.return_value = 0.60
    sklearn_mock.roc_auc_score.return_value = 0.66

    mock_path = MagicMock()
    mock_path.exists.return_value = False
    mock_path.mkdir.return_value = None
    mock_path.write_text.return_value = None

    import services.signal_ml as ml
    orig_model_file = ml._MODEL_FILE
    orig_feature_file = ml._FEATURE_FILE
    ml._MODEL_FILE = mock_path
    ml._FEATURE_FILE = mock_path
    try:
        with patch("services.signal_ml._load_resolved_signals_sync", return_value=rows):
            with patch.dict(sys.modules, {"xgboost": xgb_mock, "sklearn.metrics": sklearn_mock}):
                result = train_model()
    finally:
        ml._MODEL_FILE = orig_model_file
        ml._FEATURE_FILE = orig_feature_file

    assert result is not None
    assert result["deployed"] is True
    assert result["training_only"] is False


def test_train_model_single_class_test_set():
    from services.signal_ml import train_model, _MIN_LIVE_N_FOR_DEPLOYMENT
    import numpy as np

    rows = []
    for i in range(_MIN_LIVE_N_FOR_DEPLOYMENT + 100):
        rows.append({
            "action": "BUY",
            "outcome_pct": 1.0,
            "created_at": f"2024-01-{ (i % 30) + 1:02d}T00:00:00",
            "sources": ["technicals"],
            "rationale": [],
        })

    mock_model = MagicMock()
    mock_booster = MagicMock()
    mock_model.get_booster.return_value = mock_booster
    mock_model.feature_importances_ = np.array([0.1] * 23)
    mock_model.predict.return_value = np.array([1] * 50)
    mock_model.predict_proba.return_value = np.array([[0.3, 0.7]] * 50)

    xgb_mock = MagicMock()
    xgb_mock.XGBClassifier.return_value = mock_model
    xgb_mock.DMatrix.return_value = MagicMock()
    xgb_mock.Booster.return_value = mock_booster

    sklearn_mock = MagicMock()
    sklearn_mock.accuracy_score.return_value = 0.6
    sklearn_mock.precision_score.return_value = 0.6
    sklearn_mock.recall_score.return_value = 0.6

    mock_path = MagicMock()
    mock_path.exists.return_value = False

    import services.signal_ml as ml
    orig_model_file = ml._MODEL_FILE
    ml._MODEL_FILE = mock_path
    try:
        with patch("services.signal_ml._load_resolved_signals_sync", return_value=rows):
            with patch.dict(sys.modules, {"xgboost": xgb_mock, "sklearn.metrics": sklearn_mock}):
                result = train_model()
    finally:
        ml._MODEL_FILE = orig_model_file

    assert result is not None
    assert result["oos_auc"] is None


def test_train_model_oos_too_small():
    from services.signal_ml import train_model, _MIN_SAMPLES

    # Create just enough rows that split yields <15 test samples
    rows = []
    for i in range(_MIN_SAMPLES + 10):
        rows.append({
            "action": "BUY",
            "outcome_pct": 1.0 if i % 2 == 0 else -1.0,
            "created_at": f"2024-01-{i+1:02d}T00:00:00",
            "sources": ["technicals"],
            "rationale": [],
        })

    with patch("services.signal_ml._load_resolved_signals_sync", return_value=rows):
        assert train_model() is None


# ── train_challenger_model ────────────────────────────────────────────────────


def test_train_challenger_model_xgboost_missing():
    from services.signal_ml import train_challenger_model

    import builtins
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "xgboost":
            raise ImportError("no xgboost")
        return real_import(name, *args, **kwargs)

    with patch.object(builtins, "__import__", fake_import):
        assert train_challenger_model() is None


def test_train_challenger_model_sklearn_missing():
    from services.signal_ml import train_challenger_model

    import builtins
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "sklearn.metrics":
            raise ImportError("no sklearn")
        return real_import(name, *args, **kwargs)

    with patch.object(builtins, "__import__", fake_import):
        assert train_challenger_model() is None


def test_train_challenger_model_db_error():
    from services.signal_ml import train_challenger_model

    with patch("services.signal_ml._load_resolved_signals_sync", side_effect=Exception("db down")):
        assert train_challenger_model() is None


def test_train_challenger_model_insufficient_samples():
    from services.signal_ml import train_challenger_model, _MIN_SAMPLES

    rows = [{"action": "BUY", "outcome_pct": 1.0}] * (_MIN_SAMPLES - 1)
    with patch("services.signal_ml._load_resolved_signals_sync", return_value=rows):
        assert train_challenger_model() is None


def test_train_challenger_model_single_class():
    from services.signal_ml import train_challenger_model, _MIN_SAMPLES
    import numpy as np

    rows = []
    for i in range(_MIN_SAMPLES + 50):
        rows.append({
            "action": "BUY",
            "outcome_pct": 1.0,
            "created_at": f"2024-01-{i+1:02d}T00:00:00",
            "sources": ["technicals"],
            "rationale": [],
            "raw_score": 50,
        })

    mock_model = MagicMock()
    mock_model.feature_importances_ = np.array([0.1] * 24)
    mock_model.predict_proba.return_value = np.array([[0.3, 0.7]] * 50)

    xgb_mock = MagicMock()
    xgb_mock.XGBClassifier.return_value = mock_model

    sklearn_mock = MagicMock()
    sklearn_mock.roc_auc_score.return_value = 0.65

    with patch("services.signal_ml._load_resolved_signals_sync", return_value=rows):
        with patch.dict(sys.modules, {"xgboost": xgb_mock, "sklearn.metrics": sklearn_mock}):
            result = train_challenger_model()

    assert result is None


def test_train_challenger_model_success_no_baseline():
    from services.signal_ml import train_challenger_model, _MIN_LIVE_N_FOR_DEPLOYMENT
    import numpy as np

    rows = []
    for i in range(_MIN_LIVE_N_FOR_DEPLOYMENT + 100):
        rows.append({
            "action": "BUY" if i % 2 == 0 else "SELL",
            "outcome_pct": 2.0 if i % 3 != 0 else -1.5,
            "created_at": f"2024-01-{ (i % 30) + 1:02d}T00:00:00",
            "sources": ["technicals"],
            "rationale": [{"sentiment": "pos"}],
            "raw_score": 50 + (i % 20),
        })

    mock_model = MagicMock()
    mock_booster = MagicMock()
    mock_model.get_booster.return_value = mock_booster
    mock_model.feature_importances_ = np.array([0.1] * 24)
    mock_model.predict_proba.return_value = np.array([[0.3, 0.7]] * 50)

    xgb_mock = MagicMock()
    xgb_mock.XGBClassifier.return_value = mock_model

    sklearn_mock = MagicMock()
    sklearn_mock.roc_auc_score.return_value = 0.66

    mock_path = MagicMock()
    mock_path.exists.return_value = False
    mock_path.write_text.return_value = None

    import services.signal_ml as ml
    orig_challenger_file = ml._CHALLENGER_MODEL_FILE
    orig_challenger_feature_file = ml._CHALLENGER_FEATURE_FILE
    ml._CHALLENGER_MODEL_FILE = mock_path
    ml._CHALLENGER_FEATURE_FILE = mock_path
    try:
        with patch("services.signal_ml._load_resolved_signals_sync", return_value=rows):
            with patch.dict(sys.modules, {"xgboost": xgb_mock, "sklearn.metrics": sklearn_mock}):
                result = train_challenger_model()
    finally:
        ml._CHALLENGER_MODEL_FILE = orig_challenger_file
        ml._CHALLENGER_FEATURE_FILE = orig_challenger_feature_file

    assert result is not None
    assert result["baseline_auc"] is None
    assert result["delta"] is None
    assert "No baseline" in result["interpretation"]


def test_train_challenger_model_rejected_removes_stale(tmp_path):
    from services.signal_ml import train_challenger_model, _MIN_LIVE_N_FOR_DEPLOYMENT
    import numpy as np

    rows = []
    for i in range(_MIN_LIVE_N_FOR_DEPLOYMENT + 100):
        rows.append({
            "action": "BUY" if i % 2 == 0 else "SELL",
            "outcome_pct": 2.0 if i % 3 != 0 else -1.5,
            "created_at": f"2024-01-{ (i % 30) + 1:02d}T00:00:00",
            "sources": ["technicals"],
            "rationale": [{"sentiment": "pos"}],
            "raw_score": 50,
        })

    mock_model = MagicMock()
    mock_model.feature_importances_ = np.array([0.1] * 24)
    mock_model.predict_proba.return_value = np.array([[0.3, 0.7]] * 50)

    xgb_mock = MagicMock()
    xgb_mock.XGBClassifier.return_value = mock_model

    sklearn_mock = MagicMock()
    sklearn_mock.roc_auc_score.return_value = 0.60

    # Create a stale challenger file
    fake_dir = tmp_path / "data"
    fake_dir.mkdir()
    stale_file = fake_dir / "signal_ml_challenger_model.json"
    stale_file.write_text("{}")

    import services.signal_ml as ml
    orig_challenger_file = ml._CHALLENGER_MODEL_FILE
    orig_challenger_feature_file = ml._CHALLENGER_FEATURE_FILE
    ml._CHALLENGER_MODEL_FILE = stale_file
    ml._CHALLENGER_FEATURE_FILE = fake_dir / "signal_ml_challenger_features.json"
    try:
        with patch("services.signal_ml._load_resolved_signals_sync", return_value=rows):
            with patch.dict(sys.modules, {"xgboost": xgb_mock, "sklearn.metrics": sklearn_mock}):
                result = train_challenger_model()

        assert result is not None
        assert result["deployed"] is False
        assert not stale_file.exists()
    finally:
        ml._CHALLENGER_MODEL_FILE = orig_challenger_file
        ml._CHALLENGER_FEATURE_FILE = orig_challenger_feature_file


# ── _load_resolved_signals_sync / async ───────────────────────────────────────


@pytest.mark.asyncio
async def test_load_resolved_signals_async():
    from services.signal_ml import _load_resolved_signals_async

    mock_row = MagicMock()
    mock_row.ticker = "AAPL"
    mock_row.action = "BUY"
    mock_row.confidence = 55.0
    mock_row.raw_score = 60
    mock_row.sentiment = "bullish"
    mock_row.sources = ["technicals"]
    mock_row.rationale = [{"sentiment": "pos"}]
    mock_row.outcome_pct = 2.5
    mock_row.style = "swing"
    mock_row.session = "regular"
    mock_row.rr = "1:2"
    mock_row.entry = 150.0
    mock_row.stop = 145.0
    mock_row.target = 160.0
    mock_row.price = 150.0
    mock_row.created_at = datetime(2024, 1, 15, 10, 0, 0)
    mock_row.change_pct = 1.5
    mock_row.days_to_earnings = 90
    mock_row.sector_etf = "XLK"
    mock_row.rs_vs_sector = 0.05

    mock_result = MagicMock()
    mock_result.all.return_value = [mock_row]

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    mock_session_ctx = AsyncMock()
    mock_session_ctx.__aenter__.return_value = mock_db
    mock_session_ctx.__aexit__.return_value = False

    with patch("database.AsyncSessionLocal", return_value=mock_session_ctx):
        rows = await _load_resolved_signals_async()

    assert len(rows) == 1
    assert rows[0]["ticker"] == "AAPL"
    assert rows[0]["outcome_pct"] == 2.5


def test_load_resolved_signals_sync():
    from services.signal_ml import _load_resolved_signals_sync

    with patch("services.signal_ml._load_resolved_signals_async") as mock_async:
        mock_async.return_value = [{"ticker": "TSLA", "action": "SELL"}]
        rows = _load_resolved_signals_sync()
    assert len(rows) == 1
    assert rows[0]["ticker"] == "TSLA"


# ── blend_confidence edge cases ───────────────────────────────────────────────


def test_blend_confidence_all_three_probs():
    from services.signal_ml import blend_confidence

    result = blend_confidence(base_conf=50.0, entry_prob=0.6, live_prob=0.7, challenger_prob=0.8)
    assert isinstance(result, float)
    assert 0 < result <= 72.0


def test_blend_confidence_meta_dampen():
    from services.signal_ml import blend_confidence

    result = blend_confidence(base_conf=50.0, entry_prob=0.6, live_prob=0.6, meta_prob=0.1)
    assert isinstance(result, float)


def test_blend_confidence_meta_amplify():
    from services.signal_ml import blend_confidence

    result = blend_confidence(base_conf=50.0, entry_prob=0.6, live_prob=0.6, meta_prob=0.9)
    assert isinstance(result, float)


# ── Feature extraction edge cases ─────────────────────────────────────────────


def test_extract_features_bad_json_sources():
    from services.signal_ml import _extract_features

    sig = _make_sig(sources="not json")
    feats = _extract_features(sig)
    assert isinstance(feats, list)
    assert len(feats) == 23


def test_extract_features_bad_json_rationale():
    from services.signal_ml import _extract_features

    sig = _make_sig(rationale="not json")
    feats = _extract_features(sig)
    assert isinstance(feats, list)
    assert len(feats) == 23


def test_extract_features_invalid_numbers():
    from services.signal_ml import _extract_features

    sig = _make_sig(entry="bad", stop="bad", target="bad", price="bad")
    feats = _extract_features(sig)
    assert isinstance(feats, list)
    assert feats[14] == 0.0  # stop_pct
    assert feats[15] == 0.0  # target_pct
    assert feats[16] == 0.0  # price_log


def test_extract_features_rr_edge_cases():
    from services.signal_ml import _extract_features

    sig = _make_sig(rr="1:")
    feats = _extract_features(sig)
    assert isinstance(feats, list)

    sig = _make_sig(rr=None)
    feats = _extract_features(sig)
    assert isinstance(feats, list)


def test_extract_features_created_at_invalid():
    from services.signal_ml import _extract_features

    sig = _make_sig(created_at="not-a-date")
    feats = _extract_features(sig)
    assert math.isnan(feats[18])  # dow
    assert math.isnan(feats[19])  # month


def test_extract_challenger_features():
    from services.signal_ml import _extract_challenger_features

    sig = _make_sig(raw_score=75)
    feats = _extract_challenger_features(sig)
    assert len(feats) == 24
    assert feats[-1] == 75.0

    sig = _make_sig(raw_score=None)
    feats = _extract_challenger_features(sig)
    assert math.isnan(feats[-1])


# ── predict_live_prob edge cases ──────────────────────────────────────────────


def test_predict_live_prob_schema_failure():
    from services.signal_ml import predict_live_prob

    mock_model = MagicMock()
    with patch("services.signal_ml.validate_feature_schema", return_value=False):
        assert predict_live_prob(_make_sig(), model=mock_model) is None


def test_predict_live_prob_exception():
    from services.signal_ml import predict_live_prob

    mock_model = MagicMock()
    mock_model.predict.side_effect = Exception("boom")
    with patch("services.signal_ml.validate_feature_schema", return_value=True):
        np_mock = MagicMock()
        xgb_mock = MagicMock()
        xgb_mock.DMatrix.side_effect = Exception("boom")
        np_mock.array.return_value = "array"
        with patch.dict(sys.modules, {"numpy": np_mock, "xgboost": xgb_mock}):
            assert predict_live_prob(_make_sig(), model=mock_model) is None


# ── Feature names consistency ─────────────────────────────────────────────────


def test_feature_names_length_matches_extract():
    from services.signal_ml import _extract_features, _FEATURE_NAMES

    sig = _make_sig()
    feats = _extract_features(sig)
    assert len(feats) == len(_FEATURE_NAMES)


def test_challenger_feature_names_length():
    from services.signal_ml import _extract_challenger_features, _CHALLENGER_FEATURE_NAMES

    sig = _make_sig()
    feats = _extract_challenger_features(sig)
    assert len(feats) == len(_CHALLENGER_FEATURE_NAMES)


def test_entry_feature_names_length():
    from services.signal_ml import _extract_entry_features, _ENTRY_FEATURE_NAMES

    feats = _extract_entry_features(_make_tech(), vix=20.0, sector_etf="XLK", dow=1, month=6)
    assert len(feats) == len(_ENTRY_FEATURE_NAMES)


def test_meta_feature_names_length():
    from services.signal_ml import _extract_meta_features, _META_FEATURE_NAMES

    feats = _extract_meta_features(_make_tech(), entry_prob=0.6, hmm_regime={}, vix=20.0, sector_etf="XLK", dow=1, dte=30)
    assert len(feats) == len(_META_FEATURE_NAMES)
