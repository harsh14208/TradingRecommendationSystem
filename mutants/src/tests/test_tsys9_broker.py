"""TSYS-9: runtime risk limits, broker reconciliation, credential key versioning."""

import types
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from services import broker_svc


def _result(scalar_value):
    r = MagicMock()
    r.scalar.return_value = scalar_value
    return r


def _user(**kw):
    defaults = dict(id=1, max_daily_orders=None, max_ticker_notional=None)
    defaults.update(kw)
    return types.SimpleNamespace(**defaults)


# ── TSYS-9b runtime risk limits ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_no_limits_set_does_not_query_or_block():
    db = AsyncMock()
    db.execute = AsyncMock()
    reason = await broker_svc.check_runtime_risk_limits(_user(), "NVDA", 100.0, db)
    assert reason is None
    db.execute.assert_not_called()  # both limits None → no DB work


@pytest.mark.asyncio
async def test_max_daily_orders_blocks_at_limit():
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_result(3))  # already 3 today
    reason = await broker_svc.check_runtime_risk_limits(_user(max_daily_orders=3), "NVDA", 100.0, db)
    assert reason is not None and "max_daily_orders" in reason


@pytest.mark.asyncio
async def test_max_ticker_notional_blocks_when_exceeded():
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_result(450.0))  # $450 already in NVDA today
    reason = await broker_svc.check_runtime_risk_limits(_user(max_ticker_notional=500.0), "NVDA", 100.0, db)
    assert reason is not None and "max_ticker_notional" in reason


@pytest.mark.asyncio
async def test_within_limits_passes():
    db = AsyncMock()
    # order_count query → 1, ticker_notional query → 50.0
    db.execute = AsyncMock(side_effect=[_result(1), _result(50.0)])
    reason = await broker_svc.check_runtime_risk_limits(
        _user(max_daily_orders=10, max_ticker_notional=1000.0), "NVDA", 100.0, db
    )
    assert reason is None


# ── TSYS-9d credential key versioning ────────────────────────────────────────


def test_encrypt_decrypt_roundtrip():
    ct = broker_svc.encrypt_credential("secret-key-123")
    assert ct != "secret-key-123"
    assert broker_svc.decrypt_credential(ct) == "secret-key-123"


def test_current_key_version():
    assert broker_svc.current_key_version() == broker_svc._BROKER_KEY_VERSION >= 1


def test_rotate_credential_preserves_plaintext():
    ct = broker_svc.encrypt_credential("rotate-me")
    rotated = broker_svc.rotate_credential(ct)
    assert rotated is not None
    assert broker_svc.decrypt_credential(rotated) == "rotate-me"


def test_decrypt_invalid_token_returns_none():
    assert broker_svc.decrypt_credential("not-a-valid-token") is None


# ── TSYS-9a broker reconciliation ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reconcile_updates_filled_and_flags_orphan(monkeypatch):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    matched = types.SimpleNamespace(
        id=11, user_id=1, alpaca_order_id="ord_filled", status="submitted", created_at=now, error_msg=None
    )
    orphan = types.SimpleNamespace(
        id=12,
        user_id=1,
        alpaca_order_id="ord_missing",
        status="submitted",
        created_at=now - timedelta(hours=48),
        error_msg=None,
    )

    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalars=lambda: MagicMock(all=lambda: [matched, orphan])))
    db.get = AsyncMock(
        return_value=types.SimpleNamespace(
            alpaca_key_enc="enc",
            alpaca_secret_enc="enc",
            auto_execute_broker="alpaca",
            alpaca_account_type="paper",
        )
    )
    db.commit = AsyncMock()

    monkeypatch.setattr(broker_svc, "decrypt_credential", lambda c: "key")
    # Patch the real module attribute — `from services import alpaca_rest` resolves
    # the package attribute, so a sys.modules swap alone would not take effect.
    import services.alpaca_rest as alpaca_rest

    monkeypatch.setattr(alpaca_rest, "get_orders", AsyncMock(return_value=[{"id": "ord_filled", "status": "filled"}]))

    summary = await broker_svc.reconcile_broker_orders(db)

    assert matched.status == "filled"
    assert orphan.status == "orphan"
    assert summary["updated"] == 1
    assert summary["orphaned"] == 1
    db.commit.assert_awaited()
