"""Confidence ontology invariants for the signal engine.

These tests encode the contract that:

- ``calibratedProbability`` is the calibrated probability of winning and is
  immutable after ``_assemble_signal()`` returns.
- ``displayConfidence`` is the user-facing confidence and may absorb
  portfolio-context tilts (peer confirmation, cross-sectional ranking).
- ``positionSizeScale`` absorbs risk/context adjustments (correlation,
  concentration, liquidity).
- ``rankScore`` / ``rankPercentile`` are display/order metadata only.
"""

from unittest.mock import AsyncMock, patch

import pytest

from services.engines.assembler import _assemble_signal
from services.gates.warning import apply_warning_deconfliction
from services.signal_engine import scan_all


def _minimal_assemble_inputs(score: float = 50.0, rationale: list | None = None) -> dict:
    return {
        "ticker": "AAPL",
        "info": {"company": "Apple Inc."},
        "tech": {"price": 100.0, "atr": 2.0, "rsi": 38.0, "bb_pct_b": 0.20, "ibs": 0.14},
        "score": score,
        "rationale": rationale or [{"head": "RSI Oversold", "sentiment": "pos", "src": "Technical"}],
        "sources": {"Technical"},
        "_force_hold": False,
        "_is_low_atr": False,
        "_atr_pct_pre": 0.02,
        "total_confidence_penalty": 0.0,
        "avg_sent": 0.5,
        "price": 100.0,
        "atr": 2.0,
        "market_ctx": {"macro": {"sp500_trend": "up"}},
        "earnings_cal": {},
        "sector_rs": None,
        "days_to_earnings": 15,
    }


def test_assembler_emits_ontology_fields():
    sig = _assemble_signal(**_minimal_assemble_inputs())
    assert sig is not None
    assert "alphaScore" in sig
    assert "rawConfidence" in sig
    assert "calibratedProbability" in sig
    assert "displayConfidence" in sig
    assert "rankScore" in sig
    assert "rankPercentile" in sig
    # Backward-compatible alias preserved.
    assert sig["confidence"] == sig["displayConfidence"]


def test_calibrated_probability_bounded():
    sig = _assemble_signal(**_minimal_assemble_inputs(score=90.0))
    assert sig is not None
    assert 35.0 <= sig["calibratedProbability"] <= 72.0
    assert 35.0 <= sig["displayConfidence"] <= 72.0


def test_hold_has_no_levels():
    sig = _assemble_signal(**_minimal_assemble_inputs(score=0.0, rationale=[]))
    assert sig is not None
    assert sig["action"] == "HOLD"
    assert sig["entry"] is None
    assert sig["stop"] is None
    assert sig["target"] is None


def test_no_nan_in_probability_fields():
    sig = _assemble_signal(**_minimal_assemble_inputs())
    assert sig is not None
    for key in ("alphaScore", "rawConfidence", "calibratedProbability", "displayConfidence"):
        value = sig[key]
        assert value == value, f"{key} is NaN"
        assert value != float("inf") and value != float("-inf"), f"{key} is Inf"


def test_warning_deconfliction_affects_raw_not_calibrated_separately():
    # A BUY with an overbought warning should lower rawConfidence; calibration
    # then maps that lowered raw value to calibratedProbability.
    rationale = [
        {"head": "RSI Oversold", "sentiment": "pos", "src": "Technical"},
        {"head": "RSI Overbought", "sentiment": "neg", "src": "Technical"},
    ]
    sig = _assemble_signal(**_minimal_assemble_inputs(score=55.0, rationale=rationale))
    assert sig is not None
    # rawConfidence absorbed the warning haircut.
    assert sig["rawConfidence"] < 72.0
    # calibratedProbability is bounded and derived from rawConfidence.
    assert 35.0 <= sig["calibratedProbability"] <= 72.0
    # displayConfidence starts equal to calibratedProbability.
    assert sig["displayConfidence"] == sig["calibratedProbability"]


def test_apply_warning_deconfliction_is_pure_function():
    rationale = [{"head": "RSI Overbought"}]
    out = apply_warning_deconfliction("BUY", 80.0, rationale)
    assert out == 73.6
    # Original rationale is not mutated.
    assert rationale == [{"head": "RSI Overbought"}]


@pytest.mark.asyncio
async def test_scan_all_post_scan_does_not_mutate_calibrated_probability():
    # Build ten directional signals so the cross-sectional ranking branch fires.
    tickers = [f"T{i}" for i in range(10)]
    signals = []
    for i, ticker in enumerate(tickers):
        conf = 55.0 + i * 1.5  # 55.0 .. 68.5
        signals.append(
            {
                "ticker": ticker,
                "action": "BUY",
                # Backward-compatible alias equals display confidence from assembler.
                "confidence": conf,
                "calibratedProbability": conf,
                "displayConfidence": conf,
                "positionSizeScale": 1.0,
                "sectorEtf": "XLK",
                "rationale": [],
                "sources": set(),
            }
        )

    with patch(
        "services.signal_engine.generate_signal",
        new=AsyncMock(side_effect=lambda ticker, **kwargs: signals[tickers.index(ticker)]),
    ):
        results = await scan_all(tickers)

    assert len(results) == 10
    for sig in results:
        # calibratedProbability must be exactly what _assemble_signal produced.
        expected_conf = 55.0 + tickers.index(sig["ticker"]) * 1.5
        assert sig["calibratedProbability"] == expected_conf
        # displayConfidence may have been tilted by ranking but stays bounded.
        assert 35.0 <= sig["displayConfidence"] <= 72.0
        # rank metadata was populated for the 10-signal universe.
        assert sig.get("rankPercentile") is not None
        assert sig.get("rankScore") is not None


@pytest.mark.asyncio
async def test_scan_all_peer_context_only_changes_display_confidence():
    # Three BUYs in the same sector; peer confirmation logic only changes
    # displayConfidence, not calibratedProbability.
    base_signal = {
        "ticker": "AAPL",
        "action": "BUY",
        "confidence": 60.0,
        "calibratedProbability": 60.0,
        "displayConfidence": 60.0,
        "positionSizeScale": 1.0,
        "sectorEtf": "XLK",
        "rationale": [],
        "sources": set(),
    }
    signals = [
        {**base_signal, "ticker": "AAPL"},
        {**base_signal, "ticker": "MSFT"},
        {**base_signal, "ticker": "NVDA"},
    ]

    with patch(
        "services.signal_engine.generate_signal",
        new=AsyncMock(side_effect=lambda ticker, **kwargs: signals[[s["ticker"] for s in signals].index(ticker)]),
    ):
        results = await scan_all(["AAPL", "MSFT", "NVDA"])

    for sig in results:
        assert sig["calibratedProbability"] == 60.0
