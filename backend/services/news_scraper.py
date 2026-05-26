"""
Headless news scraper: Yahoo Finance RSS, Seeking Alpha RSS, Reuters RSS, Finviz fallback.

Priority order per ticker:
  1. Yahoo Finance RSS  — free per-ticker feed, no key, reliable uptime
  2. Seeking Alpha RSS  — free per-ticker feed, structured analyst + news items
  3. Reuters via Google News RSS — reliable attribution, no key required
  4. Finviz news table  — aiohttp first; Playwright if blocked (optional dep)

Results are deduped by headline word-overlap and merged newest-first.
Cache TTL: 10 min (news_scraper sits alongside Finnhub, not replacing it).

Install Playwright once with:
    pip install playwright && playwright install chromium
If playwright is absent, Yahoo/SeekingAlpha/Reuters still work; Finviz is skipped.
"""

import asyncio
import logging
import re
import ssl
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional

import aiohttp
import certifi

from services.news import score_sentiment

# Shared SSL context using certifi's CA bundle — required on macOS/Python 3.14
# where the system cert store is not automatically available to aiohttp.
_ssl_ctx = ssl.create_default_context(cafile=certifi.where())

log = logging.getLogger("signal.news_scraper")

_CACHE: dict[str, tuple[list, float]] = {}
_TTL = 600   # 10 minutes — news is time-sensitive

# Chrome-like UA to avoid trivial bot blocks on Finviz / Google
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",  # omit br — aiohttp lacks brotli support
    "Connection":      "keep-alive",
}


# ── Yahoo Finance RSS ─────────────────────────────────────────────────────────

async def _fetch_yahoo_finance(ticker: str, session: aiohttp.ClientSession) -> list[dict]:
    """
    Yahoo Finance publishes a free per-ticker RSS feed with recent headlines.
    Endpoint: feeds.finance.yahoo.com/rss/2.0/headline?s=TICKER
    No API key required; generally very reliable.
    """
    url = (
        f"https://feeds.finance.yahoo.com/rss/2.0/headline"
        f"?s={ticker.upper()}&region=US&lang=en-US"
    )
    try:
        async with session.get(url, ssl=_ssl_ctx, headers=_HEADERS,
                               timeout=aiohttp.ClientTimeout(total=12)) as r:
            if r.status != 200:
                log.debug(f"[yahoo] {ticker}: HTTP {r.status}")
                return []
            text = await r.text()
    except Exception as e:
        log.debug(f"[yahoo] {ticker}: {e}")
        return []

    text = re.sub(r'\s+xmlns(?::\w+)?="[^"]+"', "", text)
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        log.debug(f"[yahoo] {ticker}: XML parse error: {e}")
        return []

    items: list[dict] = []
    for item in root.findall(".//item")[:10]:
        title     = (item.findtext("title")       or "").strip()
        link      = (item.findtext("link")        or "").strip()
        desc      = (item.findtext("description") or "").strip()
        pub       = item.findtext("pubDate")       or ""
        desc_clean = re.sub(r"<[^>]+>", "", desc)[:300]
        hours_ago  = _hours_since(pub)
        if title and hours_ago < 7 * 24:
            items.append({
                "headline":  title,
                "summary":   desc_clean or title,
                "sentiment": score_sentiment(title + " " + desc_clean),
                "hours_ago": hours_ago,
                "source":    "Yahoo Finance",
                "url":       link,
            })
    return items


# ── Seeking Alpha RSS ────────────────────────────────────────────────────────

async def _fetch_seeking_alpha(ticker: str, session: aiohttp.ClientSession) -> list[dict]:
    """
    Seeking Alpha publishes a free per-ticker RSS feed at a stable public URL.
    Covers earnings previews, analyst articles, and breaking corporate news.
    """
    url = f"https://seekingalpha.com/api/sa/combined/{ticker.upper()}.xml"
    try:
        async with session.get(url, ssl=_ssl_ctx, timeout=aiohttp.ClientTimeout(total=12)) as r:
            if r.status != 200:
                log.debug(f"[seekingalpha] {ticker}: HTTP {r.status}")
                return []
            text = await r.text()
    except Exception as e:
        log.debug(f"[seekingalpha] {ticker}: {e}")
        return []

    # Strip namespace declarations AND any prefixed elements (sa:, media:)
    # so ElementTree can parse without "unbound prefix" errors.
    text = re.sub(r'\s+xmlns(?::\w+)?="[^"]+"', "", text)   # strip xmlns attrs
    text = re.sub(r"</?(?:sa|media):[^>]*>", "", text)       # remove sa:/media: tags
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        log.debug(f"[seekingalpha] {ticker}: XML parse error: {e}")
        return []

    items: list[dict] = []
    for item in root.findall(".//item")[:10]:
        title  = (item.findtext("title")       or "").strip()
        desc   = (item.findtext("description") or "").strip()
        link   = (item.findtext("link")        or "").strip()
        pub    = item.findtext("pubDate")       or ""

        desc_clean = re.sub(r"<[^>]+>", "", desc)[:300]
        hours_ago  = _hours_since(pub)
        if title and hours_ago < 7 * 24:
            items.append({
                "headline":  title,
                "summary":   desc_clean or title,
                "sentiment": score_sentiment(title + " " + desc_clean),
                "hours_ago": hours_ago,
                "source":    "Seeking Alpha",
                "url":       link,
            })
    return items


# ── Reuters via Google News RSS ───────────────────────────────────────────────

async def _fetch_reuters(ticker: str, company: str, session: aiohttp.ClientSession) -> list[dict]:
    """
    Google News RSS scoped to reuters.com gives clean, structured Reuters items.
    No API key; respects robots.txt (bots=allowed for /rss/ path).
    """
    q = f"{ticker} {company}".strip().replace(" ", "+")
    url = (
        f"https://news.google.com/rss/search"
        f"?q={q}+site:reuters.com"
        f"&hl=en-US&gl=US&ceid=US:en"
    )
    try:
        async with session.get(url, ssl=_ssl_ctx, headers=_HEADERS, timeout=aiohttp.ClientTimeout(total=15)) as r:
            if r.status != 200:
                log.debug(f"[reuters] {ticker}: HTTP {r.status}")
                return []
            text = await r.text()
    except Exception as e:
        log.debug(f"[reuters] {ticker}: {e}")
        return []

    # Strip namespace declarations so ElementTree can parse without extra handling
    text = re.sub(r'\s+xmlns(?::\w+)?="[^"]+"', "", text)
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        log.debug(f"[reuters] {ticker}: XML parse error: {e}")
        return []

    items: list[dict] = []
    for item in root.findall(".//item")[:8]:
        title   = (item.findtext("title") or "").strip()
        link    = (item.findtext("link")  or "").strip()
        pub     = item.findtext("pubDate") or ""

        # Google News appends " - Reuters" — strip it for clean headlines
        title = re.sub(r"\s*[-–]\s*Reuters\s*$", "", title).strip()
        hours_ago = _hours_since(pub)

        if title and len(title) > 10 and hours_ago < 7 * 24:
            items.append({
                "headline":  title,
                "summary":   title,
                "sentiment": score_sentiment(title),
                "hours_ago": hours_ago,
                "source":    "Reuters",
                "url":       link,
            })
    return items


# ── Finviz (aiohttp → Playwright fallback) ────────────────────────────────────

async def _fetch_finviz(ticker: str) -> list[dict]:
    """
    Finviz news table at /quote.ashx?t={ticker}.
    aiohttp with browser UA works most of the time.
    Playwright is used as a fallback when Finviz returns a CAPTCHA/JS wall.
    """
    url = f"https://finviz.com/quote?t={ticker.upper()}"
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(headers=_HEADERS, connector=connector) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status == 200:
                    html = await r.text()
                    items = _parse_finviz_html(html)
                    if items:
                        log.debug(f"[finviz] {ticker}: {len(items)} items via aiohttp")
                        return items
    except Exception as e:
        log.debug(f"[finviz] aiohttp failed: {e}")

    # Playwright fallback — only invoked if aiohttp returned nothing
    return await _playwright_finviz(ticker, url)


def _parse_finviz_html(html: str) -> list[dict]:
    """
    Parse Finviz's server-rendered news-table HTML.

    Current table structure (as of 2026):
      <tr ... onclick="trackAndOpenNews(event, 'SOURCE', 'URL');">
        <td ...>Today HH:MM(AM|PM)  OR  May-01-25 HH:MM(AM|PM)</td>
        <td ...><div ...><div ...>
          <a class="tab-link-news" href="URL">HEADLINE</a>
    """
    items: list[dict] = []
    now = datetime.now()
    current_date: Optional[datetime] = None

    # Finviz onclick: trackAndOpenNews(event, \'SOURCE\', \'URL\');
    # Split HTML into per-row blocks on the <tr onclick= boundary

    # Split HTML into per-row blocks on the <tr onclick= boundary
    row_blocks = re.split(r'(?=<tr[^>]+onclick="trackAndOpenNews)', html)

    for block in row_blocks[1:]:   # skip everything before the first news row
        # Extract source + url from onclick
        oc = re.search(
            r"""onclick="trackAndOpenNews\(event,\s*'([^']+)',\s*'([^']+)'\)""",
            block,
        )
        if not oc:
            continue
        source, url = oc.group(1).strip(), oc.group(2).strip()

        # Extract date string from first <td>
        dt_m = re.search(
            r"<td[^>]*>\s*((?:Today|\w{3}-\d{1,2}-\d{2})[^<]*?)\s*</td>",
            block,
        )
        date_raw = dt_m.group(1).strip() if dt_m else ""

        # Extract headline from <a class="tab-link-news"...>
        hl_m = re.search(r'<a\s+class="tab-link-news"[^>]*>\s*([^<]+?)\s*</a>', block)
        headline = hl_m.group(1).strip() if hl_m else ""
        if not headline:
            continue

        # Parse the date cell
        if date_raw.startswith("Today"):
            # "Today HH:MMAM/PM" — use today's date
            try:
                time_part = date_raw.replace("Today", "").strip()
                current_date = datetime.now().replace(
                    hour=int(time_part.split(":")[0]),
                    minute=int(time_part[time_part.index(":")+1:time_part.index(":")+3]),
                    second=0, microsecond=0,
                )
            except Exception:
                current_date = datetime.now()
        elif re.match(r"\w{3}-\d{2}-\d{2}", date_raw):
            for fmt in ("%b-%d-%y %I:%M%p", "%b-%d-%y %I:%M %p"):
                try:
                    current_date = datetime.strptime(date_raw, fmt)
                    break
                except ValueError:
                    pass

        hours_ago = max(0, int((now - current_date).total_seconds() / 3600)) if current_date else 48
        if hours_ago > 7 * 24:
            continue

        items.append({
            "headline":  headline,
            "summary":   headline,
            "sentiment": score_sentiment(headline),
            "hours_ago": hours_ago,
            "source":    source or "Finviz",
            "url":       url if url.startswith("http") else f"https://finviz.com{url}",
        })
        if len(items) >= 10:
            break
    return items


def _playwright_finviz_sync(url: str) -> str:
    """
    Out-of-process Playwright scrape using the synchronous API.
    Runs in a ThreadPoolExecutor via asyncio.to_thread() so Chromium never
    blocks the main event loop. Returns raw HTML or "" on failure.
    """
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        return ""
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
                      "--disable-extensions", "--single-process"],
            )
            ctx = browser.new_context(
                user_agent=_HEADERS["User-Agent"],
                viewport={"width": 1280, "height": 800},
                locale="en-US",
            )
            page = ctx.new_page()
            page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,ttf,mp4,mp3}",
                       lambda r: r.abort())
            page.goto(url, wait_until="domcontentloaded", timeout=25_000)
            try:
                page.wait_for_selector("#news-table", timeout=8_000)
            except PWTimeout:
                pass
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        log.debug(f"[finviz playwright_sync] {e}")
        return ""


async def _playwright_finviz(ticker: str, url: str) -> list[dict]:
    """
    Playwright chromium scraper for Finviz — runs in a worker thread so
    Chromium never blocks the asyncio event loop (out-of-process equivalent).
    Optional dependency; silently returns [] if Playwright is not installed.
    """
    try:
        import playwright  # noqa: F401 — just check availability
    except ImportError:
        log.debug("[finviz] playwright not installed — skipping JS fallback")
        return []

    try:
        # Run synchronous Playwright in a thread — keeps event loop free.
        # 30s total wall-clock budget; the sync function itself has a 25s page timeout.
        html = await asyncio.wait_for(
            asyncio.to_thread(_playwright_finviz_sync, url),
            timeout=30.0,
        )
        if not html:
            return []
        items = _parse_finviz_html(html)
        log.debug(f"[finviz playwright] {ticker}: {len(items)} items (threaded)")
        return items
    except asyncio.TimeoutError:
        log.debug(f"[finviz playwright] {ticker}: timed out after 30s")
        return []
    except Exception as e:
        log.debug(f"[finviz playwright] {ticker}: {e}")
        return []


# ── Merge + deduplication ─────────────────────────────────────────────────────

def _headline_words(s: str) -> frozenset:
    """Normalised word-set for overlap-based deduplication."""
    return frozenset(w.lower() for w in re.split(r"\W+", s) if len(w) > 4)


def _merge_dedupe(sources: list[list[dict]]) -> list[dict]:
    merged: list[dict] = []
    seen: list[frozenset] = []
    for item in (i for src in sources for i in src):
        ws = _headline_words(item.get("headline", ""))
        if not ws:
            continue
        if any(len(ws & prev) / max(len(ws), 1) > 0.50 for prev in seen):
            continue  # headline is >50% the same words as something already included
        seen.append(ws)
        merged.append(item)
    merged.sort(key=lambda x: x.get("hours_ago", 9999))
    return merged[:12]


# ── Public entry point ────────────────────────────────────────────────────────

async def get_scraped_news(ticker: str, company: str = "", days: int = 7) -> list[dict]:
    """
    Fetch news from Benzinga RSS, Reuters (via Google News RSS), and Finviz
    concurrently. Returns a merged, deduplicated list sorted newest-first.

    Cached for 20 minutes per ticker. Safe to call on every scan cycle —
    the three sources together take < 2s under normal network conditions.
    """
    cache_key = ticker.upper()
    cached = _CACHE.get(cache_key)
    if cached and time.time() - cached[1] < _TTL:
        return cached[0]

    connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
    async with aiohttp.ClientSession(headers=_HEADERS, connector=connector) as session:
        yahoo, sa, reuters, finviz = await asyncio.gather(
            _fetch_yahoo_finance(ticker, session),
            _fetch_seeking_alpha(ticker, session),
            _fetch_reuters(ticker, company or ticker, session),
            _fetch_finviz(ticker),
            return_exceptions=True,
        )

    yahoo   = yahoo   if isinstance(yahoo,   list) else []
    sa      = sa      if isinstance(sa,      list) else []
    reuters = reuters if isinstance(reuters, list) else []
    finviz  = finviz  if isinstance(finviz,  list) else []

    result = _merge_dedupe([yahoo, sa, reuters, finviz])
    _CACHE[cache_key] = (result, time.time())

    log.info(
        f"[news_scraper] {ticker}: {len(result)} merged items "
        f"(yahoo={len(yahoo)}, seekingalpha={len(sa)}, reuters={len(reuters)}, finviz={len(finviz)})"
    )
    return result


# ── Helper ────────────────────────────────────────────────────────────────────

def _hours_since(date_str: str) -> int:
    """Parse an RFC-2822 pubDate and return hours since publication."""
    if not date_str:
        return 9999
    try:
        pub_dt = parsedate_to_datetime(date_str)
        delta  = datetime.now(pub_dt.tzinfo) - pub_dt
        return max(0, int(delta.total_seconds() / 3600))
    except Exception:
        return 9999
