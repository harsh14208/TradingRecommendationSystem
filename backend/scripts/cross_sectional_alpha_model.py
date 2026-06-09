"""Cross-sectional, market-neutral alpha model (Qlib-style) for Signal.Trade.

WHY THIS EXISTS
---------------
The legacy engine predicts an *absolute* up/down move for one ticker at a time,
so its returns carry market beta and its Sharpe is capped (~0.28 IS). This script
implements the opposite paradigm: every trading day we *rank* the whole S&P 500
cross-section against itself and trade the spread (long the best-ranked decile,
short the worst). A dollar-neutral long/short book has, by construction, ~zero
net beta, so its Sharpe is no longer bounded by the market's Sharpe — the path to
1.0+ runs through (a) a real cross-sectional signal and (b) keeping turnover cost
below the gross spread. Those two are the whole game; everything else is plumbing.

HONESTY GUARDRAILS (read before trusting any number this prints)
----------------------------------------------------------------
A market-neutral Sharpe is trivially easy to *fake*. This script is built to not
fake it, and the headline number is the OOS, net-of-cost Sharpe — not gross, not
in-sample. Specifically:
  * Survivorship-bias-free universe: membership is taken from point-in-time S&P
    constituent intervals, so we never trade a name before it joined the index.
  * No lookahead in features: cross-sectional z-scores use ONLY same-day data.
  * No lookahead in the split: train and test are chronological with an embargo
    gap of one forecast horizon between them (the target is forward-looking, so a
    naive split leaks the boundary).
  * No overlapping-return inflation: we rebalance every HORIZON days
    (non-overlapping), the standard fix for autocorrelated overlapping samples.
  * Costs are charged on turnover. A daily/decile L/S book turns over almost
    fully every rebalance; ignoring that is the #1 way a "1.0 Sharpe" evaporates
    in production. Gross AND net are printed so the cost drag is explicit.

DATA REALITY (what's actually on disk, not what we wish we had)
--------------------------------------------------------------
  * cache_ohlcv/   yfinance CSVs, adjusted, 2003-present. Multi-row header.
  * cache_earnings/  JSON list of earnings *dates* only — NO surprise magnitude.
    So we engineer earnings *proximity* features, not a surprise factor. Swap in
    a real surprise feed later via add_earnings_features().
  * short_interest_biweekly (Postgres)  bi-weekly, ~2017-12+. Optional; loaded
    only with --short-interest and degrades gracefully if the DB is unreachable.

USAGE
-----
    cd backend && python scripts/cross_sectional_alpha_model.py
    cd backend && python scripts/cross_sectional_alpha_model.py --short-interest
    cd backend && python scripts/cross_sectional_alpha_model.py --split 2019-01-01 --decile 0.1 --cost-bps 10

The feature engineering is intentionally split into small add_*_features() helpers
so you can iterate on signals without touching the pipeline or the backtester.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

# xgboost is the installed gradient booster (3.2.0); lightgbm is interchangeable
# if you prefer it — the model interface used here is the sklearn wrapper.
import xgboost as xgb

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.abspath(os.path.join(_HERE, ".."))
_DATA = os.path.join(_BACKEND, "data")
_OHLCV_DIR = os.path.join(_DATA, "cache_ohlcv")
_EARNINGS_DIR = os.path.join(_DATA, "cache_earnings")
_CONSTITUENTS = os.path.join(_DATA, "sp500_historical_constituents.json")
_MEMBERSHIP_CSV = os.path.join(_DATA, "sp500_ticker_start_end.csv")  # full PIT history

# Forward-return horizon = rebalance period in trading days. Was 5 (weekly);
# raised to 21 (~monthly) 2026-06-09 after the horizon sweep: net Sharpe goes
# -0.058 (h=5) -> +0.347 (h=21), because fewer/larger rebalances slash annual
# turnover cost (the binding constraint — per-rebalance turnover is flat ~1.34,
# but ~12 rebalances/yr vs ~50 cuts total cost drag ~4x). h=21 is cost-robust to
# ~20bps one-way and 11/15 OOS folds are net-positive. h=25 is a lower-drawdown
# variant (net +0.322, MaxDD -24.7% vs -30.9%) — run `--horizon 25` for it.
HORIZON = 21  # forward-return horizon in trading days; also the rebalance period
MIN_NAMES_PER_DAY = 20  # don't z-score / trade a thin cross-section
TRADING_DAYS = 252
FWD_RET_CAP = 0.50  # data-error guard: clip |5d forward return| beyond this

# Tickers in the OHLCV cache that are ETFs/indices, not single-name equities.
# They must never enter the stock cross-section (they'd dominate the ranks).
_ETF_LIKE = {
    "SPY",
    "QQQ",
    "DIA",
    "IWM",
    "HYG",
    "TLT",
    "UUP",
    "GLD",
    "SLV",
    "USO",
    "XLB",
    "XLC",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLP",
    "XLRE",
    "XLU",
    "XLV",
    "XLY",
    "VXX",
    "UVXY",
    "EEM",
    "EFA",
}
BENCHMARK = "SPY"  # used only for reporting / sanity, not for the neutral target


# ---------------------------------------------------------------------------
# Step 1: Data ingestion & merge
# ---------------------------------------------------------------------------


def _latest_ohlcv_path(ticker: str) -> str | None:
    """Return the most recent cached OHLCV CSV for ``ticker`` (cache filenames
    embed an end-date, so several vintages can coexist; we take the newest)."""
    matches = sorted(glob.glob(os.path.join(_OHLCV_DIR, f"{ticker}_*_1d_adjTrue.csv")))
    return matches[-1] if matches else None


def load_ohlcv(ticker: str) -> pd.DataFrame | None:
    """Load one ticker's adjusted OHLCV as a tidy DatetimeIndex DataFrame.

    yfinance writes a 3-row header we have to defuse:
        row 0: Price,Close,High,Low,Open,Volume   <- real column names
        row 1: Ticker,AAPL,AAPL,...               <- noise
        row 2: Date,,,,,                          <- noise
        row 3+: 2003-01-02,0.22,...               <- data (col 0 is the date)
    We keep header row 0, drop rows 1-2, and rename the leading column to Date.
    """
    path = _latest_ohlcv_path(ticker)
    if not path:
        return None
    try:
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
    return df[["Open", "High", "Low", "Close", "Volume"]] if not df.empty else None


def _norm_ticker(ticker: str) -> str:
    """Match the cache filename convention (BF.B -> BF-B, same as yfinance)."""
    return ticker.replace(".", "-")


def load_universe(source: str = "full") -> dict[str, list[tuple[pd.Timestamp, pd.Timestamp]]]:
    """Load the survivorship-bias-free S&P membership intervals.

    Returns {ticker: [(start, end), ...]} where each interval is a window the
    ticker was an index member. The panel is masked so a name only trades on days
    it was actually in the index — the §84 point-in-time fix.

    source="full"    -> FULL constituent history (`sp500_ticker_start_end.csv`,
                        from github.com/fja05680/sp500 — 1200+ names). Wide but
                        diluted/contaminated by recycled tickers (see §86 Step 6).
    source="curated" -> the live engine's VALIDATED IS universe
                        (`backtest_technicals.TICKERS`, ~110 large/liquid names) —
                        the set that actually produced the 0.42 baseline and where
                        the edge lives. PIT intervals are still taken from the full
                        membership history; we just restrict to these names.

    Only tickers that ALSO have an OHLCV cache and are not ETFs survive, so the
    live universe = (constituents ∩ fetchable prices).
    """
    cached = {os.path.basename(p).split("_")[0] for p in glob.glob(os.path.join(_OHLCV_DIR, "*_1d_adjTrue.csv"))}

    allowed: set[str] | None = None
    if source == "curated":
        try:  # works whether run as a file (scripts/ on path) or as a module
            import backtest_technicals as bt  # type: ignore
        except ModuleNotFoundError:
            import scripts.backtest_technicals as bt
        allowed = {_norm_ticker(str(t)) for t in bt.TICKERS}  # the live IS universe

    universe: dict[str, list[tuple[pd.Timestamp, pd.Timestamp]]] = {}

    def _eligible(ticker: str) -> bool:
        return bool(ticker) and ticker not in _ETF_LIKE and ticker in cached and (allowed is None or ticker in allowed)

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
            if pd.isna(end):  # blank end = still a current member
                end = pd.Timestamp("2100-01-01")
            universe.setdefault(ticker, []).append((start, end))
        if universe:
            return universe

    # Fallback: legacy JSON {ticker: [[start, end], ...]}.
    with open(_CONSTITUENTS) as f:
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


def _membership_mask(dates: pd.DatetimeIndex, spans) -> np.ndarray:
    """Boolean array: True on each date the ticker was an index member."""
    mask = np.zeros(len(dates), dtype=bool)
    for start, end in spans:
        mask |= (dates >= start) & (dates <= end)
    return mask


def load_earnings(ticker: str) -> list[pd.Timestamp]:
    """Earnings *dates* (no surprise magnitude is cached). Sorted ascending."""
    path = os.path.join(_EARNINGS_DIR, f"{ticker}.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            raw = json.load(f)
    except Exception:
        return []
    out = sorted(pd.to_datetime(d, errors="coerce") for d in raw)
    return [d for d in out if pd.notna(d)]


def load_short_interest(tickers: list[str]) -> pd.DataFrame:
    """Optional bi-weekly short interest from Postgres (short_interest_biweekly).

    Returns a long DataFrame [ticker, date, short_interest, days_to_cover] or an
    empty frame if the DB is unreachable / table absent. We never let alt-data
    availability break the core OHLCV pipeline — short interest is additive only,
    and only exists ~2017-12+ so it can't drive the early sample anyway.
    """
    try:
        from sqlalchemy import create_engine, text

        from database import DATABASE_URL  # resolved from .env / env

        # The app uses an async driver; strip it for a plain sync read here.
        url = DATABASE_URL.replace("+asyncpg", "").replace("+aiosqlite", "")
        engine = create_engine(url)
        q = text(
            "SELECT ticker, date, short_interest, days_to_cover FROM short_interest_biweekly WHERE ticker = ANY(:tk)"
        )
        with engine.connect() as conn:
            df = pd.read_sql(q, conn, params={"tk": list(tickers)})
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as exc:  # pragma: no cover - environment dependent
        print(f"  [short-interest] unavailable, continuing without it: {exc}")
        return pd.DataFrame(columns=["ticker", "date", "short_interest", "days_to_cover"])


# ---------------------------------------------------------------------------
# Feature engineering — each helper adds raw (pre-normalization) columns.
# Add your own factor by writing another add_*_features() and registering it in
# build_panel(); cross-sectional normalization (Step 2) is applied generically.
# ---------------------------------------------------------------------------

# Columns produced below that should be cross-sectionally z-scored each day.
RAW_FEATURE_COLS = [
    "mom_12_1",  # 12-1 month momentum (skip last month) — classic XS factor
    "rev_5",  # 5-day short-term reversal
    "rev_21",  # 21-day reversal / mean-reversion pressure
    "vol_21",  # 21-day realized volatility (low-vol anomaly)
    "dollar_vol_21",  # liquidity / size proxy
    "dist_ma50",  # price distance from 50d MA (stretch)
    "rsi_14",  # Wilder RSI (overbought/oversold)
    "days_since_earn",  # earnings proximity (no surprise data available)
]


def add_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """Momentum / reversal / volatility / liquidity from adjusted prices.

    Every feature uses ONLY past data as of each row's date (rolling windows and
    backward returns), so there is no lookahead within a ticker. Cross-sectional
    normalization in Step 2 is what makes them comparable across names.
    """
    out = df.copy()
    close = out["Close"]
    ret1 = close.pct_change()

    # 12-1 momentum: cumulative return from t-252 to t-21 (skip the last month to
    # avoid contaminating with the short-term-reversal effect).
    out["mom_12_1"] = close.shift(21) / close.shift(252) - 1.0
    out["rev_5"] = close / close.shift(5) - 1.0
    out["rev_21"] = close / close.shift(21) - 1.0
    out["vol_21"] = ret1.rolling(21).std()
    out["dollar_vol_21"] = (close * out["Volume"]).rolling(21).mean()
    out["dist_ma50"] = close / close.rolling(50).mean() - 1.0

    # Wilder RSI(14)
    delta = close.diff()
    gain = delta.clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0.0)).ewm(alpha=1 / 14, adjust=False).mean()
    rs = gain / loss.replace(0.0, np.nan)
    out["rsi_14"] = 100 - 100 / (1 + rs)
    return out


def add_earnings_features(df: pd.DataFrame, earnings: list[pd.Timestamp]) -> pd.DataFrame:
    """Days since the most recent earnings event (proximity factor).

    NOTE: the cache stores earnings *dates only*. A true earnings-surprise factor
    (SUE, drift) needs surprise magnitudes — wire those in here when available.
    Until then this captures post-earnings-announcement-drift timing, capped at
    63 days so a name with no recent print isn't treated as an extreme outlier.
    """
    out = df.copy()
    if not earnings:
        out["days_since_earn"] = np.nan
        return out
    earn_idx = pd.DatetimeIndex(earnings)
    pos = earn_idx.searchsorted(out.index, side="right") - 1
    days = np.full(len(out), np.nan)
    valid = pos >= 0
    days[valid] = (out.index[valid] - earn_idx[pos[valid]]).days
    out["days_since_earn"] = np.clip(days, 0, 63)
    return out


# Short-interest feature columns (level + VELOCITY). Velocity is the hypothesis
# under test: a rising short base (crowding) vs a falling one (covering) should
# carry cross-sectional information that the static level does not.
_SI_COLS = [
    "days_to_cover",  # level: short_interest / ADV (squeeze fuel)
    "si_chg_1",  # velocity: % change in shares-short vs prior settlement (~2wk)
    "si_chg_3",  # velocity: % change vs 3 settlements ago (~6wk, smoother)
    "dtc_chg_1",  # change in days-to-cover vs prior settlement
]


def add_short_interest_features(panel: pd.DataFrame, si: pd.DataFrame) -> pd.DataFrame:
    """Merge short-interest LEVEL + VELOCITY, as-of-joined to daily rows.

    Velocity is computed on the native bi-weekly cadence (pct/diff vs the prior
    *settlement*, not vs the forward-filled daily value) so it reflects real
    reporting-to-reporting change. We then merge_asof BACKWARD, attaching to each
    trading day only the most recent settlement on or before it — point-in-time
    correct (FINRA reports with a lag), zero lookahead. History is ~2017-12+, so
    pre-2018 rows get NaN → neutralized to 0 in the cross-sectional z-score.
    """
    if si.empty:
        return panel
    si = si.sort_values(["ticker", "date"]).copy()
    g = si.groupby("ticker")
    si["si_chg_1"] = g["short_interest"].pct_change(1)
    si["si_chg_3"] = g["short_interest"].pct_change(3)
    si["dtc_chg_1"] = g["days_to_cover"].diff(1)
    si = si.replace([np.inf, -np.inf], np.nan)  # guard div-by-zero in pct_change

    merged = []
    for ticker, grp in panel.groupby("ticker", sort=False):
        s = si[si["ticker"] == ticker][["date", *_SI_COLS]].dropna(subset=["days_to_cover"])
        grp = grp.sort_values("date")
        if s.empty:
            for c in _SI_COLS:
                grp[c] = np.nan
        else:
            grp = pd.merge_asof(grp, s, on="date", direction="backward")
        merged.append(grp)
    panel = pd.concat(merged, ignore_index=True)

    for c in _SI_COLS:
        if c in panel.columns and c not in RAW_FEATURE_COLS:
            RAW_FEATURE_COLS.append(c)
    return panel


# ---------------------------------------------------------------------------
# WorldQuant-101 orthogonal alphas (research EXP4/EXP5, 2026-06-09)
# ---------------------------------------------------------------------------
# Of 30 OHLCV-computable WQ-101 alphas screened for IC, two cleared usable IR
# (~0.11-0.14) AND low turnover AND the orthogonality bar (max |corr| ~0.2 vs the
# 8 RAW_FEATURE_COLS — genuinely new information, not repackaged reversal/RSI):
#   wq002 = -corr(rank(Δ²log volume), rank((close-open)/open), 6)   — vol/return microstructure
#   wq026 = -ts_max(corr(ts_rank(volume,5), ts_rank(high,5), 5), 3) — vol/high co-movement
# Both embed a cross-sectional rank(), so they're computed on the wide panel (not
# per-ticker) before the generic z-score. Enabled by --wq-alphas (off by default
# until the net-of-cost lift is confirmed). The dropped WQ candidates wq004
# (|corr|=0.62 vs rev_5) and wq019 (0.57 vs rsi_14) were redundant with existing
# reversal/RSI features.
WQ_ALPHA_COLS = ["wq002", "wq026"]


def _wq_alpha_panel(tickers: list[str]) -> pd.DataFrame:
    """Compute the orthogonal WQ-101 alphas on wide OHLCV panels.

    Returns a long [date, ticker, wq002, wq026] frame to merge into the model
    panel. Uses trailing windows only (no lookahead). ts_rank is vectorized via
    shift-counts (avoids a slow rolling.apply over the full universe).
    """
    o_, h_, c_, v_ = {}, {}, {}, {}
    for t in tickers:
        df = load_ohlcv(_norm_ticker(t))
        if df is None:
            df = load_ohlcv(t)
        if df is None or len(df) < 300:
            continue
        o_[t], h_[t], c_[t], v_[t] = df["Open"], df["High"], df["Close"], df["Volume"]
    if not c_:
        return pd.DataFrame(columns=["date", "ticker", *WQ_ALPHA_COLS])
    o = pd.DataFrame(o_).sort_index()
    h = pd.DataFrame(h_).reindex_like(o)
    c = pd.DataFrame(c_).reindex_like(o)
    v = pd.DataFrame(v_).reindex_like(o)

    def _rank(d):  # cross-sectional percentile rank
        return d.rank(axis=1, pct=True)

    def _corr(x, y, n):  # rolling Pearson per ticker
        mx, my = x.rolling(n).mean(), y.rolling(n).mean()
        cov = (x * y).rolling(n).mean() - mx * my
        sx, sy = x.rolling(n).std(ddof=0), y.rolling(n).std(ddof=0)
        return (cov / (sx * sy)).replace([np.inf, -np.inf], np.nan)

    def _ts_rank(d, n):  # percentile of current value within trailing n (vectorized)
        le = sum((d.shift(j) <= d).astype(float) for j in range(n))
        return le / n

    logv = np.log(v.where(v > 0))
    wq002 = -1 * _corr(_rank(logv - logv.shift(2)), _rank((c - o) / o), 6)
    wq026 = -1 * _corr(_ts_rank(v, 5), _ts_rank(h, 5), 5).rolling(3).max()

    out = pd.concat({"wq002": wq002.stack(), "wq026": wq026.stack()}, axis=1).reset_index()
    out.columns = ["date", "ticker", "wq002", "wq026"]
    return out


def build_panel(
    use_short_interest: bool = False,
    min_price: float = 5.0,
    min_dollar_vol: float = 1e7,
    universe_source: str = "full",
) -> pd.DataFrame:
    """Step 1 assembled: long panel [date, ticker, features..., fwd_ret].

    One row per (ticker, trading-day). Membership-masked so each name only
    appears on days it was an actual S&P member. Includes the HORIZON-day forward
    return per ticker (the raw ingredient of the market-neutral target).

    LIQUIDITY FILTER (critical for a wide universe): a decile L/S book is driven
    entirely by the tails of the cross-section, so penny/illiquid names — whose
    weekly moves are enormous and untradable, and whose data is often dirty near
    delisting — will hijack both legs and explode the vol if left in. We drop any
    ticker-day below `min_price` or `min_dollar_vol` (21d avg). Both use trailing
    data only, so the filter is point-in-time and lookahead-free.
    """
    universe = load_universe(source=universe_source)
    print(f"Universe [{universe_source}]: {len(universe)} survivorship-bias-free single names")
    print(f"Liquidity filter: price >= ${min_price:.0f}, 21d $vol >= ${min_dollar_vol / 1e6:.0f}M")

    frames = []
    for i, (ticker, spans) in enumerate(sorted(universe.items()), 1):
        ohlcv = load_ohlcv(ticker)
        if ohlcv is None or len(ohlcv) < 300:
            continue
        feats = add_price_features(ohlcv)
        feats = add_earnings_features(feats, load_earnings(ticker))

        # HORIZON-day forward return (the only forward-looking column; it becomes
        # the label and is never used as an input feature).
        feats["fwd_ret"] = feats["Close"].shift(-HORIZON) / feats["Close"] - 1.0

        # Apply point-in-time index membership, then the liquidity screen.
        feats = feats[_membership_mask(feats.index, spans)]
        feats = feats[(feats["Close"] >= min_price) & (feats["dollar_vol_21"] >= min_dollar_vol)]
        if feats.empty:
            continue

        keep = [c for c in RAW_FEATURE_COLS if c in feats.columns] + ["fwd_ret"]
        tidy = feats[keep].copy()
        tidy.insert(0, "ticker", ticker)
        tidy.insert(0, "date", feats.index)
        frames.append(tidy)
        if i % 50 == 0:
            print(f"  ...processed {i} tickers")

    panel = pd.concat(frames, ignore_index=True)

    if use_short_interest:
        si = load_short_interest(sorted(universe.keys()))
        panel = add_short_interest_features(panel, si)

    panel = panel.sort_values(["date", "ticker"]).reset_index(drop=True)
    print(f"Panel: {len(panel):,} rows, {panel['date'].nunique():,} trading days")
    return panel


# ---------------------------------------------------------------------------
# Step 2: Cross-sectional normalization
# ---------------------------------------------------------------------------


def cross_sectional_zscore(panel: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
    """Replace each feature with its same-day cross-sectional z-score.

    THIS IS THE HEART OF THE STRATEGY. "TSLA short interest = 10%" is meaningless
    in isolation; "TSLA is +2.3σ vs the S&P cross-section *today*" is tradable.
    For every date we standardize each feature across all member names that day:
        z = (x - mean_today) / std_today
    Outliers are winsorized to ±3σ AFTER standardizing so a single blow-up name
    can't swamp the rank. Days with too few names are dropped (thin = noisy).
    All inputs are same-day, so this introduces zero lookahead.
    """
    panel = panel.copy()

    # Drop thin cross-sections before normalizing.
    counts = panel.groupby("date")["ticker"].transform("count")
    panel = panel[counts >= MIN_NAMES_PER_DAY].copy()

    # DATA-INTEGRITY GUARD. With a free-yfinance universe, recycled/delisted ticker
    # symbols splice unrelated companies into one series, yielding spurious multi-
    # hundred-percent 5-day "returns" that would otherwise detonate the short leg
    # (vol → 400%, equity → negative). A genuine S&P member with >$10M ADV almost
    # never moves ±50% in a week, so we treat anything beyond as a data error and
    # winsorize the forward return to ±FWD_RET_CAP before it reaches target or P&L.
    panel["fwd_ret"] = panel["fwd_ret"].clip(-FWD_RET_CAP, FWD_RET_CAP)

    # Vectorized per-day standardization (transform avoids the apply-on-groups
    # deprecation and is far faster than a Python-level group loop). Winsorize to
    # ±3σ after standardizing so one blow-up name can't swamp the rank.
    by_date = panel.groupby("date")
    for col in feature_cols:
        mu = by_date[col].transform("mean")
        sd = by_date[col].transform("std")  # ddof=1; equals 0 only for constant cols
        z = (panel[col] - mu) / sd.replace(0.0, np.nan)
        panel[col + "_z"] = z.clip(-3, 3)

    # The neutral target: forward return MINUS the equal-weight cross-sectional
    # mean forward return that day. This is exactly the P&L a dollar-neutral book
    # earns, so training on it aligns the model's objective with the backtest.
    panel["fwd_ret_rel"] = panel["fwd_ret"] - panel.groupby("date")["fwd_ret"].transform("mean")

    # Impute residual NaNs in z-features with 0 (= "average name today").
    z_cols = [c + "_z" for c in feature_cols]
    panel[z_cols] = panel[z_cols].fillna(0.0)
    return panel


# ---------------------------------------------------------------------------
# Step 3: Model training
# ---------------------------------------------------------------------------


@dataclass
class TrainedModel:
    model: xgb.XGBRegressor
    z_cols: list[str]
    split_date: pd.Timestamp


def train_model(panel: pd.DataFrame, feature_cols: list[str], split: str, quiet: bool = False) -> TrainedModel:
    """Train XGBoost to predict the market-neutral relative forward return.

    Split is strictly chronological with an EMBARGO of HORIZON days: the last
    HORIZON days before `split` are dropped because their forward returns reach
    into the test period (label leakage at the seam). No row shuffling, ever.
    A small validation tail of the training set drives early stopping.
    """
    z_cols = [c + "_z" for c in feature_cols]
    split_date = pd.to_datetime(split)
    embargo_start = split_date - pd.Timedelta(days=HORIZON * 2)  # calendar buffer

    train = panel[panel["date"] < embargo_start].dropna(subset=["fwd_ret_rel"])
    if train.empty:
        raise SystemExit(f"No training rows before {embargo_start.date()} — check --split.")

    # Carve a chronological validation tail (last ~15% of train dates) for early
    # stopping; keeping it time-ordered avoids leaking the future into model selection.
    cut_dates = np.sort(train["date"].unique())
    val_cut = cut_dates[int(len(cut_dates) * 0.85)]
    tr = train[train["date"] < val_cut]
    va = train[train["date"] >= val_cut]

    model = xgb.XGBRegressor(
        n_estimators=600,
        learning_rate=0.02,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=20,  # regularize: each leaf needs many names
        reg_lambda=2.0,
        objective="reg:squarederror",
        eval_metric="rmse",
        early_stopping_rounds=40,
        n_jobs=-1,
        random_state=42,
    )
    model.fit(
        tr[z_cols],
        tr["fwd_ret_rel"],
        eval_set=[(va[z_cols], va["fwd_ret_rel"])],
        verbose=False,
    )
    if not quiet:
        print(f"Trained on {len(tr):,} rows (val {len(va):,}); best_iteration={model.best_iteration}")
        # Feature importance — sanity check signal isn't coming from one column.
        imp = sorted(zip(z_cols, model.feature_importances_), key=lambda x: -x[1])
        print("Top features:", ", ".join(f"{n}={v:.2f}" for n, v in imp[:6]))
    return TrainedModel(model=model, z_cols=z_cols, split_date=split_date)


# ---------------------------------------------------------------------------
# Step 4: Portfolio construction & market-neutral backtest
# ---------------------------------------------------------------------------


PERIODS_PER_YEAR = TRADING_DAYS / HORIZON


def _simulate(test: pd.DataFrame, model, z_cols: list[str], decile: float, exit_decile: float | None = None) -> dict:
    """Cost-FREE simulation core: build the decile L/S book over a test slice and
    return per-rebalance gross returns + turnover, plus the IC and quintile
    diagnostic. Cost is applied downstream so cost-sensitivity is free (re-running
    the booker per cost level would be wasteful and is unnecessary — gross P&L and
    turnover don't depend on the cost assumption).

    Baskets are rebalanced on NON-OVERLAPPING dates (every HORIZON days). Both
    `model` and `z_cols` are passed explicitly so walk-forward folds can each
    supply their own freshly-trained model.

    TURNOVER MODE (`exit_decile`):
      * None  -> classic full-refresh: each period the book is exactly the top/
        bottom `decile`. Maximum responsiveness, maximum turnover.
      * >decile -> Qlib TopkDropout-style HYSTERESIS: a name ENTERS the long book
        when it ranks in the top `decile`, but is only SOLD once it falls out of
        the wider top `exit_decile` band (symmetric for shorts). Names flickering
        around the entry boundary no longer churn in and out, which is the whole
        point — our cost sweep showed net Sharpe is turnover-bound, so widening
        the exit band trades a little signal freshness for a lot less cost.
    """
    test = test.dropna(subset=["fwd_ret_rel"]).copy()
    if test.empty:
        return {"gross": np.array([]), "turnover": np.array([]), "dates": np.array([])}
    test["pred"] = model.predict(test[z_cols])

    # IC: daily rank corr between prediction and realized relative return — the
    # model's raw edge before any portfolio/cost effects.
    ics = []
    for _, g in test.groupby("date"):
        if len(g) >= MIN_NAMES_PER_DAY:
            ics.append(g["pred"].corr(g["fwd_ret_rel"], method="spearman"))
    ics = [x for x in ics if pd.notna(x)]

    # groupby returns date-sorted groups; step by HORIZON for non-overlapping
    # rebalances. (Iterating groups avoids datetime64-vs-Timestamp key mismatches.)
    groups = list(test.groupby("date"))

    prev_long: set[str] = set()
    prev_short: set[str] = set()
    gross_list, turn_list, used_dates = [], [], []
    decile_rows: list[list[float]] = []

    for i in range(0, len(groups), HORIZON):
        d, g = groups[i]
        if len(g) < MIN_NAMES_PER_DAY:
            continue
        g = g.sort_values("pred", ascending=False).reset_index(drop=True)
        n = len(g)
        k = max(1, int(round(n * decile)))

        if exit_decile is None or exit_decile <= decile:
            # Classic full-refresh decile book.
            long_set = set(g["ticker"].iloc[:k])
            short_set = set(g["ticker"].iloc[n - k :])
        else:
            # Hysteresis: hold until a name leaves the wider exit band.
            frac = np.arange(n) / max(1, n - 1)  # 0 = best pred ... 1 = worst
            ranks = dict(zip(g["ticker"], frac))
            present = set(g["ticker"])
            entry_long = set(g["ticker"][frac <= decile])
            keep_long = {t for t in prev_long if t in present and ranks[t] <= exit_decile}
            long_set = entry_long | keep_long
            entry_short = set(g["ticker"][frac >= 1 - decile])
            keep_short = {t for t in prev_short if t in present and ranks[t] >= 1 - exit_decile}
            short_set = entry_short | keep_short

        ret = dict(zip(g["ticker"], g["fwd_ret"]))
        long_ret = np.mean([ret[t] for t in long_set]) if long_set else 0.0
        short_ret = np.mean([ret[t] for t in short_set]) if short_set else 0.0
        gross = long_ret - short_ret

        # One-way turnover per leg as a fraction of the target leg size (2k name-
        # slots both ways), kept on the same scale as the full-refresh baseline so
        # cost comparisons across modes are apples-to-apples.
        turnover = len(long_set ^ prev_long) / max(1, 2 * k) + len(short_set ^ prev_short) / max(1, 2 * k)
        gross_list.append(gross)
        turn_list.append(turnover)
        used_dates.append(d)
        prev_long, prev_short = long_set, short_set

        try:
            buckets = pd.qcut(g["pred"], 5, labels=False, duplicates="drop")
            decile_rows.append([g["fwd_ret"][buckets == b].mean() for b in range(5)])
        except ValueError:
            pass

    return {
        "gross": np.asarray(gross_list, dtype=float),
        "turnover": np.asarray(turn_list, dtype=float),
        "dates": np.asarray(used_dates),
        "mean_ic": float(np.mean(ics)) if ics else float("nan"),
        "ic_ir": (
            float(np.mean(ics) / np.std(ics) * np.sqrt(TRADING_DAYS)) if ics and np.std(ics) > 0 else float("nan")
        ),
        "decile_means": (np.nanmean(np.array(decile_rows), axis=0).tolist() if decile_rows else []),
    }


def _stats(gross: np.ndarray, turnover: np.ndarray, cost_bps: float) -> dict:
    """Annualized gross/net stats from per-period gross returns + turnover."""
    net = gross - turnover * (cost_bps / 1e4)

    def _sh(x):
        return (
            float(x.mean() * PERIODS_PER_YEAR / (x.std(ddof=1) * np.sqrt(PERIODS_PER_YEAR)))
            if len(x) > 2 and x.std(ddof=1) > 0
            else float("nan")
        )

    equity = np.cumprod(1 + net)
    peak = np.maximum.accumulate(equity)
    return {
        "n_periods": len(net),
        "sharpe_gross": _sh(gross),
        "sharpe_net": _sh(net),
        "ann_ret_gross": float(gross.mean() * PERIODS_PER_YEAR),
        "ann_ret_net": float(net.mean() * PERIODS_PER_YEAR),
        "ann_vol": float(net.std(ddof=1) * np.sqrt(PERIODS_PER_YEAR)) if len(net) > 2 else float("nan"),
        "max_dd": float((equity / peak - 1).min()) if len(net) else float("nan"),
        "avg_turnover": float(turnover.mean()) if len(turnover) else float("nan"),
    }


def single_split_backtest(
    panel: pd.DataFrame, tm: TrainedModel, decile: float, cost_bps: float, exit_decile: float | None = None
) -> dict:
    """One chronological train/test split (the original default mode)."""
    test = panel[panel["date"] >= tm.split_date]
    sim = _simulate(test, tm.model, tm.z_cols, decile, exit_decile)
    if len(sim["gross"]) < 3:
        raise SystemExit("Too few rebalance periods in test window — widen the split.")
    res = _stats(sim["gross"], sim["turnover"], cost_bps)
    res.update(
        {
            "mean_ic": sim["mean_ic"],
            "ic_ir": sim["ic_ir"],
            "decile_means": sim["decile_means"],
            "test_start": pd.Timestamp(sim["dates"].min()).date(),
            "test_end": pd.Timestamp(sim["dates"].max()).date(),
        }
    )
    return res


def _block_bootstrap_sharpe_ci(net: np.ndarray, block: int = 4, n_boot: int = 2000) -> tuple[float, float]:
    """5/95 CI on the net Sharpe via a circular block bootstrap.

    Plain bootstrap assumes i.i.d. periods; L/S spread returns have mild serial
    structure, so we resample contiguous blocks (size ~`block` periods ≈ a month)
    to preserve it. If the 5th percentile clears 0, the Sharpe is unlikely to be
    a single-window fluke.
    """
    if len(net) < block * 3:
        return float("nan"), float("nan")
    rng = np.random.default_rng(42)
    n = len(net)
    n_blocks = int(np.ceil(n / block))
    sharpes = []
    for _ in range(n_boot):
        starts = rng.integers(0, n, size=n_blocks)
        idx = np.concatenate([(np.arange(s, s + block) % n) for s in starts])[:n]
        sample = net[idx]
        sd = sample.std(ddof=1)
        if sd > 0:
            sharpes.append(sample.mean() * PERIODS_PER_YEAR / (sd * np.sqrt(PERIODS_PER_YEAR)))
    if not sharpes:
        return float("nan"), float("nan")
    return float(np.percentile(sharpes, 5)), float(np.percentile(sharpes, 95))


def walk_forward(
    panel: pd.DataFrame,
    feature_cols: list[str],
    decile: float,
    cost_bps: float,
    start_year: int,
    test_years: int = 1,
    exit_decile: float | None = None,
) -> dict:
    """Purged, expanding-window walk-forward CV.

    For each fold the model is retrained ONLY on data strictly before the test
    window (with a HORIZON-day embargo at the seam, since the target is forward-
    looking), then scored on the held-out window. Folds' out-of-sample period
    returns are concatenated into one continuous OOS track — this is the number
    that mirrors how the strategy would actually have traded, retraining as it
    went. Reports the aggregate net Sharpe, a block-bootstrap CI, and per-fold
    Sharpe so you can see whether the edge is stable or driven by one regime.
    """
    last_year = pd.Timestamp(panel["date"].max()).year
    fold_starts = list(range(start_year, last_year + 1, test_years))

    all_gross, all_turn, all_dates = [], [], []
    fold_summ: list[tuple] = []
    print(
        f"\nWalk-forward CV: {len(fold_starts)} expanding folds ({start_year}→{last_year}, {test_years}y test windows)"
    )

    for y in fold_starts:
        split = f"{y}-01-01"
        test_end = pd.Timestamp(f"{y + test_years}-01-01")
        try:
            tm = train_model(panel, feature_cols, split, quiet=True)
        except SystemExit:
            continue  # not enough history yet for this fold
        test = panel[(panel["date"] >= tm.split_date) & (panel["date"] < test_end)]
        sim = _simulate(test, tm.model, tm.z_cols, decile, exit_decile)
        if len(sim["gross"]) < 3:
            continue
        fs = _stats(sim["gross"], sim["turnover"], cost_bps)
        fold_summ.append((y, fs["n_periods"], sim["mean_ic"], fs["sharpe_net"]))
        all_gross.append(sim["gross"])
        all_turn.append(sim["turnover"])
        all_dates.append(sim["dates"])

    if not all_gross:
        raise SystemExit("Walk-forward produced no usable folds — lower --wf-start.")

    gross = np.concatenate(all_gross)
    turn = np.concatenate(all_turn)
    dates = np.concatenate(all_dates)
    res = _stats(gross, turn, cost_bps)
    net = gross - turn * (cost_bps / 1e4)
    lo, hi = _block_bootstrap_sharpe_ci(net)
    res.update(
        {
            "fold_summary": fold_summ,
            "sharpe_ci": (lo, hi),
            "test_start": pd.Timestamp(dates.min()).date(),
            "test_end": pd.Timestamp(dates.max()).date(),
            "gross_series": gross,
            "turnover_series": turn,
            "mean_ic": float(np.nanmean([f[2] for f in fold_summ])),
        }
    )
    return res


def cost_sensitivity(gross: np.ndarray, turnover: np.ndarray, levels=(0, 5, 10, 20, 40)) -> None:
    """Print net Sharpe across a sweep of one-way cost assumptions (bps).

    The crossover point — where net Sharpe falls below ~0.5 or below 0 — tells you
    how much execution slippage this strategy can tolerate. A daily/decile book
    that only works at 0 bps is not a strategy, it's a backtest artifact.
    """
    print("-" * 64)
    print("  Cost sensitivity (one-way bps -> net Sharpe):")
    for bps in levels:
        s = _stats(gross, turnover, bps)["sharpe_net"]
        print(f"    {bps:>3} bps : {s:+.3f}")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def report(res: dict, decile: float, cost_bps: float, mode: str) -> None:
    pct = lambda x: f"{x * 100:+.2f}%"  # noqa: E731
    title = (
        "WALK-FORWARD CV (purged, expanding, retrained per fold)"
        if mode == "wf"
        else "CROSS-SECTIONAL MARKET-NEUTRAL BACKTEST (single split)"
    )
    print("\n" + "=" * 64)
    print(f"  {title}")
    print("=" * 64)
    print(f"  OOS window       : {res['test_start']} -> {res['test_end']}")
    print(f"  Rebalances       : {res['n_periods']} (every {HORIZON} trading days)")
    print(f"  Decile / leg     : top/bottom {decile:.0%}")
    print(f"  Cost (one-way)   : {cost_bps:.1f} bps on turnover")
    print(f"  Avg turnover     : {res.get('avg_turnover', float('nan')):.2f} per rebalance (1.0 = full)")
    print("-" * 64)

    if res.get("fold_summary"):
        print("  Per-fold (year | rebals | IC | net Sharpe):")
        for y, n, ic, sh in res["fold_summary"]:
            print(f"    {y}  |  {n:>3}  |  IC {ic:+.4f}  |  Sh {sh:+.3f}")
        pos = sum(1 for *_, sh in res["fold_summary"] if sh > 0)
        print(f"  Folds with positive net Sharpe: {pos}/{len(res['fold_summary'])}")
        print("-" * 64)

    print(f"  Mean IC (rank)   : {res['mean_ic']:+.4f}")
    print(f"  Ann. return  net : {pct(res['ann_ret_net'])}")
    print(f"  Ann. return gross: {pct(res['ann_ret_gross'])}")
    print(f"  Ann. volatility  : {pct(res['ann_vol'])}")
    print(f"  Max drawdown     : {pct(res['max_dd'])}")
    print("-" * 64)
    print(f"  SHARPE  (gross)  : {res['sharpe_gross']:.3f}")
    print(f"  SHARPE  (NET)    : {res['sharpe_net']:.3f}   <-- the only one that counts")
    if res.get("sharpe_ci"):
        lo, hi = res["sharpe_ci"]
        clears = "✅ clears 0" if lo > 0 else "⚠ includes 0 — could be a fluke"
        print(f"  Net Sharpe 90% CI: [{lo:+.3f}, {hi:+.3f}]   {clears}")
    print("-" * 64)
    if res.get("decile_means"):
        cells = "  ".join(pct(x) for x in res["decile_means"])
        print(f"  Quintile fwd-ret (low->high pred): {cells}")
        mono = all(res["decile_means"][i] <= res["decile_means"][i + 1] for i in range(len(res["decile_means"]) - 1))
        print(f"  Monotonic in prediction: {'YES ✅' if mono else 'no (signal is noisy)'}")
    print("=" * 64)
    if res["sharpe_net"] < 0.5:
        print("  Reality check: net Sharpe < 0.5. The gross spread isn't beating")
        print("  turnover cost. Improve IC (better features) or cut turnover")
        print("  (longer horizon / wider deciles / holding overlap) before trusting this.")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    global HORIZON, PERIODS_PER_YEAR  # may be overridden by --horizon below
    ap = argparse.ArgumentParser(description="Cross-sectional market-neutral alpha model")
    ap.add_argument("--split", default="2019-01-01", help="single-split train/test boundary (chronological)")
    ap.add_argument("--decile", type=float, default=0.10, help="fraction per long/short leg")
    ap.add_argument("--cost-bps", type=float, default=10.0, help="one-way turnover cost in bps")
    ap.add_argument("--short-interest", action="store_true", help="merge Postgres short interest")
    ap.add_argument(
        "--walk-forward",
        action="store_true",
        help="purged expanding-window CV with retraining per fold + bootstrap Sharpe CI",
    )
    ap.add_argument("--wf-start", type=int, default=2012, help="first walk-forward test year")
    ap.add_argument("--wf-test-years", type=int, default=1, help="length of each test window in years")
    ap.add_argument("--cost-sweep", action="store_true", help="print net Sharpe across a cost-bps sweep")
    ap.add_argument("--min-price", type=float, default=5.0, help="min share price for the liquidity screen")
    ap.add_argument("--min-dollar-vol", type=float, default=1e7, help="min 21d avg dollar volume")
    ap.add_argument(
        "--exit-decile",
        type=float,
        default=None,
        help="Qlib TopkDropout hysteresis: hold a name until it leaves this wider "
        "band (e.g. --decile 0.10 --exit-decile 0.25). Omit for full-refresh.",
    )
    ap.add_argument(
        "--universe",
        choices=["full", "curated"],
        default="full",
        help="'full' = complete S&P 500 history; 'curated' = legacy large-cap set (0.42 baseline)",
    )
    ap.add_argument(
        "--wq-alphas",
        action="store_true",
        help="add the orthogonal WorldQuant-101 alphas (wq002, wq026) as extra features",
    )
    ap.add_argument(
        "--horizon",
        type=int,
        default=HORIZON,
        help="forward-return horizon = rebalance period in trading days (default 21). "
        "Longer horizons cut annual turnover cost (the binding constraint on net Sharpe); "
        "use 25 for the lower-drawdown variant.",
    )
    args = ap.parse_args()

    # Override the horizon globals before any data is built (forward return,
    # rebalance step, embargo, and the annualization factor all read these).
    HORIZON = args.horizon
    PERIODS_PER_YEAR = TRADING_DAYS / HORIZON
    if args.horizon != 21:
        print(f"Horizon override: {HORIZON}d rebalance (PERIODS_PER_YEAR={PERIODS_PER_YEAR:.1f})")

    panel = build_panel(
        use_short_interest=args.short_interest,
        min_price=args.min_price,
        min_dollar_vol=args.min_dollar_vol,
        universe_source=args.universe,
    )
    feature_cols = [c for c in RAW_FEATURE_COLS if c in panel.columns]
    if args.wq_alphas:
        print("Adding WorldQuant-101 orthogonal alphas (wq002, wq026)…")
        wq = _wq_alpha_panel(sorted(panel["ticker"].unique()))
        panel = panel.merge(wq, on=["date", "ticker"], how="left")
        feature_cols += [c for c in WQ_ALPHA_COLS if c in panel.columns]
        print(f"  feature set now {len(feature_cols)}: {feature_cols}")
    panel = cross_sectional_zscore(panel, feature_cols)

    if args.walk_forward:
        res = walk_forward(
            panel,
            feature_cols,
            args.decile,
            args.cost_bps,
            start_year=args.wf_start,
            test_years=args.wf_test_years,
            exit_decile=args.exit_decile,
        )
        report(res, args.decile, args.cost_bps, mode="wf")
        if args.cost_sweep:
            cost_sensitivity(res["gross_series"], res["turnover_series"])
    else:
        tm = train_model(panel, feature_cols, args.split)
        res = single_split_backtest(panel, tm, args.decile, args.cost_bps, exit_decile=args.exit_decile)
        report(res, args.decile, args.cost_bps, mode="single")
        if args.cost_sweep:
            sim = _simulate(panel[panel["date"] >= tm.split_date], tm.model, tm.z_cols, args.decile, args.exit_decile)
            cost_sensitivity(sim["gross"], sim["turnover"])


if __name__ == "__main__":
    main()
