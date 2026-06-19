"""Unit tests for the Massive options flat-file → IV panel loader (no network/S3)."""

import datetime

import pandas as pd

import services.massive_options_data as m


def test_parse_opra_roundtrip():
    assert m._parse_opra("O:AAPL260116C00150000") == ("AAPL", datetime.date(2026, 1, 16), "C", 150.0)
    assert m._parse_opra("O:SPY240805P00500000") == ("SPY", datetime.date(2024, 8, 5), "P", 500.0)


def test_parse_opra_rejects_bad():
    assert m._parse_opra("AAPL") is None
    assert m._parse_opra("") is None
    assert m._parse_opra("O:AAPL260116X00150000") is None  # bad call/put flag


def test_bs_implied_vol_roundtrip():
    S, K, T, iv = 100.0, 100.0, 30 / 365, 0.25
    px = m._bs_price(S, K, T, iv, "C")
    assert abs(m._implied_vol(px, S, K, T, "C") - iv) < 1e-3
    # put–call: a put at the same strike must recover the same IV
    pput = m._bs_price(S, K, T, iv, "P")
    assert abs(m._implied_vol(pput, S, K, T, "P") - iv) < 1e-3


def test_implied_vol_below_intrinsic_is_nan():
    # price under intrinsic value cannot be inverted
    assert m._implied_vol(0.01, 100.0, 50.0, 30 / 365, "C") != m._implied_vol(0.01, 100.0, 50.0, 30 / 365, "C")


def test_summarize_recovers_flat_surface():
    S, T = 500.0, 30 / 365
    exp = datetime.date(2024, 9, 4)
    rows = []
    for k in range(440, 561, 10):
        for cp in ("C", "P"):
            rows.append(
                {
                    "root": "SPY",
                    "expiry": exp,
                    "cp": cp,
                    "strike": float(k),
                    "close": m._bs_price(S, float(k), T, 0.20, cp),
                    "volume": 100,
                }
            )
    out = m._summarize_underlying(pd.DataFrame(rows), S, datetime.date(2024, 8, 5))
    assert out["ticker"] == "SPY"
    assert abs(out["atm_iv_30d"] - 0.20) < 0.01  # recovered ATM IV
    assert abs(out["pc_iv_skew"]) < 0.02  # flat surface → ~0 skew
    assert out["total_opt_volume"] == 2600
