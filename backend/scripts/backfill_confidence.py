"""
scripts/backfill_confidence.py

Backfills historical signal confidence values using the current v2 calibration.

WHY: The old pipeline used a narrow sigmoid + 65% ceiling + Platt bins that
     systematically overconfident signals in the 70-101% band (actual WR 55%
     vs predicted 85%). The v2 calibration (isotonic + 78% ceiling) corrects this.
     The 26 gates added in §59–§82 shifted the score distribution — the isotonic
     calibration trained on pre-§82 signals is no longer aligned with the new
     distribution.  Running this script re-trains on post-§82 resolved signals
     and backfills all stored confidence values.

HOW: We don't store the raw score, so a perfect re-run is impossible. Instead
     we treat each signal's stored confidence as the raw input to the NEW
     calibration function. This correctly pulls overconfident signals downward
     and fixes the ceiling. The approximation error is small (~1-3pp) for
     mid-band signals.

READINESS GUARD (A4): The script requires ≥200 resolved signals created AFTER
     the §82 gates launched (2026-05-29).  Below this threshold the calibration
     map is too noisy to be reliable and the script exits with a warning.
     Use --check to see the current count without attempting recalibration.

USAGE:
    python scripts/backfill_confidence.py --check          # show readiness + Brier
    python scripts/backfill_confidence.py                  # dry run — shows what would change
    python scripts/backfill_confidence.py --apply          # writes to DB
    python scripts/backfill_confidence.py --apply --min-delta 3   # only update if delta ≥ 3pp
    python scripts/backfill_confidence.py --force          # skip N≥200 guard (testing only)
"""

from __future__ import annotations

import asyncio
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
sys.path.insert(0, _PARENT)

from datetime import datetime

from database import get_db
from models import Signal
from services.calibration import apply_calibration, load_calibration, run_calibration
from sqlalchemy import func, select, update

# §82 gates launched 2026-05-29 — signals after this date use the new 26-gate stack.
_SECTION_82_LAUNCH = datetime(2026, 5, 29)
_MIN_POST_82_RESOLVED = 200  # minimum resolved signals after §82 to trust recalibration


async def check_readiness() -> None:
    """Report A4 recalibration readiness without modifying anything."""
    print("# Confidence Recalibration Readiness Check (A4)\n")
    db_gen = get_db()
    db = await anext(db_gen)
    try:
        # Count all resolved signals
        total_resolved = (
            await db.execute(select(func.count()).select_from(Signal).where(Signal.outcome_pct.isnot(None)))
        ).scalar_one()
        # Count resolved signals after §82 launch
        post82_resolved = (
            await db.execute(
                select(func.count())
                .select_from(Signal)
                .where(Signal.outcome_pct.isnot(None), Signal.created_at >= _SECTION_82_LAUNCH)
            )
        ).scalar_one()
        # Count all signals
        total_signals = (await db.execute(select(func.count()).select_from(Signal))).scalar_one()
    finally:
        await db.close()

    needed = max(0, _MIN_POST_82_RESOLVED - post82_resolved)
    ready = post82_resolved >= _MIN_POST_82_RESOLVED

    print(f"  Total signals in DB:          {total_signals:,}")
    print(f"  Total resolved:               {total_resolved:,}")
    print(f"  Post-§82 resolved (≥{_SECTION_82_LAUNCH.date()}): {post82_resolved:,}")
    print(f"  Required for recalibration:   {_MIN_POST_82_RESOLVED}")
    print()

    if ready:
        print("  ✅ READY — run without --check to recalibrate.")
    else:
        print(f"  ⏳ NOT READY — need {needed} more resolved signals after {_SECTION_82_LAUNCH.date()}.")
        print("     The §82 gates shifted the score distribution; recalibrating too early")
        print("     produces a noisy isotonic map that can make Brier WORSE.")
        print(f"     Estimated wait: ~{needed // 7 + 1} weeks at current signal volume.")

    # Also show current Brier if calibration exists
    try:
        cal_map = load_calibration()
        meta = cal_map.get("_meta", {})
        if meta.get("brier_walkforward"):
            print(f"\n  Current Brier (saved cal): {meta['brier_walkforward']:.4f}")
            print(f"  Trained on N={meta.get('n_train', '?')} signals, validated on N={meta.get('n_valid', '?')}")
    except Exception:
        pass


async def backfill(apply: bool = False, min_delta: float = 0.5, force: bool = False) -> None:
    print("# Confidence Backfill — v2 calibration\n")
    print(f"  Mode:      {'APPLY (writes to DB)' if apply else 'DRY RUN (no writes)'}")
    print(f"  Min delta: {min_delta}pp (signals with |Δ| < {min_delta}pp are skipped)\n")

    # ── A4 readiness guard ────────────────────────────────────────────────────
    if not force:
        db_gen_check = get_db()
        db_check = await anext(db_gen_check)
        try:
            post82_resolved = (
                await db_check.execute(
                    select(func.count())
                    .select_from(Signal)
                    .where(Signal.outcome_pct.isnot(None), Signal.created_at >= _SECTION_82_LAUNCH)
                )
            ).scalar_one()
        finally:
            await db_check.close()

        if post82_resolved < _MIN_POST_82_RESOLVED:
            needed = _MIN_POST_82_RESOLVED - post82_resolved
            print(
                f"  ⏳ READINESS GUARD: only {post82_resolved} post-§82 resolved signals "
                f"(need {_MIN_POST_82_RESOLVED}, {needed} more).\n"
                "  Recalibration skipped — isotonic map would be too noisy.\n"
                "  Run --check for full status, or --force to override (testing only)."
            )
            return
        print(f"  ✅ Readiness guard passed ({post82_resolved} post-§82 resolved ≥ {_MIN_POST_82_RESOLVED})\n")

    # ── Step 1: refresh calibration map from all resolved outcomes ─────────────
    print("Step 1/3 — Refreshing calibration map from resolved outcomes…")
    try:
        cal_map = await run_calibration()
        meta = cal_map.get("_meta", {})
        brier_str = f"{meta['brier_walkforward']:.4f}" if meta.get("brier_walkforward") else "n/a"
        print(f"  ok  Brier={brier_str}  n_train={meta.get('n_train', '?')}  n_val={meta.get('n_valid', '?')}\n")
    except Exception as e:
        print(f"  run_calibration() failed ({e}), falling back to saved calibration.json")
        cal_map = load_calibration()
        if not cal_map:
            print("[error] No calibration map available. Run run_calibration() first.")
            return
        print(f"  Loaded saved cal_map ({len(cal_map)} keys)\n")

    # ── Step 2: read all signals (only columns needed — avoids raw_score migration gap) ──
    print("Step 2/3 — Reading all signals from DB…")
    db_gen = get_db()
    db = await anext(db_gen)
    try:
        rows = (
            await db.execute(select(Signal.id, Signal.action, Signal.confidence).order_by(Signal.created_at.asc()))
        ).all()
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
    n_up = len(updates)
    if n_up == 0:
        print(f"  No signals exceed the {min_delta}pp delta threshold. Nothing to update.")
        return

    deltas = [u["delta"] for u in updates]
    avg_d = sum(deltas) / len(deltas)
    lower = sum(1 for d in deltas if d < 0)
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
        print(f"  {band:<15} {ob:>8,} {nb:>8,} {nb - ob:>+8,}")

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
                await db2.execute(update(Signal).where(Signal.id == u["id"]).values(confidence=round(u["new"], 2)))
        await db2.commit()
    finally:
        await db2.close()
    print("done.\n")
    print(f"✓ Backfill complete — {n_up:,} signals updated.")
    print("  Re-run calc_tbd_metrics.py to verify the calibration diagram.")


def _band_dist(confs: list[float]) -> dict[str, int]:
    bands: dict[str, int] = {}
    for c in confs:
        if c < 55:
            b = "<55%"
        elif c < 65:
            b = "55–65%"
        elif c < 70:
            b = "65–70%"
        elif c < 75:
            b = "70–75%"
        elif c < 80:
            b = "75–80%"
        else:
            b = "80%+"
        bands[b] = bands.get(b, 0) + 1
    return bands


def _chunks(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


# ── CAL-2: Per-sector calibration analysis ───────────────────────────────────

_SECTOR_ETF_MAP = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLV": "Healthcare",
    "XLY": "Consumer Disc.",
    "XLC": "Communication",
    "XLI": "Industrials",
    "XLE": "Energy",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLP": "Consumer Staples",
    "XLU": "Utilities",
}


async def per_sector_calibration() -> None:
    """
    CAL-2: Compute per-sector Brier score vs global Brier.

    If any sector's Brier exceeds the global baseline by >0.01,
    sector-conditional calibration curves should be deployed.
    """
    db_gen = get_db()
    db = await db_gen.__anext__()
    try:
        from models import Signal
        from sqlalchemy import select as _sel

        rows = list(
            (await db.execute(_sel(Signal).where(Signal.outcome_pct.isnot(None)).where(Signal.confidence.isnot(None))))
            .scalars()
            .all()
        )
    finally:
        await db.close()

    if not rows:
        print("No resolved signals found.")
        return

    total = len(rows)
    global_brier = sum(((s.confidence / 100.0) - (1.0 if (s.outcome_pct or 0) > 0 else 0.0)) ** 2 for s in rows) / total

    def _sector(sig):
        for card in sig.rationale or []:
            head = card.get("head", "")
            for etf in _SECTOR_ETF_MAP:
                if etf in head:
                    return etf
        return "Unknown"

    from collections import defaultdict

    buckets: dict = defaultdict(list)
    for s in rows:
        buckets[_sector(s)].append(s)

    print(f"\n{'─' * 72}")
    print("  CAL-2: Per-Sector Brier Score Analysis")
    print(f"  Global Brier: {global_brier:.4f}  (cal v4 baseline: 0.2641)")
    print(f"  Total N: {total}")
    print(f"{'─' * 72}\n")
    print(f"  {'Sector':<22} {'ETF':>5}  {'N':>5}  {'Brier':>7}  {'ΔBrier':>8}  Verdict")
    print(f"  {'─' * 22} {'─' * 5}  {'─' * 5}  {'─' * 7}  {'─' * 8}  {'─' * 20}")

    needs_sector_cal = False
    for etf, sigs in sorted(buckets.items(), key=lambda x: -len(x[1])):
        n = len(sigs)
        if n < 10:
            continue
        brier = sum(((s.confidence / 100.0) - (1.0 if (s.outcome_pct or 0) > 0 else 0.0)) ** 2 for s in sigs) / n
        delta = brier - global_brier
        verdict = "✅ OK" if abs(delta) < 0.01 else ("⚠ WATCH" if abs(delta) < 0.02 else "❌ DEPLOY SECTOR CAL")
        if abs(delta) >= 0.01:
            needs_sector_cal = True
        sector_name = _SECTOR_ETF_MAP.get(etf, etf)
        print(f"  {sector_name:<22} {etf:>5}  {n:>5}  {brier:>7.4f}  {delta:>+8.4f}  {verdict}")

    print(f"\n  {'Global (all)':<22} {'—':>5}  {total:>5}  {global_brier:>7.4f}  {'—':>8}")
    print()
    if needs_sector_cal:
        print("  ❌ At least one sector deviates >0.01 Brier — deploy sector-conditional calibration.")
        print("     Add 'sector' grouping to backfill() and fit separate isotonic curves per ETF.")
    else:
        print("  ✅ All sectors within ±0.01 of global Brier — global calibration is sufficient.")
    print(f"{'─' * 72}\n")


# ── CAL-3: Reliability diagram (calibration curve) ───────────────────────────


async def reliability_diagram() -> None:
    """
    CAL-3: Print a text-mode reliability diagram (calibration curve).

    Bins resolved signals by confidence, shows actual WR per bin.
    Ideal: points on the diagonal (predicted_conf ≈ actual_WR).
    """
    db_gen = get_db()
    db = await db_gen.__anext__()
    try:
        from models import Signal
        from sqlalchemy import select as _sel

        rows = list(
            (await db.execute(_sel(Signal).where(Signal.outcome_pct.isnot(None)).where(Signal.confidence.isnot(None))))
            .scalars()
            .all()
        )
    finally:
        await db.close()

    if not rows:
        print("No resolved signals.")
        return

    bins = [
        (0, 40),
        (40, 45),
        (45, 50),
        (50, 55),
        (55, 60),
        (60, 65),
        (65, 70),
        (70, 75),
        (75, 80),
        (80, 100),
    ]

    print(f"\n{'─' * 72}")
    print("  CAL-3: Reliability Diagram (Calibration Curve)")
    print("  Ideal: actual WR ≈ predicted confidence → points on diagonal.")
    print(f"{'─' * 72}\n")
    print(f"  {'Conf Bin':<12} {'N':>5}  {'Pred Conf':>10}  {'Actual WR':>10}  {'Gap':>7}  Bar")
    print(f"  {'─' * 12} {'─' * 5}  {'─' * 10}  {'─' * 10}  {'─' * 7}  {'─' * 20}")

    for lo, hi in bins:
        bucket = [s for s in rows if lo <= (s.confidence or 0) < hi]
        n = len(bucket)
        if n < 3:
            continue
        pred_conf = sum(s.confidence for s in bucket) / n
        actual_wr = sum(1 for s in bucket if (s.outcome_pct or 0) > 0) / n * 100
        gap = actual_wr - pred_conf
        flag = "✅" if abs(gap) < 5 else ("⚠ " if abs(gap) < 10 else "❌")
        # ASCII bar chart showing deviation
        bar_len = min(20, max(0, int(abs(gap) / 2)))
        bar = ("←" if gap < 0 else "→") * bar_len
        print(f"  {lo:>3}–{hi:<3}%      {n:>5}  {pred_conf:>9.1f}%  {actual_wr:>9.1f}%  {gap:>+6.1f}%  {flag}{bar}")

    print()
    print("  ✅ Gap < 5pp  |  ⚠ Gap 5–10pp  |  ❌ Gap > 10pp → recalibration needed")
    print(f"{'─' * 72}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Backfill signal confidence with v2 calibration")
    parser.add_argument("--check", action="store_true", help="Report readiness + current Brier without recalibrating")
    parser.add_argument("--apply", action="store_true", help="Write changes to DB (default: dry run)")
    parser.add_argument(
        "--min-delta", type=float, default=0.5, help="Minimum |Δconfidence| in pp to update (default: 0.5)"
    )
    parser.add_argument("--force", action="store_true", help="Skip N≥200 readiness guard (testing only)")
    parser.add_argument("--sector-cal", action="store_true", help="CAL-2: per-sector Brier analysis")
    parser.add_argument("--reliability-diagram", action="store_true", help="CAL-3: text-mode calibration curve")
    args = parser.parse_args()

    if args.sector_cal:
        asyncio.run(per_sector_calibration())
    elif args.reliability_diagram:
        asyncio.run(reliability_diagram())
    elif args.check:
        asyncio.run(check_readiness())
    else:
        asyncio.run(backfill(apply=args.apply, min_delta=args.min_delta, force=args.force))
