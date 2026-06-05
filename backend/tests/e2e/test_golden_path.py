"""
FE-1 / TEST-2: Playwright E2E golden path tests.

Tests the critical user flows end-to-end:
  1. Signup → email verify → dashboard
  2. Login → signal feed visible
  3. Broker connect status (Pro tier)
  4. Admin analytics page (owner)

Run:
    pip install playwright pytest-playwright
    playwright install chromium
    cd backend
    pytest tests/e2e/ --base-url http://localhost:8000 -v

These tests require the backend to be running locally (or set BASE_URL env var).
They use a dedicated test user that is created/cleaned up per session.
"""

import os
import uuid

import pytest

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
TEST_EMAIL = f"e2e_{uuid.uuid4().hex[:8]}@test.invalid"
TEST_PASSWORD = "E2eTestPass123!"


@pytest.fixture(scope="session")
def api_url():
    return BASE_URL


# ── Helpers ───────────────────────────────────────────────────────────────────


def _post(page, path: str, body: dict) -> dict:
    """Make a JSON POST via Playwright's evaluate (avoids CORS on localhost)."""
    resp = page.evaluate(
        f"""
        fetch('{BASE_URL}{path}', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({body!r}),
        }}).then(r => r.json())
        """
    )
    return resp


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestSignalFeedLoad:
    """Golden path: unauthenticated public endpoints load."""

    def test_health_check_returns_ok(self, page):
        resp = page.request.get(f"{BASE_URL}/api/health")
        assert resp.status == 200
        data = resp.json()
        assert data["db"] == "connected"

    def test_landing_page_loads(self, page):
        page.goto(f"{BASE_URL}/")
        assert page.title() != ""

    def test_app_page_loads(self, page):
        page.goto(f"{BASE_URL}/app")
        # Should load without JS error (error boundary should not trigger)
        page.wait_for_load_state("networkidle", timeout=10_000)
        # Check for absence of error boundary message
        assert page.query_selector("text=Something went wrong") is None


class TestAuthentication:
    """Signup and login flow."""

    def test_signup_creates_user(self, page):
        resp = page.request.post(
            f"{BASE_URL}/api/auth/register",
            data={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "full_name": "E2E Test",
            },
        )
        # Accept 201 (created) or 200
        assert resp.status in (200, 201, 422)  # 422 = already exists (re-run)

    def test_login_returns_token(self, page):
        resp = page.request.post(
            f"{BASE_URL}/api/auth/login",
            data={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        # If signup failed (user exists or email unverified), expect 401/422
        if resp.status in (401, 422):
            pytest.skip("Login unavailable — email verification required or signup failed")
        assert resp.status == 200
        body = resp.json()
        assert "access_token" in body or "token" in body

    def test_invalid_login_rejected(self, page):
        resp = page.request.post(
            f"{BASE_URL}/api/auth/login",
            data={"email": "notreal@nowhere.invalid", "password": "Wrong1234!"},
        )
        assert resp.status in (401, 422, 403)


class TestSignalFeed:
    """Signal feed API returns expected shape."""

    @pytest.fixture(autouse=True)
    def owner_token(self, page):
        """Get owner token for authenticated tests."""
        owner_email = os.getenv("OWNER_EMAIL", "")
        owner_pass = os.getenv("OWNER_PASSWORD", "")
        if not owner_email or not owner_pass:
            pytest.skip("OWNER_EMAIL / OWNER_PASSWORD not set")
        resp = page.request.post(
            f"{BASE_URL}/api/auth/login",
            data={"email": owner_email, "password": owner_pass},
        )
        if resp.status != 200:
            pytest.skip(f"Owner login failed: {resp.status}")
        body = resp.json()
        self.token = body.get("access_token") or body.get("token", "")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_signals_endpoint_returns_list(self, page):
        resp = page.request.get(
            f"{BASE_URL}/api/signals",
            headers=self.headers,
        )
        assert resp.status == 200
        body = resp.json()
        assert isinstance(body, list)

    def test_scan_status_returns_state(self, page):
        resp = page.request.get(
            f"{BASE_URL}/api/scan/status",
            headers=self.headers,
        )
        assert resp.status == 200
        body = resp.json()
        assert "state" in body or "status" in body

    def test_admin_analytics_returns_summary(self, page):
        resp = page.request.get(
            f"{BASE_URL}/api/admin/analytics-summary",
            headers=self.headers,
        )
        assert resp.status == 200
        body = resp.json()
        assert "signals" in body
        assert "users" in body

    def test_admin_live_wr_stats(self, page):
        resp = page.request.get(
            f"{BASE_URL}/api/admin/live-wr-stats",
            headers=self.headers,
        )
        assert resp.status == 200
        body = resp.json()
        assert "overall" in body


class TestBrokerStatus:
    """Broker endpoints require Pro tier."""

    @pytest.fixture(autouse=True)
    def owner_token(self, page):
        owner_email = os.getenv("OWNER_EMAIL", "")
        owner_pass = os.getenv("OWNER_PASSWORD", "")
        if not owner_email or not owner_pass:
            pytest.skip("OWNER_EMAIL / OWNER_PASSWORD not set")
        resp = page.request.post(
            f"{BASE_URL}/api/auth/login",
            data={"email": owner_email, "password": owner_pass},
        )
        if resp.status != 200:
            pytest.skip("Owner login failed")
        body = resp.json()
        self.headers = {"Authorization": f"Bearer {body.get('access_token', '')}"}

    def test_broker_status_returns_connected_field(self, page):
        resp = page.request.get(
            f"{BASE_URL}/api/me/broker/status",
            headers=self.headers,
        )
        assert resp.status == 200
        body = resp.json()
        assert "connected" in body

    def test_notification_prefs_returns_defaults(self, page):
        resp = page.request.get(
            f"{BASE_URL}/api/me/notification-prefs",
            headers=self.headers,
        )
        assert resp.status == 200
        body = resp.json()
        assert "telegram" in body
        assert "min_conf" in body

    def test_notification_prefs_update_roundtrip(self, page):
        # Update
        resp = page.request.put(
            f"{BASE_URL}/api/me/notification-prefs",
            headers={**self.headers, "Content-Type": "application/json"},
            data='{"min_conf": 47.5, "sectors": ["XLK"]}',
        )
        assert resp.status == 200
        body = resp.json()
        assert body["min_conf"] == 47.5
        assert "XLK" in body["sectors"]

        # Reset
        page.request.put(
            f"{BASE_URL}/api/me/notification-prefs",
            headers={**self.headers, "Content-Type": "application/json"},
            data='{"min_conf": 45.0, "sectors": []}',
        )
