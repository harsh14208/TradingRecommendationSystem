import pytest
import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.calibration import _blend, apply_calibration


def test_blend():
    # Under minimum requirements returns 0
    assert _blend(2) == 0.0

    # Reaches 50% blend at 10 items (min(0.90, 10/20) = 0.50), N_FULL=20, MAX_BLEND=0.90
    assert _blend(10) == pytest.approx(0.50)

    # Caps at 90% weight regardless of high numbers
    assert _blend(20) == 0.90
    assert _blend(50) == 0.90

def test_apply_calibration():
    cal_map = {
        "60": {"win_rate": 0.50, "n": 30, "blend": 0.8}
    }
    # raw_conf = 62 -> falls into bin 60 -> emp_wr = 50%, blend 0.8
    # math: 50*0.8 + 62*0.2 = 40 + 12.4 = 52.4
    conf, entry = apply_calibration(62.0, "BUY", cal_map)
    assert conf == 52.4
    assert entry is not None
    assert entry["n"] == 30

def test_apply_calibration_no_map():
    conf, entry = apply_calibration(62.0, "BUY", {})
    assert conf == 62.0
    assert entry is None