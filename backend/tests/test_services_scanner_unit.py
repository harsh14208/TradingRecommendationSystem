import types
from datetime import datetime

import pytest

from services import scanner


def test_pct_buy_and_sell_sign_and_rounding():
    # BUY: positive when current > entry
    assert scanner._pct(current=110, entry=100, action="BUY") == 10.0

    # BUY: negative when current < entry
    assert scanner._pct(current=90, entry=100, action="BUY") == -10.0

    # SELL: sign inverted logic (SELL uses -raw)
    # raw = (current-entry)/entry*100 = 10.0, SELL should return -10.0
    assert scanner._pct(current=110, entry=100, action="SELL") == -10.0

    # None / invalid guards
    assert scanner._pct(current=0, entry=100, action="BUY") is None
    assert scanner._pct(current=110, entry=0, action="BUY") is None
    assert scanner._pct(current=None, entry=100, action="BUY") is None


def test_check_data_quality_counts_and_transition_alerts():
    # Provide a minimal "df" object with required shape:
    # - len(df) works
    # - df["Close"].iloc[-1] works
    class _SeriesLike:
        def __init__(self, last):
            self._last = last

        @property
        def iloc(self):
            class _ILoc:
                def __init__(self, last):
                    self._last = last

                def __getitem__(self, idx):
                    if idx == -1:
                        return self._last
                    raise IndexError

            return _ILoc(self._last)

    class _DFLike:
        def __init__(self, close_last, n=5):
            self._n = n
            self._close_last = close_last
            self._close_series = _SeriesLike(close_last)

        def __len__(self):
            return self._n

        def __getitem__(self, key):
            if key == "Close":
                return self._close_series
            raise KeyError(key)

    # Reset module state
    scanner._data_quality.clear()

    # 1) first 4 degraded -> no alert
    histories = {"AAPL": _DFLike(close_last=0, n=5)}
    alerts = []
    for _ in range(4):
        alerts = scanner._check_data_quality(histories, settings=types.SimpleNamespace())
        assert alerts == []

    # 2) 5th consecutive -> alert once
    alerts
