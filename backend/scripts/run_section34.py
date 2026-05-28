"""
run_section34.py — Time-Loss Reduction Experiments

The 20-year backtest shows 118 time_loss exits (32% of all trades, 0% WR,
avg −2.31%). Adaptive exits are the opposite: 35 trades, 100% WR, +2.98% avg.
Goal: shrink time_loss by catching "thesis-failed" trades earlier without
hurting winners.

§34a  Diagnostic   — time_loss breakdown by score bucket / exit day / sector
§34b  Fail-fast    — lower MAX_LOSS_DAYS from 4 to 2 or 3
§34c  No-progress  — exit day N if price < entry×1.003 AND RSI ≤ 50
§34d  Score-seg    — high-score (≥50) hold=10, low-score (40-49) hold=5
§34e  Combined     — best fail-fast + no-progress together

Universe: 24-ticker production set (matches §19/§20 OOS study).
Expected runtime: ~4-8 minutes.

Usage:
    cd backend
    python scripts/run_section34.py 2>&1 | tee /tmp/decomp_s34.log
"""

from __future__ import annotations

import os
import sys
import warnings

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _p in [_PARENT, _HERE]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from backtest_technicals import (
    END,
    HOLD_DAYS,
    MAX_LOSS_DAYS,
    START,
    compute_indicators,
    compute_scores,
    fetch_spy_trend,
    fetch_stlfsi4,
    fmt_sharpe,
    print_table,
    simulate_ticker,
    stats,
)

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

# 24-ticker production universe (§19/§20)
UNIVERSE = [
    "AAPL",
    "MSFT",
    "AMZN",
    "GOOGL",
    "META",
    "NVDA",
    "AMD",
    "TSLA",
    "NFLX",
    "CRM",
    "JPM",
    "GS",
    "MA",
    "V",
    "XOM",
    "COP",
    "UNH",
    "LLY",
    "HD",
    "NKE",
    "BA",
    "CAT",
    "NEE",
    "AMT",
]

# MR-only base config matching live engine (§16 best)
BASE_CFG = dict(
    mr_only=True,
    hold_days_override=HOLD_DAYS,
    buy_thresh_override=40,
    atr_pct_rank_min_override=20.0,
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _download(ticker: str) -> pd.DataFrame | None:
    raw = yf.download(ticker, start=START, end=END, interval="1d", auto_adjust=True, progress=False)
    if raw.empty or len(raw) < 250:
        return None
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    df = raw[["Open", "High", "Low", "Close", "Volume"]].copy()
    df = df.ffill().dropna(subset=["Close", "Volume"])
    compute_indicators(df)
    df["score"] = compute_scores(df)
    if "vwap_pct" not in df.columns:
        df["vwap_pct"] = float("nan")
    if "vwap_pct_prev" not in df.columns:
        df["vwap_pct_prev"] = df["vwap_pct"].shift(1)
    if "vwap_slope_pos" not in df.columns:
        df["vwap_slope_pos"] = False
    return df


def _run_universe(dfs, vix, spy, stlfsi4, **overrides) -> pd.DataFrame:
    all_trades = []
    for ticker, df in dfs.items():
        t = simulate_ticker(ticker, df, vix, spy, stlfsi4, **{**BASE_CFG, **overrides})
        if not t.empty:
            all_trades.append(t)
    return pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()


def _summary(label: str, df: pd.DataFrame, hold: int = HOLD_DAYS) -> dict:
    if df.empty:
        return {"label": label, "n": 0}
    rets = df["net_pct"].tolist()
    s = stats(rets)
    ann = round(s["sharpe"] * (252 / hold) ** 0.5, 2) if s["sharpe"] else None
    reasons = df["exit_reason"].value_counts().to_dict()
    tl = reasons.get("time_loss", 0) + reasons.get("no_progress", 0)
    adapt = reasons.get("adaptive", 0)
    return {
        "label": label,
        "n": s["n"],
        "wr": s["wr"],
        "avg": s["avg"],
        "ann_sharpe": ann,
        "max_dd": s["max_dd"],
        "time_loss": tl,
        "adaptive": adapt,
        "tl_pct": round(tl / s["n"] * 100, 1) if s["n"] else 0,
    }


def _section(title: str) -> None:
    print(f"\n## {title}\n")


def _print_summary_table(rows: list[dict]) -> None:
    headers = ["Label", "N", "WR", "Avg", "Ann.Sh", "MaxDD", "TL#", "TL%", "Adapt#"]
    table = []
    for r in rows:
        if r.get("n", 0) == 0:
            table.append([r["label"]] + ["—"] * 8)
            continue
        table.append(
            [
                r["label"],
                r["n"],
                f"{r['wr']:.1f}%" if r["wr"] is not None else "—",
                f"{r['avg']:+.2f}%" if r["avg"] is not None else "—",
                fmt_sharpe(r["ann_sharpe"]),
                f"-{r['max_dd']:.2f}%" if r["max_dd"] is not None else "—",
                r.get("time_loss", "—"),
                f"{r.get('tl_pct', 0):.1f}%",
                r.get("adaptive", "—"),
            ]
        )
    print_table(headers, table)


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    print("# §34 — Time-Loss Reduction Experiments\n")
    print(f"> Period: {START} → {END}  |  MR-only  |  24-ticker production universe\n")
    print(f"> Baseline: MAX_LOSS_DAYS={MAX_LOSS_DAYS}, HOLD_DAYS={HOLD_DAYS}\n")

    # ── Alt data ─────────────────────────────────────────────────────────────
    print("Fetching VIX…", end=" ", flush=True)
    try:
        v = yf.download("^VIX", start=START, end=END, interval="1d", auto_adjust=False, progress=False)
        if isinstance(v.columns, pd.MultiIndex):
            v.columns = v.columns.get_level_values(0)
        vix = {pd.Timestamp(str(k)[:10]): float(val) for k, val in v["Close"].items() if pd.notna(val)}
        print(f"ok ({len(vix)} bars)")
    except Exception as e:
        vix = {}
        print(f"failed ({e})")

    print("Fetching SPY trend…", end=" ", flush=True)
    spy = fetch_spy_trend(START, END)
    print(f"ok ({len(spy)} bars)")

    print("Fetching STLFSI4…", end=" ", flush=True)
    stlfsi4 = fetch_stlfsi4(START, END, FRED_API_KEY)
    print(f"ok ({len(stlfsi4)} bars)" if stlfsi4 else "skipped (no API key)")

    # ── Download universe ─────────────────────────────────────────────────────
    dfs: dict[str, pd.DataFrame] = {}
    print(f"\nDownloading {len(UNIVERSE)} tickers…")
    for t in UNIVERSE:
        print(f"  {t}…", end=" ", flush=True)
        d = _download(t)
        if d is not None:
            dfs[t] = d
            print(f"ok ({len(d)} bars)")
        else:
            print("skip")

    if not dfs:
        print("No data — aborting.")
        return

    # ─────────────────────────────────────────────────────────────────────────
    # §34a — Diagnostic: time_loss breakdown
    # ─────────────────────────────────────────────────────────────────────────
    _section("§34a — Time-Loss Diagnostic")
    print("> Running baseline to collect time_loss trades for breakdown…\n")

    baseline_df = _run_universe(dfs, vix, spy, stlfsi4)
    baseline_sum = _summary("Baseline", baseline_df)
    _print_summary_table([baseline_sum])

    if not baseline_df.empty:
        tl = baseline_df[baseline_df["exit_reason"] == "time_loss"].copy()
        print(f"\n### time_loss sub-population (N={len(tl)})")

        # Exit day distribution
        if "exit_day" in tl.columns:
            print("\n#### By exit day")
            day_tbl = []
            for day in sorted(tl["exit_day"].unique()):
                sub = tl[tl["exit_day"] == day]
                day_tbl.append(
                    [
                        f"Day {day}",
                        len(sub),
                        f"{sub['net_pct'].mean():+.2f}%",
                        f"{(sub['net_pct'] > 0).mean() * 100:.1f}%",
                    ]
                )
            print_table(["Exit Day", "N", "Avg Ret", "WR"], day_tbl)

        # Score bucket distribution
        if "score" in tl.columns:
            print("\n#### By score bucket")
            score_tbl = []
            for lo, hi, label in [(30, 45, "30-44"), (45, 50, "45-49"), (50, 60, "50-59"), (60, 100, "60+")]:
                sub = tl[(tl["score"] >= lo) & (tl["score"] < hi)]
                if sub.empty:
                    continue
                score_tbl.append(
                    [
                        label,
                        len(sub),
                        f"{len(sub) / len(tl) * 100:.1f}%",
                        f"{sub['net_pct'].mean():+.2f}%",
                    ]
                )
            print_table(["Score", "N", "% of TL", "Avg Ret"], score_tbl)

        # Ticker distribution (top 10 offenders)
        if "ticker" in tl.columns:
            print("\n#### Top 10 tickers by time_loss count")
            tc = (
                tl.groupby("ticker")
                .agg(
                    n=("net_pct", "count"),
                    avg_ret=("net_pct", "mean"),
                )
                .sort_values("n", ascending=False)
                .head(10)
            )
            ticker_tbl = []
            for ticker, row in tc.iterrows():
                ticker_tbl.append([ticker, row["n"], f"{row['avg_ret']:+.2f}%"])
            print_table(["Ticker", "TL trades", "Avg Ret"], ticker_tbl)

    # ─────────────────────────────────────────────────────────────────────────
    # §34b — Fail-fast: lower MAX_LOSS_DAYS
    # ─────────────────────────────────────────────────────────────────────────
    _section("§34b — Fail-Fast (lower MAX_LOSS_DAYS)")
    print("> Hypothesis: cutting time_loss trigger from day 4 to day 2 or 3 reduces")
    print("> the drag without hurting trades that need a day or two to set up.\n")

    ff_rows = [baseline_sum]
    for mld in [2, 3]:
        df = _run_universe(dfs, vix, spy, stlfsi4, max_loss_days_override=mld)
        ff_rows.append(_summary(f"MLD={mld}", df))

    _print_summary_table(ff_rows)

    print("\n> Key: does WR / avg improve when we exit failing trades sooner?")
    print("> Watch TL# — it should drop; watch WR and Avg — they should rise or hold.")

    # ─────────────────────────────────────────────────────────────────────────
    # §34c — No-progress exit
    # ─────────────────────────────────────────────────────────────────────────
    _section("§34c — No-Progress Exit (price < entry×1.003 AND RSI ≤ 50 by day N)")
    print("> Hypothesis: trades that haven't gained ≥0.3% by day N with flat RSI")
    print("> are stuck, not bouncing. Exit them before the full hold expires.\n")
    print("> This is a complement to fail-fast: fires on flat/stuck trades,")
    print("> not just clearly-losing trades.\n")

    np_rows = [baseline_sum]
    for npd in [3, 4, 5]:
        df = _run_universe(dfs, vix, spy, stlfsi4, no_progress_days=npd)
        np_rows.append(_summary(f"NP@day{npd}", df))

    _print_summary_table(np_rows)

    # Break down exit_reason mix for best no-progress variant
    print("\n#### No-progress exit reason breakdown")
    for npd in [3, 4, 5]:
        df = _run_universe(dfs, vix, spy, stlfsi4, no_progress_days=npd)
        if not df.empty:
            rc = df["exit_reason"].value_counts()
            print(f"  NP@day{npd}: " + "  ".join(f"{k}={v}" for k, v in rc.items()))

    # ─────────────────────────────────────────────────────────────────────────
    # §34d — Score-segmented hold
    # ─────────────────────────────────────────────────────────────────────────
    _section("§34d — Score-Segmented Hold (high-score=hold10, low-score=hold5)")
    print("> Hypothesis: high-confidence MR setups need the full hold to complete,")
    print("> but low-confidence ones are wasting days 6-10 as dead weight.\n")
    print("> Method: split universe by entry score, run each half independently.\n")

    # Collect all baseline trades with scores
    if not baseline_df.empty and "score" in baseline_df.columns:
        hi_tickers = set()
        lo_tickers = set()

        # Identify which tickers have score ≥50 trades more often than not
        # (rough proxy — we'll run the full split both ways)
        # Run high-score bucket: trades where score >= 50, full hold
        hi_df_list = []
        lo_df_list = []
        for ticker, df in dfs.items():
            t_base = simulate_ticker(ticker, df, vix, spy, stlfsi4, **BASE_CFG)
            if t_base.empty:
                continue
            # High-score: score ≥ 50 → use full hold (no change)
            # Low-score: score 40-49 → hold=5
            # We can't filter by score inside simulate_ticker, but we can compare
            # the two hold variants and observe where the difference concentrates.
            hi_df_list.append(t_base[t_base["score"] >= 50])
            lo_base = t_base[t_base["score"] < 50]
            lo_df_list.append(lo_base)

        hi_df = pd.concat(hi_df_list, ignore_index=True) if hi_df_list else pd.DataFrame()
        lo_df_base = pd.concat(lo_df_list, ignore_index=True) if lo_df_list else pd.DataFrame()

        # Now run the low-score group with hold=5
        lo_short_list = []
        for ticker, df in dfs.items():
            t_short = simulate_ticker(ticker, df, vix, spy, stlfsi4, **{**BASE_CFG, "hold_days_override": 5})
            if t_short.empty:
                continue
            lo_short_list.append(t_short[t_short["score"] < 50])
        lo_df_short = pd.concat(lo_short_list, ignore_index=True) if lo_short_list else pd.DataFrame()

        print("### High-score (≥50) — full hold=10")
        _print_summary_table([_summary("HI: hold=10", hi_df)])

        print("\n### Low-score (40-49) — baseline hold=10 vs shortened hold=5")
        seg_rows = [
            _summary("LO: hold=10 (baseline)", lo_df_base),
            _summary("LO: hold=5  (shorter)", lo_df_short),
        ]
        _print_summary_table(seg_rows)

        print("\n> If LO hold=5 beats LO hold=10: use score-adaptive hold in live engine.")
    else:
        print("  (skipped — no baseline trades to segment)")

    # ─────────────────────────────────────────────────────────────────────────
    # §34e — Combined best
    # ─────────────────────────────────────────────────────────────────────────
    _section("§34e — Combined: best fail-fast + no-progress")
    print("> Combine the two best single-tweak variants to test additive benefit.\n")

    # Pick best MLD and best NPD from §34b/c results
    # Hard-coded to the candidates most likely to win; adjust after reviewing §34b/c
    combos = [
        ("MLD=3 + NP@day4", dict(max_loss_days_override=3, no_progress_days=4)),
        ("MLD=3 + NP@day3", dict(max_loss_days_override=3, no_progress_days=3)),
        ("MLD=2 + NP@day3", dict(max_loss_days_override=2, no_progress_days=3)),
    ]

    combo_rows = [baseline_sum]
    for label, overrides in combos:
        df = _run_universe(dfs, vix, spy, stlfsi4, **overrides)
        combo_rows.append(_summary(label, df))

    _print_summary_table(combo_rows)

    # ─────────────────────────────────────────────────────────────────────────
    # Final summary
    # ─────────────────────────────────────────────────────────────────────────
    _section("§34 — Summary")
    print("Key metrics to read:")
    print("  Ann.Sharpe  — overall risk-adjusted performance (higher = better)")
    print("  TL%         — fraction of trades exiting as time_loss (lower = better)")
    print("  Avg         — mean net return per trade (higher = better)")
    print("  WR          — win rate (generally should not drop more than 1-2pp)\n")
    print("Decision criteria:")
    print("  1. Ann.Sharpe improves OR holds flat → keep the change")
    print("  2. TL% drops meaningfully (>5pp)    → confirms thesis-fail detection works")
    print("  3. Avg improves                     → not just eliminating losers but improving winners")
    print("  4. N should not drop more than 15%  → not over-filtering entries\n")
    print("If combined §34e beats standalone §34b and §34c:")
    print("  → Implement both max_loss_days and no_progress_days in live signal_engine.py")
    print("  → Add score-segmented hold if §34d shows meaningful LO improvement\n")


if __name__ == "__main__":
    main()
