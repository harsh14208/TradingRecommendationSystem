import os
import logging
import aiohttp
import pandas as pd
from datetime import datetime, timedelta

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
    end_dt = datetime.utcnow()
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
                # Convert ms timestamp to datetime and set as index
                df["Datetime"] = pd.to_datetime(df["t"], unit="ms", utc=True)
                # Convert to ET timezone exactly like yfinance does by default
                df["Datetime"] = df["Datetime"].dt.tz_convert("America/New_York")
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


async def get_polygon_weekly_bars(ticker: str, weeks: int = 26) -> pd.DataFrame | None:
    """
    Fetch the last `weeks` weekly OHLCV bars from Polygon.io (free tier).
    Used for weekly trend strength confirmation — reduces false signals in
    choppy markets that look bullish on daily but not on weekly timeframe.
    Returns DataFrame with columns Open/High/Low/Close/Volume, or None on error.
    """
    api_key = _get_api_key()
    if not api_key:
        return None

    end_dt   = datetime.utcnow()
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
                df["Datetime"] = pd.to_datetime(df["t"], unit="ms", utc=True)
                df.set_index("Datetime", inplace=True)
                df.rename(columns={"o": "Open", "h": "High", "l": "Low",
                                   "c": "Close", "v": "Volume"}, inplace=True)
                return df[["Open", "High", "Low", "Close", "Volume"]].tail(weeks)
    except Exception as e:
        log.warning(f"[polygon] weekly bars {ticker}: {e}")
        return None