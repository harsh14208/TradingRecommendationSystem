"""
scripts/drift_detector.py

REF-2: Replay Engine Drift Detection.
Weekly automated validation comparing live database signals against replayed
decisions using point-in-time feature snapshots.

Two entry points:
  * ``detect_drift(...)`` — returns a result dict, raises nothing on drift.
    Safe to call in-process from the scheduled job in ``main.py``.
  * ``main()`` — CLI wrapper that prints a report and ``sys.exit``s 1 on drift.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
sys.path.insert(0, _PARENT)

from database import AsyncSessionLocal
from models import FeatureSnapshot, Signal
from services.delivery_gates import check_delivery_gates
from sqlalchemy import select


class MockSettings:
    min_confidence = 40.0  # Match v8.0 min_confidence configuration


async def _compare_signals(db, lookback_days: int, verbose: bool) -> dict:
    """Core drift comparison. Returns a result dict; never calls sys.exit."""
    cutoff = datetime.utcnow() - timedelta(days=lookback_days)

    stmt = select(Signal).where(Signal.created_at >= cutoff)
    res = await db.execute(stmt)
    signals = res.scalars().all()

    discrepancies: list[dict] = []
    matched_count = 0
    no_snapshot_count = 0

    for sig in signals:
        snap_stmt = select(FeatureSnapshot).where(FeatureSnapshot.signal_id == sig.id)
        snap_res = await db.execute(snap_stmt)
        snap = snap_res.scalars().first()

        if not snap:
            no_snapshot_count += 1
            if verbose:
                print(f"⚠️ Signal ID {sig.id} ({sig.ticker}): No matching FeatureSnapshot found. Cannot verify drift.")
            continue

        # Reconstruct signal dict from snapshot features
        replay_conf = snap.quality_score if snap.quality_score is not None else sig.confidence
        sig_dict = {
            "ticker": sig.ticker,
            "action": sig.action,
            "confidence": replay_conf,
            "style": sig.style or "swing",
            "rsi": snap.rsi,
            "bb_pct_b": snap.bb_pct_b,
            "ibs": snap.ibs,
            "vwap_pct": snap.vwap_pct,
            "atr_pct": snap.atr_pct,
            "zscore": snap.zscore,
            "sources": sig.sources or [],
            "entry": sig.entry,
            "target": sig.target,
            "stop": sig.stop,
        }
        if sig.extra_data:
            sig_dict.update(sig.extra_data)
        if snap.features:
            sig_dict["hasMr"] = snap.features.get("hasMr", True)
            for k in ["vix_term_ratio", "vix_9d_ratio", "sector_momentum"]:
                if k in snap.features and sig_dict.get(k) is None:
                    sig_dict[k] = snap.features[k]

        settings = MockSettings()
        skip_reason, _updated_sig = await check_delivery_gates(sig_dict, db, settings)

        replay_passed = skip_reason is None
        live_passed = sig.is_sent

        # Confidence drift only when both sides are numeric.
        conf_drift = (
            abs(replay_conf - sig.confidence) if replay_conf is not None and sig.confidence is not None else 0.0
        )

        has_drift = False
        desc = ""
        if replay_passed != live_passed:
            has_drift = True
            desc = (
                f"Decision discrepancy: Live Sent={live_passed} | "
                f"Replay Passed={replay_passed} (Skip reason: {skip_reason})"
            )
        elif conf_drift > 0.01:
            has_drift = True
            desc = f"Confidence discrepancy: Live Conf={sig.confidence:.2f}% | Replay Conf={replay_conf:.2f}%"

        if has_drift:
            discrepancies.append(
                {"signal_id": sig.id, "ticker": sig.ticker, "created_at": sig.created_at, "description": desc}
            )
            if verbose:
                print(f"❌ DRIFT DETECTED: Signal ID {sig.id} ({sig.ticker}) at {sig.created_at} | {desc}")
        else:
            matched_count += 1
            if verbose:
                print(f"✅ MATCHED: Signal ID {sig.id} ({sig.ticker}) matches replay engine perfectly.")

    return {
        "checked": len(signals),
        "matched": matched_count,
        "drifts": len(discrepancies),
        "no_snapshot": no_snapshot_count,
        "discrepancies": discrepancies,
    }


async def detect_drift(lookback_days: int = 7, db=None, verbose: bool = True) -> dict:
    """Compare live signals vs. replayed decisions over the last ``lookback_days``.

    Returns a result dict ``{checked, matched, drifts, no_snapshot, discrepancies}``.
    Pass an open ``db`` session to reuse one (tests); otherwise a session is opened.
    """
    if verbose:
        print("## REF-2: Replay Engine Drift Detection\n")
        print(f"Comparing live Signal records vs. Replay Engine over the last {lookback_days} days...\n")

    if db is not None:
        result = await _compare_signals(db, lookback_days, verbose)
    else:
        async with AsyncSessionLocal() as own_db:
            result = await _compare_signals(own_db, lookback_days, verbose)

    if verbose:
        if result["checked"] == 0:
            print("No Signal records found in the database for the lookback period.")
        print("\nDrift Detection Summary:")
        print(f"  Total signals checked: {result['checked']}")
        print(f"  Matched perfectly: {result['matched']}")
        print(f"  Drifts detected: {result['drifts']}")
        if result["drifts"]:
            print("\n🚨 WARNING: System logic or data drift detected! Check signal assembler and gate inputs.")
        else:
            print("\n🎉 SUCCESS: All replayed signals match live records. No drift detected.")

    return result


def main():
    result = asyncio.run(detect_drift())
    sys.exit(1 if result["drifts"] else 0)


if __name__ == "__main__":
    main()
