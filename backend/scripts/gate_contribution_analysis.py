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
    python scripts/gate_contribution_analysis.py --sector-wr   # ALPHA-4: per-sector WR
    python scripts/gate_contribution_analysis.py --live-dsr    # OOS-4: Deflated Sharpe on live
    python scripts/gate_contribution_analysis.py --brier-drift  # CAL-4: Brier drift monitoring

Statistically meaningful at N≥200 resolved signals.  A ⚠ warning is shown
below this threshold but the script still runs.
"""

from __future__ import annotations

import argparse
import asyncio
import math
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

# ALPHA-4: sector codes extracted from signal ticker metadata
_SECTOR_FIELD = "sector"  # key in signal.extra_data or rationale


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


def _wilson_ci(wins: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score 95% CI for a proportion. Returns (lower, upper) as percentages."""
    if n == 0:
        return 0.0, 100.0
    p = wins / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, (centre - margin) * 100), min(100.0, (centre + margin) * 100)


async def _run(min_n: int, after_date: datetime | None) -> None:
    db_gen = get_db()
    db = await db_gen.__anext__()
    try:
        # is_sent filter: live audits must mirror the delivered track record
        # (matches /live-wr-stats). validate_predictions only resolves delivered
        # signals today, so this is currently a no-op guard against future drift.
        stmt = select(Signal).where(Signal.outcome_pct.isnot(None)).where(Signal.is_sent == True)
        if after_date:
            stmt = stmt.where(Signal.created_at >= after_date)
        result = await db.execute(stmt)
        signals: list[Signal] = list(result.scalars().all())
    finally:
        await db.close()

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


_FUNDAMENTAL_GATES: list[tuple[str, list[str], str]] = [
    ("§50 Piotroski F-Score", ["Piotroski"], "signal_engine.py apply_quality_screens"),
    ("§51 Forward PE trap", ["Forward PE", "Value Trap", "PE Ratio"], "signal_engine.py"),
    ("§52 Short Interest velocity", ["Short Interest"], "signal_engine.py"),
    ("§73 Insider BUY clustering", ["Insider Cluster", "Insider Buy", "Form 4"], "edgar.py"),
    ("§74 Beneish M-Score", ["Beneish"], "fundamentals.py"),
    ("§76 Altman Z-Score", ["Altman"], "fundamentals.py"),
    ("§58 EPS Revision", ["EPS Revision", "Analyst Revision"], "signal_engine.py"),
]


async def _run_section85(after_date: datetime | None) -> None:
    """§85-1: Fundamental modifier audit — segment by each modifier, compare WR vs baseline.
    Remove any modifier with ΔWR < −1pp and N≥30 (adds noise without IS backtest validation).
    """
    db_gen = get_db()
    db = await db_gen.__anext__()
    try:
        # is_sent filter: live audits must mirror the delivered track record
        # (matches /live-wr-stats). validate_predictions only resolves delivered
        # signals today, so this is currently a no-op guard against future drift.
        stmt = select(Signal).where(Signal.outcome_pct.isnot(None)).where(Signal.is_sent == True)
        if after_date:
            stmt = stmt.where(Signal.created_at >= after_date)
        result = await db.execute(stmt)
        signals: list[Signal] = list(result.scalars().all())
    finally:
        await db.close()

    total = len(signals)
    if not total:
        print("No resolved signals found.")
        return

    wins = sum(1 for s in signals if _win(s.outcome_pct))
    baseline_wr = wins / total * 100
    avg_ret = sum(s.outcome_pct for s in signals if s.outcome_pct is not None) / total

    print(f"\n{'─' * 75}")
    print("  §85-1 Fundamental Modifier Audit")
    print("  These modifiers are LIVE-ONLY — not in IS backtest (technical-only).")
    print("  IS/live WR gap: 70.7% → 42.5%. Audit identifies which modifiers drag WR.")
    if after_date:
        print(f"  Filter: after {after_date.date()}")
    print(f"{'─' * 75}")
    print(f"  Resolved signals : {total:,}")
    print(f"  Baseline WR      : {baseline_wr:.1f}%  avg_ret={avg_ret:+.2f}%")
    if total < 200:
        print(f"\n  ⚠  {total} resolved signals — need ≥200 for reliable §85-1 verdict.")
        print("  Showing preliminary data. Rerun at N≥200 for removal decisions.")
    print(f"{'─' * 75}\n")

    rows = []
    for name, patterns, source in _FUNDAMENTAL_GATES:
        fired = [s for s in signals if _gate_fired(s.rationale or [], patterns)]
        n = len(fired)
        if n < 3:
            rows.append((name, 0, 0.0, 0.0, "⏳ N<3", source))
            continue
        wr = sum(1 for s in fired if _win(s.outcome_pct)) / n * 100
        delta = wr - baseline_wr
        verdict = (
            "✅ KEEP"
            if delta >= 2.0
            else "⚠  WATCH"
            if abs(delta) < 1.0
            else f"❌ REMOVE (N={n})"
            if n >= 30
            else f"❌ pending (N={n}<30)"
        )
        rows.append((name, n, wr, delta, verdict, source))

    col_w = max(len(r[0]) for r in rows) + 2
    print(f"  {'Fundamental Modifier':<{col_w}} {'N':>5}  {'WR%':>6}  {'ΔWR':>7}  Verdict")
    print(f"  {'─' * col_w} {'─' * 5}  {'─' * 6}  {'─' * 7}  {'─' * 20}")
    for name, n, wr, delta, verdict, source in rows:
        n_s = str(n) if n else "—"
        wr_s = f"{wr:>5.1f}%" if n else "—"
        d_s = f"{delta:>+6.1f}pp" if n else "—"
        print(f"  {name:<{col_w}} {n_s:>5}  {wr_s}  {d_s}  {verdict}")

    print(f"\n  {'─' * col_w} {'─' * 5}  {'─' * 6}  {'─' * 7}")
    print(f"  {'Baseline (all)':<{col_w}} {total:>5}  {baseline_wr:>5.1f}%  {'—':>7}")
    print()
    print("  ✅ KEEP: ΔWR ≥ +2pp  |  ⚠ WATCH: within ±1pp  |  ❌ REMOVE: ΔWR < −1pp + N≥30")
    print("  Removal procedure: comment out score line in signal_engine.py, retest WR.")
    print("  Each removal is a separate commit — revert if WR drops further.")
    print(f"{'─' * 75}\n")


# ── ALPHA-4: Per-sector live WR audit ─────────────────────────────────────────

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


def _extract_sector(signal: Signal) -> str:
    """Extract sector ETF code from the signal.

    ACT-2: read the Signal.sector_etf column first — it is populated at
    signal-creation time and is authoritative. Only ~57% of signals carry an
    ETF code in their rationale heads, so rationale parsing alone tagged 43%
    of signals "Unknown". Order: column → rationale head → extra_data.
    """
    col_sector = getattr(signal, "sector_etf", None)
    if col_sector:
        return col_sector
    rationale = signal.rationale or []
    for card in rationale:
        head = card.get("head", "")
        for etf in _SECTOR_ETF_MAP:
            if etf in head:
                return etf
    # Fall back to extra_data if populated
    extra = getattr(signal, "extra_data", None) or {}
    return extra.get("sector_etf", extra.get("sector", "Unknown"))


async def _run_sector_wr(after_date: datetime | None, min_n: int) -> None:
    """ALPHA-4: Per-sector live WR audit. Block sectors with WR < 50% at N≥30."""
    db_gen = get_db()
    db = await db_gen.__anext__()
    try:
        # is_sent filter: live audits must mirror the delivered track record
        # (matches /live-wr-stats). validate_predictions only resolves delivered
        # signals today, so this is currently a no-op guard against future drift.
        stmt = select(Signal).where(Signal.outcome_pct.isnot(None)).where(Signal.is_sent == True)
        if after_date:
            stmt = stmt.where(Signal.created_at >= after_date)
        result = await db.execute(stmt)
        signals: list[Signal] = list(result.scalars().all())
    finally:
        await db.close()

    if not signals:
        print("No resolved signals found.")
        return

    total = len(signals)
    total_wins = sum(1 for s in signals if _win(s.outcome_pct))
    baseline_wr = total_wins / total * 100

    from collections import defaultdict

    sector_buckets: dict[str, list[Signal]] = defaultdict(list)
    for s in signals:
        sector_buckets[_extract_sector(s)].append(s)

    print(f"\n{'─' * 80}")
    print("  ALPHA-4: Per-Sector Live WR Audit")
    if after_date:
        print(f"  Filter: after {after_date.date()}")
    print(f"  Baseline WR: {baseline_wr:.1f}% (N={total})")
    if total < _MIN_STATS_N:
        print(f"  ⚠  Only {total} resolved signals — stats are preliminary.")
    print(f"{'─' * 80}\n")
    print(f"  {'Sector':<22} {'ETF':>5}  {'N':>5}  {'WR%':>6}  {'ΔWR':>7}  {'95% CI':>15}  Action")
    print(f"  {'─' * 22} {'─' * 5}  {'─' * 5}  {'─' * 6}  {'─' * 7}  {'─' * 15}  {'─' * 20}")

    rows = []
    for etf, sector_signals in sector_buckets.items():
        n = len(sector_signals)
        if n < min_n:
            continue
        wins = sum(1 for s in sector_signals if _win(s.outcome_pct))
        wr = wins / n * 100
        delta = wr - baseline_wr
        lo, hi = _wilson_ci(wins, n)
        rows.append((etf, n, wins, wr, delta, lo, hi))

    rows.sort(key=lambda r: r[3], reverse=True)

    for etf, n, wins, wr, delta, lo, hi in rows:
        sector_name = _SECTOR_ETF_MAP.get(etf, etf)
        ci_str = f"[{lo:.0f}%–{hi:.0f}%]"
        if wr < 50 and n >= 30:
            action = "❌ BLOCK — add to BLOCKED_SECTORS"
        elif wr < 55 and n >= 30:
            action = "⚠  WATCH"
        else:
            action = "✅ OK"
        print(f"  {sector_name:<22} {etf:>5}  {n:>5}  {wr:>5.1f}%  {delta:>+6.1f}pp  {ci_str:>15}  {action}")

    print(f"\n  {'─' * 22} {'─' * 5}  {'─' * 5}  {'─' * 6}  {'─' * 7}")
    print(f"  {'Baseline (all)':<22} {'—':>5}  {total:>5}  {baseline_wr:>5.1f}%")
    print()
    print("  ❌ BLOCK: live WR < 50% at N≥30 → add ETF to BLOCKED_SECTORS in delivery_gates.py")
    print(f"{'─' * 80}\n")


# ── OOS-4: Live Deflated Sharpe Ratio ─────────────────────────────────────────


async def _run_live_dsr(after_date: datetime | None) -> None:
    """
    OOS-4: Compute Deflated Sharpe Ratio on live resolved signals.

    DSR = SR_hat * (1 - γ·ln(T)) / √(1 + (γ²-1)/2 · SR_hat²·T)
    where γ ≈ 0.5772 (Euler–Mascheroni), T = number of observations.

    This accounts for data-mining bias when the same backtest IS universe
    was used to select parameters. Must exceed data-mining expectation of ~0.20.

    Reference: Bailey & López de Prado (2014), "The Deflated Sharpe Ratio".
    """
    db_gen = get_db()
    db = await db_gen.__anext__()
    try:
        # is_sent filter: live audits must mirror the delivered track record
        # (matches /live-wr-stats). validate_predictions only resolves delivered
        # signals today, so this is currently a no-op guard against future drift.
        stmt = select(Signal).where(Signal.outcome_pct.isnot(None)).where(Signal.is_sent == True)
        if after_date:
            stmt = stmt.where(Signal.created_at >= after_date)
        result = await db.execute(stmt)
        signals: list[Signal] = list(result.scalars().all())
    finally:
        await db.close()

    outcomes = [s.outcome_pct for s in signals if s.outcome_pct is not None]
    n = len(outcomes)

    print(f"\n{'─' * 72}")
    print("  OOS-4: Live Deflated Sharpe Ratio (DSR)")
    print(f"{'─' * 72}")

    if n < 30:
        print(f"  ⚠  Only {n} resolved signals — need ≥30 for DSR (≥100 preferred).")
        print(f"{'─' * 72}\n")
        return

    mean_ret = sum(outcomes) / n
    variance = sum((r - mean_ret) ** 2 for r in outcomes) / (n - 1)
    std_ret = math.sqrt(variance) if variance > 0 else 1e-9

    # Per-trade Sharpe (non-annualised, same scale as IS backtest)
    sr_per_trade = mean_ret / std_ret

    # Annualise: ~25 trades/year at 10d hold (250 trading days / 10)
    sr_hat = sr_per_trade * math.sqrt(25)

    # Deflated Sharpe: apply data-mining correction.
    # Full Bailey-López de Prado (2014) formula requires the normal CDF;
    # here we use the simpler Bonferroni-style deflation:
    #   DSR = SR_hat - z_alpha × SE(SR_hat)
    # where SE(SR_hat) ≈ sqrt((1 + 0.5 × SR_hat^2) / n) (asymptotic std of SR estimator)
    # and z_alpha = 1.96 (95% significance, one-tailed).
    sr_se = math.sqrt(max(0.0, (1 + 0.5 * sr_per_trade**2) / max(n - 1, 1)))
    dsr = sr_per_trade - 1.96 * sr_se  # per-trade deflated SR
    dsr_ann = dsr * math.sqrt(25)  # annualised

    # Haircut vs IS baseline (IS SR 0.20 with §63 coint)
    IS_BASELINE_SR = 0.20
    OOS_HAIRCUT = 0.55  # historical IS→OOS haircut
    forward_estimate = IS_BASELINE_SR * OOS_HAIRCUT

    verdict = "✅ PASS" if dsr_ann > 0.10 else ("⚠  MARGINAL" if dsr_ann > 0.00 else "❌ FAIL")

    print(f"  Resolved signals : {n}")
    print(f"  Mean return      : {mean_ret:+.3f}%")
    print(f"  Std return       : {std_ret:.3f}%")
    print(f"  Raw Sharpe (ann) : {sr_hat:.3f}")
    print(f"  SR std error     : {sr_se:.4f}  (95% deflation: -{1.96 * sr_se:.4f})")
    print(f"  Deflated Sharpe  : {dsr_ann:.3f}  {verdict}")
    print(f"  IS baseline SR   : {IS_BASELINE_SR:.2f}  (v10.5, N=230)")
    print(f"  Forward estimate : {forward_estimate:.2f}  ({OOS_HAIRCUT * 100:.0f}% OOS haircut)")
    print()
    if dsr < 0.10:
        print("  ⚠  DSR below 0.10 threshold — IS parameter selection may not generalise.")
        print("     Actions: (a) wait for N≥100 more live trades before concluding,")
        print("              (b) review if signal universe drift occurred post-A19.")
    else:
        print("  ✅ DSR above 0.10 — live edge is statistically meaningful.")
    print(f"{'─' * 72}\n")


# ── CAL-4: Brier score drift monitoring ───────────────────────────────────────


async def _run_brier_drift(after_date: datetime | None, window_days: int = 30) -> None:
    """
    CAL-4: Track rolling Brier score on live resolved signals.

    Brier score = mean((confidence/100 - outcome_binary)²).
    Lower is better. Cal v4 baseline: 0.2641.
    Alert threshold: 0.28 (degradation). Auto-flag for recalibration above 0.30.
    """
    from datetime import timedelta

    db_gen = get_db()
    db = await db_gen.__anext__()
    try:
        # is_sent filter: live audits must mirror the delivered track record
        # (matches /live-wr-stats). validate_predictions only resolves delivered
        # signals today, so this is currently a no-op guard against future drift.
        stmt = (
            select(Signal)
            .where(Signal.outcome_pct.isnot(None))
            .where(Signal.is_sent == True)
            .where(Signal.confidence.isnot(None))
        )
        if after_date:
            stmt = stmt.where(Signal.created_at >= after_date)
        result = await db.execute(stmt)
        signals: list[Signal] = list(result.scalars().all())
    finally:
        await db.close()

    if not signals:
        print("No resolved signals with confidence found.")
        return

    # Sort by created_at
    signals.sort(key=lambda s: s.created_at or datetime.min)

    # Overall Brier score
    def brier(sigs: list[Signal]) -> float:
        if not sigs:
            return float("nan")
        total = 0.0
        for s in sigs:
            p = (s.confidence or 50.0) / 100.0
            y = 1.0 if (s.outcome_pct or 0) > 0 else 0.0
            total += (p - y) ** 2
        return total / len(sigs)

    overall_brier = brier(signals)
    n = len(signals)

    # Rolling window Brier scores
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    window_start = now - timedelta(days=window_days)
    recent = [s for s in signals if (s.created_at or datetime.min) >= window_start]
    rolling_brier = brier(recent)

    # Reference baseline from calibration v4
    CAL_V4_BRIER = 0.2641
    ALERT_THRESHOLD = 0.28
    RECAL_THRESHOLD = 0.30

    print(f"\n{'─' * 72}")
    print("  CAL-4: Brier Score Drift Monitor")
    print(f"{'─' * 72}")
    print(f"  Total resolved   : {n}")
    print(f"  Overall Brier    : {overall_brier:.4f}  (cal v4 baseline: {CAL_V4_BRIER:.4f})")
    print(f"  Rolling ({window_days}d) Brier: {rolling_brier:.4f}  (N={len(recent)})")

    if len(recent) < 10:
        print(f"  ⚠  Only {len(recent)} signals in rolling window — rolling Brier unreliable.")
    elif rolling_brier > RECAL_THRESHOLD:
        print(f"\n  🔴 ALERT: Rolling Brier {rolling_brier:.4f} > {RECAL_THRESHOLD:.2f} recalibration threshold!")
        print("     Action: run `python scripts/backfill_confidence.py --force --apply`")
    elif rolling_brier > ALERT_THRESHOLD:
        print(f"\n  ⚠  WARNING: Rolling Brier {rolling_brier:.4f} > {ALERT_THRESHOLD:.2f} alert threshold.")
        print("     Monitor closely. Recalibrate if sustained for >7 days.")
    else:
        drift = rolling_brier - CAL_V4_BRIER
        print(f"\n  ✅ Brier stable. Rolling drift vs v4 baseline: {drift:+.4f}")

    # Trend: split signals into quartiles by time, show Brier per quartile
    if n >= 40:
        q_size = n // 4
        print(f"\n  Brier trend (4 time quartiles of N={q_size} each):")
        for qi in range(4):
            q_sigs = signals[qi * q_size : (qi + 1) * q_size]
            q_brier = brier(q_sigs)
            trend = "↑" if qi > 0 and q_brier > brier(signals[(qi - 1) * q_size : qi * q_size]) else "↓"
            oldest = q_sigs[0].created_at
            newest = q_sigs[-1].created_at
            period = f"{oldest.strftime('%b %d') if oldest else '?'}–{newest.strftime('%b %d') if newest else '?'}"
            print(f"    Q{qi + 1} ({period}): Brier={q_brier:.4f} {trend}")

    print(f"\n{'─' * 72}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="A5 gate contribution monitoring")
    parser.add_argument("--min-n", type=int, default=10, help="Minimum N to include in report (default: 10)")
    parser.add_argument("--after", type=str, default=None, help="Only signals after this date (YYYY-MM-DD)")
    parser.add_argument(
        "--section85", action="store_true", help="§85-1 mode: fundamental modifiers only, with removal recommendations"
    )
    parser.add_argument("--sector-wr", action="store_true", help="ALPHA-4: per-sector live WR audit with Wilson CI")
    parser.add_argument(
        "--live-dsr", action="store_true", help="OOS-4: compute Deflated Sharpe Ratio on live resolved signals"
    )
    parser.add_argument("--brier-drift", action="store_true", help="CAL-4: rolling Brier score drift monitor")
    parser.add_argument("--window-days", type=int, default=30, help="Rolling window for Brier drift (default: 30)")
    args = parser.parse_args()

    after_dt: datetime | None = None
    if args.after:
        after_dt = datetime.fromisoformat(args.after).replace(tzinfo=timezone.utc)

    if args.section85:
        asyncio.run(_run_section85(after_dt))
    elif args.sector_wr:
        asyncio.run(_run_sector_wr(after_dt, args.min_n))
    elif args.live_dsr:
        asyncio.run(_run_live_dsr(after_dt))
    elif args.brier_drift:
        asyncio.run(_run_brier_drift(after_dt, args.window_days))
    else:
        asyncio.run(_run(args.min_n, after_dt))


if __name__ == "__main__":
    main()
