import os
import sys

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.calibration import _MAX_BLEND, _N_FULL, _blend, apply_calibration


def test_blend():
    # Under minimum requirements returns 0
    assert _blend(2) == 0.0

    # At _N_FULL samples reaches _MAX_BLEND
    assert _blend(_N_FULL) == pytest.approx(_MAX_BLEND)

    # Caps at _MAX_BLEND regardless of higher counts
    assert _blend(_N_FULL * 2) == pytest.approx(_MAX_BLEND)
    assert _blend(1000) == pytest.approx(_MAX_BLEND)


def test_apply_calibration():
    cal_map = {"60": {"win_rate": 0.50, "n": 30, "blend": 0.8}}
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
