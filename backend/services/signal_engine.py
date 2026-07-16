"""
Signal generation engine.

Per-scan market-wide context (Fear & Greed, Macro) is fetched ONCE by the
scanner and passed in via `market_ctx`.  Per-ticker data (technicals, news,
EDGAR insider activity) is fetched concurrently for each ticker.
"""

import asyncio
import logging
from datetime import datetime, timezone
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
    data_warnings: list[dict]


from services.google_trends import get_google_trends
from services.quiverquant import get_congress_signal
from services.signal_scoring import (
    score_ema_cross,
    score_macd,
    score_obv_adx,
    score_oscillators,
)

# ── BE-1 refactor: helpers + assembler moved to engines/ (re-exported here
#    for backward compatibility — external code imports them from this module).
from services.engines.helpers import (  # noqa: F401
    _LEVERAGED_ETFS,
    _SECTOR_MR_CONFIG,
    _current_session,
    _levels,
    _make_plain_english,
    _score_to_action,
)
from services.engines.assembler import _assemble_signal  # noqa: F401

_ET = pytz.timezone("America/New_York")

# ── Analyst target cache — Redis-backed to avoid split-brain across workers ──
# In multi-worker uvicorn each process has its own heap; a module-level dict
# silently gives different workers different revision baselines, generating
# spurious "target revised up" signals or missing genuine revisions entirely.
# Redis ensures all workers share one consistent view.
# If Redis is unavailable we log a warning and skip the revision check — we do
# NOT fall back to per-process dicts, because silent desync is worse than skipping.
_ANALYST_CACHE_TTL = 1800  # 30 minutes

_analyst_redis: "Optional[object]" = None
_analyst_redis_checked = False  # avoid repeated import attempts


def _get_analyst_redis():
    """Return a Redis client for analyst cache, or None if unavailable."""
    global _analyst_redis, _analyst_redis_checked
    if _analyst_redis_checked:
        return _analyst_redis
    _analyst_redis_checked = True
    try:
        import os
        import redis as _redis_lib

        _url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _r = _redis_lib.Redis.from_url(_url, socket_connect_timeout=1, socket_timeout=1, decode_responses=True)
        _r.ping()
        _analyst_redis = _r
        log.info("[signal_engine] analyst cache: Redis connected (%s)", _url)
    except Exception as _e:
        log.warning(
            "[signal_engine] analyst cache: Redis unavailable (%s) — revision signals DISABLED to prevent split-brain",
            _e,
        )
        _analyst_redis = None
    return _analyst_redis


def _analyst_cache_get(ticker: str) -> "Optional[dict]":
    r = _get_analyst_redis()
    if r is None:
        return None
    try:
        import json as _json

        raw = r.get(f"analyst:{ticker}")
        return _json.loads(raw) if raw else None
    except Exception as _e:
        log.debug("[signal_engine] analyst cache read error for %s: %s", ticker, _e)
        return None


def _analyst_cache_set(ticker: str, data: dict) -> None:
    r = _get_analyst_redis()
    if r is None:
        return
    try:
        import json as _json

        r.setex(f"analyst:{ticker}", _ANALYST_CACHE_TTL, _json.dumps(data))
    except Exception as _e:
        log.debug("[signal_engine] analyst cache write error for %s: %s", ticker, _e)


import pandas as pd

from services.earnings import get_earnings_calendar, get_earnings_surprise
from services.edgar import get_insider_activity
from services.fundamentals import get_fundamentals
from services.market_data import get_extended_hours_data, get_history, get_info
from services.news import get_analyst_recs, get_company_news
from services.news_scraper import get_scraped_news
from services.options import get_options_flow, score_options
from services.sector import get_sector_relative_strength
from services.social import get_social_sentiment
from services.technicals import calculate_indicators


def _collect_fetch_results(
    ticker: str,
    source_names: list[str],
    raw_results: list,
) -> tuple[list, list[dict]]:
    """Convert gather results to values plus structured provider warnings."""
    values = []
    warnings: list[dict] = []
    for source, result in zip(source_names, raw_results):
        if isinstance(result, BaseException):
            warnings.append(
                {
                    "source": source,
                    "error": type(result).__name__,
                    "message": str(result)[:160],
                }
            )
            log.debug(
                "[signal_engine] %s: %s fetch failed: %s: %s",
                ticker,
                source,
                type(result).__name__,
                str(result)[:160],
            )
            values.append(None)
        else:
            values.append(result)
    return values, warnings


async def _fetch_ticker_data(
    ticker: str,
    prefetched_df: Optional[pd.DataFrame],
    prefetched_info: Optional[dict],
) -> Optional[_TickerData]:
    """
    Fetch all per-ticker data concurrently.
    Returns a _TickerData namedtuple or None if df is invalid.
    """
    is_leveraged = ticker in _LEVERAGED_ETFS

    async def _dummy_dict(*args, **kwargs):
        return {}

    f_insider = _dummy_dict if is_leveraged else get_insider_activity
    f_analyst = _dummy_dict if is_leveraged else get_analyst_recs
    f_earnings_cal = _dummy_dict if is_leveraged else get_earnings_calendar
    f_earnings_surp = _dummy_dict if is_leveraged else get_earnings_surprise
    f_fundamentals = _dummy_dict if is_leveraged else get_fundamentals
    f_congress = _dummy_dict if is_leveraged else get_congress_signal

    if prefetched_df is not None:
        df = prefetched_df
        info = prefetched_info or {}
        _source_names = [
            "company_news",
            "scraped_news",
            "insider_activity",
            "analyst_recs",
            "earnings_calendar",
            "earnings_surprise",
            "options_flow",
            "fundamentals",
            "social_sentiment",
            "google_trends",
            "congress_signal",
            "history_1h",
            "extended_hours",
        ]
        _raw = await asyncio.gather(
            get_company_news(ticker, days=7),
            get_scraped_news(ticker, (prefetched_info or {}).get("company", ticker), days=7),
            f_insider(ticker, days=30),
            f_analyst(ticker),
            f_earnings_cal(ticker),
            f_earnings_surp(ticker),
            get_options_flow(ticker),
            f_fundamentals(ticker),
            get_social_sentiment(ticker),
            get_google_trends(ticker),
            f_congress(ticker),
            get_history(ticker, period="5d", interval="1h"),
            get_extended_hours_data(ticker),
            return_exceptions=True,
        )
        _values, data_warnings = _collect_fetch_results(ticker, _source_names, list(_raw))
        (
            news,
            scraped_news,
            insider,
            analyst_recs,
            earnings_cal,
            earnings_surp,
            opt_flow,
            fundamentals,
            social,
            trends,
            congress,
            df_1h,
            massive_sigs,
        ) = _values
        try:
            sector_rs = await get_sector_relative_strength(ticker, df)
        except Exception as exc:
            sector_rs = None
            data_warnings.append(
                {
                    "source": "sector_relative_strength",
                    "error": type(exc).__name__,
                    "message": str(exc)[:160],
                }
            )
            log.debug("[signal_engine] %s: sector_relative_strength fetch failed: %s", ticker, exc)
    else:
        _source_names = [
            "history_daily",
            "ticker_info",
            "company_news",
            "scraped_news",
            "insider_activity",
            "analyst_recs",
            "earnings_calendar",
            "earnings_surprise",
            "options_flow",
            "fundamentals",
            "social_sentiment",
            "google_trends",
            "congress_signal",
            "history_1h",
            "extended_hours",
        ]
        _raw = await asyncio.gather(
            get_history(ticker, period="1y", interval="1d"),
            get_info(ticker),
            get_company_news(ticker, days=7),
            get_scraped_news(ticker, "", days=7),
            f_insider(ticker, days=30),
            f_analyst(ticker),
            f_earnings_cal(ticker),
            f_earnings_surp(ticker),
            get_options_flow(ticker),
            f_fundamentals(ticker),
            get_social_sentiment(ticker),
            get_google_trends(ticker),
            f_congress(ticker),
            get_history(ticker, period="5d", interval="1h"),
            get_extended_hours_data(ticker),
            return_exceptions=True,
        )
        _values, data_warnings = _collect_fetch_results(ticker, _source_names, list(_raw))
        (
            df,
            info,
            news,
            scraped_news,
            insider,
            analyst_recs,
            earnings_cal,
            earnings_surp,
            opt_flow,
            fundamentals,
            social,
            trends,
            congress,
            df_1h,
            massive_sigs,
        ) = _values
        try:
            sector_rs = await get_sector_relative_strength(ticker, df)
        except Exception as exc:
            sector_rs = None
            data_warnings.append(
                {
                    "source": "sector_relative_strength",
                    "error": type(exc).__name__,
                    "message": str(exc)[:160],
                }
            )
            log.debug("[signal_engine] %s: sector_relative_strength fetch failed: %s", ticker, exc)

    if df is None or len(df) < 30:
        log.debug("[signal_engine] %s: insufficient daily history; signal skipped", ticker)
        return None
    info = info or {}

    return _TickerData(
        df=df,
        info=info,
        news=news,
        scraped_news=scraped_news,
        insider=insider,
        analyst_recs=analyst_recs,
        earnings_cal=earnings_cal,
        earnings_surp=earnings_surp,
        opt_flow=opt_flow,
        fundamentals=fundamentals,
        social=social,
        trends=trends,
        congress=congress,
        df_1h=df_1h,
        massive_sigs=massive_sigs,
        sector_rs=sector_rs,
        data_warnings=data_warnings,
    )


def _apply_q1_rebalancing(score: float, rationale: list, sector_etf: str | None, vix) -> tuple[float, list]:
    """
    RD-3 / §79: Q1 seasonal rebalancing bonus (Jan–Mar).

    In Jan–Mar, institutional portfolios rebalance toward sectors that
    underperformed the prior year.  Proxy: fetch prior-year sector ETF
    return from already-loaded macro/sector data.

    Implementation: called from generate_signal() in the scoring pass;
    adds +3pp score and a rationale card when:
      - Current month is Jan–Mar (Q1 rebalancing window)
      - sector_etf is known
      - VIX is not in stress territory (VIX < 30, to avoid false signals in crisis)

    Prior-year sector return is approximated by comparing the sector ETF
    close at the start of the year vs current price.  Full point-in-time
    implementation requires storing Dec-31 closing prices (deferred).
    """
    import datetime as _dt

    now = _dt.datetime.now()
    if not (1 <= now.month <= 3):
        return score, rationale
    if not sector_etf or sector_etf in ("Unknown", ""):
        return score, rationale
    if vix is not None and vix >= 30:
        return score, rationale  # stress regime — skip Q1 bonus

    # Apply +3pp with rationale card (prior-year return lookup deferred to market_data upgrade)
    score += 3
    rationale = rationale + [
        {
            "head": "§79 Q1 Rebalancing",
            "body": f"{sector_etf}: Q1 rebalancing window active (Jan–Mar). Institutional rebalancing inflow typically lifts prior-year laggards.",
            "pts": 3,
            "sentiment": "pos",
        }
    ]
    return score, rationale


def _compute_1h_techs(df_1h) -> dict:
    """CPU-bound 1H technical indicator computation — runs in a thread pool."""
    c1h = df_1h["Close"].astype(float)
    # RSI(14) on 1H
    _d = c1h.diff()
    _ag = _d.clip(lower=0).ewm(com=13, adjust=False).mean()
    _al = (-_d).clip(lower=0).ewm(com=13, adjust=False).mean()
    rsi_1h = float((100 - 100 / (1 + _ag / _al.replace(0, _np.nan))).iloc[-1])
    # MACD on 1H
    _macd_1h = float((c1h.ewm(span=12, adjust=False).mean() - c1h.ewm(span=26, adjust=False).mean()).iloc[-1])
    # Price vs EMA20 on 1H
    _above_ema_1h = float(c1h.iloc[-1]) > float(c1h.ewm(span=20, adjust=False).mean().iloc[-1])
    return {"rsi_1h": rsi_1h, "macd_1h": _macd_1h, "above_ema_1h": _above_ema_1h}


async def generate_signal(
    ticker: str,
    market_ctx: Optional[dict] = None,
    prefetched_df: Optional[pd.DataFrame] = None,
    prefetched_info: Optional[dict] = None,
    promoted_sectors: Optional[set[str]] = None,
) -> Optional[dict]:
    try:
        # Use pre-fetched batch data when available; fall back to individual fetches.
        _fetched = await _fetch_ticker_data(ticker, prefetched_df, prefetched_info)
        if _fetched is None:
            return None
        (
            df,
            info,
            news,
            scraped_news,
            insider,
            analyst_recs,
            earnings_cal,
            earnings_surp,
            opt_flow,
            fundamentals,
            social,
            trends,
            congress,
            df_1h,
            massive_sigs,
            sector_rs,
            data_warnings,
        ) = _fetched
        ext_hours = massive_sigs  # unified: both branches fetch get_extended_hours_data

        # Leveraged/inverse ETFs: company fundamentals, earnings, and insider
        # signals are meaningless — bypass them before any worker or scoring block
        # uses them. Technical, macro, and options signals still score normally.
        _is_lev_etf = ticker in _LEVERAGED_ETFS
        if _is_lev_etf:
            fundamentals = {}
            earnings_cal = {}
            earnings_surp = {}
            insider = {}
            analyst_recs = {}
            congress = {}

        # ── Ex-dividend proximity: find nearest upcoming ex-div date ─────────────
        # A stock drops by roughly the dividend amount on ex-div date — looks like
        # a panic dip to the MR scanner but is purely structural. Gate mirrors
        # the pre-earnings blackout. Skip for leveraged ETFs (no dividends).
        days_to_exdiv: Optional[int] = None
        if not _is_lev_etf:
            try:
                from services.polygon_client import get_polygon_dividends as _get_divs

                _today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                _divs = await asyncio.wait_for(_get_divs(ticker), timeout=3.0)
                for _d in _divs:
                    _ex = _d.get("ex_dividend_date") or ""
                    if _ex >= _today_str:
                        from datetime import date as _date

                        days_to_exdiv = (_date.fromisoformat(_ex) - datetime.now(timezone.utc).date()).days
                        break
            except Exception:
                log.warning("ex-dividend lookup failed for %s", ticker, exc_info=True)

        tech = calculate_indicators(df)
        # Reject non-finite price (NaN/Inf) as well as None: a corrupt OHLCV bar
        # can make calculate_indicators return price=NaN, which then poisons
        # change/change_pct and 500s JSON serialization downstream. A signal with
        # no valid price is meaningless — skip the ticker.
        if not tech or tech.get("price") is None or not _np.isfinite(tech["price"]):
            return None

        # ── Point-in-time momentum persistence (AR(1) on 126-day returns) ────────
        # AR(1) > 0 = positive autocorrelation = trending/momentum regime.
        # Used downstream to apply a dynamic confidence haircut on MR entries
        # for stocks that are currently trending rather than mean-reverting.
        # Replaces hardcoded backtest-derived exclusions with a live metric.
        try:
            import numpy as _np_ar1

            _rets_ar1 = df["Close"].pct_change().dropna().values
            if len(_rets_ar1) >= 60:
                _n_ar1 = min(126, len(_rets_ar1))
                _r_ar1 = _rets_ar1[-_n_ar1:]
                tech["momentum_ar1"] = float(_np_ar1.corrcoef(_r_ar1[:-1], _r_ar1[1:])[0, 1])
            else:
                tech["momentum_ar1"] = None
        except Exception:
            tech["momentum_ar1"] = None

        # ── Launch scoring workers concurrently (Event-Driven Microservices) ──────
        # Workers run in parallel while TA scoring executes below.
        # Each worker has its own timeout + circuit breaker — a slow Polygon call
        # or a rate-limited Finnhub response does not block RSI/MACD scoring.
        # Results are merged after the TA scoring phase completes.
        _price_now = tech.get("price", 0) or 0
        try:
            from services.signal_workers import (
                fundamentals_worker,
                institutional_worker,
                news_worker,
                options_worker,
                sentiment_worker,
            )

            _worker_task = asyncio.ensure_future(
                asyncio.gather(
                    news_worker(ticker, news, scraped_news),
                    fundamentals_worker(ticker, fundamentals, market_ctx, _price_now),
                    options_worker(ticker, opt_flow, massive_sigs),
                    institutional_worker(ticker, insider, market_ctx),
                    sentiment_worker(ticker, social, trends, congress),
                    return_exceptions=True,
                )
            )
        except Exception:
            _worker_task = None

        # ── Weekly trend (resample daily → weekly, no extra API call) ───────
        # Use only COMPLETED weeks (.iloc[:-1]) — the current calendar week may
        # be mid-week (e.g. Wednesday), making .last() return today's close and
        # broadcasting it across Mon-Wed, creating implicit look-ahead in backtests
        # and inconsistent live-vs-backtest behaviour.
        weekly_trend = 0  # +1 uptrend, -1 downtrend, 0 neutral
        try:
            weekly = df["Close"].resample("W").last().dropna()
            if len(weekly) >= 2:
                weekly = weekly.iloc[:-1]  # drop current (potentially incomplete) week
            if len(weekly) >= 20:
                w_sma20 = float(weekly.iloc[-20:].mean())
                w_price = float(weekly.iloc[-1])
                if w_price > w_sma20 * 1.02:
                    weekly_trend = 1
                elif w_price < w_sma20 * 0.98:
                    weekly_trend = -1
        except Exception:
            log.warning("weekly trend calculation failed for %s", ticker, exc_info=True)

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
                _last10 = _wclose[-10:]
                _weeks_above = int(sum(1 for c in _last10 if c > _wsma13))
                _weeks_below = 10 - _weeks_above
                if _weeks_above >= 8:
                    _weekly_ohlcv_score = 4
                elif _weeks_below >= 8:
                    _weekly_ohlcv_score = -4
        except Exception:
            log.warning("weekly OHLCV fetch failed for %s", ticker, exc_info=True)

        price = tech["price"]
        # `or` alone doesn't catch NaN (NaN is truthy), so a NaN ATR would flow
        # into _levels and produce NaN stop/target. Fall back to 2% of price when
        # atr is missing, zero, or non-finite.
        _atr_raw = tech.get("atr")
        atr = _atr_raw if (_atr_raw is not None and _np.isfinite(_atr_raw)) else price * 0.02
        rsi = tech.get("rsi")
        hist = tech.get("macd_hist", 0) or 0
        hist_p = tech.get("macd_hist_prev", 0) or 0
        sma20 = tech.get("sma20")
        sma50 = tech.get("sma50")
        sma200 = tech.get("sma200")

        # ── Polygon pre-computed indicators (validation + RSI blend) ───────────
        _poly_ind: dict = {}
        _poly_weekly: dict = {}
        try:
            from services.polygon_indicators import blend_rsi, get_indicators, get_weekly_indicators

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
            log.warning("polygon indicator blend failed for %s", ticker, exc_info=True)
        bb_upper = tech.get("bb_upper")
        bb_lower = tech.get("bb_lower")
        _bb_pct_b = tech.get("bb_pct_b")  # 0=lower band, 1=upper band; used for tiered MR scoring
        volume = tech.get("volume", 0)
        avg_vol = tech.get("avg_volume", 1) or 1

        score = 0.0
        rationale = []
        sources = {"Technical"}
        dominant = "macd"
        vol_confidence_penalty = 0.0
        rs_confidence_penalty = 0.0
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
        _is_low_atr = _atr_pct_pre < 0.010  # ATR < 1.0% of price

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
        _macd_mr_dip = (tech.get("bb_pct_b") is not None and float(tech["bb_pct_b"]) < 0.22) or (
            tech.get("ibs") is not None and float(tech["ibs"]) < 0.15
        )
        _macd_sd, _macd_td, _macd_rat, _macd_dom = score_macd(hist, hist_p, mr_dip=_macd_mr_dip)
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
        trend_score += _adx_td
        rationale.extend(_vol_rat)

        # ── Regime classifier — variables used at two application points ────────
        # Defined here (after ADX is scored into trend_score) so the trend
        # multiplier applies before trend_score is capped and added to score.
        # mean_rev_score is 0 here (filled by Bollinger/Z-score below);
        # its multiplier is applied at line ~1900 where osc+mean_rev are combined.
        _adx_regime = tech.get("adx") or 0
        _is_trending_bull = _adx_regime > 25 and sma200 and price > sma200
        _is_ranging_mkt = _adx_regime < 25  # raised from 20 — more markets treated as ranging
        if _is_ranging_mkt:
            trend_score *= 0.25  # suppress momentum 75% — crossovers whipsaw in chop (raised from 60%)

        # ── MACD + RSI joint confirmation (arXiv 2022: 73-86% WR validated) ────
        # Research: MACD cross is most powerful when RSI confirms the direction.
        # Bullish MACD with RSI >60 = momentum fired into overbought stock → suppress.
        # Bearish MACD with RSI <40 = momentum fired into oversold stock → suppress.
        # Suppression factor tightened 0.50→0.30 (Tier 3 backtest: +0.36 Sharpe).
        # Applied here — BEFORE trend_score is capped and added to score.
        if rsi is not None:
            if trend_score > 0 and rsi > 60 or trend_score < 0 and rsi < 40:
                trend_score *= 0.30

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

        # ── Decomposed Scoring via ScoringContext (BE-1) ───────────────────────
        from services.engines.context import ScoringContext
        from services.engines.scorers import score_moving_averages_block, score_bollinger_bands_block

        vix = (market_ctx or {}).get("macro", {}).get("vix") if market_ctx else None

        ctx = ScoringContext(ticker, df, info, market_ctx)
        ctx.tech = tech
        ctx.price = price
        ctx.atr = atr
        ctx.vix = vix
        ctx._atr_pct_pre = _atr_pct_pre
        ctx._is_low_atr = _is_low_atr
        ctx._is_lev_etf = _is_lev_etf

        ctx.score = score
        ctx.rationale = rationale
        ctx.sources = sources
        ctx.ma_score = ma_score
        ctx.mean_rev_score = mean_rev_score

        score_moving_averages_block(ctx)
        score_bollinger_bands_block(ctx)

        score = ctx.score
        rationale = ctx.rationale
        sources = ctx.sources
        ma_score = ctx.ma_score
        mean_rev_score = ctx.mean_rev_score

        # ── 52-Week High / Low Proximity ────────────────────────────────
        # 52W high = momentum/breakout signal → momentum_score bucket.
        # 52W low  = mean-reversion/deep-value signal → mean_rev_score bucket.
        wk52_h = tech.get("week52_high")
        wk52_l = tech.get("week52_low")
        if wk52_h and wk52_l and wk52_h > wk52_l:
            pct_from_high = (price - wk52_h) / wk52_h * 100
            pct_from_low = (price - wk52_l) / wk52_l * 100
            if pct_from_high > -3:
                momentum_score += 10
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Near 52-Week High — Breakout Zone",
                        "body": f"Price is within 3% of its 52-week high (${wk52_h:.2f}). Potential breakout; strong momentum.",
                        "sentiment": "pos",
                        "meta": f"52W High ${wk52_h:.2f} | {pct_from_high:.1f}% away",
                    }
                )
            elif pct_from_low < 10:
                # +8 boost REMOVED (gate-audit 2026-07-15): directly contradicts the
                # §77 hard block — near-52wk-low cohorts are validated at 31-35% WR
                # (live audits 2026-05-31 + 2026-07-14/15, this card's own delivered
                # cohort −16.4pp, N=21). Structural decline, not deep value.
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Near 52-Week Low",
                        "body": (
                            f"Price is within 10% of its 52-week low (${wk52_l:.2f}). Live audits show "
                            "near-annual-low names win only 31-35% — structural decline, not value. "
                            "No score boost (§77-aligned); BUYs within 8% of the low are blocked."
                        ),
                        "sentiment": "neg",
                        "meta": f"52W Low ${wk52_l:.2f} | +{pct_from_low:.1f}% from bottom (boost removed 2026-07-15)",
                    }
                )

        # ── Candlestick Pattern ─────────────────────────────────────────
        pattern = tech.get("candle_pattern")
        if pattern == "hammer":
            score += 12
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Hammer Candle — Bullish Reversal",
                    "body": "Hammer pattern detected: buyers rejected lower prices, closing near the high. Classic reversal signal.",
                    "sentiment": "pos",
                    "meta": "Candlestick: Hammer",
                }
            )
        elif pattern == "bullish_engulfing":
            score += 12
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Bullish Engulfing Pattern",
                    "body": "Today's candle fully engulfs yesterday's bearish candle. Strong buyer conviction.",
                    "sentiment": "pos",
                    "meta": "Candlestick: Bullish Engulfing",
                }
            )
        elif pattern == "shooting_star":
            score -= 12
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Shooting Star — Bearish Reversal",
                    "body": "Shooting star detected: sellers rejected higher prices, closing near the low. Distribution signal.",
                    "sentiment": "neg",
                    "meta": "Candlestick: Shooting Star",
                }
            )
        elif pattern == "bearish_engulfing":
            score -= 12
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Bearish Engulfing Pattern",
                    "body": "Today's candle fully engulfs yesterday's bullish candle. Strong seller conviction.",
                    "sentiment": "neg",
                    "meta": "Candlestick: Bearish Engulfing",
                }
            )
        elif pattern == "doji":
            # Doji = indecision; only noteworthy in context of a strong prior trend
            if score > 15:
                score -= 5
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Doji — Momentum Stalling",
                        "body": "Doji candle after bullish run. Buyers and sellers at equilibrium — potential reversal.",
                        "sentiment": "neg",
                        "meta": "Candlestick: Doji",
                    }
                )
            elif score < -15:
                score += 5
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Doji — Bearish Momentum Stalling",
                        "body": "Doji candle after bearish run. Potential exhaustion of selling pressure.",
                        "sentiment": "pos",
                        "meta": "Candlestick: Doji",
                    }
                )

        # PIVOT (S1/R1) scoring removed — alpha decomp v6/v7 confirmed redundant
        # (ΔSharpe = +0.01 when removed; information already captured by BB/VWAP bands)

        # ── Volume confirmation ─────────────────────────────────────────
        vol_ratio = volume / avg_vol
        if vol_ratio < 0.80:
            # Low-volume signal — flag for confidence penalty applied at the end
            vol_confidence_penalty = 0.10
            rationale.append(
                {
                    "src": "Technical",
                    "head": f"Low Volume — Conviction Reduced ({vol_ratio:.0%} of avg)",
                    "body": (
                        f"Today's volume ({volume:,}) is only {vol_ratio:.0%} of the 20-day average. "
                        "Low-volume price moves lack institutional participation and are more "
                        "prone to reversal. Signal confidence reduced."
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.2f}× | Avg {avg_vol:,}",
                }
            )
        elif vol_ratio > 1.5:
            # Routed into volume_score (not direct score) so it is capped alongside
            # OBV/CMF — prevents 8 pts bypassing the volume family cap entirely.
            _vol_conf = 8 if score >= 0 else -8
            volume_score += _vol_conf
            rationale.append(
                {
                    "src": "Technical",
                    "head": "High-Volume Confirmation",
                    "body": f"Volume {vol_ratio:.1f}× 20-day average — conviction behind the move.",
                    "sentiment": "pos" if _vol_conf > 0 else "neg",
                    "meta": f"Vol {volume:,} | Avg {avg_vol:,}",
                }
            )

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
                # Short interest comes from FINRA — not available via Polygon.
                # But at least we can recompute short_float_pct from known float + yfinance shortRatio.
                # signal_engine uses info.get("short_float_pct") from yfinance .info, which can be None.
                # If yfinance gave us sharesShort but not floatShares, recompute:
                _shares_short = info.get("shares_short")
                if _float_shares and _float_shares > 0 and _shares_short:
                    short_float = round(_shares_short / _float_shares * 100, 1)
                    log.debug(
                        f"[signal_engine] {ticker} float from Polygon: "
                        f"{_float_shares:,} → short_float={short_float:.1f}%"
                    )
            except Exception:
                log.warning("short float lookup failed for %s", ticker, exc_info=True)
        if short_float is not None:
            dtc_ok = short_ratio is not None and short_ratio > 5
            if short_float > 20 and dtc_ok and score > 5:
                # Classic squeeze setup: both thresholds met — high conviction
                score += 12
                sources.add("Short Interest")
                rationale.append(
                    {
                        "src": "Short Interest",
                        "head": f"High-Conviction Squeeze Setup — {short_float:.1f}% Float Short",
                        "body": (
                            f"{short_float:.1f}% of float is sold short with {short_ratio:.1f} days-to-cover. "
                            "Both thresholds confirm a short squeeze setup: any sustained upward move forces "
                            "rapid, mechanically-driven short covering."
                        ),
                        "sentiment": "pos",
                        "meta": f"Short Float {short_float:.1f}% | DTC {short_ratio:.1f}d",
                    }
                )
            elif short_float > 20 and score > 5:
                # High float short but low days-to-cover — partial squeeze signal
                score += 7
                sources.add("Short Interest")
                ratio_str = f" Days-to-cover: {short_ratio:.1f}." if short_ratio else ""
                rationale.append(
                    {
                        "src": "Short Interest",
                        "head": f"High Short Float {short_float:.1f}% — Squeeze Potential",
                        "body": (
                            f"{short_float:.1f}% of float is sold short.{ratio_str} "
                            "Rising price with heavy short interest can trigger forced short covering."
                        ),
                        "sentiment": "pos",
                        "meta": f"Short Float {short_float:.1f}%",
                    }
                )
            elif short_float > 20 and dtc_ok and score < -10:
                # Symmetric to the +12 squeeze BUY: high short interest with strong
                # days-to-cover, but on a confirmed bearish signal = institutional
                # conviction confirmation. Was previously asymmetric (only -5 pts).
                score -= 12
                sources.add("Short Interest")
                rationale.append(
                    {
                        "src": "Short Interest",
                        "head": f"High Short Interest Confirms Bear — {short_float:.1f}% Float Short",
                        "body": (
                            f"{short_float:.1f}% of float is sold short with {short_ratio:.1f}d DTC. "
                            "High institutional conviction backs the bearish thesis — significant "
                            "short positioning rarely placed without fundamental justification."
                        ),
                        "sentiment": "neg",
                        "meta": f"Short Float {short_float:.1f}% | DTC {short_ratio:.1f}d",
                    }
                )
            elif short_float > 20 and score < -10:
                score -= 7
                sources.add("Short Interest")
                rationale.append(
                    {
                        "src": "Short Interest",
                        "head": f"Heavy Short Float Confirms Bear — {short_float:.1f}%",
                        "body": f"{short_float:.1f}% of float is short — strong institutional conviction in the bearish thesis.",
                        "sentiment": "neg",
                        "meta": f"Short Float {short_float:.1f}%",
                    }
                )
            elif short_float > 15 and score < -5:
                score -= 5
                sources.add("Short Interest")
                rationale.append(
                    {
                        "src": "Short Interest",
                        "head": f"Elevated Short Interest {short_float:.1f}%",
                        "body": f"{short_float:.1f}% of float is short — moderate institutional conviction in bearish thesis.",
                        "sentiment": "neg",
                        "meta": f"Short Float {short_float:.1f}%",
                    }
                )

        # ── §52 Short Interest Velocity (see gates/fundamentals.py) ─────────
        from services.gates.fundamentals import apply_short_interest_velocity as _si_vel_fn

        score, _si_cards, _si_srcs = _si_vel_fn(score, info)
        rationale.extend(_si_cards)
        sources.update(_si_srcs)

        # ── Short-Volume Pressure (Polygon alt-data, T-1) ────────────────────
        # Alpha check (2026-06-09, scripts/check_short_volume_alpha.py): MR-BUY
        # outcomes fall monotonically with the entry short-volume ratio — Low(<41%)
        # WR 75%/+0.56%, Mid 67%/+0.43%, High(>52%) WR 37.5%/-0.79%. High short
        # conviction on an oversold name = falling-knife (corroborates the §R5
        # cross-sectional finding). Conservative penalty (small N=25 — provisional;
        # short_volume_daily backfilled for forward re-validation). Uses T-1 to avoid
        # look-ahead (FINRA short volume finalises after the close).
        if score > 0:
            try:
                from datetime import date as _date

                from sqlalchemy import select as _sel

                from database import AsyncSessionLocal as _ASL
                from models import ShortVolumeDaily as _SVD

                # Latest T-1 short-volume from the backfilled table (kept current by the
                # nightly refresh). DB read, not an API call in the hot scan path.
                async with _ASL() as _svdb:
                    _row = (
                        await _svdb.execute(
                            _sel(_SVD.short_volume_ratio)
                            .where(_SVD.ticker == ticker, _SVD.date < _date.today())
                            .order_by(_SVD.date.desc())
                            .limit(1)
                        )
                    ).first()
                _svr = float(_row[0]) if _row and _row[0] is not None else None
                if _svr is not None and _svr >= 55.0:
                    score -= 4
                    sources.add("Alt-Data")
                    rationale.append(
                        {
                            "src": "Alt-Data",
                            "head": f"Elevated Short Volume — {_svr:.0f}% short-marked",
                            "body": (
                                f"{_svr:.0f}% of recent consolidated volume was short-marked (FINRA via Polygon). "
                                "Oversold names with >55% short volume historically keep falling (MR win rate "
                                "37.5% vs 75% for low short pressure) — institutional short conviction, not a bounce."
                            ),
                            "sentiment": "neg",
                            "meta": f"short_volume_ratio={_svr:.1f}% (>55% = falling-knife risk)",
                        }
                    )
            except Exception as _sv_err:
                log.debug("[short_volume] %s: %s", ticker, _sv_err)

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
                rationale.append(
                    {
                        "src": "Technicals",
                        "head": f"Near 52-Week High — {_pos_pct:.0f}th Percentile of Range",
                        "body": (
                            f"Price is in the top {100 - _pos_pct:.0f}% of its 52-week range "
                            f"(${_wk52l:.2f}–${_wk52h:.2f}). Near-52wk-high stocks outperform by "
                            "6-8% annually in academic studies — momentum continuation signal."
                        ),
                        "sentiment": "pos",
                        "meta": f"52w_pos={_pos_pct:.1f}%",
                    }
                )
            elif _pos >= 0.75:
                score += 2
                rationale.append(
                    {
                        "src": "Technicals",
                        "head": f"Upper Quartile of 52-Week Range — {_pos_pct:.0f}th Percentile",
                        "body": "Price in upper 25% of 52-week range — mild momentum confirmation.",
                        "sentiment": "pos",
                        "meta": f"52w_pos={_pos_pct:.1f}%",
                    }
                )
            elif _pos <= 0.10:
                score -= 4
                rationale.append(
                    {
                        "src": "Technicals",
                        "head": f"Near 52-Week Low — {_pos_pct:.0f}th Percentile of Range",
                        "body": (
                            f"Price in the bottom {_pos_pct:.0f}% of its 52-week range. "
                            "Near-52wk-low stocks systematically underperform — value trap risk. "
                            "Require much stronger fundamental catalyst before buying."
                        ),
                        "sentiment": "neg",
                        "meta": f"52w_pos={_pos_pct:.1f}%",
                    }
                )
            elif _pos <= 0.25:
                score -= 2
                rationale.append(
                    {
                        "src": "Technicals",
                        "head": f"Lower Quartile of 52-Week Range — {_pos_pct:.0f}th Percentile",
                        "body": "Price in bottom 25% of 52-week range — mild downtrend confirmation.",
                        "sentiment": "neg",
                        "meta": f"52w_pos={_pos_pct:.1f}%",
                    }
                )

        # ── Institutional & Insider Ownership ────────────────────────────────
        # High insider ownership = management conviction (skin-in-the-game).
        # High institutional ownership validates the thesis but also signals
        # crowded positioning risk. Uses yfinance free fields.
        action = _score_to_action(score)[0]  # preliminary direction for conditional checks
        _inst_own = info.get("held_pct_inst")  # e.g. 0.657 = 65.7%
        _insid_own = info.get("held_pct_insiders")  # e.g. 0.016 = 1.6%
        if _insid_own is not None and not _is_lev_etf:
            if _insid_own > 0.15:  # >15% insider ownership
                score += 3
                sources.add("Fundamentals")
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"High Insider Ownership — {_insid_own * 100:.1f}%",
                        "body": (
                            f"Insiders hold {_insid_own * 100:.1f}% of shares — strong skin-in-the-game "
                            "alignment. High insider ownership is a quality signal: management is "
                            "directly incentivised by share price performance."
                        ),
                        "sentiment": "pos",
                        "meta": f"insider_own={_insid_own * 100:.1f}%",
                    }
                )
            elif _insid_own < 0.005 and action == "BUY":  # <0.5% insider ownership
                score -= 1
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"Very Low Insider Ownership — {_insid_own * 100:.2f}%",
                        "body": (
                            f"Insiders hold only {_insid_own * 100:.2f}% — management has minimal "
                            "direct financial stake. Slightly reduces conviction on BUY signals."
                        ),
                        "sentiment": "neg",
                        "meta": f"insider_own={_insid_own * 100:.2f}%",
                    }
                )
        if _inst_own is not None and not _is_lev_etf:
            if _inst_own > 0.80:  # >80% = very crowded institutional trade
                sources.add("Fundamentals")
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"Crowded Institutional Trade — {_inst_own * 100:.1f}% Held",
                        "body": (
                            f"{_inst_own * 100:.1f}% of shares are held by institutions — heavily crowded. "
                            "While this validates the thesis, crowded trades are vulnerable to "
                            "rapid de-risking when sentiment shifts."
                        ),
                        "sentiment": "neg" if action == "BUY" else "pos",
                        "meta": f"inst_own={_inst_own * 100:.1f}%",
                    }
                )

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
                _all_news.append(
                    {
                        "headline": _a["headline"],
                        "sentiment": _a["sentiment"],  # already age-decayed
                        "hours_ago": 0,  # decay already applied
                        "source": "Benzinga",
                        "summary": _a["headline"],
                    }
                )
            if _bzg_articles:
                sources.add("Benzinga")
        except Exception:
            log.warning("Benzinga news fetch failed for %s", ticker, exc_info=True)

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
                total_w += w
            avg_sent = weighted_s / total_w if total_w > 0 else 0.0

            # Which external sources contributed?
            _src_labels = {n.get("source", "") for n in _all_news}
            if news:
                sources.add("Finnhub")
            for _sl in ("Benzinga", "Reuters", "Finviz"):
                if _sl in _src_labels:
                    sources.add(_sl)

            # When the async news_worker is running, skip inline score/rationale
            # additions — the worker's ScoringResult is merged later. Applying
            # both inline and worker news sentiment would double-count headlines.
            if _worker_task is None:
                # Cap news contribution at ±15 — sentiment alone is noisy
                _top = sorted(_all_news, key=lambda x: x.get("hours_ago", 9999))[0]
                _src_lbl = _top.get("source", "News")
                if avg_sent > 0.25:
                    score += min(15, round(avg_sent * 22))
                    rationale.append(
                        {
                            "src": _src_lbl,
                            "head": _top["headline"][:90],
                            "body": _top.get("summary", _top["headline"])[:250],
                            "sentiment": "pos",
                            "meta": f"{_src_lbl} · {_top.get('hours_ago', '?')}h ago | {len(_all_news)} articles",
                        }
                    )
                elif avg_sent < -0.25:
                    score += max(-15, round(avg_sent * 22))
                    rationale.append(
                        {
                            "src": _src_lbl,
                            "head": _top["headline"][:90],
                            "body": _top.get("summary", _top["headline"])[:250],
                            "sentiment": "neg",
                            "meta": f"{_src_lbl} · {_top.get('hours_ago', '?')}h ago | {len(_all_news)} articles",
                        }
                    )

        # ── SEC EDGAR — insider trades (Form 4) ─────────────────────────
        # Score contribution lives in institutional_worker (signal_workers.py).
        # Confidence penalty stays here: it reads accumulated `score`, which workers cannot access.
        if insider and insider.get("filings", 0) >= 3:
            net = insider.get("net_shares", 0) or 0
            sell_val = insider.get("sell_value", 0) or 0
            buy_val = insider.get("buy_value", 0) or 0
            if score > 0 and net < 0 and sell_val > 250_000:
                insider_confidence_penalty = 0.10
            elif score < 0 and net > 0 and buy_val > 250_000:
                insider_confidence_penalty = 0.08

        # §73 Insider Clustering REMOVED (dead-code audit 2026-07-14): the
        # 'Insider Cluster Buy' card fired 0 times in 87,982 all-time signals —
        # insider['unique_buyers'] never reaches 2 (EDGAR Form-4 parsing yields
        # sparse/empty buyer counts on this large-cap universe). The plain
        # insider net-flow confidence penalties above DO fire and are kept.

        # ── Liquidity Ceiling (NAAIM > 90%) ─────────────────────────────
        aaii = (market_ctx or {}).get("aaii") or {}
        naaim_exposure = aaii.get("exposure", 50)
        liquidity_ceiling = naaim_exposure > 90

        # ── Relative Strength vs S&P 500 ────────────────────────────────
        macro = (market_ctx or {}).get("macro") or {}
        spy_1m = macro.get("spy_1m_ret")
        if spy_1m is not None and len(df) >= 21:
            close_arr = df["Close"].astype(float)
            _c21 = float(close_arr.iloc[-21])
            if not _c21 or not _np.isfinite(_c21) or abs(_c21) < 1e-9:
                log.warning("[signal_engine] %s: skipping 1m RS — 21-day close is zero/NaN/inf (%s)", ticker, _c21)
                rel_strength = None
            else:
                ticker_1m = (float(close_arr.iloc[-1]) / _c21 - 1) * 100
                rel_strength = round(ticker_1m - spy_1m, 2)
                # Gate-audit 2026-07-15: expose 1M SPY-relative strength to the
                # assembler's RS-laggard hard gate (live: RS<-8 cohort WR 35.3%,
                # -14.5pp vs base, N=85 — penalty alone was too weak).
                tech["rel_strength_1m"] = rel_strength
            if rel_strength is not None and rel_strength > 8:
                if not liquidity_ceiling:
                    score += 12
                    sources.add("Relative Strength")
                    rationale.append(
                        {
                            "src": "Relative Strength",
                            "head": f"Outperforming S&P 500 by {rel_strength:.1f}%",
                            "body": (
                                f"1-month return: {ticker_1m:+.1f}% vs S&P 500 {spy_1m:+.1f}%. "
                                f"Relative strength of +{rel_strength:.1f}% signals institutional accumulation."
                            ),
                            "sentiment": "pos",
                            "meta": f"1M: {ticker_1m:+.1f}% | SPY: {spy_1m:+.1f}%",
                        }
                    )
            elif rel_strength is not None and rel_strength > 2:
                if not liquidity_ceiling:
                    score += 4  # mild outperformance still a positive signal
            elif rel_strength is not None and rel_strength < -8:
                if not liquidity_ceiling:
                    score -= 12
                sources.add("Relative Strength")
                rationale.append(
                    {
                        "src": "Relative Strength",
                        "head": f"Underperforming S&P 500 by {abs(rel_strength):.1f}%",
                        "body": (
                            f"1-month return: {ticker_1m:+.1f}% vs S&P 500 {spy_1m:+.1f}%. "
                            f"Persistent underperformance suggests institutional selling or fundamental weakness."
                        ),
                        "sentiment": "neg",
                        "meta": f"1M: {ticker_1m:+.1f}% | SPY: {spy_1m:+.1f}%",
                    }
                )
            elif rel_strength is not None and rel_strength < -2:
                if not liquidity_ceiling:
                    score -= 5  # mild underperformance is a negative signal
            # Confidence penalty only for persistent underperformers (> -5% vs SPY).
            # The -2% to -5% band is already captured by the score -= 5 above; the
            # confidence penalty here is reserved for meaningful sustained lagging.
            if rel_strength is not None and rel_strength < -5 and score > 0:
                rs_confidence_penalty = 0.08

        # ── Fear & Greed (market-wide, passed from scanner) ─────────────
        fg = (market_ctx or {}).get("fear_greed")
        if fg:
            bias = fg["score_bias"]
            score += bias
            if abs(bias) >= 7:
                sources.add("Fear&Greed")
                rationale.append(
                    {
                        "src": "Fear & Greed",
                        "head": f"Market {fg['label']} — F&G {fg['score']:.0f}/100",
                        "body": (
                            f"CNN Fear & Greed Index at {fg['score']:.0f}/100 ({fg['label']}). "
                            + (
                                "Contrarian signal: extreme fear historically marks bottoms."
                                if bias > 0
                                else "Contrarian signal: extreme greed historically precedes corrections."
                            )
                        ),
                        "sentiment": fg["sentiment"],
                        "meta": f"F&G = {fg['score']:.0f} | 1w ago: {fg.get('prev_1w', '?')}",
                    }
                )

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
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Strong Price Momentum +{roc10:.1f}% (10d)",
                        "body": f"Price is up {roc10:.1f}% over the last 10 sessions. Momentum traders will follow.",
                        "sentiment": "pos",
                        "meta": f"ROC(10) = +{roc10:.1f}%",
                    }
                )
            elif roc10 < -8:
                momentum_score -= 8
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Negative Price Momentum {roc10:.1f}% (10d)",
                        "body": f"Price is down {abs(roc10):.1f}% over the last 10 sessions. Selling pressure persists.",
                        "sentiment": "neg",
                        "meta": f"ROC(10) = {roc10:.1f}%",
                    }
                )
            elif roc10 > 4:
                momentum_score += 4
            elif roc10 < -4:
                momentum_score -= 4

        # RSI_DIV scoring removed — alpha decomp v6/v7 confirmed redundant
        # (ΔSharpe = +0.03 when removed; noise in the presence of RSI level + KC + Donchian)

        # ── MACD Zero-Line Cross ─────────────────────────────────────────
        # Routed into trend_score (same family as MACD state/histogram) so all
        # three MACD signals (crossover, state, zero-cross) share one cap.
        if tech.get("macd_zero_cross_up"):
            trend_score += 10
            rationale.append(
                {
                    "src": "Technical",
                    "head": "MACD Crossed Zero — Trend Flipping Bullish",
                    "body": "MACD just crossed above zero. The underlying trend has shifted from bearish to bullish — stronger than a signal-line cross alone.",
                    "sentiment": "pos",
                    "meta": f"MACD = {tech.get('macd', 0):.5f}",
                }
            )
        elif tech.get("macd_zero_cross_down"):
            trend_score -= 10
            rationale.append(
                {
                    "src": "Technical",
                    "head": "MACD Crossed Zero — Trend Flipping Bearish",
                    "body": "MACD just crossed below zero. The underlying trend has shifted from bullish to bearish — stronger than a signal-line cross alone.",
                    "sentiment": "neg",
                    "meta": f"MACD = {tech.get('macd', 0):.5f}",
                }
            )

        # ── Z-Score Mean Reversion ───────────────────────────────────────
        zscore = tech.get("zscore")
        if zscore is not None:
            if zscore < -2.5:
                mean_rev_score += 14
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Z-Score Extreme Oversold ({zscore:.1f}σ)",
                        "body": f"Price is {abs(zscore):.1f} standard deviations below its 20-day average — statistically rare. Strong mean-reversion setup.",
                        "sentiment": "pos",
                        "meta": f"Z-Score = {zscore:.2f}σ",
                    }
                )
            elif zscore < -2.0:
                mean_rev_score += 8
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Z-Score Oversold ({zscore:.1f}σ)",
                        "body": f"Price {abs(zscore):.1f}σ below 20-day mean. Statistically stretched to the downside.",
                        "sentiment": "pos",
                        "meta": f"Z-Score = {zscore:.2f}σ",
                    }
                )
            elif zscore > 2.5:
                mean_rev_score -= 14
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Z-Score Extreme Overbought (+{zscore:.1f}σ)",
                        "body": f"Price is {zscore:.1f} standard deviations above its 20-day average — statistically rare. Mean-reversion risk is high.",
                        "sentiment": "neg",
                        "meta": f"Z-Score = +{zscore:.2f}σ",
                    }
                )
            elif zscore > 2.0:
                mean_rev_score -= 8
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Z-Score Overbought (+{zscore:.1f}σ)",
                        "body": f"Price {zscore:.1f}σ above 20-day mean. Statistically stretched to the upside.",
                        "sentiment": "neg",
                        "meta": f"Z-Score = +{zscore:.2f}σ",
                    }
                )

        # MFI scoring removed — alpha decomp v6/v7 confirmed redundant
        # (ΔSharpe = +0.04 when removed; volume-weighted RSI already captured by OBV + RSI)

        # ── IBS — Internal Bar Strength ──────────────────────────────────
        # Where the close landed within the day's range (0 = at low, 1 = at high).
        # Pure daily mean-reversion exhaustion signal, independent of RSI/MFI.
        ibs = tech.get("ibs")
        if ibs is not None:
            sources.add("Technical")
            if ibs < 0.10:
                mean_rev_score += 12
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"IBS Extreme Oversold ({ibs:.2f}) — Close Near Daily Low",
                        "body": (
                            f"Close landed at only {ibs * 100:.0f}% of today's range — extremely close to the session low. "
                            "Strong single-bar mean-reversion signal: sellers exhausted, bounce likely next session."
                        ),
                        "sentiment": "pos",
                        "meta": f"IBS = {ibs:.3f}",
                    }
                )
            elif ibs < 0.20:
                mean_rev_score += 8
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"IBS Oversold ({ibs:.2f}) — Close Near Low",
                        "body": f"IBS at {ibs:.2f} — close near the daily low. Sellers dominated intraday but may be tiring. Daily mean-reversion setup.",
                        "sentiment": "pos",
                        "meta": f"IBS = {ibs:.3f}",
                    }
                )
            elif ibs > 0.90:
                mean_rev_score -= 10
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"IBS Overbought ({ibs:.2f}) — Close Near Daily High",
                        "body": (
                            f"Close at {ibs * 100:.0f}% of today's range — extremely close to the session high. "
                            "Buyers dominated but may be exhausted. Distribution risk next session."
                        ),
                        "sentiment": "neg",
                        "meta": f"IBS = {ibs:.3f}",
                    }
                )
            elif ibs > 0.80:
                mean_rev_score -= 6
            # Combined extremes: IBS + RSI both confirming = higher conviction
            if ibs is not None and rsi is not None:
                if ibs < 0.10 and rsi < 30:
                    mean_rev_score += 4
                elif ibs > 0.90 and rsi > 70:
                    mean_rev_score -= 4

        # osc_score cap deferred: combined with mean_rev_score into a single
        # "stretched price" bucket at the end of that section (see ±30 cap below).
        # This prevents RSI oversold + Z-score oversold from stacking across two caps.

        # ── Weekly Multi-Timeframe RSI + SMA Confirmation ────────────────────
        # Weekly RSI < 40 AND daily RSI < 35 = double-confirmed oversold (72% win rate).
        # Weekly price above SMA(20) AND daily above SMA(200) = multi-timeframe uptrend.
        if _poly_weekly:
            _w_rsi = _poly_weekly.get("weekly_rsi")
            _w_sma20 = _poly_weekly.get("weekly_sma20")
            if _w_rsi is not None and rsi is not None:
                if _w_rsi < 40 and rsi < 35:
                    osc_score += 8  # double-confirmed oversold — into osc_score (capped in stretch bucket)
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"Double-Confirmed Oversold: Weekly RSI {_w_rsi:.1f} + Daily RSI {rsi:.1f}",
                            "body": (
                                f"Weekly RSI ({_w_rsi:.1f}) and daily RSI ({rsi:.1f}) are both in oversold territory. "
                                "Multi-timeframe RSI confluence has a 72% historical win rate vs 58% daily-only. "
                                "Institutional buyers watching this level."
                            ),
                            "sentiment": "pos",
                            "meta": f"W-RSI={_w_rsi:.1f} D-RSI={rsi:.1f}",
                        }
                    )
                elif _w_rsi > 70 and rsi > 65:
                    osc_score -= 6  # into osc_score (capped in stretch bucket)
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"Double-Confirmed Overbought: Weekly RSI {_w_rsi:.1f} + Daily RSI {rsi:.1f}",
                            "body": (
                                f"Both weekly ({_w_rsi:.1f}) and daily ({rsi:.1f}) RSI are elevated. "
                                "Multi-timeframe overbought alignment increases pullback risk significantly."
                            ),
                            "sentiment": "neg",
                            "meta": f"W-RSI={_w_rsi:.1f} D-RSI={rsi:.1f}",
                        }
                    )
            if _w_sma20 and sma200 and price:
                _w_above = price > _w_sma20
                _d_above = price > sma200
                if _w_above and _d_above:
                    score += 4
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": "Multi-Timeframe Uptrend Confirmed",
                            "body": (
                                f"Price is above both weekly SMA(20) (${_w_sma20:.2f}) and daily SMA(200) (${sma200:.2f}). "
                                "Dual-timeframe trend alignment: intermediate and long-term trends both bullish."
                            ),
                            "sentiment": "pos",
                            "meta": f"W-SMA20=${_w_sma20:.2f} D-SMA200=${sma200:.2f}",
                        }
                    )
                elif not _w_above and not _d_above:
                    score -= 4
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": "Multi-Timeframe Downtrend Confirmed",
                            "body": (
                                f"Price is below both weekly SMA(20) (${_w_sma20:.2f}) and daily SMA(200) (${sma200:.2f}). "
                                "Dual-timeframe downtrend."
                            ),
                            "sentiment": "neg",
                            "meta": f"W-SMA20=${_w_sma20:.2f} D-SMA200=${sma200:.2f}",
                        }
                    )

        # ── Bollinger Band Squeeze + %B ──────────────────────────────────
        bb_squeeze = tech.get("bb_squeeze", False)
        bb_pct_b = tech.get("bb_pct_b")
        if bb_squeeze and bb_pct_b is not None:
            if bb_pct_b > 0.5:
                mean_rev_score += 8
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Bollinger Squeeze — Upside Breakout Setup",
                        "body": "Bollinger Bands are at their tightest in 20 days (low volatility). Price sits in the upper half — compression before expansion, likely upward.",
                        "sentiment": "pos",
                        "meta": f"BB%B = {bb_pct_b:.2f} | Squeeze ON",
                    }
                )
            else:
                mean_rev_score -= 8
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Bollinger Squeeze — Downside Breakout Risk",
                        "body": "Bollinger Bands at 20-day minimum width. Price in lower half — volatility compression before a likely breakdown.",
                        "sentiment": "neg",
                        "meta": f"BB%B = {bb_pct_b:.2f} | Squeeze ON",
                    }
                )
        elif bb_pct_b is not None:
            # bb_pct_b <0.05/0.95 extremes without squeeze — already handled by
            # the tiered BB%B section above (_bb_pct_b). This block is kept only
            # for the squeeze path (bb_pct_b loaded at line 3689); no extra addition.
            pass

        # ── Combined "Stretched Price" cap — MR cap raised ±8→±18 ────────────
        # OSC weight restored to 1.0 (§45 sweep: OSC×1.0 only breakeven on 105-ticker universe;
        # prior OSC×0.3 was calibrated on 24-ticker subset and did not generalize).
        # MR cap raised to ±18 to match backtest score_row() research baseline.
        # Regime adjustment: in bull trend, suppress bearish mean-rev (dip-buy valid).
        if _is_trending_bull and mean_rev_score < 0:
            mean_rev_score *= 0.20
        score += (max(-18.0, min(18.0, osc_score)) * 1.0 + max(-18.0, min(18.0, mean_rev_score))) * 0.85

        # ── Keltner Channels(20, 2×ATR) ──────────────────────────────────────
        # Backtest-validated (alpha decomp v3): below kc_lower on oversold RSI
        # = ATR-extreme oversold = MR bounce setup (routes to mean_rev_score).
        # Above kc_upper = momentum breakout (unchanged, routes to score directly).
        kc_upper = tech.get("kc_upper")
        kc_lower = tech.get("kc_lower")
        if kc_upper and kc_lower:
            sources.add("Technical")
            _kc_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
            if price > kc_upper:
                score += 8
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Keltner Channel Breakout (${kc_upper:.2f})",
                        "body": (
                            f"Price ${price:.2f} broke above the upper Keltner Channel "
                            f"(${kc_upper:.2f}). ATR-based channels filter noise better than "
                            "Bollinger — a KC breakout signals genuine momentum, not just volatility expansion."
                        ),
                        "sentiment": "pos",
                        "meta": f"KC Upper: ${kc_upper:.2f}",
                    }
                )
            elif price < kc_lower:
                if _kc_rsi is not None and _kc_rsi < 42:
                    # MR-contrarian: ATR-extreme oversold = bounce candidate (direct score)
                    # Note: routes to score directly (not mean_rev_score) because mean_rev_score
                    # was already assembled at line ~2200; second-block additions only affect
                    # the _stretch_total momentum dampener, not the score itself.
                    score += 8
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"Keltner Lower Breach — ATR-Extreme Oversold (RSI {_kc_rsi:.1f})",
                            "body": (
                                f"Price ${price:.2f} below lower Keltner Channel (${kc_lower:.2f}) "
                                f"with RSI {_kc_rsi:.1f}. KC breach on oversold RSI marks "
                                "ATR-extreme oversold — statistically strong mean-reversion setup."
                            ),
                            "sentiment": "pos",
                            "meta": f"KC Lower: ${kc_lower:.2f} | RSI: {_kc_rsi:.1f}",
                        }
                    )
                else:
                    # Momentum breakdown when not oversold
                    score -= 8
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"Keltner Channel Breakdown (${kc_lower:.2f})",
                            "body": (
                                f"Price ${price:.2f} fell below the lower Keltner Channel "
                                f"(${kc_lower:.2f}). KC breakdowns are high-conviction distribution signals."
                            ),
                            "sentiment": "neg",
                            "meta": f"KC Lower: ${kc_lower:.2f}",
                        }
                    )
            elif price < kc_lower * 1.01 and _kc_rsi is not None and _kc_rsi < 50:
                # Approaching lower KC from above = nearing support zone (direct score)
                score += 5
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Approaching Keltner Support (${kc_lower:.2f})",
                        "body": f"Price ${price:.2f} within 1% of lower Keltner Channel. ATR-based support approaching — watch for bounce.",
                        "sentiment": "pos",
                        "meta": f"KC Lower: ${kc_lower:.2f}",
                    }
                )
            # Bollinger Bands entirely inside KC = maximum volatility squeeze
            if bb_upper and bb_lower and bb_upper < kc_upper and bb_lower > kc_lower:
                # ±4 direction-chasing modifier NEUTRALIZED (gate-audit 2026-07-15):
                # cohort −8.1pp vs baseline (N=36). "Breakout direction is likely
                # set" is momentum logic — at an MR dip the compression resolves
                # DOWN as often as up. Card informational.
                squeeze_sentiment = "neu"
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Keltner–Bollinger Squeeze — Maximum Coil",
                        "body": (
                            "Bollinger Bands are fully contained within Keltner Channels — "
                            "the tightest possible volatility compression. Historically this precedes "
                            "explosive directional moves. The breakout direction is likely set."
                        ),
                        "sentiment": squeeze_sentiment,
                        "meta": f"BB inside KC | KC: ${kc_lower:.2f}–${kc_upper:.2f}",
                    }
                )

        # ── Donchian Channel (20-day) — MR-contrarian ────────────────────
        # Backtest-validated (alpha decomp v3): near 20-day low = extreme oversold
        # over a 20-session window = high-probability mean-reversion bounce setup.
        # Near 20-day high = momentum continuation (routes to momentum_score).
        _dc_low = tech.get("donchian_low")
        _dc_high = tech.get("donchian_high")
        _dc_lowp = tech.get("donchian_low_p")
        _dc_hip = tech.get("donchian_high_p")
        _dc_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
        if _dc_low and _dc_high and _dc_high > _dc_low:
            sources.add("Technical")
            _dc_range = _dc_high - _dc_low
            _dc_pos = (price - _dc_low) / _dc_range  # 0 = at 20d low, 1 = at 20d high
            # MR path: only activate when approaching oversold (RSI < 45)
            # avoids double-counting with the existing Donchian momentum block (line ~3460)
            if _dc_lowp and price <= _dc_lowp * 1.002 and _dc_rsi is not None and _dc_rsi < 45:
                # New 20-day low on oversold RSI — weight 0.5× (§42: OSC↔DONCHIAN corr=0.70 double-counts MR)
                score += 4
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"New 20-Day Low — Donchian Oversold Extension (RSI {_dc_rsi:.1f})",
                        "body": (
                            f"Price ${price:.2f} at new 20-session low (${_dc_low:.2f}) "
                            f"with RSI {_dc_rsi:.1f}. Double-confirmed oversold: Donchian extension + "
                            "approaching RSI oversold. High-probability mean-reversion bounce zone."
                        ),
                        "sentiment": "pos",
                        "meta": f"20d Low: ${_dc_low:.2f} | RSI: {_dc_rsi:.1f}",
                    }
                )
            elif _dc_pos <= 0.10 and _dc_rsi is not None and _dc_rsi < 50:
                # In bottom 10% of 20-day range — weight 0.5× (§42: double-count with OSC reduced)
                score += 2
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Near 20-Day Donchian Low — Oversold Zone",
                        "body": (
                            f"Price in bottom {_dc_pos * 100:.0f}% of its 20-session range "
                            f"(${_dc_low:.2f}–${_dc_high:.2f}). Extended below near-term value."
                        ),
                        "sentiment": "pos",
                        "meta": f"Donchian pos: {_dc_pos * 100:.0f}%",
                    }
                )
            elif _dc_hip and price >= _dc_hip * 0.998:
                # At new 20-day high = momentum breakout
                momentum_score += 8
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "New 20-Day High — Donchian Breakout",
                        "body": (
                            f"Price ${price:.2f} at new 20-session high (${_dc_high:.2f}). "
                            "20-day channel breakout signals accumulating institutional momentum."
                        ),
                        "sentiment": "pos",
                        "meta": f"20d High: ${_dc_high:.2f}",
                    }
                )
            elif _dc_pos >= 0.90:
                # In top 10% of 20-day range = approaching breakout zone
                momentum_score += 4

        # ── Consecutive Close Streak vs SMA20 ────────────────────────────
        # Backtest-validated (alpha decomp v3): negative streak (extended below SMA20)
        # routes to mean_rev_score as a bounce candidate, not a bearish momentum signal.
        # Positive streak (above SMA20) remains a momentum signal.
        streak = tech.get("close_streak", 0)
        if streak >= 7:
            momentum_score += 8
            rationale.append(
                {
                    "src": "Technical",
                    "head": f"{streak} Straight Closes Above SMA20",
                    "body": f"Price has closed above its 20-day average for {streak} consecutive sessions. Persistent institutional buying.",
                    "sentiment": "pos",
                    "meta": f"Streak: {streak} days above SMA20",
                }
            )
        elif streak <= -7:
            # Extended weakness below SMA20 = bounce candidate (direct score — after mean_rev assembly)
            score += 7
            rationale.append(
                {
                    "src": "Technical",
                    "head": f"{abs(streak)} Days Below SMA20 — Mean-Reversion Setup",
                    "body": (
                        f"Price has closed below its 20-day average for {abs(streak)} straight sessions. "
                        "Extended SMA20 undercuts are statistically reliable mean-reversion setups — "
                        "the longer the streak, the higher the probability of a bounce to the moving average."
                    ),
                    "sentiment": "pos",
                    "meta": f"Streak: {streak} days below SMA20",
                }
            )
        elif streak >= 4:
            momentum_score += 4
        elif streak <= -4:
            # Moderate weakness = mild MR signal (direct score)
            score += 4

        # ── Credit Stress (HYG trend from macro context) ─────────────────
        hyg_1m = macro.get("hyg_1m_ret")
        if hyg_1m is not None:
            if hyg_1m < -3:
                score -= 8
                sources.add("Macro")
                rationale.append(
                    {
                        "src": "Macro",
                        "head": f"Credit Stress: HYG Down {hyg_1m:.1f}% (1M)",
                        "body": "High-yield bonds are falling — a sign of rising credit stress. Risk assets (stocks) tend to follow bonds lower when credit deteriorates.",
                        "sentiment": "neg",
                        "meta": f"HYG 1M = {hyg_1m:.1f}%",
                    }
                )
            elif hyg_1m > 2:
                score += 5
                sources.add("Macro")
                rationale.append(
                    {
                        "src": "Macro",
                        "head": f"Credit Healthy: HYG Up {hyg_1m:.1f}% (1M)",
                        "body": "High-yield bonds rising — credit markets are healthy. Risk-on environment favours equities.",
                        "sentiment": "pos",
                        "meta": f"HYG 1M = {hyg_1m:.1f}%",
                    }
                )

        # ── Post-Earnings Cooldown ───────────────────────────────────────
        # Days 0-2 after an earnings release: price discovery is still underway,
        # IV crush is happening, and gap fills / post-earnings drift make all
        # technical indicators unreliable. Hard-HOLD for 2 trading days.
        # Days 3-4: partial suppression (×0.80) — initial reaction is settling.
        # Post-earnings blackout/settling REMOVED (dead-code audit 2026-07-14):
        # zero fires across 87,982 signals spanning hundreds of earnings events —
        # earnings_cal['days_since_earnings'] never populates, so this protection
        # never functioned. The PRE-earnings blackout below is the one that fires
        # (630+ cards) and is unchanged.

        # ── Earnings Proximity Risk ──────────────────────────────────────
        days_to_earnings = earnings_cal.get("days_to_earnings")
        edate = earnings_cal.get("next_earnings_date", "")
        if days_to_earnings is not None and days_to_earnings >= 0:
            sources.add("Earnings")
            if days_to_earnings <= 2:
                # Hard blackout: binary event risk overrides ALL technical signals.
                # IV typically spikes 20–50% into earnings — directional analysis fails.
                score = 0
                _force_hold = True  # subsequent signals must not re-open a directional trade
                sources.add("Risk Gate")
                rationale.append(
                    {
                        "src": "Risk Gate",
                        "head": f"Earnings Blackout — {days_to_earnings}d to Binary Event ({edate})",
                        "body": (
                            f"Earnings report in {days_to_earnings} day(s) ({edate}). "
                            "All directional signals are hard-blocked: options implied volatility "
                            "spikes 20–50% ahead of earnings, making price targets statistically "
                            "unreliable. Signal forced to HOLD — reassess after the print."
                        ),
                        "sentiment": "neg",
                        "meta": f"BLACKOUT: earnings {edate}",
                    }
                )
            elif days_to_earnings <= 5:
                # No score penalty: live data (529 trades, §11c) shows 3-7d pre-earnings
                # signals achieve 100% WR and +7.34% avg return vs 48.8% WR in the safe
                # zone. Pre-earnings MR setups mean-revert sharply ahead of the print.
                # Score multiplier removed — awareness note only.
                rationale.append(
                    {
                        "src": "Earnings",
                        "head": f"Earnings in {days_to_earnings}d — Pre-Earnings Setup",
                        "body": (
                            f"Earnings report in {days_to_earnings} days ({edate}). "
                            "IV will expand — options directional trades are expensive. "
                            "Live data shows pre-earnings MR setups outperform: size accordingly."
                        ),
                        "sentiment": "neg",
                        "meta": f"Next earnings: {edate}",
                    }
                )
            elif days_to_earnings <= 7:
                # Same rationale as ≤5d: live data shows 3-7d zone outperforms safe zone.
                rationale.append(
                    {
                        "src": "Earnings",
                        "head": f"Earnings in {days_to_earnings}d — Pre-Earnings Awareness",
                        "body": (
                            f"Earnings report in {days_to_earnings} days ({edate}). "
                            "Stocks often build positioning ahead of earnings — can support MR bounces."
                        ),
                        "sentiment": "neg",
                        "meta": f"Next earnings: {edate}",
                    }
                )
            elif days_to_earnings <= 14:
                # Live data: 8-14d zone shows 75% WR, +7.93% avg ret (vs 48.8% safe zone).
                # Penalty removed — informational note only.
                rationale.append(
                    {
                        "src": "Earnings",
                        "head": f"Earnings in {days_to_earnings}d — Awareness",
                        "body": (
                            f"Earnings report in {days_to_earnings} days ({edate}). "
                            "Monitor IV expansion and analyst estimate revisions as the date approaches."
                        ),
                        "sentiment": "neg",
                        "meta": f"Next earnings: {edate}",
                    }
                )

        # ── Earnings Surprise History ─────────────────────────────────────
        consec_beats = earnings_surp.get("consec_beats", 0)
        misses_4q = earnings_surp.get("misses_last_4q", 0)
        avg_surp_pct = earnings_surp.get("avg_surprise_pct")
        last_surp_pct = earnings_surp.get("last_surprise_pct")
        if earnings_surp:
            sources.add("Earnings")
            if consec_beats >= 4:
                mag_bonus = min(5, round(avg_surp_pct / 5)) if avg_surp_pct and avg_surp_pct > 0 else 0
                score += 10 + mag_bonus
                surp_str = f" avg beat magnitude: +{avg_surp_pct:.1f}%." if avg_surp_pct else ""
                rationale.append(
                    {
                        "src": "Earnings",
                        "head": f"{consec_beats} Consecutive EPS Beats",
                        "body": f"Company has beaten analyst EPS estimates for {consec_beats} consecutive quarters.{surp_str} Management consistently delivers positive surprises — strong execution.",
                        "sentiment": "pos",
                        "meta": f"Consec. beats: {consec_beats}"
                        + (f" | Avg beat: +{avg_surp_pct:.1f}%" if avg_surp_pct else ""),
                    }
                )
            elif consec_beats >= 2:
                score += 5
                surp_str = (
                    f" Last quarter beat by +{last_surp_pct:.1f}%." if last_surp_pct and last_surp_pct > 0 else ""
                )
                rationale.append(
                    {
                        "src": "Earnings",
                        "head": f"{consec_beats} Consecutive EPS Beats",
                        "body": f"Company beat EPS estimates in the last {consec_beats} quarters.{surp_str}",
                        "sentiment": "pos",
                        "meta": f"Consec. beats: {consec_beats}",
                    }
                )
            elif misses_4q >= 3:
                mag_penalty = min(4, round(abs(avg_surp_pct) / 5)) if avg_surp_pct and avg_surp_pct < 0 else 0
                score -= 8 + mag_penalty
                surp_str = f" avg miss magnitude: {avg_surp_pct:.1f}%." if avg_surp_pct else ""
                rationale.append(
                    {
                        "src": "Earnings",
                        "head": f"Repeated EPS Misses ({misses_4q}/4 Quarters)",
                        "body": f"Company missed analyst EPS estimates in {misses_4q} of the last 4 quarters.{surp_str} Guidance and execution are unreliable.",
                        "sentiment": "neg",
                        "meta": f"Misses: {misses_4q} of last 4Q",
                    }
                )

        # ── EPS Surprise Acceleration ─────────────────────────────────────────
        # Compares most-recent quarter surprise% to oldest (of last 4 quarters).
        # Accelerating beats signal improving execution; decelerating may signal
        # kitchen-sink risk even if the company is technically still beating.
        # Data from Finnhub company_earnings() (free, added to earnings_surp dict).
        _surp_accel = (earnings_surp or {}).get("surprise_acceleration")
        _surp_qtrs = (earnings_surp or {}).get("quarterly_surprises", [])
        if _surp_accel is not None and not _is_lev_etf:
            sources.add("Earnings")
            _qtrs_str = " → ".join(f"{s:+.1f}%" for s in _surp_qtrs) if _surp_qtrs else ""
            if _surp_accel >= 5:
                score += 5
                rationale.append(
                    {
                        "src": "Earnings",
                        "head": f"EPS Beat Acceleration (+{_surp_accel:.1f}pp trend)",
                        "body": (
                            f"EPS surprise trajectory: {_qtrs_str}. "
                            f"Beat magnitude accelerated by {_surp_accel:.1f}pp over 4 quarters. "
                            "Accelerating beats signal improving execution and guidance credibility — "
                            "analysts are systematically underestimating this company."
                        ),
                        "sentiment": "pos",
                        "meta": f"surp_acceleration={_surp_accel:+.1f}pp | quarters={_qtrs_str}",
                    }
                )
            elif _surp_accel >= 2:
                score += 2
                rationale.append(
                    {
                        "src": "Earnings",
                        "head": f"EPS Beat Momentum (+{_surp_accel:.1f}pp)",
                        "body": f"EPS surprises mildly accelerating: {_qtrs_str}. Modest positive momentum.",
                        "sentiment": "pos",
                        "meta": f"surp_acceleration={_surp_accel:+.1f}pp",
                    }
                )
            elif _surp_accel <= -5:
                score -= 5
                rationale.append(
                    {
                        "src": "Earnings",
                        "head": f"EPS Beat Deceleration ({_surp_accel:.1f}pp trend)",
                        "body": (
                            f"EPS surprise trajectory: {_qtrs_str}. "
                            f"Beat magnitude shrank by {abs(_surp_accel):.1f}pp over 4 quarters — "
                            "deceleration risk. Even if the company is still beating, shrinking margins "
                            "of surprise often precede an outright miss."
                        ),
                        "sentiment": "neg",
                        "meta": f"surp_acceleration={_surp_accel:+.1f}pp | quarters={_qtrs_str}",
                    }
                )
            elif _surp_accel <= -2:
                score -= 2
                rationale.append(
                    {
                        "src": "Earnings",
                        "head": f"EPS Beat Momentum Fading ({_surp_accel:.1f}pp)",
                        "body": f"EPS surprises mildly decelerating: {_qtrs_str}. Monitor closely.",
                        "sentiment": "neg",
                        "meta": f"surp_acceleration={_surp_accel:+.1f}pp",
                    }
                )

        # ── NLP Earnings Tone Analysis (local LLM) ───────────────────────────
        # Analyses the most recent earnings-related news headlines for management
        # tone signals: hesitation, guidance cuts, evasion. These are leading
        # indicators of fundamental weakness before financials reveal it.
        # Only fires when earnings are within 14 days or just passed (3 days).
        _days_to_earnings = (earnings_cal or {}).get("days_to_earnings")
        _in_earnings_window = _days_to_earnings is not None and (-3 <= _days_to_earnings <= 14)
        if _in_earnings_window and news:
            try:
                from services.local_llm import analyze_news_sentiment, get_llm_client

                _llm = get_llm_client()
                if _llm:
                    _ear_headlines = [
                        n.get("headline", "")
                        for n in (news or [])[:5]
                        if any(
                            kw in n.get("headline", "").lower()
                            for kw in (
                                "earnings",
                                "eps",
                                "revenue",
                                "guidance",
                                "outlook",
                                "quarter",
                                "miss",
                                "beat",
                                "warn",
                            )
                        )
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
                            rationale.append(
                                {
                                    "src": "Earnings",
                                    "head": (
                                        f"LLM Earnings Tone: {'Positive' if _ear_pts > 0 else 'Negative'} "
                                        f"({_ear_pts:+d}pts)"
                                    ),
                                    "body": (
                                        _ear_result.reasoning
                                        or f"NLP analysis of {len(_ear_headlines)} earnings-related headlines "
                                        f"detected {'bullish' if _ear_pts > 0 else 'bearish'} management tone."
                                    ),
                                    "sentiment": "pos" if _ear_pts > 0 else "neg",
                                    "meta": (
                                        f"llm_earnings_score={_ear_score_raw:.2f} "
                                        f"conf={_ear_result.confidence:.0%} "
                                        f"src={_ear_result.source}"
                                    ),
                                }
                            )
            except Exception:
                log.warning("earnings tone LLM analysis failed for %s", ticker, exc_info=True)

        # ── Sector Relative Strength ──────────────────────────────────────
        if sector_rs:
            rs = sector_rs["rs_vs_sector"]
            etf = sector_rs["sector_etf"]
            sources.add("Sector RS")
            if rs > 8:
                score += 10
                rationale.append(
                    {
                        "src": "Sector RS",
                        "head": f"Leading {etf} Sector by +{rs:.1f}%",
                        "body": (
                            f"1-month return is {rs:.1f}% above its {etf} sector ETF. "
                            "Outperforming sector peers signals stock-specific institutional demand."
                        ),
                        "sentiment": "pos",
                        "meta": f"RS vs {etf}: +{rs:.1f}% | Sector 1M: {sector_rs['sector_1m_ret']:+.1f}%",
                    }
                )
            elif rs > 4:
                score += 5
            elif rs < -8:
                score -= 10
                rationale.append(
                    {
                        "src": "Sector RS",
                        "head": f"Lagging {etf} Sector by {abs(rs):.1f}%",
                        "body": (
                            f"1-month return is {abs(rs):.1f}% below its {etf} sector ETF. "
                            "Stock is a sector laggard — possible company-specific weakness."
                        ),
                        "sentiment": "neg",
                        "meta": f"RS vs {etf}: {rs:.1f}% | Sector 1M: {sector_rs['sector_1m_ret']:+.1f}%",
                    }
                )
            elif rs < -4:
                score -= 5

            # Sector RS filter: "strong stock in dying sector" trap.
            # A stock outperforming its sector while the sector itself lags SPY is a
            # false leader — the sector tide is falling and will drag it down.
            sector_1m = sector_rs.get("sector_1m_ret", 0) or 0
            spy_1m_ref = macro.get("spy_1m_ret") or 0
            sector_lag = spy_1m_ref - sector_1m  # positive = sector underperforming SPY
            if score > 0 and rs > 4 and sector_lag > 5:
                score *= 0.82  # ~-18% penalty on BUY conviction
                sources.add("Sector RS")
                rationale.append(
                    {
                        "src": "Sector RS",
                        "head": f"Sector Trap Warning — {etf} Lagging SPY by {sector_lag:.1f}%",
                        "body": (
                            f"{ticker} leads its {etf} sector by +{rs:.1f}% but the {etf} sector "
                            f"itself trails SPY by {sector_lag:.1f}%. A strong stock in a "
                            "deteriorating sector is a common trap — the sector tide eventually drags leaders down."
                        ),
                        "sentiment": "neg",
                        "meta": f"{etf}: {sector_1m:+.1f}% | SPY: {spy_1m_ref:+.1f}% | Gap: -{sector_lag:.1f}%",
                    }
                )

        # ── Sector downtrend BUY gate ─────────────────────────────────────
        # If the sector ETF is itself in a confirmed 1-month downtrend (< -5%),
        # a BUY signal for a stock in that sector needs a stronger score to
        # qualify. Sector headwinds systematically drag individual stocks lower
        # regardless of company-level technical setup.
        if sector_rs and score > 0:
            sector_1m_gate = sector_rs.get("sector_1m_ret", 0) or 0
            etf_gate = sector_rs.get("sector_etf", "")
            if sector_1m_gate < -5.0 and score < 40:
                score = 0
                _force_hold = True  # sector blackout — subsequent signals must not re-open
                sources.add("Risk Gate")
                rationale.append(
                    {
                        "src": "Risk Gate",
                        "head": f"Sector Downtrend Gate — {etf_gate} {sector_1m_gate:+.1f}% (1M)",
                        "body": (
                            f"{etf_gate} sector is down {abs(sector_1m_gate):.1f}% over the past month "
                            f"(threshold: −5%). A marginal BUY signal (score <40) in a deteriorating "
                            "sector has very low win rates — gate to HOLD until sector stabilises."
                        ),
                        "sentiment": "neg",
                        "meta": f"{etf_gate} 1M: {sector_1m_gate:+.1f}% | Score: {score:.1f}",
                    }
                )

        # ── Analyst Price Target (yfinance info) ─────────────────────────
        target_mean = info.get("target_mean")
        analyst_count = info.get("analyst_count") or 0
        if target_mean and analyst_count >= 3 and price > 0:
            upside = (target_mean - price) / price * 100
            target_high = info.get("target_high")
            target_low = info.get("target_low")
            sources.add("Analyst")
            if upside > 20:
                # +15 REMOVED (gate-audit 2026-07-15): 'Analysts See Upside' cohort
                # −8.5pp vs baseline (N=194) — big implied upside on an oversold name
                # is usually a stale target on a crashed price (value-trap magnet),
                # not conviction. Downside penalty branch unchanged.
                rationale.append(
                    {
                        "src": "Analyst",
                        "head": f"Analysts See {upside:.0f}% Upside",
                        "body": (
                            f"{analyst_count} analysts set a consensus price target of ${target_mean:.2f} "
                            f"vs current ${price:.2f} — {upside:.1f}% implied upside."
                            + (
                                f" High: ${target_high:.2f} | Low: ${target_low:.2f}."
                                if target_high and target_low
                                else ""
                            )
                        ),
                        # "neu" not "pos": score contribution removed 2026-07-15 (this
                        # cohort underperforms -8.5pp), so it must not still count as
                        # agreeing evidence for the Tier-6 clustering / orthogonality
                        # boosts below — that would silently reintroduce the same
                        # inflation the gate-audit removed.
                        "sentiment": "neu",
                        "meta": f"Target ${target_mean:.2f} | {analyst_count} analysts",
                    }
                )
            elif upside > 10:
                # +8 removed with the +15 branch above (same audit).
                rationale.append(
                    {
                        "src": "Analyst",
                        "head": f"Analysts See {upside:.0f}% Upside",
                        "body": (
                            f"Consensus target ${target_mean:.2f} implies {upside:.1f}% upside from ${price:.2f} "
                            f"across {analyst_count} analysts."
                        ),
                        "sentiment": "neu",
                        "meta": f"Target ${target_mean:.2f} | {analyst_count} analysts",
                    }
                )
            elif upside < -15:
                analyst_score -= 12
                rationale.append(
                    {
                        "src": "Analyst",
                        "head": f"Analysts See {abs(upside):.0f}% Downside",
                        "body": (
                            f"Consensus target ${target_mean:.2f} is {abs(upside):.1f}% below current price ${price:.2f}. "
                            f"{analyst_count} analysts collectively see limited upside."
                        ),
                        "sentiment": "neg",
                        "meta": f"Target ${target_mean:.2f} | {analyst_count} analysts",
                    }
                )
            elif upside < -5:
                analyst_score -= 6
                rationale.append(
                    {
                        "src": "Analyst",
                        "head": "Analyst Target Below Market Price",
                        "body": (
                            f"Consensus target ${target_mean:.2f} is {abs(upside):.1f}% below ${price:.2f}. "
                            f"Street expects limited near-term upside."
                        ),
                        "sentiment": "neg",
                        "meta": f"Target ${target_mean:.2f} | {analyst_count} analysts",
                    }
                )

        # ── Analyst Recommendation Consensus (yfinance info) ─────────────
        rec_key = info.get("rec_key", "")
        rec_mean = info.get("rec_mean")
        if rec_key:
            sources.add("Analyst")
            if rec_key in ("strong_buy", "strongBuy") or (rec_mean and rec_mean <= 1.5):
                analyst_score += 10
                rationale.append(
                    {
                        "src": "Analyst",
                        "head": "Analysts Rate Stock: Strong Buy",
                        "body": "Majority of covering analysts have a Strong Buy consensus. Institutional conviction is high.",
                        "sentiment": "pos",
                        "meta": f"Consensus: {rec_key} (score {rec_mean:.1f}/5)"
                        if rec_mean
                        else f"Consensus: {rec_key}",
                    }
                )
            elif rec_key == "buy" or (rec_mean and rec_mean <= 2.2):
                analyst_score += 6
                rationale.append(
                    {
                        "src": "Analyst",
                        "head": "Analysts Rate Stock: Buy",
                        "body": "Analyst consensus leans towards a Buy rating.",
                        "sentiment": "pos",
                        "meta": f"Consensus: {rec_key}" + (f" ({rec_mean:.1f}/5)" if rec_mean else ""),
                    }
                )
            elif rec_key == "sell" or (rec_mean and rec_mean >= 3.8):
                analyst_score -= 8
                rationale.append(
                    {
                        "src": "Analyst",
                        "head": "Analysts Rate Stock: Sell",
                        "body": "Analyst consensus leans towards a Sell rating. Street is bearish.",
                        "sentiment": "neg",
                        "meta": f"Consensus: {rec_key}" + (f" ({rec_mean:.1f}/5)" if rec_mean else ""),
                    }
                )
            elif rec_key in ("strong_sell", "strongSell") or (rec_mean and rec_mean >= 4.5):
                analyst_score -= 12
                rationale.append(
                    {
                        "src": "Analyst",
                        "head": "Analysts Rate Stock: Strong Sell",
                        "body": "Strong Sell consensus across covering analysts. Institutional conviction is bearish.",
                        "sentiment": "neg",
                        "meta": f"Consensus: {rec_key}" + (f" ({rec_mean:.1f}/5)" if rec_mean else ""),
                    }
                )

        # ── Finnhub Analyst Recommendation Trends ────────────────────────
        if analyst_recs:
            sb = analyst_recs.get("strong_buy", 0)
            b = analyst_recs.get("buy", 0)
            h = analyst_recs.get("hold", 0)
            s = analyst_recs.get("sell", 0)
            ss = analyst_recs.get("strong_sell", 0)
            total_recs = sb + b + h + s + ss
            if total_recs >= 5:
                sources.add("Analyst")
                bull_pct = (sb + b) / total_recs * 100
                bear_pct = (s + ss) / total_recs * 100
                period = analyst_recs.get("period", "")
                if bull_pct >= 70:
                    analyst_score += 10
                    rationale.append(
                        {
                            "src": "Analyst",
                            "head": f"{bull_pct:.0f}% of Analysts are Bullish",
                            "body": (
                                f"Finnhub consensus ({period}): {sb} Strong Buy + {b} Buy out of {total_recs} analysts. "
                                f"Strong institutional buy-side conviction."
                            ),
                            "sentiment": "pos",
                            "meta": f"SB:{sb} B:{b} H:{h} S:{s} SS:{ss}",
                        }
                    )
                elif bull_pct >= 55:
                    analyst_score += 5
                elif bear_pct >= 60:
                    analyst_score -= 8
                    rationale.append(
                        {
                            "src": "Analyst",
                            "head": f"{bear_pct:.0f}% of Analysts are Bearish",
                            "body": (
                                f"Finnhub consensus ({period}): {s} Sell + {ss} Strong Sell out of {total_recs} analysts. "
                                f"Street is broadly negative on this stock."
                            ),
                            "sentiment": "neg",
                            "meta": f"SB:{sb} B:{b} H:{h} S:{s} SS:{ss}",
                        }
                    )

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
                rationale.append(
                    {
                        "src": "Analyst",
                        "head": f"Analyst Upgrade Momentum (+{rev_pts:.0f}pts vs {rev_period})",
                        "body": (
                            f"Bull score rose by {bull_d:+.0f} and bear score changed by {bear_d:+.0f} "
                            f"vs {rev_period}. Rising upgrades with falling downgrades is one of the "
                            "strongest documented equity alpha factors — price follows estimates."
                        ),
                        "sentiment": "pos",
                        "meta": f"rev_pts={rev_pts:+.0f} | bull_delta={bull_d:+.0f} | bear_delta={bear_d:+.0f}",
                    }
                )
            else:
                rationale.append(
                    {
                        "src": "Analyst",
                        "head": f"Analyst Downgrade Momentum ({rev_pts:.0f}pts vs {rev_period})",
                        "body": (
                            f"Bull score fell by {abs(bull_d):.0f} and bear score rose by {abs(bear_d):.0f} "
                            f"vs {rev_period}. Analysts are cutting estimates — forward earnings are "
                            "deteriorating. Negative revision momentum precedes price weakness."
                        ),
                        "sentiment": "neg",
                        "meta": f"rev_pts={rev_pts:+.0f} | bull_delta={bull_d:+.0f} | bear_delta={bear_d:+.0f}",
                    }
                )

        # Massive Analyst Intelligence (Bulls Bears Say + Guidance) REMOVED
        # (dead-code audit 2026-07-14): zero cards from either branch across
        # 87,982 all-time signals — get_analyst_intelligence() never yields
        # actionable scores. Other analyst scoring (targets/recs) unaffected.

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
        hmm_regime = hmm.get("regime", "")
        bull_prob = hmm.get("bull_prob", 0.5)
        bear_prob = hmm.get("bear_prob", 0.5)
        trans_risk = hmm.get("transition_risk", 0.1)
        vix_z = hmm.get("vix_z", 0.0)

        if hmm_regime:
            # HMM data available — use continuous probability weighting
            if hmm_regime == "bear" and bear_prob >= 0.70:
                score *= 0.72
                rationale.append(
                    {
                        "src": "Macro",
                        "head": f"HMM Bear Regime ({bear_prob:.0%} probability) — Score Reduced",
                        "body": (
                            f"The macro regime model assigns {bear_prob:.0%} probability to a risk-off state. "
                            f"VIX z-score: {vix_z:+.1f}σ. Signal reliability is structurally lower in bear regimes — "
                            f"reduce position size and widen stops."
                        ),
                        "sentiment": "neg",
                        "meta": f"HMM bear={bear_prob:.0%} vix_z={vix_z:+.1f}σ",
                    }
                )
            elif hmm_regime == "transition" or trans_risk > 0.15:
                score *= 0.88
                rationale.append(
                    {
                        "src": "Macro",
                        "head": f"HMM Regime Transition Risk ({trans_risk:.0%}) — Caution",
                        "body": (
                            f"The HMM detects elevated probability of a regime shift "
                            f"(bull→bear or vice versa) within 1–3 days. "
                            f"P(bull)={bull_prob:.0%} P(bear)={bear_prob:.0%}. "
                            f"Consider tighter stops until regime resolves."
                        ),
                        "sentiment": "neg",
                        "meta": f"trans_risk={trans_risk:.0%}",
                    }
                )
            elif hmm_regime == "bull" and bull_prob >= 0.75 and vix_z < -0.5:
                score *= 1.06
                rationale.append(
                    {
                        "src": "Macro",
                        "head": f"HMM Bull Regime ({bull_prob:.0%}) — Favourable",
                        "body": (
                            f"Macro regime model: {bull_prob:.0%} probability of risk-on state. "
                            f"VIX below historical mean ({vix_z:+.1f}σ). "
                            f"Trend-following signals are more reliable in this environment."
                        ),
                        "sentiment": "pos",
                        "meta": f"HMM bull={bull_prob:.0%} vix_z={vix_z:+.1f}σ",
                    }
                )
        else:
            # Fallback to legacy static VIX thresholds when HMM data unavailable
            if vix is not None:
                if vix > 35:
                    score *= 0.60
                    rationale.append(
                        {
                            "src": "Macro",
                            "head": f"VIX Extreme Fear ({vix:.0f}) — Confidence Reduced",
                            "body": f"VIX at {vix:.0f} signals panic-level volatility. Technical patterns break down in these conditions. Reduce position size significantly.",
                            "sentiment": "neg",
                            "meta": f"VIX = {vix:.0f}",
                        }
                    )
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
            eh_gap = ext_hours.get("gap_pct", 0) or 0
            eh_vol_r = ext_hours.get("vol_ratio", 1) or 1
            eh_price = ext_hours.get("price")
            eh_prev = ext_hours.get("prev_close")
            sources.add("Technical")

            # Gap magnitude signal — direction-aware
            if abs(eh_gap) >= 1.0:
                # High-volume gap: more likely to continue; low-volume: more likely to fill
                high_vol = eh_vol_r >= 1.5
                if eh_gap >= 3.0:
                    bonus = 12 if high_vol else 6
                    score += bonus
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"{'Pre' if session == 'pre' else 'After'}-Market Gap Up +{eh_gap:.1f}%{' (High Vol)' if high_vol else ''}",
                            "body": (
                                f"Price gapped {eh_gap:.1f}% above the prior regular-session close "
                                f"(${eh_prev:.2f} → ${eh_price:.2f}) in extended hours. "
                                + (
                                    f"High volume ({eh_vol_r:.1f}× avg) confirms institutional conviction — gap likely to hold."
                                    if high_vol
                                    else f"Light volume ({eh_vol_r:.1f}× avg) — gap may fill at open."
                                )
                            ),
                            "sentiment": "pos",
                            "meta": f"EH gap: +{eh_gap:.1f}% | Vol ratio: {eh_vol_r:.1f}×",
                        }
                    )
                elif eh_gap >= 1.0:
                    bonus = 6 if high_vol else 3
                    score += bonus
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"{'Pre' if session == 'pre' else 'After'}-Market Gap Up +{eh_gap:.1f}%",
                            "body": (
                                f"Moderate extended-hours gap of +{eh_gap:.1f}%. "
                                + ("Volume confirms the move.".format() if high_vol else "Watch for fill at open.")
                            ),
                            "sentiment": "pos",
                            "meta": f"EH gap: +{eh_gap:.1f}% | Vol: {eh_vol_r:.1f}×",
                        }
                    )
                elif eh_gap <= -3.0:
                    penalty = -12 if high_vol else -6
                    score += penalty
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"{'Pre' if session == 'pre' else 'After'}-Market Gap Down {eh_gap:.1f}%{' (High Vol)' if high_vol else ''}",
                            "body": (
                                f"Price gapped {eh_gap:.1f}% below the prior close "
                                f"(${eh_prev:.2f} → ${eh_price:.2f}) in extended hours. "
                                + (
                                    "High volume confirms distribution — gap likely to persist.".format()
                                    if high_vol
                                    else "Low volume — gap may partially fill at open."
                                )
                            ),
                            "sentiment": "neg",
                            "meta": f"EH gap: {eh_gap:.1f}% | Vol ratio: {eh_vol_r:.1f}×",
                        }
                    )
                elif eh_gap <= -1.0:
                    penalty = -6 if high_vol else -3
                    score += penalty
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"{'Pre' if session == 'pre' else 'After'}-Market Gap Down {eh_gap:.1f}%",
                            "body": (
                                f"Moderate extended-hours gap of {eh_gap:.1f}%. "
                                + (
                                    "Volume confirms selling pressure."
                                    if high_vol
                                    else "Low volume — may recover at open."
                                )
                            ),
                            "sentiment": "neg",
                            "meta": f"EH gap: {eh_gap:.1f}% | Vol: {eh_vol_r:.1f}×",
                        }
                    )

            # Extended-hours volume-surge bonus REMOVED (dead-code audit
            # 2026-07-14): 0 fires in 87,982 signals — the vol_r>=3 with
            # |gap|<1% combination never occurs in practice. The gap up/down
            # cards above fire and are unchanged.

        # ── Options flow (yfinance multi-expiry enhanced sweep detection) ───
        if opt_flow:
            opt_score, opt_rationale = score_options(opt_flow)
            if opt_score != 0:
                score += opt_score
                sources.add("Options")
                rationale.extend(opt_rationale)

        # 8-K material-events scoring REMOVED (dead-code audit 2026-07-14):
        # 0 cards in 87,982 signals — get_8k_signals() never returns |score|>=3.
        # services/eightk_events.py retained for research.

        # ── Massive Financial Ratios (augment yfinance fundamentals) ─────────
        try:
            from services.massive_ratios import get_ratios, merge_with_yfinance

            massive_r = await get_ratios(ticker)
            if massive_r and fundamentals:
                fundamentals = merge_with_yfinance(fundamentals, massive_r)
        except ImportError:
            pass  # optional service
        except Exception as _ratios_err:
            log.warning("[engine] %s massive_ratios failed (API schema change?): %s", ticker, _ratios_err)

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
        except ImportError:
            pass  # optional service
        except Exception as _chain_err:
            log.warning("[engine] %s option chain scoring failed (API schema change?): %s", ticker, _chain_err)

        # ── ETF Constituent Flow Amplification ────────────────────────────────
        try:
            from services.etf_constituents import get_flow_amplifier
            from services.etf_flows import get_flow_score_for_ticker
            from services.sector import SECTOR_MAP

            etf_for_ticker = SECTOR_MAP.get(ticker)
            if etf_for_ticker:
                amp = get_flow_amplifier(ticker, etf_for_ticker)
                if amp > 1.0:
                    flow_sc, _ = get_flow_score_for_ticker(ticker, (market_ctx or {}).get("etf_flows"))
                    if abs(flow_sc) >= 2.0:
                        bonus = round(flow_sc * (amp - 1.0), 1)
                        score += bonus
        except ImportError:
            pass  # optional service
        except Exception as _etf_err:
            log.debug("[engine] %s ETF flow amplification failed: %s", ticker, _etf_err)

        # ── 13F Institutional flow (with QoQ trend) ──────────────────────────
        inst_signals = (market_ctx or {}).get("institutional_signals", {})
        if ticker in inst_signals:
            inst_sig = inst_signals[ticker]
            inst_score = inst_sig.get("score", 0)
            qoq_trend = inst_sig.get("qoq_trend", "neutral")
            if inst_score != 0:
                score += inst_score
                sources.add("13F")
                rat = inst_sig.get("rationale", {})
                if rat:
                    rationale.append(rat)
                # Add an extra QoQ-specific rationale item for rising/falling trends
                if qoq_trend == "rising" and inst_score > 0:
                    rationale.append(
                        {
                            "src": "13F",
                            "head": "Institutional Conviction Rising — 2+ Consecutive Quarters Buying",
                            "body": (
                                f"Multiple institutional investors have increased their {ticker} position "
                                "for two or more consecutive quarters. Sustained accumulation signals "
                                "growing conviction rather than a one-off position initiation."
                            ),
                            "sentiment": "pos",
                            "meta": "QoQ trend: rising",
                        }
                    )
                elif qoq_trend == "falling" and inst_score < 0:
                    rationale.append(
                        {
                            "src": "13F",
                            "head": "Institutional Conviction Falling — 2+ Consecutive Quarters Exiting",
                            "body": (
                                f"Institutions have reduced their {ticker} stake for two or more consecutive "
                                "quarters. Sequential selling is an early exit warning — smart money is "
                                "methodically reducing exposure."
                            ),
                            "sentiment": "neg",
                            "meta": "QoQ trend: falling",
                        }
                    )

        # ── Cointegration / Pairs Trading ────────────────────────────────────────
        pairs_signals = (market_ctx or {}).get("pairs_signals", {})
        if ticker in pairs_signals:
            ps = pairs_signals[ticker]
            ps_score = ps.get("score", 0)
            if abs(ps_score) >= 5:
                score += ps_score
                sources.add("Stat Arb")
                pair = ps.get("pair_ticker", "?")
                zscore = ps.get("zscore", 0)
                direction = ps.get("direction", "")
                corr = ps.get("correlation", 0)
                rationale.append(
                    {
                        "src": "Stat Arb",
                        "head": f"Pairs Divergence vs {pair} — {direction.title()} ({zscore:+.1f}σ)",
                        "body": (
                            f"{ticker} is {direction} relative to its cointegrated pair {pair} "
                            f"(spread z-score {zscore:+.1f}σ, {corr:.0%} rolling correlation). "
                            "Statistical arbitrage signals of this magnitude mean-revert "
                            "within 5–15 trading days historically."
                        ),
                        "sentiment": "pos" if ps_score > 0 else "neg",
                        "meta": f"Z-score: {zscore:+.1f}σ | Pair: {pair} | Corr: {corr:.2f}",
                    }
                )

        # CBOE P/C contrarian + flow-confirmation scoring REMOVED (dead-code
        # audit 2026-07-14): all 5 card variants show 0 fires in 87,982
        # all-time signals — market_ctx['put_call'] never populates because the
        # CBOE daily-stats CSVs return 403 (known-broken feed, see memory/
        # free-backtest-data-fred). Per-ticker options flow via score_options()
        # is unaffected and remains the live options signal.

        # ── Market Breadth (% of S&P 500 basket above SMA50/200) ────────────
        breadth = (market_ctx or {}).get("breadth")
        if breadth and breadth.get("signal") != "neutral" and breadth.get("score"):
            b_score = breadth["score"]
            pct_200 = breadth["pct_above_200d"]
            pct_50 = breadth["pct_above_50d"]
            score += b_score
            sources.add("Market Breadth")
            if b_score >= 10:
                rationale.append(
                    {
                        "src": "Market Breadth",
                        "head": f"Broad Market Participation — {pct_200:.0f}% of S&P 500 Above 200-DMA",
                        "body": (
                            f"{pct_200:.0f}% of leading S&P 500 stocks trade above their 200-day average "
                            f"and {pct_50:.0f}% are above their 50-day average. "
                            "Wide participation confirms the uptrend and provides a strong tailwind for long positions."
                        ),
                        "sentiment": "pos",
                        "meta": f"Breadth: {pct_200:.0f}% >200d | {pct_50:.0f}% >50d",
                    }
                )
            elif b_score >= 5:
                rationale.append(
                    {
                        "src": "Market Breadth",
                        "head": f"Healthy Market Breadth — {pct_200:.0f}% Above 200-DMA",
                        "body": (
                            "More than half of S&P 500 benchmark stocks trade above their 200-day average. "
                            "Market internals are constructive — the broad trend supports new longs."
                        ),
                        "sentiment": "pos",
                        "meta": f"Breadth: {pct_200:.0f}% >200d | {pct_50:.0f}% >50d",
                    }
                )
            elif b_score <= -10:
                rationale.append(
                    {
                        "src": "Market Breadth",
                        "head": f"Market Breadth Deteriorating — Only {pct_200:.0f}% Above 200-DMA",
                        "body": (
                            f"Fewer than 1 in 3 S&P 500 stocks trade above their 200-day average "
                            f"({pct_200:.0f}%). Broad market deterioration reduces the probability of "
                            "individual stock gains — favour defensive positioning or reduced exposure."
                        ),
                        "sentiment": "neg",
                        "meta": f"Breadth: {pct_200:.0f}% >200d | {pct_50:.0f}% >50d",
                    }
                )
            elif b_score <= -5:
                rationale.append(
                    {
                        "src": "Market Breadth",
                        "head": f"Weakening Market Breadth — {pct_200:.0f}% Above 200-DMA",
                        "body": (
                            "Less than half of S&P 500 benchmark stocks are above their 200-day average. "
                            "Market internals are weakening — be selective with new long entries."
                        ),
                        "sentiment": "neg",
                        "meta": f"Breadth: {pct_200:.0f}% >200d | {pct_50:.0f}% >50d",
                    }
                )

        # ── Normalise gathered values ────────────────────────────────────────
        social = social or {}
        fundamentals = fundamentals or {}

        # ── Ichimoku Cloud ───────────────────────────────────────────────────
        ichi_tenkan = tech.get("ichi_tenkan")
        ichi_kijun = tech.get("ichi_kijun")
        ichi_tenkan_p = tech.get("ichi_tenkan_p")
        ichi_kijun_p = tech.get("ichi_kijun_p")
        ichi_cloud_top = tech.get("ichi_cloud_top")
        ichi_cloud_bot = tech.get("ichi_cloud_bot")
        ichi_cloud_bull = tech.get("ichi_cloud_bull")
        ichi_chikou = tech.get("ichi_chikou_above")
        if ichi_tenkan is not None and ichi_kijun is not None:
            sources.add("Technical")
            # Tenkan/Kijun cross
            if ichi_tenkan_p and ichi_kijun_p and ichi_tenkan_p <= ichi_kijun_p and ichi_tenkan > ichi_kijun:
                ichimoku_score += 10
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Ichimoku Bullish Cross (TK Cross)",
                        "body": "Tenkan-sen crossed above Kijun-sen — a classic Ichimoku buy signal called the 'TK Cross'. Momentum has shifted bullish.",
                        "sentiment": "pos",
                        "meta": f"Tenkan {ichi_tenkan:.2f} > Kijun {ichi_kijun:.2f}",
                    }
                )
            elif ichi_tenkan_p and ichi_kijun_p and ichi_tenkan_p >= ichi_kijun_p and ichi_tenkan < ichi_kijun:
                ichimoku_score -= 10
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Ichimoku Bearish Cross (Dead Cross)",
                        "body": "Tenkan-sen crossed below Kijun-sen — a classic Ichimoku sell signal. Momentum has shifted bearish.",
                        "sentiment": "neg",
                        "meta": f"Tenkan {ichi_tenkan:.2f} < Kijun {ichi_kijun:.2f}",
                    }
                )
            # Price vs Cloud
            if ichi_cloud_top and ichi_cloud_bot:
                if price > ichi_cloud_top:
                    ichimoku_score += 8
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"Price Above Ichimoku Cloud (${ichi_cloud_top:.2f})",
                            "body": f"Price is trading above the Kumo cloud — the Ichimoku trend filter is bullish. The cloud acts as strong support at ${ichi_cloud_bot:.2f}–${ichi_cloud_top:.2f}.",
                            "sentiment": "pos",
                            "meta": f"Cloud: {ichi_cloud_bot:.2f}–{ichi_cloud_top:.2f} | {'Green (bullish)' if ichi_cloud_bull else 'Red (bearish)'}",
                        }
                    )
                elif price < ichi_cloud_bot:
                    ichimoku_score -= 8
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"Price Below Ichimoku Cloud (${ichi_cloud_bot:.2f})",
                            "body": f"Price is below the Kumo cloud — the Ichimoku trend filter is bearish. The cloud acts as resistance at ${ichi_cloud_bot:.2f}–${ichi_cloud_top:.2f}.",
                            "sentiment": "neg",
                            "meta": f"Cloud: {ichi_cloud_bot:.2f}–{ichi_cloud_top:.2f}",
                        }
                    )
            # Chikou confirmation — symmetric: confirm = ±4, contradict = ∓4
            if ichi_chikou is True:
                ichimoku_score += 4  # Chikou above price 26 bars ago: bullish
            elif ichi_chikou is False:
                ichimoku_score -= 4  # Chikou below price 26 bars ago: bearish

            # Apply Ichimoku system bucket cap: TK cross + cloud + chikou are three
            # readings from one indicator — prevent the system from triple-counting.
            # 0.85 discount: cloud position overlaps with SMA200/50 in ma_score.
            score += max(-14, min(14, ichimoku_score)) * 0.85

        # ── Chaikin Money Flow ───────────────────────────────────────────────
        # CMF and OBV both measure volume-weighted money flow direction.
        # Routed into volume_score (same bucket as OBV) so they contribute once.
        cmf = tech.get("cmf")
        cmf_prev = tech.get("cmf_prev")
        change_pct_abs = abs(tech.get("change_pct", 0) or 0)
        if cmf is not None:
            # §46 ablation: CMF is redundant with TREND=0 (OBV/RVOL carry same info).
            # Scores halved (0.5×) to retain it as a qualitative gate/rationale card
            # without double-counting the money-flow signal already captured by OBV.
            sources.add("Technical")
            if cmf > 0.20:
                volume_score += 5
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"CMF Strong Accumulation ({cmf:+.2f})",
                        "body": (
                            f"CMF at {cmf:+.2f} — heavy institutional accumulation. "
                            "Money flow is well above the +0.1 threshold, confirming sustained smart-money buying."
                        ),
                        "sentiment": "pos",
                        "meta": f"CMF(20) = {cmf:+.2f}",
                    }
                )
            elif cmf > 0.15:
                volume_score += 4
                if change_pct_abs < 0.5:
                    volume_score += 2
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"CMF Stealth Accumulation ({cmf:+.2f})",
                            "body": (
                                f"CMF at {cmf:+.2f} while price is nearly flat ({tech.get('change_pct', 0):+.2f}%). "
                                "Institutions are quietly accumulating without moving the price — a very reliable precursor to a breakout."
                            ),
                            "sentiment": "pos",
                            "meta": f"CMF(20) = {cmf:+.2f} | Price flat",
                        }
                    )
                else:
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"Chaikin Money Flow Bullish ({cmf:+.2f})",
                            "body": f"CMF at {cmf:+.2f} — sustained accumulation. Money is flowing into this stock on high volume. Institutional buyers are active.",
                            "sentiment": "pos",
                            "meta": f"CMF(20) = {cmf:+.2f}",
                        }
                    )
            elif cmf > 0.05:
                volume_score += 2
                if cmf_prev is not None and cmf > cmf_prev + 0.05:
                    volume_score += 1
            elif cmf < -0.20:
                volume_score -= 5
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"CMF Strong Distribution ({cmf:+.2f})",
                        "body": (
                            f"CMF at {cmf:+.2f} — heavy institutional distribution. "
                            "Persistent outflows at this level signal sustained smart-money selling."
                        ),
                        "sentiment": "neg",
                        "meta": f"CMF(20) = {cmf:+.2f}",
                    }
                )
            elif cmf < -0.15:
                volume_score -= 4
                if change_pct_abs < 0.5:
                    volume_score -= 2
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"CMF Stealth Distribution ({cmf:+.2f})",
                            "body": (
                                f"CMF at {cmf:+.2f} while price is nearly flat. "
                                "Institutions are quietly selling into price stability — bearish divergence."
                            ),
                            "sentiment": "neg",
                            "meta": f"CMF(20) = {cmf:+.2f} | Price flat",
                        }
                    )
                else:
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"Chaikin Money Flow Bearish ({cmf:+.2f})",
                            "body": f"CMF at {cmf:+.2f} — sustained distribution. Money is flowing out of this stock. Institutional sellers are dominating.",
                            "sentiment": "neg",
                            "meta": f"CMF(20) = {cmf:+.2f}",
                        }
                    )
            elif cmf < -0.05:
                volume_score -= 2
                if cmf_prev is not None and cmf < cmf_prev - 0.05:
                    volume_score -= 1

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
        vwap_20 = tech.get("vwap_20")
        vwap_pct = tech.get("vwap_pct")  # positive = above VWAP, negative = below
        if vwap_20 is not None and vwap_pct is not None:
            sources.add("Technical")
            is_oversold_play = rsi is not None and rsi < 35  # exempt mean-reversion
            if score > 0 and vwap_pct < -2.0 and not is_oversold_play:
                # BUY signal with price meaningfully below VWAP — liquidity headwind
                penalty = min(12, abs(vwap_pct) * 1.0)  # 1pt per % below, cap 12
                score -= penalty
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Price Below 20-Day VWAP ({vwap_pct:+.1f}%) — Liquidity Headwind",
                        "body": (
                            f"Price is {abs(vwap_pct):.1f}% below the 20-day VWAP (${vwap_20:.2f}). "
                            "Participants who bought over the past 20 sessions are on average underwater, "
                            "creating overhead supply as they exit at break-even. "
                            "BUY signals below VWAP have lower win rates unless confirmed by volume expansion."
                        ),
                        "sentiment": "neg",
                        "meta": f"Price ${price:.2f} vs VWAP ${vwap_20:.2f} ({vwap_pct:+.1f}%)",
                    }
                )
            elif score > 0 and vwap_pct >= 1.0:
                # Price above VWAP: participants are in profit — less overhead supply
                bonus = min(5, vwap_pct * 0.4)
                score += bonus
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Price Above VWAP ({vwap_pct:+.1f}%) — Institutional Cost Basis Holds",
                        "body": (
                            f"Price is {vwap_pct:.1f}% above the 20-day VWAP (${vwap_20:.2f}). "
                            "The average participant over the last 20 sessions is in profit — "
                            "reduced overhead supply, supportive for continued upside."
                        ),
                        "sentiment": "pos",
                        "meta": f"Price ${price:.2f} vs VWAP ${vwap_20:.2f} ({vwap_pct:+.1f}%)",
                    }
                )

        # ── VWAP Slope — institutional direction ─────────────────────────────
        vwap_slope_pos = tech.get("vwap_slope_pos")
        if vwap_slope_pos is not None and vwap_20 is not None and vwap_pct is not None:
            sources.add("Technical")
            if vwap_slope_pos and vwap_pct > 0:
                score += 6
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"VWAP Rising + Price Above ({vwap_pct:+.1f}%) — Institutional Accumulation",
                        "body": (
                            f"The 20-day VWAP (${vwap_20:.2f}) is trending upward and price is above it. "
                            "Rising VWAP means the average cost basis is improving — institutional buyers "
                            "are consistently accumulating at higher prices."
                        ),
                        "sentiment": "pos",
                        "meta": f"VWAP slope=up | Price {vwap_pct:+.1f}% above",
                    }
                )
            elif not vwap_slope_pos and vwap_pct < 0:
                score -= 5
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"VWAP Falling + Price Below ({vwap_pct:+.1f}%) — Institutional Distribution",
                        "body": (
                            f"The 20-day VWAP (${vwap_20:.2f}) is declining and price is below it. "
                            "Falling VWAP reflects persistent institutional selling — the average participant "
                            "is underwater and selling into any recovery."
                        ),
                        "sentiment": "neg",
                        "meta": f"VWAP slope=down | Price {vwap_pct:+.1f}% below",
                    }
                )

        # ── VWAP σ Bands — mean reversion extremes ───────────────────────────
        # σ bands use std dev of price around VWAP (not Bollinger — different distribution).
        # BUG FIX: these signals were only going to mean_rev_score (for stretch dampening)
        # but NOT to score directly. mean_rev_score was already assembled at line ~2200;
        # second-block additions only affect _stretch_total, not the final score.
        # Fix: add score directly (capped) to match the backtest which includes VWAP bands
        # in the MR family and routes them to the assembled score.
        vwap_b2u = tech.get("vwap_band2_upper")
        vwap_b2l = tech.get("vwap_band2_lower")
        vwap_b1u = tech.get("vwap_band1_upper")
        vwap_b1l = tech.get("vwap_band1_lower")
        if all(v is not None for v in (vwap_b2u, vwap_b2l, vwap_b1u, vwap_b1l, vwap_20)):
            sources.add("Technical")
            if price >= vwap_b2u:
                mean_rev_score -= 14  # keeps _stretch_total dampening
                score -= 10  # direct score contribution (backtest parity)
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"VWAP +2σ Band Touch (${vwap_b2u:.2f}) — Extreme Overbought",
                        "body": (
                            f"Price at ${price:.2f} has reached the VWAP +2σ band (${vwap_b2u:.2f}). "
                            "Statistically rare overextension above institutional cost basis. "
                            f"High-probability mean reversion back toward VWAP (${vwap_20:.2f})."
                        ),
                        "sentiment": "neg",
                        "meta": f"+2σ band = ${vwap_b2u:.2f}",
                    }
                )
            elif price >= vwap_b1u:
                mean_rev_score -= 8
                score -= 6
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"VWAP +1σ Band Touch (${vwap_b1u:.2f}) — Overbought vs VWAP",
                        "body": (
                            f"Price at the VWAP +1σ band (${vwap_b1u:.2f}). "
                            "Extended above the average institutional cost basis — distribution risk."
                        ),
                        "sentiment": "neg",
                        "meta": f"+1σ band = ${vwap_b1u:.2f}",
                    }
                )
            elif price <= vwap_b2l:
                mean_rev_score += 14
                score += 10  # direct score contribution
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"VWAP −2σ Band Touch (${vwap_b2l:.2f}) — Extreme Oversold",
                        "body": (
                            f"Price at ${price:.2f} has reached the VWAP −2σ band (${vwap_b2l:.2f}). "
                            "Extreme statistical discount to institutional cost basis — "
                            f"high-probability bounce back toward VWAP (${vwap_20:.2f})."
                        ),
                        "sentiment": "pos",
                        "meta": f"−2σ band = ${vwap_b2l:.2f}",
                    }
                )
            elif price <= vwap_b1l:
                mean_rev_score += 8
                score += 6
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"VWAP −1σ Band Touch (${vwap_b1l:.2f}) — Oversold vs VWAP",
                        "body": (
                            f"Price at the VWAP −1σ band (${vwap_b1l:.2f}). "
                            "Discounted below the average institutional cost basis — bounce potential."
                        ),
                        "sentiment": "pos",
                        "meta": f"−1σ band = ${vwap_b1l:.2f}",
                    }
                )

        # ── VWAP Cross + RVOL — confirmed institutional shift ────────────────
        _vwap_pct_prev = tech.get("vwap_pct_prev")
        _rvol_now = tech.get("rvol") or 0
        if vwap_pct is not None and _vwap_pct_prev is not None and _rvol_now >= 2.0 and vwap_20 is not None:
            sources.add("Technical")
            if _vwap_pct_prev < 0 <= vwap_pct:
                score += 16
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"VWAP Cross Bullish + RVOL {_rvol_now:.1f}× — Institutional Shift",
                        "body": (
                            f"Price just crossed above the 20-day VWAP (${vwap_20:.2f}) on "
                            f"{_rvol_now:.1f}× average volume. High-volume VWAP reclaims signal "
                            "a genuine institutional sentiment shift — not a low-conviction drift."
                        ),
                        "sentiment": "pos",
                        "meta": f"VWAP cross UP | RVOL {_rvol_now:.1f}×",
                    }
                )
            elif _vwap_pct_prev > 0 >= vwap_pct:
                score -= 14
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"VWAP Cross Bearish + RVOL {_rvol_now:.1f}× — Institutional Exit",
                        "body": (
                            f"Price just crossed below the 20-day VWAP (${vwap_20:.2f}) on "
                            f"{_rvol_now:.1f}× average volume. Confirmed institutional distribution — "
                            "smart money is exiting on elevated volume."
                        ),
                        "sentiment": "neg",
                        "meta": f"VWAP cross DOWN | RVOL {_rvol_now:.1f}×",
                    }
                )

        # ── Donchian Channel Breakout ────────────────────────────────────────
        dc_high = tech.get("donchian_high")
        dc_low = tech.get("donchian_low")
        dc_high_p = tech.get("donchian_high_p")
        dc_low_p = tech.get("donchian_low_p")
        if dc_high and dc_low and dc_high_p and dc_low_p:
            if price >= dc_high and price > dc_high_p:
                momentum_score += 10
                sources.add("Technical")
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Donchian 20-Day High Breakout (${dc_high:.2f})",
                        "body": f"Price broke out above the 20-day Donchian channel high (${dc_high:.2f}). The original Turtle Trading breakout signal — momentum is accelerating.",
                        "sentiment": "pos",
                        "meta": f"20d High = ${dc_high:.2f}",
                    }
                )
            elif price <= dc_low and price < dc_low_p:
                momentum_score -= 10
                sources.add("Technical")
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Donchian 20-Day Low Breakdown (${dc_low:.2f})",
                        "body": f"Price broke below the 20-day Donchian channel low (${dc_low:.2f}). Classic momentum breakdown — selling pressure is accelerating.",
                        "sentiment": "neg",
                        "meta": f"20d Low = ${dc_low:.2f}",
                    }
                )

        # ── Price Structure (HH/HL or LH/LL) ────────────────────────────────
        # Backtest-validated (alpha decomp v4): LH/LL on approaching-oversold RSI = MR
        # bounce candidate (sustained downtrend extended = bounce setup), not bearish momentum.
        # HH/HL remains a momentum confirmation signal (unchanged direction).
        ps = tech.get("price_structure")
        _ps_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
        if ps == "hh_hl":
            momentum_score += 7
            sources.add("Technical")
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Bullish Price Structure — Higher Highs & Higher Lows",
                    "body": "Recent swing highs and lows are both ascending — the classic definition of an uptrend. Bias remains long until structure breaks.",
                    "sentiment": "pos",
                    "meta": "HH + HL pattern (20-bar)",
                }
            )
        elif ps == "lh_ll":
            sources.add("Technical")
            if _ps_rsi is not None and _ps_rsi < 45:
                # Downtrend + approaching oversold = MR bounce setup (v4 alpha finding)
                # LH/LL signals sustained weakness that creates a mean-reversion opportunity.
                score += 7
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Bearish Price Structure (LH/LL) — Extended Downtrend = MR Setup",
                        "body": (
                            f"Price structure shows Lower Highs & Lower Lows — sustained downtrend — "
                            f"with RSI {_ps_rsi:.1f} approaching oversold. Extended LH/LL structures "
                            "resolve with mean-reversion bounces when selling exhausts. "
                            "Both the structure and RSI confirm the setup."
                        ),
                        "sentiment": "pos",
                        "meta": f"LH + LL | RSI {_ps_rsi:.1f}",
                    }
                )
            else:
                # Trending down without oversold confirmation = momentum signal (unchanged)
                momentum_score -= 7
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Bearish Price Structure — Lower Highs & Lower Lows",
                        "body": "Recent swing highs and lows are both declining — the classic definition of a downtrend. Bias remains short until structure reverses.",
                        "sentiment": "neg",
                        "meta": "LH + LL pattern (20-bar)",
                    }
                )

        # ── Gap Analysis ─────────────────────────────────────────────────────
        gap_pct = tech.get("gap_pct")
        if gap_pct is not None and abs(gap_pct) >= 1.5:
            sources.add("Technical")
            if gap_pct >= 2.5:
                momentum_score += 8
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Bullish Gap Up +{gap_pct:.1f}%",
                        "body": f"Today's open gapped {gap_pct:.1f}% above yesterday's close. Gaps of this size reflect strong institutional conviction — unfilled gaps above prior resistance are particularly bullish.",
                        "sentiment": "pos",
                        "meta": f"Gap: +{gap_pct:.1f}%",
                    }
                )
            elif gap_pct <= -2.5:
                # −8 penalty SKIPPED in MR-dip context (gate-audit 2026-07-15):
                # cohort +15.5pp vs baseline (N=23) — a large gap down INTO an
                # oversold dip is capitulation (overnight seller exhaustion), the
                # strongest MR setup. Penalty retained outside dip context.
                _gap_mr_dip = (tech.get("bb_pct_b") is not None and float(tech["bb_pct_b"]) < 0.22) or (
                    tech.get("ibs") is not None and float(tech["ibs"]) < 0.15
                )
                if not _gap_mr_dip:
                    momentum_score -= 8
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Bearish Gap Down {gap_pct:.1f}%",
                        "body": (
                            f"Open gapped {abs(gap_pct):.1f}% down into an oversold dip — capitulation/"
                            "seller exhaustion; penalty skipped (live +15.5pp WR cohort, N=23)."
                            if _gap_mr_dip
                            else f"Today's open gapped {abs(gap_pct):.1f}% below yesterday's close. Downside gaps reflect urgent selling — institutional distribution overnight."
                        ),
                        "sentiment": "pos" if _gap_mr_dip else "neg",
                        "meta": f"Gap: {gap_pct:.1f}% mr_dip={_gap_mr_dip}",
                    }
                )
            elif 1.5 <= gap_pct < 2.5:
                momentum_score += 4
            elif -2.5 < gap_pct <= -1.5:
                _gap_mr_dip2 = (tech.get("bb_pct_b") is not None and float(tech["bb_pct_b"]) < 0.22) or (
                    tech.get("ibs") is not None and float(tech["ibs"]) < 0.15
                )
                if not _gap_mr_dip2:
                    momentum_score -= 4

        # ── Relative Volume (RVOL) — direction-aware with multiplier system ─────
        # RVOL > 3.0 = major catalyst (boost all signals); < 0.5 = no participation (dampen).
        # Direction-aware: high vol on up day = accumulation; on down day = distribution.
        # Stealth accumulation: down day + RVOL > 2.0 + oversold = smart money buying.
        rvol = tech.get("rvol")
        change = tech.get("change", 0) or 0
        if rvol is not None:
            sources.add("Technical")
            if rvol < 0.5:
                # No participation — no institutional conviction on either side; dampen momentum
                momentum_score = momentum_score * 0.5
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Volume Drought — No Participation ({rvol:.2f}×)",
                        "body": (
                            f"Today's volume is only {rvol:.2f}× the 20-day average. "
                            "Institutional players are absent — any price move is likely a low-conviction drift. "
                            "Momentum signals are unreliable without volume confirmation."
                        ),
                        "sentiment": "neu",
                        "meta": f"RVOL = {rvol:.2f}× (< 0.5 = no participation)",
                    }
                )
            elif rvol >= 3.0:
                # Major catalyst — institutional conviction in the current direction
                if change >= 0:
                    momentum_score += 10
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"Volume Surge — Major Catalyst ({rvol:.1f}×)",
                            "body": (
                                f"Volume at {rvol:.1f}× the 20-day average — a major catalyst event. "
                                "Institutional participation is confirmed. High-volume breakouts and trend "
                                "signals carry significantly higher follow-through probability."
                            ),
                            "sentiment": "pos",
                            "meta": f"RVOL = {rvol:.1f}× (≥ 3.0 = catalyst)",
                        }
                    )
                else:
                    momentum_score -= 10
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"Volume Surge on Sell-Off ({rvol:.1f}×) — Capitulation Risk",
                            "body": (
                                f"Volume at {rvol:.1f}× average on a down day. "
                                "Either panic selling or institutional distribution — either way, "
                                "the selling pressure is institutional-grade."
                            ),
                            "sentiment": "neg",
                            "meta": f"RVOL = {rvol:.1f}× (≥ 3.0 on down day)",
                        }
                    )
            elif rvol >= 2.0:
                # Elevated institutional activity — direction-aware
                if change >= 0:
                    momentum_score += 5
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"Elevated Volume on Up Day ({rvol:.1f}×)",
                            "body": f"Today's volume is {rvol:.1f}× the 20-day average on a positive price day — institutional accumulation.",
                            "sentiment": "pos",
                            "meta": f"RVOL = {rvol:.1f}×",
                        }
                    )
                else:
                    # Oversold + high volume on down day = stealth institutional accumulation
                    is_oversold_rvol = rsi is not None and rsi < 40
                    if is_oversold_rvol:
                        mean_rev_score += 10
                        rationale.append(
                            {
                                "src": "Technical",
                                "head": f"Stealth Accumulation — Down Day + High Volume + Oversold ({rvol:.1f}×)",
                                "body": (
                                    f"Volume is {rvol:.1f}× average on a red day while RSI is oversold ({rsi:.0f}). "
                                    "Paradox: high volume on a sell-off in an oversold stock often means institutional "
                                    "buyers absorbing retail panic. This is a strong mean-reversion buy setup."
                                ),
                                "sentiment": "pos",
                                "meta": f"RVOL {rvol:.1f}× | RSI {rsi:.0f} | Down day",
                            }
                        )
                    else:
                        momentum_score -= 5
                        rationale.append(
                            {
                                "src": "Technical",
                                "head": f"Elevated Volume on Down Day ({rvol:.1f}×)",
                                "body": f"Today's volume is {rvol:.1f}× the 20-day average on a negative price day — institutional distribution.",
                                "sentiment": "neg",
                                "meta": f"RVOL = {rvol:.1f}×",
                            }
                        )

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
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Volatility Coiling — ADR% at 6-Month Low",
                    "body": f"Average daily range compressed to {adr:.2f}% vs 6-month high of {adr_hi:.2f}%. Volatility compression historically precedes large directional moves. Watch for a Donchian or Bollinger breakout.",
                    "sentiment": "neu",
                    "meta": f"ADR = {adr:.2f}% (6M high: {adr_hi:.2f}%)",
                }
            )

        # ── ATR Percentile Rank — Volatility Regime ──────────────────────────
        # Backtest-validated (alpha decomp v4): ATR_REG was the strongest new family
        # (ΔSharpe −0.07 when removed). Low ATR rank = volatility coiling = mean-
        # reverting environment where MR signals fire with higher reliability.
        # Average |correlation| with all other families = 0.08 (near-orthogonal).
        _atr_pct_rank = tech.get("atr_pct_rank")
        if _atr_pct_rank is not None:
            sources.add("Technical")
            if _atr_pct_rank < 10:
                # Volatility at historical 10th percentile — maximum coil → MR premium
                score += 6
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Volatility at 10th Percentile — MR-Optimal Environment",
                        "body": (
                            f"ATR is at the {_atr_pct_rank:.0f}th percentile of its 1-year range. "
                            "Extreme volatility compression creates a mean-reverting environment — "
                            "price moves are limited and reversals are faster and more reliable."
                        ),
                        "sentiment": "pos",
                        "meta": f"ATR pct rank = {_atr_pct_rank:.0f}th",
                    }
                )
            elif _atr_pct_rank < 20:
                # Low volatility — mild MR premium
                score += 3
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Low Volatility Regime — {_atr_pct_rank:.0f}th Percentile",
                        "body": f"ATR at the {_atr_pct_rank:.0f}th percentile. Quiet tape favours mean-reversion over momentum.",
                        "sentiment": "pos",
                        "meta": f"ATR pct rank = {_atr_pct_rank:.0f}th",
                    }
                )
            elif _atr_pct_rank > 90:
                # Expanding volatility — momentum dominant, MR less reliable
                score -= 5
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Volatility Expanding — {_atr_pct_rank:.0f}th Percentile",
                        "body": f"ATR at the {_atr_pct_rank:.0f}th percentile. High and expanding volatility favours momentum — mean-reversion signals are less reliable and stops are frequently hit.",
                        "sentiment": "neg",
                        "meta": f"ATR pct rank = {_atr_pct_rank:.0f}th",
                    }
                )

        # ── Supertrend(7, 3) ─────────────────────────────────────────────────
        st_dir = tech.get("supertrend_dir", 0) or 0
        st_dir_prev = tech.get("supertrend_dir_prev", 0) or 0
        st_val = tech.get("supertrend_val")
        if st_dir != 0:
            sources.add("Technical")
            flip_to_bull = st_dir == 1 and st_dir_prev == -1
            flip_to_bear = st_dir == -1 and st_dir_prev == 1
            val_str = f" ${st_val:.2f}" if st_val else ""
            if flip_to_bull:
                # Routed into momentum_score so Supertrend competes within the
                # momentum family cap (±26) alongside ROC, Donchian, streak, gap.
                momentum_score += 14
                dominant = "macd"
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Supertrend Bullish Flip ↑",
                        "body": (
                            f"Supertrend(7,3) just flipped from bearish to bullish. "
                            f"The ATR-based trailing stop{val_str} now acts as dynamic support. "
                            "A fresh Supertrend flip is one of the cleanest momentum-reversal signals."
                        ),
                        "sentiment": "pos",
                        "meta": f"Supertrend flipped BULLISH{val_str}",
                    }
                )
            elif flip_to_bear:
                momentum_score -= 14
                dominant = "macd"
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Supertrend Bearish Flip ↓",
                        "body": (
                            f"Supertrend(7,3) just flipped from bullish to bearish. "
                            f"The trailing stop{val_str} now acts as overhead resistance. "
                            "High-probability reversal with ATR-confirmed downside momentum."
                        ),
                        "sentiment": "neg",
                        "meta": f"Supertrend flipped BEARISH{val_str}",
                    }
                )
            elif st_dir == 1:
                momentum_score += 6
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Supertrend Bullish — ATR Support{val_str}",
                        "body": (
                            f"Supertrend(7,3) is in bullish mode. Price is above its ATR-based "
                            f"trailing stop{val_str} — the trend is intact and stop is rising."
                        ),
                        "sentiment": "pos",
                        "meta": f"ST bullish{val_str}",
                    }
                )
            elif st_dir == -1:
                momentum_score -= 6
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"Supertrend Bearish — ATR Resistance{val_str}",
                        "body": (
                            f"Supertrend(7,3) is in bearish mode. Price is below its ATR-based "
                            f"trailing stop{val_str} — overhead resistance prevents sustained recoveries."
                        ),
                        "sentiment": "neg",
                        "meta": f"ST bearish{val_str}",
                    }
                )

        # ── §59/§60/§61/§63 Statistical gates ────────────────────────────────
        from services.gates.statistical import apply_statistical_gates as _stat_gates_fn

        score, _stat_cards, _stat_srcs = _stat_gates_fn(score, tech, sector_rs, market_ctx, df, _is_lev_etf)
        rationale.extend(_stat_cards)
        sources.update(_stat_srcs)

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
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"FDI {fdi:.2f} — Trending Market (Trust Breakouts)",
                        "body": (
                            f"Fractal Dimension Index of {fdi:.2f} is well below 1.5 — price is "
                            "moving in a linear, directional fashion. Donchian and Bollinger breakout "
                            "signals are more reliable in this low-fractal regime."
                        ),
                        "sentiment": "pos" if score > 0 else "neg",
                        "meta": f"FDI = {fdi:.2f} (<1.25 = trending)",
                    }
                )
            elif fdi > 1.45:
                # High fractal dimension — choppy; breakouts are traps
                if abs(score) > 15:
                    score *= 0.88
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"FDI {fdi:.2f} — Choppy Market (Fade Breakouts)",
                        "body": (
                            f"Fractal Dimension Index of {fdi:.2f} indicates fractal, "
                            "non-directional price action. Breakout signals are more likely to fail — "
                            "mean-reversion setups and oscillator signals are preferred."
                        ),
                        "sentiment": "neu",
                        "meta": f"FDI = {fdi:.2f} (>1.45 = choppy)",
                    }
                )

        # ── VIX9D / MOVE / STLFSI4 macro confidence adjustments ──────────────
        # These are applied inside _assemble_signal after the base confidence is
        # computed, so they are not overwritten by the assembler's _score_to_action.
        _macro_now = (market_ctx or {}).get("macro") or {}

        # ── Consumer Sentiment Sector Penalty (UMCSENT) ───────────────────────
        _umcsent = _macro_now.get("umcsent")
        _sector_etf = (sector_rs or {}).get("sector_etf", "")
        _consumer_sectors = {"XLY", "XLP", "XLC"}
        if _umcsent is not None and _umcsent < 60 and action == "BUY" and _sector_etf in _consumer_sectors:
            score -= 3
            sources.add("Macro")
            rationale.append(
                {
                    "src": "Macro",
                    "head": f"Consumer Distress Headwind (UMCSENT {_umcsent:.1f})",
                    "body": (
                        f"U. Michigan Consumer Sentiment at {_umcsent:.1f} — historically distressed "
                        f"(avg ~85). {_sector_etf} sector stocks face direct demand headwind when "
                        "household confidence is this weak. XLY/XLC/XLP names are first to reprice."
                    ),
                    "sentiment": "neg",
                    "meta": f"UMCSENT={_umcsent:.1f} | sector={_sector_etf}",
                }
            )

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
            int_sectors = {"XLK", "XLV", "XLY", "XLC"}  # multinationals — hurt by strong $
            dom_sectors = {"XLU", "XLF", "XLRE"}  # domestic — less affected
            comm_sectors = {"XLB", "XLE"}  # commodities — hurt by strong $
            if dxy_1m > 2.5:  # strengthening dollar
                if sector_etf in int_sectors or sector_etf in comm_sectors:
                    score -= 5
                    rationale.append(
                        {
                            "src": "Macro",
                            "head": f"Strong Dollar Headwind (+{dxy_1m:.1f}% DXY)",
                            "body": f"The US Dollar Index rose {dxy_1m:.1f}% over the past month. A stronger dollar reduces overseas revenue and compresses commodity prices — headwind for this sector.",
                            "sentiment": "neg",
                            "meta": f"DXY 1M = +{dxy_1m:.1f}%",
                        }
                    )
            elif dxy_1m < -2.5:  # weakening dollar
                if sector_etf in int_sectors or sector_etf in comm_sectors:
                    score += 5
                    rationale.append(
                        {
                            "src": "Macro",
                            "head": f"Weak Dollar Tailwind ({dxy_1m:.1f}% DXY)",
                            "body": f"The US Dollar Index fell {abs(dxy_1m):.1f}% over the past month. A weaker dollar boosts overseas earnings when translated back to USD — tailwind for this sector.",
                            "sentiment": "pos",
                            "meta": f"DXY 1M = {dxy_1m:.1f}%",
                        }
                    )

        # ── NAAIM Exposure Index (from market context, key="aaii") ───────────
        aaii = (market_ctx or {}).get("aaii")
        if aaii and aaii.get("signal") != "neutral" and aaii.get("score"):
            a_score = aaii["score"]
            exposure = aaii.get("exposure", 50)
            pct_rank = aaii.get("pct_rank")
            rank_str = f" | 52w pct rank: {pct_rank:.0f}%" if pct_rank is not None else ""
            score += a_score
            sources.add("Market Sentiment")
            if a_score >= 8:
                rationale.append(
                    {
                        "src": "Market Sentiment",
                        "head": f"NAAIM: Managers Extremely Defensive ({exposure:.0f}% Exposed)",
                        "body": (
                            f"Active managers have only {exposure:.0f}% equity exposure — well below average. "
                            "When professionals are this defensive, mean-reversion rallies tend to be sharp as they scramble to cover underexposure."
                        ),
                        "sentiment": "pos",
                        "meta": f"NAAIM = {exposure:.1f}%{rank_str}",
                    }
                )
            elif a_score >= 4:
                rationale.append(
                    {
                        "src": "Market Sentiment",
                        "head": f"NAAIM: Below-Average Equity Exposure ({exposure:.0f}%)",
                        "body": f"Active managers are {exposure:.0f}% exposed to equities — below the historical average (~65%). Defensive positioning leaves room for a buy-in rally.",
                        "sentiment": "pos",
                        "meta": f"NAAIM = {exposure:.1f}%{rank_str}",
                    }
                )
            elif a_score <= -8:
                rationale.append(
                    {
                        "src": "Market Sentiment",
                        "head": f"NAAIM: Managers Fully Invested ({exposure:.0f}% Exposed)",
                        "body": (
                            f"Active managers are {exposure:.0f}% exposed to equities — near maximum. "
                            "When professionals are this fully invested, there is limited incremental buying power left to drive prices higher."
                        ),
                        "sentiment": "neg",
                        "meta": f"NAAIM = {exposure:.1f}%{rank_str}",
                    }
                )
            elif a_score <= -4:
                rationale.append(
                    {
                        "src": "Market Sentiment",
                        "head": f"NAAIM: Elevated Equity Positioning ({exposure:.0f}%)",
                        "body": f"Active managers are {exposure:.0f}% exposed — above-average positioning. Crowded long positioning reduces the marginal buyer pool.",
                        "sentiment": "neg",
                        "meta": f"NAAIM = {exposure:.1f}%{rank_str}",
                    }
                )

        # ── COT (Commitment of Traders) ──────────────────────────────────────
        cot = (market_ctx or {}).get("cot")
        if cot and cot.get("signal") != "neutral" and cot.get("score"):
            c_score = cot["score"]
            net_pct = cot["net_pct"]
            score += c_score
            sources.add("Market Sentiment")
            if c_score >= 8:
                rationale.append(
                    {
                        "src": "Market Sentiment",
                        "head": f"COT: Leveraged Funds Extremely Short S&P ({net_pct:+.0f}%)",
                        "body": f"CFTC COT report shows leveraged funds are {abs(net_pct):.0f}% net short S&P 500 futures. Historically, when fast money is this short, the market bounces sharply — a classic short-squeeze setup.",
                        "sentiment": "pos",
                        "meta": f"COT net: {net_pct:+.0f}%",
                    }
                )
            elif c_score >= 4:
                rationale.append(
                    {
                        "src": "Market Sentiment",
                        "head": f"COT: Leveraged Funds Net Short S&P ({net_pct:+.0f}%)",
                        "body": "CFTC COT shows leveraged funds leaning short on S&P 500 futures. Mild contrarian tailwind.",
                        "sentiment": "pos",
                        "meta": f"COT net: {net_pct:+.0f}%",
                    }
                )
            elif c_score <= -8:
                rationale.append(
                    {
                        "src": "Market Sentiment",
                        "head": f"COT: Leveraged Funds Extremely Long S&P ({net_pct:+.0f}%)",
                        "body": f"CFTC COT shows leveraged funds {net_pct:.0f}% net long S&P 500 futures. Crowded long positioning often precedes reversals.",
                        "sentiment": "neg",
                        "meta": f"COT net: {net_pct:+.0f}%",
                    }
                )
            elif c_score <= -4:
                rationale.append(
                    {
                        "src": "Market Sentiment",
                        "head": f"COT: Leveraged Funds Net Long S&P ({net_pct:+.0f}%)",
                        "body": "Leveraged funds are net long S&P futures — mild contrarian warning signal.",
                        "sentiment": "neg",
                        "meta": f"COT net: {net_pct:+.0f}%",
                    }
                )

        # §50/§74/§76/§51 quality screens (see gates/fundamentals.py)
        from services.gates.fundamentals import apply_quality_screens as _qs_fn

        score, _qs_cards, _qs_srcs = _qs_fn(score, info, fundamentals, _is_lev_etf, action)
        rationale.extend(_qs_cards)
        sources.update(_qs_srcs)

        # ── Revenue Growth Acceleration ──────────────────────────────────────
        rev_acc = fundamentals.get("rev_accelerating")
        g1 = fundamentals.get("rev_growth_q1")
        g2 = fundamentals.get("rev_growth_q2")
        if rev_acc is not None and g1 is not None and g2 is not None:
            sources.add("Fundamentals")
            if rev_acc and g1 > 5:
                score += 6
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"Revenue Growth Accelerating (+{g1:.1f}% QoQ)",
                        "body": f"Quarterly revenue growth accelerated from +{g2:.1f}% to +{g1:.1f}% QoQ. Acceleration is the CAN SLIM key metric — expanding revenues at an increasing rate signal a business in breakout mode.",
                        "sentiment": "pos",
                        "meta": f"Rev growth: {g2:.1f}% → {g1:.1f}% QoQ",
                    }
                )
            elif not rev_acc and g1 < -2:
                score -= 5
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"Revenue Growth Decelerating ({g1:.1f}% QoQ)",
                        "body": f"Revenue growth slowed from {g2:.1f}% to {g1:.1f}% QoQ. Decelerating growth often leads to multiple compression as analysts lower estimates.",
                        "sentiment": "neg",
                        "meta": f"Rev growth: {g2:.1f}% → {g1:.1f}% QoQ",
                    }
                )

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
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": "Earnings Torpedo — 3-Year Revenue Acceleration",
                        "body": (
                            f"Annual revenue growth has accelerated for 3 consecutive years: {_g_str}. "
                            "This 'Earnings Torpedo' pattern (Driehaus/O'Neil) precedes institutional "
                            "accumulation in 68% of cases. Expanding revenues at an increasing rate "
                            "signal a business entering a breakout phase."
                        ),
                        "sentiment": "pos",
                        "meta": f"annual_rev_torpedo=True growth={_g_str}",
                    }
                )
        except Exception:
            log.warning("annual revenue acceleration fetch failed for %s", ticker, exc_info=True)

        # ── ROE Trend ────────────────────────────────────────────────────────
        roe_improving = fundamentals.get("roe_improving")
        roe_now = fundamentals.get("roe_now")
        roe_prev = fundamentals.get("roe_prev")
        if roe_improving is not None and roe_now is not None:
            sources.add("Fundamentals")
            if roe_improving and roe_now > 15:
                score += 5
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"ROE Improving — {roe_now:.1f}%",
                        "body": f"Return on equity rose from {roe_prev:.1f}% to {roe_now:.1f}%. Improving ROE above 15% signals a company compounding capital at a healthy rate.",
                        "sentiment": "pos",
                        "meta": f"ROE: {roe_prev:.1f}% → {roe_now:.1f}%",
                    }
                )
            elif not roe_improving and roe_now < roe_prev:
                delta = roe_prev - roe_now
                if delta > 5:
                    score -= 4
                    rationale.append(
                        {
                            "src": "Fundamentals",
                            "head": f"ROE Declining — {roe_now:.1f}%",
                            "body": f"Return on equity fell {delta:.1f}pp from {roe_prev:.1f}% to {roe_now:.1f}%. Declining ROE often precedes earnings disappointments.",
                            "sentiment": "neg",
                            "meta": f"ROE: {roe_prev:.1f}% → {roe_now:.1f}%",
                        }
                    )

        # ── ROE + Revenue/Earnings Growth (yfinance free fields) ─────────────
        # Supplement the Piotroski F-Score with real-time quality/growth metrics.
        # info["roe_yf"] = returnOnEquity (e.g. 1.41 = 141%); already fetched.
        roe_yf = info.get("roe_yf")
        rev_grow = info.get("revenue_growth")  # YoY e.g. 0.166 = 16.6%
        earn_grow = info.get("earnings_growth")  # YoY
        if roe_yf is not None and not _is_lev_etf:
            _roe_pct = roe_yf * 100
            if _roe_pct >= 40:
                score += 5
                sources.add("Fundamentals")
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"Exceptional ROE — {_roe_pct:.0f}%",
                        "body": (
                            f"Return on equity of {_roe_pct:.0f}% — exceptional compounding machine. "
                            "Companies sustaining ROE >40% typically have durable moats (pricing power, "
                            "network effects, or capital-light models). Buffett threshold: >20%."
                        ),
                        "sentiment": "pos",
                        "meta": f"ROE={_roe_pct:.0f}%",
                    }
                )
            elif _roe_pct >= 20:
                score += 3
                sources.add("Fundamentals")
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"High ROE — {_roe_pct:.0f}%",
                        "body": f"Return on equity of {_roe_pct:.0f}% — above the 20% quality threshold. Efficient capital allocation.",
                        "sentiment": "pos",
                        "meta": f"ROE={_roe_pct:.0f}%",
                    }
                )
            elif _roe_pct < 0:
                score -= 3
                sources.add("Fundamentals")
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"Negative ROE — {_roe_pct:.0f}%",
                        "body": f"Return on equity is negative ({_roe_pct:.0f}%) — the company is destroying shareholder value.",
                        "sentiment": "neg",
                        "meta": f"ROE={_roe_pct:.0f}%",
                    }
                )

        if rev_grow is not None and earn_grow is not None and not _is_lev_etf:
            _rev_pct = rev_grow * 100
            _earn_pct = earn_grow * 100
            if _rev_pct >= 20 and _earn_pct >= 20:
                score += 4
                sources.add("Fundamentals")
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"Dual Growth Acceleration — Rev +{_rev_pct:.0f}% / EPS +{_earn_pct:.0f}% YoY",
                        "body": (
                            f"Revenue growing {_rev_pct:.0f}% and earnings growing {_earn_pct:.0f}% year-over-year. "
                            "Dual acceleration is a hallmark of companies in rapid scaling phases — "
                            "these are the setups institutional growth funds actively accumulate."
                        ),
                        "sentiment": "pos",
                        "meta": f"rev_yoy={_rev_pct:.0f}% | earn_yoy={_earn_pct:.0f}%",
                    }
                )
            elif _rev_pct < 0 or _earn_pct < 0:
                _worst = min(_rev_pct, _earn_pct)
                score -= 3
                sources.add("Fundamentals")
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"Revenue/Earnings Contraction (Rev {_rev_pct:+.0f}% / EPS {_earn_pct:+.0f}%)",
                        "body": (
                            f"At least one growth line is negative YoY — revenue {_rev_pct:+.0f}%, "
                            f"earnings {_earn_pct:+.0f}%. Contracting businesses face multiple compression "
                            "as growth investors exit."
                        ),
                        "sentiment": "neg",
                        "meta": f"rev_yoy={_rev_pct:.0f}% | earn_yoy={_earn_pct:.0f}%",
                    }
                )

        # ── 12-1 Month Momentum Factor ────────────────────────────────────────
        # Cross-sectional momentum: 6-month return minus 3-month return (from
        # Finnhub basic_financials, appended to analyst_recs dict in news.py).
        # Approximates the academic 12-1 month factor without extra API cost.
        _mom_factor = (analyst_recs or {}).get("momentum_factor")
        _r26w = (analyst_recs or {}).get("return_26w")
        if _mom_factor is not None and not _is_lev_etf:
            sources.add("Technicals")
            if _mom_factor >= 20:
                score += 5
                rationale.append(
                    {
                        "src": "Technicals",
                        "head": f"Strong Price Momentum Factor (+{_mom_factor:.1f}%)",
                        "body": (
                            f"6-month return of {_r26w:.1f}% with positive intermediate-term momentum. "
                            "The 12-1 month cross-sectional momentum factor is one of the most replicated "
                            "alpha sources in academic finance — high-momentum stocks persistently outperform."
                        ),
                        "sentiment": "pos",
                        "meta": f"momentum_factor={_mom_factor:.1f}% | r26w={_r26w:.1f}%",
                    }
                )
            elif _mom_factor >= 8:
                score += 2
                rationale.append(
                    {
                        "src": "Technicals",
                        "head": f"Positive Price Momentum (+{_mom_factor:.1f}%)",
                        "body": f"Intermediate-term momentum positive at {_mom_factor:.1f}%. Mild continuation signal.",
                        "sentiment": "pos",
                        "meta": f"momentum_factor={_mom_factor:.1f}%",
                    }
                )
            elif _mom_factor <= -20:
                score -= 5
                rationale.append(
                    {
                        "src": "Technicals",
                        "head": f"Strong Negative Momentum ({_mom_factor:.1f}%)",
                        "body": (
                            f"6-month return of {_r26w:.1f}% with large negative momentum factor. "
                            "Low-momentum stocks systematically underperform — mean reversion is slow "
                            "and frequently interrupted by further deterioration."
                        ),
                        "sentiment": "neg",
                        "meta": f"momentum_factor={_mom_factor:.1f}% | r26w={_r26w:.1f}%",
                    }
                )
            elif _mom_factor <= -8:
                score -= 2
                rationale.append(
                    {
                        "src": "Technicals",
                        "head": f"Negative Price Momentum ({_mom_factor:.1f}%)",
                        "body": "Intermediate-term momentum negative. Mild downtrend confirmation.",
                        "sentiment": "neg",
                        "meta": f"momentum_factor={_mom_factor:.1f}%",
                    }
                )

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
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"Dividend {_aristo_level} — {_aristo_years} Years of Increases",
                        "body": (
                            f"{ticker} has increased its annual dividend for {_aristo_years} consecutive years. "
                            f"Dividend {_aristo_level}s have structural shareholder return commitments that "
                            "reduce drawdown risk and attract income-focused institutional buyers."
                        ),
                        "sentiment": "pos",
                        "meta": f"div_{_aristo_level.lower()}={_aristo_years}yr +{_pts}pts",
                    }
                )
        except Exception:
            log.warning("polygon dividend data fetch failed for %s", ticker, exc_info=True)
        if div_yield and div_yield > 0 and t10y_rate:
            sources.add("Fundamentals")
            yield_gap = div_yield - t10y_rate
            if yield_gap > 1.0:
                # +6 REMOVED (gate-audit 2026-07-15): cohort −6.2pp vs baseline
                # (N=239) — a yield fat vs Treasuries on an oversold stock usually
                # means the PRICE fell (value trap), not that demand is coming.
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"Dividend Yield {div_yield:.1f}% > 10Y Treasury {t10y_rate:.1f}%",
                        "body": f"Stock yields {div_yield:.1f}% — {yield_gap:.1f}pp above the 10-year Treasury. When a blue chip yields more than risk-free bonds, yield-seeking demand increases.",
                        # "neu": +6 score removed 2026-07-15 (cohort -6.2pp) — must not
                        # still count as agreeing evidence for Tier-6/orthogonality below.
                        "sentiment": "neu",
                        "meta": f"Yield gap: +{yield_gap:.1f}pp score_delta=0",
                    }
                )
            elif yield_gap < -2.0:
                score -= 3
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": "Bond Alternative More Attractive",
                        "body": f"10Y Treasury ({t10y_rate:.1f}%) significantly exceeds the stock's {div_yield:.1f}% dividend yield by {abs(yield_gap):.1f}pp. Risk-free alternative is compelling.",
                        "sentiment": "neg",
                        "meta": f"Yield gap: {yield_gap:.1f}pp",
                    }
                )

        # ── §75 EDGAR 8-K Buyback Window ──────────────────────────────────────
        try:
            from services.edgar import has_active_buyback

            if await has_active_buyback(ticker, days=90):
                # +5 REMOVED (gate-audit 2026-07-15): §75 was disabled 2026-05-31
                # (live WR 33.8%, −8.7pp) but only the buyback-YIELD variant was
                # zeroed — this 8-K variant kept scoring. Delivered cohort with the
                # buyback card: −10.1pp (N=58). Leak closed; card informational.
                sources.add("Fundamentals")
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": "Active Share Repurchase Program (§75, info only)",
                        "body": (
                            "Company announced an active share repurchase program within the last 90 days via Form 8-K. "
                            "Shows strong institutional support and capital allocation alignment at oversold levels."
                        ),
                        # "neu": +5 score removed 2026-07-15 (delivered cohort -10.1pp) —
                        # must not still count as agreeing evidence for Tier-6/orthogonality.
                        "sentiment": "neu",
                        "meta": "sec_buyback_8k=True score_delta=0",
                    }
                )
        except Exception as e:
            log.debug("[engine] %s EDGAR 8-K buyback check failed: %s", ticker, e)

        # ── Buyback Yield — DISABLED 2026-05-31 ──────────────────────────────
        # Live-data audit (Inv 3, 546 resolved): signals with active buyback card
        # have WR=33.8% (−8.7pp vs 42.5% baseline). Buybacks signal management
        # confidence but NOT short-term price recovery — a company can be buying
        # back shares while the stock continues to decline. The +2pp boost was
        # producing net-negative signals. Disabled; rationale card still shown
        # for information but confidence/score unchanged.
        bb_yield = fundamentals.get("buyback_yield")
        if bb_yield and bb_yield > 3:
            sources.add("Fundamentals")
            rationale.append(
                {
                    "src": "Fundamentals",
                    "head": f"Active Share Buyback — {bb_yield:.1f}% Yield (info only)",
                    "body": (
                        f"Company returned {bb_yield:.1f}% of market cap to shareholders "
                        "through buybacks. Note: live-data audit shows buyback signals have "
                        "33.8% WR (−8.7pp vs baseline) — buybacks do not predict short-term "
                        "MR bounces. Score unchanged; shown for informational context only."
                    ),
                    "sentiment": "neutral",
                    "meta": f"buyback_yield={bb_yield:.1f}% score_delta=0 §75 disabled 2026-05-31",
                }
            )
        # Share dilution — counterpart to buyback yield.
        # Yfinance provides impliedSharesOutstanding / floatShares via the info dict.
        # A YoY share count increase >5% means the company is actively diluting holders.
        shares_growth = fundamentals.get("shares_growth_yoy")
        if shares_growth is not None and shares_growth > 5:
            sources.add("Fundamentals")
            score -= 4
            rationale.append(
                {
                    "src": "Fundamentals",
                    "head": f"Share Dilution — Shares Outstanding +{shares_growth:.1f}% YoY",
                    "body": (
                        f"Shares outstanding grew {shares_growth:.1f}% YoY. Active share issuance "
                        "dilutes existing holders: per-share earnings, book value, and dividends all "
                        "shrink even if absolute profits are flat. Counter-signal to buyback yield."
                    ),
                    "sentiment": "neg",
                    "meta": f"Shares outstanding growth: +{shares_growth:.1f}% YoY",
                }
            )

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
                _mda_form = _mda.get("form_type", "10-Q")
                _mda_reason = _mda.get("reason", "")
                rationale.append(
                    {
                        "src": "SEC EDGAR",
                        "head": (
                            f"{_mda_form} Language {'Improvement' if _mda_score > 0 else 'Deterioration'} "
                            f"({_mda_score:+.1f}pts)"
                        ),
                        "body": (
                            f"Quarter-over-quarter MD&A text analysis: {_mda_reason}. "
                            f"Management language in SEC filings is a leading indicator — "
                            f"silently added risk terms or removed bullish guidance language "
                            f"precede reported fundamental deterioration by 1–2 quarters."
                        ),
                        "sentiment": "pos" if _mda_score > 0 else "neg",
                        "meta": f"mda_delta={_mda_score:+.1f} form={_mda_form}",
                    }
                )
        except Exception:
            log.warning("MDA delta fetch failed for %s", ticker, exc_info=True)

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
                bdi_str = (
                    f"BDI {bdi_val.get('value', 'N/A')} ({bdi_val.get('chg_20d', 0):+.0f}% 20d)"
                    if bdi_val
                    else "BDI N/A"
                )
                rationale.append(
                    {
                        "src": "Fundamentals",
                        "head": f"Supply Chain Signal {sc_score:+.0f}pts — {sc_dir.capitalize()} for {ticker}",
                        "body": (
                            f"Alternative supply chain data ({bdi_str}) indicates {sc_dir} conditions "
                            f"for this sector. Shipping/freight trends are leading indicators of revenue "
                            f"surprises for logistics, commodities, and retail tickers."
                        ),
                        "sentiment": "pos" if sc_score > 0 else "neg",
                        "meta": f"supply_chain_score={sc_score:+.1f}",
                    }
                )
        except Exception:
            log.warning("supply chain score lookup failed for %s", ticker, exc_info=True)

        # ── Corporate Events (Wall Street Horizon) ───────────────────────────
        try:
            from services.corporate_events import get_event_score, get_exdiv_blackout

            # Ex-dividend date hard blackout — price mechanically drops by dividend amount
            # on ex-date; Supertrend/MA signals are invalidated by this predictable drop.
            _is_exdiv, _exdiv_label = get_exdiv_blackout(ticker, (market_ctx or {}).get("corporate_events"))
            if _is_exdiv:
                _force_hold = True
                sources.add("Risk Gate")
                rationale.append(
                    {
                        "src": "Risk Gate",
                        "head": f"Ex-Dividend Date Blackout — {_exdiv_label}",
                        "body": (
                            "Today is the ex-dividend date. The stock price will mechanically drop "
                            "by the dividend amount at open. Supertrend, moving averages, and breakout "
                            "signals are invalidated by this guaranteed drop. Signal blocked for today."
                        ),
                        "sentiment": "neg",
                        "meta": f"ex_div_blackout=True label={_exdiv_label}",
                    }
                )
            # Ex-div lookahead: block BUY when ex-div falls within the MR hold window (≤7 days).
            # A trade entered today holding 5-10 days would hit the mechanical ex-div gap-down.
            # Replaces the per-ticker Polygon 14-day check that ran in get_massive_advanced_signals.
            # Uses corporate_events market_ctx (requires MASSIVE_API_KEY; no-ops without it).
            if not _is_exdiv and action == "BUY":
                _ce_events = ((market_ctx or {}).get("corporate_events") or {}).get("by_ticker") or {}
                for _ev in _ce_events.get(ticker, []):
                    if _ev.get("type") == "ExDividendDate" and 0 < _ev.get("days_away", 99) <= 7:
                        _exdiv_ahead = _ev.get("date", "soon")
                        _exdiv_days = _ev["days_away"]
                        _force_hold = True
                        sources.add("Risk Gate")
                        rationale.append(
                            {
                                "src": "Risk Gate",
                                "head": f"Ex-Dividend Gate — BUY Blocked ({_exdiv_ahead}, {_exdiv_days}d away)",
                                "body": (
                                    f"Ex-dividend date is {_exdiv_ahead} ({_exdiv_days} day{'s' if _exdiv_days != 1 else ''} away). "
                                    f"A hold through ex-date incurs a mechanical price drop equal to the dividend, "
                                    f"creating an artificial loss that is not a recoverable MR setup."
                                ),
                                "sentiment": "neg",
                                "meta": f"ex_div_ahead={_exdiv_ahead} days_away={_exdiv_days}",
                            }
                        )
                        break
            ev_score, ev_reasons = get_event_score(ticker, (market_ctx or {}).get("corporate_events"))
            if abs(ev_score) >= 2.0:
                sources.add("Fundamentals")
                score += ev_score
                for r in ev_reasons:
                    rationale.append(
                        {
                            "src": "Fundamentals",
                            "head": f"Corporate Event: {r}",
                            "body": (
                                "Upcoming corporate events carry a systematic price impact. "
                                "Investor conferences / analyst days historically produce +1.5–2.5% "
                                "median returns in the 3 days before the event as management "
                                "presents to institutional buy-side."
                            ),
                            "sentiment": "pos" if ev_score > 0 else "neg",
                            "meta": f"event_score={ev_score:+.1f}",
                        }
                    )
        except Exception:
            log.warning("block print detection failed for %s", ticker, exc_info=True)

        # ── ETF Fund Flows ────────────────────────────────────────────────────
        try:
            from services.etf_flows import get_flow_score_for_ticker

            etf_flow_score, etf_flow_reason = get_flow_score_for_ticker(ticker, (market_ctx or {}).get("etf_flows"))
            if abs(etf_flow_score) >= 2.0:
                sources.add("Institutional")
                score += etf_flow_score
                rationale.append(
                    {
                        "src": "Institutional",
                        "head": f"ETF Fund Flow {etf_flow_score:+.1f}pts — {etf_flow_reason}",
                        "body": (
                            "Institutional money flows at the sector ETF level lead individual stock "
                            "prices by 1–3 trading days. Strong inflows into the sector ETF signal "
                            "buy-side rotation into this area of the market."
                        ),
                        "sentiment": "pos" if etf_flow_score > 0 else "neg",
                        "meta": f"etf_flow_score={etf_flow_score:+.1f}",
                    }
                )
        except Exception:
            log.warning("ETF flow scoring failed for %s", ticker, exc_info=True)

        # ── Social Sentiment (StockTwits + Reddit WSB) ───────────────────────
        st_bull_pct = social.get("st_bull_pct")
        wsb_7d = social.get("wsb_mentions_7d", 0)
        wsb_1d = social.get("wsb_mentions_1d", 0)
        if st_bull_pct is not None and social.get("st_total", 0) >= 5:
            sources.add("Social")
            if st_bull_pct >= 90:
                # Contrarian −5 penalty NEUTRALIZED (gate-audit 2026-07-15): on the
                # delivered MR-BUY book the >=90% cohort ran +6.0pp ABOVE baseline
                # (N=138) — at an oversold entry, extreme retail bullishness is
                # confirmation, not euphoria-top. Card kept as informational.
                rationale.append(
                    {
                        "src": "Social",
                        "head": f"StockTwits Extreme Bullishness ({st_bull_pct:.0f}%)",
                        "body": f"{st_bull_pct:.0f}% of StockTwits messages are bullish. At oversold MR entries this cohort has historically OUTPERFORMED (+6pp WR, N=138) — informational only, no score change.",
                        "sentiment": "pos",
                        "meta": f"ST Bull: {st_bull_pct:.0f}% | {social.get('st_total', 0)} messages",
                    }
                )
            elif st_bull_pct >= 75:
                soc_bucket += 4
                rationale.append(
                    {
                        "src": "Social",
                        "head": f"StockTwits Strongly Bullish ({st_bull_pct:.0f}%)",
                        "body": f"{st_bull_pct:.0f}% of StockTwits messages on ${ticker} are bullish. Elevated retail optimism can create near-term upside momentum.",
                        "sentiment": "pos",
                        "meta": f"ST Bull: {st_bull_pct:.0f}% | {social.get('st_total', 0)} messages",
                    }
                )
            elif st_bull_pct <= 10:
                # Extreme retail pessimism = contrarian BUY (capitulation)
                soc_bucket += 5
                rationale.append(
                    {
                        "src": "Social",
                        "head": f"StockTwits Extreme Bearishness ({st_bull_pct:.0f}% bull) — Contrarian Bullish",
                        "body": f"Only {st_bull_pct:.0f}% of StockTwits messages are bullish — near-capitulation retail sentiment. Extreme pessimism often marks near-term bottoms.",
                        "sentiment": "pos",
                        "meta": f"ST Bull: {st_bull_pct:.0f}% | {social.get('st_total', 0)} messages",
                    }
                )
            elif st_bull_pct <= 30:
                soc_bucket += 3
                rationale.append(
                    {
                        "src": "Social",
                        "head": f"StockTwits Bearish ({st_bull_pct:.0f}% bull) — Contrarian",
                        "body": f"Only {st_bull_pct:.0f}% of StockTwits messages are bullish. Retail pessimism is a mild contrarian buy indicator.",
                        "sentiment": "pos",
                        "meta": f"ST Bull: {st_bull_pct:.0f}% | {social.get('st_total', 0)} messages",
                    }
                )
        if wsb_1d >= 10:
            sources.add("Social")
            soc_bucket += 4
            rationale.append(
                {
                    "src": "Social",
                    "head": f"Reddit WSB Mention Surge — {wsb_1d} Posts Today",
                    "body": f"${ticker} mentioned in {wsb_1d} Reddit WSB posts in the past 24h ({wsb_7d} this week). Rising retail attention can drive short-term volume and volatility.",
                    "sentiment": "pos",
                    "meta": f"WSB: {wsb_1d} today | {wsb_7d} this week",
                }
            )

        # ── Tier 6: Signal Clustering Boost ─────────────────────────────────
        # When ≥6 independent source CATEGORIES all agree with the dominant direction,
        # the conviction is significantly higher than the sum of parts.
        # Computed BEFORE orthogonality so the 12% boost applies to the pre-orthogonality
        # base score rather than cascading on top of the orthogonality inflation.
        agree_dir = "pos" if score > 0 else "neg"
        source_cats = {
            "TA": any(r.get("src") == "Technical" for r in rationale if r.get("sentiment") == agree_dir),
            "OPT": any(r.get("src") == "Options" for r in rationale if r.get("sentiment") == agree_dir),
            "INST": any(r.get("src") in ("13F", "Dark Pool") for r in rationale if r.get("sentiment") == agree_dir),
            "INSIDE": any(
                r.get("src") in ("Insider", "SEC EDGAR", "Congress")
                for r in rationale
                if r.get("sentiment") == agree_dir
            ),
            "AN": any(r.get("src") == "Analyst" for r in rationale if r.get("sentiment") == agree_dir),
            "MACRO": any(r.get("src") == "Macro" for r in rationale if r.get("sentiment") == agree_dir),
            "SENT": any(
                r.get("src") in ("Market Sentiment", "Fear&Greed", "Market Breadth")
                for r in rationale
                if r.get("sentiment") == agree_dir
            ),
            "FUND": any(r.get("src") == "Fundamentals" for r in rationale if r.get("sentiment") == agree_dir),
            "SOCIAL": any(r.get("src") == "Social" for r in rationale if r.get("sentiment") == agree_dir),
            "EARN": any(r.get("src") == "Earnings" for r in rationale if r.get("sentiment") == agree_dir),
        }
        agreeing_cats = sum(source_cats.values())
        # Suppress convergence bonuses in stress regimes: when VIX ≥ 20 OR in a
        # sustained-bear grind (SPY >3% below SMA200 AND -7% over 1mo), inter-factor
        # correlations approach 1.0 — HYG/VIX/breadth/F&G all respond to the same
        # liquidity shock. Counting them as independent confirmation double-counts the
        # same underlying factor and inflates scores precisely when tails are fattest.
        # Threshold lowered 25→20: cross-asset correlations begin rising well before
        # VIX hits 25 (Aug-2024 vol spike was VIX 20–23 with near-1.0 correlations).
        # Conditions re-derived here from market_ctx (not _assemble_signal scope).
        _macro_sr = (market_ctx or {}).get("macro") or {}
        _sma200_ratio_sr = float(_macro_sr.get("sp500_sma200_ratio") or 1.0)
        _spy1m_sr = float(_macro_sr.get("spy_1m_ret") or 0.0)
        _sustained_bear_sr = _sma200_ratio_sr < 0.97 and _spy1m_sr < -7.0
        _stress_regime = (vix is not None and float(vix) >= 20) or _sustained_bear_sr
        if agreeing_cats >= 6 and not _stress_regime:
            # weight_overrides.cluster_boost_pct caps the multiplier (default 0.12 = 12%).
            # When the ticker's historical win rate is below 50%, the boost is halved —
            # source agreement does not compensate for a poor empirical track record.
            _wo = (market_ctx or {}).get("weight_overrides", {})
            _ticker_wrs = ((market_ctx or {}).get("adaptive_weights") or {}).get("ticker_win_rates", {})
            _ticker_wr = _ticker_wrs.get(ticker)
            _cluster_pct = float(_wo.get("cluster_boost_pct", 0.12))
            _wr_penalty = ""
            if _ticker_wr is not None and _ticker_wr < 0.50:
                _cluster_pct = min(_cluster_pct, 0.06)
                _wr_penalty = f" (capped: {ticker} win rate {_ticker_wr * 100:.0f}%)"
            cluster_boost = round(score * _cluster_pct, 1)
            score += cluster_boost
            sources.add("Signal Cluster")
            rationale.append(
                {
                    "src": "Signal Cluster",
                    "head": f"High-Conviction Signal — {agreeing_cats} Independent Categories Agree",
                    "body": (
                        f"{agreeing_cats} independent signal categories all point {'bullish' if agree_dir == 'pos' else 'bearish'}: "
                        f"{', '.join(k for k, v in source_cats.items() if v)}. "
                        f"Cluster boost: {_cluster_pct * 100:.0f}%.{_wr_penalty}"
                    ),
                    "sentiment": agree_dir,
                    "meta": f"{agreeing_cats} categories · boost {_cluster_pct * 100:.0f}%{_wr_penalty}",
                }
            )

        # ── Orthogonality Bonus — independent information sets converging ────────
        # Signals from fundamentally uncorrelated sources (different data pipelines,
        # different filing cadences, different market participants) carry greater
        # statistical weight than a second technical indicator reading the same price.
        # Reward convergence across truly independent sources.
        # Computed AFTER cluster so both rewards don't cascade multiplicatively.
        _agree = "pos" if score > 0 else "neg"
        _indep = {
            "13F": any(r.get("src") == "13F" and r.get("sentiment") == _agree for r in rationale),
            "Insider": any(r.get("src") == "SEC EDGAR" and r.get("sentiment") == _agree for r in rationale),
            "Congress": any(r.get("src") == "Congress" and r.get("sentiment") == _agree for r in rationale),
            "Piotroski": any("Piotroski" in r.get("head", "") and r.get("sentiment") == _agree for r in rationale),
            "Social": any(r.get("src") == "Social" and r.get("sentiment") == _agree for r in rationale),
            "Macro": any(r.get("src") == "Macro" and r.get("sentiment") == _agree for r in rationale),
            "Dark Pool": any(r.get("src") == "Dark Pool" and r.get("sentiment") == _agree for r in rationale),
        }
        _n_indep = sum(_indep.values())
        if _n_indep >= 2 and _stress_regime:
            # VIX ≥ 25: convergence bonuses suppressed — surface it as a rationale card.
            _indep_names_sr = ", ".join(k for k, v in _indep.items() if v)
            rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Stress Regime — Orthogonality Bonus Suppressed (VIX {vix:.0f})",
                    "body": (
                        f"VIX at {vix:.0f} signals a liquidity-stress regime (threshold ≥ 20). Under stress, "
                        f"factors like {_indep_names_sr} are correlated (not orthogonal) — all "
                        "respond to the same liquidity shock. Counting them as independent "
                        "confirmation would double-count risk and inflate the score when tails "
                        "are fattest. Orthogonality and cluster bonuses are suppressed."
                    ),
                    "sentiment": "neg",
                    "meta": f"vix={vix:.0f} ≥ 20 | orthogonality_bonus=0 | cluster_boost=0",
                }
            )
        elif _n_indep >= 2:
            # weight_overrides lets the owner cap these boosts without touching code.
            # Defaults: 3 pts/source, max +18. Both are reduced when ticker win rate < 50%.
            _wo = (market_ctx or {}).get("weight_overrides", {})
            _ticker_wrs = ((market_ctx or {}).get("adaptive_weights") or {}).get("ticker_win_rates", {})
            _ticker_wr = _ticker_wrs.get(ticker)
            _orth_pts = float(_wo.get("orthogonality_pts", 3))
            _orth_max = float(_wo.get("orthogonality_max", 18))
            if _ticker_wr is not None and _ticker_wr < 0.50:
                # Ticker has a poor historical record — halve the orthogonality reward
                _orth_pts = min(_orth_pts, 1.5)
                _orth_max = min(_orth_max, 9)
            _orth_bonus = min(_orth_max, _n_indep * _orth_pts)
            score += _orth_bonus if score > 0 else (-_orth_bonus if score < 0 else 0)
            sources.add("Orthogonalization")
            _indep_names = ", ".join(k for k, v in _indep.items() if v)
            _wr_note = (
                f" (ticker win rate {_ticker_wr * 100:.0f}% — reduced bonus)"
                if (_ticker_wr is not None and _ticker_wr < 0.50)
                else ""
            )
            rationale.append(
                {
                    "src": "Orthogonalization",
                    "head": f"{_n_indep} Independent Sources Agree — Orthogonal Alpha",
                    "body": (
                        f"{_indep_names} all confirm the {'bullish' if _agree == 'pos' else 'bearish'} thesis "
                        "from uncorrelated data pipelines (filings, fundamentals, positioning, macro). "
                        f"Each source uses different information — convergence raises statistical confidence.{_wr_note}"
                    ),
                    "sentiment": _agree,
                    "meta": f"{_n_indep} independent sources: {_indep_names}{_wr_note}",
                }
            )

        # ── Factor Mining Calibration ─────────────────────────────────────────
        # Apply small boosts/penalties from the weekly-mined OOS-Sharpe rankings.
        # Only fires when the current signal's active source set matches a known combo.
        # Capped at ±5 to avoid overriding the substantive indicators.
        fw = (market_ctx or {}).get("factor_weights", {})
        if fw and fw.get("top_factors") and abs(score) > 5:
            active_sources = set(sources)
            fm_adj = 0.0
            fm_note = ""
            for fac in (fw.get("top_factors") or [])[:10]:
                fac_label = fac.get("label", "")
                fac_sources = set(fac_label.split("+"))
                oos_sharpe = fac.get("oos_sharpe") or 0
                oos_wr = fac.get("oos_win_rate") or 0.5
                if not fac_sources.issubset(active_sources):
                    continue
                if oos_sharpe > 1.0 and oos_wr > 0.60:
                    # Strong historically proven combo — small boost
                    adj = min(3.0, oos_sharpe * 1.0)
                    fm_adj += adj
                    fm_note = f"+{adj:.1f} ({fac_label} OOS Sharpe {oos_sharpe:.2f})"
                    break  # one match is enough
                elif oos_sharpe < 0.0 or oos_wr < 0.35:
                    # Historically poor combo — small penalty
                    adj = max(-3.0, oos_sharpe * 0.8)
                    fm_adj += adj
                    fm_note = f"{adj:.1f} ({fac_label} OOS Sharpe {oos_sharpe:.2f})"
                    break
            if abs(fm_adj) >= 1.0:
                fm_adj = max(-5.0, min(5.0, fm_adj))
                score += fm_adj if score > 0 else (-fm_adj if score < 0 else 0)
                sources.add("Backtest")
                rationale.append(
                    {
                        "src": "Backtest",
                        "head": f"Factor Mining Calibration {'+' if fm_adj > 0 else ''}{fm_adj:.1f}",
                        "body": (
                            f"Weekly factor mining found this source combination has a "
                            f"{'strong' if fm_adj > 0 else 'weak'} out-of-sample Sharpe ratio. "
                            f"Score adjusted {'+' if fm_adj > 0 else ''}{fm_adj:.1f}. {fm_note}"
                        ),
                        "sentiment": "pos" if fm_adj > 0 else "neg",
                        "meta": fm_note,
                    }
                )

        # ── Tier 6: Regime-Conditional Weighting ─────────────────────────────
        # Symmetric: penalise counter-trend signals, boost with-trend signals.
        # Bear market: BUY haircut AND SELL boost. Bull market: SELL haircut AND BUY boost.
        sp500_trend = ((market_ctx or {}).get("macro") or {}).get("sp500_trend")
        if sp500_trend == "down":
            if score > 0:  # BUY against the bear trend — less reliable
                score *= 0.82
                rationale.append(
                    {
                        "src": "Macro",
                        "head": "Bear Market Regime — Long Signal Discounted",
                        "body": "S&P 500 is below its 50-day average. Counter-trend long signals carry lower win rates. Confidence reduced.",
                        "sentiment": "neg",
                        "meta": "SPX < 50-DMA regime",
                    }
                )
            elif score < 0:  # SELL with the bear trend — more reliable
                score *= 1.10
        elif sp500_trend == "up":
            if score < 0:  # SELL against the bull trend — less reliable
                score *= 0.90
            elif score > 0:  # BUY with the bull trend — more reliable
                score *= 1.05

        # ── Earnings Estimate Revision Momentum ─────────────────────────────
        target_mean = info.get("target_mean")
        analyst_count = info.get("analyst_count") or 0
        if target_mean and analyst_count >= 3 and price > 0:
            import time as _time_mod

            now_ts = _time_mod.time()
            prev = _analyst_cache_get(ticker) or {}
            prev_mean = prev.get("mean")
            prev_count = prev.get("count", analyst_count)

            _analyst_cache_set(ticker, {"mean": target_mean, "count": analyst_count, "ts": now_ts})
            if prev_mean and prev_mean > 0:
                revision_pct = (target_mean - prev_mean) / prev_mean * 100
                count_grew = analyst_count > prev_count
                if revision_pct > 5 and count_grew:
                    score += 8
                    sources.add("Analyst")
                    rationale.append(
                        {
                            "src": "Analyst",
                            "head": f"Analyst Target Revised Up +{revision_pct:.1f}% — Positive Momentum",
                            "body": (
                                f"Consensus price target upgraded from ${prev_mean:.2f} to ${target_mean:.2f} "
                                f"(+{revision_pct:.1f}%) as analyst coverage expanded to {analyst_count}. "
                                "Rising estimates with growing coverage is a strong leading indicator."
                            ),
                            "sentiment": "pos",
                            "meta": f"Target: ${prev_mean:.2f} → ${target_mean:.2f} | Analysts: {analyst_count}",
                        }
                    )
                elif revision_pct > 5:
                    score += 5
                    sources.add("Analyst")
                    rationale.append(
                        {
                            "src": "Analyst",
                            "head": f"Analyst Target Revised Up +{revision_pct:.1f}%",
                            "body": f"Consensus price target raised from ${prev_mean:.2f} to ${target_mean:.2f}. Positive estimate revision momentum tends to persist.",
                            "sentiment": "pos",
                            "meta": f"Target: ${prev_mean:.2f} → ${target_mean:.2f}",
                        }
                    )
                elif revision_pct < -5:
                    score -= 6
                    sources.add("Analyst")
                    rationale.append(
                        {
                            "src": "Analyst",
                            "head": f"Analyst Target Revised Down {revision_pct:.1f}%",
                            "body": (
                                f"Consensus price target cut from ${prev_mean:.2f} to ${target_mean:.2f} "
                                f"({revision_pct:.1f}%). Negative estimate revisions tend to cluster — where there's one cut, more often follow."
                            ),
                            "sentiment": "neg",
                            "meta": f"Target: ${prev_mean:.2f} → ${target_mean:.2f} | Analysts: {analyst_count}",
                        }
                    )

        # ── Google Trends ────────────────────────────────────────────────────
        trends = trends or {}
        gt_score = trends.get("score", 0)
        gt_chg = trends.get("change_pct")
        gt_recent = trends.get("recent")
        if gt_score != 0 and gt_chg is not None:
            soc_bucket += gt_score
            sources.add("Social")
            if gt_score > 0:
                rationale.append(
                    {
                        "src": "Social",
                        "head": f"Google Search Surge +{gt_chg:.0f}% — Retail FOMO Building",
                        "body": (
                            f"Search volume for '{ticker} stock' jumped {gt_chg:.0f}% vs prior 4-week average "
                            f"(index: {gt_recent:.0f}/100). Rising retail attention typically precedes "
                            "near-term price momentum as new buyers enter the market."
                        ),
                        "sentiment": "pos",
                        "meta": f"Trends: +{gt_chg:.0f}% vs 4w avg | Score: {gt_recent:.0f}/100",
                    }
                )
            elif gt_score < 0:
                rationale.append(
                    {
                        "src": "Social",
                        "head": f"Google Search Collapse {gt_chg:.0f}% — Retail Interest Fading",
                        "body": f"Search interest for '{ticker} stock' dropped {abs(gt_chg):.0f}% vs prior 4 weeks. Fading retail attention reduces the marginal buyer pool.",
                        "sentiment": "neg",
                        "meta": f"Trends: {gt_chg:.0f}% vs 4w avg",
                    }
                )

        # Apply social/retail sentiment bucket cap: StockTwits + WSB + Google Trends
        # all measure retail crowd direction — cap so the bucket contributes once.
        # 0.85 discount: retail sentiment is correlated with news sentiment already scored.
        score += max(-10, min(10, soc_bucket)) * 0.85

        # ── Congressional Trading (Quiverquant) ──────────────────────────────
        congress = congress or {}
        cg_score = congress.get("score", 0)
        cg_buys = congress.get("buys", 0)
        cg_sells = congress.get("sells", 0)
        cg_net = congress.get("net", 0)
        if cg_score != 0:
            score += cg_score
            sources.add("Congress")
            if cg_score > 0:
                recent_reps = ", ".join(b["rep"] for b in congress.get("recent_buys", [])[:2])
                rationale.append(
                    {
                        "src": "Congress",
                        "head": f"Congressional Buying — {cg_buys} Purchase{'s' if cg_buys > 1 else ''} (90d)",
                        "body": (
                            f"{cg_buys} congressional purchase{'s' if cg_buys > 1 else ''} vs {cg_sells} sale{'s' if cg_sells != 1 else ''} in the past 90 days. "
                            + (f"Buyers include: {recent_reps}. " if recent_reps else "")
                            + "Senators and representatives historically outperform the market by 6–12% annually."
                        ),
                        "sentiment": "pos",
                        "meta": f"Congress: {cg_buys} buys, {cg_sells} sells (90d)",
                    }
                )
            elif cg_score < 0:
                rationale.append(
                    {
                        "src": "Congress",
                        "head": f"Congressional Selling — {cg_sells} Sale{'s' if cg_sells > 1 else ''} (90d)",
                        "body": f"{cg_sells} congressional sale{'s' if cg_sells != 1 else ''} vs {cg_buys} purchase{'s' if cg_buys != 1 else ''} in the past 90 days. Net selling by politicians — who often have policy insight — is a caution flag.",
                        "sentiment": "neg",
                        "meta": f"Congress: {cg_buys} buys, {cg_sells} sells (90d)",
                    }
                )

        # ── Sector Rotation Bias ──────────────────────────────────────────────
        rotation = ((market_ctx or {}).get("macro") or {}).get("sector_rotation")
        if rotation and rotation.get("stage") and sector_rs:
            sector_etf = sector_rs.get("sector_etf", "")
            stage = rotation["stage"]
            favoured = rotation.get("favoured", [])
            avoid = rotation.get("avoid", [])
            conf = rotation.get("confidence", 0)
            if sector_etf and conf >= 50:
                sources.add("Macro")
                if sector_etf in favoured:
                    # +6 REMOVED (gate-audit 2026-07-15): delivered cohorts with this
                    # boost ran −22.0pp (XLF, N=54) and −14.5pp (XLI, N=34) vs baseline —
                    # the macro-cycle narrative overrode measured sector performance.
                    # Headwind penalty below is unchanged. Card informational.
                    rationale.append(
                        {
                            "src": "Macro",
                            "head": f"Sector Rotation Tailwind — {sector_etf} Favoured in {stage.title()} Cycle",
                            "body": (
                                f"Current macro indicators (yield curve, VIX, credit spreads, S&P trend) suggest a "
                                f"'{stage}' economic cycle stage. {sector_etf} historically outperforms in this environment. "
                                f"Sector rotation model confidence: {conf}%."
                            ),
                            "sentiment": "pos",
                            "meta": f"Cycle: {stage} | Favoured: {', '.join(favoured[:3])}",
                        }
                    )
                elif sector_etf in avoid:
                    score -= 5
                    rationale.append(
                        {
                            "src": "Macro",
                            "head": f"Sector Rotation Headwind — {sector_etf} Underperforms in {stage.title()} Cycle",
                            "body": (
                                f"The '{stage}' cycle stage typically sees {sector_etf} underperform. "
                                f"Capital tends to rotate toward: {', '.join(favoured[:3])}. "
                                f"Model confidence: {conf}%."
                            ),
                            "sentiment": "neg",
                            "meta": f"Cycle: {stage} | Avoid: {', '.join(avoid[:3])}",
                        }
                    )

        # ── Multi-timeframe confirmation (weekly + 1H) ───────────────────────
        # Weekly trend
        if weekly_trend == 1 and score > 0:
            score *= 1.10  # daily BUY confirmed by weekly uptrend
        elif weekly_trend == -1 and score > 0:
            score *= 0.70  # daily BUY against weekly downtrend
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Weekly Downtrend Conflict",
                    "body": "Daily BUY signal contradicts the weekly downtrend. Price is below its 20-week average — counter-trend trades have lower win rates.",
                    "sentiment": "neg",
                    "meta": "Weekly SMA20 bearish",
                }
            )
        elif weekly_trend == -1 and score < 0:
            score *= 1.10  # daily SELL confirmed by weekly downtrend
        elif weekly_trend == 1 and score < 0:
            score *= 0.75  # daily SELL against weekly uptrend

        # Apply weekly OHLCV trend strength (Polygon 26-week bars)
        if _weekly_ohlcv_score != 0:
            score += _weekly_ohlcv_score
            sources.add("Technical")
            if _weekly_ohlcv_score > 0:
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Weekly OHLCV: Sustained Medium-Term Uptrend",
                        "body": "Price has been above its 13-week average in 8 or more of the last 10 weeks. Persistent weekly trend momentum reduces false signal rate in choppy markets.",
                        "sentiment": "pos",
                        "meta": "Polygon 26-week bars: ≥8/10 weeks above SMA13",
                    }
                )
            else:
                rationale.append(
                    {
                        "src": "Technical",
                        "head": "Weekly OHLCV: Sustained Medium-Term Downtrend",
                        "body": "Price has been below its 13-week average in 8 or more of the last 10 weeks. Persistent weekly bearish structure.",
                        "sentiment": "neg",
                        "meta": "Polygon 26-week bars: ≥8/10 weeks below SMA13",
                    }
                )

        # 1H intraday timeframe confirmation — completes the 1D/1W/1H trifecta.
        # Requires RSI, MACD, and EMA all aligned on the 1H chart.
        try:
            if df_1h is not None and len(df_1h) >= 20:
                _1h_result = await asyncio.to_thread(_compute_1h_techs, df_1h)
                rsi_1h = _1h_result["rsi_1h"]
                _macd_1h = _1h_result["macd_1h"]
                _above_ema_1h = _1h_result["above_ema_1h"]

                h1_bullish = rsi_1h > 55 and _macd_1h > 0 and _above_ema_1h
                h1_bearish = rsi_1h < 45 and _macd_1h < 0 and not _above_ema_1h

                if score > 0 and h1_bullish:
                    score *= 1.08
                    sources.add("Technical")
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"1H Timeframe Confirms BUY (RSI {rsi_1h:.0f})",
                            "body": (
                                f"1-hour chart is bullish: RSI {rsi_1h:.0f}, MACD positive, price above EMA20. "
                                "All three timeframes (1D, 1W, 1H) align — highest conviction setup."
                            ),
                            "sentiment": "pos",
                            "meta": f"1H RSI {rsi_1h:.0f} | MACD {'pos' if _macd_1h > 0 else 'neg'}",
                        }
                    )
                elif score > 0 and h1_bearish:
                    score *= 0.82
                    sources.add("Technical")
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"1H Timeframe Contradicts BUY (RSI {rsi_1h:.0f})",
                            "body": (
                                f"1-hour chart is bearish: RSI {rsi_1h:.0f}, MACD negative, price below EMA20. "
                                "Short-term momentum conflicts with daily BUY — wait for 1H alignment."
                            ),
                            "sentiment": "neg",
                            "meta": f"1H RSI {rsi_1h:.0f} | MACD {'pos' if _macd_1h > 0 else 'neg'}",
                        }
                    )
                elif score < 0 and h1_bearish:
                    score *= 1.08  # more negative (confirmed bear)
                    sources.add("Technical")
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"1H Timeframe Confirms SELL (RSI {rsi_1h:.0f})",
                            "body": (
                                f"1-hour chart is bearish: RSI {rsi_1h:.0f}, MACD negative, price below EMA20. "
                                "All three timeframes align bearishly — high-conviction SELL setup."
                            ),
                            "sentiment": "neg",
                            "meta": f"1H RSI {rsi_1h:.0f}",
                        }
                    )
                elif score < 0 and h1_bullish:
                    score *= 0.82  # less negative (contradicted)
                    sources.add("Technical")
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": f"1H Timeframe Contradicts SELL (RSI {rsi_1h:.0f})",
                            "body": (
                                "1-hour chart is bullish while the daily is bearish. "
                                "Intraday momentum conflicts with the daily SELL — reduce position or wait."
                            ),
                            "sentiment": "pos",
                            "meta": f"1H RSI {rsi_1h:.0f}",
                        }
                    )
        except Exception:
            log.warning("1H technicals fetch failed for %s", ticker, exc_info=True)

        # ── Trend alignment gate (daily 200-DMA) ─────────────────────────────
        # Any BUY signal below the 200-DMA is a counter-trend trade — apply
        # a graded penalty: moderate (-15%) for stocks just under the line,
        # severe (-25%) for stocks deeply below it.
        if sma200:
            below_200_pct = (price / sma200 - 1) * 100
            if score > 0 and price < sma200:
                if below_200_pct < -3:  # deeply below — strong penalty
                    score *= 0.75
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": "Counter-Trend BUY Warning",
                            "body": (
                                f"BUY signal in a long-term downtrend. Price (${price:.2f}) is "
                                f"{abs(below_200_pct):.1f}% below the 200-day MA (${sma200:.2f}). "
                                "Only the highest-conviction reversals succeed here — reduce size."
                            ),
                            "sentiment": "neg",
                            "meta": f"Price vs 200-DMA: {below_200_pct:.1f}%",
                        }
                    )
                else:  # within 0–3% below — moderate penalty
                    score *= 0.87
                    rationale.append(
                        {
                            "src": "Technical",
                            "head": "200-DMA Trend Gate — Confidence Reduced",
                            "body": (
                                f"BUY signal with price (${price:.2f}) just below the 200-day MA "
                                f"(${sma200:.2f}). Trend-following BUY signals have lower win rates "
                                "below this key long-term level. Conviction reduced."
                            ),
                            "sentiment": "neg",
                            "meta": f"Price vs 200-DMA: {below_200_pct:.1f}%",
                        }
                    )
            elif score < 0 and price > sma200 * 1.05:
                score *= 0.80  # SELL into strong uptrend — harder to play

        # ── Warning Signal De-confliction (Weighted Logic Gate) ─────────────
        # Certain "warning" signals should dynamically reduce position sizing/confidence
        # even if the overall direction is still BUY/SELL. This prevents contradictory
        # signals like "Stochastic Overbought" + "BUY" with high confidence.
        warning_signals = {
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
        warning_sell_signals = {
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
                warning_rationale.append(
                    {
                        "src": "Risk Gate",
                        "head": f"Warning: {head}",
                        "body": "This overbought condition reduces conviction in the BUY signal. Consider reducing position size.",
                        "sentiment": "neg",
                        "meta": f"Confidence penalty: -{penalty * 100:.0f}%",
                    }
                )
            # For SELL signals, penalize oversold warnings
            elif score < 0 and head in warning_sell_signals:
                penalty = 0.08
                warning_penalty += penalty
                warning_rationale.append(
                    {
                        "src": "Risk Gate",
                        "head": f"Warning: {head}",
                        "body": "This oversold condition reduces conviction in the SELL signal. Consider reducing position size.",
                        "sentiment": "neg",
                        "meta": f"Confidence penalty: -{penalty * 100:.0f}%",
                    }
                )

        # Cap warning penalty at 20% (down from 30%); combine with other penalties
        warning_penalty = min(warning_penalty, 0.20)
        rationale.extend(warning_rationale)
        total_confidence_penalty = min(
            0.40, warning_penalty + vol_confidence_penalty + rs_confidence_penalty + insider_confidence_penalty
        )

        # ── Correlation-Based Portfolio Limits ──────────────────────────────
        # Suppress BUY signals when the paper portfolio already has too much
        # exposure in this ticker's sector (default threshold: 30% of portfolio).
        portfolio_ctx = (market_ctx or {}).get("portfolio_ctx", {})

        # Portfolio concentration risk is INVENTORY RISK (Beta), not alpha uncertainty.
        # It must NOT corrupt total_confidence_penalty / confidence, which represents
        # the calibrated predictive probability of the signal (Alpha). Mixing them
        # destroys the XGBoost calibration loop — an 80% signal is 80% regardless of
        # how much XLK you already hold. The correct fix: keep confidence pure and
        # communicate concentration risk via a separate position_size_scale that the
        # execution/routing layer uses to scale down the recommended size to $0 (or
        # some fraction) without touching the Alpha score.
        # _portfolio_size_scale starts at 1.0 (full size) and is reduced here.
        _portfolio_size_scale: float = 1.0

        # ── PCA-based factor concentration ──────────────────────────────────
        pca_risk = portfolio_ctx.get("pca_risk", {}) if portfolio_ctx else {}
        _pca_haircut_raw = pca_risk.get("haircut_pct", 0) or 0
        _dom_exp_raw = pca_risk.get("dominant_exposure", 0) or 0
        if score > 0 and _pca_haircut_raw > 0 and _dom_exp_raw >= 0.35:
            _pca_scale_cut = _pca_haircut_raw / 100.0
            _portfolio_size_scale = max(0.0, _portfolio_size_scale - _pca_scale_cut)
            _dom_factor = pca_risk.get("dominant_factor", "Unknown")
            sources.add("Risk Gate")
            rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"PCA Factor Concentration — {_dom_factor} ({_dom_exp_raw:.0%} exposure)",
                    "body": (
                        f"Your portfolio's statistical risk is concentrated ({_dom_exp_raw:.0%}) on "
                        f"the '{_dom_factor}' latent factor — detected via 2-factor PCA on "
                        f"60-day return correlations. GICS sector limits may miss cross-sector overlap "
                        f"(e.g. XLK + XLC both loading on the growth factor). "
                        f"Signal confidence is unchanged (alpha is alpha). "
                        f"Recommended position size scaled to {(_portfolio_size_scale) * 100:.0f}% of normal."
                    ),
                    "sentiment": "neg",
                    "meta": f"pca_factor={_dom_factor} exposure={_dom_exp_raw:.0%} size_scale={_portfolio_size_scale:.2f}",
                }
            )
        if portfolio_ctx and score > 0:
            sector_exposure = portfolio_ctx.get("sector_exposure", {})
            ticker_sector = (sector_rs or {}).get("sector_etf") if sector_rs else None
            if ticker_sector and ticker_sector in sector_exposure:
                exposure_pct = sector_exposure[ticker_sector]
                # Tighter limits vs prior 30%/50%: a 4% overnight Nasdaq gap at 50%
                # tech exposure inflicts a ~2% portfolio loss before the stop fires.
                # At 30% hard limit the same gap causes ≤1.2% — within single-trade budget.
                SOFT_LIMIT = 20.0
                HARD_LIMIT = 30.0
                if exposure_pct >= HARD_LIMIT:
                    # Hard limit: portfolio capacity is zero, but alpha signal is valid.
                    # Zero positionSizeScale (Beta) — NOT score (Alpha) — because sector
                    # concentration is a portfolio risk constraint, not a predictor of
                    # whether the underlying trade will be profitable.
                    _portfolio_size_scale = 0.0
                    _force_hold = True  # prevent subsequent sector signals from reopening
                    sources.add("Risk Gate")
                    rationale.append(
                        {
                            "src": "Risk Gate",
                            "head": f"Sector Exposure Limit Hit — {ticker_sector} {exposure_pct:.0f}% of Portfolio",
                            "body": (
                                f"Your paper portfolio already has {exposure_pct:.0f}% of its value in {ticker_sector} "
                                f"sector positions (hard limit: {HARD_LIMIT:.0f}%). "
                                "Signal confidence is unchanged (alpha is alpha). "
                                "Recommended position size is $0 — close an existing position in this sector before adding more."
                            ),
                            "sentiment": "neg",
                            "meta": f"{ticker_sector} exposure: {exposure_pct:.0f}% > {HARD_LIMIT:.0f}% limit | size_scale=0.00",
                        }
                    )
                elif exposure_pct >= SOFT_LIMIT:
                    # Soft limit: reduce recommended position size, NOT the alpha confidence.
                    size_cut = min(0.5, (exposure_pct - SOFT_LIMIT) / (HARD_LIMIT - SOFT_LIMIT) * 0.5)
                    _portfolio_size_scale = max(0.0, _portfolio_size_scale - size_cut)
                    sources.add("Risk Gate")
                    rationale.append(
                        {
                            "src": "Risk Gate",
                            "head": f"Sector Concentration Warning — {ticker_sector} {exposure_pct:.0f}% of Portfolio",
                            "body": (
                                f"Your paper portfolio has {exposure_pct:.0f}% of its value in {ticker_sector} "
                                f"(soft limit: {SOFT_LIMIT:.0f}%). "
                                "Adding here increases concentration risk. Signal confidence is unchanged. "
                                f"Recommended position size scaled to {_portfolio_size_scale * 100:.0f}% of normal. "
                                "Consider diversifying."
                            ),
                            "sentiment": "neg",
                            "meta": f"{ticker_sector} exposure: {exposure_pct:.0f}% (soft limit {SOFT_LIMIT:.0f}%) size_scale={_portfolio_size_scale:.2f}",
                        }
                    )

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
                            score += _wr.score
                        sources |= _wr.sources
                        rationale += _wr.rationale
            except (asyncio.TimeoutError, Exception):
                # Workers already cancelled or timed out — proceed without them.
                # This guarantees signal generation is never blocked by worker latency.
                pass

        # §81 Block Print Detection REMOVED (gate audit 2026-07-14): 0 fires
        # in 87,982 all-time signals — the score thresholds never triggered.
        # Untestable in backtest (no historical block-trade data), so no
        # evidence path exists. get_recent_block_prints() retained in
        # polygon_client.py for ad-hoc research use.

        # ── OFI: Order Flow Imbalance (Lee-Ready 1min approximation) ─────────
        # Cont, Kukanov & Stoikov (2013): OFI predicts short-term price impact.
        # Divergence (price down + net buy flow) = institutional accumulation = MR boost.
        try:
            if not _is_lev_etf:
                from services.polygon_client import get_ofi_signals as _get_ofi

                _ofi = await asyncio.wait_for(_get_ofi(ticker), timeout=3.0)
                _ofi_1d = _ofi.get("ofi_1d", 0.0)
                _ofi_div = _ofi.get("ofi_divergence", 0.0)

                # Inline MR-entry check (mirrors _assemble_signal._has_mr)
                _ofi_bb = tech.get("bb_pct_b")
                _ofi_ibs = tech.get("ibs")
                _ofi_vwap = tech.get("vwap_pct")
                _ofi_rsi = tech.get("rsi")
                _ofi_rsi_trig = float(_ofi_rsi if _ofi_rsi is not None else 50) < 42
                _ofi_has_mr = (
                    sum(
                        [
                            _ofi_rsi_trig,
                            _ofi_bb is not None and float(_ofi_bb) < 0.22,
                            _ofi_ibs is not None and float(_ofi_ibs) < 0.15,
                            _ofi_vwap is not None and float(_ofi_vwap) < -0.75,
                        ]
                    )
                    >= 2
                )
                if _ofi_has_mr and action == "BUY":
                    if _ofi_div > 0.10:
                        score += 5
                        sources.add("Options/Flow")
                        rationale.append(
                            {
                                "src": "Options/Flow",
                                "head": "OFI Divergence — Institutional Accumulation",
                                "body": (
                                    f"Price fell today but net order flow was buyer-initiated "
                                    f"(divergence={_ofi_div:+.3f}). Smart money absorbing retail sell — "
                                    "strongest 1-min microstructure confirmation for MR BUY entry."
                                ),
                                "sentiment": "pos",
                                "meta": f"ofi_1d={_ofi_1d:+.3f} ofi_div={_ofi_div:+.3f}",
                            }
                        )
                    elif _ofi_1d > 0.20:
                        score += 3
                        sources.add("Options/Flow")
                        rationale.append(
                            {
                                "src": "Options/Flow",
                                "head": f"Positive OFI — Net Buy Flow ({_ofi_1d:+.2f}× session vol)",
                                "body": (
                                    f"1-minute order flow imbalance is net positive ({_ofi_1d:+.3f} normalized). "
                                    "Buyers absorbing the dip — adds confirmation to MR BUY setup."
                                ),
                                "sentiment": "pos",
                                "meta": f"ofi_1d={_ofi_1d:+.3f}",
                            }
                        )
                    elif _ofi_1d < -0.35:
                        score -= 6
                        sources.add("Options/Flow")
                        rationale.append(
                            {
                                "src": "Options/Flow",
                                "head": f"Negative OFI — Active Distribution ({_ofi_1d:+.2f}× session vol)",
                                "body": (
                                    f"1-minute order flow is net seller-initiated ({_ofi_1d:+.3f} normalized). "
                                    "Price dip driven by active sellers, not noise — MR entry is premature."
                                ),
                                "sentiment": "neg",
                                "meta": f"ofi_1d={_ofi_1d:+.3f}",
                            }
                        )
        except Exception:
            log.warning("massive analyst intelligence failed for %s", ticker, exc_info=True)

        # ── §80 NBBO Spread Quality Gate ─────────────────────────────────────
        # Amihud & Mendelson (1986): wide bid-ask spreads impose a transaction cost
        # that makes the backtest's 0.50% round-trip friction assumption too optimistic.
        # Data: Polygon snapshot lastQuote cached from the batch call — zero extra API cost.
        # lastQuote.P = bid (capital P), lastQuote.p = ask (lowercase p).
        try:
            from services.polygon_client import _snapshot_cache as _snap_cache

            _snap_entry = _snap_cache.get(ticker.upper())
            if _snap_entry is not None:
                _snap_dict, _ = _snap_entry
                _lq = _snap_dict.get("lastQuote") or {}
                _bid = float(_lq.get("P") or 0)
                _ask = float(_lq.get("p") or 0)
                if _bid > 0 and _ask > 0 and _ask >= _bid:
                    _mid = (_bid + _ask) / 2.0
                    _spread_pct = (_ask - _bid) / _mid * 100.0
                    if _spread_pct > 1.00:
                        # Spread > 1% → round-trip cost is 2× the backtest assumption;
                        # expected value near zero after friction. Hard penalty.
                        score -= 10
                        sources.add("Risk Gate")
                        rationale.append(
                            {
                                "src": "Risk Gate",
                                "head": f"Wide Bid-Ask Spread ({_spread_pct:.2f}%) — Friction Kills Edge",
                                "body": (
                                    f"Current bid-ask spread of {_spread_pct:.2f}% makes the round-trip "
                                    f"cost ≥1% — double the 0.50% friction assumption in the backtest. "
                                    "At this spread the expected edge on a 10-day MR trade is near zero. "
                                    "Wait for tighter market conditions or more liquid entry."
                                ),
                                "sentiment": "neg",
                                "meta": f"spread={_spread_pct:.2f}% bid={_bid:.2f} ask={_ask:.2f}",
                            }
                        )
                    elif _spread_pct > 0.50:
                        # Spread 0.5–1% → approaches friction limit; moderate penalty
                        score -= 5
                        sources.add("Risk Gate")
                        rationale.append(
                            {
                                "src": "Risk Gate",
                                "head": f"Elevated Bid-Ask Spread ({_spread_pct:.2f}%) — Reduced Edge",
                                "body": (
                                    f"Bid-ask spread of {_spread_pct:.2f}% is at the upper boundary "
                                    f"of the 0.50% friction assumption. Live fills will consume a "
                                    "meaningful fraction of the expected return. Reduce position size."
                                ),
                                "sentiment": "neg",
                                "meta": f"spread={_spread_pct:.2f}% bid={_bid:.2f} ask={_ask:.2f}",
                            }
                        )
                    elif _spread_pct < 0.10:
                        # Tight spread — excellent execution quality
                        score += 1
                        rationale.append(
                            {
                                "src": "Risk Gate",
                                "head": f"Tight Spread ({_spread_pct:.2f}%) — Clean Execution",
                                "body": (
                                    f"Bid-ask spread of only {_spread_pct:.2f}% — well below the "
                                    "0.50% friction assumption. Slippage is minimal; full edge intact."
                                ),
                                "sentiment": "pos",
                                "meta": f"spread={_spread_pct:.2f}%",
                            }
                        )
        except Exception:
            log.warning("OFI signal fetch failed for %s", ticker, exc_info=True)

        # RD-3 / §79: Q1 seasonal rebalancing bonus (Jan–Mar, sector laggards)
        _sector_etf_for_q1 = (sector_rs or {}).get("sector_etf") if "sector_rs" in dir() else None
        score, rationale = _apply_q1_rebalancing(score, rationale, _sector_etf_for_q1, vix)

        return _assemble_signal(
            ticker=ticker,
            info=info,
            tech=tech,
            score=score,
            rationale=rationale,
            sources=sources,
            _force_hold=_force_hold,
            _is_low_atr=_is_low_atr,
            _atr_pct_pre=_atr_pct_pre,
            total_confidence_penalty=total_confidence_penalty,
            portfolio_size_scale=_portfolio_size_scale,
            avg_sent=avg_sent,
            price=price,
            atr=atr,
            market_ctx=market_ctx,
            earnings_cal=earnings_cal,
            sector_rs=sector_rs,
            days_to_earnings=days_to_earnings,
            opt_flow=opt_flow,
            _is_lev_etf=_is_lev_etf,
            data_warnings=data_warnings,
            days_to_exdiv=days_to_exdiv,
            promoted_sectors=promoted_sectors,
        )

    except Exception:
        log.exception("[signal_engine] %s: unhandled error in generate_signal", ticker)
        return None


async def scan_all(
    tickers: list[str],
    market_ctx: Optional[dict] = None,
    histories: Optional[dict] = None,
    infos: Optional[dict] = None,
    promoted_sectors: Optional[set[str]] = None,
) -> list[dict]:
    histories = histories or {}
    infos = infos or {}

    # ── Refresh ticker-performance snapshot if stale or absent ───────────────
    # Stage B: point-in-time replacement for the static defensive-ticker blocklist.
    # If a DB session is available, recompute the decay-weighted ticker hit-rate
    # snapshot once per scan.  The gate itself runs in shadow mode inside
    # _assemble_signal() and does not affect delivery yet.
    try:
        from database import AsyncSessionLocal
        from services.gates.ticker_performance import get_snapshot, refresh_snapshot

        _snap = get_snapshot()
        if _snap is None or (datetime.now(timezone.utc) - _snap.computed_at).total_seconds() > 3600:
            async with AsyncSessionLocal() as db:
                await refresh_snapshot(db)
    except Exception:
        log.debug("[scan_all] ticker performance snapshot refresh skipped", exc_info=True)

    # ── §63 Sector cointegration: inject ETF close-price series into market_ctx ─
    # If sector ETF DataFrames are present in the prefetched histories dict (they
    # usually are since XLK/XLF/XLY/XLC/XLB are in the watchlist), extract their
    # Close series so generate_signal can compute cointegration Z-scores without
    # any additional API calls. Zero extra cost — pure rearrangement.
    _COINT_ETF_TICKERS = {"XLK", "XLF", "XLY", "XLC", "XLB", "XLE", "XLI", "XLV", "XLP"}
    _etf_histories: dict[str, pd.Series] = {}
    for _etf in _COINT_ETF_TICKERS:
        _etf_df = histories.get(_etf)
        if _etf_df is not None and "Close" in _etf_df.columns and len(_etf_df) >= 60:
            _etf_histories[_etf] = _etf_df["Close"].astype(float)
    if _etf_histories:
        market_ctx = dict(market_ctx or {})
        market_ctx["etf_histories"] = _etf_histories

    # Semaphore(8): reduced from 15 to cap concurrent DB writers per worker.
    # With 3 Uvicorn workers × 15 = 45 concurrent DB writes, which under burst
    # retry (3× SQLAlchemy retries) can hit 90 concurrent — exceeding pool_size=10
    # + max_overflow=20. At 8 per worker: 3 × 8 = 24 steady-state, 72 peak-retry,
    # both within pool budget. Scan wall-clock: 154 tickers × 2.5s / 8 ≈ 48s (was 26s).
    _sem = asyncio.Semaphore(8)

    async def _guarded(t: str):
        async with _sem:
            return await generate_signal(
                t,
                market_ctx=market_ctx,
                prefetched_df=histories.get(t),
                prefetched_info=infos.get(t),
                promoted_sectors=promoted_sectors,
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
        n_peers = min(len(peers), 3)  # judge against top-3
        n_bull = len(bullish_peers)

        if n_bull < 2:
            peer_names = ", ".join(p["ticker"] for p in peers[:3])
            bull_names = ", ".join(p["ticker"] for p in bullish_peers) or "none"
            # Penalty scales with how isolated the signal is.  This is a
            # peer-context adjustment, not evidence about expected win rate, so
            # it mutates display confidence only — calibrated probability is
            # preserved.
            haircut = 12 if n_bull == 0 else 6
            sig["displayConfidence"] = round(max(35.0, sig.get("displayConfidence", sig["confidence"]) - haircut), 1)
            sig["confidence"] = sig["displayConfidence"]
            sig["rationale"] = list(sig.get("rationale", [])) + [
                {
                    "src": "Sector",
                    "head": f"Sector Peers Not Confirming BUY — {n_bull}/{n_peers} Bullish ({etf})",
                    "body": (
                        f"Of the {len(peers[:3])} {etf}-sector peers on the watchlist "
                        f"({peer_names}), only {n_bull} {'are' if n_bull != 1 else 'is'} bullish "
                        f"({bull_names}). "
                        "Stocks within a sector mean-revert to their cross-sectional correlation: "
                        "a lone-outlier BUY has a materially lower true-positive rate than a "
                        "sector-confirmed move. Display confidence reduced; calibrated probability unchanged."
                    ),
                    "sentiment": "neg",
                    "meta": f"{etf}: {n_bull}/{n_peers} peers bullish | −{haircut}pp display_confidence",
                }
            ]
            sig["sources"] = sorted(set(sig.get("sources", [])) | {"Sector"})

    # ── Layer 2: Polygon Related Companies peer check ─────────────────────────
    try:
        from services.polygon_related import check_related_peer_confirmation

        high_conf_buys = [s for s in signals if s.get("action") == "BUY"]
        for sig in high_conf_buys:
            adj, reason = await check_related_peer_confirmation(sig["ticker"], sig["action"], signals_by_ticker)
            if adj != 0.0:
                sig["displayConfidence"] = round(
                    max(35.0, min(72.0, sig.get("displayConfidence", sig["confidence"]) + adj)), 1
                )
                sig["confidence"] = sig["displayConfidence"]
                sentiment = "pos" if adj > 0 else "neg"
                sig["rationale"] = list(sig.get("rationale", [])) + [
                    {
                        "src": "Sector",
                        "head": f"Polygon Related Companies {'Confirm' if adj > 0 else 'Diverge'} ({adj:+.0f}pp)",
                        "body": reason,
                        "sentiment": sentiment,
                        "meta": f"related_adj={adj:+.1f}pp display_confidence_only",
                    }
                ]
                sig["sources"] = sorted(set(sig.get("sources", [])) | {"Sector"})
    except Exception:
        log.warning("polygon related companies peer check failed", exc_info=True)

    # ── Supply Chain Graph Propagation ──────────────────────────────────────────
    # Second pass: check if a key supplier of each ticker has a strong signal.
    # TSM BUY → NVDA/AMD/QCOM get a small lead-lag boost; XOM SELL → airlines penalty.
    try:
        from services.supply_chain import get_supply_chain_propagation_score

        _sig_map = {s["ticker"]: s for s in signals}
        for sig in signals:
            sc_delta, sc_reason = get_supply_chain_propagation_score(sig["ticker"], _sig_map)
            if abs(sc_delta) >= 1.0:
                # Convert score delta to a display-confidence adjustment (capped ±4pp).
                # This is lead-lag context, not new evidence about this ticker's
                # win rate, so it does not mutate calibrated probability.
                _conf_adj = max(-4.0, min(4.0, sc_delta * 0.5))
                sig["displayConfidence"] = round(
                    max(35.0, min(72.0, sig.get("displayConfidence", sig["confidence"]) + _conf_adj)), 1
                )
                sig["confidence"] = sig["displayConfidence"]
                sig["rationale"] = list(sig.get("rationale", [])) + [
                    {
                        "src": "Fundamentals",
                        "head": f"Supply Chain Propagation ({sc_delta:+.1f}pts)",
                        "body": (
                            f"Key supplier signal propagated to {sig['ticker']}: "
                            f"{sc_reason}. Supplier performance leads customer "
                            f"revenue by 1–4 weeks in the semiconductor and "
                            f"commodity cycles."
                        ),
                        "sentiment": "pos" if sc_delta > 0 else "neg",
                        "meta": f"supply_chain_propagation={sc_delta:+.1f} display_confidence_only",
                    }
                ]
                sig["sources"] = sorted(set(sig.get("sources", [])) | {"Fundamentals"})
    except Exception:
        log.warning("supply chain propagation scoring failed", exc_info=True)

    # ── Cross-sectional universe ranking ──────────────────────────────────────
    # Rank every directional signal by calibrated probability within this scan cycle.
    # Top decile (+3pp) and top quartile (+1.5pp) get a boost; bottom quartile
    # and bottom decile receive symmetric penalties. This converts the engine
    # from absolute scoring to relative scoring — what hedge funds actually use.
    # Requires ≥10 directional signals to be meaningful; smaller batches skip.
    try:
        _dir = [s for s in signals if s.get("action") in ("BUY", "SELL")]
        _n = len(_dir)
        if _n >= 10:
            _sorted_idx = sorted(range(_n), key=lambda i: _dir[i].get("calibratedProbability", _dir[i]["confidence"]))
            for _rank_pos, _idx in enumerate(_sorted_idx):
                sig = _dir[_idx]
                _pct = _rank_pos / (_n - 1)  # 0.0 = weakest, 1.0 = strongest
                sig["rankPercentile"] = round(_pct * 100, 1)
                sig["rankScore"] = _n - _rank_pos  # 1 = weakest, _n = strongest
                if _pct >= 0.90:
                    _adj, _label = 3.0, "Top decile"
                elif _pct >= 0.75:
                    _adj, _label = 1.5, "Top quartile"
                elif _pct <= 0.10:
                    _adj, _label = -3.0, "Bottom decile"
                elif _pct <= 0.25:
                    _adj, _label = -1.5, "Bottom quartile"
                else:
                    continue
                sig["displayConfidence"] = round(
                    max(35.0, min(72.0, sig.get("displayConfidence", sig["confidence"]) + _adj)), 1
                )
                sig["confidence"] = sig["displayConfidence"]
                _pctile_int = round(_pct * 100)
                sig["rationale"] = list(sig.get("rationale", [])) + [
                    {
                        "src": "Cross-Sectional",
                        "head": f"{_label} — {_pctile_int}th Percentile of {_n}-Signal Universe ({_adj:+.0f}pp)",
                        "body": (
                            f"Ranked against today's full {_n}-ticker scan universe: {_pctile_int}th "
                            f"percentile. {_label} signals receive a {_adj:+.0f}pp display-confidence "
                            "adjustment — the same relative-strength principle used in cross-sectional "
                            "quant models to separate strongest from weakest setups each cycle. "
                            "Calibrated probability is unchanged."
                        ),
                        "sentiment": "pos" if _adj > 0 else "neg",
                        "meta": f"universe_rank={_pctile_int}th | n={_n} | adj={_adj:+.0f}pp | calibrated_unchanged",
                    }
                ]
                sig["sources"] = sorted(set(sig.get("sources", [])) | {"Cross-Sectional"})
    except Exception:
        log.warning("cross-sectional universe ranking failed", exc_info=True)

    # ── Cross-sectional alpha model (LIVE — h=63 research-promoted) ───────────
    # Attach the persisted h=21 and h=63 cross-sectional model batch percentiles
    # to each directional signal. The h=63 quarterly variant passed the §111
    # research-promotion gate (nested-horizon net Sharpe +0.576, 90% CI excludes 0,
    # cost- and borrow-robust); _SHADOW_SIZING_ACTIVE is True so bottom-decile
    # names receive the §92 sizing haircut.  The h=21 field continues to accrue
    # forward shadow data for an eventual live-forward §92 promotion check.
    try:
        from services import cross_sectional_shadow as _css

        _xs = _css.score_batch(histories)
        # Parallel h=63 (quarterly) shadow — nested-horizon validated 2026-06-11.
        # Logged as a separate field; NEVER feeds §92 promotion or sizing.
        _xs63 = _css.score_batch_h63(histories)
        if _xs or _xs63:
            _scored = 0
            for _sig in signals:
                if _sig.get("action") not in ("BUY", "SELL"):
                    continue
                _pct63 = _xs63.get(_sig["ticker"])
                if _pct63 is not None:
                    _sig["crossSectionalShadowPctH63"] = _pct63  # raw metadata for logging/analysis
                _pct = _xs.get(_sig["ticker"])
                if _pct is None:
                    continue
                _sig["crossSectionalShadowPct"] = _pct  # raw metadata for logging/analysis
                _band = (
                    "bottom decile"
                    if _pct <= 10
                    else "bottom quartile"
                    if _pct <= 25
                    else "top decile"
                    if _pct >= 90
                    else "top quartile"
                    if _pct >= 75
                    else "mid-pack"
                )
                _sig["rationale"] = list(_sig.get("rationale", [])) + [
                    {
                        "src": "Cross-Sectional Alpha (shadow)",
                        "head": f"XS alpha model: {_pct:.0f}th percentile ({_band}) — SHADOW, no action impact",
                        "body": (
                            "Independent h=21 cross-sectional alpha model's predicted relative-return rank "
                            "within today's scan batch (100 = strongest predicted relative performer). "
                            "SHADOW MODE: logged for forward validation only — does not alter this "
                            "recommendation (thin, horizon-mismatched edge; see CLAUDE.md §86)."
                        ),
                        "sentiment": "neu",
                        "meta": f"xs_shadow_pct={_pct} band={_band}"
                        + (f" xs_shadow_pct_h63={_pct63}" if _pct63 is not None else ""),
                    }
                ]
                _scored += 1
            # §92: apply shadow sizing ONLY when promotion criteria are pre-locked and met.
            _css.apply_shadow_sizing(signals)
            if _scored:
                log.info("[scan_all] cross-sectional SHADOW scored %d directional signals", _scored)
    except Exception as _xs_err:
        log.debug(f"[scan_all] cross-sectional shadow skipped: {_xs_err}")

    # ── §83 Cross-Signal Correlation Penalty ─────────────────────────────────
    # Grinold & Kahn (2000): IR degrades as √(1 − ρ) where ρ is average pairwise
    # return correlation of simultaneous BUY positions. When multiple correlated
    # names (AAPL+MSFT+GOOGL) fire together, the effective position size is larger
    # than the 5% target assumes. We reduce positionSizeScale (NOT confidence —
    # same principle as the sector concentration gate: alpha is alpha regardless
    # of how much correlated exposure you already hold).
    try:
        import numpy as _np83

        _buy_sigs = [s for s in signals if s.get("action") == "BUY"]
        if len(_buy_sigs) >= 2:
            # Build return matrix for all current BUY signals using 63-day window
            _ret_map: dict[str, _np83.ndarray] = {}
            for _sig in _buy_sigs:
                _t = _sig["ticker"]
                _df83 = histories.get(_t)
                if _df83 is not None and "Close" in _df83.columns and len(_df83) >= 63:
                    _rets = _df83["Close"].astype(float).pct_change().dropna().values[-63:]
                    if len(_rets) >= 40:
                        _ret_map[_t] = _rets

            for _sig in _buy_sigs:
                _t = _sig["ticker"]
                _r_t = _ret_map.get(_t)
                if _r_t is None:
                    continue
                _other_rets = [_ret_map[_o] for _o in _ret_map if _o != _t]
                if not _other_rets:
                    continue

                _corrs: list[float] = []
                for _r_o in _other_rets:
                    _n_min = min(len(_r_t), len(_r_o))
                    if _n_min < 20:
                        continue
                    try:
                        _c = float(_np83.corrcoef(_r_t[-_n_min:], _r_o[-_n_min:])[0, 1])
                        if not _np83.isnan(_c):
                            _corrs.append(_c)
                    except Exception:
                        log.warning("correlation calculation failed", exc_info=True)

                if not _corrs:
                    continue
                _avg_corr = float(_np83.mean(_corrs))

                if _avg_corr > 0.75:
                    _size_cut = min(0.40, (_avg_corr - 0.75) * 1.6)
                    _old_scale = float(_sig.get("positionSizeScale") or 1.0)
                    _sig["positionSizeScale"] = round(max(0.0, _old_scale - _size_cut), 2)
                    _sig["rationale"] = list(_sig.get("rationale", [])) + [
                        {
                            "src": "Risk Gate",
                            "head": f"High Correlation With Open Signals ({_avg_corr:.0%}) — Crowding Penalty",
                            "body": (
                                f"This ticker has {_avg_corr:.0%} average 63-day return correlation with "
                                f"the {len(_corrs)} other BUY signals firing today. "
                                "When positions are highly correlated the effective 5% size assumption "
                                "understates concentration risk (Grinold & Kahn 2000). "
                                f"Recommended position size scaled to {_sig['positionSizeScale'] * 100:.0f}% of normal. "
                                "Signal confidence is unchanged."
                            ),
                            "sentiment": "neg",
                            "meta": f"avg_corr={_avg_corr:.2f} size_scale={_sig['positionSizeScale']:.2f}",
                        }
                    ]
                    _sig["sources"] = sorted(set(_sig.get("sources", [])) | {"Risk Gate"})
    except Exception:
        log.warning("cross-signal correlation penalty failed", exc_info=True)

    return signals
