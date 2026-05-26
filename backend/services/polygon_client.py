import os
import logging
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta, timezone

log = logging.getLogger("signal.trade.polygon")

_BASE = "https://api.polygon.io"

def _get_api_key() -> str:
    """
    Resolve Polygon.io API key from env.
    Checks POLYGON_API_KEY first, then MASSIVE_API_KEY (same provider, different env var name).
    """
    return os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""


async def get_polygon_history(ticker: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame | None:
    """
    Fetch historical OHLCV data from Polygon.io.
    Returns a DataFrame identical in shape to yfinance (Open, High, Low, Close, Volume).
    """
    api_key = _get_api_key()
    if not api_key:
        return None

    # Map interval to Polygon multiplier and timespan
    if interval == "1d":
        multiplier, timespan = 1, "day"
    elif interval == "1h":
        multiplier, timespan = 1, "hour"
    elif interval == "5m":
        multiplier, timespan = 5, "minute"
    else:
        multiplier, timespan = 1, "day"

    # Map yfinance period strings to date ranges
    end_dt = datetime.now(timezone.utc).replace(tzinfo=None)
    if period == "1d":
        start_dt = end_dt - timedelta(days=2) # Extra days to ensure we get data over weekends
    elif period == "5d":
        start_dt = end_dt - timedelta(days=7)
    elif period == "1mo":
        start_dt = end_dt - timedelta(days=30)
    elif period == "3mo":
        start_dt = end_dt - timedelta(days=90)
    elif period == "6mo":
        start_dt = end_dt - timedelta(days=180)
    elif period == "1y":
        start_dt = end_dt - timedelta(days=365)
    elif period == "2y":
        start_dt = end_dt - timedelta(days=730)
    else:
        start_dt = end_dt - timedelta(days=90)

    start_str = start_dt.strftime("%Y-%m-%d")
    end_str = end_dt.strftime("%Y-%m-%d")

    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker.upper()}/range/{multiplier}/{timespan}/{start_str}/{end_str}"
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 50000,
        "apiKey": api_key
    }

    try:
        import ssl, certifi
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10, ssl=ssl_ctx) as resp:
                if resp.status != 200:
                    log.warning(f"[polygon] Error fetching {ticker}: HTTP {resp.status}")
                    return None
                data = await resp.json()
                
                results = data.get("results", [])
                if not results:
                    return pd.DataFrame()
                
                df = pd.DataFrame(results)
                df.loc[:, "Datetime"] = pd.to_datetime(df["t"], unit="ms", utc=True).dt.tz_convert("America/New_York")
                df.set_index("Datetime", inplace=True)
                
                # Rename to match yfinance output exactly
                df.rename(columns={
                    "o": "Open",
                    "h": "High",
                    "l": "Low",
                    "c": "Close",
                    "v": "Volume"
                }, inplace=True)
                
                # Return only the necessary columns in correct case
                return df[["Open", "High", "Low", "Close", "Volume"]]
    except Exception as e:
        log.warning(f"[polygon] Exception fetching {ticker}: {e}")
        return None


async def get_polygon_histories_batch(
    tickers: list[str], period: str = "1y", interval: str = "1d", concurrency: int = 20
) -> dict[str, pd.DataFrame]:
    """
    Fetch OHLCV for many tickers from Polygon/Massive first.
    Callers can fall back missing tickers to yfinance.
    """
    if not _get_api_key() or not tickers:
        return {}

    sem = asyncio.Semaphore(max(1, concurrency))

    async def _one(ticker: str):
        async with sem:
            df = await get_polygon_history(ticker, period=period, interval=interval)
            if df is not None and not df.empty and len(df) >= 2:
                return ticker, df
            return ticker, None

    results = await asyncio.gather(*[_one(t.upper()) for t in tickers], return_exceptions=True)
    out: dict[str, pd.DataFrame] = {}
    for item in results:
        if isinstance(item, Exception):
            continue
        ticker, df = item
        if df is not None:
            out[ticker] = df
    return out


async def get_polygon_quotes_batch(tickers: list[str]) -> list[dict]:
    """Return quote-like {t, p, c} rows using recent Polygon daily bars."""
    histories = await get_polygon_histories_batch(tickers, period="5d", interval="1d")
    quotes: list[dict] = []
    for ticker in tickers:
        df = histories.get(ticker.upper())
        if df is None or len(df) < 2:
            continue
        try:
            close = df["Close"].dropna()
            if len(close) < 2:
                continue
            price = float(close.iloc[-1])
            prev = float(close.iloc[-2])
            if prev <= 0:
                continue
            quotes.append({
                "t": ticker.upper(),
                "p": round(price, 2),
                "c": round((price - prev) / prev * 100, 2),
            })
        except Exception:
            continue
    return quotes


async def get_polygon_info(ticker: str) -> dict | None:
    """Fetch reference metadata available from Polygon's ticker details endpoint."""
    api_key = _get_api_key()
    if not api_key:
        return None
    url = f"{_BASE}/v3/reference/tickers/{ticker.upper()}"
    params = {"apiKey": api_key}
    try:
        import ssl, certifi
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10, ssl=ssl_ctx) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
        result = data.get("results") or {}
        if not result:
            return None
        return {
            "company": result.get("name") or ticker.upper(),
            "market_cap": result.get("market_cap"),
            "weighted_shares_outstanding": result.get("weighted_shares_outstanding"),
            "homepage_url": result.get("homepage_url"),
            "sic_description": result.get("sic_description"),
        }
    except Exception as e:
        log.debug(f"[polygon] info {ticker}: {e}")
        return None


async def get_polygon_infos_batch(tickers: list[str], concurrency: int = 20) -> dict[str, dict]:
    if not _get_api_key() or not tickers:
        return {}
    sem = asyncio.Semaphore(max(1, concurrency))

    async def _one(ticker: str):
        async with sem:
            return ticker.upper(), await get_polygon_info(ticker)

    results = await asyncio.gather(*[_one(t) for t in tickers], return_exceptions=True)
    out: dict[str, dict] = {}
    for item in results:
        if isinstance(item, Exception):
            continue
        ticker, info = item
        if info:
            out[ticker] = info
    return out


async def get_polygon_weekly_bars(ticker: str, weeks: int = 26) -> pd.DataFrame | None:
    """
    Fetch the last `weeks` weekly OHLCV bars from Polygon.io.
    Used for weekly trend strength confirmation — reduces false signals in
    choppy markets that look bullish on daily but not on weekly timeframe.
    Returns DataFrame with columns Open/High/Low/Close/Volume, or None on error.
    """
    api_key = _get_api_key()
    if not api_key:
        return None

    end_dt   = datetime.now(timezone.utc).replace(tzinfo=None)
    start_dt = end_dt - timedelta(weeks=weeks + 4)  # extra buffer for weekends/holidays
    url = (f"https://api.polygon.io/v2/aggs/ticker/{ticker.upper()}"
           f"/range/1/week/{start_dt.strftime('%Y-%m-%d')}/{end_dt.strftime('%Y-%m-%d')}")
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": api_key}

    try:
        import ssl as _ssl, certifi as _certifi
        ssl_ctx = _ssl.create_default_context(cafile=_certifi.where())
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10, ssl=ssl_ctx) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                results = data.get("results", [])
                if not results:
                    return pd.DataFrame()
                df = pd.DataFrame(results)
                df.loc[:, "Datetime"] = pd.to_datetime(df["t"], unit="ms", utc=True)
                df.set_index("Datetime", inplace=True)
                df.rename(columns={"o": "Open", "h": "High", "l": "Low",
                                   "c": "Close", "v": "Volume"}, inplace=True)
                return df[["Open", "High", "Low", "Close", "Volume"]].tail(weeks)
    except Exception as e:
        log.warning(f"[polygon] weekly bars {ticker}: {e}")
        return None
