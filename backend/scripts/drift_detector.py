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


# Skip reasons driven by CONFIG / POLICY / market-state toggles — i.e. NOT derivable
# from the point-in-time feature snapshot. When live and replay disagree because one
# of these changed between signal time and replay time (the long-only / SELL toggle,
# recalibrated confidence floors, blocked-ticker/sector lists, the VIX<15 or FOMC
# market-state gates, sector saturation), that is an INTENTIONAL policy change — not
# replay-engine drift — so it is tracked separately and does NOT trip the alarm.
# Snapshot-deterministic logic gates ("no MR setup", "not BUY/SELL", "profit < min")
# remain alarming because the replay should reproduce them exactly.
_POLICY_SKIP_PATTERNS = (
    "long-only",
    "delivery disabled",
    "style disabled",
    "blocked",
    "floor",
    "vix=",
    "fomc",
    "already has",
)


def _is_policy_skip(reason) -> bool:
    """True if a skip reason comes from a config/policy/market-state toggle rather
    than snapshot-deterministic logic."""
    if not reason:
        return False
    r = str(reason).lower()
    return any(p in r for p in _POLICY_SKIP_PATTERNS)


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
        kind = "logic"
        desc = ""
        if replay_passed != live_passed:
            has_drift = True
            # A live-vs-replay decision split is EXPECTED policy drift (not a bug) when
            # the replay skips for a config/policy/market-state reason that toggled since
            # the signal was sent (e.g. SELL → long-only). Everything else is logic drift.
            kind = "policy" if (not replay_passed and _is_policy_skip(skip_reason)) else "logic"
            desc = (
                f"Decision discrepancy: Live Sent={live_passed} | "
                f"Replay Passed={replay_passed} (Skip reason: {skip_reason})"
            )
        elif conf_drift > 0.01:
            has_drift = True
            kind = "logic"
            desc = f"Confidence discrepancy: Live Conf={sig.confidence:.2f}% | Replay Conf={replay_conf:.2f}%"

        if has_drift:
            discrepancies.append(
                {
                    "signal_id": sig.id,
                    "ticker": sig.ticker,
                    "created_at": sig.created_at,
                    "description": desc,
                    "kind": kind,
                }
            )
            if verbose:
                tag = "POLICY DRIFT (expected)" if kind == "policy" else "DRIFT DETECTED"
                print(f"❌ {tag}: Signal ID {sig.id} ({sig.ticker}) at {sig.created_at} | {desc}")
        else:
            matched_count += 1
            if verbose:
                print(f"✅ MATCHED: Signal ID {sig.id} ({sig.ticker}) matches replay engine perfectly.")

    logic_drifts = sum(1 for d in discrepancies if d.get("kind") != "policy")
    return {
        "checked": len(signals),
        "matched": matched_count,
        "drifts": len(discrepancies),
        "logic_drifts": logic_drifts,
        "policy_drifts": len(discrepancies) - logic_drifts,
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
        print(
            f"  Logic/data drifts: {result['logic_drifts']}  "
            f"(policy/config drifts: {result['policy_drifts']} — expected from gate toggles)"
        )
        if result["logic_drifts"]:
            print("\n🚨 WARNING: Replay-engine logic/data drift! Check signal assembler and gate inputs.")
        else:
            print(
                f"\n🎉 SUCCESS: No logic/data drift. {result['policy_drifts']} policy/config "
                "divergence(s) are expected (intentional gate toggles)."
            )

    return result


def main():
    result = asyncio.run(detect_drift())
    sys.exit(1 if result["logic_drifts"] else 0)


if __name__ == "__main__":
    main()
