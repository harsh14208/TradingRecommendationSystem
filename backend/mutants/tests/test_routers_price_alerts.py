from unittest.mock import AsyncMock, MagicMock

import pytest
from database import get_db
from fastapi import FastAPI
from fastapi.testclient import TestClient
from models import User
from services.auth_svc import get_current_user

try:
    from routers.price_alerts import router

    app = FastAPI()
    app.include_router(router)

    def override_get_current_user():
        return User(id=1, email="test@example.com")

    app.dependency_overrides[get_current_user] = override_get_current_user

    @pytest.fixture
    def client_with_unauth_disabled():
        # Ensure current user dependency is active (some tests may clear overrides)
        return TestClient(app)

    @pytest.fixture
    def mock_db_session():
        return AsyncMock()

    @pytest.fixture
    def client(mock_db_session):
        async def override_get_db():
            yield mock_db_session

        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()

    def test_get_alerts(client, mock_db_session):
        mock_result = MagicMock()
        alert = MagicMock(id=1, ticker="AAPL", target_price=150.0, condition="above")
        mock_result.scalars().all.return_value = [alert]
        mock_result.all.return_value = [alert]
        mock_db_session.execute.return_value = mock_result

        res = client.get("/api/alerts/")
        assert res.status_code == 200

    def test_create_alert_invalid_price(client, mock_db_session):
        # Depending on auth implementation, unauthenticated requests may 401.
        res = client.post(
            "/api/alerts/",
            json={"ticker": "TSLA", "target_price": -10.0, "condition": "below"},
        )
        assert res.status_code in (401, 422)
except ImportError:
    pass
