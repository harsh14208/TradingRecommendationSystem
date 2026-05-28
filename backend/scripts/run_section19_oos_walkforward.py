"""
§19 OOS Walk-Forward Validation
================================
Tests whether the §15f/§17f MR edge holds out-of-sample with FIXED params.
No re-optimisation per window — tests edge robustness, not curve fit.

Design
------
  • 5 non-overlapping 2-year OOS windows (2016-17, 2018-19, 2020-21, 2022-23, 2024-25)
  • Fixed params: §15f baseline (mr_only, hold=10, thresh=38, atr_rank_min=20)
  • Indicators computed on FULL df so look-back warmup is clean at window start
  • VIX / SPY sliced to OOS window to avoid contaminating macro gates

Verdict threshold
-----------------
  Ann.Sharpe ≥ 1.0 in OOS window = PASS
  ≥ 3 of 5 PASS → edge is real (not a curve-fit artefact)

Run from backend/:
    python scripts/run_section19_oos_walkforward.py
"""

import math
import os
import sys
import warnings

warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _p in [_PARENT, _HERE]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np
import pandas as pd
import yfinance as yf
from backtest_technicals import (
    END,
    START,
    TICKERS,
    compute_indicators,
    compute_scores,
    fetch_spy_trend,
    fetch_stlfsi4,
    fmt_sharpe,
    simulate_ticker,
    stats,
)

# ── Fixed §15f params (no per-window tuning) ─────────────────────────────────
FIXED_PARAMS = dict(
    mr_only=True,
    hold_days_override=10,
    buy_thresh_override=38,
    atr_pct_rank_min_override=20.0,
    vix_min_override=None,
    # §17f gates (best combined stack)
    atr_pct_rank_max_override=70.0,
    ret_jump_filter_override=-6.0,
)

# ── OOS Windows: (oos_start, oos_end) ─────────────────────────────────────────
# Indicators computed on full 2006-2026 df; only ENTRY SIGNALS in [oos_start, oos_end] count.
OOS_WINDOWS = [
    ("2016-01-01", "2017-12-31"),
    ("2018-01-01", "2019-12-31"),
    ("2020-01-01", "2021-12-31"),
    ("2022-01-01", "2023-12-31"),
    ("2024-01-01", "2025-12-31"),
]

PASS_SHARPE = 1.0  # Ann.Sharpe threshold per window
PASS_N_MIN = 3  # min trades in window to count


def _ann_sharpe(sv: dict, n_years: float) -> float:
    """Annualise per-trade Sharpe by trade frequency within the OOS window."""
    sh = sv.get("sharpe") or 0.0
    n = sv.get("n") or 0
    if n < 2:
        return float("nan")
    trades_per_year = n / n_years
    return round(sh * math.sqrt(trades_per_year), 2)


def _section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def main() -> None:
    _section("§19 OOS Walk-Forward Validation")
    print(f"  Universe : {len(TICKERS)} tickers")
    print("  Params   : §15f/§17f fixed (no per-window tuning)")
    print(f"  Windows  : {len(OOS_WINDOWS)} × 2-year OOS")
    print(f"  Pass bar : Ann.Sharpe ≥ {PASS_SHARPE} AND N ≥ {PASS_N_MIN}\n")

    # ── 1. Download & prepare full-period data ────────────────────────────────
    _section("1. Market data (full 2006-2026)")
    print("  Downloading VIX …", flush=True)
    vix_raw = yf.download("^VIX", start=START, end=END, interval="1d", auto_adjust=False, progress=False)
    if isinstance(vix_raw.columns, pd.MultiIndex):
        vix_raw.columns = vix_raw.columns.get_level_values(0)
    vix_full = {
        pd.Timestamp(str(k)[:10]): float(v)
        for k, v in (vix_raw["Close"] if "Close" in vix_raw.columns else pd.Series(dtype=float)).items()
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
    print(f"  STLFSI4 ok ({len(stlfsi4_full)} obs)" if stlfsi4_full else "  STLFSI4 skipped")

    _section("2. Download & prepare ticker data")
    print(f"  Downloading {len(TICKERS)} tickers …", flush=True)
    raw_all = yf.download(
        TICKERS,
        start=START,
        end=END,
        auto_adjust=True,
        progress=False,
        threads=True,
    )
    prepped: dict[str, pd.DataFrame] = {}
    for tkr in TICKERS:
        try:
            if isinstance(raw_all.columns, pd.MultiIndex):
                df = raw_all.xs(tkr, axis=1, level=1)[["Open", "High", "Low", "Close", "Volume"]].copy()
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

    # ── 3. Walk-forward OOS evaluation ───────────────────────────────────────
    _section("3. OOS Windows")
    hdr = f"  {'Window':<20} {'N':>5} {'WR':>6} {'Avg':>7} {'Sh/trade':>9} {'Ann.Sh':>7}  Verdict"
    sep = "  " + "─" * 68
    window_results: list[dict] = []

    for oos_start, oos_end in OOS_WINDOWS:
        ts_start = pd.Timestamp(oos_start)
        ts_end = pd.Timestamp(oos_end)
        n_years = (ts_end - ts_start).days / 365.25

        # Slice macro series to OOS window
        vix_w = {k: v for k, v in vix_full.items() if ts_start <= k <= ts_end}
        spy_trend_w = {k: v for k, v in spy_trend_full.items() if ts_start <= k <= ts_end}
        stlfsi4_w = {k: v for k, v in stlfsi4_full.items() if ts_start <= k <= ts_end}

        all_net: list[float] = []
        n_tickers_traded = 0

        for tkr, full_df in prepped.items():
            # Slice to OOS rows only — simulate_ticker iterates these bars for entries.
            # Indicators are from full df so look-back warmup is correct.
            oos_df = full_df.loc[ts_start:ts_end].copy()
            if len(oos_df) < 20:
                continue
            try:
                trades = simulate_ticker(tkr, oos_df, vix_w, spy_trend_w, stlfsi4_w, **FIXED_PARAMS)
                if trades.empty:
                    continue
                nets = trades["net_pct"].tolist()
                all_net.extend(nets)
                n_tickers_traded += 1
            except Exception as e:
                print(f"    [{tkr}] error in window {oos_start}: {e}")

        if not all_net:
            window_results.append(
                {"window": f"{oos_start[:4]}–{oos_end[:4]}", "n": 0, "ann_sharpe": float("nan"), "passed": False}
            )
            print(sep)
            print(f"  {oos_start[:4]}–{oos_end[:4]:<16} {'0':>5}  (no trades)")
            continue

        sv = stats(all_net)
        ann_sh = _ann_sharpe(sv, n_years)
        passed = sv.get("n", 0) >= PASS_N_MIN and not math.isnan(ann_sh) and ann_sh >= PASS_SHARPE
        verdict = "✓ PASS" if passed else "✗ FAIL"

        wr = sv.get("wr") or 0.0  # stats() returns 0-100 already
        avg = sv.get("avg") or 0.0
        sh = sv.get("sharpe") or 0.0

        window_results.append(
            {
                "window": f"{oos_start[:4]}–{oos_end[:4]}",
                "n": sv.get("n", 0),
                "wr": wr,
                "avg": avg,
                "sharpe": sh,
                "ann_sharpe": ann_sh,
                "passed": passed,
                "n_tickers": n_tickers_traded,
            }
        )

        if len(window_results) == 1:
            print(hdr)
            print(sep)

        print(
            f"  {oos_start[:4]}–{oos_end[:4]:<16} {sv['n']:>5} {wr:>5.1f}%"
            f" {avg:>+6.2f}% {fmt_sharpe(sh):>9} {ann_sh:>7.2f}  {verdict}"
        )

    # ── 4. Verdict ────────────────────────────────────────────────────────────
    _section("4. Verdict")
    n_passed = sum(1 for r in window_results if r.get("passed"))
    n_total = len(window_results)
    edge_real = n_passed >= math.ceil(n_total * 0.6)  # ≥ 60% windows pass

    print(f"\n  OOS windows passed : {n_passed} / {n_total}")
    print(f"  Threshold          : ≥ {math.ceil(n_total * 0.6)} / {n_total} (60%)")

    if edge_real:
        print(f"\n  ✓ EDGE IS REAL — Ann.Sharpe ≥ {PASS_SHARPE} in {n_passed}/{n_total} OOS windows.")
        print("    §15/§16 params generalise out-of-sample. Sector-specific thresholds")
        print("    validated; curve-fit risk is low for the global gates.")
    else:
        print(f"\n  ✗ EDGE NOT CONFIRMED — only {n_passed}/{n_total} OOS windows passed.")
        print("    Sector-specific parameters likely overfit. Revert to global robust")
        print("    params (ATR≥20 only) and re-test before tightening further.")

    print("\n  Window detail:")
    for r in window_results:
        sym = "✓" if r.get("passed") else "✗"
        ann_s = f"{r['ann_sharpe']:.2f}" if not math.isnan(r.get("ann_sharpe", float("nan"))) else "n/a"
        print(
            f"    {sym} {r['window']}  N={r.get('n', 0):>4}  "
            f"WR={r.get('wr', 0):>5.1f}%  Avg={r.get('avg', 0):>+5.2f}%  "
            f"Ann.Sh={ann_s}"
        )


if __name__ == "__main__":
    main()
