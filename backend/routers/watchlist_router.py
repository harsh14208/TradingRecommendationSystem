import re

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import Signal, User, WatchlistItem
from pydantic import BaseModel, field_validator
from services.auth_svc import get_current_user
from services.market_data import get_quotes_batch
from sqlalchemy import func, select
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


def _row(r: WatchlistItem, quote: dict | None, sig_count: int = 0) -> dict:
    return {
        "ticker": r.ticker,
        "company": r.company or r.ticker,
        "is_active": r.is_active,
        "price": quote.get("p") if quote else None,
        "change": quote.get("c") if quote else None,
        "sigs": sig_count,
        "alert": sig_count > 0,
    }


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

    tickers = [r.ticker for r in rows]
    quotes = {}
    if tickers:
        try:
            quotes = {q.get("t", "").upper(): q for q in await get_quotes_batch(tickers) if q.get("t")}
        except Exception:
            quotes = {}

    sig_counts: dict[str, int] = {}
    if tickers:
        try:
            sig_rows = (
                await db.execute(
                    select(Signal.ticker, func.count(Signal.id))
                    .where(Signal.ticker.in_(tickers))
                    .where(Signal.is_active == True)
                    .where(Signal.created_at >= func.datetime("now", "-1 day"))
                    .group_by(Signal.ticker)
                )
            ).all()
            sig_counts = {r.ticker: r[1] for r in sig_rows}
        except Exception:
            sig_counts = {}

    return [_row(r, quotes.get(r.ticker), sig_counts.get(r.ticker, 0)) for r in rows]


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
