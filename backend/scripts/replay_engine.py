"""
scripts/replay_engine.py

QENG-2b: Event-driven as-of replay engine.
Replays stored feature snapshots through live delivery gates.
"""

import asyncio
import os
import sys
from datetime import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
sys.path.insert(0, _PARENT)

from database import AsyncSessionLocal
from models import FeatureSnapshot, Signal
from services.delivery_gates import check_delivery_gates
from sqlalchemy import select

class MockSettings:
    min_confidence = 60.0

async def run_replay():
    print("## QENG-2b: Event-Driven As-Of Replay Engine\n")
    
    async with AsyncSessionLocal() as db:
        # Fetch feature snapshots
        res = await db.execute(select(FeatureSnapshot).order_by(FeatureSnapshot.created_at.desc()).limit(100))
        snapshots = res.scalars().all()
        
        if not snapshots:
            print("No stored FeatureSnapshot records found in the database.")
            print("To verify the engine, we will generate a mock snapshot and replay it...")
            
            # Let's create a mock snapshot
            # Try to get a valid signal to link to
            sig_res = await db.execute(select(Signal).limit(1))
            sig = sig_res.scalar_one_or_none()
            sig_id = sig.id if sig else None
            
            from services.feature_store import save_feature_snapshot
            snapshot = await save_feature_snapshot(
                db=db,
                ticker="AAPL",
                ts=datetime.now(),
                features={
                    "rsi": 35.0,
                    "bb_pct_b": 0.18,
                    "ibs": 0.10,
                    "vwap_pct": -0.85,
                    "atr_pct": 3.5,
                    "zscore": -2.1,
                    "quality_score": 45.0,
                    "hasMr": True
                },
                signal_id=sig_id,
                effective_time=datetime.now(),
                provider="polygon",
                signal_policy_version="1.0"
            )
            await db.commit()
            print(f"Created mock feature snapshot (ID: {snapshot.id})")
            snapshots = [snapshot]
            
        print(f"Replaying {len(snapshots)} snapshots through delivery gates...")
        
        settings = MockSettings()
        passed_count = 0
        failed_count = 0
        
        for snap in snapshots:
            # Reconstruct the signal dictionary context from the snapshot
            sig_dict = {
                "ticker": "AAPL",  # Default if instrument lookup fails
                "action": "BUY",
                "confidence": snap.quality_score or 72.0,
                "hasMr": snap.features.get("hasMr", True) if snap.features else True,
                "style": "swing",
                "rsi": snap.rsi,
                "bb_pct_b": snap.bb_pct_b,
                "ibs": snap.ibs,
                "vwap_pct": snap.vwap_pct,
                "atr_pct": snap.atr_pct,
                "zscore": snap.zscore,
            }
            
            # Retrieve ticker from Instrument
            try:
                from models import Instrument
                res_inst = await db.execute(select(Instrument).where(Instrument.id == snap.instrument_id))
                inst = res_inst.scalar_one_or_none()
                if inst:
                    sig_dict["ticker"] = inst.ticker
            except Exception:
                pass
                
            skip_reason, updated_sig = await check_delivery_gates(sig_dict, db, settings)
            
            if skip_reason is None:
                passed_count += 1
                status = "PASSED ✅"
                detail = "Signal eligible for delivery"
            else:
                failed_count += 1
                status = "BLOCKED ❌"
                detail = f"Skip reason: {skip_reason}"
                
            print(f"Snapshot ID {snap.id} ({sig_dict['ticker']}): {status} | {detail}")
            
        print(f"\nReplay Summary:")
        print(f"  Total replayed: {len(snapshots)}")
        print(f"  Passed: {passed_count}")
        print(f"  Blocked: {failed_count}")

def main():
    asyncio.run(run_replay())

if __name__ == "__main__":
    main()
