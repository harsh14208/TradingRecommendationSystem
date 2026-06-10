"""
Isolated scoring workers for signal_engine.py.

Each worker is a self-contained async function wrapped by WorkerTask that:
  • Accepts pre-fetched data from generate_signal's asyncio.gather phase.
  • Optionally performs its own supplemental IO (Polygon dividends, annual
    financials, float data) — the calls that currently sit inside the sequential
    scoring loop and block TA computation.
  • Returns a ScoringResult(score, sources, rationale) on success, or
    ScoringResult(ok=False) on timeout/circuit-break — never raises.

All 5 workers are launched concurrently at the start of generate_signal(),
running while TA scoring executes. Results are merged after TA completes,
eliminating the sequential IO wait.

Worker timeouts are tuned to data-source SLAs:
  TA           — 2s  (pure computation, should be instant)
  News         — 8s  (Benzinga + Finnhub; Benzinga batch usually cached)
  Fundamentals — 12s (Polygon dividend + annual API; 6h cached so usually fast)
  Options      — 6s  (score_options on pre-fetched data + massive_sigs)
  Institutional— 5s  (insider scoring + 13F from market_ctx)
  Sentiment    — 5s  (social + Google Trends; both cached)
"""

import logging

from services.worker_bus import ScoringResult, WorkerTask

log = logging.getLogger("signal.trade.workers")


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


# ─── 1. News Worker ────────────────────────────────────────────────────────────
# Merges Benzinga (fetched here), Finnhub and scraped news. Deduplicates on
# headline word-overlap. Returns news score contribution + headline rationale.


@WorkerTask(name="news", timeout=8.0, retries=2, cb_threshold=4, cb_reset_secs=120.0)
async def news_worker(
    ticker: str,
    news: list,
    scraped_news: list,
) -> ScoringResult:
    import re as _re

    result = ScoringResult()
    _all_news: list[dict] = []
    _seen_ws: list[frozenset] = []

    def _ws(s: str) -> frozenset:
        return frozenset(w.lower() for w in _re.split(r"\W+", s) if len(w) > 4)

    # Benzinga via Polygon — already in per-ticker cache from batch prefetch
    try:
        from services.benzinga_news import get_benzinga_news

        _bzg = await get_benzinga_news(ticker)
        for a in _bzg:
            _all_news.append(
                {
                    "headline": a["headline"],
                    "sentiment": a["sentiment"],
                    "hours_ago": 0,
                    "source": "Benzinga",
                    "summary": a["headline"],
                }
            )
        if _bzg:
            result.sources.add("Benzinga")
    except Exception:
        pass

    # Merge Finnhub + scraped, dedup by headline word-overlap
    for item in list(news or []) + list(scraped_news or []):
        ws = _ws(item.get("headline", ""))
        if ws and not any(len(ws & prev) / max(len(ws), 1) > 0.5 for prev in _seen_ws):
            _seen_ws.append(ws)
            _all_news.append(item)

    if not _all_news:
        return result

    # Age-decay weighted average sentiment
    total_w, weighted_s = 0.0, 0.0
    for n in _all_news:
        w = 1.0 / (1.0 + n.get("hours_ago", 48) / 24.0)
        weighted_s += n["sentiment"] * w
        total_w += w
    avg_sent = weighted_s / total_w if total_w > 0 else 0.0

    if news:
        result.sources.add("Finnhub")
    for lbl in ("Reuters", "Finviz"):
        if any(n.get("source", "") == lbl for n in _all_news):
            result.sources.add(lbl)

    top = sorted(_all_news, key=lambda x: x.get("hours_ago", 9999))[0]
    lbl = top.get("source", "News")
    meta = f"{lbl} · {top.get('hours_ago', '?')}h ago | {len(_all_news)} articles"

    if avg_sent > 0.25:
        result.score += min(15, round(avg_sent * 22))
        result.rationale.append(
            {
                "src": lbl,
                "head": top["headline"][:90],
                "body": top.get("summary", top["headline"])[:250],
                "sentiment": "pos",
                "meta": meta,
            }
        )
    elif avg_sent < -0.25:
        result.score += max(-15, round(avg_sent * 22))
        result.rationale.append(
            {
                "src": lbl,
                "head": top["headline"][:90],
                "body": top.get("summary", top["headline"])[:250],
                "sentiment": "neg",
                "meta": meta,
            }
        )
    return result


# ─── 2. Fundamentals Worker ────────────────────────────────────────────────────
# Scores Piotroski F-Score, FCF yield, ROE, dividend yield + Aristocrat bonus,
# Earnings Torpedo (3-year acceleration), and Polygon float for short squeeze.
# Does its own supplemental IO: Polygon dividends, annual financials, float.
# All three have 6h+ caches so the first call per day is the only slow one.


@WorkerTask(name="fundamentals", timeout=12.0, retries=1, cb_threshold=3, cb_reset_secs=300.0)
async def fundamentals_worker(
    ticker: str,
    fundamentals: dict,
    market_ctx: dict | None,
    price: float,
) -> ScoringResult:
    result = ScoringResult()
    if not fundamentals:
        return result

    macro = (market_ctx or {}).get("macro") or {}
    t10y = macro.get("t10y")

    # FCF Yield
    fcf = fundamentals.get("fcf_yield")
    if fcf is not None:
        result.sources.add("Fundamentals")
        if fcf > 8:
            result.score += 8
            result.rationale.append(
                {
                    "src": "Fundamentals",
                    "head": f"Strong FCF Yield {fcf:.1f}%",
                    "body": f"FCF yield of {fcf:.1f}% — above Treasury rates. Company self-funds growth without new debt.",
                    "sentiment": "pos",
                    "meta": f"FCF Yield: {fcf:.1f}%",
                }
            )
        elif fcf > 4:
            result.score += 4
        elif fcf < 0:
            result.score -= 6
            result.rationale.append(
                {
                    "src": "Fundamentals",
                    "head": "Negative Free Cash Flow",
                    "body": "Company burns more cash than it generates. External financing required.",
                    "sentiment": "neg",
                    "meta": f"FCF Yield: {fcf:.1f}%",
                }
            )

    # Polygon accurate dividend yield + Aristocrat bonus
    try:
        from services.massive_ratios import get_polygon_dividend_data

        div_data = await get_polygon_dividend_data(ticker)
        ttm_amt = div_data.get("div_ttm_amount")
        if ttm_amt and ttm_amt > 0 and price > 0:
            div_yield = round(ttm_amt / price * 100, 2)
            if t10y:
                gap = div_yield - t10y
                result.sources.add("Fundamentals")
                if gap > 1.0:
                    result.score += 6
                    result.rationale.append(
                        {
                            "src": "Fundamentals",
                            "head": f"Dividend Yield {div_yield:.1f}% > 10Y Treasury {t10y:.1f}%",
                            "body": f"Stock yields {div_yield:.1f}% — {gap:.1f}pp above Treasury. Yield-seeking demand mechanically bid.",
                            "sentiment": "pos",
                            "meta": f"Yield gap: +{gap:.1f}pp",
                        }
                    )
                elif gap < -2.0:
                    result.score -= 3
        aristo = div_data.get("div_aristocrat_level", "")
        if aristo:
            yrs = div_data.get("div_aristocrat_years", 0)
            pts = {"King": 5, "Aristocrat": 4, "Achiever": 2}.get(aristo, 0)
            result.score += pts
            result.sources.add("Fundamentals")
            result.rationale.append(
                {
                    "src": "Fundamentals",
                    "head": f"Dividend {aristo} — {yrs} Years of Increases",
                    "body": f"{ticker} has grown its dividend for {yrs} consecutive years. Structural commitment to shareholder returns.",
                    "sentiment": "pos",
                    "meta": f"div_{aristo.lower()}={yrs}yr +{pts}pts",
                }
            )
    except Exception:
        pass

    # Earnings Torpedo — 3-year annual revenue acceleration
    try:
        from services.massive_ratios import get_annual_revenue_acceleration

        ann = await get_annual_revenue_acceleration(ticker)
        if ann.get("revenue_torpedo"):
            gs = ann.get("annual_rev_growth", [])
            gs_str = " → ".join(f"+{g:.1f}%" for g in reversed(gs))
            result.score += 8
            result.sources.add("Fundamentals")
            result.rationale.append(
                {
                    "src": "Fundamentals",
                    "head": "Earnings Torpedo — 3-Year Revenue Acceleration",
                    "body": f"Annual revenue growth has accelerated 3 consecutive years: {gs_str}. Precedes institutional accumulation in 68% of cases (Driehaus/O'Neil).",
                    "sentiment": "pos",
                    "meta": f"annual_rev_torpedo=True growth={gs_str}",
                }
            )
    except Exception:
        pass

    # Polygon float for short squeeze accuracy
    try:
        from services.polygon_reference import get_float_data

        fdata = await get_float_data(ticker)
        float_shares = fdata.get("float_shares")
        shares_short = fundamentals.get("shares_short")
        if float_shares and float_shares > 0 and shares_short:
            sf = round(shares_short / float_shares * 100, 1)
            if sf > 20:
                result.sources.add("Short Interest")
                result.score += 9
                result.rationale.append(
                    {
                        "src": "Short Interest",
                        "head": f"High Short Float {sf:.1f}% (Polygon float data)",
                        "body": f"{sf:.1f}% of float sold short via Polygon-derived float. Rising price forces mechanical short covering.",
                        "sentiment": "pos",
                        "meta": f"short_float_polygon={sf:.1f}%",
                    }
                )
    except Exception:
        pass

    return result


# ─── 3. Options Worker ────────────────────────────────────────────────────────
# Scores multi-expiry options sweeps, GEX, dark pool from massive_sigs.


@WorkerTask(name="options", timeout=6.0, retries=1, cb_threshold=4, cb_reset_secs=180.0)
async def options_worker(
    ticker: str,
    opt_flow: dict | None,
    massive_sigs: dict | None,
) -> ScoringResult:
    result = ScoringResult()

    if opt_flow:
        try:
            from services.options import score_options

            opt_score, opt_rat = score_options(opt_flow)
            if opt_score != 0:
                result.score += opt_score
                result.sources.add("Options")
                result.rationale.extend(opt_rat)
        except Exception:
            pass

    if massive_sigs:
        # Dark pool short volume
        sv = (massive_sigs.get("short_interest") or {}).get("short_volume_pct", 0)
        if sv > 55:
            result.score -= 12
            result.sources.add("Dark Pool")
            result.rationale.append(
                {
                    "src": "Dark Pool",
                    "head": "Heavy Dark Pool Short Volume",
                    "body": f"Off-exchange short volume {sv:.1f}% — institutional distribution.",
                    "sentiment": "neg",
                    "meta": "Short Volume",
                }
            )
        elif 0 < sv < 35:
            result.score += 10
            result.sources.add("Dark Pool")
            result.rationale.append(
                {
                    "src": "Dark Pool",
                    "head": "Light Dark Pool Short Volume",
                    "body": f"Off-exchange short volume {sv:.1f}% — institutional accumulation.",
                    "sentiment": "pos",
                    "meta": "Short Volume",
                }
            )

        # FTDs & Reg SHO
        ftd = massive_sigs.get("ftd") or {}
        if ftd.get("is_reg_sho") and ftd.get("spike_pct", 0) > 300:
            result.score += 15
            result.sources.add("Fundamentals")
            result.rationale.append(
                {
                    "src": "Fundamentals",
                    "head": f"Reg SHO + FTD Spike ({ftd.get('spike_pct', 0):.0f}%)",
                    "body": "Stock on Reg SHO list with surging Fails-to-Deliver. High probability of forced short covering.",
                    "sentiment": "pos",
                    "meta": "FTD spike",
                }
            )

        # GEX
        gex_val = (massive_sigs.get("gex") or {}).get("net_gex", 0.0)
        if gex_val > 1_000_000:
            result.score += 0  # net effect on score is muted but included for rationale
            result.sources.add("Options")
            result.rationale.append(
                {
                    "src": "Options",
                    "head": "Positive Gamma Exposure (GEX)",
                    "body": "Dealers net long gamma. Volatility pinned — favours mean-reversion.",
                    "sentiment": "pos",
                    "meta": f"net_gex={gex_val:,.0f}",
                }
            )
        elif gex_val < -1_000_000:
            result.sources.add("Options")
            result.rationale.append(
                {
                    "src": "Options",
                    "head": "Negative Gamma Exposure (GEX)",
                    "body": "Dealers net short gamma. Volatility may amplify moves — momentum favoured.",
                    "sentiment": "neg",
                    "meta": f"net_gex={gex_val:,.0f}",
                }
            )

        # Retail vs Institutional flow divergence
        rif = massive_sigs.get("retail_vs_institutional") or {}
        inst_flow = rif.get("institutional_flow_usd", 0)
        ret_flow = rif.get("retail_flow_usd", 0)
        if abs(inst_flow) > 500_000 and inst_flow * ret_flow < 0:
            dir_str = "buying" if inst_flow > 0 else "selling"
            result.score += 8 if inst_flow > 0 else -8
            result.sources.add("Dark Pool")
            result.rationale.append(
                {
                    "src": "Dark Pool",
                    "head": f"Institutional {dir_str.capitalize()} vs Retail Divergence",
                    "body": f"Institutions are {dir_str} (${abs(inst_flow) / 1e6:.1f}M) while retail goes the other way. Smart money edge.",
                    "sentiment": "pos" if inst_flow > 0 else "neg",
                    "meta": f"inst={inst_flow / 1e6:+.1f}M ret={ret_flow / 1e6:+.1f}M",
                }
            )

    return result


# ─── 4. Institutional Worker ──────────────────────────────────────────────────
# Scores SEC Form 4 insider clusters and 13F QoQ trend from market_ctx.


@WorkerTask(name="institutional", timeout=5.0, retries=1, cb_threshold=4, cb_reset_secs=180.0)
async def institutional_worker(
    ticker: str,
    insider: dict | None,
    market_ctx: dict | None,
) -> ScoringResult:
    result = ScoringResult()

    # SEC Form 4 insider activity
    if insider and insider.get("filings", 0) > 0:
        iscore = insider["score"]
        result.score += iscore
        if abs(iscore) >= 4:
            result.sources.add("SEC EDGAR")
            net = insider.get("net_shares", 0)
            n_fv = insider.get("filings", 0)
            if iscore > 0:
                result.rationale.append(
                    {
                        "src": "SEC EDGAR",
                        "head": f"Insider Cluster Buy — {n_fv} Form 4 Filings",
                        "body": f"Multiple insiders purchased net {net:,} shares. Cluster buys within 30 days signal high conviction by executives who know the business best.",
                        "sentiment": "pos",
                        "meta": f"Net shares: +{net:,} | Filings: {n_fv}",
                    }
                )
            else:
                result.rationale.append(
                    {
                        "src": "SEC EDGAR",
                        "head": f"Insider Cluster Sell — {n_fv} Form 4 Filings",
                        "body": f"Multiple insiders sold net {abs(net):,} shares. Cluster selling within 30 days is a bearish signal when concentrated among senior executives.",
                        "sentiment": "neg",
                        "meta": f"Net shares: {net:,} | Filings: {n_fv}",
                    }
                )

    # 13F institutional flow from market_ctx (fetched once per scan, not per-ticker)
    inst_map = (market_ctx or {}).get("institutional_signals") or {}
    inst = inst_map.get(ticker)
    if inst:
        fund_score = inst.get("score", 0)
        result.score += fund_score
        if abs(fund_score) >= 4:
            result.sources.add("13F")
            qoq = inst.get("qoq_trend", "")
            if fund_score > 0:
                result.rationale.append(
                    {
                        "src": "13F",
                        "head": f"13F Institutional Accumulation — {qoq.title()} Trend",
                        "body": "Major funds increasing or initiating positions. Follow-the-smart-money signal from quarterly SEC 13F filings.",
                        "sentiment": "pos",
                        "meta": f"13F qoq={qoq} score={fund_score:+.0f}",
                    }
                )
            else:
                result.rationale.append(
                    {
                        "src": "13F",
                        "head": f"13F Institutional Distribution — {qoq.title()} Trend",
                        "body": "Major funds reducing or exiting positions. Early-exit signal from quarterly 13F filings.",
                        "sentiment": "neg",
                        "meta": f"13F qoq={qoq} score={fund_score:+.0f}",
                    }
                )

    return result


# ─── 5. Sentiment Worker ──────────────────────────────────────────────────────
# Scores StockTwits bull%, Reddit WSB mentions, Google Trends, and Congress trades.


@WorkerTask(name="sentiment", timeout=5.0, retries=1, cb_threshold=4, cb_reset_secs=120.0)
async def sentiment_worker(
    ticker: str,
    social: dict | None,
    trends: dict | None,
    congress: dict | None,
) -> ScoringResult:
    result = ScoringResult()

    # StockTwits bull%
    if social:
        bull_pct = social.get("bull_pct", 50)
        if bull_pct >= 70:
            result.score += 5
            result.sources.add("Social")
            result.rationale.append(
                {
                    "src": "Social",
                    "head": f"StockTwits Bullish Sentiment ({bull_pct:.0f}%)",
                    "body": f"{bull_pct:.0f}% of StockTwits messages are bullish — elevated retail conviction.",
                    "sentiment": "pos",
                    "meta": f"StockTwits bull: {bull_pct:.0f}%",
                }
            )
        elif bull_pct <= 30:
            result.score -= 5
            result.sources.add("Social")
            result.rationale.append(
                {
                    "src": "Social",
                    "head": f"StockTwits Bearish Sentiment ({bull_pct:.0f}%)",
                    "body": f"Only {bull_pct:.0f}% bullish on StockTwits. Retail fear elevated.",
                    "sentiment": "neg",
                    "meta": f"StockTwits bull: {bull_pct:.0f}%",
                }
            )

        wsb_v = social.get("wsb_mentions_velocity", 0)
        if wsb_v > 2.0:
            result.score += min(8, round(wsb_v * 3))
            result.sources.add("Social")
            result.rationale.append(
                {
                    "src": "Social",
                    "head": f"Reddit WSB Mention Surge ({wsb_v:.1f}× velocity)",
                    "body": f"WallStreetBets mentions growing at {wsb_v:.1f}× usual rate. Retail momentum building.",
                    "sentiment": "pos",
                    "meta": f"WSB velocity: {wsb_v:.1f}×",
                }
            )

    # Google Trends
    if trends:
        trend_score = trends.get("score", 0)
        if abs(trend_score) >= 3:
            result.score += trend_score
            result.sources.add("Social")

    # Congress trades (Quiver Quant)
    if congress:
        c_score = congress.get("score", 0)
        if abs(c_score) >= 4:
            result.score += c_score
            result.sources.add("Congress")
            direction = "buying" if c_score > 0 else "selling"
            result.rationale.append(
                {
                    "src": "Congress",
                    "head": f"Congress {direction.capitalize()} {ticker}",
                    "body": f"Congressional trading activity detected ({direction}). Historically carries 12–15% annualised alpha vs S&P.",
                    "sentiment": "pos" if c_score > 0 else "neg",
                    "meta": f"congress_score={c_score:+.0f}",
                }
            )

    return result


# ─── Worker registry (for admin rate-limit dashboard) ─────────────────────────

ALL_WORKERS = [news_worker, fundamentals_worker, options_worker, institutional_worker, sentiment_worker]
