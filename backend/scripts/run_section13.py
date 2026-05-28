"""
run_section13.py — Focused §13 + §14 research runner.

Skips §10a-§12 entirely. Loads full ticker universe (74 base + 7 new tech),
applies extra indicators, then runs §13 (ATR regime + beta-hedge) and
§14 (Tech/FAANG sector optimization: 5-day hold, BUY_THRESH=38, new tickers).

Expected runtime: ~60 minutes.

Usage:
    cd backend
    python scripts/run_section13.py 2>&1 | tee /tmp/decomp_§14.log
"""

from __future__ import annotations

import os
import sys
import warnings
from multiprocessing import Pool

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
    START,
    fetch_spy_trend,
    fetch_stlfsi4,
    process_ticker,
)
from signal_alpha_decomposition import (
    TICKERS,
    _download_etf_closes,
    _pool_init,
    _prescore,
    _section,
    compute_extra_indicators,
    run_atr_research,
    run_sector_research,
    run_tech_optimization,
)


def main() -> None:
    print("# §13 Focused Research Run — ATR Regime + Beta-Hedge\n")
    print("> Skipping §10a-§12. Loading data then jumping straight to §13.")
    print(f"> 74 tickers · MR=0.1 + ATR%rank≥20 base · Period: {START} → {END}\n")

    # ── Fetch alt-data ────────────────────────────────────────────────────────
    print("Fetching VIX…", end=" ", flush=True)
    try:
        vix_df = yf.download("^VIX", start=START, end=END, interval="1d", auto_adjust=False, progress=False)
        if isinstance(vix_df.columns, pd.MultiIndex):
            vix_df.columns = vix_df.columns.get_level_values(0)
        vix = {pd.Timestamp(str(k)[:10]): float(v) for k, v in vix_df["Close"].items() if pd.notna(v)}
        print(f"ok ({len(vix)} bars)")
    except Exception as e:
        vix = {}
        print(f"failed ({e})")

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

    # ── Parallel ticker download + bt indicators ──────────────────────────────
    _section(f"Downloading {len(TICKERS)} tickers")
    print(f"\nDownloading {len(TICKERS)} tickers (parallel)…\n")
    with Pool(8) as p:
        results = p.map(
            process_ticker,
            [(t, vix, spy_trend, stlfsi4, True) for t in TICKERS],
        )

    all_dfs: dict = {}
    for ticker, _t, _bh, df in results:
        if df is not None:
            all_dfs[ticker] = df

    if not all_dfs:
        print("[error] No ticker data loaded.")
        return

    # ── Extra indicators (required by compute_scores_masked inside §13) ───────
    print("Computing extra indicators (WK52, RS, RS_RANK, CMF, DONCHIAN, HYG, PRICESTR)…", flush=True)
    spy_s = spy_closes if not spy_closes.empty else None
    hyg_s = hyg_closes if not hyg_closes.empty else None
    for df in all_dfs.values():
        compute_extra_indicators(df, spy_closes=spy_s, hyg_closes=hyg_s)

    print(f"\n  {len(all_dfs)} tickers ready. Pre-scoring and building shared pool…\n")

    # ── Pre-score once; share pool across §13 + §14 (avoids macOS spawn deadlock) ──
    print("Pre-scoring tickers (MR=0.1)…", end=" ", flush=True)
    pre_dfs = _prescore(all_dfs, mr_w=0.1)
    print(f"done ({len(pre_dfs)} tickers).")

    N_WORKERS = min(8, os.cpu_count() or 4)
    with Pool(N_WORKERS, initializer=_pool_init, initargs=(pre_dfs, vix, spy_trend, stlfsi4)) as shared_pool:
        # ── §13. ATR Regime & Beta-Hedge Research ────────────────────────────
        run_atr_research(all_dfs, vix, spy_trend, stlfsi4, spy_closes=spy_s, pool=shared_pool, pre_dfs=pre_dfs)

        # ── §14. Tech/FAANG Sector Optimization ──────────────────────────────
        run_tech_optimization(all_dfs, vix, spy_trend, stlfsi4, pool=shared_pool, pre_dfs=pre_dfs)

        # ── §15. Sector-Specific Filter Research ─────────────────────────────
        run_sector_research(all_dfs, vix, spy_trend, stlfsi4, pool=shared_pool, pre_dfs=pre_dfs)


if __name__ == "__main__":
    main()
