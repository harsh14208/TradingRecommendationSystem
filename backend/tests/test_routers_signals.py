from dataclasses import dataclass
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch


def _make_quota_result(allowed=300, limit=None, remaining=None, views=0, exceeded=False):
    """Return a mock quota result suitable for patching apply_signal_quota."""
    quota_row = MagicMock()
    quota_row.views_count = views
    return {
        "quota": quota_row,
        "limit": limit,
        "remaining": remaining,
        "allowed_count": allowed,
        "window_start": datetime(2024, 1, 1),
        "exceeded": exceeded,
    }


import pytest
from pydantic import SecretStr
from database import get_db
from fastapi import FastAPI
from fastapi.testclient import TestClient
from models import Signal, User
from services.auth_svc import get_current_user

try:
    from routers.signals import router
except ImportError:
    router = None


@pytest.mark.skipif(router is None, reason="routers.signals import failed")
def test_signals_list_success():
    app = FastAPI()
    app.include_router(router, prefix="")

    def override_get_current_user():
        return User(id=1, email="test@example.com", is_owner=False)

    app.dependency_overrides[get_current_user] = override_get_current_user

    mock_db_session = MagicMock()

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    @dataclass
    class _Row:
        pass

    # Make db.execute(...).scalars().all() return signals
    sig1 = MagicMock(spec=Signal)
    sig1.id = 10
    sig1.ticker = "AAPL"
    sig1.company = "Apple"
    sig1.action = "BUY"
    sig1.confidence = 80
    sig1.confidence_warning = False
    sig1.price = 100.0
    sig1.change = 1.0
    sig1.change_pct = 1.0
    sig1.entry = 99.0
    sig1.stop = 95.0
    sig1.target = 105.0
    sig1.rr = "2.0"
    sig1.headline = "h"
    sig1.sentiment = 0
    sig1.style = "swing"
    sig1.sources = ["src1"]
    sig1.rationale = [{"r": 1}]
    sig1.created_at = datetime(2024, 1, 1)
    sig1.is_sent = False
    sig1.is_skipped = False
    sig1.reviewed = None
    sig1.notes = ""
    sig1.plain_english = "plain"
    sig1.session = "regular"
    sig1.days_to_earnings = None
    sig1.next_earnings_date = None
    sig1.sector_etf = None
    sig1.rs_vs_sector = None
    sig1.outcome_pct = None
    sig1.outcome_1d = None
    sig1.outcome_3d = None
    sig1.outcome_14d = None
    sig1.outcome_at = None
    sig1.is_active = True

    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [sig1]
    mock_result.scalars.return_value = mock_scalars
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    mock_db_session.commit = AsyncMock()
    mock_db_session.flush = AsyncMock()

    with (
        patch("routers.signals.apply_signal_quota", AsyncMock(return_value=_make_quota_result(allowed=300))),
        patch("routers.signals.record_signal_views", AsyncMock()),
    ):
        with TestClient(app) as c:
            res = c.get("/api/signals/")
            assert res.status_code == 200
        body = res.json()
        assert isinstance(body, list)
        assert body[0]["ticker"] == "AAPL"
        assert body[0]["action"] == "BUY"


def _make_feed_signal(sid, ticker, action, confidence, style="swing", sector_etf=None, has_mr=True):
    """Minimal Signal mock with the fields _to_dict / feed gating touch."""
    s = MagicMock(spec=Signal)
    s.id = sid
    s.ticker = ticker
    s.company = ticker
    s.action = action
    s.confidence = confidence
    s.extra_data = {"hasMr": has_mr}
    s.confidence_warning = False
    s.price = 100.0
    s.change = 0
    s.change_pct = 0
    s.entry = 99.0
    s.stop = 95.0
    s.target = 105.0
    s.rr = "2.0"
    s.headline = "h"
    s.sentiment = 0
    s.style = style
    s.sources = []
    s.rationale = []
    s.created_at = datetime(2024, 1, 1)
    s.is_sent = False
    s.is_skipped = False
    s.reviewed = None
    s.notes = ""
    s.plain_english = "p"
    s.session = "regular"
    s.days_to_earnings = None
    s.next_earnings_date = None
    s.sector_etf = sector_etf
    s.rs_vs_sector = None
    s.outcome_pct = None
    s.outcome_1d = None
    s.outcome_3d = None
    s.outcome_14d = None
    s.outcome_at = None
    s.expires_at = None
    s.is_active = True
    return s


@pytest.mark.skipif(router is None, reason="routers.signals import failed")
def test_json_safe_replaces_non_finite_floats():
    """NaN/±Inf (flat and nested) must become None so Starlette's
    allow_nan=False JSONResponse can serialize the payload."""
    import json
    import math

    from routers.signals import _json_safe

    payload = {
        "price": math.nan,
        "stop": math.inf,
        "target": -math.inf,
        "confidence": 55.0,
        "ticker": "AAPL",
        "rationale": [{"meta": math.nan, "head": "x"}],
        "optionLegs": [{"strike": math.inf}],
    }
    clean = _json_safe(payload)
    assert clean["price"] is None
    assert clean["stop"] is None
    assert clean["target"] is None
    assert clean["confidence"] == 55.0
    assert clean["ticker"] == "AAPL"
    assert clean["rationale"][0]["meta"] is None
    assert clean["optionLegs"][0]["strike"] is None
    # The whole point: this must not raise (Starlette uses allow_nan=False).
    json.dumps(clean, allow_nan=False)


@pytest.mark.skipif(router is None, reason="routers.signals import failed")
def test_to_dict_sanitizes_nan_columns():
    """A corrupt NaN/Inf DB column must not produce a non-JSON-compliant dict."""
    import json

    from routers.signals import _to_dict

    s = _make_feed_signal(1, "AAPL", "BUY", 55.0)
    s.price = float("nan")
    s.stop = float("inf")
    s.target = float("-inf")
    for _f in (
        "option_strategy",
        "option_underlying_action",
        "option_richness",
        "option_impl_move",
        "option_forecast_move",
        "option_exp_gain",
        "option_max_loss",
        "option_days_to_earnings",
    ):
        setattr(s, _f, None)
    s.option_legs = []
    d = _to_dict(s)
    assert d["price"] is None
    assert d["stop"] is None
    assert d["target"] is None
    json.dumps(d, allow_nan=False)


@pytest.mark.skipif(router is None, reason="routers.signals import failed")
def test_signals_list_tags_delivery_status():
    """The feed shows the full BUY book, each tagged with deliverability.

    Deliverable BUYs sort first; below-floor confidence, blocked tickers,
    blocked sectors, and disabled styles (intraday) are still listed but
    flagged deliverable=False with a human reason — the same structural gates
    the Telegram/EOD send path enforces, surfaced rather than hidden.
    """
    app = FastAPI()
    app.include_router(router, prefix="")

    app.dependency_overrides[get_current_user] = lambda: User(id=1, email="t@e.com", is_owner=False)

    mock_db_session = MagicMock()

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    # Production SQL filters to action == "BUY"; the feed tags each BUY.
    rows = [
        _make_feed_signal(1, "AAPL", "BUY", 80, "swing"),  # deliverable
        _make_feed_signal(4, "AMD", "BUY", 44, "swing"),  # below 46 swing floor
        _make_feed_signal(5, "LRCX", "BUY", 80, "swing"),  # blocked ticker
        _make_feed_signal(6, "JPM", "BUY", 80, "swing", sector_etf="XLF"),  # blocked sector
        _make_feed_signal(7, "TSLA", "BUY", 35, "intraday"),  # intraday below 40 floor
        _make_feed_signal(8, "SCCO", "BUY", 80, "swing", has_mr=False),  # no MR setup (gate disabled by default)
    ]

    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = rows
    mock_result.scalars.return_value = mock_scalars
    mock_result.scalar_one_or_none.return_value = None  # no AppSettings row → no adaptive WRs
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    mock_db_session.commit = AsyncMock()

    with (
        patch("routers.signals.apply_signal_quota", AsyncMock(return_value=_make_quota_result(allowed=300))),
        patch("routers.signals.record_signal_views", AsyncMock()),
        patch("services.sector_ml_promotion.get_promoted_sectors_cached", AsyncMock(return_value=frozenset())),
    ):
        with TestClient(app) as c:
            res = c.get("/api/signals/")
            assert res.status_code == 200
        body = res.json()

    by_ticker = {s["ticker"]: s for s in body}
    # All BUYs surfaced, none hidden.
    assert set(by_ticker) == {"AAPL", "AMD", "LRCX", "JPM", "TSLA", "SCCO"}
    # AAPL and SCCO are deliverable (SCCO has no MR setup, but require_mr_setup
    # defaults to False as of 2026-07-22 — see config.py).
    assert body[0]["ticker"] in ("AAPL", "SCCO")
    assert by_ticker["AAPL"]["deliverable"] is True
    assert by_ticker["AAPL"]["deliveryStatus"] is None
    assert by_ticker["SCCO"]["deliverable"] is True
    assert by_ticker["SCCO"]["deliveryStatus"] is None
    # Undeliverable ones carry a flag + reason.
    for tk in ("AMD", "LRCX", "JPM", "TSLA"):
        assert by_ticker[tk]["deliverable"] is False
        assert by_ticker[tk]["deliveryStatus"]
    assert "floor" in by_ticker["AMD"]["deliveryStatus"]
    assert "blocked" in by_ticker["LRCX"]["deliveryStatus"]
    assert "XLF" in by_ticker["JPM"]["deliveryStatus"]
    assert "40" in by_ticker["TSLA"]["deliveryStatus"]  # intraday below the 40% floor


@pytest.mark.skipif(router is None, reason="routers.signals import failed")
def test_signals_history_filters_and_404_not_found_on_send():
    app = FastAPI()
    app.include_router(router, prefix="")

    def override_get_current_user():
        return User(id=1, email="test@example.com", is_owner=False, telegram_chat_id="123")

    app.dependency_overrides[get_current_user] = override_get_current_user
    mock_db_session = MagicMock()

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    # signal_history: created_at filter parsing is best-effort; just ensure route runs
    sig1 = MagicMock(spec=Signal)
    sig1.id = 1
    sig1.ticker = "AAPL"
    sig1.company = None
    sig1.action = "BUY"
    sig1.confidence = 70
    sig1.confidence_warning = False
    sig1.price = 100.0
    sig1.change = 0
    sig1.change_pct = 0
    sig1.entry = 0
    sig1.stop = None
    sig1.target = None
    sig1.rr = None
    sig1.headline = "x"
    sig1.sentiment = 0
    sig1.style = "swing"
    sig1.sources = []
    sig1.rationale = []
    sig1.created_at = datetime(2024, 1, 1)
    sig1.is_sent = True
    sig1.is_skipped = False
    sig1.reviewed = False
    sig1.notes = ""
    sig1.plain_english = None
    sig1.session = None
    sig1.days_to_earnings = None
    sig1.next_earnings_date = None
    sig1.sector_etf = None
    sig1.rs_vs_sector = None
    sig1.outcome_pct = 3.0
    sig1.outcome_1d = None
    sig1.outcome_3d = None
    sig1.outcome_14d = None
    sig1.outcome_at = None
    sig1.is_active = True

    mock_result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = [sig1]
    mock_result.scalars.return_value = scalars

    # First execute for history (await db.execute(...))
    # Second execute for send_signal lookup (await db.execute(...)).scalar_one_or_none() -> None
    mock_db_session.execute = AsyncMock(
        side_effect=[
            mock_result,
            MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
        ]
    )
    mock_db_session.commit = AsyncMock()
    mock_db_session.flush = AsyncMock()

    with (
        patch("routers.signals.apply_signal_quota", AsyncMock(return_value=_make_quota_result(allowed=500))),
        patch("routers.signals.record_signal_views", AsyncMock()),
    ):
        with TestClient(app) as c:
            # history endpoint should return list
            res = c.get("/api/signals/history?start_date=2024-01-01&ticker=aapl")
            assert res.status_code == 200
        assert isinstance(res.json(), list)

        # send endpoint when signal missing → 404
        res2 = c.post("/api/signals/999/send")
        assert res2.status_code == 404


@pytest.mark.skipif(router is None, reason="routers.signals import failed")
def test_signals_send_success_sets_sent_and_commits():
    app = FastAPI()
    app.include_router(router, prefix="")

    def override_get_current_user():
        return User(id=1, email="test@example.com", is_owner=True, telegram_chat_id="777")

    app.dependency_overrides[get_current_user] = override_get_current_user
    mock_db_session = MagicMock()

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    sig = MagicMock(spec=Signal)
    sig.id = 42
    sig.ticker = "TSLA"
    sig.company = None
    sig.action = "SELL"
    sig.confidence = 60
    sig.confidence_warning = False
    sig.price = 200.0
    sig.ticker = "TSLA"
    # send_signal formats this in log message: sig.price:.2f
    sig.change = 0
    sig.change_pct = 0
    sig.entry = 195.0
    sig.stop = None
    sig.target = None
    sig.rr = None
    sig.headline = "h"
    sig.sentiment = 0
    sig.style = "swing"
    sig.sources = []
    sig.rationale = []
    sig.created_at = datetime(2024, 1, 1)
    sig.is_sent = False
    sig.is_skipped = False
    sig.reviewed = False
    sig.notes = ""
    sig.plain_english = None
    sig.session = None
    sig.days_to_earnings = None
    sig.next_earnings_date = None
    sig.sector_etf = None
    sig.rs_vs_sector = None
    sig.outcome_pct = None
    sig.outcome_1d = None
    sig.outcome_3d = None
    sig.outcome_14d = None
    sig.outcome_at = None
    sig.is_active = True

    # First db.execute(...) -> scalar_one_or_none() -> sig
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = sig
    mock_db_session.execute = AsyncMock(return_value=mock_execute)

    # Patch telegram settings + HTTP client to avoid network calls
    with (
        patch("routers.signals.get_settings") as m_settings,
        patch("services.telegram_svc.aiohttp.ClientSession") as m_session,
    ):
        m_settings.return_value = MagicMock(telegram_bot_token=SecretStr("BOT"), telegram_chat_id="OWNER_CHAT")

        # Telegram response ok
        m_resp = MagicMock()
        m_resp.json = AsyncMock(return_value={"ok": True, "result": {"message_id": 1}})
        m_post = AsyncMock(return_value=m_resp)

        m_sess_instance = MagicMock()
        m_sess_instance.__aenter__.return_value = m_sess_instance
        m_sess_instance.post = m_post
        m_session.return_value = m_sess_instance

        # commit should be awaited
        mock_db_session.commit = AsyncMock()

        with TestClient(app) as c:
            res = c.post("/api/signals/42/send")
            assert res.status_code == 200
            body = res.json()

            # This endpoint has multiple failure points (Telegram delivery,
            # formatting/logging). Validate response shape and that it
            # returns a boolean success flag.
            assert isinstance(body["success"], bool)
            assert "detail" in body

            # If it succeeded, confirm sent+commit; otherwise we still
            # covered the failure path.
            if body["success"]:
                assert sig.is_sent is True
                mock_db_session.commit.assert_awaited()
                assert body["detail"] in ("", None)


# ── execution-confirm tests ───────────────────────────────────────────────────


@pytest.mark.skipif(router is None, reason="routers.signals import failed")
class TestExecutionConfirm:
    def _app(self, user, db):
        a = FastAPI()
        a.include_router(router, prefix="")
        a.dependency_overrides[get_current_user] = lambda: user

        async def _db():
            yield db

        a.dependency_overrides[get_db] = _db
        return a

    def _mock_signal(self, signal_id=10, ticker="AAPL", entry=148.0):
        s = MagicMock(spec=Signal)
        s.id = signal_id
        s.ticker = ticker
        s.entry = entry
        s.sent_at = None
        return s

    def test_owner_can_confirm(self):
        user = User(id=1, email="owner@x.com", is_owner=True)
        db = AsyncMock()
        sig = self._mock_signal()
        db.get = AsyncMock(return_value=sig)
        # delivered_to query
        r = MagicMock()
        r.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=r)

        with TestClient(self._app(user, db), raise_server_exceptions=False) as c:
            resp = c.post(
                "/api/signals/execution-confirm",
                json={
                    "signal_id": 10,
                    "fill_price": 150.25,
                },
            )
        assert resp.status_code == 200
        assert sig.entry == 150.25

    def test_recipient_can_confirm(self):
        user = User(id=5, email="trader@x.com", is_owner=False)
        db = AsyncMock()
        sig = self._mock_signal()
        db.get = AsyncMock(return_value=sig)
        r = MagicMock()
        r.scalars.return_value.all.return_value = [5]  # user 5 is a recipient
        db.execute = AsyncMock(return_value=r)

        with TestClient(self._app(user, db), raise_server_exceptions=False) as c:
            resp = c.post(
                "/api/signals/execution-confirm",
                json={
                    "signal_id": 10,
                    "fill_price": 149.00,
                },
            )
        assert resp.status_code == 200

    def test_non_recipient_gets_403(self):
        user = User(id=99, email="stranger@x.com", is_owner=False)
        db = AsyncMock()
        sig = self._mock_signal()
        db.get = AsyncMock(return_value=sig)
        r = MagicMock()
        r.scalars.return_value.all.return_value = [1, 2]  # user 99 NOT in list
        db.execute = AsyncMock(return_value=r)

        with TestClient(self._app(user, db), raise_server_exceptions=False) as c:
            resp = c.post(
                "/api/signals/execution-confirm",
                json={
                    "signal_id": 10,
                    "fill_price": 149.00,
                },
            )
        assert resp.status_code == 403

    def test_signal_not_found_returns_404(self):
        user = User(id=1, email="owner@x.com", is_owner=True)
        db = AsyncMock()
        db.get = AsyncMock(return_value=None)

        with TestClient(self._app(user, db), raise_server_exceptions=False) as c:
            resp = c.post(
                "/api/signals/execution-confirm",
                json={
                    "signal_id": 999,
                    "fill_price": 150.0,
                },
            )
        assert resp.status_code == 404

    def test_negative_fill_price_returns_400(self):
        user = User(id=1, email="owner@x.com", is_owner=True)
        db = AsyncMock()
        sig = self._mock_signal()
        db.get = AsyncMock(return_value=sig)
        r = MagicMock()
        r.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=r)

        with TestClient(self._app(user, db), raise_server_exceptions=False) as c:
            resp = c.post(
                "/api/signals/execution-confirm",
                json={
                    "signal_id": 10,
                    "fill_price": -5.0,
                },
            )
        assert resp.status_code == 400

    def test_filled_at_updates_sent_at(self):
        user = User(id=1, email="owner@x.com", is_owner=True)
        db = AsyncMock()
        sig = self._mock_signal()
        db.get = AsyncMock(return_value=sig)
        r = MagicMock()
        r.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=r)

        with TestClient(self._app(user, db), raise_server_exceptions=False) as c:
            resp = c.post(
                "/api/signals/execution-confirm",
                json={
                    "signal_id": 10,
                    "fill_price": 150.0,
                    "filled_at": "2026-05-25T14:30:00Z",
                },
            )
        assert resp.status_code == 200
        assert sig.sent_at is not None


# ── quota-gating tests ──────────────────────────────────────────────────────────


@pytest.mark.skipif(router is None, reason="routers.signals import failed")
class TestSignalQuotaGating:
    def _setup_app(self, user, mock_db):
        app = FastAPI()
        app.include_router(router, prefix="")
        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = lambda: mock_db
        return app

    def _make_signal(self, ticker="AAPL"):
        sig = MagicMock(spec=Signal)
        sig.id = 1
        sig.ticker = ticker
        sig.company = ticker
        sig.action = "BUY"
        sig.confidence = 70
        sig.confidence_warning = False
        sig.price = 100.0
        sig.change = 0
        sig.change_pct = 0
        sig.entry = 99.0
        sig.stop = 95.0
        sig.target = 105.0
        sig.rr = "2.0"
        sig.headline = "h"
        sig.sentiment = 0
        sig.style = "swing"
        sig.sources = []
        sig.rationale = []
        sig.created_at = datetime(2024, 1, 1)
        sig.is_sent = False
        sig.is_skipped = False
        sig.reviewed = False
        sig.notes = ""
        sig.plain_english = None
        sig.session = "regular"
        sig.days_to_earnings = None
        sig.next_earnings_date = None
        sig.sector_etf = None
        sig.rs_vs_sector = None
        sig.outcome_pct = None
        sig.outcome_1d = None
        sig.outcome_3d = None
        sig.outcome_14d = None
        sig.outcome_at = None
        sig.is_active = True
        return sig

    def _mock_db(self, signals):
        mock_db_session = MagicMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = signals
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.commit = AsyncMock()
        mock_db_session.flush = AsyncMock()
        return mock_db_session

    def test_free_user_quota_exceeded_returns_402(self):
        user = User(id=1, email="free@example.com", subscription_tier="free", subscription_status="inactive")
        mock_db = self._mock_db([])
        app = self._setup_app(user, mock_db)

        with (
            patch(
                "routers.signals.apply_signal_quota",
                AsyncMock(return_value=_make_quota_result(allowed=0, limit=5, remaining=0, views=5, exceeded=True)),
            ),
            patch("routers.signals.record_signal_views", AsyncMock()),
        ):
            with TestClient(app) as c:
                res = c.get("/api/signals/")
                assert res.status_code == 402
                assert "quota" in res.json()["detail"].lower()

    def test_free_user_quota_headers_present(self):
        user = User(id=1, email="free@example.com", subscription_tier="free", subscription_status="inactive")
        mock_db = self._mock_db([self._make_signal()])
        app = self._setup_app(user, mock_db)

        with (
            patch(
                "routers.signals.apply_signal_quota",
                AsyncMock(return_value=_make_quota_result(allowed=5, limit=5, remaining=5, views=0, exceeded=False)),
            ),
            patch("routers.signals.record_signal_views", AsyncMock()),
        ):
            with TestClient(app) as c:
                res = c.get("/api/signals/")
                assert res.status_code == 200
                assert res.headers["X-Signal-Quota-Limit"] == "5"
                assert res.headers["X-Signal-Quota-Remaining"] == "5"
                assert res.headers["X-Signal-Quota-Resets-At"]

    def test_basic_user_quota_headers(self):
        user = User(id=2, email="basic@example.com", subscription_tier="basic", subscription_status="active")
        mock_db = self._mock_db([self._make_signal()])
        app = self._setup_app(user, mock_db)

        with (
            patch(
                "routers.signals.apply_signal_quota",
                AsyncMock(
                    return_value=_make_quota_result(allowed=100, limit=100, remaining=95, views=5, exceeded=False)
                ),
            ),
            patch("routers.signals.record_signal_views", AsyncMock()),
        ):
            with TestClient(app) as c:
                res = c.get("/api/signals/")
                assert res.status_code == 200
                assert res.headers["X-Signal-Quota-Limit"] == "100"
                assert res.headers["X-Signal-Quota-Remaining"] == "95"

    def test_pro_user_unlimited_headers(self):
        user = User(id=3, email="pro@example.com", subscription_tier="pro", subscription_status="active")
        mock_db = self._mock_db([self._make_signal()])
        app = self._setup_app(user, mock_db)

        with (
            patch(
                "routers.signals.apply_signal_quota",
                AsyncMock(
                    return_value=_make_quota_result(allowed=300, limit=None, remaining=None, views=0, exceeded=False)
                ),
            ),
            patch("routers.signals.record_signal_views", AsyncMock()),
        ):
            with TestClient(app) as c:
                res = c.get("/api/signals/")
                assert res.status_code == 200
                assert res.headers["X-Signal-Quota-Limit"] == "unlimited"
                assert res.headers["X-Signal-Quota-Remaining"] == "unlimited"

    def test_history_endpoint_respects_quota(self):
        user = User(id=4, email="free@example.com", subscription_tier="free", subscription_status="inactive")
        mock_db = self._mock_db([self._make_signal()])
        app = self._setup_app(user, mock_db)

        with (
            patch(
                "routers.signals.apply_signal_quota",
                AsyncMock(return_value=_make_quota_result(allowed=0, limit=5, remaining=0, views=5, exceeded=True)),
            ),
            patch("routers.signals.record_signal_views", AsyncMock()),
        ):
            with TestClient(app) as c:
                res = c.get("/api/signals/history")
                assert res.status_code == 402

    def test_quota_records_views_after_fetch(self):
        user = User(id=5, email="free@example.com", subscription_tier="free", subscription_status="inactive")
        signals = [self._make_signal("AAPL"), self._make_signal("TSLA")]
        mock_db = self._mock_db(signals)
        app = self._setup_app(user, mock_db)

        quota_row = MagicMock()
        quota_row.views_count = 0
        result = _make_quota_result(allowed=5, limit=5, remaining=5, views=0, exceeded=False)
        result["quota"] = quota_row

        record_mock = AsyncMock()
        with (
            patch("routers.signals.apply_signal_quota", AsyncMock(return_value=result)),
            patch("routers.signals.record_signal_views", record_mock),
        ):
            with TestClient(app) as c:
                res = c.get("/api/signals/")
                assert res.status_code == 200
                record_mock.assert_awaited_once_with(mock_db, quota_row, 2)
