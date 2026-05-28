"""
§20 OOS Walk-Forward — Relaxed Global Params
=============================================
Same 5-window OOS design as §19, but with the §15f/§17f sector-specific
threshold stack removed.  Tests whether the BASE MR signal generalises OOS
before any sector tuning is applied.

§19 question left open:
  Is the 1/5-pass OOS result caused by sector-param overfit,
  or by the base MR edge being genuinely weaker than in-sample?

§20 config (relaxed global):
  thresh=35      vs §19 thresh=38
  ATR ceiling    REMOVED  (was §17f: ≤70)
  Return-jump    REMOVED  (was §17f: <-6%)
  VIX floor      NONE     (same as §19)
  hold=10        SAME

Interpretation:
  ≥3/5 pass → base signal is real; sector-specific params are the overfit source
  ≤1/5 pass → base MR edge is weaker than in-sample (regime shift or lucky IS)

Run from backend/:
    python scripts/run_section20_oos_relaxed.py
"""
import os
import sys
import math
import warnings
warnings.filterwarnings("ignore")

_HERE   = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _p in [_PARENT, _HERE]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np
import pandas as pd
import yfinance as yf

from backtest_technicals import (
    TICKERS, START, END,
    compute_indicators, compute_scores,
    simulate_ticker, stats, fmt_sharpe,
    fetch_spy_trend, fetch_stlfsi4,
)

# ── Relaxed global params — no sector-specific tuning, no §17f gates ─────────
FIXED_PARAMS = dict(
    mr_only                   = True,
    hold_days_override        = 10,
    buy_thresh_override       = 35,    # base discovery threshold (vs §19: 38)
    atr_pct_rank_min_override = 20.0,  # keep ATR minimum (structural quality floor)
    vix_min_override          = None,  # no VIX floor
    atr_pct_rank_max_override = None,  # ATR ceiling REMOVED (was §17f: ≤70)
    ret_jump_filter_override  = None,  # return-jump filter REMOVED (was §17f: <-6%)
)

OOS_WINDOWS = [
    ("2016-01-01", "2017-12-31"),
    ("2018-01-01", "2019-12-31"),
    ("2020-01-01", "2021-12-31"),
    ("2022-01-01", "2023-12-31"),
    ("2024-01-01", "2025-12-31"),
]

PASS_SHARPE = 1.0
PASS_N_MIN  = 5


def _ann_sharpe(sv: dict, n_years: float) -> float:
    sh = sv.get("sharpe") or 0.0
    n  = sv.get("n")      or 0
    if n < 2:
        return float("nan")
    return round(sh * math.sqrt(n / n_years), 2)


def _section(title: str) -> None:
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


def main() -> None:
    _section("§20 OOS Walk-Forward — Relaxed Global Params")
    print(f"  Universe  : {len(TICKERS)} tickers")
    print(f"  Params    : thresh=35, ATR≥20, no §17f gates, no VIX floor")
    print(f"  vs §19    : thresh=38, ATR [20,70], ret_jump<-6%")
    print(f"  Windows   : {len(OOS_WINDOWS)} × 2-year OOS")
    print(f"  Pass bar  : Ann.Sharpe ≥ {PASS_SHARPE} AND N ≥ {PASS_N_MIN}\n")

    _section("1. Market data (full 2006-2026)")
    print("  Downloading VIX …", flush=True)
    vix_raw = yf.download("^VIX", start=START, end=END, interval="1d",
                           auto_adjust=False, progress=False)
    if isinstance(vix_raw.columns, pd.MultiIndex):
        vix_raw.columns = vix_raw.columns.get_level_values(0)
    vix_full = {
        pd.Timestamp(str(k)[:10]): float(v)
        for k, v in (vix_raw["Close"] if "Close" in vix_raw.columns
                     else pd.Series(dtype=float)).items()
        if pd.notna(v)
    }
    print(f"  VIX ok ({len(vix_full)} bars)")

    spy_trend_full = fetch_spy_trend(START, END)
    print(f"  SPY ok ({len(spy_trend_full)} bars)")

    _fred_key = ""
    try:
        for line in open(os.path.join(_PARENT, ".env")):
            if line.startswith("FRED_API_KEY="):
                _fred_key = line.strip().split("=", 1)[1]
    except Exception:
        pass
    stlfsi4_full = fetch_stlfsi4(START, END, _fred_key)
    print(f"  STLFSI4 ok ({len(stlfsi4_full)} obs)" if stlfsi4_full
          else "  STLFSI4 skipped")

    _section("2. Download & prepare ticker data")
    print(f"  Downloading {len(TICKERS)} tickers …", flush=True)
    raw_all = yf.download(
        TICKERS, start=START, end=END,
        auto_adjust=True, progress=False, threads=True,
    )
    prepped: dict[str, pd.DataFrame] = {}
    for tkr in TICKERS:
        try:
            if isinstance(raw_all.columns, pd.MultiIndex):
                df = raw_all.xs(tkr, axis=1, level=1)[
                    ["Open", "High", "Low", "Close", "Volume"]].copy()
            else:
                df = raw_all[["Open", "High", "Low", "Close", "Volume"]].copy()
            df = df.ffill().dropna(subset=["Close", "Volume"])
            if len(df) < 250:
                print(f"  {tkr}: insufficient data — skipped")
                continue
            compute_indicators(df)
            df["score"] = compute_scores(df)
            if "vwap_pct" not in df.columns:
                df["vwap_pct"] = np.nan
            if "vwap_pct_prev" not in df.columns:
                df["vwap_pct_prev"] = df["vwap_pct"].shift(1)
            if "vwap_slope_pos" not in df.columns:
                df["vwap_slope_pos"] = False
            prepped[tkr] = df
        except Exception as e:
            print(f"  {tkr}: prep failed — {e}")
    print(f"  {len(prepped)} tickers prepared")

    _section("3. OOS Windows")
    hdr = (f"  {'Window':<20} {'N':>5} {'WR':>6} {'Avg':>7}"
           f" {'Sh/trade':>9} {'Ann.Sh':>7}  Verdict")
    sep = "  " + "─" * 68
    window_results: list[dict] = []

    for oos_start, oos_end in OOS_WINDOWS:
        ts_start = pd.Timestamp(oos_start)
        ts_end   = pd.Timestamp(oos_end)
        n_years  = (ts_end - ts_start).days / 365.25

        vix_w       = {k: v for k, v in vix_full.items()       if ts_start <= k <= ts_end}
        spy_trend_w = {k: v for k, v in spy_trend_full.items() if ts_start <= k <= ts_end}
        stlfsi4_w   = {k: v for k, v in stlfsi4_full.items()   if ts_start <= k <= ts_end}

        all_net: list[float] = []
        n_tickers_traded = 0

        for tkr, full_df in prepped.items():
            oos_df = full_df.loc[ts_start:ts_end].copy()
            if len(oos_df) < 20:
                continue
            try:
                trades = simulate_ticker(tkr, oos_df, vix_w, spy_trend_w, stlfsi4_w,
                                         **FIXED_PARAMS)
                if trades.empty:
                    continue
                all_net.extend(trades["net_pct"].tolist())
                n_tickers_traded += 1
            except Exception as e:
                print(f"    [{tkr}] error in window {oos_start}: {e}")

        if not all_net:
            window_results.append({"window": f"{oos_start[:4]}–{oos_end[:4]}",
                                   "n": 0, "ann_sharpe": float("nan"), "passed": False})
            print(sep)
            print(f"  {oos_start[:4]}–{oos_end[:4]:<16} {'0':>5}  (no trades)")
            continue

        sv      = stats(all_net)
        ann_sh  = _ann_sharpe(sv, n_years)
        passed  = (sv.get("n", 0) >= PASS_N_MIN and
                   not math.isnan(ann_sh) and ann_sh >= PASS_SHARPE)
        verdict = "✓ PASS" if passed else "✗ FAIL"

        wr  = sv.get("wr")     or 0.0
        avg = sv.get("avg")    or 0.0
        sh  = sv.get("sharpe") or 0.0

        window_results.append({
            "window":     f"{oos_start[:4]}–{oos_end[:4]}",
            "n":          sv.get("n", 0),
            "wr":         wr,
            "avg":        avg,
            "sharpe":     sh,
            "ann_sharpe": ann_sh,
            "passed":     passed,
            "n_tickers":  n_tickers_traded,
        })

        if len(window_results) == 1:
            print(hdr)
            print(sep)

        print(f"  {oos_start[:4]}–{oos_end[:4]:<16} {sv['n']:>5} {wr:>5.1f}%"
              f" {avg:>+6.2f}% {fmt_sharpe(sh):>9} {ann_sh:>7.2f}  {verdict}")

    _section("4. Verdict")
    n_passed  = sum(1 for r in window_results if r.get("passed"))
    n_total   = len(window_results)
    threshold = math.ceil(n_total * 0.6)
    edge_real = n_passed >= threshold

    print(f"\n  OOS windows passed : {n_passed} / {n_total}")
    print(f"  Threshold          : ≥ {threshold} / {n_total} (60%)\n")

    if edge_real:
        print(f"  ✓ BASE SIGNAL GENERALISES — {n_passed}/{n_total} OOS windows pass.")
        print(f"    The §15f/§17f SECTOR-SPECIFIC threshold stack was the overfit source.")
        print(f"    The core MR edge is real. Recommendation: simplify _SECTOR_MR_CONFIG,")
        print(f"    rely on global ATR≥20 quality filter rather than per-sector VIX/thresh.")
    else:
        print(f"  ✗ BASE SIGNAL ALSO WEAK — only {n_passed}/{n_total} OOS windows pass.")
        print(f"    The core MR edge itself is weaker than in-sample (not just sector overfit).")
        print(f"    Possible causes: regime shift post-2016, or IS results were partially lucky.")
        print(f"    Recommendation: accept lower expected live Sharpe (~0.3-0.5 per trade).")

    print(f"\n  Window detail:")
    for r in window_results:
        sym   = "✓" if r.get("passed") else "✗"
        ann_s = (f"{r['ann_sharpe']:.2f}"
                 if not math.isnan(r.get("ann_sharpe", float("nan"))) else "n/a")
        print(f"    {sym} {r['window']}  N={r.get('n',0):>4}  "
              f"WR={r.get('wr',0):>5.1f}%  Avg={r.get('avg',0):>+5.2f}%  "
              f"Ann.Sh={ann_s}")

    print(f"\n  §19 comparison (thresh=38, §17f gates ON, 56 tickers):")
    s19 = [
        ("2016–2017", 13, 69.2, +0.98, 0.94),
        ("2018–2019", 20, 60.0, +1.41, 1.18),
        ("2020–2021", 26, 50.0, +0.79, 0.74),
        ("2022–2023",  8, 62.5, +1.51, 0.97),
        ("2024–2025",  9, 44.4, +0.22, 0.11),
    ]
    for w, n19, wr19, avg19, ann19 in s19:
        r20 = next((r for r in window_results if r["window"] == w), None)
        ann20 = (f"{r20['ann_sharpe']:.2f}"
                 if r20 and not math.isnan(r20.get("ann_sharpe", float("nan")))
                 else "n/a")
        n20  = r20["n"] if r20 else 0
        delta = (r20["ann_sharpe"] - ann19
                 if r20 and not math.isnan(r20.get("ann_sharpe", float("nan")))
                 else float("nan"))
        d_str = f"{delta:+.2f}" if not math.isnan(delta) else "n/a"
        print(f"    {w}  §19 N={n19:>3} Ann={ann19:.2f}  →  "
              f"§20 N={n20:>3} Ann={ann20}  (Δ={d_str})")


if __name__ == "__main__":
    main()
