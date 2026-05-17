from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from models import Source, User
from services.auth_svc import get_current_user

router = APIRouter(prefix="/api/sources", tags=["sources"])

_DEFAULTS = [
    {"id": "yf",   "name": "Yahoo Finance",      "abbr": "YAHO", "description": "Real-time quotes, fundamentals & financials",               "is_on": True,  "latency_ms": 120, "feed": "realtime"},
    {"id": "fh",   "name": "Finnhub",             "abbr": "FINN", "description": "Company news, insider trades, earnings calendar",           "is_on": True,  "latency_ms": 95,  "feed": "5m"},
    {"id": "tech", "name": "Technical Analysis",  "abbr": "TECH", "description": "RSI, MACD, SMA, ATR, Bollinger Bands",                     "is_on": True,  "latency_ms": 5,   "feed": "realtime"},
    {"id": "ed",   "name": "SEC EDGAR",           "abbr": "EDGR", "description": "Form 4 insider trades — buys/sells by officers & directors","is_on": True,  "latency_ms": 400, "feed": "1h"},
    {"id": "fg",   "name": "Fear & Greed Index",  "abbr": "F&G",  "description": "CNN Fear & Greed — composite market-sentiment score 0–100", "is_on": True,  "latency_ms": 80,  "feed": "1h"},
    {"id": "macro","name": "Macro (VIX / Rates)", "abbr": "MCRO", "description": "VIX, 10-Y Treasury yield, S&P 500 trend, FRED Fed rate",    "is_on": True,  "latency_ms": 150, "feed": "1h"},
    {"id": "tw",   "name": "Twitter / X",         "abbr": "TWIT", "description": "Curated financial accounts sentiment",                      "is_on": False, "latency_ms": 180, "feed": "5m"},
    {"id": "rd",   "name": "Reddit WSB",          "abbr": "RDDT", "description": "r/wallstreetbets & r/investing sentiment",                  "is_on": False, "latency_ms": 220, "feed": "15m"},
]


async def _seed(db: AsyncSession):
    existing = {r.id for r in (await db.execute(select(Source))).scalars()}
    for d in _DEFAULTS:
        if d["id"] not in existing:
            db.add(Source(**{k: v for k, v in d.items()}))
    await db.commit()


@router.get("")
async def list_sources(db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    await _seed(db)
    rows = (await db.execute(select(Source))).scalars().all()
    return [
        {"id": r.id, "name": r.name, "abbr": r.abbr, "description": r.description,
         "is_on": r.is_on, "requests_24h": r.requests_24h, "latency_ms": r.latency_ms, "feed": r.feed}
        for r in rows
    ]


@router.patch("/{source_id}")
@router.put("/{source_id}")
async def toggle_source(source_id: str, body: Optional[dict] = Body(default=None), db: AsyncSession = Depends(get_db)):
    src = (await db.execute(select(Source).where(Source.id == source_id))).scalar_one_or_none()
    if not src:
        raise HTTPException(404, "Source not found")
    # Accept explicit is_on from body, or just toggle current state
    if body and "is_on" in body:
        src.is_on = bool(body["is_on"])
    else:
        src.is_on = not src.is_on
    await db.commit()
    return {"id": source_id, "is_on": src.is_on}
