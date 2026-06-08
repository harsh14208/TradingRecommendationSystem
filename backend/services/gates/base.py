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


class GatePipeline:
    """
    Applies a list of GateBase gates in order against a SignalContext.

    No early-exit on HOLD: downstream gates that guard on `ctx.action == "BUY"`
    skip themselves naturally.  This preserves informational cards (e.g., data
    quality disclosures) that should fire regardless of action.
    """

    def __init__(self, gates: list[GateBase]) -> None:
        self.gates = gates

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

    def __repr__(self) -> str:
        names = ", ".join(repr(g) for g in self.gates)
        return f"GatePipeline([{names}])"
