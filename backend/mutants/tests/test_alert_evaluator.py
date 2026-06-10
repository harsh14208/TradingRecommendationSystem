"""Tests for services/alert_evaluator.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_db(alerts=None, user=None):
    db = AsyncMock()
    # scalars().all() for the initial fetch
    scalars_mock = MagicMock()
    scalars_mock.all = MagicMock(return_value=alerts or [])
    result_mock = MagicMock()
    result_mock.scalars = MagicMock(return_value=scalars_mock)
    db.execute = AsyncMock(return_value=result_mock)
    db.get = AsyncMock(return_value=user)
    db.commit = AsyncMock()
    return db


def _make_alert(ticker="AAPL", condition="above", target_price=150.0, user_id=1):
    a = MagicMock()
    a.ticker = ticker
    a.condition = condition
    a.target_price = target_price
    a.user_id = user_id
    a.is_active = True
    return a


def _make_user(chat_id="12345"):
    u = MagicMock()
    u.telegram_chat_id = chat_id
    return u


@pytest.mark.asyncio
async def test_no_alerts_returns_early():
    from services.alert_evaluator import evaluate_price_alerts

    db = _make_db(alerts=[])
    await evaluate_price_alerts(db)
    db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_above_condition_triggered():
    from services.alert_evaluator import evaluate_price_alerts

    alert = _make_alert(condition="above", target_price=150.0)
    user = _make_user("999")
    db = _make_db(alerts=[alert], user=user)

    with patch("services.alert_evaluator.get_info", AsyncMock(return_value={"price": 155.0})):
        await evaluate_price_alerts(db)

    assert alert.is_active is False
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_above_condition_not_triggered():
    from services.alert_evaluator import evaluate_price_alerts

    alert = _make_alert(condition="above", target_price=150.0)
    user = _make_user("999")
    db = _make_db(alerts=[alert], user=user)

    with patch("services.alert_evaluator.get_info", AsyncMock(return_value={"price": 140.0})):
        await evaluate_price_alerts(db)

    assert alert.is_active is True
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_below_condition_triggered():
    from services.alert_evaluator import evaluate_price_alerts

    alert = _make_alert(condition="below", target_price=100.0)
    user = _make_user("999")
    db = _make_db(alerts=[alert], user=user)

    with patch("services.alert_evaluator.get_info", AsyncMock(return_value={"price": 90.0})):
        await evaluate_price_alerts(db)

    assert alert.is_active is False
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_below_condition_not_triggered():
    from services.alert_evaluator import evaluate_price_alerts

    alert = _make_alert(condition="below", target_price=100.0)
    db = _make_db(alerts=[alert])

    with patch("services.alert_evaluator.get_info", AsyncMock(return_value={"price": 110.0})):
        await evaluate_price_alerts(db)

    assert alert.is_active is True


@pytest.mark.asyncio
async def test_no_price_in_info_skips():
    from services.alert_evaluator import evaluate_price_alerts

    alert = _make_alert(condition="above", target_price=150.0)
    db = _make_db(alerts=[alert])

    with patch("services.alert_evaluator.get_info", AsyncMock(return_value={})):
        await evaluate_price_alerts(db)

    assert alert.is_active is True


@pytest.mark.asyncio
async def test_exception_in_get_info_handled():
    from services.alert_evaluator import evaluate_price_alerts

    alert = _make_alert()
    db = _make_db(alerts=[alert])

    with patch("services.alert_evaluator.get_info", AsyncMock(side_effect=Exception("network error"))):
        await evaluate_price_alerts(db)  # should not raise

    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_triggered_user_no_telegram_chat_id():
    from services.alert_evaluator import evaluate_price_alerts

    alert = _make_alert(condition="above", target_price=100.0)
    user = _make_user(chat_id=None)
    db = _make_db(alerts=[alert], user=user)

    with patch("services.alert_evaluator.get_info", AsyncMock(return_value={"price": 110.0})):
        await evaluate_price_alerts(db)

    assert alert.is_active is False


@pytest.mark.asyncio
async def test_triggered_no_user_found():
    from services.alert_evaluator import evaluate_price_alerts

    alert = _make_alert(condition="above", target_price=100.0)
    db = _make_db(alerts=[alert], user=None)

    with patch("services.alert_evaluator.get_info", AsyncMock(return_value={"price": 110.0})):
        await evaluate_price_alerts(db)

    assert alert.is_active is False


@pytest.mark.asyncio
async def test_multiple_tickers_grouped():
    from services.alert_evaluator import evaluate_price_alerts

    a1 = _make_alert(ticker="AAPL", condition="above", target_price=100.0)
    a2 = _make_alert(ticker="GOOG", condition="below", target_price=200.0)
    db = _make_db(alerts=[a1, a2])

    async def _fake_info(ticker):
        return {"price": 150.0 if ticker == "AAPL" else 150.0}

    with patch("services.alert_evaluator.get_info", side_effect=_fake_info):
        await evaluate_price_alerts(db)

    assert a1.is_active is False  # 150 >= 100 → triggered
    assert a2.is_active is False  # 150 <= 200 → triggered
