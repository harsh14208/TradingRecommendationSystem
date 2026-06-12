from unittest.mock import AsyncMock, MagicMock

import pytest
from database import get_db
from fastapi import FastAPI
from fastapi.testclient import TestClient
from models import User
from routers.settings_router import router
from services.auth_svc import get_current_user

app = FastAPI()
app.include_router(router, prefix="")


def override_get_current_user():
    return User(id=1, email="test@example.com", is_owner=True)


app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture
def mock_db_session():
    return AsyncMock()


@pytest.fixture
def client(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_get_settings(client, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = MagicMock(data={"theme": "dark"})
    mock_db_session.execute.return_value = mock_result
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json().get("theme") == "dark"


def test_update_settings(client, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = MagicMock(data={"theme": "dark"})
    mock_db_session.execute.return_value = mock_result
    response = client.put("/api/settings", json={"data": {"theme": "light"}})
    assert response.status_code == 200
