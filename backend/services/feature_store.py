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

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = features.get("quality_score") or features.get("qualityScore")

    snapshot = FeatureSnapshot(
        instrument_id=inst.id,
        signal_id=signal_id,
        ts=ts,  # observation time
        rsi=float(rsi) if rsi is not None else None,
        bb_pct_b=float(bb_pct_b) if bb_pct_b is not None else None,
        ibs=float(ibs) if ibs is not None else None,
        vwap_pct=float(vwap_pct) if vwap_pct is not None else None,
        atr_pct=float(atr_pct) if atr_pct is not None else None,
        zscore=float(zscore) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
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
