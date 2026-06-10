"""
backend/scripts/cross_sectional_mr_backtest.py

Cross-sectional mean-reversion backtest on the S&P 500 constituents.

Compares our per-trade mean-reversion edge (IC) in a high-breadth, daily-rebalanced,
market-neutral framework against the low-breadth, long-only retail signal design.

Methodology:
  1. Load all S&P 500 constituents and their historical OHLCV data.
  2. Filter by point-in-time index membership (enforcing survivorship bias correction).
  3. Compute the exact vectorized technical reversion score (BB%B, IBS, VWAP%, RSI).
  4. Daily/weekly rebalance:
     - Rank active constituents by score.
     - Long top decile (most oversold, high score).
     - Short bottom decile (most overbought, low score).
     - Calculate gross forward returns.
     - Charge turnover-based transaction costs (friction).
  5. Report annualized CAGR, Volatility, Sharpe (Gross & Net), Max DD, and Turnover.

Run from backend/:
    python scripts/cross_sectional_mr_backtest.py
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.abspath(os.path.join(_HERE, ".."))
sys.path.insert(0, _BACKEND)

from scripts.backtest_technicals import (
    START,
    END,
    TICKERS as CURATED_TICKERS,
    compute_indicators,
    compute_scores,
    TICKER_TO_SECTOR,
    cached_yf_download,
)

_OHLCV_DIR = os.path.join(_BACKEND, "data", "cache_ohlcv")
_CONSTITUENTS_JSON = os.path.join(_BACKEND, "data", "sp500_historical_constituents.json")
_MEMBERSHIP_CSV = os.path.join(_BACKEND, "data", "sp500_ticker_start_end.csv")


def _norm_ticker(ticker: str) -> str:
    return ticker.replace(".", "-")


def load_and_compute_ticker(args):
    ticker, start, end, cache_indicators_dir = args
    ticker_clean = ticker.replace("^", "_").replace("-", "_").replace(" ", "_")

    # Check if indicator cache exists
    matches = sorted(glob.glob(os.path.join(cache_indicators_dir, f"{ticker_clean}_{start}_*.csv")))
    df = None
    if matches:
        path = matches[-1]
        try:
            df = pd.read_csv(path, index_col=0, parse_dates=True)
        except Exception:
            df = None

    if df is None:
        df = load_ohlcv(ticker)
        if df is None or len(df) < 100:
            return ticker, None
        try:
            df = compute_indicators(df)
            # Save to cache
            cache_path = os.path.join(cache_indicators_dir, f"{ticker_clean}_{start}_{end}.csv")
            df.to_csv(cache_path)
        except Exception:
            return ticker, None

    return ticker, df


def compute_coint_z_series(ticker_prices: pd.Series, etf_prices: pd.Series, window: int = 252) -> pd.Series:
    combined = pd.DataFrame({"s": ticker_prices, "e": etf_prices}).dropna()
    if len(combined) < 60:
        return pd.Series(dtype=float, index=combined.index)
    W = window + 1
    s_col = combined["s"]
    e_col = combined["e"]

    sum_s = s_col.rolling(W, min_periods=60).sum()
    sum_e = e_col.rolling(W, min_periods=60).sum()
    sum_se = (s_col * e_col).rolling(W, min_periods=60).sum()
    sum_ee = (e_col**2).rolling(W, min_periods=60).sum()
    sum_ss = (s_col**2).rolling(W, min_periods=60).sum()
    N = s_col.rolling(W, min_periods=60).count()

    denom = N * sum_ee - sum_e**2
    denom_valid = denom.abs() > 1e-12

    beta = np.where(denom_valid, (N * sum_se - sum_s * sum_e) / denom, np.nan)
    alpha = np.where(denom_valid, (sum_s - beta * sum_e) / N, np.nan)

    resid_last = s_col - (beta * e_col + alpha)
    ss = sum_ss + beta**2 * sum_ee + N * alpha**2 - 2 * beta * sum_se - 2 * alpha * sum_s + 2 * beta * alpha * sum_e
    var = np.maximum(ss / (N - 1), 0.0)
    sigma = np.sqrt(var)

    z_score = np.where((sigma > 1e-8) & denom_valid, resid_last / sigma, np.nan)

    _COINT_REQUIRE_STATIONARY = True
    _COINT_ADF_PMAX = 0.10
    if _COINT_REQUIRE_STATIONARY:
        z_arr = np.asarray(z_score, dtype=float)
        sv = s_col.values
        ev = e_col.values
        ok = np.zeros(len(combined), dtype=bool)
        step = 63
        try:
            from statsmodels.tsa.stattools import coint

            for end in range(window, len(combined), step):
                try:
                    pval = coint(sv[end - window : end], ev[end - window : end])[1]
                except Exception:
                    pval = 1.0
                if pval < _COINT_ADF_PMAX:
                    ok[end : end + step] = True
            z_arr = np.where(ok, z_arr, np.nan)
        except Exception:
            pass
        return pd.Series(z_arr, index=combined.index)

    return pd.Series(z_score, index=combined.index)


def load_universe(source: str = "full") -> dict[str, list[tuple[pd.Timestamp, pd.Timestamp]]]:
    """Load point-in-time S&P 500 index constituent intervals."""
    cached = {os.path.basename(p).split("_")[0] for p in glob.glob(os.path.join(_OHLCV_DIR, "*_1d_adjTrue.csv"))}

    allowed = None
    if source == "curated":
        allowed = {_norm_ticker(str(t)) for t in CURATED_TICKERS}

    universe = {}

    def _eligible(ticker: str) -> bool:
        return (
            bool(ticker)
            and ticker not in {"SPY", "QQQ"}
            and ticker in cached
            and (allowed is None or ticker in allowed)
        )

    # Try CSV first
    if os.path.exists(_MEMBERSHIP_CSV):
        df = pd.read_csv(_MEMBERSHIP_CSV)
        for _, row in df.iterrows():
            ticker = _norm_ticker(str(row["ticker"]))
            if not _eligible(ticker):
                continue
            start = pd.to_datetime(row["start_date"], errors="coerce")
            end = pd.to_datetime(row.get("end_date"), errors="coerce")
            if pd.isna(start):
                continue
            if pd.isna(end):
                end = pd.Timestamp("2100-01-01")
            universe.setdefault(ticker, []).append((start, end))
        if universe:
            return universe

    # Fallback to legacy JSON
    if os.path.exists(_CONSTITUENTS_JSON):
        with open(_CONSTITUENTS_JSON) as f:
            raw = json.load(f)
        for ticker, intervals in raw.items():
            ticker = _norm_ticker(ticker)
            if not _eligible(ticker):
                continue
            spans = []
            for span in intervals:
                start = pd.to_datetime(span[0])
                end_raw = span[1] if len(span) > 1 and span[1] else "2100-01-01"
                spans.append((start, pd.to_datetime(end_raw)))
            if spans:
                universe[ticker] = spans

    return universe


def load_ohlcv(ticker: str) -> pd.DataFrame | None:
    """Load adjusted price history for a ticker, stripping multirow headers if any."""
    matches = sorted(glob.glob(os.path.join(_OHLCV_DIR, f"{ticker}_*_1d_adjTrue.csv")))
    if not matches:
        return None
    path = matches[-1]
    try:
        # Check if file has a multirow header (skip if row 1 starts with Ticker)
        df = pd.read_csv(path, skiprows=[1, 2])
    except Exception:
        return None
    df = df.rename(columns={"Price": "Date"})
    if "Date" not in df.columns or "Close" not in df.columns:
        return None
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).set_index("Date").sort_index()
    for col in ("Open", "High", "Low", "Close", "Volume"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Close"])

    # Clean bad data/penny stock anomalies (S&P 500 constituents shouldn't be under $1)
    df = df[df["Close"] >= 1.0]

    # Filter extreme daily return outliers (unadjusted stock splits or data errors)
    if len(df) > 1:
        pct = df["Close"].pct_change()
        valid_mask = (pct.isna()) | ((pct > -0.8) & (pct < 1.5))
        df = df[valid_mask]

    return df[["Open", "High", "Low", "Close", "Volume"]] if not df.empty else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, default="full", choices=["full", "curated"])
    parser.add_argument("--decile", type=float, default=0.10, help="decile threshold (e.g. 0.10 = top/bottom 10%)")
    parser.add_argument("--horizon", type=int, default=1, help="rebalance horizon in trading days")
    parser.add_argument("--cost-bps", type=float, default=15.0, help="one-way execution cost on turnover in bps")
    parser.add_argument("--quick", action="store_true", help="run on first 30 tickers only to debug")
    parser.add_argument("--start", type=str, default="2003-01-01")
    parser.add_argument("--end", type=str, default="2026-06-09")
    args = parser.parse_args()

    print("\n# Cross-Sectional Mean-Reversion Backtest — Signal.Trade")
    print(f"  Period   : {args.start} to {args.end}")
    print(f"  Horizon  : {args.horizon}d rebalance")
    print(f"  Decile   : {args.decile:.2f} ({args.decile * 100:.0f}%)")
    print(f"  Friction : {args.cost_bps:.1f} bps per trade ({args.cost_bps * 2:.1f} bps round-trip per turn)\n")

    # 1. Load S&P universe membership
    print("Loading index constituent intervals...")
    universe = load_universe(args.source)
    tickers = list(universe.keys())
    if args.quick:
        tickers = tickers[:30]
        print(f"  [Quick Mode] restricted to first {len(tickers)} tickers.")
    print(f"Loaded {len(universe)} constituent mapping paths.")

    # 2. Load and compute technical indicators/scores for each constituent
    print("Loading OHLCV data & computing technical reversion scores...")
    cache_ind_dir = os.path.join(_BACKEND, "data", "cache_indicators")
    os.makedirs(cache_ind_dir, exist_ok=True)

    args_list = [(t, START, END, cache_ind_dir) for t in tickers]

    print(f"Loading/calculating technical indicators for {len(tickers)} tickers sequentially...")
    raw_ticker_dfs = {}
    n_processed = 0
    for t_args in args_list:
        ticker, df = load_and_compute_ticker(t_args)
        if df is not None:
            raw_ticker_dfs[ticker] = df
        n_processed += 1
        if n_processed % 50 == 0:
            print(
                f"  Processed {n_processed}/{len(tickers)} tickers (loaded {len(raw_ticker_dfs)} valid)...", flush=True
            )

    print(f"Successfully loaded {len(raw_ticker_dfs)} tickers. Computing sector cointegration Z-scores...")

    # Compute cointegration Z-scores
    _sector_etfs = list({TICKER_TO_SECTOR.get(t, "XLK") for t in raw_ticker_dfs})
    try:
        _etf_raw = cached_yf_download(
            _sector_etfs, start=START, end=END, interval="1d", auto_adjust=True, progress=False
        )
        if isinstance(_etf_raw.columns, pd.MultiIndex):
            _etf_close = _etf_raw["Close"]
        else:
            _etf_close = _etf_raw[["Close"]] if "Close" in _etf_raw.columns else _etf_raw
        _etf_close.index = pd.to_datetime([str(i)[:10] for i in _etf_close.index])

        for t, df in raw_ticker_dfs.items():
            etf_name = TICKER_TO_SECTOR.get(t, "XLK")
            if etf_name in _etf_close.columns:
                etf_p = _etf_close[etf_name]
                cz = compute_coint_z_series(df["Close"], etf_p)
                df["coint_z"] = cz.reindex(df.index)
    except Exception as e:
        print(f"Warning: Cointegration calculation failed ({e}), scores will be computed without it.")

    print("Computing technical scores...")
    ticker_data = {}
    for t, df in raw_ticker_dfs.items():
        try:
            df["score"] = compute_scores(df)
            ticker_data[t] = df
        except Exception as e:
            print(f"Failed to score {t}: {e}")

    print(f"Successfully processed {len(ticker_data)} tickers with technical scores.")

    # 3. Align daily cross-sectional panel
    print("Aligning panel dates...")
    start_ts = pd.Timestamp(args.start)
    end_ts = pd.Timestamp(args.end)

    # Generate unified trading calendar (use SPY or union of dates)
    spy_df = load_ohlcv("SPY")
    if spy_df is not None:
        all_dates = spy_df.index
    else:
        all_dates = pd.DatetimeIndex(sorted(list(set().union(*(df.index for df in ticker_data.values())))))

    trading_dates = all_dates[(all_dates >= start_ts) & (all_dates <= end_ts)]
    print(f"Aligned {len(trading_dates)} trading days.")

    # 4. Run the rebalance simulation
    print("Simulating cross-sectional long/short book...")

    gross_returns = []
    turnovers = []
    dates_run = []

    prev_long = set()
    prev_short = set()

    # We step by the rebalance horizon
    for idx in range(0, len(trading_dates) - args.horizon, args.horizon):
        date = trading_dates[idx]
        next_date = trading_dates[idx + args.horizon]

        # Collect active constituents and their scores on this date
        candidates = []
        for t, df in ticker_data.items():
            # Check point-in-time membership
            spans = universe.get(t, [])
            is_member = False
            for start, end in spans:
                if start <= date <= end:
                    is_member = True
                    break

            if is_member and date in df.index and next_date in df.index:
                row = df.loc[date]
                next_row = df.loc[next_date]

                score = row["score"]
                # Forward return close-to-close over the horizon
                fwd_ret = (next_row["Close"] / row["Close"]) - 1.0

                if pd.notna(score) and pd.notna(fwd_ret):
                    if row["Close"] >= 1.0 and next_row["Close"] >= 1.0 and abs(fwd_ret) < 0.5:
                        candidates.append({"ticker": t, "score": score, "fwd_ret": fwd_ret})

        n_names = len(candidates)
        if n_names < 20:  # don't trade on thin days
            continue

        df_candidates = pd.DataFrame(candidates)
        df_candidates = df_candidates.sort_values("score", ascending=False).reset_index(drop=True)

        k = max(1, int(round(n_names * args.decile)))

        # Long the highest scores (most oversold)
        long_set = set(df_candidates["ticker"].iloc[:k])
        # Short the lowest scores (most overbought)
        short_set = set(df_candidates["ticker"].iloc[n_names - k :])

        # Compute returns
        ret_map = dict(zip(df_candidates["ticker"], df_candidates["fwd_ret"]))
        long_ret = np.mean([ret_map[t] for t in long_set])
        short_ret = np.mean([ret_map[t] for t in short_set])

        # L/S gross return
        gross = long_ret - short_ret

        # Calculate one-way turnover per leg
        long_turnover = len(long_set ^ prev_long) / (2 * k) if prev_long else 1.0
        short_turnover = len(short_set ^ prev_short) / (2 * k) if prev_short else 1.0
        total_turnover = long_turnover + short_turnover

        gross_returns.append(gross)
        turnovers.append(total_turnover)
        dates_run.append(date)

        prev_long = long_set
        prev_short = short_set

    if not gross_returns:
        print("Error: No trading dates found with sufficient constituents. Aborting.")
        return

    # 5. Compute statistics
    print("Computing metrics...")
    df_perf = pd.DataFrame({"gross": gross_returns, "turnover": turnovers}, index=dates_run)

    # Net returns
    df_perf["net"] = df_perf["gross"] - df_perf["turnover"] * (args.cost_bps * 1e-4)

    # Annualization factor
    periods_per_year = 252.0 / args.horizon

    avg_gross = df_perf["gross"].mean() * periods_per_year
    vol_gross = df_perf["gross"].std() * np.sqrt(periods_per_year)
    sharpe_gross = avg_gross / vol_gross if vol_gross > 0 else 0.0

    avg_net = df_perf["net"].mean() * periods_per_year
    vol_net = df_perf["net"].std() * np.sqrt(periods_per_year)
    sharpe_net = avg_net / vol_net if vol_net > 0 else 0.0

    avg_turnover = df_perf["turnover"].mean()
    max_dd = (df_perf["net"].cumsum() - df_perf["net"].cumsum().cummax()).min()

    print("\n## Backtest Results\n")
    print("| Metric | Gross (Before Costs) | Net (After Costs) |")
    print("|:---|---:|---:|")
    print(f"| Annualized Return | {avg_gross * 100:.2f}% | {avg_net * 100:.2f}% |")
    print(f"| Annualized Vol    | {vol_gross * 100:.2f}% | {vol_net * 100:.2f}% |")
    print(f"| Sharpe Ratio      | **{sharpe_gross:.2f}** | **{sharpe_net:.2f}** |")
    print(f"| Max Drawdown      | — | {max_dd * 100:.2f}% |")
    print(f"| Rebalance Periods | {len(df_perf)} | {len(df_perf)} |")
    print(f"| Avg Turnover/Period| {avg_turnover * 100:.1f}% | (100% = full portfolio turn) |")
    print()


if __name__ == "__main__":
    main()
