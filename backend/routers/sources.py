from typing import Optional

from database import get_db
from fastapi import APIRouter, Body, Depends
from models import Source, User
from services.auth_svc import get_current_user
from services.source_svc import seed_sources, toggle_source
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.get("")
async def list_sources(db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    await seed_sources(db)
    rows = (await db.execute(select(Source))).scalars().all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "abbr": r.abbr,
            "description": r.description,
            "is_on": r.is_on,
            "requests_24h": r.requests_24h,
            "latency_ms": r.latency_ms,
            "feed": r.feed,
        }
        for r in rows
    ]


@router.patch("/{source_id}")
@router.put("/{source_id}")
async def toggle_source_endpoint(
    source_id: str,
    body: Optional[dict] = Body(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    src = await toggle_source(db, source_id, user.is_owner, body)
    return {"id": source_id, "is_on": src.is_on}
