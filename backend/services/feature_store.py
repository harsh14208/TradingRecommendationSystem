"""
services/feature_store.py

QENG-2a: Point-in-time feature store.
Persists immutable feature snapshots and tracks dataset lineage.
"""

import hashlib
import json
import math
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from models import FeatureSnapshot, Instrument


def _safe_float(value) -> Optional[float]:
    """Coerce a feature value to a finite float, or None.

    Hot-scalar columns are populated straight from the (provider-supplied)
    feature dict. A stray string ("N/A"), None, or non-finite value would make
    a bare ``float(...)`` raise and abort the whole snapshot insert — the same
    persist-error class that NaN/Inf caused before ``_json_safe``. Null the
    column instead of crashing the scan.
    """
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _json_safe(value):
    """Recursively replace non-finite floats (NaN/Inf) with None.

    Postgres' json type rejects the bare NaN/Infinity tokens that Python's
    json.dumps emits, which otherwise crashes the feature-snapshot insert
    (and with it the whole scan persist step).
    """
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


async def get_or_create_instrument(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker, name=f"{ticker} Common Stock", asset_type="equity", currency="USD", is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def save_feature_snapshot(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0",
) -> FeatureSnapshot:
    """
    QENG-2a: Persist immutable feature snapshots keyed by ticker, observation time,
    effective time, provider timestamp, retrieval time, provider, adjusted/raw values,
    feature vector hash, and signal policy version.
    """
    inst = await get_or_create_instrument(db, ticker)

    # Sanitize NaN/Inf before anything touches the json column (Postgres rejects them).
    features = _json_safe(features)

    # Calculate feature vector hash
    features_json = json.dumps(features, sort_keys=True)
    vector_hash = hashlib.sha256(features_json.encode("utf-8")).hexdigest()

    # Extract hot scalars for indexing if present. _safe_float guarantees a
    # finite float or None so a malformed provider value can never abort the
    # snapshot insert (and with it the whole scan persist step).
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct")
    if atr_pct is None:
        atr_pct = features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = features.get("quality_score")
    if quality_score is None:
        quality_score = features.get("qualityScore")

    snapshot = FeatureSnapshot(
        instrument_id=inst.id,
        signal_id=signal_id,
        ts=ts,  # observation time
        rsi=_safe_float(rsi),
        bb_pct_b=_safe_float(bb_pct_b),
        ibs=_safe_float(ibs),
        vwap_pct=_safe_float(vwap_pct),
        atr_pct=_safe_float(atr_pct),
        zscore=_safe_float(zscore),
        quality_score=_safe_float(quality_score),
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version,
    )
    db.add(snapshot)
    await db.flush()
    return snapshot
