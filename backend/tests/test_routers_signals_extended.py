"""Extended tests for routers/signals.py — covering uncovered paths."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import Signal, User
from services.auth_svc import get_current_user


def _make_user(is_owner=True, tier="pro"):
    u = User(id=1, email="t@t.com", is_owner=is_owner, subscription_tier=tier, subscription_status="active")
    return u


def _make_signal(
    id=1,
    ticker="AAPL",
    action="BUY",
    confidence=75,
    is_active=True,
    is_sent=False,
    outcome_pct=None,
    outcome_1d=None,
    created_at=None,
):
    s = MagicMock(spec=Signal)
    s.id = id
    s.ticker = ticker
    s.company = "Apple Inc."
    s.action = action
    s.confidence = confidence
    s.confidence_warning = False
    s.price = 150.0
    s.change = 1.0
    s.change_pct = 0.67
    s.entry = 148.0
    s.stop = 142.0
    s.target = 160.0
    s.rr = "2.0"
    s.headline = "Strong momentum"
    s.sentiment = 0.8
    s.style = "swing"
    s.sources = ["RSI", "BB"]
    s.rationale = [{"factor": "RSI oversold"}]
    s.created_at = created_at or datetime(2026, 3, 1, 10, 0, 0)
    s.is_sent = is_sent
    s.is_skipped = False
    s.reviewed = None
    s.notes = ""
    s.plain_english = "Strong buy signal"
    s.session = "regular"
    s.days_to_earnings = 15
    s.next_earnings_date = None
    s.sector_etf = "XLK"
    s.rs_vs_sector = 1.2
    s.outcome_pct = outcome_pct
    s.outcome_1d = outcome_1d
    s.outcome_3d = None
    s.outcome_14d = None
    s.outcome_at = None
    s.is_active = is_active
    s.raw_score = 62.0
    return s


def _make_app(is_owner=True, tier="pro"):
    from routers.signals import router

    app = FastAPI()
    app.include_router(router)
    user = _make_user(is_owner=is_owner, tier=tier)

    def _user():
        return user

    app.dependency_overrides[get_current_user] = _user
    return app


def _mock_db_single(signal=None):
    mock_db = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = signal
    result.scalars.return_value.all.return_value = [signal] if signal else []
    mock_db.execute = AsyncMock(return_value=result)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def _get_db():
        yield mock_db

    return _get_db


def test_history_endpoint():
    signals = [
        _make_signal(1, "AAPL", outcome_pct=2.0, is_sent=True, created_at=datetime(2026, 3, 1)),
        _make_signal(2, "NVDA", outcome_pct=-1.0, is_sent=True, created_at=datetime(2026, 3, 2)),
    ]
    mock_db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = signals
    mock_db.execute = AsyncMock(return_value=result)

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        resp = client.get("/api/signals/history")
    assert resp.status_code == 200


def test_send_signal_success():
    sig = _make_signal(1, "AAPL", is_sent=False)
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db_single(sig)

    mock_settings = MagicMock()
    mock_settings.telegram_chat_id = "123456789"
    mock_settings.telegram_bot_token = "bot_token_abc"

    with (
        patch("routers.signals.get_settings", return_value=mock_settings),
        patch("services.telegram_svc.send_telegram_message", new_callable=AsyncMock, return_value=(True, "")),
    ):
        with TestClient(app) as client:
            resp = client.post("/api/signals/1/send")
    assert resp.status_code == 200


def test_send_signal_not_found():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db_single(None)
    with TestClient(app) as client:
        resp = client.post("/api/signals/999/send")
    assert resp.status_code == 404


def test_send_signal_blocked_ticker():
    """ACT-4(a): manual /send must reject BLOCKED_TICKERS (no MR edge)."""
    sig = _make_signal(1, "STT", is_sent=False)  # STT is in BLOCKED_TICKERS
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db_single(sig)
    with TestClient(app) as client:
        resp = client.post("/api/signals/1/send")
    assert resp.status_code == 400
    assert "blocked" in resp.json()["detail"].lower()


def test_skip_signal_success():
    sig = _make_signal(1, "AAPL", is_sent=False)
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db_single(sig)
    with TestClient(app) as client:
        resp = client.post("/api/signals/1/skip")
    assert resp.status_code == 200


def test_skip_signal_not_found():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db_single(None)
    with TestClient(app) as client:
        resp = client.post("/api/signals/999/skip")
    assert resp.status_code == 404


def test_review_signal_success():
    sig = _make_signal(1, "AAPL")
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db_single(sig)
    with TestClient(app) as client:
        resp = client.post("/api/signals/1/review", json={"reviewed": True, "notes": "good signal"})
    assert resp.status_code == 200


def test_update_notes():
    sig = _make_signal(1, "AAPL")
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db_single(sig)
    with TestClient(app) as client:
        resp = client.patch("/api/signals/1/notes", json={"notes": "updated note"})
    assert resp.status_code == 200


def test_manual_scan_owner():
    app = _make_app(is_owner=True)
    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=MagicMock())

    async def _get_db():
        yield mock_db

    app.dependency_overrides[get_db] = _get_db

    with (
        patch("services.scanner.run_scan", new_callable=AsyncMock, return_value=None),
        patch("routers.websocket_router.manager") as mock_mgr,
    ):
        mock_mgr.broadcast = AsyncMock()
        with TestClient(app) as client:
            resp = client.post("/api/signals/scan")
    assert resp.status_code == 200


def test_manual_scan_non_owner():
    app = _make_app(is_owner=False)
    with TestClient(app) as client:
        resp = client.post("/api/signals/scan")
    assert resp.status_code == 403


def test_backtest_stats_empty():
    mock_db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=result)

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        resp = client.get("/api/signals/backtest")
    assert resp.status_code == 200


def test_backtest_stats_with_data():
    signals = [_make_signal(i, "AAPL", outcome_pct=2.0 if i % 2 else -1.0, is_sent=True) for i in range(10)]
    mock_db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = signals
    mock_db.execute = AsyncMock(return_value=result)

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        resp = client.get("/api/signals/backtest")
    assert resp.status_code == 200


def test_track_record_endpoint():
    signals = [
        _make_signal(i, "AAPL", outcome_pct=1.5, is_sent=True, created_at=datetime(2026, 3, i + 1)) for i in range(5)
    ]
    mock_db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = signals
    mock_db.execute = AsyncMock(return_value=result)

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        resp = client.get("/api/signals/track-record")
    assert resp.status_code == 200


def test_backtest_horizons():
    signals = [_make_signal(i, "AAPL", outcome_pct=1.5, outcome_1d=0.5, is_sent=True) for i in range(5)]
    mock_db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = signals
    mock_db.execute = AsyncMock(return_value=result)

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        resp = client.get("/api/signals/backtest/horizons")
    assert resp.status_code == 200


def test_correlation_empty():
    mock_db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=result)

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        resp = client.get("/api/signals/correlation")
    assert resp.status_code == 200


def test_alpha_decay_endpoint():
    signals = [
        _make_signal(i, "AAPL", outcome_pct=1.5, outcome_1d=0.5, is_sent=True, created_at=datetime(2026, 3, i + 1))
        for i in range(8)
    ]
    mock_db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = signals
    mock_db.execute = AsyncMock(return_value=result)

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        resp = client.get("/api/signals/alpha-decay")
    assert resp.status_code == 200


def test_calibration_curve():
    signals = [
        _make_signal(i, "AAPL", confidence=60 + i, outcome_pct=1.0 if i % 2 else -0.5, is_sent=True) for i in range(20)
    ]
    mock_db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = signals
    mock_db.execute = AsyncMock(return_value=result)

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        resp = client.get("/api/signals/backtest/calibration")
    assert resp.status_code == 200


def test_sparkline():
    app = _make_app()
    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=MagicMock())

    async def _get_db():
        yield mock_db

    app.dependency_overrides[get_db] = _get_db
    import pandas as pd

    df = pd.DataFrame({"Close": [100.0, 101.0, 102.0]}, index=pd.date_range("2026-01-01", periods=3))
    with patch("services.market_data.get_history", new_callable=AsyncMock, return_value=df):
        with TestClient(app) as client:
            resp = client.get("/api/signals/AAPL/spark")
    assert resp.status_code == 200


def test_confidence_history_invalid_ticker():
    app = _make_app()
    with TestClient(app) as client:
        resp = client.get("/api/signals/../../../etc/passwd/confidence-history")
    assert resp.status_code in (400, 404, 422)


def test_factor_mining_results():
    app = _make_app()
    with patch("services.factor_miner.get_factor_mining_results", return_value={"factors": []}):
        with TestClient(app) as client:
            resp = client.get("/api/signals/factor-mining")
    assert resp.status_code == 200


def test_backfill_outcomes_non_owner():
    app = _make_app(is_owner=False)
    with TestClient(app) as client:
        resp = client.post("/api/signals/backtest/backfill")
    assert resp.status_code == 403


def test_best_outcome_logic():
    from routers.signals import _best_outcome

    s = MagicMock(spec=Signal)
    s.outcome_pct = 3.0
    s.outcome_3d = 2.0
    s.outcome_1d = 1.0
    s.outcome_14d = 4.0
    assert _best_outcome(s) == 3.0  # outcome_pct is first priority


def test_best_outcome_fallback():
    from routers.signals import _best_outcome

    s = MagicMock(spec=Signal)
    s.outcome_pct = None
    s.outcome_3d = None
    s.outcome_1d = 1.5
    s.outcome_14d = None
    assert _best_outcome(s) == 1.5


def test_outcome_horizon_logic():
    from routers.signals import _outcome_horizon

    s = MagicMock(spec=Signal)
    s.outcome_pct = 2.0
    s.outcome_3d = None
    s.outcome_1d = None
    s.outcome_14d = None
    assert _outcome_horizon(s) == "7d"  # outcome_pct maps to "7d"


def test_outcome_horizon_1d():
    from routers.signals import _outcome_horizon

    s = MagicMock(spec=Signal)
    s.outcome_pct = None
    s.outcome_3d = None
    s.outcome_1d = 0.5
    s.outcome_14d = None
    assert _outcome_horizon(s) == "1d"
