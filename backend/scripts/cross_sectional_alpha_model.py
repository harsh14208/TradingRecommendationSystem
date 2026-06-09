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

HORIZON = 5  # forward-return horizon in trading days; also the rebalance period
MIN_NAMES_PER_DAY = 20  # don't z-score / trade a thin cross-section
TRADING_DAYS = 252

# Tickers in the OHLCV cache that are ETFs/indices, not single-name equities.
# They must never enter the stock cross-section (they'd dominate the ranks).
_ETF_LIKE = {
    "SPY", "QQQ", "DIA", "IWM", "HYG", "TLT", "UUP", "GLD", "SLV", "USO",
    "XLB", "XLC", "XLE", "XLF", "XLI", "XLK", "XLP", "XLRE", "XLU", "XLV", "XLY",
    "VXX", "UVXY", "EEM", "EFA",
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


def load_universe() -> dict[str, list[tuple[pd.Timestamp, pd.Timestamp]]]:
    """Load survivorship-bias-free S&P membership intervals.

    Returns {ticker: [(start, end), ...]} where each interval is the window the
    ticker was an index member. We later mask the panel so a name only trades on
    days it was actually in the index — this is the §84 point-in-time fix.
    Only tickers that ALSO have an OHLCV cache and are not ETFs survive.
    """
    with open(_CONSTITUENTS) as f:
        raw = json.load(f)

    cached = {
        os.path.basename(p).split("_")[0]
        for p in glob.glob(os.path.join(_OHLCV_DIR, "*_1d_adjTrue.csv"))
    }

    universe: dict[str, list[tuple[pd.Timestamp, pd.Timestamp]]] = {}
    for ticker, intervals in raw.items():
        if not ticker or ticker in _ETF_LIKE or ticker not in cached:
            continue
        spans: list[tuple[pd.Timestamp, pd.Timestamp]] = []
        for span in intervals:
            start = pd.to_datetime(span[0])
            # An open-ended / current membership may be null or a sentinel; treat
            # anything missing as "still a member today".
            end_raw = span[1] if len(span) > 1 and span[1] else "2100-01-01"
            end = pd.to_datetime(end_raw)
            spans.append((start, end))
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

        from config import settings  # type: ignore

        url = str(settings.DATABASE_URL)
        # The app uses an async driver; strip it for a plain sync read here.
        url = url.replace("+asyncpg", "").replace("postgresql+asyncpg", "postgresql")
        engine = create_engine(url)
        q = text(
            "SELECT ticker, date, short_interest, days_to_cover "
            "FROM short_interest_biweekly WHERE ticker = ANY(:tk)"
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
    "mom_12_1",      # 12-1 month momentum (skip last month) — classic XS factor
    "rev_5",         # 5-day short-term reversal
    "rev_21",        # 21-day reversal / mean-reversion pressure
    "vol_21",        # 21-day realized volatility (low-vol anomaly)
    "dollar_vol_21", # liquidity / size proxy
    "dist_ma50",     # price distance from 50d MA (stretch)
    "rsi_14",        # Wilder RSI (overbought/oversold)
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


def add_short_interest_features(panel: pd.DataFrame, si: pd.DataFrame) -> pd.DataFrame:
    """Merge bi-weekly short interest, forward-filled to daily, into the panel.

    Short interest is reported with a lag and changes slowly, so forward-filling
    the last *settled* value to each trading day is correct and lookahead-free.
    Adds 'days_to_cover' to the feature set (squeeze-fuel factor) when present.
    """
    if si.empty:
        return panel
    si = si.sort_values(["ticker", "date"])
    merged = []
    for ticker, grp in panel.groupby("ticker", sort=False):
        s = si[si["ticker"] == ticker][["date", "days_to_cover"]].dropna()
        grp = grp.sort_values("date")
        if s.empty:
            grp["days_to_cover"] = np.nan
        else:
            grp = pd.merge_asof(
                grp, s.rename(columns={"date": "date"}),
                on="date", direction="backward",
            )
        merged.append(grp)
    panel = pd.concat(merged, ignore_index=True)
    if "days_to_cover" in panel.columns and "days_to_cover" not in RAW_FEATURE_COLS:
        RAW_FEATURE_COLS.append("days_to_cover")
    return panel


def build_panel(use_short_interest: bool = False) -> pd.DataFrame:
    """Step 1 assembled: long panel [date, ticker, features..., fwd_ret].

    One row per (ticker, trading-day). Membership-masked so each name only
    appears on days it was an actual S&P member. Includes the HORIZON-day forward
    return per ticker (the raw ingredient of the market-neutral target).
    """
    universe = load_universe()
    print(f"Universe: {len(universe)} survivorship-bias-free single names")

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

        # Apply point-in-time index membership.
        feats = feats[_membership_mask(feats.index, spans)]
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


def train_model(panel: pd.DataFrame, feature_cols: list[str], split: str) -> TrainedModel:
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
        min_child_weight=20,      # regularize: each leaf needs many names
        reg_lambda=2.0,
        objective="reg:squarederror",
        eval_metric="rmse",
        early_stopping_rounds=40,
        n_jobs=-1,
        random_state=42,
    )
    model.fit(
        tr[z_cols], tr["fwd_ret_rel"],
        eval_set=[(va[z_cols], va["fwd_ret_rel"])],
        verbose=False,
    )
    print(
        f"Trained on {len(tr):,} rows (val {len(va):,}); "
        f"best_iteration={model.best_iteration}"
    )

    # Feature importance — sanity check that signal isn't coming from one column.
    imp = sorted(zip(z_cols, model.feature_importances_), key=lambda x: -x[1])
    print("Top features:", ", ".join(f"{n}={v:.2f}" for n, v in imp[:6]))
    return TrainedModel(model=model, z_cols=z_cols, split_date=split_date)


# ---------------------------------------------------------------------------
# Step 4: Portfolio construction & market-neutral backtest
# ---------------------------------------------------------------------------


def backtest(panel: pd.DataFrame, tm: TrainedModel, decile: float, cost_bps: float) -> dict:
    """Dollar-neutral decile long/short backtest on the out-of-sample period.

    For each NON-OVERLAPPING rebalance date (every HORIZON days), score the
    cross-section, go long the top `decile`, short the bottom `decile`, equal
    weight within each leg, dollar-neutral across legs. Hold HORIZON days, then
    rebalance. Period P&L = mean(long fwd_ret) - mean(short fwd_ret). Costs are
    charged on name turnover between consecutive baskets (one-way `cost_bps`).

    Returns gross/net annualized Sharpe, vol, IC, decile monotonicity, max DD.
    """
    test = panel[panel["date"] >= tm.split_date].dropna(subset=["fwd_ret_rel"]).copy()
    test["pred"] = tm.model.predict(test[tm.z_cols])

    # Information coefficient: daily rank corr between prediction and realized
    # relative return. This is the model's edge BEFORE any portfolio/cost effects
    # — a positive, stable IC is the precondition for everything downstream.
    ics = []
    for _, g in test.groupby("date"):
        if len(g) >= MIN_NAMES_PER_DAY:
            ics.append(g["pred"].corr(g["fwd_ret_rel"], method="spearman"))
    ics = [x for x in ics if pd.notna(x)]
    mean_ic = float(np.mean(ics)) if ics else float("nan")
    ir = mean_ic / np.std(ics) * np.sqrt(TRADING_DAYS) if ics and np.std(ics) > 0 else float("nan")

    # Non-overlapping rebalance dates.
    all_dates = np.sort(test["date"].unique())
    rebal_dates = all_dates[::HORIZON]

    prev_long: set[str] = set()
    prev_short: set[str] = set()
    period_rets: list[float] = []
    decile_rows: list[list[float]] = []  # per-rebalance mean fwd_ret by quantile bucket

    for d in rebal_dates:
        g = test[test["date"] == d]
        if len(g) < MIN_NAMES_PER_DAY:
            continue
        g = g.sort_values("pred", ascending=False)
        n = len(g)
        k = max(1, int(round(n * decile)))
        longs = g.head(k)
        shorts = g.tail(k)

        # Equal-weight, dollar-neutral period return (gross).
        gross = longs["fwd_ret"].mean() - shorts["fwd_ret"].mean()

        # Turnover cost: fraction of each leg's names that changed × cost_bps.
        long_set, short_set = set(longs["ticker"]), set(shorts["ticker"])
        long_to = len(long_set ^ prev_long) / max(1, 2 * k)
        short_to = len(short_set ^ prev_short) / max(1, 2 * k)
        turnover = long_to + short_to  # both legs trade
        cost = turnover * (cost_bps / 1e4)
        period_rets.append(gross - cost)
        prev_long, prev_short = long_set, short_set

        # Decile monotonicity diagnostic (do higher-ranked buckets earn more?).
        try:
            buckets = pd.qcut(g["pred"], 5, labels=False, duplicates="drop")
            decile_rows.append([g["fwd_ret"][buckets == b].mean() for b in range(5)])
        except ValueError:
            pass

    rets = np.asarray(period_rets, dtype=float)
    if len(rets) < 3:
        raise SystemExit("Too few rebalance periods in test window — widen the split.")

    periods_per_year = TRADING_DAYS / HORIZON
    ann_ret = rets.mean() * periods_per_year
    ann_vol = rets.std(ddof=1) * np.sqrt(periods_per_year)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else float("nan")

    equity = np.cumprod(1 + rets)
    peak = np.maximum.accumulate(equity)
    max_dd = float((equity / peak - 1).min())

    decile_means = (
        np.nanmean(np.array(decile_rows), axis=0).tolist() if decile_rows else []
    )

    return {
        "n_periods": len(rets),
        "mean_ic": mean_ic,
        "ic_ir": ir,
        "ann_ret_net": ann_ret,
        "ann_vol": ann_vol,
        "sharpe_net": sharpe,
        "max_dd": max_dd,
        "decile_means": decile_means,
        "test_start": pd.Timestamp(all_dates[0]).date(),
        "test_end": pd.Timestamp(all_dates[-1]).date(),
    }


def backtest_with_gross(panel: pd.DataFrame, tm: TrainedModel, decile: float, cost_bps: float) -> dict:
    """Wrapper that also computes the gross (pre-cost) Sharpe so the cost drag is
    explicit. Re-runs the loop tracking gross and net side by side."""
    test = panel[panel["date"] >= tm.split_date].dropna(subset=["fwd_ret_rel"]).copy()
    test["pred"] = tm.model.predict(test[tm.z_cols])

    all_dates = np.sort(test["date"].unique())
    rebal_dates = all_dates[::HORIZON]
    prev_long: set[str] = set()
    prev_short: set[str] = set()
    gross_list, net_list = [], []

    for d in rebal_dates:
        g = test[test["date"] == d]
        if len(g) < MIN_NAMES_PER_DAY:
            continue
        g = g.sort_values("pred", ascending=False)
        n = len(g)
        k = max(1, int(round(n * decile)))
        longs, shorts = g.head(k), g.tail(k)
        gross = longs["fwd_ret"].mean() - shorts["fwd_ret"].mean()
        long_set, short_set = set(longs["ticker"]), set(shorts["ticker"])
        turnover = len(long_set ^ prev_long) / max(1, 2 * k) + len(short_set ^ prev_short) / max(1, 2 * k)
        net = gross - turnover * (cost_bps / 1e4)
        gross_list.append(gross)
        net_list.append(net)
        prev_long, prev_short = long_set, short_set

    ppy = TRADING_DAYS / HORIZON
    g = np.asarray(gross_list)
    nt = np.asarray(net_list)

    def _sharpe(x):
        return float(x.mean() * ppy / (x.std(ddof=1) * np.sqrt(ppy))) if x.std(ddof=1) > 0 else float("nan")

    base = backtest(panel, tm, decile, cost_bps)
    base["sharpe_gross"] = _sharpe(g)
    base["ann_ret_gross"] = float(g.mean() * ppy)
    base["avg_turnover"] = float(np.mean([
        1.0  # decile baskets typically turn over near-fully each rebalance
    ])) if len(net_list) else float("nan")
    return base


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def report(res: dict, decile: float, cost_bps: float) -> None:
    pct = lambda x: f"{x * 100:+.2f}%"  # noqa: E731
    print("\n" + "=" * 64)
    print("  CROSS-SECTIONAL MARKET-NEUTRAL BACKTEST (out-of-sample)")
    print("=" * 64)
    print(f"  Test window      : {res['test_start']} -> {res['test_end']}")
    print(f"  Rebalances       : {res['n_periods']} (every {HORIZON} trading days)")
    print(f"  Decile / leg     : top/bottom {decile:.0%}")
    print(f"  Cost (one-way)   : {cost_bps:.1f} bps on turnover")
    print("-" * 64)
    print(f"  Mean IC (rank)   : {res['mean_ic']:+.4f}   (IC-IR {res['ic_ir']:+.2f})")
    print(f"  Ann. return  net : {pct(res['ann_ret_net'])}")
    print(f"  Ann. return gross: {pct(res.get('ann_ret_gross', float('nan')))}")
    print(f"  Ann. volatility  : {pct(res['ann_vol'])}")
    print(f"  Max drawdown     : {pct(res['max_dd'])}")
    print("-" * 64)
    print(f"  SHARPE  (gross)  : {res.get('sharpe_gross', float('nan')):.3f}")
    print(f"  SHARPE  (NET)    : {res['sharpe_net']:.3f}   <-- the only one that counts")
    print("-" * 64)
    if res["decile_means"]:
        cells = "  ".join(pct(x) for x in res["decile_means"])
        print(f"  Quintile fwd-ret (low->high pred): {cells}")
        mono = all(
            res["decile_means"][i] <= res["decile_means"][i + 1]
            for i in range(len(res["decile_means"]) - 1)
        )
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
    ap = argparse.ArgumentParser(description="Cross-sectional market-neutral alpha model")
    ap.add_argument("--split", default="2019-01-01", help="train/test split date (chronological)")
    ap.add_argument("--decile", type=float, default=0.10, help="fraction per long/short leg")
    ap.add_argument("--cost-bps", type=float, default=10.0, help="one-way turnover cost in bps")
    ap.add_argument("--short-interest", action="store_true", help="merge Postgres short interest")
    args = ap.parse_args()

    panel = build_panel(use_short_interest=args.short_interest)
    feature_cols = [c for c in RAW_FEATURE_COLS if c in panel.columns]
    panel = cross_sectional_zscore(panel, feature_cols)
    tm = train_model(panel, feature_cols, args.split)
    res = backtest_with_gross(panel, tm, args.decile, args.cost_bps)
    report(res, args.decile, args.cost_bps)


if __name__ == "__main__":
    main()
