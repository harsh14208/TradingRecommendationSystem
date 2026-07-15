"""
Fundamental quality gates extracted from generate_signal() and _assemble_signal().

Functional API (for gates inside generate_signal — they modify accumulated score):
    apply_short_interest_velocity(score, info)
        -> (new_score, cards, sources)  [§52]
    apply_quality_screens(score, info, fundamentals, is_lev_etf, action)
        -> (new_score, cards, sources)  [§50 Piotroski, §51 ForwardPE]

GateBase class (for gate inside _assemble_signal — can change action):
    FundamentalValueTrapGate
        Revenue declining >20% YoY AND FCF yield < −5% → HOLD.  Live only (not
        point-in-time); excluded from backtest_technicals.py to avoid look-ahead bias.

Public API summary:
    apply_short_interest_velocity(score, info) -> (score, cards, sources)
    apply_quality_screens(score, info, fundamentals, is_lev_etf, action) -> (score, cards, sources)
    FundamentalValueTrapGate — GateBase; use in a GatePipeline inside _assemble_signal
"""

from __future__ import annotations

from .base import GateBase, SignalContext


# ── Functional API — used in generate_signal() ────────────────────────────────


def apply_short_interest_velocity(
    score: float,
    info: dict,
) -> tuple[float, list[dict], set[str]]:
    """
    §52 Short Interest Velocity — Squeeze Signal.

    Rapidly decreasing SI while oversold = shorts losing conviction + covering
    pressure amplifies the MR snap-back. Increasing SI = informed bear conviction.
    Data: yfinance sharesShort (current) vs sharesShortPriorMonth (prior).

    Returns:
        (new_score, cards, sources)
    """
    cards: list[dict] = []
    new_sources: set[str] = set()

    si_cur = info.get("shares_short")
    si_prior = info.get("shares_short_prior")
    if si_cur is None or si_prior is None or si_prior <= 0:
        return score, cards, new_sources

    si_vel = (si_cur - si_prior) / si_prior
    if si_vel < -0.15 and score >= 0:
        score += 4
        new_sources.add("Short Interest")
        cards.append(
            {
                "src": "Short Interest",
                "head": f"Short Covering Acceleration ({si_vel * 100:+.0f}% MoM) — Squeeze Incoming (§52)",
                "body": (
                    f"Short interest fell {abs(si_vel) * 100:.0f}% vs prior reporting period "
                    f"({int(si_prior):,} → {int(si_cur):,} shares). "
                    "Rapidly decreasing SI while oversold = shorts losing conviction and covering into "
                    "weakness. Their covering adds buy pressure on top of the fundamental reversal. "
                    "Boehmer et al. (2008): SI velocity is predictive; covering + oversold = prime MR setup. "
                    "Confidence +4pp (§52)."
                ),
                "sentiment": "pos",
                "meta": f"si_vel={si_vel:+.2f} si_cur={int(si_cur):,} si_prior={int(si_prior):,} §52",
            }
        )
    elif si_vel > 0.20 and score >= 0:
        score -= 5
        new_sources.add("Short Interest")
        cards.append(
            {
                "src": "Short Interest",
                "head": f"Shorts Adding Aggressively (+{si_vel * 100:.0f}% MoM) — Bear Conviction (§52)",
                "body": (
                    f"Short interest rose {si_vel * 100:.0f}% vs prior reporting period "
                    f"({int(si_prior):,} → {int(si_cur):,} shares). "
                    "Rapidly increasing SI signals informed institutional conviction in the bearish "
                    "thesis — short sellers are not panicking, they are adding. "
                    "This fundamentally undermines the MR bounce thesis. Confidence −5pp (§52)."
                ),
                "sentiment": "neg",
                "meta": f"si_vel={si_vel:+.2f} si_cur={int(si_cur):,} si_prior={int(si_prior):,} §52",
            }
        )

    return score, cards, new_sources


# apply_insider_clustering (§73) REMOVED 2026-07-14 (dead-code audit):
# 0 fires in 87,982 all-time signals — unique_buyers never >= 2 from the
# EDGAR Form-4 feed on this universe. edgar.py still computes insider data
# for the net-flow penalties in signal_engine.py.


def apply_quality_screens(
    score: float,
    info: dict,
    fundamentals: dict,
    is_lev_etf: bool,
    action: str,
) -> tuple[float, list[dict], set[str]]:
    """
    Composite fundamental quality screens applied at the end of the scoring pass.

    Includes:
      §50 Piotroski F-Score     — financial strength 0-9 scale
      §51 Forward PE            — value trap vs genuinely cheap filter
      (§74 Beneish removed 2026-07-14; §76 Altman removed 2026-06-03)

    Args:
        score:        current composite score (to be adjusted)
        info:         ticker info dict (from yfinance)
        fundamentals: fundamentals dict (from get_fundamentals())
        is_lev_etf:   True for leveraged/inverse ETFs (screens skipped)
        action:       current preliminary action ("BUY"/"SELL"/"HOLD")

    Returns:
        (new_score, cards, sources)
    """
    cards: list[dict] = []
    new_sources: set[str] = set()

    # ── §50 Piotroski F-Score ─────────────────────────────────────────────────
    f_score = fundamentals.get("piotroski_f")
    if f_score is not None:
        new_sources.add("Fundamentals")
        if f_score >= 7:
            score += 12
            cards.append(
                {
                    "src": "Fundamentals",
                    "head": f"Piotroski F-Score {f_score}/9 — Financially Strong",
                    "body": (
                        f"Piotroski F-Score of {f_score}/9: company scores strongly across profitability, "
                        "leverage, and efficiency tests. High-F-score stocks outperform low-F-score stocks "
                        "by 7–9% annually in academic studies."
                    ),
                    "sentiment": "pos",
                    "meta": f"F-Score: {f_score}/9",
                }
            )
        elif f_score >= 5:
            score += 5
        elif f_score <= 2:
            score -= 10
            cards.append(
                {
                    "src": "Fundamentals",
                    "head": f"Piotroski F-Score {f_score}/9 — Financially Weak",
                    "body": (
                        f"Piotroski F-Score of only {f_score}/9: poor profitability, increasing leverage, "
                        "and deteriorating efficiency. Low-F-score stocks are academic short candidates."
                    ),
                    "sentiment": "neg",
                    "meta": f"F-Score: {f_score}/9",
                }
            )
        elif f_score <= 4:
            score -= 4

    # §74 Beneish M-Score — REMOVED 2026-07-14 (gate audit)
    # §85-1 live audit on the corrected 725-signal book: fired N=70 with WR
    # 22.9% (ΔWR −24.2pp vs 47.0% baseline) — 24× past the pre-registered
    # removal threshold (ΔWR<−1pp @ N≥30). Firing was concentrated on the
    # now-blocked SELL/intraday cohorts; on the surviving BUY position/swing
    # book it fired on ZERO signals — no benefit either way. Quarterly
    # yfinance financials are also not point-in-time (untestable in backtest),
    # and accounting quality is a multi-quarter thesis, not a 10d MR one.
    # fundamentals.py still computes beneish_m for research/display.

    # §76 Altman Z-Score — REMOVED 2026-06-03
    # EDGAR validation showed 79/106 IS tickers (74%) are permanently below Z'<1.23
    # (the distress threshold) due to structural reasons unrelated to bankruptcy:
    #   - Financial companies (banks): high leverage is business model, not distress
    #   - Tech companies: high goodwill/intangibles deflate book equity
    #   - Service/retail: asset-light models have low fixed assets vs liabilities
    # The formula (Altman 1968) was calibrated on manufacturing companies.
    # Applying it to the IS universe was penalising ~80% of signals by -15 pts,
    # contributing to the IS/live WR gap. Removed after backtest_edgar.py confirmed
    # standalone Altman hurts IS Sharpe: N 230→79, Sh 0.20→0.16 (-0.03).

    # §51 Forward PE Value Trap Filter — REMOVED 2026-07-14 (gate audit)
    # 24 fires in 87,982 all-time signals (cheap-side: 0) and N<3 in the
    # resolved book — inert. Ledger confidence was "Low — valuation multiples
    # don't predict a 10d bounce" (the AQR value premium is a 12-month effect)
    # and the modifier was never validatable point-in-time.

    return score, cards, new_sources


# ── GateBase class — used in _assemble_signal() ───────────────────────────────


class FundamentalValueTrapGate(GateBase):
    """
    Fundamental Value-Trap Gate — gates on fundamentally deteriorating companies.

    MR bounces on companies with BOTH revenue declining >20% YoY AND FCF yield
    below −5% are value traps — the stock is oversold for a real reason.

    DATA WARNING: revenue_growth and freeCashflow come from yfinance .info,
    which reflects current-day values, NOT point-in-time data. Applying this
    gate inside a historical backtest constitutes look-ahead bias. This gate
    is intentionally excluded from backtest_technicals.py for this reason.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY" or ctx.is_lev_etf:
            return
        rev_grow = ctx.info.get("revenue_growth")
        fcf_abs = ctx.info.get("freeCashflow")
        mktcap = ctx.info.get("market_cap")
        fcf_yield = (fcf_abs / mktcap * 100) if (fcf_abs is not None and mktcap and mktcap > 0) else None
        rev_trap = rev_grow is not None and rev_grow < -0.20
        fcf_trap = fcf_yield is not None and fcf_yield < -5.0
        if not (rev_trap and fcf_trap):
            return
        ctx.action = "HOLD"
        ctx.sources.add("Risk Gate")
        rev_str = f"{rev_grow * 100:+.1f}%" if rev_grow is not None else "—"
        fcf_str = f"{fcf_yield:+.1f}%" if fcf_yield is not None else "—"
        ctx.rationale.append(
            {
                "src": "Risk Gate",
                "head": f"Value-Trap Gate — Revenue {rev_str} YoY, FCF Yield {fcf_str}",
                "body": (
                    f"Revenue declining {rev_str} year-over-year with FCF yield of {fcf_str}. "
                    "Stocks that are technically oversold AND fundamentally deteriorating "
                    "are value traps — the technical signal reflects a real business problem, "
                    "not a temporary dip. MR bounces on cash-burning revenue-decliners "
                    "have significantly lower win rates. Signal gated to HOLD."
                ),
                "sentiment": "neg",
                "meta": f"rev_growth={rev_str} | fcf_yield={fcf_str} | gate=value_trap",
            }
        )
