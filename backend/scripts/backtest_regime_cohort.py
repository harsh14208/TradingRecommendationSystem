#!/usr/bin/env python3
"""
Backtest: Regime-Conditional Model Allocation (US11410240B2).

Loads the in-sample trade ledger from backtest_technicals.py and tests whether
allocating to sector/model cohorts conditionally on the HMM macro regime
improves risk-adjusted returns.

The baseline is the existing portfolio simulation (5 concurrent slots, equal
weight among open positions). The regime-conditional variants compute an
expanding-window empirical-Bayes net edge per (sector_etf, regime) cohort and
either:

  * filter: skip trades whose cohort edge is not positive, or
  * size:  scale notionals by the cohort's shrunk net edge.

No look-ahead is used: the edge for a trade is computed only from prior trades
in the same cohort.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Allow imports from backend/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Reuse the canonical event-time portfolio simulator from backtest_technicals.py
from scripts.backtest_technicals import run_portfolio_simulation

DEFAULT_SLOTS = 5
COLD_START_N = 8  # min observations before acting on a cohort
SHRINK_K = 16.0  # empirical-Bayes pseudo-count
Z = 1.0  # lower-confidence-bound multiplier
SIZE_CLAMP = (0.0, 1.5)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Regime-cohort backtest")
    parser.add_argument(
        "--trades",
        default=str(ROOT / "data" / "backtest_trades_is.csv"),
        help="Path to backtest_trades_is.csv",
    )
    parser.add_argument(
        "--slots",
        type=int,
        default=DEFAULT_SLOTS,
        help="Number of concurrent portfolio slots",
    )
    parser.add_argument(
        "--min-cohort-n",
        type=int,
        default=COLD_START_N,
        help="Minimum cohort observations before using its edge (passthrough otherwise)",
    )
    parser.add_argument(
        "--shrink-k",
        type=float,
        default=SHRINK_K,
        help="Empirical-Bayes pseudo-count for shrinkage",
    )
    parser.add_argument(
        "--strategy",
        choices=["filter", "size", "both"],
        default="both",
        help="Which regime-cohort strategy to evaluate",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "data" / "backtest_regime_cohort.csv"),
        help="Where to write per-trade results",
    )
    return parser.parse_args()


# ── Regime labelling helpers ─────────────────────────────────────────────────


def regime_bull_bear(bull_prob: pd.Series) -> pd.Series:
    """Two-regime split."""
    return pd.Series(np.where(bull_prob >= 0.5, "bull", "bear"), index=bull_prob.index)


def regime_three_state(bull_prob: pd.Series, trans_risk: pd.Series) -> pd.Series:
    """Three-regime split that respects the HMM transition-risk output."""
    out = pd.Series(index=bull_prob.index, dtype="object")
    out[trans_risk > 0.20] = "transition"
    out[(bull_prob >= 0.60) & (trans_risk <= 0.20)] = "bull"
    out[(bull_prob < 0.40) & (trans_risk <= 0.20)] = "bear"
    mask = ((bull_prob >= 0.40) & (bull_prob < 0.60)) & (trans_risk <= 0.20)
    out[mask] = "transition"
    return out


def regime_vix(vix: pd.Series) -> pd.Series:
    """VIX-level regime: calm / elevated / stress."""
    out = pd.Series(index=vix.index, dtype="object")
    out[vix < 20] = "calm"
    out[(vix >= 20) & (vix < 30)] = "elevated"
    out[vix >= 30] = "stress"
    return out


def regime_spy_trend(spy_trend: pd.Series) -> pd.Series:
    """SPY trend direction at entry."""
    return pd.Series(np.where(spy_trend >= 0, "spy_bull", "spy_bear"), index=spy_trend.index)


def regime_macro(vix: pd.Series, spy_trend: pd.Series) -> pd.Series:
    """Combined macro regime using VIX level and SPY trend."""
    out = pd.Series(index=vix.index, dtype="object")
    vix_label = regime_vix(vix)
    spy_label = regime_spy_trend(spy_trend)
    for idx in vix.index:
        out[idx] = f"{vix_label[idx]}|{spy_label[idx]}"
    return out


def regime_hmm_vix(bull_prob: pd.Series, vix: pd.Series) -> pd.Series:
    """HMM bull/bear crossed with VIX stress flag."""
    out = pd.Series(index=bull_prob.index, dtype="object")
    hmm = regime_bull_bear(bull_prob)
    vix_stress = vix >= 30
    for idx in bull_prob.index:
        suffix = "stress" if vix_stress[idx] else "normal"
        out[idx] = f"{hmm[idx]}|{suffix}"
    return out


# ── Empirical-Bayes cohort edge ──────────────────────────────────────────────


def _mean_std(vals: list[float]) -> tuple[float, float]:
    n = len(vals)
    if n == 0:
        return 0.0, 0.0
    m = sum(vals) / n
    if n < 2:
        return m, 0.0
    var = sum((v - m) ** 2 for v in vals) / (n - 1)
    return m, math.sqrt(var)


def compute_regime_cohort_snapshot(
    history: pd.DataFrame,
    shrink_k: float,
    z: float = Z,
) -> dict:
    """Compute shrunk net edge per (sector, regime) cohort.

    Hierarchy: cohort(sector,regime) → parent(regime) → global.
    Returns dict with keys global, parents, cohorts.
    """
    outcomes = history["net_pct"].astype(float).tolist()
    g_mean, g_std = _mean_std(outcomes)
    pooled_std = g_std if g_std > 0 else 1.0
    total_n = len(outcomes)

    def shrink(raw_mean: float, n: int, prior_mean: float) -> float:
        return (n * raw_mean + shrink_k * prior_mean) / (n + shrink_k)

    # Parent = per-regime bucket
    parents: dict[str, list[float]] = {}
    for _, r in history.iterrows():
        parents.setdefault(str(r["regime"]), []).append(float(r["net_pct"]))

    parent_est: dict[str, dict] = {}
    for reg, vals in parents.items():
        n = len(vals)
        raw_mean, _ = _mean_std(vals)
        shrunk = shrink(raw_mean, n, g_mean)
        parent_est[reg] = {"n": n, "raw_net": raw_mean, "net": shrunk}

    # Cohort = (sector, regime)
    cohorts: dict[str, dict] = {}
    grouped = history.groupby(["sector_etf", "regime"])["net_pct"].apply(list)
    for (sector, reg), vals in grouped.items():
        key = f"{sector}|{reg}"
        n = len(vals)
        raw_mean, raw_std = _mean_std(vals)
        prior = parent_est.get(reg, {}).get("net", g_mean)
        shrunk = shrink(raw_mean, n, prior)
        n_eff = n + shrink_k
        sd = raw_std if (n >= 4 and raw_std > 0) else pooled_std
        se = sd / math.sqrt(n_eff)
        lb = shrunk - z * se
        cohorts[key] = {
            "sector": sector,
            "regime": reg,
            "n": n,
            "raw_net": raw_mean,
            "net": shrunk,
            "se": se,
            "lb_net": lb,
            "deliver": lb > 0.0,
        }

    return {
        "total_n": total_n,
        "global": {"n": total_n, "net": g_mean, "std": g_std},
        "parents": parent_est,
        "cohorts": cohorts,
    }


def get_cohort_edge(snapshot: dict, sector: str, regime: str) -> tuple[float, int, bool]:
    key = f"{sector}|{regime}"
    c = snapshot.get("cohorts", {}).get(key)
    if c:
        return c["net"], c["n"], c["deliver"]
    p = snapshot.get("parents", {}).get(regime)
    if p:
        return p["net"], p["n"], True
    g = snapshot.get("global", {})
    return g.get("net", 0.0), g.get("n", 0), True


# ── Portfolio simulation ─────────────────────────────────────────────────────


def simulate_portfolio(trades: pd.DataFrame, slots: int = DEFAULT_SLOTS) -> pd.Series:
    """Build a daily equity curve assuming equal capital split among `slots`
    concurrent positions.

    Trades are assigned to the first available slot (greedy fill).  Each trade
    earns return on 1/slots of the slot's equity.  This mirrors the 5-slot
    portfolio simulation in backtest_technicals.py.
    """
    if trades.empty:
        return pd.Series(dtype=float)

    trades = trades.copy()
    trades["entry_date"] = pd.to_datetime(trades["date"])
    trades["exit_date"] = trades["entry_date"] + pd.to_timedelta(trades["exit_day"].fillna(0), unit="D")
    trades = trades.sort_values(["entry_date"]).reset_index(drop=True)

    start = trades["entry_date"].min()
    end = trades["exit_date"].max()
    days = pd.date_range(start=start, end=end, freq="D")

    # One equity series per slot, reindexed to the full date range.
    slot_equities: list[pd.Series] = []
    slot_next_free: list[pd.Timestamp] = [pd.Timestamp.min] * slots

    for slot_idx in range(slots):
        eq = pd.Series(1.0, index=days)
        slot_equities.append(eq)

    for _, tr in trades.iterrows():
        ed = tr["entry_date"]
        ex = tr["exit_date"]
        slot_idx = next((i for i, free_at in enumerate(slot_next_free) if free_at <= ed), None)
        if slot_idx is None:
            continue  # crowded out (should be rare with correct slot count)

        eq = slot_equities[slot_idx]
        entry_equity = eq.loc[ed]
        ret = tr["net_pct"] / 100.0
        # P&L accrues only at exit, costlessly held in the slot until then.
        pnl = (entry_equity / slots) * ret
        exit_idx = eq.index.get_indexer([ex], method="nearest")[0]
        eq.iloc[exit_idx:] += pnl
        slot_next_free[slot_idx] = ex

    portfolio = pd.concat(slot_equities, axis=1).mean(axis=1)
    return portfolio


def portfolio_metrics(equity: pd.Series, trades: pd.DataFrame) -> dict:
    if equity.empty or len(equity) < 30:
        return {"sharpe": 0.0, "ann_return": 0.0, "max_dd": 0.0, "trades": len(trades)}

    daily_ret = equity.pct_change().dropna()
    ann_ret = daily_ret.mean() * 252
    ann_vol = daily_ret.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol > 1e-9 else 0.0

    cummax = equity.cummax()
    dd = (equity - cummax) / cummax
    max_dd = dd.min()

    return {
        "sharpe": sharpe,
        "ann_return": ann_ret,
        "ann_vol": ann_vol,
        "max_dd": max_dd,
        "trades": len(trades),
        "final_equity": equity.iloc[-1],
    }


# ── Per-trade stats ──────────────────────────────────────────────────────────


def trade_stats(trades: pd.DataFrame) -> dict:
    r = trades["net_pct"].dropna()
    if r.empty:
        return {"n": 0, "wr": 0.0, "avg": 0.0, "sharpe": 0.0}
    avg = r.mean()
    std = r.std(ddof=0)
    sharpe = (avg / std) * np.sqrt(252 / 5.0) if std > 1e-9 else 0.0
    return {"n": len(r), "wr": (r > 0).mean() * 100.0, "avg": avg, "sharpe": sharpe}


# ── Regime-cohort sizing/filter pipeline ─────────────────────────────────────


def apply_regime_cohort(
    trades: pd.DataFrame,
    strategy: str,
    min_cohort_n: int,
    shrink_k: float,
) -> pd.DataFrame:
    """Return trades augmented with regime-cohort multipliers."""
    trades = trades.copy().sort_values("date").reset_index(drop=True)
    trades["entry_date"] = pd.to_datetime(trades["date"])

    history: list[dict] = []
    decisions: list[dict] = []

    for _, row in trades.iterrows():
        sector = row["sector_etf"]
        regime = row["regime"]

        if len(history) < min_cohort_n:
            decisions.append({"regime_cohort_mult": 1.0, "cohort_n": 0, "cohort_net": 0.0, "cold_start": True})
            history.append(row.to_dict())
            continue

        hist_df = pd.DataFrame(history)
        snapshot = compute_regime_cohort_snapshot(hist_df, shrink_k)
        net_edge, n_obs, deliver = get_cohort_edge(snapshot, sector, regime)

        mult = 1.0
        if strategy == "filter":
            mult = 1.0 if deliver and net_edge > 0 else 0.0
        elif strategy == "size":
            global_net = snapshot.get("global", {}).get("net", 0.0)
            if n_obs >= min_cohort_n:
                ratio = net_edge / max(abs(global_net), 0.1) if global_net else 1.0
                mid = (SIZE_CLAMP[0] + SIZE_CLAMP[1]) / 2.0
                mult = float(np.clip(mid + ratio * (SIZE_CLAMP[1] - mid) * 0.5, *SIZE_CLAMP))
            else:
                mult = 1.0
        elif strategy == "both":
            if not deliver or net_edge <= 0:
                mult = 0.0
            else:
                global_net = snapshot.get("global", {}).get("net", 0.0)
                if n_obs >= min_cohort_n and global_net:
                    ratio = net_edge / max(abs(global_net), 0.1)
                    mid = (SIZE_CLAMP[0] + SIZE_CLAMP[1]) / 2.0
                    mult = float(np.clip(mid + ratio * (SIZE_CLAMP[1] - mid) * 0.5, 0.5, SIZE_CLAMP[1]))

        decisions.append(
            {
                "regime_cohort_mult": mult,
                "cohort_n": n_obs,
                "cohort_net": net_edge,
                "cold_start": False,
            }
        )
        history.append(row.to_dict())

    mult_df = pd.DataFrame(decisions)
    result = pd.concat([trades.reset_index(drop=True), mult_df], axis=1)
    result["net_pct_rc"] = result["net_pct"] * result["regime_cohort_mult"]
    return result


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    args = parse_args()
    trades = pd.read_csv(args.trades)

    required = {"date", "net_pct", "sector_etf", "hmm_bull_prob", "exit_day", "action"}
    missing = required - set(trades.columns)
    if missing:
        raise SystemExit(f"Missing columns: {missing}")

    trades["date"] = pd.to_datetime(trades["date"])
    trades["regime_2"] = regime_bull_bear(trades["hmm_bull_prob"])
    trades["regime_3"] = regime_three_state(trades["hmm_bull_prob"], trades.get("hmm_trans_risk"))

    # Richer regime labels when market data is available.
    _vix_col = "vix_entry" if "vix_entry" in trades.columns else ("vix" if "vix" in trades.columns else None)
    _spy_col = "spy_trend_entry" if "spy_trend_entry" in trades.columns else None
    if _vix_col:
        trades["regime_vix"] = regime_vix(trades[_vix_col])
    else:
        trades["regime_vix"] = "unknown"
    if _spy_col:
        trades["regime_spy"] = regime_spy_trend(trades[_spy_col])
    else:
        trades["regime_spy"] = "unknown"
    if _vix_col and _spy_col:
        trades["regime_macro"] = regime_macro(trades[_vix_col], trades[_spy_col])
    else:
        trades["regime_macro"] = "unknown"
    if _vix_col:
        trades["regime_hmm_vix"] = regime_hmm_vix(trades["hmm_bull_prob"], trades[_vix_col])
    else:
        trades["regime_hmm_vix"] = "unknown"
    trades["regime"] = trades["regime_2"]  # default 2-regime

    baseline_pm = run_portfolio_simulation(trades, max_concurrent=args.slots, quiet=True) or {}
    baseline_pm = {k: baseline_pm.get(k, 0.0) for k in ("ann_sharpe", "cagr", "max_dd", "skipped")}
    baseline_ts = trade_stats(trades)

    print("=" * 70)
    print("Regime-Conditional Model Allocation Backtest (US11410240B2)")
    print(f"Trades loaded: {len(trades)}  |  Slots: {args.slots}")
    print("=" * 70)
    print("\nBaseline (all trades)")
    print(f"  Trades: {baseline_ts['n']}")
    print(f"  WR:     {baseline_ts['wr']:.1f}%")
    print(f"  Avg:    {baseline_ts['avg']:+.2f}%")
    print(f"  Trd Sh: {baseline_ts['sharpe']:.2f}")
    print(f"  Port Sh:{baseline_pm.get('ann_sharpe', 0.0):.2f}")
    print(f"  Ann Ret:{baseline_pm.get('cagr', 0.0):+.2f}%")
    print(f"  Max DD: -{baseline_pm.get('max_dd', 0.0):.2f}%")

    best_variant: dict | None = None
    variants = []
    strategies = ["filter", "size", "both"] if args.strategy == "both" else [args.strategy]

    regime_cols = ["regime_2", "regime_3"]
    if _vix_col:
        regime_cols.append("regime_vix")
    if _vix_col and _spy_col:
        regime_cols.extend(["regime_macro", "regime_hmm_vix"])
    for strategy in strategies:
        for regime_col in regime_cols:
            work = trades.copy()
            work["regime"] = work[regime_col]
            rc = apply_regime_cohort(work, strategy, args.min_cohort_n, args.shrink_k)
            taken = rc[rc["regime_cohort_mult"] > 0.0].copy()
            taken["net_pct"] = taken["net_pct_rc"]

            pm = run_portfolio_simulation(taken, max_concurrent=args.slots, quiet=True) or {}
            pm = {k: pm.get(k, 0.0) for k in ("ann_sharpe", "cagr", "max_dd", "skipped")}
            ts = trade_stats(taken)
            variant = {
                "strategy": strategy,
                "regime": regime_col,
                "trades_taken": int(len(taken)),
                "trades_skipped": int(len(rc) - len(taken)),
                "wr": ts["wr"],
                "avg": ts["avg"],
                "trade_sharpe": ts["sharpe"],
                "port_sharpe": pm["ann_sharpe"],
                "ann_return": pm["cagr"],
                "max_dd": pm["max_dd"],
            }
            variants.append(variant)

            print(f"\nVariant: {strategy} | {regime_col}")
            print(f"  Taken:  {variant['trades_taken']}  Skipped: {variant['trades_skipped']}")
            print(f"  WR:     {variant['wr']:.1f}%")
            print(f"  Avg:    {variant['avg']:+.2f}%")
            print(f"  Trd Sh: {variant['trade_sharpe']:.2f}")
            print(f"  Port Sh:{variant['port_sharpe']:.2f}")
            print(f"  Ann Ret:{variant.get('ann_return', variant.get('cagr', 0.0)):+.2f}%")
            print(f"  Max DD: -{variant.get('max_dd', 0.0):.2f}%")

            if best_variant is None or variant["port_sharpe"] > best_variant["port_sharpe"]:
                best_variant = variant

    # ── Cohort edge snapshot (full history, for diagnostics) ───────────────────
    full_snapshot = compute_regime_cohort_snapshot(trades, args.shrink_k)
    print("\n## Cohort net-edge snapshot (full-sample, diagnostics only)")
    print(f"{'Cohort':<16} {'N':>4} {'RawNet':>8} {'ShrNet':>8} {'LB':>8} {'Deliver':>8}")
    for key, c in sorted(full_snapshot.get("cohorts", {}).items()):
        print(
            f"{key:<16} {c['n']:>4} {c['raw_net']:>+7.2f}% "
            f"{c['net']:>+7.2f}% {c['lb_net']:>+7.2f}% "
            f"{'YES' if c['deliver'] else 'NO':>8}"
        )

    print("\n" + "=" * 70)
    if best_variant:
        print(
            f"Best variant: {best_variant['strategy']} | {best_variant['regime']}  "
            f"Port Sharpe {best_variant['port_sharpe']:.2f}"
        )
        delta_sh = best_variant["port_sharpe"] - baseline_pm["ann_sharpe"]
        delta_dd = abs(best_variant["max_dd"]) - abs(baseline_pm["max_dd"])
        print(f"Δ Sharpe vs baseline: {delta_sh:+.2f}")
        print(f"Δ MaxDD vs baseline: {delta_dd:+.2f}pp")

        # Graduation requires meaningful Sharpe uplift without materially worse DD.
        if delta_sh > 0.20 and delta_dd <= 1.0 and best_variant["trades_taken"] >= max(50, len(trades) * 0.5):
            print("VERDICT: GRADUATE — integrate into live cohort gate + portfolio allocator.")
        elif delta_sh > 0.10 and delta_dd <= 2.0:
            print("VERDICT: PROMISING — run OOS/backtest_technicals integration next; watch MaxDD.")
        elif delta_sh > 0.05:
            print("VERDICT: MARGINAL — needs richer regime labels or more data.")
        else:
            print("VERDICT: REJECT — no material lift in this dataset.")

    if args.strategy in ("both", "size", "filter"):
        rc = apply_regime_cohort(trades.copy(), args.strategy, args.min_cohort_n, args.shrink_k)
        rc.to_csv(args.output, index=False)
        print(f"\nWrote per-trade regime-cohort results to {args.output}")


if __name__ == "__main__":
    main()
