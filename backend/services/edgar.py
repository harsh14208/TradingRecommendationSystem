"""
SEC EDGAR Form 4 insider-trading scraper.
Uses EDGAR's free public JSON API — no API key required.
Required by EDGAR ToS: always send a descriptive User-Agent.
"""

import ssl
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
import certifi

HEADERS = {"User-Agent": "SignalTrade research@signaltrade.com", "Accept-Encoding": "gzip"}
_ssl_ctx = ssl.create_default_context(cafile=certifi.where())

# Pre-seeded CIKs for the default watchlist — avoids the 3 MB tickers.json download
# on every cold-start.  Unknown tickers fall back to the live lookup.
_KNOWN_CIKS: dict[str, str] = {
    # Top 10 by market cap
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "NVDA": "0001045810",
    "AMZN": "0001018724",
    "GOOGL": "0001652044",
    "GOOG": "0001652044",
    "META": "0001326801",
    "TSLA": "0001318605",
    "AVGO": "0001730168",
    "BRK-B": "0001067983",
    "JPM": "0000019617",
    # Next tier
    "V": "0001403161",
    "LLY": "0000059478",
    "WMT": "0000104169",
    "XOM": "0000034088",
    "UNH": "0000731766",
    "MA": "0001141391",
    "JNJ": "0000200406",
    "COST": "0000909832",
    "ORCL": "0001341439",
    # Tech / growth
    "AMD": "0000002488",
    "NFLX": "0001065280",
    "PLTR": "0001321655",
    "SMCI": "0000866374",
    "CRM": "0001108524",
    "SNOW": "0001640147",
}

_cik_map: dict[str, str] = dict(_KNOWN_CIKS)
_cik_map_ts: float = 0.0
_activity_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 3600  # 1 hour


async def _ensure_cik_map() -> None:
    """Lazy-load the full ticker→CIK map from EDGAR (one 3 MB download, cached forever)."""
    global _cik_map_ts
    if _cik_map_ts > 0:
        return
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(
                "https://www.sec.gov/files/company_tickers.json",
                headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as r:
                if r.status == 200:
                    data = await r.json(content_type=None)
                    for entry in data.values():
                        _cik_map[entry["ticker"]] = str(entry["cik_str"]).zfill(10)
                    _cik_map_ts = time.time()
    except Exception as e:
        print(f"[edgar] tickers.json fetch failed: {e}")


async def _get_cik(ticker: str) -> Optional[str]:
    if ticker in _cik_map:
        return _cik_map[ticker]
    await _ensure_cik_map()
    return _cik_map.get(ticker)


def _parse_form4(xml_text: str) -> tuple[int, int, float, float]:
    """Return (buy_shares, sell_shares, buy_value, sell_value)."""
    buys = sells = 0
    buy_val = sell_val = 0.0
    try:
        root = ET.fromstring(xml_text)
        for trans in root.iter():
            if "nonDerivativeTransaction" not in trans.tag:
                continue
            code = shares = price = None
            for child in trans.iter():
                tag = child.tag.split("}")[-1]  # strip namespace
                if tag == "transactionAcquiredDisposedCode":
                    for v in child:
                        if v.tag.split("}")[-1] == "value":
                            code = (v.text or "").strip().upper()
                elif tag == "transactionShares":
                    for v in child:
                        if v.tag.split("}")[-1] == "value":
                            try:
                                shares = float(v.text)
                            except (TypeError, ValueError):
                                pass
                elif tag == "transactionPricePerShare":
                    for v in child:
                        if v.tag.split("}")[-1] == "value":
                            try:
                                price = float(v.text)
                            except (TypeError, ValueError):
                                pass
            if code == "A" and shares:
                buys += int(shares)
                buy_val += shares * (price or 0)
            elif code == "D" and shares:
                sells += int(shares)
                sell_val += shares * (price or 0)
    except ET.ParseError:
        pass
    return buys, sells, buy_val, sell_val


async def get_insider_activity(ticker: str, days: int = 30) -> Optional[dict]:
    cached = _activity_cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    cik = await _get_cik(ticker)
    if not cik:
        return None

    empty = {"buys": 0, "sells": 0, "buy_value": 0, "sell_value": 0, "net_shares": 0, "score": 0.0, "filings": 0}

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            # ── Fetch submission history ────────────────────────────────
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return None
                subs = await r.json(content_type=None)

            recent = subs.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            dates = recent.get("filingDate", [])
            accessions = recent.get("accessionNumber", [])
            pri_docs = recent.get("primaryDocument", [])

            cutoff = datetime.now() - timedelta(days=days)
            form4s = []
            for i, form in enumerate(forms):
                if form != "4":
                    continue
                try:
                    if datetime.strptime(dates[i], "%Y-%m-%d") >= cutoff:
                        form4s.append(
                            {
                                "acc": accessions[i].replace("-", ""),
                                "doc": pri_docs[i],
                            }
                        )
                except (ValueError, IndexError):
                    continue

            if not form4s:
                _activity_cache[ticker] = (empty, time.time())
                return empty

            # ── Parse up to 5 most recent Form 4 XML docs ──────────────
            total_buys = total_sells = 0
            total_bv = total_sv = 0.0

            for f4 in form4s[:5]:
                cik_int = int(cik)
                xml_url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{f4['acc']}/{f4['doc']}"
                try:
                    async with session.get(xml_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as r:
                        if r.status != 200:
                            continue
                        text = await r.text()
                    b, s, bv, sv = _parse_form4(text)
                    total_buys += b
                    total_bv += bv
                    total_sells += s
                    total_sv += sv
                except Exception:
                    continue

            net = total_buys - total_sells
            denom = total_buys + total_sells
            # Insiders buying is a stronger signal than selling (sells can be diversification)
            score = round((net / denom * 15) if denom > 0 else 0.0, 1)

            result = {
                "buys": total_buys,
                "sells": total_sells,
                "buy_value": round(total_bv, 0),
                "sell_value": round(total_sv, 0),
                "net_shares": net,
                "score": score,
                "filings": len(form4s),
            }
            _activity_cache[ticker] = (result, time.time())
            return result

    except Exception as e:
        print(f"[edgar] {ticker}: {e}")
        return None


# ── 10-K / 10-Q MD&A Delta Analysis ─────────────────────────────────────────
# Tracks textual changes in SEC filings (MD&A and Risk Factors sections) QoQ.
# When companies silently add new risk warnings or change forward-looking language,
# it is a leading indicator of fundamental weakness.
#
# Strategy: fetch the two most recent 10-Q/10-K filings, extract MD&A section text,
# compute word-level diff. Flag: new negative risk language, removed bullish language.
#
# Cache: 24 hours (filings update quarterly).

_mda_cache: dict[str, tuple[dict, float]] = {}
_MDA_CACHE_TTL = 86400  # 24 hours

_RISK_KEYWORDS_NEG = {
    "uncertain",
    "uncertainty",
    "headwind",
    "challenging",
    "deteriorat",
    "decline",
    "decreased",
    "impairment",
    "write-down",
    "writedown",
    "litigation",
    "regulatory",
    "investigation",
    "significant risk",
    "material weakness",
    "going concern",
    "liquidity risk",
    "covenant",
    "adverse",
    "exposure",
    "inflationary",
    "supply constraint",
}
_RISK_KEYWORDS_POS = {
    "growth",
    "expand",
    "acceleration",
    "momentum",
    "record",
    "exceed",
    "outperform",
    "opportunit",
    "invest",
    "innovate",
    "strong demand",
    "favorable",
    "margin improvement",
    "pipeline",
}


async def _fetch_filing_text(cik: str, form_type: str = "10-Q") -> list[str]:
    """
    Return text of the last 2 10-Q (or 10-K) filings for a given CIK.
    Uses EDGAR XBRL inline viewer for quick text extraction.
    Returns list of (at most 2) filing texts, newest first.
    """
    url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    texts = []
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url, headers=HEADERS, ssl=_ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status != 200:
                    return []
                data = await r.json(content_type=None)

        filings = data.get("filings", {}).get("recent", {})
        forms = filings.get("form", [])
        accs = filings.get("accessionNumber", [])
        dates = filings.get("filingDate", [])

        targets = [(acc, dt) for form, acc, dt in zip(forms, accs, dates) if form == form_type][:2]

        for acc, _dt in targets:
            acc_clean = acc.replace("-", "")
            # Fetch the filing index to find the primary document
            idx_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_clean}/{acc}-index.json"
            try:
                async with aiohttp.ClientSession() as sess:
                    async with sess.get(
                        idx_url, headers=HEADERS, ssl=_ssl_ctx, timeout=aiohttp.ClientTimeout(total=6)
                    ) as r:
                        if r.status != 200:
                            continue
                        idx = await r.json(content_type=None)

                # Find the primary HTML/HTM document
                primary_doc = None
                for item in idx.get("directory", {}).get("item", []) or []:
                    name = item.get("name", "")
                    if name.endswith((".htm", ".html")) and not name.startswith("R"):
                        primary_doc = name
                        break

                if not primary_doc:
                    continue

                doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_clean}/{primary_doc}"
                async with aiohttp.ClientSession() as sess:
                    async with sess.get(
                        doc_url, headers=HEADERS, ssl=_ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                    ) as r:
                        if r.status != 200:
                            continue
                        html = await r.text(errors="replace")

                # Extract plain text (strip HTML tags)
                import re as _re

                plain = _re.sub(r"<[^>]+>", " ", html)
                plain = _re.sub(r"\s+", " ", plain)
                texts.append(plain[:50_000])  # cap at 50K chars per filing
            except Exception:
                continue
    except Exception:
        pass
    return texts


def _extract_mda_section(text: str) -> str:
    """Extract MD&A / Risk Factors section from raw SEC filing text."""
    import re as _re

    mda_pattern = _re.compile(
        r"(?:management.{0,30}discussion.{0,30}analysis|item\s+2[\.\s])"
        r"(.{500,15000})"
        r"(?:item\s+3|quantitative.{0,30}qualitative|market risk)",
        _re.IGNORECASE | _re.DOTALL,
    )
    m = mda_pattern.search(text)
    if m:
        return m.group(1)[:8000]
    # Fallback: return middle section of filing
    mid = len(text) // 3
    return text[mid : mid + 8000]


def _score_mda_delta(current: str, previous: str) -> tuple[float, str]:
    """
    Compare two MD&A texts and return (score_delta, human_reason).
    Positive delta = current filing more bullish / less risky than prior.
    Negative delta = new risk language added or bullish language removed.
    """
    import re as _re

    def _words(t: str) -> set[str]:
        return set(w.lower() for w in _re.split(r"\W+", t) if len(w) > 3)

    cur_w = _words(current)
    prev_w = _words(previous)
    new_w = cur_w - prev_w  # words added in current filing
    gone_w = prev_w - cur_w  # words removed from current filing

    # Count newly added risk vs bullish language
    new_neg = sum(1 for kw in _RISK_KEYWORDS_NEG if any(kw in w for w in new_w))
    new_pos = sum(1 for kw in _RISK_KEYWORDS_POS if any(kw in w for w in new_w))
    gone_pos = sum(1 for kw in _RISK_KEYWORDS_POS if any(kw in w for w in gone_w))

    score_delta = (new_pos - gone_pos) * 1.5 - new_neg * 2.0
    score_delta = max(-8.0, min(8.0, round(score_delta, 1)))

    reason_parts = []
    if new_neg > 2:
        reason_parts.append(f"{new_neg} new risk terms added")
    if gone_pos > 2:
        reason_parts.append(f"{gone_pos} bullish terms removed")
    if new_pos > 2:
        reason_parts.append(f"{new_pos} new positive terms")
    reason = "; ".join(reason_parts) if reason_parts else "No significant language change"
    return score_delta, reason


async def get_mda_delta(ticker: str) -> dict:
    """
    Fetch the two most recent 10-Q filings for `ticker`, extract MD&A sections,
    and compute a score delta based on language shift.
    Returns {"score": float, "reason": str, "form_type": str} or {}.
    Cache: 24 hours.
    """
    cached = _mda_cache.get(ticker)
    if cached and time.time() - cached[1] < _MDA_CACHE_TTL:
        return cached[0]

    cik = _KNOWN_CIKS.get(ticker.upper())
    if not cik:
        _mda_cache[ticker] = ({}, time.time())
        return {}

    try:
        texts = await _fetch_filing_text(cik, "10-Q")
        form_type = "10-Q"
        if len(texts) < 2:
            texts = await _fetch_filing_text(cik, "10-K")
            form_type = "10-K"
        if len(texts) < 2:
            _mda_cache[ticker] = ({}, time.time())
            return {}

        mda_cur = _extract_mda_section(texts[0])
        mda_prev = _extract_mda_section(texts[1])
        delta, reason = _score_mda_delta(mda_cur, mda_prev)

        result = {"score": delta, "reason": reason, "form_type": form_type}
        _mda_cache[ticker] = (result, time.time())
        return result
    except Exception as e:
        print(f"[edgar mda_delta] {ticker}: {e}")
        _mda_cache[ticker] = ({}, time.time())
        return {}
