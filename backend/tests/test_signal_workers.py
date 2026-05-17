"""
Tests for services/signal_workers.py pure/sync-reachable logic.

Workers are async functions decorated with @WorkerTask.
We test them by:
  1. Mocking their internal service calls (Benzinga, options, etc.)
  2. Calling them directly via asyncio.run / pytest-asyncio
  3. Asserting on the returned ScoringResult

Also tests the ScoringResult and WorkerTask infrastructure.
"""
import sys
import os
import asyncio
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from unittest.mock import AsyncMock, MagicMock, patch
from services.worker_bus import ScoringResult, WorkerTask, CircuitBreaker


# ── ScoringResult dataclass ────────────────────────────────────────────────────

class TestScoringResult:

    def test_default_values(self):
        r = ScoringResult()
        assert r.score == 0.0
        assert r.sources == set()
        assert r.rationale == []
        assert r.ok is True

    def test_ok_false(self):
        r = ScoringResult(ok=False)
        assert r.ok is False

    def test_score_assignment(self):
        r = ScoringResult(score=42.0)
        assert r.score == 42.0

    def test_sources_is_independent_per_instance(self):
        r1 = ScoringResult()
        r2 = ScoringResult()
        r1.sources.add("Finnhub")
        assert "Finnhub" not in r2.sources


# ── CircuitBreaker ─────────────────────────────────────────────────────────────

class TestCircuitBreaker:

    def test_starts_closed(self):
        cb = CircuitBreaker("test", threshold=3, reset_secs=60.0)
        assert not cb.is_open()

    def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker("test", threshold=3, reset_secs=60.0)
        for _ in range(3):
            cb.record_failure()
        assert cb.is_open()

    def test_does_not_open_before_threshold(self):
        cb = CircuitBreaker("test", threshold=3, reset_secs=60.0)
        cb.record_failure()
        cb.record_failure()
        assert not cb.is_open()

    def test_success_resets_failure_count(self):
        cb = CircuitBreaker("test", threshold=3, reset_secs=60.0)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert not cb.is_open()
        # Two failures after reset should not open
        cb.record_failure()
        cb.record_failure()
        assert not cb.is_open()

    def test_resets_after_timeout(self):
        import time
        cb = CircuitBreaker("test", threshold=1, reset_secs=0.01)
        cb.record_failure()
        assert cb.is_open()
        time.sleep(0.05)
        # After reset_secs, is_open() should return False and reset state
        assert not cb.is_open()


# ── WorkerTask decorator ───────────────────────────────────────────────────────

class TestWorkerTask:

    def test_wraps_function_correctly(self):
        @WorkerTask(name="test_w", timeout=5.0, retries=1)
        async def dummy_worker():
            return ScoringResult(score=10.0)

        assert callable(dummy_worker)

    @pytest.mark.asyncio
    async def test_successful_call_returns_result(self):
        @WorkerTask(name="ok_w", timeout=5.0, retries=1)
        async def ok_worker():
            return ScoringResult(score=5.0)

        result = await ok_worker()
        assert result.ok is True
        assert result.score == 5.0

    @pytest.mark.asyncio
    async def test_timeout_returns_ok_false(self):
        @WorkerTask(name="slow_w", timeout=0.01, retries=1)
        async def slow_worker():
            await asyncio.sleep(5)
            return ScoringResult(score=99.0)

        result = await slow_worker()
        assert result.ok is False

    @pytest.mark.asyncio
    async def test_exception_returns_ok_false(self):
        @WorkerTask(name="exc_w", timeout=5.0, retries=1)
        async def bad_worker():
            raise RuntimeError("something broke")

        result = await bad_worker()
        assert result.ok is False

    @pytest.mark.asyncio
    async def test_circuit_open_skips_call(self):
        @WorkerTask(name="cb_w", timeout=5.0, retries=1, cb_threshold=1)
        async def flaky_worker():
            raise RuntimeError("always fails")

        # Trigger circuit open
        await flaky_worker()
        # Now circuit should be open — next call returns ok=False immediately
        result = await flaky_worker()
        assert result.ok is False

    def test_stats_property(self):
        @WorkerTask(name="stats_w", timeout=5.0, retries=1)
        async def stat_worker():
            return ScoringResult()

        stats = stat_worker._task.stats
        assert "name" in stats
        assert stats["name"] == "stats_w"
        assert "calls" in stats
        assert "errors" in stats


# ── news_worker ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_news_worker_empty_inputs():
    """news_worker with no news items returns ok=True and score=0."""
    with patch("services.benzinga_news.get_benzinga_news", new=AsyncMock(return_value=[])):
        from services.signal_workers import news_worker
        result = await news_worker(ticker="AAPL", news=[], scraped_news=[])
    assert result.ok is True
    assert result.score == 0


@pytest.mark.asyncio
async def test_news_worker_positive_sentiment():
    """Strongly positive average sentiment should add to score."""
    items = [{"headline": "Big earnings beat", "sentiment": 0.8, "hours_ago": 1, "source": "Finnhub"}]
    with patch("services.benzinga_news.get_benzinga_news", new=AsyncMock(return_value=[])):
        from services.signal_workers import news_worker
        result = await news_worker(ticker="AAPL", news=items, scraped_news=[])
    assert result.score > 0


@pytest.mark.asyncio
async def test_news_worker_negative_sentiment():
    """Strongly negative average sentiment should subtract from score."""
    items = [{"headline": "Massive miss, fraud probe", "sentiment": -0.9, "hours_ago": 1, "source": "Finnhub"}]
    with patch("services.benzinga_news.get_benzinga_news", new=AsyncMock(return_value=[])):
        from services.signal_workers import news_worker
        result = await news_worker(ticker="AAPL", news=items, scraped_news=[])
    assert result.score < 0


@pytest.mark.asyncio
async def test_news_worker_neutral_no_rationale():
    """Neutral sentiment (|avg| < 0.25) should produce no rationale."""
    items = [{"headline": "Stock moved sideways", "sentiment": 0.1, "hours_ago": 2, "source": "Finnhub"}]
    with patch("services.benzinga_news.get_benzinga_news", new=AsyncMock(return_value=[])):
        from services.signal_workers import news_worker
        result = await news_worker(ticker="AAPL", news=items, scraped_news=[])
    assert result.rationale == []


# ── options_worker ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_options_worker_no_data():
    """options_worker with no opt_flow and no massive_sigs → score=0."""
    from services.signal_workers import options_worker
    result = await options_worker(ticker="AAPL", opt_flow=None, massive_sigs=None)
    assert result.ok is True
    assert result.score == 0


@pytest.mark.asyncio
async def test_options_worker_high_dark_pool_short():
    """Dark pool short volume > 55% → bearish signal."""
    massive_sigs = {"short_interest": {"short_volume_pct": 60.0}, "ftd": {}, "gex": {}, "retail_vs_institutional": {}}
    from services.signal_workers import options_worker
    result = await options_worker(ticker="TSLA", opt_flow=None, massive_sigs=massive_sigs)
    assert result.score < 0
    assert "Dark Pool" in result.sources


@pytest.mark.asyncio
async def test_options_worker_low_dark_pool_short():
    """Dark pool short volume < 35% → bullish signal."""
    massive_sigs = {"short_interest": {"short_volume_pct": 25.0}, "ftd": {}, "gex": {}, "retail_vs_institutional": {}}
    from services.signal_workers import options_worker
    result = await options_worker(ticker="TSLA", opt_flow=None, massive_sigs=massive_sigs)
    assert result.score > 0


# ── institutional_worker ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_institutional_worker_no_data():
    """No insider or market_ctx → score=0."""
    from services.signal_workers import institutional_worker
    result = await institutional_worker(ticker="AAPL", insider=None, market_ctx=None)
    assert result.ok is True
    assert result.score == 0


@pytest.mark.asyncio
async def test_institutional_worker_insider_buy():
    """Cluster insider buying with positive score adds to result."""
    insider = {"filings": 3, "score": 8, "net_shares": 5000}
    from services.signal_workers import institutional_worker
    result = await institutional_worker(ticker="AAPL", insider=insider, market_ctx=None)
    assert result.score == 8
    assert "SEC EDGAR" in result.sources


@pytest.mark.asyncio
async def test_institutional_worker_insider_sell():
    """Cluster insider selling with negative score subtracts from result."""
    insider = {"filings": 2, "score": -6, "net_shares": -10000}
    from services.signal_workers import institutional_worker
    result = await institutional_worker(ticker="AAPL", insider=insider, market_ctx=None)
    assert result.score == -6


# ── sentiment_worker ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_sentiment_worker_no_data():
    """No social/trends/congress → score=0."""
    from services.signal_workers import sentiment_worker
    result = await sentiment_worker(ticker="AAPL", social=None, trends=None, congress=None)
    assert result.ok is True
    assert result.score == 0


@pytest.mark.asyncio
async def test_sentiment_worker_high_bull_pct():
    """StockTwits bull% >= 70 → positive score."""
    from services.signal_workers import sentiment_worker
    result = await sentiment_worker(
        ticker="AAPL",
        social={"bull_pct": 75.0, "wsb_mentions_velocity": 0},
        trends=None,
        congress=None,
    )
    assert result.score > 0
    assert "Social" in result.sources


@pytest.mark.asyncio
async def test_sentiment_worker_low_bull_pct():
    """StockTwits bull% <= 30 → negative score."""
    from services.signal_workers import sentiment_worker
    result = await sentiment_worker(
        ticker="AAPL",
        social={"bull_pct": 20.0, "wsb_mentions_velocity": 0},
        trends=None,
        congress=None,
    )
    assert result.score < 0


@pytest.mark.asyncio
async def test_sentiment_worker_wsb_velocity():
    """WSB mention velocity > 2 → adds bonus."""
    from services.signal_workers import sentiment_worker
    result = await sentiment_worker(
        ticker="GME",
        social={"bull_pct": 50.0, "wsb_mentions_velocity": 3.0},
        trends=None,
        congress=None,
    )
    assert result.score > 0


# ── options_worker extended coverage ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_options_worker_reg_sho_ftd_spike():
    """Reg SHO + FTD spike > 300% → adds 15 points."""
    massive_sigs = {
        "short_interest": {"short_volume_pct": 40.0},
        "ftd": {"is_reg_sho": True, "spike_pct": 400.0},
        "gex": {},
        "retail_vs_institutional": {},
    }
    from services.signal_workers import options_worker
    result = await options_worker(ticker="BBBY", opt_flow=None, massive_sigs=massive_sigs)
    assert result.score >= 15
    assert "Fundamentals" in result.sources


@pytest.mark.asyncio
async def test_options_worker_positive_gex():
    """Positive GEX > 1M → adds rationale (no score change but sources added)."""
    massive_sigs = {
        "short_interest": {"short_volume_pct": 40.0},
        "ftd": {},
        "gex": {"net_gex": 2_000_000.0},
        "retail_vs_institutional": {},
    }
    from services.signal_workers import options_worker
    result = await options_worker(ticker="SPY", opt_flow=None, massive_sigs=massive_sigs)
    assert "Options" in result.sources
    assert any("GEX" in r["head"] for r in result.rationale)


@pytest.mark.asyncio
async def test_options_worker_negative_gex():
    """Negative GEX < -1M → adds negative GEX rationale."""
    massive_sigs = {
        "short_interest": {"short_volume_pct": 40.0},
        "ftd": {},
        "gex": {"net_gex": -2_000_000.0},
        "retail_vs_institutional": {},
    }
    from services.signal_workers import options_worker
    result = await options_worker(ticker="SPY", opt_flow=None, massive_sigs=massive_sigs)
    assert any("Negative Gamma" in r["head"] for r in result.rationale)


@pytest.mark.asyncio
async def test_options_worker_institutional_buying_vs_retail():
    """Institutional buying vs retail selling → bullish divergence signal."""
    massive_sigs = {
        "short_interest": {"short_volume_pct": 40.0},
        "ftd": {},
        "gex": {},
        "retail_vs_institutional": {
            "institutional_flow_usd": 1_000_000.0,
            "retail_flow_usd": -500_000.0,
        },
    }
    from services.signal_workers import options_worker
    result = await options_worker(ticker="AAPL", opt_flow=None, massive_sigs=massive_sigs)
    assert result.score > 0
    assert "Dark Pool" in result.sources


@pytest.mark.asyncio
async def test_options_worker_institutional_selling_vs_retail():
    """Institutional selling vs retail buying → bearish divergence signal."""
    massive_sigs = {
        "short_interest": {"short_volume_pct": 40.0},
        "ftd": {},
        "gex": {},
        "retail_vs_institutional": {
            "institutional_flow_usd": -1_000_000.0,
            "retail_flow_usd": 500_000.0,
        },
    }
    from services.signal_workers import options_worker
    result = await options_worker(ticker="AAPL", opt_flow=None, massive_sigs=massive_sigs)
    assert result.score < 0


@pytest.mark.asyncio
async def test_options_worker_opt_flow_with_score():
    """opt_flow is passed and score_options returns a non-zero score."""
    from services.signal_workers import options_worker
    with patch("services.options.score_options", return_value=(15, [{"src": "Options", "head": "Call Sweep"}])):
        result = await options_worker(ticker="TSLA", opt_flow={"data": "present"}, massive_sigs=None)
    assert result.score == 15
    assert "Options" in result.sources


# ── fundamentals_worker coverage ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fundamentals_worker_empty_fundamentals():
    """Empty fundamentals dict → score=0."""
    from services.signal_workers import fundamentals_worker
    result = await fundamentals_worker(ticker="AAPL", fundamentals={}, market_ctx=None, price=150.0)
    assert result.ok is True
    assert result.score == 0


@pytest.mark.asyncio
async def test_fundamentals_worker_high_piotroski():
    """F-Score >= 7 → +12 score with rationale."""
    with patch("services.massive_ratios.get_polygon_dividend_data", new=AsyncMock(return_value={})), \
         patch("services.massive_ratios.get_annual_revenue_acceleration", new=AsyncMock(return_value={})), \
         patch("services.polygon_reference.get_float_data", new=AsyncMock(return_value={})):
        from services.signal_workers import fundamentals_worker
        result = await fundamentals_worker(
            ticker="AAPL",
            fundamentals={"piotroski_f": 8},
            market_ctx=None,
            price=150.0,
        )
    assert result.score >= 12
    assert any("F-Score" in r["head"] for r in result.rationale)


@pytest.mark.asyncio
async def test_fundamentals_worker_low_piotroski():
    """F-Score <= 2 → -10 score."""
    with patch("services.massive_ratios.get_polygon_dividend_data", new=AsyncMock(return_value={})), \
         patch("services.massive_ratios.get_annual_revenue_acceleration", new=AsyncMock(return_value={})), \
         patch("services.polygon_reference.get_float_data", new=AsyncMock(return_value={})):
        from services.signal_workers import fundamentals_worker
        result = await fundamentals_worker(
            ticker="AAPL",
            fundamentals={"piotroski_f": 1},
            market_ctx=None,
            price=150.0,
        )
    assert result.score <= -10


@pytest.mark.asyncio
async def test_fundamentals_worker_high_fcf_yield():
    """FCF yield > 8% → +8 score."""
    with patch("services.massive_ratios.get_polygon_dividend_data", new=AsyncMock(return_value={})), \
         patch("services.massive_ratios.get_annual_revenue_acceleration", new=AsyncMock(return_value={})), \
         patch("services.polygon_reference.get_float_data", new=AsyncMock(return_value={})):
        from services.signal_workers import fundamentals_worker
        result = await fundamentals_worker(
            ticker="AAPL",
            fundamentals={"fcf_yield": 10.0},
            market_ctx=None,
            price=150.0,
        )
    assert result.score >= 8


@pytest.mark.asyncio
async def test_fundamentals_worker_negative_fcf():
    """Negative FCF → -6 score."""
    with patch("services.massive_ratios.get_polygon_dividend_data", new=AsyncMock(return_value={})), \
         patch("services.massive_ratios.get_annual_revenue_acceleration", new=AsyncMock(return_value={})), \
         patch("services.polygon_reference.get_float_data", new=AsyncMock(return_value={})):
        from services.signal_workers import fundamentals_worker
        result = await fundamentals_worker(
            ticker="AAPL",
            fundamentals={"fcf_yield": -2.0},
            market_ctx=None,
            price=150.0,
        )
    assert result.score <= -6


# ── institutional_worker 13F path ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_institutional_worker_13f_accumulation():
    """13F institutional accumulation adds score and rationale."""
    market_ctx = {
        "institutional_signals": {
            "AAPL": {"score": 8, "qoq_trend": "increasing"},
        }
    }
    from services.signal_workers import institutional_worker
    result = await institutional_worker(ticker="AAPL", insider=None, market_ctx=market_ctx)
    assert result.score == 8
    assert "13F" in result.sources
    assert any("Accumulation" in r["head"] for r in result.rationale)


@pytest.mark.asyncio
async def test_institutional_worker_13f_distribution():
    """13F institutional distribution subtracts score."""
    market_ctx = {
        "institutional_signals": {
            "TSLA": {"score": -6, "qoq_trend": "decreasing"},
        }
    }
    from services.signal_workers import institutional_worker
    result = await institutional_worker(ticker="TSLA", insider=None, market_ctx=market_ctx)
    assert result.score == -6
    assert "13F" in result.sources


@pytest.mark.asyncio
async def test_institutional_worker_insider_small_score_no_source():
    """Insider score < 4 adds score but doesn't add SEC EDGAR source or rationale."""
    insider = {"filings": 1, "score": 2, "net_shares": 100}
    from services.signal_workers import institutional_worker
    result = await institutional_worker(ticker="AAPL", insider=insider, market_ctx=None)
    assert result.score == 2
    assert "SEC EDGAR" not in result.sources
    assert result.rationale == []


# ── sentiment_worker congress path ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_sentiment_worker_congress_buying():
    """Congress buying with score >= 4 → adds score and rationale."""
    from services.signal_workers import sentiment_worker
    result = await sentiment_worker(
        ticker="NVDA",
        social=None,
        trends=None,
        congress={"score": 5},
    )
    assert result.score == 5
    assert "Congress" in result.sources


@pytest.mark.asyncio
async def test_sentiment_worker_congress_selling():
    """Congress selling with score <= -4 → subtracts score."""
    from services.signal_workers import sentiment_worker
    result = await sentiment_worker(
        ticker="NVDA",
        social=None,
        trends=None,
        congress={"score": -5},
    )
    assert result.score == -5


@pytest.mark.asyncio
async def test_sentiment_worker_google_trends_positive():
    """Trends score >= 3 → adds to result."""
    from services.signal_workers import sentiment_worker
    result = await sentiment_worker(
        ticker="AAPL",
        social=None,
        trends={"score": 4},
        congress=None,
    )
    assert result.score == 4
    assert "Social" in result.sources


@pytest.mark.asyncio
async def test_sentiment_worker_google_trends_negative():
    """Trends score <= -3 → subtracts."""
    from services.signal_workers import sentiment_worker
    result = await sentiment_worker(
        ticker="AAPL",
        social=None,
        trends={"score": -4},
        congress=None,
    )
    assert result.score == -4


@pytest.mark.asyncio
async def test_sentiment_worker_trends_below_threshold_ignored():
    """Trends score abs < 3 → ignored."""
    from services.signal_workers import sentiment_worker
    result = await sentiment_worker(
        ticker="AAPL",
        social=None,
        trends={"score": 2},
        congress=None,
    )
    assert result.score == 0
