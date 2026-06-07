"""
Local LLM Inference for Sentiment Analysis and Macro Risk-Gating.

This module provides a local LLM abstraction for offloading sentiment analysis
and macro risk-gating to a local model (e.g., Llama 3.1, Mistral, Phi-3).
This keeps trading logic private and avoids API costs for processing news feeds.

Supports Ollama, LM Studio, or any OpenAI-compatible local server.
"""

import logging
import re
import time
from dataclasses import dataclass
from typing import Optional
from services.http_client import get_ssl_context

logger = logging.getLogger(__name__)

# Configuration
LOCAL_LLM_ENABLED = True  # Set to False to disable local LLM
LOCAL_LLM_PROVIDER = "ollama"  # Options: "ollama", "lm-studio", "openai-compatible"
LOCAL_LLM_MODEL = "llama3.1:8b"  # Default model for Ollama
LOCAL_LLM_URL = "http://localhost:11434"  # Ollama default
LOCAL_LLM_API_KEY = None  # For OpenAI-compatible servers

# Fallback to rule-based analysis if LLM unavailable
_fallback_mode = False


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""

    score: float  # -1.0 (very bearish) to +1.0 (very bullish)
    confidence: float  # 0.0 to 1.0
    label: str  # "bullish", "bearish", "neutral"
    reasoning: str  # Brief explanation
    source: str  # "llm" or "fallback"


@dataclass
class RiskGateResult:
    """Result of macro risk gating analysis."""

    risk_level: str  # "low", "medium", "high", "extreme"
    confidence: float  # 0.0 to 1.0
    factors: list[str]  # Key risk factors identified
    recommendation: str  # "proceed", "caution", "reduce_size", "avoid"
    source: str  # "llm" or "fallback"


def _parse_sentiment_score(text: str) -> float:
    """Parse a sentiment score from LLM response text."""
    # Look for a number between -1 and 1
    match = re.search(r"[-+]?\d*\.\d+|[-+]?\d+", text)
    if match:
        score = float(match.group())
        return max(-1.0, min(1.0, score))
    return 0.0


def _analyze_sentiment_fallback(news_items: list[dict]) -> SentimentResult:
    """Fallback rule-based sentiment analysis when LLM is unavailable."""
    if not news_items:
        return SentimentResult(
            score=0.0,
            confidence=0.3,
            label="neutral",
            reasoning="No news items to analyze",
            source="fallback",
        )

    # Simple keyword-based sentiment
    bullish_keywords = [
        "beat",
        "upgrade",
        "buy",
        "growth",
        "profit",
        "revenue",
        "positive",
        "exceed",
        "outperform",
        "bullish",
        "rally",
        "surge",
        "gain",
        "rise",
        "strong",
        "record",
        "breakthrough",
        "approval",
        "partnership",
    ]
    bearish_keywords = [
        "miss",
        "downgrade",
        "sell",
        "loss",
        "decline",
        "negative",
        "underperform",
        "bearish",
        "drop",
        "plunge",
        "fall",
        "weak",
        "lawsuit",
        "investigation",
        "recall",
        "warning",
        "delay",
    ]

    total_score = 0.0
    total_confidence = 0.0

    for item in news_items:
        headline = (item.get("headline") or "").lower()
        summary = (item.get("summary") or "").lower()
        text = f"{headline} {summary}"

        bull_count = sum(1 for kw in bullish_keywords if kw in text)
        bear_count = sum(1 for kw in bearish_keywords if kw in text)
        total_words = len(text.split())

        if total_words > 0:
            item_score = (bull_count - bear_count) / max(1, total_words) * 10
            item_confidence = min(0.8, (bull_count + bear_count) / max(1, total_words) * 5)
            total_score += item_score
            total_confidence += item_confidence

    avg_score = total_score / len(news_items) if news_items else 0
    avg_confidence = total_confidence / len(news_items) if news_items else 0

    score = max(-1.0, min(1.0, avg_score))
    label = "bullish" if score > 0.2 else "bearish" if score < -0.2 else "neutral"

    return SentimentResult(
        score=score,
        confidence=avg_confidence,
        label=label,
        reasoning=f"Keyword analysis: {len(news_items)} news items processed",
        source="fallback",
    )


def _risk_gate_fallback(macro_data: dict) -> RiskGateResult:
    """Fallback rule-based risk gating when LLM is unavailable."""
    vix = macro_data.get("vix", 20)
    yc_spread = macro_data.get("yc_spread", 0.5)
    breadth = macro_data.get("breadth_pct", 50)
    credit_spread = macro_data.get("credit_spread", 100)

    risk_score = 0
    factors = []

    # VIX assessment
    if vix > 40:
        risk_score += 3
        factors.append(f"Extreme volatility (VIX={vix:.0f})")
    elif vix > 25:
        risk_score += 2
        factors.append(f"High volatility (VIX={vix:.0f})")
    elif vix < 12:
        risk_score -= 1
        factors.append("Low volatility environment")

    # Yield curve
    if yc_spread < -0.5:
        risk_score += 2
        factors.append("Inverted yield curve (recession signal)")
    elif yc_spread < 0:
        risk_score += 1
        factors.append("Flattening yield curve")

    # Market breadth
    if breadth < 30:
        risk_score += 2
        factors.append(f"Poor market breadth ({breadth}% above 200DMA)")
    elif breadth > 80:
        risk_score -= 1
        factors.append("Strong market participation")

    # Credit spreads
    if credit_spread > 200:
        risk_score += 2
        factors.append("Wide credit spreads (stress signal)")
    elif credit_spread < 100:
        risk_score -= 1
        factors.append("Tight credit spreads (healthy)")

    # Determine risk level
    if risk_score >= 5:
        risk_level = "extreme"
        recommendation = "avoid"
    elif risk_score >= 3:
        risk_level = "high"
        recommendation = "reduce_size"
    elif risk_score >= 1:
        risk_level = "medium"
        recommendation = "caution"
    else:
        risk_level = "low"
        recommendation = "proceed"

    confidence = min(0.9, 0.5 + abs(risk_score) * 0.05)

    return RiskGateResult(
        risk_level=risk_level,
        confidence=confidence,
        factors=factors,
        recommendation=recommendation,
        source="fallback",
    )


class LocalLLMClient:
    """Abstract local LLM client interface."""

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text from a prompt."""
        raise NotImplementedError

    def is_available(self) -> bool:
        """Check if the LLM is available."""
        raise NotImplementedError


async def _aio_post(url: str, payload: dict, headers: dict = None, timeout: int = 30) -> dict:
    """Non-blocking POST via aiohttp. Replaces urllib.request.urlopen."""

    import aiohttp

    _ssl = get_ssl_context()
    hdrs = {"Content-Type": "application/json", **(headers or {})}
    async with aiohttp.ClientSession() as sess:
        async with sess.post(
            url, json=payload, headers=hdrs, ssl=_ssl, timeout=aiohttp.ClientTimeout(total=timeout)
        ) as r:
            return await r.json(content_type=None)


async def _aio_get(url: str, headers: dict = None, timeout: int = 5) -> int:
    """Non-blocking GET status check via aiohttp."""

    import aiohttp

    _ssl = get_ssl_context()
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(
                url, headers=headers or {}, ssl=_ssl, timeout=aiohttp.ClientTimeout(total=timeout)
            ) as r:
                return r.status
    except Exception:
        return 0


class OllamaClient(LocalLLMClient):
    """Ollama local LLM client — fully async (no blocking urllib)."""

    def __init__(self, model: str = LOCAL_LLM_MODEL, url: str = LOCAL_LLM_URL):
        self.model = model
        self.url = url.rstrip("/")
        self._available: Optional[bool] = None
        self._last_check = 0.0

    def is_available(self) -> bool:
        now = time.time()
        if self._available is not None and (now - self._last_check) < 60:
            return self._available
        # Non-blocking socket probe — avoids blocking urllib.request.urlopen
        # in the asyncio event loop thread. Socket connect with 2s timeout
        # only touches the TCP layer; no HTTP round-trip needed for availability.
        try:
            import socket as _socket

            parsed = self.url.replace("http://", "").replace("https://", "").split("/")[0]
            host, _, port_str = parsed.partition(":")
            port = int(port_str) if port_str else (443 if "https" in self.url else 80)
            s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex((host, port))
            s.close()
            self._available = result == 0
        except Exception:
            self._available = False
        self._last_check = now
        return self._available

    async def agenerate(self, prompt: str, system_prompt: str = "") -> str:
        """Async generate — does not block the FastAPI event loop."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {"temperature": 0.1, "top_p": 0.9},
        }
        result = await _aio_post(f"{self.url}/api/generate", payload, timeout=30)
        return result.get("response", "")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Sync wrapper — only for legacy callers outside asyncio context."""
        import asyncio as _aio

        try:
            loop = _aio.get_running_loop()
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                return ex.submit(_aio.run, self.agenerate(prompt, system_prompt)).result()
        except RuntimeError:
            return _aio.run(self.agenerate(prompt, system_prompt))


class OpenAICompatibleClient(LocalLLMClient):
    """OpenAI-compatible local LLM client (LM Studio, etc.) — fully async."""

    def __init__(self, model: str = LOCAL_LLM_MODEL, url: str = "http://localhost:1234/v1", api_key: str = None):
        self.model = model
        self.url = url.rstrip("/")
        self.api_key = api_key or "not-needed"
        self._available: Optional[bool] = None
        self._last_check = 0.0

    def is_available(self) -> bool:
        now = time.time()
        if self._available is not None and (now - self._last_check) < 60:
            return self._available
        # Same non-blocking TCP socket probe as OllamaClient — avoids blocking
        # urllib.request in the event loop thread.
        try:
            import socket as _socket

            parsed = self.url.replace("http://", "").replace("https://", "").split("/")[0]
            host, _, port_str = parsed.partition(":")
            port = int(port_str) if port_str else (443 if "https" in self.url else 1234)
            s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex((host, port))
            s.close()
            self._available = result == 0
        except Exception:
            self._available = False
        self._last_check = now
        return self._available

    async def agenerate(self, prompt: str, system_prompt: str = "") -> str:
        """Async generate — does not block the FastAPI event loop."""
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 256,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        result = await _aio_post(f"{self.url}/chat/completions", payload, headers=headers, timeout=30)
        return result["choices"][0]["message"]["content"]

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        import asyncio as _aio

        try:
            _aio.get_running_loop()
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                return ex.submit(_aio.run, self.agenerate(prompt, system_prompt)).result()
        except RuntimeError:
            return _aio.run(self.agenerate(prompt, system_prompt))


# Global client instance
_llm_client: Optional[LocalLLMClient] = None


def get_llm_client() -> Optional[LocalLLMClient]:
    """Get or create the LLM client."""
    global _llm_client
    if _llm_client is not None:
        return _llm_client

    if not LOCAL_LLM_ENABLED:
        logger.info("Local LLM disabled by configuration")
        return None

    if LOCAL_LLM_PROVIDER == "ollama":
        client = OllamaClient()
    elif LOCAL_LLM_PROVIDER == "openai-compatible":
        client = OpenAICompatibleClient()
    else:
        client = OllamaClient()  # Default

    if client.is_available():
        _llm_client = client
        logger.info(f"Local LLM connected: {LOCAL_LLM_PROVIDER}/{LOCAL_LLM_MODEL}")
    else:
        logger.warning(f"Local LLM not available at {LOCAL_LLM_URL}, using fallback analysis")
        _llm_client = None

    return _llm_client


def analyze_news_sentiment(news_items: list[dict], ticker: str = "") -> SentimentResult:
    """
    Analyze sentiment of news items using local LLM or fallback.

    Args:
        news_items: List of news items with 'headline' and 'summary' fields
        ticker: Optional ticker symbol for context

    Returns:
        SentimentResult with score, confidence, and reasoning
    """
    client = get_llm_client()

    if client is None or not client.is_available():
        logger.debug(f"Using fallback sentiment analysis for {ticker}")
        return _analyze_sentiment_fallback(news_items)

    # Prepare news text
    news_text = "\n\n".join(
        f"Headline: {item.get('headline', '')}\nSummary: {item.get('summary', '')}"
        for item in news_items[:10]  # Limit to 10 items
    )

    system_prompt = """You are a financial sentiment analyst. Analyze news headlines and summaries to determine market sentiment for a stock.
Respond with a sentiment score between -1.0 (very bearish) and +1.0 (very bullish), followed by a brief explanation.
Format: SCORE: <number> | REASONING: <explanation>"""

    prompt = f"""Analyze the following news for {ticker or "this stock"}:

{news_text}

Provide a sentiment score and reasoning."""

    try:
        response = client.generate(prompt, system_prompt)

        # Parse response
        score = _parse_sentiment_score(response)
        reasoning_match = re.search(r"REASONING:\s*(.+)", response, re.IGNORECASE)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else response[:100]

        label = "bullish" if score > 0.2 else "bearish" if score < -0.2 else "neutral"
        confidence = min(0.9, 0.5 + abs(score) * 0.4)

        return SentimentResult(
            score=score,
            confidence=confidence,
            label=label,
            reasoning=reasoning,
            source="llm",
        )
    except Exception as e:
        logger.warning(f"LLM sentiment analysis failed for {ticker}: {e}, using fallback")
        return _analyze_sentiment_fallback(news_items)


def assess_macro_risk(macro_data: dict) -> RiskGateResult:
    """
    Assess macro risk level using local LLM or fallback.

    Args:
        macro_data: Dictionary with macro indicators (VIX, yield curve, breadth, etc.)

    Returns:
        RiskGateResult with risk level, factors, and recommendation
    """
    client = get_llm_client()

    if client is None or not client.is_available():
        logger.debug("Using fallback macro risk assessment")
        return _risk_gate_fallback(macro_data)

    # Format macro data for LLM
    macro_text = "\n".join(f"- {k}: {v}" for k, v in macro_data.items() if v is not None)

    system_prompt = """You are a macro risk analyst. Assess the overall market risk level based on provided indicators.
Consider: volatility (VIX), yield curve, market breadth, credit spreads, economic data.
Respond with: RISK: <low/medium/high/extreme> | CONFIDENCE: <0-1> | FACTORS: <key factors> | RECOMMENDATION: <proceed/caution/reduce_size/avoid>"""

    prompt = f"""Assess the macro risk level based on these indicators:

{macro_text}

Provide risk assessment and trading recommendation."""

    try:
        response = client.generate(prompt, system_prompt)

        # Parse response
        risk_match = re.search(r"RISK:\s*(\w+)", response, re.IGNORECASE)
        conf_match = re.search(r"CONFIDENCE:\s*([\d.]+)", response, re.IGNORECASE)
        factors_match = re.search(r"FACTORS:\s*(.+?)(?:\||$)", response, re.IGNORECASE)
        rec_match = re.search(r"RECOMMENDATION:\s*(\w+)", response, re.IGNORECASE)

        risk_level = risk_match.group(1).lower() if risk_match else "medium"
        if risk_level not in ("low", "medium", "high", "extreme"):
            risk_level = "medium"

        confidence = float(conf_match.group(1)) if conf_match else 0.5
        confidence = max(0.1, min(0.95, confidence))

        factors = []
        if factors_match:
            factors = [f.strip() for f in factors_match.group(1).split(",")]

        recommendation = rec_match.group(1).lower() if rec_match else "caution"
        if recommendation not in ("proceed", "caution", "reduce_size", "avoid"):
            recommendation = "caution"

        return RiskGateResult(
            risk_level=risk_level,
            confidence=confidence,
            factors=factors,
            recommendation=recommendation,
            source="llm",
        )
    except Exception as e:
        logger.warning(f"LLM macro risk assessment failed: {e}, using fallback")
        return _risk_gate_fallback(macro_data)


def get_llm_status() -> dict:
    """Get the current LLM status."""
    client = get_llm_client()
    if client:
        return {
            "enabled": True,
            "provider": LOCAL_LLM_PROVIDER,
            "model": LOCAL_LLM_MODEL,
            "available": client.is_available(),
            "url": LOCAL_LLM_URL,
        }
    return {
        "enabled": LOCAL_LLM_ENABLED,
        "provider": LOCAL_LLM_PROVIDER,
        "model": LOCAL_LLM_MODEL,
        "available": False,
        "fallback_mode": True,
        "note": "Using rule-based analysis fallback",
    }
