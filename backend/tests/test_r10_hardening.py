"""R10-18: regression tests for the two production bugs found in the
2026-06-08 server-log audit, plus the persist-path robustness they exposed.

These guard the exact failure modes that were green in the unit suite yet
broke in production:

  1. A NaN/Inf float reaching a Postgres ``json`` column crashed
     ``save_feature_snapshot`` and aborted the whole scan cycle.
  2. Duplicate ``(provider, endpoint)`` rows made ``scalar_one_or_none()``
     raise ``MultipleResultsFound`` on every reliability record.
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.feature_store import _json_safe, _safe_float, save_feature_snapshot


# ── Bug #1: NaN/Inf → json column ──────────────────────────────────────────


def test_json_safe_replaces_non_finite_recursively():
    src = {
        "rsi": float("nan"),
        "nested": {"a": float("inf"), "b": float("-inf"), "c": 1.5},
        "list": [1.0, float("nan"), "x", None],
        "ok": 42,
        "s": "hello",
    }
    out = _json_safe(src)

    # finite / non-float values preserved
    assert out["ok"] == 42
    assert out["s"] == "hello"
    assert out["nested"]["c"] == 1.5
    assert out["list"][0] == 1.0
    assert out["list"][2] == "x"
    assert out["list"][3] is None

    # non-finite floats nulled at every depth
    assert out["rsi"] is None
    assert out["nested"]["a"] is None
    assert out["nested"]["b"] is None
    assert out["list"][1] is None

    # serializable with NO NaN/Infinity tokens (Postgres json rejects them)
    dumped = json.dumps(out)
    assert "NaN" not in dumped
    assert "Infinity" not in dumped


def test_json_safe_handles_scalar_inputs():
    assert _json_safe(3.2) == 3.2
    assert _json_safe(float("nan")) is None
    assert _json_safe(float("inf")) is None
    assert _json_safe("x") == "x"
    assert _json_safe(None) is None
    assert _json_safe([float("inf")]) == [None]


@pytest.mark.asyncio
async def test_save_feature_snapshot_sanitizes_nan_before_storage():
    """The real sanitization wiring (not a mock of it): a NaN-laden feature
    dict must produce a finite, json-serializable snapshot — the exact case
    that crashed every live scan before the fix."""
    inst = MagicMock()
    inst.id = 7

    res = MagicMock()
    res.scalar_one_or_none.return_value = inst  # instrument already exists

    added = []
    db = MagicMock()
    db.execute = AsyncMock(return_value=res)
    db.flush = AsyncMock()
    db.add = MagicMock(side_effect=lambda obj: added.append(obj))

    features = {"rsi": float("nan"), "bb_pct_b": 0.1, "deep": {"x": float("inf")}}
    snap = await save_feature_snapshot(
        db=db,
        ticker="AAPL",
        ts=datetime.utcnow(),
        features=features,
    )

    # stored feature vector is finite and serializable (no NaN token)
    assert snap.features["rsi"] is None
    assert snap.features["deep"]["x"] is None
    assert snap.features["bb_pct_b"] == 0.1
    json.dumps(snap.features)  # must not raise

    # extracted hot scalar that was NaN is nulled, not NaN
    assert snap.rsi is None
    assert snap.bb_pct_b == 0.1

    # input dict was not mutated in place
    import math

    assert math.isnan(features["rsi"])


# ── R10-5: hot-scalar extraction must never raise on a malformed value ──────


def test_safe_float_coerces_or_nulls():
    assert _safe_float(1.5) == 1.5
    assert _safe_float("2.5") == 2.5  # numeric string coerced
    assert _safe_float(3) == 3.0
    # anything non-numeric / non-finite / None → None, never an exception
    assert _safe_float(None) is None
    assert _safe_float("N/A") is None
    assert _safe_float("") is None
    assert _safe_float(float("nan")) is None
    assert _safe_float(float("inf")) is None
    assert _safe_float([1, 2]) is None
    assert _safe_float({"a": 1}) is None


@pytest.mark.asyncio
async def test_save_feature_snapshot_tolerates_malformed_hot_scalars():
    """A provider value like "N/A" in a hot-scalar slot must null the indexed
    column rather than raise ``ValueError`` and abort the whole snapshot —
    the PIT feature-store persist-error class targeted by R10-5."""
    inst = MagicMock()
    inst.id = 11

    res = MagicMock()
    res.scalar_one_or_none.return_value = inst

    db = MagicMock()
    db.execute = AsyncMock(return_value=res)
    db.flush = AsyncMock()
    db.add = MagicMock()

    features = {
        "rsi": "N/A",  # malformed string
        "bb_pct_b": None,
        "ibs": 0.0,  # falsy-but-valid: must survive as 0.0, not be dropped
        "vwap_pct": "-0.8",  # numeric string
        "atr_pct": float("inf"),  # non-finite (already nulled by _json_safe)
        "quality_score": 0.0,  # falsy-but-valid; no fallthrough to qualityScore
    }
    snap = await save_feature_snapshot(db=db, ticker="MSFT", ts=datetime.utcnow(), features=features)

    assert snap.rsi is None  # "N/A" nulled, did not raise
    assert snap.bb_pct_b is None
    assert snap.ibs == 0.0  # falsy zero preserved
    assert snap.vwap_pct == -0.8  # numeric string coerced
    assert snap.atr_pct is None
    assert snap.quality_score == 0.0  # falsy zero preserved


# ── Bug #2: duplicate scorecard rows → MultipleResultsFound ─────────────────


def test_provider_scorecard_has_unique_constraint():
    """The uq_provider_endpoint constraint is what prevents the duplicate
    rows that broke every reliability record. Guard against its removal."""
    from sqlalchemy import UniqueConstraint

    from models import ProviderHealthScorecard

    unique_col_sets = {
        tuple(sorted(col.name for col in c.columns))
        for c in ProviderHealthScorecard.__table__.constraints
        if isinstance(c, UniqueConstraint)
    }
    assert ("endpoint", "provider") in unique_col_sets


@pytest.mark.asyncio
async def test_record_endpoint_call_tolerates_duplicate_rows():
    """If duplicate rows exist, the resilient ``.scalars().first()`` read must
    be used — ``scalar_one_or_none()`` would raise MultipleResultsFound."""
    from services.provider_reliability import record_endpoint_call

    scorecard = MagicMock()
    scorecard.latency_avg_ms = 100.0
    scorecard.error_rate = 0.0
    scorecard.stale_data_rate = 0.0
    scorecard.schema_drift_count = 0
    scorecard.health_score = 100.0
    scorecard.is_active = True

    res = MagicMock()
    res.scalars.return_value.first.return_value = scorecard
    res.scalar_one_or_none.side_effect = AssertionError(
        "must not call scalar_one_or_none — it raises on duplicate rows"
    )

    session = MagicMock()
    session.execute = AsyncMock(return_value=res)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    db = MagicMock()
    db.return_value.__aenter__.return_value = session
    db.return_value.__aexit__.return_value = None

    with patch("services.provider_reliability.AsyncSessionLocal", db):
        await record_endpoint_call("polygon", "/v2/aggs", 120.0, 200)

    session.commit.assert_called_once()
