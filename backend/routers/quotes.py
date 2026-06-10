import asyncio
import logging
import re

from config import TIERS, get_settings
from fastapi import APIRouter, Depends, HTTPException, Response
from models import User
from services.auth_svc import get_current_user
from services.breadth import get_market_breadth
from services.fear_greed import get_fear_greed, get_put_call_ratio
from services.market_data import get_history, get_quotes

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["quotes"])

# Polygon and Finnhub free-tier terms prohibit commercial redistribution of
# raw OHLCV and real-time price data. All chart endpoints require a paid
# subscription so the data is only accessible to licensed subscribers.
_DATA_LICENSE_HEADER = (
    "Data sourced from Polygon.io and yfinance under their respective free-tier "
    "terms. Not for redistribution. Signal.Trade redistributes derived signals "
    "(confidence scores) under a commercial subscription licence."
)


def _require_basic(user: User):
    """Raise 402 if user is on free tier — raw OHLCV requires Basic subscription."""
    if user.is_owner:
        return
    tier_idx = TIERS.index(user.subscription_tier or "free")
    if tier_idx < TIERS.index("basic") or user.subscription_status != "active":
        raise HTTPException(
            status_code=402,
            detail="Raw chart data requires a Basic subscription. "
            "Upgrade at /app#pricing to access interactive charts.",
        )


SECTOR_ETFS = ["XLK", "XLF", "XLY", "XLC", "XLV", "XLP", "XLE", "XLI", "XLB", "XLRE", "XLU"]


@router.get("/quotes")
async def ticker_tape():
    settings = get_settings()
    return await get_quotes(settings.tickers)


@router.get("/chart/{ticker}")
async def chart_data(
    ticker: str,
    response: Response,
    period: str = "3mo",
    user: User = Depends(get_current_user),
):
    _require_basic(user)
    if response:
        response.headers["X-Data-License"] = _DATA_LICENSE_HEADER

    valid_periods = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"}
    period = period if period in valid_periods else "3mo"
    interval = "5m" if period == "1d" else "1h" if period == "5d" else "1d"

    df = await get_history(ticker.upper(), period=period, interval=interval)
    if df is None:
        return []

    return [
        {
            "date": idx.strftime("%Y-%m-%d %H:%M"),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        }
        for idx, row in df.iterrows()
    ]


@router.get("/chart/{ticker}/relative")
async def relative_chart(
    ticker: str,
    response: Response,
    period: str = "3mo",
    versus: str = "SPY",
    user: User = Depends(get_current_user),
):
    """Return ticker and benchmark normalised to 100 at start — for relative performance overlay."""
    _require_basic(user)
    if response:
        response.headers["X-Data-License"] = _DATA_LICENSE_HEADER

    valid_periods = {"1mo", "3mo", "6mo", "1y", "2y"}
    period = period if period in valid_periods else "3mo"

    ticker_df, bench_df = await asyncio.gather(
        get_history(ticker.upper(), period=period, interval="1d"),
        get_history(versus.upper(), period=period, interval="1d"),
    )
    if ticker_df is None or bench_df is None or ticker_df.empty or bench_df.empty:
        return {"ticker": [], "bench": [], "versus": versus}

    def normalise(df):
        closes = df["Close"].astype(float)
        base = float(closes.iloc[0])
        return [
            {"date": idx.strftime("%Y-%m-%d"), "value": round((float(v) / base - 1) * 100, 3)}
            for idx, v in closes.items()
        ]

    return {"ticker": normalise(ticker_df), "bench": normalise(bench_df), "versus": versus}


@router.get("/market/overview")
async def market_overview():
    """
    Fetch a full market overview dashboard from various sources.
    This acts as a backend health check by touching multiple data services.
    """
    try:

        def _fetch_massive_indices():
            import os
            from datetime import datetime, timedelta

            try:
                from massive import RESTClient
            except ImportError:
                raise ImportError("massive-api-client is not installed. Run: pip install massive-api-client")

            api_key = os.getenv("MASSIVE_API_KEY")
            if not api_key:
                raise ValueError("MASSIVE_API_KEY not found in .env")

            client = RESTClient(api_key)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            def process_aggs(ticker):
                try:
                    aggs = list(
                        client.list_aggs(
                            ticker, 1, "day", start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), limit=50
                        )
                    )
                    if not aggs or len(aggs) < 2:
                        return None
                    closes = [a.close for a in aggs]
                    latest, prev = closes[-1], closes[-2]
                    return {
                        "value": latest,
                        "change": latest - prev,
                        "change_pct": (latest - prev) / prev * 100,
                        "history": closes,
                    }
                except Exception:
                    return None

            return {
                "spx": process_aggs("I:SPX"),
                "ndx": process_aggs("I:NDX"),
                "vix": process_aggs("I:VIX"),
                "dxy": process_aggs("I:DXY"),
            }

        # Fetch Massive data and other web-scraped indicators concurrently
        massive_task = asyncio.to_thread(_fetch_massive_indices)

        massive_res, tnx_df, fg, pc, breadth = await asyncio.gather(
            massive_task,
            get_history("^TNX", period="1mo", interval="1d"),  # 10Y Yield
            get_fear_greed(),
            get_put_call_ratio(),
            get_market_breadth(),
            return_exceptions=True,
        )

        def process_df(df):
            if isinstance(df, Exception) or df is None or df.empty or len(df) < 2:
                return None
            closes = df["Close"].astype(float)
            latest, prev = closes.iloc[-1], closes.iloc[-2]
            change = latest - prev
            change_pct = (change / prev) * 100 if prev != 0 else 0
            return {"value": latest, "change": change, "change_pct": change_pct, "history": closes.tolist()}

        if isinstance(massive_res, Exception):
            logging.getLogger(__name__).error(f"Massive API Error: {massive_res}")
            massive_res = {}  # Fallback to empty if Massive fails, so other cards still load

        overview = {
            "spx": massive_res.get("spx"),
            "ndx": massive_res.get("ndx"),
            "vix": massive_res.get("vix"),
            "dxy": massive_res.get("dxy"),
            "yield_10y": process_df(tnx_df),
            "fear_greed": None
            if isinstance(fg, Exception) or fg is None
            else {"score": fg.get("score"), "label": fg.get("label"), "history": fg.get("history", [])},
            "put_call_ratio": None
            if isinstance(pc, Exception) or pc is None
            else {"ratio": pc.get("ratio"), "history": pc.get("history", [])},
            "breadth": None if isinstance(breadth, Exception) or breadth is None else breadth,
        }

        # Filter out any failed data fetches. The boolean logic here is critical:
        # the `v is not None` check must apply before any `v.get()` calls to
        # prevent an AttributeError if a data source returned None or an exception.
        successful_data = {
            k: v
            for k, v in overview.items()
            if v is not None
            and (
                v.get("value") is not None
                or v.get("score") is not None
                or v.get("ratio") is not None
                or v.get("pct_above_200d") is not None
            )
        }
        if not successful_data:
            raise HTTPException(status_code=503, detail="Market overview data sources are currently unavailable.")
        return successful_data

    except Exception as e:
        logging.getLogger(__name__).error(f"Error in market_overview endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching market overview.")


@router.get("/massive/endpoints")
async def massive_endpoints():
    """Fetch the llms.txt index to expose all Massive functionalities."""
    import re

    import aiohttp

    async with aiohttp.ClientSession() as session:
        async with session.get("https://massive.com/docs/rest/llms.txt") as resp:
            if resp.status != 200:
                return [
                    {
                        "name": "Error",
                        "endpoints": [
                            {
                                "name": "Failed to fetch llms.txt",
                                "url": "",
                                "description": "Could not reach massive.com",
                            }
                        ],
                    }
                ]
            text = await resp.text()

    categories = []
    current_cat = None

    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("## "):
            current_cat = {"name": line[3:].strip(), "endpoints": []}
            categories.append(current_cat)
        elif line.startswith("- [") and current_cat is not None:
            match = re.match(r"- \[(.+?)\]\((.+?)\):\s*(.*)", line)
            if match:
                name, url, desc = match.groups()
                current_cat["endpoints"].append({"name": name, "url": url, "description": desc})
    return categories


_MASSIVE_SAFE_ENDPOINTS = {
    re.compile(r"^v\d+/reference/tickers/[A-Z0-9]+$"),
    re.compile(r"^v\d+/reference/dividends/[A-Z0-9]+$"),
    re.compile(r"^v\d+/reference/splits/[A-Z0-9]+$"),
    re.compile(r"^v\d+/reference/news$"),
    re.compile(r"^v\d+/aggs/ticker/[A-Z0-9:.]+/range/\d+/\w+/\d{4}-\d{2}-\d{2}/\d{4}-\d{2}-\d{2}$"),
    re.compile(r"^v\d+/snapshot/locale/us/markets/stocks/tickers$"),
    re.compile(r"^v\d+/snapshot/locale/us/markets/stocks/tickers/[A-Z0-9:.]+$"),
    re.compile(r"^v\d+/indicators/[a-z]+$"),
}


def _is_safe_endpoint(endpoint: str) -> bool:
    normalized = endpoint.lstrip("/")
    return any(pattern.match(normalized) for pattern in _MASSIVE_SAFE_ENDPOINTS)


@router.post("/massive/proxy")
async def massive_proxy(
    payload: dict,
    user: User = Depends(get_current_user),
):
    """Generic proxy to call specific allowed Massive/Polygon REST API endpoints."""
    import os

    import aiohttp

    if not user.is_owner:
        raise HTTPException(403, detail="Owner access required")

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        raise HTTPException(503, "MASSIVE_API_KEY not set")

    endpoint = payload.get("endpoint", "").lstrip("/")
    method = payload.get("method", "GET")
    params = payload.get("params", {})

    if not _is_safe_endpoint(endpoint):
        raise HTTPException(400, detail="Endpoint not in allowlist")

    import ssl

    import certifi

    url = f"https://api.polygon.io/{endpoint}"
    params["apiKey"] = api_key
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())

    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, params=params, ssl=ssl_ctx) as resp:
            try:
                data = await resp.json()
            except Exception:
                data = {"text": await resp.text()}
            return {"status": resp.status, "data": data}


_sector_cache: dict = {"data": None, "ts": 0}


def _ret(closes, days: int) -> float | None:
    """Return % change over the last `days` trading days, or None if insufficient data."""
    if closes is None or len(closes) < 2:
        return None
    n = min(days, len(closes) - 1)
    base = float(closes.iloc[-n - 1])
    if base == 0:
        return None
    return round((float(closes.iloc[-1]) / base - 1) * 100, 2)


def _ytd_ret(df) -> float | None:
    """Return % change from the first trading day of the current calendar year."""
    if df is None or df.empty:
        return None
    from datetime import date

    jan1 = date.today().replace(month=1, day=1)
    ytd_df = df[df.index.date >= jan1]  # type: ignore[attr-defined]
    if ytd_df.empty or len(ytd_df) < 2:
        return None
    base = float(ytd_df["Close"].iloc[0])
    if base == 0:
        return None
    return round((float(ytd_df["Close"].iloc[-1]) / base - 1) * 100, 2)


@router.get("/market/sectors")
async def sector_heatmap():
    """Return multi-timeframe performance for all SPDR sector ETFs (batch fetched, 1hr cache)."""
    now = asyncio.get_running_loop().time()
    if _sector_cache["data"] is not None and now - _sector_cache["ts"] < 3600:
        return _sector_cache["data"]

    from services.market_data import get_histories_batch

    try:
        histories = await asyncio.wait_for(get_histories_batch(SECTOR_ETFS, period="1y", interval="1d"), timeout=20.0)
    except asyncio.TimeoutError:
        logging.getLogger(__name__).warning("sector_heatmap: yfinance batch fetch timed out.")
        return _sector_cache["data"] or []
    except Exception as e:
        logging.getLogger(__name__).error(f"sector_heatmap: Error fetching batch histories: {e}")
        return _sector_cache["data"] or []

    out = []
    for etf in SECTOR_ETFS:
        df = histories.get(etf)
        if df is None or df.empty:
            continue
        closes = df["Close"].astype(float)
        if len(closes) < 2:
            continue
        out.append(
            {
                "etf": etf,
                "ret_1d": _ret(closes, 1),
                "ret_1w": _ret(closes, 5),
                "ret_1m": _ret(closes, 21),
                "ret_3m": _ret(closes, 63),
                "ret_ytd": _ytd_ret(df),
            }
        )

    out.sort(key=lambda x: x["ret_1m"] or 0, reverse=True)
    _sector_cache["data"] = out
    _sector_cache["ts"] = now
    return out


# FOMC decision dates (published by Fed a year in advance — update annually)
_FOMC_DATES = [
    "2025-01-29",
    "2025-03-19",
    "2025-05-07",
    "2025-06-18",
    "2025-07-30",
    "2025-09-17",
    "2025-10-29",
    "2025-12-10",
    "2026-01-28",
    "2026-03-18",
    "2026-05-06",
    "2026-06-17",
    "2026-07-29",
    "2026-09-16",
    "2026-10-28",
    "2026-12-09",
]

# FRED release IDs → enriched metadata
# release_id: FRED numeric ID; impact: HIGH/MEDIUM/LOW; time: ET release time
_FRED_RELEASES: dict[int, dict] = {
    10: {
        "label": "CPI",
        "name": "Consumer Price Index",
        "color": "#f59e0b",
        "time": "8:30 AM ET",
        "impact": "HIGH",
        "desc": "Measures change in prices paid by consumers for goods and services. "
        "The Fed's primary inflation gauge alongside PCE. "
        "Hot print → rates stay higher for longer → equities fall.",
    },
    50: {
        "label": "NFP",
        "name": "Non-Farm Payrolls",
        "color": "#60a5fa",
        "time": "8:30 AM ET",
        "impact": "HIGH",
        "desc": "Monthly change in employment excluding farm workers. "
        "Strongest of the monthly labour reports. "
        "Strong jobs → Fed hawkish → yields rise → growth stocks under pressure.",
    },
    19: {
        "label": "PCE",
        "name": "PCE Price Index",
        "color": "#a78bfa",
        "time": "8:30 AM ET",
        "impact": "HIGH",
        "desc": "Personal Consumption Expenditures price index — the Fed's preferred "
        "inflation measure (broader basket than CPI, chain-weighted). "
        "Directly drives FOMC rate decisions.",
    },
    25: {
        "label": "PPI",
        "name": "Producer Price Index",
        "color": "#fb923c",
        "time": "8:30 AM ET",
        "impact": "MEDIUM",
        "desc": "Measures change in selling prices received by domestic producers. "
        "Leading indicator of consumer inflation — PPI pressures eventually pass through to CPI.",
    },
    108: {
        "label": "RETAIL",
        "name": "Retail Sales",
        "color": "#34d399",
        "time": "8:30 AM ET",
        "impact": "MEDIUM",
        "desc": "Monthly change in total sales at retail stores. "
        "Proxy for consumer spending (~70% of GDP). "
        "Beat → growth optimism → cyclical stocks outperform.",
    },
    175: {
        "label": "GDP",
        "name": "GDP (Advance Estimate)",
        "color": "#38bdf8",
        "time": "8:30 AM ET",
        "impact": "HIGH",
        "desc": "First estimate of quarterly GDP growth. "
        "Revised twice over the following two months. "
        "Miss → recession fears → defensive rotation.",
    },
}

_cal_cache: dict = {"data": None, "ts": 0}


@router.get("/market/calendar")
async def economic_calendar():
    """Return upcoming economic events with enriched metadata (time, impact, description)."""
    import ssl
    import time

    import aiohttp
    import certifi

    now = time.time()
    if _cal_cache["data"] is not None and now - _cal_cache["ts"] < 3600 * 12:
        return _cal_cache["data"]

    from datetime import date, timedelta

    today = date.today()
    end = (today + timedelta(days=180)).isoformat()
    today_s = today.isoformat()

    # FOMC hardcoded (most reliable — published a year in advance)
    events: list[dict] = [
        {
            "date": d,
            "label": "FOMC",
            "name": "FOMC Rate Decision",
            "color": "#ef4444",
            "time": "2:00 PM ET",
            "impact": "HIGH",
            "desc": "Federal Open Market Committee announces the federal funds rate target. "
            "Market-moving for ALL asset classes. Press conference at 2:30 PM ET. "
            "Dot plot + Summary of Economic Projections released at quarterly meetings.",
        }
        for d in _FOMC_DATES
        if today_s <= d <= end
    ]

    settings = get_settings()
    if settings.fred_api_key:
        ctx = ssl.create_default_context(cafile=certifi.where())

        # Share one session across all FRED requests — avoids 6 TCP handshakes
        async def fetch_all_releases():
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ctx)) as session:

                async def fetch_one(release_id: int, meta: dict):
                    url = (
                        f"https://api.stlouisfed.org/fred/release/dates"
                        f"?release_id={release_id}&realtime_start={today_s}&realtime_end={end}"
                        f"&include_release_dates_with_no_data=true"
                        f"&api_key={settings.fred_api_key}&file_type=json"
                    )
                    try:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                            if r.status == 200:
                                d = await r.json()
                                for item in d.get("release_dates") or []:
                                    dt = item.get("date")
                                    if dt:
                                        events.append(
                                            {
                                                "date": dt,
                                                "label": meta["label"],
                                                "name": meta["name"],
                                                "color": meta["color"],
                                                "time": meta["time"],
                                                "impact": meta["impact"],
                                                "desc": meta["desc"],
                                            }
                                        )
                    except Exception:
                        pass

                await asyncio.gather(*[fetch_one(rid, m) for rid, m in _FRED_RELEASES.items()])

        await fetch_all_releases()

    events.sort(key=lambda e: e["date"])
    _cal_cache["data"] = events
    _cal_cache["ts"] = now
    return events


_detail_cache: dict = {"data": None, "ts": 0}


@router.get("/market/sectors/detail")
async def sector_detail():
    """
    Each sector ETF with 1-month return + all watchlist/DB stocks in that sector,
    sorted by their individual 1-month performance.
    """
    import time

    from database import AsyncSessionLocal
    from models import Signal, WatchlistItem
    from services.market_data import get_histories_batch
    from services.sector import SECTOR_MAP, YFINANCE_TO_ETF
    from sqlalchemy import desc, select

    now = time.time()
    if _detail_cache["data"] is not None and now - _detail_cache["ts"] < 1800:
        return _detail_cache["data"]

    settings = get_settings()

    # 1. Sector ETF performances
    etf_perf = {s["etf"]: s["ret_1m"] for s in await sector_heatmap()}

    # 2. Watchlist tickers
    try:
        async with AsyncSessionLocal() as db:
            wl_rows = (await db.execute(select(WatchlistItem).where(WatchlistItem.is_active == True))).scalars().all()
            tickers = [r.ticker for r in wl_rows] if wl_rows else settings.tickers

            # Latest signal per ticker for action/confidence
            sig_rows = (
                (
                    await db.execute(
                        select(Signal)
                        .where(Signal.ticker.in_(tickers))
                        .where(Signal.is_active == True)
                        .order_by(desc(Signal.created_at))
                    )
                )
                .scalars()
                .all()
            )
    except Exception:
        tickers = settings.tickers
        sig_rows = []

    latest_sig: dict = {}
    for s in sig_rows:
        if s.ticker not in latest_sig:
            latest_sig[s.ticker] = s

    # 3. Batch 1-month history for all tickers
    histories = await get_histories_batch(tickers, period="1mo", interval="1d")

    # 4. Determine sector for each ticker; build stock list
    # For unknowns not in SECTOR_MAP try yfinance info['sector']
    unknown = [t for t in tickers if t not in SECTOR_MAP]
    yf_sectors: dict[str, str] = {}
    if unknown:
        try:
            import yfinance as yf
            from services.market_data import _session

            for t in unknown:
                try:
                    info = yf.Ticker(t, session=_session).info or {}
                    yf_sec = info.get("sector") or info.get("sectorDisp") or ""
                    etf = YFINANCE_TO_ETF.get(yf_sec)
                    if etf:
                        yf_sectors[t] = etf
                except Exception:
                    pass
        except Exception:
            pass

    # 5. Build per-sector stock list
    sector_stocks: dict[str, list] = {etf: [] for etf in SECTOR_ETFS}
    uncategorised: list = []

    for ticker in tickers:
        df = histories.get(ticker)
        ret_1m = None
        if df is not None and not df.empty and len(df) >= 2:
            closes = df["Close"].astype(float)
            ret_1m = round((float(closes.iloc[-1]) / float(closes.iloc[0]) - 1) * 100, 2)

        sig = latest_sig.get(ticker)
        stock = {
            "ticker": ticker,
            "company": sig.company if sig else ticker,
            "ret_1m": ret_1m,
            "action": sig.action if sig else None,
            "confidence": sig.confidence if sig else None,
            "price": sig.price if sig else None,
        }

        etf = SECTOR_MAP.get(ticker) or yf_sectors.get(ticker)
        if etf and etf in sector_stocks:
            sector_stocks[etf].append(stock)
        else:
            uncategorised.append(stock)

    # 6. Assemble result — all 11 sectors even if empty
    SECTOR_NAMES = {
        "XLK": "Technology",
        "XLF": "Financials",
        "XLY": "Consumer Discretionary",
        "XLC": "Communication Services",
        "XLV": "Healthcare",
        "XLP": "Consumer Staples",
        "XLE": "Energy",
        "XLI": "Industrials",
        "XLB": "Materials",
        "XLRE": "Real Estate",
        "XLU": "Utilities",
    }

    result = []
    for etf in SECTOR_ETFS:
        stocks = sector_stocks[etf]
        stocks.sort(key=lambda s: (s["ret_1m"] is None, -(s["ret_1m"] or 0)))
        result.append(
            {
                "etf": etf,
                "name": SECTOR_NAMES.get(etf, etf),
                "ret_1m": etf_perf.get(etf),
                "stocks": stocks,
            }
        )

    result.sort(key=lambda x: (x["ret_1m"] is None, -(x["ret_1m"] or 0)))

    if uncategorised:
        result.append(
            {
                "etf": "OTHER",
                "name": "Other / Unclassified",
                "ret_1m": None,
                "stocks": uncategorised,
            }
        )

    _detail_cache["data"] = result
    _detail_cache["ts"] = now
    return result


_sector_stocks_cache: dict[str, tuple[list, float]] = {}


@router.get("/market/sectors/{etf}/stocks")
async def sector_stocks(etf: str):
    """
    All stocks in a given sector ETF with 1-month returns and latest signal.
    Fetched on-demand and cached per sector for 30 minutes.
    """
    import time

    from database import AsyncSessionLocal
    from models import Signal
    from services.market_data import get_histories_batch
    from services.sector import SECTOR_MAP
    from sqlalchemy import desc, select

    etf = etf.upper()
    cached = _sector_stocks_cache.get(etf)
    if cached and time.time() - cached[1] < 1800:
        return cached[0]

    # All tickers in this sector
    tickers = [t for t, e in SECTOR_MAP.items() if e == etf]
    if not tickers:
        return []

    # Batch 1-month history (one HTTP call for all tickers)
    histories = await get_histories_batch(tickers, period="1mo", interval="1d")

    # Latest active signal per ticker for action/confidence/price
    try:
        async with AsyncSessionLocal() as db:
            sig_rows = (
                (
                    await db.execute(
                        select(Signal)
                        .where(Signal.ticker.in_(tickers))
                        .where(Signal.is_active == True)
                        .order_by(desc(Signal.created_at))
                    )
                )
                .scalars()
                .all()
            )
    except Exception:
        sig_rows = []

    latest_sig: dict = {}
    for s in sig_rows:
        if s.ticker not in latest_sig:
            latest_sig[s.ticker] = s

    from services.market_data import COMPANY_NAMES

    result = []
    for ticker in tickers:
        df = histories.get(ticker)
        ret_1m = None
        if df is not None and not df.empty and len(df) >= 2:
            closes = df["Close"].astype(float)
            ret_1m = round((float(closes.iloc[-1]) / float(closes.iloc[0]) - 1) * 100, 2)

        sig = latest_sig.get(ticker)
        result.append(
            {
                "ticker": ticker,
                "company": (sig.company if sig and sig.company else None) or COMPANY_NAMES.get(ticker, ticker),
                "ret_1m": ret_1m,
                "action": sig.action if sig else None,
                "confidence": sig.confidence if sig else None,
                "price": sig.price if sig else None,
            }
        )

    result.sort(key=lambda s: (s["ret_1m"] is None, -(s["ret_1m"] or 0)))
    _sector_stocks_cache[etf] = (result, time.time())
    return result
