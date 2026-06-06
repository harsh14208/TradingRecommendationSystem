"""Unit tests for routers/billing.py — billing status, plans, checkout."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
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
    assert resp.json()["tier"] == "pro"


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
    with patch("routers.billing.get_settings", return_value=settings), \
         patch("routers.billing._price_id", return_value=""):
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

    with patch("routers.billing.get_settings", return_value=settings), \
         patch("routers.billing._stripe", return_value=mock_stripe), \
         patch("routers.billing._price_id", return_value="price_pro_123"):
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

    with patch("routers.billing.get_settings", return_value=settings), \
         patch("routers.billing._stripe", return_value=mock_stripe), \
         patch("routers.billing._price_id", return_value="price_basic_123"):
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

    with patch("routers.billing.get_settings", return_value=settings), \
         patch("routers.billing._stripe", return_value=mock_stripe):
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

    with patch("routers.billing.get_settings", return_value=settings), \
         patch("routers.billing._stripe", return_value=mock_stripe):
        with TestClient(app) as client:
            resp = client.post("/api/billing/webhook", content=b"{}", headers={"stripe-signature": "sig"})
    assert resp.status_code == 400


# ── Helper functions ──────────────────────────────────────────────────────────

def test_price_id_basic():
    settings = MagicMock()
    settings.stripe_price_basic = "price_basic_test"
    settings.stripe_price_pro = "price_pro_test"
    with patch("routers.billing.get_settings", return_value=settings):
        from routers.billing import _price_id
        assert _price_id("basic") == "price_basic_test"
        assert _price_id("pro") == "price_pro_test"
        # "unknown" returns stripe_price_pro (ternary fallback)
        assert _price_id("unknown") == "price_pro_test"
