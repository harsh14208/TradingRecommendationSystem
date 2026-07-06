"""Regression tests for the VRP strategy classifier `_decide`.

Focus: the buy-vol (LONG_STRADDLE) side must be as strict as the sell-vol side.
Near-fair-priced names (richness ~1.0) must NOT be bought as long straddles —
that was the source of the paper-options theta bleed.
"""

from __future__ import annotations

import pandas as pd

from scripts.orats_recommendation_engine import _CHEAP_MAX, _CHEAP_PCT, _decide


def _row(richness: float, richness_pct: float, dir_action=None, dte=None) -> pd.Series:
    return pd.Series(
        {
            "dir_action": dir_action,
            "richness": richness,
            "richness_pct": richness_pct,
            "days_to_earnings": dte,
            "impl_move": 0.012,
            "forecast_move": 0.014,
        }
    )


def test_near_fair_name_is_not_a_long_straddle() -> None:
    # richness 0.99 (implied ~1% below forecast) is fair, not cheap — even if it
    # happens to rank in the cheapest quintile. Buying vol here only pays theta.
    assert _decide(_row(0.99, 0.05), 21)[0] == "NO_ACTION"


def test_genuinely_cheap_and_bottom_quintile_is_long_straddle() -> None:
    # Deep discount AND cheapest quintile → the only case that buys premium.
    assert _decide(_row(0.60, 0.05), 21)[0] == "LONG_STRADDLE"


def test_deep_discount_but_not_bottom_quintile_is_no_action() -> None:
    # Cheap in absolute terms but mid-pack cross-sectionally → skip (symmetry with
    # the sell side, which requires the top quintile).
    assert _decide(_row(0.60, 0.50), 21)[0] == "NO_ACTION"


def test_cheap_boundaries() -> None:
    # richness at the ceiling is NOT cheap (strict <); just under, with bottom-quintile
    # rank, is.
    assert _decide(_row(_CHEAP_MAX, _CHEAP_PCT), 21)[0] == "NO_ACTION"
    assert _decide(_row(_CHEAP_MAX - 0.01, _CHEAP_PCT), 21)[0] == "LONG_STRADDLE"


def test_rich_side_unchanged() -> None:
    # Overpriced vol with no directional edge still harvests VRP.
    assert _decide(_row(1.40, 0.95), 21)[0] == "SELL_STRANGLE"
