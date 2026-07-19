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


# Shared system prompt used for every provider. Keep it short so reasoning
# models (e.g. Kimi Code) do not paraphrase instructions instead of following
# them. The concrete JSON example is supplied in the user message.
_SYSTEM_PROMPT = """You are a disciplined quantitative trading risk analyst.
Review one trade signal moments before it is sent to a broker.
Be conservative: only approve clean, favorable setups. Block marginal signals.
Respond with a single JSON object only — no Markdown, no explanation outside the JSON."""


def _normalize_risk_flag(flag: Any) -> Optional[str]:
    """Coerce model risk flag into the canonical vocabulary."""
    if flag is None:
        return None
    flag = str(flag).lower().strip()
    if flag in ("", "null", "none"):
        return None
    return flag if flag in _RISK_FLAGS else "other"


def _build_prompt(signal: dict, market_ctx: Optional[dict], include_role_prefix: bool = False) -> str:
    """Serialize signal + market context into a structured review prompt.""

    Kimi Code reasoning models respond better when the analyst role and JSON
    rules are part of the user message rather than a separate system message.
    """
    role_prefix = """You are a disciplined quantitative trading risk analyst. Review one trade signal moments before it is sent to a broker.
Be conservative: only approve clean, favorable setups. Block marginal signals.
Respond with a single JSON object only — no Markdown, no explanation outside the JSON.

"""
    if include_role_prefix:
        prompt = role_prefix
    else:
        prompt = ""
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

    prompt += f"""Review the following trade signal before execution.

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

    prompt += """
Return ONLY a single JSON object matching this schema:
{
  "decision": "approve" | "block",
  "reasoning": "1-3 sentence explanation",
  "risk_flag": "none" | "macro" | "technical" | "concentration" | "liquidity" | "earnings" | "sentiment" | "valuation" | "other",
  "confidence": 0.0-1.0
}

Example response:
{"decision": "approve", "reasoning": "Clean setup with favorable risk/reward.", "risk_flag": "none", "confidence": 0.85}
"""
    return prompt


def _extract_json(text: str) -> Optional[str]:
    """Best-effort extraction of the first valid JSON object from model output."""
    text = text.strip()

    # 1. Try a fenced code block.
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)

    # 2. Find the first `{` and walk forward to match braces, returning the
    #    first substring that parses as JSON. This handles models that output
    #    JSON followed by extra reasoning text.
    start = text.find("{")
    while start != -1:
        depth = 0
        in_string = False
        escape = False
        for i, ch in enumerate(text[start:], start=start):
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
            else:
                if ch == '"':
                    in_string = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        candidate = text[start : i + 1]
                        try:
                            json.loads(candidate)
                            return candidate
                        except json.JSONDecodeError:
                            break
        start = text.find("{", start + 1)

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


async def _call_openai(
    prompt: str,
    model: str,
    timeout: int,
    base_url: str,
    api_key: str,
    temperature: float = 0.1,
    system_prompt: Optional[str] = _SYSTEM_PROMPT,
    max_tokens: int = 1024,
) -> str:
    """Call an OpenAI-compatible chat/completions endpoint."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
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
            message = data["choices"][0]["message"]
            # Reasoning models (e.g. Kimi Code) may split output across
            # content and reasoning_content. Concatenate them so JSON extraction
            # can find the object regardless of which field holds it.
            content = message.get("content") or ""
            reasoning = message.get("reasoning_content") or ""
            return f"{content}\n{reasoning}".strip()

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
            # Kimi Code keys (sk-kimi-...) use the coding endpoint. That endpoint
            # only accepts temperature=1. Reasoning models also work best when
            # instructions are inline in the user message, so we skip the system
            # message and prepend the role prefix there. We request more tokens
            # because reasoning models can consume a lot before emitting JSON.
            kimi_prompt = _build_prompt(signal, market_ctx, include_role_prefix=True)
            text = await _call_openai(
                kimi_prompt,
                model,
                timeout,
                "https://api.kimi.com/coding/v1",
                api_key,
                temperature=1.0,
                system_prompt=None,
                max_tokens=2048,
            )
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
