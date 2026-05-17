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

def _annualize_factor(n_trades: int, date_range_days: int) -> float:
    """Trades per year given observed trade frequency."""
    if date_range_days <= 0 or n_trades <= 0:
        return 252.0
    trades_per_day = n_trades / date_range_days
    return trades_per_day * 252


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
    ann     = _annualize_factor(n, date_range_days)
    sqrt_ann = math.sqrt(ann)

    # Sharpe (trade-level, annualized, assuming 0% risk-free rate)
    sharpe = (mu / sigma * sqrt_ann) if sigma > 0 else float("nan")

    # Sortino — only penalise downside
    downside = [r for r in returns if r < 0]
    sigma_d  = _std(downside + [0.0] * (n - len(downside)), ddof=1)
    sortino  = (mu / sigma_d * sqrt_ann) if sigma_d > 0 else float("nan")

    # Max drawdown (5% position sizing)
    capital, peak, max_dd = 10_000.0, 10_000.0, 0.0
    for r in returns:
        capital += capital * 0.05 * (r / 100)
        peak     = max(peak, capital)
        max_dd   = max(max_dd, (peak - capital) / peak * 100)

    # Calmar  = annualized avg return / max drawdown
    ann_return = mu * ann
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

async def analyze_db() -> None:
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
        mae_vals    = []
        mfe_vals    = []
        realized_rr = []
        hit_stop_count = hit_target_count = 0

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
                if r.hit_target:
                    hit_target_count += 1
                # Realized R:R (actual outcome / distance to stop)
                if r.entry and r.stop and r.entry > 0 and r.stop > 0 and r.outcome_pct is not None:
                    try:
                        risk_pct = abs(float(r.entry) - float(r.stop)) / float(r.entry) * 100
                        if risk_pct > 0:
                            realized_rr.append(ret / risk_pct)
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
        print(f"> **Coverage:** {date_range_str} · **{gm['count']} resolved trades** "
              f"· annualization factor: {rm.get('ann_factor', 252):.0f}×/yr\n")

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
                ["Kelly Fraction",       f"{gm['kelly']:.1f}%",             "optimal position size"],
                ["Annualized Return",    _fmt(rm.get("ann_return"), "+.1f", "%"), "avg × ann factor"],
            ]
        )

        # ── 2. Risk-adjusted metrics ──────────────────────────────────────────
        print("\n## 2. Risk-Adjusted Metrics\n")
        print_table(
            ["Metric", "Value", "Benchmark"],
            [
                ["Sharpe Ratio",   _fmt(rm.get("sharpe"), ".2f"),   "> 1.0 = good, > 2.0 = excellent"],
                ["Sortino Ratio",  _fmt(rm.get("sortino"), ".2f"),  "> 1.5 = good (downside-only σ)"],
                ["Calmar Ratio",   _fmt(rm.get("calmar"), ".2f"),   "> 0.5 = acceptable"],
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
        print(f"- **Hit Target:** {hit_target_count} / {n} ({hit_target_count/n*100:.1f}%)")
        print(f"- **Hit Stop:**   {hit_stop_count} / {n} ({hit_stop_count/n*100:.1f}%)")
        if mae_vals:
            avg_mae = _mean(mae_vals)
            print(f"- **Avg MAE:**  {avg_mae:+.2f}%  | worst: {min(mae_vals):+.2f}%")
        if mfe_vals:
            avg_mfe = _mean(mfe_vals)
            print(f"- **Avg MFE:**  {avg_mfe:+.2f}%  | best: {max(mfe_vals):+.2f}%")
        if mae_vals and mfe_vals:
            mfe_mae = avg_mfe / abs(avg_mae) if avg_mae != 0 else float("inf")
            print(f"- **MFE/MAE Ratio:** {mfe_mae:.2f}×  (>1 = moves right before reversing)")
        if realized_rr:
            avg_rrr = _mean(realized_rr)
            print(f"- **Realized R:R:** {avg_rrr:.2f}×  (actual outcome / stop distance)")
            pct_above_1 = sum(1 for v in realized_rr if v > 1) / len(realized_rr) * 100
            print(f"- **% Trades > 1R:** {pct_above_1:.1f}%")

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

    except Exception as analysis_err:
        print(f"[error] Analysis failed: {analysis_err}")
        raise


if __name__ == "__main__":
    asyncio.run(analyze_db())
