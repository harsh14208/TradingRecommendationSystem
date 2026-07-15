"""
Technical and regime-based gates extracted from _assemble_signal().

Pre-options pipeline (run before OptionsFlowConfirmationGate):
  StlfsiVixGate           — §STLFSI financial-stress + VIX hard block
  GlobalVixMinGate        — §12b global VIX ≥ 20 MR minimum
  Sma200BuyGate           — SMA200 downtrend BUY suppression
  SellUptrendGate         — SELL above SMA200 without alt-data confirmation
  SpyNeutralZoneGate      — SPY ±2% of SMA200 transition zone
  BearHighVixGate         — S&P down + VIX > 25 + score < 50
  MrPersistenceGate       — AR(1) momentum-persistence haircut (Hurst proxy)
  MrEntryConditionGate    — require BB%B / IBS / VWAP% oversold condition
  IbsSma20ConfluenceGate  — IBS sole trigger must be sustained ≥5 days
  AtrRankFloorGate        — §12e dormant-vol floor (ATR rank < 20th pct)
  SectorVixFloorGate      — §15c per-sector VIX minimum for MR entries
  AtrRankCeilingGate      — §17a trending-panic ceiling (ATR rank > 70th pct)
  ReturnJumpGate          — §17b single-day drop > −6% fundamental repricing
  VixDirectionGate        — §17c rising VIX (3d slope > 3) blocks MR entry
  Max21Gate               — §MAX low-MAX filter (trailing 21d max return > median)

Post-options pipeline (run after OptionsFlowConfirmationGate):
  SectorScoreFloorGate    — §15d per-sector minimum score for MR BUY
  NearEarningsCautionGate — §34 8-14d pre-earnings confidence haircut
  DeepBearRsiGate         — crisis regime (VIX > 28 + SPY < −5%) RSI gate
  SustainedBearGate       — slow-burn bear −5pp confidence haircut
  PriceSma20DistanceGate  — price must be ≥ 2% below SMA20 for BUY

All gates guard on ctx.action == "BUY" (or "SELL" where noted) and skip
naturally when a prior gate set action = "HOLD".

ctx.sector_config must be populated by the caller:
    ctx.sector_config = _SECTOR_MR_CONFIG.get(ctx.sector_etf, {})
"""

from __future__ import annotations

from .base import GateBase, SignalContext


# ── Pre-options pipeline ───────────────────────────────────────────────────────


class StlfsiVixGate(GateBase):
    """
    Financial-stress + VIX regime hard-gate.

    STLFSI4 > 1.5 and VIX > 30: hard HOLD — individual-stock signals
    become unreliable when equity correlations spike to 1.0 in a crisis.
    STLFSI4 > 1.0 and VIX > 25 and score < 50: elevated-stress soft gate.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        stlfsi = ctx.macro.get("stlfsi")
        if stlfsi is None or ctx.vix is None:
            return
        if stlfsi > 1.5 and ctx.vix > 30:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Stress Regime Gate — BUY Blocked (STLFSI4 {stlfsi:+.2f}, VIX {ctx.vix:.0f})",
                    "body": (
                        f"St. Louis Financial Stress Index at {stlfsi:+.2f} (crisis >1.5) with "
                        f"VIX at {ctx.vix:.0f} — systemic stress regime active. In high-stress environments "
                        "equity correlations spike toward 1.0, individual-stock signals have near-zero "
                        "predictive power, and BUY signals fail at high rates. All BUY signals gated "
                        "to HOLD until STLFSI4 drops below 1.0."
                    ),
                    "sentiment": "neg",
                    "meta": f"STLFSI4={stlfsi:+.2f} | VIX={ctx.vix:.0f} | hard_gate=stress_regime",
                }
            )
        elif stlfsi > 1.0 and ctx.vix > 25 and ctx.score < 50:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Elevated Stress Gate — Marginal BUY Blocked (Score {ctx.score:.0f} < 50, STLFSI4 {stlfsi:+.2f})",
                    "body": (
                        f"STLFSI4 at {stlfsi:+.2f} (elevated, threshold 1.0) with VIX at {ctx.vix:.0f}. "
                        "Marginal BUY signals fail at elevated rates in stress regimes. "
                        "Requiring score ≥50 for BUY until financial stress normalises."
                    ),
                    "sentiment": "neg",
                    "meta": f"STLFSI4={stlfsi:+.2f} | VIX={ctx.vix:.0f} | score={ctx.score:.1f} < 50",
                }
            )


class GlobalVixMinGate(GateBase):
    """
    §12b global VIX ≥ 20 MR entry minimum.

    23yr 103-ticker backtest: VIX ≥ 20 → Sharpe 0.23 vs 0.13 baseline,
    WR 64.1%, MaxDD −0.87%.  Only fires for MR-condition entries.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or not ctx.has_mr:
            return
        if ctx.vix is not None and ctx.vix < 20:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Global VIX Minimum Gate — Low Fear Regime (VIX {ctx.vix:.0f} < 20)",
                    "body": (
                        f"VIX at {ctx.vix:.0f} is below the MR entry floor. "
                        "Mean-reversion bounces require a fear premium to close the gap — "
                        "low-VIX entries have insufficient panic depth for reliable reversal. "
                        f"103-ticker 23yr backtest (§12b): VIX≥20 → Sharpe 0.23 vs 0.13 baseline, "
                        "WR 64.1%, MaxDD -0.87%. Waiting for VIX ≥ 20."
                    ),
                    "sentiment": "neg",
                    "meta": f"vix={ctx.vix:.0f} < 20 | mr_entry=True | global_vix_min_gate=True",
                }
            )


class Sma200BuyGate(GateBase):
    """
    SMA200 downtrend BUY gate.

    Price < 99% of SMA200 and RSI ≥ 25 and score < 60 → HOLD.
    Waiver: RSI < 25 (extreme oversold) or score ≥ 60 (strong alt-data).
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        sma200 = ctx.tech.get("sma200")
        rsi = float(ctx.tech.get("rsi") or 50)
        if sma200 is None or ctx.price is None:
            return
        if ctx.price < sma200 * 0.99 and rsi >= 25 and ctx.score < 60:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "SMA200 Downtrend Gate — BUY Suppressed",
                    "body": (
                        f"Price ${ctx.price:.2f} is {(ctx.price / sma200 - 1) * 100:.1f}% below the 200-day MA "
                        f"(${sma200:.2f}). 20-year backtest: BUY signals in long-term downtrends "
                        "are net-negative. Gate waived only when RSI < 25 (extreme oversold) "
                        "or score ≥ 60 (strong alt-data confirmation)."
                    ),
                    "sentiment": "neg",
                    "meta": f"price={ctx.price:.2f} sma200={sma200:.2f} rsi={rsi:.1f} | gate=sma200_downtrend",
                }
            )


class SellUptrendGate(GateBase):
    """
    SELL above SMA200 without alt-data confirmation.

    Technical-only SELL signals above SMA200 average −0.71%/trade.
    Require at least one non-technical source to short into an uptrend.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "SELL":
            return
        sma200 = ctx.tech.get("sma200")
        if sma200 is None or ctx.price is None:
            return
        has_alt = bool({"Options", "News", "Macro", "13F", "SEC EDGAR", "Dark Pool", "Short Interest"} & ctx.sources)
        if ctx.price > sma200 * 1.01 and not has_alt and ctx.score > -45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "SELL Alt-Data Gate — Uptrend Confirmation Required",
                    "body": (
                        f"Price ${ctx.price:.2f} is above 200-day MA (${sma200:.2f}) — confirmed uptrend. "
                        "30-year backtest: technical-only SELL signals in uptrends average -0.71%/trade "
                        "across all market cycles. Requires options flow, news catalyst, macro signal, "
                        "or institutional data to short into an uptrend."
                    ),
                    "sentiment": "neg",
                    "meta": f"price={ctx.price:.2f} sma200={sma200:.2f} | gate=sell_uptrend_no_altdata",
                }
            )


class SpyNeutralZoneGate(GateBase):
    """
    SPY ±2% of SMA200 neutral zone gate.

    Regime transitions create whipsaw signals. Require score ≥ 45 at this
    critical inflection point.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        spy_neutral = ctx.macro.get("sp500_neutral_zone", False)
        if not spy_neutral or ctx.score >= 45:
            return
        ctx.action = "HOLD"
        ctx.sources.add("Risk Gate")
        sma200_ratio = ctx.macro.get("sp500_sma200_ratio", 1.0)
        ctx.rationale.append(
            {
                "src": "Risk Gate",
                "head": f"SPY Neutral Zone Gate — {(sma200_ratio - 1) * 100:+.1f}% vs SMA200 (Score {ctx.score:.0f} < 45)",
                "body": (
                    f"SPY is {(sma200_ratio - 1) * 100:+.1f}% vs its 200-day MA (±2% transition zone). "
                    "Regime transitions create whipsaw signals — marginal BUY entries fail at "
                    "high rates. Requiring score ≥ 45 for conviction before acting at this "
                    "critical inflection point."
                ),
                "sentiment": "neg",
                "meta": f"SPY/SMA200 ratio={sma200_ratio:.4f} | neutral_zone=True | score={ctx.score:.1f}",
            }
        )


class BearHighVixGate(GateBase):
    """
    Bear + high-VIX hard BUY gate.

    S&P 500 in downtrend, VIX > 25, score < 50 → HOLD.
    20yr backtest: bear-market BUY signals average −1.7%/trade.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        if ctx.sp500_trend == "down" and ctx.vix is not None and ctx.vix > 25 and ctx.score < 50:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Bear+VIX Gate — BUY Blocked (Score {ctx.score:.0f} < 50, VIX {ctx.vix:.0f})",
                    "body": (
                        f"S&P 500 is in a downtrend (below 50-DMA) and VIX is {ctx.vix:.0f}. "
                        "20-year backtest: BUY signals in this regime average -1.7%/trade. "
                        "Requiring score ≥50 — only high-conviction alt-data-confirmed entries."
                    ),
                    "sentiment": "neg",
                    "meta": f"SPX trend: down | VIX: {ctx.vix:.0f} | Score: {ctx.score:.1f}",
                }
            )


class MrPersistenceGate(GateBase):
    """
    AR(1) momentum-persistence MR suitability gate (Hurst proxy).

    AR(1) > 0.05 on 126-day daily returns = positive return autocorrelation =
    trending/momentum regime.  Applies a confidence haircut scaled by AR(1)
    magnitude; halved when revenue is not declining (healthy dip vs value trap).
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or not ctx.has_mr:
            return
        ar1 = ctx.tech.get("momentum_ar1")
        if ar1 is None or float(ar1) <= 0.05:
            return
        ar1_val = float(ar1)
        ar1_full = round(min(10.0, (ar1_val - 0.05) * 200), 1)
        rev = ctx.info.get("revenue_growth")
        growing = rev is not None and float(rev) > -0.10
        ar1_pen = round(ar1_full * 0.5, 1) if growing else ar1_full
        if ar1_pen <= 0:
            return
        ctx.confidence = round(max(35.0, ctx.confidence - ar1_pen), 1)
        ctx.sources.add("Risk Gate")
        rev_str = f"{float(rev) * 100:+.1f}%" if rev is not None else "unknown"
        regime = "Dip in Momentum Stock" if growing else "Value Trap Risk"
        ctx.rationale.append(
            {
                "src": "Risk Gate",
                "head": f"MR Persistence Gate — AR(1) {ar1_val:.3f} ({regime}, −{ar1_pen:.0f}pp)",
                "body": (
                    f"126-day return AR(1) coefficient: {ar1_val:.3f}. "
                    "Positive autocorrelation means this stock is trend-following, not mean-reverting. "
                    + (
                        f"Revenue growth {rev_str} suggests this is a healthy pullback "
                        f"in a growing business — haircut halved to {ar1_pen:.0f}pp. "
                        if growing
                        else f"Revenue growth {rev_str} combined with momentum persistence "
                        f"raises value-trap risk — oversold for a real reason. Full {ar1_pen:.0f}pp haircut. "
                    )
                    + "(Dynamic rule; reverts automatically when AR(1) drops below 0.05.)"
                ),
                "sentiment": "neg",
                "meta": (
                    f"ar1_126d={ar1_val:.3f} > 0.05 | rev_growth={rev_str} "
                    f"| haircut={ar1_pen:.1f}pp | regime={'dip' if growing else 'value_trap'}"
                ),
            }
        )


class MrEntryConditionGate(GateBase):
    """
    MR entry condition gate.

    Require at least ONE genuine oversold condition (BB%B < 0.22, IBS < 0.15,
    or VWAP% < −0.75) for BUY signals with score < 65.
    20yr backtest (§v5.12): MR-condition entries +1.07% avg vs −0.74% without.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or ctx.has_mr or ctx.score >= 65:
            return
        bb = ctx.tech.get("bb_pct_b")
        ibs = ctx.tech.get("ibs")
        vwap = ctx.tech.get("vwap_pct")
        bb_s = f"{float(bb):.2f}" if bb is not None else "—"
        ibs_s = f"{float(ibs):.2f}" if ibs is not None else "—"
        vwap_s = f"{float(vwap):.1f}" if vwap is not None else "—"
        ctx.action = "HOLD"
        ctx.sources.add("Risk Gate")
        ctx.rationale.append(
            {
                "src": "Risk Gate",
                "head": "MR Entry Condition Gate — No Oversold/Undervalued Setup",
                "body": (
                    f"BUY score {ctx.score:.0f} fired without a mean-reversion entry condition. "
                    f"20yr backtest: entries without BB%%B<0.22, IBS<0.15, or VWAP%%<−0.75 "
                    f"deliver −0.74%% avg vs +1.07%% for MR-condition entries (Sharpe 0.04 vs 0.27). "
                    f"Current: BB%%B {bb_s} | IBS {ibs_s} | VWAP%% {vwap_s}. "
                    "Require at least one MR condition. Exception: score≥65 (strong alt-data)."
                ),
                "sentiment": "neg",
                "meta": (
                    f"RSI={float(ctx.tech.get('rsi') or 50):.1f} BB%B={bb_s} IBS={ibs_s} VWAP%={vwap_s} "
                    f"score={ctx.score:.1f} | no_mr_condition=True"
                ),
            }
        )


class IbsSma20ConfluenceGate(GateBase):
    """
    IBS sole trigger + SMA20 streak confluence gate (§17e, Pagonidis 2013).

    When IBS < 0.15 is the ONLY MR trigger (BB%B and VWAP% not oversold),
    require ≥ 5 consecutive days below SMA20 to confirm sustained selling.
    A single bad close near the low without multi-day selling is weaker.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or not ctx.has_mr:
            return
        ibs = ctx.tech.get("ibs")
        bb = ctx.tech.get("bb_pct_b")
        vwap = ctx.tech.get("vwap_pct")
        ibs_sole = (
            ibs is not None
            and float(ibs) < 0.15
            and (bb is None or float(bb) >= 0.22)
            and (vwap is None or float(vwap) >= -0.75)
        )
        if not ibs_sole:
            return
        streak = ctx.tech.get("close_streak")
        if streak is None or float(streak) <= -5:
            return  # streak ≤ -5 means ≥5 days below SMA20 — waived
        ctx.action = "HOLD"
        ctx.sources.add("Risk Gate")
        ctx.rationale.append(
            {
                "src": "Risk Gate",
                "head": (
                    f"IBS Sole Trigger — SMA20 Streak Insufficient ({abs(float(streak)):.0f} days below, need ≥5)"
                ),
                "body": (
                    f"IBS<0.15 is the only MR trigger (BB%B not oversold, VWAP not negative). "
                    f"The stock has been below SMA20 for only {abs(float(streak)):.0f} consecutive day(s). "
                    "Pagonidis (2013): IBS-triggered entries require ≥5 consecutive days below SMA20 to confirm "
                    "sustained selling pressure. A single bad day closing near the low may be a one-off event, "
                    "not a genuine capitulation. The bounce edge is significantly weaker without this confluence."
                ),
                "sentiment": "neg",
                "meta": (
                    f"ibs={float(ibs):.2f} close_streak={float(streak):.0f} "
                    f"rsi={float(ctx.tech.get('rsi') or 50):.0f} | ibs_sole=True | sma20_streak_gate=True"
                ),
            }
        )


class AtrRankFloorGate(GateBase):
    """
    §12e dormant-volatility ATR rank floor gate.

    ATR rank < 20th pct (or sector-specific floor) → structurally weak bounces.
    Uses ctx.sector_config for sector-specific floor (e.g. XLF requires ≥ 30).
    Only applies to MR BUY entries.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or not ctx.has_mr:
            return
        atr_rank = ctx.tech.get("atr_pct_rank")
        if atr_rank is None:
            return
        atr_rank_min = ctx.sector_config.get("atr_rank_min", 20)
        if float(atr_rank) < atr_rank_min:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": (
                        f"Dormant Volatility Gate — ATR Rank {float(atr_rank):.0f}th Percentile "
                        f"(Floor: ≥{atr_rank_min})"
                    ),
                    "body": (
                        f"ATR is at the {float(atr_rank):.0f}th percentile of its 1-year range. "
                        f"Alpha decomp §12e (74 tickers) + §15e (sector analysis): MR entries in dormant "
                        f"regimes (ATR rank < {atr_rank_min}th percentile) produce structurally weak "
                        f"bounces. {'Financials sector requires stricter ATR≥30 (§15e). ' if atr_rank_min > 20 else ''}"
                        "Requiring ATR rank ≥ 20 improved annualized Sharpe from 0.92 → 1.00."
                    ),
                    "sentiment": "neg",
                    "meta": (
                        f"atr_pct_rank={float(atr_rank):.0f} < {atr_rank_min} "
                        f"| sector={ctx.sector_etf} | mr_entry=True | dormant_regime=True"
                    ),
                }
            )


class SectorVixFloorGate(GateBase):
    """
    §15c per-sector VIX minimum for MR entries.

    Uses ctx.sector_config["vix_min"] to enforce sector-specific VIX floors.
    Low-VIX entries in certain sectors lack the fear premium that powers MR bounces.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or not ctx.has_mr:
            return
        vix_min = ctx.sector_config.get("vix_min")
        if vix_min is None or ctx.vix is None:
            return
        if ctx.vix < vix_min:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": (
                        f"Sector VIX Floor — {ctx.sector_etf} MR Entry Requires VIX ≥ {vix_min:.0f} "
                        f"(Current VIX: {ctx.vix:.0f})"
                    ),
                    "body": (
                        f"Alpha decomp §15c (68 tickers, 20-year): {ctx.sector_etf} mean-reversion "
                        f"entries require VIX ≥ {vix_min:.0f} for statistical edge. "
                        "Low-VIX entries in this sector have significantly lower win rates — "
                        "the 'fear premium' that powers MR bounces is absent. "
                        f"Current VIX {ctx.vix:.0f} is below the sector floor."
                    ),
                    "sentiment": "neg",
                    "meta": (
                        f"sector={ctx.sector_etf} vix={ctx.vix:.0f} < vix_min={vix_min:.0f} "
                        "| mr_entry=True | sector_vix_floor=True"
                    ),
                }
            )


class AtrRankCeilingGate(GateBase):
    """
    §17a trending-panic ATR rank ceiling.

    ATR rank > 70th pct in high-VIX regime → forced selling still accelerating.
    Skipped in low-VIX calm markets (VIX < 18) where trending-panic risk is absent.
    """

    _VIX_REGIME_PIVOT = 18.0

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or not ctx.has_mr:
            return
        if ctx.vix is not None and float(ctx.vix) < self._VIX_REGIME_PIVOT:
            return  # low-VIX regime — skip ceiling
        atr_rank = ctx.tech.get("atr_pct_rank")
        if atr_rank is None or float(atr_rank) <= 70:
            return
        ctx.action = "HOLD"
        ctx.sources.add("Risk Gate")
        ctx.rationale.append(
            {
                "src": "Risk Gate",
                "head": f"Trending-Panic Gate — ATR Rank {float(atr_rank):.0f}th Percentile (Ceiling: ≤70)",
                "body": (
                    f"ATR is at the {float(atr_rank):.0f}th percentile — extreme trending volatility. "
                    "At this regime, forced selling is accelerating, not exhausted. "
                    "MR bounces require panic-level volatility (ATR 20th–70th pct); "
                    "above the 70th pct the stock is in a breakdown, not a dip. "
                    "Quantpedia ATR regime research: P70 is the optimal MR ceiling. "
                    f"(Gate active when VIX ≥ {self._VIX_REGIME_PIVOT:.0f}; "
                    + (f"current VIX {float(ctx.vix):.0f}.)" if ctx.vix is not None else "VIX unavailable.)")
                ),
                "sentiment": "neg",
                "meta": (
                    f"atr_pct_rank={float(atr_rank):.0f} > 70 | mr_entry=True | trending_panic=True | vix_regime=high"
                ),
            }
        )


class ReturnJumpGate(GateBase):
    """
    §17b single-day return jump filter.

    Drop > −6% in a single session = likely fundamental repricing event
    (earnings miss, guidance cut, fraud, regulatory action), not temporary panic.
    Alpha Architect: filtering return jumps tripled cumulative returns.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or not ctx.has_mr:
            return
        chg = ctx.tech.get("change_pct")
        if chg is None or float(chg) >= -6.0:
            return
        ctx.action = "HOLD"
        ctx.sources.add("Risk Gate")
        ctx.rationale.append(
            {
                "src": "Risk Gate",
                "head": f"Return Jump Filter — Single-Day Drop {float(chg):.1f}% Exceeds −6% Threshold",
                "body": (
                    f"Today's {float(chg):.1f}% decline is above the −6% threshold "
                    "for fundamental repricing events (earnings miss, guidance cut, regulatory action). "
                    "Alpha Architect research: filtering single-day return jumps of this magnitude "
                    "tripled cumulative returns by removing stocks undergoing regime changes, "
                    "not temporary panics. Mean-reversion bounces require a recoverable dislocation; "
                    "drops exceeding 6% in a single session often reflect genuine value destruction."
                ),
                "sentiment": "neg",
                "meta": f"change_pct={float(chg):.1f}% < -6.0 | mr_entry=True | return_jump=True",
            }
        )


class VixDirectionGate(GateBase):
    """
    §17c VIX direction gate — rising VIX blocks MR entry.

    VIX 3-day slope > 3.0 with VIX > 16: panic still building, not peaking.
    Academic research (Preprints.org, Feb 2026): extreme VIX leads to strong
    returns only AFTER it peaks and begins to fall.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or not ctx.has_mr:
            return
        vix_slope = ctx.macro.get("vix_3d_slope")
        if vix_slope is None or ctx.vix is None:
            return
        if ctx.vix > 16 and float(vix_slope) > 3.0:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"VIX Still Rising — Panic Building, Not Peaking (3d Slope: +{float(vix_slope):.1f})",
                    "body": (
                        f"VIX has risen {float(vix_slope):.1f} points over the past 3 days "
                        f"(current: {ctx.vix:.1f}). Academic research (VIX mean reversion studies): "
                        "MR bounces are most reliable after VIX peaks and begins declining — "
                        "the capitulation signal. A rising VIX indicates forced selling is still "
                        "accelerating. Waiting for VIX stabilization before MR entry avoids "
                        "catching a falling knife in the early phase of a panic."
                    ),
                    "sentiment": "neg",
                    "meta": (
                        f"vix={ctx.vix:.1f} vix_3d_slope={float(vix_slope):.1f} > 3.0 | mr_entry=True | vix_rising=True"
                    ),
                }
            )


class Max21Gate(GateBase):
    """
    §MAX low-MAX filter — keep BUY signals whose trailing 21-day maximum daily
    close-to-close return is at or below the ticker's own expanding median.

    Chen et al. ("Maxing Out Short-term Reversals") find reversal returns are
    much stronger in high-MAX lottery-like names.  In this vol-gated MR book,
    the opposite holds: high-MAX names add noise and tail risk, while low-MAX
    names deliver steadier mean-reversion.  The gate is causal — the median is
    computed on the ticker's own expanding history up to and including today.
    """

    version = "1.0"

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or not ctx.has_mr:
            return
        max_21 = ctx.tech.get("max_21")
        max_21_median = ctx.tech.get("max_21_median")
        if max_21 is None or max_21_median is None:
            return
        if float(max_21) <= float(max_21_median):
            return
        ctx.action = "HOLD"
        ctx.sources.add("Risk Gate")
        ctx.rationale.append(
            {
                "src": "Risk Gate",
                "head": (
                    f"MAX-21 Filter — Trailing 21-Day Max Return {float(max_21):.2f}% "
                    f"Above Median {float(max_21_median):.2f}%"
                ),
                "body": (
                    f"{ctx.ticker}'s highest daily return over the last 21 sessions was "
                    f"{float(max_21):.2f}%, above its expanding median of "
                    f"{float(max_21_median):.2f}%. High-MAX names behave like lottery "
                    "tickets in this vol-gated universe and add reversal noise / tail "
                    "risk. The causal low-MAX filter keeps only lower-MAX setups."
                ),
                "sentiment": "neg",
                "meta": (f"max21={float(max_21):.2f} median={float(max_21_median):.2f} filter=low_max"),
            }
        )


# ── Post-options pipeline ──────────────────────────────────────────────────────


class SectorScoreFloorGate(GateBase):
    """
    §15d per-sector minimum score for MR BUY entries.

    Uses ctx.sector_config["buy_thresh"]. buy_thresh ≥ 999 = sector
    confirmed negative alpha (XLV, XLI, XLRE) — hard block.
    buy_thresh adjusted −3pp in low-VIX calm regime (§21).
    """

    _VIX_REGIME_PIVOT = 18.0

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or not ctx.has_mr:
            return
        buy_thresh = ctx.sector_config.get("buy_thresh")
        if buy_thresh is None:
            return
        vix_low = ctx.vix is not None and float(ctx.vix) < self._VIX_REGIME_PIVOT
        if vix_low and buy_thresh < 999:
            buy_thresh = max(35, buy_thresh - 3)
        if ctx.score >= buy_thresh:
            return
        ctx.action = "HOLD"
        ctx.sources.add("Risk Gate")
        sector_blocked = buy_thresh >= 999
        if sector_blocked:
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Sector MR Blocked — {ctx.sector_etf} Confirmed Negative Alpha (§16a Research)",
                    "body": (
                        f"§16a alpha decomp (94 tickers, 20-year): {ctx.sector_etf} mean-reversion entries "
                        "show confirmed negative risk-adjusted returns. "
                        + (
                            "Healthcare (XLV): §16a Sharpe −0.17, WR 29.4% — structural resistance to MR bounces. "
                            if ctx.sector_etf == "XLV"
                            else ""
                        )
                        + (
                            "Industrials (XLI): §16a Sharpe −0.48, WR 28.6% — cyclical noise overrides MR signal. "
                            if ctx.sector_etf == "XLI"
                            else ""
                        )
                        + (
                            "Real Estate (XLRE): §16a Sharpe −15 (N=2) — rate-sensitivity invalidates MR setup. "
                            if ctx.sector_etf == "XLRE"
                            else ""
                        )
                        + "This sector is excluded from MR signal delivery pending improved data."
                    ),
                    "sentiment": "neg",
                    "meta": (
                        f"sector={ctx.sector_etf} score={ctx.score:.0f} buy_thresh=999 "
                        "| mr_entry=True | sector_blocked=True | §16a_confirmed_negative=True"
                    ),
                }
            )
        else:
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": (
                        f"Sector Score Floor — {ctx.sector_etf} MR Entry Requires Score ≥ {buy_thresh} "
                        f"(Current: {ctx.score:.0f})"
                    ),
                    "body": (
                        f"Alpha decomp §15d (68 tickers, 20-year): {ctx.sector_etf} mean-reversion "
                        f"entries below score {buy_thresh} have poor risk-adjusted returns. "
                        + (
                            "Tech (XLK) thresh=40 is the quality boundary — lower scores add noise. "
                            if ctx.sector_etf == "XLK"
                            else ""
                        )
                        + (
                            "Financials (XLF) thresh=42 achieves 83.3% WR and Sharpe 0.89 in isolation. "
                            if ctx.sector_etf == "XLF"
                            else ""
                        )
                        + f"Current composite score {ctx.score:.0f} is below the {ctx.sector_etf} sector floor."
                    ),
                    "sentiment": "neg",
                    "meta": (
                        f"sector={ctx.sector_etf} score={ctx.score:.0f} < buy_thresh={buy_thresh} "
                        "| mr_entry=True | sector_score_floor=True"
                    ),
                }
            )


class NearEarningsCautionGate(GateBase):
    """
    §34 near-earnings caution gate — 8-14d pre-earnings haircut.

    §34 live-engine reanalysis (543 signals): near-earnings zone outperforms
    safe zone (62.5% vs 50.5% WR) overall when alt-data is present.
    Without any alt-data: −3pp. With calls but no revision: −2pp.
    Hard block at ≤2d to earnings is handled by delivery_gates separately.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        dte = ctx.days_to_earnings
        if dte is None or not (8 <= dte <= 14):
            return
        has_pos_analyst = any(r.get("src") == "Analyst" and r.get("sentiment") == "pos" for r in ctx.rationale)
        has_unusual_calls = bool(ctx.opt_flow and ctx.opt_flow.get("sweep_calls")) or bool(
            ctx.opt_flow and (ctx.opt_flow.get("unusual_vol_ratio") or 0.0) > 2.0
        )
        if not has_pos_analyst and not has_unusual_calls:
            ctx.confidence = round(max(35.0, ctx.confidence - 3), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Near-Earnings Caution — {dte}d to Earnings, No Alt-Data",
                    "body": (
                        f"Earnings in {dte} days (caution zone: 8-14d). "
                        "Neither analyst revision nor unusual call activity confirms the setup. "
                        "§34 live data: near-earnings zone still outperforms the safe zone (62.5% vs 50.5% WR) "
                        "overall — hard block replaced by −3pp haircut. Proceed with reduced size."
                    ),
                    "sentiment": "neg",
                    "meta": (f"days_to_earnings={dte} | no_pos_revision=True | no_unusual_calls=True | penalty=-3pp"),
                }
            )
        elif not has_pos_analyst:
            ctx.confidence = round(max(35.0, ctx.confidence - 2), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Near-Earnings Caution — {dte}d to Earnings, No Analyst Revision",
                    "body": (
                        f"Earnings in {dte} days (caution zone: 8-14d). "
                        "Unusual call activity detected (partial confirmation) but no positive analyst "
                        "revision. Applying −2pp confidence haircut. Proceed with reduced size."
                    ),
                    "sentiment": "neg",
                    "meta": (
                        f"days_to_earnings={dte} | no_pos_revision=True "
                        f"| has_unusual_calls={has_unusual_calls} | penalty=-2pp"
                    ),
                }
            )


class DeepBearRsiGate(GateBase):
    """
    Deep-bear RSI gate — crisis regime (VIX > 28 + SPY < −5% vs SMA200).

    In systemic downturns, RSI 35-42 "oversold" entries are falling knives.
    Only RSI < 35 (extreme capitulation) has positive edge in this regime.
    Rate-Hike Bear 2022 trades at RSI 35-42 averaged −2.03% across 4 trades.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        if ctx.vix is None or ctx.vix <= 28:
            return
        sma200_ratio = float(ctx.macro.get("sp500_sma200_ratio") or 1.0)
        if sma200_ratio >= 0.95:
            return  # not a deep-bear regime
        rsi = float(ctx.tech.get("rsi") or 50)
        if rsi >= 35:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": (
                        f"Deep-Bear RSI Gate — Crisis Regime "
                        f"(VIX {ctx.vix:.0f}, SPY {(sma200_ratio - 1) * 100:.1f}% vs SMA200)"
                    ),
                    "body": (
                        f"VIX at {ctx.vix:.0f} (>28) and SPY at {(sma200_ratio - 1) * 100:.1f}% vs SMA200 "
                        f"— confirmed crisis/systemic downturn. RSI {rsi:.0f} is oversold but not "
                        "at capitulation levels. In panic regimes, RSI 35-42 entries are falling knives: "
                        "backtest showed only RSI<35 has positive expected value here. "
                        "Waiting for extreme oversold (RSI<35) before entering."
                    ),
                    "sentiment": "neg",
                    "meta": (
                        f"VIX={ctx.vix:.0f}>28 SPY_vs_SMA200={(sma200_ratio - 1) * 100:.1f}%<-5% "
                        f"RSI={rsi:.1f}≥35 | deep_bear_rsi_gate=True"
                    ),
                }
            )


class SustainedBearGate(GateBase):
    """
    §34 sustained-bear macro gate — slow-burn bear confidence haircut.

    Acute crises are handled by DeepBearRsiGate. Slow-burn bears
    (VIX not spiking but SPY grinding down >3% below SMA200 + down >7% over 1M)
    get a −5pp confidence haircut.  §34 live data: bear regimes → 0% WR.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        sma200_ratio = float(ctx.macro.get("sp500_sma200_ratio") or 1.0)
        spy_1m = float(ctx.macro.get("spy_1m_ret") or 0.0)
        deep_bear = ctx.vix is not None and ctx.vix > 28 and sma200_ratio < 0.95
        if deep_bear:
            return  # handled by DeepBearRsiGate
        if sma200_ratio < 0.97 and spy_1m < -7.0:
            haircut = 5.0
            ctx.confidence = round(max(35.0, ctx.confidence - haircut), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": (
                        f"Sustained-Bear Gate — SPY {(sma200_ratio - 1) * 100:.1f}% vs SMA200, {spy_1m:.1f}% 1-Month"
                    ),
                    "body": (
                        f"SPY is {(sma200_ratio - 1) * 100:.1f}% below its 200-day SMA and has "
                        f"returned {spy_1m:.1f}% over the past month — a confirmed sustained downtrend. "
                        "§34 live data: bear regimes (COVID 2020, Rate-Hike Bear 2022) produced 0% WR "
                        f"for MR signals. Applying −{haircut:.0f}pp confidence haircut. "
                        "Only extreme-oversold setups with strong multi-source confirmation should proceed."
                    ),
                    "sentiment": "neg",
                    "meta": (
                        f"sp500_sma200_ratio={sma200_ratio:.4f} spy_1m_ret={spy_1m:.1f}% "
                        f"| sustained_bear=True | haircut=-{haircut:.0f}pp"
                    ),
                }
            )


class PriceSma20DistanceGate(GateBase):
    """
    Price-SMA20 distance gate (§v5.12 validated).

    Require price ≥ 2% below SMA20 for mid-conviction BUY entries (score < 65).
    RSI < 42 alone can trigger after a slow drift to SMA20 — not a genuine
    oversold extension. Backtest improvement: WR +2.1pp, avg +0.14%.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or ctx.score >= 65 or ctx.price is None:
            return
        sma20 = ctx.tech.get("sma20")
        if sma20 is None or float(sma20) <= 0:
            return
        if ctx.price >= float(sma20) * 0.98:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            dist = (ctx.price / float(sma20) - 1) * 100
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Price-SMA20 Distance Gate — Only {abs(dist):.1f}% Below 20-DMA",
                    "body": (
                        f"Price ${ctx.price:.2f} is only {abs(dist):.1f}% below the 20-day SMA "
                        f"(${float(sma20):.2f}). Require ≥2% below SMA20 to confirm a genuine "
                        "short-term oversold extension. A slow drift to SMA20 lacks the capitulation "
                        "pressure needed for a reliable mean-reversion bounce. "
                        "Gate waived at score≥65 (strong independent confirmation)."
                    ),
                    "sentiment": "neg",
                    "meta": f"price={ctx.price:.2f} sma20={float(sma20):.2f} dist={dist:+.2f}% score={ctx.score:.1f}",
                }
            )
