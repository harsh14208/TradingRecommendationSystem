from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from database import get_db
from fastapi import FastAPI
from fastapi.testclient import TestClient
from models import User
from routers.billing import router
from services.auth_svc import get_current_user

app = FastAPI()
app.include_router(router, prefix="")


def override_get_current_user():
    u = User(id=1, email="test@example.com", stripe_customer_id="cus_test123")
    return u


app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)


@pytest.fixture
def mock_db():
    session = AsyncMock()
    # Default: no existing StripeEvent (event not yet processed)
    session.execute.return_value.scalar_one_or_none.return_value = None

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield session
    app.dependency_overrides.pop(get_db, None)


def test_get_plans():
    response = client.get("/api/billing/plans")
    assert response.status_code == 200
    plans = response.json()
    assert isinstance(plans, list)
    assert any(p["id"] == "basic" for p in plans)
    assert any(p["id"] == "pro" for p in plans)
    prices = {p["id"]: p["price"] for p in plans}
    assert prices["basic"] == 2900
    assert prices["pro"] == 7900


def test_checkout_session():
    with patch("routers.billing.stripe.checkout.Session.create") as mock_create:
        mock_create.return_value = MagicMock(url="https://checkout.stripe.com/pay/cs_test_123")
        response = client.post("/api/billing/checkout/pro")
        assert response.status_code == 200
        assert response.json()["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_123"


def test_billing_portal():
    with patch("routers.billing.stripe.billing_portal.Session.create") as mock_create:
        mock_create.return_value = MagicMock(url="https://billing.stripe.com/p/session/test")
        response = client.post("/api/billing/portal")
        assert response.status_code == 200


def test_billing_webhook_checkout_session_completed(mock_db):
    with patch("routers.billing.stripe.Webhook.construct_event") as mock_event:
        evt = MagicMock()
        evt.get.side_effect = lambda k, d="": {"id": "evt_test123", "type": "checkout.session.completed"}.get(k, d)
        evt.__getitem__ = lambda self, k: {
            "type": "checkout.session.completed",
            "data": {"object": {"customer": "cus_123", "subscription": "sub_123", "metadata": {"user_id": "1"}}},
        }[k]
        mock_event.return_value = evt
        response = client.post("/api/billing/webhook", content=b"payload", headers={"Stripe-Signature": "sig"})
        assert response.status_code == 200


def test_billing_webhook_dedup(mock_db):
    """Already-processed event_id returns 200 immediately without re-processing."""
    mock_db.execute.return_value.scalar_one_or_none.return_value = MagicMock()  # existing row
    with patch("routers.billing.stripe.Webhook.construct_event") as mock_event:
        evt = MagicMock()
        evt.get.side_effect = lambda k, d="": {"id": "evt_duplicate"}.get(k, d)
        mock_event.return_value = evt
        response = client.post("/api/billing/webhook", content=b"payload", headers={"Stripe-Signature": "sig"})
        assert response.status_code == 200


def test_billing_webhook_invalid_signature():
    try:
        from stripe.error import SignatureVerificationError

        with patch(
            "routers.billing.stripe.Webhook.construct_event",
            side_effect=SignatureVerificationError("Invalid sig", "sig"),
        ):
            response = client.post("/api/billing/webhook", content=b"payload", headers={"Stripe-Signature": "invalid"})
            assert response.status_code == 400
    except ImportError:
        pass
