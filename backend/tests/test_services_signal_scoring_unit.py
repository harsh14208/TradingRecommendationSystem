"""Unit tests for services/signal_scoring.py — family scorer functions."""


def _make_tech(**kwargs):
    defaults = {
        "rsi": 50.0,
        "stoch_k": 50.0,
        "stoch_d": 50.0,
        "cci": 0.0,
        "williams_r": -50.0,
        "macd": 0.0,
        "macd_signal": 0.0,
        "macd_hist": 0.0,
        "ema_cross": 0.0,
        "price": 100.0,
        "atr": 2.0,
        "atr_pct": 2.0,
        "sma_20": 99.0,
        "sma_50": 98.0,
        "sma_200": 95.0,
        "obv": 100000.0,
        "adx": 20.0,
        "plus_di": 25.0,
        "minus_di": 20.0,
        "volume": 1000000.0,
        "volume_ratio": 1.0,
        "bb_pct_b": 0.5,
        "ibs": 0.5,
        "vwap_pct": 0.0,
    }
    defaults.update(kwargs)
    return defaults


# ── score_oscillators ────────────────────────────────────────────────────────


def test_score_oscillators_neutral():
    from services.signal_scoring import score_oscillators

    score, rationale, hint = score_oscillators(_make_tech(), rsi=50.0)
    assert isinstance(score, float)
    assert isinstance(rationale, list)


def test_score_oscillators_rsi_oversold():
    from services.signal_scoring import score_oscillators

    score, rationale, hint = score_oscillators(_make_tech(rsi=25.0), rsi=25.0)
    assert score >= 20
    assert any("Oversold" in r["head"] for r in rationale)
    assert hint == "rsi"


def test_score_oscillators_rsi_weakening():
    from services.signal_scoring import score_oscillators

    score, rationale, _ = score_oscillators(_make_tech(rsi=35.0), rsi=35.0)
    assert score >= 10


def test_score_oscillators_rsi_overbought():
    from services.signal_scoring import score_oscillators

    score, rationale, hint = score_oscillators(_make_tech(rsi=75.0), rsi=75.0)
    assert score <= -20
    assert hint == "rsi"


def test_score_oscillators_rsi_elevated():
    from services.signal_scoring import score_oscillators

    score, _, _ = score_oscillators(_make_tech(rsi=65.0), rsi=65.0)
    assert score <= -10


def test_score_oscillators_rsi_none():
    from services.signal_scoring import score_oscillators

    score, rationale, hint = score_oscillators(_make_tech(), rsi=None)
    assert isinstance(score, float)


def test_score_oscillators_stoch_oversold():
    from services.signal_scoring import score_oscillators

    tech = _make_tech(stoch_k=15.0, stoch_d=18.0)
    score, rationale, _ = score_oscillators(tech, rsi=50.0)
    assert score > 0  # stoch_k < 20 → positive signal


def test_score_oscillators_returns_tuple():
    from services.signal_scoring import score_oscillators

    result = score_oscillators(_make_tech(), rsi=50.0)
    assert len(result) == 3


# ── score_macd ───────────────────────────────────────────────────────────────


def test_score_macd_bullish_crossover():
    from services.signal_scoring import score_macd

    # hist crosses from negative to positive
    score, trend, rationale, hint = score_macd(hist=0.1, hist_p=-0.05)
    assert score >= 22
    assert hint == "macd"


def test_score_macd_bearish_crossover():
    from services.signal_scoring import score_macd

    score, trend, rationale, hint = score_macd(hist=-0.1, hist_p=0.05)
    assert score <= -22
    assert hint == "macd"


def test_score_macd_continuation_bullish():
    from services.signal_scoring import score_macd

    score, trend, rationale, hint = score_macd(hist=0.5, hist_p=0.3)
    assert isinstance(score, float)
    # No crossover, just continuation
    assert hint != "macd" or score > 0


def test_score_macd_neutral():
    from services.signal_scoring import score_macd

    score, trend, rationale, hint = score_macd(hist=0.0, hist_p=0.0)
    assert isinstance(score, float)


# ── score_ema_cross ───────────────────────────────────────────────────────────


def test_score_ema_cross_bullish_cross():
    from services.signal_scoring import score_ema_cross

    tech = _make_tech()
    tech["ema8"] = 105.0
    tech["ema21"] = 103.0
    tech["ema8_prev"] = 102.0  # was below → bullish cross
    tech["ema21_prev"] = 103.0
    score, trend, rationale = score_ema_cross(tech)
    assert score == 12.0
    assert any("Bullish" in r["head"] for r in rationale)


def test_score_ema_cross_bearish_cross():
    from services.signal_scoring import score_ema_cross

    tech = _make_tech()
    tech["ema8"] = 99.0
    tech["ema21"] = 103.0
    tech["ema8_prev"] = 104.0  # was above → bearish cross
    tech["ema21_prev"] = 103.0
    score, trend, rationale = score_ema_cross(tech)
    assert score == -12.0


def test_score_ema_cross_empty():
    from services.signal_scoring import score_ema_cross

    score, trend, rationale = score_ema_cross({})
    assert score == 0.0


# ── score_obv_adx ────────────────────────────────────────────────────────────


def test_score_obv_adx_strong_trend():
    from services.signal_scoring import score_obv_adx

    tech = _make_tech(adx=35.0, plus_di=30.0, minus_di=15.0, obv_above=True, obv_slope=0.5)
    vol_delta, trend_delta, rationale = score_obv_adx(tech, running_score=10.0)
    assert isinstance(vol_delta, float)
    assert isinstance(trend_delta, float)


def test_score_obv_adx_weak():
    from services.signal_scoring import score_obv_adx

    tech = _make_tech(adx=15.0, plus_di=20.0, minus_di=20.0)
    vol_delta, trend_delta, rationale = score_obv_adx(tech, running_score=0.0)
    assert isinstance(vol_delta, float)


def test_score_obv_adx_empty():
    from services.signal_scoring import score_obv_adx

    vol_delta, trend_delta, rationale = score_obv_adx({}, running_score=0.0)
    assert vol_delta == 0.0
    assert trend_delta == 0.0


# ── score_moving_averages ────────────────────────────────────────────────────


def test_score_moving_averages_price_above_sma200():
    from services.signal_scoring import score_moving_averages

    score, rationale = score_moving_averages(price=110.0, sma50=105.0, sma200=90.0, poly_ind={})
    assert score > 0
    assert any("200" in r["head"] for r in rationale)


def test_score_moving_averages_price_below_sma200():
    from services.signal_scoring import score_moving_averages

    score, rationale = score_moving_averages(price=85.0, sma50=95.0, sma200=110.0, poly_ind={})
    assert score < 0


def test_score_moving_averages_none_smas():
    from services.signal_scoring import score_moving_averages

    score, rationale = score_moving_averages(price=100.0, sma50=None, sma200=None, poly_ind={})
    assert score == 0.0


def test_score_moving_averages_returns_tuple():
    from services.signal_scoring import score_moving_averages

    result = score_moving_averages(price=100.0, sma50=99.0, sma200=95.0, poly_ind={})
    assert len(result) == 2
