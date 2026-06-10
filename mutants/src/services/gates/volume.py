"""
Volume, momentum-quality, and liquidity gates extracted from _assemble_signal().

Gates (applied in pipeline order):
  RvolGate             — RVOL BUY prerequisite (regime-adaptive threshold)
  AdxGate              — ADX minimum (no entries in directionless markets)
  OverboughtWeakTrendGate — RSI overbought + fading ADX topping filter
  DollarVolumeGate     — thin liquidity confidence haircut + low-ATR disclosure

Each gate is independently unit-testable:
    ctx = SignalContext(action="BUY", confidence=65.0, score=52.0,
                        rationale=[], sources=set(), ...)
    RvolGate().apply(ctx)
    assert ctx.action == "HOLD"
"""

from __future__ import annotations

from .base import GateBase, SignalContext


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁRvolGateǁapply__mutmut: MutantDict = {}  # type: ignore


class RvolGate(GateBase):
    """
    RVOL BUY prerequisite (regime-adaptive threshold).

    Normal regime  (ADR compressed): requires RVOL ≥ 1.2×.
    Expanded regime (ADR elevated) : requires RVOL ≥ 1.0×.
    Waiver: RSI < 30 (pure oversold bounce — no volume confirmation needed).
    """

    @_mutmut_mutated(mutants_xǁRvolGateǁapply__mutmut)
    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_orig(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_1(self, ctx: SignalContext) -> None:
        if ctx.action == "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_2(self, ctx: SignalContext) -> None:
        if ctx.action != "XXBUYXX":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_3(self, ctx: SignalContext) -> None:
        if ctx.action != "buy":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_4(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = None
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_5(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") and 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_6(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get(None) or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_7(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("XXvolumeXX") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_8(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("VOLUME") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_9(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 1
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_10(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = None
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_11(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") and 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_12(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get(None) or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_13(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("XXavg_volumeXX") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_14(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("AVG_VOLUME") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_15(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 1
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_16(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol < 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_17(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 1:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_18(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = None
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_19(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume * avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_20(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = None
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_21(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None or ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_22(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get(None) is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_23(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("XXrsiXX") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_24(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("RSI") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_25(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_26(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get(None) < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_27(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("XXrsiXX") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_28(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("RSI") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_29(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") <= 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_30(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 31
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_31(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = None
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_32(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get(None, True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_33(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", None)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_34(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get(True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_35(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", )
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_36(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("XXadr_compressionXX", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_37(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("ADR_COMPRESSION", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_38(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", False)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_39(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = None
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_40(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 2.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_41(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 2.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_42(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio <= threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_43(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = None
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_44(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "XXHOLDXX"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_45(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "hold"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_46(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add(None)
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_47(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("XXRisk GateXX")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_48(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("risk gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_49(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("RISK GATE")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_50(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                None
            )

    def xǁRvolGateǁapply__mutmut_51(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "XXsrcXX": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_52(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "SRC": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_53(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "XXRisk GateXX",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_54(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "risk gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_55(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "RISK GATE",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_56(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "XXheadXX": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_57(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "HEAD": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_58(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "XXbodyXX": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_59(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "BODY": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_60(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. " - (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_61(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "XXinstitutional participation. Low-volume breakouts fail at high rates XX"
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_62(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_63(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "INSTITUTIONAL PARTICIPATION. LOW-VOLUME BREAKOUTS FAIL AT HIGH RATES "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_64(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "XXregardless of score. Oversold bounce (RSI < 30) is the only waiver. XX"
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_65(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. oversold bounce (rsi < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_66(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "REGARDLESS OF SCORE. OVERSOLD BOUNCE (RSI < 30) IS THE ONLY WAIVER. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_67(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "XXVol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×.XX"
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_68(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "vol regime: expanded (adr not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_69(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "VOL REGIME: EXPANDED (ADR NOT COMPRESSED) — THRESHOLD RELAXED TO 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_70(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_71(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "XXVol regime: normal — standard 1.2× threshold applied.XX"
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_72(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_73(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "VOL REGIME: NORMAL — STANDARD 1.2× THRESHOLD APPLIED."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_74(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "XXsentimentXX": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_75(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "SENTIMENT": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_76(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "XXnegXX",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_77(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "NEG",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_78(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "XXmetaXX": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

    def xǁRvolGateǁapply__mutmut_79(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "META": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )

mutants_xǁRvolGateǁapply__mutmut['_mutmut_orig'] = RvolGate.xǁRvolGateǁapply__mutmut_orig # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_1'] = RvolGate.xǁRvolGateǁapply__mutmut_1 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_2'] = RvolGate.xǁRvolGateǁapply__mutmut_2 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_3'] = RvolGate.xǁRvolGateǁapply__mutmut_3 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_4'] = RvolGate.xǁRvolGateǁapply__mutmut_4 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_5'] = RvolGate.xǁRvolGateǁapply__mutmut_5 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_6'] = RvolGate.xǁRvolGateǁapply__mutmut_6 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_7'] = RvolGate.xǁRvolGateǁapply__mutmut_7 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_8'] = RvolGate.xǁRvolGateǁapply__mutmut_8 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_9'] = RvolGate.xǁRvolGateǁapply__mutmut_9 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_10'] = RvolGate.xǁRvolGateǁapply__mutmut_10 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_11'] = RvolGate.xǁRvolGateǁapply__mutmut_11 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_12'] = RvolGate.xǁRvolGateǁapply__mutmut_12 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_13'] = RvolGate.xǁRvolGateǁapply__mutmut_13 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_14'] = RvolGate.xǁRvolGateǁapply__mutmut_14 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_15'] = RvolGate.xǁRvolGateǁapply__mutmut_15 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_16'] = RvolGate.xǁRvolGateǁapply__mutmut_16 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_17'] = RvolGate.xǁRvolGateǁapply__mutmut_17 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_18'] = RvolGate.xǁRvolGateǁapply__mutmut_18 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_19'] = RvolGate.xǁRvolGateǁapply__mutmut_19 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_20'] = RvolGate.xǁRvolGateǁapply__mutmut_20 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_21'] = RvolGate.xǁRvolGateǁapply__mutmut_21 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_22'] = RvolGate.xǁRvolGateǁapply__mutmut_22 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_23'] = RvolGate.xǁRvolGateǁapply__mutmut_23 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_24'] = RvolGate.xǁRvolGateǁapply__mutmut_24 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_25'] = RvolGate.xǁRvolGateǁapply__mutmut_25 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_26'] = RvolGate.xǁRvolGateǁapply__mutmut_26 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_27'] = RvolGate.xǁRvolGateǁapply__mutmut_27 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_28'] = RvolGate.xǁRvolGateǁapply__mutmut_28 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_29'] = RvolGate.xǁRvolGateǁapply__mutmut_29 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_30'] = RvolGate.xǁRvolGateǁapply__mutmut_30 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_31'] = RvolGate.xǁRvolGateǁapply__mutmut_31 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_32'] = RvolGate.xǁRvolGateǁapply__mutmut_32 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_33'] = RvolGate.xǁRvolGateǁapply__mutmut_33 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_34'] = RvolGate.xǁRvolGateǁapply__mutmut_34 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_35'] = RvolGate.xǁRvolGateǁapply__mutmut_35 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_36'] = RvolGate.xǁRvolGateǁapply__mutmut_36 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_37'] = RvolGate.xǁRvolGateǁapply__mutmut_37 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_38'] = RvolGate.xǁRvolGateǁapply__mutmut_38 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_39'] = RvolGate.xǁRvolGateǁapply__mutmut_39 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_40'] = RvolGate.xǁRvolGateǁapply__mutmut_40 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_41'] = RvolGate.xǁRvolGateǁapply__mutmut_41 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_42'] = RvolGate.xǁRvolGateǁapply__mutmut_42 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_43'] = RvolGate.xǁRvolGateǁapply__mutmut_43 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_44'] = RvolGate.xǁRvolGateǁapply__mutmut_44 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_45'] = RvolGate.xǁRvolGateǁapply__mutmut_45 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_46'] = RvolGate.xǁRvolGateǁapply__mutmut_46 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_47'] = RvolGate.xǁRvolGateǁapply__mutmut_47 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_48'] = RvolGate.xǁRvolGateǁapply__mutmut_48 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_49'] = RvolGate.xǁRvolGateǁapply__mutmut_49 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_50'] = RvolGate.xǁRvolGateǁapply__mutmut_50 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_51'] = RvolGate.xǁRvolGateǁapply__mutmut_51 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_52'] = RvolGate.xǁRvolGateǁapply__mutmut_52 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_53'] = RvolGate.xǁRvolGateǁapply__mutmut_53 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_54'] = RvolGate.xǁRvolGateǁapply__mutmut_54 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_55'] = RvolGate.xǁRvolGateǁapply__mutmut_55 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_56'] = RvolGate.xǁRvolGateǁapply__mutmut_56 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_57'] = RvolGate.xǁRvolGateǁapply__mutmut_57 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_58'] = RvolGate.xǁRvolGateǁapply__mutmut_58 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_59'] = RvolGate.xǁRvolGateǁapply__mutmut_59 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_60'] = RvolGate.xǁRvolGateǁapply__mutmut_60 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_61'] = RvolGate.xǁRvolGateǁapply__mutmut_61 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_62'] = RvolGate.xǁRvolGateǁapply__mutmut_62 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_63'] = RvolGate.xǁRvolGateǁapply__mutmut_63 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_64'] = RvolGate.xǁRvolGateǁapply__mutmut_64 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_65'] = RvolGate.xǁRvolGateǁapply__mutmut_65 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_66'] = RvolGate.xǁRvolGateǁapply__mutmut_66 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_67'] = RvolGate.xǁRvolGateǁapply__mutmut_67 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_68'] = RvolGate.xǁRvolGateǁapply__mutmut_68 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_69'] = RvolGate.xǁRvolGateǁapply__mutmut_69 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_70'] = RvolGate.xǁRvolGateǁapply__mutmut_70 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_71'] = RvolGate.xǁRvolGateǁapply__mutmut_71 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_72'] = RvolGate.xǁRvolGateǁapply__mutmut_72 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_73'] = RvolGate.xǁRvolGateǁapply__mutmut_73 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_74'] = RvolGate.xǁRvolGateǁapply__mutmut_74 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_75'] = RvolGate.xǁRvolGateǁapply__mutmut_75 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_76'] = RvolGate.xǁRvolGateǁapply__mutmut_76 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_77'] = RvolGate.xǁRvolGateǁapply__mutmut_77 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_78'] = RvolGate.xǁRvolGateǁapply__mutmut_78 # type: ignore # mutmut generated
mutants_xǁRvolGateǁapply__mutmut['xǁRvolGateǁapply__mutmut_79'] = RvolGate.xǁRvolGateǁapply__mutmut_79 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut: MutantDict = {}  # type: ignore


class AdxGate(GateBase):
    """
    ADX minimum gate — no entries in completely directionless markets.

    Fires when ADX < 18 and RSI ≥ 30 and score < 45.
    Waived for deep-oversold bounces (RSI < 30) where MR works even flat.
    """

    @_mutmut_mutated(mutants_xǁAdxGateǁapply__mutmut)
    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_orig(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_1(self, ctx: SignalContext) -> None:
        if ctx.action == "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_2(self, ctx: SignalContext) -> None:
        if ctx.action != "XXBUYXX":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_3(self, ctx: SignalContext) -> None:
        if ctx.action != "buy":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_4(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = None
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_5(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get(None)
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_6(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("XXadxXX")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_7(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("ADX")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_8(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = None
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_9(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(None)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_10(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") and 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_11(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get(None) or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_12(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("XXrsiXX") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_13(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("RSI") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_14(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 51)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_15(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is not None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_16(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 or ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_17(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 or rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_18(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(None) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_19(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) <= 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_20(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 19 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_21(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi > 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_22(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 31 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_23(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score <= 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_24(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 46:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_25(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = None
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_26(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "XXHOLDXX"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_27(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "hold"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_28(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add(None)
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_29(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("XXRisk GateXX")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_30(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("risk gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_31(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("RISK GATE")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_32(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                None
            )

    def xǁAdxGateǁapply__mutmut_33(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "XXsrcXX": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_34(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "SRC": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_35(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "XXRisk GateXX",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_36(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "risk gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_37(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "RISK GATE",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_38(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "XXheadXX": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_39(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "HEAD": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_40(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(None):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_41(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "XXbodyXX": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_42(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "BODY": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_43(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(None):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_44(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "XXand breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 XX"
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_45(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. requiring adx ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_46(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "AND BREAKOUT SIGNALS WHIPSAW IN CHOPPY FLAT MARKETS. REQUIRING ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_47(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "XXto confirm a minimum directional trend before issuing BUY.XX"
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_48(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing buy."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_49(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "TO CONFIRM A MINIMUM DIRECTIONAL TREND BEFORE ISSUING BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_50(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "XXsentimentXX": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_51(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "SENTIMENT": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_52(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "XXnegXX",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_53(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "NEG",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_54(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "XXmetaXX": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_55(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "META": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

    def xǁAdxGateǁapply__mutmut_56(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(None):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )

mutants_xǁAdxGateǁapply__mutmut['_mutmut_orig'] = AdxGate.xǁAdxGateǁapply__mutmut_orig # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_1'] = AdxGate.xǁAdxGateǁapply__mutmut_1 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_2'] = AdxGate.xǁAdxGateǁapply__mutmut_2 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_3'] = AdxGate.xǁAdxGateǁapply__mutmut_3 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_4'] = AdxGate.xǁAdxGateǁapply__mutmut_4 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_5'] = AdxGate.xǁAdxGateǁapply__mutmut_5 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_6'] = AdxGate.xǁAdxGateǁapply__mutmut_6 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_7'] = AdxGate.xǁAdxGateǁapply__mutmut_7 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_8'] = AdxGate.xǁAdxGateǁapply__mutmut_8 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_9'] = AdxGate.xǁAdxGateǁapply__mutmut_9 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_10'] = AdxGate.xǁAdxGateǁapply__mutmut_10 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_11'] = AdxGate.xǁAdxGateǁapply__mutmut_11 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_12'] = AdxGate.xǁAdxGateǁapply__mutmut_12 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_13'] = AdxGate.xǁAdxGateǁapply__mutmut_13 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_14'] = AdxGate.xǁAdxGateǁapply__mutmut_14 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_15'] = AdxGate.xǁAdxGateǁapply__mutmut_15 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_16'] = AdxGate.xǁAdxGateǁapply__mutmut_16 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_17'] = AdxGate.xǁAdxGateǁapply__mutmut_17 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_18'] = AdxGate.xǁAdxGateǁapply__mutmut_18 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_19'] = AdxGate.xǁAdxGateǁapply__mutmut_19 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_20'] = AdxGate.xǁAdxGateǁapply__mutmut_20 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_21'] = AdxGate.xǁAdxGateǁapply__mutmut_21 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_22'] = AdxGate.xǁAdxGateǁapply__mutmut_22 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_23'] = AdxGate.xǁAdxGateǁapply__mutmut_23 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_24'] = AdxGate.xǁAdxGateǁapply__mutmut_24 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_25'] = AdxGate.xǁAdxGateǁapply__mutmut_25 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_26'] = AdxGate.xǁAdxGateǁapply__mutmut_26 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_27'] = AdxGate.xǁAdxGateǁapply__mutmut_27 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_28'] = AdxGate.xǁAdxGateǁapply__mutmut_28 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_29'] = AdxGate.xǁAdxGateǁapply__mutmut_29 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_30'] = AdxGate.xǁAdxGateǁapply__mutmut_30 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_31'] = AdxGate.xǁAdxGateǁapply__mutmut_31 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_32'] = AdxGate.xǁAdxGateǁapply__mutmut_32 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_33'] = AdxGate.xǁAdxGateǁapply__mutmut_33 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_34'] = AdxGate.xǁAdxGateǁapply__mutmut_34 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_35'] = AdxGate.xǁAdxGateǁapply__mutmut_35 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_36'] = AdxGate.xǁAdxGateǁapply__mutmut_36 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_37'] = AdxGate.xǁAdxGateǁapply__mutmut_37 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_38'] = AdxGate.xǁAdxGateǁapply__mutmut_38 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_39'] = AdxGate.xǁAdxGateǁapply__mutmut_39 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_40'] = AdxGate.xǁAdxGateǁapply__mutmut_40 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_41'] = AdxGate.xǁAdxGateǁapply__mutmut_41 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_42'] = AdxGate.xǁAdxGateǁapply__mutmut_42 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_43'] = AdxGate.xǁAdxGateǁapply__mutmut_43 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_44'] = AdxGate.xǁAdxGateǁapply__mutmut_44 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_45'] = AdxGate.xǁAdxGateǁapply__mutmut_45 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_46'] = AdxGate.xǁAdxGateǁapply__mutmut_46 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_47'] = AdxGate.xǁAdxGateǁapply__mutmut_47 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_48'] = AdxGate.xǁAdxGateǁapply__mutmut_48 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_49'] = AdxGate.xǁAdxGateǁapply__mutmut_49 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_50'] = AdxGate.xǁAdxGateǁapply__mutmut_50 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_51'] = AdxGate.xǁAdxGateǁapply__mutmut_51 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_52'] = AdxGate.xǁAdxGateǁapply__mutmut_52 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_53'] = AdxGate.xǁAdxGateǁapply__mutmut_53 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_54'] = AdxGate.xǁAdxGateǁapply__mutmut_54 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_55'] = AdxGate.xǁAdxGateǁapply__mutmut_55 # type: ignore # mutmut generated
mutants_xǁAdxGateǁapply__mutmut['xǁAdxGateǁapply__mutmut_56'] = AdxGate.xǁAdxGateǁapply__mutmut_56 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut: MutantDict = {}  # type: ignore


class OverboughtWeakTrendGate(GateBase):
    """
    RSI overbought + weak trend gate (topping market filter).

    Fires when RSI > 70 AND ADX < 28 AND sp500_trend == "up" AND score < 40.
    When ADX ≥ 28, RSI > 70 is a valid momentum continuation — not fired.
    """

    @_mutmut_mutated(mutants_xǁOverboughtWeakTrendGateǁapply__mutmut)
    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_orig(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_1(self, ctx: SignalContext) -> None:
        if ctx.action == "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_2(self, ctx: SignalContext) -> None:
        if ctx.action != "XXBUYXX":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_3(self, ctx: SignalContext) -> None:
        if ctx.action != "buy":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_4(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = None
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_5(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(None)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_6(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") and 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_7(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get(None) or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_8(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("XXrsiXX") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_9(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("RSI") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_10(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 51)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_11(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = None
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_12(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get(None)
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_13(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("XXadxXX")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_14(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("ADX")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_15(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = None
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_16(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(None) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_17(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_18(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 26.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_19(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 or ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_20(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 or adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_21(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" or rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_22(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend != "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_23(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "XXupXX" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_24(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "UP" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_25(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi >= 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_26(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 71 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_27(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val <= 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_28(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 29 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_29(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score <= 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_30(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 41:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_31(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = None
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_32(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "XXHOLDXX"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_33(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "hold"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_34(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add(None)
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_35(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("XXRisk GateXX")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_36(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("risk gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_37(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("RISK GATE")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_38(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                None
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_39(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "XXsrcXX": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_40(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "SRC": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_41(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "XXRisk GateXX",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_42(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "risk gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_43(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "RISK GATE",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_44(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "XXheadXX": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_45(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "HEAD": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_46(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "XXbodyXX": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_47(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "BODY": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_48(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "XXThis pattern — extended price + fading momentum — precedes reversals in bull XX"
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_49(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "this pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_50(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "THIS PATTERN — EXTENDED PRICE + FADING MOMENTUM — PRECEDES REVERSALS IN BULL "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_51(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "XXmarkets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; XX"
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_52(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. when adx ≥ 28 (strong trend), rsi > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_53(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "MARKETS. WHEN ADX ≥ 28 (STRONG TREND), RSI > 70 IS A VALID CONTINUATION; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_54(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "XXbelow 28 it is a topping signal. Marginal score blocked.XX"
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_55(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_56(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "BELOW 28 IT IS A TOPPING SIGNAL. MARGINAL SCORE BLOCKED."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_57(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "XXsentimentXX": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_58(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "SENTIMENT": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_59(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "XXnegXX",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_60(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "NEG",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_61(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "XXmetaXX": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

    def xǁOverboughtWeakTrendGateǁapply__mutmut_62(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "META": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )

mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['_mutmut_orig'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_orig # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_1'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_1 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_2'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_2 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_3'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_3 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_4'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_4 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_5'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_5 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_6'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_6 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_7'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_7 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_8'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_8 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_9'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_9 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_10'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_10 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_11'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_11 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_12'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_12 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_13'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_13 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_14'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_14 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_15'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_15 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_16'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_16 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_17'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_17 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_18'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_18 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_19'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_19 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_20'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_20 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_21'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_21 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_22'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_22 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_23'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_23 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_24'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_24 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_25'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_25 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_26'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_26 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_27'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_27 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_28'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_28 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_29'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_29 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_30'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_30 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_31'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_31 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_32'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_32 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_33'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_33 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_34'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_34 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_35'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_35 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_36'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_36 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_37'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_37 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_38'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_38 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_39'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_39 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_40'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_40 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_41'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_41 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_42'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_42 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_43'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_43 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_44'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_44 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_45'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_45 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_46'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_46 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_47'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_47 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_48'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_48 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_49'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_49 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_50'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_50 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_51'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_51 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_52'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_52 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_53'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_53 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_54'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_54 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_55'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_55 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_56'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_56 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_57'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_57 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_58'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_58 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_59'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_59 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_60'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_60 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_61'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_61 # type: ignore # mutmut generated
mutants_xǁOverboughtWeakTrendGateǁapply__mutmut['xǁOverboughtWeakTrendGateǁapply__mutmut_62'] = OverboughtWeakTrendGate.xǁOverboughtWeakTrendGateǁapply__mutmut_62 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut: MutantDict = {}  # type: ignore


class DollarVolumeGate(GateBase):
    """
    Thin dollar-volume confidence haircut + low-ATR regime disclosure.

    Dollar volume < $5M/day → −4pp or −8pp confidence haircut (soft gate,
    not HOLD).  Low-ATR regime annotation fires regardless of action.
    """

    @_mutmut_mutated(mutants_xǁDollarVolumeGateǁapply__mutmut)
    def apply(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_orig(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_1(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = None
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_2(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price / (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_3(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") and 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_4(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get(None) or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_5(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("XXvolumeXX") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_6(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("VOLUME") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_7(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 1) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_8(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 1
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_9(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") or 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_10(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action not in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_11(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("XXBUYXX", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_12(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("buy", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_13(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "XXSELLXX") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_14(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "sell") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_15(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 1 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_16(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 <= dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_17(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol <= 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_18(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5000001:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_19(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = None
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_20(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 9 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_21(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol <= 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_22(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1000001 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_23(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 5
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_24(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = None
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_25(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(None, 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_26(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), None)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_27(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_28(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), )
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_29(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(None, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_30(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, None), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_31(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_32(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_33(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(36.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_34(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence + pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_35(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 2)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_36(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add(None)
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_37(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("XXRisk GateXX")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_38(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("risk gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_39(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("RISK GATE")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_40(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                None
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_41(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "XXsrcXX": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_42(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "SRC": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_43(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "XXRisk GateXX",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_44(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "risk gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_45(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "RISK GATE",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_46(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "XXheadXX": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_47(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "HEAD": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_48(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol * 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_49(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1000001.0:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_50(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "XXbodyXX": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_51(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "BODY": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_52(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol * 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_53(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1000001.0:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_54(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "XXThin liquidity means bid-ask spread costs erode signal edge, and large orders XX"
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_55(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_56(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "THIN LIQUIDITY MEANS BID-ASK SPREAD COSTS ERODE SIGNAL EDGE, AND LARGE ORDERS "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_57(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "XXmove price against the position. Use a smaller position size.XX"
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_58(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_59(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "MOVE PRICE AGAINST THE POSITION. USE A SMALLER POSITION SIZE."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_60(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "XXsentimentXX": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_61(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "SENTIMENT": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_62(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "XXnegXX",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_63(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "NEG",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_64(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "XXmetaXX": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_65(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "META": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_66(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol * 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_67(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1000001.0:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_68(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add(None)
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_69(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("XXRisk GateXX")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_70(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("risk gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_71(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("RISK GATE")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_72(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                None
            )

    def xǁDollarVolumeGateǁapply__mutmut_73(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "XXsrcXX": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_74(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "SRC": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_75(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "XXRisk GateXX",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_76(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "risk gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_77(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "RISK GATE",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_78(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "XXheadXX": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_79(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "HEAD": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_80(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "XXLow-ATR Regime Switch Active — Momentum BypassedXX",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_81(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "low-atr regime switch active — momentum bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_82(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "LOW-ATR REGIME SWITCH ACTIVE — MOMENTUM BYPASSED",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_83(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "XXbodyXX": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_84(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "BODY": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_85(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre / 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_86(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 101:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_87(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "XXTrend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) XX"
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_88(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "trend and momentum scoring families (macd state, ma cross, adx, roc, donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_89(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "TREND AND MOMENTUM SCORING FAMILIES (MACD STATE, MA CROSS, ADX, ROC, DONCHIAN) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_90(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "XXhave been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, XX"
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_91(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. only mean-reversion signals (bollinger, z-score, rsi oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_92(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "HAVE BEEN BYPASSED. ONLY MEAN-REVERSION SIGNALS (BOLLINGER, Z-SCORE, RSI OVERSOLD, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_93(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "XXpivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers.XX"
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_94(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. this reduces false buy signals on ko/pep/t-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_95(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "PIVOT SUPPORT) ARE SCORED. THIS REDUCES FALSE BUY SIGNALS ON KO/PEP/T-STYLE TICKERS."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_96(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "XXsentimentXX": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_97(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "SENTIMENT": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_98(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "XXnegXX" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_99(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "NEG" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_100(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action != "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_101(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "XXHOLDXX" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_102(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "hold" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_103(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "XXposXX",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_104(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "POS",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_105(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "XXmetaXX": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_106(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "META": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_107(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre / 100:.2f}%",
                }
            )

    def xǁDollarVolumeGateǁapply__mutmut_108(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 101:.2f}%",
                }
            )

mutants_xǁDollarVolumeGateǁapply__mutmut['_mutmut_orig'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_1'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_2'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_3'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_4'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_5'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_6'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_7'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_8'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_9'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_10'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_10 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_11'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_11 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_12'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_12 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_13'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_13 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_14'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_14 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_15'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_15 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_16'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_16 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_17'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_17 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_18'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_18 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_19'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_19 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_20'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_20 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_21'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_21 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_22'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_22 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_23'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_23 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_24'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_24 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_25'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_25 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_26'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_26 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_27'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_27 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_28'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_28 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_29'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_29 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_30'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_30 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_31'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_31 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_32'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_32 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_33'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_33 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_34'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_34 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_35'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_35 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_36'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_36 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_37'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_37 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_38'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_38 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_39'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_39 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_40'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_40 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_41'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_41 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_42'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_42 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_43'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_43 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_44'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_44 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_45'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_45 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_46'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_46 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_47'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_47 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_48'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_48 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_49'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_49 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_50'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_50 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_51'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_51 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_52'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_52 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_53'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_53 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_54'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_54 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_55'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_55 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_56'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_56 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_57'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_57 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_58'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_58 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_59'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_59 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_60'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_60 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_61'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_61 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_62'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_62 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_63'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_63 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_64'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_64 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_65'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_65 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_66'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_66 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_67'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_67 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_68'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_68 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_69'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_69 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_70'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_70 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_71'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_71 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_72'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_72 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_73'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_73 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_74'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_74 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_75'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_75 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_76'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_76 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_77'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_77 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_78'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_78 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_79'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_79 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_80'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_80 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_81'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_81 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_82'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_82 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_83'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_83 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_84'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_84 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_85'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_85 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_86'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_86 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_87'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_87 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_88'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_88 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_89'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_89 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_90'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_90 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_91'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_91 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_92'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_92 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_93'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_93 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_94'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_94 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_95'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_95 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_96'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_96 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_97'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_97 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_98'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_98 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_99'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_99 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_100'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_100 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_101'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_101 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_102'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_102 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_103'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_103 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_104'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_104 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_105'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_105 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_106'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_106 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_107'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_107 # type: ignore # mutmut generated
mutants_xǁDollarVolumeGateǁapply__mutmut['xǁDollarVolumeGateǁapply__mutmut_108'] = DollarVolumeGate.xǁDollarVolumeGateǁapply__mutmut_108 # type: ignore # mutmut generated
