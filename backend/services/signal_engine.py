"""
Signal generation engine.

Per-scan market-wide context (Fear & Greed, Macro) is fetched ONCE by the
scanner and passed in via `market_ctx`.  Per-ticker data (technicals, news,
EDGAR insider activity) is fetched concurrently for each ticker.
"""
import asyncio
import logging
from datetime import datetime, time as dtime
from typing import NamedTuple, Optional
import numpy as _np
import pytz

log = logging.getLogger("signal.trade.engine")


class _TickerData(NamedTuple):
    df: "pd.DataFrame"
    info: dict
    news: list
    scraped_news: list
    insider: list
    analyst_recs: list
    earnings_cal: object
    earnings_surp: object
    opt_flow: object
    fundamentals: dict
    social: object
    trends: object
    congress: object
    df_1h: object
    massive_sigs: object
    sector_rs: object


from services.google_trends import get_google_trends
from services.quiverquant import get_congress_signal
from services.dark_pool import get_massive_advanced_signals
from services.signal_scoring import (
    score_oscillators,
    score_macd,
    score_ema_cross,
    score_obv_adx,
    score_moving_averages,
)

_ET = pytz.timezone("America/New_York")

# Per-ticker analyst target cache with TTL: {ticker: {"mean": float, "count": int, "ts": float}}
_analyst_cache: dict[str, dict] = {}
_ANALYST_CACHE_TTL = 3600  # 1 hour — invalidate stale entries

def _current_session() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):  return "pre"
    if dtime(9, 30) <= t < dtime(16, 0): return "regular"
    if dtime(16, 0) <= t < dtime(20, 0): return "after"
    return "closed"

import pandas as pd

from services.earnings import get_earnings_calendar, get_earnings_surprise
from services.edgar import get_insider_activity
from services.fundamentals import get_fundamentals
from services.market_data import get_history, get_info, get_extended_hours_data
from services.news import get_analyst_recs, get_company_news
from services.news_scraper import get_scraped_news
from services.options import get_options_flow, score_options
from services.sector import get_sector_relative_strength
from services.social import get_social_sentiment
from services.technicals import calculate_indicators


def _score_to_action(score: float, agreement: int = 0) -> tuple[str, float]:
    import math
    abs_s = abs(score)
    # Sigmoid calibrated against DB win rates (May 2026 calibration data).
    # Asymptote lowered from 92% → 84%: empirical data shows that signals above
    # 80% confidence have historically yielded only 50-67% actual win rates — a
    # 15-38pp overconfidence gap. Capping at 84% brings the scale closer to reality.
    # score=25→~55%, score=40→~63%, score=60→~71%, score=90→~80%, score=150→~84%
    agreement_bonus = min(4.0, agreement * 0.35)  # slightly reduced agreement bonus
    raw = 40.0 + 44.0 * (1.0 - math.exp(-abs_s / 65.0)) + agreement_bonus
    confidence = round(min(72.0, raw), 1)   # hard ceiling: 72% max — empirical data shows 75-84% signals win at only 48-50%
    # Thresholds are asymmetric by design: the scoring system has a structural bullish
    # bias (~+13 pts) from analyst consensus, large-cap fundamentals, and bull-market
    # technicals. Raising the BUY bar to 35 and lowering the SELL bar to -18 corrects
    # for this: empirical BUY win rate is 42% (below coin-flip) vs SELL at 48%.
    if score >= 35:
        return "BUY",  confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(40.0, min(55.0, confidence))


def _levels(price: float, atr: float, action: str):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    # Dynamic ATR multipliers based on ATR-to-price ratio (volatility proxy).
    # High vol → tighter stops to limit $ loss; low vol → wider stops to avoid noise shakeout.
    atr_pct = atr / price if price > 0 else 0.02
    if atr_pct > 0.025:    # high volatility  (ATR > 2.5% of price)
        stop_mult, tgt_mult = 2.0, 2.5
    elif atr_pct < 0.010:  # low volatility   (ATR < 1.0% of price)
        stop_mult, tgt_mult = 3.0, 4.0
    else:                  # normal volatility
        stop_mult, tgt_mult = 2.0, 3.0
    stop   = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult  * atr, 2) if action == "BUY" else round(entry - tgt_mult  * atr, 2)
    risk   = abs(entry - stop)
    reward = abs(target - entry)
    rr     = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


_TIMEFRAME = {
    "intraday": ("within today's session (next few hours)",   "Today"),
    "swing":    ("over the next 2–10 trading days",           "2–10 days"),
    "position": ("over the coming weeks to months",           "Weeks–months"),
}

# Leveraged and inverse-leveraged ETFs. Scoring blocks that rely on company
# fundamentals (Piotroski, FCF, earnings, insider Form 4, analyst EPS revisions,
# 13F) are bypassed for these tickers because those signals don't apply to
# daily-rebalancing derivative products. Technical and macro signals still run.
# Style is capped at "swing" — holding beyond ~5 days incurs significant
# volatility-decay drag that makes position-style targets unreliable.
_LEVERAGED_ETFS: frozenset[str] = frozenset({
    # ── 3× Bull ──────────────────────────────────────────────────────────────
    "TQQQ",  # ProShares UltraPro QQQ
    "UPRO",  # ProShares UltraPro S&P 500
    "SPXL",  # Direxion Daily S&P 500 Bull 3×
    "SOXL",  # Direxion Daily Semiconductor Bull 3×
    "TECL",  # Direxion Daily Technology Bull 3×
    "FAS",   # Direxion Daily Financial Bull 3×
    "TNA",   # Direxion Daily Small Cap Bull 3×
    "LABU",  # Direxion Daily S&P Biotech Bull 3×
    "WEBL",  # Direxion Daily Dow Jones Internet Bull 3×
    "FNGU",  # MicroSectors FANG+ Index 3× Leveraged
    "NAIL",  # Direxion Daily Homebuilders & Supplies Bull 3×
    "DPST",  # Direxion Daily Regional Banks Bull 3×
    "YINN",  # Direxion Daily FTSE China Bull 3×
    "DRN",   # Direxion Daily Real Estate Bull 3×
    "TMF",   # Direxion Daily 20+ Year Treasury Bull 3×
    "HIBL",  # Direxion Daily S&P 500 High Beta Bull 3×
    "MIDU",  # Direxion Daily Mid Cap Bull 3×
    "WANT",  # Direxion Daily Consumer Discretionary Bull 3×
    "CURE",  # Direxion Daily Healthcare Bull 3×
    "INDL",  # Direxion Daily MSCI India Bull 2×
    "GUSH",  # Direxion Daily S&P Oil & Gas E&P Bull 2×
    "NUGT",  # Direxion Daily Gold Miners Bull 2×
    "JNUG",  # Direxion Daily Junior Gold Miners Bull 2×
    "UCO",   # ProShares Ultra DJ-AIG Crude Oil 2×
    "SSO",   # ProShares Ultra S&P 500 2×
    "QLD",   # ProShares Ultra QQQ 2×
    "ROM",   # ProShares Ultra Technology 2×
    "UWM",   # ProShares Ultra Russell2000 2×
    # ── 3× Bear / Inverse ────────────────────────────────────────────────────
    "SQQQ",  # ProShares UltraPro Short QQQ
    "SPXS",  # Direxion Daily S&P 500 Bear 3×
    "SPXU",  # ProShares UltraPro Short S&P 500
    "SOXS",  # Direxion Daily Semiconductor Bear 3×
    "TECS",  # Direxion Daily Technology Bear 3×
    "FAZ",   # Direxion Daily Financial Bear 3×
    "TZA",   # Direxion Daily Small Cap Bear 3×
    "LABD",  # Direxion Daily S&P Biotech Bear 3×
    "FNGD",  # MicroSectors FANG+ Index −3× Inverse
    "YANG",  # Direxion Daily FTSE China Bear 3×
    "DRV",   # Direxion Daily Real Estate Bear 3×
    "TMV",   # Direxion Daily 20+ Year Treasury Bear 3×
    "HIBS",  # Direxion Daily S&P 500 High Beta Bear 3×
    "SRTY",  # ProShares UltraPro Short Russell2000
    "DRIP",  # Direxion Daily S&P Oil & Gas E&P Bear 2×
    "DUST",  # Direxion Daily Gold Miners Bear 2×
    "JDST",  # Direxion Daily Junior Gold Miners Bear 2×
    "SCO",   # ProShares UltraShort DJ-AIG Crude Oil 2×
    "SDS",   # ProShares UltraShort S&P 500 2×
    "QID",   # ProShares UltraShort QQQ 2×
    "REW",   # ProShares UltraShort Technology 2×
    "TWM",   # ProShares UltraShort Russell2000 2×
})

def _make_plain_english(action: str, ticker: str, style: str, rationale: list,
                         confidence: float, entry, stop, target) -> dict:
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
        "summary":    summary,
        "timeframe":  tf_long,
        "tf_short":   tf_short,
        "top_reasons": top,
    }


async def _fetch_ticker_data(
    ticker: str,
    prefetched_df: Optional[pd.DataFrame],
    prefetched_info: Optional[dict],
) -> Optional[_TickerData]:
    """
    Fetch all per-ticker data concurrently.
    Returns a _TickerData namedtuple or None if df is invalid.
    """
    if prefetched_df is not None:
        df   = prefetched_df
        info = prefetched_info or {}
        _raw = await asyncio.gather(
            get_company_news(ticker, days=7),
            get_scraped_news(ticker, (prefetched_info or {}).get("company", ticker), days=7),
            get_insider_activity(ticker, days=30),
            get_analyst_recs(ticker),
            get_earnings_calendar(ticker),
            get_earnings_surprise(ticker),
            get_options_flow(ticker),
            get_fundamentals(ticker),
            get_social_sentiment(ticker),
            get_google_trends(ticker),
            get_congress_signal(ticker),
            get_history(ticker, period="5d", interval="1h"),
            get_extended_hours_data(ticker),
            return_exceptions=True,
        )
        news, scraped_news, insider, analyst_recs, earnings_cal, earnings_surp, opt_flow, fundamentals, social, trends, congress, df_1h, massive_sigs = [
            None if isinstance(r, BaseException) else r for r in _raw
        ]
        sector_rs = await get_sector_relative_strength(ticker, df)
    else:
        _raw = await asyncio.gather(
            get_history(ticker, period="1y", interval="1d"),
            get_info(ticker),
            get_company_news(ticker, days=7),
            get_scraped_news(ticker, "", days=7),
            get_insider_activity(ticker, days=30),
            get_analyst_recs(ticker),
            get_earnings_calendar(ticker),
            get_earnings_surprise(ticker),
            get_options_flow(ticker),
            get_fundamentals(ticker),
            get_social_sentiment(ticker),
            get_google_trends(ticker),
            get_congress_signal(ticker),
            get_history(ticker, period="5d", interval="1h"),
            get_extended_hours_data(ticker),
            return_exceptions=True,
        )
        df, info, news, scraped_news, insider, analyst_recs, earnings_cal, earnings_surp, opt_flow, fundamentals, social, trends, congress, df_1h, massive_sigs = [
            None if isinstance(r, BaseException) else r for r in _raw
        ]
        sector_rs = await get_sector_relative_strength(ticker, df)

    if df is None or len(df) < 30:
        return None

    return _TickerData(
        df=df, info=info, news=news, scraped_news=scraped_news,
        insider=insider, analyst_recs=analyst_recs,
        earnings_cal=earnings_cal, earnings_surp=earnings_surp,
        opt_flow=opt_flow, fundamentals=fundamentals,
        social=social, trends=trends, congress=congress,
        df_1h=df_1h, massive_sigs=massive_sigs, sector_rs=sector_rs,
    )


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
    avg_sent: float,
    price: float,
    atr: float,
    market_ctx: Optional[dict],
    earnings_cal: dict,
    sector_rs: Optional[dict],
    days_to_earnings: Optional[int],
) -> Optional[dict]:
    """
    Apply risk gates, calibrate confidence, derive style, and build
    the final signal dict. Returns None if action is forced to HOLD
    and confidence < threshold.
    """
    # Derive macro/regime variables from market_ctx inline.
    macro        = (market_ctx or {}).get("macro") or {}
    vix          = macro.get("vix")
    sp500_trend  = macro.get("sp500_trend")

    # ── Assemble final signal ───────────────────────────────────────
    # Enforce any blackout/gate that set _force_hold=True mid-scoring.
    # score=0 alone is not sufficient because subsequent signal blocks
    # (e.g. macro, options, institutional) can re-inflate it back above
    # the ±25 BUY/SELL threshold. The flag survives all subsequent scoring.
    if _force_hold:
        score = 0.0  # ensure no stale residual from post-zero signals

    # Agreement count excludes meta-signals that are artifacts of the scoring
    # machinery rather than independent evidence (Risk Gate, Orthogonalization,
    # Signal Cluster, Backtest). Counting them inflated the agreement bonus for
    # any signal with many firing post-processing checks.
    _META_SRCS = {"Risk Gate", "Orthogonalization", "Signal Cluster", "Backtest"}
    agree_sent = "pos" if score > 0 else "neg"
    agreement  = sum(1 for r in rationale
                     if r.get("sentiment") == agree_sent
                     and r.get("src") not in _META_SRCS)
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
        rationale.append({"src": "Risk Gate",
            "head": f"Chronic Loser Exclusion — Win Rate {ticker_wr*100:.0f}%",
            "body": (f"{ticker} has a historical win rate below 45%. BUY signals on "
                     "persistent structural underperformers are mathematically "
                     "negative expected value. Signal excluded."),
            "sentiment": "neg",
            "meta": f"Win rate {ticker_wr*100:.0f}% < 45%"})

    # ── True Orthogonality Minimum ──────────────────────────────────────
    _core_families = {"Technical", "Options", "13F", "SEC EDGAR", "Fundamentals", "Macro", "Dark Pool", "Short Interest", "Analyst", "Social"}
    _active_families = len([s for s in sources if s in _core_families])
    if action == "BUY" and _active_families < 3 and score < 50:
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append({"src": "Risk Gate",
            "head": f"Orthogonality Gate — Only {_active_families}/3 Source Families",
            "body": ("A reliable BUY signal requires convergence from at least 3 independent "
                     "data families (e.g., Technical + Options + Fundamentals). Correlated "
                     "indicators within the same family do not provide enough independent edge."),
            "sentiment": "neg",
            "meta": f"Active families: {_active_families} < 3"})

    # ── RVOL >= 1.2 BUY Prerequisite ────────────────────────────────────
    volume = tech.get("volume", 0)
    avg_vol = tech.get("avg_volume", 1) or 1
    vol_ratio = volume / avg_vol
    is_oversold_play = tech.get("rsi") is not None and tech.get("rsi") < 35
    if action == "BUY" and vol_ratio < 1.2 and not is_oversold_play and score < 50:
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append({"src": "Risk Gate",
            "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}×)",
            "body": ("BUY signals require Relative Volume (RVOL) ≥ 1.2 to confirm "
                     "institutional participation, unless deeply oversold. Volume is "
                     "too low to confirm the breakout."),
            "sentiment": "neg",
            "meta": f"RVOL {vol_ratio:.1f}× < 1.2"})

    # ── Dollar-volume minimum gate ────────────────────────────────────────
    # A signal on a thinly-traded stock ($price × volume < $5M/day) is unreliable:
    # bid-ask spreads dominate, institutional algorithms don't participate, and
    # a single large order moves price. Reduce confidence rather than hard-gate
    # so the signal still appears with a clear warning.
    _dollar_vol = price * (tech.get("volume") or 0) if price else 0
    if action in ("BUY", "SELL") and _dollar_vol > 0 and _dollar_vol < 5_000_000:
        _dv_pen = 8 if _dollar_vol < 1_000_000 else 4
        confidence = round(max(35.0, confidence - _dv_pen), 1)
        sources.add("Risk Gate")
        rationale.append({"src": "Risk Gate",
            "head": f"Thin Dollar Volume — ${_dollar_vol/1e6:.1f}M/day ({_dv_pen}pp confidence haircut)",
            "body": (f"Daily dollar volume of ${_dollar_vol/1e6:.1f}M is below the $5M threshold. "
                     "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                     "move price against the position. Use a smaller position size."),
            "sentiment": "neg",
            "meta": f"dollar_vol=${_dollar_vol/1e6:.1f}M | penalty={_dv_pen}pp"})

    # Annotate the low-ATR regime switch if it was active this signal
    if _is_low_atr:
        sources.add("Risk Gate")
        rationale.append({"src": "Risk Gate",
            "head": f"Low-ATR Regime Switch Active — Momentum Bypassed",
            "body": (f"ATR is only {_atr_pct_pre*100:.2f}% of price — structurally range-bound stock. "
                     "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                     "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                     "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."),
            "sentiment": "neg" if action == "HOLD" else "pos",
            "meta": f"low_atr_regime=True atr_pct={_atr_pct_pre*100:.2f}%"})

    # ── Low-volatility stock BUY gate ───────────────────────────────────
    # Stocks with ATR < 0.8% of price (KO, PEP, T, JNJ, WFC, etc.) have
    # tight, mean-reverting price action where technical breakout signals
    # fail at much higher rates. Validation: ALL such tickers had 0% win
    # rates despite 70-85% confidence. Require a stronger score (≥35) and
    # a non-negative macro environment before issuing a BUY.
    atr_pct = atr / price if price > 0 else 0.02
    _macro_score_now = macro.get("macro_score", 0) if macro else 0
    if (action == "BUY"
            and atr_pct < 0.008          # ATR < 0.8% of price = low-vol stock
            and (score < 35 or _macro_score_now < 0)):
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append({"src": "Risk Gate",
            "head": f"Low-Vol Stock Gate — ATR {atr_pct*100:.2f}% (Need Score ≥35 + Macro ≥0)",
            "body": (f"ATR is only {atr_pct*100:.2f}% of price — low-volatility defensive stock. "
                     "Technical signals on tight-range stocks have historically near-zero win rates "
                     "in this system. Requiring score ≥35 AND non-negative macro before issuing BUY."),
            "sentiment": "neg",
            "meta": f"ATR%: {atr_pct*100:.2f}% | Score: {score:.1f} | Macro: {_macro_score_now:+.0f}"})

    # ── Defensive-ticker BUY gate ────────────────────────────────────────
    # Tickers that showed 0% BUY win rate across ≥3 resolved signals in the
    # May 2026 validation (n=529). These span low-vol defensives, banks, and
    # consumer staples where momentum signals structurally misfire.
    # The ATR gate above catches KO/PEP/T; this gate covers higher-ATR names
    # (BAC, C, USB, PNC, TGT, etc.) that slip past the ATR threshold.
    _DEFENSIVE_BUY_BLOCK = {
        "BAC", "KO", "PEP", "T", "NEE", "PG", "USB", "PNC", "C", "TGT",
        "AIG", "WM", "MCO", "TT", "DE", "TJX",
    }
    if action == "BUY" and ticker in _DEFENSIVE_BUY_BLOCK:
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append({"src": "Risk Gate",
            "head": f"Defensive-Ticker BUY Gate — {ticker} 0% BUY Win Rate (n≥3)",
            "body": (f"{ticker} has shown a 0% BUY win rate across validated signals. "
                     "Momentum and technical breakout signals structurally misfire on this "
                     "ticker — the price action is mean-reverting or macro-driven rather than "
                     "trend-following. BUY gated to HOLD until a re-validation shows positive edge."),
            "sentiment": "neg",
            "meta": f"Ticker: {ticker} | Validation: 0% BUY win rate | Gate: defensive_ticker_block"})

    # ── Leveraged / inverse-leveraged ETF disclosure ─────────────────────
    # Always fire for any leveraged ETF signal, regardless of action.
    # Fundamentals, earnings, and insider scoring are already bypassed upstream;
    # this card surfaces the decay risk to the user and confirms the bypass.
    if ticker in _LEVERAGED_ETFS:
        _lev_bull = ticker not in {
            "SQQQ","SPXS","SPXU","SOXS","TECS","FAZ","TZA","LABD",
            "FNGD","YANG","DRV","TMV","HIBS","SRTY","DRIP","DUST",
            "JDST","SCO","SDS","QID","REW","TWM",
        }
        _mult = "3×" if ticker not in {"GUSH","DRIP","NUGT","DUST","JNUG","JDST",
                                        "UCO","SCO","SSO","SDS","QLD","QID",
                                        "ROM","REW","UWM","TWM","INDL"} else "2×"
        _dir  = "Bull" if _lev_bull else "Bear (Inverse)"
        sources.add("Risk Gate")
        rationale.append({"src": "Risk Gate",
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
            "meta": f"type=leveraged_etf | mult={_mult} | dir={'bull' if _lev_bull else 'bear'}"})

    # ── Market-cap tier modifier ──────────────────────────────────────────
    # Mega-caps ($500B+) have wall-to-wall analyst coverage, crowded positioning,
    # and slower momentum decay — momentum signals are less differentiated.
    # Small-caps (<$2B) add a volatility premium notice to the rationale.
    _mktcap = info.get("market_cap")
    if _mktcap and action in ("BUY", "SELL") and not _is_lev_etf:
        if _mktcap >= 500_000_000_000:          # mega-cap ≥ $500B
            confidence = round(max(35.0, confidence - 2), 1)
            sources.add("Risk Gate")
            rationale.append({"src": "Risk Gate",
                "head": f"Mega-Cap Crowding Haircut (${_mktcap/1e12:.1f}T)",
                "body": (f"Market cap of ${_mktcap/1e12:.1f}T means this stock has wall-to-wall analyst "
                         "coverage, crowded institutional positioning, and slower-decaying momentum. "
                         "Edge is smaller vs mid/small cap — confidence haircut applied."),
                "sentiment": "neg",
                "meta": f"mktcap=${_mktcap/1e9:.0f}B | tier=mega | adj=-2pp"})
        elif _mktcap < 2_000_000_000:           # small-cap < $2B
            sources.add("Risk Gate")
            rationale.append({"src": "Risk Gate",
                "head": f"Small-Cap Volatility Notice (${_mktcap/1e9:.1f}B)",
                "body": (f"Market cap of ${_mktcap/1e9:.1f}B — small-cap territory. Higher volatility, "
                         "wider bid-ask spreads, and lower liquidity amplify both gains and losses. "
                         "Size position accordingly (suggest ½ of normal allocation)."),
                "sentiment": "neg",
                "meta": f"mktcap=${_mktcap/1e9:.1f}B | tier=small"})

    # ── Bear + high-VIX hard BUY gate ───────────────────────────────────
    # The regime multiplier (×0.82) lowers the score but the BUY threshold
    # stays at ±35, so marginal signals still cross into BUY. In a confirmed
    # downtrend + elevated VIX, require score ≥42 before allowing a BUY.
    # SELL signals in bear + high-VIX are NOT gated — the trend supports them.
    if (action == "BUY"
            and sp500_trend == "down"
            and vix is not None and vix > 25
            and score < 42):
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append({"src": "Risk Gate",
            "head": f"Bear+VIX Gate — BUY Blocked (Score {score:.0f} < 42, VIX {vix:.0f})",
            "body": (f"S&P 500 is in a downtrend (below 50-DMA) and VIX is {vix:.0f}. "
                     "Marginal BUY signals (score <42) have historically failed in this "
                     "regime. Signal gated to HOLD — wait for a stronger setup."),
            "sentiment": "neg",
            "meta": f"SPX trend: down | VIX: {vix:.0f} | Score: {score:.1f}"})

    # ── BUY:SELL saturation circuit breaker ─────────────────────────────
    # When the rolling 7-day BUY:SELL ratio exceeds 4:1, the system is over-
    # optimistic. Raise the effective BUY threshold to 42 so only high-conviction
    # signals survive. SELL signals are never suppressed by this gate — the
    # circuit breaker only corrects the bullish bias, not the bearish direction.
    if (action == "BUY"
            and (market_ctx or {}).get("buy_saturated")
            and score < 42):
        action = "HOLD"
        _ratio = (market_ctx or {}).get("buy_sell_ratio", 4.0)
        sources.add("Risk Gate")
        rationale.append({"src": "Risk Gate",
            "head": f"BUY Saturation Gate — 7d BUY:SELL Ratio {_ratio:.1f}:1 (>4.0)",
            "body": (f"The system has generated {_ratio:.1f} BUY signals for every SELL signal "
                     "over the past 7 days — a sign of structural over-optimism. "
                     "Marginal BUY signals (score <42) are suppressed until the ratio normalises below 4.0."),
            "sentiment": "neg",
            "meta": f"7d BUY:SELL = {_ratio:.1f}:1 | Score: {score:.1f}"})

    # ── Broad market breadth BUY gate ───────────────────────────────────
    # When >70% of S&P 500 stocks are above their 200-DMA, the technical
    # baseline is already elevated: Supertrend, price structure, and momentum
    # signals all default positive, adding ~+15 pts before any real edge fires.
    # Require a stronger score (≥42) to confirm genuine alpha beyond the tide.
    # SELL signals are never gated here — breadth strength doesn't protect shorts.
    if action == "BUY" and score < 42:
        _breadth_ctx = (market_ctx or {}).get("breadth") or {}
        _pct_200     = _breadth_ctx.get("pct_above_200d", 0) or 0
        if _pct_200 > 70:
            action = "HOLD"
            sources.add("Risk Gate")
            rationale.append({"src": "Risk Gate",
                "head": f"Broad Market Breadth Gate — {_pct_200:.0f}% Above 200-DMA (Score {score:.0f} < 42)",
                "body": (f"{_pct_200:.0f}% of S&P 500 stocks are above their 200-day average — "
                         "technical baselines (Supertrend, momentum, price structure) are uniformly "
                         "elevated, adding ~15 pts of structural noise to every BUY signal. "
                         "Requiring score ≥42 ensures only genuine alpha clears the bar."),
                "sentiment": "neg",
                "meta": f"Breadth: {_pct_200:.0f}% >200d | Score: {score:.1f}"})

    # Apply combined post-processing confidence penalty (warning signals + low volume)
    if total_confidence_penalty > 0 and action in ("BUY", "SELL"):
        confidence = round(max(35.0, confidence * (1 - total_confidence_penalty)), 1)

    # ── Macro Contradiction Cap ──────────────────────────────────────────
    # A BUY signal at ≥70% confidence while macro is meaningfully bearish
    # (macro_score < −3) is a contradiction: the stock-level technicals say
    # buy, but the macro environment says sell everything. Cap confidence at
    # 65% to reflect the elevated failure rate of these cross-current setups.
    # Symmetric: a SELL at ≥70% confidence with a bullish macro is capped too.
    if action in ("BUY", "SELL") and confidence >= 70:
        _m_score = macro.get("macro_score", 0) if macro else 0
        _m_contradiction = (_m_score < -3 and action == "BUY") or (_m_score > 3 and action == "SELL")
        if _m_contradiction:
            confidence = round(min(confidence, 65.0), 1)
            rationale.append({"src": "Macro",
                "head": f"Macro Contradiction — Confidence Capped at 65%",
                "body": (f"Macro score is {_m_score:+.0f} ({'bearish' if _m_score < 0 else 'bullish'}), "
                         f"contradicting the {action} signal. High-confidence {action} signals "
                         "in a contradictory macro environment have significantly lower win rates. "
                         "Confidence capped at 65% until macro aligns."),
                "sentiment": "neg",
                "meta": f"Macro score: {_m_score:+.0f} | Action: {action}"})

    # ── Macro News Sentiment BUY Cap ─────────────────────────────────────
    # When SPY/QQQ ETF news is strongly negative AND VIX > 20, cap all BUY signals at 65%.
    if action == "BUY":
        _news_sent = (macro or {}).get("macro_news_sentiment")
        _vix_now   = (macro or {}).get("vix") or 0
        if _news_sent is not None and _news_sent < -0.3 and _vix_now > 20:
            _new_cap = 65.0
            if confidence > _new_cap:
                confidence = round(min(confidence, _new_cap), 1)
                rationale.append({"src": "Macro",
                    "head": f"Macro News Negative (SPY/QQQ) — BUY Cap {_new_cap:.0f}%",
                    "body": (f"ETF-level news sentiment is {_news_sent:+.2f} (negative) with VIX at {_vix_now:.1f}. "
                             "Broad-market news fear combined with elevated volatility caps BUY confidence "
                             "until macro news normalises."),
                    "sentiment": "neg",
                    "meta": f"macro_news_sentiment={_news_sent:+.2f} vix={_vix_now:.1f}"})

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
                vix_note = (f" (VIX {vix:.0f} → {vix_dampener:.0%} dampener applied)"
                            if vix is not None and vix_dampener < 1.0 else "")
                rationale.append({"src": "Backtest",
                    "head": f"Historical {action} Win Rate {win_rate*100:.0f}% — Confidence {direction_lbl}",
                    "body": (f"Past {action} signals have a {win_rate*100:.0f}% win rate. "
                             f"Confidence adjusted {'+' if wr_delta>0 else ''}{wr_delta:.1f} points.{vix_note}"),
                    "sentiment": "pos" if wr_delta > 0 else "neg",
                    "meta": f"{action} win rate: {win_rate*100:.0f}%"})

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
            rationale.append({"src": "Backtest",
                "head": f"{_streak}-Signal Loss Streak — Confidence Reduced",
                "body": (f"{ticker} has lost on {_streak} consecutive resolved signals. "
                         f"Confidence reduced by {_streak_penalty:.0f}pp until a winning signal breaks the streak."),
                "sentiment": "neg",
                "meta": f"Loss streak: {_streak} | Penalty: -{_streak_penalty:.0f}pp"})

    # ── VIX Hard Confidence Floor ────────────────────────────────────────
    # Panic regimes (VIX > 30) mechanically increase realized volatility and
    # the correlation of all risk assets — directional edge deteriorates sharply.
    # Signals below 75% confidence have statistically poor win rates in these
    # conditions: "catching falling knives." Hard-gate to HOLD.
    if vix is not None and vix > 30 and action in ("BUY", "SELL") and confidence < 75:
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append({
            "src":  "Risk Gate",
            "head": f"VIX Regime Floor — {confidence:.0f}% Below 75% Threshold (VIX {vix:.0f})",
            "body": (
                f"VIX at {vix:.0f} signals an active panic regime (threshold: 30). "
                "In elevated-VIX environments, {}-confidence signals have historically poor "
                "win rates — technical patterns break down as correlations spike and "
                "liquidity thin outs. Signal gated to HOLD until VIX normalises below 30."
            ).format(f"{confidence:.0f}%"),
            "sentiment": "neg",
            "meta": f"VIX = {vix:.0f} | Min confidence gate: 75% | Actual: {confidence:.0f}%",
        })

    # ── Style derivation from rationale composition ───────────────────────
    # Intraday wins over all — a fresh RSI extreme or Bollinger touch is a
    # short-term reversal play regardless of structural context.
    # Position only fires when genuinely structural signals (strong fundamentals,
    # confirmed institutional buying) dominate with NO short-term overrides.
    # Everything else defaults to swing.
    _heads_str = " || ".join(r.get("head", "") for r in rationale)

    _is_intraday = any(kw in _heads_str for kw in [
        "RSI Oversold", "RSI Overbought", "RSI Weakening", "RSI Elevated",
        "Bollinger Band Touch",
        "Bullish RSI Divergence", "Bearish RSI Divergence",
        "Stochastic Bullish Cross", "Stochastic Bearish Cross",
        "Williams %R Oversold", "Williams %R Overbought",
        "CCI Oversold", "CCI Overbought",
    ])

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
    _is_position = (not _is_intraday) and any(kw in _heads_str for kw in [
        "F-Score 7", "F-Score 8", "F-Score 9",   # only high-quality F-scores
        "Strong FCF Yield",
        "Active Share Buyback",
        "Institutional Conviction Rising",        # QoQ trend required
        "Institutional Conviction Falling",
    ])

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

    entry, stop, target, rr = _levels(price, atr, action)

    # ── Risk-Free Rate Yield Dampener ────────────────────────────────────
    # Every equity trade competes against the risk-free rate. If the signal's
    # projected return (entry → target) doesn't clear a meaningful risk premium
    # over Treasuries, the trade has negative expected value on a Sharpe basis.
    t10y_rate = ((market_ctx or {}).get("macro") or {}).get("t10y")
    if t10y_rate and t10y_rate > 2.0 and action == "BUY" and entry and target and entry > 0:
        projected_pct = abs(target - entry) / entry * 100
        # Growth / high-beta sectors require a larger premium (investors face more risk)
        sector_etf_key = (sector_rs or {}).get("sector_etf", "")
        high_beta = sector_etf_key in {"XLK", "XLC", "XLY", "XLB"}
        required_premium = 3.5 if high_beta else 2.0   # pp above risk-free
        excess = projected_pct - t10y_rate - required_premium

        if excess < -required_premium:
            # Projected return doesn't even beat the risk-free rate outright
            confidence = round(max(35.0, confidence - 14), 1)
            sources.add("Macro")
            rationale.append({"src": "Macro",
                "head": f"Risk-Adjusted Return Negative vs Bonds ({projected_pct:.1f}% target vs {t10y_rate:.1f}% risk-free)",
                "body": (
                    f"Signal target implies a {projected_pct:.1f}% return — below the "
                    f"{t10y_rate:.1f}% 10-Year Treasury yield. Holding risk-free bonds "
                    "dominates this trade on a Sharpe basis. Confidence reduced significantly."
                ),
                "sentiment": "neg",
                "meta": f"Projected {projected_pct:.1f}% | 10Y {t10y_rate:.1f}% | Premium: {excess:.1f}pp"})
        elif excess < 0:
            # Return beats risk-free but misses the required risk premium
            penalty = round(abs(excess) / required_premium * 8, 1)
            confidence = round(max(35.0, confidence - penalty), 1)
            sources.add("Macro")
            rationale.append({"src": "Macro",
                "head": f"Thin Risk Premium Over Bonds ({projected_pct:.1f}% vs {t10y_rate:.1f}% + {required_premium:.1f}pp premium)",
                "body": (
                    f"Projected return of {projected_pct:.1f}% only clears the risk-free rate "
                    f"by {projected_pct - t10y_rate:.1f}pp — below the {required_premium:.1f}pp "
                    "risk premium required for this sector's beta. "
                    "The marginal risk-adjusted case is weak."
                ),
                "sentiment": "neg",
                "meta": f"Excess return: {projected_pct - t10y_rate:.1f}pp | Required: {required_premium:.1f}pp"})
        elif excess > required_premium * 2:
            # Generous excess return — genuine edge over risk-free
            boost = min(5.0, excess * 0.3)
            confidence = round(min(72.0, confidence + boost), 1)
            sources.add("Macro")
            rationale.append({"src": "Macro",
                "head": f"Strong Risk-Adjusted Return ({projected_pct:.1f}% target, {excess:.1f}pp above hurdle)",
                "body": (
                    f"Signal target of {projected_pct:.1f}% clears the {t10y_rate:.1f}% risk-free rate "
                    f"by {projected_pct - t10y_rate:.1f}pp — {excess:.1f}pp above the "
                    f"{required_premium:.1f}pp required premium. Genuine Sharpe-positive edge."
                ),
                "sentiment": "pos",
                "meta": f"Excess return: {excess:.1f}pp above hurdle | 10Y: {t10y_rate:.1f}%"})
    plain_english = _make_plain_english(action, ticker, style, rationale, confidence, entry, stop, target)

    headline = (
        f"{rationale[0]['head']} · {len(rationale)} signals agree"
        if len(rationale) > 1
        else (rationale[0]["head"] if rationale else f"{action} signal detected")
    )

    # ── Platt-style empirical calibration ───────────────────────────────
    # Blend raw model confidence toward the observed win rate in the same
    # 5pp bin from historical resolved signals. Blend factor = n_samples/30,
    # capped at 0.80 — low-data bins stay close to the model; well-sampled
    # bins shift strongly toward reality. Refit weekly alongside factor mining.
    if action in ("BUY", "SELL"):
        from services.calibration import apply_calibration
        cal_map = (market_ctx or {}).get("calibration_map", {})
        if cal_map:
            pre_cal = confidence
            confidence, _bin = apply_calibration(confidence, action, cal_map)
            if _bin and abs(confidence - pre_cal) >= 2:
                _emp_wr   = round(_bin["win_rate"] * 100, 1)
                _n        = _bin["n"]
                _blend    = round(_bin["blend"] * 100)
                _gap      = round(_emp_wr - pre_cal, 1)
                _bin_lo   = (int(pre_cal) // 5) * 5
                _bin_hi   = _bin_lo + 5
                _dir      = "DOWN" if confidence < pre_cal else "UP"
                _over     = confidence < pre_cal  # True = was overconfident

                rationale.append({"src": "Backtest",
                    "head": (
                        f"Calibration {_dir}: {pre_cal:.0f}% → {confidence:.0f}%"
                        f" ({'overconfident' if _over else 'underconfident'} by {abs(_gap):.0f}pp)"
                    ),
                    "body": (
                        f"The model assigned {pre_cal:.0f}% confidence, but {_n} resolved "
                        f"{action} signals in the {_bin_lo}–{_bin_hi}% band have an actual "
                        f"win rate of {_emp_wr:.0f}% — a {abs(_gap):.0f}pp "
                        f"{'overconfidence' if _over else 'underconfidence'} gap. "
                        f"Confidence blended {_blend}% toward the empirical rate "
                        f"(blend weight = {_blend}% because n={_n} resolved signals in this band). "
                        + (
                            f"The model is systematically {'over' if _over else 'under'}confident "
                            f"at this score level — likely because "
                            + ("multiple correlated technical signals agree but the macro or sector context "
                               "limits real-world follow-through."
                               if _over else
                               "the model's scoring underweights how reliably these signals perform "
                               "in practice.")
                        )
                    ),
                    "sentiment": "pos" if not _over else "neg",
                    "meta": (
                        f"Bin {_bin_lo}–{_bin_hi}% | "
                        f"Empirical WR: {_emp_wr:.0f}% | "
                        f"n={_n} signals | "
                        f"Blend: {_blend}% empirical + {100-_blend}% model"
                    ),
                })

    # ── XGBoost confidence adjustment ────────────────────────────────────
    # Applies a multiplicative adjustment (0.75–1.25×) derived from the
    # XGBoost model trained on resolved signals. Runs after Platt calibration
    # so the ML layer refines — not replaces — empirical calibration.
    # Gracefully skipped when the model file is absent or xgboost is not installed.
    try:
        from services.signal_ml import get_model, adjust_confidence as _ml_adjust
        _ml_model = get_model()
        if _ml_model is not None and action in ("BUY", "SELL"):
            _sig_dict_for_ml = {
                "confidence": confidence,
                "sentiment":  avg_sent,
                "sources":    list(sources),
                "rationale":  rationale,
                "action":     action,
                "style":      style,
                "rr":         rr,
                "entry":      entry,
                "stop":       stop,
                "target":     target,
                "price":      price,
                "session":    _current_session(),
            }
            confidence = _ml_adjust(_sig_dict_for_ml, _ml_model)
    except Exception:
        pass

    # Hard final ceiling — ensures no post-processing step (adaptive weights,
    # yield dampener, factor mining boost) can push confidence above 72%.
    # Empirical calibration (May 2026, n=529): bands 75-84% win at only 48-50%,
    # and 65-70% wins at only 56% — the model's real ceiling of predictive power.
    if action in ("BUY", "SELL"):
        confidence = round(min(72.0, max(35.0, confidence)), 1)

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
        if win_rate_hist is not None and confidence - win_rate_hist * 100 > 20:
            confidence_warning = True
        elif total_confidence_penalty >= 0.15:
            confidence_warning = True

    return {
        "ticker":              ticker,
        "company":             info.get("company", ticker),
        "action":              action,
        "confidence":          confidence,
        "confidence_warning":  confidence_warning,
        "price":               price,
        "change":              tech.get("change",     0),
        "changePct":           tech.get("change_pct", 0),
        "entry":               entry,
        "stop":                stop,
        "target":              target,
        "rr":                  rr,
        "headline":            headline,
        "sentiment":           round(avg_sent, 2),
        "style":               style,
        "sources":             sorted(sources),
        "rationale":           rationale,
        "ts":                  datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session":             _current_session(),
        "daysToEarnings":      days_to_earnings,
        "nextEarningsDate":    earnings_cal.get("next_earnings_date"),
        "sectorEtf":           sector_rs["sector_etf"] if sector_rs else None,
        "rsVsSector":          sector_rs["rs_vs_sector"] if sector_rs else None,
        "plain_english":       plain_english,
        "beta":                info.get("beta"),
    }


def _compute_1h_techs(df_1h) -> dict:
    """CPU-bound 1H technical indicator computation — runs in a thread pool."""
    c1h = df_1h["Close"].astype(float)
    # RSI(14) on 1H
    _d  = c1h.diff()
    _ag = _d.clip(lower=0).ewm(com=13, adjust=False).mean()
    _al = (-_d).clip(lower=0).ewm(com=13, adjust=False).mean()
    rsi_1h = float((100 - 100 / (1 + _ag / _al.replace(0, _np.nan))).iloc[-1])
    # MACD on 1H
    _macd_1h = float(
        (c1h.ewm(span=12, adjust=False).mean()
         - c1h.ewm(span=26, adjust=False).mean()).iloc[-1])
    # Price vs EMA20 on 1H
    _above_ema_1h = float(c1h.iloc[-1]) > float(
        c1h.ewm(span=20, adjust=False).mean().iloc[-1])
    return {"rsi_1h": rsi_1h, "macd_1h": _macd_1h, "above_ema_1h": _above_ema_1h}


async def generate_signal(
    ticker: str,
    market_ctx: Optional[dict] = None,
    prefetched_df: Optional[pd.DataFrame] = None,
    prefetched_info: Optional[dict] = None,
) -> Optional[dict]:
    try:
        # Use pre-fetched batch data when available; fall back to individual fetches.
        _fetched = await _fetch_ticker_data(ticker, prefetched_df, prefetched_info)
        if _fetched is None:
            return None
        df, info, news, scraped_news, insider, analyst_recs, earnings_cal, earnings_surp, opt_flow, fundamentals, social, trends, congress, df_1h, massive_sigs, sector_rs = _fetched
        ext_hours = massive_sigs  # unified: both branches fetch get_extended_hours_data

        # Leveraged/inverse ETFs: company fundamentals, earnings, and insider
        # signals are meaningless — bypass them before any worker or scoring block
        # uses them. Technical, macro, and options signals still score normally.
        _is_lev_etf = ticker in _LEVERAGED_ETFS
        if _is_lev_etf:
            fundamentals = {}
            earnings_cal  = {}
            earnings_surp = {}
            insider       = {}
            analyst_recs  = {}
            congress      = {}

        tech = calculate_indicators(df)
        if not tech or tech.get("price") is None:
            return None

        # ── Launch scoring workers concurrently (Event-Driven Microservices) ──────
        # Workers run in parallel while TA scoring executes below.
        # Each worker has its own timeout + circuit breaker — a slow Polygon call
        # or a rate-limited Finnhub response does not block RSI/MACD scoring.
        # Results are merged after the TA scoring phase completes.
        _price_now = tech.get("price", 0) or 0
        try:
            from services.signal_workers import (
                news_worker, fundamentals_worker, options_worker,
                institutional_worker, sentiment_worker,
            )
            _worker_task = asyncio.ensure_future(asyncio.gather(
                news_worker(ticker, news, scraped_news),
                fundamentals_worker(ticker, fundamentals, market_ctx, _price_now),
                options_worker(ticker, opt_flow, massive_sigs),
                institutional_worker(ticker, insider, market_ctx),
                sentiment_worker(ticker, social, trends, congress),
                return_exceptions=True,
            ))
        except Exception:
            _worker_task = None

        # ── Weekly trend (resample daily → weekly, no extra API call) ───────
        weekly_trend = 0  # +1 uptrend, -1 downtrend, 0 neutral
        try:
            weekly = df["Close"].resample("W").last().dropna()
            if len(weekly) >= 20:
                w_sma20 = float(weekly.iloc[-20:].mean())
                w_price = float(weekly.iloc[-1])
                if w_price > w_sma20 * 1.02:
                    weekly_trend = 1
                elif w_price < w_sma20 * 0.98:
                    weekly_trend = -1
        except Exception:
            pass

        # ── Weekly OHLCV Trend Strength from Polygon ─────────────────────────
        # 26 weekly bars → close vs weekly SMA(13).
        # Above for 8+ of last 10 weeks = confirmed medium-term uptrend (+4pts).
        # Below for 8+ of last 10 weeks = confirmed downtrend (-4pts).
        _weekly_ohlcv_score = 0
        try:
            from services.polygon_client import get_polygon_weekly_bars
            _wdf = await get_polygon_weekly_bars(ticker, weeks=26)
            if _wdf is not None and len(_wdf) >= 14:
                _wclose = _wdf["Close"].values
                _wsma13 = float(_np.mean(_wclose[-13:]))
                _last10  = _wclose[-10:]
                _weeks_above = int(sum(1 for c in _last10 if c > _wsma13))
                _weeks_below = 10 - _weeks_above
                if _weeks_above >= 8:
                    _weekly_ohlcv_score = 4
                elif _weeks_below >= 8:
                    _weekly_ohlcv_score = -4
        except Exception:
            pass

        price    = tech["price"]
        atr      = tech.get("atr") or price * 0.02
        rsi      = tech.get("rsi")
        hist     = tech.get("macd_hist",      0) or 0
        hist_p   = tech.get("macd_hist_prev", 0) or 0
        sma20    = tech.get("sma20")
        sma50    = tech.get("sma50")
        sma200   = tech.get("sma200")

        # ── Polygon pre-computed indicators (validation + RSI blend) ───────────
        _poly_ind: dict = {}
        _poly_weekly: dict = {}
        try:
            from services.polygon_indicators import (
                get_indicators, get_weekly_indicators, blend_rsi, polygon_sma_crossover
            )
            _poly_ind, _poly_weekly = await asyncio.gather(
                get_indicators(ticker),
                get_weekly_indicators(ticker),
            )
            if _poly_ind:
                rsi = blend_rsi(rsi, _poly_ind.get("rsi"))
                if not sma200 and _poly_ind.get("sma200"):
                    sma200 = _poly_ind["sma200"]
                if not sma50 and _poly_ind.get("sma50"):
                    sma50 = _poly_ind["sma50"]
                if not sma20 and _poly_ind.get("sma20"):
                    sma20 = _poly_ind["sma20"]
                poly_hist = _poly_ind.get("macd_hist", 0) or 0
                if hist != 0 and poly_hist != 0 and (hist > 0) == (poly_hist > 0):
                    hist = hist * 1.1
        except Exception:
            pass
        bb_upper = tech.get("bb_upper")
        bb_lower = tech.get("bb_lower")
        volume   = tech.get("volume",     0)
        avg_vol  = tech.get("avg_volume", 1) or 1

        score     = 0.0
        rationale = []
        sources   = {"Technical"}
        dominant  = "macd"
        vol_confidence_penalty     = 0.0
        rs_confidence_penalty      = 0.0
        insider_confidence_penalty = 0.0
        # Hard-HOLD flag — set by earnings/sector blackouts mid-scoring.
        # score=0 alone is NOT sufficient because subsequent signal blocks
        # (macro, options, institutional, etc.) can re-inflate it above 25.
        # This flag is checked at final assembly and forces HOLD unconditionally.
        _force_hold = False

        # ── Low-ATR Regime Switch ─────────────────────────────────────────────
        # Stocks with ATR < 1.0% of price (KO, PEP, T, JNJ, WFC, etc.) are
        # structurally range-bound. Breakout momentum logic fails on these (0%
        # win rate in May 2026 validation). When low-ATR is detected, bypass the
        # trend and momentum scoring families entirely; route scoring to
        # mean-reversion only (Z-Score, Bollinger, pivot). Oscillators (RSI
        # oversold/overbought) still apply as they measure magnitude, not trend.
        _atr_pct_pre = (atr / price) if price > 0 else 0.02
        _is_low_atr  = _atr_pct_pre < 0.010   # ATR < 1.0% of price

        # Oscillator group (RSI/Stoch/WR/CCI/MFI): correlated — cap at ±28.
        osc_score = 0.0
        # Moving-average family (SMA200/SMA50/Golden-Death Cross): same underlying
        # price, cap at ±22 to prevent triple-counting "above all MAs" scenarios.
        ma_score = 0.0
        # Trend-continuation family (MACD non-cross / EMA state / ADX): all
        # measure whether the existing trend is strengthening — cap at ±18.
        trend_score = 0.0
        # Volume family (OBV structural trend): cap at ±16.
        volume_score = 0.0
        # Mean-reversion extremes (BB touch, pivot, Z-score, BB squeeze): all ask
        # "is price statistically stretched?" — cap at ±18.
        mean_rev_score = 0.0
        # Momentum family (ROC10, streak, Donchian, price structure, gap, RVOL):
        # all confirm the same directional price momentum — cap at ±18.
        momentum_score = 0.0
        # Analyst consensus family (price target, rec consensus, Finnhub recs):
        # all read "what sell-side thinks" — highly correlated — cap at ±18.
        analyst_score = 0.0
        # Options/P-C ratio family (contrarian bias + directional confirmation):
        # both derived from the same P/C ratio — cap at ±12.
        pc_score = 0.0
        # Social/retail sentiment (StockTwits, WSB, Google Trends): all measure
        # retail crowd direction — cap at ±10.
        soc_bucket = 0.0
        # Ichimoku system (TK cross, cloud, chikou): three signals from one
        # indicator system — cap at ±14.
        ichimoku_score = 0.0

        # ── Oscillators: RSI, Stochastic, Williams %R, CCI ────────────────────
        _osc_delta, _osc_rat, _osc_dom = score_oscillators(tech, rsi)
        osc_score += _osc_delta
        rationale.extend(_osc_rat)
        if _osc_dom:
            dominant = _osc_dom

        # ── MACD crossover + continuation ───────────────────────────────────
        # Crossover (_macd_sd) and continuation state (_macd_td) both derive from
        # the same MACD indicator. Both now route into trend_score so the family
        # cap (±22) governs the total MACD contribution, not just the state part.
        _macd_sd, _macd_td, _macd_rat, _macd_dom = score_macd(hist, hist_p)
        trend_score += _macd_sd
        trend_score += _macd_td
        rationale.extend(_macd_rat)
        if _macd_dom:
            dominant = _macd_dom

        # ── EMA 8/21 Short-term Momentum ────────────────────────────────────
        # EMA cross (_ema_sd) is another trend signal correlated with MACD cross —
        # route into trend_score so both share the family cap.
        _ema_sd, _ema_td, _ema_rat = score_ema_cross(tech)
        trend_score += _ema_sd
        trend_score += _ema_td
        rationale.extend(_ema_rat)

        # ── OBV + ADX ───────────────────────────────────────────────────────
        _vol_delta, _adx_td, _vol_rat = score_obv_adx(tech, score)
        volume_score += _vol_delta
        trend_score  += _adx_td
        rationale.extend(_vol_rat)

        # Apply volume and trend-continuation family caps before MA section.
        # Low-ATR regime: skip trend_score and volume_score — breakout / momentum
        # signals are structurally invalid on tight-range defensive stocks.
        # Mean-reversion signals (Bollinger, Z-score, pivot) still score normally.
        if not _is_low_atr:
            score += max(-22, min(22, volume_score)) * 0.85
            # trend cap raised ±18→±22: MACD cross + EMA cross now route here
            # alongside MACD state + ADX, so the combined potential is higher.
            score += max(-22, min(22, trend_score)) * 0.85
        # Reset volume_score so the CMF section (lines ~2790+) fills it fresh.
        # Without this reset, CMF contributions accumulate in volume_score but
        # never get applied to score — a silent bug where CMF rationale cards
        # appeared in the UI but had zero effect on the actual signal score.
        volume_score = 0.0

        # ── Moving averages — all routed to ma_score family bucket ─────────
        # SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
        # Cap the family at ±22 to prevent triple-counting "above all MAs".
        # Low-ATR: skip MA family — moving-average breakout logic invalid on range-bound stocks.
        _ma_delta, _ma_rat = score_moving_averages(price, sma50, sma200, _poly_ind or {})
        ma_score += _ma_delta
        rationale.extend(_ma_rat)

        if not _is_low_atr:
            score += max(-22, min(22, ma_score))

        # ── Bollinger Bands ─────────────────────────────────────────────
        if bb_lower and bb_upper:
            if price <= bb_lower * 1.005:
                mean_rev_score += 10
                rationale.append({"src": "Technical", "head": "Lower Bollinger Band Touch",
                    "body": "Price at lower BB — potential mean-reversion bounce.",
                    "sentiment": "pos", "meta": f"BB Lower ${bb_lower:.2f}"})
            elif price >= bb_upper * 0.995:
                mean_rev_score -= 10
                rationale.append({"src": "Technical", "head": "Upper Bollinger Band Touch",
                    "body": "Price at upper BB — potential overextension.",
                    "sentiment": "neg", "meta": f"BB Upper ${bb_upper:.2f}"})

        # ── 52-Week High / Low Proximity ────────────────────────────────
        # 52W high = momentum/breakout signal → momentum_score bucket.
        # 52W low  = mean-reversion/deep-value signal → mean_rev_score bucket.
        wk52_h = tech.get("week52_high")
        wk52_l = tech.get("week52_low")
        if wk52_h and wk52_l and wk52_h > wk52_l:
            pct_from_high = (price - wk52_h) / wk52_h * 100
            pct_from_low  = (price - wk52_l) / wk52_l * 100
            if pct_from_high > -3:
                momentum_score += 10
                rationale.append({"src": "Technical", "head": "Near 52-Week High — Breakout Zone",
                    "body": f"Price is within 3% of its 52-week high (${wk52_h:.2f}). Potential breakout; strong momentum.",
                    "sentiment": "pos", "meta": f"52W High ${wk52_h:.2f} | {pct_from_high:.1f}% away"})
            elif pct_from_low < 10:
                mean_rev_score += 8
                rationale.append({"src": "Technical", "head": "Near 52-Week Low — Deep Value Zone",
                    "body": f"Price is within 10% of its 52-week low (${wk52_l:.2f}). Oversold on annual basis.",
                    "sentiment": "pos", "meta": f"52W Low ${wk52_l:.2f} | +{pct_from_low:.1f}% from bottom"})

        # ── Candlestick Pattern ─────────────────────────────────────────
        pattern = tech.get("candle_pattern")
        if pattern == "hammer":
            score += 12
            rationale.append({"src": "Technical", "head": "Hammer Candle — Bullish Reversal",
                "body": "Hammer pattern detected: buyers rejected lower prices, closing near the high. Classic reversal signal.",
                "sentiment": "pos", "meta": "Candlestick: Hammer"})
        elif pattern == "bullish_engulfing":
            score += 12
            rationale.append({"src": "Technical", "head": "Bullish Engulfing Pattern",
                "body": "Today's candle fully engulfs yesterday's bearish candle. Strong buyer conviction.",
                "sentiment": "pos", "meta": "Candlestick: Bullish Engulfing"})
        elif pattern == "shooting_star":
            score -= 12
            rationale.append({"src": "Technical", "head": "Shooting Star — Bearish Reversal",
                "body": "Shooting star detected: sellers rejected higher prices, closing near the low. Distribution signal.",
                "sentiment": "neg", "meta": "Candlestick: Shooting Star"})
        elif pattern == "bearish_engulfing":
            score -= 12
            rationale.append({"src": "Technical", "head": "Bearish Engulfing Pattern",
                "body": "Today's candle fully engulfs yesterday's bullish candle. Strong seller conviction.",
                "sentiment": "neg", "meta": "Candlestick: Bearish Engulfing"})
        elif pattern == "doji":
            # Doji = indecision; only noteworthy in context of a strong prior trend
            if score > 15:
                score -= 5
                rationale.append({"src": "Technical", "head": "Doji — Momentum Stalling",
                    "body": "Doji candle after bullish run. Buyers and sellers at equilibrium — potential reversal.",
                    "sentiment": "neg", "meta": "Candlestick: Doji"})
            elif score < -15:
                score += 5
                rationale.append({"src": "Technical", "head": "Doji — Bearish Momentum Stalling",
                    "body": "Doji candle after bearish run. Potential exhaustion of selling pressure.",
                    "sentiment": "pos", "meta": "Candlestick: Doji"})

        # ── Pivot Point Support / Resistance ────────────────────────────
        pivot    = tech.get("pivot")
        pivot_r1 = tech.get("pivot_r1")
        pivot_s1 = tech.get("pivot_s1")
        if pivot and pivot_r1 and pivot_s1:
            tol = atr * 0.3
            if abs(price - pivot_s1) < tol:
                mean_rev_score += 8
                rationale.append({"src": "Technical", "head": "At Pivot S1 Support",
                    "body": f"Price near classic pivot S1 support (${pivot_s1:.2f}). High-probability bounce level.",
                    "sentiment": "pos", "meta": f"Pivot ${pivot:.2f} | S1 ${pivot_s1:.2f}"})
            elif abs(price - pivot_r1) < tol:
                mean_rev_score -= 8
                rationale.append({"src": "Technical", "head": "At Pivot R1 Resistance",
                    "body": f"Price near classic pivot R1 resistance (${pivot_r1:.2f}). Potential ceiling; watch for rejection.",
                    "sentiment": "neg", "meta": f"Pivot ${pivot:.2f} | R1 ${pivot_r1:.2f}"})

        # ── Volume confirmation ─────────────────────────────────────────
        vol_ratio = volume / avg_vol
        if vol_ratio < 0.80:
            # Low-volume signal — flag for confidence penalty applied at the end
            vol_confidence_penalty = 0.10
            rationale.append({"src": "Technical",
                "head": f"Low Volume — Conviction Reduced ({vol_ratio:.0%} of avg)",
                "body": (f"Today's volume ({volume:,}) is only {vol_ratio:.0%} of the 20-day average. "
                         "Low-volume price moves lack institutional participation and are more "
                         "prone to reversal. Signal confidence reduced."),
                "sentiment": "neg",
                "meta": f"RVOL {vol_ratio:.2f}× | Avg {avg_vol:,}"})
        elif vol_ratio > 1.5:
            # Routed into volume_score (not direct score) so it is capped alongside
            # OBV/CMF — prevents 8 pts bypassing the volume family cap entirely.
            _vol_conf = 8 if score >= 0 else -8
            volume_score += _vol_conf
            rationale.append({"src": "Technical", "head": "High-Volume Confirmation",
                "body": f"Volume {vol_ratio:.1f}× 20-day average — conviction behind the move.",
                "sentiment": "pos" if _vol_conf > 0 else "neg",
                "meta": f"Vol {volume:,} | Avg {avg_vol:,}"})

        # ── Short Interest (squeeze potential) ──────────────────────────
        short_float = info.get("short_float_pct")
        short_ratio = info.get("short_ratio")  # days-to-cover
        # Polygon Reference Data float fix: yfinance floatShares is None for ~30% of tickers.
        # Fall back to Polygon-derived float if yfinance didn't provide short_float_pct.
        if short_float is None:
            try:
                from services.polygon_reference import get_float_data
                _fdata = await get_float_data(ticker)
                _float_shares = _fdata.get("float_shares")
                _total_shares = _fdata.get("total_shares")
                # Short interest comes from FINRA — we can't get it from Polygon free tier.
                # But at least we can recompute short_float_pct from known float + yfinance shortRatio.
                # signal_engine uses info.get("short_float_pct") from yfinance .info, which can be None.
                # If yfinance gave us sharesShort but not floatShares, recompute:
                _shares_short = info.get("shares_short")
                if _float_shares and _float_shares > 0 and _shares_short:
                    short_float = round(_shares_short / _float_shares * 100, 1)
                    log.debug(f"[signal_engine] {ticker} float from Polygon: "
                              f"{_float_shares:,} → short_float={short_float:.1f}%")
            except Exception:
                pass
        if short_float is not None:
            dtc_ok = short_ratio is not None and short_ratio > 5
            if short_float > 20 and dtc_ok and score > 5:
                # Classic squeeze setup: both thresholds met — high conviction
                score += 12
                sources.add("Short Interest")
                rationale.append({"src": "Short Interest",
                    "head": f"High-Conviction Squeeze Setup — {short_float:.1f}% Float Short",
                    "body": (f"{short_float:.1f}% of float is sold short with {short_ratio:.1f} days-to-cover. "
                             "Both thresholds confirm a short squeeze setup: any sustained upward move forces "
                             "rapid, mechanically-driven short covering."),
                    "sentiment": "pos",
                    "meta": f"Short Float {short_float:.1f}% | DTC {short_ratio:.1f}d"})
            elif short_float > 20 and score > 5:
                # High float short but low days-to-cover — partial squeeze signal
                score += 7
                sources.add("Short Interest")
                ratio_str = f" Days-to-cover: {short_ratio:.1f}." if short_ratio else ""
                rationale.append({"src": "Short Interest",
                    "head": f"High Short Float {short_float:.1f}% — Squeeze Potential",
                    "body": (f"{short_float:.1f}% of float is sold short.{ratio_str} "
                             "Rising price with heavy short interest can trigger forced short covering."),
                    "sentiment": "pos",
                    "meta": f"Short Float {short_float:.1f}%"})
            elif short_float > 20 and dtc_ok and score < -10:
                # Symmetric to the +12 squeeze BUY: high short interest with strong
                # days-to-cover, but on a confirmed bearish signal = institutional
                # conviction confirmation. Was previously asymmetric (only -5 pts).
                score -= 12
                sources.add("Short Interest")
                rationale.append({"src": "Short Interest",
                    "head": f"High Short Interest Confirms Bear — {short_float:.1f}% Float Short",
                    "body": (f"{short_float:.1f}% of float is sold short with {short_ratio:.1f}d DTC. "
                             "High institutional conviction backs the bearish thesis — significant "
                             "short positioning rarely placed without fundamental justification."),
                    "sentiment": "neg",
                    "meta": f"Short Float {short_float:.1f}% | DTC {short_ratio:.1f}d"})
            elif short_float > 20 and score < -10:
                score -= 7
                sources.add("Short Interest")
                rationale.append({"src": "Short Interest",
                    "head": f"Heavy Short Float Confirms Bear — {short_float:.1f}%",
                    "body": f"{short_float:.1f}% of float is short — strong institutional conviction in the bearish thesis.",
                    "sentiment": "neg", "meta": f"Short Float {short_float:.1f}%"})
            elif short_float > 15 and score < -5:
                score -= 5
                sources.add("Short Interest")
                rationale.append({"src": "Short Interest",
                    "head": f"Elevated Short Interest {short_float:.1f}%",
                    "body": f"{short_float:.1f}% of float is short — moderate institutional conviction in bearish thesis.",
                    "sentiment": "neg", "meta": f"Short Float {short_float:.1f}%"})

        # ── 52-Week Range Position ───────────────────────────────────────────
        # George & Hwang (2004): stocks within 5% of their 52wk high outperform
        # by 6-8% annually. Near-high = continuation; near-low = danger zone.
        # Uses info["week_52_high"] / info["week_52_low"] extracted from yfinance.
        _wk52h = info.get("week_52_high")
        _wk52l = info.get("week_52_low")
        if _wk52h and _wk52l and price and (_wk52h - _wk52l) > 0 and not _is_lev_etf:
            _rng = _wk52h - _wk52l
            _pos = (price - _wk52l) / _rng  # 0.0 = at 52wk low, 1.0 = at 52wk high
            _pos_pct = round(_pos * 100, 1)
            sources.add("Technicals")
            if _pos >= 0.90:
                score += 4
                rationale.append({"src": "Technicals",
                    "head": f"Near 52-Week High — {_pos_pct:.0f}th Percentile of Range",
                    "body": (f"Price is in the top {100-_pos_pct:.0f}% of its 52-week range "
                             f"(${_wk52l:.2f}–${_wk52h:.2f}). Near-52wk-high stocks outperform by "
                             "6-8% annually in academic studies — momentum continuation signal."),
                    "sentiment": "pos", "meta": f"52w_pos={_pos_pct:.1f}%"})
            elif _pos >= 0.75:
                score += 2
                rationale.append({"src": "Technicals",
                    "head": f"Upper Quartile of 52-Week Range — {_pos_pct:.0f}th Percentile",
                    "body": f"Price in upper 25% of 52-week range — mild momentum confirmation.",
                    "sentiment": "pos", "meta": f"52w_pos={_pos_pct:.1f}%"})
            elif _pos <= 0.10:
                score -= 4
                rationale.append({"src": "Technicals",
                    "head": f"Near 52-Week Low — {_pos_pct:.0f}th Percentile of Range",
                    "body": (f"Price in the bottom {_pos_pct:.0f}% of its 52-week range. "
                             "Near-52wk-low stocks systematically underperform — value trap risk. "
                             "Require much stronger fundamental catalyst before buying."),
                    "sentiment": "neg", "meta": f"52w_pos={_pos_pct:.1f}%"})
            elif _pos <= 0.25:
                score -= 2
                rationale.append({"src": "Technicals",
                    "head": f"Lower Quartile of 52-Week Range — {_pos_pct:.0f}th Percentile",
                    "body": f"Price in bottom 25% of 52-week range — mild downtrend confirmation.",
                    "sentiment": "neg", "meta": f"52w_pos={_pos_pct:.1f}%"})

        # ── Institutional & Insider Ownership ────────────────────────────────
        # High insider ownership = management conviction (skin-in-the-game).
        # High institutional ownership validates the thesis but also signals
        # crowded positioning risk. Uses yfinance free fields.
        _inst_own  = info.get("held_pct_inst")     # e.g. 0.657 = 65.7%
        _insid_own = info.get("held_pct_insiders")  # e.g. 0.016 = 1.6%
        if _insid_own is not None and not _is_lev_etf:
            if _insid_own > 0.15:   # >15% insider ownership
                score += 3
                sources.add("Fundamentals")
                rationale.append({"src": "Fundamentals",
                    "head": f"High Insider Ownership — {_insid_own*100:.1f}%",
                    "body": (f"Insiders hold {_insid_own*100:.1f}% of shares — strong skin-in-the-game "
                             "alignment. High insider ownership is a quality signal: management is "
                             "directly incentivised by share price performance."),
                    "sentiment": "pos", "meta": f"insider_own={_insid_own*100:.1f}%"})
            elif _insid_own < 0.005 and action == "BUY":  # <0.5% insider ownership
                score -= 1
                rationale.append({"src": "Fundamentals",
                    "head": f"Very Low Insider Ownership — {_insid_own*100:.2f}%",
                    "body": (f"Insiders hold only {_insid_own*100:.2f}% — management has minimal "
                             "direct financial stake. Slightly reduces conviction on BUY signals."),
                    "sentiment": "neg", "meta": f"insider_own={_insid_own*100:.2f}%"})
        if _inst_own is not None and not _is_lev_etf:
            if _inst_own > 0.80:    # >80% = very crowded institutional trade
                sources.add("Fundamentals")
                rationale.append({"src": "Fundamentals",
                    "head": f"Crowded Institutional Trade — {_inst_own*100:.1f}% Held",
                    "body": (f"{_inst_own*100:.1f}% of shares are held by institutions — heavily crowded. "
                             "While this validates the thesis, crowded trades are vulnerable to "
                             "rapid de-risking when sentiment shifts."),
                    "sentiment": "neg" if action == "BUY" else "pos",
                    "meta": f"inst_own={_inst_own*100:.1f}%"})

        # ── News sentiment (Benzinga RT + Finnhub + Reuters/Finviz) ─────────
        # Priority: Massive Benzinga (pre-scored, <2min latency) first.
        # Fall back to Finnhub + RSS scrapers. Dedup on headline word overlap.
        avg_sent = 0.0
        _all_news: list[dict] = []
        _seen_ws: list[frozenset] = []

        # Inject Benzinga articles (already scored, age-decayed) as highest-priority
        try:
            from services.benzinga_news import get_benzinga_news
            _bzg_articles = await get_benzinga_news(ticker)
            for _a in _bzg_articles:
                _all_news.append({
                    "headline":  _a["headline"],
                    "sentiment": _a["sentiment"],   # already age-decayed
                    "hours_ago": 0,                 # decay already applied
                    "source":    "Benzinga",
                    "summary":   _a["headline"],
                })
            if _bzg_articles:
                sources.add("Benzinga")
        except Exception:
            pass

        def _nws(s: str) -> frozenset:
            import re as _re
            return frozenset(w.lower() for w in _re.split(r"\W+", s) if len(w) > 4)

        for _item in list(news or []) + list(scraped_news or []):
            _ws = _nws(_item.get("headline", ""))
            if _ws and not any(len(_ws & _prev) / max(len(_ws), 1) > 0.5 for _prev in _seen_ws):
                _seen_ws.append(_ws)
                _all_news.append(_item)

        if _all_news:
            # Age-decay weight: halves every 24 hours
            total_w, weighted_s = 0.0, 0.0
            for n in _all_news:
                w = 1.0 / (1.0 + n.get("hours_ago", 48) / 24.0)
                weighted_s += n["sentiment"] * w
                total_w    += w
            avg_sent = weighted_s / total_w if total_w > 0 else 0.0

            # Which external sources contributed?
            _src_labels = {n.get("source", "") for n in _all_news}
            if news:
                sources.add("Finnhub")
            for _sl in ("Benzinga", "Reuters", "Finviz"):
                if _sl in _src_labels:
                    sources.add(_sl)

            # Cap news contribution at ±15 — sentiment alone is noisy
            _top = sorted(_all_news, key=lambda x: x.get("hours_ago", 9999))[0]
            _src_lbl = _top.get("source", "News")
            if avg_sent > 0.25:
                score += min(15, round(avg_sent * 22))
                rationale.append({
                    "src":       _src_lbl,
                    "head":      _top["headline"][:90],
                    "body":      _top.get("summary", _top["headline"])[:250],
                    "sentiment": "pos",
                    "meta":      f"{_src_lbl} · {_top.get('hours_ago', '?')}h ago | {len(_all_news)} articles",
                })
            elif avg_sent < -0.25:
                score += max(-15, round(avg_sent * 22))
                rationale.append({
                    "src":       _src_lbl,
                    "head":      _top["headline"][:90],
                    "body":      _top.get("summary", _top["headline"])[:250],
                    "sentiment": "neg",
                    "meta":      f"{_src_lbl} · {_top.get('hours_ago', '?')}h ago | {len(_all_news)} articles",
                })

        # ── SEC EDGAR — insider trades (Form 4) ─────────────────────────
        if insider and insider.get("filings", 0) > 0:
            iscore   = insider["score"]
            score   += iscore
            if abs(iscore) >= 4:
                sources.add("SEC EDGAR")
                net  = insider["net_shares"]
                verb = "Buying" if net > 0 else "Selling"
                rationale.append({
                    "src":       "SEC EDGAR",
                    "head":      f"Insiders {verb} — {insider['filings']} Form 4s (30d)",
                    "body":      (
                        f"{insider['filings']} insider filings in last 30 days. "
                        f"Net: {abs(net):,} shares {'acquired' if net > 0 else 'disposed'}. "
                        f"Buy value ${insider['buy_value']:,.0f} | Sell value ${insider['sell_value']:,.0f}."
                    ),
                    "sentiment": "pos" if iscore > 0 else "neg",
                    "meta":      f"Buys {insider['buys']:,} | Sells {insider['sells']:,}",
                })
            # Confidence-level penalty when insider activity directly contradicts direction
            # (score already penalises the direction; this adds a conviction-level haircut)
            if insider.get("filings", 0) >= 3:
                net       = insider.get("net_shares", 0) or 0
                sell_val  = insider.get("sell_value",  0) or 0
                buy_val   = insider.get("buy_value",   0) or 0
                if score > 0 and net < 0 and sell_val > 250_000:
                    insider_confidence_penalty = 0.10
                elif score < 0 and net > 0 and buy_val > 250_000:
                    insider_confidence_penalty = 0.08

        # ── Liquidity Ceiling (NAAIM > 90%) ─────────────────────────────
        aaii = (market_ctx or {}).get("aaii") or {}
        naaim_exposure = aaii.get("exposure", 50)
        liquidity_ceiling = (naaim_exposure > 90)

        # ── Relative Strength vs S&P 500 ────────────────────────────────
        macro     = (market_ctx or {}).get("macro") or {}
        spy_1m    = macro.get("spy_1m_ret")
        if spy_1m is not None and len(df) >= 21:
            close_arr   = df["Close"].astype(float)
            ticker_1m   = (float(close_arr.iloc[-1]) / float(close_arr.iloc[-21]) - 1) * 100
            rel_strength = round(ticker_1m - spy_1m, 2)
            if rel_strength > 8:
                if not liquidity_ceiling:
                    score += 12
                    sources.add("Relative Strength")
                    rationale.append({"src": "Relative Strength", "head": f"Outperforming S&P 500 by {rel_strength:.1f}%",
                        "body": (f"1-month return: {ticker_1m:+.1f}% vs S&P 500 {spy_1m:+.1f}%. "
                                 f"Relative strength of +{rel_strength:.1f}% signals institutional accumulation."),
                        "sentiment": "pos", "meta": f"1M: {ticker_1m:+.1f}% | SPY: {spy_1m:+.1f}%"})
            elif rel_strength > 2:
                if not liquidity_ceiling:
                    score += 4  # mild outperformance still a positive signal
            elif rel_strength < -8:
                score -= 12
                sources.add("Relative Strength")
                rationale.append({"src": "Relative Strength", "head": f"Underperforming S&P 500 by {abs(rel_strength):.1f}%",
                    "body": (f"1-month return: {ticker_1m:+.1f}% vs S&P 500 {spy_1m:+.1f}%. "
                             f"Persistent underperformance suggests institutional selling or fundamental weakness."),
                    "sentiment": "neg", "meta": f"1M: {ticker_1m:+.1f}% | SPY: {spy_1m:+.1f}%"})
            elif rel_strength < -2:
                score -= 5  # mild underperformance is a negative signal
            # Confidence penalty only for persistent underperformers (> -5% vs SPY).
            # The -2% to -5% band is already captured by the score -= 5 above; the
            # confidence penalty here is reserved for meaningful sustained lagging.
            if rel_strength < -5 and score > 0:
                rs_confidence_penalty = 0.08

        # ── Fear & Greed (market-wide, passed from scanner) ─────────────
        fg = (market_ctx or {}).get("fear_greed")
        if fg:
            bias = fg["score_bias"]
            score += bias
            if abs(bias) >= 7:
                sources.add("Fear&Greed")
                rationale.append({
                    "src":       "Fear & Greed",
                    "head":      f"Market {fg['label']} — F&G {fg['score']:.0f}/100",
                    "body":      (
                        f"CNN Fear & Greed Index at {fg['score']:.0f}/100 ({fg['label']}). "
                        + ("Contrarian signal: extreme fear historically marks bottoms."
                           if bias > 0 else
                           "Contrarian signal: extreme greed historically precedes corrections.")
                    ),
                    "sentiment": fg["sentiment"],
                    "meta":      f"F&G = {fg['score']:.0f} | 1w ago: {fg.get('prev_1w', '?')}",
                })

        # ── Macro context (market-wide, passed from scanner) ────────────
        # Cap at ±8 per ticker so macro can't single-handedly push a weak
        # signal to BUY/SELL (raw macro score can reach ±25 in strong regimes).
        if macro and macro.get("macro_score"):
            m_score = macro["macro_score"]
            m_rationale = list(macro.get("rationale", []))
            
            if liquidity_ceiling:
                for item in list(m_rationale):
                    if "Copper/Gold" in item.get("head", "") and item.get("sentiment") == "pos":
                        m_score -= 6
                        m_rationale.remove(item)

            macro_contrib = max(-8, min(8, m_score))
            score += macro_contrib
            for item in m_rationale:
                rationale.append(item)
                sources.add("Macro")

        # ── ROC(10) Momentum ────────────────────────────────────────────
        roc10 = tech.get("roc10")
        if roc10 is not None:
            if roc10 > 8:
                momentum_score += 8
                rationale.append({"src": "Technical", "head": f"Strong Price Momentum +{roc10:.1f}% (10d)",
                    "body": f"Price is up {roc10:.1f}% over the last 10 sessions. Momentum traders will follow.",
                    "sentiment": "pos", "meta": f"ROC(10) = +{roc10:.1f}%"})
            elif roc10 < -8:
                momentum_score -= 8
                rationale.append({"src": "Technical", "head": f"Negative Price Momentum {roc10:.1f}% (10d)",
                    "body": f"Price is down {abs(roc10):.1f}% over the last 10 sessions. Selling pressure persists.",
                    "sentiment": "neg", "meta": f"ROC(10) = {roc10:.1f}%"})
            elif roc10 > 4:
                momentum_score += 4
            elif roc10 < -4:
                momentum_score -= 4

        # ── RSI Divergence ───────────────────────────────────────────────
        # Routed into osc_score (not direct score) so it competes with RSI level
        # within the combined stretch cap — prevents +15 divergence on top of +20
        # RSI-oversold stacking to the same family concept.
        rsi_div = tech.get("rsi_divergence")
        if rsi_div == "bullish":
            osc_score += 12; dominant = "rsi"
            rationale.append({"src": "Technical", "head": "Bullish RSI Divergence",
                "body": "Price made a lower low but RSI made a higher low — momentum is recovering while price dips. Classic reversal warning.",
                "sentiment": "pos", "meta": "RSI divergence: bullish"})
        elif rsi_div == "bearish":
            osc_score -= 12; dominant = "rsi"
            rationale.append({"src": "Technical", "head": "Bearish RSI Divergence",
                "body": "Price made a higher high but RSI made a lower high — momentum is fading while price rises. Classic exhaustion signal.",
                "sentiment": "neg", "meta": "RSI divergence: bearish"})

        # ── MACD Zero-Line Cross ─────────────────────────────────────────
        # Routed into trend_score (same family as MACD state/histogram) so all
        # three MACD signals (crossover, state, zero-cross) share one cap.
        if tech.get("macd_zero_cross_up"):
            trend_score += 10
            rationale.append({"src": "Technical", "head": "MACD Crossed Zero — Trend Flipping Bullish",
                "body": "MACD just crossed above zero. The underlying trend has shifted from bearish to bullish — stronger than a signal-line cross alone.",
                "sentiment": "pos", "meta": f"MACD = {tech.get('macd', 0):.5f}"})
        elif tech.get("macd_zero_cross_down"):
            trend_score -= 10
            rationale.append({"src": "Technical", "head": "MACD Crossed Zero — Trend Flipping Bearish",
                "body": "MACD just crossed below zero. The underlying trend has shifted from bullish to bearish — stronger than a signal-line cross alone.",
                "sentiment": "neg", "meta": f"MACD = {tech.get('macd', 0):.5f}"})

        # ── Z-Score Mean Reversion ───────────────────────────────────────
        zscore = tech.get("zscore")
        if zscore is not None:
            if zscore < -2.5:
                mean_rev_score += 14
                rationale.append({"src": "Technical", "head": f"Z-Score Extreme Oversold ({zscore:.1f}σ)",
                    "body": f"Price is {abs(zscore):.1f} standard deviations below its 20-day average — statistically rare. Strong mean-reversion setup.",
                    "sentiment": "pos", "meta": f"Z-Score = {zscore:.2f}σ"})
            elif zscore < -2.0:
                mean_rev_score += 8
                rationale.append({"src": "Technical", "head": f"Z-Score Oversold ({zscore:.1f}σ)",
                    "body": f"Price {abs(zscore):.1f}σ below 20-day mean. Statistically stretched to the downside.",
                    "sentiment": "pos", "meta": f"Z-Score = {zscore:.2f}σ"})
            elif zscore > 2.5:
                mean_rev_score -= 14
                rationale.append({"src": "Technical", "head": f"Z-Score Extreme Overbought (+{zscore:.1f}σ)",
                    "body": f"Price is {zscore:.1f} standard deviations above its 20-day average — statistically rare. Mean-reversion risk is high.",
                    "sentiment": "neg", "meta": f"Z-Score = +{zscore:.2f}σ"})
            elif zscore > 2.0:
                mean_rev_score -= 8
                rationale.append({"src": "Technical", "head": f"Z-Score Overbought (+{zscore:.1f}σ)",
                    "body": f"Price {zscore:.1f}σ above 20-day mean. Statistically stretched to the upside.",
                    "sentiment": "neg", "meta": f"Z-Score = +{zscore:.2f}σ"})

        # ── Money Flow Index MFI(14) — volume-weighted RSI ───────────────
        mfi = tech.get("mfi")
        if mfi is not None:
            if mfi < 20:
                osc_score += 8
                rationale.append({"src": "Technical", "head": f"MFI Oversold ({mfi:.0f})",
                    "body": f"Money Flow Index at {mfi:.0f} — money is flowing OUT heavily. Volume-confirmed oversold condition. Bounce setup.",
                    "sentiment": "pos", "meta": f"MFI(14) = {mfi:.1f}"})
            elif mfi < 30:
                osc_score += 4
            elif mfi > 80:
                osc_score -= 8
                rationale.append({"src": "Technical", "head": f"MFI Overbought ({mfi:.0f})",
                    "body": f"Money Flow Index at {mfi:.0f} — money is flowing IN excessively. Volume-confirmed overbought condition. Distribution risk.",
                    "sentiment": "neg", "meta": f"MFI(14) = {mfi:.1f}"})
            elif mfi > 70:
                osc_score -= 4

        # osc_score cap deferred: combined with mean_rev_score into a single
        # "stretched price" bucket at the end of that section (see ±30 cap below).
        # This prevents RSI oversold + Z-score oversold from stacking across two caps.

        # ── Weekly Multi-Timeframe RSI + SMA Confirmation ────────────────────
        # Weekly RSI < 40 AND daily RSI < 35 = double-confirmed oversold (72% win rate).
        # Weekly price above SMA(20) AND daily above SMA(200) = multi-timeframe uptrend.
        if _poly_weekly:
            _w_rsi  = _poly_weekly.get("weekly_rsi")
            _w_sma20 = _poly_weekly.get("weekly_sma20")
            if _w_rsi is not None and rsi is not None:
                if _w_rsi < 40 and rsi < 35:
                    osc_score += 8  # double-confirmed oversold — into osc_score (capped in stretch bucket)
                    rationale.append({"src": "Technical",
                        "head": f"Double-Confirmed Oversold: Weekly RSI {_w_rsi:.1f} + Daily RSI {rsi:.1f}",
                        "body": (f"Weekly RSI ({_w_rsi:.1f}) and daily RSI ({rsi:.1f}) are both in oversold territory. "
                                 "Multi-timeframe RSI confluence has a 72% historical win rate vs 58% daily-only. "
                                 "Institutional buyers watching this level."),
                        "sentiment": "pos",
                        "meta": f"W-RSI={_w_rsi:.1f} D-RSI={rsi:.1f}"})
                elif _w_rsi > 70 and rsi > 65:
                    osc_score -= 6  # into osc_score (capped in stretch bucket)
                    rationale.append({"src": "Technical",
                        "head": f"Double-Confirmed Overbought: Weekly RSI {_w_rsi:.1f} + Daily RSI {rsi:.1f}",
                        "body": (f"Both weekly ({_w_rsi:.1f}) and daily ({rsi:.1f}) RSI are elevated. "
                                 "Multi-timeframe overbought alignment increases pullback risk significantly."),
                        "sentiment": "neg",
                        "meta": f"W-RSI={_w_rsi:.1f} D-RSI={rsi:.1f}"})
            if _w_sma20 and sma200 and price:
                _w_above = price > _w_sma20
                _d_above = price > sma200
                if _w_above and _d_above:
                    score += 4
                    rationale.append({"src": "Technical",
                        "head": "Multi-Timeframe Uptrend Confirmed",
                        "body": (f"Price is above both weekly SMA(20) (${_w_sma20:.2f}) and daily SMA(200) (${sma200:.2f}). "
                                 "Dual-timeframe trend alignment: intermediate and long-term trends both bullish."),
                        "sentiment": "pos",
                        "meta": f"W-SMA20=${_w_sma20:.2f} D-SMA200=${sma200:.2f}"})
                elif not _w_above and not _d_above:
                    score -= 4
                    rationale.append({"src": "Technical",
                        "head": "Multi-Timeframe Downtrend Confirmed",
                        "body": (f"Price is below both weekly SMA(20) (${_w_sma20:.2f}) and daily SMA(200) (${sma200:.2f}). "
                                 "Dual-timeframe downtrend."),
                        "sentiment": "neg",
                        "meta": f"W-SMA20=${_w_sma20:.2f} D-SMA200=${sma200:.2f}"})

        # ── Bollinger Band Squeeze + %B ──────────────────────────────────
        bb_squeeze = tech.get("bb_squeeze", False)
        bb_pct_b   = tech.get("bb_pct_b")
        if bb_squeeze and bb_pct_b is not None:
            if bb_pct_b > 0.5:
                mean_rev_score += 8
                rationale.append({"src": "Technical", "head": "Bollinger Squeeze — Upside Breakout Setup",
                    "body": "Bollinger Bands are at their tightest in 20 days (low volatility). Price sits in the upper half — compression before expansion, likely upward.",
                    "sentiment": "pos", "meta": f"BB%B = {bb_pct_b:.2f} | Squeeze ON"})
            else:
                mean_rev_score -= 8
                rationale.append({"src": "Technical", "head": "Bollinger Squeeze — Downside Breakout Risk",
                    "body": "Bollinger Bands at 20-day minimum width. Price in lower half — volatility compression before a likely breakdown.",
                    "sentiment": "neg", "meta": f"BB%B = {bb_pct_b:.2f} | Squeeze ON"})
        elif bb_pct_b is not None:
            if bb_pct_b < 0.05:
                mean_rev_score += 5
            elif bb_pct_b > 0.95:
                mean_rev_score -= 5

        # ── Combined "Stretched Price" cap (osc_score + mean_rev_score) ────────
        # Oscillators (RSI, Stoch, Williams, CCI, MFI, divergence, weekly RSI) and
        # mean-reversion (Z-score, BB touch/squeeze, BB%B, pivot) all ask the same
        # question: "is price statistically stretched from its norm?"
        # Applying two separate caps (±28 osc + ±18*0.85 mean_rev = up to ±43.3 pts)
        # for what is conceptually one signal family was the largest stacking bug.
        # Unified into a single ±30 cap with 0.85 corr-discount.
        score += max(-30.0, min(30.0, osc_score + mean_rev_score)) * 0.85

        # ── Keltner Channels(20, 2×ATR) ──────────────────────────────────────
        kc_upper = tech.get("kc_upper")
        kc_lower = tech.get("kc_lower")
        if kc_upper and kc_lower:
            sources.add("Technical")
            if price > kc_upper:
                score += 8
                rationale.append({"src": "Technical",
                    "head": f"Keltner Channel Breakout (${kc_upper:.2f})",
                    "body": (f"Price ${price:.2f} broke above the upper Keltner Channel "
                             f"(${kc_upper:.2f}). ATR-based channels filter noise better than "
                             "Bollinger — a KC breakout signals genuine momentum, not just volatility expansion."),
                    "sentiment": "pos", "meta": f"KC Upper: ${kc_upper:.2f}"})
            elif price < kc_lower:
                score -= 8
                rationale.append({"src": "Technical",
                    "head": f"Keltner Channel Breakdown (${kc_lower:.2f})",
                    "body": (f"Price ${price:.2f} fell below the lower Keltner Channel "
                             f"(${kc_lower:.2f}). KC breakdowns are high-conviction distribution signals."),
                    "sentiment": "neg", "meta": f"KC Lower: ${kc_lower:.2f}"})
            # Bollinger Bands entirely inside KC = maximum volatility squeeze
            if bb_upper and bb_lower and bb_upper < kc_upper and bb_lower > kc_lower:
                squeeze_sentiment = "pos" if score > 0 else "neg"
                score += 4 if score > 0 else (-4 if score < 0 else 0)
                rationale.append({"src": "Technical",
                    "head": "Keltner–Bollinger Squeeze — Maximum Coil",
                    "body": ("Bollinger Bands are fully contained within Keltner Channels — "
                             "the tightest possible volatility compression. Historically this precedes "
                             "explosive directional moves. The breakout direction is likely set."),
                    "sentiment": squeeze_sentiment,
                    "meta": f"BB inside KC | KC: ${kc_lower:.2f}–${kc_upper:.2f}"})

        # ── Consecutive Close Streak vs SMA20 ────────────────────────────
        streak = tech.get("close_streak", 0)
        if streak >= 7:
            momentum_score += 8
            rationale.append({"src": "Technical", "head": f"{streak} Straight Closes Above SMA20",
                "body": f"Price has closed above its 20-day average for {streak} consecutive sessions. Persistent institutional buying.",
                "sentiment": "pos", "meta": f"Streak: {streak} days above SMA20"})
        elif streak <= -7:
            momentum_score -= 8
            rationale.append({"src": "Technical", "head": f"{abs(streak)} Straight Closes Below SMA20",
                "body": f"Price has closed below its 20-day average for {abs(streak)} straight sessions. Sustained distribution.",
                "sentiment": "neg", "meta": f"Streak: {abs(streak)} days below SMA20"})
        elif streak >= 4:
            momentum_score += 4
        elif streak <= -4:
            momentum_score -= 4

        # ── Credit Stress (HYG trend from macro context) ─────────────────
        hyg_1m = macro.get("hyg_1m_ret")
        if hyg_1m is not None:
            if hyg_1m < -3:
                score -= 8
                sources.add("Macro")
                rationale.append({"src": "Macro", "head": f"Credit Stress: HYG Down {hyg_1m:.1f}% (1M)",
                    "body": "High-yield bonds are falling — a sign of rising credit stress. Risk assets (stocks) tend to follow bonds lower when credit deteriorates.",
                    "sentiment": "neg", "meta": f"HYG 1M = {hyg_1m:.1f}%"})
            elif hyg_1m > 2:
                score += 5
                sources.add("Macro")
                rationale.append({"src": "Macro", "head": f"Credit Healthy: HYG Up {hyg_1m:.1f}% (1M)",
                    "body": "High-yield bonds rising — credit markets are healthy. Risk-on environment favours equities.",
                    "sentiment": "pos", "meta": f"HYG 1M = {hyg_1m:.1f}%"})

        # ── Post-Earnings Cooldown ───────────────────────────────────────
        # Days 0-2 after an earnings release: price discovery is still underway,
        # IV crush is happening, and gap fills / post-earnings drift make all
        # technical indicators unreliable. Hard-HOLD for 2 trading days.
        # Days 3-4: partial suppression (×0.80) — initial reaction is settling.
        _last_earnings = earnings_cal.get("last_earnings_date", "")
        _days_since = earnings_cal.get("days_since_earnings")
        if _days_since is not None and 0 <= _days_since <= 4:
            sources.add("Earnings")
            if _days_since <= 2:
                score = 0
                _force_hold = True   # subsequent signals must not re-open a directional trade
                sources.add("Risk Gate")
                rationale.append({"src": "Risk Gate",
                    "head": f"Post-Earnings Blackout — {_days_since}d After Report ({_last_earnings})",
                    "body": (f"Earnings were reported {_days_since} day(s) ago ({_last_earnings}). "
                             "Price discovery and IV crush are still in progress — technical signals "
                             "are unreliable immediately after earnings. Signal forced to HOLD."),
                    "sentiment": "neg",
                    "meta": f"POST-EARNINGS: {_days_since}d after {_last_earnings}"})
            else:
                score *= 0.80
                rationale.append({"src": "Earnings",
                    "head": f"Post-Earnings Settling — {_days_since}d After Report",
                    "body": (f"Earnings {_days_since} days ago. Initial post-earnings reaction is "
                             "still settling — conviction reduced until price normalises."),
                    "sentiment": "neg",
                    "meta": f"Last earnings: {_last_earnings}"})

        # ── Earnings Proximity Risk ──────────────────────────────────────
        days_to_earnings = earnings_cal.get("days_to_earnings")
        edate = earnings_cal.get("next_earnings_date", "")
        if days_to_earnings is not None and days_to_earnings >= 0:
            sources.add("Earnings")
            if days_to_earnings <= 2:
                # Hard blackout: binary event risk overrides ALL technical signals.
                # IV typically spikes 20–50% into earnings — directional analysis fails.
                score = 0
                _force_hold = True   # subsequent signals must not re-open a directional trade
                sources.add("Risk Gate")
                rationale.append({"src": "Risk Gate",
                    "head": f"Earnings Blackout — {days_to_earnings}d to Binary Event ({edate})",
                    "body": (
                        f"Earnings report in {days_to_earnings} day(s) ({edate}). "
                        "All directional signals are hard-blocked: options implied volatility "
                        "spikes 20–50% ahead of earnings, making price targets statistically "
                        "unreliable. Signal forced to HOLD — reassess after the print."
                    ),
                    "sentiment": "neg", "meta": f"BLACKOUT: earnings {edate}"})
            elif days_to_earnings <= 5:
                score *= 0.75
                rationale.append({"src": "Earnings",
                    "head": f"Earnings in {days_to_earnings}d — Elevated Event Risk",
                    "body": (f"Earnings report in {days_to_earnings} days ({edate}). "
                             "IV expansion ahead of earnings makes directional options trades expensive."),
                    "sentiment": "neg", "meta": f"Next earnings: {edate}"})
            elif days_to_earnings <= 7:
                score *= 0.87
                rationale.append({"src": "Earnings",
                    "head": f"Earnings in {days_to_earnings}d — Early Caution",
                    "body": (f"Earnings report in {days_to_earnings} days ({edate}). "
                             "Stocks often coil or whipsaw in the week before earnings as positioning builds."),
                    "sentiment": "neg", "meta": f"Next earnings: {edate}"})
            elif days_to_earnings <= 14:
                score *= 0.95
                rationale.append({"src": "Earnings",
                    "head": f"Earnings in {days_to_earnings}d — Awareness",
                    "body": (f"Earnings report in {days_to_earnings} days ({edate}). "
                             "Begin tracking IV expansion and analyst estimate revisions."),
                    "sentiment": "neg", "meta": f"Next earnings: {edate}"})

        # ── Earnings Surprise History ─────────────────────────────────────
        consec_beats    = earnings_surp.get("consec_beats", 0)
        misses_4q       = earnings_surp.get("misses_last_4q", 0)
        avg_surp_pct    = earnings_surp.get("avg_surprise_pct")
        last_surp_pct   = earnings_surp.get("last_surprise_pct")
        if earnings_surp:
            sources.add("Earnings")
            if consec_beats >= 4:
                mag_bonus = min(5, round(avg_surp_pct / 5)) if avg_surp_pct and avg_surp_pct > 0 else 0
                score += 10 + mag_bonus
                surp_str = f" avg beat magnitude: +{avg_surp_pct:.1f}%." if avg_surp_pct else ""
                rationale.append({"src": "Earnings",
                    "head": f"{consec_beats} Consecutive EPS Beats",
                    "body": f"Company has beaten analyst EPS estimates for {consec_beats} consecutive quarters.{surp_str} Management consistently delivers positive surprises — strong execution.",
                    "sentiment": "pos",
                    "meta": f"Consec. beats: {consec_beats}" + (f" | Avg beat: +{avg_surp_pct:.1f}%" if avg_surp_pct else "")})
            elif consec_beats >= 2:
                score += 5
                surp_str = f" Last quarter beat by +{last_surp_pct:.1f}%." if last_surp_pct and last_surp_pct > 0 else ""
                rationale.append({"src": "Earnings",
                    "head": f"{consec_beats} Consecutive EPS Beats",
                    "body": f"Company beat EPS estimates in the last {consec_beats} quarters.{surp_str}",
                    "sentiment": "pos",
                    "meta": f"Consec. beats: {consec_beats}"})
            elif misses_4q >= 3:
                mag_penalty = min(4, round(abs(avg_surp_pct) / 5)) if avg_surp_pct and avg_surp_pct < 0 else 0
                score -= 8 + mag_penalty
                surp_str = f" avg miss magnitude: {avg_surp_pct:.1f}%." if avg_surp_pct else ""
                rationale.append({"src": "Earnings",
                    "head": f"Repeated EPS Misses ({misses_4q}/4 Quarters)",
                    "body": f"Company missed analyst EPS estimates in {misses_4q} of the last 4 quarters.{surp_str} Guidance and execution are unreliable.",
                    "sentiment": "neg",
                    "meta": f"Misses: {misses_4q} of last 4Q"})

        # ── EPS Surprise Acceleration ─────────────────────────────────────────
        # Compares most-recent quarter surprise% to oldest (of last 4 quarters).
        # Accelerating beats signal improving execution; decelerating may signal
        # kitchen-sink risk even if the company is technically still beating.
        # Data from Finnhub company_earnings() (free, added to earnings_surp dict).
        _surp_accel = (earnings_surp or {}).get("surprise_acceleration")
        _surp_qtrs  = (earnings_surp or {}).get("quarterly_surprises", [])
        if _surp_accel is not None and not _is_lev_etf:
            sources.add("Earnings")
            _qtrs_str = " → ".join(f"{s:+.1f}%" for s in _surp_qtrs) if _surp_qtrs else ""
            if _surp_accel >= 5:
                score += 5
                rationale.append({"src": "Earnings",
                    "head": f"EPS Beat Acceleration (+{_surp_accel:.1f}pp trend)",
                    "body": (f"EPS surprise trajectory: {_qtrs_str}. "
                             f"Beat magnitude accelerated by {_surp_accel:.1f}pp over 4 quarters. "
                             "Accelerating beats signal improving execution and guidance credibility — "
                             "analysts are systematically underestimating this company."),
                    "sentiment": "pos",
                    "meta": f"surp_acceleration={_surp_accel:+.1f}pp | quarters={_qtrs_str}"})
            elif _surp_accel >= 2:
                score += 2
                rationale.append({"src": "Earnings",
                    "head": f"EPS Beat Momentum (+{_surp_accel:.1f}pp)",
                    "body": f"EPS surprises mildly accelerating: {_qtrs_str}. Modest positive momentum.",
                    "sentiment": "pos",
                    "meta": f"surp_acceleration={_surp_accel:+.1f}pp"})
            elif _surp_accel <= -5:
                score -= 5
                rationale.append({"src": "Earnings",
                    "head": f"EPS Beat Deceleration ({_surp_accel:.1f}pp trend)",
                    "body": (f"EPS surprise trajectory: {_qtrs_str}. "
                             f"Beat magnitude shrank by {abs(_surp_accel):.1f}pp over 4 quarters — "
                             "deceleration risk. Even if the company is still beating, shrinking margins "
                             "of surprise often precede an outright miss."),
                    "sentiment": "neg",
                    "meta": f"surp_acceleration={_surp_accel:+.1f}pp | quarters={_qtrs_str}"})
            elif _surp_accel <= -2:
                score -= 2
                rationale.append({"src": "Earnings",
                    "head": f"EPS Beat Momentum Fading ({_surp_accel:.1f}pp)",
                    "body": f"EPS surprises mildly decelerating: {_qtrs_str}. Monitor closely.",
                    "sentiment": "neg",
                    "meta": f"surp_acceleration={_surp_accel:+.1f}pp"})

        # ── NLP Earnings Tone Analysis (local LLM) ───────────────────────────
        # Analyses the most recent earnings-related news headlines for management
        # tone signals: hesitation, guidance cuts, evasion. These are leading
        # indicators of fundamental weakness before financials reveal it.
        # Only fires when earnings are within 14 days or just passed (3 days).
        _days_to_earnings = (earnings_cal or {}).get("days_to_earnings")
        _in_earnings_window = (
            _days_to_earnings is not None and (
                -3 <= _days_to_earnings <= 14
            )
        )
        if _in_earnings_window and news:
            try:
                from services.local_llm import get_llm_client, analyze_news_sentiment
                _llm = get_llm_client()
                if _llm:
                    _ear_headlines = [
                        n.get("headline", "") for n in (news or [])[:5]
                        if any(kw in n.get("headline", "").lower()
                               for kw in ("earnings", "eps", "revenue", "guidance",
                                          "outlook", "quarter", "miss", "beat", "warn"))
                    ]
                    if _ear_headlines:
                        _ear_result = await asyncio.to_thread(
                            analyze_news_sentiment, [{"headline": h} for h in _ear_headlines], ticker
                        )
                        _ear_score_raw = _ear_result.score  # -1.0 to +1.0
                        if abs(_ear_score_raw) >= 0.3:
                            _ear_pts = round(_ear_score_raw * 8)  # scale to ±8 pts
                            score += _ear_pts
                            sources.add("Earnings")
                            rationale.append({"src": "Earnings",
                                "head": (f"LLM Earnings Tone: {'Positive' if _ear_pts > 0 else 'Negative'} "
                                         f"({_ear_pts:+d}pts)"),
                                "body": (_ear_result.reasoning or
                                         f"NLP analysis of {len(_ear_headlines)} earnings-related headlines "
                                         f"detected {'bullish' if _ear_pts > 0 else 'bearish'} management tone."),
                                "sentiment": "pos" if _ear_pts > 0 else "neg",
                                "meta": (f"llm_earnings_score={_ear_score_raw:.2f} "
                                         f"conf={_ear_result.confidence:.0%} "
                                         f"src={_ear_result.source}")})
            except Exception:
                pass

        # ── Sector Relative Strength ──────────────────────────────────────
        if sector_rs:
            rs  = sector_rs["rs_vs_sector"]
            etf = sector_rs["sector_etf"]
            sources.add("Sector RS")
            if rs > 8:
                score += 10
                rationale.append({"src": "Sector RS",
                    "head": f"Leading {etf} Sector by +{rs:.1f}%",
                    "body": (f"1-month return is {rs:.1f}% above its {etf} sector ETF. "
                             "Outperforming sector peers signals stock-specific institutional demand."),
                    "sentiment": "pos",
                    "meta": f"RS vs {etf}: +{rs:.1f}% | Sector 1M: {sector_rs['sector_1m_ret']:+.1f}%"})
            elif rs > 4:
                score += 5
            elif rs < -8:
                score -= 10
                rationale.append({"src": "Sector RS",
                    "head": f"Lagging {etf} Sector by {abs(rs):.1f}%",
                    "body": (f"1-month return is {abs(rs):.1f}% below its {etf} sector ETF. "
                             "Stock is a sector laggard — possible company-specific weakness."),
                    "sentiment": "neg",
                    "meta": f"RS vs {etf}: {rs:.1f}% | Sector 1M: {sector_rs['sector_1m_ret']:+.1f}%"})
            elif rs < -4:
                score -= 5

            # Sector RS filter: "strong stock in dying sector" trap.
            # A stock outperforming its sector while the sector itself lags SPY is a
            # false leader — the sector tide is falling and will drag it down.
            sector_1m  = sector_rs.get("sector_1m_ret", 0) or 0
            spy_1m_ref = macro.get("spy_1m_ret") or 0
            sector_lag = spy_1m_ref - sector_1m  # positive = sector underperforming SPY
            if score > 0 and rs > 4 and sector_lag > 5:
                score *= 0.82  # ~-18% penalty on BUY conviction
                sources.add("Sector RS")
                rationale.append({"src": "Sector RS",
                    "head": f"Sector Trap Warning — {etf} Lagging SPY by {sector_lag:.1f}%",
                    "body": (f"{ticker} leads its {etf} sector by +{rs:.1f}% but the {etf} sector "
                             f"itself trails SPY by {sector_lag:.1f}%. A strong stock in a "
                             "deteriorating sector is a common trap — the sector tide eventually drags leaders down."),
                    "sentiment": "neg",
                    "meta": f"{etf}: {sector_1m:+.1f}% | SPY: {spy_1m_ref:+.1f}% | Gap: -{sector_lag:.1f}%"})

        # ── Sector downtrend BUY gate ─────────────────────────────────────
        # If the sector ETF is itself in a confirmed 1-month downtrend (< -5%),
        # a BUY signal for a stock in that sector needs a stronger score to
        # qualify. Sector headwinds systematically drag individual stocks lower
        # regardless of company-level technical setup.
        if sector_rs and score > 0:
            sector_1m_gate = sector_rs.get("sector_1m_ret", 0) or 0
            etf_gate       = sector_rs.get("sector_etf", "")
            if sector_1m_gate < -5.0 and score < 40:
                score = 0
                _force_hold = True   # sector blackout — subsequent signals must not re-open
                sources.add("Risk Gate")
                rationale.append({"src": "Risk Gate",
                    "head": f"Sector Downtrend Gate — {etf_gate} {sector_1m_gate:+.1f}% (1M)",
                    "body": (f"{etf_gate} sector is down {abs(sector_1m_gate):.1f}% over the past month "
                             f"(threshold: −5%). A marginal BUY signal (score <40) in a deteriorating "
                             "sector has very low win rates — gate to HOLD until sector stabilises."),
                    "sentiment": "neg",
                    "meta": f"{etf_gate} 1M: {sector_1m_gate:+.1f}% | Score: {score:.1f}"})

        # ── Analyst Price Target (yfinance info) ─────────────────────────
        target_mean   = info.get("target_mean")
        analyst_count = info.get("analyst_count") or 0
        if target_mean and analyst_count >= 3 and price > 0:
            upside = (target_mean - price) / price * 100
            target_high = info.get("target_high")
            target_low  = info.get("target_low")
            sources.add("Analyst")
            if upside > 20:
                analyst_score += 15
                rationale.append({"src": "Analyst", "head": f"Analysts See {upside:.0f}% Upside",
                    "body": (f"{analyst_count} analysts set a consensus price target of ${target_mean:.2f} "
                             f"vs current ${price:.2f} — {upside:.1f}% implied upside."
                             + (f" High: ${target_high:.2f} | Low: ${target_low:.2f}." if target_high and target_low else "")),
                    "sentiment": "pos", "meta": f"Target ${target_mean:.2f} | {analyst_count} analysts"})
            elif upside > 10:
                analyst_score += 8
                rationale.append({"src": "Analyst", "head": f"Analysts See {upside:.0f}% Upside",
                    "body": (f"Consensus target ${target_mean:.2f} implies {upside:.1f}% upside from ${price:.2f} "
                             f"across {analyst_count} analysts."),
                    "sentiment": "pos", "meta": f"Target ${target_mean:.2f} | {analyst_count} analysts"})
            elif upside < -15:
                analyst_score -= 12
                rationale.append({"src": "Analyst", "head": f"Analysts See {abs(upside):.0f}% Downside",
                    "body": (f"Consensus target ${target_mean:.2f} is {abs(upside):.1f}% below current price ${price:.2f}. "
                             f"{analyst_count} analysts collectively see limited upside."),
                    "sentiment": "neg", "meta": f"Target ${target_mean:.2f} | {analyst_count} analysts"})
            elif upside < -5:
                analyst_score -= 6
                rationale.append({"src": "Analyst", "head": f"Analyst Target Below Market Price",
                    "body": (f"Consensus target ${target_mean:.2f} is {abs(upside):.1f}% below ${price:.2f}. "
                             f"Street expects limited near-term upside."),
                    "sentiment": "neg", "meta": f"Target ${target_mean:.2f} | {analyst_count} analysts"})

        # ── Analyst Recommendation Consensus (yfinance info) ─────────────
        rec_key  = info.get("rec_key", "")
        rec_mean = info.get("rec_mean")
        if rec_key:
            sources.add("Analyst")
            if rec_key in ("strong_buy", "strongBuy") or (rec_mean and rec_mean <= 1.5):
                analyst_score += 10
                rationale.append({"src": "Analyst", "head": "Analysts Rate Stock: Strong Buy",
                    "body": "Majority of covering analysts have a Strong Buy consensus. Institutional conviction is high.",
                    "sentiment": "pos", "meta": f"Consensus: {rec_key} (score {rec_mean:.1f}/5)" if rec_mean else f"Consensus: {rec_key}"})
            elif rec_key == "buy" or (rec_mean and rec_mean <= 2.2):
                analyst_score += 6
                rationale.append({"src": "Analyst", "head": "Analysts Rate Stock: Buy",
                    "body": "Analyst consensus leans towards a Buy rating.",
                    "sentiment": "pos", "meta": f"Consensus: {rec_key}" + (f" ({rec_mean:.1f}/5)" if rec_mean else "")})
            elif rec_key == "sell" or (rec_mean and rec_mean >= 3.8):
                analyst_score -= 8
                rationale.append({"src": "Analyst", "head": "Analysts Rate Stock: Sell",
                    "body": "Analyst consensus leans towards a Sell rating. Street is bearish.",
                    "sentiment": "neg", "meta": f"Consensus: {rec_key}" + (f" ({rec_mean:.1f}/5)" if rec_mean else "")})
            elif rec_key in ("strong_sell", "strongSell") or (rec_mean and rec_mean >= 4.5):
                analyst_score -= 12
                rationale.append({"src": "Analyst", "head": "Analysts Rate Stock: Strong Sell",
                    "body": "Strong Sell consensus across covering analysts. Institutional conviction is bearish.",
                    "sentiment": "neg", "meta": f"Consensus: {rec_key}" + (f" ({rec_mean:.1f}/5)" if rec_mean else "")})

        # ── Finnhub Analyst Recommendation Trends ────────────────────────
        if analyst_recs:
            sb  = analyst_recs.get("strong_buy",  0)
            b   = analyst_recs.get("buy",         0)
            h   = analyst_recs.get("hold",        0)
            s   = analyst_recs.get("sell",        0)
            ss  = analyst_recs.get("strong_sell", 0)
            total_recs = sb + b + h + s + ss
            if total_recs >= 5:
                sources.add("Analyst")
                bull_pct = (sb + b) / total_recs * 100
                bear_pct = (s + ss) / total_recs * 100
                period   = analyst_recs.get("period", "")
                if bull_pct >= 70:
                    analyst_score += 10
                    rationale.append({"src": "Analyst",
                        "head": f"{bull_pct:.0f}% of Analysts are Bullish",
                        "body": (f"Finnhub consensus ({period}): {sb} Strong Buy + {b} Buy out of {total_recs} analysts. "
                                 f"Strong institutional buy-side conviction."),
                        "sentiment": "pos",
                        "meta": f"SB:{sb} B:{b} H:{h} S:{s} SS:{ss}"})
                elif bull_pct >= 55:
                    analyst_score += 5
                elif bear_pct >= 60:
                    analyst_score -= 8
                    rationale.append({"src": "Analyst",
                        "head": f"{bear_pct:.0f}% of Analysts are Bearish",
                        "body": (f"Finnhub consensus ({period}): {s} Sell + {ss} Strong Sell out of {total_recs} analysts. "
                                 f"Street is broadly negative on this stock."),
                        "sentiment": "neg",
                        "meta": f"SB:{sb} B:{b} H:{h} S:{s} SS:{ss}"})

        # ── Analyst estimate revision momentum ───────────────────────────────
        # Compare this month's bull/bear scores to last month's. Rising upgrades
        # and falling downgrades are one of the most consistent documented alpha
        # factors (SUE effect, earnings revision momentum). Revision data comes
        # from the same Finnhub recommendation_trends call already made above —
        # no additional API cost.
        rev_pts = analyst_recs.get("revision_pts") if analyst_recs else None
        if rev_pts is not None and abs(rev_pts) >= 2:
            analyst_score += rev_pts
            sources.add("Analyst")
            bull_d = analyst_recs.get("bull_delta", 0)
            bear_d = analyst_recs.get("bear_delta", 0)
            rev_period = analyst_recs.get("revision_period", "prior month")
            if rev_pts > 0:
                rationale.append({"src": "Analyst",
                    "head": f"Analyst Upgrade Momentum (+{rev_pts:.0f}pts vs {rev_period})",
                    "body": (f"Bull score rose by {bull_d:+.0f} and bear score changed by {bear_d:+.0f} "
                             f"vs {rev_period}. Rising upgrades with falling downgrades is one of the "
                             "strongest documented equity alpha factors — price follows estimates."),
                    "sentiment": "pos",
                    "meta": f"rev_pts={rev_pts:+.0f} | bull_delta={bull_d:+.0f} | bear_delta={bear_d:+.0f}"})
            else:
                rationale.append({"src": "Analyst",
                    "head": f"Analyst Downgrade Momentum ({rev_pts:.0f}pts vs {rev_period})",
                    "body": (f"Bull score fell by {abs(bull_d):.0f} and bear score rose by {abs(bear_d):.0f} "
                             f"vs {rev_period}. Analysts are cutting estimates — forward earnings are "
                             "deteriorating. Negative revision momentum precedes price weakness."),
                    "sentiment": "neg",
                    "meta": f"rev_pts={rev_pts:+.0f} | bull_delta={bull_d:+.0f} | bear_delta={bear_d:+.0f}"})

        # ── Massive Analyst Intelligence (Bulls Bears Say + Guidance) ───────
        try:
            from services.massive_analyst import get_analyst_intelligence
            ai = await get_analyst_intelligence(ticker)
            if ai:
                bbs = ai.get("bulls_bears", {})
                gd  = ai.get("guidance", {})
                # Bulls Bears Say — adds colour to rationale
                bbs_score = bbs.get("score", 0.0)
                if abs(bbs_score) >= 2.0:
                    analyst_score += bbs_score
                    bbs_label = bbs.get("label", "neutral").capitalize()
                    bc, rc = bbs.get("bull_count", 0), bbs.get("bear_count", 0)
                    text = bbs.get("bull_text" if bbs_score > 0 else "bear_text", "")
                    rationale.append({"src": "Analyst",
                        "head": f"Bulls Bears Say: {bbs_label} ({bc} bull / {rc} bear analysts)",
                        "body": text[:250] or f"{bc} analysts bullish vs {rc} bearish on {ticker}.",
                        "sentiment": "pos" if bbs_score > 0 else "neg",
                        "meta": f"bbs_score={bbs_score:+.1f}"})
                # Corporate Guidance signal (high-weight catalyst)
                gd_score = gd.get("score", 0.0)
                if abs(gd_score) >= 4.0:
                    analyst_score += gd_score
                    rationale.append({"src": "Analyst",
                        "head": f"Corporate Guidance {'Raised' if gd_score > 0 else 'Cut'}",
                        "body": gd.get("summary", "Company updated EPS/revenue guidance."),
                        "sentiment": "pos" if gd_score > 0 else "neg",
                        "meta": f"guidance_score={gd_score:+.1f}"})
        except Exception:
            pass

        # Apply analyst consensus bucket cap: price target + rec consensus + Finnhub
        # recs all read "what sell-side thinks" — cap so the bucket contributes once.
        # Positive cap lowered from +18 → +10: sell-side has a structural bullish
        # coverage bias (~55% of ratings are Buy/Strong Buy) that inflates BUY signals.
        # Negative cap kept at -18 — bearish analyst consensus is rarer and more meaningful.
        score += max(-18, min(10, analyst_score))

        # ── HMM Regime multiplier (replaces static VIX thresholds) ─────────────
        # The HMM provides a probabilistic regime label that *leads* moving averages
        # by detecting transitions in the latent state before they appear in prices.
        vix = macro.get("vix")
        hmm = (market_ctx or {}).get("hmm_regime", {})
        hmm_regime    = hmm.get("regime", "")
        bull_prob     = hmm.get("bull_prob", 0.5)
        bear_prob     = hmm.get("bear_prob", 0.5)
        trans_risk    = hmm.get("transition_risk", 0.1)
        vix_z         = hmm.get("vix_z", 0.0)

        if hmm_regime:
            # HMM data available — use continuous probability weighting
            if hmm_regime == "bear" and bear_prob >= 0.70:
                score *= 0.72
                rationale.append({"src": "Macro",
                    "head": f"HMM Bear Regime ({bear_prob:.0%} probability) — Score Reduced",
                    "body": (f"The macro regime model assigns {bear_prob:.0%} probability to a risk-off state. "
                             f"VIX z-score: {vix_z:+.1f}σ. Signal reliability is structurally lower in bear regimes — "
                             f"reduce position size and widen stops."),
                    "sentiment": "neg", "meta": f"HMM bear={bear_prob:.0%} vix_z={vix_z:+.1f}σ"})
            elif hmm_regime == "transition" or trans_risk > 0.15:
                score *= 0.88
                rationale.append({"src": "Macro",
                    "head": f"HMM Regime Transition Risk ({trans_risk:.0%}) — Caution",
                    "body": (f"The HMM detects elevated probability of a regime shift "
                             f"(bull→bear or vice versa) within 1–3 days. "
                             f"P(bull)={bull_prob:.0%} P(bear)={bear_prob:.0%}. "
                             f"Consider tighter stops until regime resolves."),
                    "sentiment": "neg", "meta": f"trans_risk={trans_risk:.0%}"})
            elif hmm_regime == "bull" and bull_prob >= 0.75 and vix_z < -0.5:
                score *= 1.06
                rationale.append({"src": "Macro",
                    "head": f"HMM Bull Regime ({bull_prob:.0%}) — Favourable",
                    "body": (f"Macro regime model: {bull_prob:.0%} probability of risk-on state. "
                             f"VIX below historical mean ({vix_z:+.1f}σ). "
                             f"Trend-following signals are more reliable in this environment."),
                    "sentiment": "pos", "meta": f"HMM bull={bull_prob:.0%} vix_z={vix_z:+.1f}σ"})
        else:
            # Fallback to legacy static VIX thresholds when HMM data unavailable
            if vix is not None:
                if vix > 35:
                    score *= 0.60
                    rationale.append({"src": "Macro", "head": f"VIX Extreme Fear ({vix:.0f}) — Confidence Reduced",
                        "body": f"VIX at {vix:.0f} signals panic-level volatility. Technical patterns break down in these conditions. Reduce position size significantly.",
                        "sentiment": "neg", "meta": f"VIX = {vix:.0f}"})
                elif vix > 25:
                    score *= 0.82
                    sources.add("Macro")
                elif vix < 15:
                    score *= 1.06

        # ── Extended-Hours (Pre-Market / After-Hours) Signal ─────────────────
        # Fires only outside regular session (4–9:30 AM ET, 4–8 PM ET).
        # Pre-market gaps and extended-hours volume are meaningful leading indicators:
        # a large gap on high extended-hours volume has a ~68% continuation rate
        # into the regular session (vs ~52% for low-volume gaps that often fill).
        session = _current_session()
        if ext_hours and session in ("pre", "after"):
            eh_gap    = ext_hours.get("gap_pct",   0) or 0
            eh_vol_r  = ext_hours.get("vol_ratio",  1) or 1
            eh_price  = ext_hours.get("price")
            eh_prev   = ext_hours.get("prev_close")
            sources.add("Technical")

            # Gap magnitude signal — direction-aware
            if abs(eh_gap) >= 1.0:
                # High-volume gap: more likely to continue; low-volume: more likely to fill
                high_vol = eh_vol_r >= 1.5
                if eh_gap >= 3.0:
                    bonus = 12 if high_vol else 6
                    score += bonus
                    rationale.append({"src": "Technical",
                        "head": f"{'Pre' if session=='pre' else 'After'}-Market Gap Up +{eh_gap:.1f}%{' (High Vol)' if high_vol else ''}",
                        "body": (f"Price gapped {eh_gap:.1f}% above the prior regular-session close "
                                 f"(${eh_prev:.2f} → ${eh_price:.2f}) in extended hours. "
                                 + ("High volume ({:.1f}× avg) confirms institutional conviction — gap likely to hold.".format(eh_vol_r)
                                    if high_vol else
                                    "Light volume ({:.1f}× avg) — gap may fill at open.".format(eh_vol_r))),
                        "sentiment": "pos",
                        "meta": f"EH gap: +{eh_gap:.1f}% | Vol ratio: {eh_vol_r:.1f}×"})
                elif eh_gap >= 1.0:
                    bonus = 6 if high_vol else 3
                    score += bonus
                    rationale.append({"src": "Technical",
                        "head": f"{'Pre' if session=='pre' else 'After'}-Market Gap Up +{eh_gap:.1f}%",
                        "body": (f"Moderate extended-hours gap of +{eh_gap:.1f}%. "
                                 + ("Volume confirms the move.".format() if high_vol else "Watch for fill at open.")),
                        "sentiment": "pos",
                        "meta": f"EH gap: +{eh_gap:.1f}% | Vol: {eh_vol_r:.1f}×"})
                elif eh_gap <= -3.0:
                    penalty = -12 if high_vol else -6
                    score += penalty
                    rationale.append({"src": "Technical",
                        "head": f"{'Pre' if session=='pre' else 'After'}-Market Gap Down {eh_gap:.1f}%{' (High Vol)' if high_vol else ''}",
                        "body": (f"Price gapped {eh_gap:.1f}% below the prior close "
                                 f"(${eh_prev:.2f} → ${eh_price:.2f}) in extended hours. "
                                 + ("High volume confirms distribution — gap likely to persist.".format()
                                    if high_vol else "Low volume — gap may partially fill at open.")),
                        "sentiment": "neg",
                        "meta": f"EH gap: {eh_gap:.1f}% | Vol ratio: {eh_vol_r:.1f}×"})
                elif eh_gap <= -1.0:
                    penalty = -6 if high_vol else -3
                    score += penalty
                    rationale.append({"src": "Technical",
                        "head": f"{'Pre' if session=='pre' else 'After'}-Market Gap Down {eh_gap:.1f}%",
                        "body": (f"Moderate extended-hours gap of {eh_gap:.1f}%. "
                                 + ("Volume confirms selling pressure." if high_vol else "Low volume — may recover at open.")),
                        "sentiment": "neg",
                        "meta": f"EH gap: {eh_gap:.1f}% | Vol: {eh_vol_r:.1f}×"})

            # Extended-hours volume surge even with a small gap = institutional activity
            if eh_vol_r >= 3.0 and abs(eh_gap) < 1.0:
                direction_bonus = 4 if eh_gap >= 0 else -4
                score += direction_bonus
                rationale.append({"src": "Technical",
                    "head": f"Extended-Hours Volume Surge ({eh_vol_r:.1f}×) — Flat Price",
                    "body": (f"Extended-hours volume is {eh_vol_r:.1f}× above average with only a "
                             f"{eh_gap:+.2f}% price move. Unusual volume without price movement often "
                             "signals institutional positioning ahead of the regular session."),
                    "sentiment": "pos" if direction_bonus > 0 else "neg",
                    "meta": f"EH vol: {eh_vol_r:.1f}× | Gap: {eh_gap:+.2f}%"})

        # ── Options flow (yfinance multi-expiry enhanced sweep detection) ───
        if opt_flow:
            opt_score, opt_rationale = score_options(opt_flow)
            if opt_score != 0:
                score += opt_score
                sources.add("Options")
                rationale.extend(opt_rationale)

            # ── Massive API Advanced Signals ─────────────────────────────────────
            if massive_sigs:
                # 1. Dark Pool / Short Interest
                short_vol_pct = massive_sigs.get("short_interest", {}).get("short_volume_pct", 0)
                if short_vol_pct > 55.0:
                    score -= 12.0
                    sources.add("Dark Pool")
                    rationale.append({
                        "src": "Dark Pool", "head": "Heavy Dark Pool Short Volume",
                        "body": f"Off-exchange short volume surged to {short_vol_pct:.1f}%, indicating significant stealth institutional distribution and overhead supply.",
                        "sentiment": "neg", "meta": "Short Interest"
                    })
                elif 0 < short_vol_pct < 35.0:
                    score += 10.0
                    sources.add("Dark Pool")
                    rationale.append({
                        "src": "Dark Pool", "head": "Light Dark Pool Short Volume",
                        "body": f"Off-exchange short volume dropped to {short_vol_pct:.1f}%, indicating institutional accumulation and a lack of short-selling pressure.",
                        "sentiment": "pos", "meta": "Short Interest"
                    })

                # 2. Fails-to-Deliver (FTDs) & Reg SHO
                ftd = massive_sigs.get("ftd", {})
                if ftd.get("is_reg_sho") and ftd.get("spike_pct", 0) > 300:
                    score += 15.0
                    sources.add("Fundamentals")
                    rationale.append({
                        "src": "Fundamentals", "head": f"Reg SHO Threshold + FTD Spike ({ftd.get('spike_pct', 0):.0f}%)",
                        "body": "Stock is on Reg SHO list with surging Fails-to-Deliver. High probability of forced mechanical short covering.",
                        "sentiment": "pos", "meta": "FTD Spike"
                    })

                # 3. Options Gamma Exposure (GEX)
                gex = massive_sigs.get("gex", {})
                net_gex = gex.get("net_gex", 0.0)
                if net_gex > 1000000:
                    mean_rev_score += 5.0
                    momentum_score -= 5.0
                    sources.add("Options")
                    rationale.append({
                        "src": "Options", "head": "Positive Gamma Exposure (GEX)",
                        "body": "Dealers are net long gamma. Volatility is pinned, favouring mean-reversion and range-bound trading.",
                        "sentiment": "neu", "meta": "Positive GEX"
                    })
                elif net_gex < -1000000:
                    momentum_score += 5.0
                    mean_rev_score -= 5.0
                    sources.add("Options")
                    rationale.append({
                        "src": "Options", "head": "Negative Gamma Exposure (GEX)",
                        "body": "Dealers are net short gamma. Volatility is unpinned, favouring momentum breakouts and trend acceleration.",
                        "sentiment": "neu", "meta": "Negative GEX"
                    })

                # 4. Retail vs Institutional Flow Divergence
                retail_flow = massive_sigs.get("retail_flow", 0.0)
                dp_flow = massive_sigs.get("dark_pool_flow", 0.0)
                if retail_flow < -1.0 and dp_flow > 5.0:
                    score += 10.0
                    sources.add("Dark Pool")
                    rationale.append({
                        "src": "Dark Pool", "head": "Smart Money Divergence — Retail Capitulation",
                        "body": "Heavy retail odd-lot selling met with massive off-exchange institutional block buying. Strong reversal signal.",
                        "sentiment": "pos", "meta": "Flow Divergence"
                    })
                elif retail_flow > 1.0 and dp_flow < -5.0:
                    score -= 10.0
                    sources.add("Dark Pool")
                    rationale.append({
                        "src": "Dark Pool", "head": "Smart Money Divergence — Institutional Distribution",
                        "body": "Retail odd-lot buying is providing liquidity for off-exchange institutional block selling. Distribution warning.",
                        "sentiment": "neg", "meta": "Flow Divergence"
                    })

                # 5. Real-Time Order Book Imbalance (Level 2)
                order_book = massive_sigs.get("order_book", {})
                bid_ask_ratio = order_book.get("bid_ask_ratio", 1.0)
                if bid_ask_ratio >= 4.0:
                    score += 8.0
                    sources.add("Technical")
                    rationale.append({
                        "src": "Technical", "head": f"Level 2 Imbalance: 4:1 Bid Support",
                        "body": "Order book shows 4x more bid liquidity than ask liquidity within 1% of the spread. Massive structural support floor.",
                        "sentiment": "pos", "meta": "Level 2"
                    })
                elif bid_ask_ratio <= 0.25:
                    score -= 8.0
                    sources.add("Technical")
                    rationale.append({
                        "src": "Technical", "head": f"Level 2 Imbalance: Heavy Ask Resistance",
                        "body": "Order book shows 4x more ask liquidity than bid liquidity within 1% of the spread. Massive structural resistance ceiling.",
                        "sentiment": "neg", "meta": "Level 2"
                    })

                # 6. Corporate Actions: Real-Time Buyback Executions
                corp_actions = massive_sigs.get("corp_actions", {})
                if corp_actions.get("active_asr") or corp_actions.get("issuer_buying"):
                    score += 15.0
                    sources.add("Fundamentals")
                    rationale.append({
                        "src": "Fundamentals", "head": "Active Issuer Share Repurchase",
                        "body": "Corporate treasury is actively buying shares on the tape (Accelerated Share Repurchase). Mechanical bid under the stock.",
                        "sentiment": "pos", "meta": "Corporate Action"
                    })

        # ── 8-K Material Events ───────────────────────────────────────────────
        try:
            from services.eightk_events import get_8k_signals
            ek = await get_8k_signals(ticker)
            if ek and abs(ek.get("score", 0)) >= 3.0:
                sources.add("Fundamentals")
                score += ek["score"]
                for ev_label in ek.get("events", [])[:2]:
                    rationale.append({"src": "Fundamentals",
                        "head": f"8-K Event: {ev_label}",
                        "body": ("SEC Form 8-K reports material corporate events within 4 business days. "
                                 "These are the earliest public disclosures of M&A, CEO changes, "
                                 "material agreements, and guidance updates."),
                        "sentiment": "pos" if ek["score"] > 0 else "neg",
                        "meta": f"8k_score={ek['score']:+.1f}"})
        except Exception:
            pass

        # ── Massive Financial Ratios (augment yfinance fundamentals) ─────────
        try:
            from services.massive_ratios import get_ratios, merge_with_yfinance
            massive_r = await get_ratios(ticker)
            if massive_r and fundamentals:
                fundamentals = merge_with_yfinance(fundamentals, massive_r)
        except Exception:
            pass

        # ── Full Option Chain Analysis (GEX + Skew + Max Pain) ───────────────
        try:
            from services.massive_options import get_option_chain_signals, score_option_chain
            chain_signals = await get_option_chain_signals(ticker, price)
            if chain_signals:
                chain_score, chain_rat = score_option_chain(chain_signals, price, action)
                if abs(chain_score) >= 2.0:
                    sources.add("Options")
                    score += chain_score
                    rationale.extend(chain_rat)
        except Exception:
            pass

        # ── ETF Constituent Flow Amplification ────────────────────────────────
        try:
            from services.sector import SECTOR_MAP
            from services.etf_constituents import get_flow_amplifier
            from services.etf_flows import get_flow_score_for_ticker
            etf_for_ticker = SECTOR_MAP.get(ticker)
            if etf_for_ticker:
                amp = get_flow_amplifier(ticker, etf_for_ticker)
                if amp > 1.0:
                    flow_sc, _ = get_flow_score_for_ticker(ticker, (market_ctx or {}).get("etf_flows"))
                    if abs(flow_sc) >= 2.0:
                        bonus = round(flow_sc * (amp - 1.0), 1)
                        score += bonus
        except Exception:
            pass

        # ── 13F Institutional flow (with QoQ trend) ──────────────────────────
        inst_signals = (market_ctx or {}).get("institutional_signals", {})
        if ticker in inst_signals:
            inst_sig   = inst_signals[ticker]
            inst_score = inst_sig.get("score", 0)
            qoq_trend  = inst_sig.get("qoq_trend", "neutral")
            if inst_score != 0:
                score += inst_score
                sources.add("13F")
                rat = inst_sig.get("rationale", {})
                if rat:
                    rationale.append(rat)
                # Add an extra QoQ-specific rationale item for rising/falling trends
                if qoq_trend == "rising" and inst_score > 0:
                    rationale.append({
                        "src": "13F",
                        "head": "Institutional Conviction Rising — 2+ Consecutive Quarters Buying",
                        "body": (
                            f"Multiple institutional investors have increased their {ticker} position "
                            "for two or more consecutive quarters. Sustained accumulation signals "
                            "growing conviction rather than a one-off position initiation."
                        ),
                        "sentiment": "pos",
                        "meta": "QoQ trend: rising",
                    })
                elif qoq_trend == "falling" and inst_score < 0:
                    rationale.append({
                        "src": "13F",
                        "head": "Institutional Conviction Falling — 2+ Consecutive Quarters Exiting",
                        "body": (
                            f"Institutions have reduced their {ticker} stake for two or more consecutive "
                            "quarters. Sequential selling is an early exit warning — smart money is "
                            "methodically reducing exposure."
                        ),
                        "sentiment": "neg",
                        "meta": "QoQ trend: falling",
                    })

        # ── Cointegration / Pairs Trading ────────────────────────────────────────
        pairs_signals = (market_ctx or {}).get("pairs_signals", {})
        if ticker in pairs_signals:
            ps       = pairs_signals[ticker]
            ps_score = ps.get("score", 0)
            if abs(ps_score) >= 5:
                score += ps_score
                sources.add("Stat Arb")
                pair      = ps.get("pair_ticker", "?")
                zscore    = ps.get("zscore", 0)
                direction = ps.get("direction", "")
                corr      = ps.get("correlation", 0)
                rationale.append({
                    "src":       "Stat Arb",
                    "head":      f"Pairs Divergence vs {pair} — {direction.title()} ({zscore:+.1f}σ)",
                    "body":      (
                        f"{ticker} is {direction} relative to its cointegrated pair {pair} "
                        f"(spread z-score {zscore:+.1f}σ, {corr:.0%} rolling correlation). "
                        "Statistical arbitrage signals of this magnitude mean-revert "
                        "within 5–15 trading days historically."
                    ),
                    "sentiment": "pos" if ps_score > 0 else "neg",
                    "meta":      f"Z-score: {zscore:+.1f}σ | Pair: {pair} | Corr: {corr:.2f}",
                })

        # ── CBOE Put/Call Ratio (contrarian sentiment) ───────────────────────
        pc = (market_ctx or {}).get("put_call")
        if pc and pc.get("bias"):
            bias = pc["bias"]
            pc_score += bias
            if abs(bias) >= 8:
                sources.add("Options")
                signal_txt = "extreme put buying (fear)" if bias > 0 else "extreme call buying (complacency)"
                rationale.append({"src": "Options",
                    "head": f"CBOE P/C Ratio {pc['ratio']} — {signal_txt.split('(')[1].rstrip(')')} signal",
                    "body": (f"CBOE total put/call ratio at {pc['ratio']}. "
                             + ("Ratio >1.15 signals excessive fear — contrarian bullish."
                                if bias > 0 else "Ratio <0.65 signals complacency — contrarian bearish.")),
                    "sentiment": "pos" if bias > 0 else "neg",
                    "meta": f"P/C = {pc['ratio']}"})

        # ── Options Flow Direction Confirmation ──────────────────────────────
        # Directional layer: does the options market flow align with or contradict
        # the current signal? Both use the same P/C ratio — bucketed with contrarian
        # above so the ratio only contributes once to the total score.
        if pc and pc.get("ratio"):
            pc_ratio = float(pc["ratio"])
            if score > 0:  # BUY signal
                if pc_ratio < 0.70:
                    # Calls dominating — options market is directionally bullish, confirms BUY
                    pc_score += 6
                    sources.add("Options")
                    rationale.append({"src": "Options",
                        "head": f"Options Flow Confirms BUY (P/C {pc_ratio:.2f})",
                        "body": (f"CBOE P/C ratio of {pc_ratio:.2f} shows call volume dominating puts. "
                                 "The options market is directionally bullish — confirming this BUY signal."),
                        "sentiment": "pos", "meta": f"P/C = {pc_ratio:.2f} (calls dominant)"})
                elif pc_ratio > 1.50:
                    # Puts dominating — options market is directionally bearish, contradicts BUY
                    pc_score -= 10
                    sources.add("Options")
                    rationale.append({"src": "Options",
                        "head": f"Options Flow Contradicts BUY (P/C {pc_ratio:.2f})",
                        "body": (f"CBOE P/C ratio of {pc_ratio:.2f} shows put volume dominating calls. "
                                 "The options market is positioning bearishly — this conflicts with the BUY signal."),
                        "sentiment": "neg", "meta": f"P/C = {pc_ratio:.2f} (puts dominant)"})
            elif score < 0:  # SELL signal
                if pc_ratio > 1.50:
                    # Puts dominating — confirms SELL direction
                    pc_score -= 6
                    sources.add("Options")
                    rationale.append({"src": "Options",
                        "head": f"Options Flow Confirms SELL (P/C {pc_ratio:.2f})",
                        "body": (f"CBOE P/C ratio of {pc_ratio:.2f} shows heavy put buying. "
                                 "The options market is directionally bearish — confirming this SELL signal."),
                        "sentiment": "neg", "meta": f"P/C = {pc_ratio:.2f} (puts dominant)"})
                elif pc_ratio < 0.70:
                    # Calls dominating — contradicts SELL direction
                    pc_score += 10
                    sources.add("Options")
                    rationale.append({"src": "Options",
                        "head": f"Options Flow Contradicts SELL (P/C {pc_ratio:.2f})",
                        "body": (f"CBOE P/C ratio of {pc_ratio:.2f} shows calls dominating. "
                                 "Options market is bullish — this contradicts the SELL signal."),
                        "sentiment": "pos", "meta": f"P/C = {pc_ratio:.2f} (calls dominant)"})

        # Apply P/C ratio bucket cap: contrarian bias + directional confirmation both
        # derived from the same ratio — prevent the same data point scoring twice.
        # 0.85 discount: overlaps with score_options() sweep/flow signals already in score.
        score += max(-12, min(12, pc_score)) * 0.85

        # ── Market Breadth (% of S&P 500 basket above SMA50/200) ────────────
        breadth = (market_ctx or {}).get("breadth")
        if breadth and breadth.get("signal") != "neutral" and breadth.get("score"):
            b_score  = breadth["score"]
            pct_200  = breadth["pct_above_200d"]
            pct_50   = breadth["pct_above_50d"]
            score   += b_score
            sources.add("Market Breadth")
            if b_score >= 10:
                rationale.append({
                    "src":  "Market Breadth",
                    "head": f"Broad Market Participation — {pct_200:.0f}% of S&P 500 Above 200-DMA",
                    "body": (f"{pct_200:.0f}% of leading S&P 500 stocks trade above their 200-day average "
                             f"and {pct_50:.0f}% are above their 50-day average. "
                             "Wide participation confirms the uptrend and provides a strong tailwind for long positions."),
                    "sentiment": "pos",
                    "meta": f"Breadth: {pct_200:.0f}% >200d | {pct_50:.0f}% >50d",
                })
            elif b_score >= 5:
                rationale.append({
                    "src":  "Market Breadth",
                    "head": f"Healthy Market Breadth — {pct_200:.0f}% Above 200-DMA",
                    "body": (f"More than half of S&P 500 benchmark stocks trade above their 200-day average. "
                             "Market internals are constructive — the broad trend supports new longs."),
                    "sentiment": "pos",
                    "meta": f"Breadth: {pct_200:.0f}% >200d | {pct_50:.0f}% >50d",
                })
            elif b_score <= -10:
                rationale.append({
                    "src":  "Market Breadth",
                    "head": f"Market Breadth Deteriorating — Only {pct_200:.0f}% Above 200-DMA",
                    "body": (f"Fewer than 1 in 3 S&P 500 stocks trade above their 200-day average "
                             f"({pct_200:.0f}%). Broad market deterioration reduces the probability of "
                             "individual stock gains — favour defensive positioning or reduced exposure."),
                    "sentiment": "neg",
                    "meta": f"Breadth: {pct_200:.0f}% >200d | {pct_50:.0f}% >50d",
                })
            elif b_score <= -5:
                rationale.append({
                    "src":  "Market Breadth",
                    "head": f"Weakening Market Breadth — {pct_200:.0f}% Above 200-DMA",
                    "body": (f"Less than half of S&P 500 benchmark stocks are above their 200-day average. "
                             "Market internals are weakening — be selective with new long entries."),
                    "sentiment": "neg",
                    "meta": f"Breadth: {pct_200:.0f}% >200d | {pct_50:.0f}% >50d",
                })

        # ── Normalise gathered values ────────────────────────────────────────
        social       = social       or {}
        fundamentals = fundamentals or {}

        # ── Ichimoku Cloud ───────────────────────────────────────────────────
        ichi_tenkan    = tech.get("ichi_tenkan")
        ichi_kijun     = tech.get("ichi_kijun")
        ichi_tenkan_p  = tech.get("ichi_tenkan_p")
        ichi_kijun_p   = tech.get("ichi_kijun_p")
        ichi_cloud_top = tech.get("ichi_cloud_top")
        ichi_cloud_bot = tech.get("ichi_cloud_bot")
        ichi_cloud_bull = tech.get("ichi_cloud_bull")
        ichi_chikou    = tech.get("ichi_chikou_above")
        if ichi_tenkan and ichi_kijun:
            sources.add("Technical")
            # Tenkan/Kijun cross
            if (ichi_tenkan_p and ichi_kijun_p and
                    ichi_tenkan_p <= ichi_kijun_p and ichi_tenkan > ichi_kijun):
                ichimoku_score += 10
                rationale.append({"src": "Technical", "head": "Ichimoku Bullish Cross (TK Cross)",
                    "body": "Tenkan-sen crossed above Kijun-sen — a classic Ichimoku buy signal called the 'TK Cross'. Momentum has shifted bullish.",
                    "sentiment": "pos", "meta": f"Tenkan {ichi_tenkan:.2f} > Kijun {ichi_kijun:.2f}"})
            elif (ichi_tenkan_p and ichi_kijun_p and
                    ichi_tenkan_p >= ichi_kijun_p and ichi_tenkan < ichi_kijun):
                ichimoku_score -= 10
                rationale.append({"src": "Technical", "head": "Ichimoku Bearish Cross (Dead Cross)",
                    "body": "Tenkan-sen crossed below Kijun-sen — a classic Ichimoku sell signal. Momentum has shifted bearish.",
                    "sentiment": "neg", "meta": f"Tenkan {ichi_tenkan:.2f} < Kijun {ichi_kijun:.2f}"})
            # Price vs Cloud
            if ichi_cloud_top and ichi_cloud_bot:
                if price > ichi_cloud_top:
                    ichimoku_score += 8
                    rationale.append({"src": "Technical", "head": f"Price Above Ichimoku Cloud (${ichi_cloud_top:.2f})",
                        "body": f"Price is trading above the Kumo cloud — the Ichimoku trend filter is bullish. The cloud acts as strong support at ${ichi_cloud_bot:.2f}–${ichi_cloud_top:.2f}.",
                        "sentiment": "pos", "meta": f"Cloud: {ichi_cloud_bot:.2f}–{ichi_cloud_top:.2f} | {'Green (bullish)' if ichi_cloud_bull else 'Red (bearish)'}"})
                elif price < ichi_cloud_bot:
                    ichimoku_score -= 8
                    rationale.append({"src": "Technical", "head": f"Price Below Ichimoku Cloud (${ichi_cloud_bot:.2f})",
                        "body": f"Price is below the Kumo cloud — the Ichimoku trend filter is bearish. The cloud acts as resistance at ${ichi_cloud_bot:.2f}–${ichi_cloud_top:.2f}.",
                        "sentiment": "neg", "meta": f"Cloud: {ichi_cloud_bot:.2f}–{ichi_cloud_top:.2f}"})
            # Chikou confirmation — symmetric: confirm = ±4, contradict = ∓4
            if ichi_chikou is True:
                ichimoku_score += 4   # Chikou above price 26 bars ago: bullish
            elif ichi_chikou is False:
                ichimoku_score -= 4   # Chikou below price 26 bars ago: bearish

            # Apply Ichimoku system bucket cap: TK cross + cloud + chikou are three
            # readings from one indicator — prevent the system from triple-counting.
            # 0.85 discount: cloud position overlaps with SMA200/50 in ma_score.
            score += max(-14, min(14, ichimoku_score)) * 0.85

        # ── Chaikin Money Flow ───────────────────────────────────────────────
        # CMF and OBV both measure volume-weighted money flow direction.
        # Routed into volume_score (same bucket as OBV) so they contribute once.
        cmf      = tech.get("cmf")
        cmf_prev = tech.get("cmf_prev")
        change_pct_abs = abs(tech.get("change_pct", 0) or 0)
        if cmf is not None:
            sources.add("Technical")
            if cmf > 0.20:
                # Strong accumulation — boosted weight vs the 0.15 threshold
                volume_score += 10
                rationale.append({"src": "Technical", "head": f"CMF Strong Accumulation ({cmf:+.2f})",
                    "body": (f"CMF at {cmf:+.2f} — heavy institutional accumulation. "
                             "Money flow is well above the +0.1 threshold, confirming sustained smart-money buying."),
                    "sentiment": "pos", "meta": f"CMF(20) = {cmf:+.2f}"})
            elif cmf > 0.15:
                volume_score += 8
                # Stealth accumulation: strong CMF on a flat price = institutional buying quietly
                if change_pct_abs < 0.5:
                    volume_score += 4
                    rationale.append({"src": "Technical", "head": f"CMF Stealth Accumulation ({cmf:+.2f})",
                        "body": (f"CMF at {cmf:+.2f} while price is nearly flat ({tech.get('change_pct', 0):+.2f}%). "
                                 "Institutions are quietly accumulating without moving the price — a very reliable precursor to a breakout."),
                        "sentiment": "pos", "meta": f"CMF(20) = {cmf:+.2f} | Price flat"})
                else:
                    rationale.append({"src": "Technical", "head": f"Chaikin Money Flow Bullish ({cmf:+.2f})",
                        "body": f"CMF at {cmf:+.2f} — sustained accumulation. Money is flowing into this stock on high volume. Institutional buyers are active.",
                        "sentiment": "pos", "meta": f"CMF(20) = {cmf:+.2f}"})
            elif cmf > 0.05:
                volume_score += 4
                # CMF rising (accelerating) is better than stable
                if cmf_prev is not None and cmf > cmf_prev + 0.05:
                    volume_score += 2
            elif cmf < -0.20:
                volume_score -= 10
                rationale.append({"src": "Technical", "head": f"CMF Strong Distribution ({cmf:+.2f})",
                    "body": (f"CMF at {cmf:+.2f} — heavy institutional distribution. "
                             "Persistent outflows at this level signal sustained smart-money selling."),
                    "sentiment": "neg", "meta": f"CMF(20) = {cmf:+.2f}"})
            elif cmf < -0.15:
                volume_score -= 8
                if change_pct_abs < 0.5:
                    volume_score -= 3  # stealth distribution penalty
                    rationale.append({"src": "Technical", "head": f"CMF Stealth Distribution ({cmf:+.2f})",
                        "body": (f"CMF at {cmf:+.2f} while price is nearly flat. "
                                 "Institutions are quietly selling into price stability — bearish divergence."),
                        "sentiment": "neg", "meta": f"CMF(20) = {cmf:+.2f} | Price flat"})
                else:
                    rationale.append({"src": "Technical", "head": f"Chaikin Money Flow Bearish ({cmf:+.2f})",
                        "body": f"CMF at {cmf:+.2f} — sustained distribution. Money is flowing out of this stock. Institutional sellers are dominating.",
                        "sentiment": "neg", "meta": f"CMF(20) = {cmf:+.2f}"})
            elif cmf < -0.05:
                volume_score -= 4
                if cmf_prev is not None and cmf < cmf_prev - 0.05:
                    volume_score -= 2  # CMF accelerating downward

        # Apply CMF volume_score cap (second application after reset above).
        # CMF contributions are now capped at ±22 * 0.85 separately from the OBV
        # block — both families cap at the same limit but cannot stack.
        if not _is_low_atr:
            score += max(-22, min(22, volume_score)) * 0.85

        # ── VWAP Liquidity Filter ────────────────────────────────────────────
        # Rolling 20-day VWAP is the institutional "cost basis" line for the period.
        # Price below VWAP means the average participant is underwater — a structural
        # liquidity headwind for BUY signals (selling pressure from break-even sellers).
        # Exemption: mean-reversion / oversold plays legitimately buy below VWAP.
        vwap_20  = tech.get("vwap_20")
        vwap_pct = tech.get("vwap_pct")  # positive = above VWAP, negative = below
        if vwap_20 is not None and vwap_pct is not None:
            sources.add("Technical")
            is_oversold_play = rsi is not None and rsi < 35  # exempt mean-reversion
            if score > 0 and vwap_pct < -2.0 and not is_oversold_play:
                # BUY signal with price meaningfully below VWAP — liquidity headwind
                penalty = min(12, abs(vwap_pct) * 1.0)  # 1pt per % below, cap 12
                score  -= penalty
                rationale.append({"src": "Technical",
                    "head": f"Price Below 20-Day VWAP ({vwap_pct:+.1f}%) — Liquidity Headwind",
                    "body": (
                        f"Price is {abs(vwap_pct):.1f}% below the 20-day VWAP (${vwap_20:.2f}). "
                        "Participants who bought over the past 20 sessions are on average underwater, "
                        "creating overhead supply as they exit at break-even. "
                        "BUY signals below VWAP have lower win rates unless confirmed by volume expansion."
                    ),
                    "sentiment": "neg",
                    "meta": f"Price ${price:.2f} vs VWAP ${vwap_20:.2f} ({vwap_pct:+.1f}%)"})
            elif score > 0 and vwap_pct >= 1.0:
                # Price above VWAP: participants are in profit — less overhead supply
                bonus = min(5, vwap_pct * 0.4)
                score += bonus
                rationale.append({"src": "Technical",
                    "head": f"Price Above VWAP ({vwap_pct:+.1f}%) — Institutional Cost Basis Holds",
                    "body": (
                        f"Price is {vwap_pct:.1f}% above the 20-day VWAP (${vwap_20:.2f}). "
                        "The average participant over the last 20 sessions is in profit — "
                        "reduced overhead supply, supportive for continued upside."
                    ),
                    "sentiment": "pos",
                    "meta": f"Price ${price:.2f} vs VWAP ${vwap_20:.2f} ({vwap_pct:+.1f}%)"})

        # ── Donchian Channel Breakout ────────────────────────────────────────
        dc_high   = tech.get("donchian_high")
        dc_low    = tech.get("donchian_low")
        dc_high_p = tech.get("donchian_high_p")
        dc_low_p  = tech.get("donchian_low_p")
        if dc_high and dc_low and dc_high_p and dc_low_p:
            if price >= dc_high and price > dc_high_p:
                momentum_score += 10
                sources.add("Technical")
                rationale.append({"src": "Technical", "head": f"Donchian 20-Day High Breakout (${dc_high:.2f})",
                    "body": f"Price broke out above the 20-day Donchian channel high (${dc_high:.2f}). The original Turtle Trading breakout signal — momentum is accelerating.",
                    "sentiment": "pos", "meta": f"20d High = ${dc_high:.2f}"})
            elif price <= dc_low and price < dc_low_p:
                momentum_score -= 10
                sources.add("Technical")
                rationale.append({"src": "Technical", "head": f"Donchian 20-Day Low Breakdown (${dc_low:.2f})",
                    "body": f"Price broke below the 20-day Donchian channel low (${dc_low:.2f}). Classic momentum breakdown — selling pressure is accelerating.",
                    "sentiment": "neg", "meta": f"20d Low = ${dc_low:.2f}"})

        # ── Price Structure (HH/HL or LH/LL) ────────────────────────────────
        ps = tech.get("price_structure")
        if ps == "hh_hl":
            momentum_score += 7
            sources.add("Technical")
            rationale.append({"src": "Technical", "head": "Bullish Price Structure — Higher Highs & Higher Lows",
                "body": "Recent swing highs and lows are both ascending — the classic definition of an uptrend. Bias remains long until structure breaks.",
                "sentiment": "pos", "meta": "HH + HL pattern (20-bar)"})
        elif ps == "lh_ll":
            momentum_score -= 7
            sources.add("Technical")
            rationale.append({"src": "Technical", "head": "Bearish Price Structure — Lower Highs & Lower Lows",
                "body": "Recent swing highs and lows are both declining — the classic definition of a downtrend. Bias remains short until structure reverses.",
                "sentiment": "neg", "meta": "LH + LL pattern (20-bar)"})

        # ── Gap Analysis ─────────────────────────────────────────────────────
        gap_pct = tech.get("gap_pct")
        if gap_pct is not None and abs(gap_pct) >= 1.5:
            sources.add("Technical")
            if gap_pct >= 2.5:
                momentum_score += 8
                rationale.append({"src": "Technical", "head": f"Bullish Gap Up +{gap_pct:.1f}%",
                    "body": f"Today's open gapped {gap_pct:.1f}% above yesterday's close. Gaps of this size reflect strong institutional conviction — unfilled gaps above prior resistance are particularly bullish.",
                    "sentiment": "pos", "meta": f"Gap: +{gap_pct:.1f}%"})
            elif gap_pct <= -2.5:
                momentum_score -= 8
                rationale.append({"src": "Technical", "head": f"Bearish Gap Down {gap_pct:.1f}%",
                    "body": f"Today's open gapped {abs(gap_pct):.1f}% below yesterday's close. Downside gaps reflect urgent selling — institutional distribution overnight.",
                    "sentiment": "neg", "meta": f"Gap: {gap_pct:.1f}%"})
            elif 1.5 <= gap_pct < 2.5:
                momentum_score += 4
            elif -2.5 < gap_pct <= -1.5:
                momentum_score -= 4

        # ── Relative Volume (RVOL) — direction-aware ─────────────────────────
        # High volume on an up day confirms accumulation; on a down day it confirms
        # distribution. Blind positive bias removed.
        rvol = tech.get("rvol")
        change = tech.get("change", 0) or 0
        if rvol is not None and rvol >= 2.0:
            sources.add("Technical")
            if change >= 0:
                momentum_score += 5
                rationale.append({"src": "Technical", "head": f"Elevated Volume on Up Day ({rvol:.1f}×)",
                    "body": f"Today's volume is {rvol:.1f}× the 20-day average on a positive price day — institutional accumulation.",
                    "sentiment": "pos", "meta": f"RVOL = {rvol:.1f}×"})
            else:
                momentum_score -= 5
                rationale.append({"src": "Technical", "head": f"Elevated Volume on Down Day ({rvol:.1f}×)",
                    "body": f"Today's volume is {rvol:.1f}× the 20-day average on a negative price day — institutional distribution.",
                    "sentiment": "neg", "meta": f"RVOL = {rvol:.1f}×"})

        # Apply momentum family bucket cap: ROC10 + streak + Donchian + price
        # structure + gap + RVOL all confirm the same directional momentum.
        # ── Stretch / Momentum mutual exclusion ─────────────────────────────────
        # Mean-reversion and trend-continuation are contradictory theses.
        # When the stretched-price signal strongly dominates one direction, dampen
        # momentum signals running counter to it — they're the cause of the stretch,
        # not independent confirmation.  (0.4× instead of zero keeps a trace of the
        # momentum context in the rationale and score, just not at full weight.)
        _stretch_total = osc_score + mean_rev_score
        if _stretch_total < -12 and momentum_score > 0:
            # Strongly overbought (bearish stretch) but positive momentum: dampen
            momentum_score *= 0.4
        elif _stretch_total > 12 and momentum_score < 0:
            # Strongly oversold (bullish stretch) but negative momentum: dampen
            # (falling momentum created the oversold — don't let it double-penalise)
            momentum_score *= 0.4

        # Low-ATR: skip momentum family — breakout/momentum signals invalid on range-bound stocks.
        if not _is_low_atr:
            score += max(-26, min(26, momentum_score)) * 0.85

        # ── ADR Compression ──────────────────────────────────────────────────
        if tech.get("adr_compression"):
            adr = tech.get("adr_pct", 0)
            adr_hi = tech.get("adr_6m_high", adr)
            sources.add("Technical")
            rationale.append({"src": "Technical", "head": "Volatility Coiling — ADR% at 6-Month Low",
                "body": f"Average daily range compressed to {adr:.2f}% vs 6-month high of {adr_hi:.2f}%. Volatility compression historically precedes large directional moves. Watch for a Donchian or Bollinger breakout.",
                "sentiment": "neu", "meta": f"ADR = {adr:.2f}% (6M high: {adr_hi:.2f}%)"})

        # ── Supertrend(7, 3) ─────────────────────────────────────────────────
        st_dir      = tech.get("supertrend_dir",      0) or 0
        st_dir_prev = tech.get("supertrend_dir_prev", 0) or 0
        st_val      = tech.get("supertrend_val")
        if st_dir != 0:
            sources.add("Technical")
            flip_to_bull = st_dir == 1  and st_dir_prev == -1
            flip_to_bear = st_dir == -1 and st_dir_prev ==  1
            val_str      = f" ${st_val:.2f}" if st_val else ""
            if flip_to_bull:
                # Routed into momentum_score so Supertrend competes within the
                # momentum family cap (±26) alongside ROC, Donchian, streak, gap.
                momentum_score += 14; dominant = "macd"
                rationale.append({"src": "Technical",
                    "head": "Supertrend Bullish Flip ↑",
                    "body": (f"Supertrend(7,3) just flipped from bearish to bullish. "
                             f"The ATR-based trailing stop{val_str} now acts as dynamic support. "
                             "A fresh Supertrend flip is one of the cleanest momentum-reversal signals."),
                    "sentiment": "pos",
                    "meta": f"Supertrend flipped BULLISH{val_str}"})
            elif flip_to_bear:
                momentum_score -= 14; dominant = "macd"
                rationale.append({"src": "Technical",
                    "head": "Supertrend Bearish Flip ↓",
                    "body": (f"Supertrend(7,3) just flipped from bullish to bearish. "
                             f"The trailing stop{val_str} now acts as overhead resistance. "
                             "High-probability reversal with ATR-confirmed downside momentum."),
                    "sentiment": "neg",
                    "meta": f"Supertrend flipped BEARISH{val_str}"})
            elif st_dir == 1:
                momentum_score += 6
                rationale.append({"src": "Technical",
                    "head": f"Supertrend Bullish — ATR Support{val_str}",
                    "body": (f"Supertrend(7,3) is in bullish mode. Price is above its ATR-based "
                             f"trailing stop{val_str} — the trend is intact and stop is rising."),
                    "sentiment": "pos",
                    "meta": f"ST bullish{val_str}"})
            elif st_dir == -1:
                momentum_score -= 6
                rationale.append({"src": "Technical",
                    "head": f"Supertrend Bearish — ATR Resistance{val_str}",
                    "body": (f"Supertrend(7,3) is in bearish mode. Price is below its ATR-based "
                             f"trailing stop{val_str} — overhead resistance prevents sustained recoveries."),
                    "sentiment": "neg",
                    "meta": f"ST bearish{val_str}"})

        # ── Hurst Exponent — Regime Classification ────────────────────────────
        hurst = tech.get("hurst")
        if hurst is not None:
            sources.add("Technical")
            if hurst > 0.60:
                # Persistent trending regime — trust momentum signals more
                trend_bonus = 5 if score > 0 else (-5 if score < 0 else 0)
                score += trend_bonus
                rationale.append({"src": "Technical",
                    "head": f"Hurst Exponent {hurst:.2f} — Trending Regime",
                    "body": (f"Hurst exponent of {hurst:.2f} > 0.5 confirms persistent price momentum. "
                             "This stock is in a 'trending' state — breakout and momentum signals "
                             "carry higher win rates here than oscillator-based reversals."),
                    "sentiment": "pos" if score > 0 else "neg",
                    "meta": f"Hurst = {hurst:.2f} (>0.6 = strong trend)"})
            elif hurst < 0.40:
                # Anti-persistent mean-reverting regime — moderate strong directional signals
                if abs(score) > 15:
                    score *= 0.87
                rationale.append({"src": "Technical",
                    "head": f"Hurst Exponent {hurst:.2f} — Mean-Reverting Regime",
                    "body": (f"Hurst exponent of {hurst:.2f} < 0.5 indicates anti-persistent "
                             "price behaviour — recent trends are likely to reverse. "
                             "Momentum/breakout signals are suspect; oversold/overbought reversals are more reliable."),
                    "sentiment": "neu",
                    "meta": f"Hurst = {hurst:.2f} (<0.4 = mean-reverting)"})

        # ── Fractal Dimension Index — Donchian & Bollinger regime filter ─────────
        # FDI complements Hurst: while Hurst uses variance scaling, FDI uses the ratio
        # of the total price path length to the period's high-low range. Together they
        # provide two independent regime readings from different mathematical approaches.
        fdi = tech.get("fdi")
        if fdi is not None:
            sources.add("Technical")
            if fdi < 1.25:
                # Low fractal dimension — nearly linear trend; breakouts are reliable
                fdi_bonus = 5 if score > 0 else (-5 if score < 0 else 0)
                score += fdi_bonus
                rationale.append({"src": "Technical",
                    "head": f"FDI {fdi:.2f} — Trending Market (Trust Breakouts)",
                    "body": (f"Fractal Dimension Index of {fdi:.2f} is well below 1.5 — price is "
                             "moving in a linear, directional fashion. Donchian and Bollinger breakout "
                             "signals are more reliable in this low-fractal regime."),
                    "sentiment": "pos" if score > 0 else "neg",
                    "meta": f"FDI = {fdi:.2f} (<1.25 = trending)"})
            elif fdi > 1.45:
                # High fractal dimension — choppy; breakouts are traps
                if abs(score) > 15:
                    score *= 0.88
                rationale.append({"src": "Technical",
                    "head": f"FDI {fdi:.2f} — Choppy Market (Fade Breakouts)",
                    "body": (f"Fractal Dimension Index of {fdi:.2f} indicates fractal, "
                             "non-directional price action. Breakout signals are more likely to fail — "
                             "mean-reversion setups and oscillator signals are preferred."),
                    "sentiment": "neu",
                    "meta": f"FDI = {fdi:.2f} (>1.45 = choppy)"})

        # ── VIX Term Structure (from macro context) ──────────────────────────
        vix_ratio = (market_ctx or {}).get("macro", {}).get("vix_term_ratio") if market_ctx else None
        if vix_ratio is None and market_ctx:
            vix_ratio = (market_ctx.get("macro") or {}).get("vix_term_ratio")

        # ── VIX9D — Near-Term Event Risk ─────────────────────────────────────
        _macro_now = (market_ctx or {}).get("macro") or {}
        _vix9d_ratio = _macro_now.get("vix9d_ratio")
        if _vix9d_ratio is not None and _vix9d_ratio > 1.10 and action in ("BUY", "SELL"):
            _vix9d = _macro_now.get("vix9d", 0)
            confidence = round(max(35.0, confidence - 4), 1)
            sources.add("Macro")
            rationale.append({"src": "Macro",
                "head": f"Near-Term Event Risk (VIX9D/VIX {_vix9d_ratio:.2f}×) — Confidence −4pp",
                "body": (f"9-day VIX ({_vix9d:.1f}) is {_vix9d_ratio:.2f}× the spot VIX. "
                         "Near-term options demand is concentrated — a known upcoming event (earnings, "
                         "FOMC, CPI) is distorting short-horizon signals. Wait for post-event clarity "
                         "before acting on this signal."),
                "sentiment": "neg", "meta": f"VIX9D/VIX = {_vix9d_ratio:.2f}×"})

        # ── MOVE Index — Bond Market Stress ──────────────────────────────────
        _move = _macro_now.get("move")
        if _move is not None and _move > 140 and action == "BUY":
            confidence = round(max(35.0, confidence - 5), 1)
            sources.add("Macro")
            rationale.append({"src": "Macro",
                "head": f"Treasury Vol Stress (MOVE {_move:.0f}) — Confidence −5pp",
                "body": (f"CBOE MOVE Index at {_move:.0f} — bond market implied vol is highly elevated. "
                         "Elevated MOVE historically leads equity drawdowns by 2–3 weeks. "
                         "Reduce position sizing until MOVE normalises below 120."),
                "sentiment": "neg", "meta": f"^MOVE = {_move:.0f}"})

        # ── STLFSI4 — Financial Stress (macro signal into single-stock) ───────
        # Already scored globally in macro.py; here we apply a confidence cap
        # when stress is extreme to prevent overconfident single-stock BUYs.
        _stlfsi = _macro_now.get("stlfsi")
        if _stlfsi is not None and _stlfsi > 1.0 and action == "BUY":
            confidence = round(min(confidence, 58.0), 1)
            sources.add("Macro")
            rationale.append({"src": "Macro",
                "head": f"Financial Stress Override (STLFSI4 {_stlfsi:+.2f}) — BUY Cap 58%",
                "body": (f"St. Louis Financial Stress Index at {_stlfsi:+.2f} (>1.0 = crisis). "
                         "In high-stress regimes, even strong individual-stock setups frequently fail "
                         "because correlated forced selling overrides fundamentals. BUY confidence "
                         "capped at 58% until FSI returns below 0.5."),
                "sentiment": "neg", "meta": f"STLFSI4 = {_stlfsi:+.3f}"})

        # ── Consumer Sentiment Sector Penalty (UMCSENT) ───────────────────────
        _umcsent = _macro_now.get("umcsent")
        _sector_etf = (sector_rs or {}).get("sector_etf", "")
        _consumer_sectors = {"XLY", "XLP", "XLC"}
        if (_umcsent is not None and _umcsent < 60
                and action == "BUY" and _sector_etf in _consumer_sectors):
            score -= 3
            sources.add("Macro")
            rationale.append({"src": "Macro",
                "head": f"Consumer Distress Headwind (UMCSENT {_umcsent:.1f})",
                "body": (f"U. Michigan Consumer Sentiment at {_umcsent:.1f} — historically distressed "
                         f"(avg ~85). {_sector_etf} sector stocks face direct demand headwind when "
                         "household confidence is this weak. XLY/XLC/XLP names are first to reprice."),
                "sentiment": "neg", "meta": f"UMCSENT={_umcsent:.1f} | sector={_sector_etf}"})

        # ── Yield Curve (from macro context) ────────────────────────────────
        yc_spread = ((market_ctx or {}).get("macro") or {}).get("yc_spread")
        if yc_spread is not None and abs(yc_spread) > 0.5 and yc_spread not in [None]:
            # Already scored in macro.py and passed via macro_score — just add rationale if not yet present
            pass  # macro.py handles the scoring; we just avoid double-counting

        # ── DXY Impact ───────────────────────────────────────────────────────
        dxy_1m = ((market_ctx or {}).get("macro") or {}).get("dxy_1m")
        if dxy_1m is not None and abs(dxy_1m) >= 2.5:
            # DXY impact is sector-conditional
            # Get sector from sector_rs if available
            sector_etf = (sector_rs or {}).get("sector_etf", "")
            sources.add("Macro")
            int_sectors  = {"XLK", "XLV", "XLY", "XLC"}  # multinationals — hurt by strong $
            dom_sectors  = {"XLU", "XLF", "XLRE"}          # domestic — less affected
            comm_sectors = {"XLB", "XLE"}                  # commodities — hurt by strong $
            if dxy_1m > 2.5:  # strengthening dollar
                if sector_etf in int_sectors or sector_etf in comm_sectors:
                    score -= 5
                    rationale.append({"src": "Macro", "head": f"Strong Dollar Headwind (+{dxy_1m:.1f}% DXY)",
                        "body": f"The US Dollar Index rose {dxy_1m:.1f}% over the past month. A stronger dollar reduces overseas revenue and compresses commodity prices — headwind for this sector.",
                        "sentiment": "neg", "meta": f"DXY 1M = +{dxy_1m:.1f}%"})
            elif dxy_1m < -2.5:  # weakening dollar
                if sector_etf in int_sectors or sector_etf in comm_sectors:
                    score += 5
                    rationale.append({"src": "Macro", "head": f"Weak Dollar Tailwind ({dxy_1m:.1f}% DXY)",
                        "body": f"The US Dollar Index fell {abs(dxy_1m):.1f}% over the past month. A weaker dollar boosts overseas earnings when translated back to USD — tailwind for this sector.",
                        "sentiment": "pos", "meta": f"DXY 1M = {dxy_1m:.1f}%"})

        # ── NAAIM Exposure Index (from market context, key="aaii") ───────────
        aaii = (market_ctx or {}).get("aaii")
        if aaii and aaii.get("signal") != "neutral" and aaii.get("score"):
            a_score  = aaii["score"]
            exposure = aaii.get("exposure", 50)
            pct_rank = aaii.get("pct_rank")
            rank_str = f" | 52w pct rank: {pct_rank:.0f}%" if pct_rank is not None else ""
            score   += a_score
            sources.add("Market Sentiment")
            if a_score >= 8:
                rationale.append({"src": "Market Sentiment",
                    "head": f"NAAIM: Managers Extremely Defensive ({exposure:.0f}% Exposed)",
                    "body": (f"Active managers have only {exposure:.0f}% equity exposure — well below average. "
                             "When professionals are this defensive, mean-reversion rallies tend to be sharp as they scramble to cover underexposure."),
                    "sentiment": "pos", "meta": f"NAAIM = {exposure:.1f}%{rank_str}"})
            elif a_score >= 4:
                rationale.append({"src": "Market Sentiment",
                    "head": f"NAAIM: Below-Average Equity Exposure ({exposure:.0f}%)",
                    "body": f"Active managers are {exposure:.0f}% exposed to equities — below the historical average (~65%). Defensive positioning leaves room for a buy-in rally.",
                    "sentiment": "pos", "meta": f"NAAIM = {exposure:.1f}%{rank_str}"})
            elif a_score <= -8:
                rationale.append({"src": "Market Sentiment",
                    "head": f"NAAIM: Managers Fully Invested ({exposure:.0f}% Exposed)",
                    "body": (f"Active managers are {exposure:.0f}% exposed to equities — near maximum. "
                             "When professionals are this fully invested, there is limited incremental buying power left to drive prices higher."),
                    "sentiment": "neg", "meta": f"NAAIM = {exposure:.1f}%{rank_str}"})
            elif a_score <= -4:
                rationale.append({"src": "Market Sentiment",
                    "head": f"NAAIM: Elevated Equity Positioning ({exposure:.0f}%)",
                    "body": f"Active managers are {exposure:.0f}% exposed — above-average positioning. Crowded long positioning reduces the marginal buyer pool.",
                    "sentiment": "neg", "meta": f"NAAIM = {exposure:.1f}%{rank_str}"})

        # ── COT (Commitment of Traders) ──────────────────────────────────────
        cot = (market_ctx or {}).get("cot")
        if cot and cot.get("signal") != "neutral" and cot.get("score"):
            c_score  = cot["score"]
            net_pct  = cot["net_pct"]
            score   += c_score
            sources.add("Market Sentiment")
            if c_score >= 8:
                rationale.append({"src": "Market Sentiment", "head": f"COT: Leveraged Funds Extremely Short S&P ({net_pct:+.0f}%)",
                    "body": f"CFTC COT report shows leveraged funds are {abs(net_pct):.0f}% net short S&P 500 futures. Historically, when fast money is this short, the market bounces sharply — a classic short-squeeze setup.",
                    "sentiment": "pos", "meta": f"COT net: {net_pct:+.0f}%"})
            elif c_score >= 4:
                rationale.append({"src": "Market Sentiment", "head": f"COT: Leveraged Funds Net Short S&P ({net_pct:+.0f}%)",
                    "body": f"CFTC COT shows leveraged funds leaning short on S&P 500 futures. Mild contrarian tailwind.",
                    "sentiment": "pos", "meta": f"COT net: {net_pct:+.0f}%"})
            elif c_score <= -8:
                rationale.append({"src": "Market Sentiment", "head": f"COT: Leveraged Funds Extremely Long S&P ({net_pct:+.0f}%)",
                    "body": f"CFTC COT shows leveraged funds {net_pct:.0f}% net long S&P 500 futures. Crowded long positioning often precedes reversals.",
                    "sentiment": "neg", "meta": f"COT net: {net_pct:+.0f}%"})
            elif c_score <= -4:
                rationale.append({"src": "Market Sentiment", "head": f"COT: Leveraged Funds Net Long S&P ({net_pct:+.0f}%)",
                    "body": f"Leveraged funds are net long S&P futures — mild contrarian warning signal.",
                    "sentiment": "neg", "meta": f"COT net: {net_pct:+.0f}%"})

        # ── Piotroski F-Score ───────────────────────────────────────────────
        f_score = fundamentals.get("piotroski_f")
        if f_score is not None:
            sources.add("Fundamentals")
            if f_score >= 7:
                score += 12
                rationale.append({"src": "Fundamentals", "head": f"Piotroski F-Score {f_score}/9 — Financially Strong",
                    "body": f"Piotroski F-Score of {f_score}/9: company scores strongly across profitability, leverage, and efficiency tests. High-F-score stocks outperform low-F-score stocks by 7–9% annually in academic studies.",
                    "sentiment": "pos", "meta": f"F-Score: {f_score}/9"})
            elif f_score >= 5:
                score += 5
            elif f_score <= 2:
                score -= 10
                rationale.append({"src": "Fundamentals", "head": f"Piotroski F-Score {f_score}/9 — Financially Weak",
                    "body": f"Piotroski F-Score of only {f_score}/9: poor profitability, increasing leverage, and deteriorating efficiency. Low-F-score stocks are academic short candidates.",
                    "sentiment": "neg", "meta": f"F-Score: {f_score}/9"})
            elif f_score <= 4:
                score -= 4

        # ── Free Cash Flow Yield ─────────────────────────────────────────────
        fcf_yield = fundamentals.get("fcf_yield")
        if fcf_yield is not None:
            sources.add("Fundamentals")
            if fcf_yield > 8:
                score += 8
                rationale.append({"src": "Fundamentals", "head": f"Strong FCF Yield {fcf_yield:.1f}%",
                    "body": f"Free cash flow yield of {fcf_yield:.1f}% — substantially above current Treasury rates. The company generates enough cash to fund growth, buybacks, or dividends without new debt.",
                    "sentiment": "pos", "meta": f"FCF Yield: {fcf_yield:.1f}%"})
            elif fcf_yield > 4:
                score += 4
            elif fcf_yield < 0:
                score -= 6
                rationale.append({"src": "Fundamentals", "head": "Negative Free Cash Flow",
                    "body": "Company is burning more cash than it generates from operations. Requires external financing (debt or equity) to fund operations. Higher risk.",
                    "sentiment": "neg", "meta": f"FCF Yield: {fcf_yield:.1f}%"})

        # ── Revenue Growth Acceleration ──────────────────────────────────────
        rev_acc = fundamentals.get("rev_accelerating")
        g1      = fundamentals.get("rev_growth_q1")
        g2      = fundamentals.get("rev_growth_q2")
        if rev_acc is not None and g1 is not None and g2 is not None:
            sources.add("Fundamentals")
            if rev_acc and g1 > 5:
                score += 6
                rationale.append({"src": "Fundamentals", "head": f"Revenue Growth Accelerating (+{g1:.1f}% QoQ)",
                    "body": f"Quarterly revenue growth accelerated from +{g2:.1f}% to +{g1:.1f}% QoQ. Acceleration is the CAN SLIM key metric — expanding revenues at an increasing rate signal a business in breakout mode.",
                    "sentiment": "pos", "meta": f"Rev growth: {g2:.1f}% → {g1:.1f}% QoQ"})
            elif not rev_acc and g1 < -2:
                score -= 5
                rationale.append({"src": "Fundamentals", "head": f"Revenue Growth Decelerating ({g1:.1f}% QoQ)",
                    "body": f"Revenue growth slowed from {g2:.1f}% to {g1:.1f}% QoQ. Decelerating growth often leads to multiple compression as analysts lower estimates.",
                    "sentiment": "neg", "meta": f"Rev growth: {g2:.1f}% → {g1:.1f}% QoQ"})

        # ── Earnings Torpedo — 3-Year Annual Revenue Acceleration ──────────────
        # Driehaus/O'Neil: 3 consecutive years of positive AND accelerating YoY growth
        # precedes institutional accumulation in 68% of cases. Uses annual Polygon data.
        try:
            from services.massive_ratios import get_annual_revenue_acceleration
            _annual = await get_annual_revenue_acceleration(ticker)
            if _annual.get("revenue_torpedo"):
                _growths = _annual.get("annual_rev_growth", [])
                sources.add("Fundamentals")
                score += 8
                _g_str = " → ".join(f"+{g:.1f}%" for g in reversed(_growths))
                rationale.append({"src": "Fundamentals",
                    "head": f"Earnings Torpedo — 3-Year Revenue Acceleration",
                    "body": (f"Annual revenue growth has accelerated for 3 consecutive years: {_g_str}. "
                             "This 'Earnings Torpedo' pattern (Driehaus/O'Neil) precedes institutional "
                             "accumulation in 68% of cases. Expanding revenues at an increasing rate "
                             "signal a business entering a breakout phase."),
                    "sentiment": "pos",
                    "meta": f"annual_rev_torpedo=True growth={_g_str}"})
        except Exception:
            pass

        # ── ROE Trend ────────────────────────────────────────────────────────
        roe_improving = fundamentals.get("roe_improving")
        roe_now       = fundamentals.get("roe_now")
        roe_prev      = fundamentals.get("roe_prev")
        if roe_improving is not None and roe_now is not None:
            sources.add("Fundamentals")
            if roe_improving and roe_now > 15:
                score += 5
                rationale.append({"src": "Fundamentals", "head": f"ROE Improving — {roe_now:.1f}%",
                    "body": f"Return on equity rose from {roe_prev:.1f}% to {roe_now:.1f}%. Improving ROE above 15% signals a company compounding capital at a healthy rate.",
                    "sentiment": "pos", "meta": f"ROE: {roe_prev:.1f}% → {roe_now:.1f}%"})
            elif not roe_improving and roe_now < roe_prev:
                delta = roe_prev - roe_now
                if delta > 5:
                    score -= 4
                    rationale.append({"src": "Fundamentals", "head": f"ROE Declining — {roe_now:.1f}%",
                        "body": f"Return on equity fell {delta:.1f}pp from {roe_prev:.1f}% to {roe_now:.1f}%. Declining ROE often precedes earnings disappointments.",
                        "sentiment": "neg", "meta": f"ROE: {roe_prev:.1f}% → {roe_now:.1f}%"})

        # ── ROE + Revenue/Earnings Growth (yfinance free fields) ─────────────
        # Supplement the Piotroski F-Score with real-time quality/growth metrics.
        # info["roe_yf"] = returnOnEquity (e.g. 1.41 = 141%); already fetched.
        roe_yf    = info.get("roe_yf")
        rev_grow  = info.get("revenue_growth")   # YoY e.g. 0.166 = 16.6%
        earn_grow = info.get("earnings_growth")  # YoY
        if roe_yf is not None and not _is_lev_etf:
            _roe_pct = roe_yf * 100
            if _roe_pct >= 40:
                score += 5
                sources.add("Fundamentals")
                rationale.append({"src": "Fundamentals",
                    "head": f"Exceptional ROE — {_roe_pct:.0f}%",
                    "body": (f"Return on equity of {_roe_pct:.0f}% — exceptional compounding machine. "
                             "Companies sustaining ROE >40% typically have durable moats (pricing power, "
                             "network effects, or capital-light models). Buffett threshold: >20%."),
                    "sentiment": "pos", "meta": f"ROE={_roe_pct:.0f}%"})
            elif _roe_pct >= 20:
                score += 3
                sources.add("Fundamentals")
                rationale.append({"src": "Fundamentals",
                    "head": f"High ROE — {_roe_pct:.0f}%",
                    "body": f"Return on equity of {_roe_pct:.0f}% — above the 20% quality threshold. Efficient capital allocation.",
                    "sentiment": "pos", "meta": f"ROE={_roe_pct:.0f}%"})
            elif _roe_pct < 0:
                score -= 3
                sources.add("Fundamentals")
                rationale.append({"src": "Fundamentals",
                    "head": f"Negative ROE — {_roe_pct:.0f}%",
                    "body": f"Return on equity is negative ({_roe_pct:.0f}%) — the company is destroying shareholder value.",
                    "sentiment": "neg", "meta": f"ROE={_roe_pct:.0f}%"})

        if rev_grow is not None and earn_grow is not None and not _is_lev_etf:
            _rev_pct  = rev_grow  * 100
            _earn_pct = earn_grow * 100
            if _rev_pct >= 20 and _earn_pct >= 20:
                score += 4
                sources.add("Fundamentals")
                rationale.append({"src": "Fundamentals",
                    "head": f"Dual Growth Acceleration — Rev +{_rev_pct:.0f}% / EPS +{_earn_pct:.0f}% YoY",
                    "body": (f"Revenue growing {_rev_pct:.0f}% and earnings growing {_earn_pct:.0f}% year-over-year. "
                             "Dual acceleration is a hallmark of companies in rapid scaling phases — "
                             "these are the setups institutional growth funds actively accumulate."),
                    "sentiment": "pos", "meta": f"rev_yoy={_rev_pct:.0f}% | earn_yoy={_earn_pct:.0f}%"})
            elif _rev_pct < 0 or _earn_pct < 0:
                _worst = min(_rev_pct, _earn_pct)
                score -= 3
                sources.add("Fundamentals")
                rationale.append({"src": "Fundamentals",
                    "head": f"Revenue/Earnings Contraction (Rev {_rev_pct:+.0f}% / EPS {_earn_pct:+.0f}%)",
                    "body": (f"At least one growth line is negative YoY — revenue {_rev_pct:+.0f}%, "
                             f"earnings {_earn_pct:+.0f}%. Contracting businesses face multiple compression "
                             "as growth investors exit."),
                    "sentiment": "neg", "meta": f"rev_yoy={_rev_pct:.0f}% | earn_yoy={_earn_pct:.0f}%"})

        # ── 12-1 Month Momentum Factor ────────────────────────────────────────
        # Cross-sectional momentum: 6-month return minus 3-month return (from
        # Finnhub basic_financials, appended to analyst_recs dict in news.py).
        # Approximates the academic 12-1 month factor without extra API cost.
        _mom_factor = (analyst_recs or {}).get("momentum_factor")
        _r26w       = (analyst_recs or {}).get("return_26w")
        if _mom_factor is not None and not _is_lev_etf:
            sources.add("Technicals")
            if _mom_factor >= 20:
                score += 5
                rationale.append({"src": "Technicals",
                    "head": f"Strong Price Momentum Factor (+{_mom_factor:.1f}%)",
                    "body": (f"6-month return of {_r26w:.1f}% with positive intermediate-term momentum. "
                             "The 12-1 month cross-sectional momentum factor is one of the most replicated "
                             "alpha sources in academic finance — high-momentum stocks persistently outperform."),
                    "sentiment": "pos", "meta": f"momentum_factor={_mom_factor:.1f}% | r26w={_r26w:.1f}%"})
            elif _mom_factor >= 8:
                score += 2
                rationale.append({"src": "Technicals",
                    "head": f"Positive Price Momentum (+{_mom_factor:.1f}%)",
                    "body": f"Intermediate-term momentum positive at {_mom_factor:.1f}%. Mild continuation signal.",
                    "sentiment": "pos", "meta": f"momentum_factor={_mom_factor:.1f}%"})
            elif _mom_factor <= -20:
                score -= 5
                rationale.append({"src": "Technicals",
                    "head": f"Strong Negative Momentum ({_mom_factor:.1f}%)",
                    "body": (f"6-month return of {_r26w:.1f}% with large negative momentum factor. "
                             "Low-momentum stocks systematically underperform — mean reversion is slow "
                             "and frequently interrupted by further deterioration."),
                    "sentiment": "neg", "meta": f"momentum_factor={_mom_factor:.1f}% | r26w={_r26w:.1f}%"})
            elif _mom_factor <= -8:
                score -= 2
                rationale.append({"src": "Technicals",
                    "head": f"Negative Price Momentum ({_mom_factor:.1f}%)",
                    "body": f"Intermediate-term momentum negative. Mild downtrend confirmation.",
                    "sentiment": "neg", "meta": f"momentum_factor={_mom_factor:.1f}%"})

        # ── Dividend Yield vs 10Y Rate (Polygon accurate TTM yield) ────────────
        # yfinance dividendYield is None for ~40% of tickers; Polygon gives exact amounts.
        # Try Polygon TTM amount first; fall back to yfinance.
        div_yield = fundamentals.get("div_yield_pct")
        t10y_rate = ((market_ctx or {}).get("macro") or {}).get("t10y")
        try:
            from services.massive_ratios import get_polygon_dividend_data
            _div_data = await get_polygon_dividend_data(ticker)
            _ttm_amount = _div_data.get("div_ttm_amount")
            if _ttm_amount and _ttm_amount > 0 and price and price > 0:
                div_yield = round(_ttm_amount / price * 100, 2)
            # Aristocrat bonus
            _aristo_years = _div_data.get("div_aristocrat_years", 0)
            _aristo_level = _div_data.get("div_aristocrat_level", "")
            if _aristo_level:
                sources.add("Fundamentals")
                _pts = {"King": 5, "Aristocrat": 4, "Achiever": 2}.get(_aristo_level, 0)
                score += _pts
                rationale.append({"src": "Fundamentals",
                    "head": f"Dividend {_aristo_level} — {_aristo_years} Years of Increases",
                    "body": (f"{ticker} has increased its annual dividend for {_aristo_years} consecutive years. "
                             f"Dividend {_aristo_level}s have structural shareholder return commitments that "
                             "reduce drawdown risk and attract income-focused institutional buyers."),
                    "sentiment": "pos",
                    "meta": f"div_{_aristo_level.lower()}={_aristo_years}yr +{_pts}pts"})
        except Exception:
            pass
        if div_yield and div_yield > 0 and t10y_rate:
            sources.add("Fundamentals")
            yield_gap = div_yield - t10y_rate
            if yield_gap > 1.0:
                score += 6
                rationale.append({"src": "Fundamentals", "head": f"Dividend Yield {div_yield:.1f}% > 10Y Treasury {t10y_rate:.1f}%",
                    "body": f"Stock yields {div_yield:.1f}% — {yield_gap:.1f}pp above the 10-year Treasury. When a blue chip yields more than risk-free bonds, yield-seeking demand increases.",
                    "sentiment": "pos", "meta": f"Yield gap: +{yield_gap:.1f}pp"})
            elif yield_gap < -2.0:
                score -= 3
                rationale.append({"src": "Fundamentals", "head": f"Bond Alternative More Attractive",
                    "body": f"10Y Treasury ({t10y_rate:.1f}%) significantly exceeds the stock's {div_yield:.1f}% dividend yield by {abs(yield_gap):.1f}pp. Risk-free alternative is compelling.",
                    "sentiment": "neg", "meta": f"Yield gap: {yield_gap:.1f}pp"})

        # ── Buyback Yield / Share Dilution ───────────────────────────────────
        bb_yield = fundamentals.get("buyback_yield")
        if bb_yield and bb_yield > 3:
            sources.add("Fundamentals")
            # Bonus reduced from +4 → +2: buybacks were an unconditional positive with
            # no negative counterpart, contributing to structural BUY bias.
            score += 2
            rationale.append({"src": "Fundamentals", "head": f"Active Share Buyback — {bb_yield:.1f}% Yield",
                "body": f"Company returned {bb_yield:.1f}% of market cap to shareholders through buybacks. Active repurchases signal management confidence and reduce the float — mechanically bullish.",
                "sentiment": "pos", "meta": f"Buyback yield: {bb_yield:.1f}%"})
        # Share dilution — counterpart to buyback yield.
        # Yfinance provides impliedSharesOutstanding / floatShares via the info dict.
        # A YoY share count increase >5% means the company is actively diluting holders.
        shares_growth = fundamentals.get("shares_growth_yoy")
        if shares_growth is not None and shares_growth > 5:
            sources.add("Fundamentals")
            score -= 4
            rationale.append({"src": "Fundamentals",
                "head": f"Share Dilution — Shares Outstanding +{shares_growth:.1f}% YoY",
                "body": (f"Shares outstanding grew {shares_growth:.1f}% YoY. Active share issuance "
                         "dilutes existing holders: per-share earnings, book value, and dividends all "
                         "shrink even if absolute profits are flat. Counter-signal to buyback yield."),
                "sentiment": "neg", "meta": f"Shares outstanding growth: +{shares_growth:.1f}% YoY"})

        # ── 10-K / 10-Q MD&A Delta Analysis ──────────────────────────────────
        # Compares current vs prior SEC filing MD&A language. New risk terms
        # (−pts) or removed bullish language (−pts) are leading indicators of
        # weakness before it appears in financials. Cached 24h per ticker.
        try:
            from services.edgar import get_mda_delta
            _mda = await get_mda_delta(ticker)
            _mda_score = _mda.get("score", 0)
            if abs(_mda_score) >= 2.0:
                sources.add("SEC EDGAR")
                score += _mda_score
                _mda_form   = _mda.get("form_type", "10-Q")
                _mda_reason = _mda.get("reason", "")
                rationale.append({"src": "SEC EDGAR",
                    "head": (f"{_mda_form} Language {'Improvement' if _mda_score > 0 else 'Deterioration'} "
                             f"({_mda_score:+.1f}pts)"),
                    "body": (f"Quarter-over-quarter MD&A text analysis: {_mda_reason}. "
                             f"Management language in SEC filings is a leading indicator — "
                             f"silently added risk terms or removed bullish guidance language "
                             f"precede reported fundamental deterioration by 1–2 quarters."),
                    "sentiment": "pos" if _mda_score > 0 else "neg",
                    "meta": f"mda_delta={_mda_score:+.1f} form={_mda_form}"})
        except Exception:
            pass

        # ── Supply Chain Alternative Data ────────────────────────────────────
        try:
            from services.supply_chain import get_supply_chain_score
            sc_score = get_supply_chain_score(ticker, (market_ctx or {}).get("supply_chain"))
            if abs(sc_score) >= 2.0:
                sources.add("Fundamentals")
                score += sc_score
                sc_dir = "positive" if sc_score > 0 else "negative"
                sc_data = (market_ctx or {}).get("supply_chain", {})
                bdi_val = sc_data.get("bdi", {})
                bdi_str = f"BDI {bdi_val.get('value', 'N/A')} ({bdi_val.get('chg_20d', 0):+.0f}% 20d)" if bdi_val else "BDI N/A"
                rationale.append({"src": "Fundamentals",
                    "head": f"Supply Chain Signal {sc_score:+.0f}pts — {sc_dir.capitalize()} for {ticker}",
                    "body": (f"Alternative supply chain data ({bdi_str}) indicates {sc_dir} conditions "
                             f"for this sector. Shipping/freight trends are leading indicators of revenue "
                             f"surprises for logistics, commodities, and retail tickers."),
                    "sentiment": "pos" if sc_score > 0 else "neg",
                    "meta": f"supply_chain_score={sc_score:+.1f}"})
        except Exception:
            pass

        # ── Corporate Events (Wall Street Horizon) ───────────────────────────
        try:
            from services.corporate_events import get_event_score, get_exdiv_blackout
            # Ex-dividend date hard blackout — price mechanically drops by dividend amount
            # on ex-date; Supertrend/MA signals are invalidated by this predictable drop.
            _is_exdiv, _exdiv_label = get_exdiv_blackout(ticker,
                                                          (market_ctx or {}).get("corporate_events"))
            if _is_exdiv:
                _force_hold = True
                sources.add("Risk Gate")
                rationale.append({"src": "Risk Gate",
                    "head": f"Ex-Dividend Date Blackout — {_exdiv_label}",
                    "body": ("Today is the ex-dividend date. The stock price will mechanically drop "
                             "by the dividend amount at open. Supertrend, moving averages, and breakout "
                             "signals are invalidated by this guaranteed drop. Signal blocked for today."),
                    "sentiment": "neg",
                    "meta": f"ex_div_blackout=True label={_exdiv_label}"})
            ev_score, ev_reasons = get_event_score(ticker, (market_ctx or {}).get("corporate_events"))
            if abs(ev_score) >= 2.0:
                sources.add("Fundamentals")
                score += ev_score
                for r in ev_reasons:
                    rationale.append({"src": "Fundamentals",
                        "head": f"Corporate Event: {r}",
                        "body": ("Upcoming corporate events carry a systematic price impact. "
                                 "Investor conferences / analyst days historically produce +1.5–2.5% "
                                 "median returns in the 3 days before the event as management "
                                 "presents to institutional buy-side."),
                        "sentiment": "pos" if ev_score > 0 else "neg",
                        "meta": f"event_score={ev_score:+.1f}"})
        except Exception:
            pass

        # ── ETF Fund Flows ────────────────────────────────────────────────────
        try:
            from services.etf_flows import get_flow_score_for_ticker
            etf_flow_score, etf_flow_reason = get_flow_score_for_ticker(
                ticker, (market_ctx or {}).get("etf_flows")
            )
            if abs(etf_flow_score) >= 2.0:
                sources.add("Institutional")
                score += etf_flow_score
                rationale.append({"src": "Institutional",
                    "head": f"ETF Fund Flow {etf_flow_score:+.1f}pts — {etf_flow_reason}",
                    "body": ("Institutional money flows at the sector ETF level lead individual stock "
                             "prices by 1–3 trading days. Strong inflows into the sector ETF signal "
                             "buy-side rotation into this area of the market."),
                    "sentiment": "pos" if etf_flow_score > 0 else "neg",
                    "meta": f"etf_flow_score={etf_flow_score:+.1f}"})
        except Exception:
            pass

        # ── Social Sentiment (StockTwits + Reddit WSB) ───────────────────────
        st_bull_pct = social.get("st_bull_pct")
        wsb_7d      = social.get("wsb_mentions_7d", 0)
        wsb_1d      = social.get("wsb_mentions_1d", 0)
        if st_bull_pct is not None and social.get("st_total", 0) >= 5:
            sources.add("Social")
            if st_bull_pct >= 90:
                # Extreme retail bullishness = contrarian SELL (euphoria top)
                soc_bucket -= 5
                rationale.append({"src": "Social", "head": f"StockTwits Extreme Bullishness ({st_bull_pct:.0f}%) — Contrarian Bearish",
                    "body": f"{st_bull_pct:.0f}% of StockTwits messages are bullish — near-euphoric retail sentiment. Historically extreme retail bullishness precedes short-term reversals.",
                    "sentiment": "neg", "meta": f"ST Bull: {st_bull_pct:.0f}% | {social.get('st_total',0)} messages"})
            elif st_bull_pct >= 75:
                soc_bucket += 4
                rationale.append({"src": "Social", "head": f"StockTwits Strongly Bullish ({st_bull_pct:.0f}%)",
                    "body": f"{st_bull_pct:.0f}% of StockTwits messages on ${ticker} are bullish. Elevated retail optimism can create near-term upside momentum.",
                    "sentiment": "pos", "meta": f"ST Bull: {st_bull_pct:.0f}% | {social.get('st_total',0)} messages"})
            elif st_bull_pct <= 10:
                # Extreme retail pessimism = contrarian BUY (capitulation)
                soc_bucket += 5
                rationale.append({"src": "Social", "head": f"StockTwits Extreme Bearishness ({st_bull_pct:.0f}% bull) — Contrarian Bullish",
                    "body": f"Only {st_bull_pct:.0f}% of StockTwits messages are bullish — near-capitulation retail sentiment. Extreme pessimism often marks near-term bottoms.",
                    "sentiment": "pos", "meta": f"ST Bull: {st_bull_pct:.0f}% | {social.get('st_total',0)} messages"})
            elif st_bull_pct <= 30:
                soc_bucket += 3
                rationale.append({"src": "Social", "head": f"StockTwits Bearish ({st_bull_pct:.0f}% bull) — Contrarian",
                    "body": f"Only {st_bull_pct:.0f}% of StockTwits messages are bullish. Retail pessimism is a mild contrarian buy indicator.",
                    "sentiment": "pos", "meta": f"ST Bull: {st_bull_pct:.0f}% | {social.get('st_total',0)} messages"})
        if wsb_1d >= 10:
            sources.add("Social")
            soc_bucket += 4
            rationale.append({"src": "Social", "head": f"Reddit WSB Mention Surge — {wsb_1d} Posts Today",
                "body": f"${ticker} mentioned in {wsb_1d} Reddit WSB posts in the past 24h ({wsb_7d} this week). Rising retail attention can drive short-term volume and volatility.",
                "sentiment": "pos", "meta": f"WSB: {wsb_1d} today | {wsb_7d} this week"})

        # ── Tier 6: Signal Clustering Boost ─────────────────────────────────
        # When ≥6 independent source CATEGORIES all agree with the dominant direction,
        # the conviction is significantly higher than the sum of parts.
        # Computed BEFORE orthogonality so the 12% boost applies to the pre-orthogonality
        # base score rather than cascading on top of the orthogonality inflation.
        agree_dir = "pos" if score > 0 else "neg"
        source_cats = {
            "TA":      any(r.get("src") == "Technical"        for r in rationale if r.get("sentiment") == agree_dir),
            "OPT":     any(r.get("src") == "Options"          for r in rationale if r.get("sentiment") == agree_dir),
            "INST":    any(r.get("src") in ("13F", "Dark Pool") for r in rationale if r.get("sentiment") == agree_dir),
            "INSIDE":  any(r.get("src") in ("Insider","SEC EDGAR") for r in rationale if r.get("sentiment") == agree_dir),
            "AN":      any(r.get("src") == "Analyst"          for r in rationale if r.get("sentiment") == agree_dir),
            "MACRO":   any(r.get("src") == "Macro"            for r in rationale if r.get("sentiment") == agree_dir),
            "SENT":    any(r.get("src") in ("Market Sentiment","Fear&Greed","Market Breadth") for r in rationale if r.get("sentiment") == agree_dir),
            "FUND":    any(r.get("src") == "Fundamentals"     for r in rationale if r.get("sentiment") == agree_dir),
            "SOCIAL":  any(r.get("src") == "Social"           for r in rationale if r.get("sentiment") == agree_dir),
            "EARN":    any(r.get("src") == "Earnings"         for r in rationale if r.get("sentiment") == agree_dir),
        }
        agreeing_cats = sum(source_cats.values())
        if agreeing_cats >= 6:
            # weight_overrides.cluster_boost_pct caps the multiplier (default 0.12 = 12%).
            # When the ticker's historical win rate is below 50%, the boost is halved —
            # source agreement does not compensate for a poor empirical track record.
            _wo         = (market_ctx or {}).get("weight_overrides", {})
            _ticker_wrs = ((market_ctx or {}).get("adaptive_weights") or {}).get("ticker_win_rates", {})
            _ticker_wr  = _ticker_wrs.get(ticker)
            _cluster_pct = float(_wo.get("cluster_boost_pct", 0.12))
            _wr_penalty  = ""
            if _ticker_wr is not None and _ticker_wr < 0.50:
                _cluster_pct = min(_cluster_pct, 0.06)
                _wr_penalty  = f" (capped: {ticker} win rate {_ticker_wr*100:.0f}%)"
            cluster_boost = round(score * _cluster_pct, 1)
            score += cluster_boost
            sources.add("Signal Cluster")
            rationale.append({"src": "Signal Cluster",
                "head": f"High-Conviction Signal — {agreeing_cats} Independent Categories Agree",
                "body": (f"{agreeing_cats} independent signal categories all point {'bullish' if agree_dir=='pos' else 'bearish'}: "
                         f"{', '.join(k for k,v in source_cats.items() if v)}. "
                         f"Cluster boost: {_cluster_pct*100:.0f}%.{_wr_penalty}"),
                "sentiment": agree_dir,
                "meta": f"{agreeing_cats} categories · boost {_cluster_pct*100:.0f}%{_wr_penalty}"})

        # ── Orthogonality Bonus — independent information sets converging ────────
        # Signals from fundamentally uncorrelated sources (different data pipelines,
        # different filing cadences, different market participants) carry greater
        # statistical weight than a second technical indicator reading the same price.
        # Reward convergence across truly independent sources.
        # Computed AFTER cluster so both rewards don't cascade multiplicatively.
        _agree = "pos" if score > 0 else "neg"
        _indep = {
            "13F":       any(r.get("src") == "13F"       and r.get("sentiment") == _agree for r in rationale),
            "Insider":   any(r.get("src") == "SEC EDGAR" and r.get("sentiment") == _agree for r in rationale),
            "Congress":  any(r.get("src") == "Insider"   and r.get("sentiment") == _agree for r in rationale),
            "Piotroski": any("Piotroski" in r.get("head","") and r.get("sentiment") == _agree for r in rationale),
            "Social":    any(r.get("src") == "Social"    and r.get("sentiment") == _agree for r in rationale),
            "Macro":     any(r.get("src") == "Macro"     and r.get("sentiment") == _agree for r in rationale),
            "Dark Pool": any(r.get("src") == "Dark Pool" and r.get("sentiment") == _agree for r in rationale),
            "Dark Pool": any(r.get("src") == "Dark Pool" and r.get("sentiment") == _agree for r in rationale),
        }
        _n_indep = sum(_indep.values())
        if _n_indep >= 2:
            # weight_overrides lets the owner cap these boosts without touching code.
            # Defaults: 3 pts/source, max +18. Both are reduced when ticker win rate < 50%.
            _wo              = (market_ctx or {}).get("weight_overrides", {})
            _ticker_wrs      = ((market_ctx or {}).get("adaptive_weights") or {}).get("ticker_win_rates", {})
            _ticker_wr       = _ticker_wrs.get(ticker)
            _orth_pts        = float(_wo.get("orthogonality_pts", 3))
            _orth_max        = float(_wo.get("orthogonality_max", 18))
            if _ticker_wr is not None and _ticker_wr < 0.50:
                # Ticker has a poor historical record — halve the orthogonality reward
                _orth_pts = min(_orth_pts, 1.5)
                _orth_max = min(_orth_max, 9)
            _orth_bonus = min(_orth_max, _n_indep * _orth_pts)
            score += _orth_bonus if score > 0 else (-_orth_bonus if score < 0 else 0)
            sources.add("Orthogonalization")
            _indep_names = ", ".join(k for k, v in _indep.items() if v)
            _wr_note = f" (ticker win rate {_ticker_wr*100:.0f}% — reduced bonus)" if (_ticker_wr is not None and _ticker_wr < 0.50) else ""
            rationale.append({"src": "Orthogonalization",
                "head": f"{_n_indep} Independent Sources Agree — Orthogonal Alpha",
                "body": (f"{_indep_names} all confirm the {'bullish' if _agree == 'pos' else 'bearish'} thesis "
                         "from uncorrelated data pipelines (filings, fundamentals, positioning, macro). "
                         f"Each source uses different information — convergence raises statistical confidence.{_wr_note}"),
                "sentiment": _agree,
                "meta": f"{_n_indep} independent sources: {_indep_names}{_wr_note}"})

        # ── Factor Mining Calibration ─────────────────────────────────────────
        # Apply small boosts/penalties from the weekly-mined OOS-Sharpe rankings.
        # Only fires when the current signal's active source set matches a known combo.
        # Capped at ±5 to avoid overriding the substantive indicators.
        fw = (market_ctx or {}).get("factor_weights", {})
        if fw and fw.get("top_factors") and abs(score) > 5:
            active_sources = set(sources)
            fm_adj  = 0.0
            fm_note = ""
            for fac in (fw.get("top_factors") or [])[:10]:
                fac_label    = fac.get("label", "")
                fac_sources  = set(fac_label.split("+"))
                oos_sharpe   = fac.get("oos_sharpe") or 0
                oos_wr       = fac.get("oos_win_rate") or 0.5
                if not fac_sources.issubset(active_sources):
                    continue
                if oos_sharpe > 1.0 and oos_wr > 0.60:
                    # Strong historically proven combo — small boost
                    adj = min(3.0, oos_sharpe * 1.0)
                    fm_adj  += adj
                    fm_note  = f"+{adj:.1f} ({fac_label} OOS Sharpe {oos_sharpe:.2f})"
                    break  # one match is enough
                elif oos_sharpe < 0.0 or oos_wr < 0.35:
                    # Historically poor combo — small penalty
                    adj = max(-3.0, oos_sharpe * 0.8)
                    fm_adj  += adj
                    fm_note  = f"{adj:.1f} ({fac_label} OOS Sharpe {oos_sharpe:.2f})"
                    break
            if abs(fm_adj) >= 1.0:
                fm_adj = max(-5.0, min(5.0, fm_adj))
                score += fm_adj if score > 0 else (-fm_adj if score < 0 else 0)
                sources.add("Backtest")
                rationale.append({"src": "Backtest",
                    "head": f"Factor Mining Calibration {'+' if fm_adj > 0 else ''}{fm_adj:.1f}",
                    "body": (f"Weekly factor mining found this source combination has a "
                             f"{'strong' if fm_adj > 0 else 'weak'} out-of-sample Sharpe ratio. "
                             f"Score adjusted {'+' if fm_adj > 0 else ''}{fm_adj:.1f}. {fm_note}"),
                    "sentiment": "pos" if fm_adj > 0 else "neg",
                    "meta": fm_note})

        # ── Tier 6: Regime-Conditional Weighting ─────────────────────────────
        # Symmetric: penalise counter-trend signals, boost with-trend signals.
        # Bear market: BUY haircut AND SELL boost. Bull market: SELL haircut AND BUY boost.
        sp500_trend = ((market_ctx or {}).get("macro") or {}).get("sp500_trend")
        if sp500_trend == "down":
            if score > 0:   # BUY against the bear trend — less reliable
                score *= 0.82
                rationale.append({"src": "Macro", "head": "Bear Market Regime — Long Signal Discounted",
                    "body": "S&P 500 is below its 50-day average. Counter-trend long signals carry lower win rates. Confidence reduced.",
                    "sentiment": "neg", "meta": "SPX < 50-DMA regime"})
            elif score < 0:  # SELL with the bear trend — more reliable
                score *= 1.10
        elif sp500_trend == "up":
            if score < 0:   # SELL against the bull trend — less reliable
                score *= 0.90
            elif score > 0:  # BUY with the bull trend — more reliable
                score *= 1.05

        # ── Earnings Estimate Revision Momentum ─────────────────────────────
        target_mean   = info.get("target_mean")
        analyst_count = info.get("analyst_count") or 0
        if target_mean and analyst_count >= 3 and price > 0:
            import time as _time_mod
            now_ts = _time_mod.time()
            prev = _analyst_cache.get(ticker, {})
            prev_mean  = prev.get("mean")
            prev_ts    = prev.get("ts", 0)
            prev_count = prev.get("count", analyst_count)
            
            # Invalidate stale cache entries (>1 hour old)
            if prev_ts and (now_ts - prev_ts) > _ANALYST_CACHE_TTL:
                prev_mean = None  # Force refresh
            
            _analyst_cache[ticker] = {"mean": target_mean, "count": analyst_count, "ts": now_ts}
            if prev_mean and prev_mean > 0:
                revision_pct = (target_mean - prev_mean) / prev_mean * 100
                count_grew   = analyst_count > prev_count
                if revision_pct > 5 and count_grew:
                    score += 8
                    sources.add("Analyst")
                    rationale.append({"src": "Analyst",
                        "head": f"Analyst Target Revised Up +{revision_pct:.1f}% — Positive Momentum",
                        "body": (f"Consensus price target upgraded from ${prev_mean:.2f} to ${target_mean:.2f} "
                                 f"(+{revision_pct:.1f}%) as analyst coverage expanded to {analyst_count}. "
                                 "Rising estimates with growing coverage is a strong leading indicator."),
                        "sentiment": "pos",
                        "meta": f"Target: ${prev_mean:.2f} → ${target_mean:.2f} | Analysts: {analyst_count}"})
                elif revision_pct > 5:
                    score += 5
                    sources.add("Analyst")
                    rationale.append({"src": "Analyst",
                        "head": f"Analyst Target Revised Up +{revision_pct:.1f}%",
                        "body": f"Consensus price target raised from ${prev_mean:.2f} to ${target_mean:.2f}. Positive estimate revision momentum tends to persist.",
                        "sentiment": "pos",
                        "meta": f"Target: ${prev_mean:.2f} → ${target_mean:.2f}"})
                elif revision_pct < -5:
                    score -= 6
                    sources.add("Analyst")
                    rationale.append({"src": "Analyst",
                        "head": f"Analyst Target Revised Down {revision_pct:.1f}%",
                        "body": (f"Consensus price target cut from ${prev_mean:.2f} to ${target_mean:.2f} "
                                 f"({revision_pct:.1f}%). Negative estimate revisions tend to cluster — where there's one cut, more often follow."),
                        "sentiment": "neg",
                        "meta": f"Target: ${prev_mean:.2f} → ${target_mean:.2f} | Analysts: {analyst_count}"})

        # ── Google Trends ────────────────────────────────────────────────────
        trends = trends or {}
        gt_score  = trends.get("score", 0)
        gt_chg    = trends.get("change_pct")
        gt_recent = trends.get("recent")
        if gt_score != 0 and gt_chg is not None:
            soc_bucket += gt_score
            sources.add("Social")
            if gt_score > 0:
                rationale.append({"src": "Social",
                    "head": f"Google Search Surge +{gt_chg:.0f}% — Retail FOMO Building",
                    "body": (f"Search volume for '{ticker} stock' jumped {gt_chg:.0f}% vs prior 4-week average "
                             f"(index: {gt_recent:.0f}/100). Rising retail attention typically precedes "
                             "near-term price momentum as new buyers enter the market."),
                    "sentiment": "pos",
                    "meta": f"Trends: +{gt_chg:.0f}% vs 4w avg | Score: {gt_recent:.0f}/100"})
            elif gt_score < 0:
                rationale.append({"src": "Social",
                    "head": f"Google Search Collapse {gt_chg:.0f}% — Retail Interest Fading",
                    "body": f"Search interest for '{ticker} stock' dropped {abs(gt_chg):.0f}% vs prior 4 weeks. Fading retail attention reduces the marginal buyer pool.",
                    "sentiment": "neg",
                    "meta": f"Trends: {gt_chg:.0f}% vs 4w avg"})

        # Apply social/retail sentiment bucket cap: StockTwits + WSB + Google Trends
        # all measure retail crowd direction — cap so the bucket contributes once.
        # 0.85 discount: retail sentiment is correlated with news sentiment already scored.
        score += max(-10, min(10, soc_bucket)) * 0.85

        # ── Congressional Trading (Quiverquant) ──────────────────────────────
        congress = congress or {}
        cg_score = congress.get("score", 0)
        cg_buys  = congress.get("buys", 0)
        cg_sells = congress.get("sells", 0)
        cg_net   = congress.get("net", 0)
        if cg_score != 0:
            score += cg_score
            sources.add("Insider")
            if cg_score > 0:
                recent_reps = ", ".join(b["rep"] for b in congress.get("recent_buys", [])[:2])
                rationale.append({"src": "Insider",
                    "head": f"Congressional Buying — {cg_buys} Purchase{'s' if cg_buys>1 else ''} (90d)",
                    "body": (f"{cg_buys} congressional purchase{'s' if cg_buys>1 else ''} vs {cg_sells} sale{'s' if cg_sells!=1 else ''} in the past 90 days. "
                             + (f"Buyers include: {recent_reps}. " if recent_reps else "")
                             + "Senators and representatives historically outperform the market by 6–12% annually."),
                    "sentiment": "pos",
                    "meta": f"Congress: {cg_buys} buys, {cg_sells} sells (90d)"})
            elif cg_score < 0:
                rationale.append({"src": "Insider",
                    "head": f"Congressional Selling — {cg_sells} Sale{'s' if cg_sells>1 else ''} (90d)",
                    "body": f"{cg_sells} congressional sale{'s' if cg_sells!=1 else ''} vs {cg_buys} purchase{'s' if cg_buys!=1 else ''} in the past 90 days. Net selling by politicians — who often have policy insight — is a caution flag.",
                    "sentiment": "neg",
                    "meta": f"Congress: {cg_buys} buys, {cg_sells} sells (90d)"})

        # ── Sector Rotation Bias ──────────────────────────────────────────────
        rotation = ((market_ctx or {}).get("macro") or {}).get("sector_rotation")
        if rotation and rotation.get("stage") and sector_rs:
            sector_etf = sector_rs.get("sector_etf", "")
            stage      = rotation["stage"]
            favoured   = rotation.get("favoured", [])
            avoid      = rotation.get("avoid", [])
            conf       = rotation.get("confidence", 0)
            if sector_etf and conf >= 50:
                sources.add("Macro")
                if sector_etf in favoured:
                    score += 6
                    rationale.append({"src": "Macro",
                        "head": f"Sector Rotation Tailwind — {sector_etf} Favoured in {stage.title()} Cycle",
                        "body": (f"Current macro indicators (yield curve, VIX, credit spreads, S&P trend) suggest a "
                                 f"'{stage}' economic cycle stage. {sector_etf} historically outperforms in this environment. "
                                 f"Sector rotation model confidence: {conf}%."),
                        "sentiment": "pos",
                        "meta": f"Cycle: {stage} | Favoured: {', '.join(favoured[:3])}"})
                elif sector_etf in avoid:
                    score -= 5
                    rationale.append({"src": "Macro",
                        "head": f"Sector Rotation Headwind — {sector_etf} Underperforms in {stage.title()} Cycle",
                        "body": (f"The '{stage}' cycle stage typically sees {sector_etf} underperform. "
                                 f"Capital tends to rotate toward: {', '.join(favoured[:3])}. "
                                 f"Model confidence: {conf}%."),
                        "sentiment": "neg",
                        "meta": f"Cycle: {stage} | Avoid: {', '.join(avoid[:3])}"})

        # ── Multi-timeframe confirmation (weekly + 1H) ───────────────────────
        # Weekly trend
        if weekly_trend == 1 and score > 0:
            score *= 1.10  # daily BUY confirmed by weekly uptrend
        elif weekly_trend == -1 and score > 0:
            score *= 0.70  # daily BUY against weekly downtrend
            rationale.append({"src": "Technical", "head": "Weekly Downtrend Conflict",
                "body": "Daily BUY signal contradicts the weekly downtrend. Price is below its 20-week average — counter-trend trades have lower win rates.",
                "sentiment": "neg", "meta": "Weekly SMA20 bearish"})
        elif weekly_trend == -1 and score < 0:
            score *= 1.10  # daily SELL confirmed by weekly downtrend
        elif weekly_trend == 1 and score < 0:
            score *= 0.75  # daily SELL against weekly uptrend

        # Apply weekly OHLCV trend strength (Polygon 26-week bars)
        if _weekly_ohlcv_score != 0:
            score += _weekly_ohlcv_score
            sources.add("Technical")
            if _weekly_ohlcv_score > 0:
                rationale.append({"src": "Technical",
                    "head": "Weekly OHLCV: Sustained Medium-Term Uptrend",
                    "body": "Price has been above its 13-week average in 8 or more of the last 10 weeks. Persistent weekly trend momentum reduces false signal rate in choppy markets.",
                    "sentiment": "pos", "meta": "Polygon 26-week bars: ≥8/10 weeks above SMA13"})
            else:
                rationale.append({"src": "Technical",
                    "head": "Weekly OHLCV: Sustained Medium-Term Downtrend",
                    "body": "Price has been below its 13-week average in 8 or more of the last 10 weeks. Persistent weekly bearish structure.",
                    "sentiment": "neg", "meta": "Polygon 26-week bars: ≥8/10 weeks below SMA13"})

        # 1H intraday timeframe confirmation — completes the 1D/1W/1H trifecta.
        # Requires RSI, MACD, and EMA all aligned on the 1H chart.
        try:
            if df_1h is not None and len(df_1h) >= 20:
                _1h_result = await asyncio.to_thread(_compute_1h_techs, df_1h)
                rsi_1h       = _1h_result["rsi_1h"]
                _macd_1h     = _1h_result["macd_1h"]
                _above_ema_1h = _1h_result["above_ema_1h"]

                h1_bullish = rsi_1h > 55 and _macd_1h > 0 and _above_ema_1h
                h1_bearish = rsi_1h < 45 and _macd_1h < 0 and not _above_ema_1h

                if score > 0 and h1_bullish:
                    score *= 1.08
                    sources.add("Technical")
                    rationale.append({"src": "Technical",
                        "head": f"1H Timeframe Confirms BUY (RSI {rsi_1h:.0f})",
                        "body": (f"1-hour chart is bullish: RSI {rsi_1h:.0f}, MACD positive, price above EMA20. "
                                 "All three timeframes (1D, 1W, 1H) align — highest conviction setup."),
                        "sentiment": "pos", "meta": f"1H RSI {rsi_1h:.0f} | MACD {'pos' if _macd_1h > 0 else 'neg'}"})
                elif score > 0 and h1_bearish:
                    score *= 0.82
                    sources.add("Technical")
                    rationale.append({"src": "Technical",
                        "head": f"1H Timeframe Contradicts BUY (RSI {rsi_1h:.0f})",
                        "body": (f"1-hour chart is bearish: RSI {rsi_1h:.0f}, MACD negative, price below EMA20. "
                                 "Short-term momentum conflicts with daily BUY — wait for 1H alignment."),
                        "sentiment": "neg", "meta": f"1H RSI {rsi_1h:.0f} | MACD {'pos' if _macd_1h > 0 else 'neg'}"})
                elif score < 0 and h1_bearish:
                    score *= 1.08  # more negative (confirmed bear)
                    sources.add("Technical")
                    rationale.append({"src": "Technical",
                        "head": f"1H Timeframe Confirms SELL (RSI {rsi_1h:.0f})",
                        "body": (f"1-hour chart is bearish: RSI {rsi_1h:.0f}, MACD negative, price below EMA20. "
                                 "All three timeframes align bearishly — high-conviction SELL setup."),
                        "sentiment": "neg", "meta": f"1H RSI {rsi_1h:.0f}"})
                elif score < 0 and h1_bullish:
                    score *= 0.82  # less negative (contradicted)
                    sources.add("Technical")
                    rationale.append({"src": "Technical",
                        "head": f"1H Timeframe Contradicts SELL (RSI {rsi_1h:.0f})",
                        "body": (f"1-hour chart is bullish while the daily is bearish. "
                                 "Intraday momentum conflicts with the daily SELL — reduce position or wait."),
                        "sentiment": "pos", "meta": f"1H RSI {rsi_1h:.0f}"})
        except Exception:
            pass  # 1H data unavailable or insufficient — degrade gracefully

        # ── Trend alignment gate (daily 200-DMA) ─────────────────────────────
        # Any BUY signal below the 200-DMA is a counter-trend trade — apply
        # a graded penalty: moderate (-15%) for stocks just under the line,
        # severe (-25%) for stocks deeply below it.
        if sma200:
            below_200_pct = (price / sma200 - 1) * 100
            if score > 0 and price < sma200:
                if below_200_pct < -3:  # deeply below — strong penalty
                    score *= 0.75
                    rationale.append({"src": "Technical", "head": "Counter-Trend BUY Warning",
                        "body": (f"BUY signal in a long-term downtrend. Price (${price:.2f}) is "
                                 f"{abs(below_200_pct):.1f}% below the 200-day MA (${sma200:.2f}). "
                                 "Only the highest-conviction reversals succeed here — reduce size."),
                        "sentiment": "neg", "meta": f"Price vs 200-DMA: {below_200_pct:.1f}%"})
                else:  # within 0–3% below — moderate penalty
                    score *= 0.87
                    rationale.append({"src": "Technical", "head": "200-DMA Trend Gate — Confidence Reduced",
                        "body": (f"BUY signal with price (${price:.2f}) just below the 200-day MA "
                                 f"(${sma200:.2f}). Trend-following BUY signals have lower win rates "
                                 "below this key long-term level. Conviction reduced."),
                        "sentiment": "neg", "meta": f"Price vs 200-DMA: {below_200_pct:.1f}%"})
            elif score < 0 and price > sma200 * 1.05:
                score *= 0.80  # SELL into strong uptrend — harder to play

        # ── Warning Signal De-confliction (Weighted Logic Gate) ─────────────
        # Certain "warning" signals should dynamically reduce position sizing/confidence
        # even if the overall direction is still BUY/SELL. This prevents contradictory
        # signals like "Stochastic Overbought" + "BUY" with high confidence.
        warning_signals = {
            "RSI Overbought", "RSI Elevated", "Stochastic Overbought",
            "Stochastic Bearish Cross (Overbought)", "Williams %R Overbought",
            "CCI Extreme Overbought", "MFI Overbought",
            "Broad Market Complacency", "Extreme Greed",
            "NAAIM: Managers Fully Invested",
        }
        warning_sell_signals = {
            "RSI Oversold", "RSI Weakening", "Stochastic Oversold",
            "Stochastic Bullish Cross (Oversold)", "Williams %R Oversold",
            "CCI Extreme Oversold", "MFI Oversold",
            "Extreme Fear", "Market Breadth Deteriorating",
            "NAAIM: Managers Extremely Defensive",
        }
        
        warning_penalty = 0.0
        warning_rationale = []
        for r in rationale:
            head = r.get("head", "")
            # For BUY signals, penalize overbought warnings.
            # Note: these signals already reduced score via osc_score, so the confidence
            # penalty is intentionally smaller (8%) — it reflects residual doubt that
            # persists even after the score-level penalty, not a second full deduction.
            if score > 0 and head in warning_signals:
                penalty = 0.08  # 8% confidence reduction (down from 15%)
                warning_penalty += penalty
                warning_rationale.append({
                    "src": "Risk Gate",
                    "head": f"Warning: {head}",
                    "body": f"This overbought condition reduces conviction in the BUY signal. Consider reducing position size.",
                    "sentiment": "neg",
                    "meta": f"Confidence penalty: -{penalty*100:.0f}%"
                })
            # For SELL signals, penalize oversold warnings
            elif score < 0 and head in warning_sell_signals:
                penalty = 0.08
                warning_penalty += penalty
                warning_rationale.append({
                    "src": "Risk Gate",
                    "head": f"Warning: {head}",
                    "body": f"This oversold condition reduces conviction in the SELL signal. Consider reducing position size.",
                    "sentiment": "neg",
                    "meta": f"Confidence penalty: -{penalty*100:.0f}%"
                })

        # Cap warning penalty at 20% (down from 30%); combine with other penalties
        warning_penalty = min(warning_penalty, 0.20)
        rationale.extend(warning_rationale)
        total_confidence_penalty = min(0.40, warning_penalty + vol_confidence_penalty
                                       + rs_confidence_penalty + insider_confidence_penalty)

        # ── Correlation-Based Portfolio Limits ──────────────────────────────
        # Suppress BUY signals when the paper portfolio already has too much
        # exposure in this ticker's sector (default threshold: 30% of portfolio).
        portfolio_ctx = (market_ctx or {}).get("portfolio_ctx", {})
        # ── PCA-based factor concentration haircut ──────────────────────────
        pca_risk = portfolio_ctx.get("pca_risk", {}) if portfolio_ctx else {}
        if pca_risk.get("concentration_warning") and score > 0:
            _pca_haircut = pca_risk.get("haircut_pct", 0) / 100.0
            if _pca_haircut > 0:
                total_confidence_penalty = min(0.50, total_confidence_penalty + _pca_haircut)
                _dom_factor = pca_risk.get("dominant_factor", "Unknown")
                _dom_exp    = pca_risk.get("dominant_exposure", 0)
                sources.add("Risk Gate")
                rationale.append({"src": "Risk Gate",
                    "head": f"PCA Factor Concentration — {_dom_factor} ({_dom_exp:.0%} exposure)",
                    "body": (f"Your portfolio's statistical risk is concentrated ({_dom_exp:.0%}) on "
                             f"the '{_dom_factor}' latent factor — detected via 2-factor PCA on "
                             f"60-day return correlations. GICS sector limits missed this overlap. "
                             f"Confidence reduced by {_pca_haircut*100:.0f}pp to limit factor crowding."),
                    "sentiment": "neg",
                    "meta": f"pca_factor={_dom_factor} exposure={_dom_exp:.0%} haircut={_pca_haircut*100:.0f}pp"})
        if portfolio_ctx and score > 0:
            sector_exposure = portfolio_ctx.get("sector_exposure", {})
            ticker_sector   = (sector_rs or {}).get("sector_etf") if sector_rs else None
            if ticker_sector and ticker_sector in sector_exposure:
                exposure_pct = sector_exposure[ticker_sector]
                # Configurable threshold — default 30%; hard suppress above 50%
                SOFT_LIMIT = 30.0
                HARD_LIMIT = 50.0
                if exposure_pct >= HARD_LIMIT:
                    score = 0
                    _force_hold = True   # portfolio hard limit — subsequent signals must not re-open
                    sources.add("Risk Gate")
                    rationale.append({
                        "src": "Risk Gate",
                        "head": f"Sector Exposure Limit Hit — {ticker_sector} {exposure_pct:.0f}% of Portfolio",
                        "body": (
                            f"Your paper portfolio already has {exposure_pct:.0f}% of its value in {ticker_sector} "
                            f"sector positions (hard limit: {HARD_LIMIT:.0f}%). "
                            "This BUY signal is suppressed to prevent concentration risk. "
                            "Close an existing position in this sector before adding more."
                        ),
                        "sentiment": "neg",
                        "meta": f"{ticker_sector} exposure: {exposure_pct:.0f}% > {HARD_LIMIT:.0f}% limit",
                    })
                elif exposure_pct >= SOFT_LIMIT:
                    # Soft limit: confidence haircut, not full suppression
                    haircut = min(0.25, (exposure_pct - SOFT_LIMIT) / (HARD_LIMIT - SOFT_LIMIT) * 0.25)
                    total_confidence_penalty = min(0.50, total_confidence_penalty + haircut)
                    sources.add("Risk Gate")
                    rationale.append({
                        "src": "Risk Gate",
                        "head": f"Sector Concentration Warning — {ticker_sector} {exposure_pct:.0f}% of Portfolio",
                        "body": (
                            f"Your paper portfolio has {exposure_pct:.0f}% of its value in {ticker_sector} "
                            f"(soft limit: {SOFT_LIMIT:.0f}%). "
                            "Adding here increases concentration risk. Confidence reduced by "
                            f"{haircut*100:.0f}%. Consider diversifying."
                        ),
                        "sentiment": "neg",
                        "meta": f"{ticker_sector} exposure: {exposure_pct:.0f}% (soft limit {SOFT_LIMIT:.0f}%)",
                    })

        # ── Merge worker results (concurrent scoring) ──────────────────────
        # Workers launched before TA scoring; we await them here. By this point
        # TA scoring is complete so workers had the full duration to run.
        # Each ScoringResult contributes score_delta, sources, and rationale cards.
        if _worker_task is not None:
            try:
                _worker_results = await asyncio.wait_for(_worker_task, timeout=0.5)
                # timeout=0.5: workers have had many seconds already; this is just
                # the final collect. A 0.5s grace period catches any still-running ones.
                for _wr in _worker_results:
                    if isinstance(_wr, Exception):
                        continue
                    if hasattr(_wr, "ok") and _wr.ok:
                        if not _force_hold:
                            score    += _wr.score
                        sources  |= _wr.sources
                        rationale += _wr.rationale
            except (asyncio.TimeoutError, Exception):
                # Workers already cancelled or timed out — proceed without them.
                # This guarantees signal generation is never blocked by worker latency.
                pass

        return _assemble_signal(
            ticker=ticker, info=info, tech=tech,
            score=score, rationale=rationale, sources=sources,
            _force_hold=_force_hold, _is_low_atr=_is_low_atr,
            _atr_pct_pre=_atr_pct_pre, total_confidence_penalty=total_confidence_penalty,
            avg_sent=avg_sent, price=price, atr=atr,
            market_ctx=market_ctx, earnings_cal=earnings_cal,
            sector_rs=sector_rs, days_to_earnings=days_to_earnings,
        )

    except Exception:
        log.exception("[signal_engine] %s: unhandled error in generate_signal", ticker)
        return None


async def scan_all(
    tickers: list[str],
    market_ctx: Optional[dict] = None,
    histories: Optional[dict] = None,
    infos: Optional[dict] = None,
) -> list[dict]:
    histories = histories or {}
    infos     = infos     or {}

    # Semaphore(5): max 5 concurrent signal generations to prevent API rate-limit hammering.
    # Expected: 154 tickers × 2.5s each → 385s sequential → ~77s with 5× parallelism.
    _sem = asyncio.Semaphore(5)

    async def _guarded(t: str):
        async with _sem:
            return await generate_signal(
                t,
                market_ctx=market_ctx,
                prefetched_df=histories.get(t),
                prefetched_info=infos.get(t),
            )

    results = await asyncio.gather(*[_guarded(t) for t in tickers], return_exceptions=True)
    signals = [r for r in results if r is not None and not isinstance(r, BaseException)]

    # ── Sector Peer Confirmation ─────────────────────────────────────────────
    # Layer 1: ETF sector peers (broad) — existing logic
    # Layer 2: Polygon related companies (narrow) — business competitors confirmed by Polygon
    sector_map: dict[str, list[dict]] = {}
    signals_by_ticker: dict[str, dict] = {s["ticker"]: s for s in signals}
    for sig in signals:
        etf = sig.get("sectorEtf")
        if etf:
            sector_map.setdefault(etf, []).append(sig)

    for sig in signals:
        if sig.get("action") != "BUY":
            continue
        etf = sig.get("sectorEtf")
        if not etf:
            continue
        peers = [s for s in sector_map.get(etf, []) if s["ticker"] != sig["ticker"]]
        if len(peers) < 2:
            continue  # not enough sector peers in watchlist to form a view

        bullish_peers = [p for p in peers if p.get("action") == "BUY"]
        n_peers       = min(len(peers), 3)   # judge against top-3
        n_bull        = len(bullish_peers)

        if n_bull < 2:
            peer_names = ", ".join(p["ticker"] for p in peers[:3])
            bull_names = ", ".join(p["ticker"] for p in bullish_peers) or "none"
            # Penalty scales with how isolated the signal is
            haircut = 12 if n_bull == 0 else 6
            sig["confidence"] = round(max(35.0, sig["confidence"] - haircut), 1)
            sig["rationale"] = list(sig.get("rationale", [])) + [{
                "src":  "Sector",
                "head": f"Sector Peers Not Confirming BUY — {n_bull}/{n_peers} Bullish ({etf})",
                "body": (
                    f"Of the {len(peers[:3])} {etf}-sector peers on the watchlist "
                    f"({peer_names}), only {n_bull} {'are' if n_bull != 1 else 'is'} bullish "
                    f"({bull_names}). "
                    "Stocks within a sector mean-revert to their cross-sectional correlation: "
                    "a lone-outlier BUY has a materially lower true-positive rate than a "
                    "sector-confirmed move. Confidence reduced."
                ),
                "sentiment": "neg",
                "meta": f"{etf}: {n_bull}/{n_peers} peers bullish | −{haircut}pp confidence",
            }]
            sig["sources"] = sorted(set(sig.get("sources", [])) | {"Sector"})

    # ── Layer 2: Polygon Related Companies peer check ─────────────────────────
    # Only run for high-confidence BUY signals (> 65%) to stay within rate limits
    try:
        from services.polygon_related import check_related_peer_confirmation
        high_conf_buys = [s for s in signals if s.get("action") == "BUY" and s.get("confidence", 0) > 65]
        for sig in high_conf_buys:
            adj, reason = await check_related_peer_confirmation(
                sig["ticker"], sig["action"], signals_by_ticker
            )
            if adj != 0.0:
                sig["confidence"] = round(max(35.0, min(72.0, sig["confidence"] + adj)), 1)
                sentiment = "pos" if adj > 0 else "neg"
                sig["rationale"] = list(sig.get("rationale", [])) + [{
                    "src":       "Sector",
                    "head":      f"Polygon Related Companies {'Confirm' if adj > 0 else 'Diverge'} ({adj:+.0f}pp)",
                    "body":      reason,
                    "sentiment": sentiment,
                    "meta":      f"related_adj={adj:+.1f}pp",
                }]
                sig["sources"] = sorted(set(sig.get("sources", [])) | {"Sector"})
    except Exception:
        pass

    # ── Supply Chain Graph Propagation ──────────────────────────────────────────
    # Second pass: check if a key supplier of each ticker has a strong signal.
    # TSM BUY → NVDA/AMD/QCOM get a small lead-lag boost; XOM SELL → airlines penalty.
    try:
        from services.supply_chain import get_supply_chain_propagation_score
        _sig_map = {s["ticker"]: s for s in signals}
        for sig in signals:
            sc_delta, sc_reason = get_supply_chain_propagation_score(
                sig["ticker"], _sig_map
            )
            if abs(sc_delta) >= 1.0:
                # Convert score delta to confidence adjustment (capped ±4pp)
                _conf_adj = max(-4.0, min(4.0, sc_delta * 0.5))
                sig["confidence"] = round(
                    max(35.0, min(72.0, sig["confidence"] + _conf_adj)), 1
                )
                sig["rationale"] = list(sig.get("rationale", [])) + [{
                    "src":       "Fundamentals",
                    "head":      f"Supply Chain Propagation ({sc_delta:+.1f}pts)",
                    "body":      (f"Key supplier signal propagated to {sig['ticker']}: "
                                  f"{sc_reason}. Supplier performance leads customer "
                                  f"revenue by 1–4 weeks in the semiconductor and "
                                  f"commodity cycles."),
                    "sentiment": "pos" if sc_delta > 0 else "neg",
                    "meta":      f"supply_chain_propagation={sc_delta:+.1f}",
                }]
                sig["sources"] = sorted(set(sig.get("sources", [])) | {"Fundamentals"})
    except Exception:
        pass

    # ── Cross-sectional universe ranking ──────────────────────────────────────
    # Rank every directional signal by confidence within this scan cycle.
    # Top decile (+3pp) and top quartile (+1.5pp) get a boost; bottom quartile
    # and bottom decile receive symmetric penalties. This converts the engine
    # from absolute scoring to relative scoring — what hedge funds actually use.
    # Requires ≥10 directional signals to be meaningful; smaller batches skip.
    try:
        _dir = [s for s in signals if s.get("action") in ("BUY", "SELL")]
        _n   = len(_dir)
        if _n >= 10:
            _sorted_idx = sorted(range(_n), key=lambda i: _dir[i]["confidence"])
            for _rank_pos, _idx in enumerate(_sorted_idx):
                sig  = _dir[_idx]
                _pct = _rank_pos / (_n - 1)          # 0.0 = weakest, 1.0 = strongest
                if _pct >= 0.90:
                    _adj, _label = 3.0,  "Top decile"
                elif _pct >= 0.75:
                    _adj, _label = 1.5,  "Top quartile"
                elif _pct <= 0.10:
                    _adj, _label = -3.0, "Bottom decile"
                elif _pct <= 0.25:
                    _adj, _label = -1.5, "Bottom quartile"
                else:
                    continue
                sig["confidence"] = round(max(35.0, min(72.0, sig["confidence"] + _adj)), 1)
                _pctile_int = round(_pct * 100)
                sig["rationale"] = list(sig.get("rationale", [])) + [{
                    "src":       "Cross-Sectional",
                    "head":      f"{_label} — {_pctile_int}th Percentile of {_n}-Signal Universe ({_adj:+.0f}pp)",
                    "body":      (f"Ranked against today's full {_n}-ticker scan universe: {_pctile_int}th "
                                  f"percentile. {_label} signals receive a {_adj:+.0f}pp confidence "
                                  "adjustment — the same relative-strength principle used in cross-sectional "
                                  "quant models to separate strongest from weakest setups each cycle."),
                    "sentiment": "pos" if _adj > 0 else "neg",
                    "meta":      f"universe_rank={_pctile_int}th | n={_n} | adj={_adj:+.0f}pp",
                }]
                sig["sources"] = sorted(set(sig.get("sources", [])) | {"Cross-Sectional"})
    except Exception:
        pass

    return signals
