"""§18 Candidate Validation — §15f + §17f gates on 5 PASS tickers"""
import os, sys, math, warnings
warnings.filterwarnings("ignore")
_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _p in [_PARENT, _HERE]:
    if _p not in sys.path: sys.path.insert(0, _p)

import pandas as pd
import yfinance as yf
from multiprocessing import Pool

from backtest_technicals import (
    START, END, fetch_spy_trend, fetch_stlfsi4, process_ticker,
    simulate_ticker, stats, fmt_sharpe,
)
from signal_alpha_decomposition import (
    compute_extra_indicators, _download_etf_closes, _prescore, _section,
)

CANDIDATES = ["EXPE", "GOOG", "LULU", "MAR", "TPR"]

# Per-sector §15f params matching _SECTOR_MR_CONFIG in signal_engine.py
SECTOR_PARAMS = {
    "EXPE": {"hold": 10, "vix_min": 13.0,  "thresh": 40, "atr_min": 20.0},  # XLY
    "GOOG": {"hold": 10, "vix_min": None,   "thresh": 38, "atr_min": 20.0},  # XLC
    "LULU": {"hold": 10, "vix_min": 13.0,  "thresh": 40, "atr_min": 20.0},  # XLY
    "MAR":  {"hold": 10, "vix_min": 13.0,  "thresh": 40, "atr_min": 20.0},  # XLY
    "TPR":  {"hold": 10, "vix_min": 13.0,  "thresh": 40, "atr_min": 20.0},  # XLY
}

def _ann(sv):
    sh = sv.get("sharpe") or 0.0; n = sv.get("n") or 0
    return round(sh * math.sqrt(n / 20), 2) if n >= 2 else 0.0

def main():
    _section("§18 Candidate Validation")
    print(f"> Tickers: {', '.join(CANDIDATES)}\n> Period: {START} -> {END}\n")

    # ── 1. Market data ────────────────────────────────────────────────────────
    _section("1. Market data")
    try:
        vix_df = yf.download("^VIX", start=START, end=END, interval="1d",
                              auto_adjust=False, progress=False)
        if isinstance(vix_df.columns, pd.MultiIndex):
            vix_df.columns = vix_df.columns.get_level_values(0)
        vix_series = vix_df["Close"] if "Close" in vix_df.columns else pd.Series(dtype=float)
        vix = {pd.Timestamp(str(k)[:10]): float(v)
               for k, v in vix_series.items() if pd.notna(v)}
        print(f"VIX ok ({len(vix)} bars)")
    except Exception as e:
        vix = {}; print(f"VIX failed: {e}")

    spy_trend = fetch_spy_trend(START, END)
    print(f"SPY ok ({len(spy_trend)} bars)")

    _fred_key = ""
    try:
        for line in open(os.path.join(_PARENT, ".env")):
            if line.startswith("FRED_API_KEY="): _fred_key = line.strip().split("=", 1)[1]
    except Exception: pass
    stlfsi4 = fetch_stlfsi4(START, END, _fred_key)
    print(f"STLFSI4 ok ({len(stlfsi4)} obs)" if stlfsi4 else "STLFSI4 skipped")

    spy_closes = _download_etf_closes("SPY", START, END, "SPY")
    hyg_closes = _download_etf_closes("HYG", START, END, "HYG")
    spy_s = spy_closes if not spy_closes.empty else None
    hyg_s = hyg_closes if not hyg_closes.empty else None
    print(f"ETF closes ok (SPY={len(spy_closes)}, HYG={len(hyg_closes)})")

    # ── 2. Download OHLCV + compute indicators ────────────────────────────────
    _section("2. Downloading & processing tickers")
    with Pool(min(5, len(CANDIDATES))) as p:
        dl_results = p.map(process_ticker,
                           [(t, vix, spy_trend, stlfsi4, True) for t in CANDIDATES])

    all_dfs: dict = {}
    for ticker, _trades, _bh, df in dl_results:
        if df is not None and len(df) >= 50:
            all_dfs[ticker] = df
            print(f"  {ticker}: {len(df)} bars ok")
        else:
            print(f"  {ticker}: skip (insufficient data)")

    if not all_dfs:
        print("No tickers loaded — aborting."); return

    # ── 3. Extra indicators + pre-score ──────────────────────────────────────
    _section("3. Extra indicators + pre-score")
    for df in all_dfs.values():
        compute_extra_indicators(df, spy_closes=spy_s, hyg_closes=hyg_s)
    pre_dfs = _prescore(all_dfs, mr_w=0.1)
    print(f"  Done ({len(pre_dfs)} tickers, MR weight=0.1)")

    # ── 4. Backtest runs ──────────────────────────────────────────────────────
    def _run(label, ceil=None, jump=None):
        _section(label)
        print(f"  {'T':<5} {'N':>4} {'WR':>6} {'Avg':>7} {'Sh':>8} {'Ann':>7}")
        print("  " + "-" * 40)
        results = {}
        for t, df in pre_dfs.items():
            p = SECTOR_PARAMS[t]
            kw = dict(mr_only=True,
                      hold_days_override=p["hold"],
                      vix_min_override=p["vix_min"],
                      buy_thresh_override=p["thresh"],
                      atr_pct_rank_min_override=p["atr_min"])
            if ceil is not None: kw["atr_pct_rank_max_override"] = ceil
            if jump is not None: kw["ret_jump_filter_override"]   = jump
            tdf = simulate_ticker(t, df, vix, spy_trend, stlfsi4, **kw)
            if tdf.empty:
                print(f"  {t:<5} {'0':>4}"); continue
            sv = stats(tdf["net_pct"].tolist()); sv["ann"] = _ann(sv)
            results[t] = sv
            wr  = sv.get("wr") or 0   # already 0-100
            avg = sv.get("avg") or 0
            sh  = sv.get("sharpe") or 0
            print(f"  {t:<5} {sv['n']:>4} {wr:>5.1f}% {avg:>+6.2f}% {fmt_sharpe(sh):>8} {sv['ann']:>7.2f}")
        return results

    base = _run("4. §15f base gates only")
    full = _run("5. §15f + §17f (ATR≤70, jump<-6%)", ceil=70.0, jump=-6.0)

    # ── 5. Verdict ────────────────────────────────────────────────────────────
    _section("6. Verdict")
    # WR from stats() is 0-100, not 0-1
    b_pass = [t for t, sv in base.items()
              if (sv.get("wr") or 0) >= 55 and (sv.get("sharpe") or 0) >= 0.35 and sv["n"] >= 5]
    f_pass = [t for t, sv in full.items()
              if (sv.get("wr") or 0) >= 55 and (sv.get("sharpe") or 0) >= 0.35 and sv["n"] >= 3]
    print(f"\n  §15f PASS (N≥5, WR≥55%, Sh≥0.35): {b_pass}")
    print(f"  §17f PASS (N≥3, WR≥55%, Sh≥0.35): {f_pass}")
    all_pass = set(b_pass + f_pass)
    if all_pass:
        for t in sorted(all_pass):
            b = base.get(t, {}); f = full.get(t, {})
            b_wr = b.get("wr") or 0; b_sh = b.get("sharpe") or 0
            verdict = "ADD" if b_wr >= 65 and b_sh >= 0.50 else "CAUTION"
            print(f"    {t}: §15f N={b.get('n',0)} WR={b_wr:.0f}% Sh={b_sh:.2f}"
                  f"  |  §17f N={f.get('n',0)}  ->  {verdict}")
    else:
        print("  No tickers passed minimum thresholds.")
        print("\n  All results:")
        for t in sorted(pre_dfs):
            b = base.get(t, {}); f = full.get(t, {})
            print(f"    {t}: §15f N={b.get('n',0)} WR={b.get('wr') or 0:.0f}% Sh={b.get('sharpe') or 0:.2f}"
                  f"  |  §17f N={f.get('n',0)}")

if __name__ == "__main__":
    main()
