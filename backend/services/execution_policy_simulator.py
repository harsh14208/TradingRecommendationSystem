"""
QENG-3d execution-policy simulator.

Compares how the same signal book would have performed under different
entry/execution policies (market, limit, midpoint, next-open, next-close,
delayed-1d) on a cost-adjusted basis. Returns a summary table and per-trade
detail so promotion decisions are grounded in expected value, not just gross
return.

The simulator is intentionally simple: it re-prices the entry using historical
OHLCV and re-applies the same exit price / hold horizon from the baseline
trade. It does not re-run the full exit logic, so it is suitable for fast
policy screening, not final backtest replacement.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

log = logging.getLogger("signal.trade.execution_policy")

Policy = Literal["market", "limit", "midpoint", "next_open", "next_close", "delayed_1d"]
DEFAULT_POLICIES: list[Policy] = ["market", "limit", "midpoint", "next_open", "next_close", "delayed_1d"]


@dataclass
class PolicySummary:
    policy: str
    n_total: int
    n_filled: int
    fill_rate: float
    avg_gross_bps: float
    avg_net_bps: float
    win_rate: float
    gross_sharpe_annual: float | None
    net_sharpe_annual: float | None
    avg_entry_slippage_bps: float
    notes: str = ""


@dataclass
class SimulationResult:
    summaries: list[PolicySummary] = field(default_factory=list)
    per_trade: list[dict] = field(default_factory=list)


def _annualisation_factor(hold_days: pd.Series | np.ndarray) -> float:
    """Infer annualisation from median hold horizon."""
    median_days = float(np.nanmedian(hold_days)) if len(hold_days) else 5.0
    if not median_days or np.isnan(median_days) or median_days <= 0:
        median_days = 5.0
    return float(np.sqrt(252 / median_days))


def _safe_date_index(df: pd.DataFrame, dt: pd.Timestamp) -> pd.Timestamp | None:
    """Return the first index >= dt, or None if dt is outside the data range."""
    if df.empty:
        return None
    if dt < df.index.min() or dt > df.index.max():
        return None
    try:
        idx = df.index.get_indexer([dt], method="bfill")[0]
        if idx == -1:
            return None
        return df.index[idx]
    except Exception:
        return None


def _entry_bar_for_date(df: pd.DataFrame, dt: pd.Timestamp) -> pd.Series | None:
    idx = _safe_date_index(df, dt)
    return df.loc[idx] if idx is not None else None


def _next_bar_for_date(df: pd.DataFrame, dt: pd.Timestamp) -> pd.Series | None:
    idx = _safe_date_index(df, dt)
    if idx is None:
        return None
    pos = df.index.get_loc(idx)
    if isinstance(pos, slice):
        pos = pos.start
    nxt = int(pos) + 1
    if nxt >= len(df):
        return None
    return df.iloc[nxt]


def _compute_gross(action: str, entry: float, exit_price: float) -> float:
    if action.upper() == "BUY":
        return (exit_price - entry) / entry * 100.0
    return (entry - exit_price) / entry * 100.0


def _sharpe(returns: np.ndarray, annualisation: float) -> float | None:
    arr = np.asarray(returns, dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) < 2:
        return None
    std = arr.std(ddof=1)
    if std == 0 or np.isnan(std):
        return None
    return float(arr.mean() / std * annualisation)


def simulate_trade(
    trade: dict,
    ohlcv: pd.DataFrame,
    policy: Policy,
    *,
    friction_pct: float = 0.50,
    limit_atr_frac: float = 0.5,
    passive_friction_discount: float = 0.5,
) -> dict:
    """
    Return cost-adjusted outcome for a single trade under ``policy``.

    ``trade`` must contain at least:
      - ticker, action (BUY/SELL)
      - entry_date / exit_date as pd.Timestamp or ISO string
      - entry_price, exit_price
      - atr_pct (optional; required for limit policy)
    """
    action = str(trade.get("action", "BUY")).upper()
    base_entry = float(trade["entry_price"])
    exit_price = float(trade["exit_price"])
    signal_date = pd.to_datetime(trade["entry_date"]).normalize()

    filled = True
    entry_used = base_entry
    policy_friction = friction_pct
    note = ""

    bar = _entry_bar_for_date(ohlcv, signal_date)
    next_bar = _next_bar_for_date(ohlcv, signal_date)

    if policy == "market":
        entry_used = base_entry

    elif policy == "limit":
        atr_pct = float(trade.get("atr_pct", 0.0))
        if not atr_pct or bar is None:
            filled = False
            note = "missing atr_pct or ohlcv; fallback to market entry"
        else:
            limit_offset = atr_pct * limit_atr_frac / 100.0
            if action == "BUY":
                limit_price = base_entry * (1.0 - limit_offset)
                filled = bool(bar["Low"] <= limit_price)
            else:
                limit_price = base_entry * (1.0 + limit_offset)
                filled = bool(bar["High"] >= limit_price)
            entry_used = limit_price if filled else base_entry
            policy_friction = friction_pct * passive_friction_discount if filled else friction_pct
            note = "filled" if filled else "unfilled-market-fallback"

    elif policy == "midpoint":
        if bar is None:
            filled = False
            entry_used = base_entry
            note = "missing ohlcv; fallback to market entry"
        else:
            entry_used = (float(bar["High"]) + float(bar["Low"])) / 2.0
            policy_friction = friction_pct * passive_friction_discount

    elif policy == "next_open":
        if next_bar is None:
            filled = False
            entry_used = base_entry
            note = "missing next bar; fallback to market entry"
        else:
            entry_used = float(next_bar["Open"])

    elif policy == "next_close":
        if next_bar is None:
            filled = False
            entry_used = base_entry
            note = "missing next bar; fallback to market entry"
        else:
            entry_used = float(next_bar["Close"])

    elif policy == "delayed_1d":
        # Enter at next day's close to avoid overnight-gap noise.
        if next_bar is None:
            filled = False
            entry_used = base_entry
            note = "missing next bar; fallback to market entry"
        else:
            entry_used = float(next_bar["Close"])

    gross = _compute_gross(action, entry_used, exit_price)
    net = gross - policy_friction
    entry_slippage_bps = ((entry_used - base_entry) / base_entry * 100.0) * (-1.0 if action == "BUY" else 1.0)

    return {
        "ticker": trade["ticker"],
        "action": action,
        "policy": policy,
        "signal_date": signal_date.isoformat(),
        "base_entry": round(base_entry, 4),
        "entry_used": round(entry_used, 4),
        "exit_price": round(exit_price, 4),
        "filled": filled,
        "gross_pct": round(gross, 4),
        "net_pct": round(net, 4),
        "friction_pct": round(policy_friction, 4),
        "entry_slippage_bps": round(entry_slippage_bps * 100.0, 4),
        "note": note,
    }


def simulate_policies(
    trades: list[dict],
    price_data: dict[str, pd.DataFrame],
    *,
    policies: list[Policy] | None = None,
    friction_pct: float = 0.50,
    limit_atr_frac: float = 0.5,
    passive_friction_discount: float = 0.5,
) -> SimulationResult:
    """
    Run every ``policy`` across ``trades``.

    ``price_data`` maps ticker -> daily OHLCV DataFrame with DateTime index and
    Open/High/Low/Close columns.
    """
    if policies is None:
        policies = list(DEFAULT_POLICIES)

    per_trade: list[dict] = []
    grouped: dict[str, list[dict]] = {p: [] for p in policies}

    for trade in trades:
        ticker = str(trade.get("ticker", ""))
        ohlcv = price_data.get(ticker)
        if ohlcv is None or ohlcv.empty:
            log.debug("[exec_sim] no price data for %s; skipping", ticker)
            continue
        for policy in policies:
            row = simulate_trade(
                trade,
                ohlcv,
                policy,
                friction_pct=friction_pct,
                limit_atr_frac=limit_atr_frac,
                passive_friction_discount=passive_friction_discount,
            )
            per_trade.append(row)
            grouped[policy].append(row)

    summaries: list[PolicySummary] = []
    median_hold = pd.Series([float(t.get("hold_days", 5.0)) for t in trades if "hold_days" in t])
    ann_factor = _annualisation_factor(median_hold)

    for policy in policies:
        rows = grouped[policy]
        if not rows:
            summaries.append(
                PolicySummary(
                    policy=policy,
                    n_total=0,
                    n_filled=0,
                    fill_rate=0.0,
                    avg_gross_bps=0.0,
                    avg_net_bps=0.0,
                    win_rate=0.0,
                    gross_sharpe_annual=None,
                    net_sharpe_annual=None,
                    avg_entry_slippage_bps=0.0,
                    notes="no trades",
                )
            )
            continue
        n_total = len(rows)
        n_filled = sum(1 for r in rows if r["filled"])
        gross_arr = np.array([r["gross_pct"] for r in rows], dtype=float)
        net_arr = np.array([r["net_pct"] for r in rows], dtype=float)
        slip_arr = np.array([r["entry_slippage_bps"] for r in rows], dtype=float)
        summaries.append(
            PolicySummary(
                policy=policy,
                n_total=n_total,
                n_filled=n_filled,
                fill_rate=round(n_filled / n_total, 4),
                avg_gross_bps=round(float(np.mean(gross_arr)) * 100.0, 4),
                avg_net_bps=round(float(np.mean(net_arr)) * 100.0, 4),
                win_rate=round(float(np.mean(net_arr > 0)), 4),
                gross_sharpe_annual=_sharpe(gross_arr, ann_factor),
                net_sharpe_annual=_sharpe(net_arr, ann_factor),
                avg_entry_slippage_bps=round(float(np.mean(slip_arr)), 4),
            )
        )

    return SimulationResult(summaries=summaries, per_trade=per_trade)


def best_policy(result: SimulationResult, metric: str = "avg_net_bps") -> PolicySummary | None:
    """Return the policy with the highest ``metric`` among filled rows."""
    if not result.summaries:
        return None

    def _key(s: PolicySummary) -> float:
        return getattr(s, metric, None) or float("-inf")

    return max(result.summaries, key=_key)
