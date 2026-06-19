"""Tests for services/options_chain_resolver.py."""

from __future__ import annotations

from datetime import date

from services.brokers.options_broker import OptionLeg, OptionOrder
from services.options_chain_resolver import (
    OptionContract,
    filter_liquid_contracts,
    resolve_option_order,
    select_contract,
)


def _contract(
    option_symbol: str,
    ctype: str,
    strike: float,
    expiry: date,
    bid: float = 1.0,
    ask: float = 1.1,
    volume: int = 100,
    oi: int = 500,
    delta: float | None = None,
) -> OptionContract:
    mid = (bid + ask) / 2
    return OptionContract(
        option_symbol=option_symbol,
        underlying="AAPL",
        ctype=ctype,
        strike=strike,
        expiry=expiry,
        bid=bid,
        ask=ask,
        midpoint=mid,
        spread=ask - bid,
        spread_pct=(ask - bid) / mid,
        volume=volume,
        open_interest=oi,
        delta=delta,
        iv=0.30,
    )


def test_filter_liquid_contracts_rejects_wide_spreads() -> None:
    liquid = _contract("O:AAPL260717C00170000", "call", 170.0, date(2026, 7, 17), bid=1.0, ask=1.05)
    illiquid = _contract("O:AAPL260717C00180000", "call", 180.0, date(2026, 7, 17), bid=1.0, ask=3.0)
    result = filter_liquid_contracts([liquid, illiquid])
    assert len(result) == 1
    assert result[0].strike == 170.0


def test_select_contract_prefers_target_delta() -> None:
    expiry = date(2026, 7, 17)
    chain = [
        _contract("O:AAPL260717C00170000", "call", 170.0, expiry, delta=0.50),
        _contract("O:AAPL260717C00180000", "call", 180.0, expiry, delta=0.30),
        _contract("O:AAPL260717C00190000", "call", 190.0, expiry, delta=0.10),
    ]
    chosen = select_contract(chain, "call", expiry, target_delta=0.30)
    assert chosen is not None
    assert chosen.strike == 180.0


def test_select_contract_falls_back_to_target_strike() -> None:
    expiry = date(2026, 7, 17)
    chain = [
        _contract("O:AAPL260717C00170000", "call", 170.0, expiry),
        _contract("O:AAPL260717C00175000", "call", 175.0, expiry),
    ]
    chosen = select_contract(chain, "call", expiry, target_strike=176.0)
    assert chosen is not None
    assert chosen.strike == 175.0


def test_resolve_option_order_rebuilds_legs() -> None:
    expiry = date(2026, 7, 17)
    chain = [
        _contract("O:AAPL260717P00165000", "put", 165.0, expiry, delta=-0.30),
        _contract("O:AAPL260717P00170000", "put", 170.0, expiry, delta=-0.45),
    ]
    order = OptionOrder(
        underlying="AAPL",
        strategy="SELL_CASH_SEC_PUT",
        legs=[
            OptionLeg(
                side="sell",
                position="short",
                option_symbol="O:AAPL260717P00170000",
                quantity=1,
                strike=170.0,
                expiry=expiry.isoformat(),
            )
        ],
        max_loss=1000.0,
        expected_gain=50.0,
    )
    resolved = resolve_option_order(order, chain)
    assert resolved is not None
    assert len(resolved.legs) == 1
    assert resolved.legs[0].option_symbol == "O:AAPL260717P00165000"
    assert resolved.legs[0].strike == 165.0


def test_resolve_option_order_returns_none_when_illiquid() -> None:
    expiry = date(2026, 7, 17)
    chain = [
        _contract("O:AAPL260717C00170000", "call", 170.0, expiry, bid=1.0, ask=5.0),
    ]
    order = OptionOrder(
        underlying="AAPL",
        strategy="LONG_STRADDLE",
        legs=[
            OptionLeg(
                side="buy",
                position="long",
                option_symbol="O:AAPL260717C00170000",
                quantity=1,
                strike=170.0,
                expiry=expiry.isoformat(),
            )
        ],
        max_loss=1000.0,
        expected_gain=50.0,
    )
    assert resolve_option_order(order, chain) is None
