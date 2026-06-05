"""
Statistical/quant gates extracted from generate_signal().

Functional API:
    apply_statistical_gates(score, tech, sector_rs, market_ctx, df, is_lev_etf)
        -> (new_score, cards, sources)

Covers:
    §63 Sector Cointegration    — pair-deviation double-dislocation boost

Removed 2026-06-02 (--validate-live-gates: ΔSh=0.00, ΔN ≤ 8 each):
    §59 OU Half-life            — hard block too slow; scoring modifier also removed
    §60 Hurst Exponent          — hard block confirmed dead; scoring modifier also removed
    §61 Idiosyncratic Volatility — hard block confirmed dead; scoring modifier also removed
"""

from __future__ import annotations


def apply_statistical_gates(
    score: float,
    tech: dict,
    sector_rs: dict | None,
    market_ctx: dict | None,
    df,
    is_lev_etf: bool,
) -> tuple[float, list[dict], set[str]]:
    """
    Statistical/quant scoring adjustments (§63 only after 2026-06-02 cleanup).

    Args:
        score:      current composite score
        tech:       technicals dict
        sector_rs:  sector result dict (sector_etf key)
        market_ctx: market context dict (etf_histories key)
        df:         OHLCV DataFrame for the ticker
        is_lev_etf: True for leveraged/inverse ETFs (most gates skipped)

    Returns:
        (new_score, cards, sources)
    """
    cards: list[dict] = []
    sources: set[str] = set()

    # ── §63 Sector Cointegration Deviation Gate ───────────────────────────────
    # Gatev, Goetzmann & Rouwenhorst (2006): cointegration-based entries have
    # 74% WR vs 58% for non-cointegrated pairs.
    try:
        _coint_etf = (sector_rs or {}).get("sector_etf")
        _etf_hist = (market_ctx or {}).get("etf_histories", {})
        if _coint_etf and _etf_hist and _coint_etf in _etf_hist and not is_lev_etf and len(df) >= 60:
            from services.technicals import compute_cointegration_zscore as _coint_fn

            _coint_z = _coint_fn(
                df["Close"].astype(float),
                _etf_hist[_coint_etf],
            )
            if _coint_z is not None:
                if _coint_z < -2.0:
                    score += 4
                    sources.add("Technical")
                    cards.append(
                        {
                            "src": "Technical",
                            "head": f"Cointegration Deviation −{abs(_coint_z):.1f}σ vs {_coint_etf} — Double Dislocation",
                            "body": (
                                f"This stock is {abs(_coint_z):.1f} standard deviations below its "
                                f"long-run cointegration relationship with {_coint_etf}. "
                                "Pair deviations beyond −2σ revert 74% of the time (Gatev et al. 2006). "
                                "The stock is oversold vs both its own history AND its sector basket — "
                                "highest-quality MR setup."
                            ),
                            "sentiment": "pos",
                            "meta": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
                        }
                    )
                elif _coint_z < -1.0:
                    score += 2
                    sources.add("Technical")
                    cards.append(
                        {
                            "src": "Technical",
                            "head": f"Sector Pair Deviation −{abs(_coint_z):.1f}σ vs {_coint_etf}",
                            "body": (
                                f"Stock is {abs(_coint_z):.1f}σ below its cointegration mean with "
                                f"{_coint_etf}. Moderate deviation — adds confirmation to MR setup."
                            ),
                            "sentiment": "pos",
                            "meta": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
                        }
                    )
                elif _coint_z > 0.5:
                    score -= 2
                    cards.append(
                        {
                            "src": "Technical",
                            "head": f"Stock Above Sector Pair Mean (+{_coint_z:.1f}σ vs {_coint_etf})",
                            "body": (
                                f"Stock is {_coint_z:.1f}σ above its long-run relationship with "
                                f"{_coint_etf} — already at or above equilibrium relative to peers. "
                                "MR entry lacks the pair-deviation confirmation."
                            ),
                            "sentiment": "neg",
                            "meta": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
                        }
                    )
    except Exception:
        pass

    return score, cards, sources
