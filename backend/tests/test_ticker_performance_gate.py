"""Tests for the point-in-time ticker-performance gate."""

from datetime import datetime, timedelta, timezone

from services.gates.base import SignalContext
from services.gates.ticker_performance import (
    TickerPerformanceGate,
    cache_snapshot,
    compute_snapshot,
)


def _dt(days_ago: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days_ago)


def _ctx(ticker: str = "AAPL", action: str = "BUY", atr_pct_rank: float = 50.0) -> SignalContext:
    return SignalContext(
        action=action,
        confidence=60.0,
        score=55.0,
        rationale=[],
        sources=set(),
        ticker=ticker,
        tech={"atr_pct_rank": atr_pct_rank},
        info={},
        macro={},
        price=100.0,
        atr=2.0,
        has_mr=True,
        vix=20.0,
        sp500_trend="up",
        sector_etf="XLK",
        today_dow=1,
        month=6,
        opt_flow=None,
        sector_rs=None,
        earnings_cal={},
        days_to_earnings=None,
        is_low_atr=False,
        atr_pct_pre=0.02,
    )


def test_compute_snapshot_decay_weights_recent_wins_more():
    # Two losses 100 days ago, two wins 10 days ago.  Decay WR should be > raw WR.
    rows = [
        ("AAPL", "BUY", -2.0, _dt(100)),
        ("AAPL", "BUY", -1.5, _dt(95)),
        ("AAPL", "BUY", 1.0, _dt(10)),
        ("AAPL", "BUY", 1.5, _dt(5)),
    ]
    snap = compute_snapshot(rows, decay_halflife_days=30.0)
    stats = snap.get("AAPL", "BUY")
    assert stats is not None
    assert stats["n"] == 4
    assert stats["raw_win_rate"] == 0.5
    assert stats["decay_win_rate"] > stats["raw_win_rate"]


def test_compute_snapshot_respects_window():
    rows = [
        ("AAPL", "BUY", -2.0, _dt(200)),  # outside 180-day window
        ("AAPL", "BUY", 1.0, _dt(10)),
    ]
    snap = compute_snapshot(rows, window_days=180)
    stats = snap.get("AAPL", "BUY")
    assert stats is not None
    assert stats["n"] == 1


def test_gate_passes_without_snapshot():
    cache_snapshot(None)
    ctx = _ctx()
    TickerPerformanceGate(enabled=True).apply(ctx)
    assert ctx.action == "BUY"
    assert len(ctx.rationale) == 0


def test_gate_passes_with_insufficient_samples():
    rows = [("AAPL", "BUY", -2.0, _dt(10))]
    cache_snapshot(compute_snapshot(rows))
    ctx = _ctx()
    TickerPerformanceGate(enabled=True).apply(ctx)
    assert ctx.action == "BUY"
    # No rationale when n is below caution threshold.
    assert len(ctx.rationale) == 0


def test_enabled_gate_blocks_poor_performer():
    # 5 losses in the last 30 days -> decay WR ~0%.
    rows = [("AAPL", "BUY", -1.0, _dt(i)) for i in range(5, 0, -1)]
    cache_snapshot(compute_snapshot(rows, decay_halflife_days=30.0))
    ctx = _ctx()
    TickerPerformanceGate(enabled=True).apply(ctx)
    assert ctx.action == "HOLD"
    assert any("Ticker Performance Gate" in c["head"] for c in ctx.rationale)
    assert any("blocked" in c["head"].lower() for c in ctx.rationale)


def test_shadow_gate_does_not_block():
    rows = [("AAPL", "BUY", -1.0, _dt(i)) for i in range(5, 0, -1)]
    cache_snapshot(compute_snapshot(rows, decay_halflife_days=30.0))
    ctx = _ctx()
    TickerPerformanceGate(enabled=False).apply(ctx)
    assert ctx.action == "BUY"
    assert any("(shadow)" in c["head"] for c in ctx.rationale)


def test_gate_caution_reduces_size_instead_of_block():
    # 4 mixed outcomes -> decay WR below 50% but above block threshold.
    rows = [
        ("AAPL", "BUY", -2.0, _dt(5)),
        ("AAPL", "BUY", 1.0, _dt(4)),
        ("AAPL", "BUY", 1.5, _dt(3)),
        ("AAPL", "BUY", -0.5, _dt(2)),
    ]
    cache_snapshot(compute_snapshot(rows, decay_halflife_days=30.0))
    ctx = _ctx()
    TickerPerformanceGate(enabled=True).apply(ctx)
    assert ctx.action == "BUY"
    assert any("Size" in c["head"] for c in ctx.rationale)


def test_low_atr_turns_block_into_size_reduction():
    # 5 losses but ATR rank below floor -> size reduction, not block.
    rows = [("AAPL", "BUY", -1.0, _dt(i)) for i in range(5, 0, -1)]
    cache_snapshot(compute_snapshot(rows, decay_halflife_days=30.0))
    ctx = _ctx(atr_pct_rank=10.0)
    TickerPerformanceGate(enabled=True).apply(ctx)
    assert ctx.action == "BUY"
    assert any("size" in c["head"].lower() for c in ctx.rationale)


def test_auto_retirement_when_performance_improves():
    # First snapshot blocks (5 old losses); add 5 recent wins and refresh -> passes.
    rows_bad = [("AAPL", "BUY", -1.0, _dt(i + 20)) for i in range(5, 0, -1)]
    cache_snapshot(compute_snapshot(rows_bad, decay_halflife_days=30.0))
    ctx = _ctx()
    TickerPerformanceGate(enabled=True).apply(ctx)
    assert ctx.action == "HOLD"

    rows_good = rows_bad + [("AAPL", "BUY", 1.0, _dt(i)) for i in range(5, 0, -1)]
    cache_snapshot(compute_snapshot(rows_good, decay_halflife_days=30.0))
    ctx = _ctx()
    TickerPerformanceGate(enabled=True).apply(ctx)
    assert ctx.action == "BUY"


def test_gate_skips_non_buy_actions():
    rows = [("AAPL", "SELL", -1.0, _dt(i)) for i in range(5, 0, -1)]
    cache_snapshot(compute_snapshot(rows, decay_halflife_days=30.0))
    ctx = _ctx(action="SELL")
    TickerPerformanceGate(enabled=True).apply(ctx)
    assert ctx.action == "SELL"


def test_snapshot_case_insensitive_ticker():
    rows = [("aapl", "BUY", -1.0, _dt(i)) for i in range(5, 0, -1)]
    snap = compute_snapshot(rows, decay_halflife_days=30.0)
    cache_snapshot(snap)
    ctx = _ctx(ticker="AAPL")
    TickerPerformanceGate(enabled=True).apply(ctx)
    assert ctx.action == "HOLD"


def test_assembler_returns_ticker_perf_shadow_for_static_blocklist():
    from services.engines.assembler import _assemble_signal

    cache_snapshot(None)  # no dynamic snapshot -> dynamic passes
    sig = _assemble_signal(
        ticker="KO",
        info={"company": "Coca-Cola"},
        tech={"price": 60.0, "atr": 0.6, "atr_pct_rank": 25},
        score=55.0,
        rationale=[{"head": "RSI Oversold", "sentiment": "pos", "src": "Technical"}],
        sources={"Technical"},
        _force_hold=False,
        _is_low_atr=False,
        _atr_pct_pre=0.01,
        total_confidence_penalty=0.0,
        avg_sent=0.5,
        price=60.0,
        atr=0.6,
        market_ctx={"macro": {"sp500_trend": "up"}},
        earnings_cal={},
        sector_rs=None,
        days_to_earnings=15,
    )
    assert sig is not None
    assert sig["action"] == "HOLD"
    shadow = sig.get("_ticker_perf_shadow")
    assert shadow is not None
    assert shadow["ticker"] == "KO"
    assert shadow["static_blocked"] is True
    assert shadow["dynamic_decision"] == "pass"  # no snapshot
    assert shadow["hold_days"] is not None


def test_assembler_returns_ticker_perf_shadow_for_dynamic_block():
    from services.engines.assembler import _assemble_signal

    rows = [("AAPL", "BUY", -1.0, _dt(i)) for i in range(5, 0, -1)]
    cache_snapshot(compute_snapshot(rows, decay_halflife_days=30.0))
    sig = _assemble_signal(
        ticker="AAPL",
        info={"company": "Apple"},
        tech={"price": 100.0, "atr": 2.0, "atr_pct_rank": 25},
        score=55.0,
        rationale=[{"head": "RSI Oversold", "sentiment": "pos", "src": "Technical"}],
        sources={"Technical"},
        _force_hold=False,
        _is_low_atr=False,
        _atr_pct_pre=0.02,
        total_confidence_penalty=0.0,
        avg_sent=0.5,
        price=100.0,
        atr=2.0,
        market_ctx={"macro": {"sp500_trend": "up"}},
        earnings_cal={},
        sector_rs=None,
        days_to_earnings=15,
    )
    assert sig is not None
    shadow = sig.get("_ticker_perf_shadow")
    assert shadow is not None
    assert shadow["ticker"] == "AAPL"
    assert shadow["static_blocked"] is False
    assert shadow["dynamic_decision"] == "block"
    assert shadow["dynamic_n"] == 5
    assert shadow["dynamic_decay_wr"] < 0.5
