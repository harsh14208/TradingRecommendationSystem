import asyncio
import time

from fastapi import APIRouter
from services.aaii import get_aaii_sentiment
from services.breadth import get_market_breadth
from services.cot import get_cot_signal
from services.fear_greed import get_fear_greed, get_put_call_ratio
from services.macro import get_macro_context
from services.news import get_api_usage

router = APIRouter(prefix="/api/market", tags=["market"])

# Market context changes at most every few minutes — cache for 5 minutes so
# page loads don't each fire 6 concurrent external HTTP calls. A partial/failed
# fetch (e.g. transient yfinance treasury/VIX miss) is cached only briefly so the
# Market dashboard self-heals instead of pinning empty cards for the full window.
_CTX_TTL = 300  # seconds
_CTX_PARTIAL_TTL = 45  # seconds — short retry when macro came back incomplete
_ctx_cache: dict = {"data": None, "ts": 0.0, "ttl": _CTX_TTL}


@router.get("/context")
async def market_context():
    now = time.monotonic()
    if _ctx_cache["data"] and (now - _ctx_cache["ts"]) < _ctx_cache.get("ttl", _CTX_TTL):
        return _ctx_cache["data"]

    from services.macro_regime import get_macro_regime

    fg, macro, pc, breadth, aaii, cot, hmm = await asyncio.gather(
        get_fear_greed(),
        get_macro_context(),
        get_put_call_ratio(),
        get_market_breadth(),
        get_aaii_sentiment(),
        get_cot_signal(),
        get_macro_regime(),
        return_exceptions=True,
    )
    result = {
        "fear_greed": fg if not isinstance(fg, Exception) else None,
        "macro": macro if not isinstance(macro, Exception) else None,
        "put_call": pc if not isinstance(pc, Exception) else None,
        "breadth": breadth if not isinstance(breadth, Exception) else None,
        "aaii": aaii if not isinstance(aaii, Exception) else None,
        "cot": cot if not isinstance(cot, Exception) else None,
        "hmm_regime": hmm if not isinstance(hmm, Exception) else None,
        "api_usage": get_api_usage(),
    }
    # A healthy macro fetch always includes the 10Y treasury yield; if it's
    # missing the upstream fetch degraded — keep the result but retry soon.
    macro_ok = isinstance(macro, dict) and macro.get("t10y") is not None
    _ctx_cache["data"] = result
    _ctx_cache["ts"] = now
    _ctx_cache["ttl"] = _CTX_TTL if macro_ok else _CTX_PARTIAL_TTL
    return result


@router.get("/regime")
async def macro_regime():
    """
    2-state Gaussian HMM macro regime classification.
    Returns bull/bear/transition label with probabilities and transition risk.
    Results are cached for 1 hour — refit happens in background.
    """
    from services.macro_regime import get_macro_regime

    return await get_macro_regime()


@router.post("/regime/invalidate")
async def invalidate_regime_cache():
    """Force the HMM to refit on next /regime call (use after major macro events)."""
    from services.macro_regime import invalidate_cache

    invalidate_cache()
    return {"ok": True, "message": "Regime cache invalidated — will refit on next request"}


@router.get("/supply-chain")
async def supply_chain():
    """
    Alternative supply chain data: Baltic Dry Index momentum + shipping signals.
    Sector impact map for logistics/commodities/retail tickers.
    """
    from services.supply_chain import get_supply_chain_signals

    return await get_supply_chain_signals()


@router.get("/dark-pool/reconstructed")
async def dark_pool_reconstructed(ticker: str = ""):
    """
    Reconstructed dark pool institutional orders for a ticker (or all tickers).
    Groups fragmented tape prints by time/price proximity and applies tick rule for direction.
    """
    from services.dark_pool import get_reconstructed_orders

    return await get_reconstructed_orders(ticker.upper() if ticker else None)


@router.get("/events")
async def corporate_events_endpoint():
    """
    Upcoming corporate events (Wall Street Horizon via Massive):
    earnings, investor conferences, analyst days, dividends, splits, buybacks.
    4-hour cache.
    """
    from services.corporate_events import get_corporate_events

    return await get_corporate_events()


@router.get("/etf-flows")
async def etf_flows_endpoint():
    """
    ETF fund flow data for all 11 sector ETFs.
    Massive Partners API with volume-proxy fallback.
    4-hour cache.
    """
    from services.etf_flows import get_etf_flows

    return await get_etf_flows()


@router.get("/etf-constituents/{etf}")
async def etf_constituents_endpoint(etf: str):
    """
    Top-50 holdings for a sector ETF with portfolio weights.
    Massive Partners ETF Constituents API. 24-hour cache.
    """
    from services.etf_constituents import get_etf_constituents

    return await get_etf_constituents(etf.upper())


@router.get("/economy")
async def economy_endpoint():
    """
    Treasury yields, inflation (CPI/PCE), and labor market data from Massive Economy API.
    Augments/replaces FRED data. 1-hour cache.
    """
    from services.massive_economy import get_economy_data

    return await get_economy_data()


@router.get("/analyst/{ticker}")
async def analyst_intelligence_endpoint(ticker: str):
    """
    Bulls Bears Say, consensus ratings, and corporate guidance for a ticker.
    Massive Partners API. 6-hour cache.
    """
    from services.massive_analyst import get_analyst_intelligence

    return await get_analyst_intelligence(ticker.upper())


@router.get("/8k/{ticker}")
async def eightk_events_endpoint(ticker: str):
    """
    Recent 8-K material events for a ticker: M&A, CEO changes, guidance, agreements.
    Massive Stocks API. 2-hour cache.
    """
    from services.eightk_events import get_8k_signals

    return await get_8k_signals(ticker.upper())


@router.get("/options/{ticker}")
async def option_chain_endpoint(ticker: str, price: float = 0.0):
    """
    Full option chain analysis: net GEX, 25-delta skew, max pain strike.
    Massive Options API. 15-minute cache.
    """
    from services.massive_options import get_option_chain_signals

    return await get_option_chain_signals(ticker.upper(), price)


# In-memory cache for ticker → sector lookups. yfinance info calls are slow and
# we don't want the dashboard card to re-hit them on every signal click.
_ticker_sector_cache: dict[str, dict] = {}


@router.get("/sector/{ticker}")
async def ticker_sector_endpoint(ticker: str):
    """
    Resolve a single ticker's SPDR sector ETF and current performance.

    1. Uses the static SECTOR_MAP for known names.
    2. Falls back to yfinance company info for unknown tickers.
    3. Returns the matching sector ETF performance from the sector heatmap.

    The result is cached per ticker for 1 hour to keep the dashboard snappy.
    """
    from routers.quotes import _SECTOR_META, sector_heatmap
    from services.market_data import _session
    from services.sector import SECTOR_MAP, YFINANCE_TO_ETF

    ticker = ticker.upper()
    now = time.monotonic()
    cached = _ticker_sector_cache.get(ticker)
    if cached and (now - cached.get("_ts", 0)) < 3600:
        return {k: v for k, v in cached.items() if not k.startswith("_")}

    etf = SECTOR_MAP.get(ticker)

    if not etf:
        try:
            import yfinance as yf

            info = yf.Ticker(ticker, session=_session).info or {}
            sector = info.get("sector") or info.get("sectorDisp") or ""
            etf = YFINANCE_TO_ETF.get(sector)
        except Exception:
            etf = None

    if not etf:
        return {"ticker": ticker, "etf": None, "name": None}

    sectors = await sector_heatmap()
    sec = next((s for s in sectors if s.get("etf") == etf), None)
    if sec is None:
        meta = _SECTOR_META.get(etf, {"name": etf, "weight": 2.0})
        sec = {
            "etf": etf,
            "name": meta["name"],
            "weight": meta["weight"],
            "ret_1d": None,
            "ret_1w": None,
            "ret_1m": None,
            "ret_3m": None,
            "ret_ytd": None,
            "flow_1w": 0,
        }

    rank = next((i for i, s in enumerate(sectors) if s.get("etf") == etf), -1) + 1
    result = {
        "ticker": ticker,
        **sec,
        "rank": rank,
        "total": len(sectors),
    }
    _ticker_sector_cache[ticker] = {**result, "_ts": now}
    return result
