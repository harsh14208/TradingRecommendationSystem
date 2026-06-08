"""TSYS-12b: data retention & anonymization rules + enforcement.

Defines per-table retention policy and a `purge_expired` pass that prunes the
high-volume telemetry / log / audit tables by age. Core domain tables (users,
signals) are intentionally NOT auto-deleted here — they carry the product's
track record and require an explicit, separately-audited deletion flow
(see admin account-deletion, TSYS-13d).

`purge_expired` defaults to dry-run: it reports what *would* be removed without
deleting, so an operator can review before enabling enforcement.
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("retention_svc")

# table_name → (retention_days, timestamp_column, anonymize, prunable)
# `prunable` gates auto-deletion; core tables are policy-documented but not pruned.
_DEFAULT_RULES: dict[str, dict] = {
    "provider_response_samples": {"retention_days": 14, "ts": "created_at", "anonymize": False, "prunable": True},
    "provider_telemetry": {"retention_days": 30, "ts": "created_at", "anonymize": False, "prunable": True},
    "incident_timeline": {"retention_days": 90, "ts": "created_at", "anonymize": False, "prunable": True},
    "auth_audit_logs": {"retention_days": 180, "ts": "created_at", "anonymize": False, "prunable": True},
    "action_audit_logs": {"retention_days": 365, "ts": "created_at", "anonymize": False, "prunable": True},
    "outcome_path_snapshots": {"retention_days": 120, "ts": "created_at", "anonymize": False, "prunable": True},
    "outcome_resolver_audits": {"retention_days": 90, "ts": "run_at", "anonymize": False, "prunable": True},
    # Core / regulated — documented, never auto-pruned here.
    "signals": {"retention_days": 3650, "ts": "created_at", "anonymize": False, "prunable": False},
    "signal_deliveries": {"retention_days": 730, "ts": "sent_at", "anonymize": False, "prunable": False},
    "broker_orders": {"retention_days": 2555, "ts": "created_at", "anonymize": False, "prunable": False},
    "users": {"retention_days": 0, "ts": "created_at", "anonymize": True, "prunable": False},
}


# table_name → model, for the prunable tables.
def _model_for(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, attr)
        if isinstance(obj, type) and getattr(obj, "__tablename__", None) == table_name:
            return obj
    return None


def default_rules() -> dict[str, dict]:
    """Return the retention policy registry (copy)."""
    return {k: dict(v) for k, v in _DEFAULT_RULES.items()}


async def seed_default_rules(db: AsyncSession) -> int:
    """Insert any missing DataRetentionRule rows from the defaults. Idempotent."""
    from models import DataRetentionRule

    existing = set((await db.execute(select(DataRetentionRule.table_name))).scalars().all())
    added = 0
    for table_name, rule in _DEFAULT_RULES.items():
        if table_name in existing:
            continue
        db.add(
            DataRetentionRule(
                table_name=table_name,
                retention_days=rule["retention_days"],
                anonymize=rule["anonymize"],
            )
        )
        added += 1
    if added:
        await db.commit()
    return added


async def purge_expired(db: AsyncSession, dry_run: bool = True) -> dict:
    """Count (and, unless dry_run, delete) expired rows in prunable tables.

    Returns {table: {"expired": n, "deleted": n}}.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    report: dict[str, dict] = {}
    for table_name, rule in _DEFAULT_RULES.items():
        if not rule["prunable"]:
            continue
        model = _model_for(table_name)
        if model is None:
            continue
        ts_col = getattr(model, rule["ts"], None)
        if ts_col is None:
            continue
        cutoff = now - timedelta(days=rule["retention_days"])
        expired = (await db.execute(select(func.count()).select_from(model).where(ts_col < cutoff))).scalar() or 0
        deleted = 0
        if expired and not dry_run:
            rows = (await db.execute(select(model).where(ts_col < cutoff))).scalars().all()
            for r in rows:
                await db.delete(r)
            deleted = len(rows)
        report[table_name] = {"expired": expired, "deleted": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report
