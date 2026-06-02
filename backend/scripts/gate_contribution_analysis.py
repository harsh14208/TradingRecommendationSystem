"""
scripts/gate_contribution_analysis.py — A5 Gate Contribution Monitoring

Segments resolved live signals by which §47–§83 gate fired and reports
per-gate ΔWR vs the overall baseline.  Detects gates that add no value
(or actively harm WR) so they can be removed from the live engine.

Gate detection: each gate that fires leaves a card in signal.rationale
with a distinctive head/keyword.  This script matches those patterns
without requiring a schema change.

USAGE:
    python scripts/gate_contribution_analysis.py           # full report
    python scripts/gate_contribution_analysis.py --min-n 5   # lower display threshold
    python scripts/gate_contribution_analysis.py --after 2026-06-01  # post-date filter

Statistically meaningful at N≥200 resolved signals.  A ⚠ warning is shown
below this threshold but the script still runs.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import datetime, timezone
from typing import Any

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
sys.path.insert(0, _PARENT)

from database import get_db
from models import Signal
from sqlalchemy import select

# ── Gate keyword patterns ─────────────────────────────────────────────────────
# Each entry: (display_name, [substrings to match in rationale card heads])
# A gate "fired" if ANY of its patterns appears in ANY card head for that signal.
GATE_PATTERNS: list[tuple[str, list[str]]] = [
    ("§47 VIX Term Structure", ["VIX Term Structure", "VIX/VIX3M", "Backwardation"]),
    ("§48 IVR", ["IVR", "Implied Volatility Rank"]),
    ("§49 Put-Call Skew", ["Put-Call Skew", "25Δ Skew", "25d Skew"]),
    ("§50 Piotroski F-Score", ["Piotroski"]),
    ("§51 Forward PE", ["Forward PE", "Value Trap", "PE Ratio"]),
    ("§52 Short Interest Velocity", ["Short Interest Velocity"]),
    ("§57 Thursday DOW", ["Thursday", "DOW Gate"]),
    ("§58 EPS Revision", ["EPS Revision", "Analyst Revision"]),
    ("§59 OU Halflife", ["OU Halflife", "Mean-Reversion Half", "Halflife"]),
    ("§60 Hurst Exponent", ["Hurst"]),
    ("§61 Idio Vol", ["Idiosyncratic Vol", "Idio Vol"]),
    ("§63 Sector Cointegration", ["Cointegration"]),
    ("§64 Yield Curve", ["Yield Curve"]),
    ("§65 TRIN", ["TRIN"]),
    ("§66 AD Breadth", ["A/D Breadth", "AD Breadth", "Zweig Thrust"]),
    ("§68 2Y Treasury", ["2Y Treasury", "Treasury Rate"]),
    ("§69 GEX", ["GEX", "Dealer Positioning", "Gamma"]),
    ("§70 Zero-DTE", ["Zero-DTE", "0DTE"]),
    ("§71 Max Pain", ["Max Pain"]),
    ("§72 VRP Proxy", ["VRP", "Volatility Risk Premium"]),
    ("§73 Insider Clustering", ["Insider Cluster", "Insider Buy", "Form 4"]),
    ("§74 Beneish M-Score", ["Beneish"]),
    ("§76 Altman Z-Score", ["Altman"]),
    ("§77 Tax-Loss Window", ["Tax-Loss", "Tax Loss"]),
    ("§80 NBBO Spread", ["NBBO Spread", "Bid-Ask Spread"]),
    ("§81 Block Prints", ["Block Print", "Block Buy"]),
    ("§83 Cross-Signal Corr", ["Correlation Penalty", "Cross-Signal"]),
]

_MIN_STATS_N = 200  # warn below this total resolved-signal count


def _gate_fired(rationale: list[dict[str, Any]], patterns: list[str]) -> bool:
    for card in rationale:
        head = card.get("head", "")
        if any(p.lower() in head.lower() for p in patterns):
            return True
    return False


def _win(outcome_pct: float | None) -> bool | None:
    if outcome_pct is None:
        return None
    return outcome_pct > 0


async def _run(min_n: int, after_date: datetime | None) -> None:
    async with get_db() as db:
        stmt = select(Signal).where(Signal.outcome_pct.isnot(None))
        if after_date:
            stmt = stmt.where(Signal.created_at >= after_date)
        result = await db.execute(stmt)
        signals: list[Signal] = list(result.scalars().all())

    if not signals:
        print("No resolved signals found.")
        return

    total = len(signals)
    wins = sum(1 for s in signals if _win(s.outcome_pct))
    baseline_wr = wins / total * 100 if total else 0
    avg_ret = sum(s.outcome_pct for s in signals if s.outcome_pct is not None) / total

    print(f"\n{'─' * 72}")
    print("  A5 Gate Contribution Analysis")
    if after_date:
        print(f"  Filter: signals created after {after_date.date()}")
    print(f"{'─' * 72}")
    print(f"  Resolved signals : {total:,}")
    print(f"  Baseline WR      : {baseline_wr:.1f}%")
    print(f"  Baseline avg ret : {avg_ret:+.2f}%")
    if total < _MIN_STATS_N:
        print(f"\n  ⚠  Only {total} resolved signals — need ≥{_MIN_STATS_N} for reliable stats.")
    print(f"{'─' * 72}\n")

    rows: list[tuple[str, int, float, float]] = []

    for name, patterns in GATE_PATTERNS:
        fired = [s for s in signals if _gate_fired(s.rationale or [], patterns)]
        n = len(fired)
        if n < min_n:
            continue
        wr = sum(1 for s in fired if _win(s.outcome_pct)) / n * 100
        delta = wr - baseline_wr
        rows.append((name, n, wr, delta))

    # Sort by ΔWR descending
    rows.sort(key=lambda r: r[3], reverse=True)

    col_w = max((len(r[0]) for r in rows), default=30) + 2
    header = f"  {'Gate':<{col_w}} {'N':>6}  {'WR%':>6}  {'ΔWR':>7}  Signal"
    print(header)
    print(f"  {'─' * col_w} {'─' * 6}  {'─' * 6}  {'─' * 7}  {'─' * 6}")

    for name, n, wr, delta in rows:
        arrow = "✅" if delta >= 2 else ("⚠ " if abs(delta) < 1 else "❌")
        print(f"  {name:<{col_w}} {n:>6}  {wr:>5.1f}%  {delta:>+6.1f}pp  {arrow}")

    print(f"\n  {'─' * col_w} {'─' * 6}  {'─' * 6}  {'─' * 7}")
    print(f"  {'Baseline (all resolved)':<{col_w}} {total:>6}  {baseline_wr:>5.1f}%  {'—':>7}")
    print()
    print("  ✅ = gate adds ≥+2pp WR  |  ⚠ = within ±1pp (noise)  |  ❌ = drags WR")
    print("  Remove gates with ❌ after confirming N≥30 (see §85-1 / A5 in TODO.md)")
    print(f"{'─' * 72}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="A5 gate contribution monitoring")
    parser.add_argument(
        "--min-n", type=int, default=10, help="Minimum N (gate-fired signals) to include in report (default: 10)"
    )
    parser.add_argument(
        "--after", type=str, default=None, help="Only include signals created after this date (YYYY-MM-DD)"
    )
    args = parser.parse_args()

    after_dt: datetime | None = None
    if args.after:
        after_dt = datetime.fromisoformat(args.after).replace(tzinfo=timezone.utc)

    asyncio.run(_run(args.min_n, after_dt))


if __name__ == "__main__":
    main()
