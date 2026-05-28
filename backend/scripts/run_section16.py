"""
run_section16.py — Focused §16 full-universe sector research runner.

Skips §13-§15 entirely. Loads expanded 94-ticker universe (24 base + 70
expansion), applies extra indicators, then runs §16 (all 11 sectors):
  §16a  Sector baselines        — each sector at default ATR floors
  §16b  Hold sweep              — 5 / 7 / 10 per sector
  §16c  VIX floor sweep         — None / ≥13 / ≥15 per sector
  §16d  BUY_THRESH sweep        — 38 / 40 / 42 per sector
  §16e  ATR floor sweep         — ≥20 / ≥30 per sector
  §16f  Best combined           — auto-selected winners applied per sector
  §16g  Sector ranking          — rank all sectors by optimal Ann.Sharpe

Expected runtime: ~90-100 minutes.

Usage:
    cd backend
    python scripts/run_section16.py 2>&1 | tee /tmp/decomp_§16.log
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
    run_full_sector_research,
)


def main() -> None:
    print("# §16 Full-Universe Sector Research\n")
    print("> Skipping §13-§15. Loading data then jumping straight to §16.")
    print(f"> {len(TICKERS)} tickers · MR=0.1 · Period: {START} → {END}\n")

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

    # ── Extra indicators ──────────────────────────────────────────────────────
    print("Computing extra indicators (WK52, RS, RS_RANK, CMF, DONCHIAN, HYG, PRICESTR)…", flush=True)
    spy_s = spy_closes if not spy_closes.empty else None
    hyg_s = hyg_closes if not hyg_closes.empty else None
    for df in all_dfs.values():
        compute_extra_indicators(df, spy_closes=spy_s, hyg_closes=hyg_s)

    print(f"\n  {len(all_dfs)} tickers ready. Pre-scoring and building shared pool…\n")

    # ── Pre-score once; share pool for §16 ───────────────────────────────────
    print("Pre-scoring tickers (MR=0.1)…", end=" ", flush=True)
    pre_dfs = _prescore(all_dfs, mr_w=0.1)
    print(f"done ({len(pre_dfs)} tickers).")

    N_WORKERS = min(8, os.cpu_count() or 4)
    with Pool(N_WORKERS, initializer=_pool_init, initargs=(pre_dfs, vix, spy_trend, stlfsi4)) as shared_pool:
        # ── §16. Full-Universe Sector Research ───────────────────────────────
        run_full_sector_research(all_dfs, vix, spy_trend, stlfsi4, pool=shared_pool, pre_dfs=pre_dfs)


if __name__ == "__main__":
    main()
