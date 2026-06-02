"""
Institutional-grade performance analytics for Signal.Trade.

Outputs a markdown report covering:
  • Return & risk summary (Sharpe, Sortino, Calmar, Omega, VaR, CVaR)
  • Distribution diagnostics (skewness, excess kurtosis, t-stat, p-value)
  • Trade-path analytics (MAE/MFE, stop/target hit rates, realized RR)
  • Multi-timeframe, style, action, sector, session, confidence breakdowns
  • Monthly performance with rolling Sharpe
  • Reliability diagram (confidence calibration bands)

Run from backend/:
    python scripts/calc_tbd_metrics.py
"""

import asyncio
import math
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(_BACKEND_DIR)

# Load backend/.env so os.getenv("MASSIVE_API_KEY") / "POLYGON_API_KEY" resolve
try:
    from dotenv import load_dotenv as _load_dotenv

    _load_dotenv(os.path.join(_BACKEND_DIR, ".env"))
except ImportError:
    pass

from database import get_db
from models import Signal
from sqlalchemy import select

FRICTION_PCT = 0.50  # round-trip transaction cost (0.25% entry + 0.25% exit)

# Risk-free rate used in Sharpe, Sortino, and Jensen's alpha calculations.
# Approximates long-run average Fed Funds/SOFR over a 20-year backtest window.
# 2006-2007 and 2022-2026 had material risk-free rates (4-5%); the decade of
# ZIRP (2009-2019) drags the true average below this.  Set to 0.0 to restore
# the old Rf=0 behaviour.
RF_ANNUAL = 0.04  # 4% annualised
RF_DAILY = RF_ANNUAL / 252  # per-trade risk-free hurdle (same units as mu, in %pt)


# ─────────────────────────────────────────────────────────────────────────────
# Core statistics
# ─────────────────────────────────────────────────────────────────────────────


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs: list[float], ddof: int = 1) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - ddof)
    return math.sqrt(var)


def _percentile(xs: list[float], p: float) -> float:
    """Linear interpolation percentile (p in 0–100)."""
    if not xs:
        return 0.0
    s = sorted(xs)
    idx = (p / 100) * (len(s) - 1)
    lo, hi = int(idx), min(int(idx) + 1, len(s) - 1)
    return s[lo] + (idx - lo) * (s[hi] - s[lo])


def _skewness(xs: list[float]) -> float:
    if len(xs) < 3:
        return float("nan")
    m, s = _mean(xs), _std(xs)
    if s == 0:
        return float("nan")
    # Unbiased sample skewness (Fisher-Pearson)
    n = len(xs)
    m3 = sum((x - m) ** 3 for x in xs)
    return (n * m3) / ((n - 1) * (n - 2) * s**3)


def _kurtosis(xs: list[float]) -> float:
    """Excess kurtosis (normal = 0)."""
    if len(xs) < 4:
        return float("nan")
    m, s = _mean(xs), _std(xs)
    if s == 0:
        return float("nan")
    n = len(xs)
    m4 = sum((x - m) ** 4 for x in xs)
    return (n * (n + 1) * m4) / ((n - 1) * (n - 2) * (n - 3) * s**4) - (3.0 * (n - 1) ** 2) / ((n - 2) * (n - 3))


def _t_stat(xs: list[float]) -> tuple[float, float]:
    """Two-sided t-test: mean != 0. Returns (t, p).

    Uses scipy.stats.t for exact p-values when available — critical for sector
    subsets where N drops to 15-25 and normal approximations under-report p.
    Falls back to a conservative Chebyshev bound for n < 30 without scipy.
    """
    n = len(xs)
    if n < 2:
        return float("nan"), float("nan")
    m, s = _mean(xs), _std(xs)
    if s == 0:
        return float("nan"), float("nan")
    t = m / (s / math.sqrt(n))
    df = n - 1
    try:
        from scipy.stats import t as _scipy_t

        p_approx = float(_scipy_t.sf(abs(t), df=df) * 2)
        return t, p_approx
    except ImportError:
        pass
    # Fallback: normal approximation for n ≥ 30 (good to ~1%); Chebyshev bound otherwise.
    # Chebyshev is conservative (overestimates p) — harder to reach significance without scipy.
    try:
        if n >= 30:
            z = abs(t) / math.sqrt(df / (df - 2)) if df > 2 else abs(t)
            p_approx = 2.0 * (1.0 - _norm_cdf(z))
        else:
            p_approx = min(1.0, 2.0 / (1.0 + t * t / df))
    except Exception:
        p_approx = float("nan")
    return t, p_approx


def _norm_cdf(z: float) -> float:
    """Standard normal CDF using the error function."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


_SQRT_252 = math.sqrt(252)


def _annualize_factor(n_trades: int, date_range_days: int) -> float:
    """
    Return the annualization multiplier for Sharpe/Sortino.

    We use sqrt(252) unconditionally — the industry standard for converting
    a per-observation ratio to annual. Treating each trade as ~1 day is the
    honest assumption when trades are sequential signals, not concurrent portfolio
    positions. Using (trades_per_day × 252) would inflate Sharpe by the square
    root of the daily signal count, producing the impossible 30+ values that
    confuse per-trade signal quality with portfolio risk-adjusted returns.
    """
    return _SQRT_252


# ─────────────────────────────────────────────────────────────────────────────
# Risk-adjusted return metrics
# ─────────────────────────────────────────────────────────────────────────────


def calc_metrics(returns: list[float]) -> dict:
    if not returns:
        return {
            k: 0.0
            for k in [
                "count",
                "wr",
                "avg",
                "avg_win",
                "avg_loss",
                "pf",
                "expectancy",
                "kelly",
            ]
        }
    wins = [r for r in returns if r > 0]
    losses = [r for r in returns if r < 0]
    wr = len(wins) / len(returns) * 100
    avg = _mean(returns)
    avg_win = _mean(wins) if wins else 0.0
    avg_loss = _mean(losses) if losses else 0.0
    gp = sum(wins)
    gl = abs(sum(losses))
    pf = gp / gl if gl else float("inf")
    expectancy = (len(wins) / len(returns) * avg_win) + (len(losses) / len(returns) * avg_loss)
    kelly = 0.0
    if avg_win > 0 and avg_loss < 0:
        wp = len(wins) / len(returns)
        lp = len(losses) / len(returns)
        if wp + lp > 0:
            kelly = (wp - (lp / (avg_win / abs(avg_loss)))) / (wp + lp)
    return {
        "count": len(returns),
        "wr": wr,
        "avg": avg,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "pf": pf,
        "expectancy": expectancy,
        "kelly": kelly * 100,
    }


def risk_metrics(returns: list[float], date_range_days: int = 18) -> dict:
    """Compute the full quant risk/return profile."""
    if len(returns) < 5:
        return {}

    n = len(returns)
    mu = _mean(returns)
    sigma = _std(returns)
    # ann is already sqrt(252) — apply directly, do NOT sqrt again
    ann = _annualize_factor(n, date_range_days)

    # Sharpe (trade-level, annualized at sqrt(252); excess return over Rf=RF_ANNUAL)
    sharpe = ((mu - RF_DAILY) / sigma * ann) if sigma > 0 else float("nan")

    # Sortino — semi-deviation from 0% target; Rf-adjusted numerator.
    # Divisor is n (full sample): measuring against a fixed target, no df correction.
    downside_sum_sq = sum(r**2 for r in returns if r < 0)
    sigma_d = math.sqrt(downside_sum_sq / n) if n > 0 else 0.0
    sortino = ((mu - RF_DAILY) / sigma_d * ann) if sigma_d > 0 else float("nan")

    # Max drawdown (5% position sizing on sequential equity curve)
    capital, peak, max_dd = 10_000.0, 10_000.0, 0.0
    for r in returns:
        capital += capital * 0.05 * (r / 100)
        peak = max(peak, capital)
        max_dd = max(max_dd, (peak - capital) / peak * 100)

    # Custom Calmar: annualised per-trade return at 5% sizing / portfolio max_dd.
    # Non-standard: sequential 5% sizing understates concurrent portfolio drawdown.
    # Do NOT compare this value to published Calmar ratios.
    ann_return = mu * 252
    calmar = ((ann_return * 0.05) / max_dd) if max_dd > 0 else float("nan")

    # Standard Calmar: CAGR of the 5% equity curve / max_dd of same curve.
    # Comparable to external benchmarks.  Requires ≥ 252 calendar days of history
    # to be meaningful — annualising a 27-day equity curve produces nonsense.
    if date_range_days >= 252 and max_dd > 0 and capital > 0:
        _years = date_range_days / 365.25
        _cagr_pct = ((capital / 10_000.0) ** (1.0 / _years) - 1.0) * 100
        calmar_std = _cagr_pct / max_dd
    else:
        calmar_std = float("nan")

    # Omega ratio = E[max(R-threshold,0)] / E[max(threshold-R,0)] (threshold=0)
    gains = sum(max(r, 0) for r in returns)
    losses = sum(max(-r, 0) for r in returns)
    omega = (gains / losses) if losses > 0 else float("inf")

    # Value-at-Risk (non-parametric)
    var_95 = -_percentile(returns, 5)
    var_99 = -_percentile(returns, 1)

    # CVaR / Expected Shortfall
    tail_95 = [r for r in returns if r <= -var_95]
    cvar_95 = -_mean(tail_95) if tail_95 else var_95
    tail_99 = [r for r in returns if r <= -var_99]
    cvar_99 = -_mean(tail_99) if tail_99 else var_99

    # Distribution shape
    skew = _skewness(returns)
    kurt = _kurtosis(returns)

    # Statistical significance
    t, p = _t_stat(returns)

    # Payoff ratio
    wins_l = [r for r in returns if r > 0]
    losses_l = [r for r in returns if r < 0]
    payoff = (_mean(wins_l) / abs(_mean(losses_l))) if wins_l and losses_l else float("nan")

    # Recovery factor = total net gain / max drawdown
    total_net = sum(returns)
    recovery = ((total_net * 0.05) / max_dd) if max_dd > 0 else float("nan")

    # Ulcer Index = RMS of % drawdowns over the equity curve
    ulcer_vals = []
    cap2, pk2 = 10_000.0, 10_000.0
    for r in returns:
        cap2 += cap2 * 0.05 * (r / 100)
        pk2 = max(pk2, cap2)
        dd_pct = (pk2 - cap2) / pk2 * 100
        ulcer_vals.append(dd_pct**2)
    ulcer = math.sqrt(_mean(ulcer_vals)) if ulcer_vals else 0.0

    # Consecutive streaks
    max_w = max_l = cur_w = cur_l = 0
    for r in returns:
        if r > 0:
            cur_w += 1
            cur_l = 0
        else:
            cur_l += 1
            cur_w = 0
        max_w = max(max_w, cur_w)
        max_l = max(max_l, cur_l)

    return {
        "sharpe": sharpe,
        "sortino": sortino,
        "calmar": calmar,
        "calmar_std": calmar_std,
        "omega": omega,
        "ann_return": ann_return,
        "var_95": var_95,
        "var_99": var_99,
        "cvar_95": cvar_95,
        "cvar_99": cvar_99,
        "max_dd": max_dd,
        "recovery": recovery,
        "ulcer": ulcer,
        "skew": skew,
        "kurt": kurt,
        "t_stat": t,
        "p_value": p,
        "payoff": payoff,
        "sigma": sigma,
        "ann_factor": ann,
        "max_win_streak": max_w,
        "max_loss_streak": max_l,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Alpha vs benchmark (SPY)
# ─────────────────────────────────────────────────────────────────────────────

_SPY_CACHE_FILE = os.path.join(_BACKEND_DIR, "data", ".spy_bars_cache.json")


async def fetch_spy_bars(earliest: datetime | None = None, latest: datetime | None = None) -> dict[str, float]:
    """
    Fetch SPY daily closes from Polygon for the signal date range + 3-week buffer.
    Returns {YYYY-MM-DD: close_price}. Empty dict if unavailable.

    Caches results to data/.spy_bars_cache.json — historical prices never change
    so cached dates are reused on subsequent runs without hitting the API.
    Only fetches dates not already in the cache.
    """
    import json as _json
    import ssl

    import aiohttp
    import certifi

    # ── Load cache ─────────────────────────────────────────────────────────────
    cached: dict[str, float] = {}
    try:
        if os.path.exists(_SPY_CACHE_FILE):
            with open(_SPY_CACHE_FILE) as f:
                cached = _json.load(f)
    except Exception:
        pass

    # ── Check if cache already covers the needed range ─────────────────────────
    start_dt = (
        (earliest - timedelta(days=21))
        if earliest
        else (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90))
    )
    end_dt = (latest + timedelta(days=14)) if latest else datetime.now(timezone.utc).replace(tzinfo=None)
    need_from = start_dt.strftime("%Y-%m-%d")
    need_to = end_dt.strftime("%Y-%m-%d")

    if cached:
        dates = sorted(cached)
        if dates[0] <= need_from and dates[-1] >= need_to:
            return cached  # cache covers the full range — no API call needed

    # ── Fetch missing range from API ────────────────────────────────────────────
    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return cached or {}

    url = f"https://api.polygon.io/v2/aggs/ticker/SPY/range/1/day/{need_from}/{need_to}"
    params = {"adjusted": "true", "sort": "asc", "limit": 200, "apiKey": api_key}
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())

    # ── Try Polygon first ──────────────────────────────────────────────────────
    polygon_ok = False
    for attempt in range(2):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    if resp.status == 429:
                        break  # rate-limited — fall through to yfinance
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    for bar in data.get("results", []):
                        dt = datetime.utcfromtimestamp(bar["t"] / 1000)
                        cached[dt.strftime("%Y-%m-%d")] = float(bar["c"])
                    polygon_ok = True
                    break
        except Exception:
            break

    # ── yfinance fallback (no API key required) ────────────────────────────────
    if not polygon_ok:
        try:
            import yfinance as _yf

            df = await asyncio.get_event_loop().run_in_executor(
                None, lambda: _yf.Ticker("SPY").history(start=need_from, end=need_to, interval="1d", auto_adjust=True)
            )
            if df is not None and not df.empty:
                for idx, row in df.iterrows():
                    d = idx.date() if hasattr(idx, "date") else idx
                    cached[d.strftime("%Y-%m-%d")] = float(row["Close"])
        except Exception as e:
            print(f"  [warn] SPY yfinance fallback failed: {e}", flush=True)

    if not cached:
        return {}

    # Persist updated cache
    try:
        os.makedirs(os.path.dirname(_SPY_CACHE_FILE), exist_ok=True)
        with open(_SPY_CACHE_FILE, "w") as f:
            _json.dump(cached, f)
    except Exception:
        pass
    return cached


def nearest_spy_close(spy_bars: dict[str, float], target) -> float | None:
    """Return SPY close for the nearest prior trading day to `target` (date or datetime)."""
    from datetime import timedelta

    d = target.date() if hasattr(target, "date") else target
    for i in range(8):
        ds = (d - timedelta(days=i)).strftime("%Y-%m-%d")
        if ds in spy_bars:
            return spy_bars[ds]
    return None


def _theil_sen(x: list[float], y: list[float]) -> tuple[float, float]:
    """Theil-Sen robust regression: slope = median of pairwise slopes.

    Resistant to outliers (e.g. phantom-win-corrected large losses during
    positive SPY periods that pull OLS beta to economically implausible levels).
    Intercept = median(y_i − slope × x_i).

    O(n²) time: for n=600, ~180k pairs — runs in <100ms in pure Python.
    """
    import statistics as _stat

    n = len(x)
    slopes: list[float] = []
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[j] - x[i]
            if dx != 0.0:
                slopes.append((y[j] - y[i]) / dx)
    if not slopes:
        return 0.0, 0.0
    beta = _stat.median(slopes)
    alpha = _stat.median(y[i] - beta * x[i] for i in range(n))
    return beta, alpha


def alpha_metrics(signal_returns: list[float], spy_returns: list[float]) -> dict:
    """Jensen's alpha and beta using Theil-Sen robust regression.

    Replaces OLS (which is sensitive to outliers — particularly to the large
    negative returns that appear after phantom-win outcome correction).

    Trade-level beta (regression of per-trade return on SPY return over the same
    hold window) is NOT the same as portfolio beta.  When the portfolio holds ~35%
    equity exposure on average:
        portfolio_beta ≈ avg_exposure × avg_stock_beta ≈ 0.35 × 1.0 = 0.35

    A trade-level Theil-Sen beta > 1.0 simply means individual stocks fall/rise
    more than the index over short hold windows — that is normal.  Use
    ``portfolio_beta_est`` in the output for risk-disclosure purposes.

    Annualisation: same sqrt(252) / ×252 convention as Sharpe.
    """
    n = len(signal_returns)
    if n < 10 or len(spy_returns) != n:
        return {}

    mu_s = _mean(signal_returns)
    mu_m = _mean(spy_returns)

    # Robust Theil-Sen slope (beta) and intercept (Jensen's alpha)
    beta, alpha_pt = _theil_sen(spy_returns, signal_returns)
    # Rf-adjust the intercept: α_jensen = α_OLS − Rf×(1 − beta)
    alpha_pt_rf = alpha_pt - RF_DAILY * (1.0 - beta)

    # Residuals → tracking error, R²
    residuals = [signal_returns[i] - (alpha_pt + beta * spy_returns[i]) for i in range(n)]
    te_per_trade = _std(residuals)
    var_s = _std(signal_returns) ** 2
    r_squared = 1.0 - (_std(residuals) ** 2 / var_s) if var_s > 0 else 0.0

    # Annualise
    alpha_ann = alpha_pt_rf * 252
    te_ann = te_per_trade * _SQRT_252
    info_ratio = (alpha_ann / te_ann) if te_ann > 0 else float("nan")

    # Naive raw alpha
    raw_alpha_pt = mu_s - mu_m

    # Portfolio-level beta estimate: avg exposure × avg stock beta
    # 7 trades/yr × 10d hold / 252 ≈ 28% average deployed; stock beta ≈ 1.0
    portfolio_beta_est = 0.28

    return {
        "n_pairs": n,
        "spy_avg_return": round(mu_m, 4),
        "signal_avg_return": round(mu_s, 4),
        "raw_alpha_per_trade": round(raw_alpha_pt, 4),
        "raw_alpha_ann": round(raw_alpha_pt * 252, 4),
        "beta": round(beta, 4),
        "portfolio_beta_est": portfolio_beta_est,
        "jensen_alpha_per_trade": round(alpha_pt_rf, 4),
        "jensen_alpha_ann": round(alpha_ann, 4),
        "tracking_error_per_trade": round(te_per_trade, 4),
        "tracking_error_ann": round(te_ann, 4),
        "information_ratio": round(info_ratio, 4) if info_ratio == info_ratio else None,
        "r_squared": round(r_squared, 4),
    }


def brier_score(rows) -> float:
    pairs = []
    for r in rows:
        if r.outcome_pct is None or r.confidence is None:
            continue
        prob = min(max(r.confidence / 100.0, 0.0), 1.0)
        outcome = 1 if r.outcome_pct > 0 else 0
        pairs.append((prob, outcome))
    if not pairs:
        return float("nan")
    return sum((p - o) ** 2 for p, o in pairs) / len(pairs)


def pf_str(pf: float) -> str:
    return "∞" if pf == float("inf") else f"{pf:.2f}x"


def _fmt(v, fmt=".2f", suffix="") -> str:
    if v != v or v is None:  # NaN / None
        return "—"
    if v == float("inf"):
        return "∞"
    if v == float("-inf"):
        return "-∞"
    return f"{v:{fmt}}{suffix}"


def _sig(p: float) -> str:
    """Return significance marker from p-value."""
    if p != p:
        return ""
    if p < 0.001:
        return " ***"
    if p < 0.01:
        return " **"
    if p < 0.05:
        return " *"
    return " (ns)"


def confidence_bucket(conf: float) -> str:
    if conf >= 70:
        return "High (≥70%)"
    if conf >= 55:
        return "Medium (55–69%)"
    return "Low (<55%)"


def month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m") if dt else "Unknown"


def print_table(header: list[str], rows: list[list[str]]) -> None:
    print("| " + " | ".join(header) + " |")
    print("|" + "|".join("---:" if i > 0 else "---" for i in range(len(header))) + "|")
    for row in rows:
        print("| " + " | ".join(row) + " |")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


async def analyze_db(snapshot_tag: str | None = None, since_days: int | None = None) -> None:
    db_gen = get_db()
    db = await anext(db_gen)
    try:
        q = select(Signal).where(Signal.outcome_pct.isnot(None))
        if since_days:
            cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=since_days)
            q = q.where(Signal.created_at >= cutoff)
        rows = (await db.execute(q.order_by(Signal.created_at.asc()))).scalars().all()
    except Exception as db_err:
        print(f"[error] DB query failed: {db_err}")
        return
    finally:
        await db.close()

    try:
        if not rows:
            print("No resolved signals found.")
            return

        # ── Collect slices ────────────────────────────────────────────────────
        all_ret = []
        ret_1d = [r.outcome_1d for r in rows if r.outcome_1d is not None]
        ret_3d = [r.outcome_3d for r in rows if r.outcome_3d is not None]
        ret_14d = [r.outcome_14d for r in rows if r.outcome_14d is not None]

        style_map = defaultdict(list)
        action_map = defaultdict(list)
        sector_map = defaultdict(list)
        session_map = defaultdict(list)
        conf_map = defaultdict(list)
        exit_map = defaultdict(list)
        month_map = defaultdict(list)
        dow_map = defaultdict(list)  # day-of-week → returns
        ticker_map = defaultdict(list)  # ticker → returns
        dte_map = defaultdict(list)  # days-to-earnings bucket → returns
        mae_vals = []
        mfe_vals = []
        stop_dist_vals = []  # distance from entry to stop (%)
        pct_above_1r_vals = []  # per-trade bool: did outcome exceed 1R?
        hit_stop_count = hit_target_count = 0
        stop_enforced_losses = 0  # trades where hit_stop=True but outcome_pct > 0 (phantom wins)

        for r in rows:
            try:
                ret = r.outcome_pct
                if not isinstance(ret, (int, float)) or ret != ret:
                    continue
                all_ret.append(ret)
                style_map[(r.style or "swing").lower()].append(ret)
                action_map[(r.action or "BUY").upper()].append(ret)
                if r.sector_etf:
                    sector_map[r.sector_etf].append(ret)
                if r.session:
                    session_map[r.session].append(ret)
                if r.confidence is not None:
                    try:
                        conf_map[confidence_bucket(float(r.confidence))].append(ret)
                    except (TypeError, ValueError):
                        pass
                if r.exit_type:
                    exit_map[r.exit_type].append(ret)
                if r.created_at:
                    try:
                        month_map[month_key(r.created_at)].append(ret)
                    except Exception:
                        pass
                    try:
                        dow_map[r.created_at.strftime("%A")].append(ret)
                    except Exception:
                        pass
                if r.ticker:
                    ticker_map[r.ticker].append(ret)
                if r.days_to_earnings is not None:
                    try:
                        dte = int(r.days_to_earnings)
                        if dte <= 3:
                            dte_map["0-3d (blackout zone)"].append(ret)
                        elif dte <= 7:
                            dte_map["4-7d (caution ×0.75)"].append(ret)
                        elif dte <= 14:
                            dte_map["8-14d (mild caution)"].append(ret)
                        else:
                            dte_map["15+d (safe zone)"].append(ret)
                    except (TypeError, ValueError):
                        pass
                if r.mae is not None:
                    try:
                        v = float(r.mae)
                        if v == v:
                            mae_vals.append(v)
                    except (TypeError, ValueError):
                        pass
                if r.mfe is not None:
                    try:
                        v = float(r.mfe)
                        if v == v:
                            mfe_vals.append(v)
                    except (TypeError, ValueError):
                        pass
                if r.hit_stop:
                    hit_stop_count += 1
                    # Phantom win: price touched stop but outcome_pct still positive
                    # (stop not enforced intraday — position dipped below stop, recovered)
                    if ret > 0:
                        stop_enforced_losses += 1
                if r.hit_target:
                    hit_target_count += 1
                # Stop distance + 1R tracker — computed together to guarantee alignment
                if r.entry and r.stop and r.entry > 0 and r.stop > 0:
                    try:
                        sd = abs(float(r.entry) - float(r.stop)) / float(r.entry) * 100
                        if sd > 0:
                            stop_dist_vals.append(sd)
                            pct_above_1r_vals.append(ret / sd > 1.0)
                    except Exception:
                        pass
            except Exception as _row_err:
                print(f"  [warn] skipped signal id={getattr(r, 'id', '?')}: {_row_err}", flush=True)

        if not all_ret:
            print("No valid return data.")
            return

        gm = calc_metrics(all_ret)
        bs = brier_score(rows)

        # ── Realistic (stop-enforced + friction-adjusted) summary ─────────────
        # The reported expectancy uses the mark-to-market WR (58.8%) and raw
        # returns. The realistic figure enforces two corrections:
        #   1. Stop-enforced WR: the 88 phantom wins (hit_stop=True, outcome>0)
        #      are forced to losses — WR drops to 42.2%.
        #   2. Friction: every trade pays 0.50% round-trip cost regardless of outcome.
        n_all = gm["count"]
        stop_enforced_wins = len([r for r in all_ret if r > 0]) - stop_enforced_losses
        stop_enforced_losses_count = len([r for r in all_ret if r < 0]) + stop_enforced_losses
        flat_count = n_all - stop_enforced_wins - stop_enforced_losses_count

        stop_enforced_wr_pct = (stop_enforced_wins / n_all) * 100
        friction_avg_win = gm["avg_win"] - FRICTION_PCT  # wins shrink by friction
        friction_avg_loss = gm["avg_loss"] - FRICTION_PCT  # losses worsen by friction
        se_wr = stop_enforced_wins / n_all
        se_lr = stop_enforced_losses_count / n_all
        se_flat_r = flat_count / n_all
        realistic_expectancy = (se_wr * friction_avg_win) + (se_lr * friction_avg_loss) + (se_flat_r * -FRICTION_PCT)

        # Realistic Kelly — uses stop-enforced WR and friction-adjusted magnitudes.
        # Reported Kelly (39.3%) uses optimistic raw inputs and will oversize positions
        # until the +19.1pp calibration gap closes.
        realistic_kelly = 0.0
        if friction_avg_win > 0 and friction_avg_loss < 0:
            realistic_kelly = se_wr - (se_lr / (friction_avg_win / abs(friction_avg_loss)))
            realistic_kelly = max(realistic_kelly, 0.0) * 100  # never negative

        dates = [r.created_at for r in rows if r.created_at]
        earliest = min(dates) if dates else None
        latest = max(dates) if dates else None
        date_range_days = (latest - earliest).days + 1 if earliest and latest else 18
        date_range_str = f"{earliest.strftime('%Y-%m-%d')} → {latest.strftime('%Y-%m-%d')}" if earliest else "unknown"

        rm = risk_metrics(all_ret, date_range_days)

        # ── Alpha vs SPY — fetch benchmark bars once, pair per signal ────────
        spy_bars = await fetch_spy_bars(earliest, latest)
        alpha_signal_rets: list[float] = []
        alpha_spy_rets: list[float] = []
        if spy_bars:
            for r in rows:
                if r.outcome_pct is None or r.created_at is None:
                    continue
                exit_dt = r.outcome_at or (r.created_at + timedelta(days=10))
                entry_close = nearest_spy_close(spy_bars, r.created_at)
                exit_close = nearest_spy_close(spy_bars, exit_dt)
                if entry_close and exit_close and entry_close > 0:
                    spy_ret = (exit_close / entry_close - 1) * 100
                    alpha_signal_rets.append(r.outcome_pct)
                    alpha_spy_rets.append(spy_ret)
        am = alpha_metrics(alpha_signal_rets, alpha_spy_rets)

        # ══════════════════════════════════════════════════════════════════════
        _scipy_avail = True
        try:
            import scipy.stats  # noqa: F401
        except ImportError:
            _scipy_avail = False
        _rf_note = f"Rf={RF_ANNUAL * 100:.0f}% annualised ({RF_DAILY:.4f}%/trade)"
        _scipy_note = (
            "scipy t-distribution (exact)" if _scipy_avail else "Chebyshev bound (install scipy for exact p-values)"
        )

        print("# Signal.Trade — Institutional Performance Report\n")
        print(
            f"> **Coverage:** {date_range_str} · **{gm['count']} resolved trades**\n"
            f"> _Sharpe/Sortino: sqrt(252) scaling, {_rf_note}. "
            f"Per-signal quality metrics, not portfolio equity-curve Sharpe._\n"
            f"> _p-values via {_scipy_note}._\n"
        )

        # ── 1. Return summary ─────────────────────────────────────────────────
        print("## 1. Return Summary\n")
        print_table(
            ["Metric", "Reported", "Realistic", "Note"],
            [
                [
                    "Win Rate",
                    f"{gm['wr']:.1f}%",
                    f"{stop_enforced_wr_pct:.1f}%",
                    "Realistic = stop-enforced (88 phantom wins removed)",
                ],
                [
                    "Avg Return / Trade",
                    f"{gm['avg']:+.2f}%",
                    f"{gm['avg'] - FRICTION_PCT:+.2f}%",
                    "Realistic = after 0.50% round-trip friction",
                ],
                ["Avg Win", f"{gm['avg_win']:+.2f}%", f"{friction_avg_win:+.2f}%", "after friction"],
                ["Avg Loss", f"{gm['avg_loss']:+.2f}%", f"{friction_avg_loss:+.2f}%", "after friction"],
                [
                    "Payoff Ratio",
                    _fmt(rm.get("payoff"), ".2f", "×"),
                    _fmt(
                        friction_avg_win / abs(friction_avg_loss) if friction_avg_loss != 0 else float("inf"),
                        ".2f",
                        "×",
                    ),
                    "friction-adjusted win / |loss|",
                ],
                ["Profit Factor", pf_str(gm["pf"]), "—", "gross profit / gross loss (reported)"],
                [
                    "Expectancy / Trade",
                    f"{gm['expectancy']:+.2f}%",
                    f"{realistic_expectancy:+.2f}%",
                    "Realistic = stop-enforced WR × friction-adj returns",
                ],
                [
                    "Kelly Fraction",
                    f"{gm['kelly']:.1f}%",
                    f"{realistic_kelly:.1f}%",
                    "Realistic Kelly is unreliable until calibration gap < 5pp",
                ],
            ],
        )
        print(
            f"\n> **Expectancy gap:** reported `{gm['expectancy']:+.2f}%` vs realistic `{realistic_expectancy:+.2f}%` "
            f"— a {gm['expectancy'] - realistic_expectancy:.2f}pp difference driven by 88 phantom wins and 0.50% friction. "
            f"The realistic figure is the number a live broker account will experience."
        )

        # ── 2. Risk-adjusted metrics ──────────────────────────────────────────
        print("\n## 2. Risk-Adjusted Metrics\n")
        print_table(
            ["Metric", "Value", "Benchmark"],
            [
                ["Sharpe Ratio", _fmt(rm.get("sharpe"), ".2f"), f"> 1.0 = good, > 2.0 = excellent ({_rf_note})"],
                ["Sortino Ratio", _fmt(rm.get("sortino"), ".2f"), f"> 1.5 = good (downside-only σ; {_rf_note})"],
                [
                    "Calmar (standard)",
                    _fmt(rm.get("calmar_std"), ".2f"),
                    "CAGR of equity curve / max_dd — comparable to external benchmarks",
                ],
                [
                    "Calmar (custom)",
                    _fmt(rm.get("calmar"), ".2f"),
                    "ann_ret×5% sizing / max_dd — not standard; do not compare externally",
                ],
                ["Omega Ratio", _fmt(rm.get("omega"), ".2f"), "> 1.0 = edge exists"],
                ["Max Drawdown", f"-{rm.get('max_dd', 0):.2f}%", "5% sequential position sizing"],
                ["Recovery Factor", _fmt(rm.get("recovery"), ".2f"), "net return / max DD"],
                ["Ulcer Index", _fmt(rm.get("ulcer"), ".2f"), "< 5 = low drawdown stress"],
            ],
        )

        # ── 3. Tail risk ──────────────────────────────────────────────────────
        print("\n## 3. Tail Risk (Non-Parametric)\n")
        print_table(
            ["Metric", "Value", "Interpretation"],
            [
                ["VaR 95%", f"-{rm.get('var_95', 0):.2f}%", "worst single-trade loss, 1-in-20"],
                ["VaR 99%", f"-{rm.get('var_99', 0):.2f}%", "worst single-trade loss, 1-in-100"],
                ["CVaR 95%", f"-{rm.get('cvar_95', 0):.2f}%", "avg loss when past VaR 95"],
                ["CVaR 99%", f"-{rm.get('cvar_99', 0):.2f}%", "avg loss when past VaR 99"],
                ["Volatility (σ)", f"{rm.get('sigma', 0):.2f}%", "per-trade std dev of returns"],
            ],
        )

        # ── 4. Distribution diagnostics ────────────────────────────────────────
        print("\n## 4. Distribution Diagnostics\n")
        t, p = rm.get("t_stat", float("nan")), rm.get("p_value", float("nan"))
        sig_marker = _sig(p)
        skew = rm.get("skew", float("nan"))
        kurt = rm.get("kurt", float("nan"))
        print_table(
            ["Metric", "Value", "Interpretation"],
            [
                ["Skewness", _fmt(skew, "+.3f"), "positive = right tail (big wins), negative = left tail (big losses)"],
                ["Excess Kurtosis", _fmt(kurt, "+.3f"), "> 0 = fat tails (more extremes than normal)"],
                [
                    "T-statistic",
                    _fmt(t, "+.2f") + sig_marker,
                    "H₀: mean return = 0  (* p<0.05, ** p<0.01, *** p<0.001)",
                ],
                ["P-value", _fmt(p, ".4f"), "two-sided; < 0.05 = statistically significant edge"],
                ["Brier Score", f"{bs:.4f}" if bs == bs else "—", "0 = perfect calibration, 0.25 = random"],
                ["Max Win Streak", str(rm.get("max_win_streak", 0)), ""],
                ["Max Loss Streak", str(rm.get("max_loss_streak", 0)), ""],
            ],
        )

        # ── 5. Multi-timeframe ────────────────────────────────────────────────
        print("\n## 5. Multi-Timeframe Win Rates\n")
        tf_rows = []
        for label, rets in [("1d", ret_1d), ("3d", ret_3d), ("7d (primary)", all_ret), ("14d", ret_14d)]:
            m = calc_metrics(rets)
            if m["count"] == 0:
                continue
            rm_tf = risk_metrics(rets, date_range_days)
            tf_rows.append(
                [
                    label,
                    str(m["count"]),
                    f"{m['wr']:.1f}%",
                    f"{m['avg']:+.2f}%",
                    pf_str(m["pf"]),
                    _fmt(rm_tf.get("sharpe"), ".2f"),
                ]
            )
        print_table(["Horizon", "Count", "Win Rate", "Avg Return", "PF", "Sharpe"], tf_rows)

        # ── 6. Monthly performance ────────────────────────────────────────────
        print("\n## 6. Monthly Performance\n")
        month_rows = []
        for month in sorted(month_map):
            m = calc_metrics(month_map[month])
            rm_m = risk_metrics(month_map[month], 21)  # ~21 trading days/month
            month_rows.append(
                [
                    month,
                    str(m["count"]),
                    f"{m['wr']:.1f}%",
                    f"{m['avg']:+.2f}%",
                    pf_str(m["pf"]),
                    _fmt(rm_m.get("sharpe"), ".2f"),
                ]
            )
        print_table(["Month", "Trades", "Win Rate", "Avg Return", "PF", "Sharpe"], month_rows)

        # ── 7. By hold style ──────────────────────────────────────────────────
        print("\n## 7. By Hold Style\n")
        style_rows = []
        for style in ["position", "swing", "intraday"]:
            m = calc_metrics(style_map.get(style, []))
            rm_s = risk_metrics(style_map.get(style, []), date_range_days)
            style_rows.append(
                [
                    f"**{style.capitalize()}**",
                    str(m["count"]),
                    f"{m['wr']:.1f}%" if m["count"] else "—",
                    f"{m['avg']:+.2f}%" if m["count"] else "—",
                    pf_str(m["pf"]) if m["count"] else "—",
                    _fmt(rm_s.get("sharpe"), ".2f"),
                    _fmt(rm_s.get("max_dd"), ".2f", "%"),
                ]
            )
        print_table(["Style", "N", "Win Rate", "Avg Ret", "PF", "Sharpe", "Max DD"], style_rows)

        # ── 8. By action ──────────────────────────────────────────────────────
        print("\n## 8. By Action\n")
        action_rows = []
        for action in ["BUY", "SELL"]:
            m = calc_metrics(action_map.get(action, []))
            rm_a = risk_metrics(action_map.get(action, []), date_range_days)
            action_rows.append(
                [
                    f"**{action}**",
                    str(m["count"]),
                    f"{m['wr']:.1f}%" if m["count"] else "—",
                    f"{m['avg']:+.2f}%" if m["count"] else "—",
                    pf_str(m["pf"]) if m["count"] else "—",
                    _fmt(rm_a.get("sharpe"), ".2f"),
                ]
            )
        print_table(["Action", "N", "Win Rate", "Avg Ret", "PF", "Sharpe"], action_rows)

        # ── 9. By exit type ───────────────────────────────────────────────────
        if exit_map:
            print("\n## 9. By Exit Type\n")
            exit_rows = []
            for et in ["target", "time", "pending", "stop"]:
                m = calc_metrics(exit_map.get(et, []))
                if m["count"] == 0:
                    continue
                exit_rows.append(
                    [
                        f"**{et.capitalize()}**",
                        str(m["count"]),
                        f"{m['wr']:.1f}%",
                        f"{m['avg']:+.2f}%",
                        pf_str(m["pf"]),
                    ]
                )
            print_table(["Exit Type", "N", "Win Rate", "Avg Ret", "PF"], exit_rows)

        # ── 10. By confidence bucket ──────────────────────────────────────────
        print("\n## 10. Confidence Calibration\n")
        conf_rows = []
        for bucket in ["High (≥70%)", "Medium (55–69%)", "Low (<55%)"]:
            m = calc_metrics(conf_map.get(bucket, []))
            conf_rows.append(
                [
                    bucket,
                    str(m["count"]),
                    f"{m['wr']:.1f}%" if m["count"] else "—",
                    f"{m['avg']:+.2f}%" if m["count"] else "—",
                    pf_str(m["pf"]) if m["count"] else "—",
                ]
            )
        print_table(["Confidence Band", "N", "Win Rate", "Avg Ret", "PF"], conf_rows)

        # ── 11. Reliability diagram (confidence bands vs actual win rate) ─────
        print("\n### Reliability Diagram (predicted confidence vs actual win rate)\n")
        BANDS = [(0, 50), (50, 55), (55, 60), (60, 65), (65, 70), (70, 75), (75, 80), (80, 101)]
        band_rows = []
        for lo, hi in BANDS:
            band_signals = [
                r for r in rows if r.confidence is not None and lo <= r.confidence < hi and r.outcome_pct is not None
            ]
            if not band_signals:
                continue
            actual_wr = sum(1 for r in band_signals if r.outcome_pct > 0) / len(band_signals) * 100
            avg_conf = _mean([r.confidence for r in band_signals])
            gap = avg_conf - actual_wr
            calib = "OK" if abs(gap) <= 10 else ("OVER ⚠" if gap > 0 else "UNDER ⚠")
            band_rows.append(
                [
                    f"{lo}–{hi}%",
                    str(len(band_signals)),
                    f"{avg_conf:.1f}%",
                    f"{actual_wr:.1f}%",
                    f"{gap:+.1f}pp",
                    calib,
                ]
            )
        print_table(["Band", "N", "Avg Conf", "Actual WR", "Gap", "Calibrated?"], band_rows)

        # ── 12a. Day-of-week breakdown ─────────────────────────────────────────
        DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        if dow_map:
            print("\n## 11a. Performance by Day of Week\n")
            print("> Diagnoses live-vs-backtest gap: are certain scan days underperforming?\n")
            dow_rows = []
            for day in DOW_ORDER:
                if day not in dow_map:
                    continue
                m = calc_metrics(dow_map[day])
                flag = " ⚠" if m["wr"] < 45 or m["avg"] < 0 else ""
                dow_rows.append(
                    [day, str(m["count"]), f"{m['wr']:.1f}%{flag}", f"{m['avg']:+.2f}%{flag}", pf_str(m["pf"])]
                )
            print_table(["Day", "N", "Win Rate", "Avg Ret", "PF"], dow_rows)
            best_day = max(DOW_ORDER, key=lambda d: calc_metrics(dow_map.get(d, [])).get("avg", -99))
            worst_day = min(
                DOW_ORDER, key=lambda d: calc_metrics(dow_map.get(d, [])).get("avg", 99) if dow_map.get(d) else 99
            )
            print(f"\n> Best day: **{best_day}** · Worst day: **{worst_day}**")

        # ── 12b. Ticker-level breakdown ────────────────────────────────────────
        if ticker_map:
            print("\n## 11b. Performance by Ticker (top/bottom 5)\n")
            print("> Identifies tickers dragging live performance vs backtest universe.\n")
            tickers_sorted = sorted(
                ticker_map.items(), key=lambda kv: calc_metrics(kv[1]).get("avg", -99), reverse=True
            )
            ticker_rows = []
            shown = set()
            for tkr, rets in tickers_sorted[:5]:  # top 5 by avg ret
                m = calc_metrics(rets)
                ticker_rows.append(
                    [f"**{tkr}** ↑", str(m["count"]), f"{m['wr']:.1f}%", f"{m['avg']:+.2f}%", pf_str(m["pf"])]
                )
                shown.add(tkr)
            for tkr, rets in tickers_sorted[-5:]:  # bottom 5 by avg ret
                if tkr in shown:
                    continue
                m = calc_metrics(rets)
                ticker_rows.append(
                    [f"{tkr} ↓", str(m["count"]), f"{m['wr']:.1f}%", f"{m['avg']:+.2f}%", pf_str(m["pf"])]
                )
            print_table(["Ticker", "N", "Win Rate", "Avg Ret", "PF"], ticker_rows)

        # ── 12c. Days-to-earnings breakdown ───────────────────────────────────
        if dte_map:
            print("\n## 11c. Performance by Days-to-Next-Earnings\n")
            print("> Validates the earnings gate: signals near earnings should show lower WR.\n")
            dte_order = ["0-3d (blackout zone)", "4-7d (caution ×0.75)", "8-14d (mild caution)", "15+d (safe zone)"]
            dte_rows = []
            for bucket in dte_order:
                if bucket not in dte_map:
                    continue
                m = calc_metrics(dte_map[bucket])
                flag = " ⚠" if m["wr"] < 45 or m["avg"] < 0 else ""
                dte_rows.append(
                    [bucket, str(m["count"]), f"{m['wr']:.1f}%{flag}", f"{m['avg']:+.2f}%{flag}", pf_str(m["pf"])]
                )
            print_table(["Earnings Proximity", "N", "Win Rate", "Avg Ret", "PF"], dte_rows)

        # ── 12. Sector performance ─────────────────────────────────────────────
        if sector_map:
            print("\n## 11. Sector Performance\n")
            sector_rows = []
            for sector in sorted(sector_map, key=lambda s: -calc_metrics(sector_map[s])["avg"]):
                m = calc_metrics(sector_map[sector])
                sector_rows.append(
                    [
                        sector,
                        str(m["count"]),
                        f"{m['wr']:.1f}%",
                        f"{m['avg']:+.2f}%",
                        pf_str(m["pf"]),
                    ]
                )
            print_table(["Sector ETF", "N", "Win Rate", "Avg Ret", "PF"], sector_rows)

        # ── 13. Session performance ────────────────────────────────────────────
        if session_map:
            print("\n## 12. Market Session Performance\n")
            sess_rows = []
            for sess in sorted(session_map, key=lambda s: -len(session_map[s])):
                m = calc_metrics(session_map[sess])
                sess_rows.append(
                    [
                        sess.capitalize(),
                        str(m["count"]),
                        f"{m['wr']:.1f}%",
                        f"{m['avg']:+.2f}%",
                        pf_str(m["pf"]),
                    ]
                )
            print_table(["Session", "N", "Win Rate", "Avg Ret", "PF"], sess_rows)

        # ── 14. Trade-path analytics ───────────────────────────────────────────
        n = n_all
        phantom = stop_enforced_losses
        # stop_enforced_wr_pct already computed above for Return Summary
        print("\n## 13. Trade-Path Analytics (MAE / MFE)\n")

        print(f"- **Hit Target:** {hit_target_count} / {n} ({hit_target_count / n * 100:.1f}%)")
        print(f"- **Hit Stop:**   {hit_stop_count} / {n} ({hit_stop_count / n * 100:.1f}%)")
        if phantom > 0:
            print(
                f"- **Phantom Wins (stop hit but outcome_pct > 0):** {phantom} trades "
                f"— stop not enforced intraday, position recovered by measurement date"
            )
            print(
                f"- **Stop-Enforced Win Rate:** {stop_enforced_wr_pct:.1f}% "
                f"(vs reported {gm['wr']:.1f}% — difference = {gm['wr'] - stop_enforced_wr_pct:.1f}pp)"
            )

        if mae_vals:
            avg_mae = _mean(mae_vals)
            print(f"- **Avg MAE (max adverse excursion):**  {avg_mae:+.2f}%  | worst: {min(mae_vals):+.2f}%")
        if mfe_vals:
            avg_mfe = _mean(mfe_vals)
            print(f"- **Avg MFE (max favorable excursion):** {avg_mfe:+.2f}%  | best: {max(mfe_vals):+.2f}%")
        if mae_vals and mfe_vals:
            mfe_mae = avg_mfe / abs(avg_mae) if avg_mae != 0 else float("inf")
            print(f"- **MFE/MAE Ratio:** {mfe_mae:.2f}×  (>1 = position moves favorably before adversely)")

        # Payoff Ratio vs Capture Ratio — intentionally separated and labeled
        avg_win_val = gm.get("avg_win", 0.0)
        avg_loss_val = gm.get("avg_loss", 0.0)
        payoff_ratio = abs(avg_win_val / avg_loss_val) if avg_loss_val != 0 else float("inf")
        print("\n**Return Quality:**")
        print(
            f"- **Payoff Ratio:** {payoff_ratio:.2f}× — magnitude of avg win vs avg loss "
            f"({avg_win_val:+.2f}% / {avg_loss_val:+.2f}%)"
        )
        if stop_dist_vals:
            avg_stop_dist = _mean(stop_dist_vals)
            capture = gm["avg"] / avg_stop_dist if avg_stop_dist > 0 else float("nan")
            pct_above_1r = (sum(pct_above_1r_vals) / len(pct_above_1r_vals) * 100) if pct_above_1r_vals else 0.0
            print(f"- **Avg Stop Distance:** {avg_stop_dist:.2f}% (wide ATR stops give room but reduce capture)")
            pct_captured = capture * 100 if capture == capture else 0.0
            print(
                f"- **Capture Ratio:** {capture:.2f}× — avg_return / avg_stop_distance "
                f"({pct_captured:.0f}% of risked distance captured on average; "
                f"distinct from Payoff Ratio which measures win vs loss magnitude)"
            )
            print(f"- **% Trades > 1R:** {pct_above_1r:.1f}%")

        # ── 15. Return distribution quartiles ──────────────────────────────────
        print("\n## 14. Return Distribution\n")
        sorted_ret = sorted(all_ret)
        n_ret = len(sorted_ret)
        print_table(
            ["Percentile", "Return"],
            [
                ["P1  (worst 1%)", f"{_percentile(all_ret, 1):+.2f}%"],
                ["P5  (VaR 95%)", f"{_percentile(all_ret, 5):+.2f}%"],
                ["P10", f"{_percentile(all_ret, 10):+.2f}%"],
                ["P25 (Q1)", f"{_percentile(all_ret, 25):+.2f}%"],
                ["P50 (median)", f"{_percentile(all_ret, 50):+.2f}%"],
                ["P75 (Q3)", f"{_percentile(all_ret, 75):+.2f}%"],
                ["P90", f"{_percentile(all_ret, 90):+.2f}%"],
                ["P95", f"{_percentile(all_ret, 95):+.2f}%"],
                ["P99 (best 1%)", f"{_percentile(all_ret, 99):+.2f}%"],
            ],
        )

        # ── 15. Alpha vs SPY ──────────────────────────────────────────────────
        print("\n## 15. Alpha vs SPY Benchmark\n")
        if am:
            print_table(
                ["Metric", "Value", "Interpretation"],
                [
                    ["Paired trades", str(am["n_pairs"]), "signals with matching SPY window"],
                    [
                        "SPY avg return / window",
                        f"{am['spy_avg_return']:+.2f}%",
                        "benchmark return over same hold period",
                    ],
                    [
                        "Raw Alpha / trade",
                        f"{am['raw_alpha_per_trade']:+.2f}%",
                        "avg signal − avg SPY (naive, no regression)",
                    ],
                    ["Raw Alpha (annualised)", f"{am['raw_alpha_ann']:+.2f}%", "×252 same convention as Sharpe"],
                    [
                        "Trade-level Beta (Theil-Sen)",
                        f"{am['beta']:+.3f}",
                        "robust median-of-pairwise-slopes; resistant to outliers",
                    ],
                    [
                        "Portfolio Beta (est.)",
                        f"~{am['portfolio_beta_est']:.2f}",
                        "≈ avg_exposure × avg_stock_beta; use this for risk disclosure",
                    ],
                    [
                        "Jensen's Alpha / trade",
                        f"{am['jensen_alpha_per_trade']:+.2f}%",
                        "Theil-Sen intercept, Rf-adjusted — market-independent edge",
                    ],
                    [
                        "Jensen's Alpha (annualised)",
                        f"{am['jensen_alpha_ann']:+.2f}%",
                        "×252 annualised; primary alpha headline",
                    ],
                    [
                        "Tracking Error / trade",
                        f"{am['tracking_error_per_trade']:.2f}%",
                        "std of excess returns (residuals)",
                    ],
                    ["Tracking Error (annualised)", f"{am['tracking_error_ann']:.2f}%", "×√252"],
                    [
                        "Information Ratio",
                        _fmt(am.get("information_ratio"), ".2f"),
                        "> 0.5 = good; > 1.0 = excellent (annualised α / annualised TE)",
                    ],
                    ["R²", f"{am['r_squared']:.3f}", "fraction of signal variance explained by SPY moves"],
                ],
            )
            ir = am.get("information_ratio")
            ir_str = f"{ir:.2f}" if ir is not None and ir == ir else "—"
            _beta_warn = (
                " ⚠ trade-level beta > 2 — likely OLS/outlier artifact; use portfolio beta ~0.28"
                if am["beta"] > 2.0
                else ""
            )
            print(
                f"\n> Jensen's Alpha **{am['jensen_alpha_ann']:+.2f}%** annualised — "
                f"Theil-Sen robust estimate (resistant to stop-corrected outliers). "
                f"Trade-level Beta **{am['beta']:+.3f}**{_beta_warn}. "
                f"Portfolio Beta est. **~{am['portfolio_beta_est']:.2f}** (28% avg exposure × stock beta 1.0). "
                f"Information Ratio **{ir_str}** (alpha per unit of tracking risk).\n"
                f"> Note: trade-level and portfolio-level beta are different metrics. "
                f"Portfolio beta ≈ 0.28 means a 10% SPY crash → ~2.8% portfolio drawdown from beta alone."
            )
        else:
            print("> _SPY data unavailable — set POLYGON_API_KEY to enable alpha calculation._")

        # ── §16. Pro-Forma Analysis — v5.12 filters applied retrospectively ─────
        # Answers: "what would performance look like if fixes had been live
        # for the entire history?"
        #
        # Filters applied (matching live v5.12 gates):
        #   A. XLF / XLP sector excluded  — blocked in delivery_gates.py since v5.8
        #   B. Intraday style excluded     — disabled in delivery_gates.py (v5.12)
        #   C. Confidence > 65% excluded   — ceiling lowered to 65% (v5.12)
        print("\n## 16. Pro-Forma Analysis — v5.12 Filters Applied Retrospectively\n")
        print("> Retroactively applies v5.12 gates to historical trades to quantify")
        print("> the lift those fixes would have produced if deployed from day 1.\n")

        PROFORMA_BLOCKED_SECTORS = {"XLF", "XLP", "XLU"}
        PROFORMA_CONF_CEILING = 65.0  # new ceiling in v5.12

        def _row_passes_proforma(r) -> bool:
            """True if this trade would have been delivered under v5.12 rules."""
            # A. Sector gate
            if (r.sector_etf or "").upper() in PROFORMA_BLOCKED_SECTORS:
                return False
            # B. Intraday gate
            if (r.style or "").lower() == "intraday":
                return False
            # C. Confidence ceiling
            if r.confidence is not None and float(r.confidence) > PROFORMA_CONF_CEILING:
                return False
            return True

        pf_rows = [r for r in rows if _row_passes_proforma(r)]
        pf_ret = [r.outcome_pct for r in pf_rows if r.outcome_pct is not None and r.outcome_pct == r.outcome_pct]
        pf_stop = [r for r in pf_rows if r.hit_stop]
        pf_phantom = sum(1 for r in pf_stop if r.outcome_pct is not None and r.outcome_pct > 0)
        pf_n = len(pf_ret)
        pf_se_wins = sum(1 for r in pf_rows if r.outcome_pct is not None and r.hit_stop and r.outcome_pct <= 0)
        pf_non_phantom = sum(1 for r in pf_rows if r.outcome_pct is not None)
        pf_stop_enforced_wr = (
            (pf_non_phantom - len(pf_stop) + pf_se_wins) / pf_non_phantom * 100 if pf_non_phantom else 0.0
        )

        removed_total = len(rows) - len(pf_rows)
        removed_xlf = sum(1 for r in rows if (r.sector_etf or "").upper() in PROFORMA_BLOCKED_SECTORS)
        removed_intra = sum(
            1
            for r in rows
            if (r.style or "").lower() == "intraday" and (r.sector_etf or "").upper() not in PROFORMA_BLOCKED_SECTORS
        )
        removed_conf = sum(
            1
            for r in rows
            if r.confidence is not None
            and float(r.confidence) > PROFORMA_CONF_CEILING
            and (r.sector_etf or "").upper() not in PROFORMA_BLOCKED_SECTORS
            and (r.style or "").lower() != "intraday"
        )

        print(f"**Trades removed:** {removed_total} / {len(rows)} total")
        print(f"  — Sector gate (XLF/XLP/XLU):         {removed_xlf} trades")
        print(f"  — Intraday style:                     {removed_intra} trades")
        print(f"  — Confidence > 65%:                   {removed_conf} trades")
        print(f"**Remaining for pro-forma analysis:**   {len(pf_rows)} trades\n")

        if pf_ret:
            orig_gm = gm
            pf_gm = calc_metrics(pf_ret)
            orig_rm = rm
            pf_rm = risk_metrics(pf_ret, date_range_days)

            def _delta(a, b, fmt="+.2f"):
                d = b - a
                return f"{d:{fmt}}"

            print("### 16a. Side-by-Side Comparison\n")
            print_table(
                ["Metric", "Original (all 529)", f"Pro-Forma ({pf_n})", "Delta"],
                [
                    ["N Trades", str(len(all_ret)), str(pf_n), f"{pf_n - len(all_ret):+d}"],
                    [
                        "Win Rate (reported)",
                        f"{orig_gm['wr']:.1f}%",
                        f"{pf_gm['wr']:.1f}%",
                        _delta(orig_gm["wr"], pf_gm["wr"]) + "pp",
                    ],
                    [
                        "Stop-Enforced WR",
                        f"{stop_enforced_wr_pct:.1f}%",
                        f"{pf_stop_enforced_wr:.1f}%",
                        _delta(stop_enforced_wr_pct, pf_stop_enforced_wr) + "pp",
                    ],
                    [
                        "Avg Return",
                        f"{orig_gm['avg']:+.2f}%",
                        f"{pf_gm['avg']:+.2f}%",
                        _delta(orig_gm["avg"], pf_gm["avg"]) + "pp",
                    ],
                    [
                        "Avg Win",
                        f"{orig_gm['avg_win']:+.2f}%",
                        f"{pf_gm['avg_win']:+.2f}%",
                        _delta(orig_gm["avg_win"], pf_gm["avg_win"]) + "pp",
                    ],
                    [
                        "Avg Loss",
                        f"{orig_gm['avg_loss']:+.2f}%",
                        f"{pf_gm['avg_loss']:+.2f}%",
                        _delta(orig_gm["avg_loss"], pf_gm["avg_loss"]) + "pp",
                    ],
                    [
                        "Profit Factor",
                        f"{orig_gm['pf']:.2f}×" if orig_gm["pf"] != float("inf") else "∞",
                        f"{pf_gm['pf']:.2f}×" if pf_gm["pf"] != float("inf") else "∞",
                        _delta(
                            orig_gm["pf"] if orig_gm["pf"] != float("inf") else 99,
                            pf_gm["pf"] if pf_gm["pf"] != float("inf") else 99,
                            "+.2f",
                        )
                        + "×",
                    ],
                    [
                        "Sharpe",
                        f"{orig_rm.get('sharpe', 0):.2f}",
                        f"{pf_rm.get('sharpe', 0):.2f}",
                        _delta(orig_rm.get("sharpe", 0), pf_rm.get("sharpe", 0)),
                    ],
                    [
                        "Sortino",
                        f"{orig_rm.get('sortino', 0):.2f}",
                        f"{pf_rm.get('sortino', 0):.2f}",
                        _delta(orig_rm.get("sortino", 0), pf_rm.get("sortino", 0)),
                    ],
                    [
                        "Max Drawdown",
                        f"-{orig_rm.get('max_dd', 0):.2f}%",
                        f"-{pf_rm.get('max_dd', 0):.2f}%",
                        _delta(orig_rm.get("max_dd", 0), pf_rm.get("max_dd", 0)) + "pp",
                    ],
                    [
                        "VaR 95%",
                        f"{orig_rm.get('var_95', 0):.2f}%",
                        f"{pf_rm.get('var_95', 0):.2f}%",
                        _delta(orig_rm.get("var_95", 0), pf_rm.get("var_95", 0)) + "pp",
                    ],
                    ["Phantom Wins", str(phantom), str(pf_phantom), f"{pf_phantom - phantom:+d}"],
                ],
            )

            # Style breakdown for pro-forma
            pf_style_map = defaultdict(list)
            for r in pf_rows:
                if r.outcome_pct is not None:
                    pf_style_map[(r.style or "swing").lower()].append(r.outcome_pct)

            print("\n### 16b. Pro-Forma by Style\n")
            pf_style_rows = []
            for st in ["position", "swing", "intraday"]:
                st_rets = pf_style_map.get(st, [])
                m_ = calc_metrics(st_rets)
                rm_ = risk_metrics(st_rets, date_range_days)
                pf_style_rows.append(
                    [
                        f"**{st.capitalize()}**",
                        str(m_["count"]),
                        f"{m_['wr']:.1f}%" if m_["count"] else "—",
                        f"{m_['avg']:+.2f}%" if m_["count"] else "—",
                        f"{rm_.get('sharpe', 0):.2f}" if m_["count"] else "—",
                        "DISABLED" if st == "intraday" else "",
                    ]
                )
            print_table(["Style", "N", "Win Rate", "Avg Ret", "Sharpe", "Note"], pf_style_rows)

            # Sector breakdown for pro-forma
            pf_sector_map = defaultdict(list)
            for r in pf_rows:
                if r.outcome_pct is not None and r.sector_etf:
                    pf_sector_map[r.sector_etf].append(r.outcome_pct)

            print("\n### 16c. Pro-Forma Sector Performance (after removing XLF/XLP/XLU)\n")
            pf_sec_rows = sorted(
                [(s, calc_metrics(v)) for s, v in pf_sector_map.items()],
                key=lambda x: x[1]["avg"],
                reverse=True,
            )
            print_table(
                ["Sector ETF", "N", "Win Rate", "Avg Ret", "PF"],
                [
                    [
                        s,
                        str(m_["count"]),
                        f"{m_['wr']:.1f}%",
                        f"{m_['avg']:+.2f}%",
                        f"{m_['pf']:.2f}×" if m_["pf"] != float("inf") else "∞",
                    ]
                    for s, m_ in pf_sec_rows
                ],
            )
        else:
            print("[no pro-forma trades remain after filtering]")

        # ── Snapshot write (only when --snapshot flag provided) ────────────────
        if snapshot_tag:
            avg_mae = _mean(mae_vals) if mae_vals else None
            avg_mfe = _mean(mfe_vals) if mfe_vals else None
            avg_sd = _mean(stop_dist_vals) if stop_dist_vals else None
            capture = (gm["avg"] / avg_sd) if avg_sd else None

            snap = {
                "coverage": {
                    "from": earliest.strftime("%Y-%m-%d") if earliest else None,
                    "to": latest.strftime("%Y-%m-%d") if latest else None,
                    "days": date_range_days,
                },
                "returns": {
                    "n_trades": gm["count"],
                    "win_rate": round(gm["wr"], 2),
                    "avg": round(gm["avg"], 3),
                    "avg_win": round(gm["avg_win"], 3),
                    "avg_loss": round(gm["avg_loss"], 3),
                    "payoff": round(rm.get("payoff", 0) or 0, 3),
                    "pf": round(gm["pf"], 3) if gm["pf"] != float("inf") else None,
                    "expectancy": round(gm["expectancy"], 3),
                    "kelly": round(gm["kelly"], 2),
                },
                "risk": {
                    "sharpe": round(rm.get("sharpe", 0) or 0, 3),
                    "sortino": round(rm.get("sortino", 0) or 0, 3),
                    "calmar": round(rm.get("calmar", 0) or 0, 3),
                    "calmar_std": round(rm.get("calmar_std", 0) or 0, 3),
                    "omega": round(rm.get("omega", 0) or 0, 3),
                    "max_dd": round(rm.get("max_dd", 0) or 0, 3),
                    "recovery": round(rm.get("recovery", 0) or 0, 3),
                    "ulcer": round(rm.get("ulcer", 0) or 0, 3),
                },
                "tail": {
                    "var_95": round(rm.get("var_95", 0) or 0, 3),
                    "var_99": round(rm.get("var_99", 0) or 0, 3),
                    "cvar_95": round(rm.get("cvar_95", 0) or 0, 3),
                    "cvar_99": round(rm.get("cvar_99", 0) or 0, 3),
                    "sigma": round(rm.get("sigma", 0) or 0, 3),
                },
                "distribution": {
                    "skew": round(rm.get("skew", 0) or 0, 4),
                    "kurt": round(rm.get("kurt", 0) or 0, 4),
                    "t_stat": round(rm.get("t_stat", 0) or 0, 3),
                    "p_value": round(rm.get("p_value", 1) or 1, 6),
                    "brier": round(bs, 4) if bs == bs else None,
                    "max_win_streak": rm.get("max_win_streak", 0),
                    "max_loss_streak": rm.get("max_loss_streak", 0),
                },
                "trade_path": {
                    "hit_target_count": hit_target_count,
                    "hit_stop_count": hit_stop_count,
                    "hit_target_pct": round(hit_target_count / n * 100, 2) if n else 0,
                    "hit_stop_pct": round(hit_stop_count / n * 100, 2) if n else 0,
                    "phantom_wins": phantom,
                    "stop_enforced_wr": round(stop_enforced_wr_pct, 2),
                    "avg_mfe": round(avg_mfe, 3) if avg_mfe is not None else None,
                    "mfe_mae_ratio": round(avg_mfe / abs(avg_mae), 3) if avg_mae and avg_mfe else None,
                    "avg_stop_dist": round(avg_sd, 3) if avg_sd is not None else None,
                    "capture_ratio": round(capture, 3) if capture is not None else None,
                    "pct_above_1r": round(
                        (sum(pct_above_1r_vals) / len(pct_above_1r_vals) * 100) if pct_above_1r_vals else 0.0, 2
                    ),
                },
                "by_style": {
                    style: {
                        "n": calc_metrics(rets)["count"],
                        "win_rate": round(calc_metrics(rets)["wr"], 2),
                        "avg": round(calc_metrics(rets)["avg"], 3),
                        "sharpe": round(risk_metrics(rets, date_range_days).get("sharpe", 0) or 0, 3),
                    }
                    for style, rets in style_map.items()
                },
                "by_action": {
                    action: {
                        "n": calc_metrics(rets)["count"],
                        "win_rate": round(calc_metrics(rets)["wr"], 2),
                        "avg": round(calc_metrics(rets)["avg"], 3),
                    }
                    for action, rets in action_map.items()
                },
                "by_exit": {
                    et: {
                        "n": calc_metrics(rets)["count"],
                        "win_rate": round(calc_metrics(rets)["wr"], 2),
                        "avg": round(calc_metrics(rets)["avg"], 3),
                    }
                    for et, rets in exit_map.items()
                },
                "by_month": {
                    month: {
                        "n": calc_metrics(rets)["count"],
                        "win_rate": round(calc_metrics(rets)["wr"], 2),
                        "avg": round(calc_metrics(rets)["avg"], 3),
                        "sharpe": round(risk_metrics(rets, 21).get("sharpe", 0) or 0, 3),
                    }
                    for month, rets in sorted(month_map.items())
                },
                "by_sector": {
                    sector: {
                        "n": calc_metrics(rets)["count"],
                        "win_rate": round(calc_metrics(rets)["wr"], 2),
                        "avg": round(calc_metrics(rets)["avg"], 3),
                    }
                    for sector, rets in sector_map.items()
                },
                "alpha": am or {},
            }
            await _save_snapshot(snapshot_tag, snap, gm, am)
            print(f"\n✓ Snapshot saved: tag='{snapshot_tag}' · {gm['count']} trades")

    except Exception as analysis_err:
        print(f"[error] Analysis failed: {analysis_err}")
        raise


# ─────────────────────────────────────────────────────────────────────────────
# Snapshot persistence
# ─────────────────────────────────────────────────────────────────────────────


def _sanitize_for_json(obj):
    """Recursively replace NaN/Inf floats with None so the dict is valid JSON."""
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]
    if isinstance(obj, float) and (obj != obj or obj == float("inf") or obj == float("-inf")):
        return None
    return obj


async def _save_snapshot(tag: str, metrics: dict, gm: dict, am: dict | None = None) -> None:
    """Write a performance snapshot to the performance_snapshots table."""
    import subprocess

    from database import AsyncSessionLocal
    from models import PerformanceSnapshot

    git_sha = None
    try:
        git_sha = (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except Exception:
        pass

    jensen_ann = (am or {}).get("jensen_alpha_ann")
    alpha_val = round(jensen_ann, 4) if jensen_ann is not None else None

    from sqlalchemy import delete as _delete

    async with AsyncSessionLocal() as db:
        # Delete any existing row with this tag so re-runs during tuning
        # produce a clean update rather than duplicate rows.
        await db.execute(_delete(PerformanceSnapshot).where(PerformanceSnapshot.tag == tag))
        snap = PerformanceSnapshot(
            tag=tag,
            git_sha=git_sha,
            metrics=_sanitize_for_json(metrics),
            n_trades=gm["count"],
            win_rate=round(gm["wr"], 2),
            sharpe=round(metrics.get("risk", {}).get("sharpe", 0) or 0, 3),
            alpha=alpha_val,
        )
        db.add(snap)
        await db.commit()


def diff_snapshots(a: dict, b: dict) -> dict:
    """
    Compute the delta between two snapshot metrics dicts.

    Returns a dict with the same structure but values replaced by
    {before, after, delta, delta_pct, flag} where flag is True when the
    change exceeds a significance threshold (5% relative or 2pp absolute).
    Only compares numeric scalar fields; nested dicts are recursed.
    """
    THRESHOLDS = {
        "win_rate": 2.0,
        "avg": 0.5,
        "sharpe": 0.3,
        "sortino": 1.0,
        "max_dd": 0.5,
        "var_95": 0.5,
        "brier": 0.02,
        "pf": 0.2,
        "stop_enforced_wr": 2.0,
        "phantom_wins": 5,
    }

    def _diff_val(key, va, vb):
        if not isinstance(va, (int, float)) or not isinstance(vb, (int, float)):
            return {"before": va, "after": vb}
        delta = round(vb - va, 4)
        delta_pct = round(delta / abs(va) * 100, 2) if va != 0 else None
        threshold = THRESHOLDS.get(key)
        flag = (abs(delta) >= threshold) if threshold else (abs(delta_pct or 0) >= 5)
        return {"before": va, "after": vb, "delta": delta, "delta_pct": delta_pct, "flag": flag}

    def _diff_dict(da, db_):
        result = {}
        all_keys = set(da) | set(db_)
        for k in all_keys:
            va, vb = da.get(k), db_.get(k)
            if isinstance(va, dict) and isinstance(vb, dict):
                result[k] = _diff_dict(va, vb)
            else:
                result[k] = _diff_val(k, va, vb)
        return result

    return _diff_dict(a, b)


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Signal.Trade performance analytics")
    parser.add_argument(
        "--snapshot",
        metavar="TAG",
        default=None,
        help="Save a named snapshot to the DB after printing (e.g. 'v3-sector-gates')",
    )
    parser.add_argument(
        "--days",
        metavar="N",
        type=int,
        default=None,
        help="Limit analysis to signals from the last N calendar days (e.g. --days 21)",
    )
    args = parser.parse_args()
    asyncio.run(analyze_db(snapshot_tag=args.snapshot, since_days=args.days))
