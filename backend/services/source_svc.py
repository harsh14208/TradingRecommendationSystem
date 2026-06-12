import inspect
import logging

from fastapi import HTTPException
from models import Source
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("signal.trade.sources")

_DEFAULTS = [
    {
        "id": "yf",
        "name": "Yahoo Finance",
        "abbr": "YAHO",
        "description": "Real-time quotes, fundamentals & financials",
        "is_on": True,
        "latency_ms": 120,
        "feed": "realtime",
    },
    {
        "id": "fh",
        "name": "Finnhub",
        "abbr": "FINN",
        "description": "Company news, insider trades, earnings calendar",
        "is_on": True,
        "latency_ms": 95,
        "feed": "5m",
    },
    {
        "id": "tech",
        "name": "Technical Analysis",
        "abbr": "TECH",
        "description": "RSI, MACD, SMA, ATR, Bollinger Bands",
        "is_on": True,
        "latency_ms": 5,
        "feed": "realtime",
    },
    {
        "id": "ed",
        "name": "SEC EDGAR",
        "abbr": "EDGR",
        "description": "Form 4 insider trades — buys/sells by officers & directors",
        "is_on": True,
        "latency_ms": 400,
        "feed": "1h",
    },
    {
        "id": "fg",
        "name": "Fear & Greed Index",
        "abbr": "F&G",
        "description": "CNN Fear & Greed — composite market-sentiment score 0–100",
        "is_on": True,
        "latency_ms": 80,
        "feed": "1h",
    },
    {
        "id": "macro",
        "name": "Macro (VIX / Rates)",
        "abbr": "MCRO",
        "description": "VIX, 10-Y Treasury yield, S&P 500 trend, FRED Fed rate",
        "is_on": True,
        "latency_ms": 150,
        "feed": "1h",
    },
    {
        "id": "tw",
        "name": "Twitter / X",
        "abbr": "TWIT",
        "description": "Curated financial accounts sentiment",
        "is_on": False,
        "latency_ms": 180,
        "feed": "5m",
    },
    {
        "id": "rd",
        "name": "Reddit WSB",
        "abbr": "RDDT",
        "description": "r/wallstreetbets & r/investing sentiment",
        "is_on": False,
        "latency_ms": 220,
        "feed": "15m",
    },
]


async def seed_sources(db: AsyncSession) -> None:
    existing = {r.id for r in (await db.execute(select(Source))).scalars()}
    for d in _DEFAULTS:
        if d["id"] not in existing:
            db.add(Source(**{k: v for k, v in d.items()}))
    try:
        await db.commit()
    except Exception:
        if inspect.iscoroutinefunction(getattr(db, "rollback", None)):
            await db.rollback()
        raise


async def toggle_source(db: AsyncSession, source_id: str, owner: bool, body: dict | None) -> Source:
    if not owner:
        raise HTTPException(403, detail="Owner access required")
    src = (await db.execute(select(Source).where(Source.id == source_id))).scalar_one_or_none()
    if not src:
        raise HTTPException(404, "Source not found")
    if body and "is_on" in body:
        src.is_on = bool(body["is_on"])
    else:
        src.is_on = not src.is_on
    try:
        await db.commit()
        if inspect.iscoroutinefunction(getattr(db, "refresh", None)):
            await db.refresh(src)
    except Exception:
        if inspect.iscoroutinefunction(getattr(db, "rollback", None)):
            await db.rollback()
        raise
    return src
