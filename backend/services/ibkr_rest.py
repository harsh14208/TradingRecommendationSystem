"""
Async client for Interactive Brokers Client Portal Web API.
Supports paper/live routing via local gateway connection.
"""

import ssl
import uuid
import logging
import aiohttp
import certifi

log = logging.getLogger("ibkr_rest")


def _base() -> str:
    from config import get_settings

    return getattr(get_settings(), "ibkr_base_url", "https://localhost:5000/v1/api")


def _headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "accept": "application/json",
    }


def _ssl_ctx() -> ssl.SSLContext | bool:
    base = _base()
    if "localhost" in base or "127.0.0.1" in base:
        return False
    return ssl.create_default_context(cafile=certifi.where())


async def get_account(api_key: str, api_secret: str = "", live: bool = False) -> dict:
    base_url = _base()
    async with aiohttp.ClientSession() as s:
        # Get list of accounts
        async with s.get(
            f"{base_url}/portfolio/accounts",
            headers=_headers(api_key),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            accounts = await r.json()
            if not accounts:
                raise ValueError("No IBKR accounts found")
            account_id = accounts[0].get("id") or accounts[0].get("accountId")

        # Get ledger for that account to extract equity / buying power
        async with s.get(
            f"{base_url}/portfolio/{account_id}/ledger",
            headers=_headers(api_key),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            ledger = await r.json()
            currency = accounts[0].get("currency", "USD")
            curr_data = ledger.get(currency, {})
            if not curr_data and ledger:
                first_key = list(ledger.keys())[0]
                curr_data = ledger.get(first_key, {})

            equity = curr_data.get("netliquidationvalue", 0.0)
            buying_power = curr_data.get("buyingpower", 0.0)
            unrealized_pl = curr_data.get("unrealizedpnl", 0.0)

            return {
                "id": account_id,
                "status": "ACTIVE",
                "equity": str(equity),
                "buying_power": str(buying_power),
                "currency": currency,
                "unrealized_pl": str(unrealized_pl),
            }


async def search_conid(symbol: str, api_key: str) -> int:
    base_url = _base()
    async with aiohttp.ClientSession() as s:
        async with s.post(
            f"{base_url}/iserver/secdef/search",
            headers=_headers(api_key),
            json={"symbol": symbol.upper(), "secType": "STK", "name": False},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            results = await r.json()
            if not results:
                raise ValueError(f"Contract not found for symbol {symbol}")
            return int(results[0]["conid"])


async def get_positions(api_key: str, api_secret: str = "", live: bool = False) -> list:
    base_url = _base()
    acct = await get_account(api_key, api_secret, live)
    acct_id = acct["id"]
    async with aiohttp.ClientSession() as s:
        async with s.get(
            f"{base_url}/portfolio/{acct_id}/positions",
            headers=_headers(api_key),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def get_orders(
    api_key: str, api_secret: str = "", status: str = "all", limit: int = 50, live: bool = False
) -> list:
    base_url = _base()
    async with aiohttp.ClientSession() as s:
        async with s.get(
            f"{base_url}/iserver/account/orders",
            headers=_headers(api_key),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            res = await r.json()
            orders = res.get("orders", [])
            return orders[:limit]


async def place_order(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    base_url = _base()
    acct = await get_account(api_key, api_secret, live)
    acct_id = acct["id"]
    conid = await search_conid(symbol, api_key)

    ib_order_type = "MKT" if order_type.lower() == "market" else "LMT"
    tif = "DAY" if time_in_force.lower() == "day" else "GTC"

    order_payload = {
        "acctId": acct_id,
        "conid": conid,
        "secType": "STK",
        "cOID": f"ibkr_{uuid.uuid4().hex[:12]}",
        "orderType": ib_order_type,
        "side": side.upper(),
        "quantity": float(qty),
        "tif": tif,
    }
    if ib_order_type == "LMT" and limit_price is not None:
        order_payload["price"] = float(limit_price)

    async with aiohttp.ClientSession() as s:
        async with s.post(
            f"{base_url}/iserver/account/{acct_id}/orders",
            headers=_headers(api_key),
            json={"orders": [order_payload]},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            res = await r.json()
            if isinstance(res, list) and len(res) > 0:
                first = res[0]
                if "replyId" in first:
                    reply_id = first["replyId"]
                    async with s.post(
                        f"{base_url}/iserver/reply/{reply_id}",
                        headers=_headers(api_key),
                        json={"confirmed": True},
                        ssl=_ssl_ctx(),
                    ) as reply_r:
                        reply_res = await reply_r.json()
                        return reply_res[0] if isinstance(reply_res, list) and reply_res else reply_res
                return first
            return res


async def place_notional_order(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
    entry_price: float | None = None,
) -> dict:
    price = entry_price
    if price is None or price <= 0:
        conid = await search_conid(symbol, api_key)
        base_url = _base()
        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"{base_url}/iserver/marketdata/snapshot",
                headers=_headers(api_key),
                params={"conids": str(conid), "fields": "31"},
                ssl=_ssl_ctx(),
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    if isinstance(data, list) and data:
                        price_str = data[0].get("31") or data[0].get("last")
                        if price_str:
                            price = float(price_str)
        if price is None or price <= 0:
            raise ValueError(f"Could not determine price for symbol {symbol} to calculate notional quantity")

    qty = round(notional / price, 4)
    if qty <= 0:
        qty = 1.0

    return await place_order(
        api_key=api_key,
        api_secret=api_secret,
        symbol=symbol,
        qty=qty,
        side=side,
        order_type="market",
        time_in_force=time_in_force,
        live=live,
    )


async def submit_bracket_stop_order(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,
    live: bool = False,
) -> dict:
    base_url = _base()
    acct = await get_account(api_key, api_secret, live)
    acct_id = acct["id"]
    conid = await search_conid(symbol, api_key)

    price = entry_price
    if price is None or price <= 0:
        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"{base_url}/iserver/marketdata/snapshot",
                headers=_headers(api_key),
                params={"conids": str(conid), "fields": "31"},
                ssl=_ssl_ctx(),
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    if isinstance(data, list) and data:
                        price_str = data[0].get("31") or data[0].get("last")
                        if price_str:
                            price = float(price_str)

    if price is None or price <= 0:
        raise ValueError(f"Could not determine price for symbol {symbol} to calculate notional quantity")

    qty = round(notional / price, 4)
    if qty <= 0:
        qty = 1.0

    parent_id = f"parent_{uuid.uuid4().hex[:8]}"
    tp_id = f"tp_{uuid.uuid4().hex[:8]}"
    sl_id = f"sl_{uuid.uuid4().hex[:8]}"

    orders = []

    # Parent Order
    parent_order = {
        "acctId": acct_id,
        "conid": conid,
        "secType": "STK",
        "cOID": parent_id,
        "orderType": "MKT",
        "side": side.upper(),
        "quantity": float(qty),
        "tif": "DAY",
    }
    orders.append(parent_order)

    # Child Order: Stop Loss
    child_side = "SELL" if side.upper() == "BUY" else "BUY"
    stop_order = {
        "acctId": acct_id,
        "conid": conid,
        "parentId": parent_id,
        "cOID": sl_id,
        "orderType": "STP",
        "side": child_side,
        "quantity": float(qty),
        "auxPrice": float(stop_price),
        "tif": "GTC",
    }
    orders.append(stop_order)

    # Child Order: Take Profit (optional)
    if take_profit_price is not None:
        tp_order = {
            "acctId": acct_id,
            "conid": conid,
            "parentId": parent_id,
            "cOID": tp_id,
            "orderType": "LMT",
            "side": child_side,
            "quantity": float(qty),
            "price": float(take_profit_price),
            "tif": "GTC",
        }
        orders.append(tp_order)

    async with aiohttp.ClientSession() as s:
        async with s.post(
            f"{base_url}/iserver/account/{acct_id}/orders",
            headers=_headers(api_key),
            json={"orders": orders},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            res = await r.json()
            if isinstance(res, list) and len(res) > 0:
                first = res[0]
                if "replyId" in first:
                    reply_id = first["replyId"]
                    async with s.post(
                        f"{base_url}/iserver/reply/{reply_id}",
                        headers=_headers(api_key),
                        json={"confirmed": True},
                        ssl=_ssl_ctx(),
                    ) as reply_r:
                        reply_res = await reply_r.json()
                        return reply_res[0] if isinstance(reply_res, list) and reply_res else reply_res
                return first
            return res


async def close_position(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    acct = await get_account(api_key, api_secret, live)
    positions = await get_positions(api_key, api_secret, live)

    position_qty = 0.0
    for pos in positions:
        if pos.get("ticker", "").upper() == symbol.upper() or pos.get("symbol", "").upper() == symbol.upper():
            position_qty = float(pos.get("position", 0.0) or pos.get("qty", 0.0))
            break

    if position_qty == 0.0:
        return {"status": "no_position"}

    side = "SELL" if position_qty > 0 else "BUY"
    qty = abs(position_qty)

    return await place_order(
        api_key=api_key,
        api_secret=api_secret,
        symbol=symbol,
        qty=qty,
        side=side,
        order_type="market",
        live=live,
    )


async def cancel_order(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    acct = await get_account(api_key, api_secret, live)
    acct_id = acct["id"]
    base_url = _base()
    async with aiohttp.ClientSession() as s:
        async with s.delete(
            f"{base_url}/iserver/account/{acct_id}/order/{order_id}",
            headers=_headers(api_key),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def get_portfolio_value(api_key: str, api_secret: str = "", live: bool = False) -> float:
    acct = await get_account(api_key, api_secret, live)
    return float(acct.get("equity") or 0.0)


async def get_unrealized_pl(api_key: str, api_secret: str = "", live: bool = False) -> float:
    acct = await get_account(api_key, api_secret, live)
    return float(acct.get("unrealized_pl") or 0.0)
