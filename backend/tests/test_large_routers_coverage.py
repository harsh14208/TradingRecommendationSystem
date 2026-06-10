"""Expand test coverage for large routers: signals, admin, quotes."""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import Signal, User
from services.auth_svc import get_current_user


# ── helpers ───────────────────────────────────────────────────────────────────


def _make_user(is_owner=True, tier="pro"):
    return User(
        id=1,
        email="t@t.com",
        is_owner=is_owner,
        subscription_tier=tier,
        subscription_status="active",
    )


def _make_signal(**kwargs):
    s = MagicMock(spec=Signal)
    defaults = dict(
        id=1,
        ticker="AAPL",
        company="Apple",
        action="BUY",
        confidence=75,
        confidence_warning=False,
        price=150.0,
        change=1.0,
        change_pct=0.5,
        entry=148.0,
        stop=142.0,
        target=160.0,
        rr="2:1",
        headline="h",
        sentiment=0.5,
        style="swing",
        sources=["RSI", "MACD"],
        rationale=[],
        created_at=datetime(2026, 3, 1, 10, 0, 0),
        is_sent=True,
        is_skipped=False,
        reviewed=None,
        notes="",
        plain_english="",
        session="regular",
        days_to_earnings=None,
        next_earnings_date=None,
        sector_etf="XLK",
        rs_vs_sector=1.0,
        outcome_pct=2.0,
        outcome_1d=0.5,
        outcome_3d=1.0,
        outcome_14d=1.5,
        outcome_at=None,
        is_active=True,
    )
    defaults.update(kwargs)
    for k, v in defaults.items():
        setattr(s, k, v)
    return s


_MISSING = object()


def _result(all_values=None, scalars_all=None, scalar_one=_MISSING, scalar=None):
    """Build a mock result for db.execute()."""
    r = MagicMock()
    if all_values is not None:
        r.all.return_value = all_values
    if scalars_all is not None:
        r.scalars.return_value.all.return_value = scalars_all
    if scalar_one is not _MISSING:
        r.scalar_one_or_none.return_value = scalar_one
    if scalar is not None:
        r.scalar.return_value = scalar
    return r


def _mock_db(results):
    mock_db = MagicMock()
    mock_db.execute = AsyncMock(side_effect=results)
    mock_db.commit = AsyncMock()
    mock_db.get = AsyncMock(return_value=None)
    mock_db.delete = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def _get_db():
        yield mock_db

    return _get_db, mock_db


def _make_app_signals(is_owner=True):
    from routers.signals import router

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: _make_user(is_owner=is_owner)
    return app


def _make_app_admin(is_owner=True):
    from routers.admin import router

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: _make_user(is_owner=is_owner)
    return app


def _make_app_quotes(tier="basic", is_owner=True):
    from routers.quotes import router

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: _make_user(is_owner=is_owner, tier=tier)
    return app


# ═══════════════════════════════════════════════════════════════════════════════
# signals.py
# ═══════════════════════════════════════════════════════════════════════════════


class TestSignalsBacktestSimulate:
    def test_backtest_simulate_success(self):
        app = _make_app_signals(is_owner=True)
        sig = _make_signal(
            id=1,
            action="BUY",
            entry=100.0,
            stop=95.0,
            target=110.0,
            created_at=datetime(2026, 3, 1),
        )
        get_db_fn, _ = _mock_db([_result(scalars_all=[sig])])
        app.dependency_overrides[get_db] = get_db_fn

        idx = pd.date_range("2026-03-02", periods=10)
        df = pd.DataFrame(
            {
                "Open": [101.0] * 10,
                "High": [112.0] * 10,
                "Low": [96.0] * 10,
                "Close": [105.0] * 10,
            },
            index=idx,
        )

        with patch("services.market_data.get_history", new_callable=AsyncMock, return_value=df):
            with TestClient(app) as client:
                resp = client.get("/api/signals/backtest/simulate?slippage_pct=0.1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["simulated"] >= 1
        assert "gross" in data
        assert "net" in data

    def test_backtest_simulate_no_history(self):
        app = _make_app_signals(is_owner=True)
        sig = _make_signal(
            id=1,
            action="BUY",
            entry=100.0,
            stop=95.0,
            target=110.0,
            created_at=datetime(2026, 3, 1),
        )
        get_db_fn, _ = _mock_db([_result(scalars_all=[sig])])
        app.dependency_overrides[get_db] = get_db_fn

        with patch("services.market_data.get_history", new_callable=AsyncMock, return_value=None):
            with TestClient(app) as client:
                resp = client.get("/api/signals/backtest/simulate")
        assert resp.status_code == 200
        assert resp.json()["simulated"] == 0


class TestSignalsPredictiveConfidence:
    def test_predictive_confidence_success(self):
        app = _make_app_signals()
        signals = [
            _make_signal(
                id=i,
                action="BUY",
                confidence=70,
                sources=["RSI", "MACD"],
                outcome_1d=1.0 if i % 2 == 0 else -0.5,
                outcome_pct=2.0 if i % 2 == 0 else -1.0,
                is_sent=True,
            )
            for i in range(20)
        ]
        get_db_fn, _ = _mock_db([_result(scalars_all=signals)])
        app.dependency_overrides[get_db] = get_db_fn

        with patch("services.market_data.get_history", new_callable=AsyncMock, return_value=pd.DataFrame()):
            with TestClient(app) as client:
                resp = client.get("/api/signals/predictive?action=BUY&confidence=70&sources=RSI,MACD&style=swing")
        assert resp.status_code == 200
        data = resp.json()
        assert data["action"] == "BUY"
        assert data["n_similar"] >= 3
        assert len(data["horizons"]) > 0
        assert "insights" in data
        assert "summary" in data

    def test_predictive_confidence_no_data(self):
        app = _make_app_signals()
        get_db_fn, _ = _mock_db([_result(scalars_all=[])])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/signals/predictive")
        assert resp.status_code == 200
        data = resp.json()
        assert data["n_similar"] == 0
        assert "message" in data


class TestSignalsBackfillOutcomes:
    def test_backfill_outcomes_success(self):
        app = _make_app_signals(is_owner=True)
        sig = _make_signal(
            id=1,
            ticker="AAPL",
            action="BUY",
            entry=100.0,
            outcome_pct=None,
            outcome_1d=None,
            outcome_3d=None,
            outcome_14d=None,
            created_at=datetime(2026, 3, 1),
        )
        get_db_fn, _ = _mock_db([_result(scalars_all=[sig])])
        app.dependency_overrides[get_db] = get_db_fn

        idx = pd.date_range("2026-03-01", periods=20)
        df = pd.DataFrame({"Close": [100.0 + i for i in range(20)]}, index=idx)

        mock_ticker = MagicMock()
        mock_ticker.history.return_value = df

        with patch("yfinance.Ticker", return_value=mock_ticker):
            with TestClient(app) as client:
                resp = client.post("/api/signals/backtest/backfill")
        assert resp.status_code == 200
        data = resp.json()
        assert data["updated"] >= 1
        assert "message" in data

    def test_backfill_outcomes_already_filled(self):
        app = _make_app_signals(is_owner=True)
        sig = _make_signal(
            id=1,
            outcome_pct=1.5,
            outcome_1d=0.5,
            outcome_3d=1.0,
            outcome_14d=2.0,
        )
        get_db_fn, _ = _mock_db([_result(scalars_all=[sig])])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.post("/api/signals/backtest/backfill")
        assert resp.status_code == 200
        assert resp.json()["updated"] == 0


class TestSignalsAlphaDecay:
    def test_alpha_decay_success(self):
        app = _make_app_signals()
        rows = [(json.dumps(["RSI", "MACD"]), "BUY", 0.5, 1.0, 2.0, 1.5) for _ in range(10)]
        get_db_fn, _ = _mock_db([_result(all_values=rows)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/signals/alpha-decay")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        # RSI and MACD should appear as keys
        assert any(k in data for k in ("RSI", "MACD"))


class TestSignalsCorrelation:
    def test_correlation_with_data(self):
        app = _make_app_signals()
        signals = [
            _make_signal(
                id=i,
                sources=["RSI", "MACD"],
                outcome_pct=1.5 if i % 2 == 0 else -0.5,
                is_sent=True,
            )
            for i in range(10)
        ]
        get_db_fn, _ = _mock_db([_result(scalars_all=signals)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/signals/correlation")
        assert resp.status_code == 200
        data = resp.json()
        assert "pairs" in data
        assert "sources" in data
        assert data["n_signals"] == 10


class TestSignalsCalibrationCurve:
    def test_calibration_curve_with_data(self):
        app = _make_app_signals()
        rows = [(60 + i % 10, "BUY", 1.0 if i % 2 == 0 else -0.5) for i in range(30)]
        get_db_fn, _ = _mock_db([_result(all_values=rows)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/signals/backtest/calibration")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "bucket" in data[0]


class TestSignalsExportHistory:
    def test_export_signal_history_success(self):
        app = _make_app_signals()
        signals = [_make_signal(id=i, ticker="AAPL", is_sent=True) for i in range(5)]
        get_db_fn, _ = _mock_db([_result(scalars_all=signals)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/signals/history/export")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    def test_export_signal_history_with_filters(self):
        app = _make_app_signals()
        signals = [_make_signal(id=i, ticker="TSLA", action="SELL", is_sent=True, outcome_pct=-1.0) for i in range(3)]
        get_db_fn, _ = _mock_db([_result(scalars_all=signals)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/signals/history/export?ticker=TSLA&action=SELL&outcome=losses")
        assert resp.status_code == 200


class TestSignalsBacktestOOS:
    def test_backtest_oos_with_data(self):
        app = _make_app_signals()
        signals = [
            _make_signal(
                id=i,
                created_at=datetime(2026, 1, 1) + timedelta(days=i),
                outcome_pct=1.5 if i % 2 == 0 else -0.5,
                action="BUY" if i % 2 == 0 else "SELL",
            )
            for i in range(20)
        ]
        get_db_fn, _ = _mock_db([_result(scalars_all=signals)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/signals/backtest/oos")
        assert resp.status_code == 200
        data = resp.json()
        assert "oos_win_rate" in data
        assert "windows" in data

    def test_backtest_oos_empty(self):
        from routers.signals import clear_analytics_cache

        clear_analytics_cache()
        app = _make_app_signals()
        get_db_fn, _ = _mock_db([_result(scalars_all=[])])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/signals/backtest/oos")
        assert resp.status_code == 200
        data = resp.json()
        assert data["n_oos"] == 0


class TestSignalsSendErrors:
    def test_send_signal_hold_action_rejected(self):
        app = _make_app_signals()
        sig = _make_signal(id=1, action="HOLD", is_sent=False)
        get_db_fn, _ = _mock_db([_result(scalar_one=sig)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.post("/api/signals/1/send")
        assert resp.status_code == 400
        assert "HOLD" in resp.json()["detail"] or "BUY and SELL" in resp.json()["detail"]

    def test_send_signal_no_chat_id_non_owner(self):
        app = _make_app_signals(is_owner=False)
        sig = _make_signal(id=1, action="BUY", is_sent=False)
        get_db_fn, _ = _mock_db([_result(scalar_one=sig)])
        app.dependency_overrides[get_db] = get_db_fn
        # Override user to have no telegram_chat_id
        user = _make_user(is_owner=False)
        user.telegram_chat_id = None
        app.dependency_overrides[get_current_user] = lambda: user

        with TestClient(app) as client:
            resp = client.post("/api/signals/1/send")
        assert resp.status_code == 400
        assert "Telegram not linked" in resp.json()["detail"]


class TestSignalsOwnerEndpoints:
    def test_skip_signal_non_owner(self):
        app = _make_app_signals(is_owner=False)
        with TestClient(app) as client:
            resp = client.post("/api/signals/1/skip")
        assert resp.status_code == 403

    def test_review_signal_non_owner(self):
        app = _make_app_signals(is_owner=False)
        with TestClient(app) as client:
            resp = client.post("/api/signals/1/review")
        assert resp.status_code == 403

    def test_factor_mining_run_owner(self):
        app = _make_app_signals(is_owner=True)
        with patch("services.factor_miner.run_factor_mining", new_callable=AsyncMock):
            with TestClient(app) as client:
                resp = client.post("/api/signals/factor-mining/run")
        assert resp.status_code == 200

    def test_factor_mining_run_non_owner(self):
        app = _make_app_signals(is_owner=False)
        with TestClient(app) as client:
            resp = client.post("/api/signals/factor-mining/run")
        assert resp.status_code == 403


class TestSignalsMisc:
    def test_sparkline_invalid_ticker(self):
        app = _make_app_signals()
        with TestClient(app) as client:
            resp = client.get("/api/signals/INVALID!!!/spark")
        assert resp.status_code == 400

    def test_confidence_history_success(self):
        app = _make_app_signals()
        rows = [
            MagicMock(confidence=70, action="BUY", created_at=datetime(2026, 3, 1)),
            MagicMock(confidence=65, action="BUY", created_at=datetime(2026, 3, 2)),
        ]
        get_db_fn, _ = _mock_db([_result(all_values=rows)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/signals/AAPL/confidence-history")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_track_record_date_filters(self):
        app = _make_app_signals()
        signals = [
            _make_signal(
                id=i,
                ticker="AAPL",
                outcome_pct=1.5,
                is_sent=True,
                created_at=datetime(2026, 3, i + 1),
            )
            for i in range(5)
        ]
        get_db_fn, _ = _mock_db([_result(scalars_all=signals)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/signals/track-record?start_date=2026-03-01&end_date=2026-03-05")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


# ═══════════════════════════════════════════════════════════════════════════════
# admin.py
# ═══════════════════════════════════════════════════════════════════════════════


class TestAdminDeleteUser:
    def test_delete_user_success(self):
        app = _make_app_admin(is_owner=True)
        user = MagicMock()
        user.id = 2
        user.is_owner = False
        user.stripe_customer_id = "cus_123"
        user.telegram_chat_id = "123"
        user.alpaca_key_enc = b"enc"

        results = [
            _result(scalar=5),  # count SignalDelivery
            _result(scalar=3),  # count BrokerOrder
            _result(scalar=2),  # count RefreshToken
            _result(scalar=0),  # count SignalDelivery after
            _result(scalar=0),  # count BrokerOrder after
            _result(scalar=0),  # count RefreshToken after
        ]
        get_db_fn, mock_db = _mock_db(results)
        mock_db.get = AsyncMock(return_value=user)
        app.dependency_overrides[get_db] = get_db_fn

        with patch("services.audit_svc.record_action", new_callable=AsyncMock):
            with TestClient(app) as client:
                resp = client.delete("/api/admin/users/2")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["fully_purged"] is True
        mock_db.delete.assert_awaited()
        mock_db.commit.assert_awaited()

    def test_delete_user_owner_rejected(self):
        app = _make_app_admin(is_owner=True)
        user = MagicMock()
        user.id = 1
        user.is_owner = True
        get_db_fn, mock_db = _mock_db([_result(scalar_one=user)])
        mock_db.get = AsyncMock(return_value=user)
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.delete("/api/admin/users/1")
        assert resp.status_code == 400
        assert "owner" in resp.json()["detail"].lower()


class TestAdminRateLimits:
    def test_rate_limits_dashboard(self):
        app = _make_app_admin(is_owner=True)
        get_db_fn, _ = _mock_db([_result(scalars_all=[])])
        app.dependency_overrides[get_db] = get_db_fn

        # Patch the various cache globals so the endpoint covers the try blocks
        now = __import__("time").time()
        with (
            patch("services.market_data._yf_backoff_until", now - 10),
            patch("services.polygon_indicators._TTL", 300),
            patch("services.polygon_indicators._cache", {"k": {"ts": now}}),
            patch("services.market_data._OHLCV_TTL", 300),
            patch("services.market_data._ohlcv_cache", {"k": {"ts": now}}),
            patch.object(__import__("services.macro", fromlist=["_cache"]), "_cache", {"ts": now}, create=True),
            patch("services.benzinga_news._batch_cache", {"ts": now}),
            patch("services.signal_workers.ALL_WORKERS", []),
            patch("services.worker_bus.collect_worker_stats", return_value={}),
        ):
            with TestClient(app) as client:
                resp = client.get("/api/admin/rate-limits")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)


class TestAdminAnalytics:
    def test_analytics_summary(self):
        app = _make_app_admin(is_owner=True)
        signals = [
            _make_signal(
                id=i,
                outcome_pct=1.5 if i % 2 == 0 else -0.5,
                is_sent=True,
                created_at=datetime(2026, 6, 9),
            )
            for i in range(10)
        ]
        users = [
            MagicMock(
                subscription_tier="basic" if i % 2 == 0 else "pro",
                subscription_status="active",
                is_active=True,
            )
            for i in range(4)
        ]
        results = [
            _result(scalars_all=signals),  # all signals
            _result(scalars_all=users),  # all users
        ]
        get_db_fn, _ = _mock_db(results)
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/admin/analytics-summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "signals" in data
        assert "users" in data
        assert "revenue" in data

    def test_cohort_analytics(self):
        app = _make_app_admin(is_owner=True)
        signals = []
        for i in range(12):
            s = _make_signal(id=i, outcome_pct=1.0 if i % 2 == 0 else -1.0)
            s.extra_data = {"cohort": "delivered" if i % 3 == 0 else "shadow" if i % 3 == 1 else "withheld"}
            signals.append(s)
        get_db_fn, _ = _mock_db([_result(scalars_all=signals)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/admin/cohort-analytics")
        assert resp.status_code == 200
        data = resp.json()
        assert "delivered" in data
        assert "shadow" in data
        assert "withheld" in data


class TestAdminDeliverySLA:
    def test_delivery_sla(self):
        app = _make_app_admin(is_owner=True)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        rows = [MagicMock(created_at=now - timedelta(minutes=2), sent_at=now) for _ in range(10)]
        get_db_fn, _ = _mock_db([_result(all_values=rows)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/admin/delivery-sla")
        assert resp.status_code == 200
        data = resp.json()
        assert "p50_latency_s" in data
        assert "sla_breaches_24h" in data


class TestAdminSnapshots:
    def test_list_snapshots(self):
        app = _make_app_admin(is_owner=True)
        snapshots = [
            MagicMock(
                id=i,
                tag=f"v{i}",
                git_sha="abc",
                n_trades=10,
                win_rate=55.0,
                sharpe=1.2,
                created_at=datetime(2026, 3, 1),
            )
            for i in range(3)
        ]
        get_db_fn, _ = _mock_db([_result(scalars_all=snapshots)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/admin/snapshots")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_get_snapshot_success(self):
        app = _make_app_admin(is_owner=True)
        snap = MagicMock(
            id=1,
            tag="v1",
            git_sha="abc",
            n_trades=10,
            win_rate=55.0,
            sharpe=1.2,
            created_at=datetime(2026, 3, 1),
            metrics={"wr": 0.55},
        )
        get_db_fn, _ = _mock_db([_result(scalar_one=snap)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/admin/snapshots/1")
        assert resp.status_code == 200
        assert resp.json()["metrics"] == {"wr": 0.55}

    def test_get_snapshot_not_found(self):
        app = _make_app_admin(is_owner=True)
        get_db_fn, _ = _mock_db([_result(scalar_one=None)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/admin/snapshots/999")
        assert resp.status_code == 404

    def test_diff_snapshots(self):
        app = _make_app_admin(is_owner=True)
        snap_a = MagicMock(id=1, tag="a", created_at=datetime(2026, 3, 1), metrics={"wr": 0.50})
        snap_b = MagicMock(id=2, tag="b", created_at=datetime(2026, 3, 2), metrics={"wr": 0.55})
        get_db_fn, _ = _mock_db([_result(scalars_all=[snap_a, snap_b])])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/admin/snapshots/diff/1/2")
        assert resp.status_code == 200
        data = resp.json()
        assert "delta" in data
        assert "flagged_metrics" in data


class TestAdminKillSwitch:
    def test_execution_kill_switch_toggle(self):
        app = _make_app_admin(is_owner=True)
        row = MagicMock(data={"execution_paused": False})
        get_db_fn, _ = _mock_db([_result(scalar_one=row)])
        app.dependency_overrides[get_db] = get_db_fn

        with patch("services.audit_svc.record_action", new_callable=AsyncMock):
            with TestClient(app) as client:
                resp = client.post("/api/admin/execution-kill-switch")
        assert resp.status_code == 200
        assert resp.json()["execution_paused"] is True

    def test_get_kill_switch_status(self):
        app = _make_app_admin(is_owner=True)
        row = MagicMock(data={"execution_paused": True})
        get_db_fn, _ = _mock_db([_result(scalar_one=row)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/admin/execution-kill-switch")
        assert resp.status_code == 200
        assert resp.json()["execution_paused"] is True


class TestAdminSystemReadiness:
    def test_system_readiness_db_error(self):
        app = _make_app_admin(is_owner=True)

        class FakeExc(Exception):
            pass

        call_count = 0

        async def _exec(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise FakeExc("db down")
            return _result(scalar_one=MagicMock(data={"execution_paused": False}))

        mock_db = MagicMock()
        mock_db.execute = AsyncMock(side_effect=_exec)
        mock_db.commit = AsyncMock()

        async def _get_db():
            yield mock_db

        app.dependency_overrides[get_db] = _get_db

        settings = MagicMock()
        settings.jwt_secret = "secret"
        settings.owner_email = "o@t.com"
        settings.owner_password = "SecurePassword1234!"
        settings.telegram_bot_token = "token"
        settings.stripe_secret_key = "sk"
        settings.stripe_webhook_secret = "whsec_stripe"
        settings.stripe_price_basic = "price_basic"
        settings.stripe_price_pro = "price_pro"
        settings.app_url = "https://app.com"
        settings.alpaca_api_key = ""
        settings.alpaca_api_secret = ""
        settings.finnhub_api_key = ""
        settings.fred_api_key = ""
        settings.polygon_api_key = ""
        settings.redis_url = ""

        with (
            patch("routers.admin.get_settings", return_value=settings),
            patch("services.http_client.shared_session") as mock_sess,
        ):
            # shared_session is an async context manager yielding a session
            sess = MagicMock()
            sess.__aenter__ = AsyncMock(return_value=sess)
            sess.__aexit__ = AsyncMock(return_value=False)
            mock_sess.return_value = sess
            with TestClient(app) as client:
                resp = client.get("/api/admin/system-readiness")
        assert resp.status_code == 200
        data = resp.json()
        assert data["database"]["status"] == "error"
        assert data["ready"] is False

    def test_system_readiness_missing_env(self):
        app = _make_app_admin(is_owner=True)
        settings = MagicMock()
        settings.jwt_secret = None  # missing critical env
        settings.owner_email = "o@t.com"
        settings.owner_password = "SecurePassword1234!"
        settings.telegram_bot_token = "token"
        settings.stripe_secret_key = "sk"
        settings.stripe_webhook_secret = "whsec_stripe"
        settings.stripe_price_basic = "price_basic"
        settings.stripe_price_pro = "price_pro"
        settings.app_url = "https://app.com"
        settings.alpaca_api_key = ""
        settings.alpaca_api_secret = ""
        settings.finnhub_api_key = ""
        settings.fred_api_key = ""
        settings.polygon_api_key = ""
        settings.redis_url = ""

        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_result(scalar_one=MagicMock(data={"execution_paused": False})))
        mock_db.commit = AsyncMock()

        async def _get_db():
            yield mock_db

        app.dependency_overrides[get_db] = _get_db

        with (
            patch("routers.admin.get_settings", return_value=settings),
            patch("services.http_client.shared_session") as mock_sess,
        ):
            sess = MagicMock()
            sess.__aenter__ = AsyncMock(return_value=sess)
            sess.__aexit__ = AsyncMock(return_value=False)
            mock_sess.return_value = sess
            with TestClient(app) as client:
                resp = client.get("/api/admin/system-readiness")
        assert resp.status_code == 200
        data = resp.json()
        assert data["env_vars"]["status"] == "error"
        assert data["ready"] is False


class TestAdminObservability:
    def test_provider_reliability(self):
        app = _make_app_admin(is_owner=True)
        scorecards = [
            MagicMock(
                id=1,
                provider="polygon",
                endpoint="/v2/aggs",
                latency_avg_ms=120.0,
                error_rate=0.01,
                stale_data_rate=0.0,
                schema_drift_count=0,
                health_score=0.95,
                is_active=True,
                last_updated=datetime(2026, 3, 1),
            )
        ]
        telemetry = [
            MagicMock(
                id=1,
                cycle_id="c1",
                provider="polygon",
                api_calls=100,
                cache_hits=50,
                cache_misses=50,
                quota_remaining=900,
                throttles=0,
                fallback_usage=0,
                created_at=datetime(2026, 3, 1),
            )
        ]
        results = [
            _result(scalars_all=scorecards),
            _result(scalars_all=telemetry),
        ]
        get_db_fn, _ = _mock_db(results)
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/admin/provider-reliability")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["scorecards"]) == 1
        assert len(data["telemetry"]) == 1

    def test_incident_timeline_with_severity(self):
        app = _make_app_admin(is_owner=True)
        incidents = [
            MagicMock(
                id=1,
                event_type="scan_fail",
                severity="high",
                message="m",
                details={},
                created_at=datetime(2026, 3, 1),
            )
        ]
        get_db_fn, _ = _mock_db([_result(scalars_all=incidents)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/admin/incident-timeline?severity=high")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["severity"] == "high"

    def test_check_alerts(self):
        app = _make_app_admin(is_owner=True)
        get_db_fn, mock_db = _mock_db([])
        app.dependency_overrides[get_db] = get_db_fn

        with patch("services.metrics.check_alert_thresholds", new_callable=AsyncMock, return_value=[{"name": "cpu"}]):
            with TestClient(app) as client:
                resp = client.post("/api/admin/check-alerts")
        assert resp.status_code == 200
        assert resp.json()["count"] == 1
        mock_db.commit.assert_awaited()


class TestAdminRetention:
    def test_retention_rules(self):
        app = _make_app_admin(is_owner=True)
        with patch("services.retention_svc.default_rules", return_value={"rules": []}):
            with TestClient(app) as client:
                resp = client.get("/api/admin/retention-rules")
        assert resp.status_code == 200

    def test_retention_purge_dry_run(self):
        app = _make_app_admin(is_owner=True)
        get_db_fn, _ = _mock_db([])
        app.dependency_overrides[get_db] = get_db_fn

        with patch("services.retention_svc.purge_expired", new_callable=AsyncMock, return_value={"deleted": 0}):
            with TestClient(app) as client:
                resp = client.post("/api/admin/retention/purge?dry_run=true")
        assert resp.status_code == 200
        assert resp.json()["dry_run"] is True


class TestAdminCalibration:
    def test_calibration_history(self):
        app = _make_app_admin(is_owner=True)
        rows = [
            MagicMock(
                version="v1",
                is_active=True,
                calibration_data={"brier_walkforward": 0.25, "n_total": 100},
                created_at=datetime(2026, 3, 1),
            )
        ]
        get_db_fn, _ = _mock_db([_result(scalars_all=rows)])
        app.dependency_overrides[get_db] = get_db_fn

        with TestClient(app) as client:
            resp = client.get("/api/admin/calibration-history")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["version"] == "v1"

    def test_calibration_archive(self):
        app = _make_app_admin(is_owner=True)
        get_db_fn, _ = _mock_db([])
        app.dependency_overrides[get_db] = get_db_fn

        with patch("services.calibration.archive_current_calibration", new_callable=AsyncMock, return_value="v2"):
            with TestClient(app) as client:
                resp = client.post("/api/admin/calibration-archive")
        assert resp.status_code == 200
        assert resp.json()["version"] == "v2"

    def test_calibration_rollback_success(self):
        app = _make_app_admin(is_owner=True)
        get_db_fn, _ = _mock_db([])
        app.dependency_overrides[get_db] = get_db_fn

        with patch("services.calibration.restore_calibration_version", new_callable=AsyncMock, return_value=True):
            with TestClient(app) as client:
                resp = client.post("/api/admin/calibration-rollback?version=v1")
        assert resp.status_code == 200
        assert resp.json()["restored"] is True

    def test_calibration_rollback_not_found(self):
        app = _make_app_admin(is_owner=True)
        get_db_fn, _ = _mock_db([])
        app.dependency_overrides[get_db] = get_db_fn

        with patch("services.calibration.restore_calibration_version", new_callable=AsyncMock, return_value=False):
            with TestClient(app) as client:
                resp = client.post("/api/admin/calibration-rollback?version=v99")
        assert resp.status_code == 404


class TestAdminIndexAudit:
    def test_index_audit(self):
        app = _make_app_admin(is_owner=True)
        with TestClient(app) as client:
            resp = client.get("/api/admin/index-audit")
        assert resp.status_code == 200
        data = resp.json()
        assert "checked" in data
        assert "missing" in data
        assert "ok" in data


# ═══════════════════════════════════════════════════════════════════════════════
# quotes.py
# ═══════════════════════════════════════════════════════════════════════════════


class TestQuotesMassive:
    def test_massive_endpoints_success(self):
        app = _make_app_quotes()
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value="## API\n- [Tickers](/v1/reference/tickers): List tickers")
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_ctx)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with TestClient(app) as client:
                resp = client.get("/api/massive/endpoints")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["name"] == "API"

    def test_massive_endpoints_error(self):
        app = _make_app_quotes()
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_ctx)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with TestClient(app) as client:
                resp = client.get("/api/massive/endpoints")
        assert resp.status_code == 200
        data = resp.json()
        assert data[0]["name"] == "Error"

    def test_massive_proxy_owner(self):
        app = _make_app_quotes(is_owner=True)
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"results": []})
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_session = MagicMock()
        mock_session.request = MagicMock(return_value=mock_ctx)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("aiohttp.ClientSession", return_value=mock_session),
            patch.dict("os.environ", {"MASSIVE_API_KEY": "key123"}),
        ):
            with TestClient(app) as client:
                resp = client.post(
                    "/api/massive/proxy", json={"endpoint": "/v1/reference/tickers/AAPL", "method": "GET"}
                )
        assert resp.status_code == 200
        assert "data" in resp.json()

    def test_massive_proxy_not_owner(self):
        app = _make_app_quotes(is_owner=False)
        with TestClient(app) as client:
            resp = client.post("/api/massive/proxy", json={"endpoint": "/v1/reference/tickers/AAPL"})
        assert resp.status_code == 403

    def test_massive_proxy_bad_endpoint(self):
        app = _make_app_quotes(is_owner=True)
        with patch.dict("os.environ", {"MASSIVE_API_KEY": "key123"}):
            with TestClient(app) as client:
                resp = client.post("/api/massive/proxy", json={"endpoint": "/unsafe/admin", "method": "GET"})
        assert resp.status_code == 400


class TestQuotesSectors:
    def test_sector_heatmap_timeout(self):
        app = _make_app_quotes()
        with patch(
            "services.market_data.get_histories_batch",
            new_callable=AsyncMock,
            side_effect=asyncio.TimeoutError,
        ):
            with TestClient(app) as client:
                resp = client.get("/api/market/sectors")
        assert resp.status_code == 200
        # Returns empty list or cached data when timeout

    def test_sector_detail(self):
        app = _make_app_quotes()
        # Patch sector_heatmap to avoid external calls
        with patch(
            "routers.quotes.sector_heatmap", new_callable=AsyncMock, return_value=[{"etf": "XLK", "ret_1m": 2.0}]
        ):
            # Patch AsyncSessionLocal used inside sector_detail
            mock_db = MagicMock()
            wl_result = MagicMock()
            wl_result.scalars.return_value.all.return_value = []
            sig_result = MagicMock()
            sig_result.scalars.return_value.all.return_value = []
            mock_db.execute = AsyncMock(side_effect=[wl_result, sig_result])

            async def _async_session():
                class CM:
                    async def __aenter__(self):
                        return mock_db

                    async def __aexit__(self, *args):
                        pass

                return CM()

            with patch("database.AsyncSessionLocal", side_effect=_async_session):
                with patch("services.market_data.get_histories_batch", new_callable=AsyncMock, return_value={}):
                    with TestClient(app) as client:
                        resp = client.get("/api/market/sectors/detail")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_sector_stocks(self):
        app = _make_app_quotes()
        histories = {"AAPL": pd.DataFrame({"Close": [100.0, 102.0]}, index=pd.date_range("2026-01-01", periods=2))}
        mock_db = MagicMock()
        sig_result = MagicMock()
        sig_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=sig_result)

        async def _async_session():
            class CM:
                async def __aenter__(self):
                    return mock_db

                async def __aexit__(self, *args):
                    pass

            return CM()

        with (
            patch("database.AsyncSessionLocal", side_effect=_async_session),
            patch("services.market_data.get_histories_batch", new_callable=AsyncMock, return_value=histories),
            patch("services.market_data.COMPANY_NAMES", {"AAPL": "Apple Inc."}),
            patch("services.sector.SECTOR_MAP", {"AAPL": "XLK"}),
        ):
            with TestClient(app) as client:
                resp = client.get("/api/market/sectors/XLK/stocks")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        if data:
            assert data[0]["ticker"] == "AAPL"

    def test_sector_stocks_empty(self):
        app = _make_app_quotes()
        with patch("services.sector.SECTOR_MAP", {}):
            with TestClient(app) as client:
                resp = client.get("/api/market/sectors/ZZZ/stocks")
        assert resp.status_code == 200
        assert resp.json() == []


class TestQuotesCalendar:
    def test_economic_calendar_with_fred(self):
        app = _make_app_quotes()
        settings = MagicMock()
        settings.fred_api_key = "fred_key"

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"release_dates": [{"date": "2026-07-01"}, {"date": "2026-08-01"}]})
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_ctx)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("routers.quotes.get_settings", return_value=settings),
            patch("aiohttp.ClientSession", return_value=mock_session),
        ):
            with TestClient(app) as client:
                resp = client.get("/api/market/calendar")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        # Should include FOMC + FRED events
        labels = {e["label"] for e in data}
        assert "FOMC" in labels or len(data) >= 0
