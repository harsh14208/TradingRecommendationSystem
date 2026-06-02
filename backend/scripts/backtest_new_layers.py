"""
Sizing ablation: measure the Sharpe contribution of each new layer.

Usage:
    # Step 1 — generate the trades CSV (run the full IS backtest):
    cd backend && python scripts/backtest_technicals.py --save-trades

    # Step 2 — run this ablation script:
    cd backend && python scripts/backtest_new_layers.py

    # Optional flags:
    #   --mc          run 10 000-sim Monte Carlo on each configuration
    #   --plot        save sizing_ablation.png bar chart

Layers tested:
  Baseline   equal weight (1.0 × every trade)
  +L7        raw-score Kelly already in backtest size_mult column
  +L8        quality_score tier (1.30× high / 1.0× mid / 0.75× low)
  +L9        HMM-proxy regime (VIX/SPY rule-based: 1.10× / 0.85× / 0.70×)
  +L8+L9     combined
  +OFI_proxy IBS-based daily OFI proxy: block distribution (ibs>0.5 on a DOWN
             day = accumulation, keep; ibs<0.2 on DOWN day = distribution, skip)

What this measures:
  L8 and L9 affect positionSizeScale (not which trades pass). So:
    size-weighted Sharpe = Sharpe of (net_pct × size_mult) series
  This is the right measure because larger positions amplify both
  gains and losses — the Sharpe of the SCALED returns is what live
  capital experiences.

  OFI_proxy affects trade SELECTION (removes distribution signals).
  It changes N and therefore Sharpe directly.

Sizing Sharpe interpretation:
  A size-weighted Sharpe > equal-weight Sharpe means capital is being
  deployed more heavily when trades are higher quality. This is the
  practical impact of L8/L9 on live portfolio performance.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_BACKEND = Path(__file__).parent.parent
_DATA_DIR = _BACKEND / "data"
_TRADES_FILE = _DATA_DIR / "backtest_trades_is.csv"

# ── Core maths ────────────────────────────────────────────────────────────────


def sharpe(returns: np.ndarray) -> float | None:
    """
    Per-trade Sharpe — matches backtest_technicals.stats() exactly:
        sharpe = mean(returns) / std(returns, ddof=1)
    No √252 scaling: backtest returns are trade-level, not daily.
    Applying √252 as if they were daily returns is wrong for a 10-day hold system.
    """
    n = len(returns)
    if n < 10:
        return None
    m = float(returns.mean())
    s = float(returns.std(ddof=1))
    if s < 1e-10:
        return None
    return round(m / s, 4)


def win_rate(returns: np.ndarray) -> float:
    return float((returns > 0).mean() * 100)


def avg_ret(returns: np.ndarray) -> float:
    return float(returns.mean())


_POSITION_SIZE = 0.05  # matches backtest_technicals.POSITION_SIZE


def max_dd(returns: np.ndarray) -> float:
    """Max drawdown on equity curve — matches backtest_technicals.stats() exactly."""
    cap, peak, mdd = 10_000.0, 10_000.0, 0.0
    for r in returns:
        cap += cap * _POSITION_SIZE * (float(r) / 100)
        peak = max(peak, cap)
        mdd = max(mdd, (peak - cap) / peak * 100)
    return round(mdd, 2)


def fmt_sh(v) -> str:
    return f"{v:.3f}" if v is not None else "—"


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    widths = [max(len(h), max((len(r[i]) for r in rows), default=0)) for i, h in enumerate(headers)]
    sep = "  ".join("-" * w for w in widths)
    print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print(sep)
    for row in rows:
        print("  ".join(str(c).ljust(w) for c, w in zip(row, widths)))
    print()


# ── Regime proxy ──────────────────────────────────────────────────────────────


def l9_multiplier(vix: float | None, spy_trend: int) -> float:
    """
    Simplified HMM-proxy using VIX + SPY trend (matches L9 thresholds in
    signal_engine.py but using deterministic rules instead of a fitted HMM).

    VIX < 18  AND  SPY ≥ 200d MA  →  bull  → 1.10×
    VIX > 25  OR   SPY < 200d MA  →  bear  → 0.70×
    otherwise                      →  trans → 0.85×
    """
    if vix is None:
        return 1.0
    if vix < 18 and spy_trend == 1:
        return 1.10
    if vix > 25 or spy_trend == -1:
        return 0.70
    return 0.85


def l8_multiplier(qs: float | None) -> float:
    """quality_score tier → L8 size multiplier (signal_engine.py L8)."""
    if qs is None:
        return 1.0
    if qs >= 60:
        return 1.30
    if qs < 30:
        return 0.75
    return 1.0


# ── OFI daily proxy ──────────────────────────────────────────────────────────


def ofi_proxy_keep(row: pd.Series) -> bool:
    """
    Daily bar OFI proxy: True = keep trade (no distribution signal).

    Logic (mirrors live OFI gate logic for MR BUY):
      change_pct < 0 (day was down — MR entry candidate)
      AND ibs < 0.20 (closed near low = sellers still in control = distribution)
        → SKIP (mirrors live -6pp penalty that often drops below threshold)

    All other cases: keep.
    IBS > 0.40 on a down day = price bounced off lows = accumulation → positive OFI proxy.
    """
    change = row.get("change_pct_entry") or row.get("change_pct")
    ibs = row.get("ibs_entry") or row.get("ibs")
    if change is None or ibs is None:
        return True  # no data → keep (graceful degradation)
    try:
        change = float(change)
        ibs = float(ibs)
    except (TypeError, ValueError):
        return True
    # Distribution signal: day was DOWN and price closed near lows
    if change < 0 and ibs < 0.20:
        return False
    return True


# ── Sizing simulation ─────────────────────────────────────────────────────────


def apply_sizing(
    trades: pd.DataFrame,
    use_l8: bool = False,
    use_l9: bool = False,
    use_ofi_proxy: bool = False,
) -> tuple[np.ndarray, int]:
    """
    Apply sizing overlays and return (size_weighted_returns, n_trades).

    Returns weighted_returns where each return = net_pct × total_size_mult.
    n_trades counts trades that survive the OFI filter (if active).
    """
    mask = np.ones(len(trades), dtype=bool)
    if use_ofi_proxy:
        mask = np.array([ofi_proxy_keep(row) for _, row in trades.iterrows()])

    filtered = trades[mask].copy()
    size_mults = np.ones(len(filtered))

    if use_l8:
        size_mults *= np.array([l8_multiplier(r.get("quality_score")) for _, r in filtered.iterrows()])

    if use_l9:
        size_mults *= np.array(
            [l9_multiplier(r.get("vix_entry"), r.get("spy_trend_entry", 0)) for _, r in filtered.iterrows()]
        )

    weighted = filtered["net_pct"].values * size_mults
    return weighted, int(mask.sum())


# ── Monte Carlo ───────────────────────────────────────────────────────────────


def monte_carlo_p5(returns: np.ndarray, n_sims: int = 10_000) -> float | None:
    """Bootstrap 5th-percentile Sharpe (same methodology as main backtest)."""
    n = len(returns)
    if n < 10:
        return None
    rng = np.random.default_rng(42)
    sims = []
    for _ in range(n_sims):
        sample = rng.choice(returns, size=n, replace=True)
        sh = sharpe(sample)
        if sh is not None:
            sims.append(sh)
    return round(float(np.percentile(sims, 5)), 3) if sims else None


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="New-layer sizing ablation on IS backtest trades")
    parser.add_argument("--trades", default=str(_TRADES_FILE), help="Path to backtest_trades_is.csv")
    parser.add_argument("--mc", action="store_true", help="Add Monte Carlo P5 column (slow: 10k sims × 5 configs)")
    parser.add_argument("--plot", action="store_true", help="Save sizing_ablation.png bar chart")
    args = parser.parse_args()

    trades_path = Path(args.trades)
    if not trades_path.exists():
        print(f"ERROR: trades file not found: {trades_path}")
        print("Generate it with:")
        print("  cd backend && python scripts/backtest_technicals.py --save-trades")
        sys.exit(1)

    trades = pd.read_csv(trades_path, parse_dates=["date"])
    print("\n# New-Layer Sizing Ablation — IS Backtest\n")
    print(f"> Loaded {len(trades)} IS trades from {trades_path.name}")

    # Validate required columns
    missing = {"net_pct", "quality_score"} - set(trades.columns)
    if missing:
        print(f"ERROR: missing columns: {missing}")
        print("Re-run backtest with: python scripts/backtest_technicals.py --save-trades")
        sys.exit(1)

    has_vix = "vix_entry" in trades.columns
    has_spy = "spy_trend_entry" in trades.columns
    has_ibs = any(c in trades.columns for c in ("ibs_entry", "ibs", "change_pct_entry", "change_pct"))

    if not has_vix:
        print("WARNING: vix_entry column missing — L9 will use neutral (1.0×) multiplier")
        print("  Re-run with the patched backtest to get L9 results\n")

    # ── Config matrix ─────────────────────────────────────────────────────────
    configs = [
        ("Baseline (equal weight)", False, False, False),
        ("+L8 quality_score tier", True, False, False),
        ("+L9 HMM-proxy regime", False, True, False),
        ("+L8 + L9 combined", True, True, False),
        ("+OFI_proxy filter only", False, False, True),
        ("+L8 + L9 + OFI_proxy", True, True, True),
    ]

    print("\n## Sizing Ablation — Sharpe / WR / N / Avg Ret / MaxDD\n")
    print(
        "> Size-weighted Sharpe = Sharpe of (net_pct × size_mult) series.\n"
        "> Larger than baseline → capital deployed more in high-quality trades.\n"
        "> OFI_proxy filters trades where ibs<0.20 on a DOWN day (distribution signal).\n"
    )

    headers = ["Configuration", "N", "WR%", "Avg Ret%", "Sharpe", "MaxDD%"]
    if args.mc:
        headers.append("MC P5")
    rows = []

    results: dict[str, dict] = {}

    for label, l8, l9, ofi in configs:
        weighted, n = apply_sizing(trades, use_l8=l8, use_l9=l9, use_ofi_proxy=ofi)
        if n < 5:
            rows.append([label, str(n), "—", "—", "—", "—"] + (["—"] if args.mc else []))
            continue
        sh = sharpe(weighted)
        wr = win_rate(weighted)
        ar = avg_ret(weighted)
        md = max_dd(weighted)
        mc_p5 = monte_carlo_p5(weighted) if args.mc else None

        results[label] = {"n": n, "sharpe": sh, "wr": wr, "avg": ar, "maxdd": md}

        row = [
            label,
            str(n),
            f"{wr:.1f}",
            f"{ar:+.3f}",
            fmt_sh(sh),
            f"{md:.2f}",
        ]
        if args.mc:
            row.append(fmt_sh(mc_p5))
        rows.append(row)

    print_table(headers, rows)

    # ── L8 tier breakdown ─────────────────────────────────────────────────────
    print("## L8 Quality Score Tier Breakdown\n")
    print(
        "> This shows WR and Sharpe by tier with the exact L8 multipliers applied.\n"
        "> High tier gets 1.30× size — verify the spread survives OOS.\n"
    )
    p33 = trades["quality_score"].quantile(0.33)
    p67 = trades["quality_score"].quantile(0.67)

    tier_rows = []
    for tier_label, sub_mask, mult in [
        (f"Low  (QS < {p33:.0f})  × 0.75", trades["quality_score"] < p33, 0.75),
        (
            f"Mid  ({p33:.0f}–{p67:.0f}) × 1.00",
            (trades["quality_score"] >= p33) & (trades["quality_score"] < p67),
            1.00,
        ),
        (f"High (QS ≥ {p67:.0f})  × 1.30", trades["quality_score"] >= p67, 1.30),
    ]:
        sub = trades[sub_mask]["net_pct"].values
        if len(sub) < 3:
            continue
        weighted = sub * mult
        tier_rows.append(
            [
                tier_label,
                str(len(sub)),
                f"{win_rate(sub):.1f}",
                f"{avg_ret(sub):+.3f}",
                fmt_sh(sharpe(sub)),
                fmt_sh(sharpe(weighted)),
                f"{mult:.2f}×",
            ]
        )

    print_table(
        ["Tier", "N", "WR%", "Avg Ret%", "Sharpe (EW)", "Sharpe (sized)", "Mult"],
        tier_rows,
    )

    # ── L9 regime breakdown ───────────────────────────────────────────────────
    if has_vix and has_spy:
        print("## L9 HMM-Proxy Regime Breakdown\n")
        l9_mults = [l9_multiplier(r.get("vix_entry"), r.get("spy_trend_entry", 0)) for _, r in trades.iterrows()]
        trades = trades.copy()
        trades.loc[:, "_l9_mult"] = l9_mults
        trades.loc[:, "_regime"] = trades["_l9_mult"].map({1.10: "bull", 0.85: "transition", 0.70: "bear"})

        regime_rows = []
        for regime_label, mult in [("bear  (× 0.70)", 0.70), ("transition (× 0.85)", 0.85), ("bull  (× 1.10)", 1.10)]:
            sub = trades[trades["_l9_mult"] == mult]["net_pct"].values
            if len(sub) < 3:
                continue
            weighted = sub * mult
            regime_rows.append(
                [
                    regime_label,
                    str(len(sub)),
                    f"{win_rate(sub):.1f}",
                    f"{avg_ret(sub):+.3f}",
                    fmt_sh(sharpe(sub)),
                    fmt_sh(sharpe(weighted)),
                ]
            )

        print_table(
            ["Regime", "N", "WR%", "Avg Ret%", "Sharpe (EW)", "Sharpe (sized)"],
            regime_rows,
        )
        print(
            "> Bear regime WR < 65% → L9 0.70× correctly reduces capital.\n"
            "> Bull regime WR > 75% → L9 1.10× correctly amplifies capital.\n"
            "> If bear WR ≥ 70% — the regime proxy is too aggressive; loosen VIX threshold.\n"
        )

    # ── OFI proxy analysis ────────────────────────────────────────────────────
    if has_ibs:
        print("## OFI Proxy Analysis (IBS-based daily filter)\n")
        print(
            "> Trades where ibs < 0.20 AND change_pct < 0 are 'distribution' signals.\n"
            "> Removing them should raise WR (these are trapped-short setups, not MR bounces).\n"
        )
        ofi_keep = np.array([ofi_proxy_keep(row) for _, row in trades.iterrows()])
        kept = trades[ofi_keep]["net_pct"].values
        removed_trades = trades[~ofi_keep]["net_pct"].values

        ofi_rows = [
            [
                "All trades (baseline)",
                str(len(trades)),
                f"{win_rate(trades['net_pct'].values):.1f}",
                fmt_sh(sharpe(trades["net_pct"].values)),
            ],
            ["OFI-keep trades", str(int(ofi_keep.sum())), f"{win_rate(kept):.1f}", fmt_sh(sharpe(kept))],
            [
                "OFI-removed (distribution)",
                str(int((~ofi_keep).sum())),
                f"{win_rate(removed_trades):.1f}" if len(removed_trades) > 0 else "—",
                fmt_sh(sharpe(removed_trades)) if len(removed_trades) > 3 else "—",
            ],
        ]
        print_table(["Group", "N", "WR%", "Sharpe"], ofi_rows)
        n_removed = int((~ofi_keep).sum())
        print(
            f"> OFI filter removes {n_removed} trades ({n_removed / len(trades) * 100:.1f}% of total).\n"
            "> If removed-group WR < 50% → filter is valid; if WR ≥ 60% → filter is too aggressive.\n"
        )

    # ── Incremental Sharpe summary ────────────────────────────────────────────
    print("## Incremental Sharpe Attribution\n")
    base_sh = results.get("Baseline (equal weight)", {}).get("sharpe")
    combined_sh = results.get("+L8 + L9 combined", {}).get("sharpe")
    full_sh = results.get("+L8 + L9 + OFI_proxy", {}).get("sharpe")

    if base_sh and combined_sh:
        print(f"  Baseline Sharpe:          {base_sh:.3f}")
        if results.get("+L8 quality_score tier", {}).get("sharpe"):
            l8_sh = results["+L8 quality_score tier"]["sharpe"]
            print(f"  +L8 only:                 {l8_sh:.3f}  ({l8_sh - base_sh:+.3f})")
        if results.get("+L9 HMM-proxy regime", {}).get("sharpe"):
            l9_sh = results["+L9 HMM-proxy regime"]["sharpe"]
            print(f"  +L9 only:                 {l9_sh:.3f}  ({l9_sh - base_sh:+.3f})")
        print(f"  +L8+L9 combined:          {combined_sh:.3f}  ({combined_sh - base_sh:+.3f})")
        if full_sh:
            print(f"  +L8+L9+OFI_proxy:         {full_sh:.3f}  ({full_sh - base_sh:+.3f})")
    print()

    # ── Optional bar chart ────────────────────────────────────────────────────
    if args.plot:
        try:
            import matplotlib.pyplot as plt

            labels_plot = [r[0].replace("+", "").strip() for r in rows if r[4] != "—"]
            sharpes_plot = [float(r[4]) for r in rows if r[4] != "—"]
            fig, ax = plt.subplots(figsize=(10, 5))
            colors = ["#4C8BBE" if s <= (sharpes_plot[0] if sharpes_plot else 0) else "#27AE60" for s in sharpes_plot]
            ax.barh(labels_plot, sharpes_plot, color=colors)
            ax.axvline(sharpes_plot[0] if sharpes_plot else 0, color="gray", linestyle="--", linewidth=1)
            ax.set_xlabel("Size-Weighted Sharpe")
            ax.set_title("IS Sizing Ablation: L8/L9/OFI Contributions")
            ax.invert_yaxis()
            plt.tight_layout()
            _plot_path = _DATA_DIR / "sizing_ablation.png"
            plt.savefig(_plot_path, dpi=120)
            print(f"[--plot] Saved chart to {_plot_path}")
        except ImportError:
            print("[--plot] matplotlib not installed — skipping chart")


if __name__ == "__main__":
    main()
