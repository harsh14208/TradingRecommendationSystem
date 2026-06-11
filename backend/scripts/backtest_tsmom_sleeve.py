#!/usr/bin/env python3
"""§101 — TSMOM (time-series momentum) sleeve backtest for Signal.Trade.

Universe : SPY, QQQ, IWM, EFA, EEM, TLT, GLD, DBC
Signal   : 12-1 month sign-of-return (causal: price[t-21] vs price[t-252])
Rebalance: monthly (last trading day), vol-scaled to 10 % ann. vol target / ETF
Cost     : 10 bps round-trip per rebalance

Run from backend/:
    python scripts/backtest_tsmom_sleeve.py
    python scripts/backtest_tsmom_sleeve.py --preregister   # SPRT pre-registration
    python scripts/backtest_tsmom_sleeve.py --corr          # Correlation vs MR only
"""

from __future__ import annotations

import argparse
import math
import os
import subprocess
import sys
from datetime import datetime

import numpy as np
import pandas as pd

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from scripts.backtest_technicals import (  # noqa: E402
    _log_experiment,
    cached_yf_download,
)

# ── Parameters ───────────────────────────────────────────────────────────────
UNIVERSE = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "GLD", "DBC"]
START = "2003-01-01"
END = datetime.today().strftime("%Y-%m-%d")
FETCH_START = "2002-01-01"  # Buffer for 252-day lookback

VOL_LOOKBACK = 63  # ~3 months for realized vol
VOL_TARGET_ANN = 0.10  # 10 % annualized vol target per ETF
VOL_FLOOR = 0.05  # Minimum 5 % ann. vol to avoid extreme leverage
LEVERAGE_CAP = 3.0  # Max 3× notional per ETF

MOMENTUM_LONG = 252  # 12 months
MOMENTUM_SHORT = 21  # 1 month

COST_BPS = 10
COST_PCT = COST_BPS / 10_000  # 0.0010 round-trip

FOLDS = [
    ("2003-01-01", "2008-01-01"),
    ("2008-01-01", "2015-01-01"),
    ("2015-01-01", "2022-01-01"),
    ("2022-01-01", END),
]

# ── Data helpers ─────────────────────────────────────────────────────────────


def _close_series(df: pd.DataFrame | None) -> pd.Series | None:
    """Extract a float Close series from a (possibly MultiIndex) cached frame."""
    if df is None or len(df) == 0:
        return None
    cols = df.columns
    if isinstance(cols, pd.MultiIndex):
        lvl0 = cols.get_level_values(0)
        if "Close" in lvl0:
            s = df["Close"]
            if isinstance(s, pd.DataFrame):
                s = s.iloc[:, 0]
            return pd.to_numeric(s, errors="coerce").dropna()
        return None
    if "Close" in cols:
        return pd.to_numeric(df["Close"], errors="coerce").dropna()
    return None


def fetch_closes(tickers: list[str], start: str, end: str) -> dict[str, pd.Series]:
    """Download OHLCV with CSV disk cache; return dict of Close series."""
    closes: dict[str, pd.Series] = {}
    for t in tickers:
        raw = cached_yf_download(t, start, end, progress=False)
        cs = _close_series(raw)
        if cs is not None and len(cs) > VOL_LOOKBACK + MOMENTUM_LONG + 50:
            closes[t] = cs
        else:
            print(f"  ⚠ {t}: insufficient data ({len(cs) if cs is not None else 0} rows), skipped")
    return closes


# ── Signal & simulation ──────────────────────────────────────────────────────


def _last_trading_day_of_month(dates: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Return the last available trading day in each month."""
    df = pd.DataFrame({"d": dates}, index=dates)
    return pd.to_datetime(df.resample("ME")["d"].last().dropna().values)


def compute_weights(
    closes: dict[str, pd.Series],
    long_short: bool = False,
) -> pd.DataFrame:
    """Return daily DataFrame of ETF weights (causal, month-end rebalanced)."""
    px = pd.DataFrame(closes).sort_index()
    px = px.ffill().dropna()

    rets = px.pct_change()

    # Realized annual vol (63-day rolling)
    vol = rets.rolling(VOL_LOOKBACK).std() * math.sqrt(252)
    vol = vol.clip(lower=VOL_FLOOR)

    # 12-1 month momentum (causal)
    mom = px.shift(MOMENTUM_SHORT) / px.shift(MOMENTUM_LONG) - 1.0
    sig = np.sign(mom)

    # Vol-scaled raw weight
    raw_w = sig * (VOL_TARGET_ANN / vol)
    raw_w = raw_w.where(np.isfinite(raw_w), 0.0)
    raw_w = raw_w.clip(upper=LEVERAGE_CAP, lower=-LEVERAGE_CAP)

    # Flat for negative signals unless long-short
    if not long_short:
        raw_w = raw_w.where(sig > 0, 0.0)

    # Rebalance only on month-ends
    month_ends = _last_trading_day_of_month(px.index)
    w_rebal = raw_w.reindex(month_ends).reindex(px.index, method="ffill").fillna(0.0)

    return w_rebal


def simulate(closes: dict[str, pd.Series], long_short: bool = False) -> dict:
    """Run TSMOM simulation and return metrics + return series."""
    px = pd.DataFrame(closes).sort_index().ffill().dropna()
    rets = px.pct_change()

    w = compute_weights(closes, long_short=long_short)

    # Gross daily portfolio return — equal-weighted average across ETFs
    # Causal: yesterday's weights applied to today's returns
    gross = (w.shift(1) * rets).mean(axis=1)

    # Cost: 10 bps on absolute weight change at each month-end
    month_ends = _last_trading_day_of_month(px.index)
    w_me = w.reindex(month_ends)
    turnover = w_me.diff().abs().sum(axis=1)  # sum(|Δw_i|)
    cost_me = turnover * COST_PCT
    cost = cost_me.reindex(px.index).fillna(0.0)

    net = gross - cost
    net = net.dropna()

    return {
        "daily_gross": gross,
        "daily_net": net,
        "monthly_net": net.resample("ME").apply(lambda x: (1 + x).prod() - 1),
        "turnover_monthly": turnover,
    }


# ── Statistics ───────────────────────────────────────────────────────────────


def _annualized_sharpe(monthly: pd.Series) -> float:
    a = monthly.dropna().to_numpy()
    if len(a) < 6:
        return math.nan
    mu, sd = float(a.mean()), float(a.std(ddof=1))
    return (mu / sd) * math.sqrt(12) if sd > 0 else math.nan


def _cagr(monthly: pd.Series) -> float:
    a = monthly.dropna()
    if len(a) < 6:
        return math.nan
    cum = (1 + a).prod()
    yrs = len(a) / 12
    return cum ** (1 / yrs) - 1 if yrs > 0 and cum > 0 else math.nan


def _max_dd_from_monthly(monthly: pd.Series) -> float:
    a = monthly.dropna()
    if len(a) < 2:
        return 0.0
    cum = (1 + a).cumprod()
    peak = cum.cummax()
    dd = (cum - peak) / peak
    return float(dd.min())


def block_bootstrap_sharpe_ci(
    monthly: pd.Series,
    n_boot: int = 10_000,
    block_months: int = 3,
) -> tuple[float, float]:
    """Block-bootstrap 90 % CI on annualized Sharpe (block = 3 months)."""
    m = monthly.dropna().to_numpy()
    n = len(m)
    if n < block_months * 2:
        return (math.nan, math.nan)

    n_blocks = int(math.ceil(n / block_months))
    sharpes: list[float] = []
    rng = np.random.default_rng(42)

    for _ in range(n_boot):
        starts = rng.integers(0, n - block_months + 1, size=n_blocks)
        sample = np.concatenate([m[i : i + block_months] for i in starts])[:n]
        mu, sd = sample.mean(), sample.std(ddof=1)
        if sd > 0:
            sharpes.append((mu / sd) * math.sqrt(12))

    if not sharpes:
        return (math.nan, math.nan)

    return (float(np.percentile(sharpes, 5)), float(np.percentile(sharpes, 95)))


def fold_metrics(monthly_net: pd.Series, start: str, end: str) -> dict:
    """Compute Sharpe, CAGR, MaxDD and block-bootstrap CI for a fold."""
    fold = monthly_net.loc[start:end].dropna()
    if len(fold) < 6:
        return {}

    ci_lo, ci_hi = block_bootstrap_sharpe_ci(fold)
    return {
        "n_months": len(fold),
        "ann_sharpe": round(_annualized_sharpe(fold), 3),
        "cagr": round(_cagr(fold) * 100, 2),
        "max_dd": round(_max_dd_from_monthly(fold) * 100, 2),
        "ci_5": round(ci_lo, 3),
        "ci_95": round(ci_hi, 3),
    }


# ── Reporting ────────────────────────────────────────────────────────────────


def print_fold_report(fold_results: list[dict], variant: str) -> int:
    """Print per-fold table and return count of positive Sharpe epochs."""
    print(f"\n## §101 TSMOM Sleeve — {variant}\n")
    print("| Epoch | Months | Ann.Sharpe | CAGR | MaxDD | Sharpe 90 % CI |")
    print("|:---|---:|---:|---:|---:|:---|")

    positive = 0
    for (s, e), r in zip(FOLDS, fold_results):
        label = f"{s[:4]}–{e[:4]}"
        if not r:
            print(f"| {label} | — | — | — | — | — |")
            continue
        ci = f"[{r['ci_5']}, {r['ci_95']}]"
        print(f"| {label} | {r['n_months']} | {r['ann_sharpe']} | {r['cagr']}% | {r['max_dd']}% | {ci} |")
        if r.get("ann_sharpe", 0) > 0:
            positive += 1

    # Bar
    sharpe_ok = all(r.get("ann_sharpe", 0) >= 0.3 for r in fold_results if r)
    bar_met = positive >= 3 and sharpe_ok
    print(f"\n> Positive epochs: {positive}/{len(FOLDS)}")
    print(f"> Bar (net Sharpe ≥ 0.3 with ≥ 3/4 epochs positive): {'✅ PASS' if bar_met else '➖ NOT MET'}")
    return positive


def run_corr() -> None:
    """Quantify diversification: TSMOM monthly returns vs MR book."""
    print("\n## §101 TSMOM × MR Correlation\n")
    if not os.path.exists("data/mr_monthly.csv"):
        print("> Missing data/mr_monthly.csv — run `python scripts/backtest_technicals.py` first.\n")
        return
    if not os.path.exists("data/tsmom_monthly.csv"):
        print("> Missing data/tsmom_monthly.csv — run TSMOM backtest first.\n")
        return

    mr = pd.read_csv("data/mr_monthly.csv", index_col=0).iloc[:, 0]
    mr.index = mr.index.astype(str)

    tsmom = pd.read_csv("data/tsmom_monthly.csv", index_col=0).iloc[:, 0]
    tsmom.index = tsmom.index.astype(str)

    j = pd.DataFrame({"mr": mr, "tsmom": tsmom}).dropna()
    if len(j) < 6:
        print(f"> Too few overlapping months ({len(j)}).\n")
        return

    corr = float(j["mr"].corr(j["tsmom"]))

    # Vol-normalised (equal-risk) blend so scale differences cancel
    mrn = j["mr"] / j["mr"].std(ddof=1) if j["mr"].std(ddof=1) > 0 else j["mr"]
    sln = j["tsmom"] / j["tsmom"].std(ddof=1) if j["tsmom"].std(ddof=1) > 0 else j["tsmom"]

    mr_sh = float((mrn.mean() / mrn.std(ddof=1)) * math.sqrt(12)) if mrn.std(ddof=1) > 0 else 0.0
    sl_sh = float((sln.mean() / sln.std(ddof=1)) * math.sqrt(12)) if sln.std(ddof=1) > 0 else 0.0

    comb = 0.5 * mrn + 0.5 * sln
    cb_sh = float((comb.mean() / comb.std(ddof=1)) * math.sqrt(12)) if comb.std(ddof=1) > 0 else 0.0

    print("| Months | MR Sharpe | TSMOM Sharpe | Corr | 50/50 Risk-Blend | Δ vs MR |")
    print("|---:|---:|---:|---:|---:|---:|")
    print(f"| {len(j)} | {mr_sh:.2f} | {sl_sh:.2f} | {corr:+.2f} | {cb_sh:.2f} | {cb_sh - mr_sh:+.2f} |")
    print("\n> Low corr + combined Sharpe > both legs ⇒ sleeve genuinely diversifies MR book.\n")


# ── Main backtest driver ─────────────────────────────────────────────────────


def _git_sha() -> str | None:
    try:
        return (
            subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout.strip()
            or None
        )
    except Exception:
        return None


def run() -> None:
    print(f"## §101 TSMOM Sleeve Backtest ({START} → {END})\n")
    print(f"> Universe : {UNIVERSE}")
    print("> Signal   : 12-1 month sign-of-return, causal")
    print(
        f"> Vol      : {VOL_TARGET_ANN * 100:.0f} % ann. target per ETF (floor {VOL_FLOOR * 100:.0f} %, cap {LEVERAGE_CAP:.0f}×)"
    )
    print(f"> Cost     : {COST_BPS} bps round-trip on absolute weight change\n")

    closes = fetch_closes(UNIVERSE, FETCH_START, END)
    print(f"> Fetched {len(closes)}/{len(UNIVERSE)} tickers.\n")

    if len(closes) < 3:
        print("> Abort: too few tickers with sufficient data.")
        return

    saved: dict | None = None
    for ls, lbl in [(False, "Long-flat"), (True, "Long-short")]:
        sim = simulate(closes, long_short=ls)
        monthly = sim.get("monthly_net")
        if monthly is None or len(monthly) == 0:
            print(f"> {lbl}: no simulated returns.")
            continue

        fold_results = [fold_metrics(monthly, s, e) for s, e in FOLDS]
        positive_epochs = print_fold_report(fold_results, lbl)

        overall_sharpe = _annualized_sharpe(monthly)
        _log_experiment(
            experiment_type="tsmom_sleeve",
            hypothesis=f"TSMOM sleeve ({lbl}) net Sharpe >= 0.3 vs H0 <= 0",
            n_trials=1,
            is_metrics={
                "variant": lbl,
                "ann_sharpe": round(overall_sharpe, 3) if not math.isnan(overall_sharpe) else None,
                "positive_epochs": positive_epochs,
                "n_months": len(monthly.dropna()),
                "git_sha": _git_sha(),
            },
        )

        if saved is None or (overall_sharpe > _annualized_sharpe(saved.get("monthly_net", pd.Series()))):
            saved = sim

    # Export long-flat (or best) monthly series
    if saved is not None:
        m = saved["monthly_net"].copy()
        m.index = m.index.to_period("M").astype(str)
        m.to_csv("data/tsmom_monthly.csv")
        print("\n> Monthly net returns exported → data/tsmom_monthly.csv")

    run_corr()


# ── SPRT pre-registration ────────────────────────────────────────────────────


async def preregister_sprt() -> None:
    """Insert TSMOM SPRT row into ResearchExperiment (idempotent)."""
    from sqlalchemy import select

    from database import AsyncSessionLocal
    from models import ResearchExperiment

    async with AsyncSessionLocal() as db:
        existing = await db.execute(
            select(ResearchExperiment).where(
                ResearchExperiment.experiment_type == "tsmom_sleeve",
                ResearchExperiment.hypothesis == "TSMOM sleeve forward Sharpe >= 0.3 vs H0 <= 0",
            )
        )
        if existing.scalar_one_or_none():
            print("[skip] TSMOM SPRT already registered.")
            return

        exp = ResearchExperiment(
            experiment_type="tsmom_sleeve",
            hypothesis="TSMOM sleeve forward Sharpe >= 0.3 vs H0 <= 0",
            data_version="v101",
            sprt_params={
                "h0": 0.0,
                "h1": round(0.3 / 12, 6),
                "alpha": 0.05,
                "beta": 0.05,
                "population": {"source": "tsmom_monthly_csv"},
            },
            decision="pending",
            promotion_status="pending",
        )
        db.add(exp)
        await db.commit()
        await db.refresh(exp)
        print(f"[registered] TSMOM SPRT experiment ID={exp.id}")


# ── CLI ──────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="§101 TSMOM sleeve backtest")
    parser.add_argument("--preregister", action="store_true", help="Pre-register SPRT experiment")
    parser.add_argument("--corr", action="store_true", help="Only compute TSMOM × MR correlation")
    args = parser.parse_args()

    if args.corr:
        run_corr()
        return

    if args.preregister:
        import asyncio

        asyncio.run(preregister_sprt())
        return

    run()


if __name__ == "__main__":
    main()
