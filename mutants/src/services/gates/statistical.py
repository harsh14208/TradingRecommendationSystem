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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_apply_statistical_gates__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_apply_statistical_gates__mutmut)
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


def x_apply_statistical_gates__mutmut_orig(
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


def x_apply_statistical_gates__mutmut_1(
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
    cards: list[dict] = None
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


def x_apply_statistical_gates__mutmut_2(
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
    sources: set[str] = None

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


def x_apply_statistical_gates__mutmut_3(
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
        _coint_etf = None
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


def x_apply_statistical_gates__mutmut_4(
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
        _coint_etf = (sector_rs or {}).get(None)
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


def x_apply_statistical_gates__mutmut_5(
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
        _coint_etf = (sector_rs and {}).get("sector_etf")
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


def x_apply_statistical_gates__mutmut_6(
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
        _coint_etf = (sector_rs or {}).get("XXsector_etfXX")
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


def x_apply_statistical_gates__mutmut_7(
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
        _coint_etf = (sector_rs or {}).get("SECTOR_ETF")
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


def x_apply_statistical_gates__mutmut_8(
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
        _etf_hist = None
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


def x_apply_statistical_gates__mutmut_9(
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
        _etf_hist = (market_ctx or {}).get(None, {})
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


def x_apply_statistical_gates__mutmut_10(
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
        _etf_hist = (market_ctx or {}).get("etf_histories", None)
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


def x_apply_statistical_gates__mutmut_11(
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
        _etf_hist = (market_ctx or {}).get({})
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


def x_apply_statistical_gates__mutmut_12(
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
        _etf_hist = (market_ctx or {}).get("etf_histories", )
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


def x_apply_statistical_gates__mutmut_13(
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
        _etf_hist = (market_ctx and {}).get("etf_histories", {})
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


def x_apply_statistical_gates__mutmut_14(
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
        _etf_hist = (market_ctx or {}).get("XXetf_historiesXX", {})
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


def x_apply_statistical_gates__mutmut_15(
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
        _etf_hist = (market_ctx or {}).get("ETF_HISTORIES", {})
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


def x_apply_statistical_gates__mutmut_16(
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
        if _coint_etf and _etf_hist and _coint_etf in _etf_hist and not is_lev_etf or len(df) >= 60:
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


def x_apply_statistical_gates__mutmut_17(
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
        if _coint_etf and _etf_hist and _coint_etf in _etf_hist or not is_lev_etf and len(df) >= 60:
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


def x_apply_statistical_gates__mutmut_18(
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
        if _coint_etf and _etf_hist or _coint_etf in _etf_hist and not is_lev_etf and len(df) >= 60:
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


def x_apply_statistical_gates__mutmut_19(
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
        if _coint_etf or _etf_hist and _coint_etf in _etf_hist and not is_lev_etf and len(df) >= 60:
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


def x_apply_statistical_gates__mutmut_20(
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
        if _coint_etf and _etf_hist and _coint_etf not in _etf_hist and not is_lev_etf and len(df) >= 60:
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


def x_apply_statistical_gates__mutmut_21(
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
        if _coint_etf and _etf_hist and _coint_etf in _etf_hist and is_lev_etf and len(df) >= 60:
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


def x_apply_statistical_gates__mutmut_22(
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
        if _coint_etf and _etf_hist and _coint_etf in _etf_hist and not is_lev_etf and len(df) > 60:
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


def x_apply_statistical_gates__mutmut_23(
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
        if _coint_etf and _etf_hist and _coint_etf in _etf_hist and not is_lev_etf and len(df) >= 61:
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


def x_apply_statistical_gates__mutmut_24(
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

            _coint_z = None
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


def x_apply_statistical_gates__mutmut_25(
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
                None,
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


def x_apply_statistical_gates__mutmut_26(
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
                None,
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


def x_apply_statistical_gates__mutmut_27(
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


def x_apply_statistical_gates__mutmut_28(
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


def x_apply_statistical_gates__mutmut_29(
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
                df["Close"].astype(None),
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


def x_apply_statistical_gates__mutmut_30(
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
                df["XXCloseXX"].astype(float),
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


def x_apply_statistical_gates__mutmut_31(
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
                df["close"].astype(float),
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


def x_apply_statistical_gates__mutmut_32(
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
                df["CLOSE"].astype(float),
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


def x_apply_statistical_gates__mutmut_33(
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
            if _coint_z is None:
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


def x_apply_statistical_gates__mutmut_34(
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
                if _coint_z <= -2.0:
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


def x_apply_statistical_gates__mutmut_35(
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
                if _coint_z < +2.0:
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


def x_apply_statistical_gates__mutmut_36(
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
                if _coint_z < -3.0:
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


def x_apply_statistical_gates__mutmut_37(
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
                    score = 4
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


def x_apply_statistical_gates__mutmut_38(
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
                    score -= 4
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


def x_apply_statistical_gates__mutmut_39(
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
                    score += 5
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


def x_apply_statistical_gates__mutmut_40(
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
                    sources.add(None)
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


def x_apply_statistical_gates__mutmut_41(
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
                    sources.add("XXTechnicalXX")
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


def x_apply_statistical_gates__mutmut_42(
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
                    sources.add("technical")
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


def x_apply_statistical_gates__mutmut_43(
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
                    sources.add("TECHNICAL")
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


def x_apply_statistical_gates__mutmut_44(
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
                        None
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


def x_apply_statistical_gates__mutmut_45(
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
                            "XXsrcXX": "Technical",
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


def x_apply_statistical_gates__mutmut_46(
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
                            "SRC": "Technical",
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


def x_apply_statistical_gates__mutmut_47(
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
                            "src": "XXTechnicalXX",
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


def x_apply_statistical_gates__mutmut_48(
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
                            "src": "technical",
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


def x_apply_statistical_gates__mutmut_49(
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
                            "src": "TECHNICAL",
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


def x_apply_statistical_gates__mutmut_50(
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
                            "XXheadXX": f"Cointegration Deviation −{abs(_coint_z):.1f}σ vs {_coint_etf} — Double Dislocation",
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


def x_apply_statistical_gates__mutmut_51(
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
                            "HEAD": f"Cointegration Deviation −{abs(_coint_z):.1f}σ vs {_coint_etf} — Double Dislocation",
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


def x_apply_statistical_gates__mutmut_52(
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
                            "head": f"Cointegration Deviation −{abs(None):.1f}σ vs {_coint_etf} — Double Dislocation",
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


def x_apply_statistical_gates__mutmut_53(
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
                            "XXbodyXX": (
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


def x_apply_statistical_gates__mutmut_54(
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
                            "BODY": (
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


def x_apply_statistical_gates__mutmut_55(
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
                                f"This stock is {abs(None):.1f} standard deviations below its "
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


def x_apply_statistical_gates__mutmut_56(
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
                                "XXPair deviations beyond −2σ revert 74% of the time (Gatev et al. 2006). XX"
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


def x_apply_statistical_gates__mutmut_57(
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
                                "pair deviations beyond −2σ revert 74% of the time (gatev et al. 2006). "
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


def x_apply_statistical_gates__mutmut_58(
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
                                "PAIR DEVIATIONS BEYOND −2Σ REVERT 74% OF THE TIME (GATEV ET AL. 2006). "
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


def x_apply_statistical_gates__mutmut_59(
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
                                "XXThe stock is oversold vs both its own history AND its sector basket — XX"
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


def x_apply_statistical_gates__mutmut_60(
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
                                "the stock is oversold vs both its own history and its sector basket — "
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


def x_apply_statistical_gates__mutmut_61(
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
                                "THE STOCK IS OVERSOLD VS BOTH ITS OWN HISTORY AND ITS SECTOR BASKET — "
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


def x_apply_statistical_gates__mutmut_62(
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
                                "XXhighest-quality MR setup.XX"
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


def x_apply_statistical_gates__mutmut_63(
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
                                "highest-quality mr setup."
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


def x_apply_statistical_gates__mutmut_64(
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
                                "HIGHEST-QUALITY MR SETUP."
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


def x_apply_statistical_gates__mutmut_65(
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
                            "XXsentimentXX": "pos",
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


def x_apply_statistical_gates__mutmut_66(
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
                            "SENTIMENT": "pos",
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


def x_apply_statistical_gates__mutmut_67(
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
                            "sentiment": "XXposXX",
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


def x_apply_statistical_gates__mutmut_68(
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
                            "sentiment": "POS",
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


def x_apply_statistical_gates__mutmut_69(
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
                            "XXmetaXX": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
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


def x_apply_statistical_gates__mutmut_70(
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
                            "META": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
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


def x_apply_statistical_gates__mutmut_71(
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
                elif _coint_z <= -1.0:
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


def x_apply_statistical_gates__mutmut_72(
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
                elif _coint_z < +1.0:
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


def x_apply_statistical_gates__mutmut_73(
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
                elif _coint_z < -2.0:
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


def x_apply_statistical_gates__mutmut_74(
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
                    score = 2
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


def x_apply_statistical_gates__mutmut_75(
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
                    score -= 2
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


def x_apply_statistical_gates__mutmut_76(
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
                    score += 3
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


def x_apply_statistical_gates__mutmut_77(
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
                    sources.add(None)
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


def x_apply_statistical_gates__mutmut_78(
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
                    sources.add("XXTechnicalXX")
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


def x_apply_statistical_gates__mutmut_79(
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
                    sources.add("technical")
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


def x_apply_statistical_gates__mutmut_80(
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
                    sources.add("TECHNICAL")
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


def x_apply_statistical_gates__mutmut_81(
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
                        None
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


def x_apply_statistical_gates__mutmut_82(
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
                            "XXsrcXX": "Technical",
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


def x_apply_statistical_gates__mutmut_83(
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
                            "SRC": "Technical",
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


def x_apply_statistical_gates__mutmut_84(
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
                            "src": "XXTechnicalXX",
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


def x_apply_statistical_gates__mutmut_85(
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
                            "src": "technical",
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


def x_apply_statistical_gates__mutmut_86(
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
                            "src": "TECHNICAL",
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


def x_apply_statistical_gates__mutmut_87(
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
                            "XXheadXX": f"Sector Pair Deviation −{abs(_coint_z):.1f}σ vs {_coint_etf}",
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


def x_apply_statistical_gates__mutmut_88(
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
                            "HEAD": f"Sector Pair Deviation −{abs(_coint_z):.1f}σ vs {_coint_etf}",
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


def x_apply_statistical_gates__mutmut_89(
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
                            "head": f"Sector Pair Deviation −{abs(None):.1f}σ vs {_coint_etf}",
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


def x_apply_statistical_gates__mutmut_90(
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
                            "XXbodyXX": (
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


def x_apply_statistical_gates__mutmut_91(
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
                            "BODY": (
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


def x_apply_statistical_gates__mutmut_92(
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
                                f"Stock is {abs(None):.1f}σ below its cointegration mean with "
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


def x_apply_statistical_gates__mutmut_93(
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
                            "XXsentimentXX": "pos",
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


def x_apply_statistical_gates__mutmut_94(
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
                            "SENTIMENT": "pos",
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


def x_apply_statistical_gates__mutmut_95(
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
                            "sentiment": "XXposXX",
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


def x_apply_statistical_gates__mutmut_96(
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
                            "sentiment": "POS",
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


def x_apply_statistical_gates__mutmut_97(
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
                            "XXmetaXX": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
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


def x_apply_statistical_gates__mutmut_98(
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
                            "META": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
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


def x_apply_statistical_gates__mutmut_99(
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
                elif _coint_z >= 0.5:
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


def x_apply_statistical_gates__mutmut_100(
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
                elif _coint_z > 1.5:
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


def x_apply_statistical_gates__mutmut_101(
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
                    score = 2
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


def x_apply_statistical_gates__mutmut_102(
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
                    score += 2
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


def x_apply_statistical_gates__mutmut_103(
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
                    score -= 3
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


def x_apply_statistical_gates__mutmut_104(
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
                        None
                    )
    except Exception:
        pass

    return score, cards, sources


def x_apply_statistical_gates__mutmut_105(
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
                            "XXsrcXX": "Technical",
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


def x_apply_statistical_gates__mutmut_106(
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
                            "SRC": "Technical",
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


def x_apply_statistical_gates__mutmut_107(
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
                            "src": "XXTechnicalXX",
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


def x_apply_statistical_gates__mutmut_108(
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
                            "src": "technical",
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


def x_apply_statistical_gates__mutmut_109(
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
                            "src": "TECHNICAL",
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


def x_apply_statistical_gates__mutmut_110(
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
                            "XXheadXX": f"Stock Above Sector Pair Mean (+{_coint_z:.1f}σ vs {_coint_etf})",
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


def x_apply_statistical_gates__mutmut_111(
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
                            "HEAD": f"Stock Above Sector Pair Mean (+{_coint_z:.1f}σ vs {_coint_etf})",
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


def x_apply_statistical_gates__mutmut_112(
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
                            "XXbodyXX": (
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


def x_apply_statistical_gates__mutmut_113(
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
                            "BODY": (
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


def x_apply_statistical_gates__mutmut_114(
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
                                "XXMR entry lacks the pair-deviation confirmation.XX"
                            ),
                            "sentiment": "neg",
                            "meta": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
                        }
                    )
    except Exception:
        pass

    return score, cards, sources


def x_apply_statistical_gates__mutmut_115(
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
                                "mr entry lacks the pair-deviation confirmation."
                            ),
                            "sentiment": "neg",
                            "meta": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
                        }
                    )
    except Exception:
        pass

    return score, cards, sources


def x_apply_statistical_gates__mutmut_116(
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
                                "MR ENTRY LACKS THE PAIR-DEVIATION CONFIRMATION."
                            ),
                            "sentiment": "neg",
                            "meta": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
                        }
                    )
    except Exception:
        pass

    return score, cards, sources


def x_apply_statistical_gates__mutmut_117(
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
                            "XXsentimentXX": "neg",
                            "meta": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
                        }
                    )
    except Exception:
        pass

    return score, cards, sources


def x_apply_statistical_gates__mutmut_118(
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
                            "SENTIMENT": "neg",
                            "meta": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
                        }
                    )
    except Exception:
        pass

    return score, cards, sources


def x_apply_statistical_gates__mutmut_119(
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
                            "sentiment": "XXnegXX",
                            "meta": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
                        }
                    )
    except Exception:
        pass

    return score, cards, sources


def x_apply_statistical_gates__mutmut_120(
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
                            "sentiment": "NEG",
                            "meta": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
                        }
                    )
    except Exception:
        pass

    return score, cards, sources


def x_apply_statistical_gates__mutmut_121(
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
                            "XXmetaXX": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
                        }
                    )
    except Exception:
        pass

    return score, cards, sources


def x_apply_statistical_gates__mutmut_122(
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
                            "META": f"coint_z={_coint_z:.2f} etf={_coint_etf}",
                        }
                    )
    except Exception:
        pass

    return score, cards, sources

mutants_x_apply_statistical_gates__mutmut['_mutmut_orig'] = x_apply_statistical_gates__mutmut_orig # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_1'] = x_apply_statistical_gates__mutmut_1 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_2'] = x_apply_statistical_gates__mutmut_2 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_3'] = x_apply_statistical_gates__mutmut_3 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_4'] = x_apply_statistical_gates__mutmut_4 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_5'] = x_apply_statistical_gates__mutmut_5 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_6'] = x_apply_statistical_gates__mutmut_6 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_7'] = x_apply_statistical_gates__mutmut_7 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_8'] = x_apply_statistical_gates__mutmut_8 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_9'] = x_apply_statistical_gates__mutmut_9 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_10'] = x_apply_statistical_gates__mutmut_10 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_11'] = x_apply_statistical_gates__mutmut_11 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_12'] = x_apply_statistical_gates__mutmut_12 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_13'] = x_apply_statistical_gates__mutmut_13 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_14'] = x_apply_statistical_gates__mutmut_14 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_15'] = x_apply_statistical_gates__mutmut_15 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_16'] = x_apply_statistical_gates__mutmut_16 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_17'] = x_apply_statistical_gates__mutmut_17 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_18'] = x_apply_statistical_gates__mutmut_18 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_19'] = x_apply_statistical_gates__mutmut_19 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_20'] = x_apply_statistical_gates__mutmut_20 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_21'] = x_apply_statistical_gates__mutmut_21 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_22'] = x_apply_statistical_gates__mutmut_22 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_23'] = x_apply_statistical_gates__mutmut_23 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_24'] = x_apply_statistical_gates__mutmut_24 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_25'] = x_apply_statistical_gates__mutmut_25 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_26'] = x_apply_statistical_gates__mutmut_26 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_27'] = x_apply_statistical_gates__mutmut_27 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_28'] = x_apply_statistical_gates__mutmut_28 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_29'] = x_apply_statistical_gates__mutmut_29 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_30'] = x_apply_statistical_gates__mutmut_30 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_31'] = x_apply_statistical_gates__mutmut_31 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_32'] = x_apply_statistical_gates__mutmut_32 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_33'] = x_apply_statistical_gates__mutmut_33 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_34'] = x_apply_statistical_gates__mutmut_34 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_35'] = x_apply_statistical_gates__mutmut_35 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_36'] = x_apply_statistical_gates__mutmut_36 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_37'] = x_apply_statistical_gates__mutmut_37 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_38'] = x_apply_statistical_gates__mutmut_38 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_39'] = x_apply_statistical_gates__mutmut_39 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_40'] = x_apply_statistical_gates__mutmut_40 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_41'] = x_apply_statistical_gates__mutmut_41 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_42'] = x_apply_statistical_gates__mutmut_42 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_43'] = x_apply_statistical_gates__mutmut_43 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_44'] = x_apply_statistical_gates__mutmut_44 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_45'] = x_apply_statistical_gates__mutmut_45 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_46'] = x_apply_statistical_gates__mutmut_46 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_47'] = x_apply_statistical_gates__mutmut_47 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_48'] = x_apply_statistical_gates__mutmut_48 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_49'] = x_apply_statistical_gates__mutmut_49 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_50'] = x_apply_statistical_gates__mutmut_50 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_51'] = x_apply_statistical_gates__mutmut_51 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_52'] = x_apply_statistical_gates__mutmut_52 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_53'] = x_apply_statistical_gates__mutmut_53 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_54'] = x_apply_statistical_gates__mutmut_54 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_55'] = x_apply_statistical_gates__mutmut_55 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_56'] = x_apply_statistical_gates__mutmut_56 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_57'] = x_apply_statistical_gates__mutmut_57 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_58'] = x_apply_statistical_gates__mutmut_58 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_59'] = x_apply_statistical_gates__mutmut_59 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_60'] = x_apply_statistical_gates__mutmut_60 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_61'] = x_apply_statistical_gates__mutmut_61 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_62'] = x_apply_statistical_gates__mutmut_62 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_63'] = x_apply_statistical_gates__mutmut_63 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_64'] = x_apply_statistical_gates__mutmut_64 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_65'] = x_apply_statistical_gates__mutmut_65 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_66'] = x_apply_statistical_gates__mutmut_66 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_67'] = x_apply_statistical_gates__mutmut_67 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_68'] = x_apply_statistical_gates__mutmut_68 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_69'] = x_apply_statistical_gates__mutmut_69 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_70'] = x_apply_statistical_gates__mutmut_70 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_71'] = x_apply_statistical_gates__mutmut_71 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_72'] = x_apply_statistical_gates__mutmut_72 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_73'] = x_apply_statistical_gates__mutmut_73 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_74'] = x_apply_statistical_gates__mutmut_74 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_75'] = x_apply_statistical_gates__mutmut_75 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_76'] = x_apply_statistical_gates__mutmut_76 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_77'] = x_apply_statistical_gates__mutmut_77 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_78'] = x_apply_statistical_gates__mutmut_78 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_79'] = x_apply_statistical_gates__mutmut_79 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_80'] = x_apply_statistical_gates__mutmut_80 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_81'] = x_apply_statistical_gates__mutmut_81 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_82'] = x_apply_statistical_gates__mutmut_82 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_83'] = x_apply_statistical_gates__mutmut_83 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_84'] = x_apply_statistical_gates__mutmut_84 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_85'] = x_apply_statistical_gates__mutmut_85 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_86'] = x_apply_statistical_gates__mutmut_86 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_87'] = x_apply_statistical_gates__mutmut_87 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_88'] = x_apply_statistical_gates__mutmut_88 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_89'] = x_apply_statistical_gates__mutmut_89 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_90'] = x_apply_statistical_gates__mutmut_90 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_91'] = x_apply_statistical_gates__mutmut_91 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_92'] = x_apply_statistical_gates__mutmut_92 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_93'] = x_apply_statistical_gates__mutmut_93 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_94'] = x_apply_statistical_gates__mutmut_94 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_95'] = x_apply_statistical_gates__mutmut_95 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_96'] = x_apply_statistical_gates__mutmut_96 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_97'] = x_apply_statistical_gates__mutmut_97 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_98'] = x_apply_statistical_gates__mutmut_98 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_99'] = x_apply_statistical_gates__mutmut_99 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_100'] = x_apply_statistical_gates__mutmut_100 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_101'] = x_apply_statistical_gates__mutmut_101 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_102'] = x_apply_statistical_gates__mutmut_102 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_103'] = x_apply_statistical_gates__mutmut_103 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_104'] = x_apply_statistical_gates__mutmut_104 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_105'] = x_apply_statistical_gates__mutmut_105 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_106'] = x_apply_statistical_gates__mutmut_106 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_107'] = x_apply_statistical_gates__mutmut_107 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_108'] = x_apply_statistical_gates__mutmut_108 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_109'] = x_apply_statistical_gates__mutmut_109 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_110'] = x_apply_statistical_gates__mutmut_110 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_111'] = x_apply_statistical_gates__mutmut_111 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_112'] = x_apply_statistical_gates__mutmut_112 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_113'] = x_apply_statistical_gates__mutmut_113 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_114'] = x_apply_statistical_gates__mutmut_114 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_115'] = x_apply_statistical_gates__mutmut_115 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_116'] = x_apply_statistical_gates__mutmut_116 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_117'] = x_apply_statistical_gates__mutmut_117 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_118'] = x_apply_statistical_gates__mutmut_118 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_119'] = x_apply_statistical_gates__mutmut_119 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_120'] = x_apply_statistical_gates__mutmut_120 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_121'] = x_apply_statistical_gates__mutmut_121 # type: ignore # mutmut generated
mutants_x_apply_statistical_gates__mutmut['x_apply_statistical_gates__mutmut_122'] = x_apply_statistical_gates__mutmut_122 # type: ignore # mutmut generated
