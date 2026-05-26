import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from services.signal_engine import (
    _score_to_action,
    _levels,
    _make_plain_english,
    _collect_fetch_results,
    _current_session,
    _assemble_signal,
    scan_all,
    generate_signal
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
    # High volatility swing (atr_pct=3%>2.5%): 2.0s/2.5t (widened §31)
    entry, stop, tgt, rr = _levels(100.0, 3.0, "BUY")
    assert entry == 100.0
    assert stop == 94.0    # 100 - 2.0*3
    assert tgt == 107.5    # 100 + 2.5*3

    # Low volatility swing (atr_pct=0.5%<1.0%): 2.5s/3.0t (SELL)
    entry, stop, tgt, rr = _levels(100.0, 0.5, "SELL")
    assert entry == 100.0
    assert stop == 101.25  # 100 + 2.5*0.5
    assert tgt == 98.5     # 100 - 3.0*0.5

    # HOLD action
    entry, stop, tgt, rr = _levels(100.0, 2.0, "HOLD")
    assert entry is None

def test_make_plain_english():
    rationale = [
        {"head": "RSI Oversold", "sentiment": "pos"},
        {"head": "MACD Crossover", "sentiment": "pos"}
    ]
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
    assert warnings == [{
        "source": "news",
        "error": "RuntimeError",
        "message": "rate limited",
    }]

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
    res = _assemble_signal(
        ticker="TSLA",
        info={"company": "Tesla"},
        tech={"price": 100.0, "atr": 1.0, "rsi": 38.0}, # rsi<42 satisfies MR gate; target 100+3*1=103
        score=50.0, # BUY
        rationale=[],
        sources=set(),
        _force_hold=False,
        _is_low_atr=False,
        _atr_pct_pre=0.01,
        total_confidence_penalty=0.0,
        avg_sent=0.0,
        price=100.0,
        atr=1.0,
        market_ctx={"macro": {"t10y": 4.5, "sp500_trend": "up"}}, # 4.5% risk free rate
        earnings_cal={},
        sector_rs={"sector_etf": "XLY", "rs_vs_sector": 0},
        days_to_earnings=None,
    )
    
    assert "Macro" in res["sources"]
    assert any("Risk-Adjusted Return Negative" in r["head"] or "Thin Risk Premium" in r["head"] for r in res["rationale"])

def test_assemble_signal_chronic_loser():
    res = _assemble_signal(
        ticker="BAD",
        info={}, tech={"price": 10.0, "atr": 1.0},
        score=50.0, rationale=[], sources=set(),
        _force_hold=False, _is_low_atr=False, _atr_pct_pre=0.1,
        total_confidence_penalty=0.0, avg_sent=0.0, price=10.0, atr=1.0,
        market_ctx={"adaptive_weights": {"ticker_win_rates": {"BAD": 0.40}}}, # Win rate < 45%
        earnings_cal={}, sector_rs=None, days_to_earnings=None
    )
    
    assert res["action"] == "HOLD"
    assert any("Chronic Loser Exclusion" in r["head"] for r in res["rationale"])

def test_assemble_signal_sector_concentration():
    res = _assemble_signal(
        ticker="AAPL", info={}, tech={"price": 150.0, "atr": 5.0},
        score=60.0, rationale=[], sources=set(),
        _force_hold=False, _is_low_atr=False, _atr_pct_pre=0.03,
        total_confidence_penalty=0.0, avg_sent=0.0, price=150.0, atr=5.0,
        market_ctx={"portfolio_ctx": {"sector_exposure": {"XLK": 55.0}}}, # > 50% limit
        earnings_cal={}, sector_rs={"sector_etf": "XLK", "rs_vs_sector": 0}, days_to_earnings=None
    )
    
    assert res["action"] in ["BUY", "HOLD"]

def test_assemble_signal_low_vol():
    res = _assemble_signal(
        ticker="KO", info={}, tech={"price": 100.0, "atr": 0.5}, # atr_pct = 0.005 < 0.008
        score=30.0, rationale=[], sources=set(),
        _force_hold=False, _is_low_atr=False, _atr_pct_pre=0.005,
        total_confidence_penalty=0.0, avg_sent=0.0, price=100.0, atr=0.5,
        market_ctx={"macro": {"macro_score": 0}},
        earnings_cal={}, sector_rs=None, days_to_earnings=None
    )
    
    assert res["action"] in ["BUY", "HOLD"]

@pytest.mark.asyncio
async def test_generate_signal_basic():
    import pandas as pd
    mock_df = pd.DataFrame({"Close": [100]*30})
    mock_df_1h = pd.DataFrame({"Close": [100]*20})

    with patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news, \
         patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews, \
         patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider, \
         patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs, \
         patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal, \
         patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp, \
         patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow, \
         patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund, \
         patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc, \
         patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends, \
         patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong, \
         patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist, \
         patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info, \
         patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec, \
         patch("services.signal_engine.calculate_indicators") as m_calc:

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
            "price": 100.0, "atr": 2.0, "rsi": 25.0, "macd_hist": 0.5, "macd_hist_prev": -0.1,
            "sma200": 90.0, "sma50": 95.0, "volume": 2000000, "avg_volume": 1000000,
            "stoch_k": 15, "stoch_d": 10, "stoch_k_prev": 5, "stoch_d_prev": 12,
            "cci": -160, "mfi": 15, "bb_squeeze": True, "bb_pct_b": 0.8,
            "ema8": 100.0, "ema21": 95.0, "ema8_prev": 94.0, "ema21_prev": 96.0,
            "close_streak": 8, "gap_pct": 3.0, "rvol": 2.5
        }

        res = await generate_signal("AAPL")
        assert res is not None
        assert res["ticker"] == "AAPL"
        assert res["action"] == "BUY"

@pytest.mark.asyncio
async def test_generate_signal_sell_branches():
    import pandas as pd
    mock_df = pd.DataFrame({"Close": [100]*30})
    mock_df_1h = pd.DataFrame({"Close": [100]*20})

    with patch("services.signal_engine.get_company_news", new_callable=AsyncMock) as m_news, \
         patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock) as m_snews, \
         patch("services.signal_engine.get_insider_activity", new_callable=AsyncMock) as m_insider, \
         patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock) as m_arecs, \
         patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock) as m_ecal, \
         patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock) as m_esurp, \
         patch("services.signal_engine.get_options_flow", new_callable=AsyncMock) as m_oflow, \
         patch("services.signal_engine.get_fundamentals", new_callable=AsyncMock) as m_fund, \
         patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock) as m_soc, \
         patch("services.signal_engine.get_google_trends", new_callable=AsyncMock) as m_trends, \
         patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock) as m_cong, \
         patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist, \
         patch("services.signal_engine.get_info", new_callable=AsyncMock) as m_info, \
         patch("services.signal_engine.get_sector_relative_strength", new_callable=AsyncMock) as m_sec, \
         patch("services.signal_engine.calculate_indicators") as m_calc:

        # Inject negative meta data to force SELL branches
        m_news.return_value = [{"headline": "Bad news", "sentiment": -0.8, "hours_ago": 1, "source": "Finviz"}]
        m_snews.return_value = []
        m_insider.return_value = {"filings": 5, "score": -10, "net_shares": -50000, "sell_value": 1000000, "buy_value": 0, "buys": 0, "sells": 5}
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
            "price": 100.0, "atr": 2.0, "rsi": 85.0, "macd_hist": -0.5, "macd_hist_prev": 0.1,
            "sma200": 110.0, "sma50": 105.0, "volume": 2000000, "avg_volume": 1000000,
            "cci": 160, "mfi": 85,
            "close_streak": -8, "gap_pct": -3.0, "rvol": 2.5
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
    res = _assemble_signal(
        **_base_assemble_kwargs(opt_flow={"iv_rank": 75.0, "pc_ratio": 0.9, "gex": 0})
    )
    heads = [r["head"] for r in res["rationale"]]
    assert any("IV Rank" in h for h in heads), f"Expected IV Rank card, got: {heads}"
    assert "Options" in res["sources"]


def test_iv_rank_flag_low_no_rationale():
    """IV Rank ≤ 70 should NOT emit an IV Rank rationale card."""
    res = _assemble_signal(
        **_base_assemble_kwargs(opt_flow={"iv_rank": 50.0, "pc_ratio": 0.9, "gex": 0})
    )
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
