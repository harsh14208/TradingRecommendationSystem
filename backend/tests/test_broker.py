"""
Tests for broker execution feature:
  - services/broker_svc.py  (encryption, execute_signal_for_user)
  - routers/broker.py       (connect, status, disconnect, settings, orders)
  - services/alpaca_rest.py (place_notional_order, live base URL)
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _patch_alpaca_account():
    """Provide a healthy Alpaca account so drawdown fail-closed logic doesn't block broker tests."""
    with patch(
        "services.alpaca_rest.get_account",
        new_callable=AsyncMock,
        return_value={"equity": "10000.00", "unrealized_pl": "0.00"},
    ):
        yield


# ── Helpers ───────────────────────────────────────────────────────────────────


def _mock_aiohttp_session(json_return=None, status=200):
    resp = AsyncMock()
    resp.status = status
    resp.json = AsyncMock(return_value=json_return or {})
    resp.raise_for_status = MagicMock()

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=resp)
    cm.__aexit__ = AsyncMock(return_value=False)

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.get = MagicMock(return_value=cm)
    session.post = MagicMock(return_value=cm)
    session.delete = MagicMock(return_value=cm)
    return session


def _make_user(**kwargs):
    """Build a minimal User-like object for testing."""
    u = MagicMock()
    u.id = 1
    u.is_owner = False
    u.subscription_tier = "pro"
    u.subscription_status = "active"
    u.auto_execute = True
    u.auto_execute_broker = "alpaca"
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


# ── broker_svc: encryption ────────────────────────────────────────────────────


def test_encrypt_decrypt_roundtrip():
    from services.broker_svc import decrypt_credential, encrypt_credential

    plaintext = "PK_TEST_abc123"
    token = encrypt_credential(plaintext)
    assert token != plaintext
    result = decrypt_credential(token)
    assert result == plaintext


def test_decrypt_invalid_token_returns_none():
    from services.broker_svc import decrypt_credential

    assert decrypt_credential("not-a-valid-fernet-token") is None


def test_decrypt_empty_returns_none():
    from services.broker_svc import decrypt_credential

    assert decrypt_credential("") is None


def test_encrypt_produces_stable_bytes():
    from services.broker_svc import decrypt_credential, encrypt_credential

    plain = "my-secret-key"
    enc1 = encrypt_credential(plain)
    enc2 = encrypt_credential(plain)
    # Fernet uses random IV — ciphertexts differ but both decrypt correctly
    assert decrypt_credential(enc1) == plain
    assert decrypt_credential(enc2) == plain


# ── broker_svc: verify_alpaca_connection ─────────────────────────────────────


@pytest.mark.asyncio
async def test_verify_alpaca_connection_success():
    from services.broker_svc import verify_alpaca_connection

    fake_account = {"status": "ACTIVE", "equity": "50000"}
    with patch("services.alpaca_rest.get_account", new_callable=AsyncMock, return_value=fake_account):
        result = await verify_alpaca_connection("key", "secret", live=False)
    assert result["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_verify_alpaca_connection_bad_status():
    from services.broker_svc import verify_alpaca_connection

    bad_account = {"status": "ONBOARDING"}
    with patch("services.alpaca_rest.get_account", new_callable=AsyncMock, return_value=bad_account):
        with pytest.raises(ValueError, match="ONBOARDING"):
            await verify_alpaca_connection("key", "secret", live=False)


@pytest.mark.asyncio
async def test_verify_alpaca_connection_network_error():
    from services.broker_svc import verify_alpaca_connection

    with patch("services.alpaca_rest.get_account", new_callable=AsyncMock, side_effect=Exception("timeout")):
        with pytest.raises(ValueError, match="Could not connect"):
            await verify_alpaca_connection("key", "secret", live=False)


# ── broker_svc: execute_signal_for_user ──────────────────────────────────────


@pytest.mark.asyncio
async def test_execute_signal_no_credentials_skips():
    from services.broker_svc import execute_signal_for_user

    user = _make_user(alpaca_key_enc=None, alpaca_secret_enc=None)
    db = AsyncMock()

    await execute_signal_for_user(user, {"ticker": "AAPL", "action": "BUY"}, None, db)

    db.add.assert_not_called()


@pytest.mark.asyncio
async def test_execute_signal_bad_action_skips():
    from services.broker_svc import encrypt_credential, execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=encrypt_credential("SECRET"),
        alpaca_account_type="paper",
    )
    db = AsyncMock()

    await execute_signal_for_user(user, {"ticker": "AAPL", "action": "HOLD"}, None, db)

    db.add.assert_not_called()


@pytest.mark.asyncio
async def test_execute_signal_buy_places_notional_order():
    from services.broker_svc import encrypt_credential, execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=encrypt_credential("SECRET"),
        alpaca_account_type="paper",
        auto_execute_qty_dollars=200.0,
    )
    db = AsyncMock()
    fake_order = {"id": "abc123", "status": "pending_new"}

    with patch("services.alpaca_rest.place_notional_order", new_callable=AsyncMock, return_value=fake_order):
        await execute_signal_for_user(
            user, {"ticker": "AAPL", "action": "BUY", "positionSizeScale": 1.0, "confidence": 100.0}, 42, db
        )

    db.add.assert_called_once()
    order_record = db.add.call_args[0][0]
    assert order_record.symbol == "AAPL"
    assert order_record.side == "buy"
    assert order_record.notional == 200.0
    assert order_record.alpaca_order_id == "abc123"
    # Raw Alpaca statuses (e.g. "pending_new") are normalized to the
    # broker_orders CheckConstraint vocabulary, not stored verbatim.
    assert order_record.status == "submitted"


@pytest.mark.asyncio
async def test_execute_signal_scales_notional_by_position_size():
    from services.broker_svc import encrypt_credential, execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=encrypt_credential("SECRET"),
        alpaca_account_type="paper",
        auto_execute_qty_dollars=100.0,
    )
    db = AsyncMock()
    fake_order = {"id": "xyz", "status": "new"}

    with patch("services.alpaca_rest.place_notional_order", new_callable=AsyncMock, return_value=fake_order) as mock:
        await execute_signal_for_user(
            user, {"ticker": "TSLA", "action": "BUY", "positionSizeScale": 1.3, "confidence": 100.0}, 7, db
        )

    call_kwargs = mock.call_args
    # notional = 100 * 1.3 = 130
    assert (
        call_kwargs.kwargs.get("notional") == 130.0
        or call_kwargs[1].get("notional") == 130.0
        or call_kwargs[0][3] == 130.0
    )


@pytest.mark.asyncio
async def test_execute_signal_records_error_on_failure():
    from services.broker_svc import encrypt_credential, execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=encrypt_credential("SECRET"),
        alpaca_account_type="paper",
    )
    db = AsyncMock()

    with patch(
        "services.alpaca_rest.place_notional_order",
        new_callable=AsyncMock,
        side_effect=Exception("insufficient buying power"),
    ):
        await execute_signal_for_user(user, {"ticker": "NVDA", "action": "BUY", "confidence": 100.0}, None, db)

    db.add.assert_called_once()
    order_record = db.add.call_args[0][0]
    assert order_record.status == "error"
    assert "insufficient buying power" in (order_record.error_msg or "")


# ── alpaca_rest: base URL switching ──────────────────────────────────────────


def test_base_url_paper():
    from services.alpaca_rest import PAPER_BASE, _base

    assert _base(live=False) == PAPER_BASE


def test_base_url_live():
    from services.alpaca_rest import LIVE_BASE, _base

    assert _base(live=True) == LIVE_BASE


@pytest.mark.asyncio
async def test_place_notional_order_sends_correct_body():
    from services.alpaca_rest import place_notional_order

    session = _mock_aiohttp_session(json_return={"id": "o1", "status": "accepted"})
    with patch("aiohttp.ClientSession", return_value=session):
        result = await place_notional_order("KEY", "SECRET", "AAPL", 150.00, "buy", live=False)

    assert result["id"] == "o1"
    # Verify the body contained notional (not qty)
    call_kwargs = session.post.call_args
    body = call_kwargs[1].get("json") or call_kwargs.kwargs.get("json", {})
    assert "notional" in body
    assert body["notional"] == "150.0"
    assert "qty" not in body
    assert body["side"] == "buy"
    assert body["symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_place_notional_order_uses_live_url():
    from services.alpaca_rest import LIVE_BASE, place_notional_order

    session = _mock_aiohttp_session(json_return={"id": "o2", "status": "new"})
    with patch("aiohttp.ClientSession", return_value=session):
        await place_notional_order("KEY", "SECRET", "TSLA", 250.00, "buy", live=True)

    url = session.post.call_args[0][0]
    assert LIVE_BASE in url


# ── alpaca_rest: bracket order ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_place_bracket_order_sends_bracket_body():
    from services.alpaca_rest import place_bracket_order

    session = _mock_aiohttp_session(json_return={"id": "b1", "status": "accepted"})
    with patch("aiohttp.ClientSession", return_value=session):
        result = await place_bracket_order(
            "KEY", "SECRET", "AAPL", qty=0.5, side="buy", stop_price=170.0, take_profit_price=195.0, live=False
        )

    assert result["id"] == "b1"
    call_kwargs = session.post.call_args
    body = call_kwargs[1].get("json") or call_kwargs.kwargs.get("json", {})
    assert body["order_class"] == "bracket"
    assert body["stop_loss"]["stop_price"] == "170.0"
    assert body["take_profit"]["limit_price"] == "195.0"
    assert body["qty"] == "0.5"
    assert "notional" not in body


@pytest.mark.asyncio
async def test_submit_bracket_stop_order_sends_correct_body():
    from services.alpaca_rest import submit_bracket_stop_order

    session = _mock_aiohttp_session(json_return={"id": "b2", "status": "accepted"})
    with patch("aiohttp.ClientSession", return_value=session):
        result = await submit_bracket_stop_order(
            "KEY",
            "SECRET",
            "NVDA",
            notional=100.0,
            side="buy",
            stop_price=185.0,
            take_profit_price=210.0,
            entry_price=200.0,
            live=False,
        )

    assert result["id"] == "b2"
    call_kwargs = session.post.call_args
    body = call_kwargs[1].get("json") or call_kwargs.kwargs.get("json", {})
    assert body["order_class"] == "bracket"
    assert body["stop_loss"]["stop_price"] == "185.0"
    assert body["take_profit"]["limit_price"] == "210.0"
    assert body["notional"] == "100.0"


@pytest.mark.asyncio
async def test_submit_bracket_stop_order_oto_when_no_take_profit():
    from services.alpaca_rest import submit_bracket_stop_order

    session = _mock_aiohttp_session(json_return={"id": "n1", "status": "accepted"})
    with patch("aiohttp.ClientSession", return_value=session):
        result = await submit_bracket_stop_order(
            "KEY", "SECRET", "AAPL", notional=100.0, side="buy", stop_price=170.0, entry_price=None, live=False
        )
    assert result["id"] == "n1"
    call_kwargs = session.post.call_args
    body = call_kwargs[1].get("json") or call_kwargs.kwargs.get("json", {})
    assert body["order_class"] == "oto"
    assert "take_profit" not in body


# ── broker_svc: RISK-2 portfolio drawdown ────────────────────────────────────


@pytest.mark.asyncio
async def test_check_portfolio_drawdown_blocks_when_dd_exceeds_threshold():
    from services.broker_svc import check_portfolio_drawdown

    user = _make_user()
    bad_account = {"equity": "10000", "unrealized_pl": "-600"}  # −6% DD > −5% threshold

    with patch("services.alpaca_rest.get_account", new_callable=AsyncMock, return_value=bad_account):
        blocked = await check_portfolio_drawdown(user, "KEY", "SECRET", live=False)
    assert blocked is True


@pytest.mark.asyncio
async def test_check_portfolio_drawdown_allows_when_within_threshold():
    from services.broker_svc import check_portfolio_drawdown

    user = _make_user()
    ok_account = {"equity": "10000", "unrealized_pl": "-400"}  # −4% DD < −5% threshold

    with patch("services.alpaca_rest.get_account", new_callable=AsyncMock, return_value=ok_account):
        blocked = await check_portfolio_drawdown(user, "KEY", "SECRET", live=False)
    assert blocked is False


@pytest.mark.asyncio
async def test_execute_signal_skips_when_portfolio_dd_exceeded():
    from services.broker_svc import encrypt_credential, execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=encrypt_credential("SECRET"),
        alpaca_account_type="paper",
    )
    db = AsyncMock()

    with patch("services.broker_svc.check_portfolio_drawdown", new_callable=AsyncMock, return_value=True):
        await execute_signal_for_user(user, {"ticker": "AAPL", "action": "BUY"}, None, db)

    db.add.assert_not_called()


# ── routers/broker.py ─────────────────────────────────────────────────────────


def _make_app_with_broker_router():
    """Build a minimal FastAPI app with just the broker router for unit testing."""
    from fastapi import FastAPI

    from routers.broker import router

    app = FastAPI()
    app.include_router(router)
    return app


def test_broker_require_pro_raises_for_free_user():
    from routers.broker import _require_pro

    user = _make_user(subscription_tier="free", subscription_status="active", is_owner=False)
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        _require_pro(user)
    assert exc.value.status_code == 403


def test_broker_require_pro_passes_for_owner():
    from routers.broker import _require_pro

    user = _make_user(is_owner=True, subscription_tier="free")
    _require_pro(user)  # should not raise


def test_broker_require_pro_passes_for_pro_user():
    from routers.broker import _require_pro

    user = _make_user(is_owner=False, subscription_tier="pro", subscription_status="active")
    _require_pro(user)  # should not raise


def test_broker_require_pro_raises_for_basic_user():
    from routers.broker import _require_pro

    user = _make_user(is_owner=False, subscription_tier="basic", subscription_status="active")
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        _require_pro(user)
    assert exc.value.status_code == 403


# ── BrokerConnectIn validation ────────────────────────────────────────────────


def test_broker_connect_in_valid():
    from routers.broker import BrokerConnectIn

    body = BrokerConnectIn(broker="alpaca", account_type="paper", api_key="KEY", api_secret="SEC")
    assert body.broker == "alpaca"
    assert body.account_type == "paper"


def test_broker_connect_in_invalid_broker():
    from pydantic import ValidationError

    from routers.broker import BrokerConnectIn

    with pytest.raises(ValidationError):
        BrokerConnectIn(broker="robinhood", account_type="paper", api_key="K", api_secret="S")


def test_broker_connect_in_invalid_account_type():
    from pydantic import ValidationError

    from routers.broker import BrokerConnectIn

    with pytest.raises(ValidationError):
        BrokerConnectIn(broker="alpaca", account_type="demo", api_key="K", api_secret="S")


def test_broker_connect_in_empty_key():
    from pydantic import ValidationError

    from routers.broker import BrokerConnectIn

    with pytest.raises(ValidationError):
        BrokerConnectIn(broker="alpaca", account_type="paper", api_key="", api_secret="S")


# ── AutoExecuteSettingsIn validation ─────────────────────────────────────────


def test_auto_execute_settings_min_conf_out_of_range():
    from pydantic import ValidationError

    from routers.broker import AutoExecuteSettingsIn

    with pytest.raises(ValidationError):
        AutoExecuteSettingsIn(min_conf=110.0)


def test_auto_execute_settings_qty_below_one():
    from pydantic import ValidationError

    from routers.broker import AutoExecuteSettingsIn

    with pytest.raises(ValidationError):
        AutoExecuteSettingsIn(qty_dollars=0.5)


def test_auto_execute_settings_all_none_valid():
    from routers.broker import AutoExecuteSettingsIn

    body = AutoExecuteSettingsIn()
    assert body.enabled is None
    assert body.min_conf is None
    assert body.qty_dollars is None


# ── Kill switch ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_kill_switch_toggle_pauses_execution():
    from unittest.mock import AsyncMock, MagicMock

    from routers.admin import execution_kill_switch

    owner = MagicMock()
    owner.id = 1
    owner.is_owner = True

    # Simulate AppSettings row with execution_paused=False
    row = MagicMock()
    row.data = {"execution_paused": False}

    db = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none = MagicMock(return_value=row)
    db.execute = AsyncMock(return_value=execute_result)
    db.commit = AsyncMock()

    result = await execution_kill_switch(owner=owner, db=db)
    assert result["execution_paused"] is True


@pytest.mark.asyncio
async def test_kill_switch_toggle_resumes_execution():
    from unittest.mock import AsyncMock, MagicMock

    from routers.admin import execution_kill_switch

    owner = MagicMock()
    owner.id = 1
    owner.is_owner = True

    row = MagicMock()
    row.data = {"execution_paused": True}

    db = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none = MagicMock(return_value=row)
    db.execute = AsyncMock(return_value=execute_result)
    db.commit = AsyncMock()

    result = await execution_kill_switch(owner=owner, db=db)
    assert result["execution_paused"] is False


@pytest.mark.asyncio
async def test_scanner_skips_execution_when_kill_switch_active():
    from unittest.mock import AsyncMock, patch

    # Patch _load_db_settings to return paused=True and _market_hours_ok to True
    with (
        patch("services.scanner._market_hours_ok", new=AsyncMock(return_value=True)),
        patch("services.scanner._load_db_settings", new_callable=AsyncMock, return_value={"execution_paused": True}),
    ):
        from services.scanner import _maybe_auto_execute_for_signal

        sig = {"action": "BUY", "ticker": "AAPL", "confidence": 80}
        db = AsyncMock()

        await _maybe_auto_execute_for_signal(sig, 1, db)

        # Should return early — no DB execute call for users
        db.execute.assert_not_called()
