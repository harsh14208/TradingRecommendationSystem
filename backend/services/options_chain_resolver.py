"""Real-time options-chain resolution and liquidity filtering.

Primary data source is Polygon's ``/v3/snapshot/options/{underlying}`` endpoint,
which returns per-contract bid/ask, greeks, open interest, and volume.  The
resolver selects the exact expiry/strike/delta for a strategy and rejects
contracts that fail liquidity/spread filters.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

import aiohttp

from services.brokers.options_broker import OptionLeg, OptionOrder
from services.http_client import shared_session
from services.massive_options_data import _parse_opra

log = logging.getLogger("signal.options_chain_resolver")

_POLYGON_BASE = "https://api.polygon.io"
_MAX_PAGES = 8
_PAGE_SIZE = 250


@dataclass(frozen=True)
class OptionContract:
    """A single options contract from a real-time chain snapshot."""

    option_symbol: str
    underlying: str
    ctype: str  # "call" | "put"
    strike: float
    expiry: date
    bid: float
    ask: float
    midpoint: float
    spread: float
    spread_pct: float
    volume: int
    open_interest: int
    delta: float | None
    iv: float | None

    def is_liquid(
        self,
        min_volume: int = 10,
        min_oi: int = 100,
        max_spread_pct: float = 0.15,
        max_abs_spread: float = 0.50,
    ) -> bool:
        """Return True if the contract passes basic liquidity filters."""
        if self.bid <= 0 or self.ask <= 0:
            return False
        if self.volume < min_volume or self.open_interest < min_oi:
            return False
        if self.spread_pct > max_spread_pct and self.spread > max_abs_spread:
            return False
        return True


def _api_key() -> str | None:
    return os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY")


def _to_date(value: str | date | datetime) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def _parse_contract(raw: dict[str, Any]) -> OptionContract | None:
    """Parse one Polygon snapshot contract result."""
    details = raw.get("details") or {}
    option_symbol = details.get("ticker", "")
    parsed = _parse_opra(option_symbol)
    if not parsed:
        return None
    underlying, expiry, cp, strike = parsed
    ctype = "call" if cp == "C" else "put"

    quote = raw.get("last_quote") or {}
    bid = float(quote.get("bid") or 0.0)
    ask = float(quote.get("ask") or 0.0)
    if bid <= 0 and ask <= 0:
        # Fallback to day close if no quote is present.
        close = float((raw.get("day") or {}).get("close") or 0.0)
        if close > 0:
            bid = ask = close
        else:
            return None

    midpoint = (bid + ask) / 2.0
    spread = ask - bid
    spread_pct = spread / midpoint if midpoint > 0 else float("inf")

    volume = int((raw.get("day") or {}).get("volume", 0) or 0)
    oi = int(raw.get("open_interest", 0) or 0)

    greeks = raw.get("greeks") or {}
    delta = float(greeks.get("delta")) if greeks.get("delta") is not None else None
    iv = float(raw.get("implied_volatility")) if raw.get("implied_volatility") is not None else None

    return OptionContract(
        option_symbol=option_symbol,
        underlying=underlying,
        ctype=ctype,
        strike=strike,
        expiry=expiry,
        bid=bid,
        ask=ask,
        midpoint=midpoint,
        spread=spread,
        spread_pct=spread_pct,
        volume=volume,
        open_interest=oi,
        delta=delta,
        iv=iv,
    )


async def fetch_option_chain(
    underlying: str, api_key: str | None = None, expiry: date | None = None
) -> list[OptionContract]:
    """Fetch and parse the options chain snapshot for an underlying.

    ``expiry``, when given, filters the snapshot to a window around that date
    (``expiration_date.gte/lte`` ±14d). This is essential for high-strike-count
    names (SPY/UNH/…): the unfiltered snapshot returns near-term contracts first
    and the target monthly gets paged off the end, so resolution finds no
    candidates. Returns an empty list on any failure (callers fall back to
    placeholder legs).
    """
    key = api_key or _api_key()
    if not key:
        log.debug("No Polygon API key available for option chain lookup")
        return []

    url = f"{_POLYGON_BASE}/v3/snapshot/options/{underlying.upper()}"
    params: dict[str, Any] = {"apiKey": key, "limit": _PAGE_SIZE}
    if expiry is not None:
        params["expiration_date.gte"] = (expiry - timedelta(days=14)).isoformat()
        params["expiration_date.lte"] = (expiry + timedelta(days=14)).isoformat()
    raw: list[dict[str, Any]] = []
    try:
        async with shared_session() as session:
            next_url: str | None = url
            pages = 0
            while next_url and pages < _MAX_PAGES:
                if pages == 0:
                    async with session.get(next_url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        if resp.status != 200:
                            log.warning("Polygon option chain %s returned %d", underlying, resp.status)
                            return []
                        data = await resp.json()
                else:
                    async with session.get(next_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        if resp.status != 200:
                            break
                        data = await resp.json()
                batch = data.get("results") or []
                raw.extend(batch)
                next_url = data.get("next_url")
                pages += 1
    except Exception:
        log.exception("Failed to fetch option chain for %s", underlying)
        return []

    contracts = [_parse_contract(r) for r in raw]
    return [c for c in contracts if c is not None]


async def fetch_contract_snapshot(
    underlying: str, option_symbol: str, api_key: str | None = None
) -> OptionContract | None:
    """Fetch a single option contract snapshot (used for mark-to-market)."""
    key = api_key or _api_key()
    if not key:
        return None
    url = f"{_POLYGON_BASE}/v3/snapshot/options/{underlying.upper()}/{option_symbol.upper()}"
    params = {"apiKey": key}
    try:
        async with shared_session() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                raw = data.get("results")
                if not raw:
                    return None
                return _parse_contract(raw)
    except Exception:
        log.exception("Failed to fetch contract snapshot %s", option_symbol)
        return None


def filter_liquid_contracts(
    contracts: list[OptionContract],
    min_volume: int = 10,
    min_oi: int = 100,
    max_spread_pct: float = 0.15,
    max_abs_spread: float = 0.50,
) -> list[OptionContract]:
    """Return only contracts that pass liquidity/spread filters."""
    return [
        c
        for c in contracts
        if c.is_liquid(
            min_volume=min_volume,
            min_oi=min_oi,
            max_spread_pct=max_spread_pct,
            max_abs_spread=max_abs_spread,
        )
    ]


def _expiry_distance(c: OptionContract, target: date) -> float:
    """Prefer contracts expiring on or just after the target."""
    days = (c.expiry - target).days
    if days < 0:
        return abs(days) * 2.0  # penalize past expiry more
    return days


def _delta_distance(c: OptionContract, target_delta: float) -> float:
    """Delta distance, with sign-aware put delta."""
    if c.delta is None:
        return float("inf")
    d = c.delta
    if c.ctype == "put" and d > 0:
        d = -d
    return abs(d - target_delta)


def select_contract(
    contracts: list[OptionContract],
    ctype: str,
    target_expiry: date,
    target_strike: float | None = None,
    target_delta: float | None = None,
    min_volume: int = 10,
    min_oi: int = 100,
    max_spread_pct: float = 0.15,
    max_abs_spread: float = 0.50,
    expiry_window_days: int = 14,
    exclude: set[str] | None = None,
) -> OptionContract | None:
    """Select the best liquid contract for a leg.

    Scoring weights:
      - expiry within ``expiry_window_days`` of target (soft preference)
      - closest to ``target_delta`` when provided (delta-aware)
      - closest to ``target_strike`` otherwise

    ``exclude`` drops specific option symbols from consideration — used when
    building a spread so a protective wing can't collapse onto the same
    contract as the leg it's meant to hedge (e.g. on a coarse strike grid
    where the short and wing deltas both land on the sole nearby liquid
    strike).
    """
    ctype = ctype.lower()
    candidates = [
        c
        for c in contracts
        if c.ctype == ctype
        and (not exclude or c.option_symbol not in exclude)
        and c.is_liquid(
            min_volume=min_volume, min_oi=min_oi, max_spread_pct=max_spread_pct, max_abs_spread=max_abs_spread
        )
        and (c.expiry - target_expiry).days >= -expiry_window_days
    ]
    if not candidates:
        return None

    def score(c: OptionContract) -> float:
        exp_score = _expiry_distance(c, target_expiry) / max(expiry_window_days, 1)
        if target_delta is not None:
            delta_score = _delta_distance(c, target_delta)
        elif target_strike is not None and target_strike > 0:
            delta_score = abs(c.strike - target_strike) / target_strike
        else:
            delta_score = 0.0
        # Penalize wide spreads after expiry/delta fit.
        spread_score = c.spread_pct
        return exp_score * 1.0 + delta_score * 2.0 + spread_score * 0.5

    return min(candidates, key=score)


async def resolve_chain(
    underlying: str,
    min_volume: int = 10,
    min_oi: int = 100,
    max_spread_pct: float = 0.15,
    max_abs_spread: float = 0.50,
    api_key: str | None = None,
) -> list[OptionContract]:
    """Fetch and filter a liquid option chain."""
    contracts = await fetch_option_chain(underlying, api_key=api_key)
    return filter_liquid_contracts(
        contracts,
        min_volume=min_volume,
        min_oi=min_oi,
        max_spread_pct=max_spread_pct,
        max_abs_spread=max_abs_spread,
    )


# Convenience helpers used by the leg builder and paper simulator.


def target_delta_for_leg(strategy: str, ctype: str, position: str) -> float | None:
    """Return a sensible target delta for a leg when chain greeks are available.

    Position-aware: in an iron condor (SELL_DEFINED_RISK) the long protective
    wings must sit FURTHER out-of-the-money than the short legs (lower delta) —
    otherwise they resolve to the same contract as the short and the spread is
    degenerate (dropped as a duplicate).
    """
    if strategy == "SELL_CASH_SEC_PUT" and ctype == "put":
        return -0.30
    if strategy in ("SELL_STRANGLE", "SELL_DEFINED_RISK"):
        # Short legs ~0.30 delta; long wings ~0.15 (further OTM).
        mag = 0.30 if position == "short" else 0.15
        return mag if ctype == "call" else -mag
    if strategy == "LONG_STRADDLE":
        if ctype == "call":
            return 0.50
        if ctype == "put":
            return -0.50
    return None


def natural_fill_price(contract: OptionContract, position: str, side: str) -> float:
    """Return the realistic fill price for a paper simulation.

    Buy-to-open / buy-to-close fills at ask; sell-to-open / sell-to-close fills
    at bid.  This matches the user's preference for natural-side paper fills.
    """
    if position == "long" and side == "buy":
        return contract.ask
    if position == "short" and side == "sell":
        return contract.bid
    # Defensive fallback to mid for unexpected combos.
    return contract.midpoint


def _option_type_from_leg(leg: OptionLeg) -> str:
    """Infer call/put from the OCC symbol or the leg's side placeholder."""
    parsed = _parse_opra(leg.option_symbol)
    if parsed:
        return "call" if parsed[2] == "C" else "put"
    # Old placeholder format used side='call'|'put'.
    if leg.side in ("call", "put"):
        return leg.side
    raise ValueError(f"Cannot determine option type for {leg.option_symbol}")


def _target_expiry_from_leg(leg: OptionLeg) -> date:
    try:
        return _to_date(leg.expiry)
    except Exception:
        return date.today() + timedelta(days=30)


def resolve_option_order(order: OptionOrder, chain: list[OptionContract]) -> OptionOrder | None:
    """Rebuild an option order using real chain contracts.

    Returns a new ``OptionOrder`` with resolved legs, or ``None`` if any leg
    cannot be mapped to a liquid contract.
    """
    resolved_legs: list[OptionLeg] = []
    for leg in order.legs:
        option_type = _option_type_from_leg(leg)
        target_delta = target_delta_for_leg(order.strategy, option_type, leg.position)
        target_expiry = _target_expiry_from_leg(leg)
        contract = select_contract(
            chain,
            ctype=option_type,
            target_expiry=target_expiry,
            target_strike=leg.strike,
            target_delta=target_delta,
        )
        if contract is None:
            log.warning(
                "Could not resolve liquid contract for %s %s strike=%.2f expiry=%s",
                order.underlying,
                option_type,
                leg.strike,
                target_expiry,
            )
            return None
        resolved_legs.append(
            OptionLeg(
                side="buy" if leg.position == "long" else "sell",
                position=leg.position,
                option_symbol=contract.option_symbol,
                quantity=leg.quantity,
                strike=contract.strike,
                expiry=contract.expiry.isoformat(),
            )
        )
    return OptionOrder(
        underlying=order.underlying,
        strategy=order.strategy,
        legs=resolved_legs,
        max_loss=order.max_loss,
        expected_gain=order.expected_gain,
    )
