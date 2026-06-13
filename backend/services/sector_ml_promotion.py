"""Sector-specific ML model promotion registry (§117).

Blocked sectors (XLF, XLP, XLU, XLI) are hard-blocked by delivery gates and by
``buy_thresh=999`` in ``_SECTOR_MR_CONFIG``.  This module is the single source of
truth for which blocked sectors have earned a QENG-1c promotion and may be
unblocked.

IMPORTANT: a sector is promoted only when there is an explicit, auditable
``ResearchExperiment`` row with ``decision='promoted'`` and
``promotion_status='live'``, linked to an approved ``ModelRegistry`` row.  File
existence is NEVER used as the unblock signal — the v8.1 live leak proved that
pattern is unsafe.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import and_, select

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("sector.ml")

# Must stay in sync with services.delivery_gates.BLOCKED_SECTORS.
BLOCKED_SECTORS: frozenset[str] = frozenset({"XLF", "XLP", "XLU", "XLI"})

# In-memory cache of promoted sectors.  Populated by refresh_promoted_sectors().
# Short TTL because promotion status changes rarely and only via explicit admin
# action, but we still want scans to pick up a new promotion promptly.
_PROMOTED_SECTORS_CACHE: set[str] = set()
_PROMOTED_SECTORS_AT: datetime | None = None
_PROMOTED_SECTORS_TTL_SECONDS = 60


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _sector_from_model_id(model_id: str) -> str | None:
    """Parse sector from ``sector-entry-{SECTOR}-{timestamp}`` model IDs."""
    if not model_id.startswith("sector-entry-"):
        return None
    parts = model_id.split("-")
    if len(parts) < 4:
        return None
    return parts[2].upper()


async def refresh_promoted_sectors(db: AsyncSession) -> set[str]:
    """Return the set of currently promoted blocked sectors.

    Queries the DB each call; callers that want caching should use
    get_cached_promoted_sectors() or pass the result around.
    """
    from models import ModelRegistry, ResearchExperiment

    try:
        stmt = select(ModelRegistry.model_id).where(
            and_(
                ModelRegistry.approval_decision == "approved",
                ModelRegistry.is_active.is_(True),
                ModelRegistry.model_id.like("sector-entry-%"),
            )
        )
        approved_model_ids = {r[0] for r in (await db.execute(stmt)).all()}

        if not approved_model_ids:
            return set()

        # ResearchExperiment links via search_space["model_id"] (JSON).  Filter
        # in Python because JSON member-of semantics vary across SQLite/Postgres.
        exp_stmt = select(ResearchExperiment.search_space).where(
            and_(
                ResearchExperiment.decision == "promoted",
                ResearchExperiment.promotion_status == "live",
            )
        )
        rows = (await db.execute(exp_stmt)).all()
        promoted: set[str] = set()
        for (search_space,) in rows:
            ss = search_space or {}
            model_id = ss.get("model_id") or ""
            if model_id in approved_model_ids:
                sector = _sector_from_model_id(model_id)
                if sector in BLOCKED_SECTORS:
                    promoted.add(sector)
        return promoted
    except Exception:
        log.exception("[sector_ml_promotion] failed to refresh promoted sectors")
        return set()


def get_cached_promoted_sectors() -> set[str]:
    """Return the in-memory cached promoted sectors (may be stale)."""
    return set(_PROMOTED_SECTORS_CACHE)


def cache_promoted_sectors(sectors: set[str]) -> None:
    """Populate the in-memory cache.  Intended for scanner.py once per scan."""
    global _PROMOTED_SECTORS_CACHE, _PROMOTED_SECTORS_AT
    _PROMOTED_SECTORS_CACHE = set(sectors)
    _PROMOTED_SECTORS_AT = _utc_now()


async def get_promoted_sectors_cached(db: AsyncSession, ttl_seconds: int | None = None) -> set[str]:
    """Return promoted sectors, using the in-memory cache if still fresh."""
    global _PROMOTED_SECTORS_CACHE, _PROMOTED_SECTORS_AT
    ttl = ttl_seconds if ttl_seconds is not None else _PROMOTED_SECTORS_TTL_SECONDS
    if _PROMOTED_SECTORS_AT is not None:
        age = (_utc_now() - _PROMOTED_SECTORS_AT).total_seconds()
        if age < ttl:
            return set(_PROMOTED_SECTORS_CACHE)
    sectors = await refresh_promoted_sectors(db)
    cache_promoted_sectors(sectors)
    return sectors


def is_sector_promoted(sector: str | None, promoted_sectors: set[str] | None = None) -> bool:
    """Return True if ``sector`` is in the promoted set.

    If ``promoted_sectors`` is None, falls back to the in-memory cache.
    """
    if not sector:
        return False
    _ps = promoted_sectors if promoted_sectors is not None else _PROMOTED_SECTORS_CACHE
    return sector.upper() in _ps


def effective_sector_buy_thresh(
    sector: str | None,
    base_config: dict,
    promoted_sectors: set[str] | None = None,
) -> int | None:
    """Return the effective buy_thresh for a sector.

    Blocked sectors keep ``buy_thresh=999`` unless explicitly promoted, in which
    case the sector is treated like an active sector (``buy_thresh=None``,
    meaning the global BUY_THRESH applies).
    """
    if not sector:
        return base_config.get("buy_thresh")
    if is_sector_promoted(sector, promoted_sectors):
        return None
    return base_config.get("buy_thresh")


def effective_sector_config(
    sector: str | None,
    base_config: dict,
    promoted_sectors: set[str] | None = None,
) -> dict:
    """Return a copy of the sector MR config with buy_thresh overridden if promoted."""
    cfg = dict(base_config)
    cfg["buy_thresh"] = effective_sector_buy_thresh(sector, base_config, promoted_sectors)
    return cfg
