"""Backfill OHLCV cache for the FULL S&P 500 constituent history.

Reads the survivorship-bias-free membership list
(`data/sp500_ticker_start_end.csv`, sourced from github.com/fja05680/sp500) and
downloads adjusted daily OHLCV for every constituent not already cached, writing
each into the SAME format `cache_ohlcv/` already uses so the rest of the pipeline
(backtest_technicals, cross_sectional_alpha_model) can read it transparently.

REALITY: free yfinance only serves names that still trade. Delisted constituents
(LEH, AABA, AAMRQ, …) return empty and are skipped — that residual price-side
survivorship bias is exactly TODO §84 (needs paid Norgate/EODHD to close). What
this DOES buy is a ~3-4x wider live-name cross-section, which raises a
market-neutral book's Sharpe via breadth (∝ √N) independent of signal quality.

    cd backend && python scripts/fetch_sp500_ohlcv.py            # fetch all missing
    cd backend && python scripts/fetch_sp500_ohlcv.py --limit 20 # smoke test
"""

from __future__ import annotations

import argparse
import glob
import os
import warnings

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.abspath(os.path.join(_HERE, "..", "data"))
_OHLCV_DIR = os.path.join(_DATA, "cache_ohlcv")
_MEMBERSHIP = os.path.join(_DATA, "sp500_ticker_start_end.csv")
START = "2003-01-01"


def _yf_symbol(ticker: str) -> str:
    """yfinance uses dashes for share-class suffixes (BF.B -> BF-B)."""
    return ticker.replace(".", "-")


def _cache_path(symbol: str, last: pd.Timestamp) -> str:
    return os.path.join(_OHLCV_DIR, f"{symbol}_{START}_{last.date()}_1d_adjTrue.csv")


def _already_cached(symbol: str) -> bool:
    return bool(glob.glob(os.path.join(_OHLCV_DIR, f"{symbol}_*_1d_adjTrue.csv")))


def _write_cache(symbol: str, df: pd.DataFrame) -> None:
    """Persist one ticker in the exact 3-row-header layout the loader expects:

    Price,Close,High,Low,Open,Volume
    Ticker,<sym>,<sym>,<sym>,<sym>,<sym>
    Date,,,,,
    2003-01-02,<close>,<high>,<low>,<open>,<volume>
    """
    df = df[["Close", "High", "Low", "Open", "Volume"]].dropna(how="all")
    if df.empty:
        return
    last = df.index.max()
    lines = [
        "Price,Close,High,Low,Open,Volume",
        f"Ticker,{symbol},{symbol},{symbol},{symbol},{symbol}",
        "Date,,,,,",
    ]
    for ts, row in df.iterrows():
        lines.append(f"{ts.date()},{row['Close']},{row['High']},{row['Low']},{row['Open']},{int(row['Volume'])}")
    with open(_cache_path(symbol, last), "w") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="Backfill full S&P 500 OHLCV cache")
    ap.add_argument("--batch-size", type=int, default=40, help="tickers per yfinance call")
    ap.add_argument("--limit", type=int, default=0, help="cap tickers (0 = all) for testing")
    args = ap.parse_args()

    members = pd.read_csv(_MEMBERSHIP)
    tickers = sorted(set(members["ticker"].astype(str)))
    pending = [t for t in tickers if not _already_cached(_yf_symbol(t))]
    if args.limit:
        pending = pending[: args.limit]
    print(f"{len(tickers)} constituents | {len(pending)} to fetch (rest cached)")

    ok, empty, err = 0, 0, 0
    for i in range(0, len(pending), args.batch_size):
        batch = pending[i : i + args.batch_size]
        syms = [_yf_symbol(t) for t in batch]
        try:
            data = yf.download(
                syms,
                start=START,
                auto_adjust=True,
                progress=False,
                threads=True,
                group_by="ticker",
            )
        except Exception as exc:
            print(f"  batch {i // args.batch_size} failed: {exc}")
            err += len(batch)
            continue

        for sym in syms:
            try:
                # Multi-ticker frames are keyed by symbol at the top column level;
                # a single-ticker fallback returns a flat frame.
                sub = data[sym] if isinstance(data.columns, pd.MultiIndex) else data
                if sub is None or sub.dropna(how="all").empty:
                    empty += 1
                    continue
                _write_cache(sym, sub)
                ok += 1
            except Exception:
                err += 1
        done = i + len(batch)
        print(f"  {done}/{len(pending)}  ok={ok} delisted/empty={empty} err={err}")

    print(f"\nDone. fetched={ok}  delisted/empty={empty}  errors={err}")
    print(f"Cache now holds {len(glob.glob(os.path.join(_OHLCV_DIR, '*_1d_adjTrue.csv')))} tickers.")


if __name__ == "__main__":
    main()
