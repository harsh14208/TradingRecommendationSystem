"""
Statistical/quant gates extracted from generate_signal().

Functional API:
    apply_statistical_gates(score, tech, sector_rs, market_ctx, df, is_lev_etf)
        -> (new_score, cards, sources)

Covers:
    §60 Hurst Exponent          — regime classification (trending vs MR)
    §59 OU Half-life            — mean-reversion speed gate
    §61 Idiosyncratic Volatility — noise-band quality filter
    §63 Sector Cointegration    — pair-deviation double-dislocation boost
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
    Statistical/quant scoring adjustments for §59, §60, §61, §63.

    Args:
        score:      current composite score
        tech:       technicals dict (hurst, ou_halflife keys)
        sector_rs:  sector result dict (sector_etf key)
        market_ctx: market context dict (etf_histories key)
        df:         OHLCV DataFrame for the ticker
        is_lev_etf: True for leveraged/inverse ETFs (most gates skipped)

    Returns:
        (new_score, cards, sources)
    """
    cards: list[dict] = []
    sources: set[str] = set()

    # ── §60 Hurst Exponent — Regime Classification ────────────────────────────
    hurst = tech.get("hurst")
    if hurst is not None:
        sources.add("Technical")
        if hurst > 0.60:
            trend_bonus = 5 if score > 0 else (-5 if score < 0 else 0)
            score += trend_bonus
            cards.append(
                {
                    "src": "Technical",
                    "head": f"Hurst Exponent {hurst:.2f} — Trending Regime",
                    "body": (
                        f"Hurst exponent of {hurst:.2f} > 0.5 confirms persistent price momentum. "
                        "This stock is in a 'trending' state — breakout and momentum signals "
                        "carry higher win rates here than oscillator-based reversals."
                    ),
                    "sentiment": "pos" if score > 0 else "neg",
                    "meta": f"Hurst = {hurst:.2f} (>0.6 = strong trend)",
                }
            )
        elif hurst < 0.40:
            if abs(score) > 15:
                score *= 0.87
            cards.append(
                {
                    "src": "Technical",
                    "head": f"Hurst Exponent {hurst:.2f} — Mean-Reverting Regime",
                    "body": (
                        f"Hurst exponent of {hurst:.2f} < 0.5 indicates anti-persistent "
                        "price behaviour — recent trends are likely to reverse. "
                        "Momentum/breakout signals are suspect; oversold/overbought reversals are more reliable."
                    ),
                    "sentiment": "neu",
                    "meta": f"Hurst = {hurst:.2f} (<0.4 = mean-reverting)",
                }
            )

    # ── §59 OU Half-life — Mean-Reversion Speed ───────────────────────────────
    ou_hl = tech.get("ou_halflife")
    if ou_hl is not None and not is_lev_etf:
        sources.add("Technical")
        if ou_hl > 12:
            score -= 5
            cards.append(
                {
                    "src": "Technical",
                    "head": f"Slow OU Reversion (Half-Life {ou_hl:.1f}d) — Weak MR Entry",
                    "body": (
                        f"Ornstein-Uhlenbeck half-life of {ou_hl:.1f} days exceeds the "
                        "10-day hold window — the mean-reversion bounce may not complete "
                        "before the position needs to be closed. Favour faster-reverting setups."
                    ),
                    "sentiment": "neg",
                    "meta": f"ou_halflife={ou_hl:.1f}d (>12 = slow MR)",
                }
            )
        elif ou_hl < 5:
            score += 4
            cards.append(
                {
                    "src": "Technical",
                    "head": f"Fast OU Reversion (Half-Life {ou_hl:.1f}d) — Strong MR Setup",
                    "body": (
                        f"Ornstein-Uhlenbeck half-life of {ou_hl:.1f} days — the price "
                        "reverts strongly to its mean well within the hold window. "
                        "Short half-life is the strongest predictor of realized MR returns."
                    ),
                    "sentiment": "pos",
                    "meta": f"ou_halflife={ou_hl:.1f}d (<5 = fast MR)",
                }
            )

    # ── §61 Idiosyncratic Volatility Gate ─────────────────────────────────────
    try:
        if len(df) >= 63 and not is_lev_etf:
            _r63 = df["Close"].astype(float).pct_change().dropna().values[-63:]
            import numpy as _np

            _ivol = float(_r63.std(ddof=1)) * _np.sqrt(252) * 100
            if _ivol > 55.0:
                score -= 5
                sources.add("Technical")
                cards.append(
                    {
                        "src": "Technical",
                        "head": f"High Idiosyncratic Vol ({_ivol:.0f}%) — Wide Noise Band",
                        "body": (
                            f"63-day realized volatility of {_ivol:.0f}% (annualized) exceeds "
                            "55%. Fat tails inflate the noise-to-signal ratio — short-term "
                            "dips that resemble MR entries may be structural moves, not "
                            "temporary dislocations."
                        ),
                        "sentiment": "neg",
                        "meta": f"idio_vol={_ivol:.0f}% >55% threshold",
                    }
                )
            elif _ivol < 25.0:
                score += 2
                sources.add("Technical")
                cards.append(
                    {
                        "src": "Technical",
                        "head": f"Low Idiosyncratic Vol ({_ivol:.0f}%) — Stable Reverter",
                        "body": (
                            f"63-day realized volatility of only {_ivol:.0f}% (annualized). "
                            "Low-vol stocks have tighter noise bands — moves away from mean "
                            "are more likely genuine oversold dislocations than random noise."
                        ),
                        "sentiment": "pos",
                        "meta": f"idio_vol={_ivol:.0f}% <25% threshold",
                    }
                )
    except Exception:
        pass

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
