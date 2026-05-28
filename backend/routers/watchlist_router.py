import re

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import User, WatchlistItem
from pydantic import BaseModel, field_validator
from services.auth_svc import get_current_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])

_TICKER_RE = re.compile(r"^[A-Z]{1,5}$")


class TickerBody(BaseModel):
    ticker: str
    company: str = ""

    @field_validator("ticker")
    @classmethod
    def ticker_format(cls, v: str) -> str:
        v = v.strip().upper()
        if not _TICKER_RE.match(v):
            raise ValueError("Ticker must be 1–5 uppercase letters (e.g. AAPL)")
        return v


def _row(r: WatchlistItem) -> dict:
    return {"ticker": r.ticker, "company": r.company or r.ticker, "is_active": r.is_active}


@router.get("")
async def list_watchlist(db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    rows = (
        (await db.execute(select(WatchlistItem).where(WatchlistItem.is_active == True).order_by(WatchlistItem.ticker)))
        .scalars()
        .all()
    )
    if not rows:
        # Seed from config defaults on first call
        from config import get_settings

        settings = get_settings()
        for t in settings.tickers:
            db.add(WatchlistItem(ticker=t, company=t))
        await db.commit()
        rows = (
            (
                await db.execute(
                    select(WatchlistItem).where(WatchlistItem.is_active == True).order_by(WatchlistItem.ticker)
                )
            )
            .scalars()
            .all()
        )
    return [_row(r) for r in rows]


@router.post("")
async def add_ticker(body: TickerBody, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    ticker = body.ticker.strip().upper()
    if not ticker:
        raise HTTPException(400, "ticker required")
    existing = (await db.execute(select(WatchlistItem).where(WatchlistItem.ticker == ticker))).scalar_one_or_none()
    if existing:
        existing.is_active = True
        existing.company = body.company or existing.company or ticker
        await db.commit()
        return {"success": True, "ticker": ticker}
    db.add(WatchlistItem(ticker=ticker, company=body.company or ticker))
    await db.commit()
    return {"success": True, "ticker": ticker}


@router.delete("/{ticker}")
async def remove_ticker(ticker: str, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    item = (await db.execute(select(WatchlistItem).where(WatchlistItem.ticker == ticker.upper()))).scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Ticker not found in watchlist")
    item.is_active = False
    await db.commit()
    return {"success": True}
