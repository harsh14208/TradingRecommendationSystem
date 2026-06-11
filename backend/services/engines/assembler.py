"""Final-signal assembler (BE-1 refactor).

``_assemble_signal`` extracted verbatim from ``signal_engine.py``. Applies risk
gates, calibrates confidence, derives style, and builds the final signal dict.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import numpy as _np

from services.engines.helpers import (
    _ET,
    _LEVERAGED_ETFS,
    _SECTOR_MR_CONFIG,
    _current_session,
    _levels,
    _make_plain_english,
    _score_to_action,
)
from services.sector import SECTOR_MAP

log = logging.getLogger("signal.trade.engine")


def _assemble_signal(
    *,
    ticker: str,
    info: dict,
    tech: dict,
    score: float,
    rationale: list,
    sources: set,
    _force_hold: bool,
    _is_low_atr: bool,
    _atr_pct_pre: float,
    total_confidence_penalty: float,
    portfolio_size_scale: float = 1.0,
    avg_sent: float,
    price: float,
    atr: float,
    market_ctx: Optional[dict],
    earnings_cal: dict,
    sector_rs: Optional[dict],
    days_to_earnings: Optional[int],
    opt_flow: Optional[dict] = None,
    _is_lev_etf: bool = False,
    data_warnings: Optional[list[dict]] = None,
    days_to_exdiv: Optional[int] = None,
) -> Optional[dict]:
    """
    Apply risk gates, calibrate confidence, derive style, and build
    the final signal dict. Returns None if action is forced to HOLD
    and confidence < threshold.
    """
    # Derive macro/regime variables from market_ctx inline.
    macro = (market_ctx or {}).get("macro") or {}
    vix = macro.get("vix")
    sp500_trend = macro.get("sp500_trend")

    # ── MR entry condition flags — computed early so all downstream gates can use them ─
    # These are referenced by the VIX gate (~line 829) and many later gates;
    # defining them here once prevents UnboundLocalError from forward-references.
    _mr_bb = tech.get("bb_pct_b")
    _mr_ibs = tech.get("ibs")
    _mr_vwap = tech.get("vwap_pct")
    # MR-count-2 (backtest-validated 2026-06-09):
    # Require ≥2 of 4 oversold conditions instead of 1. Backtest showed:
    #   MR-count=1 → 155 trades, Sharpe 0.20
    #   MR-count=2 → 154 trades, Sharpe 0.21 (+0.01, -1 trade)
    # Single-condition MR setups (e.g. IBS-only) are the weakest class and
    # disproportionately hit stops. Requiring 2+ filters these without
    # materially reducing trade count.
    _mr_rsi_trig = float(tech.get("rsi") or 50) < 42
    _mr_bb_trig = _mr_bb is not None and float(_mr_bb) < 0.22
    _mr_ibs_trig = _mr_ibs is not None and float(_mr_ibs) < 0.15
    _mr_vwap_trig = _mr_vwap is not None and float(_mr_vwap) < -0.75
    _has_mr = sum([_mr_rsi_trig, _mr_bb_trig, _mr_ibs_trig, _mr_vwap_trig]) >= 2

    # ── Assemble final signal ───────────────────────────────────────
    # Enforce any blackout/gate that set _force_hold=True mid-scoring.
    # score=0 alone is not sufficient because subsequent signal blocks
    # (e.g. macro, options, institutional) can re-inflate it back above
    # the ±25 BUY/SELL threshold. The flag survives all subsequent scoring.
    if _force_hold:
        score = 0.0  # ensure no stale residual from post-zero signals

    data_warnings = data_warnings or []
    if data_warnings:
        sources.add("Data Quality")
        affected = ", ".join(w.get("source", "unknown") for w in data_warnings[:4])
        extra = "" if len(data_warnings) <= 4 else f" and {len(data_warnings) - 4} more"
        rationale.append(
            {
                "src": "Data Quality",
                "head": "Partial Data Degradation",
                "body": (
                    f"{ticker} signal generated with partial provider coverage. "
                    f"Unavailable source(s): {affected}{extra}. Technical scoring still ran, "
                    "but confidence should be interpreted with this data gap in mind."
                ),
                "sentiment": "neu",
                "meta": "missing_sources=" + ",".join(w.get("source", "unknown") for w in data_warnings),
            }
        )

    # Agreement count excludes meta-signals that are artifacts of the scoring
    # machinery rather than independent evidence (Risk Gate, Orthogonalization,
    # Signal Cluster, Backtest). Counting them inflated the agreement bonus for
    # any signal with many firing post-processing checks.
    _META_SRCS = {"Risk Gate", "Orthogonalization", "Signal Cluster", "Backtest"}
    agree_sent = "pos" if score > 0 else "neg"
    agreement = sum(1 for r in rationale if r.get("sentiment") == agree_sent and r.get("src") not in _META_SRCS)
    action, confidence = _score_to_action(score, agreement)

    # Enforce blackout action regardless of what _score_to_action computed.
    if _force_hold:
        action = "HOLD"

    # ── Chronic-Loser Ticker Exclusion ──────────────────────────────────
    adaptive = (market_ctx or {}).get("adaptive_weights", {})
    ticker_wrs = adaptive.get("ticker_win_rates", {})
    ticker_wr = ticker_wrs.get(ticker)
    if action == "BUY" and ticker_wr is not None and ticker_wr < 0.45:
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"Chronic Loser Exclusion — Win Rate {ticker_wr * 100:.0f}%",
                "body": (
                    f"{ticker} has a historical win rate below 45%. BUY signals on "
                    "persistent structural underperformers are mathematically "
                    "negative expected value. Signal excluded."
                ),
                "sentiment": "neg",
                "meta": f"Win rate {ticker_wr * 100:.0f}% < 45%",
            }
        )

    # ── True Orthogonality Minimum ──────────────────────────────────────
    _core_families = {
        "Technical",
        "Options",
        "13F",
        "SEC EDGAR",
        "Congress",
        "Fundamentals",
        "Macro",
        "Dark Pool",
        "Short Interest",
        "Analyst",
        "Social",
    }
    _active_families = len([s for s in sources if s in _core_families])
    if action == "BUY" and _active_families < 3 and score < 50:
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"Orthogonality Gate — Only {_active_families}/3 Source Families",
                "body": (
                    "A reliable BUY signal requires convergence from at least 3 independent "
                    "data families (e.g., Technical + Options + Fundamentals). Correlated "
                    "indicators within the same family do not provide enough independent edge."
                ),
                "sentiment": "neg",
                "meta": f"Active families: {_active_families} < 3",
            }
        )

    # ── Technical-Only SELL Gate ────────────────────────────────────────
    # 30-year backtest shows technical-only SELL signals average -0.71%/trade.
    # Require at least one non-technical confirmation (Options, Macro, News, etc.)
    _alt_data_sources = {
        "Options",
        "Macro",
        "13F",
        "SEC EDGAR",
        "Dark Pool",
        "Insider",
        "Congress",
        "Analyst",
        "Fundamentals",
        "Earnings",
        "Benzinga",
        "Finnhub",
        "Reuters",
        "Finviz",
        "Social",
    }
    _has_alt = any(s in _alt_data_sources for s in sources)
    if action == "SELL" and not _has_alt:
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": "Technical-Only SELL Gate — Missing Alt-Data Confirmation",
                "body": (
                    "30-year backtesting shows technical-only SELL signals have negative "
                    "expected value (-0.71% avg return). SELL signals require confirmation "
                    "from at least one alternative data source (Options, Macro, News, etc.) "
                    "to fire. Signal gated to HOLD."
                ),
                "sentiment": "neg",
                "meta": "technical_only_sell=True",
            }
        )

    # ── Volume / liquidity / momentum-quality pipeline ──────────────────────
    # Constructs a SignalContext once (reused by all downstream pipelines).
    # rationale and sources are the same list/set objects — mutated in place.
    from services.gates.base import GatePipeline, SignalContext as _SCtx
    from services.gates.volume import (
        AdxGate,
        DollarVolumeGate,
        OverboughtWeakTrendGate,
        RvolGate,
    )

    _se_sector_etf_ctx = (sector_rs or {}).get("sector_etf") or SECTOR_MAP.get(ticker.upper(), "")
    _sig_ctx = _SCtx(
        action=action,
        confidence=confidence,
        score=score,
        rationale=rationale,
        sources=sources,
        ticker=ticker,
        tech=tech,
        info=info,
        macro=macro,
        price=price,
        atr=atr,
        has_mr=_has_mr,
        vix=vix,
        sp500_trend=sp500_trend,
        sector_etf=_se_sector_etf_ctx,
        today_dow=datetime.now(_ET).weekday(),
        month=datetime.now(timezone.utc).month,
        opt_flow=opt_flow,
        sector_rs=sector_rs,
        earnings_cal=earnings_cal,
        days_to_earnings=days_to_earnings,
        is_low_atr=_is_low_atr,
        atr_pct_pre=_atr_pct_pre,
        sector_config=_SECTOR_MR_CONFIG.get(_se_sector_etf_ctx, {}),
        is_lev_etf=_is_lev_etf,
    )

    GatePipeline([RvolGate(), AdxGate(), OverboughtWeakTrendGate(), DollarVolumeGate()]).run(_sig_ctx)

    # Sync mutable state back; rationale/sources already mutated in place.
    action = _sig_ctx.action
    confidence = _sig_ctx.confidence
    score = _sig_ctx.score
    # Keep aliases needed by remaining inline gates below.
    _adx_gate = tech.get("adx")
    _rsi_gate = float(tech.get("rsi") or 50)

    # ── Low-volatility stock BUY gate ───────────────────────────────────
    # Stocks with ATR < 0.8% of price (KO, PEP, T, JNJ, WFC, etc.) have
    # tight, mean-reverting price action where technical breakout signals
    # fail at much higher rates. Validation: ALL such tickers had 0% win
    # rates despite 70-85% confidence. Require a stronger score (≥35) and
    # a non-negative macro environment before issuing a BUY.
    atr_pct = atr / price if price > 0 else 0.02
    _macro_score_now = macro.get("macro_score", 0) if macro else 0
    if action == "BUY" and atr_pct < 0.007:
        # Hard block: ATR < 0.7%/day means the stock can't generate enough 5-day
        # return to clear friction. 20-year backtest showed these trades drag avg
        # return by -0.20%+ even in positive macro environments.
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"Minimum ATR Gate — ATR {atr_pct * 100:.2f}% Below 0.7% Floor",
                "body": (
                    f"ATR is {atr_pct * 100:.2f}% of price — stock moves too little to generate "
                    "returns above friction in a 5-day hold. Backtest confirmed these trades "
                    "are negative expected value across all macro environments."
                ),
                "sentiment": "neg",
                "meta": f"ATR%: {atr_pct * 100:.2f}% < 0.7% floor",
            }
        )

    # ── Defensive-ticker BUY gate ────────────────────────────────────────
    # Tickers that showed 0% BUY win rate across ≥3 resolved signals in the
    # May 2026 validation (n=529). These span low-vol defensives, banks, and
    # consumer staples where momentum signals structurally misfire.
    # The ATR gate above catches KO/PEP/T; this gate covers higher-ATR names
    # (BAC, C, USB, PNC, TGT, etc.) that slip past the ATR threshold.
    _DEFENSIVE_BUY_BLOCK = {
        # Live-validated 0% BUY win rate (May 2026, n=529 resolved signals).
        # All entries here come from FORWARD performance data — NOT from
        # the 20yr backtest. Backtest-derived exclusions were removed (audit
        # finding: hardcoding tickers found via historical backtest is look-ahead
        # selection bias). The dynamic AR(1) momentum-persistence gate below
        # replaces those exclusions with a point-in-time quantitative rule.
        "KO",
        "PEP",
        "T",
        "NEE",
        "PG",
        "USB",
        "PNC",
        "C",
        "AIG",
        "WM",
        "MCO",
        "TT",
        "DE",
        "TJX",
        # Live validated 0% WR (May 2026, §11b ticker analysis)
        "APH",  # 0/4 trades, avg -8.70% — worst live ticker
        "EOG",  # 0/2 trades, avg -7.00% — energy, structurally weak on MR signals
        "SYK",  # 0/1 trades, avg -6.81% — healthcare, earnings-driven not technical
        "CVX",  # 0/2 trades, avg -5.99% — energy/macro driven
        "UPS",  # 0/1 trades, avg -6.31% — logistics, cyclical/macro not chart
        # Backtest-validated: event-driven / range-bound / non-technical
        # Pharma (drug-approval dominated, not chart-driven)
        "ABBV",
        "MRK",
        "PFE",
        "LLY",
        "TMO",
        # Consumer staples / tobacco (low-ATR, mean-reverting)
        "PM",
        "WMT",
        # Analog/commodity semiconductors (earnings-cycle driven)
        "TXN",
        # Consumer brand (fashion cycles, not technical)
        "NKE",
        # Payments (behaves like a financial in stress)
        "V",
        # TSLA, SBUX, GS, MA, BLK, SCHW, PANW, GEN, CPAY — REMOVED.
        # Were added based on 20yr backtest negative avg return (look-ahead bias).
        # Now handled dynamically by the AR(1) momentum-persistence gate below.
    }
    if action == "BUY" and ticker in _DEFENSIVE_BUY_BLOCK:
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"Defensive-Ticker BUY Gate — {ticker} Blocked",
                "body": (
                    f"{ticker} is in the defensive block: either 0% live BUY win rate (n≥3) "
                    "or negative avg return across 20yr technical backtest. "
                    "Price action is event-driven, macro-driven, or non-MR-responsive. "
                    "BUY gated to HOLD until re-validation shows positive expected value."
                ),
                "sentiment": "neg",
                "meta": f"Ticker: {ticker} | Gate: defensive_ticker_block",
            }
        )

    # ── Fundamental Value-Trap Gate (see gates/fundamentals.py) ─────────────
    from services.gates.fundamentals import FundamentalValueTrapGate as _VTGate

    _sig_ctx.action = action
    _sig_ctx.confidence = confidence
    _sig_ctx.score = score
    GatePipeline([_VTGate()]).run(_sig_ctx)
    action = _sig_ctx.action
    confidence = _sig_ctx.confidence
    score = _sig_ctx.score

    # ── Leveraged / inverse-leveraged ETF disclosure ─────────────────────
    # Always fire for any leveraged ETF signal, regardless of action.
    # Fundamentals, earnings, and insider scoring are already bypassed upstream;
    # this card surfaces the decay risk to the user and confirms the bypass.
    if ticker in _LEVERAGED_ETFS:
        _lev_bull = ticker not in {
            "SQQQ",
            "SPXS",
            "SPXU",
            "SOXS",
            "TECS",
            "FAZ",
            "TZA",
            "LABD",
            "FNGD",
            "YANG",
            "DRV",
            "TMV",
            "HIBS",
            "SRTY",
            "DRIP",
            "DUST",
            "JDST",
            "SCO",
            "SDS",
            "QID",
            "REW",
            "TWM",
        }
        _mult = (
            "3×"
            if ticker
            not in {
                "GUSH",
                "DRIP",
                "NUGT",
                "DUST",
                "JNUG",
                "JDST",
                "UCO",
                "SCO",
                "SSO",
                "SDS",
                "QLD",
                "QID",
                "ROM",
                "REW",
                "UWM",
                "TWM",
                "INDL",
            }
            else "2×"
        )
        _dir = "Bull" if _lev_bull else "Bear (Inverse)"
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"{_mult} Leveraged ETF — {_dir} | Hold ≤5 Days",
                "body": (
                    f"{ticker} is a {_mult} {_dir} leveraged ETF. Each 1% move in the "
                    f"underlying index produces approximately {_mult} in this ETF. "
                    "Key risks: (1) Volatility decay — daily rebalancing causes "
                    "compounding drag; a 10% round-trip in the underlying can cost "
                    "2–8% of NAV even if price returns to start. "
                    "(2) No fundamental scoring — P/E, FCF, earnings, insider activity, "
                    "and analyst revisions are not applicable and have been bypassed. "
                    "(3) Signals are based on technical and macro factors only. "
                    "Recommended maximum hold: swing (2–5 trading days). "
                    "Use position sizing of ⅓ or less vs an equivalent single-stock trade."
                ),
                "sentiment": "neg",
                "meta": f"type=leveraged_etf | mult={_mult} | dir={'bull' if _lev_bull else 'bear'}",
            }
        )

    # ── Market-cap tier modifier ──────────────────────────────────────────
    # Mega-caps ($500B+) have wall-to-wall analyst coverage, crowded positioning,
    # and slower momentum decay — momentum signals are less differentiated.
    # Small-caps (<$2B) add a volatility premium notice to the rationale.
    _mktcap = info.get("market_cap")
    if _mktcap and action in ("BUY", "SELL") and not _is_lev_etf:
        if _mktcap >= 500_000_000_000:  # mega-cap ≥ $500B
            confidence = round(max(35.0, confidence - 2), 1)
            sources.add("Risk Gate")
            rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Mega-Cap Crowding Haircut (${_mktcap / 1e12:.1f}T)",
                    "body": (
                        f"Market cap of ${_mktcap / 1e12:.1f}T means this stock has wall-to-wall analyst "
                        "coverage, crowded institutional positioning, and slower-decaying momentum. "
                        "Edge is smaller vs mid/small cap — confidence haircut applied."
                    ),
                    "sentiment": "neg",
                    "meta": f"mktcap=${_mktcap / 1e9:.0f}B | tier=mega | adj=-2pp",
                }
            )
        elif _mktcap < 2_000_000_000:  # small-cap < $2B
            sources.add("Risk Gate")
            rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Small-Cap Volatility Notice (${_mktcap / 1e9:.1f}B)",
                    "body": (
                        f"Market cap of ${_mktcap / 1e9:.1f}B — small-cap territory. Higher volatility, "
                        "wider bid-ask spreads, and lower liquidity amplify both gains and losses. "
                        "Size position accordingly (suggest ½ of normal allocation)."
                    ),
                    "sentiment": "neg",
                    "meta": f"mktcap=${_mktcap / 1e9:.1f}B | tier=small",
                }
            )

    # ── Pre-options technicals pipeline (Part 1: stress + regime + SMA gates) ─────
    # Runs: StlfsiVixGate → GlobalVixMinGate → Sma200BuyGate → SellUptrendGate
    #       → SpyNeutralZoneGate → BearHighVixGate
    from services.gates.technicals import (
        BearHighVixGate as _BHVGate,
        GlobalVixMinGate as _GVMGate,
        Sma200BuyGate as _S200Gate,
        SellUptrendGate as _SellUTGate,
        SpyNeutralZoneGate as _SpyNZGate,
        StlfsiVixGate as _StlfsiGate,
    )

    _sig_ctx.action = action
    _sig_ctx.confidence = confidence
    _sig_ctx.score = score
    GatePipeline(
        [
            _StlfsiGate(),
            _GVMGate(),
            _S200Gate(),
            _SellUTGate(),
            _SpyNZGate(),
            _BHVGate(),
        ]
    ).run(_sig_ctx)
    action = _sig_ctx.action
    confidence = _sig_ctx.confidence
    score = _sig_ctx.score

    # ── BUY:SELL saturation circuit breaker ─────────────────────────────
    # When the rolling 7-day BUY:SELL ratio exceeds 4:1, the system is over-
    # optimistic. Raise the effective BUY threshold to 42 so only high-conviction
    # signals survive. SELL signals are never suppressed by this gate — the
    # circuit breaker only corrects the bullish bias, not the bearish direction.
    if action == "BUY" and (market_ctx or {}).get("buy_saturated") and score < 42:
        action = "HOLD"
        _ratio = (market_ctx or {}).get("buy_sell_ratio", 4.0)
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"BUY Saturation Gate — 7d BUY:SELL Ratio {_ratio:.1f}:1 (>4.0)",
                "body": (
                    f"The system has generated {_ratio:.1f} BUY signals for every SELL signal "
                    "over the past 7 days — a sign of structural over-optimism. "
                    "Marginal BUY signals (score <42) are suppressed until the ratio normalises below 4.0."
                ),
                "sentiment": "neg",
                "meta": f"7d BUY:SELL = {_ratio:.1f}:1 | Score: {score:.1f}",
            }
        )

    # ── Broad market breadth BUY gate ───────────────────────────────────
    # When >70% of S&P 500 stocks are above their 200-DMA, the technical
    # baseline is already elevated: Supertrend, price structure, and momentum
    # signals all default positive, adding ~+15 pts before any real edge fires.
    # Require a stronger score (≥42) to confirm genuine alpha beyond the tide.
    # SELL signals are never gated here — breadth strength doesn't protect shorts.
    if action == "BUY" and score < 42:
        _breadth_ctx = (market_ctx or {}).get("breadth") or {}
        _pct_200 = _breadth_ctx.get("pct_above_200d", 0) or 0
        if _pct_200 > 70:
            action = "HOLD"
            sources.add("Risk Gate")
            rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Broad Market Breadth Gate — {_pct_200:.0f}% Above 200-DMA (Score {score:.0f} < 42)",
                    "body": (
                        f"{_pct_200:.0f}% of S&P 500 stocks are above their 200-day average — "
                        "technical baselines (Supertrend, momentum, price structure) are uniformly "
                        "elevated, adding ~15 pts of structural noise to every BUY signal. "
                        "Requiring score ≥42 ensures only genuine alpha clears the bar."
                    ),
                    "sentiment": "neg",
                    "meta": f"Breadth: {_pct_200:.0f}% >200d | Score: {score:.1f}",
                }
            )

    # ── Pre-options technicals pipeline (Part 2: MR quality gates) ─────────────
    # Runs: MrPersistenceGate → MrEntryConditionGate → IbsSma20ConfluenceGate
    #       → AtrRankFloorGate → SectorVixFloorGate → AtrRankCeilingGate
    #       → ReturnJumpGate → VixDirectionGate
    from services.gates.technicals import (
        AtrRankCeilingGate as _ARCGate,
        AtrRankFloorGate as _ARFGate,
        IbsSma20ConfluenceGate as _IBSGate,
        MrEntryConditionGate as _MRECGate,
        MrPersistenceGate as _MRPGate,
        ReturnJumpGate as _RJGate,
        SectorVixFloorGate as _SVFGate,
        VixDirectionGate as _VDGate,
    )

    _sig_ctx.action = action
    _sig_ctx.confidence = confidence
    _sig_ctx.score = score
    GatePipeline(
        [
            _MRPGate(),
            _MRECGate(),
            _IBSGate(),
            _ARFGate(),
            _SVFGate(),
            _ARCGate(),
            _RJGate(),
            _VDGate(),
        ]
    ).run(_sig_ctx)
    action = _sig_ctx.action
    confidence = _sig_ctx.confidence
    score = _sig_ctx.score

    # ── Options flow pipeline ───────────────────────────────────────────────
    # _sig_ctx is the same SignalContext object built in the volume pipeline
    # above — reuse it with updated action/confidence/score already synced.
    # Runs: OptionsFlowConfirmationGate → IvRankFlagGate → IvrMrGate →
    #       PutCallSkewGate → IvTermStructureGate → PutSweepCapitulationGate
    from services.gates.options import (
        IvRankFlagGate,
        IvTermStructureGate,
        IvrMrGate,
        OptionsFlowConfirmationGate,
        PutCallSkewGate,
        PutSweepCapitulationGate,
    )

    # Refresh mutable state on the context before running (downstream inline
    # gates may have changed action/confidence since the volume pipeline ran).
    _sig_ctx.action = action
    _sig_ctx.confidence = confidence
    _sig_ctx.score = score

    GatePipeline(
        [
            OptionsFlowConfirmationGate(),
            IvRankFlagGate(),
            IvrMrGate(),
            PutCallSkewGate(),
            IvTermStructureGate(),
            PutSweepCapitulationGate(),
        ]
    ).run(_sig_ctx)

    action = _sig_ctx.action
    confidence = _sig_ctx.confidence
    score = _sig_ctx.score

    # ── Post-options technicals pipeline ──────────────────────────────────────
    # Runs: SectorScoreFloorGate → NearEarningsCautionGate → DeepBearRsiGate
    #       → SustainedBearGate → PriceSma20DistanceGate
    from services.gates.technicals import (
        DeepBearRsiGate as _DBRGate,
        NearEarningsCautionGate as _NECGate,
        PriceSma20DistanceGate as _PS20Gate,
        SectorScoreFloorGate as _SSFGate,
        SustainedBearGate as _SBGate,
    )

    _sig_ctx.action = action
    _sig_ctx.confidence = confidence
    _sig_ctx.score = score
    GatePipeline(
        [
            _SSFGate(),
            _NECGate(),
            _DBRGate(),
            _SBGate(),
            _PS20Gate(),
        ]
    ).run(_sig_ctx)
    action = _sig_ctx.action
    confidence = _sig_ctx.confidence
    score = _sig_ctx.score

    # ── §57 DOW gate + §77 tax-loss window ─────────────────────────────────
    from services.gates.calendar import apply_calendar_gates as _cal_gates

    _today_dow = datetime.now(_ET).weekday()  # 0=Mon … 4=Fri
    _month_now = datetime.now(timezone.utc).month
    action, confidence, _cal_cards, _cal_sources = _cal_gates(
        action=action,
        confidence=confidence,
        score=score,
        today_dow=_today_dow,
        month=_month_now,
        price=price,
        info=info,
    )
    rationale.extend(_cal_cards)
    sources.update(_cal_sources)

    # Apply combined post-processing confidence penalty (warning signals + low volume)
    if total_confidence_penalty > 0 and action in ("BUY", "SELL"):
        confidence = round(max(35.0, confidence * (1 - total_confidence_penalty)), 1)

    # ── Macro Contradiction Cap ──────────────────────────────────────────
    # A BUY signal at ≥70% confidence while macro is meaningfully bearish
    # (macro_score < −3) is a contradiction: the stock-level technicals say
    # buy, but the macro environment says sell everything. Cap confidence at
    # 65% to reflect the elevated failure rate of these cross-current setups.
    # Symmetric: a SELL at ≥70% confidence with a bullish macro is capped too.
    #
    # _conf_macro_cap tracks the strictest macro cap so the hard final ceiling
    # can re-enforce it after adaptive win-rate / yield-dampener adjustments,
    # which run later and could otherwise push confidence back above the cap.
    _conf_macro_cap = 72.0  # default = hard ceiling (no active cap)
    if action in ("BUY", "SELL") and confidence >= 70:
        _m_score = macro.get("macro_score", 0) if macro else 0
        _m_contradiction = (_m_score < -3 and action == "BUY") or (_m_score > 3 and action == "SELL")
        if _m_contradiction:
            _conf_macro_cap = min(_conf_macro_cap, 65.0)
            confidence = round(min(confidence, 65.0), 1)
            rationale.append(
                {
                    "src": "Macro",
                    "head": "Macro Contradiction — Confidence Capped at 65%",
                    "body": (
                        f"Macro score is {_m_score:+.0f} ({'bearish' if _m_score < 0 else 'bullish'}), "
                        f"contradicting the {action} signal. High-confidence {action} signals "
                        "in a contradictory macro environment have significantly lower win rates. "
                        "Confidence capped at 65% until macro aligns."
                    ),
                    "sentiment": "neg",
                    "meta": f"Macro score: {_m_score:+.0f} | Action: {action}",
                }
            )

    # ── Macro News Sentiment BUY Cap ─────────────────────────────────────
    # When SPY/QQQ ETF news is strongly negative AND VIX > 20, cap all BUY signals at 65%.
    if action == "BUY":
        _news_sent = (macro or {}).get("macro_news_sentiment")
        _vix_now = (macro or {}).get("vix") or 0
        if _news_sent is not None and _news_sent < -0.3 and _vix_now > 20:
            _new_cap = 65.0
            _conf_macro_cap = min(_conf_macro_cap, _new_cap)
            if confidence > _new_cap:
                confidence = round(min(confidence, _new_cap), 1)
                rationale.append(
                    {
                        "src": "Macro",
                        "head": f"Macro News Negative (SPY/QQQ) — BUY Cap {_new_cap:.0f}%",
                        "body": (
                            f"ETF-level news sentiment is {_news_sent:+.2f} (negative) with VIX at {_vix_now:.1f}. "
                            "Broad-market news fear combined with elevated volatility caps BUY confidence "
                            "until macro news normalises."
                        ),
                        "sentiment": "neg",
                        "meta": f"macro_news_sentiment={_news_sent:+.2f} vix={_vix_now:.1f}",
                    }
                )

    # ── Adaptive confidence from historical win rates (VIX-adjusted) ───────
    # In high-volatility regimes, historical win rates are less predictive —
    # patterns break down when VIX is elevated. Dampen the adjustment accordingly.
    adaptive = (market_ctx or {}).get("adaptive_weights", {})
    if adaptive and action in ("BUY", "SELL"):
        wr_key = f"{action}_win_rate"
        win_rate = adaptive.get(wr_key)
        if win_rate is not None:
            # Volatility dampener: reduce the historical-accuracy adjustment under stress.
            # Thresholds mirror the VIX score multipliers (35/25/15) so both adjustments
            # activate at the same regime boundaries rather than misaligned breakpoints.
            vix_dampener = 1.0
            if vix is not None:
                if vix > 35:
                    vix_dampener = 0.40  # panic regime — history unreliable (mirrors 0.60× score mult)
                elif vix > 25:
                    vix_dampener = 0.60  # elevated vol (mirrors 0.82× score mult)
                elif vix > 15:
                    vix_dampener = 0.85  # slightly elevated (mirrors 1.06× score boost boundary)
            wr_delta = round((win_rate - 0.50) * 16 * vix_dampener, 1)
            confidence = round(min(72.0, max(35.0, confidence + wr_delta)), 1)
            if abs(wr_delta) >= 3:
                sources.add("Backtest")
                direction_lbl = "boosted" if wr_delta > 0 else "reduced"
                vix_note = (
                    f" (VIX {vix:.0f} → {vix_dampener:.0%} dampener applied)"
                    if vix is not None and vix_dampener < 1.0
                    else ""
                )
                rationale.append(
                    {
                        "src": "Backtest",
                        "head": f"Historical {action} Win Rate {win_rate * 100:.0f}% — Confidence {direction_lbl}",
                        "body": (
                            f"Past {action} signals have a {win_rate * 100:.0f}% win rate. "
                            f"Confidence adjusted {'+' if wr_delta > 0 else ''}{wr_delta:.1f} points.{vix_note}"
                        ),
                        "sentiment": "pos" if wr_delta > 0 else "neg",
                        "meta": f"{action} win rate: {win_rate * 100:.0f}%",
                    }
                )

    # ── Consecutive Loss Streak Suppression ─────────────────────────────
    # If this ticker has lost on N consecutive recent resolved signals, penalise
    # confidence by 5pp per loss beyond the first — max −20pp. Prevents the engine
    # from repeatedly issuing high-confidence signals on persistently failing setups.
    if action in ("BUY", "SELL") and adaptive:
        _loss_streaks = adaptive.get("ticker_loss_streaks", {})
        _streak = _loss_streaks.get(ticker, 0)
        if _streak >= 2:
            _streak_penalty = round(min(20.0, (_streak - 1) * 5.0), 1)
            confidence = round(max(35.0, confidence - _streak_penalty), 1)
            sources.add("Backtest")
            rationale.append(
                {
                    "src": "Backtest",
                    "head": f"{_streak}-Signal Loss Streak — Confidence Reduced",
                    "body": (
                        f"{ticker} has lost on {_streak} consecutive resolved signals. "
                        f"Confidence reduced by {_streak_penalty:.0f}pp until a winning signal breaks the streak."
                    ),
                    "sentiment": "neg",
                    "meta": f"Loss streak: {_streak} | Penalty: -{_streak_penalty:.0f}pp",
                }
            )

    # ── VIX Hard Confidence Floor ────────────────────────────────────────
    # Panic regimes (VIX > 30) mechanically increase realized volatility and
    # the correlation of all risk assets — directional edge deteriorates sharply.
    # Signals below 75% confidence have statistically poor win rates in these
    # conditions: "catching falling knives." Hard-gate to HOLD.
    if vix is not None and vix > 30 and action in ("BUY", "SELL") and confidence < 75:
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"VIX Regime Floor — {confidence:.0f}% Below 75% Threshold (VIX {vix:.0f})",
                "body": (
                    f"VIX at {vix:.0f} signals an active panic regime (threshold: 30). "
                    "In elevated-VIX environments, {}-confidence signals have historically poor "
                    "win rates — technical patterns break down as correlations spike and "
                    "liquidity thin outs. Signal gated to HOLD until VIX normalises below 30."
                ).format(f"{confidence:.0f}%"),
                "sentiment": "neg",
                "meta": f"VIX = {vix:.0f} | Min confidence gate: 75% | Actual: {confidence:.0f}%",
            }
        )

    # ── Style derivation from rationale composition ───────────────────────
    # Intraday wins over all — a fresh RSI extreme or Bollinger touch is a
    # short-term reversal play regardless of structural context.
    # Position only fires when genuinely structural signals (strong fundamentals,
    # confirmed institutional buying) dominate with NO short-term overrides.
    # Everything else defaults to swing.
    _heads_str = " || ".join(r.get("head", "") for r in rationale)

    _is_intraday = any(
        kw in _heads_str
        for kw in [
            "RSI Oversold",
            "RSI Overbought",
            "RSI Weakening",
            "RSI Elevated",
            "Bollinger Band Touch",
            "Bullish RSI Divergence",
            "Bearish RSI Divergence",
            "Stochastic Bullish Cross",
            "Stochastic Bearish Cross",
            "Williams %R Oversold",
            "Williams %R Overbought",
            "CCI Oversold",
            "CCI Overbought",
        ]
    )

    # "Position" requires STRONG fundamentals or CONFIRMED institutional
    # conviction — not just any Piotroski mention or minor institutional flow.
    # Previously, F-Score 3/9 and inst_score=6 would both set position=True,
    # causing 94% of signals to be classified as "position" (wrong style,
    # wrong hold time shown to users, wrong horizon in plain-English summary).
    #
    # New rules — position requires at LEAST one of:
    #   • Piotroski F-Score explicitly ≥7 in the head ("F-Score 7/9" or "8/9" or "9/9")
    #   • Strong FCF yield (already only fires for >8%)
    #   • Active share buyback (management signalling)
    #   • Institutional conviction TREND (QoQ rising/falling — requires 2+ quarters data)
    #   • Very strong institutional flow (score >10, not just >5)
    _is_position = (not _is_intraday) and any(
        kw in _heads_str
        for kw in [
            "F-Score 7",
            "F-Score 8",
            "F-Score 9",  # only high-quality F-scores
            "Strong FCF Yield",
            "Active Share Buyback",
            "Institutional Conviction Rising",  # QoQ trend required
            "Institutional Conviction Falling",
        ]
    )

    _inst_score = abs(((market_ctx or {}).get("institutional_signals") or {}).get(ticker, {}).get("score", 0))
    if _inst_score > 10:
        _is_position = True

    if _is_intraday:
        style = "intraday"
    elif _is_position:
        style = "position"
    else:
        style = "swing"

    # Leveraged/inverse ETFs accumulate volatility-decay drag beyond ~5 days.
    # Position-style hold times are incompatible with daily-rebalancing products.
    if _is_lev_etf and style == "position":
        style = "swing"

    entry, stop, target, rr = _levels(price, atr, action, style, rsi=_rsi_gate)

    # ── Risk-Free Rate Yield Dampener ────────────────────────────────────
    # Every equity trade competes against the risk-free rate. If the signal's
    # projected return (entry → target) doesn't clear a meaningful risk premium
    # over Treasuries, the trade has negative expected value on a Sharpe basis.
    t10y_rate = ((market_ctx or {}).get("macro") or {}).get("t10y")
    if t10y_rate and t10y_rate > 2.0 and action == "BUY" and entry and target and entry > 0:
        projected_pct = abs(target - entry) / entry * 100
        # Growth / high-beta sectors require a larger premium (investors face more risk)
        sector_etf_key = (sector_rs or {}).get("sector_etf") or SECTOR_MAP.get(ticker.upper(), "")
        high_beta = sector_etf_key in {"XLK", "XLC", "XLY", "XLB"}
        required_premium = 3.5 if high_beta else 2.0  # pp above risk-free
        excess = projected_pct - t10y_rate - required_premium

        if excess < -required_premium:
            # Projected return doesn't even beat the risk-free rate outright
            confidence = round(max(35.0, confidence - 14), 1)
            sources.add("Macro")
            rationale.append(
                {
                    "src": "Macro",
                    "head": f"Risk-Adjusted Return Negative vs Bonds ({projected_pct:.1f}% target vs {t10y_rate:.1f}% risk-free)",
                    "body": (
                        f"Signal target implies a {projected_pct:.1f}% return — below the "
                        f"{t10y_rate:.1f}% 10-Year Treasury yield. Holding risk-free bonds "
                        "dominates this trade on a Sharpe basis. Confidence reduced significantly."
                    ),
                    "sentiment": "neg",
                    "meta": f"Projected {projected_pct:.1f}% | 10Y {t10y_rate:.1f}% | Premium: {excess:.1f}pp",
                }
            )
        elif excess < 0:
            # Return beats risk-free but misses the required risk premium
            penalty = round(abs(excess) / required_premium * 8, 1)
            confidence = round(max(35.0, confidence - penalty), 1)
            sources.add("Macro")
            rationale.append(
                {
                    "src": "Macro",
                    "head": f"Thin Risk Premium Over Bonds ({projected_pct:.1f}% vs {t10y_rate:.1f}% + {required_premium:.1f}pp premium)",
                    "body": (
                        f"Projected return of {projected_pct:.1f}% only clears the risk-free rate "
                        f"by {projected_pct - t10y_rate:.1f}pp — below the {required_premium:.1f}pp "
                        "risk premium required for this sector's beta. "
                        "The marginal risk-adjusted case is weak."
                    ),
                    "sentiment": "neg",
                    "meta": f"Excess return: {projected_pct - t10y_rate:.1f}pp | Required: {required_premium:.1f}pp",
                }
            )
        elif excess > required_premium * 2:
            # Generous excess return — genuine edge over risk-free
            boost = min(5.0, excess * 0.3)
            confidence = round(min(72.0, confidence + boost), 1)
            sources.add("Macro")
            rationale.append(
                {
                    "src": "Macro",
                    "head": f"Strong Risk-Adjusted Return ({projected_pct:.1f}% target, {excess:.1f}pp above hurdle)",
                    "body": (
                        f"Signal target of {projected_pct:.1f}% clears the {t10y_rate:.1f}% risk-free rate "
                        f"by {projected_pct - t10y_rate:.1f}pp — {excess:.1f}pp above the "
                        f"{required_premium:.1f}pp required premium. Genuine Sharpe-positive edge."
                    ),
                    "sentiment": "pos",
                    "meta": f"Excess return: {excess:.1f}pp above hurdle | 10Y: {t10y_rate:.1f}%",
                }
            )

    # ── §64/§65/§66/§68 macro extension gates ─────────────────────────────
    from services.gates.macro_extensions import score_macro_extensions as _macro_ext

    _sector_etf_key = (sector_rs or {}).get("sector_etf") or SECTOR_MAP.get(ticker.upper(), "")
    confidence, _mext_cards, _mext_sources = _macro_ext(
        action=action,
        confidence=confidence,
        macro=macro,
        sector_etf=_sector_etf_key,
    )
    rationale.extend(_mext_cards)
    sources.update(_mext_sources)

    plain_english = _make_plain_english(action, ticker, style, rationale, confidence, entry, stop, target)

    headline = (
        f"{rationale[0]['head']} · {len(rationale)} signals agree"
        if len(rationale) > 1
        else (rationale[0]["head"] if rationale else f"{action} signal detected")
    )

    # Persist raw confidence so downstream calibration trains on the pre-calibrated
    # value, avoiding an iterative isotonic-on-isotonic feedback loop.
    raw_confidence = confidence

    # ── XGBoost confidence adjustment (signal model + entry model) ───────
    # Two complementary models blended 50/50 before a single ±25% adjustment:
    #   Signal model  — trained on live DB signals (metadata quality)
    #   Entry model   — trained on 23yr backtest (technical setup quality)
    # Gracefully skipped when models are absent or xgboost is not installed.
    _day_chg_pct = tech.get("change_pct")  # used in ML feature dict below
    _shadow_scores = None
    if action in ("BUY", "SELL"):
        try:
            from services.signal_ml import (
                blend_confidence as _ml_blend,
                get_challenger_model as _get_challenger_model,
                get_model as _get_live_model,
                predict_challenger_prob as _pred_challenger,
                predict_entry_prob_sector as _pred_entry_sector,
                predict_live_prob as _pred_live,
                predict_meta_prob as _pred_meta,
            )

            _live_model = _get_live_model()
            # §93a: decouple static sector lookup from RS fetch — sector-specific
            # entry models were under-applied when RS data failed (81% of signals).
            _sector_etf_ml = (sector_rs or {}).get("sector_etf") or SECTOR_MAP.get(ticker.upper())

            _sig_dict_ml = {
                "raw_score": score,
                "sentiment": avg_sent,
                "sources": list(sources),
                "rationale": rationale,
                "action": action,
                "style": style,
                "rr": rr,
                "entry": entry,
                "stop": stop,
                "target": target,
                "price": price,
                "session": _current_session(),
                "change_pct": _day_chg_pct,
                "days_to_earnings": days_to_earnings,
                "sector_etf": _sector_etf_ml,
                "rs_vs_sector": (sector_rs or {}).get("rs_vs_sector"),
            }
            _live_prob = _pred_live(_sig_dict_ml, _live_model)
            # Use sector-specific entry model when available (XLF/XLP/XLU);
            # falls back to global model automatically via predict_entry_prob_sector.
            _entry_prob = _pred_entry_sector(tech, vix, _sector_etf_ml)
            # A17 challenger: raw_score is already in _sig_dict_ml; model is None
            # until train_challenger_model() clears the AUC delta bar.
            _challenger_prob = _pred_challenger(_sig_dict_ml, _get_challenger_model())
            # Meta-label: P(primary model is correct | context). Uses entry_prob as
            # key input — teaches when the primary signal is reliable.
            _meta_prob = _pred_meta(
                tech,
                _entry_prob,
                (market_ctx or {}).get("hmm_regime"),
                vix,
                _sector_etf_ml,
                days_to_earnings,
                vix_term_ratio=macro.get("vix_term_ratio"),
                sector_momentum=(sector_rs or {}).get("sector_5d_ret"),
                vix_9d_ratio=macro.get("vix_9d_ratio"),
                # §89: FF ST_Rev — fetched daily in backtest; live cache TBD
                ff_str=None,
            )

            if _live_prob is not None or _entry_prob is not None or _challenger_prob is not None:
                confidence = _ml_blend(confidence, _entry_prob, _live_prob, _challenger_prob, _meta_prob)
                if _challenger_prob is not None:
                    _shadow_scores = {
                        "model_id": "A17_challenger",
                        "score": float(_challenger_prob),
                        "confidence": float(confidence),
                        "champion_score": float(_live_prob or 0.0),
                        "champion_confidence": float(confidence),
                    }
        except Exception as _ml_err:
            log.debug("[engine] %s ML blend failed (model may need retraining): %s", ticker, _ml_err)

    # Hard final ceiling — ensures no post-processing step (adaptive weights,
    # yield dampener, factor mining boost) can push confidence above 72%.
    # Empirical calibration (May 2026, n=529): bands 75-84% win at only 48-50%,
    # and 65-70% wins at only 56% — the model's real ceiling of predictive power.
    # _conf_macro_cap re-enforces any active macro contradiction / news-sentiment
    # cap, preventing adaptive win-rate or yield boosts from bypassing it.
    if action in ("BUY", "SELL"):
        confidence = round(min(_conf_macro_cap, max(35.0, confidence)), 1)

    # Final de-confliction safety (string-based warning heads can be brittle):
    # if we detect a known overbought/oversold warning head, apply a small
    # confidence haircut to reduce false-high conviction.
    if action == "BUY":
        overbought_heads = {
            "RSI Overbought",
            "RSI Elevated",
            "Stochastic Overbought",
            "Stochastic Bearish Cross (Overbought)",
            "Williams %R Overbought",
            "CCI Extreme Overbought",
            "MFI Overbought",
            "Broad Market Complacency",
            "Extreme Greed",
            "NAAIM: Managers Fully Invested",
        }
        if any(r.get("head") in overbought_heads for r in rationale):
            confidence = round(max(35.0, confidence * 0.92), 1)
    elif action == "SELL":
        oversold_heads = {
            "RSI Oversold",
            "RSI Weakening",
            "Stochastic Oversold",
            "Stochastic Bullish Cross (Oversold)",
            "Williams %R Oversold",
            "CCI Extreme Oversold",
            "MFI Oversold",
            "Extreme Fear",
            "Market Breadth Deteriorating",
            "NAAIM: Managers Extremely Defensive",
        }
        if any(r.get("head") in oversold_heads for r in rationale):
            confidence = round(max(35.0, confidence * 0.92), 1)

    # Calibration warning: fires when signal confidence significantly exceeds the
    # historically observed win rate for this action type, or when strong conflicting
    # signals were penalised away but confidence still appears high to the user.
    confidence_warning = False
    if action in ("BUY", "SELL") and confidence >= 75:
        win_rate_hist = (adaptive or {}).get(f"{action}_win_rate")
        if win_rate_hist is not None and confidence - win_rate_hist * 100 > 20 or total_confidence_penalty >= 0.15:
            confidence_warning = True

    # ── MR exit guidance (§35b: RSI45 adaptive exit — 47% hit rate, 100% WR) ──
    # Tells position holders when the mean-reversion bounce is likely complete.
    # Only added for BUY signals with a confirmed MR setup — not for momentum or
    # general BUYs — because the RSI45 threshold was calibrated on MR entries.
    if action == "BUY" and _has_mr:
        _hold_rec = _SECTOR_MR_CONFIG.get(
            (sector_rs or {}).get("sector_etf") or SECTOR_MAP.get(ticker.upper(), ""), {}
        ).get("hold_days", 10)
        rationale = list(rationale) + [
            {
                "src": "Risk Gate",
                "head": "MR Exit Signal: RSI > 45 While Profitable",
                "body": (
                    f"Mean-reversion bounces typically complete when RSI(14) crosses "
                    f"above 45 while the position is profitable (>0.5% gain). "
                    f"20-year backtest: this exit fires on 47% of MR trades at "
                    f"100% win rate, avg +3.0% return. "
                    f"If RSI stays below 45, hold up to {_hold_rec} days while the "
                    f"thesis is intact (price above entry, no stop breach)."
                ),
                "sentiment": "pos",
                "meta": "exit_guidance=rsi45 source=§35b",
            }
        ]

    # ── L8 quality_score — IS-validated MR trade quality composite ───────────
    # Formula: 40%×(score−50)/30 + 35%×OU_speed + 25%×Hurst_MR  → [0, 100]
    # Thresholds recalibrated to IS p67/p33: High(≥43) Sh=0.51 | Mid(35–43) Sh=0.31 | Low(<35) Sh=0.17
    # All three inputs are already in tech dict — zero extra API cost.
    _ou_hl_qs = float(tech.get("ou_halflife") or 12.5)
    _hurst_qs = float(tech.get("hurst") or 0.65)
    _quality_score = min(
        100.0,
        max(
            0.0,
            min(40.0, (score - 50.0) / 30.0 * 40.0)
            + 35.0 * max(0.0, 1.0 - _ou_hl_qs / 25.0)
            + 25.0 * max(0.0, 1.0 - (_hurst_qs - 0.5) / 0.30),
        ),
    )

    # ── L9 HMM regime vars — sourced from macro_regime.py (1h cache) ─────────
    _hmm_ctx = (market_ctx or {}).get("hmm_regime", {})
    _hmm_regime_label = _hmm_ctx.get("regime", "")
    _hmm_bear_prob = float(_hmm_ctx.get("bear_prob", 0.5))
    _hmm_bull_prob = float(_hmm_ctx.get("bull_prob", 0.5))
    _hmm_trans_risk = float(_hmm_ctx.get("transition_risk", 0.1))

    # ── Calibration as the LAST confidence-mutating step ────────────────────
    # QUANT_ENGINE_REVIEW §1.4 / §5 Snippet 8: calibration was previously applied
    # *before* ML blend, overbought haircuts, and peer haircut — but trained on
    # the *final stored* confidence.  This created an iterative feedback loop.
    # Now calibration sees the fully-mutated confidence and is applied just
    # before delivery, with the hard ceiling enforced afterwards.
    if action in ("BUY", "SELL"):
        from services.calibration import apply_calibration

        cal_map = (market_ctx or {}).get("calibration_map", {})
        if cal_map:
            pre_cal = confidence
            _sp500_trend = macro.get("sp500_trend") if macro else None
            _cal_regime = "bull" if _sp500_trend == "up" else "bear" if _sp500_trend == "down" else "neutral"
            confidence, _bin = apply_calibration(confidence, action, cal_map, regime=_cal_regime)
            if _bin and abs(confidence - pre_cal) >= 2:
                _source = _bin.get("source", "platt")
                _emp_wr = round((_bin.get("win_rate") or _bin.get("prob", pre_cal / 100)) * 100, 1)
                _n = _bin.get("n", 0)
                _blend = round((_bin.get("blend", 0)) * 100)
                _gap = round(_emp_wr - pre_cal, 1)
                _bin_lo = (int(pre_cal) // 5) * 5
                _bin_hi = _bin_lo + 5
                _dir = "DOWN" if confidence < pre_cal else "UP"
                _over = confidence < pre_cal
                _is_iso = "isotonic" in _source

                if _is_iso:
                    _body = (
                        f"Isotonic regression ({_source}) mapped {pre_cal:.0f}% → {confidence:.0f}%. "
                        f"Empirical win rate at this confidence level: {_emp_wr:.0f}%. "
                        f"The model is {'over' if _over else 'under'}confident by {abs(_gap):.0f}pp "
                        f"in this confidence region based on resolved signal history."
                    )
                    _meta = f"source={_source} | EmpWR: {_emp_wr:.0f}%"
                else:
                    _body = (
                        f"The model assigned {pre_cal:.0f}% confidence, but {_n} resolved "
                        f"{action} signals in the {_bin_lo}–{_bin_hi}% band have an actual "
                        f"win rate of {_emp_wr:.0f}% — a {abs(_gap):.0f}pp "
                        f"{'overconfidence' if _over else 'underconfidence'} gap. "
                        f"Confidence blended {_blend}% toward the empirical rate."
                    )
                    _meta = (
                        f"Bin {_bin_lo}–{_bin_hi}% | "
                        f"Empirical WR: {_emp_wr:.0f}% | "
                        f"n={_n} signals | "
                        f"Blend: {_blend}% empirical + {100 - _blend}% model"
                    )

                rationale.append(
                    {
                        "src": "Backtest",
                        "head": (
                            f"Calibration {_dir}: {pre_cal:.0f}% → {confidence:.0f}%"
                            f" ({'overconfident' if _over else 'underconfident'} by {abs(_gap):.0f}pp)"
                        ),
                        "body": _body,
                        "sentiment": "pos" if not _over else "neg",
                        "meta": _meta,
                    }
                )
            # Re-apply hard ceiling after calibration so no post-calibration value
            # escapes the empirical cap.
            confidence = round(min(_conf_macro_cap, max(35.0, confidence)), 1)

    return {
        "ticker": ticker,
        "company": info.get("company", ticker),
        "action": action,
        "raw_score": score,
        "raw_confidence": raw_confidence,
        "confidence": confidence,
        "confidence_warning": confidence_warning,
        "price": price,
        "change": tech.get("change", 0),
        "changePct": tech.get("change_pct", 0),
        "entry": entry,
        "stop": stop,
        "target": target,
        "rr": rr,
        "headline": headline,
        "sentiment": round(avg_sent, 2),
        "style": style,
        "sources": sorted(sources),
        "rationale": rationale,
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session": _current_session(),
        "daysToEarnings": days_to_earnings,
        "daysToExDiv": days_to_exdiv,
        "nextEarningsDate": earnings_cal.get("next_earnings_date"),
        # sector_etf is a static SECTOR_MAP lookup — always populate it even when
        # the relative-strength fetch failed (sector_rs is None). Decoupling these
        # keeps the audit tag and the BLOCKED_SECTORS delivery gate working; only
        # the RS *metrics* below go null when live data is unavailable.
        "sectorEtf": (sector_rs["sector_etf"] if sector_rs else SECTOR_MAP.get(ticker.upper())),
        "rsVsSector": sector_rs["rs_vs_sector"] if sector_rs else None,
        "plain_english": plain_english,
        "beta": info.get("beta"),
        "dataWarnings": data_warnings,
        "positionSizeScale": round(
            # §QuantEngine sizing stack (nine layers):
            # L1 portfolio_size_scale — sector concentration + PCA cross-sector (§43/§83)
            # L2 VIX-regime overlay   — fear 1.15×/panic 1.10×/calm 0.75× (§56)
            # L3 vol-targeting        — 0.25/ticker_vol_ann clamped [0.5,2.0]
            # L4 conviction sizing    — (conf-40)/14+0.5 clamped [0.5,1.5]
            #    conf=40→0.5×  conf=47→1.0×  conf=54+→1.5× (anchored to min_confidence=40)
            # L5 gate-quality boost   — Inv3: Hurst+20.6pp, Piotroski+13.1pp, IVR+10.1pp
            #    fires only for BUY; caps at 1.5× total; rewards best-predictor gates
            # L6 regime dampener      — calm bull (VIX<18 + bull trend) reduces MR sizing 0.8×
            #    AI-momentum regimes produce shallow bounces; Inv2+temporal: current regime weak
            # L7 raw-score Kelly      — §18/§12a: non-linear score-band sizing (backtest-validated).
            #    <50→0.50×  50-55→0.75×  55-60→1.00×  60-65→1.15×  65-70→1.30×  70-75→1.45×  ≥75→1.55×
            # L8 quality_score tier   — IS Sh spread High(≥43) 0.51 vs Low(<35) 0.17, v10.1 2026-06-01
            #    high(≥43)→1.30× mid(35–43)→1.0× low(<35)→0.75×; zero N impact (all trades pass)
            # L9 HMM regime sizing    — macro_regime.py 2-state Baum-Welch leads VIX by 1-3d
            #    IS ablation: bull 1.10× never fires on MR entries (low-VIX = no MR triggers)
            #    bear(≥80%)→0.70× transition/trans_risk>20%→0.85× bull→1.0× (no amplification)
            #    MaxDD confirmed: 0.86→0.73 from transition dampener (ablation 2026-06-01)
            portfolio_size_scale
            * (
                1.15
                if (vix is not None and 20 <= vix <= 30 and confidence >= 58)
                else 1.10
                if (vix is not None and vix > 30 and confidence >= 55)
                else 0.75
                if (vix is not None and vix < 15)
                else 1.0
            )
            * (
                max(0.5, min(2.0, 0.25 / max(_atr_pct_pre * _np.sqrt(252), 0.05)))
                * max(0.5, min(1.5, (confidence - 40.0) / 14.0 + 0.5))
                * min(
                    1.5,
                    # L5: gate-quality — multiply for each high-predictor gate that fired
                    (
                        1.20
                        if any("Hurst" in c.get("head", "") and c.get("sentiment") == "pos" for c in rationale)
                        else 1.0
                    )
                    * (
                        1.15
                        if any("Piotroski" in c.get("head", "") and c.get("sentiment") == "pos" for c in rationale)
                        else 1.0
                    )
                    * (
                        1.10
                        if any(
                            ("IVR" in c.get("head", "") or "IV Rank" in c.get("head", ""))
                            and c.get("sentiment") == "pos"
                            for c in rationale
                        )
                        else 1.0
                    ),
                )
                * (
                    # L6: calm-bull regime dampener (AI-rally / low-VIX momentum)
                    0.80
                    if (
                        vix is not None
                        and vix < 18
                        and (macro or {}).get("sp500_trend") == "up"
                        and (macro or {}).get("macro_score", 0) > 3
                    )
                    else 1.0
                )
                * (  # L7 raw-score Kelly — §18/§12a: non-linear score-band sizing (backtest-validated)
                    1.55
                    if score >= 75
                    else 1.45
                    if score >= 70
                    else 1.30
                    if score >= 65
                    else 1.15
                    if score >= 60
                    else 1.00
                    if score >= 55
                    else 0.75
                    if score >= 50
                    else 0.50
                )
                # L8: quality_score tier — thresholds recalibrated 2026-06-01 to IS p67/p33.
                # IS distribution: High(≥43) N=63 Sh=0.51 | Mid(35–43) N=63 Sh=0.31 | Low(<35) N=62 Sh=0.17
                # Old thresholds (60/30) put 80% in Mid (neutral) → no lift. Corrected to (43/35).
                * (1.30 if _quality_score >= 43 else 0.75 if _quality_score < 35 else 1.0)
                # L9: HMM regime sizing — transition dampener only (2026-06-01 fix)
                # Bear dampener REMOVED: IS ablation shows bear WR=72% > baseline 70.7%.
                # HMM "bear" fires on highest-VIX periods — exactly when MR bounces are strongest
                # (deepest fear = deepest overselling = most reliable 10d recovery). Sizing DOWN
                # in these periods cut our best trades. Fix: bear → 1.0× (neutral).
                # Transition dampener KEPT: MaxDD 0.86% → 0.73% confirmed (regime uncertainty
                # = incomplete information = appropriate size reduction).
                * (0.85 if (_hmm_regime_label == "transition" or _hmm_trans_risk > 0.20) else 1.0)
                if action == "BUY"
                else 1.0
            ),
            2,
        ),
        "recommendedHoldDays": (
            _SECTOR_MR_CONFIG.get((sector_rs or {}).get("sector_etf") or SECTOR_MAP.get(ticker.upper(), ""), {}).get(
                "hold_days", 10
            )
            if _has_mr
            else 10
        ),
        "vix": vix,
        "crossAssetHeadwinds": macro.get("cross_asset_headwinds"),
        "nfci": macro.get("nfci"),
        "baa10y": macro.get("baa10y"),
        "t10y3m": macro.get("t10y3m"),
        # §82: trailing stop as % of entry — 2× ATR provides dynamic stop that adapts
        # to realized vol and avoids being stopped out by normal intraday noise.
        "trailingStopPct": round(atr / price * 200, 2) if (price and atr and price > 0) else None,
        # L8: quality_score tier for live tracking and hard-gate research
        "qualityScore": round(_quality_score, 1),
        # L9: HMM regime label for frontend display and future hard-gate research
        "hmmRegime": _hmm_regime_label or None,
        # ATR%rank — delivery_gates uses this for ATR≤70 quality gate (trend-dominant regime check)
        "atrPctRank": round(float(tech.get("atr_pct_rank") or 50), 1),
        # MR setup flag — delivery_gates enforces this as a hard BUY gate.
        # True = at least TWO of: RSI<42, BB%B<0.22, IBS<0.15, VWAP%<-0.75%.
        # Changed from 1→2 on 2026-06-09: backtest showed MR-count=2 improves
        # Sharpe 0.20→0.21 with only -1 trade (154 vs 155). Single-condition
        # MR setups (especially IBS-only) are the weakest class.
        # Without this flag the live engine issues BUYs on uptrending stocks
        # (Golden Cross, Above 200-DMA, EPS beats) that have never been validated
        # in the 23-year backtest, producing live WR ≈42% vs backtest WR ≈68%.
        "hasMr": _has_mr,
        # ALPHA-5: VIX regime tag — informational; used by per-regime WR audit (gate_contribution_analysis.py --sector-wr)
        # after N≥100 resolved signals per regime. Not a delivery gate yet.
        "vixRegime": (
            "stress"
            if (vix is not None and vix >= 30)
            else "elevated"
            if (vix is not None and vix >= 20)
            else "calm"
            if vix is not None
            else "unknown"
        ),
        "gate_traces": _sig_ctx.gate_traces,
        "shadow_scores": _shadow_scores,
        "features": {
            **tech,
            "vix": vix,
            "sp500_trend": sp500_trend,
            "quality_score": _quality_score,
            "hasMr": _has_mr,
            "vix_term_ratio": macro.get("vix_term_ratio"),
            "vix_9d_ratio": macro.get("vix_9d_ratio"),
            "sector_momentum": (sector_rs or {}).get("sector_5d_ret"),
        },
    }
