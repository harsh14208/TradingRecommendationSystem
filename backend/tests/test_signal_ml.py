import math
from unittest.mock import MagicMock, patch

from services.signal_ml import (
    _extract_entry_features,
    _extract_features,
    adjust_confidence,
    blend_confidence,
    predict_entry_prob,
    predict_live_prob,
    train_model,
)


def test_extract_features():
    sig = {
        "confidence": 75.0,
        "sentiment": 0.5,
        "sources": ["Options", "Macro"],
        "rationale": [{"sentiment": "pos"}, {"sentiment": "pos"}, {"sentiment": "neg"}],
        "rr": "1:2.5",
        "action": "BUY",
        "session": "pre",
        "style": "swing",
        "entry": 100.0,
        "stop": 95.0,
        "target": 110.0,
        "price": 100.0,
        "created_at": "2026-01-05 10:00:00",  # Monday, January
        "change_pct": -1.5,
        "days_to_earnings": 80,
        "sector_etf": "XLK",
        "rs_vs_sector": 0.03,
    }

    features = _extract_features(sig)

    # 23 features: confidence/sentiment removed (§ML-fix — they are Platt-scaled
    # outputs of this same model, not independent signals; feeding them back in
    # creates circular dependency that destroys probabilistic integrity).
    assert len(features) == 23
    assert features[0] == 2  # n_sources
    assert features[1] == 3  # n_rationale
    assert features[2] == 2  # n_pos
    assert features[3] == 1  # n_neg
    assert features[4] == 2.5  # rr_numeric
    assert features[5] == 1  # is_buy
    assert features[6] == 1  # has_options
    assert features[7] == 0  # has_dark_pool
    assert features[8] == 0  # has_fundamentals
    assert features[9] == 0  # has_institutional
    assert features[10] == 1  # has_macro
    assert features[11] == 0  # has_earnings
    assert features[12] == 1  # is_pre_market
    assert features[13] == 0  # is_position_style
    assert features[14] == 5.0  # stop_pct (100-95)/100*100
    assert features[15] == 10.0  # target_pct (110-100)/100*100
    assert features[16] == math.log10(100.0)  # price_log
    assert features[17] == -1.5  # change_pct
    assert features[18] == 0.0  # day_of_week (Monday = 0)
    assert features[19] == 1.0  # month (January)
    assert features[20] == 0.0  # sector_ord (XLK = 0)
    assert features[21] == 3.0  # dte_bucket (80d → bucket 3)
    assert features[22] == 0.03  # rs_vs_sector


def test_extract_features_sparse_nulls():
    """NaN returned for absent sparse fields — no KeyError or crash."""
    import math as _math

    sig = {
        "confidence": 58.0,
        "action": "BUY",
        "price": 50.0,
        "entry": 50.0,
        "stop": 47.0,
        "target": 56.0,
    }
    features = _extract_features(sig)
    assert len(features) == 23
    assert _math.isnan(features[18])  # dow — no created_at
    assert _math.isnan(features[20])  # sector_ord — None
    assert _math.isnan(features[21])  # dte_bucket — None
    assert _math.isnan(features[22])  # rs_vs_sector — None


def test_adjust_confidence():
    sig = {"confidence": 60.0}
    mock_model = MagicMock()
    # Predict returns a list/array with one element: [0.8] representing win_prob
    mock_model.predict.return_value = [0.8]

    mock_xgb = MagicMock()
    mock_np = MagicMock()
    mock_np.array.return_value = [[]]

    with patch.dict("sys.modules", {"xgboost": mock_xgb, "numpy": mock_np}):
        adj = adjust_confidence(sig, mock_model)
        # Math:
        # base_win_prob = 60 / 100 * 0.85 = 0.51
        # win_prob = 0.8
        # ratio = 0.8 / 0.51 = 1.568 (which gets clamped to 1.25 limit)
        # 60 * 1.25 = 75.0, capped by the empirical 72% ceiling
        assert adj == 72.0


def test_adjust_confidence_none_model():
    sig = {"confidence": 60.0}
    # If the model is not trained yet (None), it should gracefully return the original confidence
    assert adjust_confidence(sig, None) == 60.0


def test_extract_entry_features():
    """Entry feature vector is 14 elements with correct values."""
    tech = {
        "bb_pct_b": 0.15,
        "ibs": 0.20,
        "vwap_pct": -1.5,
        "rsi": 35.0,
        "adx": 22.0,
        "rvol": 1.8,
        "atr": 2.0,
        "price": 100.0,
        "price_zscore": -1.2,
        "ou_halflife": 8.0,
        "hurst": 0.45,
    }
    features = _extract_entry_features(tech, vix=18.5, sector_etf="XLK", dow=0, month=3)

    assert len(features) == 14
    assert features[0] == 0.15  # bb_pct_b
    assert features[1] == 0.20  # ibs
    assert features[2] == -1.5  # vwap_pct
    assert features[3] == 35.0  # rsi
    assert features[4] == 22.0  # adx
    assert features[5] == 1.8  # rvol
    assert features[6] == 2.0  # atr_pct = 2/100*100
    assert features[7] == -1.2  # price_zscore
    assert features[8] == 8.0  # ou_halflife
    assert features[9] == 0.45  # hurst
    assert features[10] == 18.5  # vix
    assert features[11] == 0.0  # sector_ord XLK=0
    assert features[12] == 0.0  # dow Monday=0
    assert features[13] == 3.0  # month March


def test_extract_entry_features_sparse_nulls():
    """NaN returned for absent tech fields and missing context — no crash."""
    tech = {"price": 50.0}  # no indicators
    features = _extract_entry_features(tech, vix=None, sector_etf=None, dow=None, month=None)

    assert len(features) == 14
    assert math.isnan(features[0])  # bb_pct_b missing
    assert math.isnan(features[2])  # vwap_pct missing
    assert math.isnan(features[10])  # vix None
    assert math.isnan(features[11])  # sector_ord None
    assert math.isnan(features[12])  # dow None
    assert math.isnan(features[13])  # month None
    # atr_pct = 0/50*100 = 0.0 (atr defaults to 0 when absent)
    assert features[6] == 0.0


def test_predict_live_prob_returns_float():
    mock_model = MagicMock()
    mock_model.predict.return_value = [0.72]
    mock_xgb = MagicMock()
    mock_np = MagicMock()
    mock_np.array.return_value = [[]]

    with patch.dict("sys.modules", {"xgboost": mock_xgb, "numpy": mock_np}):
        prob = predict_live_prob({"confidence": 60.0, "action": "BUY"}, mock_model)
    assert prob == 0.72


def test_predict_live_prob_none_model():
    assert predict_live_prob({"confidence": 60.0}, None) is None


def test_predict_entry_prob_none_model():
    assert predict_entry_prob({}, None, None, None) is None


def test_blend_confidence_both_probs():
    """50/50 blend of entry_prob=0.8 and live_prob=0.6 → combined=0.7."""
    # base=60%, combined=0.70
    # base_win_prob = 60/100*0.85 = 0.51
    # ratio = 0.70/0.51 = 1.373 → clamped to 1.25
    # 60 * 1.25 = 75 → capped at 72.0
    result = blend_confidence(60.0, entry_prob=0.8, live_prob=0.6)
    assert result == 72.0


def test_blend_confidence_only_entry():
    """Falls back to entry prob alone when live prob is None."""
    # entry_prob=0.4, live_prob=None → combined=0.4
    # base_win_prob = 60/100*0.85 = 0.51
    # ratio = 0.4/0.51 = 0.784 → clamped to 0.784 (within 0.75–1.25)
    # 60 * 0.784 = 47.1
    result = blend_confidence(60.0, entry_prob=0.4, live_prob=None)
    assert result == round(min(72.0, 60.0 * max(0.75, min(1.25, 0.4 / (0.51)))), 1)


def test_blend_confidence_both_none():
    """Returns base confidence unchanged when both probs are None."""
    assert blend_confidence(62.5, entry_prob=None, live_prob=None) == 62.5


@patch("services.signal_ml._load_resolved_signals_sync")
def test_train_model_insufficient_data(mock_load):
    # Mock out the DB load to return fewer than the 50 required samples
    mock_load.return_value = [{"action": "BUY", "outcome_pct": 1.5} for _ in range(10)]

    res = train_model()
    # Model training should skip and return None
    assert res is None
