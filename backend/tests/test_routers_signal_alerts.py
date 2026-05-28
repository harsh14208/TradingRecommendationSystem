"""
Tests for routers/signal_alerts.py — per-ticker signal confidence alert rules.

Endpoints:
  GET    /api/alerts/signals/      list
  POST   /api/alerts/signals/      create
  PATCH  /api/alerts/signals/{id}  update
  DELETE /api/alerts/signals/{id}  delete
"""
import sys, os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from routers.signal_alerts import router
from services.auth_svc import get_current_user
from database import get_db
from models import User, SignalAlert

app = FastAPI()
app.include_router(router)


def _mock_user():
    return User(id=1, email="trader@example.com", is_owner=False,
                subscription_tier="pro", is_active=True, email_verified=True)


def _mock_alert(alert_id=1, ticker="NVDA", min_conf=72.0, action="BUY", active=True):
    a = MagicMock(spec=SignalAlert)
    a.id = alert_id
    a.user_id = 1
    a.ticker = ticker
    a.min_confidence = min_conf
    a.action_filter = action
    a.is_active = active
    return a


@pytest.fixture
def mock_db():
    db = AsyncMock()
    r = MagicMock()
    r.scalars.return_value.all.return_value = []
    r.scalar_one_or_none.return_value = None
    db.execute.return_value = r
    return db


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_current_user] = _mock_user
    async def _override_db():
        yield mock_db
    app.dependency_overrides[get_db] = _override_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


class TestListSignalAlerts:
    def test_empty_list(self, client, mock_db):
        r = MagicMock()
        r.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = r
        resp = client.get("/api/alerts/signals/")
        assert resp.status_code == 200
        assert resp.json()["alerts"] == []

    def test_returns_existing_alerts(self, client, mock_db):
        alert = _mock_alert()
        r = MagicMock()
        r.scalars.return_value.all.return_value = [alert]
        mock_db.execute.return_value = r
        resp = client.get("/api/alerts/signals/")
        assert resp.status_code == 200
        assert len(resp.json()["alerts"]) == 1
        assert resp.json()["alerts"][0]["ticker"] == "NVDA"


class TestCreateSignalAlert:
    def test_valid_buy_alert(self, client, mock_db):
        r = MagicMock()
        r.scalar_one_or_none.return_value = None  # no existing rule
        mock_db.execute.return_value = r
        created = _mock_alert()
        mock_db.refresh = AsyncMock()

        async def _fake_refresh(obj):
            obj.id = 1
        mock_db.refresh.side_effect = _fake_refresh

        resp = client.post("/api/alerts/signals/", json={
            "ticker": "NVDA",
            "min_confidence": 72.0,
            "action_filter": "BUY",
        })
        assert resp.status_code == 200
        assert mock_db.add.called
        added = mock_db.add.call_args[0][0]
        assert isinstance(added, SignalAlert)
        assert added.ticker == "NVDA"
        assert added.min_confidence == 72.0
        assert added.action_filter == "BUY"

    def test_invalid_ticker_422(self, client, mock_db):
        resp = client.post("/api/alerts/signals/", json={
            "ticker": "nvda123",  # lowercase + digits
            "min_confidence": 72.0,
        })
        assert resp.status_code == 422

    def test_confidence_out_of_range_422(self, client, mock_db):
        resp = client.post("/api/alerts/signals/", json={
            "ticker": "NVDA",
            "min_confidence": 110.0,
        })
        assert resp.status_code == 422

    def test_invalid_action_filter_422(self, client, mock_db):
        resp = client.post("/api/alerts/signals/", json={
            "ticker": "NVDA",
            "min_confidence": 70.0,
            "action_filter": "HOLD",  # not valid
        })
        assert resp.status_code == 422

    def test_duplicate_active_rule_409(self, client, mock_db):
        existing = _mock_alert()
        r = MagicMock()
        r.scalar_one_or_none.return_value = existing
        mock_db.execute.return_value = r
        resp = client.post("/api/alerts/signals/", json={
            "ticker": "NVDA",
            "min_confidence": 75.0,
        })
        assert resp.status_code == 409

    def test_any_action_filter_default(self, client, mock_db):
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = r
        mock_db.refresh = AsyncMock()

        resp = client.post("/api/alerts/signals/", json={
            "ticker": "AAPL",
            "min_confidence": 65.0,
        })
        assert resp.status_code == 200
        added = mock_db.add.call_args[0][0]
        assert added.action_filter == "any"


class TestUpdateSignalAlert:
    def test_update_confidence(self, client, mock_db):
        alert = _mock_alert()
        mock_db.get = AsyncMock(return_value=alert)
        resp = client.patch("/api/alerts/signals/1", json={"min_confidence": 80.0})
        assert resp.status_code == 200
        assert alert.min_confidence == 80.0

    def test_update_not_found_404(self, client, mock_db):
        mock_db.get = AsyncMock(return_value=None)
        resp = client.patch("/api/alerts/signals/999", json={"min_confidence": 80.0})
        assert resp.status_code == 404

    def test_deactivate_alert(self, client, mock_db):
        alert = _mock_alert()
        mock_db.get = AsyncMock(return_value=alert)
        resp = client.patch("/api/alerts/signals/1", json={"is_active": False})
        assert resp.status_code == 200
        assert alert.is_active is False


class TestDeleteSignalAlert:
    def test_delete_existing(self, client, mock_db):
        alert = _mock_alert()
        mock_db.get = AsyncMock(return_value=alert)
        resp = client.delete("/api/alerts/signals/1")
        assert resp.status_code == 200
        assert mock_db.delete.called

    def test_delete_not_owned_returns_403(self, client, mock_db):
        alert = _mock_alert()
        alert.user_id = 999  # different user
        mock_db.get = AsyncMock(return_value=alert)
        resp = client.delete("/api/alerts/signals/1")
        assert resp.status_code == 403
        assert not mock_db.delete.called
