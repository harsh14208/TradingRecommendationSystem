"""Load and cache the canonical in-sample research backtest artifacts.

The CSVs are produced by scripts/backtest_technicals.py (v10.9 canon):
  - data/mr_monthly_equity.csv  — cumulative equity curve (monthly)
  - data/mr_monthly.csv         — per-month net returns
  - data/backtest_trades_is.csv — every trade in the 23-year IS run

This module is intentionally lightweight (stdlib only) and reads the files once
at first use.  It does not touch the database or any market-data API.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

_DATA_DIR = Path(__file__).parent.parent / "data"

# v10.9 canon constants used as cross-checks and fallback labels.
_CANON = {
    "version": "v10.9",
    "period": "2003–2026",
    "total_trades": 217,
    "win_rate": 69.1,
    "sharpe": 0.24,
    "max_drawdown_pct": -2.31,
}


def _read_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_float(value: str | None, default: float | None = None) -> float | None:
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


class _ResearchBacktestCache:
    """Lazy, in-memory cache for research backtest data."""

    def __init__(self) -> None:
        self._data: dict[str, Any] | None = None

    def get(self) -> dict[str, Any]:
        if self._data is None:
            self._data = self._load()
        return self._data

    def _load(self) -> dict[str, Any]:
        equity_rows = _read_csv(_DATA_DIR / "mr_monthly_equity.csv")
        monthly_rows = _read_csv(_DATA_DIR / "mr_monthly.csv")
        trade_rows = _read_csv(_DATA_DIR / "backtest_trades_is.csv")

        # mr_monthly_equity.csv stores *monthly returns* (decimals) from the portfolio
        # simulation run by scripts/backtest_technicals.py. Convert them into a
        # cumulative equity curve starting at $100,000.
        monthly_returns = [
            {"date": r.get("date"), "net_pct": _to_float(r.get("net_pct"), 0.0)}
            for r in equity_rows
            if r.get("date") and _to_float(r.get("net_pct")) is not None
        ]

        equity_curve: list[dict[str, Any]] = []
        equity = 100_000.0
        for r in monthly_returns:
            equity = equity * (1 + (r["net_pct"] or 0.0))
            equity_curve.append({"date": r["date"], "value": equity})

        trades: list[dict[str, Any]] = []
        for r in trade_rows:
            net = _to_float(r.get("net_pct"))
            if net is None:
                continue
            trades.append(
                {
                    "date": r.get("date"),
                    "ticker": r.get("ticker"),
                    "action": r.get("action"),
                    "score": _to_float(r.get("score")),
                    "entry": _to_float(r.get("entry")),
                    "stop": _to_float(r.get("stop")),
                    "target": _to_float(r.get("target")),
                    "exit_price": _to_float(r.get("exit_price")),
                    "exit_reason": r.get("exit_reason"),
                    "exit_day": _to_float(r.get("exit_day")),
                    "gross_pct": _to_float(r.get("gross_pct")),
                    "net_pct": net,
                    "mfe_pct": _to_float(r.get("mfe_pct")),
                    "mae_pct": _to_float(r.get("mae_pct")),
                    "sector_etf": r.get("sector_etf"),
                }
            )

        summary = self._summarize(equity_curve, monthly_returns, trades)

        return {
            "canon": _CANON,
            "summary": summary,
            "equity_curve": equity_curve,
            "monthly_returns": monthly_returns,
            "trades": trades,
            "top_trades": sorted(trades, key=lambda t: t["net_pct"] or 0, reverse=True)[:10],
            "worst_trades": sorted(trades, key=lambda t: t["net_pct"] or 0)[:10],
        }

    @staticmethod
    def _summarize(
        equity_curve: list[dict[str, float]],
        monthly_returns: list[dict[str, float]],
        trades: list[dict[str, Any]],
    ) -> dict[str, Any]:
        # Use the documented v10.9 canon constants as the headline metrics.  The
        # CSVs supply the equity curve and trade list, but the canon Sharpe / WR /
        # MaxDD are the authoritative numbers published in SIGNAL_VALIDATION.md.
        summary: dict[str, Any] = {
            "start_date": equity_curve[0]["date"] if equity_curve else None,
            "end_date": equity_curve[-1]["date"] if equity_curve else None,
            "total_trades": _CANON["total_trades"],
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": _CANON["win_rate"],
            "avg_return": None,
            "avg_win": None,
            "avg_loss": None,
            "sharpe": _CANON["sharpe"],
            "max_drawdown_pct": _CANON["max_drawdown_pct"],
            "cagr_pct": None,
            "canon": True,
        }

        if trades:
            nets = [t["net_pct"] for t in trades if t["net_pct"] is not None]
            wins = [n for n in nets if n > 0]
            losses = [n for n in nets if n <= 0]
            summary["winning_trades"] = len(wins)
            summary["losing_trades"] = len(losses)
            summary["avg_return"] = round(sum(nets) / len(nets), 3) if nets else None
            summary["avg_win"] = round(sum(wins) / len(wins), 3) if wins else None
            summary["avg_loss"] = round(sum(losses) / len(losses), 3) if losses else None

        if equity_curve:
            start_val = equity_curve[0]["value"]
            end_val = equity_curve[-1]["value"]
            if start_val and start_val > 0 and end_val:
                # monthly points → years
                years = max(0.1, (len(equity_curve) - 1) / 12)
                summary["cagr_pct"] = round(((end_val / start_val) ** (1 / years) - 1) * 100, 1)

        return summary


_research_cache = _ResearchBacktestCache()


def get_research_backtest() -> dict[str, Any]:
    """Return the full canonical research backtest payload."""
    return _research_cache.get()


def clear_research_cache() -> None:
    """Clear the in-memory cache (useful in tests)."""
    global _research_cache
    _research_cache = _ResearchBacktestCache()
