"""Unit tests for services/signal_ml.py — pure helper functions."""
import math
from unittest.mock import MagicMock



# ── _sector_ord ───────────────────────────────────────────────────────────────

def test_sector_ord_known():
    from services.signal_ml import _sector_ord
    result = _sector_ord("XLK")
    assert isinstance(result, float)
    assert not math.isnan(result)


def test_sector_ord_unknown():
    from services.signal_ml import _sector_ord
    result = _sector_ord("UNKNOWN")
    assert result == -1.0


def test_sector_ord_none():
    from services.signal_ml import _sector_ord
    result = _sector_ord(None)
    assert math.isnan(result)


def test_sector_ord_empty():
    from services.signal_ml import _sector_ord
    result = _sector_ord("")
    assert math.isnan(result)


def test_sector_ord_case_insensitive():
    from services.signal_ml import _sector_ord
    assert _sector_ord("xlk") == _sector_ord("XLK")


# ── _dte_bucket ───────────────────────────────────────────────────────────────

def test_dte_bucket_none():
    from services.signal_ml import _dte_bucket
    result = _dte_bucket(None)
    assert math.isnan(result)


def test_dte_bucket_blackout():
    from services.signal_ml import _dte_bucket
    assert _dte_bucket(0) == 0.0
    assert _dte_bucket(6) == 0.0


def test_dte_bucket_approaching():
    from services.signal_ml import _dte_bucket
    assert _dte_bucket(7) == 1.0
    assert _dte_bucket(34) == 1.0


def test_dte_bucket_post_earnings():
    from services.signal_ml import _dte_bucket
    assert _dte_bucket(35) == 2.0
    assert _dte_bucket(65) == 2.0


def test_dte_bucket_clean():
    from services.signal_ml import _dte_bucket
    assert _dte_bucket(66) == 3.0
    assert _dte_bucket(200) == 3.0


# ── _extract_features ────────────────────────────────────────────────────────

def _make_sig(**kwargs):
    defaults = {
        "ticker": "AAPL",
        "action": "BUY",
        "confidence": 55.0,
        "raw_score": 60,
        "atr_pct": 2.5,
        "rsi": 28.0,
        "bb_pct_b": 0.10,
        "ibs": 0.12,
        "volume_ratio": 1.4,
        "sector_etf": "XLK",
        "sources": ["technicals", "macro"],
        "rationale": [
            {"sentiment": "pos", "head": "RSI oversold"},
            {"sentiment": "neg", "head": "VIX elevated"},
        ],
        "rr": "1:2.0",
        "session": "regular",
        "dte_to_earnings": 90,
        "rs_vs_sector": 0.05,
        "spread_pct": 0.1,
    }
    defaults.update(kwargs)
    return defaults


def test_extract_features_returns_list():
    from services.signal_ml import _extract_features
    feats = _extract_features(_make_sig())
    assert isinstance(feats, list)
    assert len(feats) > 0
    assert all(isinstance(f, (float, int)) or (isinstance(f, float) and math.isnan(f)) for f in feats)


def test_extract_features_rr_parsing():
    from services.signal_ml import _extract_features
    f1 = _extract_features(_make_sig(rr="1:2.5"))
    f2 = _extract_features(_make_sig(rr="1.5"))
    f3 = _extract_features(_make_sig(rr=""))
    assert isinstance(f1, list)
    assert isinstance(f2, list)
    assert isinstance(f3, list)


def test_extract_features_string_sources():
    from services.signal_ml import _extract_features
    # sources as JSON string
    feats = _extract_features(_make_sig(sources='["technicals", "macro"]'))
    assert isinstance(feats, list)


def test_extract_features_string_rationale():
    from services.signal_ml import _extract_features
    feats = _extract_features(_make_sig(rationale='[{"sentiment": "pos", "head": "x"}]'))
    assert isinstance(feats, list)


def test_extract_features_sell_action():
    from services.signal_ml import _extract_features
    feats = _extract_features(_make_sig(action="SELL"))
    assert isinstance(feats, list)


def test_extract_features_missing_fields():
    from services.signal_ml import _extract_features
    # Minimal signal
    feats = _extract_features({"action": "BUY"})
    assert isinstance(feats, list)
    assert len(feats) > 0


# ── auc_ci_95 ─────────────────────────────────────────────────────────────────

def test_auc_ci_95_reasonable():
    from services.signal_ml import auc_ci_95
    lo, hi = auc_ci_95(auc=0.64, n_pos=100, n_neg=200)
    assert lo < 0.64 < hi
    assert 0.0 <= lo <= 1.0
    assert 0.0 <= hi <= 1.0


def test_auc_ci_95_perfect():
    from services.signal_ml import auc_ci_95
    lo, hi = auc_ci_95(auc=1.0, n_pos=100, n_neg=100)
    assert lo > 0.9


def test_auc_ci_95_small_n():
    from services.signal_ml import auc_ci_95
    lo, hi = auc_ci_95(auc=0.60, n_pos=10, n_neg=10)
    assert lo < hi


# ── blend_confidence ─────────────────────────────────────────────────────────

def test_blend_confidence_all_none():
    from services.signal_ml import blend_confidence
    result = blend_confidence(base_conf=55.0, entry_prob=None, live_prob=None)
    assert result == 55.0


def test_blend_confidence_entry_only():
    from services.signal_ml import blend_confidence
    result = blend_confidence(base_conf=55.0, entry_prob=0.65, live_prob=None)
    assert isinstance(result, float)
    assert 0 < result <= 72  # clamped to _MAX_CONFIDENCE (72.0)


def test_blend_confidence_both_probs():
    from services.signal_ml import blend_confidence
    result = blend_confidence(base_conf=55.0, entry_prob=0.65, live_prob=0.60)
    assert isinstance(result, float)
    assert result > 0


def test_blend_confidence_ratio_clamped_high():
    from services.signal_ml import blend_confidence
    # Very high prob → ratio clamped at 1.25, ceiling at _MAX_CONFIDENCE=72
    result = blend_confidence(base_conf=55.0, entry_prob=0.99, live_prob=0.99)
    assert result <= 72.0
    assert result >= 55.0  # should increase confidence


def test_blend_confidence_ratio_clamped_low():
    from services.signal_ml import blend_confidence
    # Very low prob → ratio clamped at 0.75
    result = blend_confidence(base_conf=55.0, entry_prob=0.01, live_prob=0.01)
    expected_min = round(55.0 * 0.75, 1)
    assert result >= expected_min - 0.2


def test_blend_confidence_with_meta_prob():
    from services.signal_ml import blend_confidence
    result = blend_confidence(base_conf=55.0, entry_prob=0.65, live_prob=0.60, meta_prob=0.8)
    assert isinstance(result, float)
    assert result > 0


def test_blend_confidence_with_challenger():
    from services.signal_ml import blend_confidence
    result = blend_confidence(
        base_conf=55.0, entry_prob=0.65, live_prob=0.60, challenger_prob=0.70
    )
    assert isinstance(result, float)


# ── get_model / load_model ────────────────────────────────────────────────────

def test_get_model_returns_none_when_no_model():
    from services.signal_ml import get_model
    import services.signal_ml as ml
    original = ml._model
    ml._model = None
    result = get_model()
    assert result is None
    ml._model = original


def test_get_entry_model_returns_none_when_file_absent():
    from services.signal_ml import get_entry_model
    import services.signal_ml as ml
    from pathlib import Path
    original_path = ml._ENTRY_MODEL_FILE
    ml._ENTRY_MODEL_FILE = Path("/nonexistent/path/entry_model.xgb")
    result = get_entry_model()
    assert result is None
    ml._ENTRY_MODEL_FILE = original_path


def test_get_challenger_model_returns_none():
    from services.signal_ml import get_challenger_model
    import services.signal_ml as ml
    original = ml._challenger_model
    ml._challenger_model = None
    result = get_challenger_model()
    assert result is None
    ml._challenger_model = original


# ── adjust_confidence ────────────────────────────────────────────────────────

def test_adjust_confidence_no_model():
    from services.signal_ml import adjust_confidence
    result = adjust_confidence(_make_sig(), model=None)
    assert isinstance(result, float)
    assert result == _make_sig()["confidence"]


def test_adjust_confidence_with_model():
    from services.signal_ml import adjust_confidence
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.35, 0.65]]
    result = adjust_confidence(_make_sig(), model=mock_model)
    assert isinstance(result, float)


def test_adjust_confidence_model_error():
    from services.signal_ml import adjust_confidence
    mock_model = MagicMock()
    mock_model.predict_proba.side_effect = Exception("model error")
    result = adjust_confidence(_make_sig(), model=mock_model)
    # Falls back to base confidence
    assert isinstance(result, float)


# ── predict_live_prob ────────────────────────────────────────────────────────

def test_predict_live_prob_no_model():
    from services.signal_ml import predict_live_prob
    result = predict_live_prob(_make_sig(), model=None)
    assert result is None


def test_predict_live_prob_with_model():
    from services.signal_ml import predict_live_prob
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.40, 0.60]]
    result = predict_live_prob(_make_sig(), model=mock_model)
    assert result is not None
    assert 0.0 <= result <= 1.0
