import asyncio
import logging
import os
import time
from datetime import datetime, timedelta, timezone

import aiohttp
import pandas as pd

log = logging.getLogger("signal.trade.polygon")

_BASE = "https://api.polygon.io"

# In-process snapshot cache: keyed by ticker, value is (snap_dict, monotonic_ts).
# Populated by get_polygon_snapshot_batch(); reused by get_polygon_extended_hours()
# so a scan cycle's batch call eliminates per-ticker individual snapshot requests.
_snapshot_cache: dict[str, tuple[dict, float]] = {}
_SNAPSHOT_TTL = 300  # 5 min — one full scan cycle

# Dividend reference cache: stable data, 24 h TTL
_div_cache: dict[str, tuple[list, float]] = {}
_DIV_TTL = 86_400


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
        start_dt = end_dt - timedelta(days=2)  # Extra days to ensure we get data over weekends
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
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": api_key}

    try:
        import ssl

        import certifi

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
                df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"}, inplace=True)

                # Return only the necessary columns in correct case
                return df[["Open", "High", "Low", "Close", "Volume"]]
    except Exception as e:
        log.warning(f"[polygon] Exception fetching {ticker}: {type(e).__name__}: {e}")
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


async def get_polygon_snapshot_batch(tickers: list[str]) -> dict[str, dict]:
    """Single batch call → real-time price, change, VWAP, volume for all tickers.

    Response is under the "tickers" key (NOT "results"). Each snap is cached in
    _snapshot_cache so get_polygon_extended_hours() can reuse it without a second call.
    """
    api_key = _get_api_key()
    if not api_key or not tickers:
        return {}
    url = f"{_BASE}/v2/snapshot/locale/us/markets/stocks/tickers"
    params = {"tickers": ",".join(t.upper() for t in tickers), "apiKey": api_key}
    try:
        import ssl as _ssl

        import certifi as _certifi

        ssl_ctx = _ssl.create_default_context(cafile=_certifi.where())
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=15, ssl=ssl_ctx) as resp:
                if resp.status != 200:
                    log.warning("[polygon] snapshot batch: HTTP %s", resp.status)
                    return {}
                data = await resp.json()
        now = time.monotonic()
        out: dict[str, dict] = {}
        for snap in data.get("tickers") or []:  # NOTE: "tickers" key, NOT "results"
            t = (snap.get("ticker") or "").upper()
            if not t:
                continue
            _snapshot_cache[t] = (snap, now)
            out[t] = snap
        return out
    except Exception as e:
        log.warning("[polygon] snapshot batch error: %s", e)
        return {}


async def get_polygon_quotes_batch(tickers: list[str]) -> list[dict]:
    """Return real-time quote {t, p, c} rows via a single batch snapshot call.

    Replaces the old approach of N individual OHLCV calls. Falls back to empty
    list if Polygon is unavailable; market_data.py caller will use yfinance.
    """
    snaps = await get_polygon_snapshot_batch(tickers)
    quotes: list[dict] = []
    for ticker in tickers:
        snap = snaps.get(ticker.upper())
        if not snap:
            continue
        try:
            last_trade = snap.get("lastTrade") or {}
            prev_day = snap.get("prevDay") or {}
            price = float(last_trade.get("p") or 0)
            prev_close = float(prev_day.get("c") or 0)
            if price <= 0 or prev_close <= 0:
                continue
            quotes.append(
                {
                    "t": ticker.upper(),
                    "p": round(price, 2),
                    "c": round((price - prev_close) / prev_close * 100, 2),
                }
            )
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
        import ssl

        import certifi

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


_weekly_cache: dict[str, tuple[pd.DataFrame, float]] = {}
_WEEKLY_TTL = 43200  # 12 hours


async def get_polygon_weekly_bars(ticker: str, weeks: int = 26) -> pd.DataFrame | None:
    """
    Fetch the last `weeks` weekly OHLCV bars from Polygon.io.
    Used for weekly trend strength confirmation — reduces false signals in
    choppy markets that look bullish on daily but not on weekly timeframe.
    Returns DataFrame with columns Open/High/Low/Close/Volume, or None on error.
    """
    t = ticker.upper()
    now = time.monotonic()
    cached, ts = _weekly_cache.get(t, (None, 0.0))
    if cached is not None and now - ts < _WEEKLY_TTL:
        return cached.copy()

    api_key = _get_api_key()
    if not api_key:
        return None

    end_dt = datetime.now(timezone.utc).replace(tzinfo=None)
    start_dt = end_dt - timedelta(weeks=weeks + 4)  # extra buffer for weekends/holidays
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker.upper()}"
        f"/range/1/week/{start_dt.strftime('%Y-%m-%d')}/{end_dt.strftime('%Y-%m-%d')}"
    )
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": api_key}

    try:
        import ssl as _ssl

        import certifi as _certifi

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
                df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"}, inplace=True)
                df_out = df[["Open", "High", "Low", "Close", "Volume"]].tail(weeks)
                _weekly_cache[t] = (df_out, time.monotonic())
                return df_out.copy()
    except Exception as e:
        log.warning(f"[polygon] weekly bars {ticker}: {e}")
        return None


async def get_polygon_extended_hours(ticker: str) -> dict | None:
    """Return extended-hours stats. Checks _snapshot_cache first (populated by
    get_polygon_snapshot_batch during scan), falling back to an individual call.
    """
    api_key = _get_api_key()
    if not api_key:
        return None

    t = ticker.upper()
    snap_cached, ts = _snapshot_cache.get(t, (None, 0.0))
    if snap_cached is not None and time.monotonic() - ts < _SNAPSHOT_TTL:
        t_data = snap_cached
    else:
        url = f"{_BASE}/v2/snapshot/locale/us/markets/stocks/tickers/{t}"
        params = {"apiKey": api_key}
        try:
            import ssl as _ssl

            import certifi as _certifi

            ssl_ctx = _ssl.create_default_context(cafile=_certifi.where())
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10, ssl=ssl_ctx) as resp:
                    if resp.status != 200:
                        log.debug("[polygon] snapshot %s: HTTP %s", t, resp.status)
                        return None
                    data = await resp.json()
            t_data = data.get("ticker") or {}
            _snapshot_cache[t] = (t_data, time.monotonic())
        except Exception as e:
            log.debug("[polygon] extended_hours %s: %s", t, e)
            return None

    last_trade = t_data.get("lastTrade") or {}
    prev_day = t_data.get("prevDay") or {}
    min_data = t_data.get("min") or {}

    ext_price = last_trade.get("p")
    prev_close = prev_day.get("c")
    if not ext_price or not prev_close:
        return None

    ext_price = float(ext_price)
    prev_close = float(prev_close)
    gap_pct = round((ext_price - prev_close) / prev_close * 100, 3)
    direction = "up" if gap_pct > 0.1 else "down" if gap_pct < -0.1 else "flat"
    ext_volume = int(min_data.get("v") or 0)

    return {
        "price": ext_price,
        "prev_close": prev_close,
        "gap_pct": gap_pct,
        "vol_ratio": 1.0,
        "direction": direction,
        "ext_volume": ext_volume,
    }


async def get_polygon_dividends(ticker: str) -> list[dict]:
    """Fetch upcoming ex-dividend dates from Polygon reference API.

    Returns list of {ex_dividend_date, cash_amount, pay_date, frequency},
    sorted ascending by ex_dividend_date (nearest first).
    Cached 24 h per ticker — dividend schedules are stable intraday.
    """
    api_key = _get_api_key()
    if not api_key:
        return []
    t = ticker.upper()
    cached, ts = _div_cache.get(t, (None, 0.0))
    if cached is not None and time.monotonic() - ts < _DIV_TTL:
        return cached
    url = f"{_BASE}/v3/reference/dividends"
    params = {"ticker": t, "limit": 5, "order": "desc", "sort": "ex_dividend_date", "apiKey": api_key}
    try:
        import ssl as _ssl

        import certifi as _certifi

        ssl_ctx = _ssl.create_default_context(cafile=_certifi.where())
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10, ssl=ssl_ctx) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
        results = [
            {
                "ex_dividend_date": r.get("ex_dividend_date"),
                "cash_amount": r.get("cash_amount"),
                "pay_date": r.get("pay_date"),
                "frequency": r.get("frequency"),
            }
            for r in (data.get("results") or [])
            if r.get("ex_dividend_date")
        ]
        results.sort(key=lambda x: x["ex_dividend_date"])
        _div_cache[t] = (results, time.monotonic())
        return results
    except Exception as e:
        log.debug("[polygon] dividends %s: %s", t, e)
        return []


# ── §81 Block Print Detection ──────────────────────────────────────────────────
# Easley & O'Hara (1987): large trades carry more information than small trades.
# Block prints (>=min_block_size shares) at the ask near day-low = institutional
# accumulation; at the bid near day-high = institutional distribution.
_block_print_cache: dict[str, tuple[dict, float]] = {}
_BLOCK_PRINT_TTL = 600  # 10 min — refreshed each scan cycle

# ── OFI (Order Flow Imbalance) ────────────────────────────────────────────────
# Lee-Ready (1991) approximation on 1-min Polygon aggregate bars.
# ofi_t = V_t × sign(C_t − C_{t−1}): buyer-initiated if price ticked up, else seller.
# Normalized by session ADV so the metric is comparable across tickers.
_ofi_cache: dict[str, tuple[dict, float]] = {}
_OFI_TTL = 600  # 10 min


async def get_recent_block_prints(
    ticker: str,
    min_block_size: int = 5_000,
) -> dict:
    """Return recent block-trade summary for `ticker`.

    Fetches the last 500 trades via Polygon /v3/trades and classifies each
    print as accumulation (at ask, near day-low) or distribution (at bid,
    near day-high).

    Returns:
        {
            "block_buys": int,
            "block_sells": int,
            "block_buy_volume": float,
            "block_sell_volume": float,
        }
    An empty dict is returned on error or when Polygon is unavailable.
    """
    t = ticker.upper()
    cached = _block_print_cache.get(t)
    if cached and time.monotonic() - cached[1] < _BLOCK_PRINT_TTL:
        return cached[0]

    api_key = _get_api_key()
    if not api_key:
        return {}

    # Get current price context from snapshot cache
    snap_entry = _snapshot_cache.get(t)
    if snap_entry is None:
        return {}
    snap, _ = snap_entry
    day = snap.get("day") or {}
    day_low = float(day.get("l") or 0)
    day_high = float(day.get("h") or 0)
    last_trade = snap.get("lastTrade") or {}
    mid_price = float(last_trade.get("p") or 0)
    if mid_price <= 0:
        return {}

    url = f"{_BASE}/v3/trades/{t}"
    params = {
        "limit": 500,
        "sort": "timestamp",
        "order": "desc",
        "apiKey": api_key,
    }
    try:
        import ssl as _ssl

        import certifi as _certifi

        ssl_ctx = _ssl.create_default_context(cafile=_certifi.where())
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10, ssl=ssl_ctx) as resp:
                if resp.status != 200:
                    return {}
                data = await resp.json()

        block_buys = 0
        block_sells = 0
        block_buy_vol = 0.0
        block_sell_vol = 0.0

        for trade in data.get("results") or []:
            size = int(trade.get("size") or 0)
            if size < min_block_size:
                continue
            price = float(trade.get("price") or 0)
            if price <= 0:
                continue

            # Classify by price relative to intraday range:
            # Near day-low (within 1%): buyer-initiated = accumulation
            # Near day-high (within 1%): seller-initiated = distribution
            at_low = day_low > 0 and price <= day_low * 1.01
            at_high = day_high > 0 and price >= day_high * 0.99

            if at_low:
                block_buys += 1
                block_buy_vol += size
            elif at_high:
                block_sells += 1
                block_sell_vol += size

        result = {
            "block_buys": block_buys,
            "block_sells": block_sells,
            "block_buy_volume": block_buy_vol,
            "block_sell_volume": block_sell_vol,
        }
        _block_print_cache[t] = (result, time.monotonic())
        return result
    except Exception as e:
        log.debug("[polygon] block_prints %s: %s", t, e)
        return {}


async def get_ofi_signals(ticker: str) -> dict:
    """
    Order Flow Imbalance from Polygon 1-minute aggregate bars.

    Returns:
        ofi_30m        — normalized OFI over last 30 bars (half-hour)
        ofi_2h         — normalized OFI over last 120 bars (two hours)
        ofi_1d         — normalized OFI over full session
        ofi_divergence — price_ret * -1 * ofi_1d; positive when price fell
                         but buyers were net absorbing (accumulation signal)

    All values are normalized by session total volume; range roughly [-1, +1].
    Empty dict returned on error or when Polygon key is absent.
    """
    t = ticker.upper()
    cached = _ofi_cache.get(t)
    if cached and time.monotonic() - cached[1] < _OFI_TTL:
        return cached[0]

    api_key = _get_api_key()
    if not api_key:
        return {}

    try:
        import ssl as _ssl

        import certifi as _certifi
        import numpy as _np

        ssl_ctx = _ssl.create_default_context(cafile=_certifi.where())

        # Fetch today's 1-minute bars (full session = up to 390 bars)
        now_utc = datetime.now(timezone.utc)
        # Use yesterday as from-date so pre-market bars are included
        from_dt = (now_utc - timedelta(days=2)).strftime("%Y-%m-%d")
        to_dt = now_utc.strftime("%Y-%m-%d")
        url = f"{_BASE}/v2/aggs/ticker/{t}/range/1/minute/{from_dt}/{to_dt}"
        params = {
            "adjusted": "true",
            "sort": "asc",
            "limit": 1000,
            "apiKey": api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5, ssl=ssl_ctx) as resp:
                if resp.status != 200:
                    return {}
                data = await resp.json(content_type=None)

        results = data.get("results") or []
        if len(results) < 10:
            return {}

        closes = _np.array([float(r.get("c") or 0) for r in results])
        volumes = _np.array([float(r.get("v") or 0) for r in results])

        # Lee-Ready sign: price ticked up → buyer-initiated; down → seller
        price_diff = _np.diff(closes, prepend=closes[0])
        signs = _np.where(price_diff > 0, 1.0, _np.where(price_diff < 0, -1.0, 0.0))
        ofi_series = signs * volumes

        session_vol = float(volumes.sum()) or 1.0
        ofi_30m = float(ofi_series[-30:].sum()) / session_vol
        ofi_2h = float(ofi_series[-120:].sum()) / session_vol
        ofi_1d = float(ofi_series.sum()) / session_vol

        # Divergence: positive when price fell but net flow was buying
        price_ret_today = float(closes[-1] / closes[0] - 1) if closes[0] > 0 else 0.0
        ofi_divergence = price_ret_today * -1.0 * ofi_1d

        result = {
            "ofi_30m": round(ofi_30m, 4),
            "ofi_2h": round(ofi_2h, 4),
            "ofi_1d": round(ofi_1d, 4),
            "ofi_divergence": round(ofi_divergence, 6),
        }
        _ofi_cache[t] = (result, time.monotonic())
        return result

    except Exception as e:
        log.debug("[polygon] ofi %s: %s", t, e)
        return {}
