"""
scripts/drift_detector.py

REF-2: Replay Engine Drift Detection.
Weekly automated validation script comparing live database signals against
replayed decisions using point-in-time feature snapshots.
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

async def detect_drift(lookback_days: int = 7):
    print("## REF-2: Replay Engine Drift Detection\n")
    print(f"Comparing live Signal records vs. Replay Engine over the last {lookback_days} days...\n")
    
    async with AsyncSessionLocal() as db:
        cutoff = datetime.utcnow() - timedelta(days=lookback_days)
        
        # Query signals that were processed in the lookback period
        stmt = select(Signal).where(Signal.created_at >= cutoff)
        res = await db.execute(stmt)
        signals = res.scalars().all()
        
        if not signals:
            print("No Signal records found in the database for the lookback period.")
            return
            
        discrepancies = []
        matched_count = 0
        
        for sig in signals:
            # Find the corresponding FeatureSnapshot
            snap_stmt = select(FeatureSnapshot).where(FeatureSnapshot.signal_id == sig.id)
            snap_res = await db.execute(snap_stmt)
            snap = snap_res.scalar_one_or_none()
            
            if not snap:
                print(f"⚠️ Signal ID {sig.id} ({sig.ticker}): No matching FeatureSnapshot found. Cannot verify drift.")
                continue
                
            # Reconstruct signal dict from snapshot features
            sig_dict = {
                "ticker": sig.ticker,
                "action": sig.action,
                "confidence": snap.quality_score or sig.confidence,
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
            skip_reason, updated_sig = await check_delivery_gates(sig_dict, db, settings)
            
            # Compare Replay outcome vs. Live outcome
            replay_passed = (skip_reason is None)
            live_passed = sig.is_sent
            
            # Check confidence drift
            conf_drift = abs(sig_dict["confidence"] - sig.confidence)
            
            has_drift = False
            desc = ""
            
            if replay_passed != live_passed:
                has_drift = True
                desc = f"Decision discrepancy: Live Sent={live_passed} | Replay Passed={replay_passed} (Skip reason: {skip_reason})"
            elif conf_drift > 0.01:
                has_drift = True
                desc = f"Confidence discrepancy: Live Conf={sig.confidence:.2f}% | Replay Conf={sig_dict['confidence']:.2f}%"
                
            if has_drift:
                discrepancies.append({
                    "signal_id": sig.id,
                    "ticker": sig.ticker,
                    "created_at": sig.created_at,
                    "description": desc
                })
                print(f"❌ DRIFT DETECTED: Signal ID {sig.id} ({sig.ticker}) at {sig.created_at} | {desc}")
            else:
                matched_count += 1
                print(f"✅ MATCHED: Signal ID {sig.id} ({sig.ticker}) matches replay engine perfectly.")
                
        print(f"\nDrift Detection Summary:")
        print(f"  Total signals checked: {len(signals)}")
        print(f"  Matched perfectly: {matched_count}")
        print(f"  Drifts detected: {len(discrepancies)}")
        
        if discrepancies:
            print("\n🚨 WARNING: System logic or data drift detected! Check signal assembler and gate inputs.")
            sys.exit(1)
        else:
            print("\n🎉 SUCCESS: All replayed signals match live records. No drift detected.")
            sys.exit(0)

def main():
    asyncio.run(detect_drift())

if __name__ == "__main__":
    main()
