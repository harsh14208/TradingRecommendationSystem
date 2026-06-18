"""Leaf helpers and shared constants for the signal engine (BE-1 refactor).

Extracted verbatim from ``signal_engine.py``. This module has no dependency on
``signal_engine`` (leaf of the import DAG): ``signal_engine`` and
``engines/assembler.py`` both import from here.
"""

from datetime import datetime
from datetime import time as dtime

import pytz

_ET = pytz.timezone("America/New_York")


# ── Per-sector MR calibration (alpha-decomp §13-§15 findings) ────────────────
# Keys: sector ETF symbol (from services.sector.SECTOR_MAP).
# vix_min:      minimum VIX at MR entry (§15c). None = no floor.
# hold_days:    recommended hold period for MR bounces (§15b).
# atr_rank_min: minimum ATR%rank for MR entries (§15e). 20 = global default.
# buy_thresh:   minimum composite score for MR BUY signals (§15d). None = global 35.
# Sectors with None calibration = pending §16 research; global defaults apply.
#
# CURVE-FIT WARNING: per-sector thresholds (vix_min, buy_thresh, atr_rank_min)
# are tuned on N=4–24 tickers per sector.  These parameters likely over-fit
# in-sample; treat sector-specific values as soft priors, not hard truths.
# Validate via OOS walk-forward before tightening further.  The global ATR≥20
# gate is the most robust signal; sector-specific overlays add marginal lift.
_SECTOR_MR_CONFIG: dict[str, dict] = {
    # ── Active sectors — global buy_thresh and vix_min (de-curated per audit) ────
    # Per-sector buy_thresh and vix_min were tuned on N=4–24 tickers (§15-§16).
    # Walk-forward OOS (§19/§20/§35a): strict per-sector params passed 1/5 windows;
    # global/relaxed params passed 2/5. Over-curated params destroyed OOS survival.
    # FIX: remove per-sector buy_thresh and vix_min. Keep only structurally-proven
    # gates: atr_rank_min (ATR≥20 is robust across all regimes) and hold_days
    # (already deployed in live recommendedHoldDays — low-harm to leave).
    "XLK": {"vix_min": None, "hold_days": 5, "atr_rank_min": 20, "buy_thresh": None},  # Tech/FAANG
    "XLF": {
        "vix_min": None,
        "hold_days": 7,
        "atr_rank_min": 30,
        "buy_thresh": None,
    },  # Financials (blocked by delivery_gates XLF floor anyway)
    "XLY": {"vix_min": None, "hold_days": 10, "atr_rank_min": 20, "buy_thresh": None},  # Consumer Disc
    "XLP": {
        "vix_min": None,
        "hold_days": 10,
        "atr_rank_min": 20,
        "buy_thresh": None,
    },  # Consumer Staples (blocked by delivery_gates)
    "XLE": {"vix_min": None, "hold_days": 5, "atr_rank_min": 20, "buy_thresh": None},  # Energy
    "XLC": {"vix_min": None, "hold_days": 10, "atr_rank_min": 20, "buy_thresh": None},  # Telecom/Comm
    "XLB": {"vix_min": None, "hold_days": 5, "atr_rank_min": 20, "buy_thresh": None},  # Materials
    "XLU": {
        "vix_min": None,
        "hold_days": 10,
        "atr_rank_min": 20,
        "buy_thresh": 999,
    },  # Utilities — no viable MR edge; blocked
    # ── §16 confirmed-negative sectors — buy_thresh=999 blocks all MR entries ────
    "XLV": {
        "vix_min": None,
        "hold_days": 7,
        "atr_rank_min": 30,
        "buy_thresh": 999,
    },  # Healthcare — §16a Sharpe −0.17; blocked
    "XLI": {
        "vix_min": None,
        "hold_days": 7,
        "atr_rank_min": 20,
        "buy_thresh": 999,
    },  # Industrials — §16a Sharpe −0.48; blocked
    "XLRE": {
        "vix_min": None,
        "hold_days": 5,
        "atr_rank_min": 20,
        "buy_thresh": 999,
    },  # Real Estate — §16a Sharpe −15; blocked
}


def _current_session() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def _score_to_action(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # BUY bar 35 / SELL bar -30 corrects for this.
    # §relax-sweep (2026-06-18): the backtest BUY_THRESH 50→45 relaxation grew N +60%
    # OOS-CLEAN at FLAT Sharpe (0.18) — the entry-score band just below the cutoff carries
    # real, OOS-generalising alpha. The live score scale differs (50+ families inflate it),
    # so this is a conservative proportional mirror: BUY bar 35→32 (~10%, matching 50→45).
    # NOTE: this admits score 32-35 BUYs (conf ~48%, still above the 46% swing floor) and
    # partially relaxes the bullish-bias correction; it does NOT fix live signal-starvation
    # (that bottleneck is the upstream MR-setup hasMr gate, not the score bar). Easily
    # reverted to 35 if live WR in the 32-35 band underperforms.
    if score >= 32:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def _levels(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


_TIMEFRAME = {
    "intraday": ("within today's session (next few hours)", "Today"),
    "swing": ("over the next 2–10 trading days", "2–10 days"),
    "position": ("over the coming weeks to months", "Weeks–months"),
}

# Leveraged and inverse-leveraged ETFs. Scoring blocks that rely on company
# fundamentals (Piotroski, FCF, earnings, insider Form 4, analyst EPS revisions,
# 13F) are bypassed for these tickers because those signals don't apply to
# daily-rebalancing derivative products. Technical and macro signals still run.
# Style is capped at "swing" — holding beyond ~5 days incurs significant
# volatility-decay drag that makes position-style targets unreliable.
_LEVERAGED_ETFS: frozenset[str] = frozenset(
    {
        # ── 3× Bull ──────────────────────────────────────────────────────────────
        "TQQQ",  # ProShares UltraPro QQQ
        "UPRO",  # ProShares UltraPro S&P 500
        "SPXL",  # Direxion Daily S&P 500 Bull 3×
        "SOXL",  # Direxion Daily Semiconductor Bull 3×
        "TECL",  # Direxion Daily Technology Bull 3×
        "FAS",  # Direxion Daily Financial Bull 3×
        "TNA",  # Direxion Daily Small Cap Bull 3×
        "LABU",  # Direxion Daily S&P Biotech Bull 3×
        "WEBL",  # Direxion Daily Dow Jones Internet Bull 3×
        "FNGU",  # MicroSectors FANG+ Index 3× Leveraged
        "NAIL",  # Direxion Daily Homebuilders & Supplies Bull 3×
        "DPST",  # Direxion Daily Regional Banks Bull 3×
        "YINN",  # Direxion Daily FTSE China Bull 3×
        "DRN",  # Direxion Daily Real Estate Bull 3×
        "TMF",  # Direxion Daily 20+ Year Treasury Bull 3×
        "HIBL",  # Direxion Daily S&P 500 High Beta Bull 3×
        "MIDU",  # Direxion Daily Mid Cap Bull 3×
        "WANT",  # Direxion Daily Consumer Discretionary Bull 3×
        "CURE",  # Direxion Daily Healthcare Bull 3×
        "INDL",  # Direxion Daily MSCI India Bull 2×
        "GUSH",  # Direxion Daily S&P Oil & Gas E&P Bull 2×
        "NUGT",  # Direxion Daily Gold Miners Bull 2×
        "JNUG",  # Direxion Daily Junior Gold Miners Bull 2×
        "UCO",  # ProShares Ultra DJ-AIG Crude Oil 2×
        "SSO",  # ProShares Ultra S&P 500 2×
        "QLD",  # ProShares Ultra QQQ 2×
        "ROM",  # ProShares Ultra Technology 2×
        "UWM",  # ProShares Ultra Russell2000 2×
        # ── 3× Bear / Inverse ────────────────────────────────────────────────────
        "SQQQ",  # ProShares UltraPro Short QQQ
        "SPXS",  # Direxion Daily S&P 500 Bear 3×
        "SPXU",  # ProShares UltraPro Short S&P 500
        "SOXS",  # Direxion Daily Semiconductor Bear 3×
        "TECS",  # Direxion Daily Technology Bear 3×
        "FAZ",  # Direxion Daily Financial Bear 3×
        "TZA",  # Direxion Daily Small Cap Bear 3×
        "LABD",  # Direxion Daily S&P Biotech Bear 3×
        "FNGD",  # MicroSectors FANG+ Index −3× Inverse
        "YANG",  # Direxion Daily FTSE China Bear 3×
        "DRV",  # Direxion Daily Real Estate Bear 3×
        "TMV",  # Direxion Daily 20+ Year Treasury Bear 3×
        "HIBS",  # Direxion Daily S&P 500 High Beta Bear 3×
        "SRTY",  # ProShares UltraPro Short Russell2000
        "DRIP",  # Direxion Daily S&P Oil & Gas E&P Bear 2×
        "DUST",  # Direxion Daily Gold Miners Bear 2×
        "JDST",  # Direxion Daily Junior Gold Miners Bear 2×
        "SCO",  # ProShares UltraShort DJ-AIG Crude Oil 2×
        "SDS",  # ProShares UltraShort S&P 500 2×
        "QID",  # ProShares UltraShort QQQ 2×
        "REW",  # ProShares UltraShort Technology 2×
        "TWM",  # ProShares UltraShort Russell2000 2×
    }
)


def _make_plain_english(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }
