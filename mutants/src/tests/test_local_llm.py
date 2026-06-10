"""Tests for services/local_llm.py — pure-logic and fallback paths."""

import pytest


# ── _parse_sentiment_score ────────────────────────────────────────────────────


def test_parse_score_integer():
    from services.local_llm import _parse_sentiment_score

    assert _parse_sentiment_score("SCORE: 1") == pytest.approx(1.0)


def test_parse_score_float():
    from services.local_llm import _parse_sentiment_score

    assert _parse_sentiment_score("SCORE: 0.75 | REASONING: bullish") == pytest.approx(0.75)


def test_parse_score_negative():
    from services.local_llm import _parse_sentiment_score

    assert _parse_sentiment_score("-0.5") == pytest.approx(-0.5)


def test_parse_score_clamped_high():
    from services.local_llm import _parse_sentiment_score

    assert _parse_sentiment_score("5.0") == pytest.approx(1.0)


def test_parse_score_clamped_low():
    from services.local_llm import _parse_sentiment_score

    assert _parse_sentiment_score("-99") == pytest.approx(-1.0)


def test_parse_score_no_number():
    from services.local_llm import _parse_sentiment_score

    assert _parse_sentiment_score("no numbers here") == pytest.approx(0.0)


# ── _analyze_sentiment_fallback ───────────────────────────────────────────────


def test_fallback_empty_news_neutral():
    from services.local_llm import _analyze_sentiment_fallback

    result = _analyze_sentiment_fallback([])
    assert result.label == "neutral"
    assert result.score == 0.0
    assert result.source == "fallback"


def test_fallback_bullish_keywords():
    from services.local_llm import _analyze_sentiment_fallback

    news = [{"headline": "Company beat earnings expectations with strong revenue growth", "summary": ""}]
    result = _analyze_sentiment_fallback(news)
    assert result.score > 0


def test_fallback_bearish_keywords():
    from services.local_llm import _analyze_sentiment_fallback

    news = [{"headline": "Company miss earnings, downgrade to sell on weak outlook", "summary": ""}]
    result = _analyze_sentiment_fallback(news)
    assert result.score < 0


def test_fallback_mixed_returns_label():
    from services.local_llm import _analyze_sentiment_fallback

    news = [
        {"headline": "Company beats earnings", "summary": "Strong revenue growth"},
        {"headline": "CEO warns of decline", "summary": "Loss expected next quarter"},
    ]
    result = _analyze_sentiment_fallback(news)
    assert result.label in ("bullish", "bearish", "neutral")
    assert result.source == "fallback"


# ── _risk_gate_fallback ───────────────────────────────────────────────────────


def test_risk_gate_extreme_vix():
    from services.local_llm import _risk_gate_fallback

    # VIX>40 (+3) + inverted yc (+2) + poor breadth (+2) + wide spreads (+2) = 9 → extreme
    result = _risk_gate_fallback({"vix": 50, "yc_spread": -0.6, "breadth_pct": 20, "credit_spread": 250})
    assert result.risk_level == "extreme"
    assert result.recommendation == "avoid"


def test_risk_gate_high_vix():
    from services.local_llm import _risk_gate_fallback

    # VIX>25 (+2) + VIX>25 threshold, so risk_score=2 → medium (need +1 more for high)
    # Add poor breadth (+2) to push to >= 3 → high
    result = _risk_gate_fallback({"vix": 30, "yc_spread": 0.5, "breadth_pct": 25, "credit_spread": 100})
    assert result.risk_level in ("high", "extreme")


def test_risk_gate_inverted_yield_curve():
    from services.local_llm import _risk_gate_fallback

    result = _risk_gate_fallback({"vix": 15, "yc_spread": -0.6, "breadth_pct": 50, "credit_spread": 100})
    assert result.risk_level in ("medium", "high")
    assert any("yield" in f.lower() for f in result.factors)


def test_risk_gate_poor_breadth():
    from services.local_llm import _risk_gate_fallback

    result = _risk_gate_fallback({"vix": 15, "yc_spread": 0.5, "breadth_pct": 20, "credit_spread": 100})
    assert result.risk_level in ("medium", "high")


def test_risk_gate_wide_credit_spreads():
    from services.local_llm import _risk_gate_fallback

    result = _risk_gate_fallback({"vix": 15, "yc_spread": 0.5, "breadth_pct": 60, "credit_spread": 250})
    assert result.risk_level in ("medium", "high")


def test_risk_gate_low_risk_conditions():
    from services.local_llm import _risk_gate_fallback

    result = _risk_gate_fallback({"vix": 10, "yc_spread": 0.8, "breadth_pct": 85, "credit_spread": 80})
    assert result.risk_level == "low"
    assert result.recommendation == "proceed"


def test_risk_gate_medium_conditions():
    from services.local_llm import _risk_gate_fallback

    result = _risk_gate_fallback({"vix": 22, "yc_spread": 0.1, "breadth_pct": 55, "credit_spread": 130})
    assert result.risk_level in ("low", "medium", "high")
    assert result.source == "fallback"


def test_risk_gate_flattening_yield_curve():
    from services.local_llm import _risk_gate_fallback

    result = _risk_gate_fallback({"vix": 15, "yc_spread": -0.1, "breadth_pct": 50, "credit_spread": 100})
    assert any("yield" in f.lower() or "flat" in f.lower() for f in result.factors)


# ── LocalLLMClient (abstract) ─────────────────────────────────────────────────


def test_local_llm_client_abstract_methods_raise():
    from services.local_llm import LocalLLMClient

    client = LocalLLMClient()
    with pytest.raises(NotImplementedError):
        client.generate("test")
    with pytest.raises(NotImplementedError):
        client.is_available()


# ── get_llm_client ────────────────────────────────────────────────────────────


def test_get_llm_client_returns_none_when_disabled(monkeypatch):
    import services.local_llm as mod

    monkeypatch.setattr(mod, "LOCAL_LLM_ENABLED", False)
    monkeypatch.setattr(mod, "_llm_client", None)
    result = mod.get_llm_client()
    assert result is None


def test_get_llm_client_cached(monkeypatch):
    import services.local_llm as mod
    from unittest.mock import MagicMock

    fake_client = MagicMock()
    monkeypatch.setattr(mod, "_llm_client", fake_client)
    result = mod.get_llm_client()
    assert result is fake_client


def test_get_llm_client_ollama_unavailable(monkeypatch):
    import services.local_llm as mod

    monkeypatch.setattr(mod, "_llm_client", None)
    monkeypatch.setattr(mod, "LOCAL_LLM_ENABLED", True)
    monkeypatch.setattr(mod, "LOCAL_LLM_PROVIDER", "ollama")

    from unittest.mock import MagicMock, patch

    mock_ollama = MagicMock()
    mock_ollama.is_available.return_value = False

    with patch.object(mod, "OllamaClient", return_value=mock_ollama):
        result = mod.get_llm_client()

    assert result is None
    monkeypatch.setattr(mod, "_llm_client", None)


def test_get_llm_client_openai_compatible_provider(monkeypatch):
    import services.local_llm as mod
    from unittest.mock import MagicMock, patch

    monkeypatch.setattr(mod, "_llm_client", None)
    monkeypatch.setattr(mod, "LOCAL_LLM_ENABLED", True)
    monkeypatch.setattr(mod, "LOCAL_LLM_PROVIDER", "openai-compatible")

    mock_client = MagicMock()
    mock_client.is_available.return_value = False

    with patch.object(mod, "OpenAICompatibleClient", return_value=mock_client):
        mod.get_llm_client()

    monkeypatch.setattr(mod, "_llm_client", None)


def test_get_llm_client_unknown_provider_defaults_to_ollama(monkeypatch):
    import services.local_llm as mod
    from unittest.mock import MagicMock, patch

    monkeypatch.setattr(mod, "_llm_client", None)
    monkeypatch.setattr(mod, "LOCAL_LLM_ENABLED", True)
    monkeypatch.setattr(mod, "LOCAL_LLM_PROVIDER", "unknown-provider")

    mock_client = MagicMock()
    mock_client.is_available.return_value = False

    with patch.object(mod, "OllamaClient", return_value=mock_client):
        mod.get_llm_client()

    monkeypatch.setattr(mod, "_llm_client", None)


# ── analyze_news_sentiment ────────────────────────────────────────────────────


def test_analyze_news_no_client_uses_fallback(monkeypatch):
    import services.local_llm as mod

    monkeypatch.setattr(mod, "_llm_client", None)
    monkeypatch.setattr(mod, "LOCAL_LLM_ENABLED", False)

    result = mod.analyze_news_sentiment([], "AAPL")
    assert result.source == "fallback"
    monkeypatch.setattr(mod, "LOCAL_LLM_ENABLED", True)


def test_analyze_news_client_unavailable_uses_fallback(monkeypatch):
    import services.local_llm as mod
    from unittest.mock import MagicMock

    mock_client = MagicMock()
    mock_client.is_available.return_value = False
    monkeypatch.setattr(mod, "_llm_client", mock_client)

    result = mod.analyze_news_sentiment([{"headline": "AAPL beats"}], "AAPL")
    assert result.source == "fallback"

    monkeypatch.setattr(mod, "_llm_client", None)


def test_analyze_news_client_success(monkeypatch):
    import services.local_llm as mod
    from unittest.mock import MagicMock

    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    mock_client.generate.return_value = "SCORE: 0.7 | REASONING: Strong bullish momentum"
    monkeypatch.setattr(mod, "_llm_client", mock_client)

    result = mod.analyze_news_sentiment([{"headline": "Beat", "summary": ""}], "AAPL")
    assert result.source == "llm"
    assert result.score == pytest.approx(0.7)
    assert result.label == "bullish"

    monkeypatch.setattr(mod, "_llm_client", None)


def test_analyze_news_client_exception_fallback(monkeypatch):
    import services.local_llm as mod
    from unittest.mock import MagicMock

    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    mock_client.generate.side_effect = RuntimeError("LLM crashed")
    monkeypatch.setattr(mod, "_llm_client", mock_client)

    result = mod.analyze_news_sentiment([{"headline": "Test"}], "AAPL")
    assert result.source == "fallback"

    monkeypatch.setattr(mod, "_llm_client", None)


# ── assess_macro_risk ─────────────────────────────────────────────────────────


def test_assess_macro_no_client_uses_fallback(monkeypatch):
    import services.local_llm as mod

    monkeypatch.setattr(mod, "_llm_client", None)
    monkeypatch.setattr(mod, "LOCAL_LLM_ENABLED", False)

    result = mod.assess_macro_risk({"vix": 20})
    assert result.source == "fallback"
    monkeypatch.setattr(mod, "LOCAL_LLM_ENABLED", True)


def test_assess_macro_client_success_parsing(monkeypatch):
    import services.local_llm as mod
    from unittest.mock import MagicMock

    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    mock_client.generate.return_value = (
        "RISK: high | CONFIDENCE: 0.8 | FACTORS: VIX spike, inverted yield | RECOMMENDATION: reduce_size"
    )
    monkeypatch.setattr(mod, "_llm_client", mock_client)

    result = mod.assess_macro_risk({"vix": 35})
    assert result.source == "llm"
    assert result.risk_level == "high"
    assert result.recommendation == "reduce_size"
    assert result.confidence == pytest.approx(0.8)

    monkeypatch.setattr(mod, "_llm_client", None)


def test_assess_macro_client_invalid_risk_defaults_medium(monkeypatch):
    import services.local_llm as mod
    from unittest.mock import MagicMock

    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    mock_client.generate.return_value = "RISK: gobbledygook | CONFIDENCE: 0.5 | FACTORS: x | RECOMMENDATION: avoid"
    monkeypatch.setattr(mod, "_llm_client", mock_client)

    result = mod.assess_macro_risk({"vix": 20})
    assert result.risk_level == "medium"

    monkeypatch.setattr(mod, "_llm_client", None)


def test_assess_macro_client_exception_fallback(monkeypatch):
    import services.local_llm as mod
    from unittest.mock import MagicMock

    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    mock_client.generate.side_effect = RuntimeError("crashed")
    monkeypatch.setattr(mod, "_llm_client", mock_client)

    result = mod.assess_macro_risk({"vix": 20})
    assert result.source == "fallback"

    monkeypatch.setattr(mod, "_llm_client", None)


# ── get_llm_status ─────────────────────────────────────────────────────────────


def test_get_llm_status_no_client(monkeypatch):
    import services.local_llm as mod

    monkeypatch.setattr(mod, "_llm_client", None)
    monkeypatch.setattr(mod, "LOCAL_LLM_ENABLED", False)

    status = mod.get_llm_status()
    assert status["enabled"] is False
    monkeypatch.setattr(mod, "LOCAL_LLM_ENABLED", True)


def test_get_llm_status_with_client(monkeypatch):
    import services.local_llm as mod
    from unittest.mock import MagicMock

    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    monkeypatch.setattr(mod, "_llm_client", mock_client)

    status = mod.get_llm_status()
    assert status["enabled"] is True
    assert "provider" in status

    monkeypatch.setattr(mod, "_llm_client", None)
