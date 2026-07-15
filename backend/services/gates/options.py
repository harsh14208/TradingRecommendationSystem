"""
Options-flow gate pack extracted from _assemble_signal().

Gates (applied in pipeline order):
  OptionsFlowConfirmationGate  — PC ratio hard-block; call sweep + GEX bonus/penalty
  IvRankFlagGate               — informational elevated-IV disclosure (no score change)
  PutSweepCapitulationGate     — extreme put sweep capitulation confirmation (+5pp)
  (IvrMrGate §48 / PutCallSkewGate §49 / IvTermStructureGate removed 2026-07-14 — 0 fires ever)

All gates guard on ctx.action == "BUY" and ctx.has_mr where applicable;
a prior gate setting action = "HOLD" causes them to skip naturally.

Unit test pattern:
    from services.gates.base import SignalContext
    from services.gates.options import PutSweepCapitulationGate

    ctx = SignalContext(
        action="BUY", confidence=60.0, score=50.0, rationale=[], sources=set(),
        has_mr=True, vix=22.0, opt_flow={"iv_rank": 65},
        ...
    )
    PutSweepCapitulationGate().apply(ctx)
    assert ctx.score == 55.0
"""

from __future__ import annotations

from .base import GateBase, SignalContext


class OptionsFlowConfirmationGate(GateBase):
    """
    Options flow / GEX confirmation gate.

    Hard block: extreme put dominance (P/C > 2.0) → HOLD.
    Bonus (call sweep + positive GEX):     +15pp — highest-conviction MR setup.
    Bonus (positive GEX + call-dominant):  +5pp.
    Penalty (negative GEX + puts + low UV): −5pp.

    Only applies to MR BUY entries with opt_flow present.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or not ctx.has_mr or not ctx.opt_flow:
            return

        pc = ctx.opt_flow.get("pc_ratio")
        gex = float(ctx.opt_flow.get("gex") or 0.0)
        uv = ctx.opt_flow.get("unusual_vol_ratio")
        uv_s = f"{float(uv):.2f}" if uv is not None else "n/a"
        sweep_calls = bool(ctx.opt_flow.get("sweep_calls"))

        # Hard block: professional put hedging still building
        if pc is not None and float(pc) > 2.0:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Extreme Put Dominance — Options Flow Blocks MR Entry (P/C {float(pc):.2f})",
                    "body": (
                        f"Put/call ratio of {float(pc):.2f} across near-term expiries signals "
                        "institutional hedging at scale, not retail panic. When professionals are "
                        "buying puts this aggressively on an oversold stock, they expect further "
                        "downside — not a bounce. MR setups require fear exhaustion; extreme put "
                        "flow confirms the fear is still building."
                    ),
                    "sentiment": "neg",
                    "meta": f"pc_ratio={float(pc):.2f} > 2.0 | mr_entry=True | options_flow_gate=True",
                }
            )
            return

        # Highest-conviction: call sweep + positive GEX simultaneously
        if sweep_calls and gex > 0:
            ctx.confidence = round(min(95.0, ctx.confidence + 15), 1)
            ctx.sources.add("Options")
            gex_str = f"${gex / 1e6:.1f}M" if abs(gex) >= 1e6 else f"${gex:.0f}"
            ctx.rationale.append(
                {
                    "src": "Options",
                    "head": "Call Sweep + Positive GEX — Highest-Conviction MR Setup (+15pp)",
                    "body": (
                        f"Call sweep detected (large cross-exchange institutional order) with positive "
                        f"dealer GEX ({gex_str}). Call sweeps signal urgency — institutions are "
                        "accumulating aggressively, not passively. Positive GEX means dealers must "
                        "mechanically buy the dip to stay hedged, creating a structural support floor. "
                        "These two forces reinforce the MR bounce thesis."
                    ),
                    "sentiment": "pos",
                    "meta": f"sweep_calls=True gex={gex:.0f} | mr_entry=True | sweep_gex_combo=True | bonus=+15pp",
                }
            )
            return

        # Standard positive confirmation: positive GEX + call-dominant
        if pc is not None and gex > 0 and float(pc) < 0.75:
            ctx.confidence = round(min(95.0, ctx.confidence + 5), 1)
            ctx.sources.add("Options")
            ctx.rationale.append(
                {
                    "src": "Options",
                    "head": f"Options Flow Confirms MR Setup (P/C {float(pc):.2f}, Positive GEX)",
                    "body": (
                        f"Positive dealer GEX (${gex / 1e6:.1f}M) with call-dominant flow "
                        f"(P/C {float(pc):.2f}): dealers are net long gamma and must buy stock as "
                        "it dips — creating a mechanical support floor. Call dominance confirms "
                        "institutional accumulation, not distribution."
                    ),
                    "sentiment": "pos",
                    "meta": f"pc_ratio={float(pc):.2f} gex={gex:.0f} | mr_entry=True | options_flow_confirmed=True",
                }
            )
            return

        # Unconfirmed: negative GEX + put dominance + low unusual activity
        if pc is not None and gex < 0 and float(pc) > 1.5 and (uv is None or float(uv) < 0.5):
            ctx.confidence = round(max(35.0, ctx.confidence - 5), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Options Flow Unconfirmed — Negative GEX + Puts Dominating (P/C {float(pc):.2f})",
                    "body": (
                        f"Negative dealer GEX (${abs(gex) / 1e6:.1f}M) with put-dominant flow "
                        f"(P/C {float(pc):.2f}) and low unusual activity ratio ({uv_s}). "
                        "Dealers short gamma will amplify moves in both directions — volatility unpinned. "
                        "Put dominance without unusual call activity signals no institutional accumulation. "
                        "Applying −5pp confidence haircut."
                    ),
                    "sentiment": "neg",
                    "meta": f"pc_ratio={float(pc):.2f} gex={gex:.0f} uv={uv_s} | options_unconfirmed=True",
                }
            )


class IvRankFlagGate(GateBase):
    """
    Informational IV rank disclosure — no score/confidence change.

    IV Rank > 70 flags expensive options premium and post-earnings IV crush
    risk for the trader.  Fires regardless of has_mr.
    """

    def apply(self, ctx: SignalContext) -> None:
        if not ctx.opt_flow:
            return
        iv_rank = ctx.opt_flow.get("iv_rank")
        if iv_rank is None or float(iv_rank) <= 70:
            return

        days_since = ctx.earnings_cal.get("days_since_earnings")
        days_to = ctx.earnings_cal.get("days_to_earnings")
        near_earnings = (days_since is not None and 0 <= days_since <= 7) or (
            days_to is not None and 0 <= days_to <= 14
        )
        ivr = float(iv_rank)

        if days_since is not None and 0 <= (days_since or 999) <= 7:
            head = f"Elevated IV Rank {ivr:.0f} — Post-Earnings IV Crush Risk"
            body = (
                f"IV Rank of {ivr:.0f} (top {100 - ivr:.0f}% of trailing year) "
                f"with earnings {days_since}d ago: implied volatility will deflate rapidly (IV crush) "
                "— options premium buyers lose value even on correct directional moves. "
                "Favour stock entry over options; size equity positions accordingly."
            )
        else:
            head = f"Elevated IV Rank {ivr:.0f} — Options Premium Is Expensive"
            body = (
                f"IV Rank of {ivr:.0f} means implied volatility is elevated relative to the past year. "
                "Buying calls or puts here means paying rich premium — a significant move is needed just "
                "to break even. Consider stock entry instead of options, or wait for IV to normalise."
            )

        ctx.sources.add("Options")
        ctx.rationale.append(
            {
                "src": "Options",
                "head": head,
                "body": body,
                "sentiment": "neg",
                "meta": f"iv_rank={ivr:.1f} | near_earnings={near_earnings}",
            }
        )


# IvrMrGate (§48), PutCallSkewGate (§49), and IvTermStructureGate REMOVED
# (gate audit 2026-07-14): exact-head search shows 0 fires in 87,982 all-time
# signals — their opt_flow + has_mr (+ VIX>15) precondition combination is
# never satisfied at the assembler stage, so the claimed +4/+5pp MR credits
# were never applied even once. Untestable in backtest (no historical IV
# surface). The general score_options() IVR/skew cards are unaffected.


class PutSweepCapitulationGate(GateBase):
    """
    Extreme put sweep capitulation confirmation.

    A put sweep with vol/OI > 10× and volume > 1000 contracts (with NO call
    sweeps present) is the signature of forced protection buying at capitulation,
    not informed institutional shorting.  Confidence +5pp.
    """

    def apply(self, ctx: SignalContext) -> None:
        if not ctx.opt_flow or not ctx.has_mr or ctx.action != "BUY":
            return
        sweep_puts = ctx.opt_flow.get("sweep_puts") or []
        sweep_calls = ctx.opt_flow.get("sweep_calls") or []
        if not sweep_puts or sweep_calls:
            return
        top = sweep_puts[0]
        vol_oi = float(top.get("vol_oi", 0))
        vol = int(top.get("vol", 0))
        if vol_oi > 10 and vol > 1000:
            ctx.confidence = round(min(95.0, ctx.confidence + 5), 1)
            ctx.sources.add("Options")
            ctx.rationale.append(
                {
                    "src": "Options",
                    "head": f"Extreme Put Sweep ({vol:,} contracts, {vol_oi:.0f}× OI) — Capitulation Signal",
                    "body": (
                        f"Single-strike put sweep: {vol:,} contracts at {vol_oi:.0f}× open interest "
                        f"(strike ${top.get('strike', 0):.0f}, expiry {top.get('expiry', 'n/a')}). "
                        "Extreme vol/OI ratio (>10×) with high volume is the signature of forced protection "
                        "buying at capitulation — institutions covering longs in panic, not informed shorts "
                        "(which use smaller iceberg-style orders). No offsetting call sweep present. "
                        "Confidence +5pp."
                    ),
                    "sentiment": "pos",
                    "meta": f"sweep_put_vol={vol} vol_oi={vol_oi:.1f}× capitulation_signal=True",
                }
            )
