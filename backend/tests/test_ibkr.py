"""
Tests for Interactive Brokers (IBKR) integration:
  - services/ibkr_rest.py
  - services/broker_svc.py (verify_ibkr_connection, execute_signal_for_user)
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from services.broker_svc import encrypt_credential


def _mock_aiohttp_session(json_return=None, status=200):
    resp = AsyncMock()
    resp.status = status
    resp.json = AsyncMock(return_value=json_return or {})
    resp.raise_for_status = MagicMock()

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=resp)
    cm.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.get = MagicMock(return_value=cm)
    session.post = MagicMock(return_value=cm)
    session.delete = MagicMock(return_value=cm)
    return session


def _make_user(**kwargs):
    u = MagicMock()
    u.id = 42
    u.is_owner = False
    u.subscription_tier = "pro"
    u.subscription_status = "active"
    u.auto_execute = True
    u.auto_execute_broker = "ibkr"
    u.auto_execute_min_conf = 75.0
    u.auto_execute_qty_dollars = 100.0
    u.alpaca_key_enc = None
    u.alpaca_secret_enc = None
    u.alpaca_account_type = "paper"
    # TSYS-9b runtime risk limits default to unset (None) like a real User row.
    u.max_daily_orders = None
    u.max_ticker_notional = None
    for k, v in kwargs.items():
        setattr(u, k, v)
    return u


# ── verify_ibkr_connection tests ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_verify_ibkr_connection_success():
    from services.broker_svc import verify_ibkr_connection

    fake_account = {"id": "DU123", "status": "ACTIVE"}

    with patch("services.ibkr_rest.get_account", new_callable=AsyncMock, return_value=fake_account):
        result = await verify_ibkr_connection("token", "dummy", live=False)
        assert result["id"] == "DU123"


@pytest.mark.asyncio
async def test_verify_ibkr_connection_error():
    from services.broker_svc import verify_ibkr_connection

    with patch("services.ibkr_rest.get_account", new_callable=AsyncMock, side_effect=ValueError("Failed")):
        with pytest.raises(ValueError, match="Could not connect to IBKR"):
            await verify_ibkr_connection("token", "dummy", live=False)


# ── ibkr_rest client tests ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ibkr_rest_get_account():
    from services import ibkr_rest

    fake_accounts = [{"id": "DU123456", "currency": "USD"}]
    fake_ledger = {"USD": {"netliquidationvalue": 150000.0, "buyingpower": 400000.0, "unrealizedpnl": 1200.0}}

    # We need to mock ClientSession.get
    session = _mock_aiohttp_session()
    # First get call for accounts, second for ledger
    session.get = MagicMock(
        side_effect=[
            AsyncMock(
                __aenter__=AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value=fake_accounts)))
            ),
            AsyncMock(
                __aenter__=AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value=fake_ledger)))
            ),
        ]
    )

    with patch("aiohttp.ClientSession", return_value=session):
        res = await ibkr_rest.get_account("key", "secret")
        assert res["id"] == "DU123456"
        assert res["equity"] == "150000.0"
        assert res["buying_power"] == "400000.0"


@pytest.mark.asyncio
async def test_ibkr_rest_search_conid():
    from services import ibkr_rest

    fake_results = [{"conid": 265598, "symbol": "AAPL"}]
    session = _mock_aiohttp_session(json_return=fake_results)

    with patch("aiohttp.ClientSession", return_value=session):
        conid = await ibkr_rest.search_conid("AAPL", "key")
        assert conid == 265598


@pytest.mark.asyncio
async def test_ibkr_rest_place_order():
    from services import ibkr_rest

    fake_order_res = [{"id": "order_123", "status": "submitted"}]
    session = _mock_aiohttp_session()
    session.get = MagicMock(
        side_effect=[
            AsyncMock(
                __aenter__=AsyncMock(
                    return_value=AsyncMock(
                        status=200, json=AsyncMock(return_value=[{"id": "DU123", "currency": "USD"}])
                    )
                )
            ),
            AsyncMock(
                __aenter__=AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"USD": {}})))
            ),
        ]
    )
    session.post = MagicMock(
        side_effect=[
            AsyncMock(
                __aenter__=AsyncMock(
                    return_value=AsyncMock(status=200, json=AsyncMock(return_value=[{"conid": 265598}]))
                )
            ),  # search
            AsyncMock(
                __aenter__=AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value=fake_order_res)))
            ),  # order
        ]
    )

    with patch("aiohttp.ClientSession", return_value=session):
        res = await ibkr_rest.place_order("key", "secret", "AAPL", 10, "BUY")
        assert res["id"] == "order_123"


# ── execute_signal_for_user with IBKR ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_execute_signal_ibkr_notional():
    from services.broker_svc import execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=encrypt_credential("SECRET"),
        alpaca_account_type="paper",
        auto_execute_broker="ibkr",
    )

    db = AsyncMock()

    # Mock drawdown check to return False
    with patch("services.broker_svc.check_portfolio_drawdown", new_callable=AsyncMock, return_value=False):
        # Mock place_notional_order
        with patch(
            "services.ibkr_rest.place_notional_order",
            new_callable=AsyncMock,
            return_value={"id": "ibkr_123", "status": "filled"},
        ) as mock_place:
            await execute_signal_for_user(
                user,
                {"ticker": "AAPL", "action": "BUY", "price": 150.0, "positionSizeScale": 1.5, "confidence": 100.0},
                1,
                db,
            )

            # Assert notional order placed with $150 ($100 * 1.5 scale)
            mock_place.assert_called_once_with(
                "KEY", "SECRET", symbol="AAPL", notional=150.0, side="buy", live=False, entry_price=150.0
            )

            # Assert order was saved to database
            assert db.add.call_count == 1
            order = db.add.call_args[0][0]
            assert order.broker == "ibkr"
            assert order.alpaca_order_id == "ibkr_123"
            assert order.status == "filled"


@pytest.mark.asyncio
async def test_execute_signal_ibkr_no_secret_still_executes():
    """Regression: IBKR uses a single bearer token (no secret). A user connected
    via IBKR has alpaca_secret_enc=None — auto-execution must still run, not be
    silently skipped by the credential guard."""
    from services.broker_svc import execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("TOKEN"),
        alpaca_secret_enc=None,  # IBKR has no secret
        alpaca_account_type="paper",
        auto_execute_broker="ibkr",
    )

    db = AsyncMock()

    with patch("services.broker_svc.check_portfolio_drawdown", new_callable=AsyncMock, return_value=False):
        with patch(
            "services.ibkr_rest.place_notional_order",
            new_callable=AsyncMock,
            return_value={"id": "ibkr_999", "status": "filled"},
        ) as mock_place:
            await execute_signal_for_user(
                user, {"ticker": "AAPL", "action": "BUY", "price": 150.0, "confidence": 100.0}, 1, db
            )

            # Order placed despite missing secret (empty string passed through)
            mock_place.assert_called_once_with(
                "TOKEN", "", symbol="AAPL", notional=100.0, side="buy", live=False, entry_price=150.0
            )
            assert db.add.call_count == 1
            order = db.add.call_args[0][0]
            assert order.broker == "ibkr"
            assert order.alpaca_order_id == "ibkr_999"


@pytest.mark.asyncio
async def test_execute_signal_ibkr_bracket_stop():
    from services.broker_svc import execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=encrypt_credential("SECRET"),
        alpaca_account_type="paper",
        auto_execute_broker="ibkr",
    )

    db = AsyncMock()

    with patch("services.broker_svc.check_portfolio_drawdown", new_callable=AsyncMock, return_value=False):
        with patch(
            "services.ibkr_rest.submit_bracket_stop_order",
            new_callable=AsyncMock,
            return_value={"id": "ibkr_bracket", "status": "submitted"},
        ) as mock_bracket:
            await execute_signal_for_user(
                user,
                {
                    "ticker": "AAPL",
                    "action": "BUY",
                    "price": 150.0,
                    "stop": 140.0,
                    "target": 170.0,
                    "positionSizeScale": 1.0,
                    "confidence": 100.0,
                },
                1,
                db,
            )

            mock_bracket.assert_called_once_with(
                "KEY",
                "SECRET",
                symbol="AAPL",
                notional=100.0,
                side="buy",
                stop_price=140.0,
                take_profit_price=170.0,
                entry_price=150.0,
                live=False,
            )

            assert db.add.call_count == 1
            order = db.add.call_args[0][0]
            assert order.broker == "ibkr"
            assert order.alpaca_order_id == "ibkr_bracket"
