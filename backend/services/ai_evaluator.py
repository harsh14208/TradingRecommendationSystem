"""AI pre-execution trade evaluator.

Calls a configured LLM provider (OpenAI, Anthropic, or any OpenAI-compatible
local endpoint) to review a signal immediately before capital is committed.
The evaluator is inserted **after** all engineering risk guards (drawdown,
runtime risk limits, capacity/slippage checks) so it acts as a final
qualitative gate, not a replacement for quantitative risk controls.

When disabled or when the AI provider is unreachable, the gate defaults to
``approved=True`` so a network outage cannot freeze all trading unless the
operator explicitly configures ``AI_EVAL_FAIL_OPEN_ON_ERROR=false``.
"""

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Optional

import aiohttp

from config import get_settings
from services.http_client import get_session, get_ssl_context, retry_with_backoff

log = logging.getLogger("ai_evaluator")


@dataclass
class AIEvalResult:
    """Result of an AI pre-execution trade review."""

    approved: bool
    reasoning: str
    risk_flag: Optional[str] = None
    confidence: Optional[float] = None
    raw_response: Optional[str] = None


# Conservative list of risk flags the model may return. Anything outside this
# set is coerced to ``other`` so downstream analytics stay well-formed.
_RISK_FLAGS = {
    "none",
    "macro",
    "technical",
    "concentration",
    "liquidity",
    "earnings",
    "sentiment",
    "valuation",
    "other",
}


# Shared system prompt used for every provider. It is intentionally long so the
# model stays in a risk-aware, quantitative mindset and returns structured JSON.
_SYSTEM_PROMPT = """You are a disciplined quantitative trading risk analyst.
Your job is to review one trade signal moments before it is sent to a broker.

Rules:
- Only approve when the setup, risk/reward, and current market context are favorable.
- Be conservative: a marginal signal should be blocked.
- If the signal conflicts with common sense risk management (e.g., stop wider than target with no strong edge, low liquidity, adverse macro, upcoming earnings), block it.
- Respond with a single JSON object. Do not wrap it in Markdown.

Required JSON schema:
{
  "decision": "approve" | "block",
  "reasoning": "1-3 sentence explanation",
  "risk_flag": "none" | "macro" | "technical" | "concentration" | "liquidity" | "earnings" | "sentiment" | "valuation" | "other",
  "confidence": 0.0-1.0
}
"""


def _normalize_risk_flag(flag: Any) -> Optional[str]:
    """Coerce model risk flag into the canonical vocabulary."""
    if flag is None:
        return None
    flag = str(flag).lower().strip()
    if flag in ("", "null", "none"):
        return None
    return flag if flag in _RISK_FLAGS else "other"


def _build_prompt(signal: dict, market_ctx: Optional[dict]) -> str:
    """Serialize signal + market context into a structured review prompt."""
    ticker = signal.get("ticker", "UNKNOWN")
    action = signal.get("action", "UNKNOWN")
    confidence = signal.get("confidence")
    price = signal.get("price")
    entry = signal.get("entry")
    stop = signal.get("stop") or signal.get("stopPrice")
    target = signal.get("target") or signal.get("targetPrice")
    style = signal.get("style", "swing")
    sector_etf = signal.get("sectorEtf") or signal.get("sector_etf")
    cohort = signal.get("cohort", "")
    sources = signal.get("sources", [])
    rationale = signal.get("rationale", [])

    if isinstance(sources, list):
        sources_text = ", ".join(str(s) for s in sources)
    else:
        sources_text = str(sources)

    rationale_text = ""
    if isinstance(rationale, list):
        rationale_text = "\n".join(
            f"- [{card.get('src', '?')}] {card.get('head', '')}: {card.get('body', '')}" for card in rationale
        )
    elif isinstance(rationale, str):
        rationale_text = rationale

    market_text = ""
    if market_ctx:
        market_text = "\n".join(f"- {k}: {v}" for k, v in market_ctx.items() if v is not None)

    prompt = f"""Review the following trade signal before execution.

Signal:
- Ticker: {ticker}
- Action: {action}
- Signal confidence: {confidence}
- Current price: {price}
- Entry: {entry}
- Stop: {stop}
- Target: {target}
- Style: {style}
- Sector ETF: {sector_etf or "N/A"}
- Cohort: {cohort or "N/A"}
- Sources: {sources_text or "N/A"}

Rationale:
{rationale_text or "None provided"}
"""
    if market_text:
        prompt += f"\nMarket context:\n{market_text}\n"

    prompt += "\nReturn only the required JSON object."
    return prompt


def _extract_json(text: str) -> Optional[str]:
    """Best-effort extraction of a JSON object from model output."""
    text = text.strip()

    # 1. Try a fenced code block.
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)

    # 2. Try the first top-level JSON object in the text.
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        return match.group(1)

    return None


def _parse_response(text: str, fail_open: bool) -> AIEvalResult:
    """Parse a model response into a typed AIEvalResult."""
    json_text = _extract_json(text)
    if json_text is None:
        log.warning("ai_evaluator: no JSON object found in response: %s", text[:200])
        return AIEvalResult(
            approved=fail_open,
            reasoning="Could not parse AI response; fail-open."
            if fail_open
            else "Could not parse AI response; fail-closed.",
            risk_flag="parse_error",
            raw_response=text,
        )

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        log.warning("ai_evaluator: invalid JSON: %s", exc)
        return AIEvalResult(
            approved=fail_open,
            reasoning="Invalid JSON from AI; fail-open." if fail_open else "Invalid JSON from AI; fail-closed.",
            risk_flag="parse_error",
            raw_response=text,
        )

    decision = str(data.get("decision", "")).lower().strip()
    approved = decision == "approve"

    confidence = data.get("confidence")
    if confidence is not None:
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = None
        if confidence is not None:
            confidence = max(0.0, min(1.0, confidence))

    return AIEvalResult(
        approved=approved,
        reasoning=str(data.get("reasoning", "")),
        risk_flag=_normalize_risk_flag(data.get("risk_flag")),
        confidence=confidence,
        raw_response=text,
    )


def _get_secret(settings, name: str) -> str:
    """Safely extract a string value from a SecretStr or plain string setting."""
    value = getattr(settings, name, "")
    if value is None:
        return ""
    if hasattr(value, "get_secret_value"):
        return value.get_secret_value()
    return str(value)


async def _call_openai(prompt: str, model: str, timeout: int, base_url: str, api_key: str) -> str:
    """Call an OpenAI-compatible chat/completions endpoint."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 512,
    }
    # response_format is only valid on the official OpenAI API and a few
    # compatible hosts. When an explicit local base URL is provided, skip it
    # to avoid surprising 400s from lightweight servers.
    if base_url == "https://api.openai.com/v1":
        payload["response_format"] = {"type": "json_object"}

    async def _post() -> str:
        session = get_session()
        async with session.post(
            url,
            headers=headers,
            json=payload,
            ssl=get_ssl_context(),
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data["choices"][0]["message"]["content"]

    return await retry_with_backoff(_post)


async def _call_anthropic(prompt: str, model: str, timeout: int, api_key: str) -> str:
    """Call the Anthropic Messages API."""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": model,
        "max_tokens": 512,
        "temperature": 0.1,
        "system": _SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}],
    }

    async def _post() -> str:
        session = get_session()
        async with session.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            ssl=get_ssl_context(),
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data["content"][0]["text"]

    return await retry_with_backoff(_post)


async def evaluate_trade(
    signal: dict,
    market_ctx: Optional[dict] = None,
) -> AIEvalResult:
    """
    Run an AI pre-execution review on ``signal``.

    Returns ``approved=True`` when the evaluator is disabled, when no provider
    key is configured, or when the API call fails and
    ``AI_EVAL_FAIL_OPEN_ON_ERROR`` is true (default).
    """
    settings = get_settings()
    if not getattr(settings, "ai_eval_enabled", False):
        return AIEvalResult(approved=True, reasoning="AI evaluation disabled")

    provider = getattr(settings, "ai_eval_provider", "openai").lower().strip()
    model = getattr(settings, "ai_eval_model", "gpt-4o-mini")
    timeout = int(getattr(settings, "ai_eval_timeout", 15))
    fail_open = bool(getattr(settings, "ai_eval_fail_open_on_error", True))

    prompt = _build_prompt(signal, market_ctx)

    try:
        if provider == "anthropic":
            api_key = _get_secret(settings, "anthropic_api_key")
            if not api_key:
                log.warning("ai_evaluator: anthropic provider selected but ANTHROPIC_API_KEY is unset")
                return AIEvalResult(approved=fail_open, reasoning="Anthropic key missing", risk_flag="config_error")
            text = await _call_anthropic(prompt, model, timeout, api_key)
        elif provider == "kimi":
            api_key = _get_secret(settings, "kimi_api_key")
            if not api_key:
                log.warning("ai_evaluator: kimi provider selected but KIMI_API_KEY is unset")
                return AIEvalResult(approved=fail_open, reasoning="Kimi key missing", risk_flag="config_error")
            # Kimi exposes an OpenAI-compatible endpoint.
            text = await _call_openai(prompt, model, timeout, "https://api.moonshot.cn/v1", api_key)
        elif provider in ("openai", "openai-compatible"):
            api_key = _get_secret(settings, "openai_api_key")
            base_url = getattr(settings, "ai_eval_base_url", "").rstrip("/") or "https://api.openai.com/v1"
            if not api_key and base_url == "https://api.openai.com/v1":
                log.warning("ai_evaluator: openai provider selected but OPENAI_API_KEY is unset")
                return AIEvalResult(approved=fail_open, reasoning="OpenAI key missing", risk_flag="config_error")
            text = await _call_openai(prompt, model, timeout, base_url, api_key)
        else:
            log.warning("ai_evaluator: unknown provider %r, defaulting to openai", provider)
            api_key = _get_secret(settings, "openai_api_key")
            text = await _call_openai(prompt, model, timeout, "https://api.openai.com/v1", api_key)

        return _parse_response(text, fail_open=fail_open)

    except aiohttp.ClientResponseError as exc:
        log.warning("ai_evaluator: provider returned %s: %s", exc.status, exc.message)
        return AIEvalResult(
            approved=fail_open,
            reasoning=f"AI provider HTTP {exc.status}",
            risk_flag="api_error",
        )
    except Exception as exc:
        log.warning("ai_evaluator: evaluation failed: %s", exc)
        return AIEvalResult(
            approved=fail_open,
            reasoning=f"AI evaluation error: {exc}",
            risk_flag="api_error",
        )
