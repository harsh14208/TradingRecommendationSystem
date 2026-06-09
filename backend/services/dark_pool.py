"""
Dark Pool / Off-Exchange Block Trades.
Powered by Massive API (massive.com)

Layer 1 — Live WebSocket stream: accumulate raw notional flow from
  off-exchange prints (Exchange ID 4 = FINRA TRF).

Layer 2 — Block Trade Reconstruction: group fragmented tape prints
  by time/price proximity and infer institutional order direction
  using the Lee-Ready tick rule (buy-initiated vs sell-initiated).
"""

import asyncio
import logging
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from services.http_client import get_ssl_context, shared_session

log = logging.getLogger("signal.trade.dark_pool")

# ── Raw flow accumulator ($ millions per ticker) ──────────────────────────────
_flow_data: dict[str, float] = {}

# Liveness heartbeat for the stream watchdog. handle_messages() stamps this on
# every batch the Massive client delivers; the watchdog in start_dark_pool_stream
# treats "no heartbeat for _STALL_SEC" as a dead connection. (Previously the
# watchdog read a local that nothing ever updated, so it tripped unconditionally
# every 60s and restarted the stream forever.)
_last_msg_monotonic: list[float] = [time.monotonic()]

# ── Rolling print buffer for reconstruction (last 30 minutes of prints) ───────
_MAX_BUFFER_AGE_S = 1800  # 30 minutes
_print_buffer: deque = deque(maxlen=100_000)  # (ts, symbol, price, size, notional)
_last_price: dict[str, float] = {}  # for tick rule direction inference


@dataclass
class _Print:
    ts: float
    symbol: str
    price: float
    size: int
    notional: float


def handle_messages(messages: list):
    now = time.time()
    # Watchdog heartbeat — any delivered batch means the connection is alive,
    # even if no print clears the off-exchange size/notional filter below.
    _last_msg_monotonic[0] = time.monotonic()
    try:
        from massive.websocket.models import EquityTrade

        for msg in messages:
            if isinstance(msg, EquityTrade):
                is_off_exchange = getattr(msg, "exchange", 0) == 4
                size = getattr(msg, "size", 0)
                price = getattr(msg, "price", 0.0)
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
        err = str(e).lower()
        # 1008 (policy violation) = server rejecting the subscription/entitlement —
        # same class as a plan limit, so propagate it to the outer long-backoff loop
        # instead of letting it fall through to the 10s hammer-retry.
        if any(k in err for k in ("plan", "upgrade", "subscription", "1008", "policy violation")):
            raise  # let outer loop apply long backoff
        log.warning(f"[dark_pool] Massive WebSocket error: {e}")


async def start_dark_pool_stream():
    """
    Start the Massive WebSocket client with a reconnect watchdog.
    If the stream silently dies (no messages for 60s), restart it automatically.
    Plan-limit errors back off for 6 hours instead of hammering every 15s.
    """
    if not os.getenv("MASSIVE_API_KEY"):
        return

    _STALL_SEC = 60
    _PLAN_LIMIT_BACKOFF = 6 * 3600  # 6 hours — plan/entitlement won't change sooner
    _MAX_CONSEC_STALLS = 3  # after this many empty stalls, treat feed as dead → long backoff
    consec_stalls = 0

    while True:
        try:
            # Fresh liveness window per attempt — otherwise a stale heartbeat makes
            # the next connection "stall" within one 10s tick instead of _STALL_SEC.
            _last_msg_monotonic[0] = time.monotonic()
            stream_task = asyncio.create_task(asyncio.to_thread(_run_darkpool_scanner))
            stalled = False
            while not stream_task.done():
                await asyncio.sleep(10)
                if time.monotonic() - _last_msg_monotonic[0] > _STALL_SEC:
                    stream_task.cancel()
                    stalled = True
                    break

            if stalled:
                consec_stalls += 1
                if consec_stalls >= _MAX_CONSEC_STALLS:
                    # Connects but never delivers — almost always a plan/entitlement
                    # gap (the firehose just isn't sent). Stop hammering every ~15s.
                    log.warning(
                        "[dark_pool] %d consecutive stalls with no messages — feed not "
                        "delivering (likely plan/entitlement); pausing 6h",
                        consec_stalls,
                    )
                    consec_stalls = 0
                    await asyncio.sleep(_PLAN_LIMIT_BACKOFF)
                else:
                    log.warning(
                        "[dark_pool] stream stalled (%ds no messages) — restarting (%d/%d)",
                        _STALL_SEC,
                        consec_stalls,
                        _MAX_CONSEC_STALLS,
                    )
                    await asyncio.sleep(5)
            else:
                await stream_task  # surface any exception (e.g. plan-limit AuthError)
                consec_stalls = 0  # clean exit without stall → reset the counter
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            return
        except Exception as e:
            err = str(e).lower()
            if any(k in err for k in ("plan", "upgrade", "subscription", "auth", "1008", "policy violation")):
                log.warning(
                    "[dark_pool] WebSocket access rejected (plan/entitlement or 1008 "
                    "policy violation) — pausing for 6h (upgrade at massive.com/pricing)"
                )
                await asyncio.sleep(_PLAN_LIMIT_BACKOFF)
            else:
                log.warning("[dark_pool] stream error: %s — retrying in 10s", e)
                await asyncio.sleep(10)


async def get_dark_pool_flow(tickers: list[str]) -> dict:
    """
    Return accumulated off-exchange (dark pool) block flow.
    Returns: { ticker: {"net_flow_m": float_millions} }
    """
    return {t: {"net_flow_m": round(_flow_data[t], 2)} for t in tickers if _flow_data.get(t, 0.0) > 0}


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
    TIME_WINDOW = 30.0  # seconds
    PRICE_WINDOW = 0.005  # 0.5%

    for sym, sym_prints in by_sym.items():
        sym_prints.sort(key=lambda p: p.ts)
        prev_price = sym_prints[0].price
        groups: list[list[_Print]] = []
        current_group: list[_Print] = [sym_prints[0]]
        ref_price = sym_prints[0].price

        for p in sym_prints[1:]:
            time_gap = p.ts - current_group[-1].ts
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

            buy_count = directions.count("buy")
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

            orders.append(
                {
                    "symbol": sym,
                    "direction": direction,
                    "direction_conf": round(confidence, 2),
                    "total_notional_m": round(total_notional / 1_000_000, 2),
                    "total_size": total_size,
                    "vwap": round(vwap, 2),
                    "print_count": len(group),
                    "time_start": int(group[0].ts),
                    "time_end": int(group[-1].ts),
                    "duration_s": round(group[-1].ts - group[0].ts, 1),
                }
            )

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
    buy_total = sum(o["total_notional_m"] for o in orders if o["direction"] == "buy")
    sell_total = sum(o["total_notional_m"] for o in orders if o["direction"] == "sell")
    net_flow = buy_total - sell_total

    return {
        "ticker": ticker or "ALL",
        "window_minutes": _MAX_BUFFER_AGE_S // 60,
        "print_count": len(active_prints),
        "orders": orders[:50],  # top 50 by notional
        "summary": {
            "buy_flow_m": round(buy_total, 2),
            "sell_flow_m": round(sell_total, 2),
            "net_flow_m": round(net_flow, 2),
            "direction": "buy" if net_flow > 1 else "sell" if net_flow < -1 else "neutral",
        },
        "has_live_data": len(active_prints) > 0,
    }


async def get_massive_advanced_signals(ticker: str) -> dict:
    """
    Fetch Polygon-backed signals for corporate actions and FTDs.

    Endpoints used (all real, verified against Polygon docs):
      - /v3/reference/dividends  — detect upcoming ex-dividend dates
      - /v3/reference/splits     — detect upcoming stock splits
      - /v2/reference/ftd        — Fails-to-Deliver + Reg SHO (Business plan; graceful 403)

    Returns:
      ftd          — {"is_reg_sho": bool, "spike_pct": float}
      corp_actions — {"ex_div_soon": bool, "ex_div_date": str|None, "split_soon": bool}
      dark_pool_flow — float (millions, from live WebSocket accumulator)
    """
    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    from datetime import date, timedelta

    ssl_ctx = get_ssl_context()

    results = {
        "ftd": {"is_reg_sho": False, "spike_pct": 0.0},
        "corp_actions": {"ex_div_soon": False, "ex_div_date": None, "split_soon": False},
        "dark_pool_flow": _flow_data.get(ticker, 0.0),
    }

    today = date.today()
    lookahead_14 = (today + timedelta(days=14)).isoformat()
    lookahead_7 = (today + timedelta(days=7)).isoformat()

    try:
        async with shared_session() as session:

            async def _get(url: str, params: dict) -> dict:
                try:
                    params["apiKey"] = api_key
                    async with session.get(url, params=params, timeout=6, ssl=ssl_ctx) as r:
                        if r.status == 200:
                            return await r.json()
                except Exception:
                    pass
                return {}

            # ── Dividends: ex-div within 14 days blocks MR entry ────────────
            div_data = await _get(
                "https://api.polygon.io/v3/reference/dividends",
                {"ticker": ticker, "ex_dividend_date.lte": lookahead_14, "order": "asc", "limit": 5},
            )
            for div in div_data.get("results") or []:
                ex_date = div.get("ex_dividend_date", "")
                if ex_date and ex_date >= today.isoformat():
                    results["corp_actions"]["ex_div_soon"] = True
                    results["corp_actions"]["ex_div_date"] = ex_date
                    break

            # ── Splits: split within 14 days ─────────────────────────────────
            split_data = await _get(
                "https://api.polygon.io/v3/reference/splits",
                {"ticker": ticker, "execution_date.lte": lookahead_14, "order": "asc", "limit": 5},
            )
            for sp in split_data.get("results") or []:
                ex_date = sp.get("execution_date", "")
                if ex_date and ex_date >= today.isoformat():
                    results["corp_actions"]["split_soon"] = True
                    break

            # ── FTDs (Business plan — graceful 403) ──────────────────────────
            ftd_data = await _get(
                "https://api.polygon.io/v2/reference/ftd",
                {"symbol": ticker, "limit": 10},
            )
            ftd_results = ftd_data.get("results") or []
            if ftd_results:
                latest = ftd_results[0]
                qty = float(latest.get("quantity", 0) or 0)
                prev_q = float(ftd_results[1].get("quantity", 0) or 0) if len(ftd_results) > 1 else 0.0
                spike = ((qty - prev_q) / prev_q * 100) if prev_q > 0 else 0.0
                is_sho = bool(latest.get("threshold_securities_list", False))
                results["ftd"] = {"is_reg_sho": is_sho, "spike_pct": round(spike, 1)}

    except Exception as e:
        log.warning(f"[dark_pool] advanced signals error for {ticker}: {e}")

    return results
