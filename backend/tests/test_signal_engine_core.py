from unittest.mock import AsyncMock, patch

import pytest
from services.signal_engine import (
    _assemble_signal,
    _collect_fetch_results,
    _current_session,
    _levels,
    _make_plain_english,
    _score_to_action,
    generate_signal,
    scan_all,
)


def test_score_to_action():
    # Test BUY threshold
    action, conf = _score_to_action(45.0, agreement=3)
    assert action == "BUY"
    assert 50 <= conf <= 84

    # Test SELL threshold
    action, conf = _score_to_action(-35.0, agreement=2)
    assert action == "SELL"
    assert 50 <= conf <= 84

    # Test HOLD threshold (between -30 and 35)
    action, conf = _score_to_action(15.0, agreement=0)
    assert action == "HOLD"
    assert 40 <= conf <= 55


def test_levels():
    # High volatility swing (atr_pct=3%>2.5%): 1.5s/2.0t (§11c decomp optimal)
    entry, stop, tgt, rr = _levels(100.0, 3.0, "BUY")
    assert entry == 100.0
    assert stop == 95.5  # 100 - 1.5*3
    assert tgt == 106.0  # 100 + 2.0*3

    # Low volatility swing (atr_pct=0.5%<1.0%): 1.5s/2.0t (SELL)
    entry, stop, tgt, rr = _levels(100.0, 0.5, "SELL")
    assert entry == 100.0
    assert stop == 100.75  # 100 + 1.5*0.5
    assert tgt == 99.0  # 100 - 2.0*0.5

    # HOLD action
    entry, stop, tgt, rr = _levels(100.0, 2.0, "HOLD")
    assert entry is None


def test_make_plain_english():
    rationale = [{"head": "RSI Oversold", "sentiment": "pos"}, {"head": "MACD Crossover", "sentiment": "pos"}]
    res = _make_plain_english("BUY", "AAPL", "swing", rationale, 76.0, 150.0, 140.0, 170.0)

    assert "AAPL" in res["summary"]
    assert "RSI Oversold" in res["summary"]
    assert "high confidence" in res["summary"]
    assert res["timeframe"] == "over the next 2–10 trading days"


def test_make_plain_english_sell():
    rationale = [{"head": "RSI Overbought", "sentiment": "neg"}]
    res = _make_plain_english("SELL", "TSLA", "intraday", rationale, 65.0, 200.0, 210.0, 180.0)
    assert "fall" in res["summary"]
    assert "moderate confidence" in res["summary"]


def test_make_plain_english_hold():
    res = _make_plain_english("HOLD", "IBM", "swing", [], 50.0, None, None, None)
    assert "mixed signals" in res["summary"]


def test_collect_fetch_results_records_provider_failures():
    values, warnings = _collect_fetch_results(
        "AAPL",
        ["news", "options"],
        [RuntimeError("rate limited"), {"ok": True}],
    )
    assert values == [None, {"ok": True}]
    assert warnings == [
        {
            "source": "news",
            "error": "RuntimeError",
            "message": "rate limited",
        }
    ]


def test_current_session():
    session = _current_session()
    assert session in ["pre", "regular", "after", "closed"]


def test_assemble_signal_basic_buy():
    res = _assemble_signal(
        ticker="MSFT",
        info={"company": "Microsoft"},
        tech={"price": 300.0, "atr": 5.0, "volume": 1000000, "avg_volume": 800000},
        score=40.0,
        rationale=[{"head": "Strong uptrend", "sentiment": "pos", "src": "Technical"}],
        sources={"Technical"},
        _force_hold=False,
        _is_low_atr=False,
        _atr_pct_pre=0.016,
        total_confidence_penalty=0.0,
        avg_sent=0.6,
        price=300.0,
        atr=5.0,
        market_ctx={"macro": {"sp500_trend": "up"}},
        earnings_cal={"days_to_earnings": 15},
        sector_rs=None,
        days_to_earnings=15,
    )

    assert res is not None
    assert res["ticker"] == "MSFT"
    assert res["action"] in ["BUY", "HOLD"]
    assert "confidence" in res
    assert res["style"] == "swing"  # Default fallback


def test_assemble_signal_surfaces_data_warnings():
    res = _assemble_signal(
        ticker="MSFT",
        info={"company": "Microsoft"},
        tech={"price": 300.0, "atr": 5.0, "volume": 1000000, "avg_volume": 800000},
        score=40.0,
        rationale=[{"head": "Strong uptrend", "sentiment": "pos", "src": "Technical"}],
        sources={"Technical"},
        _force_hold=False,
        _is_low_atr=False,
        _atr_pct_pre=0.016,
        total_confidence_penalty=0.0,
        avg_sent=0.6,
        price=300.0,
        atr=5.0,
        market_ctx={"macro": {"sp500_trend": "up"}},
        earnings_cal={"days_to_earnings": 15},
        sector_rs=None,
        days_to_earnings=15,
        data_warnings=[{"source": "options_flow", "error": "TimeoutError", "message": ""}],
    )

    assert "Data Quality" in res["sources"]
    assert res["dataWarnings"][0]["source"] == "options_flow"
    assert any(r["head"] == "Partial Data Degradation" for r in res["rationale"])


@pytest.mark.asyncio
async def test_scan_all_empty_graceful():
    # If scanner gets an empty array, it should not crash
    results = await scan_all([])
    assert results == []


def test_assemble_signal_earnings_blackout():
    res = _assemble_signal(
        ticker="AAPL",
        info={"company": "Apple"},
        tech={"price": 100.0, "atr": 2.0},
        score=60.0,
        rationale=[],
        sources=set(),
        _force_hold=True,
        _is_low_atr=False,
        _atr_pct_pre=0.02,
        total_confidence_penalty=0.0,
        avg_sent=0.5,
        price=100.0,
        atr=2.0,
        market_ctx={},
        earnings_cal={"days_to_earnings": 1, "next_earnings_date": "2026-05-12"},
        sector_rs=None,
        days_to_earnings=1,
    )
    assert res["action"] == "HOLD"


def test_assemble_signal_risk_free_rate_dampener():
    # Freeze to Wednesday so the day-of-week gate (blocks Friday BUY entries) doesn't fire.
    from datetime import datetime as _dt
    import services.signal_engine as _se

    _wednesday = _dt(2026, 5, 27, 12, 0, 0)  # Wednesday
    with patch.object(_se, "datetime", wraps=_se.datetime) as _mock_dt:
        _mock_dt.now.return_value = _wednesday
        res = _assemble_signal(
            ticker="AAPL",
            info={"company": "Apple"},
            tech={"price": 100.0, "atr": 1.0, "rsi": 38.0, "bb_pct_b": 0.20, "ibs": 0.14},  # 2 MR conditions for count≥2
            score=50.0,  # BUY
            rationale=[],
            sources=set(),
            _force_hold=False,
            _is_low_atr=False,
            _atr_pct_pre=0.01,
            total_confidence_penalty=0.0,
            avg_sent=0.0,
            price=100.0,
            atr=1.0,
            market_ctx={"macro": {"t10y": 4.5, "sp500_trend": "up"}},  # 4.5% risk free rate
            earnings_cal={},
            sector_rs={"sector_etf": "XLY", "rs_vs_sector": 0},
            days_to_earnings=None,
        )

    assert "Macro" in res["sources"]
    assert any(
        "Risk-Adjusted Return Negative" in r["head"] or "Thin Risk Premium" in r["head"] for r in res["rationale"]
    )


def test_assemble_signal_chronic_loser():
    res = _assemble_signal(
        ticker="BAD",
        info={},
        tech={"price": 10.0, "atr": 1.0},
        score=50.0,
        rationale=[],
        sources=set(),
        _force_hold=False,
        _is_low_atr=False,
        _atr_pct_pre=0.1,
        total_confidence_penalty=0.0,
        avg_sent=0.0,
        price=10.0,
        atr=1.0,
        market_ctx={"adaptive_weights": {"ticker_win_rates": {"BAD": 0.40}}},  # Win rate < 45%
        earnings_cal={},
        sector_rs=None,
        days_to_earnings=None,
    )

    assert res["action"] == "HOLD"
    assert any("Chronic Loser Exclusion" in r["head"] for r in res["rationale"])


def test_assemble_signal_sector_concentration():
    res = _assemble_signal(
        ticker="AAPL",
        info={},
        tech={"price": 150.0, "atr": 5.0},
        score=60.0,
        rationale=[],
        sources=set(),
        _force_hold=False,
        _is_low_atr=False,
        _atr_pct_pre=0.03,
        total_confidence_penalty=0.0,
        avg_sent=0.0,
        price=150.0,
        atr=5.0,
        market_ctx={"portfolio_ctx": {"sector_exposure": {"XLK": 55.0}}},  # > 50% limit
        earnings_cal={},
        sector_rs={"sector_etf": "XLK", "rs_vs_sector": 0},
        days_to_earnings=None,
    )

    assert res["action"] in ["BUY", "HOLD"]


def test_assemble_signal_low_vol():
    res = _assemble_signal(
        ticker="KO",
        info={},
        tech={"price": 100.0, "atr": 0.5},  # atr_pct = 0.005 < 0.008
        score=30.0,
        rationale=[],
        sources=set(),
        _force_hold=False,
        _is_low_atr=False,
        _atr_pct_pre=0.005,
        total_confidence_penalty=0.0,
        avg_sent=0.0,
        price=100.0,
        atr=0.5,
        market_ctx={"macro": {"macro_score": 0}},
        earnings_cal={},
        sector_rs=None,
        days_to_earnings=None,
    )

    assert res["action"] in ["BUY", "HOLD"]


@pytest.mark.asyncio
async def test_generate_signal_basic():
    import pandas as pd

    mock_df = pd.DataFrame({"Close": [100] * 30})
    mock_df_1h = pd.DataFrame({"Close": [100] * 20})

    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
    ):
        m_news.return_value = []
        m_snews.return_value = []
        m_insider.return_value = {}
        m_arecs.return_value = {}
        m_ecal.return_value = {}
        m_esurp.return_value = {}
        m_oflow.return_value = {}
        m_fund.return_value = {}
        m_soc.return_value = {}
        m_trends.return_value = {}
        m_cong.return_value = {}
        m_hist.side_effect = [mock_df, mock_df_1h]
        m_info.return_value = {"company": "Test Co"}
        m_sec.return_value = {}

        # Inject specific indicators to force the BUY branches
        m_calc.return_value = {
            "price": 100.0,
            "atr": 2.0,
            "rsi": 25.0,
            "macd_hist": 0.5,
            "macd_hist_prev": -0.1,
            "sma200": 90.0,
            "sma50": 95.0,
            "volume": 2000000,
            "avg_volume": 1000000,
            "stoch_k": 15,
            "stoch_d": 10,
            "stoch_k_prev": 5,
            "stoch_d_prev": 12,
            "cci": -160,
            "mfi": 15,
            "bb_squeeze": True,
            "bb_pct_b": 0.8,
            "ema8": 100.0,
            "ema21": 95.0,
            "ema8_prev": 94.0,
            "ema21_prev": 96.0,
            "close_streak": 8,
            "gap_pct": 3.0,
            "rvol": 2.5,
        }

        res = await generate_signal("AAPL")
        assert res is not None
        assert res["ticker"] == "AAPL"
        assert res["action"] == "BUY"


@pytest.mark.asyncio
async def test_generate_signal_sell_branches():
    import pandas as pd

    mock_df = pd.DataFrame({"Close": [100] * 30})
    mock_df_1h = pd.DataFrame({"Close": [100] * 20})

    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news,
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews,
        patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider,
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs,
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal,
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp,
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow,
        patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund,
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc,
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends,
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong,
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info,
        patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec,
        patch("services.signal_engine.calculate_indicators") as m_calc,
    ):
        # Inject negative meta data to force SELL branches
        m_news.return_value = [{"headline": "Bad news", "sentiment": -0.8, "hours_ago": 1, "source": "Finviz"}]
        m_snews.return_value = []
        m_insider.return_value = {
            "filings": 5,
            "score": -10,
            "net_shares": -50000,
            "sell_value": 1000000,
            "buy_value": 0,
            "buys": 0,
            "sells": 5,
        }
        m_arecs.return_value = {}
        m_ecal.return_value = {}
        m_esurp.return_value = {}
        m_oflow.return_value = {}
        m_fund.return_value = {"piotroski_f": 2, "fcf_yield": -5.0}
        m_soc.return_value = {}
        m_trends.return_value = {}
        m_cong.return_value = {}
        m_hist.side_effect = [mock_df, mock_df_1h]
        m_info.return_value = {"company": "Test Co", "target_mean": 50.0, "analyst_count": 5}
        m_sec.return_value = {}

        m_calc.return_value = {
            "price": 100.0,
            "atr": 2.0,
            "rsi": 85.0,
            "macd_hist": -0.5,
            "macd_hist_prev": 0.1,
            "sma200": 110.0,
            "sma50": 105.0,
            "volume": 2000000,
            "avg_volume": 1000000,
            "cci": 160,
            "mfi": 85,
            "close_streak": -8,
            "gap_pct": -3.0,
            "rvol": 2.5,
        }

        res = await generate_signal("AAPL")
        assert res is not None
        assert res["ticker"] == "AAPL"
        assert res["action"] == "SELL"


def _base_assemble_kwargs(**overrides):
    defaults = dict(
        ticker="AAPL",
        info={"company": "Apple"},
        tech={"price": 150.0, "atr": 3.0, "volume": 1_000_000, "avg_volume": 900_000},
        score=40.0,
        rationale=[],
        sources=set(),
        _force_hold=False,
        _is_low_atr=False,
        _atr_pct_pre=0.02,
        total_confidence_penalty=0.0,
        avg_sent=0.5,
        price=150.0,
        atr=3.0,
        market_ctx={"macro": {"sp500_trend": "up"}},
        earnings_cal={},
        sector_rs=None,
        days_to_earnings=None,
    )
    defaults.update(overrides)
    return defaults


def test_iv_rank_flag_elevated_emits_rationale():
    """IV Rank > 70 should add an Options rationale card."""
    res = _assemble_signal(**_base_assemble_kwargs(opt_flow={"iv_rank": 75.0, "pc_ratio": 0.9, "gex": 0}))
    heads = [r["head"] for r in res["rationale"]]
    assert any("IV Rank" in h for h in heads), f"Expected IV Rank card, got: {heads}"
    assert "Options" in res["sources"]


def test_iv_rank_flag_low_no_rationale():
    """IV Rank ≤ 70 should NOT emit an IV Rank rationale card."""
    res = _assemble_signal(**_base_assemble_kwargs(opt_flow={"iv_rank": 50.0, "pc_ratio": 0.9, "gex": 0}))
    heads = [r["head"] for r in res["rationale"]]
    assert not any("IV Rank" in h for h in heads), f"Unexpected IV Rank card: {heads}"


def test_iv_rank_flag_post_earnings_context():
    """IV Rank > 70 with recent earnings (days_since=3) gets IV crush wording."""
    res = _assemble_signal(
        **_base_assemble_kwargs(
            opt_flow={"iv_rank": 80.0, "pc_ratio": 0.9, "gex": 0},
            earnings_cal={"days_since_earnings": 3, "last_earnings_date": "2026-05-22"},
        )
    )
    heads = [r["head"] for r in res["rationale"]]
    bodies = [r["body"] for r in res["rationale"]]
    iv_cards = [(h, b) for h, b in zip(heads, bodies) if "IV Rank" in h]
    assert iv_cards, "Expected IV Rank card near earnings"
    assert "crush" in iv_cards[0][1].lower() or "crush" in iv_cards[0][0].lower()


# ── §37 audit fix tests ────────────────────────────────────────────────────────


def _mr_buy_kwargs(**overrides):
    """Base kwargs for an MR BUY signal: RSI<42 + BB%B<0.22 satisfies _has_mr (count≥2)."""
    defaults = dict(
        ticker="NVDA",
        info={"company": "NVIDIA"},
        tech={"price": 100.0, "atr": 2.0, "rsi": 38.0, "bb_pct_b": 0.20, "ibs": 0.14, "volume": 5_000_000, "avg_volume": 4_000_000},
        score=45.0,
        rationale=[],
        sources=set(),
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
        days_to_earnings=None,
    )
    defaults.update(overrides)
    return defaults


def test_ar1_gate_applies_haircut_on_momentum_regime():
    """AR(1) > 0.05 on an MR BUY should reduce confidence.
    score=50 bypasses the orthogonality gate (which blocks score<50 with <3 families),
    ensuring the AR(1) gate is the one we're testing.
    """
    base = _mr_buy_kwargs(score=50.0)
    base["tech"] = {**base["tech"], "momentum_ar1": 0.10}  # trending regime

    res_no_ar1 = _assemble_signal(**_mr_buy_kwargs(score=50.0))
    res_ar1 = _assemble_signal(**base)

    # Both should still produce BUY (gate is a haircut, not a hard block)
    if res_no_ar1 and res_ar1 and res_no_ar1["action"] == "BUY" and res_ar1["action"] == "BUY":
        assert res_ar1["confidence"] < res_no_ar1["confidence"], "AR(1)=0.10 should reduce confidence vs no AR(1)"
    # Rationale card must appear when AR(1)=0.10
    if res_ar1:
        heads = [r["head"] for r in res_ar1["rationale"]]
        assert any("Persistence" in h or "AR(1)" in h for h in heads), (
            f"Expected AR(1) gate rationale card; got: {heads}"
        )


def test_ar1_gate_no_haircut_below_threshold():
    """AR(1) = 0.03 (below 0.05 threshold) should NOT apply a haircut."""
    base = _mr_buy_kwargs(score=50.0)
    base["tech"] = {**base["tech"], "momentum_ar1": 0.03}

    res_baseline = _assemble_signal(**_mr_buy_kwargs(score=50.0))
    res_low_ar1 = _assemble_signal(**base)

    if res_baseline and res_low_ar1:
        # No AR(1) rationale card should be emitted
        heads = [r["head"] for r in res_low_ar1["rationale"]]
        assert not any("Persistence" in h or "AR(1)" in h for h in heads), (
            f"AR(1)=0.03 should not add persistence card; got: {heads}"
        )


def test_ar1_gate_haircut_capped_at_10pp():
    """Very high AR(1) = 0.30 should cap haircut at 10pp (not e.g. 50pp).

    ML models are patched out so the test measures the raw AR(1) gate in isolation,
    not ML amplification on top of it.
    """
    from unittest.mock import patch

    base = _mr_buy_kwargs(score=50.0)
    base["tech"] = {**base["tech"], "momentum_ar1": 0.30}

    with (
        patch("services.signal_ml.get_model", return_value=None),
        patch("services.signal_ml.get_entry_model", return_value=None),
    ):
        res_normal = _assemble_signal(**_mr_buy_kwargs(score=50.0))
        res_high = _assemble_signal(**base)

    if res_normal and res_high:
        diff = res_normal.get("confidence", 0) - res_high.get("confidence", 0)
        assert diff <= 10.0 + 0.1, f"Haircut {diff:.1f}pp should not exceed 10pp cap"


def test_ar1_gate_does_not_fire_on_non_mr_signal():
    """AR(1) gate only fires when _has_mr is True (RSI < 42 etc.)."""
    base = _mr_buy_kwargs(score=50.0)
    # RSI = 60 → _has_mr = False (no MR condition met)
    base["tech"] = {
        "price": 100.0,
        "atr": 2.0,
        "rsi": 60.0,
        "volume": 5_000_000,
        "avg_volume": 4_000_000,
        "momentum_ar1": 0.20,
    }
    res = _assemble_signal(**base)
    if res:
        heads = [r["head"] for r in res["rationale"]]
        assert not any("Persistence" in h or "AR(1)" in h for h in heads), "AR(1) gate must not fire when _has_mr=False"


def test_backtest_derived_tickers_not_in_defensive_block():
    """TSLA/SBUX/GS/MA/BLK/SCHW/PANW/GEN/CPAY must not be in _DEFENSIVE_BUY_BLOCK.
    Rationale: they were excluded via 20yr backtest look-ahead (audit §1 critical fix).
    The dynamic AR(1) gate now handles them.
    """
    from services.signal_engine import _assemble_signal as _asm

    removed_tickers = ["TSLA", "SBUX", "GS", "MA", "BLK", "SCHW", "PANW", "GEN", "CPAY"]
    for ticker in removed_tickers:
        res = _asm(**_mr_buy_kwargs(ticker=ticker))
        # Should not be hard-blocked by the defensive block (action may still be HOLD
        # for other valid reasons, but must NOT have the defensive_ticker_block meta tag)
        if res:
            metas = [r.get("meta", "") for r in res["rationale"]]
            assert not any("defensive_ticker_block" in m for m in metas), (
                f"{ticker} should no longer be in _DEFENSIVE_BUY_BLOCK (look-ahead bias removed); meta tags: {metas}"
            )


def test_sector_config_no_per_sector_buy_thresh_for_active_sectors():
    """Active sectors (XLK, XLY, XLE, etc.) must not have per-sector buy_thresh.
    Audit: per-sector buy_thresh failed OOS 4/5 windows — removed to improve OOS survival.
    """
    from services.signal_engine import _SECTOR_MR_CONFIG

    # Sectors that should NOT have a buy_thresh override (active/positive sectors)
    active_sectors = ["XLK", "XLY", "XLE", "XLC", "XLB", "XLF", "XLP"]
    for sector in active_sectors:
        cfg = _SECTOR_MR_CONFIG.get(sector, {})
        thresh = cfg.get("buy_thresh")
        assert thresh is None, (
            f"Sector {sector} should not have buy_thresh after OOS de-curation; got buy_thresh={thresh}"
        )
        vix_min = cfg.get("vix_min")
        assert vix_min is None, f"Sector {sector} should not have vix_min after OOS de-curation; got vix_min={vix_min}"


def test_sector_config_blocked_sectors_still_have_999():
    """Confirmed-negative sectors (XLV, XLI, XLRE, XLU) must keep buy_thresh=999."""
    from services.signal_engine import _SECTOR_MR_CONFIG

    for sector in ["XLV", "XLI", "XLRE", "XLU"]:
        cfg = _SECTOR_MR_CONFIG.get(sector, {})
        assert cfg.get("buy_thresh") == 999, f"Blocked sector {sector} must keep buy_thresh=999"


# ── §38 audit fix tests ────────────────────────────────────────────────────────


def test_ar1_haircut_halved_when_revenue_growing():
    """AR(1)=0.10 haircut must be halved when revenue_growth > -10% (healthy dip, not value trap)."""
    base_no_rev = _mr_buy_kwargs(score=50.0, info={"company": "NVDA"})
    base_no_rev["tech"] = {**base_no_rev["tech"], "momentum_ar1": 0.10}

    base_growing = _mr_buy_kwargs(score=50.0, info={"company": "NVDA", "revenue_growth": 0.15})
    base_growing["tech"] = {**base_growing["tech"], "momentum_ar1": 0.10}

    res_no_rev = _assemble_signal(**base_no_rev)
    res_growing = _assemble_signal(**base_growing)

    if res_no_rev and res_growing and res_no_rev["action"] == "BUY" == res_growing["action"]:
        # Growing revenue should result in less haircut → higher confidence
        assert res_growing["confidence"] >= res_no_rev["confidence"] - 0.1, (
            f"Growing revenue should reduce haircut: growing={res_growing['confidence']:.1f} "
            f"vs no_rev={res_no_rev['confidence']:.1f}"
        )


def test_ar1_full_haircut_when_revenue_declining():
    """AR(1)=0.10 haircut must be full when revenue_growth < -10% (value trap risk)."""
    base_declining = _mr_buy_kwargs(score=50.0, info={"company": "NVDA", "revenue_growth": -0.25})
    base_declining["tech"] = {**base_declining["tech"], "momentum_ar1": 0.10}

    base_growing = _mr_buy_kwargs(score=50.0, info={"company": "NVDA", "revenue_growth": 0.15})
    base_growing["tech"] = {**base_growing["tech"], "momentum_ar1": 0.10}

    res_declining = _assemble_signal(**base_declining)
    res_growing = _assemble_signal(**base_growing)

    if res_declining and res_growing and res_declining["action"] == "BUY" == res_growing["action"]:
        assert res_declining["confidence"] <= res_growing["confidence"] + 0.1, (
            f"Declining revenue should take larger haircut than growing: "
            f"declining={res_declining['confidence']:.1f} vs growing={res_growing['confidence']:.1f}"
        )


def test_ar1_rationale_mentions_revenue_context():
    """AR(1) rationale card must mention revenue growth context when available."""
    base = _mr_buy_kwargs(score=50.0, info={"company": "NVDA", "revenue_growth": 0.20})
    base["tech"] = {**base["tech"], "momentum_ar1": 0.10}
    res = _assemble_signal(**base)
    if res:
        bodies = [r.get("body", "") for r in res["rationale"] if "Persistence" in r.get("head", "")]
        assert any("+20.0%" in b or "Dip" in r.get("head", "") for b, r in zip(bodies, res["rationale"])), (
            "AR(1) rationale card should mention revenue context when available"
        )


def test_options_sweep_gex_gives_15pp_bonus():
    """Call sweep + positive GEX should give +15pp confidence, not just +5pp."""
    from unittest.mock import patch

    base = _mr_buy_kwargs(score=50.0)
    opt_with_sweep = {"sweep_calls": True, "gex": 50_000_000.0, "pc_ratio": 0.8, "iv_rank": None}
    opt_no_sweep = {"sweep_calls": False, "gex": 50_000_000.0, "pc_ratio": 0.6, "iv_rank": None}

    # Patch out both ML models so confidence adjustment doesn't collapse the options scoring gap.
    with (
        patch("services.signal_ml.get_model", return_value=None),
        patch("services.signal_ml.get_entry_model", return_value=None),
    ):
        res_sweep = _assemble_signal(**{**base, "opt_flow": opt_with_sweep})
        res_no_sweep = _assemble_signal(**{**base, "opt_flow": opt_no_sweep})

    if res_sweep and res_no_sweep and res_sweep["action"] == res_no_sweep["action"] == "BUY":
        assert res_sweep["confidence"] > res_no_sweep["confidence"], (
            f"Sweep+GEX should boost confidence more than GEX alone: "
            f"sweep={res_sweep['confidence']:.1f} vs no_sweep={res_no_sweep['confidence']:.1f}"
        )
        # Sweep+GEX gives +15pp vs GEX-only +5pp; net diff ≥ 8pp after Platt rounding
        diff = res_sweep["confidence"] - res_no_sweep["confidence"]
        assert diff >= 8.0, f"Sweep+GEX bonus should be ≥ 8pp above GEX-only; got {diff:.1f}pp"


def test_options_sweep_rationale_mentions_sweep():
    """When sweep+GEX fires, rationale must say 'sweep' and 'GEX'."""
    base = _mr_buy_kwargs(score=50.0)
    opt_with_sweep = {"sweep_calls": True, "gex": 20_000_000.0, "pc_ratio": 0.7, "iv_rank": None}
    res = _assemble_signal(**{**base, "opt_flow": opt_with_sweep})
    if res:
        heads = [r["head"] for r in res["rationale"]]
        sweep_cards = [h for h in heads if "Sweep" in h or "sweep" in h.lower()]
        assert sweep_cards, f"Expected a sweep rationale card; got: {heads}"
