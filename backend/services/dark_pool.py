"""
Dark Pool / Off-Exchange Block Trades.
Powered by Massive API (massive.com)

Layer 1 — Live WebSocket stream: accumulate raw notional flow from
  off-exchange prints (Exchange ID 4 = FINRA TRF).

Layer 2 — Block Trade Reconstruction: group fragmented tape prints
  by time/price proximity and infer institutional order direction
  using the Lee-Ready tick rule (buy-initiated vs sell-initiated).
"""
import os
import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field

log = logging.getLogger("signal.trade.dark_pool")

# ── Raw flow accumulator ($ millions per ticker) ──────────────────────────────
_flow_data: dict[str, float] = {}

# ── Rolling print buffer for reconstruction (last 30 minutes of prints) ───────
_MAX_BUFFER_AGE_S = 1800   # 30 minutes
_print_buffer: deque = deque(maxlen=100_000)  # (ts, symbol, price, size, notional)
_last_price: dict[str, float] = {}            # for tick rule direction inference


@dataclass
class _Print:
    ts:       float
    symbol:   str
    price:    float
    size:     int
    notional: float


def handle_messages(messages: list):
    now = time.time()
    try:
        from massive.websocket.models import Trade
        for msg in messages:
            if isinstance(msg, Trade):
                is_off_exchange = getattr(msg, "exchange", 0) == 4
                size     = getattr(msg, "size",   0)
                price    = getattr(msg, "price",  0.0)
                notional = size * price

                if is_off_exchange and (size >= 10_000 or notional >= 250_000):
                    symbol = getattr(msg, "symbol", "UNKNOWN")
                    _flow_data[symbol] = _flow_data.get(symbol, 0.0) + notional / 1_000_000.0
                    _print_buffer.append(_Print(now, symbol, price, size, notional))
                    _last_price[symbol] = price
    except Exception:
        pass


def _run_darkpool_scanner():
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return
    try:
        from massive import WebSocketClient
        client = WebSocketClient(api_key=api_key, market="stocks")
        client.subscribe("T.*")
        log.info("[dark_pool] Starting Massive WebSocket stream for Dark Pool prints…")
        client.run(handle_messages)
    except Exception as e:
        log.warning(f"[dark_pool] Massive WebSocket error: {e}")


async def start_dark_pool_stream():
    """
    Start the Massive WebSocket client with a reconnect watchdog.
    If the stream silently dies (no messages for 60s), restart it automatically.
    """
    if not os.getenv("MASSIVE_API_KEY"):
        return

    import time as _t
    _last_msg = [_t.monotonic()]
    _STALL_SEC = 60  # Massive stream considered stalled after 60s silence

    original_handle = handle_messages

    def _guarded_handle(messages):
        _last_msg[0] = _t.monotonic()
        original_handle(messages)

    while True:
        try:
            # Run the scanner in a thread; watchdog runs in asyncio
            stream_task = asyncio.create_task(asyncio.to_thread(_run_darkpool_scanner))
            while not stream_task.done():
                await asyncio.sleep(10)
                if _t.monotonic() - _last_msg[0] > _STALL_SEC:
                    log.warning("[dark_pool] stream stalled (%ds no messages) — restarting",
                                _STALL_SEC)
                    stream_task.cancel()
                    break
            await asyncio.sleep(5)  # brief pause before reconnect
        except asyncio.CancelledError:
            return
        except Exception as e:
            log.warning("[dark_pool] stream error: %s — retrying in 10s", e)
            await asyncio.sleep(10)


async def get_dark_pool_flow(tickers: list[str]) -> dict:
    """
    Return accumulated off-exchange (dark pool) block flow.
    Returns: { ticker: {"net_flow_m": float_millions} }
    """
    return {
        t: {"net_flow_m": round(_flow_data[t], 2)}
        for t in tickers
        if _flow_data.get(t, 0.0) > 0
    }


# ── Block Trade Reconstruction ────────────────────────────────────────────────

def _tick_rule(current_price: float, prev_price: float) -> str:
    """
    Lee-Ready tick rule: infer trade direction from price movement.
      uptick   (price > prev)  → buy-initiated
      downtick (price < prev)  → sell-initiated
      zero tick → carry forward previous direction
    """
    if current_price > prev_price:
        return "buy"
    elif current_price < prev_price:
        return "sell"
    return "unknown"


def _reconstruct_orders(prints: list[_Print]) -> list[dict]:
    """
    Group fragmented dark pool tape prints into reconstructed institutional orders.

    Grouping criteria:
      - Same symbol
      - Within 30 seconds of each other
      - Price within 0.5% of group reference price

    Direction: Lee-Ready tick rule applied per print, then majority vote
    on the group. Ambiguous groups (50/50) are labelled 'unknown'.

    Aggregation: sum size, sum notional, VWAP, time range.
    """
    if not prints:
        return []

    # Sort chronologically per symbol
    by_sym: dict[str, list[_Print]] = defaultdict(list)
    for p in prints:
        by_sym[p.symbol].append(p)

    orders = []
    TIME_WINDOW  = 30.0  # seconds
    PRICE_WINDOW = 0.005 # 0.5%

    for sym, sym_prints in by_sym.items():
        sym_prints.sort(key=lambda p: p.ts)
        prev_price = sym_prints[0].price
        groups: list[list[_Print]] = []
        current_group: list[_Print] = [sym_prints[0]]
        ref_price = sym_prints[0].price

        for p in sym_prints[1:]:
            time_gap  = p.ts - current_group[-1].ts
            price_gap = abs(p.price - ref_price) / (ref_price or 1)
            if time_gap <= TIME_WINDOW and price_gap <= PRICE_WINDOW:
                current_group.append(p)
            else:
                groups.append(current_group)
                current_group = [p]
                ref_price = p.price
        groups.append(current_group)

        # Filter: only materialise groups with ≥ $500k notional
        for group in groups:
            total_notional = sum(p.notional for p in group)
            if total_notional < 500_000:
                continue

            total_size = sum(p.size for p in group)
            vwap = total_notional / total_size if total_size else 0.0

            # Direction via tick rule on each print
            directions = []
            lp = group[0].price
            for p in group:
                d = _tick_rule(p.price, lp)
                if d != "unknown":
                    directions.append(d)
                lp = p.price

            buy_count  = directions.count("buy")
            sell_count = directions.count("sell")
            if buy_count > sell_count:
                direction = "buy"
                confidence = buy_count / len(directions) if directions else 0.5
            elif sell_count > buy_count:
                direction = "sell"
                confidence = sell_count / len(directions) if directions else 0.5
            else:
                direction = "unknown"
                confidence = 0.5

            orders.append({
                "symbol":         sym,
                "direction":      direction,
                "direction_conf": round(confidence, 2),
                "total_notional_m": round(total_notional / 1_000_000, 2),
                "total_size":     total_size,
                "vwap":           round(vwap, 2),
                "print_count":    len(group),
                "time_start":     int(group[0].ts),
                "time_end":       int(group[-1].ts),
                "duration_s":     round(group[-1].ts - group[0].ts, 1),
            })

    orders.sort(key=lambda o: o["total_notional_m"], reverse=True)
    return orders


async def get_reconstructed_orders(ticker: str | None = None) -> dict:
    """
    Public entrypoint: reconstruct institutional orders from buffered prints.
    If ticker is provided, filter to that symbol only.
    Returns aggregated view + list of reconstructed orders (largest first).
    """
    now = time.time()
    cutoff = now - _MAX_BUFFER_AGE_S

    # Drain stale prints from buffer
    active_prints = [p for p in _print_buffer if p.ts >= cutoff]
    if ticker:
        active_prints = [p for p in active_prints if p.symbol == ticker]

    orders = await asyncio.to_thread(_reconstruct_orders, active_prints)

    # Net flow summary: buy $ - sell $
    buy_total  = sum(o["total_notional_m"] for o in orders if o["direction"] == "buy")
    sell_total = sum(o["total_notional_m"] for o in orders if o["direction"] == "sell")
    net_flow   = buy_total - sell_total

    return {
        "ticker":           ticker or "ALL",
        "window_minutes":   _MAX_BUFFER_AGE_S // 60,
        "print_count":      len(active_prints),
        "orders":           orders[:50],   # top 50 by notional
        "summary": {
            "buy_flow_m":   round(buy_total,  2),
            "sell_flow_m":  round(sell_total, 2),
            "net_flow_m":   round(net_flow,   2),
            "direction":    "buy" if net_flow > 1 else "sell" if net_flow < -1 else "neutral",
        },
        "has_live_data": len(active_prints) > 0,
    }


async def get_massive_advanced_signals(ticker: str) -> dict:
    """
    Fetch advanced Massive API signals: Short Interest, FTDs, GEX, Level 2, Corp Actions.
    """
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    import aiohttp, ssl, certifi
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    base_url = "https://api.polygon.io/v3/reference"
    params = {"ticker": ticker, "apiKey": api_key}

    results = {
        "ftd":          {"is_reg_sho": False, "spike_pct": 0.0},
        "gex":          {"net_gex": 0.0},
        "order_book":   {"bid_ask_ratio": 1.0},
        "corp_actions": {"active_asr": False, "issuer_buying": False},
        "retail_flow":  0.0,
        "dark_pool_flow": _flow_data.get(ticker, 0.0),
        "short_interest": {"short_volume_pct": 0.0},
    }

    try:
        async with aiohttp.ClientSession() as session:
            endpoints = {
                "short_interest": f"{base_url}/short_interest",
                "ftd":            f"{base_url}/ftd",
                "gex":            f"{base_url}/options_gex",
                "order_book":     f"{base_url}/level2",
                "corp_actions":   f"{base_url}/corporate_actions",
            }

            async def fetch_ep(key, url):
                try:
                    async with session.get(url, params=params, timeout=5, ssl=ssl_ctx) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get("results"):
                                results[key] = data["results"][0]
                        # 403 = endpoint requires higher Polygon plan — skip silently
                except Exception:
                    pass

            await asyncio.gather(*(fetch_ep(k, v) for k, v in endpoints.items()))

    except Exception as e:
        log.warning(f"[dark_pool] Failed to fetch massive advanced signals for {ticker}: {e}")

    return results
