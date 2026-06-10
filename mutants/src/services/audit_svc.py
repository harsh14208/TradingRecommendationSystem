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
ACTION_BILLING_OVERRIDE = "billing_override"
ACTION_MODEL_PROMOTION = "model_promotion"
ACTION_ACCOUNT_DELETION = "account_deletion"


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_record_action__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_record_action__mutmut)
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


async def x_record_action__mutmut_orig(
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


async def x_record_action__mutmut_1(
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
            None
        )
        await db.flush()
    except Exception as e:  # pragma: no cover - audit must never break the action
        log.warning("audit_svc: failed to record action=%s: %s", action, e)


async def x_record_action__mutmut_2(
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
                user_id=None,
                action=action,
                details=details,
                ip_address=ip_address,
            )
        )
        await db.flush()
    except Exception as e:  # pragma: no cover - audit must never break the action
        log.warning("audit_svc: failed to record action=%s: %s", action, e)


async def x_record_action__mutmut_3(
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
                action=None,
                details=details,
                ip_address=ip_address,
            )
        )
        await db.flush()
    except Exception as e:  # pragma: no cover - audit must never break the action
        log.warning("audit_svc: failed to record action=%s: %s", action, e)


async def x_record_action__mutmut_4(
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
                details=None,
                ip_address=ip_address,
            )
        )
        await db.flush()
    except Exception as e:  # pragma: no cover - audit must never break the action
        log.warning("audit_svc: failed to record action=%s: %s", action, e)


async def x_record_action__mutmut_5(
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
                ip_address=None,
            )
        )
        await db.flush()
    except Exception as e:  # pragma: no cover - audit must never break the action
        log.warning("audit_svc: failed to record action=%s: %s", action, e)


async def x_record_action__mutmut_6(
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
                action=action,
                details=details,
                ip_address=ip_address,
            )
        )
        await db.flush()
    except Exception as e:  # pragma: no cover - audit must never break the action
        log.warning("audit_svc: failed to record action=%s: %s", action, e)


async def x_record_action__mutmut_7(
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
                details=details,
                ip_address=ip_address,
            )
        )
        await db.flush()
    except Exception as e:  # pragma: no cover - audit must never break the action
        log.warning("audit_svc: failed to record action=%s: %s", action, e)


async def x_record_action__mutmut_8(
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
                ip_address=ip_address,
            )
        )
        await db.flush()
    except Exception as e:  # pragma: no cover - audit must never break the action
        log.warning("audit_svc: failed to record action=%s: %s", action, e)


async def x_record_action__mutmut_9(
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
                )
        )
        await db.flush()
    except Exception as e:  # pragma: no cover - audit must never break the action
        log.warning("audit_svc: failed to record action=%s: %s", action, e)


async def x_record_action__mutmut_10(
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
        log.warning(None, action, e)


async def x_record_action__mutmut_11(
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
        log.warning("audit_svc: failed to record action=%s: %s", None, e)


async def x_record_action__mutmut_12(
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
        log.warning("audit_svc: failed to record action=%s: %s", action, None)


async def x_record_action__mutmut_13(
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
        log.warning(action, e)


async def x_record_action__mutmut_14(
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
        log.warning("audit_svc: failed to record action=%s: %s", e)


async def x_record_action__mutmut_15(
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
        log.warning("audit_svc: failed to record action=%s: %s", action, )


async def x_record_action__mutmut_16(
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
        log.warning("XXaudit_svc: failed to record action=%s: %sXX", action, e)


async def x_record_action__mutmut_17(
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
        log.warning("AUDIT_SVC: FAILED TO RECORD ACTION=%S: %S", action, e)

mutants_x_record_action__mutmut['_mutmut_orig'] = x_record_action__mutmut_orig # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_1'] = x_record_action__mutmut_1 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_2'] = x_record_action__mutmut_2 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_3'] = x_record_action__mutmut_3 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_4'] = x_record_action__mutmut_4 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_5'] = x_record_action__mutmut_5 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_6'] = x_record_action__mutmut_6 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_7'] = x_record_action__mutmut_7 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_8'] = x_record_action__mutmut_8 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_9'] = x_record_action__mutmut_9 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_10'] = x_record_action__mutmut_10 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_11'] = x_record_action__mutmut_11 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_12'] = x_record_action__mutmut_12 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_13'] = x_record_action__mutmut_13 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_14'] = x_record_action__mutmut_14 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_15'] = x_record_action__mutmut_15 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_16'] = x_record_action__mutmut_16 # type: ignore # mutmut generated
mutants_x_record_action__mutmut['x_record_action__mutmut_17'] = x_record_action__mutmut_17 # type: ignore # mutmut generated
