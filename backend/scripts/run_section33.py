"""
run_section33.py — Energy sub-sector split · XLU research · ATR stop sweep

Covers three open Pillar 0b / Pillar 0 TODOs:

  §33a  Energy sub-sector split
        Isolate EOG; compare XOM/CVX/COP/SLB as a 4-ticker energy subgroup
        under current XLE config (vix_min=15, hold=5, thresh=40, atr≥20).

  §33b  XLU utilities research
        Run §16-style backtest on NEE/DUK/SO/AEP to calibrate _SECTOR_MR_CONFIG["XLU"].
        Sweep hold (5/7/10), vix_min (None/13/15), thresh (35/38/40).

  §33c  ATR stop sweep
        Test swing stop_mult at 1.5, 2.0, 2.5, 3.0 × ATR on the 10-ticker
        "strong energy + utilities" universe to find the sweet spot.
        Current live engine: 2.0/2.5× swing.

Expected runtime: ~3-5 minutes (9 tickers × 20yr).

Usage:
    cd backend
    python scripts/run_section33.py 2>&1 | tee /tmp/decomp_s33.log
"""
from __future__ import annotations
import os, sys, warnings
from datetime import datetime

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

_HERE   = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _p in [_PARENT, _HERE]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from backtest_technicals import (
    START, END,
    compute_indicators, compute_scores,
    simulate_ticker,
    fetch_spy_trend, fetch_stlfsi4,
    stats, print_table, fmt_sharpe, fmt_pf,
)

# ── Universe ──────────────────────────────────────────────────────────────────

ENERGY_TICKERS = ["XOM", "CVX", "COP", "SLB", "EOG"]
XLU_TICKERS    = ["NEE", "DUK", "SO", "AEP"]

# XLE §16 best config
XLE_CFG = dict(vix_min_override=15.0, hold_days_override=5, buy_thresh_override=40,
               atr_pct_rank_min_override=20.0)

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _download(ticker: str) -> pd.DataFrame | None:
    raw = yf.download(ticker, start=START, end=END, interval="1d",
                      auto_adjust=True, progress=False)
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


def _run(ticker: str, df: pd.DataFrame, vix: dict, spy: dict, stlfsi4: dict,
         **kwargs) -> dict:
    t = simulate_ticker(ticker, df, vix, spy, stlfsi4, mr_only=True, **kwargs)
    if t.empty:
        return {"n": 0, "wr": None, "avg": None, "sharpe": None, "max_dd": None}
    rets = t["net_pct"].tolist()
    s = stats(rets)
    # annualised Sharpe: avg_daily ≈ avg_per_trade / hold_days; scale by sqrt(252)
    hold = kwargs.get("hold_days_override", 7) or 7
    ann_sharpe = None
    if s["sharpe"] is not None:
        ann_sharpe = round(s["sharpe"] * (252 / hold) ** 0.5, 2)
    s["ann_sharpe"] = ann_sharpe
    return s


def _section(title: str) -> None:
    print(f"\n## {title}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("# §33 — Energy Split · XLU Research · ATR Stop Sweep\n")
    print(f"> Period: {START} → {END}  |  MR-only  |  5% position size\n")

    # ── Alt data ─────────────────────────────────────────────────────────────
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
    print(f"ok ({len(stlfsi4)} bars)" if stlfsi4 else "skipped (no API key)")

    # ── Download all tickers ──────────────────────────────────────────────────
    all_tickers = ENERGY_TICKERS + XLU_TICKERS
    dfs: dict[str, pd.DataFrame] = {}
    print(f"\nDownloading {len(all_tickers)} tickers…")
    for t in all_tickers:
        print(f"  {t}…", end=" ", flush=True)
        d = _download(t)
        if d is not None:
            dfs[t] = d
            print(f"ok ({len(d)} bars)")
        else:
            print("skip (insufficient data)")

    # ─────────────────────────────────────────────────────────────────────────
    # §33a — Energy sub-sector split
    # ─────────────────────────────────────────────────────────────────────────
    _section("§33a — Energy Sub-Sector Split (XLE config: vix≥15, hold=5, thresh=40, atr≥20)")

    print("> Rationale: EOG in bad-ticker list (0/2 trades, avg −7.0%). CVX also flagged.")
    print("> Question: do XOM/CVX/COP/SLB trade as a viable MR subgroup without EOG?\n")

    energy_rows = []
    for t in ENERGY_TICKERS:
        if t not in dfs:
            continue
        s = _run(t, dfs[t], vix, spy, stlfsi4, **XLE_CFG)
        flag = "⚠ bad-ticker" if t == "EOG" else ("⚠ bad-ticker" if t == "CVX" else "")
        energy_rows.append([
            t, s["n"],
            f"{s['wr']:.1f}%" if s["wr"] is not None else "—",
            f"{s['avg']:+.2f}%" if s["avg"] is not None else "—",
            fmt_sharpe(s.get("ann_sharpe")),
            f"-{s['max_dd']:.2f}%" if s["max_dd"] is not None else "—",
            flag,
        ])

    print_table(["Ticker", "N", "WR", "Avg", "Ann.Sharpe", "MaxDD", "Note"], energy_rows)

    # Group stats: XOM/CVX/COP/SLB combined (exclude EOG)
    xle_good = [t for t in ["XOM", "CVX", "COP", "SLB"] if t in dfs]
    combined_rets = []
    for t in xle_good:
        t_df = simulate_ticker(t, dfs[t], vix, spy, stlfsi4, mr_only=True, **XLE_CFG)
        if not t_df.empty:
            combined_rets += t_df["net_pct"].tolist()
    if combined_rets:
        s = stats(combined_rets)
        hold = XLE_CFG["hold_days_override"]
        ann = round(s["sharpe"] * (252 / hold) ** 0.5, 2) if s["sharpe"] else None
        print(f"\n### XOM+CVX+COP+SLB combined (N={s['n']})")
        print(f"- WR: {s['wr']}%  Avg: {s['avg']:+.2f}%  Ann.Sharpe: {fmt_sharpe(ann)}  MaxDD: -{s['max_dd']:.2f}%")
        if ann is not None:
            if ann >= 0.40:
                print("→ **KEEP in XLE config.** Group holds up without EOG. Confirm EOG removal.")
            elif ann >= 0.20:
                print("→ Marginal. Consider raising buy_thresh to 42 or restricting to XOM+COP only.")
            else:
                print("→ Energy MR edge is structurally weak. Consider blocking XLE entirely.")

    # ─────────────────────────────────────────────────────────────────────────
    # §33b — XLU utilities research
    # ─────────────────────────────────────────────────────────────────────────
    _section("§33b — XLU Utilities Research (NEE/DUK/SO/AEP)")

    print("> Objective: calibrate _SECTOR_MR_CONFIG['XLU'] (currently pending research).\n")

    # Baseline: default (no sector config overrides except ATR≥20)
    xlu_base_rows = []
    for t in XLU_TICKERS:
        if t not in dfs:
            continue
        s = _run(t, dfs[t], vix, spy, stlfsi4, atr_pct_rank_min_override=20.0)
        xlu_base_rows.append([
            t, s["n"],
            f"{s['wr']:.1f}%" if s["wr"] is not None else "—",
            f"{s['avg']:+.2f}%" if s["avg"] is not None else "—",
            fmt_sharpe(s.get("ann_sharpe")),
            f"-{s['max_dd']:.2f}%" if s["max_dd"] is not None else "—",
        ])

    print("#### Per-ticker baseline (default hold/thresh, ATR≥20)\n")
    print_table(["Ticker", "N", "WR", "Avg", "Ann.Sharpe", "MaxDD"], xlu_base_rows)

    # Sweep: hold × vix_min × thresh
    print("\n#### §33b Parameter sweep (combined NEE+DUK+SO+AEP)\n")

    sweep_rows = []
    HOLDS   = [5, 7, 10]
    VIX_MIN = [None, 13.0, 15.0]
    THRESH  = [35, 38, 40]

    best_ann = -999.0
    best_cfg: dict = {}
    best_n   = 0

    for hold in HOLDS:
        for vmin in VIX_MIN:
            for thresh in THRESH:
                rets: list[float] = []
                for t in XLU_TICKERS:
                    if t not in dfs:
                        continue
                    td = simulate_ticker(
                        t, dfs[t], vix, spy, stlfsi4, mr_only=True,
                        hold_days_override=hold,
                        vix_min_override=vmin,
                        buy_thresh_override=thresh,
                        atr_pct_rank_min_override=20.0,
                    )
                    if not td.empty:
                        rets += td["net_pct"].tolist()
                if not rets:
                    continue
                s   = stats(rets)
                ann = round(s["sharpe"] * (252 / hold) ** 0.5, 2) if s["sharpe"] else None
                vmin_str = f"≥{vmin:.0f}" if vmin is not None else "—"
                sweep_rows.append([
                    hold, vmin_str, thresh, s["n"],
                    f"{s['wr']:.1f}%",
                    f"{s['avg']:+.2f}%",
                    fmt_sharpe(ann),
                    f"-{s['max_dd']:.2f}%",
                ])
                if ann is not None and ann > best_ann and s["n"] >= 5:
                    best_ann = ann
                    best_cfg = {"vix_min": vmin, "hold_days": hold, "buy_thresh": thresh}
                    best_n   = s["n"]

    print_table(["Hold", "VIX≥", "Thresh", "N", "WR", "Avg", "Ann.Sharpe", "MaxDD"], sweep_rows)

    if best_cfg:
        print(f"\n### XLU Best config: hold={best_cfg['hold_days']}d, "
              f"vix_min={best_cfg['vix_min']}, thresh={best_cfg['buy_thresh']} "
              f"→ Ann.Sharpe {best_ann:.2f} (N={best_n})")
        if best_ann >= 0.40:
            print("→ **ADMIT XLU** with calibrated config above.")
        elif best_ann >= 0.20:
            print("→ Marginal. Admit XLU with caution; monitor live PF before trusting.")
        else:
            print("→ **BLOCK XLU** (no viable MR edge). Set buy_thresh=999.")

    # ─────────────────────────────────────────────────────────────────────────
    # §33c — ATR stop sweep on energy + utilities universe
    # ─────────────────────────────────────────────────────────────────────────
    _section("§33c — ATR Stop Sweep (swing stop_mult: 1.5 / 2.0 / 2.5 / 3.0 ×)")

    print("> Live engine MR stop: 2.0× (widened from 1.5× in §31).")
    print("> Live stop-hit rate was 44.9% at 1.5×. After widening, open question: is 3× better?")
    print("> Test universe: all energy + XLU tickers combined (9 tickers).\n")

    STOP_VARIANTS = [
        (1.5, 2.0, "1.5s/2.0t (pre-§31 backtest default)"),
        (2.0, 2.5, "2.0s/2.5t (current live engine)"),
        (2.5, 3.0, "2.5s/3.0t (proposed wider)"),
        (3.0, 4.0, "3.0s/4.0t (aggressive wide)"),
    ]

    all_universe_tickers = [t for t in all_tickers if t in dfs]
    stop_rows = []
    for stop_m, tgt_m, label in STOP_VARIANTS:
        rets: list[float] = []
        stop_hits = 0; total = 0
        for t in all_universe_tickers:
            td = simulate_ticker(
                t, dfs[t], vix, spy, stlfsi4, mr_only=True,
                atr_pct_rank_min_override=20.0,
                stop_mult_override=stop_m,
                target_mult_override=tgt_m,
            )
            if not td.empty:
                rets += td["net_pct"].tolist()
                if "exit_reason" in td.columns:
                    stop_hits += (td["exit_reason"] == "stop").sum()
                    total     += len(td)
        if not rets:
            continue
        s = stats(rets)
        stop_rate = f"{stop_hits/total*100:.1f}%" if total > 0 else "—"
        stop_rows.append([
            label, s["n"],
            f"{s['wr']:.1f}%",
            f"{s['avg']:+.2f}%",
            fmt_sharpe(s["sharpe"]),
            f"-{s['max_dd']:.2f}%",
            stop_rate,
        ])

    print_table(
        ["Config", "N", "WR", "Avg", "Sharpe", "MaxDD", "Stop%"],
        stop_rows,
    )
    print("\n> Recommendation: pick stop_mult where WR is highest AND avg ≥ +0.30%.")
    print("> If stop% doesn't drop meaningfully from 1.5→2.0, the gain is from fewer premature exits.")

    print(f"\n---\n*§33 complete · {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")


if __name__ == "__main__":
    main()
