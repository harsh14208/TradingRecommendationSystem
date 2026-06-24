"""Read-side helpers for the dedicated options paper account.

The options paper account is a separate Alpaca paper account (its own keys); see
``services.options_paper``. This module fetches its live account/positions and
keeps a lightweight daily equity history (stored in app_settings, no migration)
so the Paper Trading → Options page can show P&L over time.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.options_paper import options_paper_credentials

log = logging.getLogger("signal.options_account")

_HISTORY_KEY = "options_pnl_history"
_HISTORY_MAX = 400  # ~ a year of trading days


def _num(v, default=0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


async def fetch_options_account(settings) -> dict | None:
    """Return {account, positions} for the options paper account, or None when the
    options credentials are not configured."""
    creds = options_paper_credentials(settings)
    if not creds:
        return None
    from services import alpaca_rest

    key, secret = creds
    try:
        account = await alpaca_rest.get_account(key, secret)
        positions = await alpaca_rest.get_positions(key, secret)
    except Exception as exc:
        log.warning("options account fetch failed: %s", exc)
        return None
    return {"account": account, "positions": positions}


async def snapshot_options_pnl(db: AsyncSession, settings) -> None:
    """Append today's options-account equity snapshot to app_settings history.

    Idempotent per calendar day (overwrites the same date). Cheap, no migration —
    keeps a rolling equity curve for the Options paper page.
    """
    snap = await fetch_options_account(settings)
    if not snap:
        return
    acct = snap["account"] or {}
    positions = snap["positions"] or []
    equity = _num(acct.get("equity"))
    if equity <= 0:
        return
    today = datetime.now(timezone.utc).date().isoformat()
    row = {
        "date": today,
        "equity": round(equity, 2),
        "cash": round(_num(acct.get("cash")), 2),
        "unrealized_pl": round(sum(_num(p.get("unrealized_pl")) for p in positions), 2),
        "n_positions": len(positions),
    }

    from models import AppSettings

    srow = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    if srow is None:
        return
    data = dict(srow.data or {})
    history = [h for h in (data.get(_HISTORY_KEY) or []) if h.get("date") != today]
    history.append(row)
    history.sort(key=lambda h: h.get("date", ""))
    data[_HISTORY_KEY] = history[-_HISTORY_MAX:]
    srow.data = data
    # JSON column needs an explicit reassign to be flagged dirty.
    from sqlalchemy.orm.attributes import flag_modified

    flag_modified(srow, "data")
    await db.commit()
    log.info("options pnl snapshot: equity=%.2f positions=%d", equity, len(positions))


def options_pnl_history(app_data: dict | None) -> list[dict]:
    """Extract the stored equity history from app_settings data."""
    return list((app_data or {}).get(_HISTORY_KEY) or [])


async def _fetch_greeks(occ_symbol: str, key: str) -> dict | None:
    """delta/gamma/theta/vega for one OCC option symbol (Polygon snapshot)."""
    import aiohttp

    from services.http_client import shared_session
    from services.massive_options_data import _parse_opra

    poly_sym = occ_symbol if occ_symbol.startswith("O:") else f"O:{occ_symbol}"
    parsed = _parse_opra(poly_sym)
    if not parsed:
        return None
    underlying = parsed[0]
    url = f"https://api.polygon.io/v3/snapshot/options/{underlying}/{poly_sym}"
    try:
        async with shared_session() as s:
            async with s.get(url, params={"apiKey": key}, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                return ((await r.json()).get("results") or {}).get("greeks") or {}
    except Exception:
        return None


async def compute_options_risk(positions: list[dict], equity: float) -> dict:
    """Net portfolio Greeks + gross exposure across open option legs.

    Options are non-linear, so stock-style beta/Sharpe don't apply — the relevant
    risks are net delta (directional), theta (daily decay/income), vega (vol), and
    gross exposure. Greeks come from Polygon snapshots; qty is signed (short<0) and
    scaled by the 100-share contract multiplier.
    """
    if not positions:
        return {}
    from services.options_chain_resolver import _api_key

    key = _api_key()
    net = {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}
    gross = 0.0
    have_greeks = False
    for p in positions:
        try:
            qty = float(p.get("qty") or 0)
        except (TypeError, ValueError):
            qty = 0.0
        gross += abs(_num(p.get("market_value")))
        g = await _fetch_greeks(p.get("symbol") or "", key) if key else None
        if g:
            have_greeks = True
            for k in net:
                if g.get(k) is not None:
                    net[k] += _num(g.get(k)) * qty * 100.0
    return {
        "net_delta": round(net["delta"], 1) if have_greeks else None,
        "net_gamma": round(net["gamma"], 2) if have_greeks else None,
        "net_theta": round(net["theta"], 2) if have_greeks else None,
        "net_vega": round(net["vega"], 2) if have_greeks else None,
        "gross_market_value": round(gross, 2),
        "exposure_pct": round(gross / equity * 100.0, 2) if equity > 0 else None,
    }
