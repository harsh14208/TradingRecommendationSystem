"""Analyze the Stage B static-vs-dynamic ticker-performance gate shadow A/B.

Run after signals have resolved (outcome_pct_7d / outcome_pct_hold backfilled):

    cd backend && python scripts/analyze_ticker_perf_shadow.py --days 30

Outputs a Markdown report to stdout with:
- Decision overlap matrix (static vs dynamic)
- Forward win rate and P&L for each disagreement bucket
- Missed winners / saved losers from each gate
- Volume impact
- Sector skew introduced by the dynamic gate
- Outcome-horizon alignment check (7d vs recommended hold days)
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("analyze_ticker_perf_shadow")


def _win(action: str, pct: float | None) -> bool | None:
    if pct is None:
        return None
    if action == "BUY":
        return pct > 0
    if action == "SELL":
        return pct < 0
    return None


@dataclass
class Bucket:
    name: str
    rows: list[Any]

    @property
    def n(self) -> int:
        return len(self.rows)

    def outcomes(self, field: str) -> list[float]:
        return [getattr(r, field) for r in self.rows if getattr(r, field) is not None]

    def wr(self, field: str) -> float | None:
        vals = self.outcomes(field)
        if not vals:
            return None
        wins = sum(1 for v in vals if v > 0)  # outcome_pct>0 is a win for both BUY/SELL in this script
        return wins / len(vals)

    def avg_return(self, field: str) -> float | None:
        vals = self.outcomes(field)
        return sum(vals) / len(vals) if vals else None

    def missed_winners(self, field: str) -> int:
        return sum(1 for r in self.rows if getattr(r, field) is not None and getattr(r, field) > 0)

    def saved_losers(self, field: str) -> int:
        return sum(1 for r in self.rows if getattr(r, field) is not None and getattr(r, field) <= 0)


def _section(title: str) -> str:
    return f"\n## {title}\n"


async def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze ticker-performance gate shadow A/B")
    parser.add_argument("--days", type=int, default=30, help="Number of days to look back")
    parser.add_argument("--outcome", choices=["7d", "hold"], default="7d", help="Outcome horizon to analyze")
    args = parser.parse_args()

    outcome_field = "outcome_pct_7d" if args.outcome == "7d" else "outcome_pct_hold"

    from database import AsyncSessionLocal
    from models import Signal, TickerPerfShadowDecision

    # scan_ts is TIMESTAMP WITHOUT TIME ZONE — cutoff must be tz-naive UTC or
    # asyncpg raises DataError (same fix as cohort_edge_gate.refresh 2026-07-13).
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=args.days)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(TickerPerfShadowDecision, Signal)
            .join(Signal, TickerPerfShadowDecision.signal_id == Signal.id)
            .where(TickerPerfShadowDecision.scan_ts >= cutoff)
            .order_by(TickerPerfShadowDecision.scan_ts.desc())
        )
        rows = result.all()

    if not rows:
        print("No shadow decisions found for the requested window.")
        return

    decisions = [d for d, _ in rows]

    # ── Overall summary ─────────────────────────────────────────────────────
    total = len(decisions)
    static_blocks = sum(1 for d in decisions if d.static_blocked)
    dynamic_blocks = sum(1 for d in decisions if d.dynamic_decision == "block")
    dynamic_cautions = sum(1 for d in decisions if d.dynamic_decision == "caution")
    dynamic_passes = sum(1 for d in decisions if d.dynamic_decision == "pass")

    print(_section("Summary"))
    print(f"- Window: last {args.days} days")
    print(f"- Outcome horizon: `{outcome_field}`")
    print(f"- Total directional signals: {total}")
    print(f"- Static blocklist blocked: {static_blocks} ({static_blocks / total:.1%})")
    print(f"- Dynamic gate blocked: {dynamic_blocks} ({dynamic_blocks / total:.1%})")
    print(f"- Dynamic gate cautioned: {dynamic_cautions} ({dynamic_cautions / total:.1%})")
    print(f"- Dynamic gate passed: {dynamic_passes} ({dynamic_passes / total:.1%})")

    # ── Decision overlap matrix ─────────────────────────────────────────────
    print(_section("Decision overlap"))
    print("| Static | Dynamic block | Dynamic caution | Dynamic pass |")
    print("|--------|---------------|-----------------|--------------|")
    for static_val in (True, False):
        counts = {"block": 0, "caution": 0, "pass": 0}
        for d in decisions:
            if d.static_blocked == static_val:
                counts[d.dynamic_decision] += 1
        static_label = "blocked" if static_val else "passed"
        print(f"| {static_label} | {counts['block']} | {counts['caution']} | {counts['pass']} |")

    # ── Disagreement buckets ────────────────────────────────────────────────
    static_only = Bucket(
        "Static blocked / Dynamic passed",
        [r[0] for r in rows if r[0].static_blocked and r[0].dynamic_decision == "pass"],
    )
    dynamic_only = Bucket(
        "Static passed / Dynamic blocked or cautioned",
        [r[0] for r in rows if not r[0].static_blocked and r[0].dynamic_decision in ("block", "caution")],
    )
    both_blocked = Bucket(
        "Both blocked",
        [r[0] for r in rows if r[0].static_blocked and r[0].dynamic_decision == "block"],
    )
    both_passed = Bucket(
        "Both passed",
        [r[0] for r in rows if not r[0].static_blocked and r[0].dynamic_decision == "pass"],
    )

    print(_section("Disagreement analysis"))
    print("| Bucket | N | Resolved | WR | Avg return | Missed winners | Saved losers |")
    print("|--------|---|----------|----|-----------|----------------|--------------|")
    for bucket in (static_only, dynamic_only, both_blocked, both_passed):
        resolved = bucket.outcomes(outcome_field)
        wr = bucket.wr(outcome_field)
        avg_ret = bucket.avg_return(outcome_field)
        wr_s = f"{wr:.1%}" if wr is not None else "n/a"
        avg_s = f"{avg_ret:+.2f}%" if avg_ret is not None else "n/a"
        print(
            f"| {bucket.name} | {bucket.n} | {len(resolved)} | "
            f"{wr_s} | {avg_s} | "
            f"{bucket.missed_winners(outcome_field)} | {bucket.saved_losers(outcome_field)} |"
        )

    # ── Missed winners / saved losers narrative ─────────────────────────────
    print(_section("Gate-level attribution"))
    print(
        f"- **Static blocklist missed winners**: {static_only.missed_winners(outcome_field)} "
        f"(signals the static list blocked but the dynamic gate would have let through)."
    )
    print(
        f"- **Static blocklist saved losers**: {static_only.saved_losers(outcome_field)} "
        f"(signals the static list blocked and the dynamic gate agrees were losers)."
    )
    print(
        f"- **Dynamic gate missed winners**: {dynamic_only.missed_winners(outcome_field)} "
        f"(signals the dynamic gate would have blocked/cautioned but the static list let through)."
    )
    print(
        f"- **Dynamic gate saved losers**: {dynamic_only.saved_losers(outcome_field)} "
        f"(signals the dynamic gate would have blocked/cautioned and they were losers)."
    )

    # ── Volume impact ───────────────────────────────────────────────────────
    print(_section("Volume impact"))
    print(
        f"- If the dynamic gate were live, signals delivered would change by "
        f"{dynamic_blocks - static_blocks:+.0f} (blocks) and {dynamic_cautions} cautions (size reductions)."
    )

    # ── Sector skew ─────────────────────────────────────────────────────────
    print(_section("Sector skew (dynamic gate)"))
    sector_counts: dict[str, dict[str, int]] = {}
    for d in decisions:
        sector = d.sector_etf or "unknown"
        sector_counts.setdefault(sector, {"block": 0, "caution": 0, "pass": 0, "total": 0})
        sector_counts[sector][d.dynamic_decision] += 1
        sector_counts[sector]["total"] += 1

    print("| Sector | Total | Block | Caution | Pass | Block% |")
    print("|--------|-------|-------|---------|------|--------|")
    for sector, counts in sorted(sector_counts.items(), key=lambda x: -x[1]["total"]):
        total_sector = counts["total"]
        block_pct = counts["block"] / total_sector if total_sector else 0
        print(
            f"| {sector} | {total_sector} | {counts['block']} | {counts['caution']} | "
            f"{counts['pass']} | {block_pct:.1%} |"
        )

    # ── Outcome horizon alignment ───────────────────────────────────────────
    print(_section("Outcome horizon alignment"))
    aligned = 0
    misaligned = 0
    hold_missing = 0
    for d, s in rows:
        # the 7d outcome lives on the shadow-decision row, not the Signal
        if d.hold_days is None or d.outcome_pct_7d is None:
            hold_missing += 1
            continue
        # Heuristic: 7d outcome is aligned if hold_days is within 5-10 days.
        # A more rigorous fix is to compute outcome_pct_hold at the actual hold day.
        if 5 <= d.hold_days <= 10:
            aligned += 1
        else:
            misaligned += 1
    print(f"- Signals with hold_days data: {len(rows) - hold_missing}")
    print(f"- 7d outcome aligned with hold guidance (5-10 days): {aligned}")
    print(f"- 7d outcome potentially misaligned: {misaligned}")
    if misaligned:
        print(
            "- **Recommendation:** backfill `outcome_pct_hold` at the signal's "
            "actual recommended hold day and re-run this report with `--outcome hold`."
        )

    print("\n---\nEnd of report.\n")


if __name__ == "__main__":
    asyncio.run(main())
