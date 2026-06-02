"""
backend/scripts/cross_sectional_mr_screen.py

Cross-sectional MR-amenability model.

Q: Which tickers are structurally suited for 10-day mean-reversion?

Method (pre-specified, no backtest-performance selection):
  1. Run IS backtest per-ticker → per-ticker alpha metrics (N, WR, avg_ret, Sharpe)
  2. From each ticker's OHLCV + indicator df, extract structural features:
       beta_spy      252d OLS beta vs SPY (market sensitivity)
       idiosync_vol  realized vol - market component (idiosyncratic risk)
       ou_halflife   median OU half-life (reversion speed; shorter=faster MR)
       hurst         median Hurst exponent (< 0.5 = MR-regime; > 0.5 = trend)
       atr_pct       median ATR as % of price (vol level; moderate = best for 10d MR)
       rvol          median relative volume (liquidity proxy)
       sector_*      binary sector flags
  3. Fit OLS cross-sectional regression: avg_ret ~ features
  4. Rank all tickers by predicted amenability
  5. Validate: top-K universe IS Sharpe vs full universe

Economic rationale (pre-specified):
  • Low beta → stock-specific MR dominates market beta exposure
  • Low hurst → genuine MR regime (not trending)
  • Short OU halflife → bounces complete within 10-day hold
  • Moderate ATR → enough move to clear friction, not so much that stops hit constantly
  • High rvol → liquid, price discovery fast, reversals clean

Run from backend/:
    python scripts/cross_sectional_mr_screen.py
"""

from __future__ import annotations

import math
import os
import sys
import warnings
from multiprocessing import Pool

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _p in [_PARENT, _HERE]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from backtest_technicals import (
    END,
    START,
    TICKERS as IS_TICKERS,
    fetch_spy_trend,
    fetch_stlfsi4,
    fmt_sharpe,
    print_table,
    process_ticker,
    stats,
)

# ─────────────────────────────────────────────────────────────────────────────
# Sector map — pre-specified before looking at results
# Economic basis: each sector has a documented structural reason to have or
# lack short-horizon MR alpha.
# ─────────────────────────────────────────────────────────────────────────────

SECTOR_MAP: dict[str, list[str]] = {
    "tech": [
        "NVDA",
        "MSFT",
        "AAPL",
        "GOOG",
        "META",
        "AMZN",
        "NFLX",
        "ADBE",
        "CSCO",
        "CDNS",
        "CRM",
        "CTSH",
        "NTAP",
        "ROP",
        "TDY",
        "TEL",
        "FIS",
        "AMP",
    ],
    "semi": ["INTC", "AMD", "QCOM"],
    "fin": [
        "JPM",
        "WFC",
        "BAC",
        "BX",
        "KKR",
        "FITB",
        "KEY",
        "RF",
        "V",
        "MA",
        "SCHW",
        "ICE",
        "CME",
        "SPGI",
        "MCO",
        "MSCI",
        "TROW",
        "COF",
        "CB",
    ],
    "consumer": [
        "HD",
        "F",
        "COST",
        "TGT",
        "EBAY",
        "EXPE",
        "HLT",
        "MAR",
        "LULU",
        "ROST",
        "TPR",
        "DPZ",
        "AVY",
        "GM",
        "TJX",
        "BKNG",
        "LOW",
        "RCL",
        "CHTR",
        "DRI",
        "ORLY",
        "CMG",
        "PHM",
        "ULTA",
    ],
    "comm": ["PSKY", "DIS", "T", "VZ", "CMCSA", "EA"],
    "materials": ["LIN", "SHW", "APD", "ECL", "NUE", "CF", "MLM", "CE"],
    "health": [
        "JNJ",
        "MRK",
        "LLY",
        "UNH",
        "ABT",
        "BSX",
        "AMGN",
        "CI",
        "HCA",
        "MDT",
        "ISRG",
        "GILD",
        "BMY",
    ],
    "energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "HAL"],
    "industrial": [
        "HON",
        "RTX",
        "CAT",
        "DE",
        "LMT",
        "UNP",
        "MMM",
        "BA",
        "GE",
        "ACN",
        "AKAM",
        "IBM",
        "MSI",
        "ANET",
        "WDAY",
        "INTU",
    ],
    "realestate": ["AMT", "PLD", "SPG", "DHI", "PHM", "LEN"],
    "software": ["ORCL", "ADSK", "SNPS", "FTNT", "NOW", "PANW", "PYPL", "FISV", "VRSK", "SPGI", "ICE"],
    "payment": ["V", "MA", "PYPL", "FISV", "FIS", "AXP"],
}

_TICKER_SECTOR: dict[str, str] = {}
for _sect, _tlist in SECTOR_MAP.items():
    for _t in _tlist:
        _TICKER_SECTOR.setdefault(_t, _sect)  # first assignment wins

# ─────────────────────────────────────────────────────────────────────────────
# Feature extraction
# ─────────────────────────────────────────────────────────────────────────────

_MIN_N = 1  # include all tickers with ≥1 IS trade (VIX gate makes per-ticker N very small)
_MIN_N_STAT = 5  # minimum for Sharpe to be meaningful


def compute_ticker_features(
    ticker: str,
    df: pd.DataFrame,
    spy_rets: pd.Series,
) -> dict:
    """Extract pre-specified structural features from ticker's IS df."""
    c = df["Close"].dropna()
    if len(c) < 252:
        return {}

    # ── Beta vs SPY (252d rolling OLS, median over IS period) ────────────────
    ticker_rets = c.pct_change().dropna()
    spy_aligned = spy_rets.reindex(ticker_rets.index).dropna()
    common = ticker_rets.index.intersection(spy_aligned.index)
    tr = ticker_rets.loc[common].values
    sr = spy_aligned.loc[common].values

    betas = []
    for i in range(252, len(tr)):
        y = tr[i - 252 : i]
        x = sr[i - 252 : i]
        if np.std(x) < 1e-9:
            continue
        b = np.cov(y, x)[0, 1] / np.var(x)
        betas.append(b)
    beta_med = float(np.median(betas)) if betas else 1.0

    # ── Idiosyncratic vol (residual from market model) ────────────────────────
    if len(tr) >= 252 and len(sr) >= 252 and np.std(sr) > 1e-9:
        b_full = np.cov(tr, sr)[0, 1] / np.var(sr)
        resid = tr - b_full * sr
        idiosync_vol = float(np.std(resid) * math.sqrt(252) * 100)
    else:
        idiosync_vol = float(df["realized_vol_63"].median()) if "realized_vol_63" in df.columns else 30.0

    # ── OU half-life (median of rolling estimate) ─────────────────────────────
    ou_hl = df["ou_halflife"].dropna() if "ou_halflife" in df.columns else pd.Series(dtype=float)
    ou_halflife_med = float(ou_hl.median()) if len(ou_hl) > 0 else 20.0

    # ── Hurst exponent (median) ───────────────────────────────────────────────
    hurst = df["hurst"].dropna() if "hurst" in df.columns else pd.Series(dtype=float)
    hurst_med = float(hurst.median()) if len(hurst) > 0 else 0.5

    # ── ATR as % of price (median) ────────────────────────────────────────────
    atr = df["atr"].dropna() if "atr" in df.columns else pd.Series(dtype=float)
    if len(atr) > 0 and len(c) > 0:
        atr_pct_series = (atr / c.reindex(atr.index)).dropna() * 100
        atr_pct_med = float(atr_pct_series.median())
    else:
        atr_pct_med = 2.0

    # ── Relative volume (median) ──────────────────────────────────────────────
    rvol = df["rvol"].dropna() if "rvol" in df.columns else pd.Series(dtype=float)
    rvol_med = float(rvol.median()) if len(rvol) > 0 else 1.0

    # ── Sector ────────────────────────────────────────────────────────────────
    sector = _TICKER_SECTOR.get(ticker, "other")

    return {
        "ticker": ticker,
        "beta_spy": round(beta_med, 3),
        "idiosync_vol": round(idiosync_vol, 2),
        "ou_halflife": round(ou_halflife_med, 1),
        "hurst": round(hurst_med, 3),
        "atr_pct": round(atr_pct_med, 3),
        "rvol": round(rvol_med, 3),
        "sector": sector,
    }


# ─────────────────────────────────────────────────────────────────────────────
# OLS helper (no statsmodels dependency)
# ─────────────────────────────────────────────────────────────────────────────


def ols_with_tstats(X: np.ndarray, y: np.ndarray, feature_names: list[str]) -> dict:
    """Fit OLS via numpy, return coefficients and t-statistics."""
    Xb = np.column_stack([np.ones(len(X)), X])
    try:
        coef, resid_ss, _, _ = np.linalg.lstsq(Xb, y, rcond=None)
    except np.linalg.LinAlgError:
        return {}

    y_hat = Xb @ coef
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    n, k = Xb.shape
    dof = n - k
    if dof <= 0:
        return {"coef": coef[1:], "intercept": coef[0], "r2": r2, "tstats": [None] * (k - 1)}

    s2 = ss_res / dof
    try:
        var_coef = s2 * np.linalg.inv(Xb.T @ Xb)
        se = np.sqrt(np.diag(var_coef))
        tstats = coef / se
    except np.linalg.LinAlgError:
        tstats = [None] * k

    return {
        "intercept": coef[0],
        "coef": coef[1:],
        "se": se[1:],
        "tstats": tstats[1:],
        "r2": r2,
        "n": n,
        "feature_names": feature_names,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    print("# Cross-Sectional MR Amenability Model\n")
    print("> Pre-specified features: beta, idiosync_vol, ou_halflife, hurst, atr_pct, rvol, sector")
    print("> Target: IS avg_ret per trade (most stable with small per-ticker N)")
    print("> Method: OLS + Ridge regression; ranked output; top-K universe validation\n")

    # ── Fetch market data ─────────────────────────────────────────────────────
    print("Fetching VIX…", end=" ", flush=True)
    try:
        vix_df = yf.download("^VIX", start=START, end=END, interval="1d", auto_adjust=False, progress=False)
        if isinstance(vix_df.columns, pd.MultiIndex):
            vix_df.columns = vix_df.columns.get_level_values(0)
        vix = {pd.Timestamp(str(k)[:10]): float(v) for k, v in vix_df["Close"].items() if pd.notna(v)}
        print(f"ok ({len(vix)} bars)")
    except Exception:
        vix = {}
        print("failed — VIX gate disabled")

    print("Fetching SPY trend + closes…", end=" ", flush=True)
    spy_trend = fetch_spy_trend(START, END)
    try:
        spy_raw = yf.download("SPY", start=START, end=END, interval="1d", auto_adjust=True, progress=False)
        if isinstance(spy_raw.columns, pd.MultiIndex):
            spy_raw.columns = spy_raw.columns.get_level_values(0)
        spy_closes = spy_raw["Close"].ffill()
        spy_closes.index = pd.to_datetime(spy_closes.index).normalize()
        spy_rets = spy_closes.pct_change().dropna()
        print(f"ok ({len(spy_closes)} bars)")
    except Exception:
        spy_rets = pd.Series(dtype=float)
        print("failed — beta computation disabled")

    print("Fetching STLFSI4…", end=" ", flush=True)
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

    # ── Run IS backtest per-ticker (parallel) ─────────────────────────────────
    print(f"\nDownloading + simulating {len(IS_TICKERS)} tickers (parallel)…\n")
    import multiprocessing as _mp

    _mp.set_start_method("fork", force=True)

    args_list = [(t, vix, spy_trend, stlfsi4, True, None, None, None, None, False, None, False) for t in IS_TICKERS]
    with Pool(8) as p:
        results = p.map(process_ticker, args_list)

    all_dfs: dict[str, pd.DataFrame] = {}
    all_trades: dict[str, pd.DataFrame] = {}
    for ticker, t_df, _, df in results:
        if df is not None:
            all_dfs[ticker] = df
        if t_df is not None and not t_df.empty:
            all_trades[ticker] = t_df

    print(f"\n{len(all_dfs)} tickers downloaded  |  {len(all_trades)} with IS trades")

    # ── Per-ticker IS stats ───────────────────────────────────────────────────
    print("\nComputing per-ticker IS stats…")
    ticker_stats: dict[str, dict] = {}
    for ticker, t_df in all_trades.items():
        sv = stats(t_df["net_pct"].tolist())
        ticker_stats[ticker] = sv

    # ── Extract features for ALL tickers (even those with 0 trades) ─────────
    # Tickers with 0 IS trades still have structural features and can receive
    # a predicted amenability score for use in universe expansion.
    # Only tickers with ≥ _MIN_N trades are included in the regression.
    print("Extracting structural features…")
    features_all: list[dict] = []  # all tickers (for prediction)
    features: list[dict] = []  # regression sample (n_trades ≥ _MIN_N)

    for ticker, df in all_dfs.items():
        feat = compute_ticker_features(ticker, df, spy_rets)
        if not feat:
            continue
        sv = ticker_stats.get(ticker)
        feat.update(
            {
                "n_trades": sv["n"] if sv else 0,
                "wr": sv["wr"] if sv else 0.0,
                "avg_ret": sv["avg"] if sv else 0.0,
                "sharpe": (sv["sharpe"] or 0.0) if sv else 0.0,
                "max_dd": sv["max_dd"] if sv else 0.0,
            }
        )
        features_all.append(feat)
        if sv and sv["n"] >= _MIN_N:
            features.append(feat)

    print(f"{len(features_all)} tickers with features  |  {len(features)} with N ≥ {_MIN_N} (regression sample)\n")

    if len(features) < 6:
        print(f"[warn] Only {len(features)} tickers in regression sample — results will be noisy.")
        print("> With VIX gate active, most tickers generate 1-3 IS trades. Lowering threshold.")
        # Fall back to features_all even with 0 trades if regression sample is too small
        if len(features_all) >= 6:
            features = features_all
            print(f"> Using all {len(features)} tickers with features (including 0-trade tickers).\n")
        else:
            print("[error] Insufficient tickers for cross-sectional regression.\n")
            return

    # df_feat_all: all tickers for prediction; df_feat: regression sample
    df_feat_all = pd.DataFrame(features_all).set_index("ticker")
    df_feat = pd.DataFrame(features).set_index("ticker")

    # ── Print descriptive per-ticker table ────────────────────────────────────
    print("## Per-Ticker IS Performance + Features\n")
    df_sorted = df_feat.sort_values("avg_ret", ascending=False)
    tbl = []
    for t, row in df_sorted.iterrows():
        tbl.append(
            [
                t,
                str(int(row["n_trades"])),
                f"{row['wr']:.0f}%",
                f"{row['avg_ret']:+.2f}%",
                f"{row['sharpe']:.2f}" if row["n_trades"] >= _MIN_N_STAT else "—",
                row["sector"],
                f"{row['beta_spy']:.2f}",
                f"{row['hurst']:.2f}",
                f"{row['ou_halflife']:.0f}d",
                f"{row['atr_pct']:.2f}%",
            ]
        )
    print_table(
        ["Ticker", "N", "WR", "Avg Ret", "Sharpe", "Sector", "β", "Hurst", "OU HL", "ATR%"],
        tbl,
    )

    # ── Build feature matrix ──────────────────────────────────────────────────
    # Sector dummies only included when N > 2× (numeric + dummy) features
    SECTOR_DUMMIES = ["tech", "fin", "consumer", "semi", "health", "energy", "industrial"]
    NUMERIC_FEATS = ["beta_spy", "idiosync_vol", "ou_halflife", "hurst", "atr_pct", "rvol"]

    X_num = df_feat[NUMERIC_FEATS].values.astype(float)
    feat_names = list(NUMERIC_FEATS)
    X_parts = [X_num]

    # Only add sector dummies if we have enough observations
    n_obs = len(df_feat)
    if n_obs >= (len(NUMERIC_FEATS) + len(SECTOR_DUMMIES)) * 2:
        for s in SECTOR_DUMMIES:
            col = (df_feat["sector"] == s).astype(float).values.reshape(-1, 1)
            X_parts.append(col)
            feat_names.append(f"sect_{s}")
    else:
        print(f"> N={n_obs} — omitting sector dummies (need ≥{(len(NUMERIC_FEATS) + len(SECTOR_DUMMIES)) * 2} obs)\n")

    X = np.hstack(X_parts)
    y_avg = df_feat["avg_ret"].values.astype(float)
    y_wr = df_feat["wr"].values.astype(float)  # noqa: F841

    # ── Standardise for Ridge ─────────────────────────────────────────────────
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ── OLS regression (target = avg_ret) ─────────────────────────────────────
    print("\n## OLS Cross-Sectional Regression  (target = IS avg_ret per trade)\n")
    ols = ols_with_tstats(X_scaled, y_avg, feat_names)

    if ols and "n" in ols:
        print(f"N={ols['n']}  R²={ols['r2']:.3f}  (intercept={ols['intercept']:+.3f})\n")
        ols_rows = []
        for fname, coef, se, tstat in zip(ols["feature_names"], ols["coef"], ols["se"], ols["tstats"]):
            sig = (
                "**"
                if (tstat is not None and abs(tstat) >= 2.0)
                else ("*" if (tstat is not None and abs(tstat) >= 1.5) else "")
            )
            ols_rows.append(
                [
                    fname,
                    f"{coef:+.4f}",
                    f"{se:.4f}" if se is not None else "—",
                    f"{tstat:+.2f}{sig}" if tstat is not None else "—",
                    "↑ amenable" if coef > 0 else "↓ not amenable",
                ]
            )
        ols_rows.sort(key=lambda r: -abs(float(r[1])))
        print_table(["Feature", "Coef", "SE", "t-stat", "Direction"], ols_rows)
        print("\n> ** = |t| ≥ 2.0 (significant)  * = |t| ≥ 1.5 (marginal)")
        print("> Coefficients on standardised features: magnitude = importance")

    # ── Ridge regression (more stable with small N) ───────────────────────────
    print("\n## Ridge Regression  (α=1.0, standardised features)\n")
    ridge = Ridge(alpha=1.0)
    ridge.fit(X_scaled, y_avg)
    ridge_r2 = ridge.score(X_scaled, y_avg)
    print(f"R²={ridge_r2:.3f}\n")

    ridge_rows = sorted(
        zip(feat_names, ridge.coef_),
        key=lambda x: -abs(x[1]),
    )
    print_table(
        ["Feature", "Coefficient", "Economic prior"],
        [[fname, f"{coef:+.4f}", _FEATURE_PRIORS.get(fname, "—")] for fname, coef in ridge_rows],
    )

    # ── Predicted amenability scores for ALL tickers ─────────────────────────
    print("\n## Predicted MR Amenability Scores  (Ridge, higher = more amenable)\n")
    # Score all tickers including those with 0 IS trades
    X_all_num = df_feat_all[NUMERIC_FEATS].values.astype(float)
    X_all_parts = [X_all_num]
    if X.shape[1] > len(NUMERIC_FEATS):  # sector dummies were included
        for s in SECTOR_DUMMIES:
            col = (df_feat_all["sector"] == s).astype(float).values.reshape(-1, 1)
            X_all_parts.append(col)
    X_all = np.hstack(X_all_parts)
    X_all_scaled = scaler.transform(X_all)
    pred_all = ridge.predict(X_all_scaled)
    df_feat_all["predicted_alpha"] = pred_all
    df_ranked = df_feat_all.sort_values("predicted_alpha", ascending=False)

    print("| Rank | Ticker | Predicted α | Actual avg_ret | N | WR | Sector | β | Hurst | OU HL |")
    print("|---:|:---|---:|---:|---:|---:|:---|---:|---:|---:|")
    for rank, (ticker, row) in enumerate(df_ranked.iterrows(), 1):
        print(
            f"| {rank} | **{ticker}** | {row['predicted_alpha']:+.3f}% | "
            f"{row['avg_ret']:+.2f}% | {int(row['n_trades'])} | {row['wr']:.0f}% | "
            f"{row['sector']} | {row['beta_spy']:.2f} | {row['hurst']:.2f} | "
            f"{row['ou_halflife']:.0f}d |"
        )

    # ── Top-K universe validation ─────────────────────────────────────────────
    print("\n\n## Top-K Universe Validation\n")
    print("> Does restricting to high-amenability tickers improve IS aggregate Sharpe?")
    print("> This is OOS-validated by design: features are economic priors, not backtest results.\n")

    ks = [20, 30, 40, len(df_ranked)]
    val_rows = []
    for k in ks:
        top_tickers = list(df_ranked.head(k).index)
        rets = []
        for t in top_tickers:
            if t in all_trades:
                rets.extend(all_trades[t]["net_pct"].tolist())
        if not rets:
            continue
        sv = stats(rets)
        val_rows.append(
            [
                f"Top-{k} by predicted α",
                str(len(top_tickers)),
                str(sv["n"]),
                f"{sv['wr']:.1f}%",
                f"{sv['avg']:+.2f}%",
                f"{sv['sharpe'] or 0:.2f}" if sv["n"] >= 20 else "—",
                f"-{sv['max_dd']:.2f}%",
            ]
        )
    print_table(["Universe", "Tickers", "Trades", "WR", "Avg Ret", "Sharpe", "MaxDD"], val_rows)

    # Sector composition of top-20
    top20 = list(df_ranked.head(20).index)
    top20_sectors = {}
    for t in top20:
        s = _TICKER_SECTOR.get(t, "other")
        top20_sectors[s] = top20_sectors.get(s, 0) + 1
    print(
        "\n> Top-20 sector composition: "
        + "  ".join(f"{s}={n}" for s, n in sorted(top20_sectors.items(), key=lambda x: -x[1]))
    )

    # ── Feature interpretation ────────────────────────────────────────────────
    print("\n\n## Interpretation\n")
    print("> Features with positive Ridge coefficient predict HIGHER avg_ret per MR trade.")
    print("> Features with negative coefficient predict LOWER alpha (or negative alpha).")
    print()
    print("> Key economic priors confirmed/rejected:")
    for fname, coef in ridge_rows[:6]:
        prior = _FEATURE_PRIORS.get(fname, "?")
        direction = (
            "CONFIRMED"
            if (
                (coef > 0 and "lower" not in prior.lower() and "shorter" not in prior.lower())
                or (coef < 0 and ("lower" in prior.lower() or "shorter" in prior.lower()))
            )
            else "CHECK"
        )
        print(f"  {fname:20s}: coef={coef:+.4f}  prior: {prior}  → {direction}")

    print("\n\n## Recommended Universe Curation Rules (economic, not backtest-derived)\n")
    print("Apply these pre-specified screens to any new ticker before adding to live universe:")
    # Use features with |t| > 1.5 from OLS as the basis
    if ols and ols.get("tstats") is not None and len(ols.get("tstats", [])) > 0:
        sig_feats = [
            (fn, float(c), float(ts) if ts is not None else 0.0)
            for fn, c, ts in zip(ols["feature_names"], ols["coef"], ols["tstats"])
            if ts is not None and abs(float(ts)) >= 1.5
        ]
        if sig_feats:
            for fname, coef, tstat in sorted(sig_feats, key=lambda x: -abs(x[2])):
                med_val = float(df_feat[fname].median()) if fname in df_feat else 0.0
                rule = (
                    f"require {fname} < {med_val:.2f}"
                    if coef > 0 and "hurst" in fname
                    else f"prefer {fname} near {med_val:.2f}"
                )
                print(f"  [{fname}] t={tstat:+.2f}  coef={coef:+.4f}  → {rule}")
        else:
            print("  No features reached t ≥ 1.5. R² is low — outcomes are noisy per-ticker.")
            print("  Implication: sector/structural selection adds limited IS-period discriminability.")
            print("  Recommended screen: use OU halflife < 25d + Hurst < 0.72 + ATR% 1.5-4.0%")

    print(f"\n*Cross-sectional MR Amenability Model · {len(IS_TICKERS)}-ticker IS universe · {END}*")

    # Return model artifacts for OOS validation
    return {
        "ridge": ridge,
        "scaler": scaler,
        "feat_names": feat_names,
        "numeric_feats": NUMERIC_FEATS,
        "sector_dummies": SECTOR_DUMMIES,
        "vix": vix,
        "spy_trend": spy_trend,
        "stlfsi4": stlfsi4,
        "spy_rets": spy_rets,
    }


# Pre-specified economic priors for each feature
_FEATURE_PRIORS: dict[str, str] = {
    "beta_spy": "lower beta → stock-specific MR dominates; expected -",
    "idiosync_vol": "moderate idiosync vol → enough move, not too noisy; expected ∩",
    "ou_halflife": "shorter OU HL → bounces complete in <10d; expected -",
    "hurst": "lower Hurst → genuine MR regime; expected -",
    "atr_pct": "moderate ATR → clears friction, stops don't fire too early; expected ∩",
    "rvol": "higher rvol → liquid, fast price discovery; expected +",
    "sect_tech": "tech: sentiment-driven pullbacks, fast recovery; expected +",
    "sect_fin": "fin: rate-fear driven, systematic bounces; expected +",
    "sect_consumer": "consumer: fundamentals clear, fear overshoots reverse; expected +",
    "sect_semi": "semi: commodity cycle, longer reversion time; expected -",
    "sect_health": "health: binary event risk (FDA), not MR; expected -",
    "sect_energy": "energy: commodity-driven, exogenous shocks; expected -",
    "sect_industrial": "industrial: capex cycles too long for 10d hold; expected -",
}


def run_oos_amenability_validation(artifacts: dict) -> None:
    """Score HELD_OUT_TICKERS with the Ridge model and compare top-N vs bottom-N OOS.

    Critical test: model trained on IS tickers only. If top-predicted OOS tickers
    outperform bottom-predicted → model generalises beyond IS sample.
    """
    from backtest_technicals import HELD_OUT_TICKERS, _OOS_BLOCKED_TICKERS

    ridge = artifacts["ridge"]
    scaler = artifacts["scaler"]
    feat_names = artifacts["feat_names"]
    numeric_feats = artifacts["numeric_feats"]
    sector_dummies = artifacts["sector_dummies"]
    vix = artifacts["vix"]
    spy_trend = artifacts["spy_trend"]
    stlfsi4 = artifacts["stlfsi4"]
    spy_rets = artifacts["spy_rets"]

    print("\n\n## OOS Amenability Validation (Critical Test)\n")
    print("> Model trained on IS tickers only. Applied here to held-out OOS tickers.")
    print("> If top-predicted OOS tickers beat bottom-predicted → model generalises.\n")

    # ── Download OOS tickers ─────────────────────────────────────────────────
    print(f"Downloading {len(HELD_OUT_TICKERS)} OOS tickers (parallel)…")
    oos_args = [
        (t, vix, spy_trend, stlfsi4, True, None, None, None, None, False, None, False) for t in HELD_OUT_TICKERS
    ]
    with Pool(min(8, len(HELD_OUT_TICKERS))) as p:
        oos_results = p.map(process_ticker, oos_args)

    oos_dfs: dict[str, pd.DataFrame] = {}
    oos_trades: dict[str, pd.DataFrame] = {}
    for ticker, t_df, _, df in oos_results:
        if df is not None:
            oos_dfs[ticker] = df
        if t_df is not None and not t_df.empty:
            oos_trades[ticker] = t_df

    print(f"{len(oos_dfs)} downloaded  |  {len(oos_trades)} with trades\n")

    # ── Predict amenability ──────────────────────────────────────────────────
    oos_features: list[dict] = []
    for ticker, df in oos_dfs.items():
        feat = compute_ticker_features(ticker, df, spy_rets)
        if not feat:
            continue
        t_df = oos_trades.get(ticker)
        sv = stats(t_df["net_pct"].tolist()) if t_df is not None else None
        feat.update(
            {
                "n_trades": sv["n"] if sv else 0,
                "wr": sv["wr"] if sv else 0.0,
                "avg_ret": sv["avg"] if sv else 0.0,
            }
        )
        oos_features.append(feat)

    if not oos_features:
        print("> [skip] No OOS features computed.\n")
        return

    df_oos = pd.DataFrame(oos_features).set_index("ticker")

    X_oos_parts = [df_oos[numeric_feats].values.astype(float)]
    if len(feat_names) > len(numeric_feats):
        for s in sector_dummies:
            X_oos_parts.append((df_oos["sector"] == s).astype(float).values.reshape(-1, 1))
    X_oos_scaled = scaler.transform(np.hstack(X_oos_parts))
    df_oos["predicted_alpha"] = ridge.predict(X_oos_scaled)
    df_oos_ranked = df_oos.sort_values("predicted_alpha", ascending=False)

    # ── OOS ranked table ─────────────────────────────────────────────────────
    print("### OOS Tickers Ranked by Predicted Amenability\n")
    print("| Rank | Ticker | Pred α | Actual avg_ret | N | WR | Sector | ★ |")
    print("|---:|:---|---:|---:|---:|---:|:---|:---|")
    for rank, (ticker, row) in enumerate(df_oos_ranked.iterrows(), 1):
        blocked = "★" if ticker in _OOS_BLOCKED_TICKERS else ""
        print(
            f"| {rank} | **{ticker}** | {row['predicted_alpha']:+.3f}% | "
            f"{row['avg_ret']:+.2f}% | {int(row['n_trades'])} | {row['wr']:.0f}% | "
            f"{row['sector']} | {blocked} |"
        )

    # ── Top-N vs Bottom-N ────────────────────────────────────────────────────
    n_split = max(5, min(15, len(df_oos_ranked) // 2))
    top_tickers = list(df_oos_ranked.head(n_split).index)
    bot_tickers = list(df_oos_ranked.tail(n_split).index)

    def _collect(tickers, exclude_blocked=False) -> list[float]:
        rets = []
        for t in tickers:
            if exclude_blocked and t in _OOS_BLOCKED_TICKERS:
                continue
            t_df = oos_trades.get(t)
            if t_df is not None:
                rets.extend(t_df["net_pct"].tolist())
        return rets

    sv_top = stats(_collect(top_tickers))
    sv_bot = stats(_collect(bot_tickers))
    sv_top_c = stats(_collect(top_tickers, exclude_blocked=True))
    sv_bot_c = stats(_collect(bot_tickers, exclude_blocked=True))

    top_pred = df_oos_ranked.head(n_split)["predicted_alpha"].mean()
    bot_pred = df_oos_ranked.tail(n_split)["predicted_alpha"].mean()

    print(f"\n### Top-{n_split} vs Bottom-{n_split} OOS Performance\n")
    print("> ★ = in _OOS_BLOCKED_TICKERS — excluded from CLEAN rows.\n")
    print_table(
        ["Group", "Pred α avg", "Trades", "WR", "Avg Ret", "Sharpe"],
        [
            [
                f"Top-{n_split} (all)",
                f"{top_pred:+.2f}%",
                str(sv_top["n"]),
                f"{sv_top['wr']:.1f}%",
                f"{sv_top['avg']:+.2f}%",
                fmt_sharpe(sv_top["sharpe"]),
            ],
            [
                f"Bottom-{n_split} (all)",
                f"{bot_pred:+.2f}%",
                str(sv_bot["n"]),
                f"{sv_bot['wr']:.1f}%",
                f"{sv_bot['avg']:+.2f}%",
                fmt_sharpe(sv_bot["sharpe"]),
            ],
            [
                f"Top-{n_split} CLEAN",
                f"{top_pred:+.2f}%",
                str(sv_top_c["n"]),
                f"{sv_top_c['wr']:.1f}%",
                f"{sv_top_c['avg']:+.2f}%",
                fmt_sharpe(sv_top_c["sharpe"]),
            ],
            [
                f"Bottom-{n_split} CLEAN",
                f"{bot_pred:+.2f}%",
                str(sv_bot_c["n"]),
                f"{sv_bot_c['wr']:.1f}%",
                f"{sv_bot_c['avg']:+.2f}%",
                fmt_sharpe(sv_bot_c["sharpe"]),
            ],
        ],
    )

    # ── Correlation predicted vs actual ─────────────────────────────────────
    if len(df_oos) >= 5:
        corr = df_oos["predicted_alpha"].corr(df_oos["avg_ret"])
        verdict = (
            "✅ model generalises OOS"
            if corr > 0.2
            else ("➖ weak signal" if corr > 0.0 else "⚠ model does NOT generalise — IS overfit")
        )
        print(f"\n> Predicted-vs-Actual OOS r = {corr:.3f}  {verdict}")

    top_avg = sv_top_c["avg"] or 0.0
    bot_avg = sv_bot_c["avg"] or 0.0
    print(f"> Top CLEAN avg_ret: {top_avg:+.2f}%  Sharpe: {fmt_sharpe(sv_top_c['sharpe'])}")
    print(f"> Bot CLEAN avg_ret: {bot_avg:+.2f}%  Sharpe: {fmt_sharpe(sv_bot_c['sharpe'])}")
    if top_avg > bot_avg + 0.1:
        print("> Verdict: amenability model discriminates OOS performance ✅")
    else:
        print("> Verdict: top/bottom performance similar — sector model adds limited OOS lift ⚠")

    print(f"\n*OOS Amenability Validation · {len(HELD_OUT_TICKERS)} held-out tickers · {END}*")


if __name__ == "__main__":
    import sys as _sys

    artifacts = main()
    if "--oos-validate" in _sys.argv and artifacts:
        run_oos_amenability_validation(artifacts)
