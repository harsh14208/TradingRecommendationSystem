"""
Pattern analysis on the latest 26-year backtest trades to identify live-engine improvements.
Reads data/backtest_trades_is.csv and prints actionable slices.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PARENT = _HERE.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

import pandas as pd

TRADES_PATH = _PARENT / "data" / "backtest_trades_is.csv"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "analysis_output"
OUTPUT_DIR.mkdir(exist_ok=True)


def stats(rets: pd.Series | list) -> dict:
    arr = pd.Series(rets).dropna()
    n = len(arr)
    if n == 0:
        return {"n": 0, "wr": 0.0, "avg": 0.0, "sharpe": None, "pf": None}
    wins = arr[arr > 0]
    losses = arr[arr <= 0]
    wr = len(wins) / n * 100
    avg = arr.mean()
    pf = wins.sum() / abs(losses.sum()) if losses.sum() != 0 else float("inf")
    std = arr.std(ddof=1)
    sharpe = avg / std if std > 0 else None
    return {
        "n": n,
        "wr": round(wr, 1),
        "avg": round(avg, 3),
        "sharpe": round(sharpe, 3) if sharpe is not None else None,
        "pf": round(pf, 2) if pf != float("inf") else None,
    }


def print_slice(title: str, groups):
    print(f"\n## {title}")
    rows = []
    for label, sub in groups:
        if isinstance(sub, pd.DataFrame):
            s = stats(sub["net_pct"])
        else:
            s = stats(sub)
        rows.append([label, s["n"], f"{s['wr']:.1f}%", f"{s['avg']:+.2f}%", s["sharpe"], s["pf"]])
    print(pd.DataFrame(rows, columns=["Bucket", "N", "WR", "Avg", "Sharpe", "PF"]).to_string(index=False))


def main():
    df = pd.read_csv(TRADES_PATH, parse_dates=["date"])
    df["year"] = df["date"].dt.year
    print(f"Loaded {len(df)} trades")

    baseline = stats(df["net_pct"])
    print(
        f"\nBaseline: N={baseline['n']}, WR={baseline['wr']}%, Avg={baseline['avg']:+.2f}%, Sharpe={baseline['sharpe']}"
    )

    # 1. Sector
    if "sector_etf" in df.columns:
        sector_groups = sorted(df["sector_etf"].dropna().unique())
        print_slice("Sector performance", [(s, df[df["sector_etf"] == s]) for s in sector_groups])

    # 2. Entry day-of-week
    dow_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri"}
    df["dow_name"] = df["dow"].map(dow_map)
    print_slice("Day-of-week", [(d, df[df["dow_name"] == d]) for d in ["Mon", "Tue", "Wed", "Thu", "Fri"]])

    # 3. Score band
    df["score_band"] = pd.cut(
        df["score"],
        bins=[44, 50, 55, 60, 999],
        labels=["45-50", "50-55", "55-60", "60+"],
        right=True,
    )
    print_slice("Score band", [(b, df[df["score_band"] == b]) for b in df["score_band"].cat.categories])

    # 4. VIX regime at entry
    def vix_bucket(v):
        if v < 15:
            return "<15"
        if v < 20:
            return "15-20"
        if v < 25:
            return "20-25"
        if v < 30:
            return "25-30"
        return ">=30"

    df["vix_bucket"] = df["vix_entry"].apply(vix_bucket)
    print_slice("VIX regime", [(b, df[df["vix_bucket"] == b]) for b in ["<15", "15-20", "20-25", "25-30", ">=30"]])

    # 5. Exit reason
    print_slice("Exit reason", [(r, df[df["exit_reason"] == r]) for r in df["exit_reason"].unique()])

    # 6. MR trigger
    if "mr_trigger" in df.columns:
        print_slice("MR trigger", [(t, df[df["mr_trigger"] == t]) for t in df["mr_trigger"].unique()])

    # 7. Quality score tier
    if "quality_score" in df.columns:
        qs = df["quality_score"].dropna()
        if len(qs) > 10:
            p33, p67 = qs.quantile([0.33, 0.67])
            print_slice(
                "Quality score tier",
                [
                    (f"Low (<{p33:.0f})", df[df["quality_score"] < p33]),
                    (f"Mid ({p33:.0f}-{p67:.0f})", df[(df["quality_score"] >= p33) & (df["quality_score"] < p67)]),
                    (f"High (>={p67:.0f})", df[df["quality_score"] >= p67]),
                ],
            )

    # 8. MAX effect
    if "max21" in df.columns:
        m = df["max21"].dropna()
        if len(m) > 10:
            p33, p67 = m.quantile([0.33, 0.67])
            print_slice(
                "MAX_21 (trailing max daily return)",
                [
                    (f"Low (<{p33:.1f}%)", df[df["max21"] < p33]),
                    (f"Mid ({p33:.1f}-{p67:.1f}%)", df[(df["max21"] >= p33) & (df["max21"] < p67)]),
                    (f"High (>={p67:.1f}%)", df[df["max21"] >= p67]),
                ],
            )

    # 9. ATR / vol tercile
    if "atr_pct" in df.columns:
        a = df["atr_pct"].dropna()
        if len(a) > 10:
            p33, p67 = a.quantile([0.33, 0.67])
            print_slice(
                "ATR% (volatility tercile)",
                [
                    (f"Low (<{p33:.1f}%)", df[df["atr_pct"] < p33]),
                    (f"Mid ({p33:.1f}-{p67:.1f}%)", df[(df["atr_pct"] >= p33) & (df["atr_pct"] < p67)]),
                    (f"High (>={p67:.1f}%)", df[df["atr_pct"] >= p67]),
                ],
            )

    # 10. Per-ticker edge (worst and best)
    print("\n## Worst 10 per-ticker Sharpe (min 2 trades)")
    tk = df.groupby("ticker").apply(
        lambda g: pd.Series(
            {**stats(g["net_pct"]), "sector_etf": g["sector_etf"].iloc[0] if "sector_etf" in g.columns else ""}
        )
    )
    tk2 = tk[tk["n"] >= 2]
    print(tk2.sort_values("sharpe").head(10)[["n", "wr", "avg", "sharpe", "pf", "sector_etf"]].to_string())

    print("\n## Best 10 per-ticker Sharpe (min 2 trades)")
    print(
        tk2.sort_values("sharpe", ascending=False)
        .head(10)[["n", "wr", "avg", "sharpe", "pf", "sector_etf"]]
        .to_string()
    )

    # 11. Recent vs historical per-ticker edge degradation
    print("\n## Tickers with positive historical edge but negative 2025+")
    historical = df[df["year"] < 2025].groupby("ticker").apply(lambda g: stats(g["net_pct"]))
    recent = df[df["year"] >= 2025].groupby("ticker").apply(lambda g: stats(g["net_pct"]))
    hist_df = pd.DataFrame(historical.tolist(), index=historical.index)
    rec_df = pd.DataFrame(recent.tolist(), index=recent.index)
    merged = hist_df.join(rec_df, lsuffix="_hist", rsuffix="_rec")
    degraded = merged[(merged["sharpe_hist"] > 0) & (merged["sharpe_rec"] < 0) & (merged["n_rec"] >= 1)]
    if not degraded.empty:
        print(degraded[["n_hist", "sharpe_hist", "n_rec", "sharpe_rec"]].to_string())
    else:
        print("None found")


if __name__ == "__main__":
    main()
