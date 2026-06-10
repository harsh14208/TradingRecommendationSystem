"""
Comprehensive tests for:
  - services/email_svc.py
  - services/factor_miner.py
  - services/news.py

Coverage targets: happy path, edge cases, empty data, missing files,
no-config fallbacks, exceptions, and all branches.
"""

from __future__ import annotations

import asyncio
import json
import math
import types
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr

# ---------------------------------------------------------------------------
# email_svc tests
# ---------------------------------------------------------------------------


class TestEmailSend:
    @pytest.fixture(autouse=True)
    def _clear_aiosmtplib_import(self):
        """Ensure aiosmtplib can be re-imported cleanly each test."""
        import sys

        for mod in list(sys.modules):
            if mod == "aiosmtplib" or mod.startswith("aiosmtplib."):
                del sys.modules[mod]
        yield

    @pytest.mark.asyncio
    async def test_send_no_smtp_configured_logs_and_returns(self, caplog):
        from services import email_svc

        fake_settings = types.SimpleNamespace(
            smtp_host="",
            smtp_user="",
            smtp_port=587,
            smtp_from="noreply@signal.trade",
            smtp_from_name="Signal.Trade",
            smtp_password=SecretStr(""),
            app_url="http://localhost:8000",
        )
        with patch("services.email_svc._settings", return_value=fake_settings):
            with caplog.at_level("INFO", logger="signal.trade.email"):
                await email_svc._send("to@test.com", "Subject", "<html>hi</html>", "hi")
        assert "SMTP not configured" in caplog.text
        assert "TO=to@test.com" in caplog.text

    @pytest.mark.asyncio
    async def test_send_success(self, caplog):
        from services import email_svc

        fake_settings = types.SimpleNamespace(
            smtp_host="smtp.example.com",
            smtp_user="user",
            smtp_port=587,
            smtp_from="noreply@signal.trade",
            smtp_from_name="Signal.Trade",
            smtp_password=SecretStr("secret"),
            app_url="http://localhost:8000",
        )
        mock_aiosmtplib = MagicMock()
        mock_aiosmtplib.send = AsyncMock()
        with patch.dict("sys.modules", {"aiosmtplib": mock_aiosmtplib}):
            with patch("services.email_svc._settings", return_value=fake_settings):
                with caplog.at_level("INFO", logger="signal.trade.email"):
                    await email_svc._send("to@test.com", "Subject", "<html>hi</html>", "hi")
        mock_aiosmtplib.send.assert_awaited_once()
        assert "sent TO=to@test.com" in caplog.text

    @pytest.mark.asyncio
    async def test_send_exception_logs_warning(self, caplog):
        from services import email_svc

        fake_settings = types.SimpleNamespace(
            smtp_host="smtp.example.com",
            smtp_user="user",
            smtp_port=587,
            smtp_from="noreply@signal.trade",
            smtp_from_name="Signal.Trade",
            smtp_password=SecretStr("secret"),
            app_url="http://localhost:8000",
        )
        mock_aiosmtplib = MagicMock()
        mock_aiosmtplib.send = AsyncMock(side_effect=ConnectionError("smtp down"))
        with patch.dict("sys.modules", {"aiosmtplib": mock_aiosmtplib}):
            with patch("services.email_svc._settings", return_value=fake_settings):
                with caplog.at_level("WARNING", logger="signal.trade.email"):
                    await email_svc._send("to@test.com", "Subject", "<html>hi</html>", "hi")
        assert "failed TO=to@test.com" in caplog.text
        assert "smtp down" in caplog.text


class TestEmailTemplates:
    @pytest.fixture(autouse=True)
    def _patch_send(self):
        from services import email_svc

        with patch.object(email_svc, "_send", new_callable=AsyncMock) as mock:
            self.mock_send = mock
            yield

    @pytest.mark.asyncio
    async def test_send_welcome_normal(self):
        from services.email_svc import send_welcome

        await send_welcome("user@test.com", "Alice")
        self.mock_send.assert_awaited_once()
        args = self.mock_send.call_args[0]
        assert args[0] == "user@test.com"
        assert "Welcome" in args[1]
        assert "Alice" in args[2]
        assert "Alice" in args[3]

    @pytest.mark.asyncio
    async def test_send_welcome_empty_name_uses_localpart(self):
        from services.email_svc import send_welcome

        await send_welcome("user@test.com", "")
        args = self.mock_send.call_args[0]
        assert "user" in args[2]

    @pytest.mark.asyncio
    async def test_send_subscription_confirmed_basic(self):
        from services.email_svc import send_subscription_confirmed

        await send_subscription_confirmed("user@test.com", "Bob", "basic", "2026-07-01")
        args = self.mock_send.call_args[0]
        assert "Basic" in args[1]
        assert "pill pro" not in args[2]

    @pytest.mark.asyncio
    async def test_send_subscription_confirmed_pro(self):
        from services.email_svc import send_subscription_confirmed

        await send_subscription_confirmed("user@test.com", "Bob", "pro", "2026-07-01")
        args = self.mock_send.call_args[0]
        assert "Pro" in args[1]
        assert "pill pro" in args[2]

    @pytest.mark.asyncio
    async def test_send_subscription_confirmed_empty_name(self):
        from services.email_svc import send_subscription_confirmed

        await send_subscription_confirmed("user@test.com", "", "basic", "2026-07-01")
        args = self.mock_send.call_args[0]
        assert "user" in args[2]

    @pytest.mark.asyncio
    async def test_send_payment_failed(self):
        from services.email_svc import send_payment_failed

        await send_payment_failed("user@test.com", "Charlie")
        args = self.mock_send.call_args[0]
        assert "Payment failed" in args[1]
        assert "Charlie" in args[2]

    @pytest.mark.asyncio
    async def test_send_payment_failed_empty_name(self):
        from services.email_svc import send_payment_failed

        await send_payment_failed("user@test.com", "")
        args = self.mock_send.call_args[0]
        assert "user" in args[2]

    @pytest.mark.asyncio
    async def test_send_subscription_canceled(self):
        from services.email_svc import send_subscription_canceled

        await send_subscription_canceled("user@test.com", "Dana", "2026-08-01")
        args = self.mock_send.call_args[0]
        assert "Subscription canceled" in args[1]
        assert "2026-08-01" in args[2]

    @pytest.mark.asyncio
    async def test_send_subscription_canceled_empty_name(self):
        from services.email_svc import send_subscription_canceled

        await send_subscription_canceled("user@test.com", "", "2026-08-01")
        args = self.mock_send.call_args[0]
        assert "user" in args[2]

    @pytest.mark.asyncio
    async def test_send_weekly_digest_full_data(self):
        from services.email_svc import send_weekly_digest

        await send_weekly_digest(
            "user@test.com",
            "2026-06-07",
            10,
            win_rate=60,
            wins=6,
            resolved=10,
            avg_ret=2.5,
            best_ticker="AAPL",
            best_ret=5.0,
            worst_ticker="TSLA",
            worst_ret=-3.0,
            spy_ret=1.0,
        )
        args = self.mock_send.call_args[0]
        assert "Weekly Digest" in args[1]
        assert "60%" in args[2]
        assert "+2.50%" in args[2]
        assert "SPY" in args[2]
        assert "AAPL" in args[2]
        assert "TSLA" in args[2]
        plain = args[3]
        assert "Win rate: 60%" in plain
        assert "Avg return: +2.50%" in plain
        assert "(vs SPY +1.00%)" in plain

    @pytest.mark.asyncio
    async def test_send_weekly_digest_no_optional_data(self):
        from services.email_svc import send_weekly_digest

        await send_weekly_digest(
            "user@test.com",
            "2026-06-07",
            0,
            win_rate=None,
            wins=0,
            resolved=0,
            avg_ret=None,
            best_ticker=None,
            best_ret=None,
            worst_ticker=None,
            worst_ret=None,
            spy_ret=None,
        )
        args = self.mock_send.call_args[0]
        assert "No resolved outcomes yet" in args[2]
        plain = args[3]
        assert "Signals sent: 0" in plain
        assert "Win rate" not in plain

    @pytest.mark.asyncio
    async def test_send_verification_email(self):
        from services.email_svc import send_verification_email

        await send_verification_email("user@test.com", "Eve", "http://verify")
        args = self.mock_send.call_args[0]
        assert "Verify your email" in args[1]
        assert "http://verify" in args[2]
        assert "Eve" in args[2]

    @pytest.mark.asyncio
    async def test_send_verification_email_empty_name(self):
        from services.email_svc import send_verification_email

        await send_verification_email("user@test.com", "", "http://verify")
        args = self.mock_send.call_args[0]
        assert "user" in args[2]

    @pytest.mark.asyncio
    async def test_send_password_reset(self):
        from services.email_svc import send_password_reset

        await send_password_reset("user@test.com", "http://reset")
        args = self.mock_send.call_args[0]
        assert "Password reset" in args[1]
        assert "http://reset" in args[2]


# ---------------------------------------------------------------------------
# factor_miner tests
# ---------------------------------------------------------------------------


class TestSharpe:
    def test_sharpe_insufficient_data(self):
        from services.factor_miner import _sharpe

        assert _sharpe([]) is None
        assert _sharpe([1.0]) is None
        assert _sharpe([1.0, 2.0]) is None

    def test_sharpe_zero_std(self):
        from services.factor_miner import _sharpe

        assert _sharpe([2.0, 2.0, 2.0]) is None

    def test_sharpe_normal(self):
        from services.factor_miner import _sharpe

        returns = [1.0, -0.5, 2.0, 0.5, 1.5]
        result = _sharpe(returns)
        assert result is not None
        assert result > 0
        # Check annualisation factor sqrt(52) is applied
        n = len(returns)
        mean_r = sum(returns) / n
        variance = sum((r - mean_r) ** 2 for r in returns) / (n - 1)
        std_r = math.sqrt(variance)
        expected = round((mean_r / std_r) * math.sqrt(52), 3)
        assert result == expected


class TestWinRate:
    def test_win_rate_empty(self):
        from services.factor_miner import _win_rate

        assert _win_rate([]) == 0.0

    def test_win_rate_all_positive(self):
        from services.factor_miner import _win_rate

        assert _win_rate([1.0, 2.0, 0.1]) == 1.0

    def test_win_rate_mixed(self):
        from services.factor_miner import _win_rate

        assert _win_rate([1.0, -1.0, 2.0, -2.0]) == 0.5


class TestEvalFactor:
    def test_eval_factor_too_few_rows(self):
        from services.factor_miner import _eval_factor, _MIN_SIGNALS

        rows = [{"outcome_pct": 1.0}] * (_MIN_SIGNALS - 1)
        assert _eval_factor(rows, "src") is None

    def test_eval_factor_too_few_oos(self):
        from services.factor_miner import _eval_factor, _MIN_SIGNALS

        # Need enough total rows (>= _MIN_SIGNALS) but OOS < _MIN_OOS_N
        n_total = _MIN_SIGNALS + 1  # small enough that test slice is tiny
        rows = [{"outcome_pct": 1.0, "created_at": datetime.now()} for _ in range(n_total)]
        result = _eval_factor(rows, "src")
        assert result is None

    def test_eval_factor_success(self):
        from services.factor_miner import _eval_factor, _MIN_OOS_N

        n_total = 100
        rows = [{"outcome_pct": float(i % 5 - 2), "created_at": datetime(2026, 1, 1)} for i in range(n_total)]
        result = _eval_factor(rows, "src")
        assert result is not None
        assert result["label"] == "src"
        assert result["total_signals"] == n_total
        assert result["oos_n"] >= _MIN_OOS_N
        assert "oos_sharpe" in result
        assert "oos_win_rate" in result
        assert "oos_avg_ret" in result
        assert "is_win_rate" in result


class TestRunFactorMining:
    @pytest.mark.asyncio
    async def test_db_read_fails(self):
        from services import factor_miner

        with patch.object(
            factor_miner, "_load_resolved_signals", new_callable=AsyncMock, side_effect=RuntimeError("db bust")
        ):
            result = await factor_miner.run_factor_mining()
        assert "error" in result
        assert "db bust" in result["error"]

    @pytest.mark.asyncio
    async def test_too_few_rows(self):
        from services import factor_miner

        rows = [{"outcome_pct": 1.0, "sources": ["s1"], "created_at": datetime.now()}] * 5
        with patch.object(factor_miner, "_load_resolved_signals", new_callable=AsyncMock, return_value=rows):
            result = await factor_miner.run_factor_mining()
        assert result.get("skipped") is True
        assert result["rows"] == 5

    @pytest.mark.asyncio
    async def test_no_combinations_meet_threshold(self):
        from services import factor_miner

        rows = [{"outcome_pct": 1.0, "sources": ["s1"], "created_at": datetime(2026, 1, i)} for i in range(1, 21)]
        with patch.object(factor_miner, "_load_resolved_signals", new_callable=AsyncMock, return_value=rows):
            result = await factor_miner.run_factor_mining()
        assert result.get("combinations_tested") == 0

    @pytest.mark.asyncio
    async def test_success_and_persistence(self):
        from services import factor_miner

        n_total = 200
        rows = [
            {"outcome_pct": float(i % 10 - 3), "sources": ["s1", "s2"], "created_at": datetime(2026, 1, 1)}
            for i in range(n_total)
        ]
        # Make timestamps unique to avoid sort stability issues
        for i, r in enumerate(rows):
            r["created_at"] = datetime(2026, 1, 1, 0, i // 60, i % 60)

        mock_data_dir = MagicMock()
        mock_weights_file = MagicMock()
        with patch.object(factor_miner, "_load_resolved_signals", new_callable=AsyncMock, return_value=rows):
            with patch.object(factor_miner, "_DATA_DIR", mock_data_dir):
                with patch.object(factor_miner, "_WEIGHTS_FILE", mock_weights_file):
                    result = await factor_miner.run_factor_mining()

        assert "run_at" in result
        assert result["signals_used"] == n_total
        assert result["combinations_tested"] > 0
        assert "top_factors" in result
        assert "promoted_count" in result
        assert "bh_significant_count" in result
        mock_data_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_weights_file.write_text.assert_called_once()
        written_json = json.loads(mock_weights_file.write_text.call_args[0][0])
        assert written_json["signals_used"] == n_total

    @pytest.mark.asyncio
    async def test_write_failure_returns_summary(self):
        from services import factor_miner

        n_total = 200
        rows = [
            {
                "outcome_pct": float(i % 10 - 3),
                "sources": ["s1"],
                "created_at": datetime(2026, 1, 1, 0, i // 60, i % 60),
            }
            for i in range(n_total)
        ]
        mock_data_dir = MagicMock()
        mock_data_dir.mkdir.side_effect = PermissionError("no write")
        with patch.object(factor_miner, "_load_resolved_signals", new_callable=AsyncMock, return_value=rows):
            with patch.object(factor_miner, "_DATA_DIR", mock_data_dir):
                result = await factor_miner.run_factor_mining()
        assert "run_at" in result
        assert result["signals_used"] == n_total


class TestLoadFactorWeights:
    def test_file_exists(self):
        from services import factor_miner

        fake_data = {"run_at": "2026-01-01", "top_factors": []}
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = json.dumps(fake_data)
        with patch.object(factor_miner, "_WEIGHTS_FILE", mock_path):
            result = factor_miner.load_factor_weights()
        assert result == fake_data

    def test_file_missing(self):
        from services import factor_miner

        mock_path = MagicMock()
        mock_path.exists.return_value = False
        with patch.object(factor_miner, "_WEIGHTS_FILE", mock_path):
            result = factor_miner.load_factor_weights()
        assert result == {}

    def test_file_corrupt(self):
        from services import factor_miner

        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = "not json"
        with patch.object(factor_miner, "_WEIGHTS_FILE", mock_path):
            result = factor_miner.load_factor_weights()
        assert result == {}


class TestGetFactorMiningResults:
    @pytest.mark.asyncio
    async def test_cached_valid(self):
        from services import factor_miner

        cached = {"run_at": "2026-01-01", "skipped": False}
        with patch.object(factor_miner, "load_factor_weights", return_value=cached):
            result = await factor_miner.get_factor_mining_results()
        assert result == cached

    @pytest.mark.asyncio
    async def test_cached_skipped_triggers_run(self):
        from services import factor_miner

        cached = {"run_at": "2026-01-01", "skipped": True}
        run_result = {"run_at": "2026-02-01", "skipped": False}
        with patch.object(factor_miner, "load_factor_weights", return_value=cached):
            with patch.object(factor_miner, "run_factor_mining", new_callable=AsyncMock, return_value=run_result):
                result = await factor_miner.get_factor_mining_results()
        assert result == run_result

    @pytest.mark.asyncio
    async def test_no_cache_triggers_run(self):
        from services import factor_miner

        run_result = {"run_at": "2026-02-01"}
        with patch.object(factor_miner, "load_factor_weights", return_value={}):
            with patch.object(factor_miner, "run_factor_mining", new_callable=AsyncMock, return_value=run_result):
                result = await factor_miner.get_factor_mining_results()
        assert result == run_result


# ---------------------------------------------------------------------------
# news tests
# ---------------------------------------------------------------------------


class TestScoreSentiment:
    def test_empty_text(self):
        from services.news import score_sentiment

        assert score_sentiment("") == 0.0

    def test_no_matches(self):
        from services.news import score_sentiment

        assert score_sentiment("the quick brown fox") == 0.0

    def test_positive(self):
        from services.news import score_sentiment

        assert score_sentiment("strong growth and profit") > 0.0

    def test_negative(self):
        from services.news import score_sentiment

        assert score_sentiment("weak decline and loss") < 0.0

    def test_mixed(self):
        from services.news import score_sentiment

        # 2 positive, 2 negative => 0.0
        assert score_sentiment("strong growth but weak decline") == 0.0


class TestTrackCall:
    def test_track_call_and_prune(self):
        from services import news

        news._call_times.clear()
        with patch("services.news.time.time", return_value=1000.0):
            news._track_call()
            news._track_call()
        assert len(news._call_times) == 2

        with patch("services.news.time.time", return_value=1061.0):
            news._track_call()
        # Old calls > 60s should be pruned
        assert len(news._call_times) == 1


class TestGetApiUsage:
    def test_get_api_usage(self):
        from services import news

        news._call_times.clear()
        with patch("services.news.time.time", return_value=1000.0):
            news._track_call()
            news._track_call()
            news._track_call()
            usage = news.get_api_usage()
        assert usage["used_last_60s"] == 3
        assert usage["limit"] == 60
        assert usage["pct"] == 5


class TestFetchNews:
    def test_fetch_news_cache_hit(self):
        from services import news

        news._cache["AAPL"] = ([{"headline": "cached"}], 9999999999.0)
        result = news._fetch_news("AAPL", 7)
        assert result == [{"headline": "cached"}]
        del news._cache["AAPL"]

    def test_fetch_news_no_api_key(self):
        from services import news

        news._cache.clear()
        fake_settings = types.SimpleNamespace(finnhub_api_key="")
        with patch("config.get_settings", return_value=fake_settings):
            result = news._fetch_news("AAPL", 7)
        assert result == []

    def test_fetch_news_success(self):
        from services import news

        news._cache.clear()
        fake_settings = types.SimpleNamespace(finnhub_api_key="FAKE_KEY")
        mock_client = MagicMock()
        mock_client.company_news = MagicMock(return_value=[{"headline": "h1"}, {"headline": "h2"}] * 20)
        mock_finnhub = MagicMock()
        mock_finnhub.Client = MagicMock(return_value=mock_client)
        with patch.dict("sys.modules", {"finnhub": mock_finnhub}):
            with patch("config.get_settings", return_value=fake_settings):
                result = news._fetch_news("AAPL", 7)
        assert len(result) == 10
        assert result[0]["headline"] == "h1"
        # Ensure it was cached
        assert "AAPL" in news._cache
        del news._cache["AAPL"]

    def test_fetch_news_exception(self):
        from services import news

        news._cache.clear()
        fake_settings = types.SimpleNamespace(finnhub_api_key="FAKE_KEY")
        mock_client = MagicMock()
        mock_client.company_news = MagicMock(side_effect=Exception("boom"))
        mock_finnhub = MagicMock()
        mock_finnhub.Client = MagicMock(return_value=mock_client)
        with patch.dict("sys.modules", {"finnhub": mock_finnhub}):
            with patch("config.get_settings", return_value=fake_settings):
                result = news._fetch_news("AAPL", 7)
        assert result == []


class TestFetchAnalystRecs:
    def test_fetch_analyst_recs_cache_hit(self):
        from services import news

        news._rec_cache["AAPL"] = ({"period": "2026-05"}, 9999999999.0)
        result = news._fetch_analyst_recs("AAPL")
        assert result == {"period": "2026-05"}
        del news._rec_cache["AAPL"]

    def test_fetch_analyst_recs_no_api_key(self):
        from services import news

        news._rec_cache.clear()
        fake_settings = types.SimpleNamespace(finnhub_api_key="")
        with patch("config.get_settings", return_value=fake_settings):
            result = news._fetch_analyst_recs("AAPL")
        assert result == {}

    def test_fetch_analyst_recs_empty_raw(self):
        from services import news

        news._rec_cache.clear()
        fake_settings = types.SimpleNamespace(finnhub_api_key="FAKE_KEY")
        mock_client = MagicMock()
        mock_client.recommendation_trends = MagicMock(return_value=[])
        mock_finnhub = MagicMock()
        mock_finnhub.Client = MagicMock(return_value=mock_client)
        with patch.dict("sys.modules", {"finnhub": mock_finnhub}):
            with patch("config.get_settings", return_value=fake_settings):
                result = news._fetch_analyst_recs("AAPL")
        assert result == {}

    def test_fetch_analyst_recs_success_no_prior(self):
        from services import news

        news._rec_cache.clear()
        fake_settings = types.SimpleNamespace(finnhub_api_key="FAKE_KEY")
        mock_client = MagicMock()
        mock_client.recommendation_trends = MagicMock(
            return_value=[{"period": "2026-05", "strongBuy": 5, "buy": 4, "hold": 3, "sell": 2, "strongSell": 1}]
        )
        mock_client.company_basic_financials = MagicMock(return_value=None)
        mock_finnhub = MagicMock()
        mock_finnhub.Client = MagicMock(return_value=mock_client)
        with patch.dict("sys.modules", {"finnhub": mock_finnhub}):
            with patch("config.get_settings", return_value=fake_settings):
                result = news._fetch_analyst_recs("AAPL")
        assert result["period"] == "2026-05"
        assert result["strong_buy"] == 5
        assert "revision_pts" not in result

    def test_fetch_analyst_recs_success_with_revision(self):
        from services import news

        news._rec_cache.clear()
        fake_settings = types.SimpleNamespace(finnhub_api_key="FAKE_KEY")
        mock_client = MagicMock()
        mock_client.recommendation_trends = MagicMock(
            return_value=[
                {"period": "2026-05", "strongBuy": 5, "buy": 4, "hold": 3, "sell": 2, "strongSell": 1},
                {"period": "2026-04", "strongBuy": 3, "buy": 3, "hold": 3, "sell": 2, "strongSell": 2},
            ]
        )
        mock_client.company_basic_financials = MagicMock(return_value=None)
        mock_finnhub = MagicMock()
        mock_finnhub.Client = MagicMock(return_value=mock_client)
        with patch.dict("sys.modules", {"finnhub": mock_finnhub}):
            with patch("config.get_settings", return_value=fake_settings):
                result = news._fetch_analyst_recs("AAPL")
        # cur_bull = 5*2+4=14, prior_bull=3*2+3=9 => bull_delta=5
        # cur_bear = 1*2+2=4, prior_bear=2*2+2=6 => bear_delta=-2
        # rev_pts = max(-8, min(8, 5 - (-2))) = max(-8, min(8, 7)) = 7
        assert result["revision_pts"] == 7

    def test_fetch_analyst_recs_with_momentum(self):
        from services import news

        news._rec_cache.clear()
        fake_settings = types.SimpleNamespace(finnhub_api_key="FAKE_KEY")
        mock_client = MagicMock()
        mock_client.recommendation_trends = MagicMock(
            return_value=[
                {"period": "2026-05", "strongBuy": 1, "buy": 1, "hold": 1, "sell": 1, "strongSell": 1},
            ]
        )
        mock_client.company_basic_financials = MagicMock(
            return_value={
                "metric": {
                    "13WeekPriceReturnDaily": 3.0,
                    "26WeekPriceReturnDaily": 9.0,
                    "52WeekHigh": 200.0,
                    "52WeekLow": 100.0,
                }
            }
        )
        mock_finnhub = MagicMock()
        mock_finnhub.Client = MagicMock(return_value=mock_client)
        with patch.dict("sys.modules", {"finnhub": mock_finnhub}):
            with patch("config.get_settings", return_value=fake_settings):
                result = news._fetch_analyst_recs("AAPL")
        assert result["momentum_factor"] == pytest.approx(9.0 - 3.0 / 3.0, 0.01)
        assert result["return_26w"] == 9.0
        assert result["return_13w"] == 3.0
        assert result["fh_52w_high"] == 200.0
        assert result["fh_52w_low"] == 100.0

    def test_fetch_analyst_recs_exception(self):
        from services import news

        news._rec_cache.clear()
        fake_settings = types.SimpleNamespace(finnhub_api_key="FAKE_KEY")
        mock_client = MagicMock()
        mock_client.recommendation_trends = MagicMock(side_effect=Exception("api down"))
        mock_finnhub = MagicMock()
        mock_finnhub.Client = MagicMock(return_value=mock_client)
        with patch.dict("sys.modules", {"finnhub": mock_finnhub}):
            with patch("config.get_settings", return_value=fake_settings):
                result = news._fetch_analyst_recs("AAPL")
        assert result == {}

    def test_fetch_analyst_recs_basic_financials_exception(self):
        from services import news

        news._rec_cache.clear()
        fake_settings = types.SimpleNamespace(finnhub_api_key="FAKE_KEY")
        mock_client = MagicMock()
        mock_client.recommendation_trends = MagicMock(
            return_value=[
                {"period": "2026-05", "strongBuy": 1, "buy": 1, "hold": 1, "sell": 1, "strongSell": 1},
            ]
        )
        mock_client.company_basic_financials = MagicMock(side_effect=Exception("fin down"))
        mock_finnhub = MagicMock()
        mock_finnhub.Client = MagicMock(return_value=mock_client)
        with patch.dict("sys.modules", {"finnhub": mock_finnhub}):
            with patch("config.get_settings", return_value=fake_settings):
                result = news._fetch_analyst_recs("AAPL")
        # Should still return recommendation data despite basic_financials failure
        assert result["period"] == "2026-05"
        assert "momentum_factor" not in result

    def test_fetch_analyst_recs_no_momentum_if_r13_missing(self):
        from services import news

        news._rec_cache.clear()
        fake_settings = types.SimpleNamespace(finnhub_api_key="FAKE_KEY")
        mock_client = MagicMock()
        mock_client.recommendation_trends = MagicMock(
            return_value=[
                {"period": "2026-05", "strongBuy": 1, "buy": 1, "hold": 1, "sell": 1, "strongSell": 1},
            ]
        )
        mock_client.company_basic_financials = MagicMock(return_value={"metric": {"26WeekPriceReturnDaily": 9.0}})
        mock_finnhub = MagicMock()
        mock_finnhub.Client = MagicMock(return_value=mock_client)
        with patch.dict("sys.modules", {"finnhub": mock_finnhub}):
            with patch("config.get_settings", return_value=fake_settings):
                result = news._fetch_analyst_recs("AAPL")
        assert "momentum_factor" not in result


class TestGetAnalystRecs:
    @pytest.mark.asyncio
    async def test_redis_cache_hit(self):
        from services import news

        with patch("services.news.cache_get", new_callable=AsyncMock, return_value={"cached": True}):
            with patch("services.news.cache_set", new_callable=AsyncMock):
                result = await news.get_analyst_recs("AAPL")
        assert result == {"cached": True}

    @pytest.mark.asyncio
    async def test_redis_cache_miss_with_data(self):
        from services import news

        loop = asyncio.get_running_loop()
        with patch("services.news.cache_get", new_callable=AsyncMock, return_value=None):
            with patch("services.news.cache_set", new_callable=AsyncMock) as mock_cache_set:
                with patch.object(loop, "run_in_executor", new_callable=AsyncMock, return_value={"period": "2026-05"}):
                    result = await news.get_analyst_recs("AAPL")
        assert result == {"period": "2026-05"}
        mock_cache_set.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_redis_cache_miss_no_data(self):
        from services import news

        loop = asyncio.get_running_loop()
        with patch("services.news.cache_get", new_callable=AsyncMock, return_value=None):
            with patch("services.news.cache_set", new_callable=AsyncMock) as mock_cache_set:
                with patch.object(loop, "run_in_executor", new_callable=AsyncMock, return_value={}):
                    result = await news.get_analyst_recs("AAPL")
        assert result == {}
        mock_cache_set.assert_not_awaited()


class TestGetCompanyNews:
    @pytest.mark.asyncio
    async def test_redis_cache_hit(self):
        from services import news

        cached = [{"headline": "cached"}]
        with patch("services.news.cache_get", new_callable=AsyncMock, return_value=cached):
            with patch("services.news.cache_set", new_callable=AsyncMock):
                result = await news.get_company_news("AAPL")
        assert result == cached

    @pytest.mark.asyncio
    async def test_redis_cache_miss_with_items(self):
        from services import news

        loop = asyncio.get_running_loop()
        raw = [
            {
                "headline": "H1",
                "summary": "S1",
                "datetime": 0,
                "source": "src",
                "url": "http://x",
            }
        ]
        with patch("services.news.cache_get", new_callable=AsyncMock, return_value=None):
            with patch("services.news.cache_set", new_callable=AsyncMock) as mock_cache_set:
                with patch.object(loop, "run_in_executor", new_callable=AsyncMock, return_value=raw):
                    result = await news.get_company_news("AAPL")
        assert len(result) == 1
        assert result[0]["headline"] == "H1"
        assert result[0]["summary"] == "S1"
        assert result[0]["source"] == "src"
        mock_cache_set.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_redis_cache_miss_empty_items(self):
        from services import news

        loop = asyncio.get_running_loop()
        with patch("services.news.cache_get", new_callable=AsyncMock, return_value=None):
            with patch("services.news.cache_set", new_callable=AsyncMock) as mock_cache_set:
                with patch.object(loop, "run_in_executor", new_callable=AsyncMock, return_value=[]):
                    result = await news.get_company_news("AAPL")
        assert result == []
        mock_cache_set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_processes_fallback_summary(self):
        from services import news

        loop = asyncio.get_running_loop()
        raw = [
            {
                "headline": "H1",
                "summary": "",
                "datetime": 0,
                "source": "src",
                "url": "http://x",
            }
        ]
        with patch("services.news.cache_get", new_callable=AsyncMock, return_value=None):
            with patch("services.news.cache_set", new_callable=AsyncMock):
                with patch.object(loop, "run_in_executor", new_callable=AsyncMock, return_value=raw):
                    result = await news.get_company_news("AAPL")
        assert result[0]["summary"] == "H1"

    @pytest.mark.asyncio
    async def test_trims_summary(self):
        from services import news

        loop = asyncio.get_running_loop()
        long_summary = "x" * 400
        raw = [
            {
                "headline": "H1",
                "summary": long_summary,
                "datetime": 0,
                "source": "src",
                "url": "http://x",
            }
        ]
        with patch("services.news.cache_get", new_callable=AsyncMock, return_value=None):
            with patch("services.news.cache_set", new_callable=AsyncMock):
                with patch.object(loop, "run_in_executor", new_callable=AsyncMock, return_value=raw):
                    result = await news.get_company_news("AAPL")
        assert len(result[0]["summary"]) == 300

    @pytest.mark.asyncio
    async def test_hours_ago_zero_when_no_datetime(self):
        from services import news

        loop = asyncio.get_running_loop()
        raw = [
            {
                "headline": "H1",
                "summary": "S1",
                "datetime": 0,
                "source": "src",
                "url": "http://x",
            }
        ]
        with patch("services.news.cache_get", new_callable=AsyncMock, return_value=None):
            with patch("services.news.cache_set", new_callable=AsyncMock):
                with patch.object(loop, "run_in_executor", new_callable=AsyncMock, return_value=raw):
                    result = await news.get_company_news("AAPL")
        assert result[0]["hours_ago"] == 0

    @pytest.mark.asyncio
    async def test_caps_at_six_items(self):
        from services import news

        loop = asyncio.get_running_loop()
        raw = [
            {"headline": f"H{i}", "summary": "S", "datetime": 0, "source": "src", "url": "http://x"} for i in range(20)
        ]
        with patch("services.news.cache_get", new_callable=AsyncMock, return_value=None):
            with patch("services.news.cache_set", new_callable=AsyncMock):
                with patch.object(loop, "run_in_executor", new_callable=AsyncMock, return_value=raw):
                    result = await news.get_company_news("AAPL")
        assert len(result) == 6
