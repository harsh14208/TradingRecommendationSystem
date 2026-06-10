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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__json_safe__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__json_safe__mutmut)
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


def x__json_safe__mutmut_orig(value):
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


def x__json_safe__mutmut_1(value):
    """Recursively replace non-finite floats (NaN/Inf) with None.

    Postgres' json type rejects the bare NaN/Infinity tokens that Python's
    json.dumps emits, which otherwise crashes the feature-snapshot insert
    (and with it the whole scan persist step).
    """
    if isinstance(value, float):
        return value if math.isfinite(None) else None
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


def x__json_safe__mutmut_2(value):
    """Recursively replace non-finite floats (NaN/Inf) with None.

    Postgres' json type rejects the bare NaN/Infinity tokens that Python's
    json.dumps emits, which otherwise crashes the feature-snapshot insert
    (and with it the whole scan persist step).
    """
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {k: _json_safe(None) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


def x__json_safe__mutmut_3(value):
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
        return [_json_safe(None) for v in value]
    return value

mutants_x__json_safe__mutmut['_mutmut_orig'] = x__json_safe__mutmut_orig # type: ignore # mutmut generated
mutants_x__json_safe__mutmut['x__json_safe__mutmut_1'] = x__json_safe__mutmut_1 # type: ignore # mutmut generated
mutants_x__json_safe__mutmut['x__json_safe__mutmut_2'] = x__json_safe__mutmut_2 # type: ignore # mutmut generated
mutants_x__json_safe__mutmut['x__json_safe__mutmut_3'] = x__json_safe__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_or_create_instrument__mutmut)
async def get_or_create_instrument(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_orig(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_1(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = None
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_2(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(None)
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_3(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(None))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_4(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(None).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_5(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker != ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_6(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = None
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_7(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_8(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = None
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_9(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=None,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_10(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=None,
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_11(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type=None,
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_12(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency=None,
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_13(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=None
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_14(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_15(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_16(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_17(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_18(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_19(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="XXequityXX",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_20(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="EQUITY",
            currency="USD",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_21(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="XXUSDXX",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_22(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="usd",
            is_active=True
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_23(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=False
        )
        db.add(inst)
        await db.flush()
    return inst


async def x_get_or_create_instrument__mutmut_24(db, ticker: str) -> Instrument:
    """Helper to get or create an instrument master record."""
    res = await db.execute(select(Instrument).where(Instrument.ticker == ticker))
    inst = res.scalar_one_or_none()
    if not inst:
        inst = Instrument(
            ticker=ticker,
            name=f"{ticker} Common Stock",
            asset_type="equity",
            currency="USD",
            is_active=True
        )
        db.add(None)
        await db.flush()
    return inst

mutants_x_get_or_create_instrument__mutmut['_mutmut_orig'] = x_get_or_create_instrument__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_1'] = x_get_or_create_instrument__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_2'] = x_get_or_create_instrument__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_3'] = x_get_or_create_instrument__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_4'] = x_get_or_create_instrument__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_5'] = x_get_or_create_instrument__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_6'] = x_get_or_create_instrument__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_7'] = x_get_or_create_instrument__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_8'] = x_get_or_create_instrument__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_9'] = x_get_or_create_instrument__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_10'] = x_get_or_create_instrument__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_11'] = x_get_or_create_instrument__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_12'] = x_get_or_create_instrument__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_13'] = x_get_or_create_instrument__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_14'] = x_get_or_create_instrument__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_15'] = x_get_or_create_instrument__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_16'] = x_get_or_create_instrument__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_17'] = x_get_or_create_instrument__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_18'] = x_get_or_create_instrument__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_19'] = x_get_or_create_instrument__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_20'] = x_get_or_create_instrument__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_21'] = x_get_or_create_instrument__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_22'] = x_get_or_create_instrument__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_23'] = x_get_or_create_instrument__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_or_create_instrument__mutmut['x_get_or_create_instrument__mutmut_24'] = x_get_or_create_instrument__mutmut_24 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut: MutantDict = {}  # type: ignore

@_mutmut_mutated(mutants_x_save_feature_snapshot__mutmut)
async def save_feature_snapshot(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_orig(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_1(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "XXpolygonXX",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_2(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "POLYGON",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_3(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "XX1.0XX"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_4(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
) -> FeatureSnapshot:
    """
    QENG-2a: Persist immutable feature snapshots keyed by ticker, observation time,
    effective time, provider timestamp, retrieval time, provider, adjusted/raw values,
    feature vector hash, and signal policy version.
    """
    inst = None

    # Sanitize NaN/Inf before anything touches the json column (Postgres rejects them).
    features = _json_safe(features)

    # Calculate feature vector hash
    features_json = json.dumps(features, sort_keys=True)
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_5(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
) -> FeatureSnapshot:
    """
    QENG-2a: Persist immutable feature snapshots keyed by ticker, observation time,
    effective time, provider timestamp, retrieval time, provider, adjusted/raw values,
    feature vector hash, and signal policy version.
    """
    inst = await get_or_create_instrument(None, ticker)

    # Sanitize NaN/Inf before anything touches the json column (Postgres rejects them).
    features = _json_safe(features)

    # Calculate feature vector hash
    features_json = json.dumps(features, sort_keys=True)
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_6(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
) -> FeatureSnapshot:
    """
    QENG-2a: Persist immutable feature snapshots keyed by ticker, observation time,
    effective time, provider timestamp, retrieval time, provider, adjusted/raw values,
    feature vector hash, and signal policy version.
    """
    inst = await get_or_create_instrument(db, None)

    # Sanitize NaN/Inf before anything touches the json column (Postgres rejects them).
    features = _json_safe(features)

    # Calculate feature vector hash
    features_json = json.dumps(features, sort_keys=True)
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_7(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
) -> FeatureSnapshot:
    """
    QENG-2a: Persist immutable feature snapshots keyed by ticker, observation time,
    effective time, provider timestamp, retrieval time, provider, adjusted/raw values,
    feature vector hash, and signal policy version.
    """
    inst = await get_or_create_instrument(ticker)

    # Sanitize NaN/Inf before anything touches the json column (Postgres rejects them).
    features = _json_safe(features)

    # Calculate feature vector hash
    features_json = json.dumps(features, sort_keys=True)
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_8(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
) -> FeatureSnapshot:
    """
    QENG-2a: Persist immutable feature snapshots keyed by ticker, observation time,
    effective time, provider timestamp, retrieval time, provider, adjusted/raw values,
    feature vector hash, and signal policy version.
    """
    inst = await get_or_create_instrument(db, )

    # Sanitize NaN/Inf before anything touches the json column (Postgres rejects them).
    features = _json_safe(features)

    # Calculate feature vector hash
    features_json = json.dumps(features, sort_keys=True)
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_9(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
) -> FeatureSnapshot:
    """
    QENG-2a: Persist immutable feature snapshots keyed by ticker, observation time,
    effective time, provider timestamp, retrieval time, provider, adjusted/raw values,
    feature vector hash, and signal policy version.
    """
    inst = await get_or_create_instrument(db, ticker)

    # Sanitize NaN/Inf before anything touches the json column (Postgres rejects them).
    features = None

    # Calculate feature vector hash
    features_json = json.dumps(features, sort_keys=True)
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_10(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
) -> FeatureSnapshot:
    """
    QENG-2a: Persist immutable feature snapshots keyed by ticker, observation time,
    effective time, provider timestamp, retrieval time, provider, adjusted/raw values,
    feature vector hash, and signal policy version.
    """
    inst = await get_or_create_instrument(db, ticker)

    # Sanitize NaN/Inf before anything touches the json column (Postgres rejects them).
    features = _json_safe(None)

    # Calculate feature vector hash
    features_json = json.dumps(features, sort_keys=True)
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_11(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    features_json = None
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_12(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    features_json = json.dumps(None, sort_keys=True)
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_13(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    features_json = json.dumps(features, sort_keys=None)
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_14(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    features_json = json.dumps(sort_keys=True)
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_15(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    features_json = json.dumps(features, )
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_16(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    features_json = json.dumps(features, sort_keys=False)
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_17(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = None

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_18(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(None).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_19(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode(None)).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_20(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('XXutf-8XX')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_21(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('UTF-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_22(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = None
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_23(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get(None)
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_24(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("XXrsiXX")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_25(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("RSI")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_26(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = None
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_27(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get(None)
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_28(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("XXbb_pct_bXX")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_29(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("BB_PCT_B")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_30(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = None
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_31(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get(None)
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_32(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("XXibsXX")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_33(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("IBS")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_34(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = None
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_35(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get(None)
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_36(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("XXvwap_pctXX")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_37(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("VWAP_PCT")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_38(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = None
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_39(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") and features.get("atr_pct_rank")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_40(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get(None) or features.get("atr_pct_rank")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_41(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("XXatr_pctXX") or features.get("atr_pct_rank")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_42(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("ATR_PCT") or features.get("atr_pct_rank")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_43(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get(None)
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_44(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("XXatr_pct_rankXX")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_45(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("ATR_PCT_RANK")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_46(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = None
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_47(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get(None)
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_48(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("XXzscoreXX")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_49(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("ZSCORE")
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_50(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = None

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_51(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = features.get("quality_score") and features.get("qualityScore")

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_52(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = features.get(None) or features.get("qualityScore")

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_53(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = features.get("XXquality_scoreXX") or features.get("qualityScore")

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_54(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = features.get("QUALITY_SCORE") or features.get("qualityScore")

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_55(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = features.get("quality_score") or features.get(None)

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_56(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = features.get("quality_score") or features.get("XXqualityScoreXX")

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_57(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = features.get("quality_score") or features.get("qualityscore")

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_58(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = features.get("quality_score") or features.get("QUALITYSCORE")

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_59(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = features.get("quality_score") or features.get("qualityScore")

    snapshot = None
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_60(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = features.get("quality_score") or features.get("qualityScore")

    snapshot = FeatureSnapshot(
        instrument_id=None,
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_61(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_id=None,
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_62(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        ts=None,  # observation time
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_63(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        rsi=None,
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_64(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        bb_pct_b=None,
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_65(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        ibs=None,
        vwap_pct=float(vwap_pct) if vwap_pct is not None else None,
        atr_pct=float(atr_pct) if atr_pct is not None else None,
        zscore=float(zscore) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_66(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        vwap_pct=None,
        atr_pct=float(atr_pct) if atr_pct is not None else None,
        zscore=float(zscore) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_67(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        atr_pct=None,
        zscore=float(zscore) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_68(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        zscore=None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_69(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        quality_score=None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_70(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        features=None,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_71(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        effective_time=None,
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_72(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        provider_timestamp=None,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_73(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        provider=None,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_74(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        feature_vector_hash=None,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_75(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=None
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_76(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

    # Extract hot scalars for indexing if present
    rsi = features.get("rsi")
    bb_pct_b = features.get("bb_pct_b")
    ibs = features.get("ibs")
    vwap_pct = features.get("vwap_pct")
    atr_pct = features.get("atr_pct") or features.get("atr_pct_rank")
    zscore = features.get("zscore")
    quality_score = features.get("quality_score") or features.get("qualityScore")

    snapshot = FeatureSnapshot(
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_77(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_78(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_79(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_80(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_81(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        vwap_pct=float(vwap_pct) if vwap_pct is not None else None,
        atr_pct=float(atr_pct) if atr_pct is not None else None,
        zscore=float(zscore) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_82(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        atr_pct=float(atr_pct) if atr_pct is not None else None,
        zscore=float(zscore) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_83(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        zscore=float(zscore) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_84(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_85(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_86(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_87(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_88(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_89(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_90(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_91(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_92(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        rsi=float(None) if rsi is not None else None,
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_93(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        rsi=float(rsi) if rsi is None else None,
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_94(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        bb_pct_b=float(None) if bb_pct_b is not None else None,
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_95(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        bb_pct_b=float(bb_pct_b) if bb_pct_b is None else None,
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
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_96(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        ibs=float(None) if ibs is not None else None,
        vwap_pct=float(vwap_pct) if vwap_pct is not None else None,
        atr_pct=float(atr_pct) if atr_pct is not None else None,
        zscore=float(zscore) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_97(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        ibs=float(ibs) if ibs is None else None,
        vwap_pct=float(vwap_pct) if vwap_pct is not None else None,
        atr_pct=float(atr_pct) if atr_pct is not None else None,
        zscore=float(zscore) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_98(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        vwap_pct=float(None) if vwap_pct is not None else None,
        atr_pct=float(atr_pct) if atr_pct is not None else None,
        zscore=float(zscore) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_99(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        vwap_pct=float(vwap_pct) if vwap_pct is None else None,
        atr_pct=float(atr_pct) if atr_pct is not None else None,
        zscore=float(zscore) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_100(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        atr_pct=float(None) if atr_pct is not None else None,
        zscore=float(zscore) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_101(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        atr_pct=float(atr_pct) if atr_pct is None else None,
        zscore=float(zscore) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_102(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        zscore=float(None) if zscore is not None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_103(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        zscore=float(zscore) if zscore is None else None,
        quality_score=float(quality_score) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_104(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        quality_score=float(None) if quality_score is not None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_105(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        quality_score=float(quality_score) if quality_score is None else None,
        features=features,
        effective_time=effective_time or datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_106(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        effective_time=effective_time and datetime.now(),
        provider_timestamp=provider_timestamp or ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_107(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        provider_timestamp=provider_timestamp and ts,
        provider=provider,
        feature_vector_hash=vector_hash,
        signal_policy_version=signal_policy_version
    )
    db.add(snapshot)
    await db.flush()
    return snapshot

async def x_save_feature_snapshot__mutmut_108(
    db,
    ticker: str,
    ts: datetime,
    features: dict,
    signal_id: Optional[int] = None,
    effective_time: Optional[datetime] = None,
    provider_timestamp: Optional[datetime] = None,
    provider: str = "polygon",
    signal_policy_version: str = "1.0"
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
    vector_hash = hashlib.sha256(features_json.encode('utf-8')).hexdigest()

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
        signal_policy_version=signal_policy_version
    )
    db.add(None)
    await db.flush()
    return snapshot

mutants_x_save_feature_snapshot__mutmut['_mutmut_orig'] = x_save_feature_snapshot__mutmut_orig # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_1'] = x_save_feature_snapshot__mutmut_1 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_2'] = x_save_feature_snapshot__mutmut_2 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_3'] = x_save_feature_snapshot__mutmut_3 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_4'] = x_save_feature_snapshot__mutmut_4 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_5'] = x_save_feature_snapshot__mutmut_5 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_6'] = x_save_feature_snapshot__mutmut_6 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_7'] = x_save_feature_snapshot__mutmut_7 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_8'] = x_save_feature_snapshot__mutmut_8 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_9'] = x_save_feature_snapshot__mutmut_9 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_10'] = x_save_feature_snapshot__mutmut_10 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_11'] = x_save_feature_snapshot__mutmut_11 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_12'] = x_save_feature_snapshot__mutmut_12 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_13'] = x_save_feature_snapshot__mutmut_13 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_14'] = x_save_feature_snapshot__mutmut_14 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_15'] = x_save_feature_snapshot__mutmut_15 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_16'] = x_save_feature_snapshot__mutmut_16 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_17'] = x_save_feature_snapshot__mutmut_17 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_18'] = x_save_feature_snapshot__mutmut_18 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_19'] = x_save_feature_snapshot__mutmut_19 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_20'] = x_save_feature_snapshot__mutmut_20 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_21'] = x_save_feature_snapshot__mutmut_21 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_22'] = x_save_feature_snapshot__mutmut_22 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_23'] = x_save_feature_snapshot__mutmut_23 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_24'] = x_save_feature_snapshot__mutmut_24 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_25'] = x_save_feature_snapshot__mutmut_25 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_26'] = x_save_feature_snapshot__mutmut_26 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_27'] = x_save_feature_snapshot__mutmut_27 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_28'] = x_save_feature_snapshot__mutmut_28 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_29'] = x_save_feature_snapshot__mutmut_29 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_30'] = x_save_feature_snapshot__mutmut_30 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_31'] = x_save_feature_snapshot__mutmut_31 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_32'] = x_save_feature_snapshot__mutmut_32 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_33'] = x_save_feature_snapshot__mutmut_33 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_34'] = x_save_feature_snapshot__mutmut_34 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_35'] = x_save_feature_snapshot__mutmut_35 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_36'] = x_save_feature_snapshot__mutmut_36 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_37'] = x_save_feature_snapshot__mutmut_37 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_38'] = x_save_feature_snapshot__mutmut_38 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_39'] = x_save_feature_snapshot__mutmut_39 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_40'] = x_save_feature_snapshot__mutmut_40 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_41'] = x_save_feature_snapshot__mutmut_41 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_42'] = x_save_feature_snapshot__mutmut_42 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_43'] = x_save_feature_snapshot__mutmut_43 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_44'] = x_save_feature_snapshot__mutmut_44 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_45'] = x_save_feature_snapshot__mutmut_45 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_46'] = x_save_feature_snapshot__mutmut_46 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_47'] = x_save_feature_snapshot__mutmut_47 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_48'] = x_save_feature_snapshot__mutmut_48 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_49'] = x_save_feature_snapshot__mutmut_49 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_50'] = x_save_feature_snapshot__mutmut_50 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_51'] = x_save_feature_snapshot__mutmut_51 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_52'] = x_save_feature_snapshot__mutmut_52 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_53'] = x_save_feature_snapshot__mutmut_53 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_54'] = x_save_feature_snapshot__mutmut_54 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_55'] = x_save_feature_snapshot__mutmut_55 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_56'] = x_save_feature_snapshot__mutmut_56 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_57'] = x_save_feature_snapshot__mutmut_57 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_58'] = x_save_feature_snapshot__mutmut_58 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_59'] = x_save_feature_snapshot__mutmut_59 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_60'] = x_save_feature_snapshot__mutmut_60 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_61'] = x_save_feature_snapshot__mutmut_61 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_62'] = x_save_feature_snapshot__mutmut_62 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_63'] = x_save_feature_snapshot__mutmut_63 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_64'] = x_save_feature_snapshot__mutmut_64 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_65'] = x_save_feature_snapshot__mutmut_65 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_66'] = x_save_feature_snapshot__mutmut_66 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_67'] = x_save_feature_snapshot__mutmut_67 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_68'] = x_save_feature_snapshot__mutmut_68 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_69'] = x_save_feature_snapshot__mutmut_69 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_70'] = x_save_feature_snapshot__mutmut_70 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_71'] = x_save_feature_snapshot__mutmut_71 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_72'] = x_save_feature_snapshot__mutmut_72 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_73'] = x_save_feature_snapshot__mutmut_73 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_74'] = x_save_feature_snapshot__mutmut_74 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_75'] = x_save_feature_snapshot__mutmut_75 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_76'] = x_save_feature_snapshot__mutmut_76 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_77'] = x_save_feature_snapshot__mutmut_77 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_78'] = x_save_feature_snapshot__mutmut_78 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_79'] = x_save_feature_snapshot__mutmut_79 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_80'] = x_save_feature_snapshot__mutmut_80 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_81'] = x_save_feature_snapshot__mutmut_81 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_82'] = x_save_feature_snapshot__mutmut_82 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_83'] = x_save_feature_snapshot__mutmut_83 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_84'] = x_save_feature_snapshot__mutmut_84 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_85'] = x_save_feature_snapshot__mutmut_85 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_86'] = x_save_feature_snapshot__mutmut_86 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_87'] = x_save_feature_snapshot__mutmut_87 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_88'] = x_save_feature_snapshot__mutmut_88 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_89'] = x_save_feature_snapshot__mutmut_89 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_90'] = x_save_feature_snapshot__mutmut_90 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_91'] = x_save_feature_snapshot__mutmut_91 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_92'] = x_save_feature_snapshot__mutmut_92 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_93'] = x_save_feature_snapshot__mutmut_93 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_94'] = x_save_feature_snapshot__mutmut_94 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_95'] = x_save_feature_snapshot__mutmut_95 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_96'] = x_save_feature_snapshot__mutmut_96 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_97'] = x_save_feature_snapshot__mutmut_97 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_98'] = x_save_feature_snapshot__mutmut_98 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_99'] = x_save_feature_snapshot__mutmut_99 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_100'] = x_save_feature_snapshot__mutmut_100 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_101'] = x_save_feature_snapshot__mutmut_101 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_102'] = x_save_feature_snapshot__mutmut_102 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_103'] = x_save_feature_snapshot__mutmut_103 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_104'] = x_save_feature_snapshot__mutmut_104 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_105'] = x_save_feature_snapshot__mutmut_105 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_106'] = x_save_feature_snapshot__mutmut_106 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_107'] = x_save_feature_snapshot__mutmut_107 # type: ignore # mutmut generated
mutants_x_save_feature_snapshot__mutmut['x_save_feature_snapshot__mutmut_108'] = x_save_feature_snapshot__mutmut_108 # type: ignore # mutmut generated
