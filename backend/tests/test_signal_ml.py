import pytest
import math
from unittest.mock import patch, MagicMock
from services.signal_ml import _extract_features, adjust_confidence, train_model

def test_extract_features():
    sig = {
        "confidence": 75.0,
        "sentiment": 0.5,
        "sources": ["Options", "Macro"],
        "rationale": [
            {"sentiment": "pos"},
            {"sentiment": "pos"},
            {"sentiment": "neg"}
        ],
        "rr": "1:2.5",
        "action": "BUY",
        "session": "pre",
        "style": "swing",
        "entry": 100.0,
        "stop": 95.0,
        "target": 110.0,
        "price": 100.0
    }
    
    features = _extract_features(sig)
    
    assert len(features) == 20
    assert features[0] == 75.0  # confidence
    assert features[1] == 0.5   # sentiment
    assert features[2] == 2     # n_sources
    assert features[3] == 3     # n_rationale
    assert features[4] == 2     # n_pos
    assert features[5] == 1     # n_neg
    assert features[6] == 2.5   # rr_numeric
    assert features[7] == 1     # is_buy
    assert features[8] == 1     # has_options
    assert features[9] == 0     # has_dark_pool
    assert features[10] == 0    # has_fundamentals
    assert features[11] == 0    # has_institutional
    assert features[12] == 1    # has_macro
    assert features[13] == 0    # has_earnings
    assert features[14] == 1    # is_pre_market
    assert features[15] == 0    # is_position_style
    assert features[16] == 5.0  # stop_pct (100-95)/100*100
    assert features[17] == 10.0 # target_pct (110-100)/100*100
    assert features[18] == math.log10(100.0) # price_log
    assert features[19] == 75   # confidence_bin

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
        # 60 * 1.25 = 75.0
        assert adj == 75.0

def test_adjust_confidence_none_model():
    sig = {"confidence": 60.0}
    # If the model is not trained yet (None), it should gracefully return the original confidence
    assert adjust_confidence(sig, None) == 60.0

@patch("services.signal_ml._load_resolved_signals_sync")
def test_train_model_insufficient_data(mock_load):
    # Mock out the DB load to return fewer than the 50 required samples
    mock_load.return_value = [{"action": "BUY", "outcome_pct": 1.5} for _ in range(10)]
    
    res = train_model()
    # Model training should skip and return None
    assert res is None