"""
run_section17.py — Focused §17 entry quality gate research runner.

Skips §13-§16. Loads strong 42-ticker universe (Tech/FAANG + Financials + Consumer),
applies extra indicators, then runs §17:
  §17a  ATR ceiling sweep     — None / ≤90 / ≤80 / ≤70 (Quantpedia P70 finding)
  §17b  Return jump filter    — block 1-day drops < −8% / −6% / −5% (Alpha Architect)
  §17c  Entry delay (T+2)     — skip continuation morning before reversal
  §17d  Best combined         — §15f + winning §17 gates stacked

Expected runtime: ~25-30 minutes.

Usage:
    cd backend
    python scripts/run_section17.py 2>&1 | tee /tmp/decomp_§17.log
"""
from __future__ import annotations
import os, sys, warnings
from multiprocessing import Pool

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
    fetch_spy_trend, fetch_stlfsi4, process_ticker,
)
from signal_alpha_decomposition import (
    TICKERS,
    compute_extra_indicators,
    run_gate_research_v17,
    _download_etf_closes,
    _pool_init,
    _prescore,
    _section,
)

# Strong 42-ticker universe (§15a confirmed, §15f optimized)
_STRONG = [
    "NVDA","MSFT","AAPL","GOOGL","META","AMZN","NFLX","ADBE","TSLA","BKNG","EBAY","INTU",
    "JPM","WFC","BAC","GS","V","MA","BLK","SCHW","CME","SPGI","MCO","ICE","MSCI","FIS","FISV",
    "HD","F","LOW","TJX","ROST","LULU","MAR","HLT","RCL","CHTR","GM","COST","SBUX","TGT","PYPL",
]


def main() -> None:
    print("# §17 Entry Quality Gate Research\n")
    print(f"> Strong 42-ticker universe only (Tech/FAANG + Financials + Consumer).")
    print(f"> Base: §15f sector-optimized filters. Testing ATR ceiling, jump filter, entry delay.")
    print(f"> Period: {START} → {END}\n")

    # ── Fetch alt-data ────────────────────────────────────────────────────────
    print("Fetching VIX…", end=" ", flush=True)
    try:
        vix_df = yf.download("^VIX", start=START, end=END, interval="1d",
                              auto_adjust=False, progress=False)
        if isinstance(vix_df.columns, pd.MultiIndex):
            vix_df.columns = vix_df.columns.get_level_values(0)
        vix = {pd.Timestamp(str(k)[:10]): float(v)
               for k, v in vix_df["Close"].items() if pd.notna(v)}
        print(f"ok ({len(vix)} bars)")
    except Exception as e:
        vix = {}; print(f"failed ({e})")

    print("Fetching SPY trend…", end=" ", flush=True)
    spy_trend = fetch_spy_trend(START, END)
    print(f"ok ({len(spy_trend)} bars)")

    print("Fetching SPY closes…", end=" ", flush=True)
    spy_closes = _download_etf_closes("SPY", START, END, "SPY")
    print(f"ok ({len(spy_closes)} bars)" if not spy_closes.empty else "failed")

    print("Fetching HYG closes…", end=" ", flush=True)
    hyg_closes = _download_etf_closes("HYG", START, END, "HYG")
    print(f"ok ({len(hyg_closes)} bars)" if not hyg_closes.empty else "failed")

    print("Fetching FRED STLFSI4…", end=" ", flush=True)
    _fred_key = os.getenv("FRED_API_KEY", "")
    if not _fred_key:
        try:
            with open(os.path.join(_PARENT, ".env")) as _ef:
                for line in _ef:
                    if line.startswith("FRED_API_KEY="):
                        _fred_key = line.strip().split("=", 1)[1]
        except Exception:
            pass
    stlfsi4 = fetch_stlfsi4(START, END, _fred_key)
    print(f"ok ({len(stlfsi4)} obs)" if stlfsi4 else "skipped")

    # ── Download only strong tickers ─────────────────────────────────────────
    _section(f"Downloading {len(_STRONG)} strong tickers")
    print(f"\nDownloading {len(_STRONG)} tickers (parallel)…\n")
    with Pool(8) as p:
        results = p.map(
            process_ticker,
            [(t, vix, spy_trend, stlfsi4, True) for t in _STRONG],
        )

    all_dfs: dict = {}
    for ticker, _t, _bh, df in results:
        if df is not None:
            all_dfs[ticker] = df

    if not all_dfs:
        print("[error] No ticker data loaded.")
        return

    # ── Extra indicators ──────────────────────────────────────────────────────
    print("Computing extra indicators…", flush=True)
    spy_s = spy_closes if not spy_closes.empty else None
    hyg_s = hyg_closes if not hyg_closes.empty else None
    for df in all_dfs.values():
        compute_extra_indicators(df, spy_closes=spy_s, hyg_closes=hyg_s)

    print(f"\n  {len(all_dfs)} tickers ready. Pre-scoring (MR=0.1)…\n")
    pre_dfs = _prescore(all_dfs, mr_w=0.1)
    print(f"done ({len(pre_dfs)} tickers).")

    N_WORKERS = min(8, os.cpu_count() or 4)
    with Pool(N_WORKERS, initializer=_pool_init,
              initargs=(pre_dfs, vix, spy_trend, stlfsi4)) as shared_pool:

        run_gate_research_v17(all_dfs, vix, spy_trend, stlfsi4,
                              pool=shared_pool, pre_dfs=pre_dfs)


if __name__ == "__main__":
    main()
