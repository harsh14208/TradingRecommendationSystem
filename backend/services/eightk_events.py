"""
8-K Material Event Signal — Massive Stocks API

Form 8-K current reports disclose material corporate events that must be
reported to the SEC within 4 business days. Categories with strong signal value:

  Item 1.01 — Material Definitive Agreement    (M&A, partnership) → +8 BUY
  Item 1.02 — Termination of Material Agreement → −6 SELL
  Item 2.01 — Completion of Acquisition/Disposition → directional
  Item 5.02 — Departure/Appointment of Directors/Officers (CEO change)
               CEO departure → −6 / CEO appointment → +3
  Item 8.01 — Other Events (share buyback, debt restructuring)
  Item 7.01 — Regulation FD (guidance, investor presentation) → ±4

Window: only process 8-Ks filed within the last 5 trading days.
Cache: 2 hours per ticker.
"""
import asyncio
import logging
import os
import time
from datetime import date, timedelta

import aiohttp

log = logging.getLogger("signal.trade.8k_events")

_cache: dict[str, dict] = {}
_TTL = 7200  # 2 hours

_BASE = "https://api.polygon.io"

# Item number → (direction_pts, label, sentiment)
_ITEM_MAP = {
    "1.01": (+8,  "Material Agreement (M&A/Partnership)", "pos"),
    "1.02": (-6,  "Agreement Termination",                "neg"),
    "2.01": (+6,  "Acquisition/Disposition Completed",   "pos"),
    "2.06": (-8,  "Material Impairment",                 "neg"),
    "5.02": (0,   "Executive Change",                    "neutral"),   # parsed separately
    "7.01": (+4,  "Reg FD / Guidance / Presentation",   "pos"),
    "8.01": (+3,  "Other Material Event",                "pos"),
}


def _parse_ceo_signal(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint   = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


async def get_8k_signals(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    import ssl, certifi
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    # Polygon.io SEC filings index — free tier accessible
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K",
              "filing_date.gte": cutoff, "limit": 5}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, ssl=ssl_ctx,
                                   timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:  # 403 = premium, return empty
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text  = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment  = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append({
                    "item":      item_key,
                    "label":     label,
                    "score":     pts,
                    "sentiment": sentiment,
                    "filed":     filed[:10],
                })

    result = {
        "score":    round(min(max(total_score, -12.0), 10.0), 1),
        "events":   event_labels,
        "filings":  parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result
