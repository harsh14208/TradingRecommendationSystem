import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import stripe
from services.billing_reconciliation import reconcile_stripe_subscriptions
from models import User


@pytest.mark.asyncio
async def test_reconcile_no_stripe_key():
    mock_db = MagicMock()
    settings = MagicMock()
    settings.stripe_secret_key = ""

    with patch("services.billing_reconciliation.get_settings", return_value=settings):
        await reconcile_stripe_subscriptions(mock_db)

    # Database should not be queried if Stripe secret key is not set
    assert not mock_db.execute.called


@pytest.mark.asyncio
async def test_reconcile_subscription_active_match():
    # User in DB matches Stripe active Basic plan
    user = User(
        id=1,
        email="user@test.com",
        stripe_customer_id="cus_123",
        stripe_subscription_id="sub_123",
        subscription_tier="basic",
        subscription_status="active",
        subscription_period_end=None,
    )

    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [user]
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_key"
    settings.stripe_price_pro = "price_pro_id"

    # Mock stripe subscription retrieve
    mock_sub = {
        "status": "active",
        "current_period_end": 1774880000,
        "items": {"data": [{"price": {"id": "price_basic_id"}}]},
    }

    with (
        patch("services.billing_reconciliation.get_settings", return_value=settings),
        patch("stripe.Subscription.retrieve", return_value=mock_sub),
    ):
        await reconcile_stripe_subscriptions(mock_db)

    # Check database changes (period end was updated)
    assert user.subscription_status == "active"
    assert user.subscription_tier == "basic"
    assert user.subscription_period_end is not None
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_reconcile_subscription_mismatch_correction():
    # User DB status says active but Stripe says past_due
    user = User(
        id=1,
        email="user@test.com",
        stripe_customer_id="cus_123",
        stripe_subscription_id="sub_123",
        subscription_tier="pro",
        subscription_status="active",
        subscription_period_end=None,
    )

    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [user]
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_key"
    settings.stripe_price_pro = "price_pro_id"

    # Stripe says past_due Basic
    mock_sub = {
        "status": "past_due",
        "current_period_end": 1774880000,
        "items": {"data": [{"price": {"id": "price_basic_id"}}]},
    }

    with (
        patch("services.billing_reconciliation.get_settings", return_value=settings),
        patch("stripe.Subscription.retrieve", return_value=mock_sub),
    ):
        await reconcile_stripe_subscriptions(mock_db)

    # Check correction (status updated to past_due, tier remains pro if only active or downgrading)
    # Wait, in reconciliation logic: user.subscription_tier = tier if mapped_status == "active" else user.subscription_tier
    # Since mapped_status is "past_due", tier stays "pro". But status is updated to "past_due"
    assert user.subscription_status == "past_due"
    assert user.subscription_tier == "pro"
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_reconcile_subscription_not_found():
    # DB has subscription, but Stripe throws No such subscription
    user = User(
        id=1,
        email="user@test.com",
        stripe_customer_id="cus_123",
        stripe_subscription_id="sub_deleted",
        subscription_tier="basic",
        subscription_status="active",
    )

    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [user]
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_key"

    err = stripe.error.InvalidRequestError("No such subscription: sub_deleted", "param")

    with (
        patch("services.billing_reconciliation.get_settings", return_value=settings),
        patch("stripe.Subscription.retrieve", side_effect=err),
    ):
        await reconcile_stripe_subscriptions(mock_db)

    # Verify user was downgraded
    assert user.subscription_tier == "free"
    assert user.subscription_status == "canceled"
    assert user.stripe_subscription_id is None
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_reconcile_customer_missing_subscription_id():
    # DB has customer_id but no sub_id; Stripe has active subscription
    user = User(
        id=1,
        email="user@test.com",
        stripe_customer_id="cus_123",
        stripe_subscription_id=None,
        subscription_tier="free",
        subscription_status="inactive",
    )

    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [user]
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_key"
    settings.stripe_price_pro = "price_pro_id"

    mock_subs = {
        "data": [
            {
                "id": "sub_found",
                "status": "active",
                "current_period_end": 1774880000,
                "items": {"data": [{"price": {"id": "price_pro_id"}}]},
            }
        ]
    }

    with (
        patch("services.billing_reconciliation.get_settings", return_value=settings),
        patch("stripe.Subscription.list", return_value=mock_subs),
    ):
        await reconcile_stripe_subscriptions(mock_db)

    # Verify subscription was linked
    assert user.stripe_subscription_id == "sub_found"
    assert user.subscription_status == "active"
    assert user.subscription_tier == "pro"
    assert user.subscription_period_end is not None
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_reconcile_customer_inactive_no_active_subs():
    # DB says user has active Basic plan, but Stripe has no active subscriptions
    user = User(
        id=1,
        email="user@test.com",
        stripe_customer_id="cus_123",
        stripe_subscription_id=None,
        subscription_tier="basic",
        subscription_status="active",
    )

    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [user]
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_key"

    # Stripe says empty subscriptions
    mock_subs = {"data": []}

    with (
        patch("services.billing_reconciliation.get_settings", return_value=settings),
        patch("stripe.Subscription.list", return_value=mock_subs),
    ):
        await reconcile_stripe_subscriptions(mock_db)

    # Verify downgraded to free
    assert user.subscription_tier == "free"
    assert user.subscription_status == "canceled"
    assert mock_db.commit.called
