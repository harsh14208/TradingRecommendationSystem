"""
run_section35.py — Five pending experiments from the research backlog

§35a  §21 VIX-regime switching OOS
      Runs the 5×2yr walk-forward with the regime-conditional strategy:
        VIX ≥ 18 → strict  (thresh=38, ATR≤70, jump<-6%)
        VIX <  18 → relaxed (thresh=35, no ATR ceil, no jump)
      Goal: pass ≥3/5 OOS windows (§19=1/5, §20=2/5).

§35b  Adaptive exit threshold sweep
      Current: price>entry×1.005 AND RSI>55.
      Test looser thresholds: RSI>45/50, profit>0.001/0.003.
      Goal: raise adaptive% from 17% without hurting WR.

§35c  §34d validated on full 56-ticker universe
      §34d used 24 tickers → hold=5 for score<50 gave WR+6.1pp.
      Confirm the finding holds at full scale.

§35d  R:R asymmetry — stop=2.0×, target sweep 2.5/3.0/3.5×
      Live stop-hit rate 44.9% (>40% threshold).
      §33c widened stops — no gain. Unexplored: widen target only.
      Goal: find optimal target multiplier to improve E[r] without
      changing stop placement.

§35e  Universe re-screen (fast mode, 2006-2016 window)
      Run screen_sp500_mr_candidates.py fast-mode to find ~30 more
      PASS tickers for the 85-ticker target universe.
      Reported here as a subprocess call; full output at /tmp/s35e_screen.log.

Expected runtime: ~15-25 min (§35a dominates at 56 tickers × 5 windows).

Usage:
    cd backend
    python scripts/run_section35.py 2>&1 | tee /tmp/decomp_s35.log
"""
from __future__ import annotations
import math
import os
import sys
import subprocess
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
    TICKERS, START, END, HOLD_DAYS,
    compute_indicators, compute_scores,
    simulate_ticker, stats, fmt_sharpe, print_table,
    fetch_spy_trend, fetch_stlfsi4,
)

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

# 5×2yr OOS windows (same as §19/§20)
OOS_WINDOWS = [
    ("2016-01-01", "2017-12-31"),
    ("2018-01-01", "2019-12-31"),
    ("2020-01-01", "2021-12-31"),
    ("2022-01-01", "2023-12-31"),
    ("2024-01-01", "2025-12-31"),
]

PASS_SHARPE = 1.0
PASS_N_MIN  = 5

# §19 reference for comparison column
_S19 = {
    "2016–2017": (13, 0.94),
    "2018–2019": (20, 1.18),
    "2020–2021": (26, 0.74),
    "2022–2023": (8,  0.97),
    "2024–2025": (9,  0.11),
}
_S20 = {
    "2016–2017": (13, 2.69),
    "2018–2019": (16, 0.74),
    "2020–2021": (37, 2.10),
    "2022–2023": (13, 0.61),
    "2024–2025": (6,  0.01),
}


def _ann_sharpe(sv: dict, n_years: float) -> float:
    sh = sv.get("sharpe") or 0.0
    n  = sv.get("n")      or 0
    if n < 2:
        return float("nan")
    return round(sh * math.sqrt(n / n_years), 2)


def _section(title: str) -> None:
    print(f"\n{'═'*65}")
    print(f"  {title}")
    print(f"{'═'*65}\n")


# ── Market data helpers ───────────────────────────────────────────────────────

def _fetch_alt_data() -> tuple[dict, dict, dict]:
    print("Fetching VIX…", end=" ", flush=True)
    try:
        v = yf.download("^VIX", start=START, end=END, interval="1d",
                        auto_adjust=False, progress=False)
        if isinstance(v.columns, pd.MultiIndex):
            v.columns = v.columns.get_level_values(0)
        vix = {pd.Timestamp(str(k)[:10]): float(val)
               for k, val in v["Close"].items() if pd.notna(val)}
        print(f"ok ({len(vix)} bars)")
    except Exception as e:
        vix = {}; print(f"failed ({e})")

    print("Fetching SPY trend…", end=" ", flush=True)
    spy = fetch_spy_trend(START, END)
    print(f"ok ({len(spy)} bars)")

    print("Fetching STLFSI4…", end=" ", flush=True)
    stlfsi4 = fetch_stlfsi4(START, END, FRED_API_KEY)
    print(f"ok ({len(stlfsi4)} bars)" if stlfsi4 else "skipped")

    return vix, spy, stlfsi4


def _prep_tickers(vix, spy, stlfsi4) -> dict[str, pd.DataFrame]:
    print(f"\nDownloading {len(TICKERS)} tickers (batch)…", flush=True)
    raw_all = yf.download(TICKERS, start=START, end=END,
                          auto_adjust=True, progress=False, threads=True)
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
                continue
            compute_indicators(df)
            df["score"] = compute_scores(df)
            for col in ("vwap_pct", "vwap_pct_prev"):
                if col not in df.columns:
                    df[col] = float("nan")
            if "vwap_slope_pos" not in df.columns:
                df["vwap_slope_pos"] = False
            prepped[tkr] = df
        except Exception:
            pass
    print(f"{len(prepped)}/{len(TICKERS)} tickers prepared")
    return prepped


def _run_oos_window(prepped, vix_full, spy_full, stlfsi4_full,
                    oos_start, oos_end, params: dict) -> dict:
    ts_start = pd.Timestamp(oos_start)
    ts_end   = pd.Timestamp(oos_end)
    n_years  = (ts_end - ts_start).days / 365.25
    vix_w    = {k: v for k, v in vix_full.items()    if ts_start <= k <= ts_end}
    spy_w    = {k: v for k, v in spy_full.items()    if ts_start <= k <= ts_end}
    st_w     = {k: v for k, v in stlfsi4_full.items()if ts_start <= k <= ts_end}

    all_net: list[float] = []
    for tkr, full_df in prepped.items():
        oos_df = full_df.loc[ts_start:ts_end].copy()
        if len(oos_df) < 20:
            continue
        try:
            t = simulate_ticker(tkr, oos_df, vix_w, spy_w, st_w, **params)
            if not t.empty:
                all_net.extend(t["net_pct"].tolist())
        except Exception:
            pass

    if not all_net:
        return {"window": f"{oos_start[:4]}–{oos_end[:4]}", "n": 0,
                "wr": 0, "avg": 0, "ann_sharpe": float("nan"), "passed": False}

    sv = stats(all_net)
    ann_sh = _ann_sharpe(sv, n_years)
    passed = sv.get("n", 0) >= PASS_N_MIN and not math.isnan(ann_sh) and ann_sh >= PASS_SHARPE
    return {
        "window": f"{oos_start[:4]}–{oos_end[:4]}",
        "n": sv["n"], "wr": sv["wr"] or 0, "avg": sv["avg"] or 0,
        "sharpe": sv.get("sharpe") or 0, "ann_sharpe": ann_sh, "passed": passed,
    }


def _print_oos_table(results: list[dict], ref_label: str = "§19",
                     ref_data: dict | None = None) -> int:
    n_passed = sum(1 for r in results if r.get("passed"))
    headers = ["Window", "N", "WR", "Avg", "Ann.Sh", "Pass?",
               f"{ref_label} N", f"{ref_label} Ann.Sh", "Δ"]
    rows = []
    for r in results:
        w   = r["window"]
        ann = r["ann_sharpe"]
        ann_s = f"{ann:.2f}" if not math.isnan(ann) else "—"
        verdict = "✓" if r.get("passed") else "✗"
        ref_n, ref_ann = (ref_data.get(w) or (None, None)) if ref_data else (None, None)
        ref_ann_s = f"{ref_ann:.2f}" if ref_ann is not None else "—"
        ref_n_s   = str(ref_n) if ref_n is not None else "—"
        delta_s = (f"{ann - ref_ann:+.2f}" if (ref_ann is not None and not math.isnan(ann))
                   else "—")
        rows.append([
            w, r["n"],
            f"{r['wr']:.1f}%" if r["n"] else "—",
            f"{r['avg']:+.2f}%" if r["n"] else "—",
            ann_s, verdict,
            ref_n_s, ref_ann_s, delta_s,
        ])
    print_table(headers, rows)
    print(f"\n  Passed: {n_passed}/{len(results)}  (threshold: ≥3/5)")
    return n_passed


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("# §35 — Five Research Experiments\n")
    print(f"> Period: {START} → {END}  |  {len(TICKERS)}-ticker production universe\n")

    vix, spy, stlfsi4 = _fetch_alt_data()
    prepped = _prep_tickers(vix, spy, stlfsi4)

    # ─────────────────────────────────────────────────────────────────────────
    # §35a — §21 VIX-Regime Switching OOS
    # ─────────────────────────────────────────────────────────────────────────
    _section("§35a — §21 VIX-Regime Switching OOS (5×2yr walk-forward)")
    print("> VIX ≥ 18 → strict  (thresh=38, ATR[20,70], ret_jump<-6%)")
    print("> VIX <  18 → relaxed (thresh=35, ATR≥20, no gates)")
    print("> Baseline §19 = 1/5 pass  |  §20 = 2/5 pass\n")

    REGIME_PARAMS = dict(
        mr_only=True,
        hold_days_override=HOLD_DAYS,
        atr_pct_rank_min_override=20.0,
        vix_min_override=None,
        vix_regime_switch=True,
        # buy_thresh / atr_max / ret_jump set dynamically per-bar by the switch
    )

    oos_results_35a: list[dict] = []
    for oos_start, oos_end in OOS_WINDOWS:
        r = _run_oos_window(prepped, vix, spy, stlfsi4,
                            oos_start, oos_end, REGIME_PARAMS)
        oos_results_35a.append(r)
        status = "✓ PASS" if r["passed"] else "✗ FAIL"
        ann_s = f"{r['ann_sharpe']:.2f}" if not math.isnan(r["ann_sharpe"]) else "—"
        print(f"  {oos_start[:4]}–{oos_end[:4]}  N={r['n']:>4}  "
              f"WR={r['wr']:>5.1f}%  Avg={r['avg']:>+5.2f}%  "
              f"Ann.Sh={ann_s:<6}  {status}")

    print()
    n_pass_35a = _print_oos_table(oos_results_35a, "§20", _S20)

    # Interpretation
    if n_pass_35a >= 3:
        print("\n  ✓ REGIME SWITCHING WORKS — ≥3/5 OOS windows pass.")
        print("    Implement dynamic VIX-regime threshold in live engine.")
    elif n_pass_35a > sum(1 for v in _S20.values() if v[1] >= PASS_SHARPE):
        print("\n  ≈ MARGINAL IMPROVEMENT over §20 — but below 3/5 threshold.")
        print("    Consider deploying regime switch speculatively; watch live data.")
    else:
        print("\n  ✗ NO IMPROVEMENT — regime switching does not help OOS.")
        print("    2024-25 hostile regime dominates regardless of switch logic.")

    # ─────────────────────────────────────────────────────────────────────────
    # §35b — Adaptive Exit Threshold Sweep
    # ─────────────────────────────────────────────────────────────────────────
    _section("§35b — Adaptive Exit Threshold Sweep")
    print("> Baseline: profit>1.005 AND RSI>55  →  17% of trades, 100% WR, avg +3.20%")
    print("> Test: loosen profit and RSI thresholds to capture more trades early.\n")

    BASE_CFG = dict(
        mr_only=True,
        hold_days_override=HOLD_DAYS,
        buy_thresh_override=40,
        atr_pct_rank_min_override=20.0,
    )

    # All trades for the full 20-year period (not OOS)
    def _run_full(dfs, **overrides) -> pd.DataFrame:
        parts = []
        for tkr, df in dfs.items():
            t = simulate_ticker(tkr, df, vix, spy, stlfsi4,
                                **{**BASE_CFG, **overrides})
            if not t.empty:
                parts.append(t)
        return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

    combos = [
        ("Baseline (1.005/RSI55)", dict(adaptive_profit_thresh_override=1.005,
                                        adaptive_rsi_thresh_override=55.0)),
        ("1.005 / RSI50",          dict(adaptive_profit_thresh_override=1.005,
                                        adaptive_rsi_thresh_override=50.0)),
        ("1.005 / RSI45",          dict(adaptive_profit_thresh_override=1.005,
                                        adaptive_rsi_thresh_override=45.0)),
        ("1.003 / RSI55",          dict(adaptive_profit_thresh_override=1.003,
                                        adaptive_rsi_thresh_override=55.0)),
        ("1.003 / RSI50",          dict(adaptive_profit_thresh_override=1.003,
                                        adaptive_rsi_thresh_override=50.0)),
        ("1.001 / RSI50",          dict(adaptive_profit_thresh_override=1.001,
                                        adaptive_rsi_thresh_override=50.0)),
        ("1.001 / RSI45",          dict(adaptive_profit_thresh_override=1.001,
                                        adaptive_rsi_thresh_override=45.0)),
    ]

    adp_rows = []
    for label, overrides in combos:
        df = _run_full(prepped, **overrides)
        if df.empty:
            adp_rows.append([label, 0, "—", "—", "—", "—", "—", "—"])
            continue
        sv = stats(df["net_pct"].tolist())
        hold = HOLD_DAYS
        ann = round(sv["sharpe"] * (252 / hold) ** 0.5, 2) if sv.get("sharpe") else None
        rc  = df["exit_reason"].value_counts()
        n_adp  = rc.get("adaptive", 0)
        n_tl   = rc.get("time_loss", 0)
        adp_pct = f"{n_adp / sv['n'] * 100:.1f}%" if sv["n"] else "—"

        # WR of adaptive-exit trades only
        adp_sub = df[df["exit_reason"] == "adaptive"]
        adp_wr = f"{(adp_sub['net_pct'] > 0).mean() * 100:.1f}%" if not adp_sub.empty else "—"
        adp_avg = f"{adp_sub['net_pct'].mean():+.2f}%" if not adp_sub.empty else "—"

        adp_rows.append([
            label,
            sv["n"],
            f"{sv['wr']:.1f}%",
            f"{sv['avg']:+.2f}%",
            fmt_sharpe(ann),
            f"{n_adp} ({adp_pct})",
            adp_wr,
            adp_avg,
        ])

    print_table(
        ["Label", "N-total", "WR", "Avg", "Ann.Sh", "Adapt# (%)", "Adpt WR", "Adpt Avg"],
        adp_rows,
    )
    print("\n> Key: Adpt% should rise; overall WR/Ann.Sh should hold or improve.")
    print("> If Adpt WR drops below 90%: threshold is too loose — exiting too early.")

    # ─────────────────────────────────────────────────────────────────────────
    # §35c — §34d Full-Universe Validation (score-segmented hold)
    # ─────────────────────────────────────────────────────────────────────────
    _section("§35c — Score-Segmented Hold on Full 56-Ticker Universe")
    print("> §34d finding (24 tickers): score 40-49 hold=5 → WR+6.1pp, Ann.Sh 0.56 vs 0.44")
    print("> Validating on the full 56-ticker production universe.\n")

    hi_parts, lo_base_parts, lo_short_parts = [], [], []
    for tkr, df in prepped.items():
        t_base = simulate_ticker(tkr, df, vix, spy, stlfsi4, **BASE_CFG)
        if t_base.empty:
            continue
        hi_parts.append(t_base[t_base["score"] >= 50])
        lo_base_parts.append(t_base[t_base["score"] < 50])

        t_short = simulate_ticker(tkr, df, vix, spy, stlfsi4,
                                  **{**BASE_CFG, "hold_days_override": 5})
        if not t_short.empty:
            lo_short_parts.append(t_short[t_short["score"] < 50])

    hi_df      = pd.concat(hi_parts,      ignore_index=True) if hi_parts      else pd.DataFrame()
    lo_base_df = pd.concat(lo_base_parts, ignore_index=True) if lo_base_parts else pd.DataFrame()
    lo_short_df= pd.concat(lo_short_parts,ignore_index=True) if lo_short_parts else pd.DataFrame()

    def _seg_row(label, df):
        if df.empty:
            return [label, 0, "—", "—", "—", "—", "—"]
        sv  = stats(df["net_pct"].tolist())
        ann = round(sv["sharpe"] * (252 / HOLD_DAYS) ** 0.5, 2) if sv.get("sharpe") else None
        rc  = df["exit_reason"].value_counts()
        tl  = rc.get("time_loss", 0)
        tl_pct = f"{tl / sv['n'] * 100:.1f}%" if sv["n"] else "—"
        return [label, sv["n"], f"{sv['wr']:.1f}%", f"{sv['avg']:+.2f}%",
                fmt_sharpe(ann), tl, tl_pct]

    print_table(
        ["Label", "N", "WR", "Avg", "Ann.Sh", "TL#", "TL%"],
        [
            _seg_row("HI score≥50,  hold=10",         hi_df),
            _seg_row("LO score<50,  hold=10 (base)",  lo_base_df),
            _seg_row("LO score<50,  hold=5  (short)", lo_short_df),
        ],
    )
    print("\n> §34d confirmed if LO hold=5 Ann.Sh > LO hold=10 Ann.Sh by ≥0.05.")

    # ─────────────────────────────────────────────────────────────────────────
    # §35d — R:R Asymmetry (stop=2.0×, target sweep)
    # ─────────────────────────────────────────────────────────────────────────
    _section("§35d — R:R Asymmetry: stop=2.0× ATR, target sweep 2.5/3.0/3.5×")
    print("> Live stop-hit rate: 44.9% (>40% threshold; §31 data).")
    print("> §33c showed widening both stop+target adds nothing.")
    print("> Unexplored: keep stop at 2.0×, widen target only → shifts R:R without")
    print("> changing stop placement. Prediction: target 3.0× improves Avg without")
    print("> hurting WR (targets hit less often but better when they do).\n")

    rr_combos = [
        ("stop=2.0, tgt=2.5 (baseline)", 2.0, 2.5),
        ("stop=2.0, tgt=3.0",            2.0, 3.0),
        ("stop=2.0, tgt=3.5",            2.0, 3.5),
        ("stop=1.5, tgt=2.5 (old)",      1.5, 2.5),  # historical comparison
    ]

    rr_rows = []
    for label, s_mult, t_mult in rr_combos:
        df = _run_full(prepped, stop_mult_override=s_mult, target_mult_override=t_mult)
        if df.empty:
            rr_rows.append([label, 0, "—", "—", "—", "—", "—", "—"])
            continue
        sv = stats(df["net_pct"].tolist())
        ann = round(sv["sharpe"] * (252 / HOLD_DAYS) ** 0.5, 2) if sv.get("sharpe") else None
        rc  = df["exit_reason"].value_counts()
        n_tgt = rc.get("target", 0)
        n_stp = rc.get("stop",   0)
        t_rate = f"{n_tgt / sv['n'] * 100:.1f}%" if sv["n"] else "—"
        s_rate = f"{n_stp / sv['n'] * 100:.1f}%" if sv["n"] else "—"
        rr_rows.append([
            label, sv["n"],
            f"{sv['wr']:.1f}%", f"{sv['avg']:+.2f}%", fmt_sharpe(ann),
            f"-{sv['max_dd']:.2f}%", t_rate, s_rate,
        ])

    print_table(
        ["Label", "N", "WR", "Avg", "Ann.Sh", "MaxDD", "Tgt%", "Stop%"],
        rr_rows,
    )
    print("\n> Optimal: highest Ann.Sh + Avg with acceptable Stop% (<45%).")
    print("> If tgt=3.0× matches or beats 2.5× → deploy in signal_engine.py.")

    # ─────────────────────────────────────────────────────────────────────────
    # §35e — Universe Re-Screen (fast mode)
    # ─────────────────────────────────────────────────────────────────────────
    _section("§35e — Universe Re-Screen (S&P 500, fast mode 2006-2016)")
    print("> Runs screen_sp500_mr_candidates.py --fast to find additional tickers.")
    print("> Target: 85-ticker universe (currently 56). Goal: N≥30/OOS window.\n")
    print("> Output: /tmp/s35e_screen.log  (this may take 30-60 min)\n")

    screener_script = os.path.join(_HERE, "screen_sp500_mr_candidates.py")
    if os.path.exists(screener_script):
        python_exe = sys.executable
        print(f"  Launching: {python_exe} {screener_script} --fast")
        print(f"  Logging to /tmp/s35e_screen.log  (runs in background)\n")
        try:
            log_fh = open("/tmp/s35e_screen.log", "w")
            proc = subprocess.Popen(
                [python_exe, screener_script, "--fast"],
                stdout=log_fh, stderr=subprocess.STDOUT,
                cwd=_PARENT,
            )
            print(f"  PID {proc.pid} started. Check /tmp/s35e_screen.log for progress.")
            print(f"  When complete, add PASS tickers to backtest_technicals.py TICKERS.")
        except Exception as e:
            print(f"  Failed to launch screener: {e}")
    else:
        print(f"  ⚠ screener script not found at {screener_script}")

    # ─────────────────────────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────────────────────────
    _section("§35 — Summary and Next Actions")
    print("§35a (VIX-regime OOS):")
    if n_pass_35a >= 3:
        print("  ✓ DEPLOY — implement dynamic VIX≥18/VIX<18 threshold switching in live engine.")
    elif n_pass_35a == 2:
        print("  ≈ SPECULATIVE — 2/5 pass same as §20. No improvement; do not deploy.")
    else:
        print("  ✗ REJECT — regime switching not effective OOS.")
    print("\n§35b (adaptive exit):")
    print("  Read table above. Deploy if Ann.Sh holds AND Adpt% rises AND Adpt WR ≥ 90%.")
    print("\n§35c (score-segmented hold full universe):")
    print("  If confirmed: wire score-segmented hold into live signal_engine.py")
    print("  recommendedHoldDays formula (score<50 → 5d, score≥50 → sector default).")
    print("\n§35d (R:R asymmetry):")
    print("  Best target mult → update TARGET_MULT in signal_engine.py / atr_levels().")
    print("\n§35e (universe re-screen):")
    print("  Review /tmp/s35e_screen.log. Copy PASS tickers into backtest_technicals.py TICKERS.")
    print("  Re-run §19 OOS with expanded universe to confirm N≥30/window.")


if __name__ == "__main__":
    main()
