"""
Custom screener builder — save named filter presets and evaluate them against
the live signal feed.

Each preset is a JSON array of filter rules stored in app_settings["screeners"].

Filter rule schema:
  { "field": str, "op": str, "value": any }

Supported fields:
  confidence, sentiment, action, style, rr, n_sources, ticker,
  has_source (value = source name string)

Supported ops:
  gt, gte, lt, lte, eq, neq, contains, in
"""
from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import AppSettings, Signal, User
from services.auth_svc import get_current_user

router = APIRouter(prefix="/api/screener", tags=["screener"])

# ── Pydantic models ────────────────────────────────────────────────────────────

_ALLOWED_FIELDS = {
    "confidence", "sentiment", "action", "style", "rr",
    "n_sources", "ticker", "has_source",
}
_ALLOWED_OPS = {"gt", "gte", "lt", "lte", "eq", "neq", "contains", "in"}
_ALLOWED_ACTIONS = {"BUY", "SELL", "HOLD"}
_ALLOWED_STYLES  = {"swing", "position"}
_NAME_RE = re.compile(r'^[\w\s\-]{1,40}$')


class FilterRule(BaseModel):
    field: str
    op: str
    value: Any

    @field_validator("field")
    @classmethod
    def field_allowed(cls, v: str) -> str:
        if v not in _ALLOWED_FIELDS:
            raise ValueError(f"field must be one of {_ALLOWED_FIELDS}")
        return v

    @field_validator("op")
    @classmethod
    def op_allowed(cls, v: str) -> str:
        if v not in _ALLOWED_OPS:
            raise ValueError(f"op must be one of {_ALLOWED_OPS}")
        return v


class ScreenerPreset(BaseModel):
    name: str
    rules: list[FilterRule]

    @field_validator("name")
    @classmethod
    def name_format(cls, v: str) -> str:
        v = v.strip()
        if not _NAME_RE.match(v):
            raise ValueError("Name must be 1–40 alphanumeric/space/dash characters")
        return v

    @field_validator("rules")
    @classmethod
    def rules_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("Screener must have at least one rule")
        if len(v) > 20:
            raise ValueError("Maximum 20 rules per screener")
        return v


# ── Rule evaluation ────────────────────────────────────────────────────────────

def _rr_numeric(sig: dict) -> float:
    try:
        return float(str(sig.get("rr", "0")).replace(":", ""))
    except (ValueError, TypeError):
        return 0.0


def _evaluate_rule(sig: dict, rule: FilterRule) -> bool:
    """Return True if signal passes the rule."""
    field, op, value = rule.field, rule.op, rule.value

    if field == "confidence":
        actual = float(sig.get("confidence") or 0)
    elif field == "sentiment":
        actual = float(sig.get("sentiment") or 0)
    elif field == "rr":
        actual = _rr_numeric(sig)
    elif field == "n_sources":
        actual = len(sig.get("sources") or [])
    elif field == "action":
        actual = (sig.get("action") or "").upper()
    elif field == "style":
        actual = (sig.get("style") or "").lower()
    elif field == "ticker":
        actual = (sig.get("ticker") or "").upper()
    elif field == "has_source":
        # value is a source name; passes if that source is in the sources list
        sources = [s.lower() for s in (sig.get("sources") or [])]
        return str(value).lower() in sources
    else:
        return False

    try:
        if op == "gt":      return actual > value
        if op == "gte":     return actual >= value
        if op == "lt":      return actual < value
        if op == "lte":     return actual <= value
        if op == "eq":      return actual == value
        if op == "neq":     return actual != value
        if op == "contains":return str(value).lower() in str(actual).lower()
        if op == "in":      return actual in (value if isinstance(value, list) else [value])
    except (TypeError, ValueError):
        return False
    return False


def apply_screener(signals: list[dict], rules: list[FilterRule]) -> list[dict]:
    """Return signals that pass ALL rules (AND logic)."""
    return [s for s in signals if all(_evaluate_rule(s, r) for r in rules)]


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _load_screeners(db: AsyncSession) -> dict[str, list]:
    row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    return (row.data or {}).get("screeners", {}) if row else {}


async def _save_screeners(db: AsyncSession, screeners: dict[str, list]) -> None:
    row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    if row is None:
        db.add(AppSettings(id=1, data={"screeners": screeners}))
    else:
        data = dict(row.data or {})
        data["screeners"] = screeners
        row.data = data
    await db.commit()


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("")
async def list_screeners(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """List all saved screener presets."""
    screeners = await _load_screeners(db)
    return [{"name": name, "rules": rules} for name, rules in screeners.items()]


@router.post("")
async def create_screener(
    preset: ScreenerPreset,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Create or replace a named screener preset."""
    screeners = await _load_screeners(db)
    if len(screeners) >= 20 and preset.name not in screeners:
        raise HTTPException(400, "Maximum 20 screeners per account")
    screeners[preset.name] = [r.model_dump() for r in preset.rules]
    await _save_screeners(db, screeners)
    return {"name": preset.name, "rules": screeners[preset.name]}


@router.delete("/{name}")
async def delete_screener(
    name: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Delete a screener preset by name."""
    screeners = await _load_screeners(db)
    if name not in screeners:
        raise HTTPException(404, "Screener not found")
    del screeners[name]
    await _save_screeners(db, screeners)
    return {"deleted": name}


@router.get("/{name}/run")
async def run_screener(
    name: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Run a saved screener against current active signals. Returns matching signals."""
    screeners = await _load_screeners(db)
    if name not in screeners:
        raise HTTPException(404, "Screener not found")

    rules = [FilterRule(**r) for r in screeners[name]]

    # Fetch all active signals
    rows = (await db.execute(
        select(Signal)
        .where(Signal.is_active == True)
        .order_by(Signal.confidence.desc())
        .limit(500)
    )).scalars().all()

    import json as _json
    signals = []
    for row in rows:
        sig = {
            "id":         row.id,
            "ticker":     row.ticker,
            "action":     row.action,
            "confidence": row.confidence,
            "sentiment":  row.sentiment,
            "style":      row.style,
            "rr":         row.rr,
            "price":      row.price,
            "sources":    row.sources if isinstance(row.sources, list) else
                          (_json.loads(row.sources) if row.sources else []),
            "headline":   row.headline,
            "ts":         row.created_at.isoformat() + "Z" if row.created_at else None,
        }
        signals.append(sig)

    matched = apply_screener(signals, rules)
    return {"name": name, "matched": len(matched), "signals": matched}


@router.post("/preview")
async def preview_screener(
    preset: ScreenerPreset,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """
    Evaluate an unsaved screener against live signals without persisting it.
    Useful for building/testing a screener in the UI before saving.
    """
    rules = preset.rules

    rows = (await db.execute(
        select(Signal)
        .where(Signal.is_active == True)
        .order_by(Signal.confidence.desc())
        .limit(500)
    )).scalars().all()

    import json as _json
    signals = []
    for row in rows:
        sig = {
            "id":         row.id,
            "ticker":     row.ticker,
            "action":     row.action,
            "confidence": row.confidence,
            "sentiment":  row.sentiment,
            "style":      row.style,
            "rr":         row.rr,
            "price":      row.price,
            "sources":    row.sources if isinstance(row.sources, list) else
                          (_json.loads(row.sources) if row.sources else []),
            "headline":   row.headline,
            "ts":         row.created_at.isoformat() + "Z" if row.created_at else None,
        }
        signals.append(sig)

    matched = apply_screener(signals, rules)
    return {"matched": len(matched), "signals": matched}
