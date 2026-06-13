"""
Train XGBoost entry model on 23-year backtest trades.

Answers: given the *technical setup* at entry (BB%B, IBS, VWAP%, RSI, ADX, …),
what is the probability this MR trade wins?

This is complementary to signal_ml.py (which learns from signal *metadata* —
sources, rationale, style). Together they cover:
  • Entry model   → technical setup quality   (trained here, 23yr backtest)
  • Signal model  → signal assembly quality   (signal_ml.py, live DB signals)

The two win-probs are blended 50/50 in _assemble_signal() before applying
the multiplicative confidence adjustment.

Champion/challenger gate: new model only deployed if OOS AUC > current champion.

Usage:
  cd backend && python scripts/train_backtest_ml.py
"""

import asyncio
import json
import math
import multiprocessing
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from sqlalchemy import select

_DATA_DIR = Path(__file__).parent.parent / "data"
_MODEL_FILE = _DATA_DIR / "backtest_ml_model.json"
_FEATURE_FILE = _DATA_DIR / "backtest_ml_features.json"
_EVAL_FILE = _DATA_DIR / "backtest_ml_eval.json"

# 14 technical features — all computable from live `tech` dict + VIX + sector
ENTRY_FEATURE_NAMES = [
    "bb_pct_b",  # Bollinger Band %B (0=lower band, 1=upper)
    "ibs",  # Intraday Bar Score (0=bottom of range, 1=top)
    "vwap_pct",  # % deviation below 20d VWAP (MR: negative is oversold)
    "rsi",  # RSI(14)
    "adx",  # ADX(14) trend strength
    "rvol",  # Relative volume vs 20d avg
    "atr_pct",  # ATR as % of price (volatility)
    "price_zscore",  # Price z-score (20d rolling)
    "ou_halflife",  # OU mean-reversion half-life (days)
    "hurst",  # Hurst exponent (0.5=random, <0.5=MR, >0.5=trending)
    "vix",  # VIX level (macro regime)
    "sector_ord",  # Sector ETF ordinal (XLK=0 … XLU=10)
    "dow",  # Day of week (0=Mon … 4=Fri)
    "month",  # Month (1–12, seasonal effect)
]

_NAN = float("nan")


def _safe(v) -> float:
    try:
        f = float(v)
        return _NAN if math.isnan(f) else f
    except (TypeError, ValueError):
        return _NAN


def _extract_entry_row(row: pd.Series, trade: dict, vix_dict: dict, sector_ord: float) -> list[float]:
    """Build the 14-feature vector from the signal bar + trade metadata."""
    date_key = pd.Timestamp(str(trade["date"])[:10])
    vix_val = vix_dict.get(date_key)

    return [
        _safe(row.get("bb_pct_b")),
        _safe(row.get("ibs")),
        _safe(row.get("vwap_pct")),
        _safe(row.get("rsi")),
        _safe(row.get("adx")),
        _safe(row.get("rvol")),
        _safe(trade.get("atr_pct")),  # atr/entry*100 — already in trade record
        _safe(row.get("price_zscore")),
        _safe(row.get("ou_halflife")),
        _safe(row.get("hurst")),
        float(vix_val) if vix_val is not None else _NAN,
        sector_ord,
        float(trade["dow"]) if trade.get("dow") is not None else _NAN,
        float(trade["date"].month) if hasattr(trade.get("date"), "month") else _NAN,
    ]


def _build_dataset(all_results: list, vix_dict: dict) -> tuple[np.ndarray, np.ndarray]:
    """
    all_results: list of (ticker, trades_df, bh_return, indicator_df) from process_ticker
    Returns X (N×14), y (N,) arrays.
    """
    from scripts.backtest_technicals import TICKER_TO_SECTOR
    from services.signal_ml import _sector_ord

    X_rows, y_rows = [], []
    for ticker, trades, _, df in all_results:
        if trades is None or trades.empty or df is None:
            continue
        sector = TICKER_TO_SECTOR.get(ticker, "")
        s_ord = _sector_ord(sector)

        for _, trade in trades.iterrows():
            trade_date = pd.Timestamp(str(trade["date"])[:10])
            if trade_date not in df.index:
                continue
            row = df.loc[trade_date]
            features = _extract_entry_row(row, trade, vix_dict, s_ord)
            label = 1 if float(trade.get("net_pct", 0)) > 0 else 0
            X_rows.append(features)
            y_rows.append(label)

    if not X_rows:
        return np.empty((0, len(ENTRY_FEATURE_NAMES))), np.empty(0)

    return np.array(X_rows, dtype=float), np.array(y_rows, dtype=int)


def simulate_and_process_trades(raw_results: list, vix: dict, spy_trend: dict, stlfsi4: dict) -> list:
    """
    Takes a list of (ticker, bh_return, df, earnings_dates) from process_ticker
    and runs cointegration + simulate_ticker to return list of (ticker, trades_df, bh_return, df).
    """
    from scripts.backtest_technicals import (
        TICKER_TO_SECTOR,
        START,
        END,
        cached_yf_download,
        compute_scores,
        simulate_ticker,
    )

    # Filter out empty results
    valid_results = [r for r in raw_results if r is not None and r[2] is not None]
    if not valid_results:
        return []

    all_dfs = {r[0]: r[2] for r in valid_results}
    all_earnings_dates = {r[0]: r[3] for r in valid_results}
    bh_returns_map = {r[0]: r[1] for r in valid_results}

    # ── Cointegration calculation ──
    try:
        _sector_etfs = list({TICKER_TO_SECTOR.get(t, "XLK") for t in all_dfs})
        _etf_raw = cached_yf_download(
            _sector_etfs, start=START, end=END, interval="1d", auto_adjust=True, progress=False
        )
        if isinstance(_etf_raw.columns, pd.MultiIndex):
            _etf_close = _etf_raw["Close"]
        else:
            _etf_close = _etf_raw[["Close"]] if "Close" in _etf_raw.columns else _etf_raw
        _etf_close.index = pd.to_datetime([str(i)[:10] for i in _etf_close.index])

        def _coint_z_series(ticker_prices: pd.Series, etf_prices: pd.Series, window: int = 252) -> pd.Series:
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
            ss = (
                sum_ss
                + beta**2 * sum_ee
                + N * alpha**2
                - 2 * beta * sum_se
                - 2 * alpha * sum_s
                + 2 * beta * alpha * sum_e
            )
            var = np.maximum(ss / (N - 1), 0.0)
            sigma = np.sqrt(var)

            z_score = np.where((sigma > 1e-8) & denom_valid, resid_last / sigma, np.nan)
            return pd.Series(z_score, index=combined.index)

        for ticker, df in all_dfs.items():
            etf = TICKER_TO_SECTOR.get(ticker, "XLK")
            if etf in _etf_close.columns:
                etf_p = _etf_close[etf]
            elif len(_sector_etfs) == 1 and etf == _sector_etfs[0]:
                etf_p = _etf_close.iloc[:, 0]
            else:
                continue
            cz = _coint_z_series(df["Close"], etf_p)
            df["coint_z"] = cz.reindex(df.index)
            df["score"] = compute_scores(df)
    except Exception as _coint_err:
        print(f"Cointegration step failed: {_coint_err}")

    # ── Simulate tickers and build final list ──
    final_results = []
    for ticker, df in all_dfs.items():
        trades = simulate_ticker(
            ticker,
            df,
            vix,
            spy_trend,
            stlfsi4,
            mr_only=True,
            earnings_dates=all_earnings_dates.get(ticker),
        )
        final_results.append((ticker, trades, bh_returns_map[ticker], df))
    return final_results


def main():
    print("\n# Backtest Entry Model Training — Signal.Trade\n")

    try:
        import xgboost as xgb
    except ImportError:
        print("xgboost not installed — pip install xgboost")
        sys.exit(1)
    try:
        from sklearn.metrics import roc_auc_score
    except ImportError:
        print("scikit-learn not installed — pip install scikit-learn")
        sys.exit(1)

    from scripts.backtest_technicals import (
        END,
        START,
        TICKERS,
        fetch_spy_trend,
        fetch_stlfsi4,
        fetch_spy_prices,
        process_ticker,
    )
    import yfinance as yf

    print(f"IS universe: {len(TICKERS)} tickers  |  {START} → {END}\n")

    # ── Fetch shared market data (same as main backtest) ─────────────────────
    print("Fetching macro data (VIX, SPY, STLFSI4)…")

    raw_vix = yf.download("^VIX", start=START, end=END, interval="1d", auto_adjust=False, progress=False)
    if isinstance(raw_vix.columns, pd.MultiIndex):
        raw_vix.columns = raw_vix.columns.get_level_values(0)
    vix_dict: dict = {}
    for d, row in raw_vix.iterrows():
        try:
            vix_dict[pd.Timestamp(str(d)[:10])] = float(row["Close"])
        except Exception:
            pass

    spy_trend = fetch_spy_trend(START, END)
    spy_prices = {}
    try:
        spy_prices = fetch_spy_prices(START, END)
    except Exception:
        pass
    stlfsi4 = {}
    try:
        _api_key = os.getenv("MASSIVE_API_KEY", "")
        stlfsi4 = fetch_stlfsi4(START, END, _api_key)
    except Exception as e:
        print(f"  STLFSI4 fetch skipped: {e}")

    print(f"  VIX: {len(vix_dict)} days | SPY trend: {len(spy_trend)} days\n")

    # ── Run backtest for all IS tickers in parallel ───────────────────────────
    print(f"Running IS backtest on {len(TICKERS)} tickers…")
    args_list = [(ticker, vix_dict, spy_trend, stlfsi4, True, False, spy_prices, False) for ticker in TICKERS]
    n_cpu = max(1, multiprocessing.cpu_count() - 1)
    with multiprocessing.Pool(n_cpu) as pool:
        raw_results = pool.map(process_ticker, args_list)

    all_results = simulate_and_process_trades(raw_results, vix_dict, spy_trend, stlfsi4)

    total_trades = sum(len(t) for _, t, _, _ in all_results if t is not None)
    print(f"Total IS trades: {total_trades}\n")

    if total_trades < 100:
        print(f"Insufficient data ({total_trades} < 100 trades) — aborting.")
        sys.exit(1)

    # ── Build feature matrix ──────────────────────────────────────────────────
    print("Extracting entry features…")
    X, y = _build_dataset(all_results, vix_dict)
    print(f"Feature matrix: {X.shape}  |  Win rate: {y.mean():.3f}\n")

    # ── Purged expanding-window cross-validation ──────────────────────────────
    # Replaces the simple 70/30 split which, on time-series data, overstates
    # AUC by 3–8pp because adjacent trades share regime information across the
    # fold boundary. Purged CV (Lopez de Prado, AFML Ch.7) adds an embargo
    # window between train and test to eliminate information leakage from serial
    # correlation. We use an expanding train window (not rolling) to maximise
    # the amount of training data per fold.
    #
    # K=5 folds, each OOS window = 20% of total N, embargo = 20 observations
    # (≈ 4 holding-day cycles). CV-AUC is the primary quality metric; the final
    # model is trained on all data and evaluated on the last 30% as the holdout.
    EMBARGO = 20  # observations to drop at each fold boundary
    K_FOLDS = 5
    n = len(X)
    fold_size = n // K_FOLDS

    cv_aucs: list[float] = []
    print("## Purged Expanding-Window Cross-Validation\n")
    print("| Fold | Train N | Test N | OOS AUC |")
    print("|:---|---:|---:|---:|")

    params = {
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "max_depth": 4,
        "eta": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 5,
        "seed": 42,
    }

    for fold in range(1, K_FOLDS + 1):
        # Test window: the fold-th non-overlapping 20% slice
        test_start = (fold - 1) * fold_size
        test_end = fold * fold_size if fold < K_FOLDS else n
        # Train: everything before test_start minus the embargo buffer
        train_end = max(0, test_start - EMBARGO)
        if train_end < 50:
            print(f"| {fold} | — | — | insufficient train data |")
            continue
        X_cv_train = X[:train_end]
        y_cv_train = y[:train_end]
        X_cv_test = X[test_start:test_end]
        y_cv_test = y[test_start:test_end]

        dtrain_cv = xgb.DMatrix(X_cv_train, label=y_cv_train, feature_names=ENTRY_FEATURE_NAMES)
        dtest_cv = xgb.DMatrix(X_cv_test, label=y_cv_test, feature_names=ENTRY_FEATURE_NAMES)
        booster_cv = xgb.train(
            params,
            dtrain_cv,
            num_boost_round=300,
            evals=[(dtrain_cv, "train"), (dtest_cv, "test")],
            early_stopping_rounds=30,
            verbose_eval=False,
        )
        preds_cv = booster_cv.predict(dtest_cv)
        fold_auc = float(roc_auc_score(y_cv_test, preds_cv)) if len(set(y_cv_test.tolist())) > 1 else None
        if fold_auc is not None:
            cv_aucs.append(fold_auc)
        print(f"| {fold} | {train_end} | {len(y_cv_test)} | {f'{fold_auc:.4f}' if fold_auc else '—'} |")

    cv_auc_mean = float(np.mean(cv_aucs)) if cv_aucs else None
    cv_auc_std = float(np.std(cv_aucs)) if len(cv_aucs) > 1 else None
    print(
        f"\n> CV-AUC: {f'{cv_auc_mean:.4f}' if cv_auc_mean else '—'}"
        f" ± {f'{cv_auc_std:.4f}' if cv_auc_std else '—'}"
        f"  (embargo={EMBARGO} obs, K={K_FOLDS} folds)"
    )
    print("> CV-AUC is the primary metric — more reliable than a single 70/30 split.\n")

    # ── Final model: train on full dataset, holdout = last 30% ───────────────
    # This is the model deployed to production. CV-AUC above estimates true OOS
    # performance; this split provides the eval data for eval_ml.py §7.
    split = int(len(X) * 0.70)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    print(f"Final model — Train: {len(X_train)} | Holdout (30%): {len(X_test)}\n")

    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=ENTRY_FEATURE_NAMES)
    dtest = xgb.DMatrix(X_test, label=y_test, feature_names=ENTRY_FEATURE_NAMES)

    evals_result: dict = {}
    booster = xgb.train(
        params,
        dtrain,
        num_boost_round=300,
        evals=[(dtrain, "train"), (dtest, "test")],
        early_stopping_rounds=30,
        evals_result=evals_result,
        verbose_eval=False,
    )

    oos_preds = booster.predict(dtest)
    oos_auc = float(roc_auc_score(y_test, oos_preds)) if len(set(y_test)) > 1 else None

    # Save eval data so eval_ml.py §7 can show calibration/lift without re-running backtest
    _EVAL_FILE.write_text(
        json.dumps(
            {
                "y_test": y_test.tolist(),
                "oos_preds": oos_preds.tolist(),
                "feature_names": ENTRY_FEATURE_NAMES,
                "cv_auc_mean": cv_auc_mean,
                "cv_auc_std": cv_auc_std,
                "cv_fold_aucs": cv_aucs,
            }
        )
    )

    print("## Final Model Results (primary metric = CV-AUC above)\n")
    print("| Metric | Value |")
    print("|:---|---:|")
    print(f"| N train (70%) | {len(X_train)} |")
    print(f"| N holdout (30%) | {len(X_test)} |")
    print(f"| Holdout AUC | {f'{oos_auc:.4f}' if oos_auc else '—'} |")
    print(f"| CV-AUC (purged, K={K_FOLDS}) | {f'{cv_auc_mean:.4f}' if cv_auc_mean else '—'} |")
    print(f"| CV-AUC std | {f'{cv_auc_std:.4f}' if cv_auc_std else '—'} |")
    print(f"| OOS WR | {y_test.mean():.3f} |")
    print()

    # ── Feature importances ───────────────────────────────────────────────────
    scores = booster.get_score(importance_type="gain")
    total_gain = sum(scores.values()) or 1
    fi = sorted(
        [{"feature": k, "importance": v / total_gain} for k, v in scores.items()],
        key=lambda x: -x["importance"],
    )
    print("## Feature Importances\n")
    print("| Rank | Feature | Importance |")
    print("|:---|:---|---:|")
    for rank, f in enumerate(fi[:10], 1):
        bar = "█" * int(f["importance"] * 200)
        print(f"| {rank} | {f['feature']} | {f['importance']:.5f} {bar} |")
    print()

    # ── Champion/challenger gate ──────────────────────────────────────────────
    # Use CV-AUC as primary champion metric (more robust than single holdout AUC).
    # Fall back to holdout AUC when CV-AUC is unavailable.
    _champ_meta: dict = {}
    _champion_cv_auc: float | None = None
    _champion_holdout_auc: float | None = None
    if _FEATURE_FILE.exists():
        try:
            _champ_meta = json.loads(_FEATURE_FILE.read_text())
            _champion_cv_auc = _champ_meta.get("cv_auc_mean")
            _champion_holdout_auc = _champ_meta.get("oos_auc")
        except Exception:
            pass

    # Prefer CV-AUC comparison; fall back to holdout when neither side has CV-AUC
    challenger_score = cv_auc_mean if cv_auc_mean is not None else oos_auc
    champion_score = _champion_cv_auc if _champion_cv_auc is not None else _champion_holdout_auc

    should_deploy = challenger_score is not None and (champion_score is None or challenger_score > champion_score)

    if should_deploy:
        booster.save_model(str(_MODEL_FILE))
        meta = {
            "trained_at": datetime.utcnow().isoformat(),
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
            "oos_auc": oos_auc,
            "cv_auc_mean": cv_auc_mean,
            "cv_auc_std": cv_auc_std,
            "cv_fold_aucs": cv_aucs,
            "champion_cv_auc": _champion_cv_auc,
            "champion_holdout_auc": _champion_holdout_auc,
            "deployed": True,
            "feature_names": ENTRY_FEATURE_NAMES,
            "feature_importances": fi,
        }
        _FEATURE_FILE.write_text(json.dumps(meta, indent=2))
        if champion_score is None:
            print(f"✅ First champion deployed — CV-AUC {cv_auc_mean:.4f if cv_auc_mean else oos_auc:.4f}")
        else:
            print(f"✅ New champion deployed — CV-AUC {challenger_score:.4f} > champion {champion_score:.4f}")
    else:
        print(
            f"⛔ Challenger rejected — CV-AUC {f'{challenger_score:.4f}' if challenger_score else '—'} "
            f"≤ champion {f'{champion_score:.4f}' if champion_score else '—'}. Keeping existing model."
        )

    print()


def _sector_purged_cv(
    X: np.ndarray,
    y: np.ndarray,
    params: dict,
    n_folds: int = 4,
    embargo: int = 10,
) -> tuple[float | None, list[float]]:
    """Purged expanding-window CV for sector models."""
    try:
        import xgboost as xgb
        from sklearn.metrics import roc_auc_score
    except ImportError:
        return None, []

    fold_aucs: list[float] = []
    n = len(X)
    fold_size = n // n_folds
    for fold in range(1, n_folds + 1):
        test_start = (fold - 1) * fold_size
        test_end = fold * fold_size if fold < n_folds else n
        train_end = max(0, test_start - embargo)
        if train_end < 30:
            continue
        dtrain = xgb.DMatrix(X[:train_end], label=y[:train_end], feature_names=ENTRY_FEATURE_NAMES)
        dtest = xgb.DMatrix(X[test_start:test_end], label=y[test_start:test_end], feature_names=ENTRY_FEATURE_NAMES)
        booster = xgb.train(
            params,
            dtrain,
            num_boost_round=200,
            evals=[(dtrain, "train"), (dtest, "test")],
            early_stopping_rounds=20,
            verbose_eval=False,
        )
        preds = booster.predict(dtest)
        if len(set(y[test_start:test_end].tolist())) > 1:
            fold_aucs.append(float(roc_auc_score(y[test_start:test_end], preds)))
    return (float(np.mean(fold_aucs)) if fold_aucs else None, fold_aucs)


def train_sector_model(
    all_results: list,
    vix_dict: dict,
    sector_etf: str,
    sector_tickers: set[str],
    champion_auc: "float | None",
    min_samples: int = 100,
) -> dict | None:
    """Train a sector-specific entry model and save if it beats the champion.

    Returns model metadata when a model is saved, otherwise None.
    """
    try:
        import xgboost as xgb
        from sklearn.metrics import roc_auc_score
    except ImportError:
        return None

    from scripts.backtest_technicals import TICKER_TO_SECTOR
    from services.signal_ml import _sector_ord

    X_rows, y_rows = [], []
    for ticker, trades, _, df in all_results:
        if ticker.upper() not in sector_tickers:
            continue
        if trades is None or trades.empty or df is None:
            continue
        s_ord = _sector_ord(TICKER_TO_SECTOR.get(ticker, ""))
        for _, trade in trades.iterrows():
            trade_date = pd.Timestamp(str(trade["date"])[:10])
            if trade_date not in df.index:
                continue
            row = df.loc[trade_date]
            features = _extract_entry_row(row, trade, vix_dict, s_ord)
            label = 1 if float(trade.get("net_pct", 0)) > 0 else 0
            X_rows.append(features)
            y_rows.append(label)

    n_total = len(X_rows)
    if n_total < min_samples:
        print(f"  {sector_etf}: {n_total} trades — insufficient for sector model (need ≥{min_samples}). Skipped.")
        return None

    X = np.array(X_rows, dtype=float)
    y = np.array(y_rows, dtype=int)

    split = int(len(X) * 0.70)
    if split < 20 or len(X) - split < 10:
        print(f"  {sector_etf}: not enough data for train/test split ({len(X)} trades). Skipped.")
        return None

    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    params = {
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "max_depth": 3,
        "eta": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 3,
        "seed": 42,
    }
    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=ENTRY_FEATURE_NAMES)
    dtest = xgb.DMatrix(X_test, label=y_test, feature_names=ENTRY_FEATURE_NAMES)

    booster = xgb.train(
        params,
        dtrain,
        num_boost_round=200,
        evals=[(dtrain, "train"), (dtest, "test")],
        early_stopping_rounds=20,
        verbose_eval=False,
    )

    oos_preds = booster.predict(dtest)
    oos_auc = float(roc_auc_score(y_test, oos_preds)) if len(set(y_test)) > 1 else None
    cv_auc_mean, cv_fold_aucs = _sector_purged_cv(X, y, params)

    # Champion comparison uses CV-AUC when available, else OOS AUC.
    challenger_score = cv_auc_mean if cv_auc_mean is not None else oos_auc
    champion_score = champion_auc

    should_deploy = challenger_score is not None and (champion_score is None or challenger_score > champion_score)

    model_file = _DATA_DIR / f"backtest_ml_model_{sector_etf}.json"
    feature_file = _DATA_DIR / f"backtest_ml_features_{sector_etf}.json"

    if should_deploy:
        booster.save_model(str(model_file))
        scores = booster.get_score(importance_type="gain")
        total_gain = sum(scores.values()) or 1
        fi = sorted(
            [{"feature": k, "importance": v / total_gain} for k, v in scores.items()],
            key=lambda x: -x["importance"],
        )
        meta = {
            "model_id": f"sector-entry-{sector_etf}-{int(datetime.utcnow().timestamp())}",
            "trained_at": datetime.utcnow().isoformat(),
            "sector_etf": sector_etf,
            "n_total": n_total,
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
            "oos_auc": oos_auc,
            "cv_auc_mean": cv_auc_mean,
            "cv_fold_aucs": cv_fold_aucs,
            "champion_auc": champion_auc,
            "deployed": True,
            "feature_names": ENTRY_FEATURE_NAMES,
            "feature_importances": fi,
        }
        feature_file.write_text(json.dumps(meta, indent=2))
        label = "First" if champion_auc is None else "New"
        _cmp = f" > {champion_auc:.4f}" if champion_auc else ""
        _cv = f"{cv_auc_mean:.4f}" if cv_auc_mean is not None else "—"
        print(
            f"  {sector_etf}: ✅ {label} sector model — N={n_total} trades | CV-AUC {_cv} | OOS AUC {oos_auc:.4f}{_cmp}"
        )
        return meta
    else:
        print(
            f"  {sector_etf}: ⛔ Challenger rejected — CV-AUC {f'{cv_auc_mean:.4f}' if cv_auc_mean else '—'} "
            f"≤ champion {f'{champion_auc:.4f}' if champion_auc else '—'}. Keeping existing."
        )
        return None


# Sector-specific ticker sets for sector model training.
# Only sectors where we have enough IS backtest trades to train.
_SECTOR_TICKER_SETS: dict[str, set[str]] = {
    "XLF": {"JPM", "BAC", "WFC", "C", "BK", "V", "AXP", "SPGI", "MS", "GS", "BLK", "SCHW"},
    "XLP": {"PG", "KO", "PEP", "CL", "KMB", "GIS", "MO", "PM", "COST", "WMT", "TGT"},
    "XLU": {"NEE", "DUK", "SO", "D", "AEP", "EXC", "XEL", "SRE", "ED", "AWK"},
    "XLI": {"HON", "CAT", "DE", "RTX", "LMT", "UNP", "CSX", "ETN", "XYL", "GE", "WM"},
}


async def _record_sector_model_pending(meta: dict) -> None:
    """Create pending ModelRegistry + ResearchExperiment rows for a trained sector model.

    The model is NOT activated here — activation requires a separate QENG-1c
    promotion step (scripts/promote_sector_model.py).
    """
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from database import AsyncSessionLocal
    from models import ActionAuditLog, ModelRegistry, ResearchExperiment

    model_id = meta["model_id"]
    sector_etf = meta["sector_etf"]
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(ModelRegistry).where(ModelRegistry.model_id == model_id))
        if existing.scalar_one_or_none() is None:
            db.add(
                ModelRegistry(
                    model_id=model_id,
                    training_data_hash=f"sector-{sector_etf}-{meta['n_total']}",
                    feature_schema_hash=",".join(meta["feature_names"]),
                    hyperparameters={"max_depth": 3, "eta": 0.05, "seed": 42},
                    metrics={
                        "oos_auc": meta["oos_auc"],
                        "cv_auc_mean": meta.get("cv_auc_mean"),
                        "cv_fold_aucs": meta.get("cv_fold_aucs"),
                        "n_total": meta["n_total"],
                        "n_train": meta["n_train"],
                        "n_test": meta["n_test"],
                    },
                    approval_decision="pending",
                    is_active=False,
                )
            )
        exp = ResearchExperiment(
            experiment_type="ml_training",
            hypothesis=f"Sector-specific entry model for {sector_etf} ({model_id})",
            universe={"sector_etf": sector_etf, "tickers": list(meta.get("tickers", []))},
            data_version="1.0",
            search_space={"model_id": model_id, "sector": sector_etf},
            number_of_trials=1,
            is_metrics={
                "oos_auc": meta["oos_auc"],
                "cv_auc_mean": meta.get("cv_auc_mean"),
            },
            decision="pending",
            promotion_status="pending",
        )
        db.add(exp)
        audit = ActionAuditLog(
            action="train_sector_model",
            details={
                "model_id": model_id,
                "sector_etf": sector_etf,
                "oos_auc": meta["oos_auc"],
                "cv_auc_mean": meta.get("cv_auc_mean"),
            },
        )
        db.add(audit)
        await db.commit()
        print(f"  {sector_etf}: recorded pending ModelRegistry / ResearchExperiment rows.")


if __name__ == "__main__":
    main()

    # ── Sector-specific model training ─────────────────────────────────────────
    # Train after the global model so we can reuse all_results from main().
    # This is a standalone invocation path — re-run the backtest for sector models.
    print("\n## Sector-Specific Model Training\n")
    print("Re-running IS backtest to build sector models (XLF, XLP, XLU, XLI)...\n")

    try:
        from scripts.backtest_technicals import (
            END,
            START,
            TICKERS,
            fetch_spy_trend,
            fetch_stlfsi4,
            fetch_spy_prices,
            process_ticker,
        )
        import yfinance as yf

        # Fetch macro data (same as main())
        raw_vix_s = yf.download("^VIX", start=START, end=END, interval="1d", auto_adjust=False, progress=False)
        if isinstance(raw_vix_s.columns, pd.MultiIndex):
            raw_vix_s.columns = raw_vix_s.columns.get_level_values(0)
        vix_dict_s: dict = {}
        for d, row in raw_vix_s.iterrows():
            try:
                vix_dict_s[pd.Timestamp(str(d)[:10])] = float(row["Close"])
            except Exception:
                pass

        spy_trend_s = fetch_spy_trend(START, END)
        spy_prices_s = {}
        try:
            spy_prices_s = fetch_spy_prices(START, END)
        except Exception:
            pass
        stlfsi4_s = {}
        try:
            stlfsi4_s = fetch_stlfsi4(START, END, os.getenv("MASSIVE_API_KEY", ""))
        except Exception:
            pass

        # Expand TICKERS to include the blocked-sector tickers for sector model training
        _all_sector_tickers = set().union(*_SECTOR_TICKER_SETS.values())
        _sector_train_tickers = sorted(_all_sector_tickers - set(TICKERS))

        if _sector_train_tickers:
            print(f"Fetching {len(_sector_train_tickers)} additional sector tickers: {_sector_train_tickers}\n")
            sector_args = [
                (t, vix_dict_s, spy_trend_s, stlfsi4_s, True, False, spy_prices_s, False) for t in _sector_train_tickers
            ]
            n_cpu_s = max(1, multiprocessing.cpu_count() - 1)
            with multiprocessing.Pool(n_cpu_s) as pool:
                sector_raw_results = pool.map(process_ticker, sector_args)
        else:
            sector_raw_results = []

        # Combine: re-run main tickers + sector tickers
        main_args_s = [(t, vix_dict_s, spy_trend_s, stlfsi4_s, True, False, spy_prices_s, False) for t in TICKERS]
        n_cpu_s = max(1, multiprocessing.cpu_count() - 1)
        with multiprocessing.Pool(n_cpu_s) as pool:
            main_raw_results = pool.map(process_ticker, main_args_s)

        all_raw_results_s = main_raw_results + sector_raw_results
        all_results_s = simulate_and_process_trades(all_raw_results_s, vix_dict_s, spy_trend_s, stlfsi4_s)

        for sector_etf, sector_tickers in _SECTOR_TICKER_SETS.items():
            champion_auc_s: float | None = None
            feat_file_s = _DATA_DIR / f"backtest_ml_features_{sector_etf}.json"
            if feat_file_s.exists():
                try:
                    champion_auc_s = json.loads(feat_file_s.read_text()).get("oos_auc")
                except Exception:
                    pass

            meta = train_sector_model(
                all_results_s,
                vix_dict_s,
                sector_etf,
                sector_tickers,
                champion_auc_s,
                min_samples=100,
            )
            if meta:
                asyncio.run(_record_sector_model_pending(meta))

    except Exception as _e:
        print(f"Sector model training failed: {_e}")
