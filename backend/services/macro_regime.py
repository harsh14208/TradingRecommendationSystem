"""
Macro Regime Markov-Switching Model

Implements a 2-state Gaussian HMM on macro features to identify market regimes
(Bull / Bear) and detect transition risk *before* it shows up in moving averages.

States:
  0 = Risk-On  (low VIX, positive momentum, steep yield curve)
  1 = Risk-Off (high VIX, negative momentum, flat/inverted curve)

Algorithm: Baum-Welch EM (pure numpy — no external ML dependency)

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
from typing import Optional

import numpy as np

log = logging.getLogger("signal.trade.macro_regime")

# ── Cache ────────────────────────────────────────────────────────────────────
_cache: dict = {"result": None, "ts": 0.0}
_CACHE_TTL = 3600  # re-fit once per hour (data moves slowly)

# ── HMM helpers (pure numpy) ─────────────────────────────────────────────────


def _safe_chol(M: np.ndarray) -> np.ndarray:
    """Cholesky with jitter to handle near-singular matrices."""
    for jitter in (0.0, 1e-6, 1e-4, 1e-2):
        try:
            return np.linalg.cholesky(M + np.eye(M.shape[0]) * jitter)
        except np.linalg.LinAlgError:
            continue
    return np.eye(M.shape[0])


def _log_gauss(x: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> float:
    """Log probability under multivariate Gaussian."""
    d = len(mean)
    L = _safe_chol(cov)
    diff = x - mean
    v = np.linalg.solve(L, diff)
    log_det = 2.0 * np.sum(np.log(np.maximum(np.diag(L), 1e-10)))
    return -0.5 * (d * np.log(2.0 * np.pi) + log_det + float(v @ v))


def _forward_scaled(
    X: np.ndarray, pi: np.ndarray, A: np.ndarray, means: list, covs: list
) -> tuple[np.ndarray, np.ndarray]:
    T, K = len(X), len(pi)
    alpha = np.zeros((T, K))
    scales = np.zeros(T)

    log_b = np.array([[_log_gauss(X[t], means[k], covs[k]) for k in range(K)] for t in range(T)])
    b = np.exp(log_b - log_b.max(axis=1, keepdims=True))  # stable exp

    alpha[0] = pi * b[0]
    scales[0] = alpha[0].sum() or 1e-300
    alpha[0] /= scales[0]

    for t in range(1, T):
        alpha[t] = (alpha[t - 1] @ A) * b[t]
        scales[t] = alpha[t].sum() or 1e-300
        alpha[t] /= scales[t]

    return alpha, scales


def _backward_scaled(X: np.ndarray, A: np.ndarray, means: list, covs: list, scales: np.ndarray) -> np.ndarray:
    T, K = len(X), A.shape[0]
    beta = np.ones((T, K))

    log_b = np.array([[_log_gauss(X[t], means[k], covs[k]) for k in range(K)] for t in range(T)])
    b = np.exp(log_b - log_b.max(axis=1, keepdims=True))

    for t in range(T - 2, -1, -1):
        beta[t] = (A * b[t + 1][np.newaxis, :] * beta[t + 1][np.newaxis, :]).sum(axis=1)
        beta[t] /= scales[t + 1] or 1e-300

    return beta


def _fit_hmm(X: np.ndarray, n_states: int = 2, n_iter: int = 30) -> dict:
    """
    Fit a Gaussian HMM via Baum-Welch EM.
    Returns dict with pi, A, means, covs.
    """
    T, D = X.shape
    K = n_states
    rng = np.random.default_rng(42)

    # ── Initialise with deterministic percentile split on first feature (VIX) ─
    pi = np.ones(K) / K
    A = np.full((K, K), 0.05 / (K - 1))
    np.fill_diagonal(A, 0.95)  # high self-transition — regimes are sticky

    sorted_idx = np.argsort(X[:, 0])
    split = T // K
    means = [X[sorted_idx[k * split : (k + 1) * split]].mean(axis=0) for k in range(K)]
    covs = [np.cov(X[sorted_idx[k * split : (k + 1) * split]].T) + np.eye(D) * 1e-4 for k in range(K)]
    # Ensure 2D covs
    covs = [c if c.ndim == 2 else np.diag(np.atleast_1d(c)) for c in covs]

    for iteration in range(n_iter):
        # ── E-step ────────────────────────────────────────────────────────────
        alpha, scales = _forward_scaled(X, pi, A, means, covs)
        beta = _backward_scaled(X, A, means, covs, scales)

        gamma = alpha * beta
        row_sums = gamma.sum(axis=1, keepdims=True)
        gamma /= np.where(row_sums > 0, row_sums, 1.0)

        log_b = np.array([[_log_gauss(X[t], means[k], covs[k]) for k in range(K)] for t in range(T)])
        b = np.exp(log_b - log_b.max(axis=1, keepdims=True))

        xi = np.zeros((T - 1, K, K))
        for t in range(T - 1):
            xi[t] = alpha[t][:, np.newaxis] * A * b[t + 1][np.newaxis, :] * beta[t + 1][np.newaxis, :]
            xi_sum = xi[t].sum()
            if xi_sum > 0:
                xi[t] /= xi_sum

        # ── M-step ────────────────────────────────────────────────────────────
        pi = gamma[0]
        pi /= pi.sum() or 1.0

        A_new = xi.sum(axis=0)
        row_sums = A_new.sum(axis=1, keepdims=True)
        A = A_new / np.where(row_sums > 0, row_sums, 1.0)

        gamma_sum = gamma.sum(axis=0)
        for k in range(K):
            g = gamma[:, k]
            gsum = g.sum() or 1.0
            means[k] = (g[:, np.newaxis] * X).sum(axis=0) / gsum
            diff = X - means[k]
            covs[k] = (g[:, np.newaxis, np.newaxis] * diff[:, :, np.newaxis] * diff[:, np.newaxis, :]).sum(
                axis=0
            ) / gsum
            covs[k] += np.eye(D) * 1e-4  # numerical jitter

    return {"pi": pi, "A": A, "means": means, "covs": covs}


def _viterbi(X: np.ndarray, pi: np.ndarray, A: np.ndarray, means: list, covs: list) -> tuple[np.ndarray, np.ndarray]:
    """Viterbi decode — returns (state_seq, state_probs)."""
    T, K = len(X), len(pi)
    log_b = np.array([[_log_gauss(X[t], means[k], covs[k]) for k in range(K)] for t in range(T)])
    log_A = np.log(A + 1e-300)
    log_pi = np.log(pi + 1e-300)

    delta = np.full((T, K), -np.inf)
    psi = np.zeros((T, K), dtype=int)

    delta[0] = log_pi + log_b[0]
    for t in range(1, T):
        for k in range(K):
            scores = delta[t - 1] + log_A[:, k]
            psi[t, k] = scores.argmax()
            delta[t, k] = scores[psi[t, k]] + log_b[t, k]

    path = np.zeros(T, dtype=int)
    path[-1] = delta[-1].argmax()
    for t in range(T - 2, -1, -1):
        path[t] = psi[t + 1, path[t + 1]]

    # Soft probabilities via final alpha (smoothed posteriors)
    alpha, _ = _forward_scaled(X, pi, A, means, covs)
    return path, alpha


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
        tnx_c = tnx["Close"].astype(float).reindex(idx).ffill().bfill()
        irx_c = irx["Close"].astype(float).reindex(idx).ffill().bfill()
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

        # Fit 2-state HMM
        hmm = await asyncio.to_thread(_fit_hmm, X_train, 2, 25)

        # Decode full sequence
        path, alpha = _viterbi(X_train, hmm["pi"], hmm["A"], hmm["means"], hmm["covs"])

        # ── Identify which state is "bull" (lower VIX mean = risk-on) ─────────
        # State with lower VIX feature mean = risk-on = bull
        vix_means = [hmm["means"][k][0] for k in range(2)]
        bull_state = int(np.argmin(vix_means))
        bear_state = 1 - bull_state

        current_path = int(path[-1])
        current_probs = alpha[-1]  # posterior at last observation
        bull_prob = float(current_probs[bull_state])
        bear_prob = float(current_probs[bear_state])

        # ── Transition risk: P(state changes at t+1) ─────────────────────────
        # = 1 - A[current_state, current_state]
        transition_risk = float(1.0 - hmm["A"][current_path, current_path])

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
            "model": "2-state Gaussian HMM (Baum-Welch)",
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
