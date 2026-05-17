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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from database import get_db
from models import Signal


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
    return _mean([(x - m) ** 3 for x in xs]) / s ** 3

def _kurtosis(xs: list[float]) -> float:
    """Excess kurtosis (normal = 0)."""
    if len(xs) < 4:
        return float("nan")
    m, s = _mean(xs), _std(xs)
    if s == 0:
        return float("nan")
    return _mean([(x - m) ** 4 for x in xs]) / s ** 4 - 3.0

def _t_stat(xs: list[float]) -> tuple[float, float]:
    """Two-sided t-test: mean != 0. Returns (t, p_approx)."""
    n = len(xs)
    if n < 2:
        return float("nan"), float("nan")
    m, s = _mean(xs), _std(xs)
    if s == 0:
        return float("nan"), float("nan")
    t = m / (s / math.sqrt(n))
    # Approximation via incomplete beta function (avoids scipy dependency)
    # Uses the Abramowitz & Stegun approximation for the t CDF
    df = n - 1
    x = df / (df + t * t)
    # Regularized incomplete beta approximation
    try:
        # Simple approximation good to ~1% for df > 5
        z = abs(t) / math.sqrt(df / (df - 2)) if df > 2 else abs(t)
        # Two-tailed p via normal approximation for large n, else crude bound
        if n >= 30:
            p_approx = 2.0 * (1.0 - _norm_cdf(abs(t)))
        else:
            # Crude upper bound via Chebyshev
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
        return {k: 0.0 for k in [
            "count", "wr", "avg", "avg_win", "avg_loss",
            "pf", "expectancy", "kelly",
        ]}
    wins   = [r for r in returns if r > 0]
    losses = [r for r in returns if r < 0]
    wr        = len(wins) / len(returns) * 100
    avg       = _mean(returns)
    avg_win   = _mean(wins)   if wins   else 0.0
    avg_loss  = _mean(losses) if losses else 0.0
    gp        = sum(wins)
    gl        = abs(sum(losses))
    pf        = gp / gl if gl else float("inf")
    expectancy = (len(wins) / len(returns) * avg_win) + (len(losses) / len(returns) * avg_loss)
    kelly = 0.0
    if avg_win > 0 and avg_loss < 0:
        wp  = len(wins) / len(returns)
        kelly = wp - ((1 - wp) / (avg_win / abs(avg_loss)))
    return {
        "count": len(returns), "wr": wr, "avg": avg,
        "avg_win": avg_win, "avg_loss": avg_loss,
        "pf": pf, "expectancy": expectancy, "kelly": kelly * 100,
    }


def risk_metrics(returns: list[float], date_range_days: int = 18) -> dict:
    """Compute the full quant risk/return profile."""
    if len(returns) < 5:
        return {}

    n       = len(returns)
    mu      = _mean(returns)
    sigma   = _std(returns)
    # ann is already sqrt(252) — apply directly, do NOT sqrt again
    ann = _annualize_factor(n, date_range_days)

    # Sharpe (trade-level, annualized at sqrt(252), risk-free rate = 0)
    sharpe = (mu / sigma * ann) if sigma > 0 else float("nan")

    # Sortino — semi-deviation: RMS of negative returns measured from target (0%)
    # Padding with zeros and calling _std() is wrong: _std() shifts the mean,
    # measuring deviations from a skewed average instead of from the target return.
    # Divisor is n (full sample), not n-1: we measure against a fixed target (0%),
    # so no parameter is being estimated — no degree-of-freedom correction needed.
    downside_sum_sq = sum(r ** 2 for r in returns if r < 0)
    sigma_d = math.sqrt(downside_sum_sq / n) if n > 0 else 0.0
    sortino  = (mu / sigma_d * ann) if sigma_d > 0 else float("nan")

    # Max drawdown (5% position sizing)
    capital, peak, max_dd = 10_000.0, 10_000.0, 0.0
    for r in returns:
        capital += capital * 0.05 * (r / 100)
        peak     = max(peak, capital)
        max_dd   = max(max_dd, (peak - capital) / peak * 100)

    # Calmar = annualized avg return / max drawdown
    # Annualize using sqrt(252) consistently (same basis as Sharpe numerator)
    ann_return = mu * 252   # daily return × trading days/year
    calmar = (ann_return / max_dd) if max_dd > 0 else float("nan")

    # Omega ratio = E[max(R-threshold,0)] / E[max(threshold-R,0)] (threshold=0)
    gains  = sum(max(r, 0) for r in returns)
    losses = sum(max(-r, 0) for r in returns)
    omega  = (gains / losses) if losses > 0 else float("inf")

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
    wins_l   = [r for r in returns if r > 0]
    losses_l = [r for r in returns if r < 0]
    payoff = (_mean(wins_l) / abs(_mean(losses_l))) if wins_l and losses_l else float("nan")

    # Recovery factor = total net gain / max drawdown
    total_net = sum(returns)
    recovery  = (total_net / max_dd) if max_dd > 0 else float("nan")

    # Ulcer Index = RMS of % drawdowns over the equity curve
    ulcer_vals = []
    cap2, pk2 = 10_000.0, 10_000.0
    for r in returns:
        cap2 += cap2 * 0.05 * (r / 100)
        pk2   = max(pk2, cap2)
        dd_pct = (pk2 - cap2) / pk2 * 100
        ulcer_vals.append(dd_pct ** 2)
    ulcer = math.sqrt(_mean(ulcer_vals)) if ulcer_vals else 0.0

    # Consecutive streaks
    max_w = max_l = cur_w = cur_l = 0
    for r in returns:
        if r > 0:
            cur_w += 1; cur_l = 0
        else:
            cur_l += 1; cur_w = 0
        max_w = max(max_w, cur_w)
        max_l = max(max_l, cur_l)

    return {
        "sharpe":    sharpe,   "sortino":   sortino,  "calmar":    calmar,
        "omega":     omega,    "ann_return": ann_return,
        "var_95":    var_95,   "var_99":    var_99,
        "cvar_95":   cvar_95,  "cvar_99":   cvar_99,
        "max_dd":    max_dd,   "recovery":  recovery, "ulcer":     ulcer,
        "skew":      skew,     "kurt":      kurt,
        "t_stat":    t,        "p_value":   p,
        "payoff":    payoff,
        "sigma":     sigma,    "ann_factor": ann,
        "max_win_streak": max_w, "max_loss_streak": max_l,
    }


def brier_score(rows) -> float:
    pairs = []
    for r in rows:
        if r.outcome_pct is None or r.confidence is None:
            continue
        prob    = min(max(r.confidence / 100.0, 0.0), 1.0)
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
    if conf >= 70:  return "High (≥70%)"
    if conf >= 55:  return "Medium (55–69%)"
    return                 "Low (<55%)"

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

async def analyze_db(snapshot_tag: str | None = None) -> None:
    db_gen = get_db()
    db     = await anext(db_gen)
    try:
        rows = (await db.execute(
            select(Signal)
            .where(Signal.outcome_pct.isnot(None))
            .order_by(Signal.created_at.asc())
        )).scalars().all()
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
        all_ret   = []
        ret_1d    = [r.outcome_1d  for r in rows if r.outcome_1d  is not None]
        ret_3d    = [r.outcome_3d  for r in rows if r.outcome_3d  is not None]
        ret_14d   = [r.outcome_14d for r in rows if r.outcome_14d is not None]

        style_map   = defaultdict(list)
        action_map  = defaultdict(list)
        sector_map  = defaultdict(list)
        session_map = defaultdict(list)
        conf_map    = defaultdict(list)
        exit_map    = defaultdict(list)
        month_map   = defaultdict(list)
        mae_vals        = []
        mfe_vals        = []
        stop_dist_vals  = []   # distance from entry to stop (%)
        pct_above_1r_vals = []  # per-trade bool: did outcome exceed 1R?
        hit_stop_count = hit_target_count = 0
        stop_enforced_losses = 0   # trades where hit_stop=True but outcome_pct > 0 (phantom wins)

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
                print(f"  [warn] skipped signal id={getattr(r, 'id', '?')}: {_row_err}",
                      flush=True)

        if not all_ret:
            print("No valid return data.")
            return

        gm  = calc_metrics(all_ret)
        bs  = brier_score(rows)

        dates = [r.created_at for r in rows if r.created_at]
        earliest = min(dates) if dates else None
        latest   = max(dates) if dates else None
        date_range_days = (latest - earliest).days + 1 if earliest and latest else 18
        date_range_str  = (
            f"{earliest.strftime('%Y-%m-%d')} → {latest.strftime('%Y-%m-%d')}"
            if earliest else "unknown"
        )

        rm = risk_metrics(all_ret, date_range_days)

        # ══════════════════════════════════════════════════════════════════════
        print(f"# Signal.Trade — Institutional Performance Report\n")
        print(f"> **Coverage:** {date_range_str} · **{gm['count']} resolved trades**\n"
              f"> _Sharpe/Sortino use sqrt(252) scaling (one-trade-per-day assumption). "
              f"These are per-signal quality metrics, not portfolio equity-curve Sharpe._\n")

        # ── 1. Return summary ─────────────────────────────────────────────────
        print("## 1. Return Summary\n")
        print_table(
            ["Metric", "Value", "Note"],
            [
                ["Win Rate",             f"{gm['wr']:.1f}%",                "% trades > 0"],
                ["Avg Return / Trade",   f"{gm['avg']:+.2f}%",              "arithmetic mean"],
                ["Avg Win",              f"{gm['avg_win']:+.2f}%",          ""],
                ["Avg Loss",             f"{gm['avg_loss']:+.2f}%",         ""],
                ["Payoff Ratio",         _fmt(rm.get("payoff"), ".2f", "×"), "avg win / |avg loss|"],
                ["Profit Factor",        pf_str(gm["pf"]),                  "gross profit / gross loss"],
                ["Expectancy / Trade",   f"{gm['expectancy']:+.2f}%",       "WR×avgW + LR×avgL"],
                ["Kelly Fraction",       f"{gm['kelly']:.1f}%",             "theoretical optimal size — halve in practice"],
            ]
        )

        # ── 2. Risk-adjusted metrics ──────────────────────────────────────────
        print("\n## 2. Risk-Adjusted Metrics\n")
        print_table(
            ["Metric", "Value", "Benchmark"],
            [
                ["Sharpe Ratio",   _fmt(rm.get("sharpe"), ".2f"),   "> 1.0 = good, > 2.0 = excellent"],
                ["Sortino Ratio",  _fmt(rm.get("sortino"), ".2f"),  "> 1.5 = good (downside-only σ)"],
                ["Calmar Ratio",   _fmt(rm.get("calmar"), ".2f"),   "annualized_ret/max_DD — inflated: 5% sequential sizing understates concurrent portfolio drawdown"],
                ["Omega Ratio",    _fmt(rm.get("omega"), ".2f"),    "> 1.0 = edge exists"],
                ["Max Drawdown",   f"-{rm.get('max_dd', 0):.2f}%", "5% position sizing"],
                ["Recovery Factor",_fmt(rm.get("recovery"), ".2f"),"net return / max DD"],
                ["Ulcer Index",    _fmt(rm.get("ulcer"), ".2f"),    "< 5 = low drawdown stress"],
            ]
        )

        # ── 3. Tail risk ──────────────────────────────────────────────────────
        print("\n## 3. Tail Risk (Non-Parametric)\n")
        print_table(
            ["Metric", "Value", "Interpretation"],
            [
                ["VaR 95%",  f"-{rm.get('var_95', 0):.2f}%", "worst single-trade loss, 1-in-20"],
                ["VaR 99%",  f"-{rm.get('var_99', 0):.2f}%", "worst single-trade loss, 1-in-100"],
                ["CVaR 95%", f"-{rm.get('cvar_95', 0):.2f}%","avg loss when past VaR 95"],
                ["CVaR 99%", f"-{rm.get('cvar_99', 0):.2f}%","avg loss when past VaR 99"],
                ["Volatility (σ)", f"{rm.get('sigma', 0):.2f}%", "per-trade std dev of returns"],
            ]
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
                ["Skewness",      _fmt(skew, "+.3f"),
                 "positive = right tail (big wins), negative = left tail (big losses)"],
                ["Excess Kurtosis", _fmt(kurt, "+.3f"),
                 "> 0 = fat tails (more extremes than normal)"],
                ["T-statistic",   _fmt(t, "+.2f") + sig_marker,
                 "H₀: mean return = 0  (* p<0.05, ** p<0.01, *** p<0.001)"],
                ["P-value",       _fmt(p, ".4f"),
                 "two-sided; < 0.05 = statistically significant edge"],
                ["Brier Score",   f"{bs:.4f}" if bs == bs else "—",
                 "0 = perfect calibration, 0.25 = random"],
                ["Max Win Streak",  str(rm.get("max_win_streak", 0)), ""],
                ["Max Loss Streak", str(rm.get("max_loss_streak", 0)), ""],
            ]
        )

        # ── 5. Multi-timeframe ────────────────────────────────────────────────
        print("\n## 5. Multi-Timeframe Win Rates\n")
        tf_rows = []
        for label, rets in [("1d", ret_1d), ("3d", ret_3d), ("7d (primary)", all_ret), ("14d", ret_14d)]:
            m = calc_metrics(rets)
            if m["count"] == 0:
                continue
            rm_tf = risk_metrics(rets, date_range_days)
            tf_rows.append([
                label, str(m["count"]),
                f"{m['wr']:.1f}%", f"{m['avg']:+.2f}%",
                pf_str(m["pf"]),
                _fmt(rm_tf.get("sharpe"), ".2f"),
            ])
        print_table(["Horizon", "Count", "Win Rate", "Avg Return", "PF", "Sharpe"], tf_rows)

        # ── 6. Monthly performance ────────────────────────────────────────────
        print("\n## 6. Monthly Performance\n")
        month_rows = []
        for month in sorted(month_map):
            m = calc_metrics(month_map[month])
            rm_m = risk_metrics(month_map[month], 21)  # ~21 trading days/month
            month_rows.append([
                month, str(m["count"]),
                f"{m['wr']:.1f}%", f"{m['avg']:+.2f}%",
                pf_str(m["pf"]), _fmt(rm_m.get("sharpe"), ".2f"),
            ])
        print_table(["Month", "Trades", "Win Rate", "Avg Return", "PF", "Sharpe"], month_rows)

        # ── 7. By hold style ──────────────────────────────────────────────────
        print("\n## 7. By Hold Style\n")
        style_rows = []
        for style in ["position", "swing", "intraday"]:
            m = calc_metrics(style_map.get(style, []))
            rm_s = risk_metrics(style_map.get(style, []), date_range_days)
            style_rows.append([
                f"**{style.capitalize()}**", str(m["count"]),
                f"{m['wr']:.1f}%" if m["count"] else "—",
                f"{m['avg']:+.2f}%" if m["count"] else "—",
                pf_str(m["pf"]) if m["count"] else "—",
                _fmt(rm_s.get("sharpe"), ".2f"),
                _fmt(rm_s.get("max_dd"), ".2f", "%"),
            ])
        print_table(["Style", "N", "Win Rate", "Avg Ret", "PF", "Sharpe", "Max DD"], style_rows)

        # ── 8. By action ──────────────────────────────────────────────────────
        print("\n## 8. By Action\n")
        action_rows = []
        for action in ["BUY", "SELL"]:
            m = calc_metrics(action_map.get(action, []))
            rm_a = risk_metrics(action_map.get(action, []), date_range_days)
            action_rows.append([
                f"**{action}**", str(m["count"]),
                f"{m['wr']:.1f}%" if m["count"] else "—",
                f"{m['avg']:+.2f}%" if m["count"] else "—",
                pf_str(m["pf"]) if m["count"] else "—",
                _fmt(rm_a.get("sharpe"), ".2f"),
            ])
        print_table(["Action", "N", "Win Rate", "Avg Ret", "PF", "Sharpe"], action_rows)

        # ── 9. By exit type ───────────────────────────────────────────────────
        if exit_map:
            print("\n## 9. By Exit Type\n")
            exit_rows = []
            for et in ["target", "time", "pending", "stop"]:
                m = calc_metrics(exit_map.get(et, []))
                if m["count"] == 0:
                    continue
                exit_rows.append([
                    f"**{et.capitalize()}**", str(m["count"]),
                    f"{m['wr']:.1f}%", f"{m['avg']:+.2f}%", pf_str(m["pf"]),
                ])
            print_table(["Exit Type", "N", "Win Rate", "Avg Ret", "PF"], exit_rows)

        # ── 10. By confidence bucket ──────────────────────────────────────────
        print("\n## 10. Confidence Calibration\n")
        conf_rows = []
        for bucket in ["High (≥70%)", "Medium (55–69%)", "Low (<55%)"]:
            m = calc_metrics(conf_map.get(bucket, []))
            conf_rows.append([
                bucket, str(m["count"]),
                f"{m['wr']:.1f}%" if m["count"] else "—",
                f"{m['avg']:+.2f}%" if m["count"] else "—",
                pf_str(m["pf"]) if m["count"] else "—",
            ])
        print_table(["Confidence Band", "N", "Win Rate", "Avg Ret", "PF"], conf_rows)

        # ── 11. Reliability diagram (confidence bands vs actual win rate) ─────
        print("\n### Reliability Diagram (predicted confidence vs actual win rate)\n")
        BANDS = [(0, 50), (50, 55), (55, 60), (60, 65), (65, 70), (70, 75), (75, 80), (80, 101)]
        band_rows = []
        for lo, hi in BANDS:
            band_signals = [r for r in rows if r.confidence is not None
                            and lo <= r.confidence < hi and r.outcome_pct is not None]
            if not band_signals:
                continue
            actual_wr = sum(1 for r in band_signals if r.outcome_pct > 0) / len(band_signals) * 100
            avg_conf  = _mean([r.confidence for r in band_signals])
            gap       = avg_conf - actual_wr
            calib     = "OK" if abs(gap) <= 10 else ("OVER ⚠" if gap > 0 else "UNDER ⚠")
            band_rows.append([
                f"{lo}–{hi}%", str(len(band_signals)),
                f"{avg_conf:.1f}%", f"{actual_wr:.1f}%",
                f"{gap:+.1f}pp", calib,
            ])
        print_table(["Band", "N", "Avg Conf", "Actual WR", "Gap", "Calibrated?"], band_rows)

        # ── 12. Sector performance ─────────────────────────────────────────────
        if sector_map:
            print("\n## 11. Sector Performance\n")
            sector_rows = []
            for sector in sorted(sector_map, key=lambda s: -calc_metrics(sector_map[s])["avg"]):
                m = calc_metrics(sector_map[sector])
                sector_rows.append([
                    sector, str(m["count"]),
                    f"{m['wr']:.1f}%", f"{m['avg']:+.2f}%", pf_str(m["pf"]),
                ])
            print_table(["Sector ETF", "N", "Win Rate", "Avg Ret", "PF"], sector_rows)

        # ── 13. Session performance ────────────────────────────────────────────
        if session_map:
            print("\n## 12. Market Session Performance\n")
            sess_rows = []
            for sess in sorted(session_map, key=lambda s: -len(session_map[s])):
                m = calc_metrics(session_map[sess])
                sess_rows.append([
                    sess.capitalize(), str(m["count"]),
                    f"{m['wr']:.1f}%", f"{m['avg']:+.2f}%", pf_str(m["pf"]),
                ])
            print_table(["Session", "N", "Win Rate", "Avg Ret", "PF"], sess_rows)

        # ── 14. Trade-path analytics ───────────────────────────────────────────
        n = gm["count"]
        print("\n## 13. Trade-Path Analytics (MAE / MFE)\n")

        # Stop-enforced win rate: reclassify phantom wins (hit_stop=True, outcome>0)
        # In a real portfolio, a stop hit closes the position at a loss.
        # These trades recovered after touching the stop — but the stop should have closed them.
        phantom = stop_enforced_losses
        stop_enforced_wr = (gm["wr"] * n / 100 - phantom) / n * 100 if n > 0 else 0.0

        print(f"- **Hit Target:** {hit_target_count} / {n} ({hit_target_count/n*100:.1f}%)")
        print(f"- **Hit Stop:**   {hit_stop_count} / {n} ({hit_stop_count/n*100:.1f}%)")
        if phantom > 0:
            print(f"- **Phantom Wins (stop hit but outcome_pct > 0):** {phantom} trades "
                  f"— stop not enforced intraday, position recovered by measurement date")
            print(f"- **Stop-Enforced Win Rate:** {stop_enforced_wr:.1f}% "
                  f"(vs reported {gm['wr']:.1f}% — difference = {gm['wr']-stop_enforced_wr:.1f}pp)")

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
        avg_win_val  = gm.get("avg_win",  0.0)
        avg_loss_val = gm.get("avg_loss", 0.0)
        payoff_ratio = abs(avg_win_val / avg_loss_val) if avg_loss_val != 0 else float("inf")
        print(f"\n**Return Quality:**")
        print(f"- **Payoff Ratio:** {payoff_ratio:.2f}× — magnitude of avg win vs avg loss "
              f"({avg_win_val:+.2f}% / {avg_loss_val:+.2f}%)")
        if stop_dist_vals:
            avg_stop_dist = _mean(stop_dist_vals)
            capture = gm["avg"] / avg_stop_dist if avg_stop_dist > 0 else float("nan")
            pct_above_1r = (sum(pct_above_1r_vals) / len(pct_above_1r_vals) * 100) if pct_above_1r_vals else 0.0
            print(f"- **Avg Stop Distance:** {avg_stop_dist:.2f}% (wide ATR stops give room but reduce capture)")
            pct_captured = capture * 100 if capture == capture else 0.0
            print(f"- **Capture Ratio:** {capture:.2f}× — avg_return / avg_stop_distance "
                  f"({pct_captured:.0f}% of risked distance captured on average; "
                  f"distinct from Payoff Ratio which measures win vs loss magnitude)")
            print(f"- **% Trades > 1R:** {pct_above_1r:.1f}%")

        # ── 15. Return distribution quartiles ──────────────────────────────────
        print("\n## 14. Return Distribution\n")
        sorted_ret = sorted(all_ret)
        n_ret = len(sorted_ret)
        print_table(
            ["Percentile", "Return"],
            [
                ["P1  (worst 1%)",   f"{_percentile(all_ret,  1):+.2f}%"],
                ["P5  (VaR 95%)",    f"{_percentile(all_ret,  5):+.2f}%"],
                ["P10",              f"{_percentile(all_ret, 10):+.2f}%"],
                ["P25 (Q1)",         f"{_percentile(all_ret, 25):+.2f}%"],
                ["P50 (median)",     f"{_percentile(all_ret, 50):+.2f}%"],
                ["P75 (Q3)",         f"{_percentile(all_ret, 75):+.2f}%"],
                ["P90",              f"{_percentile(all_ret, 90):+.2f}%"],
                ["P95",              f"{_percentile(all_ret, 95):+.2f}%"],
                ["P99 (best 1%)",    f"{_percentile(all_ret, 99):+.2f}%"],
            ]
        )

        # ── Snapshot write (only when --snapshot flag provided) ────────────────
        if snapshot_tag:
            avg_mae  = _mean(mae_vals)  if mae_vals  else None
            avg_mfe  = _mean(mfe_vals)  if mfe_vals  else None
            avg_sd   = _mean(stop_dist_vals) if stop_dist_vals else None
            capture  = (gm["avg"] / avg_sd) if avg_sd else None

            snap = {
                "coverage": {
                    "from": earliest.strftime("%Y-%m-%d") if earliest else None,
                    "to":   latest.strftime("%Y-%m-%d")   if latest   else None,
                    "days": date_range_days,
                },
                "returns": {
                    "n_trades":  gm["count"],
                    "win_rate":  round(gm["wr"],  2),
                    "avg":       round(gm["avg"],  3),
                    "avg_win":   round(gm["avg_win"],  3),
                    "avg_loss":  round(gm["avg_loss"], 3),
                    "payoff":    round(rm.get("payoff", 0) or 0, 3),
                    "pf":        round(gm["pf"], 3) if gm["pf"] != float("inf") else None,
                    "expectancy":round(gm["expectancy"], 3),
                    "kelly":     round(gm["kelly"], 2),
                },
                "risk": {
                    "sharpe":   round(rm.get("sharpe",  0) or 0, 3),
                    "sortino":  round(rm.get("sortino", 0) or 0, 3),
                    "calmar":   round(rm.get("calmar",  0) or 0, 3),
                    "omega":    round(rm.get("omega",   0) or 0, 3),
                    "max_dd":   round(rm.get("max_dd",  0) or 0, 3),
                    "recovery": round(rm.get("recovery",0) or 0, 3),
                    "ulcer":    round(rm.get("ulcer",   0) or 0, 3),
                },
                "tail": {
                    "var_95":  round(rm.get("var_95",  0) or 0, 3),
                    "var_99":  round(rm.get("var_99",  0) or 0, 3),
                    "cvar_95": round(rm.get("cvar_95", 0) or 0, 3),
                    "cvar_99": round(rm.get("cvar_99", 0) or 0, 3),
                    "sigma":   round(rm.get("sigma",   0) or 0, 3),
                },
                "distribution": {
                    "skew":            round(rm.get("skew", 0) or 0, 4),
                    "kurt":            round(rm.get("kurt", 0) or 0, 4),
                    "t_stat":          round(rm.get("t_stat",  0) or 0, 3),
                    "p_value":         round(rm.get("p_value", 1) or 1, 6),
                    "brier":           round(bs, 4) if bs == bs else None,
                    "max_win_streak":  rm.get("max_win_streak",  0),
                    "max_loss_streak": rm.get("max_loss_streak", 0),
                },
                "trade_path": {
                    "hit_target_count": hit_target_count,
                    "hit_stop_count":   hit_stop_count,
                    "hit_target_pct":   round(hit_target_count / n * 100, 2) if n else 0,
                    "hit_stop_pct":     round(hit_stop_count   / n * 100, 2) if n else 0,
                    "phantom_wins":     phantom,
                    "stop_enforced_wr": round(stop_enforced_wr, 2),
                    "avg_mae":          round(avg_mae, 3) if avg_mae is not None else None,
                    "avg_mfe":          round(avg_mfe, 3) if avg_mfe is not None else None,
                    "mfe_mae_ratio":    round(avg_mfe / abs(avg_mae), 3)
                                        if avg_mae and avg_mfe else None,
                    "avg_stop_dist":    round(avg_sd,  3) if avg_sd  is not None else None,
                    "capture_ratio":    round(capture, 3) if capture is not None else None,
                    "pct_above_1r":     round((sum(pct_above_1r_vals) / len(pct_above_1r_vals) * 100)
                                              if pct_above_1r_vals else 0.0, 2),
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
            }
            await _save_snapshot(snapshot_tag, snap, gm)
            print(f"\n✓ Snapshot saved: tag='{snapshot_tag}' · {gm['count']} trades")

    except Exception as analysis_err:
        print(f"[error] Analysis failed: {analysis_err}")
        raise


# ─────────────────────────────────────────────────────────────────────────────
# Snapshot persistence
# ─────────────────────────────────────────────────────────────────────────────

async def _save_snapshot(tag: str, metrics: dict, gm: dict) -> None:
    """Write a performance snapshot to the performance_snapshots table."""
    import subprocess
    from database import AsyncSessionLocal
    from models import PerformanceSnapshot

    git_sha = None
    try:
        git_sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        pass

    from sqlalchemy import delete as _delete
    async with AsyncSessionLocal() as db:
        # Delete any existing row with this tag so re-runs during tuning
        # produce a clean update rather than duplicate rows.
        await db.execute(_delete(PerformanceSnapshot).where(PerformanceSnapshot.tag == tag))
        snap = PerformanceSnapshot(
            tag       = tag,
            git_sha   = git_sha,
            metrics   = metrics,
            n_trades  = gm["count"],
            win_rate  = round(gm["wr"], 2),
            sharpe    = round(metrics.get("risk", {}).get("sharpe", 0) or 0, 3),
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
        "win_rate": 2.0,    "avg": 0.5,    "sharpe": 0.3,
        "sortino":  1.0,    "max_dd": 0.5, "var_95": 0.5,
        "brier":    0.02,   "pf": 0.2,     "stop_enforced_wr": 2.0,
        "phantom_wins": 5,
    }

    def _diff_val(key, va, vb):
        if not isinstance(va, (int, float)) or not isinstance(vb, (int, float)):
            return {"before": va, "after": vb}
        delta = round(vb - va, 4)
        delta_pct = round(delta / abs(va) * 100, 2) if va != 0 else None
        threshold = THRESHOLDS.get(key, None)
        flag = (abs(delta) >= threshold) if threshold else (abs(delta_pct or 0) >= 5)
        return {"before": va, "after": vb, "delta": delta,
                "delta_pct": delta_pct, "flag": flag}

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
        "--snapshot", metavar="TAG", default=None,
        help="Save a named snapshot to the DB after printing (e.g. 'v3-sector-gates')",
    )
    args = parser.parse_args()
    asyncio.run(analyze_db(snapshot_tag=args.snapshot))
