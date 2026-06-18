"""Lightweight frontend analytics sink.

Accepts small JSON events from the browser (CTA clicks, feature-gate impressions,
etc.) and appends them to a daily JSONL log. No third-party trackers, no PII
beyond the authenticated user_id.
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import os
from datetime import datetime, timezone
from typing import Any

from config import get_settings
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field, field_validator
from services.auth_svc import get_current_user_optional

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

_log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(_log_dir, exist_ok=True)
_analytics_logger = logging.getLogger("analytics")
_analytics_logger.setLevel(logging.INFO)
# Avoid propagating to root logger; we only want the file handler.
_analytics_logger.propagate = False

_file_handler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(_log_dir, "analytics.jsonl"),
    when="midnight",
    interval=1,
    utc=True,
    backupCount=30,
)
_file_handler.setFormatter(logging.Formatter("%(message)s"))
if not _analytics_logger.handlers:
    _analytics_logger.addHandler(_file_handler)


class AnalyticsEvent(BaseModel):
    event: str = Field(..., min_length=1, max_length=64)
    properties: dict[str, Any] = Field(default_factory=dict)
    path: str = Field(default="", max_length=512)
    ts: str | None = Field(default=None, max_length=32)
    session_id: str | None = Field(default=None, max_length=64)

    @field_validator("event")
    @classmethod
    def _event_chars(cls, v: str) -> str:
        if not v.replace("_", "").replace(".", "").replace("-", "").isalnum():
            raise ValueError("event must be alphanumeric with _.-")
        return v


@router.post("/event")
async def record_event(
    req: Request,
    body: AnalyticsEvent,
    user=Depends(get_current_user_optional),
):
    settings = get_settings()
    if not settings.analytics_enabled:
        return {"ok": True}

    row = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "user_id": getattr(user, "id", None),
        "event": body.event,
        "properties": body.properties,
        "path": body.path,
        "client_ts": body.ts,
        "session_id": body.session_id,
        "ip": _client_ip(req),
        "ua": req.headers.get("user-agent", "")[:256],
    }
    _analytics_logger.info(json.dumps(row, separators=(",", ":"), default=str))
    return {"ok": True}


def _client_ip(req: Request) -> str:
    forwarded = req.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()[:64]
    return req.client.host if req.client else ""
