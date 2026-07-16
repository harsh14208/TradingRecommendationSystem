"""Cross-sectional h=63 sleeve — paper-traded L/S book.

Builds a dollar-neutral long/short book from the research-promoted h=63 cross-sectional
model (nested-horizon net Sharpe +0.576, 90% CI excludes 0, cost- and borrow-robust).
The sleeve is tagged ``cohort="shadow"`` so it paper-trades without Telegram/Discord
notifications while forward data accrues.

The book is rebalanced from the scan batch: top decile → BUY, bottom decile → SELL,
held ~63 trading days. Names that fall out of the current top/bottom deciles generate
exit signals so stale sleeve positions are closed. Capital is allocated via
``alpha_sleeves.allocate_cross_sleeve_capital`` using the validated CrossSectional
Sharpe/vol metrics.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from services import cross_sectional_shadow as _css

log = logging.getLogger("signal.trade.cross_sectional_sleeve")

_SLEEVE_NAME = "CrossSectional"
_DEFAULT_DECILE = 0.10
_HOLD_DAYS = 63
_MIN_CONFIDENCE = 100.0


def build_cross_sectional_book(
    histories: dict[str, pd.DataFrame],
    decile: float = _DEFAULT_DECILE,
) -> tuple[list[str], list[str], dict[str, float]]:
    """Return (long_tickers, short_tickers, percentile_map) from the h=63 model.

    Long leg = top ``decile`` predicted relative performers.
    Short leg = bottom ``decile`` predicted relative performers.
    Returns empty lists if the model is unavailable or the batch is too thin.
    """
    pct = _css.score_batch_h63(histories)
    if not pct or len(pct) < _css._MIN_NAMES:
        return [], [], {}

    tickers = sorted(pct, key=pct.get)  # weakest → strongest
    n = max(1, int(round(len(tickers) * decile)))
    short_leg = tickers[:n]
    long_leg = tickers[-n:]
    return long_leg, short_leg, pct


def _last_price(df: pd.DataFrame | None) -> float | None:
    if df is None or getattr(df, "empty", True):
        return None
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    if close_col is None:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce").dropna()
    if len(close) == 0:
        return None
    return float(close.iloc[-1])


def _base_signal_dict(
    ticker: str,
    action: str,
    price: float,
    pct: float,
    decile: float,
    *,
    sleeve_notional: float | None = None,
    is_exit: bool = False,
) -> dict[str, Any]:
    """Return a minimally-populated signal dict for the cross-sectional sleeve."""
    if is_exit:
        headline = f"Cross-sectional h=63 sleeve — exit {action}"
        body = (
            "Research-promoted h=63 cross-sectional model. This ticker is no longer in the "
            f"top/bottom {decile:.0%} of today's scan universe; closing the sleeve position."
        )
        meta = f"sleeve=CrossSectional horizon=63 exit=1 pct={pct:.1f}"
    else:
        headline = f"Cross-sectional h=63 sleeve — {pct:.0f}th percentile ({action})"
        body = (
            "Research-promoted h=63 cross-sectional model. "
            f"{'Top' if action == 'BUY' else 'Bottom'} {decile:.0%} of today's "
            "scan universe by predicted 63-day relative return. "
            "Paper-traded only (shadow cohort) while forward data accrues."
        )
        meta = f"sleeve=CrossSectional horizon=63 pct={pct:.1f} decile={decile}"

    signal: dict[str, Any] = {
        "ticker": ticker,
        "company": ticker,
        "action": action,
        "price": round(price, 4),
        "entry": round(price, 4),
        "change": 0.0,
        "changePct": 0.0,
        "confidence": _MIN_CONFIDENCE,
        "displayConfidence": _MIN_CONFIDENCE,
        "calibratedProbability": _MIN_CONFIDENCE,
        "alpha_score": _MIN_CONFIDENCE,
        "raw_score": _MIN_CONFIDENCE,
        "headline": headline,
        "sentiment": 0.0,
        "style": "position",
        "sources": ["CrossSectional"],
        "sleeve": _SLEEVE_NAME,
        "cohort": "shadow",
        "recommendedHoldDays": _HOLD_DAYS,
        "crossSectionalShadowPctH63": pct,
        "positionSizeScale": 1.0,
        "sleeve_notional": round(sleeve_notional, 2) if sleeve_notional is not None else None,
        "sleeve_exit": is_exit,
        "rationale": [
            {
                "src": "Cross-Sectional Sleeve",
                "head": headline,
                "body": body,
                "sentiment": "pos" if action == "BUY" else "neg",
                "meta": meta,
            }
        ],
    }
    return signal


def make_cross_sectional_sleeve_signals(
    histories: dict[str, pd.DataFrame],
    sleeve_capital: float,
    active_positions: dict[str, str] | None = None,
    decile: float = _DEFAULT_DECILE,
) -> list[dict[str, Any]]:
    """Build shadow-cohort entry + exit signal dicts for the h=63 L/S sleeve.

    Args:
        histories: scan-batch price histories.
        sleeve_capital: dollars allocated to this sleeve (from ``allocate_cross_sleeve_capital``).
        active_positions: mapping of ticker → current sleeve action ("BUY" or "SELL")
            from existing active CrossSectional signals. Tickers not in today's
            desired long/short legs will emit an exit signal.
        decile: top/bottom decile used for the long/short legs.

    Returns:
        List of signal dicts ready for ``_persist_scan_signals`` / ``_deliver_scan_signals``.
    """
    active_positions = active_positions or {}
    long_leg, short_leg, pct = build_cross_sectional_book(histories, decile=decile)

    # If the model produced no book and there are no stale positions to close, do nothing.
    if not long_leg and not short_leg and not active_positions:
        return []

    desired: dict[str, str] = {}
    for t in long_leg:
        desired[t] = "BUY"
    for t in short_leg:
        desired[t] = "SELL"

    # Dollar-neutral: split sleeve capital equally across both legs, then equal weight
    # within each leg. Per-name notional = (sleeve_capital / 2) / names_per_leg.
    names_per_leg = max(len(long_leg), len(short_leg))
    leg_capital = sleeve_capital / 2.0
    per_name_notional = leg_capital / names_per_leg if names_per_leg > 0 else 0.0

    signals: list[dict[str, Any]] = []

    # Entry signals for today's desired long/short legs.
    for action, leg in (("BUY", long_leg), ("SELL", short_leg)):
        for ticker in leg:
            price = _last_price(histories.get(ticker))
            if price is None or price <= 0:
                log.warning("[cross_sectional_sleeve] skipping %s entry — no price", ticker)
                continue
            _pct = pct.get(ticker, 50.0)
            signals.append(
                _base_signal_dict(
                    ticker,
                    action,
                    price,
                    _pct,
                    decile,
                    sleeve_notional=per_name_notional if sleeve_capital > 0 else None,
                )
            )

    # Exit signals for positions that are no longer in the desired book.
    for ticker, current_action in active_positions.items():
        if ticker in desired:
            continue
        exit_action = "SELL" if current_action == "BUY" else "BUY"
        price = _last_price(histories.get(ticker))
        if price is None or price <= 0:
            log.warning("[cross_sectional_sleeve] skipping %s exit — no price", ticker)
            continue
        _pct = pct.get(ticker, 50.0)
        signals.append(
            _base_signal_dict(
                ticker,
                exit_action,
                price,
                _pct,
                decile,
                sleeve_notional=None,
                is_exit=True,
            )
        )

    if signals:
        log.info(
            "[cross_sectional_sleeve] built %d signals (long=%d, short=%d, exits=%d) "
            "with $%.0f per-name entry notional",
            len(signals),
            len(long_leg),
            len(short_leg),
            sum(1 for s in signals if s.get("sleeve_exit")),
            per_name_notional,
        )
    return signals


def target_sleeve_capital(
    total_equity: float,
    sleeve_sharpes: dict[str, float],
    sleeve_vols: dict[str, float] | None = None,
) -> float:
    """Return the dollar allocation for the CrossSectional sleeve given total equity."""
    if total_equity <= 0:
        return 0.0
    # Avoid circular import at module load.
    from services.alpha_sleeves import allocate_cross_sleeve_capital

    alloc = allocate_cross_sleeve_capital(sleeve_sharpes, total_equity, sleeve_vols)
    return float(alloc.get(_SLEEVE_NAME, 0.0))
