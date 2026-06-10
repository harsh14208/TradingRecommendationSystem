from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from database import get_db
from fastapi import FastAPI
from fastapi.testclient import TestClient
from models import User
from routers.auth import router

# Create an isolated FastAPI app for the auth router
app = FastAPI()
app.include_router(router, prefix="")


@pytest.fixture
def mock_db_session():
    """Creates an AsyncMock to simulate an async SQLAlchemy session."""
    return AsyncMock()


@pytest.fixture
def client(mock_db_session):
    """Overrides the get_db dependency to yield the mock session."""

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_login_success(client, mock_db_session):
    mock_user = User(
        id=1,
        email="trader@example.com",
        password_hash="hashed_password",
        is_owner=False,
        subscription_tier="free",
        is_active=True,
        email_verified=True,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db_session.execute.return_value = mock_result

    # Patch both password verification and current user dependency guard
    with (
        patch("routers.auth.verify_password", return_value=True),
        patch(
            "routers.auth.get_current_user",
            return_value=User(
                id=1,
                email="trader@example.com",
                is_owner=False,
                subscription_tier="free",
            ),
        ),
    ):
        response = client.post(
            "/api/auth/login",
            json={"email": "trader@example.com", "password": "correct_password"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    # refresh token is stored in an HttpOnly cookie by the router
    assert "token_type" in data


def test_login_user_not_found(client, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    response = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "password"},
    )

    assert response.status_code == 401
    # Router currently uses this exact message
    assert response.json()["detail"] == "Invalid email or password."


def test_login_invalid_password(client, mock_db_session):
    mock_user = User(id=1, email="trader@example.com", password_hash="hashed_password")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db_session.execute.return_value = mock_result

    with patch("routers.auth.verify_password", return_value=False):
        response = client.post(
            "/api/auth/login",
            json={"email": "trader@example.com", "password": "wrong_password"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_register_duplicate_email(client, mock_db_session):
    mock_user = User(id=1, email="existing@example.com")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db_session.execute.return_value = mock_result

    response = client.post(
        "/api/auth/register",
        json={
            "email": "existing@example.com",
            "password": "password",
            "full_name": "Existing User",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "An account with this email already exists."


def test_get_me(client, mock_db_session):
    from services.auth_svc import get_current_user

    app.dependency_overrides[get_current_user] = lambda: User(id=1, email="test@example.com")
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_logout(client, mock_db_session):
    from services.auth_svc import get_current_user

    app.dependency_overrides[get_current_user] = lambda: User(id=1, email="test@example.com")
    response = client.post("/api/auth/logout")
    assert response.status_code == 200


def test_forgot_password(client, mock_db_session):
    mock_user = User(id=1, email="trader@example.com")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db_session.execute.return_value = mock_result

    # Route always returns 200; patch email sending to avoid external deps.
    with patch("routers.auth.send_welcome"), patch.dict("os.environ", {"SMTP_HOST": "dummy_smtp"}):
        response = client.post(
            "/api/auth/forgot-password",
            json={"email": "trader@example.com"},
        )

    assert response.status_code == 200


def test_register_invalid_email(client, mock_db_session):
    response = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "password123", "full_name": "Test User"},
    )
    assert response.status_code == 422
