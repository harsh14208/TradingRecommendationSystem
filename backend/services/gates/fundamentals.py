"""
Fundamental quality gates extracted from generate_signal() and _assemble_signal().

Functional API (for gates inside generate_signal — they modify accumulated score):
    apply_short_interest_velocity(score, info)
        -> (new_score, cards, sources)  [§52]
    apply_insider_clustering(score, insider, is_lev_etf)
        -> (new_score, cards, sources)  [§73]
    apply_quality_screens(score, info, fundamentals, is_lev_etf, action)
        -> (new_score, cards, sources)  [§50 Piotroski, §74 Beneish, §76 Altman, §51 ForwardPE]

GateBase class (for gate inside _assemble_signal — can change action):
    FundamentalValueTrapGate
        Revenue declining >20% YoY AND FCF yield < −5% → HOLD.  Live only (not
        point-in-time); excluded from backtest_technicals.py to avoid look-ahead bias.

Public API summary:
    apply_short_interest_velocity(score, info) -> (score, cards, sources)
    apply_insider_clustering(score, insider, is_lev_etf) -> (score, cards, sources)
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


def apply_insider_clustering(
    score: float,
    insider: dict,
    is_lev_etf: bool,
) -> tuple[float, list[dict], set[str]]:
    """
    §73 Insider Clustering — multiple distinct insider buyers.

    Multiple distinct insiders buying simultaneously signals consensus on
    undervaluation — far stronger than a single large-holder transaction
    that may be routine compensation or scheduled diversification.

    Returns:
        (new_score, cards, sources)
    """
    cards: list[dict] = []
    new_sources: set[str] = set()

    if not insider or is_lev_etf:
        return score, cards, new_sources

    unique_buyers = insider.get("unique_buyers", 0) or 0
    if unique_buyers >= 2:
        bonus = 8 if unique_buyers >= 3 else 5
        score += bonus
        new_sources.add("SEC EDGAR")
        cards.append(
            {
                "src": "SEC EDGAR",
                "head": f"Insider Cluster Buy — {unique_buyers} Distinct Insiders",
                "body": (
                    f"{unique_buyers} distinct insiders filed Form 4 purchases in the last 30 days. "
                    "Cluster buys (multiple independent decision-makers) carry far higher "
                    "predictive power than single-insider transactions. "
                    "Academic research: insider cluster buys outperform by ~12% in the "
                    "6 months following the filings."
                ),
                "sentiment": "pos",
                "meta": f"unique_insider_buyers={unique_buyers} bonus=+{bonus}",
            }
        )

    return score, cards, new_sources


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
      §74 Beneish M-Score       — earnings manipulation screen
      §76 Altman Z-Score        — financial distress screen
      §51 Forward PE            — value trap vs genuinely cheap filter

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

    # ── §74 Beneish M-Score — Earnings Manipulation Screen ───────────────────
    beneish_m = fundamentals.get("beneish_m")
    if beneish_m is not None and not is_lev_etf:
        new_sources.add("Fundamentals")
        if beneish_m > -1.78:
            score -= 12
            cards.append(
                {
                    "src": "Fundamentals",
                    "head": f"Beneish M-Score {beneish_m:.2f} — Possible Earnings Manipulation",
                    "body": (
                        f"Beneish M-Score of {beneish_m:.2f} exceeds the −1.78 manipulation "
                        "threshold. The 8-variable model (Beneish 1999, 76% accuracy) flags "
                        "abnormal accruals, receivables growth, and asset quality deterioration "
                        "consistent with earnings inflation. WorldCom, Enron, and many major "
                        "frauds were detected by this model pre-collapse. Reduce sizing significantly."
                    ),
                    "sentiment": "neg",
                    "meta": f"M-Score={beneish_m:.2f} (threshold=-1.78)",
                }
            )

    # ── §76 Altman Z-Score — Financial Distress Screen ───────────────────────
    altman_z = fundamentals.get("altman_z")
    if altman_z is not None and not is_lev_etf:
        new_sources.add("Fundamentals")
        if altman_z < 1.81:
            score -= 15
            cards.append(
                {
                    "src": "Fundamentals",
                    "head": f"Altman Z-Score {altman_z:.2f} — Financial Distress Zone",
                    "body": (
                        f"Altman Z-Score of {altman_z:.2f} is in the distress zone (< 1.81). "
                        "Altman (1968): Z < 1.81 correctly predicted 94% of bankruptcies "
                        "within 2 years. Mean-reversion entries on distress stocks fail "
                        "catastrophically — the dip is structural, not a temporary dislocation."
                    ),
                    "sentiment": "neg",
                    "meta": f"Z-Score={altman_z:.2f} (<1.81 = distress)",
                }
            )
        elif altman_z < 2.67:
            score -= 4
            cards.append(
                {
                    "src": "Fundamentals",
                    "head": f"Altman Z-Score {altman_z:.2f} — Grey Zone",
                    "body": (
                        f"Altman Z-Score of {altman_z:.2f} falls in the grey zone (1.81–2.67). "
                        "Financial health is uncertain — elevated distress risk not fully "
                        "priced into the equity."
                    ),
                    "sentiment": "neg",
                    "meta": f"Z-Score={altman_z:.2f} (1.81-2.67 = grey zone)",
                }
            )

    # ── §51 Forward PE Value Trap Filter ─────────────────────────────────────
    fwd_pe = info.get("forward_pe")
    if fwd_pe is not None and not is_lev_etf and action == "BUY":
        new_sources.add("Fundamentals")
        if fwd_pe > 30:
            score -= 5
            cards.append(
                {
                    "src": "Fundamentals",
                    "head": f"Forward PE Value Trap Warning ({fwd_pe:.1f}×)",
                    "body": (
                        f"Forward PE of {fwd_pe:.1f}× — expensive valuation on a declining stock. "
                        "AQR research shows high-PE oversold stocks frequently fail to revert: "
                        "the market is correctly pricing deteriorating fundamentals, not panic. "
                        "Confidence reduced −5pp (§51 value trap filter)."
                    ),
                    "sentiment": "neg",
                    "meta": f"forward_pe={fwd_pe:.1f} value_trap=high §51",
                }
            )
        elif fwd_pe < 15:
            score += 3
            cards.append(
                {
                    "src": "Fundamentals",
                    "head": f"Genuinely Cheap — Forward PE {fwd_pe:.1f}×",
                    "body": (
                        f"Forward PE of {fwd_pe:.1f}× confirms this is not a value trap: "
                        "the stock is oversold AND priced cheaply relative to future earnings. "
                        "Low-PE MR setups have historically stronger reversion: "
                        "valuation provides fundamental support for the bounce. Confidence +3pp (§51)."
                    ),
                    "sentiment": "pos",
                    "meta": f"forward_pe={fwd_pe:.1f} value_confirmed §51",
                }
            )

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
