"""
Alternative Data: Supply Chain Signals

Data sources (all free / no extra API key required):
  1. Baltic Dry Index (BDI) — Stooq public CSV endpoint
     Leading indicator of raw-materials shipping demand.
  2. Energy demand proxy — Brent crude 20-day momentum via yfinance
  3. Freight proxy — Cass Freight Index (via FRED if key available)
  4. Port congestion — heuristic from BDI divergence vs crude

Sector impact map:
  High BDI + rising → bullish: XLE, XLB, CAT, DE, FCX, SCCO, UPS, FDX
  Low  BDI + falling → bearish: same tickers, plus retail importers (HD, WMT, COST)
  Energy demand spike → bullish: XOM, CVX, SLB, EOG
  Freight contraction → bearish: UPS, FDX, XPO, JBHT

Cached for 4 hours.
"""

import asyncio
import logging
import time

log = logging.getLogger("signal.trade.supply_chain")

_cache: dict = {"result": None, "ts": 0.0}
_TTL = 14400  # 4 hours

# Sector impact mapping
_BDI_BULL_TICKERS = {
    "XLE",
    "XLB",
    "XLI",
    "CAT",
    "DE",
    "FCX",
    "SCCO",
    "UPS",
    "EOG",
    "CVX",
    "XOM",
    "SLB",
    "AEM",
    "NEM",
    "COPX",
}
_BDI_BEAR_TICKERS = {"HD", "WMT", "COST", "TGT", "AMZN", "LOW"}
_ENERGY_BULL = {"XOM", "CVX", "SLB", "EOG", "XLE", "PALL", "GLD"}
_FREIGHT_BEAR = {"UPS", "FDX", "UNP", "CSX", "XPO"}


async def _fetch_bdi() -> dict | None:
    """
    Fetch Baltic Dry Index via yfinance (ticker: ^BDI).
    Returns dict with latest value, 20-day momentum, and 5-day change.
    """
    try:
        from services.market_data import get_history

        df = await get_history("^BDI", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 5:
            return None

        closes = df["Close"].astype(float).dropna().tolist()
        if len(closes) < 5:
            return None

        latest = closes[-1]
        prev5 = closes[-6] if len(closes) >= 6 else closes[0]
        prev20 = closes[-21] if len(closes) >= 21 else closes[0]
        chg_5d = (latest - prev5) / (prev5 or 1) * 100
        chg_20d = (latest - prev20) / (prev20 or 1) * 100

        if chg_20d > 15:
            trend = "strong_bull"
        elif chg_20d > 5:
            trend = "bull"
        elif chg_20d < -15:
            trend = "strong_bear"
        elif chg_20d < -5:
            trend = "bear"
        else:
            trend = "neutral"

        return {
            "value": round(latest, 0),
            "chg_5d": round(chg_5d, 1),
            "chg_20d": round(chg_20d, 1),
            "trend": trend,
            "history": [round(c, 0) for c in closes[-20:]],
        }
    except Exception as e:
        log.debug(f"[supply_chain] BDI (^BDI) fetch failed: {e}")
        return None


async def _fetch_energy_momentum() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def _fetch_freight_fred() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


def _build_sector_signals(bdi: dict | None, energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise BDI + energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── BDI signals ──────────────────────────────────────────────────────────
    if bdi:
        trend = bdi["trend"]
        chg = bdi["chg_20d"]
        if trend in ("strong_bull", "bull"):
            pts = min(8.0, abs(chg) * 0.4)
            for t in _BDI_BULL_TICKERS:
                add(t, +pts, f"BDI +{chg:.0f}% (20d) — shipping demand strong")
            for t in _BDI_BEAR_TICKERS:
                add(t, -pts * 0.5, "BDI rising → import cost headwind for retailers")
        elif trend in ("strong_bear", "bear"):
            pts = min(8.0, abs(chg) * 0.4)
            for t in _BDI_BULL_TICKERS:
                add(t, -pts, f"BDI {chg:.0f}% (20d) — shipping demand contracting")
            for t in _BDI_BEAR_TICKERS:
                add(t, +pts * 0.3, "BDI falling → lower import costs for retailers")

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


async def get_supply_chain_signals() -> dict:
    """
    Public entrypoint. Returns BDI, energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    bdi, energy, freight = await asyncio.gather(
        _fetch_bdi(), _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    bdi = bdi if isinstance(bdi, dict) else None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, bdi, energy, freight)

    result = {
        "bdi": bdi,
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("BDI", bdi), ("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] BDI={bdi['value'] if bdi else 'N/A'} "
        f"energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


def get_supply_chain_score(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −8 to +8 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("sector_signals", []):
        if sig["ticker"] == ticker:
            return sig["score"]
    return 0.0


# ── Supply Chain Graph Propagation ───────────────────────────────────────────
# Supplier → customer lead-lag relationships. When a major supplier reports
# a strong beat / miss, it carries predictive information for downstream customers.
#
# Research basis: semiconductor cycle propagates TSM → NVDA/AMD/QCOM with a 1–4
# week lag; energy costs propagate XOM/CVX → transportation/airlines; steel
# costs propagate SCCO/FCX → auto/construction; cloud capex propagates
# MSFT/AMZN/GOOGL → NVDA/AMD/AMAT (chip demand surge).
#
# Score is applied as a small (+3 to +6 pt) supplemental boost / penalty when
# a top-tier supplier has had a recent signal in the opposite direction.

_SUPPLIER_CUSTOMER_MAP: dict[str, list[str]] = {
    # Semiconductors: foundry → chip designers
    "TSM": ["NVDA", "AMD", "QCOM", "AAPL", "ARM", "MRVL", "AVGO"],
    "AMAT": ["NVDA", "AMD", "INTC", "TSM", "MU", "KLAC", "LRCX"],
    "KLAC": ["TSM", "AMAT", "MU", "NVDA", "SNPS", "CDNS"],
    "LRCX": ["TSM", "MU", "NVDA", "AMD", "AMAT"],
    # Cloud hyperscalers → GPU/infrastructure demand
    "MSFT": ["NVDA", "AMD", "AMAT", "DELL", "HPE"],
    "AMZN": ["NVDA", "AMD", "ARM", "AMAT", "UPS", "FDX"],
    "GOOGL": ["NVDA", "AMD", "ARM", "AMAT"],
    # Energy → transportation/airlines
    "XOM": ["UPS", "UNP", "DAL", "AAL"],
    "CVX": ["UPS", "UNP", "DAL", "AAL"],
    # Steel/copper → auto/construction
    "FCX": ["GM", "F", "CAT", "DE", "HON", "ETN"],
    "SCCO": ["GM", "CAT", "DE", "HON"],
    "WMT": ["UPS", "FDX", "PG", "KO", "PEP"],
}

# Direction of signal propagation (+1 = supplier bull is customer bull, -1 = inverse)
_PROPAGATION_DIRECTION: dict[str, int] = {
    "TSM": +1,
    "AMAT": +1,
    "KLAC": +1,
    "LRCX": +1,
    "MSFT": +1,
    "AMZN": +1,
    "GOOGL": +1,
    "XOM": -1,
    "CVX": -1,  # energy costs → headwind for transportation
    "FCX": -1,
    "SCCO": -1,  # materials costs → headwind for manufacturers
    "WMT": +1,
}


def get_supply_chain_propagation_score(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)
