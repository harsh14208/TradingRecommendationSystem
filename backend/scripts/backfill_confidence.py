"""
scripts/backfill_confidence.py

Backfills historical signal confidence values using the current v2 calibration.

WHY: The old pipeline used a narrow sigmoid + 65% ceiling + Platt bins that
     systematically overconfident signals in the 70-101% band (actual WR 55%
     vs predicted 85%). The v2 calibration (isotonic + 78% ceiling) corrects this.

HOW: We don't store the raw score, so a perfect re-run is impossible. Instead
     we treat each signal's stored confidence as the raw input to the NEW
     calibration function. This correctly pulls overconfident signals downward
     and fixes the ceiling. The approximation error is small (~1-3pp) for
     mid-band signals; signals capped at the old 65% ceiling are re-calibrated
     as if they scored 65% (we can't know their true underlying score).

USAGE:
    python scripts/backfill_confidence.py           # dry run — shows what would change
    python scripts/backfill_confidence.py --apply   # writes to DB
    python scripts/backfill_confidence.py --apply --min-delta 3   # only update if delta ≥ 3pp
"""
from __future__ import annotations
import asyncio
import os
import sys
from datetime import datetime, timezone

_HERE   = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
sys.path.insert(0, _PARENT)

from sqlalchemy import select, update
from database import get_db
from models import Signal
from services.calibration import run_calibration, load_calibration, apply_calibration


async def backfill(apply: bool = False, min_delta: float = 0.5) -> None:
    print("# Confidence Backfill — v2 calibration\n")
    print(f"  Mode:      {'APPLY (writes to DB)' if apply else 'DRY RUN (no writes)'}")
    print(f"  Min delta: {min_delta}pp (signals with |Δ| < {min_delta}pp are skipped)\n")

    # ── Step 1: refresh calibration map from all resolved outcomes ─────────────
    print("Step 1/3 — Refreshing calibration map from resolved outcomes…")
    try:
        cal_map = await run_calibration()
        meta = cal_map.get("_meta", {})
        brier_str = f"{meta['brier_walkforward']:.4f}" if meta.get('brier_walkforward') else "n/a"
        print(f"  ok  Brier={brier_str}"
              f"  n_train={meta.get('n_train', '?')}"
              f"  n_val={meta.get('n_valid', '?')}\n")
    except Exception as e:
        print(f"  run_calibration() failed ({e}), falling back to saved calibration.json")
        cal_map = load_calibration()
        if not cal_map:
            print("[error] No calibration map available. Run run_calibration() first.")
            return
        print(f"  Loaded saved cal_map ({len(cal_map)} keys)\n")

    # ── Step 2: read all signals ───────────────────────────────────────────────
    print("Step 2/3 — Reading all signals from DB…")
    db_gen = get_db()
    db = await anext(db_gen)
    try:
        rows = (await db.execute(
            select(Signal).order_by(Signal.created_at.asc())
        )).scalars().all()
    finally:
        await db.close()

    print(f"  {len(rows):,} signals total\n")

    # ── Step 3: compute new confidence for each signal ─────────────────────────
    print("Step 3/3 — Computing new confidence values…")
    updates: list[dict] = []  # {id, old_conf, new_conf, delta}
    skipped_below_delta = 0
    skipped_hold = 0

    for r in rows:
        action = (r.action or "BUY").upper()
        if action not in ("BUY", "SELL"):
            skipped_hold += 1
            continue

        old_conf = float(r.confidence) if r.confidence is not None else 55.0
        new_conf, _ = apply_calibration(old_conf, action, cal_map)
        delta = new_conf - old_conf

        if abs(delta) < min_delta:
            skipped_below_delta += 1
            continue

        updates.append({"id": r.id, "old": old_conf, "new": new_conf, "delta": delta})

    # ── Summary ────────────────────────────────────────────────────────────────
    n_up   = len(updates)
    if n_up == 0:
        print(f"  No signals exceed the {min_delta}pp delta threshold. Nothing to update.")
        return

    deltas = [u["delta"] for u in updates]
    avg_d  = sum(deltas) / len(deltas)
    lower  = sum(1 for d in deltas if d < 0)
    higher = sum(1 for d in deltas if d > 0)

    print(f"\n  Signals to update:  {n_up:,}")
    print(f"  Confidence LOWERED: {lower:,}  (overconfident → corrected down)")
    print(f"  Confidence RAISED:  {higher:,}  (underconfident → corrected up)")
    print(f"  Avg delta:          {avg_d:+.2f}pp")
    print(f"  Max decrease:       {min(deltas):+.2f}pp")
    print(f"  Max increase:       {max(deltas):+.2f}pp")
    print(f"  Skipped (HOLD):     {skipped_hold:,}")
    print(f"  Skipped (< {min_delta}pp):  {skipped_below_delta:,}")

    # Band shift preview
    old_bands = _band_dist([u["old"] for u in updates])
    new_bands = _band_dist([u["new"] for u in updates])
    print("\n  Confidence band shift (of updated signals):")
    print(f"  {'Band':<15} {'Before':>8} {'After':>8} {'Δ':>8}")
    for band in sorted(set(list(old_bands.keys()) + list(new_bands.keys()))):
        ob = old_bands.get(band, 0)
        nb = new_bands.get(band, 0)
        print(f"  {band:<15} {ob:>8,} {nb:>8,} {nb-ob:>+8,}")

    if not apply:
        print("\n  DRY RUN — re-run with --apply to write changes to DB.")
        return

    # ── Write to DB ────────────────────────────────────────────────────────────
    print(f"\n  Writing {n_up:,} updates to DB…", end=" ", flush=True)
    db_gen2 = get_db()
    db2 = await anext(db_gen2)
    try:
        for chunk in _chunks(updates, 500):
            for u in chunk:
                await db2.execute(
                    update(Signal)
                    .where(Signal.id == u["id"])
                    .values(confidence=round(u["new"], 2))
                )
        await db2.commit()
    finally:
        await db2.close()
    print(f"done.\n")
    print(f"✓ Backfill complete — {n_up:,} signals updated.")
    print(f"  Re-run calc_tbd_metrics.py to verify the calibration diagram.")


def _band_dist(confs: list[float]) -> dict[str, int]:
    bands: dict[str, int] = {}
    for c in confs:
        if c < 55:  b = "<55%"
        elif c < 65: b = "55–65%"
        elif c < 70: b = "65–70%"
        elif c < 75: b = "70–75%"
        elif c < 80: b = "75–80%"
        else:        b = "80%+"
        bands[b] = bands.get(b, 0) + 1
    return bands


def _chunks(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Backfill signal confidence with v2 calibration")
    parser.add_argument("--apply",     action="store_true", help="Write changes to DB (default: dry run)")
    parser.add_argument("--min-delta", type=float, default=0.5,
                        help="Minimum |Δconfidence| in pp to update (default: 0.5)")
    args = parser.parse_args()
    asyncio.run(backfill(apply=args.apply, min_delta=args.min_delta))
