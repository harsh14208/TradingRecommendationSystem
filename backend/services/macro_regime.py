"""
Macro Regime Markov-Switching Model

Implements a 2-state Gaussian HMM on macro features to identify market regimes
(Bull / Bear) and detect transition risk *before* it shows up in moving averages.

States:
  0 = Risk-On  (low VIX, positive momentum, steep yield curve)
  1 = Risk-Off (high VIX, negative momentum, flat/inverted curve)

Algorithm: 2-state Gaussian HMM via hmmlearn (tested Baum-Welch fit + Viterbi
decode). Replaced the prior hand-rolled numpy EM 2026-06-09 — see CLAUDE.md.

Output per scan:
  {
    "regime":          "bull" | "bear" | "transition",
    "bull_prob":       float,   # P(risk-on  | last 252 obs)
    "bear_prob":       float,   # P(risk-off | last 252 obs)
    "transition_risk": float,   # P(state change at t+1)
    "vix_z":           float,   # VIX z-score vs 252-day mean
    "features":        {...},   # raw feature values used
  }
"""

import asyncio
import logging
import time
import warnings
from typing import Optional

import numpy as np

log = logging.getLogger("signal.trade.macro_regime")


def _to_tz_naive(index):
    """Strip tz from a DatetimeIndex so Polygon (tz-aware) and yfinance (tz-naive)
    histories can be aligned. A no-op on already-naive indexes."""
    if getattr(index, "tz", None) is not None:
        return index.tz_localize(None)
    return index


# ── Cache ────────────────────────────────────────────────────────────────────
_cache: dict = {"result": None, "ts": 0.0}
_CACHE_TTL = 3600  # re-fit once per hour (data moves slowly)

# ── HMM fit + decode (hmmlearn) ──────────────────────────────────────────────


def _fit_and_decode(X: np.ndarray, n_states: int = 2, n_iter: int = 25) -> dict:
    """Fit a Gaussian HMM and decode the Viterbi path + smoothed posteriors.

    Uses hmmlearn's GaussianHMM (tested Baum-Welch + forward-backward) instead
    of a hand-rolled EM. A sticky transition prior (high self-transition) keeps
    regimes from flickering; the fixed random_state makes hourly refits
    reproducible so the bull/bear label is stable across scans.

    Returns dict with: path, posteriors, means, transmat.
    """
    from hmmlearn.hmm import GaussianHMM

    model = GaussianHMM(
        n_components=n_states,
        covariance_type="full",
        n_iter=n_iter,
        tol=1e-4,
        random_state=42,
        init_params="mc",  # init means + covars from data…
        params="stmc",  # …but train all of startprob/transmat/means/covars
        min_covar=1e-4,
    )
    # Sticky regime prior (regimes persist) as the EM starting point.
    model.startprob_ = np.full(n_states, 1.0 / n_states)
    transmat = np.full((n_states, n_states), 0.05 / max(n_states - 1, 1))
    np.fill_diagonal(transmat, 0.95)
    model.transmat_ = transmat

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # silence non-convergence chatter on noisy windows
        model.fit(X)
        path = model.predict(X)  # Viterbi
        posteriors = model.predict_proba(X)  # smoothed state probabilities

    return {
        "path": np.asarray(path, dtype=int),
        "posteriors": np.asarray(posteriors, dtype=float),
        "means": np.asarray(model.means_, dtype=float),
        "transmat": np.asarray(model.transmat_, dtype=float),
    }


# ── Feature engineering ───────────────────────────────────────────────────────


async def _build_feature_matrix() -> Optional[np.ndarray]:
    """
    Fetch 252 days of macro data and build a 4-feature observation matrix.
    Features (all normalised to unit scale):
      0: VIX level           — fear gauge
      1: SPY 20-day return   — price momentum
      2: 10Y-2Y spread       — yield curve shape (carry/recession signal)
      3: SPY 30-day realised vol — market turbulence
    """
    from services.market_data import get_histories_batch

    try:
        hists = await get_histories_batch(["^VIX", "SPY", "^TNX", "^IRX"], period="2y", interval="1d")
    except Exception:
        hists = {}

    spy = hists.get("SPY")
    vix = hists.get("^VIX")
    tnx = hists.get("^TNX")  # 10Y yield
    irx = hists.get("^IRX")  # 3M yield (proxy for 2Y)

    if spy is None or vix is None or spy.empty or vix.empty or len(spy) < 30:
        return None

    closes_spy = spy["Close"].astype(float)
    closes_vix = vix["Close"].astype(float)

    # Drop timezone before aligning: SPY history is tz-aware (Polygon, America/New_York)
    # while ^VIX is tz-naive (yfinance), so a raw index.intersection() comes back empty
    # even on identical calendar dates — which silently forces the HMM into fallback.
    closes_spy.index = _to_tz_naive(closes_spy.index)
    closes_vix.index = _to_tz_naive(closes_vix.index)

    # Align on common index
    idx = closes_spy.index.intersection(closes_vix.index)
    if len(idx) < 30:
        return None

    spy_c = closes_spy.reindex(idx).ffill()
    vix_c = closes_vix.reindex(idx).ffill()

    # Feature 0: VIX level (raw, normalised later)
    f_vix = vix_c.values

    # Feature 1: 20-day return on SPY
    spy_ret = spy_c.pct_change(20).fillna(0).values

    # Feature 2: yield curve slope (10Y - 3M)
    if tnx is not None and irx is not None and not tnx.empty and not irx.empty:
        tnx_c = tnx["Close"].astype(float)
        irx_c = irx["Close"].astype(float)
        tnx_c.index = _to_tz_naive(tnx_c.index)
        irx_c.index = _to_tz_naive(irx_c.index)
        tnx_c = tnx_c.reindex(idx).ffill().bfill()
        irx_c = irx_c.reindex(idx).ffill().bfill()
        f_curve = (tnx_c - irx_c).values
    else:
        f_curve = np.zeros(len(idx))

    # Feature 3: 30-day realised vol of SPY
    spy_daily_ret = spy_c.pct_change().fillna(0)
    f_rvol = spy_daily_ret.rolling(30).std().fillna(spy_daily_ret.std()).values * np.sqrt(252)

    X = np.column_stack([f_vix, spy_ret, f_curve, f_rvol])

    # Normalise each feature to zero-mean, unit-variance (using training set stats)
    means = X.mean(axis=0)
    stds = X.std(axis=0)
    stds[stds < 1e-6] = 1.0
    X_norm = (X - means) / stds

    return X_norm, means, stds, X[-1]  # return raw last obs too


# ── Public API ────────────────────────────────────────────────────────────────


async def get_macro_regime() -> dict:
    """
    Fit HMM on trailing 252 days of macro features.
    Returns regime label, probabilities, and transition risk.
    Results are cached for 1 hour.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _CACHE_TTL:
        return _cache["result"]

    log.info("[macro_regime] Fitting HMM on macro features…")
    try:
        feature_result = await _build_feature_matrix()
        if feature_result is None:
            return _fallback_regime()

        X_norm, feat_means, feat_stds, last_raw = feature_result
        T = len(X_norm)

        # Limit training window to last 252 trading days
        X_train = X_norm[-252:] if T > 252 else X_norm

        # Fit 2-state HMM + decode (hmmlearn) off the event loop.
        hmm = await asyncio.to_thread(_fit_and_decode, X_train, 2, 25)
        path = hmm["path"]
        posteriors = hmm["posteriors"]

        # ── Identify which state is "bull" (lower VIX mean = risk-on) ─────────
        vix_means = [float(hmm["means"][k][0]) for k in range(2)]
        bull_state = int(np.argmin(vix_means))
        bear_state = 1 - bull_state

        current_path = int(path[-1])
        current_probs = posteriors[-1]  # posterior at last observation
        bull_prob = float(current_probs[bull_state])
        bear_prob = float(current_probs[bear_state])

        # ── Transition risk: P(state changes at t+1) = 1 - A[s, s] ───────────
        transition_risk = float(1.0 - hmm["transmat"][current_path, current_path])

        # ── Regime label with hysteresis (transition zone = 40%–60%) ─────────
        if bull_prob >= 0.60:
            regime = "bull"
        elif bear_prob >= 0.60:
            regime = "bear"
        else:
            regime = "transition"

        # ── VIX z-score (raw, unnormalised) ───────────────────────────────────
        vix_raw = last_raw[0]
        vix_mean = feat_means[0]
        vix_std = feat_stds[0]
        vix_z = float((vix_raw - vix_mean) / (vix_std or 1.0))

        # ── Recent regime sequence (last 10 days for trend) ───────────────────
        recent = ["bull" if s == bull_state else "bear" for s in path[-10:]]
        regime_streak = sum(1 for s in reversed(recent) if s == recent[-1])

        result = {
            "regime": regime,
            "bull_prob": round(bull_prob, 3),
            "bear_prob": round(bear_prob, 3),
            "transition_risk": round(transition_risk, 3),
            "vix_z": round(vix_z, 2),
            "regime_streak_days": regime_streak,
            "recent_regimes": recent,
            "features": {
                "vix": round(float(vix_raw), 1),
                "spy_ret_20d": round(float(last_raw[1]) * 100, 2),
                "yield_curve": round(float(last_raw[2]), 2),
                "rvol_30d": round(float(last_raw[3]) * 100, 2),
            },
            "model": "2-state Gaussian HMM (hmmlearn)",
            "train_obs": len(X_train),
        }

        _cache["result"] = result
        _cache["ts"] = now
        log.info(
            f"[macro_regime] Regime={regime} bull_p={bull_prob:.2f} bear_p={bear_prob:.2f} "
            f"trans_risk={transition_risk:.2f} VIX_z={vix_z:.2f}"
        )
        return result

    except Exception as e:
        log.error(f"[macro_regime] HMM failed: {e}", exc_info=True)
        return _fallback_regime()


def _fallback_regime() -> dict:
    """Rule-based fallback when data is unavailable."""
    return {
        "regime": "unknown",
        "bull_prob": 0.5,
        "bear_prob": 0.5,
        "transition_risk": 0.1,
        "vix_z": 0.0,
        "regime_streak_days": 0,
        "recent_regimes": [],
        "features": {},
        "model": "fallback (no data)",
        "train_obs": 0,
    }


def invalidate_cache():
    """Force refitting on next call (call after major macro event)."""
    _cache["ts"] = 0.0
