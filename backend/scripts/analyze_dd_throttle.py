"""
DD-throttle performance analysis across the full 26-year backtest.
Loads data/mr_trades.csv and compares baseline vs DD-throttle portfolio simulation.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PARENT = _HERE.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

import numpy as np
import pandas as pd
from scripts.backtest_technicals import run_portfolio_simulation

TRADES_PATH = _PARENT / "data" / "backtest_trades_is.csv"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "analysis_output"
OUTPUT_DIR.mkdir(exist_ok=True)


def _build_equity_df(equity_log: list) -> pd.DataFrame:
    df = pd.DataFrame(equity_log, columns=["date", "capital"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    df["daily_ret"] = df["capital"].pct_change()
    df["peak"] = df["capital"].cummax()
    df["dd_pct"] = (df["capital"] - df["peak"]) / df["peak"] * 100
    return df


def _annual_metrics(eq: pd.DataFrame) -> pd.DataFrame:
    eq = eq.copy()
    eq["year"] = eq["date"].dt.year
    rows = []
    for yr, g in eq.groupby("year"):
        if len(g) < 2:
            continue
        start = g["capital"].iloc[0]
        end = g["capital"].iloc[-1]
        ret = (end / start - 1) * 100
        peak = g["peak"].max()
        max_dd = g["dd_pct"].min()
        rows.append({"year": yr, "start": start, "end": end, "return_pct": ret, "max_dd_pct": max_dd, "peak": peak})
    return pd.DataFrame(rows)


def _max_dd_events(eq: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    eq = eq.copy().reset_index(drop=True)
    eq["is_new_peak"] = eq["capital"] >= eq["capital"].cummax()
    # Find drawdown troughs
    troughs = eq.loc[eq["dd_pct"].groupby((eq["dd_pct"] != eq["dd_pct"].shift()).cumsum()).idxmin()]
    return troughs.nsmallest(n, "dd_pct")[["date", "capital", "peak", "dd_pct"]]


def main():
    trades = pd.read_csv(TRADES_PATH, parse_dates=["date"])
    print(f"Loaded {len(trades)} trades from {TRADES_PATH}")

    baseline = run_portfolio_simulation(trades, max_concurrent=5, dd_throttle=False, quiet=True)
    throttle = run_portfolio_simulation(
        trades, max_concurrent=5, dd_throttle=True, dd_trig=3.0, throttle_mult=0.5, quiet=True
    )

    eq_base = _build_equity_df(baseline["equity_log"])
    eq_thr = _build_equity_df(throttle["equity_log"])

    # Annual comparison
    ann_base = _annual_metrics(eq_base)
    ann_thr = _annual_metrics(eq_thr)
    ann_comp = ann_base.merge(ann_thr, on="year", suffixes=("_base", "_thr"))
    ann_comp = ann_comp.sort_values("year")

    print("\n## Annual returns: Baseline vs DD-throttle")
    print(
        ann_comp[["year", "return_pct_base", "return_pct_thr", "max_dd_pct_base", "max_dd_pct_thr"]].to_string(
            index=False
        )
    )

    # Overall summary
    print("\n## 26-year summary")
    for label, sim, eq in [("Baseline", baseline, eq_base), ("DD-throttle", throttle, eq_thr)]:
        print(f"\n{label}:")
        print(f"  CAGR: {sim['cagr']:+.2f}%")
        print(f"  Ann Sharpe: {sim['ann_sharpe']:.2f}")
        print(f"  Max DD: {sim['max_dd']:.2f}%")
        print(f"  Final capital: ${eq['capital'].iloc[-1]:,.0f}")

    # Drawdown events
    print("\n## Largest drawdown events — Baseline")
    print(_max_dd_events(eq_base).to_string(index=False))
    print("\n## Largest drawdown events — DD-throttle")
    print(_max_dd_events(eq_thr).to_string(index=False))

    # Throttle frequency
    eq_thr["throttle_active"] = eq_thr["dd_pct"] < -3.0
    throttle_days = eq_thr["throttle_active"].sum()
    total_days = len(eq_thr)
    print(f"\nDD-throttle active on {throttle_days} / {total_days} days ({throttle_days / total_days * 100:.1f}%)")

    # Save CSVs
    ann_comp.to_csv(OUTPUT_DIR / "dd_throttle_annual.csv", index=False)
    eq_base.to_csv(OUTPUT_DIR / "dd_throttle_equity_baseline.csv", index=False)
    eq_thr.to_csv(OUTPUT_DIR / "dd_throttle_equity_throttle.csv", index=False)
    print(f"\nSaved CSVs to {OUTPUT_DIR}")

    # Plot
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)

        # Equity curves
        ax = axes[0]
        ax.plot(eq_base["date"], eq_base["capital"], label="Baseline", linewidth=1.2)
        ax.plot(eq_thr["date"], eq_thr["capital"], label="DD-throttle", linewidth=1.2)
        ax.set_ylabel("Capital ($)")
        ax.set_title("Portfolio Equity: Baseline vs DD-throttle (26-year, $10k start)")
        ax.legend(loc="upper left")
        ax.grid(True, alpha=0.3)

        # Drawdowns
        ax = axes[1]
        ax.fill_between(eq_base["date"], eq_base["dd_pct"], 0, alpha=0.4, label="Baseline DD")
        ax.fill_between(eq_thr["date"], eq_thr["dd_pct"], 0, alpha=0.4, label="DD-throttle DD")
        ax.axhline(-3, color="red", linestyle="--", linewidth=0.8, label="Throttle trigger (-3%)")
        ax.set_ylabel("Drawdown (%)")
        ax.set_title("Portfolio Drawdown")
        ax.legend(loc="lower left")
        ax.grid(True, alpha=0.3)

        # Annual returns comparison
        ax = axes[2]
        x = np.arange(len(ann_comp))
        width = 0.35
        ax.bar(x - width / 2, ann_comp["return_pct_base"], width, label="Baseline")
        ax.bar(x + width / 2, ann_comp["return_pct_thr"], width, label="DD-throttle")
        ax.set_xticks(x)
        ax.set_xticklabels(ann_comp["year"], rotation=45)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_ylabel("Annual return (%)")
        ax.set_title("Annual Return Comparison")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        plot_path = OUTPUT_DIR / "dd_throttle_26yr.png"
        plt.savefig(plot_path, dpi=150)
        print(f"Saved plot to {plot_path}")
    except Exception as e:
        print(f"Plotting skipped: {e}")


if __name__ == "__main__":
    main()
