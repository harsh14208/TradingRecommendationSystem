"""
DEPLOY-5: Locust load test for Signal.Trade API.

Usage:
    pip install locust
    cd backend
    locust -f tests/locustfile.py --headless -u 100 -r 10 --run-time 60s \
      --host http://localhost:8000

Target: p95 latency <500ms, 0 errors under 100 concurrent users.
"""

from locust import HttpUser, between, task


class SignalTradeUser(HttpUser):
    """Simulates an authenticated user reading signals and quotes."""

    wait_time = between(1, 3)

    def on_start(self):
        """Authenticate once per user — obtain a JWT token."""
        resp = self.client.post(
            "/api/auth/login",
            json={"email": "loadtest@example.com", "password": "LoadTest123!"},
            name="/api/auth/login",
        )
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token") or data.get("token", "")
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            # Fallback: proceed without auth (will get 401 on protected endpoints)
            self.headers = {}

    @task(5)
    def get_signals(self):
        """Most common read path — signal feed."""
        self.client.get("/api/signals", headers=self.headers, name="/api/signals")

    @task(3)
    def get_signals_paginated(self):
        """Paginated signal list — tests DB query performance."""
        self.client.get(
            "/api/signals?limit=20&offset=0",
            headers=self.headers,
            name="/api/signals?limit=20",
        )

    @task(2)
    def health_check(self):
        """Health endpoint — should always be fast (no auth needed)."""
        self.client.get("/api/health", name="/api/health")

    @task(2)
    def get_me(self):
        """User profile endpoint."""
        self.client.get("/api/me", headers=self.headers, name="/api/me")

    @task(2)
    def get_quotes(self):
        """Quote/snapshot endpoint for a representative ticker."""
        self.client.get(
            "/api/quotes/snapshot?ticker=AAPL",
            headers=self.headers,
            name="/api/quotes/snapshot",
        )

    @task(1)
    def get_scan_status(self):
        """Scanner status — used by frontend polling."""
        self.client.get(
            "/api/scan/status",
            headers=self.headers,
            name="/api/scan/status",
        )

    @task(1)
    def get_watchlist(self):
        """Watchlist endpoint."""
        self.client.get(
            "/api/watchlist",
            headers=self.headers,
            name="/api/watchlist",
        )

    @task(1)
    def get_public_track_record(self):
        """Public track record page — no auth needed."""
        self.client.get("/api/public/track-record", name="/api/public/track-record")


class AdminUser(HttpUser):
    """Simulates an owner doing admin reads — lower frequency."""

    wait_time = between(5, 15)
    weight = 1  # 1 admin per ~10 regular users

    def on_start(self):
        resp = self.client.post(
            "/api/auth/login",
            json={"email": "owner@example.com", "password": "OwnerTest123!"},
        )
        if resp.status_code == 200:
            token = resp.json().get("access_token", "")
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    @task(3)
    def admin_health(self):
        self.client.get("/api/health", name="/api/health (admin)")

    @task(2)
    def admin_setup_status(self):
        self.client.get(
            "/api/admin/setup-status",
            headers=self.headers,
            name="/api/admin/setup-status",
        )

    @task(1)
    def admin_analytics(self):
        self.client.get(
            "/api/admin/analytics-summary",
            headers=self.headers,
            name="/api/admin/analytics-summary",
        )

    @task(1)
    def admin_live_wr(self):
        self.client.get(
            "/api/admin/live-wr-stats",
            headers=self.headers,
            name="/api/admin/live-wr-stats",
        )
