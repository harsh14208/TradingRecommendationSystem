import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from routers.watchlist_router import router
from services.auth_svc import get_current_user
from database import get_db
from models import User

app = FastAPI()
app.include_router(router, prefix="")


def override_get_current_user():
    # Mock a pro user to bypass basic tier checks
    return User(id=1, email="test@example.com", subscription_tier="pro", is_owner=False)


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


def test_add_watchlist_valid(client, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    response = client.post("/api/watchlist", json={"ticker": "TSLA"})
    assert response.status_code == 200
    assert response.json() == {"success": True, "ticker": "TSLA"}
    mock_db_session.commit.assert_awaited()


def test_add_watchlist_invalid_ticker(client, mock_db_session):
    response = client.post("/api/watchlist", json={"ticker": "INVALID123"})
    assert response.status_code == 422


def test_get_watchlist(client, mock_db_session):
    mock_result = MagicMock()

    item = MagicMock()
    item.ticker = "AAPL"
    item.company = "Apple"
    item.is_active = True

    mock_db_session.execute.return_value = mock_result
    mock_result.scalars().all.return_value = [item]

    response = client.get("/api/watchlist")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["ticker"] == "AAPL"
    assert data[0]["company"] == "Apple"
    assert data[0]["is_active"] is True


def test_delete_watchlist(client, mock_db_session):
    mock_item = MagicMock()
    mock_item.ticker = "AAPL"
    mock_item.is_active = True

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_item
    mock_db_session.execute.return_value = mock_result

    response = client.delete("/api/watchlist/AAPL")
    assert response.status_code == 200
    assert response.json() == {"success": True}
    mock_db_session.commit.assert_awaited()
    assert mock_item.is_active is False


def test_get_watchlist_seeds_from_config_when_empty(client, mock_db_session):
    """
    list_watchlist branch where `rows` is empty:
    - seed tickers from config.get_settings().tickers
    - db.add called for each ticker
    - db.commit called
    """
    class DummySettings:
        tickers = ["NVDA", "TSLA"]

    item1 = MagicMock()
    item1.ticker = "NVDA"
    item1.company = "NVDA"
    item1.is_active = True

    item2 = MagicMock()
    item2.ticker = "TSLA"
    item2.company = "TSLA"
    item2.is_active = True

    first_query = MagicMock()
    first_query.scalars().all.return_value = []

    second_query = MagicMock()
    second_query.scalars().all.return_value = [item1, item2]

    mock_db_session.execute.side_effect = [first_query, second_query]

    with patch("config.get_settings", return_value=DummySettings()):
        response = client.get("/api/watchlist")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {d["ticker"] for d in data} == {"NVDA", "TSLA"}

    assert mock_db_session.add.call_count == 2
    mock_db_session.commit.assert_awaited()


def test_add_watchlist_existing_item_reactivates(client, mock_db_session):
    """
    add_ticker branch:
    - existing item found -> set is_active True + company, commit, return success
    """
    existing_item = MagicMock()
    existing_item.ticker = "AAPL"
    existing_item.company = "OldCo"
    existing_item.is_active = False

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_item
    mock_db_session.execute.return_value = mock_result

    response = client.post("/api/watchlist", json={"ticker": "AAPL", "company": "NewCo"})
    assert response.status_code == 200
    assert response.json() == {"success": True, "ticker": "AAPL"}

    assert existing_item.is_active is True
    assert existing_item.company == "NewCo"
    mock_db_session.commit.assert_awaited()


def test_remove_watchlist_not_found_404(client, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    response = client.delete("/api/watchlist/UNKNOWN")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticker not found in watchlist"


def test_add_watchlist_trims_and_uppercases_ticker(client, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    response = client.post("/api/watchlist", json={"ticker": "  tsLa  "})
    assert response.status_code == 200
    assert response.json() == {"success": True, "ticker": "TSLA"}
    mock_db_session.commit.assert_awaited()


def test_delete_watchlist_case_insensitive(client, mock_db_session):
    mock_item = MagicMock()
    mock_item.ticker = "AAPL"
    mock_item.is_active = True

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_item
    mock_db_session.execute.return_value = mock_result

    response = client.delete("/api/watchlist/aapl")
    assert response.status_code == 200
    assert response.json() == {"success": True}
    mock_db_session.commit.assert_awaited()
    assert mock_item.is_active is False


def test_add_watchlist_existing_item_keeps_company_when_company_empty(client, mock_db_session):
    existing_item = MagicMock()
    existing_item.ticker = "AAPL"
    existing_item.company = "OldCo"
    existing_item.is_active = False

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_item
    mock_db_session.execute.return_value = mock_result

    response = client.post("/api/watchlist", json={"ticker": "AAPL", "company": ""})
    assert response.status_code == 200
    assert response.json() == {"success": True, "ticker": "AAPL"}

    assert existing_item.is_active is True
    # company expression: body.company (empty) -> falsy -> existing.company (OldCo) kept
    assert existing_item.company == "OldCo"
    mock_db_session.commit.assert_awaited()
