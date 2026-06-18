"""Unit tests for routers/billing.py — billing status, plans, checkout."""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import User
from services.auth_svc import get_current_user


def _make_user(tier="free", status="active", stripe_id=None):
    u = User(
        id=1,
        email="t@t.com",
        is_owner=False,
        subscription_tier=tier,
        subscription_status=status,
    )
    u.stripe_customer_id = stripe_id
    u.subscription_period_end = None
    u.full_name = "Test User"
    return u


def _make_app(tier="free", status="active", stripe_id=None):
    from routers.billing import router

    app = FastAPI()
    app.include_router(router)
    user = _make_user(tier=tier, status=status, stripe_id=stripe_id)

    def _user():
        return user

    app.dependency_overrides[get_current_user] = _user
    return app


def _mock_db():
    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=MagicMock())
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def _get_db():
        yield mock_db

    return _get_db


# ── GET /api/billing/plans ────────────────────────────────────────────────────


def test_get_plans():
    app = _make_app()
    with TestClient(app) as client:
        resp = client.get("/api/billing/plans")
    assert resp.status_code == 200
    data = resp.json()
    assert any(p["id"] == "free" for p in data)
    assert any(p["id"] == "pro" for p in data)


# ── GET /api/billing/status ───────────────────────────────────────────────────


def test_billing_status_free():
    app = _make_app(tier="free", status="active")
    with TestClient(app) as client:
        resp = client.get("/api/billing/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["tier"] == "free"
    assert data["status"] == "active"


def test_billing_status_pro():
    app = _make_app(tier="pro", status="active")
    with TestClient(app) as client:
        resp = client.get("/api/billing/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["tier"] == "pro"
    assert data["grace_period_end"] is None
    assert data["cancellation_date"] is None
    assert data["downgrade_date"] is None


def test_billing_status_past_due():
    from datetime import datetime, timedelta

    app = _make_app(tier="basic", status="past_due")
    user = app.dependency_overrides[get_current_user]()
    user.subscription_period_end = datetime(2026, 6, 1)

    with TestClient(app) as client:
        resp = client.get("/api/billing/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["tier"] == "basic"
    assert data["status"] == "past_due"
    assert data["grace_period_end"] == (user.subscription_period_end + timedelta(days=15)).isoformat()


# ── POST /api/billing/checkout/{tier} ────────────────────────────────────────


def test_checkout_invalid_tier():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db()
    with TestClient(app) as client:
        resp = client.post("/api/billing/checkout/enterprise")
    assert resp.status_code == 400


def test_checkout_no_stripe_key():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db()
    settings = MagicMock()
    settings.stripe_secret_key = ""
    with patch("routers.billing.get_settings", return_value=settings):
        with TestClient(app) as client:
            resp = client.post("/api/billing/checkout/pro")
    assert resp.status_code == 503


def test_checkout_no_price_id():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db()
    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_123"
    settings.stripe_price_pro = ""
    settings.stripe_price_basic = ""
    settings.app_url = "https://example.com"
    with (
        patch("routers.billing.get_settings", return_value=settings),
        patch("routers.billing._price_id", return_value=""),
    ):
        with TestClient(app) as client:
            resp = client.post("/api/billing/checkout/pro")
    assert resp.status_code == 503


def test_checkout_success_new_customer():
    app = _make_app(stripe_id=None)
    app.dependency_overrides[get_db] = _mock_db()

    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_123"
    settings.stripe_price_pro = "price_pro_123"
    settings.app_url = "https://example.com"

    mock_stripe = MagicMock()
    mock_stripe.Customer.create.return_value = MagicMock(id="cus_new123")
    mock_stripe.checkout.Session.create.return_value = MagicMock(url="https://checkout.stripe.com/session")

    with (
        patch("routers.billing.get_settings", return_value=settings),
        patch("routers.billing._stripe", return_value=mock_stripe),
        patch("routers.billing._price_id", return_value="price_pro_123"),
    ):
        with TestClient(app) as client:
            resp = client.post("/api/billing/checkout/pro")
    assert resp.status_code == 200
    assert "checkout_url" in resp.json()


def test_checkout_existing_customer():
    app = _make_app(stripe_id="cus_existing123")
    app.dependency_overrides[get_db] = _mock_db()

    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_123"
    settings.stripe_price_basic = "price_basic_123"
    settings.app_url = "https://example.com"

    mock_stripe = MagicMock()
    mock_stripe.checkout.Session.create.return_value = MagicMock(url="https://checkout.stripe.com/session2")

    with (
        patch("routers.billing.get_settings", return_value=settings),
        patch("routers.billing._stripe", return_value=mock_stripe),
        patch("routers.billing._price_id", return_value="price_basic_123"),
    ):
        with TestClient(app) as client:
            resp = client.post("/api/billing/checkout/basic")
    assert resp.status_code == 200


# ── POST /api/billing/portal ──────────────────────────────────────────────────


def test_portal_no_stripe_key():
    app = _make_app(stripe_id="cus_123")
    app.dependency_overrides[get_db] = _mock_db()
    settings = MagicMock()
    settings.stripe_secret_key = ""
    with patch("routers.billing.get_settings", return_value=settings):
        with TestClient(app) as client:
            resp = client.post("/api/billing/portal")
    assert resp.status_code == 503


def test_portal_no_customer_id():
    app = _make_app(stripe_id=None)
    app.dependency_overrides[get_db] = _mock_db()
    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_123"
    with patch("routers.billing.get_settings", return_value=settings):
        with TestClient(app) as client:
            resp = client.post("/api/billing/portal")
    assert resp.status_code == 400


def test_portal_success():
    app = _make_app(stripe_id="cus_123")
    app.dependency_overrides[get_db] = _mock_db()

    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_123"
    settings.app_url = "https://example.com"

    mock_stripe = MagicMock()
    mock_stripe.billing_portal.Session.create.return_value = MagicMock(url="https://billing.stripe.com/portal")

    with (
        patch("routers.billing.get_settings", return_value=settings),
        patch("routers.billing._stripe", return_value=mock_stripe),
    ):
        with TestClient(app) as client:
            resp = client.post("/api/billing/portal")
    assert resp.status_code == 200
    assert "portal_url" in resp.json()


# ── POST /api/billing/webhook ─────────────────────────────────────────────────


def test_webhook_no_stripe_key():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db()
    settings = MagicMock()
    settings.stripe_secret_key = ""
    settings.stripe_webhook_secret = ""
    with patch("routers.billing.get_settings", return_value=settings):
        with TestClient(app) as client:
            resp = client.post("/api/billing/webhook", content=b"{}", headers={"stripe-signature": "sig"})
    assert resp.status_code in (200, 400, 500, 503)


def test_webhook_invalid_signature():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db()
    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_123"
    settings.stripe_webhook_secret = "whsec_123"

    import stripe

    mock_stripe = MagicMock()
    mock_stripe.Webhook.construct_event.side_effect = stripe.error.SignatureVerificationError("invalid", "sig")

    with (
        patch("routers.billing.get_settings", return_value=settings),
        patch("routers.billing._stripe", return_value=mock_stripe),
    ):
        with TestClient(app) as client:
            resp = client.post("/api/billing/webhook", content=b"{}", headers={"stripe-signature": "sig"})
    assert resp.status_code == 400


# ── Helper functions ──────────────────────────────────────────────────────────


def test_price_id_basic():
    settings = MagicMock()
    settings.stripe_price_basic = "price_basic_test"
    settings.stripe_price_pro = "price_pro_test"
    settings.stripe_price_elite = "price_elite_test"
    with patch("routers.billing.get_settings", return_value=settings):
        from routers.billing import _price_id

        assert _price_id("basic") == "price_basic_test"
        assert _price_id("pro") == "price_pro_test"
        assert _price_id("elite") == "price_elite_test"
        # "unknown" returns None (no fallback for invalid tiers)
        assert _price_id("unknown") is None


@patch("routers.billing.get_settings")
@patch("routers.billing._stripe")
def test_webhook_success_audit_logging(mock_stripe, mock_get_settings):
    from models import StripeEvent

    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_123"
    settings.stripe_webhook_secret = "whsec_123"
    settings.stripe_price_pro = "price_pro_id"
    mock_get_settings.return_value = settings

    # Simulate webhook event payload
    event_payload = {
        "id": "evt_test_audit_123",
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "object": "subscription",
                "id": "sub_test_123",
                "customer": "cus_test_123",
                "status": "active",
                "current_period_end": 1774880000,
                "items": {"data": [{"price": {"id": "price_pro_id"}}]},
            }
        },
    }

    mock_stripe_instance = MagicMock()
    mock_stripe_instance.Webhook.construct_event.return_value = event_payload
    mock_stripe.return_value = mock_stripe_instance

    mock_user = _make_user(tier="free", status="inactive", stripe_id="cus_test_123")

    mock_db = MagicMock()
    # Mock database execute results
    # First query is for existing StripeEvent (returns None)
    # Second query is for finding user by stripe customer id (returns mock_user)
    mock_existing_event = MagicMock()
    mock_existing_event.scalar_one_or_none.return_value = None

    mock_user_result = MagicMock()
    mock_user_result.scalars.return_value.all.return_value = [mock_user]
    mock_user_result.scalar_one_or_none.return_value = mock_user

    call_count = [0]

    async def _execute(query):
        call_count[0] += 1
        if call_count[0] == 1:
            return mock_existing_event
        else:
            return mock_user_result

    mock_db.execute = AsyncMock(side_effect=_execute)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.add = MagicMock()

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db

    with TestClient(app) as client:
        resp = client.post("/api/billing/webhook", json=event_payload, headers={"stripe-signature": "valid_sig"})

    assert resp.status_code == 200
    # Verify a StripeEvent row was created and added to DB
    assert mock_db.add.called
    added_obj = mock_db.add.call_args_list[0][0][0]
    assert isinstance(added_obj, StripeEvent)
    assert added_obj.event_id == "evt_test_audit_123"
    assert added_obj.customer_id == "cus_test_123"
    assert added_obj.subscription_id == "sub_test_123"
    assert added_obj.event_type == "customer.subscription.updated"
    assert added_obj.handler_result == "success"
    # Transition: from free:inactive to pro:active
    assert added_obj.transition == "free:inactive -> pro:active"


@patch("routers.billing.get_settings")
@patch("routers.billing._stripe")
def test_checkout_session_contains_correct_user_metadata(mock_stripe, mock_get_settings):
    # Creating a checkout session must embed the authenticated user's ID
    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_123"
    settings.stripe_price_pro = "price_pro_id"
    mock_get_settings.return_value = settings

    # Mock Customer create and Session create
    mock_customer = MagicMock()
    mock_customer.id = "cus_new_123"
    mock_stripe_instance = MagicMock()
    mock_stripe_instance.Customer.create.return_value = mock_customer

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/pay"
    mock_stripe_instance.checkout.Session.create.return_value = mock_session
    mock_stripe.return_value = mock_stripe_instance

    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()

    async def _get_db():
        yield mock_db

    # Authenticate as user with ID 1
    app = _make_app(tier="free", status="inactive", stripe_id=None)
    app.dependency_overrides[get_db] = _get_db

    with TestClient(app) as client:
        resp = client.post("/api/billing/checkout/pro")

    assert resp.status_code == 200
    assert resp.json()["checkout_url"] == "https://checkout.stripe.com/pay"

    # Assert Stripe Session.create was called with metadata containing the correct user_id
    mock_stripe_instance.checkout.Session.create.assert_called_once()
    kwargs = mock_stripe_instance.checkout.Session.create.call_args[1]
    assert kwargs["metadata"]["user_id"] == "1"
    assert kwargs["subscription_data"]["metadata"]["user_id"] == "1"


@patch("routers.billing.get_settings")
@patch("routers.billing._stripe")
def test_webhook_checkout_completed_only_mutates_metadata_user(mock_stripe, mock_get_settings):
    # Webhook checkout completed only updates the user matching metadata user_id
    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_123"
    settings.stripe_webhook_secret = "whsec_123"
    mock_get_settings.return_value = settings

    event_payload = {
        "id": "evt_checkout_123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_123",
                "subscription": "sub_123",
                # metadata user_id does NOT match other user's id (ID 1)
                "metadata": {"user_id": "999", "tier": "pro"},
            }
        },
    }

    mock_stripe_instance = MagicMock()
    mock_stripe_instance.Webhook.construct_event.return_value = event_payload
    mock_stripe.return_value = mock_stripe_instance

    # Other user in DB (with ID 1)
    other_user = _make_user(tier="free", status="inactive", stripe_id=None)

    mock_db = MagicMock()
    # Mock database execute results
    # First query is for existing StripeEvent (returns None)
    # Second query is for finding user by stripe customer id (returns None)
    mock_existing_event = MagicMock()
    mock_existing_event.scalar_one_or_none.return_value = None

    mock_user_result = MagicMock()
    mock_user_result.scalars.return_value.all.return_value = []
    mock_user_result.scalar_one_or_none.return_value = None

    call_count = [0]

    async def _execute(query):
        call_count[0] += 1
        if call_count[0] == 1:
            return mock_existing_event
        else:
            return mock_user_result

    async def _get(model, pk):
        if pk == 999:
            return None  # metadata user 999 does not exist
        if pk == 1:
            return other_user
        return None

    mock_db.execute = AsyncMock(side_effect=_execute)
    mock_db.get = AsyncMock(side_effect=_get)
    mock_db.commit = AsyncMock()
    mock_db.add = MagicMock()

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db

    with TestClient(app) as client:
        resp = client.post("/api/billing/webhook", json=event_payload, headers={"stripe-signature": "valid_sig"})

    assert resp.status_code == 200
    # Other user must NOT be mutated (tier remains free, status remains inactive)
    assert other_user.subscription_tier == "free"
    assert other_user.subscription_status == "inactive"
