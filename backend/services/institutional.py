"""
13F Institutional Flow — SEC EDGAR XBRL parsing.

Tracks position changes from top hedge funds and institutional investors in our watchlist.
Quarterly lag (~45 days after quarter end), but high-credibility signal.

Free data source: https://data.sec.gov/  (no API key required)
Rate limit: 10 req/sec per SEC fair use policy.
"""

import asyncio
import logging
import time

import aiohttp
from services.http_client import shared_session

log = logging.getLogger("signal.trade.institutional")

# Top institutional investors tracked — (name, CIK, tier)
# Tier: "tier1" = highest credibility (Berkshire, Bridgewater, etc.)
TRACKED_FUNDS = [
    ("Berkshire Hathaway", "0001067983", "tier1"),
    ("Vanguard Group", "0000102909", "tier1"),
    ("BlackRock", "0001364742", "tier1"),
    ("State Street", "0000093751", "tier1"),
    ("Fidelity", "0000315066", "tier1"),
    ("JPMorgan Asset Mgmt", "0000049196", "tier2"),
    ("Capital Group", "0000813672", "tier2"),
    ("Invesco", "0000914208", "tier2"),
    ("Viking Global", "0001111830", "tier1"),
    ("Tiger Global", "0001167483", "tier1"),
    ("Duquesne Family Office", "0001537721", "tier1"),
    ("Pershing Square", "0001336528", "tier1"),
    ("Baupost Group", "0001100663", "tier1"),
    ("Third Point", "0001040273", "tier2"),
    ("Elliott Management", "0000886871", "tier2"),
]

TIER_SCORES = {"tier1": 8, "tier2": 4}

_CACHE: dict = {}
_CACHE_TTL = 6 * 3600  # 6 hours — filings don't change intraday

_SEC_HEADERS = {
    "User-Agent": "Signal.Trade harsh13858@gmail.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov",
}


async def _get(session: aiohttp.ClientSession, url: str) -> dict | list | None:
    try:
        async with session.get(url, headers=_SEC_HEADERS, timeout=aiohttp.ClientTimeout(total=15)) as r:
            if r.status == 200:
                return await r.json(content_type=None)
            log.debug(f"[13F] {url} → {r.status}")
            return None
    except Exception as e:
        log.debug(f"[13F] request failed {url}: {e}")
        return None


async def _fetch_latest_13f_holdings(session: aiohttp.ClientSession, cik: str) -> list[dict]:
    """
    Fetch the most recent 13F-HR filing holdings for a given CIK.
    Returns a list of {"ticker": str, "value_k": int, "shares": int, "action": str}
    where action is "new" | "increased" | "decreased" | "unchanged".
    """
    cache_key = f"13f_{cik}"
    if cache_key in _CACHE:
        if time.time() - _CACHE[cache_key]["ts"] < _CACHE_TTL:
            return _CACHE[cache_key]["data"]

    # Get filing list
    filings_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    data = await _get(session, filings_url)
    if not data:
        return []

    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accnos = recent.get("accessionNumber", [])

    # Find the three most recent 13F-HR filings (Q0, Q1, Q2) for QoQ trend tracking
    filings_13f = [(dates[i], accnos[i]) for i, form in enumerate(forms) if form in ("13F-HR", "13F-HR/A")][:3]

    if not filings_13f:
        return []

    holdings_by_quarter = []
    for filing_date, accno in filings_13f:
        accno_fmt = accno.replace("-", "")
        index_url = f"https://data.sec.gov/Archives/edgar/data/{int(cik)}/{accno_fmt}/{accno}-index.json"
        index_data = await _get(session, index_url)
        if not index_data:
            continue

        # Find the primary document (infotable.xml or similar)
        xml_url = None
        for item in index_data.get("directory", {}).get("item", []) or []:
            name = item.get("name", "")
            if "infotable" in name.lower() and name.endswith(".xml"):
                xml_url = f"https://data.sec.gov/Archives/edgar/data/{int(cik)}/{accno_fmt}/{name}"
                break

        if not xml_url:
            continue

        holdings = await _parse_infotable_xml(session, xml_url, filing_date)
        holdings_by_quarter.append(holdings)
        await asyncio.sleep(0.15)  # SEC rate limit: 10 req/sec

    if not holdings_by_quarter:
        return []

    current = {h["cusip"]: h for h in holdings_by_quarter[0]}
    previous = {h["cusip"]: h for h in holdings_by_quarter[1]} if len(holdings_by_quarter) > 1 else {}
    two_ago = {h["cusip"]: h for h in holdings_by_quarter[2]} if len(holdings_by_quarter) > 2 else {}

    result = []
    for cusip, h in current.items():
        if not h.get("ticker"):
            continue

        # Q0 vs Q1 action
        if cusip in previous:
            prev_shares = previous[cusip]["shares"]
            if h["shares"] > prev_shares * 1.05:
                action = "increased"
            elif h["shares"] < prev_shares * 0.95:
                action = "decreased"
            else:
                action = "unchanged"
        else:
            action = "new"

        # QoQ trend: compare Q1 direction vs Q2 direction to detect consecutive momentum
        qoq_trend = "neutral"
        if action in ("increased", "new") and cusip in previous and cusip in two_ago:
            q1_shares = previous[cusip]["shares"]
            q2_shares = two_ago[cusip]["shares"]
            if q1_shares > q2_shares * 1.05:
                # Two consecutive quarters of increases → rising conviction
                qoq_trend = "rising"
            elif q1_shares < q2_shares * 0.95:
                # Increased this quarter but decreased last quarter → reversing
                qoq_trend = "reversing_up"
        elif action == "decreased" and cusip in previous and cusip in two_ago:
            q1_shares = previous[cusip]["shares"]
            q2_shares = two_ago[cusip]["shares"]
            if q1_shares < q2_shares * 0.95:
                # Two consecutive quarters of decreases → falling conviction / early exit
                qoq_trend = "falling"
            elif q1_shares > q2_shares * 1.05:
                qoq_trend = "reversing_down"

        result.append({**h, "action": action, "qoq_trend": qoq_trend})

    _CACHE[cache_key] = {"ts": time.time(), "data": result}
    return result


async def _parse_infotable_xml(session: aiohttp.ClientSession, url: str, filing_date: str) -> list[dict]:
    """Parse an SEC 13F infotable XML into a list of holdings."""
    try:
        async with session.get(url, headers=_SEC_HEADERS, timeout=aiohttp.ClientTimeout(total=20)) as r:
            if r.status != 200:
                return []
            text = await r.text()
    except Exception:
        return []

    import xml.etree.ElementTree as ET

    holdings = []
    try:
        # Strip namespace for simpler parsing
        text_clean = text.replace(' xmlns="', ' xmlns_orig="')
        root = ET.fromstring(text_clean)

        for entry in root.iter("infoTable"):
            name = (entry.findtext("nameOfIssuer") or "").strip()
            cusip = (entry.findtext("cusip") or "").strip()
            value = int(entry.findtext("value") or 0)  # thousands USD
            shares = int(entry.findtext("sshPrnamt") or 0)
            ticker = _cusip_to_ticker(cusip)
            if not ticker:
                continue
            holdings.append(
                {
                    "name": name,
                    "ticker": ticker,
                    "cusip": cusip,
                    "value_k": value,
                    "shares": shares,
                    "filing_date": filing_date,
                }
            )
    except ET.ParseError:
        pass

    return holdings


# CUSIP → ticker mapping (common large-caps that appear in 13F filings)
# Deduplicated — each CUSIP appears only once
_CUSIP_MAP: dict[str, str] = {
    "037833100": "AAPL",
    "594918104": "MSFT",
    "023135106": "AMZN",
    "02079K305": "GOOGL",
    "30303M102": "META",
    "88160R101": "TSLA",
    "67066G104": "NVDA",
    "922908363": "V",
    "57636Q104": "MA",
    "46625H100": "JPM",
    "172967424": "CRM",
    "69608A108": "ORCL",
    "742718109": "PG",
    "478160104": "JNJ",
    "931427108": "UNH",
    "911312106": "UPS",
    "732834107": "PFE",
    "857477103": "STZ",
    "079879106": "BRK-B",
    "91822M106": "V",
    "345370860": "AMD",
    "78486M107": "S&P",
    "12504L109": "COP",
    "458140100": "INTC",
    "883556102": "TM",
    "66987V109": "NVO",
    "025816109": "AXP",
}


def _cusip_to_ticker(cusip: str) -> str | None:
    """Look up ticker for a CUSIP. Falls back to None for unknown CUSIPs."""
    return _CUSIP_MAP.get(cusip.strip())


async def get_institutional_signals(watchlist: list[str]) -> list[dict]:
    """
    Main entry point: fetch 13F signals for tickers in the watchlist.
    Returns list of signal dicts with keys: ticker, score, rationale, sources.
    Tracks both institutional buying AND selling for balanced signals.
    """
    watchlist_set = set(t.upper() for t in watchlist)
    results: list[dict] = []

    async with shared_session() as session:
        for fund_name, cik, tier in TRACKED_FUNDS:
            try:
                holdings = await _fetch_latest_13f_holdings(session, cik)
                for h in holdings:
                    if h["ticker"] not in watchlist_set:
                        continue

                    base_score = TIER_SCORES.get(tier, 3)
                    qoq_trend = h.get("qoq_trend", "neutral")

                    # QoQ multiplier: consecutive direction = stronger signal
                    QOQ_MULT = {
                        "rising": 1.5,  # 2+ quarters increasing → high conviction
                        "reversing_up": 1.1,  # started buying after selling
                        "neutral": 1.0,
                        "reversing_down": 1.0,  # started selling after buying — caution
                        "falling": 1.5,  # 2+ quarters decreasing → early exit warning
                    }
                    qoq_mult = QOQ_MULT.get(qoq_trend, 1.0)
                    qoq_note = {
                        "rising": " [QoQ Rising — 2+ quarters buying]",
                        "reversing_up": " [QoQ Reversing Up — new buying trend]",
                        "neutral": "",
                        "reversing_down": "",
                        "falling": " [QoQ Falling — 2+ quarters exiting]",
                    }.get(qoq_trend, "")

                    # Track both buys and sells
                    if h["action"] in ("new", "increased"):
                        if h["action"] == "new":
                            score = round((base_score + 3) * qoq_mult)
                            action_label = "opened new position"
                        else:
                            score = round(base_score * qoq_mult)
                            action_label = "increased position"

                        results.append(
                            {
                                "ticker": h["ticker"],
                                "score": score,
                                "action": "BUY",
                                "rationale": f"{fund_name} {action_label} as of {h['filing_date']} (${h['value_k']:,}K, {h['shares']:,} shares){qoq_note}",
                                "source": "13F",
                                "fund": fund_name,
                                "tier": tier,
                                "filing_date": h["filing_date"],
                                "qoq_trend": qoq_trend,
                            }
                        )
                    elif h["action"] in ("decreased",):
                        # Falling QoQ trend amplifies the bearish score
                        score = round(-base_score * qoq_mult)
                        results.append(
                            {
                                "ticker": h["ticker"],
                                "score": score,
                                "action": "SELL",
                                "rationale": f"{fund_name} decreased position as of {h['filing_date']} (${h['value_k']:,}K, {h['shares']:,} shares){qoq_note}",
                                "source": "13F",
                                "fund": fund_name,
                                "tier": tier,
                                "filing_date": h["filing_date"],
                                "qoq_trend": qoq_trend,
                            }
                        )
                await asyncio.sleep(0.1)  # SEC rate limit
            except Exception as e:
                log.debug(f"[13F] {fund_name}: {e}")
                continue

    # Aggregate by ticker — multiple funds holding = stronger signal
    by_ticker: dict = {}
    for r in results:
        t = r["ticker"]
        if t not in by_ticker:
            by_ticker[t] = {
                "ticker": t,
                "score": 0,
                "rationale_items": [],
                "funds": [],
                "actions": [],
                "qoq_trends": [],
            }
        by_ticker[t]["score"] += r["score"]
        by_ticker[t]["funds"].append(r["fund"])
        by_ticker[t]["rationale_items"].append(r["rationale"])
        by_ticker[t]["actions"].append(r["action"])
        by_ticker[t]["qoq_trends"].append(r.get("qoq_trend", "neutral"))

    aggregated = []
    for t, data in by_ticker.items():
        # Cap score at ±20 to avoid drowning out other signals
        capped_score = max(-20, min(20, data["score"]))
        fund_list = ", ".join(data["funds"][:3])
        extra = f" +{len(data['funds']) - 3} more" if len(data["funds"]) > 3 else ""

        # Determine overall sentiment and QoQ trend label
        sentiment = "pos" if capped_score > 0 else "neg" if capped_score < 0 else "neu"
        action_label = "buying" if capped_score > 0 else "selling" if capped_score < 0 else "mixed"

        # Surface the strongest QoQ trend signal for the rationale head
        trend_counts = {tr: data["qoq_trends"].count(tr) for tr in set(data["qoq_trends"])}
        dominant_trend = max(trend_counts, key=trend_counts.get) if trend_counts else "neutral"
        trend_suffix = {
            "rising": " · Rising QoQ Conviction",
            "falling": " · Falling QoQ — Early Exit Signal",
            "reversing_up": " · QoQ Turning Bullish",
            "reversing_down": "",
            "neutral": "",
        }.get(dominant_trend, "")

        aggregated.append(
            {
                "ticker": t,
                "score": capped_score,
                "source": "13F",
                "qoq_trend": dominant_trend,
                "rationale": {
                    "src": "13F",
                    "head": f"Institutional {action_label}: {fund_list}{extra}{trend_suffix}",
                    "detail": data["rationale_items"][0] if data["rationale_items"] else "",
                    "sentiment": sentiment,
                    "body": data["rationale_items"][0] if data["rationale_items"] else "",
                },
            }
        )

    return aggregated
