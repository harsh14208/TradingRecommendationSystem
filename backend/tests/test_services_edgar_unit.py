"""Unit tests for services/edgar.py — pure helper functions."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import xml.etree.ElementTree as ET


# ── _parse_form4 ──────────────────────────────────────────────────────────────

def _make_form4_xml(transactions):
    """Build a minimal Form 4 XML."""
    root = ET.Element("ownershipDocument")
    for code, shares, price in transactions:
        t = ET.SubElement(root, "nonDerivativeTransaction")
        code_el = ET.SubElement(t, "transactionAcquiredDisposedCode")
        ET.SubElement(code_el, "value").text = code
        shares_el = ET.SubElement(t, "transactionShares")
        ET.SubElement(shares_el, "value").text = str(shares)
        price_el = ET.SubElement(t, "transactionPricePerShare")
        ET.SubElement(price_el, "value").text = str(price)
    return ET.tostring(root, encoding="unicode")


def test_parse_form4_buy():
    from services.edgar import _parse_form4
    xml = _make_form4_xml([("A", 1000, 150.0)])
    buys, sells, buy_val, sell_val = _parse_form4(xml)
    assert buys == 1000
    assert sells == 0
    assert buy_val == pytest.approx(150000.0)
    assert sell_val == 0.0


def test_parse_form4_sell():
    from services.edgar import _parse_form4
    xml = _make_form4_xml([("D", 500, 200.0)])
    buys, sells, buy_val, sell_val = _parse_form4(xml)
    assert buys == 0
    assert sells == 500
    assert sell_val == pytest.approx(100000.0)


def test_parse_form4_mixed():
    from services.edgar import _parse_form4
    xml = _make_form4_xml([("A", 1000, 150.0), ("D", 200, 160.0)])
    buys, sells, buy_val, sell_val = _parse_form4(xml)
    assert buys == 1000
    assert sells == 200


def test_parse_form4_empty():
    from services.edgar import _parse_form4
    xml = "<ownershipDocument></ownershipDocument>"
    buys, sells, buy_val, sell_val = _parse_form4(xml)
    assert buys == 0
    assert sells == 0
    assert buy_val == 0.0
    assert sell_val == 0.0


def test_parse_form4_invalid_xml():
    from services.edgar import _parse_form4
    buys, sells, buy_val, sell_val = _parse_form4("NOT XML <<<")
    assert buys == 0
    assert sells == 0


def test_parse_form4_no_price():
    from services.edgar import _parse_form4
    xml = _make_form4_xml([("A", 500, 0)])
    buys, sells, buy_val, sell_val = _parse_form4(xml)
    assert buys == 500
    assert buy_val == 0.0


# ── _extract_mda_section ──────────────────────────────────────────────────────

def test_extract_mda_section_found():
    from services.edgar import _extract_mda_section
    text = (
        "Some header\n"
        "Management Discussion and Analysis\n"
        + ("Risk factors detailed discussion " * 100)
        + "\nItem 3 Quantitative and Qualitative\n"
        "more content"
    )
    result = _extract_mda_section(text)
    assert isinstance(result, str)
    assert len(result) > 0


def test_extract_mda_section_fallback():
    from services.edgar import _extract_mda_section
    # No MD&A pattern → fallback to middle section
    text = "a" * 24000
    result = _extract_mda_section(text)
    assert isinstance(result, str)
    assert len(result) == 8000


def test_extract_mda_section_empty():
    from services.edgar import _extract_mda_section
    result = _extract_mda_section("")
    assert isinstance(result, str)


def test_extract_mda_section_short():
    from services.edgar import _extract_mda_section
    result = _extract_mda_section("short text")
    assert isinstance(result, str)


# ── _score_mda_delta ──────────────────────────────────────────────────────────

def test_score_mda_delta_neutral():
    from services.edgar import _score_mda_delta
    score, reason = _score_mda_delta("revenue growth strong", "revenue growth strong")
    # Identical text → no change
    assert score == 0.0


def test_score_mda_delta_negative_risks():
    from services.edgar import _score_mda_delta
    current = "risk uncertainty challenges volatility adverse difficult"
    previous = "revenue growth strong"
    score, reason = _score_mda_delta(current, previous)
    assert score <= 0


def test_score_mda_delta_positive_new():
    from services.edgar import _score_mda_delta
    current = "growth revenue profit expanding opportunity strong"
    previous = "some text"
    score, reason = _score_mda_delta(current, previous)
    assert isinstance(score, float)
    assert isinstance(reason, str)


def test_score_mda_delta_clamped():
    from services.edgar import _score_mda_delta
    # Extreme negative
    current = ("risk risk risk adverse adverse adverse uncertainty uncertainty "
               "challenges headwind difficult deteriorate decline impair "
               "volatility volatility risk risk risk adverse") * 10
    previous = "revenue growth"
    score, reason = _score_mda_delta(current, previous)
    assert score >= -8.0


def test_score_mda_delta_returns_tuple():
    from services.edgar import _score_mda_delta
    result = _score_mda_delta("text a", "text b")
    assert isinstance(result, tuple)
    assert len(result) == 2


# ── get_mda_delta (cache path) ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_mda_delta_unknown_ticker():
    from services.edgar import get_mda_delta
    # Unknown ticker (not in _KNOWN_CIKS) → returns {}
    result = await get_mda_delta("ZZZUNKNOWN")
    assert result == {}


@pytest.mark.asyncio
async def test_get_mda_delta_cache_hit():
    import services.edgar as ed
    import time
    ed._mda_cache["AAPL"] = ({"score": 2.0, "reason": "cached"}, time.time())
    from services.edgar import get_mda_delta
    result = await get_mda_delta("AAPL")
    assert result["score"] == 2.0
    del ed._mda_cache["AAPL"]


# ── get_insider_activity cache ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_insider_activity_cache_hit():
    import services.edgar as ed
    import time
    data = {"buys": 5, "sells": 1, "score": 3.0}
    ed._activity_cache["MSFT"] = (data, time.time())
    from services.edgar import get_insider_activity
    result = await get_insider_activity("MSFT")
    assert result["buys"] == 5
    del ed._activity_cache["MSFT"]


@pytest.mark.asyncio
async def test_get_insider_activity_no_cik():
    from services.edgar import get_insider_activity
    with patch("services.edgar._get_cik", new_callable=AsyncMock, return_value=None):
        result = await get_insider_activity("UNKNOWN_TICKER_XYZ")
    assert result is None
