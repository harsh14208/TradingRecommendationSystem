"""
services/gates/base — Strategy Pattern infrastructure for signal gates.

SignalContext  : all mutable + read-only state flowing through the pipeline.
GateBase       : ABC that every gate must implement.
GatePipeline   : runner that applies a list of gates in order.

Each gate receives the context, reads what it needs, and mutates only
(action, confidence, score, rationale, sources).  Gates that want to
block a signal set ctx.action = "HOLD"; downstream guards on
`ctx.action == "BUY"` then skip naturally — no early-exit needed.

Adding a new gate:
  1. Create a class that inherits from GateBase.
  2. Implement apply(self, ctx: SignalContext) -> None.
  3. Add an instance to the appropriate GatePipeline in _assemble_signal().

Extracting from _assemble_signal() incrementally:
  After each group of gates is moved to a module, replace the inline block
  with a pipeline call and sync mutable state back to local variables.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


@dataclass
class SignalContext:
    """
    Mutable + read-only state for one signal as it moves through the gate
    pipeline.  Mutable fields (action, confidence, score, rationale, sources)
    are mutated in place by each gate.  All other fields are read-only inputs
    set once when the context is constructed.
    """

    # ── Mutable pipeline state ──────────────────────────────────────────────
    action: str
    confidence: float
    score: float
    rationale: list
    sources: set

    # ── Core signal inputs ──────────────────────────────────────────────────
    ticker: str
    tech: dict
    info: dict
    macro: dict
    price: float
    atr: float

    # ── Derived / pre-computed flags ────────────────────────────────────────
    has_mr: bool  # MR entry condition (BB%B / IBS / VWAP% / RSI thresholds)
    vix: Optional[float]
    sp500_trend: Optional[str]
    sector_etf: str  # (sector_rs or {}).get("sector_etf", "")
    today_dow: int  # 0=Monday … 4=Friday
    month: int  # 1–12

    # ── Optional enrichment inputs ──────────────────────────────────────────
    opt_flow: Optional[dict]
    sector_rs: Optional[dict]
    earnings_cal: dict
    days_to_earnings: Optional[int]
    is_low_atr: bool
    atr_pct_pre: float

    # ── Extended inputs (populated by signal_engine; default-safe for tests) ─
    sector_config: dict = field(default_factory=dict)  # _SECTOR_MR_CONFIG[sector_etf]
    is_lev_etf: bool = False  # ticker in _LEVERAGED_ETFS
    gate_traces: list[dict] = field(default_factory=list)  # TSYS-6a


class GateBase(ABC):
    """
    Abstract base for all signal gates.

    Implement apply() to read from ctx, then mutate:
      ctx.action     — set "HOLD" to block the signal
      ctx.confidence — adjust up or down (respect min=35, max=72/95 as needed)
      ctx.score      — adjust if this gate feeds raw_score (post-_score_to_action only)
      ctx.rationale  — append informational / blocking card dicts
      ctx.sources    — add source strings

    Do NOT read ctx.action == "BUY" outside of guards — always check first.
    """

    @abstractmethod
    def apply(self, ctx: SignalContext) -> None: ...

    def __repr__(self) -> str:
        return self.__class__.__name__
mutants_xǁGatePipelineǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁGatePipelineǁrun__mutmut: MutantDict = {}  # type: ignore
mutants_xǁGatePipelineǁ__repr____mutmut: MutantDict = {}  # type: ignore


class GatePipeline:
    """
    Applies a list of GateBase gates in order against a SignalContext.

    No early-exit on HOLD: downstream gates that guard on `ctx.action == "BUY"`
    skip themselves naturally.  This preserves informational cards (e.g., data
    quality disclosures) that should fire regardless of action.
    """

    @_mutmut_mutated(mutants_xǁGatePipelineǁ__init____mutmut)
    def __init__(self, gates: list[GateBase]) -> None:
        self.gates = gates

    def xǁGatePipelineǁ__init____mutmut_orig(self, gates: list[GateBase]) -> None:
        self.gates = gates

    def xǁGatePipelineǁ__init____mutmut_1(self, gates: list[GateBase]) -> None:
        self.gates = None

    @_mutmut_mutated(mutants_xǁGatePipelineǁrun__mutmut)
    def run(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_orig(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_1(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = None
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_2(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = None
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_3(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = None

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_4(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(None)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_5(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = None
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_6(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = False
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_7(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" or prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_8(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action != "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_9(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "XXHOLDXX" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_10(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "hold" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_11(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action not in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_12(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("XXBUYXX", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_13(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("buy", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_14(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "XXSELLXX"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_15(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "sell"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_16(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = None

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_17(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = True

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_18(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = ""
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_19(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = None
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_20(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[+1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_21(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-2]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_22(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ and last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_23(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get(None) == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_24(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("XXsrcXX") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_25(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("SRC") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_26(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") != gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_27(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get(None) == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_28(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("XXsrcXX") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_29(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("SRC") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_30(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") != "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_31(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "XXRisk GateXX":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_32(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "risk gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_33(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "RISK GATE":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_34(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = None

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_35(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") and last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_36(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get(None) or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_37(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("XXheadXX") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_38(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("HEAD") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_39(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get(None)

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_40(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("XXbodyXX")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_41(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("BODY")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_42(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                None
            )

    def xǁGatePipelineǁrun__mutmut_43(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "XXgate_idXX": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_44(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "GATE_ID": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_45(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "XXversionXX": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_46(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "VERSION": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_47(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(None, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_48(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, None, "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_49(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", None),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_50(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr("version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_51(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_52(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", ),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_53(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "XXversionXX", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_54(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "VERSION", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_55(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "XX1.0XX"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_56(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "XXinput_valuesXX": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_57(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "INPUT_VALUES": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_58(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "XXpriceXX": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_59(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "PRICE": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_60(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "XXatrXX": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_61(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "ATR": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_62(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "XXhas_mrXX": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_63(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "HAS_MR": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_64(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "XXvixXX": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_65(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "VIX": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_66(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "XXtickerXX": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_67(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "TICKER": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_68(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "XXscore_deltaXX": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_69(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "SCORE_DELTA": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_70(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score + prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_71(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "XXconfidence_deltaXX": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_72(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "CONFIDENCE_DELTA": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_73(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence + prev_confidence,
                    "passed": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_74(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "XXpassedXX": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_75(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "PASSED": passed,
                    "reason": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_76(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "XXreasonXX": reason,
                }
            )

    def xǁGatePipelineǁrun__mutmut_77(self, ctx: SignalContext) -> None:
        for gate in self.gates:
            prev_action = ctx.action
            prev_confidence = ctx.confidence
            prev_score = ctx.score

            gate.apply(ctx)

            passed = True
            if ctx.action == "HOLD" and prev_action in ("BUY", "SELL"):
                passed = False

            reason = None
            if ctx.rationale:
                last_card = ctx.rationale[-1]
                # If the last card's source matches this gate or Risk Gate, use its message
                if last_card.get("src") == gate.__class__.__name__ or last_card.get("src") == "Risk Gate":
                    reason = last_card.get("head") or last_card.get("body")

            ctx.gate_traces.append(
                {
                    "gate_id": gate.__class__.__name__,
                    "version": getattr(gate, "version", "1.0"),
                    "input_values": {
                        "price": ctx.price,
                        "atr": ctx.atr,
                        "has_mr": ctx.has_mr,
                        "vix": ctx.vix,
                        "ticker": ctx.ticker,
                    },
                    "score_delta": ctx.score - prev_score,
                    "confidence_delta": ctx.confidence - prev_confidence,
                    "passed": passed,
                    "REASON": reason,
                }
            )

    @_mutmut_mutated(mutants_xǁGatePipelineǁ__repr____mutmut)
    def __repr__(self) -> str:
        names = ", ".join(repr(g) for g in self.gates)
        return f"GatePipeline([{names}])"

    def xǁGatePipelineǁ__repr____mutmut_orig(self) -> str:
        names = ", ".join(repr(g) for g in self.gates)
        return f"GatePipeline([{names}])"

    def xǁGatePipelineǁ__repr____mutmut_1(self) -> str:
        names = None
        return f"GatePipeline([{names}])"

    def xǁGatePipelineǁ__repr____mutmut_2(self) -> str:
        names = ", ".join(None)
        return f"GatePipeline([{names}])"

    def xǁGatePipelineǁ__repr____mutmut_3(self) -> str:
        names = "XX, XX".join(repr(g) for g in self.gates)
        return f"GatePipeline([{names}])"

    def xǁGatePipelineǁ__repr____mutmut_4(self) -> str:
        names = ", ".join(repr(None) for g in self.gates)
        return f"GatePipeline([{names}])"

mutants_xǁGatePipelineǁ__init____mutmut['_mutmut_orig'] = GatePipeline.xǁGatePipelineǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁGatePipelineǁ__init____mutmut['xǁGatePipelineǁ__init____mutmut_1'] = GatePipeline.xǁGatePipelineǁ__init____mutmut_1 # type: ignore # mutmut generated

mutants_xǁGatePipelineǁrun__mutmut['_mutmut_orig'] = GatePipeline.xǁGatePipelineǁrun__mutmut_orig # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_1'] = GatePipeline.xǁGatePipelineǁrun__mutmut_1 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_2'] = GatePipeline.xǁGatePipelineǁrun__mutmut_2 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_3'] = GatePipeline.xǁGatePipelineǁrun__mutmut_3 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_4'] = GatePipeline.xǁGatePipelineǁrun__mutmut_4 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_5'] = GatePipeline.xǁGatePipelineǁrun__mutmut_5 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_6'] = GatePipeline.xǁGatePipelineǁrun__mutmut_6 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_7'] = GatePipeline.xǁGatePipelineǁrun__mutmut_7 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_8'] = GatePipeline.xǁGatePipelineǁrun__mutmut_8 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_9'] = GatePipeline.xǁGatePipelineǁrun__mutmut_9 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_10'] = GatePipeline.xǁGatePipelineǁrun__mutmut_10 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_11'] = GatePipeline.xǁGatePipelineǁrun__mutmut_11 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_12'] = GatePipeline.xǁGatePipelineǁrun__mutmut_12 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_13'] = GatePipeline.xǁGatePipelineǁrun__mutmut_13 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_14'] = GatePipeline.xǁGatePipelineǁrun__mutmut_14 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_15'] = GatePipeline.xǁGatePipelineǁrun__mutmut_15 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_16'] = GatePipeline.xǁGatePipelineǁrun__mutmut_16 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_17'] = GatePipeline.xǁGatePipelineǁrun__mutmut_17 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_18'] = GatePipeline.xǁGatePipelineǁrun__mutmut_18 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_19'] = GatePipeline.xǁGatePipelineǁrun__mutmut_19 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_20'] = GatePipeline.xǁGatePipelineǁrun__mutmut_20 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_21'] = GatePipeline.xǁGatePipelineǁrun__mutmut_21 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_22'] = GatePipeline.xǁGatePipelineǁrun__mutmut_22 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_23'] = GatePipeline.xǁGatePipelineǁrun__mutmut_23 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_24'] = GatePipeline.xǁGatePipelineǁrun__mutmut_24 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_25'] = GatePipeline.xǁGatePipelineǁrun__mutmut_25 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_26'] = GatePipeline.xǁGatePipelineǁrun__mutmut_26 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_27'] = GatePipeline.xǁGatePipelineǁrun__mutmut_27 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_28'] = GatePipeline.xǁGatePipelineǁrun__mutmut_28 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_29'] = GatePipeline.xǁGatePipelineǁrun__mutmut_29 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_30'] = GatePipeline.xǁGatePipelineǁrun__mutmut_30 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_31'] = GatePipeline.xǁGatePipelineǁrun__mutmut_31 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_32'] = GatePipeline.xǁGatePipelineǁrun__mutmut_32 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_33'] = GatePipeline.xǁGatePipelineǁrun__mutmut_33 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_34'] = GatePipeline.xǁGatePipelineǁrun__mutmut_34 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_35'] = GatePipeline.xǁGatePipelineǁrun__mutmut_35 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_36'] = GatePipeline.xǁGatePipelineǁrun__mutmut_36 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_37'] = GatePipeline.xǁGatePipelineǁrun__mutmut_37 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_38'] = GatePipeline.xǁGatePipelineǁrun__mutmut_38 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_39'] = GatePipeline.xǁGatePipelineǁrun__mutmut_39 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_40'] = GatePipeline.xǁGatePipelineǁrun__mutmut_40 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_41'] = GatePipeline.xǁGatePipelineǁrun__mutmut_41 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_42'] = GatePipeline.xǁGatePipelineǁrun__mutmut_42 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_43'] = GatePipeline.xǁGatePipelineǁrun__mutmut_43 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_44'] = GatePipeline.xǁGatePipelineǁrun__mutmut_44 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_45'] = GatePipeline.xǁGatePipelineǁrun__mutmut_45 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_46'] = GatePipeline.xǁGatePipelineǁrun__mutmut_46 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_47'] = GatePipeline.xǁGatePipelineǁrun__mutmut_47 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_48'] = GatePipeline.xǁGatePipelineǁrun__mutmut_48 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_49'] = GatePipeline.xǁGatePipelineǁrun__mutmut_49 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_50'] = GatePipeline.xǁGatePipelineǁrun__mutmut_50 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_51'] = GatePipeline.xǁGatePipelineǁrun__mutmut_51 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_52'] = GatePipeline.xǁGatePipelineǁrun__mutmut_52 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_53'] = GatePipeline.xǁGatePipelineǁrun__mutmut_53 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_54'] = GatePipeline.xǁGatePipelineǁrun__mutmut_54 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_55'] = GatePipeline.xǁGatePipelineǁrun__mutmut_55 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_56'] = GatePipeline.xǁGatePipelineǁrun__mutmut_56 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_57'] = GatePipeline.xǁGatePipelineǁrun__mutmut_57 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_58'] = GatePipeline.xǁGatePipelineǁrun__mutmut_58 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_59'] = GatePipeline.xǁGatePipelineǁrun__mutmut_59 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_60'] = GatePipeline.xǁGatePipelineǁrun__mutmut_60 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_61'] = GatePipeline.xǁGatePipelineǁrun__mutmut_61 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_62'] = GatePipeline.xǁGatePipelineǁrun__mutmut_62 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_63'] = GatePipeline.xǁGatePipelineǁrun__mutmut_63 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_64'] = GatePipeline.xǁGatePipelineǁrun__mutmut_64 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_65'] = GatePipeline.xǁGatePipelineǁrun__mutmut_65 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_66'] = GatePipeline.xǁGatePipelineǁrun__mutmut_66 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_67'] = GatePipeline.xǁGatePipelineǁrun__mutmut_67 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_68'] = GatePipeline.xǁGatePipelineǁrun__mutmut_68 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_69'] = GatePipeline.xǁGatePipelineǁrun__mutmut_69 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_70'] = GatePipeline.xǁGatePipelineǁrun__mutmut_70 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_71'] = GatePipeline.xǁGatePipelineǁrun__mutmut_71 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_72'] = GatePipeline.xǁGatePipelineǁrun__mutmut_72 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_73'] = GatePipeline.xǁGatePipelineǁrun__mutmut_73 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_74'] = GatePipeline.xǁGatePipelineǁrun__mutmut_74 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_75'] = GatePipeline.xǁGatePipelineǁrun__mutmut_75 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_76'] = GatePipeline.xǁGatePipelineǁrun__mutmut_76 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁrun__mutmut['xǁGatePipelineǁrun__mutmut_77'] = GatePipeline.xǁGatePipelineǁrun__mutmut_77 # type: ignore # mutmut generated

mutants_xǁGatePipelineǁ__repr____mutmut['_mutmut_orig'] = GatePipeline.xǁGatePipelineǁ__repr____mutmut_orig # type: ignore # mutmut generated
mutants_xǁGatePipelineǁ__repr____mutmut['xǁGatePipelineǁ__repr____mutmut_1'] = GatePipeline.xǁGatePipelineǁ__repr____mutmut_1 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁ__repr____mutmut['xǁGatePipelineǁ__repr____mutmut_2'] = GatePipeline.xǁGatePipelineǁ__repr____mutmut_2 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁ__repr____mutmut['xǁGatePipelineǁ__repr____mutmut_3'] = GatePipeline.xǁGatePipelineǁ__repr____mutmut_3 # type: ignore # mutmut generated
mutants_xǁGatePipelineǁ__repr____mutmut['xǁGatePipelineǁ__repr____mutmut_4'] = GatePipeline.xǁGatePipelineǁ__repr____mutmut_4 # type: ignore # mutmut generated
