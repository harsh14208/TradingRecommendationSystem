#!/usr/bin/env python3
"""ORATS options-flow opportunity model — standalone (not wired to the live engine/backtest).

Builds a cross-sectional next-day(-or-horizon) return prediction model purely from
the persisted ORATS daily feature panel (`orats_daily_features` in Postgres), then
validates it with a purged walk-forward where every prediction is checked against the
*actual* next-day outcome. The most recent date has no realized forward return yet, so
its scored cross-section is the live "near future" opportunity list.

Everything here is self-contained: the prediction target (forward stock return) is
derived from the panel's own per-ticker `stk_px` series, so no external price feed,
the live signal engine, or backtest_technicals is touched.

Two separate, non-overlapping universes, each with its own model:
  - companies (default): Polygon type CS/ADRC, point-in-time market cap
    (shares_outstanding × stk_px) ≥ $10B
  - etf:                 Polygon type ETF/ETV/ETN/ETS/FUND, AUM ≥ $1B
Shares/type are fetched once from Polygon and cached to data/orats_ticker_meta.json.

Two prediction modes (--mode):
  - direction : predict the SIGN of the forward return. Honest verdict = weak; the
                cross-sectional edge is a volatility/beta tilt, not per-name skill.
  - vol       : predict the SIZE of the move and compare it to the option-IMPLIED
                move to rank rich (sell-premium) vs cheap (buy-premium) names. This is
                the real, validated use of the paid ORATS IV — the variance risk
                premium (rich-decile options overprice the 2d move ~0.4-0.6×).

Usage:
    cd backend && python scripts/orats_opportunity_model.py                              # direction, companies ≥$10B
    cd backend && python scripts/orats_opportunity_model.py --mode vol --horizon 2       # VRP / rich-cheap, next 2 days
    cd backend && python scripts/orats_opportunity_model.py --mode vol --universe etf     # cleanest VRP (no single-name catalysts)
    cd backend && python scripts/orats_opportunity_model.py --universe etf                # separate direction ETF model
    cd backend && python scripts/orats_opportunity_model.py --placebo                    # shuffled-target noise floor

Outputs:
    - console report: walk-forward validation (direction IC / decile spread, OR vol
      forecast IC + variance-risk-premium capture by richness decile)
    - data/orats_opportunities_<universe>_<date>.csv  (direction)
    - data/orats_vol_<universe>_<date>.csv            (vol/VRP: sell- vs buy-premium lists)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from services.orats_data import load_orats_panel_from_db  # noqa: E402

log = logging.getLogger("signal.orats_opportunity_model")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

_META_CACHE = _PROJECT_ROOT / "data" / "orats_ticker_meta.json"
# Polygon ticker types grouped into the two model universes.
_COMPANY_TYPES = {"CS", "ADRC"}  # operating companies + ADRs
_ETF_TYPES = {"ETF", "ETV", "ETN", "ETS", "FUND"}  # funds / exchange-traded products

# Per-universe defaults (allowed Polygon types, market-cap/AUM floor, label).
_UNIVERSES = {
    "companies": (_COMPANY_TYPES, 1e10, "mktcap"),  # >$10B operating companies
    "etf": (_ETF_TYPES, 1e9, "AUM"),  # >$1B AUM exchange-traded products
}

# Raw panel columns that feed engineered features.
_RAW_FEATURES = [
    "atm_iv_30d",
    "pc_iv_skew",
    "iv_25d_call",
    "iv_25d_put",
    "gex",
    "dex",
    "pc_volume_ratio",
    "pc_oi_ratio",
    "total_opt_volume",
    "total_opt_oi",
    "zero_dte_put_volume",
]

# Engineered (no-lookahead) feature columns the model actually trains on.
_MODEL_FEATURES = [
    "ret_1d",
    "ret_5d",
    "ret_10d",
    "iv_level",
    "iv_chg_1d",
    "iv_chg_5d",
    "iv_rank_w",
    "skew",
    "skew_chg_5d",
    "pc_vol_ratio",
    "pc_oi_ratio_f",
    "opt_vol_surprise",
    "log_opt_oi",
    "zero_dte_put_frac",
    "gex_sign",
    "log_abs_gex",
    "dex_sign",
    "log_abs_dex",
]

# IV-sanity: drop rows whose ATM IV is an implausible multiple of the name's own
# trailing realized vol — ORATS data artifacts (bond/T-bill ETFs like SGOV/JNK/TIP
# print 400-670% IV against ~1-5% realized). Legit names cluster ~1-2x, p95 ≈ 9x.
_IV_RVOL_CAP = 8.0

# Short-straddle P&L model (fractions of underlying):
#   premium collected ≈ 0.8 × 1σ implied move (ATM straddle ≈ 2·0.4·σ√T·S)
#   seller pays the realized |move| at the horizon; loss stopped at TAIL_CAP × premium.
_STRADDLE_PREMIUM_FRAC = 0.80
_STRADDLE_COST_FRAC = 0.05  # round-trip slippage/commission as a fraction of premium
_STRADDLE_TAIL_CAP = 3.0  # risk-managed stop: max loss = 3× premium collected

# Features for the volatility / move-size model (predict |forward move|). Kept in
# raw units (no cross-sectional z-score) so the forecast is in return units and can
# be compared head-to-head with the option-implied move.
_VOL_FEATURES = [
    "iv_level",
    "rvol5",
    "rvol20",
    "iv_rank_w",
    "opt_vol_surprise",
    "log_opt_oi",
    "skew",
    "zero_dte_put_frac",
]


# ──────────────────────────────────────────────────────────────────────────
# Data loading & feature engineering
# ──────────────────────────────────────────────────────────────────────────
def _load_meta_cache() -> dict[str, dict]:
    """Reusable cache of {ticker: {"shares": float|None, "type": str|None}}.

    Seeds from the legacy split cache files (shares / type) the first time so we
    don't re-hit the API for data already pulled."""
    if _META_CACHE.exists():
        return json.loads(_META_CACHE.read_text())
    meta: dict[str, dict] = {}
    for fname, k in (("orats_shares_outstanding.json", "shares"), ("orats_ticker_type.json", "type")):
        p = _META_CACHE.parent / fname
        if p.exists():
            for t, v in json.loads(p.read_text()).items():
                meta.setdefault(t, {})[k] = v
    return meta


async def _fetch_ticker_meta(tickers: list[str], concurrency: int = 30) -> dict[str, dict]:
    """Fetch shares outstanding + security type from Polygon for uncached tickers.

    Both change quarterly at most, so the on-disk cache is reused indefinitely.
    One request per ticker yields both fields."""
    import aiohttp

    meta = _load_meta_cache()
    todo = [t for t in tickers if t not in meta or "shares" not in meta[t] or "type" not in meta[t]]
    if not todo:
        return meta
    key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY")
    if not key:
        log.warning("No POLYGON/MASSIVE API key — cannot fetch ticker meta; cache has %d entries", len(meta))
        return meta

    log.info("Fetching ticker meta (shares+type) for %d tickers from Polygon…", len(todo))
    sem = asyncio.Semaphore(concurrency)

    async def one(s, t):
        async with sem:
            try:
                async with s.get(
                    f"https://api.polygon.io/v3/reference/tickers/{t}",
                    params={"apiKey": key},
                    timeout=aiohttp.ClientTimeout(total=12),
                ) as r:
                    if r.status == 200:
                        res = (await r.json()).get("results") or {}
                        shares = res.get("weighted_shares_outstanding") or res.get("share_class_shares_outstanding")
                        return t, {"shares": shares, "type": res.get("type")}
            except Exception:
                pass
            return t, {"shares": None, "type": None}

    t0 = time.time()
    async with aiohttp.ClientSession() as s:
        for i in range(0, len(todo), 500):
            for t, m in await asyncio.gather(*[one(s, x) for x in todo[i : i + 500]]):
                meta[t] = m
            _META_CACHE.parent.mkdir(parents=True, exist_ok=True)
            _META_CACHE.write_text(json.dumps(meta))
    log.info(
        "Meta fetch done in %.0fs (%d with shares)", time.time() - t0, sum(1 for m in meta.values() if m.get("shares"))
    )
    return meta


def apply_universe_filter(df: pd.DataFrame, allowed_types: set[str], min_cap: float, label: str) -> pd.DataFrame:
    """Restrict to the requested Polygon security types with point-in-time
    market cap / AUM (shares × stk_px) ≥ min_cap. Keeps companies and ETFs as
    separate, non-overlapping cross-sections so each gets its own model."""
    meta = asyncio.run(_fetch_ticker_meta(sorted(df["ticker"].unique())))
    df = df.copy()
    df["shares_outstanding"] = df["ticker"].map(lambda t: (meta.get(t) or {}).get("shares"))
    df["sec_type"] = df["ticker"].map(lambda t: (meta.get(t) or {}).get("type"))
    df["market_cap"] = df["shares_outstanding"] * df["stk_px"]
    n_tic = df["ticker"].nunique()

    df = df[df["sec_type"].isin(allowed_types)]
    if min_cap > 0:
        df = df[df["market_cap"] >= min_cap]
    df = df.reset_index(drop=True)
    log.info(
        "Universe filter (types=%s, %s≥$%.1fB): %d → %d tickers, %d rows",
        ",".join(sorted(allowed_types)),
        label,
        min_cap / 1e9,
        n_tic,
        df["ticker"].nunique(),
        len(df),
    )
    return df


def load_panel() -> pd.DataFrame:
    df = asyncio.run(load_orats_panel_from_db())
    if df is None or df.empty:
        raise SystemExit("orats_daily_features is empty — run build_orats_panel.py --save-to-db first.")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)

    # Keep only the contiguous recent block (drop stray far-past snapshots that
    # leave a multi-month gap and break rolling features).
    counts = df.groupby("date")["ticker"].size()
    main_dates = counts[counts > counts.max() * 0.3].index
    cutoff = main_dates.min()
    n_before = df["date"].nunique()
    df = df[df["date"] >= cutoff].reset_index(drop=True)
    if df["date"].nunique() < n_before:
        log.info(
            "Dropped %d sparse pre-block dates; using %d contiguous dates from %s",
            n_before - df["date"].nunique(),
            df["date"].nunique(),
            cutoff.date(),
        )
    return df


def engineer_features(df: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """Add no-lookahead engineered features + the forward-return target.

    All time-series transforms operate within a single ticker and only look
    backward. Cross-sectional normalization happens later, per-date, at train time.
    """
    df = df.sort_values(["ticker", "date"]).copy()
    g = df.groupby("ticker", group_keys=False)

    px = df["stk_px"]
    # Past momentum (backward-looking).
    df["ret_1d"] = g["stk_px"].pct_change(1)
    df["ret_5d"] = g["stk_px"].pct_change(5)
    df["ret_10d"] = g["stk_px"].pct_change(10)

    # Trailing realized vol (annualized) from the panel's own price series — the
    # free-data baseline the paid IV must be judged against for vol forecasting.
    daily_ret = g["stk_px"].pct_change()
    df["rvol5"] = daily_ret.groupby(df["ticker"]).transform(lambda s: s.rolling(5, min_periods=3).std()) * np.sqrt(252)
    df["rvol20"] = daily_ret.groupby(df["ticker"]).transform(lambda s: s.rolling(20, min_periods=8).std()) * np.sqrt(
        252
    )

    # IV level / dynamics.
    df["iv_level"] = df["atm_iv_30d"]
    df["iv_chg_1d"] = g["atm_iv_30d"].pct_change(1)
    df["iv_chg_5d"] = g["atm_iv_30d"].pct_change(5)
    # Windowed IV rank within the available block (the stored iv_rank_252 is mostly
    # null because the 252d window can't fill inside a ~114-day panel).
    df["iv_rank_w"] = g["atm_iv_30d"].transform(
        lambda s: s.rolling(40, min_periods=15).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False)
    )

    # Skew.
    df["skew"] = df["pc_iv_skew"]
    df["skew_chg_5d"] = g["pc_iv_skew"].diff(5)

    # Flow.
    df["pc_vol_ratio"] = df["pc_volume_ratio"]
    df["pc_oi_ratio_f"] = df["pc_oi_ratio"]
    # Option-volume surprise vs the ticker's own trailing 20d average.
    trail = g["total_opt_volume"].transform(lambda s: s.rolling(20, min_periods=5).mean())
    df["opt_vol_surprise"] = np.log((df["total_opt_volume"] + 1.0) / (trail + 1.0))
    df["log_opt_oi"] = np.log1p(df["total_opt_oi"].clip(lower=0))
    df["zero_dte_put_frac"] = (df["zero_dte_put_volume"] / df["total_opt_volume"].replace(0, np.nan)).fillna(0.0)

    # Dealer positioning proxies — sign and log-magnitude (raw $ is heavy-tailed).
    df["gex_sign"] = np.sign(df["gex"].fillna(0.0))
    df["log_abs_gex"] = np.log1p(df["gex"].abs().fillna(0.0))
    df["dex_sign"] = np.sign(df["dex"].fillna(0.0))
    df["log_abs_dex"] = np.log1p(df["dex"].abs().fillna(0.0))

    # Forward-return target (the only forward-looking column; NaN on the last
    # `horizon` rows of each ticker — those are the live opportunities).
    df["fwd_ret"] = g["stk_px"].shift(-horizon) / px - 1.0
    return df


def cross_sectional_standardize(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Per-date robust z-score (winsorized) of each feature — makes the model
    learn cross-sectional ranking rather than absolute levels."""
    out = df.copy()
    for c in cols:

        def _z(s: pd.Series) -> pd.Series:
            s = s.clip(s.quantile(0.01), s.quantile(0.99))
            mu, sd = s.mean(), s.std()
            return (s - mu) / sd if sd and np.isfinite(sd) else s * 0.0

        out[c] = out.groupby("date")[c].transform(_z)
    out[cols] = out[cols].fillna(0.0)
    return out


# ──────────────────────────────────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────────────────────────────────
def _fit_predict(model_name: str, x_tr, y_tr, x_te):
    if model_name == "ridge":
        from sklearn.linear_model import Ridge

        m = Ridge(alpha=10.0)
        m.fit(x_tr, y_tr)
        return m.predict(x_te), m
    # default: regularized gradient boosting
    import xgboost as xgb

    m = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=3,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.7,
        min_child_weight=20,
        reg_lambda=5.0,
        reg_alpha=0.5,
        n_jobs=4,
        random_state=42,  # reproducible: subsample/colsample are stochastic without this
        objective="reg:squarederror",
    )
    m.fit(x_tr, y_tr)
    return m.predict(x_te), m


# ──────────────────────────────────────────────────────────────────────────
# Walk-forward validation
# ──────────────────────────────────────────────────────────────────────────
def walk_forward(
    df: pd.DataFrame,
    feats: list[str],
    horizon: int,
    min_train: int,
    refit: int,
    model_name: str,
    placebo: bool,
) -> pd.DataFrame:
    """Expanding-window walk-forward. For each test date, train on all rows whose
    forward window closed at least `embargo=horizon` days earlier (purge), predict
    the test cross-section, and store predictions next to the realized fwd_ret."""
    dates = np.array(sorted(df["date"].unique()))
    labeled = df.dropna(subset=["fwd_ret"]).copy()
    rng = np.random.default_rng(7)

    rows = []
    last_model = None
    test_dates = dates[min_train:]
    # Only walk over dates that actually have realized outcomes.
    test_dates = [d for d in test_dates if d in set(labeled["date"].unique())]

    for i, d in enumerate(test_dates):
        train = labeled[labeled["date"] < d]
        # Purge: drop train rows whose forward window overlaps the test date.
        train_dates_sorted = np.array(sorted(train["date"].unique()))
        if len(train_dates_sorted) <= horizon:
            continue
        purge_keep = set(train_dates_sorted[: len(train_dates_sorted) - horizon])
        train = train[train["date"].isin(purge_keep)]
        if len(train) < 2000:
            continue

        test = labeled[labeled["date"] == d]
        if test.empty:
            continue

        if (last_model is None) or (i % refit == 0):
            y_tr = train["fwd_ret"].values
            if placebo:
                y_tr = rng.permutation(y_tr)
            preds, last_model = _fit_predict(model_name, train[feats].values, y_tr, test[feats].values)
        else:
            if model_name == "ridge":
                preds = last_model.predict(test[feats].values)
            else:
                preds = last_model.predict(test[feats].values)

        out = test[["ticker", "date", "fwd_ret", "total_opt_volume", "iv_level"]].copy()
        out["pred"] = preds
        rows.append(out)

    if not rows:
        raise SystemExit("Walk-forward produced no predictions (insufficient history).")
    return pd.concat(rows, ignore_index=True)


# ──────────────────────────────────────────────────────────────────────────
# Metrics & reporting
# ──────────────────────────────────────────────────────────────────────────
def report_validation(preds: pd.DataFrame, horizon: int) -> dict:
    from scipy.stats import spearmanr

    daily = []
    for d, g in preds.groupby("date"):
        if g["pred"].nunique() < 5 or len(g) < 20:
            continue
        ic = spearmanr(g["pred"], g["fwd_ret"]).correlation
        q = g["pred"].rank(pct=True)
        top = g.loc[q >= 0.9, "fwd_ret"].mean()
        bot = g.loc[q <= 0.1, "fwd_ret"].mean()
        daily.append({"date": d, "ic": ic, "top_dec": top, "bot_dec": bot, "ls": top - bot, "n": len(g)})
    dd = pd.DataFrame(daily).dropna(subset=["ic"])

    ic_mean = dd["ic"].mean()
    ic_std = dd["ic"].std()
    n_days = len(dd)
    ic_ir = ic_mean / ic_std if ic_std else 0.0
    ic_t = ic_ir * np.sqrt(n_days)
    ls_mean = dd["ls"].mean()
    ls_std = dd["ls"].std()
    ls_sharpe = (ls_mean / ls_std * np.sqrt(252 / horizon)) if ls_std else 0.0

    # Long-only top-decile hit rate vs cross-sectional median each day.
    hit = []
    for d, g in preds.groupby("date"):
        q = g["pred"].rank(pct=True)
        topret = g.loc[q >= 0.9, "fwd_ret"]
        if len(topret) >= 3:
            hit.append((topret > g["fwd_ret"].median()).mean())
    top_hit = float(np.mean(hit)) if hit else float("nan")

    print("\n" + "=" * 70)
    print(f"  WALK-FORWARD VALIDATION  (horizon={horizon}d, {n_days} test days)")
    print("=" * 70)
    print(f"  Mean daily rank IC        : {ic_mean:+.4f}")
    print(f"  IC stdev                  : {ic_std:.4f}")
    print(f"  IC information ratio      : {ic_ir:+.3f}   (t-stat {ic_t:+.2f})")
    print(f"  % days IC > 0             : {(dd['ic'] > 0).mean() * 100:.1f}%")
    print(f"  Top-decile fwd ret (avg)  : {dd['top_dec'].mean() * 100:+.3f}%")
    print(f"  Bot-decile fwd ret (avg)  : {dd['bot_dec'].mean() * 100:+.3f}%")
    print(f"  Long-short decile spread  : {ls_mean * 100:+.3f}% / period")
    print(f"  L/S annualized Sharpe     : {ls_sharpe:+.2f}")
    print(f"  Top-decile hit rate       : {top_hit * 100:.1f}%  (vs 50% coin-flip)")

    # Vol-tilt honesty check: how much of the score is just the IV level, and is
    # there residual skill *within* IV terciles (i.e. real selection, not a beta tilt)?
    if "iv_level" in preds.columns:
        corr_iv = preds[["pred", "iv_level"]].corr().iloc[0, 1]
        within = []
        for d, g in preds.groupby("date"):
            if len(g) < 30:
                continue
            g = g.copy()
            g["iv_bucket"] = pd.qcut(g["iv_level"].rank(method="first"), 3, labels=False)
            day_ics = [
                spearmanr(b["pred"], b["fwd_ret"]).correlation
                for _, b in g.groupby("iv_bucket")
                if b["pred"].nunique() > 3
            ]
            day_ics = [x for x in day_ics if x == x]
            if day_ics:
                within.append(np.mean(day_ics))
        within_ic = float(np.mean(within)) if within else float("nan")
        within_t = (within_ic / (np.std(within) / np.sqrt(len(within)))) if within and np.std(within) else 0.0
        print(f"  corr(pred, IV level)      : {corr_iv:+.2f}   (high ⇒ score is mostly a vol/beta tilt)")
        print(f"  Within-IV-tercile IC      : {within_ic:+.4f}  (t {within_t:+.2f}; ~0 ⇒ no real per-name skill)")
    print("=" * 70)
    return {
        "ic_mean": ic_mean,
        "ic_t": ic_t,
        "ls_mean": ls_mean,
        "ls_sharpe": ls_sharpe,
        "top_dec": dd["top_dec"].mean(),
        "bot_dec": dd["bot_dec"].mean(),
        "n_days": n_days,
    }


# ──────────────────────────────────────────────────────────────────────────
# Live opportunities (latest date, no realized outcome yet)
# ──────────────────────────────────────────────────────────────────────────
def score_live(
    df_std: pd.DataFrame,
    df_raw: pd.DataFrame,
    feats: list[str],
    model_name: str,
    horizon: int,
    top_n: int,
    min_opt_volume: float,
    val: dict,
) -> pd.DataFrame:
    """Train on all labeled history, score the latest (unlabeled) cross-section."""
    labeled = df_std.dropna(subset=["fwd_ret"])
    latest_date = df_std["date"].max()
    live = df_std[df_std["date"] == latest_date].copy()

    preds, model = _fit_predict(model_name, labeled[feats].values, labeled["fwd_ret"].values, live[feats].values)
    live["pred"] = preds

    # Map predictions back to raw (un-standardized) context for the report.
    raw_latest = df_raw[df_raw["date"] == latest_date].set_index("ticker")
    live = live.set_index("ticker")
    live["stk_px"] = raw_latest["stk_px"]
    live["atm_iv_30d"] = raw_latest["atm_iv_30d"]
    live["total_opt_volume"] = raw_latest["total_opt_volume"]
    live["pc_iv_skew"] = raw_latest["pc_iv_skew"]
    live["market_cap"] = raw_latest.get("market_cap", np.nan)
    live = live.reset_index()

    live = live[live["total_opt_volume"] >= min_opt_volume].copy()
    live["pct_rank"] = live["pred"].rank(pct=True)

    # Reliability gate: only the extreme deciles validated out-of-sample, so tag
    # which side has demonstrated edge in walk-forward.
    long_edge = val["top_dec"] > 0
    short_edge = val["bot_dec"] < 0

    longs = live.sort_values("pred", ascending=False).head(top_n).copy()
    longs["side"] = "LONG"
    longs["reliable"] = long_edge
    shorts = live.sort_values("pred", ascending=True).head(top_n).copy()
    shorts["side"] = "SHORT"
    shorts["reliable"] = short_edge

    out = pd.concat([longs, shorts], ignore_index=True)
    cols = [
        "side",
        "ticker",
        "stk_px",
        "market_cap",
        "pred",
        "pct_rank",
        "reliable",
        "atm_iv_30d",
        "pc_iv_skew",
        "total_opt_volume",
    ]
    out = out[cols].rename(columns={"pred": "model_score"})

    print(f"\n{'=' * 70}")
    print(f"  NEAR-FUTURE OPPORTUNITIES  —  scored on {pd.Timestamp(latest_date).date()}")
    print(f"  (predicted {horizon}d-forward move; LONG edge validated={long_edge}, SHORT edge validated={short_edge})")
    print("=" * 70)
    with pd.option_context("display.max_rows", None, "display.width", 200):
        show = out.copy()
        show["stk_px"] = show["stk_px"].round(2)
        show["cap_$B"] = (show["market_cap"] / 1e9).round(2)
        show = show.drop(columns=["market_cap"])
        show["model_score"] = (show["model_score"] * 100).round(3)
        show["pct_rank"] = (show["pct_rank"] * 100).round(1)
        show["atm_iv_30d"] = show["atm_iv_30d"].round(3)
        show["pc_iv_skew"] = show["pc_iv_skew"].round(3)
        show["total_opt_volume"] = show["total_opt_volume"].astype("Int64")
        show = show.rename(columns={"model_score": "pred_move_%", "pct_rank": "xs_rank_%"})
        show = show[
            [
                "side",
                "ticker",
                "stk_px",
                "cap_$B",
                "pred_move_%",
                "xs_rank_%",
                "reliable",
                "atm_iv_30d",
                "pc_iv_skew",
                "total_opt_volume",
            ]
        ]
        print(show.to_string(index=False))
    return out, latest_date


# ──────────────────────────────────────────────────────────────────────────
# Volatility / variance-risk-premium model
# ──────────────────────────────────────────────────────────────────────────
def _fill_per_date_median(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        df[c] = df[c].fillna(df.groupby("date")[c].transform("median"))
        df[c] = df[c].fillna(df[c].median())
    return df


def _straddle_backtest(cohort: pd.DataFrame, horizon: int) -> dict:
    """Realistic short-straddle P&L for a cohort of (ticker, date, abs_move, impl_move).

    Collect ~0.8× the implied 1σ move as premium, pay the realized |move| at the
    horizon, stop the loss at TAIL_CAP× premium, net of slippage. Returns the
    distribution stats that matter for sizing a short-vol book."""
    c = cohort.dropna(subset=["abs_move", "impl_move"]).copy()
    premium = _STRADDLE_PREMIUM_FRAC * c["impl_move"]
    gross = premium - c["abs_move"]  # collect premium, pay realized intrinsic
    capped = np.maximum(gross, -_STRADDLE_TAIL_CAP * premium)  # risk-managed stop
    net = capped - _STRADDLE_COST_FRAC * premium  # slippage/commission
    n = len(net)
    if n == 0:
        return {}
    ann = np.sqrt(252.0 / horizon)
    return {
        "n": int(n),
        "mean_net": float(net.mean()),
        "uncapped_mean_net": float((gross - _STRADDLE_COST_FRAC * premium).mean()),
        "win_rate": float((net > 0).mean()),
        "worst": float(net.min()),
        "pct_hit_cap": float((gross <= -_STRADDLE_TAIL_CAP * premium).mean()),
        "sharpe_ann": float(net.mean() / net.std() * ann) if net.std() else 0.0,
    }


def _vol_compute(
    feat_df: pd.DataFrame, horizon: int, model_name: str, min_train: int, refit: int, min_opt_volume: float
) -> tuple[dict, pd.DataFrame]:
    """Core volatility/VRP computation (no printing). Returns (summary, live_df).

    summary: forecast IC, VRP ratio, premium-seller base rate, rich/cheap decile edges.
    live_df: latest-date cross-section with forecast_move / impl_move / richness, ready
    for the recommendation engine to fuse with directional signals."""
    from scipy.stats import spearmanr

    df = feat_df.copy()
    df["abs_move"] = df["fwd_ret"].abs()  # realized |move| over the horizon (NaN on live rows)
    # Data-error guard only: drop >60% horizon moves (splits/stale prints). Genuine
    # tail moves (earnings, 3x-leveraged-ETF blowups) are kept — the straddle backtest
    # needs them to show real short-vol tail risk.
    df.loc[df["abs_move"] > 0.60, "abs_move"] = np.nan
    df["impl_move"] = df["atm_iv_30d"] * np.sqrt(horizon / 252.0)  # option-implied 1σ move
    df = df[(df["atm_iv_30d"] > 0.03) & (df["atm_iv_30d"] < 4.0) & (df["stk_px"] > 5)].reset_index(drop=True)
    # IV-sanity: remove ORATS artifacts where IV is an absurd multiple of realized vol.
    iv_rvol = df["atm_iv_30d"] / df["rvol20"].clip(lower=0.03)
    artifact = df["rvol20"].notna() & (iv_rvol > _IV_RVOL_CAP)
    if artifact.any():
        log.info(
            "IV-sanity: dropped %d rows (IV/realized-vol > %.0fx — data artifacts)", int(artifact.sum()), _IV_RVOL_CAP
        )
        df = df[~artifact].reset_index(drop=True)
    df = _fill_per_date_median(df, _VOL_FEATURES)

    dates = np.array(sorted(df["date"].unique()))
    labeled = df.dropna(subset=["abs_move"])
    rows = []
    last_model = None
    test_dates = [d for d in dates[min_train:] if d in set(labeled["date"].unique())]
    for i, d in enumerate(test_dates):
        train_dates = np.array(sorted(labeled.loc[labeled["date"] < d, "date"].unique()))
        if len(train_dates) <= horizon:
            continue
        train = labeled[labeled["date"].isin(set(train_dates[: len(train_dates) - horizon]))]  # purge
        test = labeled[labeled["date"] == d]
        if len(train) < 2000 or test.empty:
            continue
        if last_model is None or i % refit == 0:
            preds, last_model = _fit_predict(
                model_name, train[_VOL_FEATURES].values, train["abs_move"].values, test[_VOL_FEATURES].values
            )
        else:
            preds = last_model.predict(test[_VOL_FEATURES].values)
        o = test[["ticker", "date", "abs_move", "impl_move", "atm_iv_30d"]].copy()
        o["forecast_move"] = np.clip(preds, 1e-4, None)
        rows.append(o)
    val = pd.concat(rows, ignore_index=True)

    fic = [spearmanr(g["forecast_move"], g["abs_move"]).correlation for _, g in val.groupby("date") if len(g) > 30]
    fic = float(np.nanmean(fic))
    vrp = (val["abs_move"] / val["impl_move"]).replace([np.inf, -np.inf], np.nan).dropna()
    val["richness"] = val["impl_move"] / val["forecast_move"]
    val["rich_dec"] = val.groupby("date")["richness"].transform(
        lambda s: pd.qcut(s.rank(method="first"), 10, labels=False)
    )
    val["sell_pnl"] = val["impl_move"] - val["abs_move"]  # premium-seller P&L proxy (return %)
    rich = val[val["rich_dec"] == 9].copy()
    cheap = val[val["rich_dec"] == 0]

    # Tail-capped short-straddle backtest on the rich (sell-premium) cohort, plus an
    # earnings proxy: exclude names whose ATM IV is in the top decile that day (a
    # blunt stand-in for pre-earnings IV — we lack per-trade historical earnings dates).
    rich["_iv_dec"] = rich.groupby("date")["atm_iv_30d"].transform(lambda s: s.rank(pct=True))
    bt_all = _straddle_backtest(rich, horizon)
    bt_ex_earn = _straddle_backtest(rich[rich["_iv_dec"] < 0.90], horizon)

    # Empirical distribution of realized/forecast move (101-point quantile grid) so the
    # recommender can turn any breakeven multiple into a win probability via its CDF.
    ratio = (val["abs_move"] / val["forecast_move"]).replace([np.inf, -np.inf], np.nan).dropna()
    ratio_q = np.quantile(ratio, np.linspace(0, 1, 101)).tolist() if len(ratio) else []

    summary = {
        "horizon": horizon,
        "test_days": int(val["date"].nunique()),
        "forecast_ic": fic,
        "vrp_mean": float(vrp.mean()),
        "vrp_median": float(vrp.median()),
        "pct_below": float((val["abs_move"] < val["impl_move"]).mean()),
        "rich_realized_implied": float((rich["abs_move"] / rich["impl_move"]).mean()),
        "cheap_realized_implied": float((cheap["abs_move"] / cheap["impl_move"]).mean()),
        "rich_edge": float(rich["sell_pnl"].mean()),
        "cheap_edge": float(cheap["sell_pnl"].mean()),
        "straddle_bt": bt_all,
        "straddle_bt_ex_earn": bt_ex_earn,
        "ratio_q": ratio_q,  # quantile grid of realized/forecast move (for win-prob CDF)
    }

    # Live: train on everything labeled, forecast the latest (unlabeled) date.
    latest = df["date"].max()
    live = df[df["date"] == latest].copy()
    preds, _ = _fit_predict(
        model_name, labeled[_VOL_FEATURES].values, labeled["abs_move"].values, live[_VOL_FEATURES].values
    )
    live["forecast_move"] = np.clip(preds, 1e-4, None)
    live["richness"] = live["impl_move"] / live["forecast_move"]
    live = live[live["total_opt_volume"] >= min_opt_volume].copy()
    # Cross-sectional richness percentile (for rich/cheap labels independent of universe size).
    live["richness_pct"] = live["richness"].rank(pct=True)
    summary["latest_date"] = pd.Timestamp(latest).date().isoformat()
    return summary, live


def get_vol_view(
    universe: str = "companies",
    horizon: int = 2,
    model_name: str = "xgb",
    min_train: int = 40,
    refit: int = 5,
    min_opt_volume: float = 500.0,
    min_market_cap: float | None = None,
) -> tuple[dict, pd.DataFrame]:
    """End-to-end: load ORATS panel → filter universe → engineer features → train/score
    → return (summary, live_df). Used by the standalone recommendation engine."""
    allowed_types, default_cap, label = _UNIVERSES[universe]
    cap = default_cap if min_market_cap is None else min_market_cap
    panel = load_panel()
    panel = apply_universe_filter(panel, allowed_types, cap, label)
    feat_df = engineer_features(panel, horizon)
    return _vol_compute(feat_df, horizon, model_name, min_train, refit, min_opt_volume)


def run_vol_mode(
    feat_df: pd.DataFrame,
    horizon: int,
    model_name: str,
    min_train: int,
    refit: int,
    top_n: int,
    min_opt_volume: float,
    output_dir: str,
    universe: str,
) -> None:
    """CLI volatility/VRP report — computes via _vol_compute, prints + writes CSV."""
    summary, live = _vol_compute(feat_df, horizon, model_name, min_train, refit, min_opt_volume)
    fic = summary["forecast_ic"]
    latest = summary["latest_date"]

    print("\n" + "=" * 72)
    print(f"  VOLATILITY / VARIANCE-RISK-PREMIUM MODEL  (horizon={horizon}d, {summary['test_days']} test days)")
    print("=" * 72)
    print(f"  Move-size forecast IC               : {fic:+.3f}   (skill at ranking which names move most)")
    print(f"  Realized move / implied move (mean) : {summary['vrp_mean']:.3f}   (median {summary['vrp_median']:.3f})")
    print(f"  % names realized < implied          : {summary['pct_below'] * 100:.1f}%  (premium-seller win base rate)")
    print("  ── Rank by richness = implied / forecasted move ──")
    print(
        f"  RICH decile (sell premium): realized/implied {summary['rich_realized_implied']:.2f}  "
        f"avg seller edge {summary['rich_edge'] * 100:+.2f}%/trade  ({horizon}d)"
    )
    print(
        f"  CHEAP decile (buy premium): realized/implied {summary['cheap_realized_implied']:.2f}  "
        f"avg seller edge {summary['cheap_edge'] * 100:+.2f}%/trade  ({horizon}d)"
    )
    print(f"  Sell-rich minus sell-cheap spread   : {(summary['rich_edge'] - summary['cheap_edge']) * 100:+.2f}%/trade")
    bt = summary.get("straddle_bt") or {}
    bx = summary.get("straddle_bt_ex_earn") or {}
    if bt:
        print(
            f"  ── Tail-capped short-straddle backtest (rich cohort, prem≈{_STRADDLE_PREMIUM_FRAC:.0%}×implied, "
            f"stop −{_STRADDLE_TAIL_CAP:.0f}× prem, {_STRADDLE_COST_FRAC:.0%} cost) ──"
        )
        print(
            f"  N={bt['n']}  net {bt['mean_net'] * 100:+.2f}%/trade  win {bt['win_rate'] * 100:.0f}%  "
            f"Sharpe(ann) {bt['sharpe_ann']:+.2f}"
        )
        print(
            f"  worst trade {bt['worst'] * 100:+.1f}%  hit-tail-cap {bt['pct_hit_cap'] * 100:.0f}%  "
            f"(uncapped net {bt['uncapped_mean_net'] * 100:+.2f}% — gap = tail damage)"
        )
        if bx:
            print(
                f"  ex top-IV-decile (earnings proxy): N={bx['n']}  net {bx['mean_net'] * 100:+.2f}%/trade  "
                f"win {bx['win_rate'] * 100:.0f}%  worst {bx['worst'] * 100:+.1f}%  Sharpe {bx['sharpe_ann']:+.2f}"
            )
    print("=" * 72)

    def _fmt(d: pd.DataFrame) -> pd.DataFrame:
        s = d[
            [
                "ticker",
                "stk_px",
                "market_cap",
                "atm_iv_30d",
                "impl_move",
                "forecast_move",
                "richness",
                "total_opt_volume",
            ]
        ].copy()
        s["cap_$B"] = (s["market_cap"] / 1e9).round(2)
        s["impl_move_%"] = (s["impl_move"] * 100).round(2)
        s["forecast_move_%"] = (s["forecast_move"] * 100).round(2)
        s["richness"] = s["richness"].round(2)
        s["atm_iv"] = s["atm_iv_30d"].round(2)
        s["stk_px"] = s["stk_px"].round(2)
        s["total_opt_volume"] = s["total_opt_volume"].astype("Int64")
        return s[
            ["ticker", "stk_px", "cap_$B", "atm_iv", "impl_move_%", "forecast_move_%", "richness", "total_opt_volume"]
        ]

    sell = live.sort_values("richness", ascending=False).head(top_n)
    buy = live.sort_values("richness", ascending=True).head(top_n)
    print(
        f"\n  NEXT-{horizon}D SELL-PREMIUM candidates (options imply more move than forecast — {pd.Timestamp(latest).date()})"
    )
    print("  short straddle/strangle, covered calls, cash-secured puts:")
    print(_fmt(sell).to_string(index=False))
    print(f"\n  NEXT-{horizon}D BUY-PREMIUM candidates (options imply LESS move than forecast — expect a move)")
    print("  long straddle/strangle if a catalyst is expected:")
    print(_fmt(buy).to_string(index=False))

    out = pd.concat([_fmt(sell).assign(bucket="SELL_PREMIUM"), _fmt(buy).assign(bucket="BUY_PREMIUM")])
    out_path = Path(output_dir) / f"orats_vol_{universe}_{pd.Timestamp(latest).date()}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    print(f"\nSaved → {out_path}")
    print("Note: the move-size forecast leans on free realized vol; the EDGE is realized-vs-implied (the VRP),")
    print("which requires the paid IV. This is a magnitude/vol view — it does NOT predict direction.")


def main() -> None:
    ap = argparse.ArgumentParser(description="ORATS standalone opportunity prediction model")
    ap.add_argument(
        "--mode",
        choices=["direction", "vol"],
        default="direction",
        help="direction = predict signed return (weak, vol-tilt only); "
        "vol = predict move SIZE + rich/cheap options vs implied (the real ORATS edge)",
    )
    ap.add_argument(
        "--horizon", type=int, default=1, help="Forward horizon in trading days (default 1; use 2-3 for vol mode)"
    )
    ap.add_argument("--min-train", type=int, default=40, help="Min train days before walk-forward starts")
    ap.add_argument("--refit", type=int, default=5, help="Refit model every N test days (default 5)")
    ap.add_argument(
        "--model",
        choices=["xgb", "ridge"],
        default=None,
        help="default resolves per-mode: direction→ridge (xgb overfits the weak signal), "
        "vol→xgb (higher move-size forecast IC). Pass to override.",
    )
    ap.add_argument("--top-n", type=int, default=20, help="Opportunities per side to print")
    ap.add_argument(
        "--min-opt-volume",
        type=float,
        default=500.0,
        help="Liquidity floor (total option volume) for the live opportunity list",
    )
    ap.add_argument(
        "--universe",
        choices=["companies", "etf"],
        default="companies",
        help="companies = type CS/ADRC ≥$10B (default); etf = ETF/ETN/fund ≥$1B AUM (separate model)",
    )
    ap.add_argument(
        "--min-market-cap",
        type=float,
        default=None,
        help="Override the per-universe market-cap/AUM floor in USD (shares×price). 0 disables.",
    )
    ap.add_argument("--placebo", action="store_true", help="Shuffle the target → noise-floor IC")
    ap.add_argument("--output-dir", default="data", help="Where to write the opportunities CSV")
    args = ap.parse_args()

    allowed_types, default_cap, cap_label = _UNIVERSES[args.universe]
    min_cap = default_cap if args.min_market_cap is None else args.min_market_cap
    model = args.model or ("xgb" if args.mode == "vol" else "ridge")

    log.info("Loading ORATS panel from Postgres…")
    panel = load_panel()
    log.info("Panel: %d rows, %d tickers, %d dates", len(panel), panel["ticker"].nunique(), panel["date"].nunique())

    log.info("=== Universe: %s ===", args.universe.upper())
    panel = apply_universe_filter(panel, allowed_types, min_cap, cap_label)

    feat_df = engineer_features(panel, args.horizon)

    if args.mode == "vol":
        # NB: no per-day winsorization here — the straddle backtest must keep genuine
        # tail moves (earnings, leveraged-ETF blowups). _vol_compute applies only a
        # 60% data-error guard. This path matches get_vol_view used by the recommender.
        run_vol_mode(
            feat_df,
            args.horizon,
            model,
            args.min_train,
            args.refit,
            args.top_n,
            args.min_opt_volume,
            args.output_dir,
            args.universe,
        )
        return

    # Direction model only: winsorize the target per-day to kill split/stale-price
    # outliers (raw std ~0.34) that would otherwise dominate the signed-return fit.
    feat_df["fwd_ret"] = feat_df.groupby("date")["fwd_ret"].transform(
        lambda s: s.clip(s.quantile(0.01), s.quantile(0.99))
    )
    std_df = cross_sectional_standardize(feat_df, _MODEL_FEATURES)

    preds = walk_forward(std_df, _MODEL_FEATURES, args.horizon, args.min_train, args.refit, model, args.placebo)
    val = report_validation(preds, args.horizon)

    if args.placebo:
        print("\n(placebo run — target shuffled; the above IC is the noise floor.)")
        return

    out, latest_date = score_live(
        std_df, feat_df, _MODEL_FEATURES, model, args.horizon, args.top_n, args.min_opt_volume, val
    )
    out_path = Path(args.output_dir) / f"orats_opportunities_{args.universe}_{pd.Timestamp(latest_date).date()}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    print(f"\nSaved {len(out)} opportunities → {out_path}")
    print("Reminder: only sides flagged reliable=True showed positive out-of-sample decile edge.")


if __name__ == "__main__":
    main()
