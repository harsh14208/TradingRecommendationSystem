import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from routers.billing import router
from services.auth_svc import get_current_user
from models import User

app = FastAPI()
app.include_router(router, prefix="")

def override_get_current_user():
    u = User(id=1, email="test@example.com", stripe_customer_id="cus_test123")
    return u

app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)

def test_get_plans():
    response = client.get("/api/billing/plans")
    assert response.status_code == 200
    plans = response.json()
    assert isinstance(plans, list)
    # Router returns {id: <tier>} not {tier: <tier>}
    assert any(p["id"] == "basic" for p in plans)
    assert any(p["id"] == "pro" for p in plans)

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

def test_billing_webhook_checkout_session_completed():
    with patch("routers.billing.stripe.Webhook.construct_event") as mock_event:
        mock_event.return_value = MagicMock(
            type="checkout.session.completed",
            data=MagicMock(object=MagicMock(customer="cus_123", subscription="sub_123", metadata={"user_id": "1"}))
        )
        response = client.post("/api/billing/webhook", content=b"payload", headers={"Stripe-Signature": "sig"})
        assert response.status_code == 200

def test_billing_webhook_invalid_signature():
    try:
        from stripe.error import SignatureVerificationError
        with patch("routers.billing.stripe.Webhook.construct_event", side_effect=SignatureVerificationError("Invalid sig", "sig")):
            response = client.post("/api/billing/webhook", content=b"payload", headers={"Stripe-Signature": "invalid"})
            assert response.status_code == 400
    except ImportError:
        pass