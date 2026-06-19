"""TSYS-13c: immutable audit trail for safety-critical admin/user actions.

`record_action` appends an ActionAuditLog row. It is best-effort and never
raises — an audit-write failure must not break the action being audited. The
table is append-only by convention (no update/delete code paths).
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("audit_svc")

# Canonical action names — keep these stable so the trail is queryable.
ACTION_KILL_SWITCH = "kill_switch_toggle"
ACTION_BROKER_CONNECT = "broker_connect"
ACTION_BROKER_DISCONNECT = "broker_disconnect"
ACTION_RISK_ACK = "risk_acknowledged"
ACTION_OPTIONS_RISK_ACK = "options_risk_acknowledged"
ACTION_OPTIONS_SETTINGS = "options_settings_changed"
ACTION_BILLING_OVERRIDE = "billing_override"
ACTION_MODEL_PROMOTION = "model_promotion"
ACTION_ACCOUNT_DELETION = "account_deletion"


async def record_action(
    db: AsyncSession,
    action: str,
    *,
    user_id: Optional[int] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Append an immutable audit record. Caller is responsible for the commit
    (so the audit row shares the action's transaction); flushes best-effort."""
    from models import ActionAuditLog

    try:
        db.add(
            ActionAuditLog(
                user_id=user_id,
                action=action,
                details=details,
                ip_address=ip_address,
            )
        )
        await db.flush()
    except Exception as e:  # pragma: no cover - audit must never break the action
        log.warning("audit_svc: failed to record action=%s: %s", action, e)
