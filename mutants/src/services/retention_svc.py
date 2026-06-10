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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__model_for__mutmut: MutantDict = {}  # type: ignore


# table_name → model, for the prunable tables.
@_mutmut_mutated(mutants_x__model_for__mutmut)
def _model_for(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, attr)
        if isinstance(obj, type) and getattr(obj, "__tablename__", None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_orig(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, attr)
        if isinstance(obj, type) and getattr(obj, "__tablename__", None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_1(table_name: str):
    import models

    for attr in dir(None):
        obj = getattr(models, attr)
        if isinstance(obj, type) and getattr(obj, "__tablename__", None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_2(table_name: str):
    import models

    for attr in dir(models):
        obj = None
        if isinstance(obj, type) and getattr(obj, "__tablename__", None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_3(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(None, attr)
        if isinstance(obj, type) and getattr(obj, "__tablename__", None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_4(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, None)
        if isinstance(obj, type) and getattr(obj, "__tablename__", None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_5(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(attr)
        if isinstance(obj, type) and getattr(obj, "__tablename__", None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_6(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, )
        if isinstance(obj, type) and getattr(obj, "__tablename__", None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_7(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, attr)
        if isinstance(obj, type) or getattr(obj, "__tablename__", None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_8(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, attr)
        if isinstance(obj, type) and getattr(None, "__tablename__", None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_9(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, attr)
        if isinstance(obj, type) and getattr(obj, None, None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_10(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, attr)
        if isinstance(obj, type) and getattr("__tablename__", None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_11(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, attr)
        if isinstance(obj, type) and getattr(obj, None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_12(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, attr)
        if isinstance(obj, type) and getattr(obj, "__tablename__", ) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_13(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, attr)
        if isinstance(obj, type) and getattr(obj, "XX__tablename__XX", None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_14(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, attr)
        if isinstance(obj, type) and getattr(obj, "__TABLENAME__", None) == table_name:
            return obj
    return None


# table_name → model, for the prunable tables.
def x__model_for__mutmut_15(table_name: str):
    import models

    for attr in dir(models):
        obj = getattr(models, attr)
        if isinstance(obj, type) and getattr(obj, "__tablename__", None) != table_name:
            return obj
    return None

mutants_x__model_for__mutmut['_mutmut_orig'] = x__model_for__mutmut_orig # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_1'] = x__model_for__mutmut_1 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_2'] = x__model_for__mutmut_2 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_3'] = x__model_for__mutmut_3 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_4'] = x__model_for__mutmut_4 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_5'] = x__model_for__mutmut_5 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_6'] = x__model_for__mutmut_6 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_7'] = x__model_for__mutmut_7 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_8'] = x__model_for__mutmut_8 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_9'] = x__model_for__mutmut_9 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_10'] = x__model_for__mutmut_10 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_11'] = x__model_for__mutmut_11 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_12'] = x__model_for__mutmut_12 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_13'] = x__model_for__mutmut_13 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_14'] = x__model_for__mutmut_14 # type: ignore # mutmut generated
mutants_x__model_for__mutmut['x__model_for__mutmut_15'] = x__model_for__mutmut_15 # type: ignore # mutmut generated
mutants_x_default_rules__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_default_rules__mutmut)
def default_rules() -> dict[str, dict]:
    """Return the retention policy registry (copy)."""
    return {k: dict(v) for k, v in _DEFAULT_RULES.items()}


def x_default_rules__mutmut_orig() -> dict[str, dict]:
    """Return the retention policy registry (copy)."""
    return {k: dict(v) for k, v in _DEFAULT_RULES.items()}


def x_default_rules__mutmut_1() -> dict[str, dict]:
    """Return the retention policy registry (copy)."""
    return {k: dict(None) for k, v in _DEFAULT_RULES.items()}

mutants_x_default_rules__mutmut['_mutmut_orig'] = x_default_rules__mutmut_orig # type: ignore # mutmut generated
mutants_x_default_rules__mutmut['x_default_rules__mutmut_1'] = x_default_rules__mutmut_1 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_seed_default_rules__mutmut)
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


async def x_seed_default_rules__mutmut_orig(db: AsyncSession) -> int:
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


async def x_seed_default_rules__mutmut_1(db: AsyncSession) -> int:
    """Insert any missing DataRetentionRule rows from the defaults. Idempotent."""
    from models import DataRetentionRule

    existing = None
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


async def x_seed_default_rules__mutmut_2(db: AsyncSession) -> int:
    """Insert any missing DataRetentionRule rows from the defaults. Idempotent."""
    from models import DataRetentionRule

    existing = set(None)
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


async def x_seed_default_rules__mutmut_3(db: AsyncSession) -> int:
    """Insert any missing DataRetentionRule rows from the defaults. Idempotent."""
    from models import DataRetentionRule

    existing = set((await db.execute(None)).scalars().all())
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


async def x_seed_default_rules__mutmut_4(db: AsyncSession) -> int:
    """Insert any missing DataRetentionRule rows from the defaults. Idempotent."""
    from models import DataRetentionRule

    existing = set((await db.execute(select(None))).scalars().all())
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


async def x_seed_default_rules__mutmut_5(db: AsyncSession) -> int:
    """Insert any missing DataRetentionRule rows from the defaults. Idempotent."""
    from models import DataRetentionRule

    existing = set((await db.execute(select(DataRetentionRule.table_name))).scalars().all())
    added = None
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


async def x_seed_default_rules__mutmut_6(db: AsyncSession) -> int:
    """Insert any missing DataRetentionRule rows from the defaults. Idempotent."""
    from models import DataRetentionRule

    existing = set((await db.execute(select(DataRetentionRule.table_name))).scalars().all())
    added = 1
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


async def x_seed_default_rules__mutmut_7(db: AsyncSession) -> int:
    """Insert any missing DataRetentionRule rows from the defaults. Idempotent."""
    from models import DataRetentionRule

    existing = set((await db.execute(select(DataRetentionRule.table_name))).scalars().all())
    added = 0
    for table_name, rule in _DEFAULT_RULES.items():
        if table_name not in existing:
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


async def x_seed_default_rules__mutmut_8(db: AsyncSession) -> int:
    """Insert any missing DataRetentionRule rows from the defaults. Idempotent."""
    from models import DataRetentionRule

    existing = set((await db.execute(select(DataRetentionRule.table_name))).scalars().all())
    added = 0
    for table_name, rule in _DEFAULT_RULES.items():
        if table_name in existing:
            break
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


async def x_seed_default_rules__mutmut_9(db: AsyncSession) -> int:
    """Insert any missing DataRetentionRule rows from the defaults. Idempotent."""
    from models import DataRetentionRule

    existing = set((await db.execute(select(DataRetentionRule.table_name))).scalars().all())
    added = 0
    for table_name, rule in _DEFAULT_RULES.items():
        if table_name in existing:
            continue
        db.add(
            None
        )
        added += 1
    if added:
        await db.commit()
    return added


async def x_seed_default_rules__mutmut_10(db: AsyncSession) -> int:
    """Insert any missing DataRetentionRule rows from the defaults. Idempotent."""
    from models import DataRetentionRule

    existing = set((await db.execute(select(DataRetentionRule.table_name))).scalars().all())
    added = 0
    for table_name, rule in _DEFAULT_RULES.items():
        if table_name in existing:
            continue
        db.add(
            DataRetentionRule(
                table_name=None,
                retention_days=rule["retention_days"],
                anonymize=rule["anonymize"],
            )
        )
        added += 1
    if added:
        await db.commit()
    return added


async def x_seed_default_rules__mutmut_11(db: AsyncSession) -> int:
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
                retention_days=None,
                anonymize=rule["anonymize"],
            )
        )
        added += 1
    if added:
        await db.commit()
    return added


async def x_seed_default_rules__mutmut_12(db: AsyncSession) -> int:
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
                anonymize=None,
            )
        )
        added += 1
    if added:
        await db.commit()
    return added


async def x_seed_default_rules__mutmut_13(db: AsyncSession) -> int:
    """Insert any missing DataRetentionRule rows from the defaults. Idempotent."""
    from models import DataRetentionRule

    existing = set((await db.execute(select(DataRetentionRule.table_name))).scalars().all())
    added = 0
    for table_name, rule in _DEFAULT_RULES.items():
        if table_name in existing:
            continue
        db.add(
            DataRetentionRule(
                retention_days=rule["retention_days"],
                anonymize=rule["anonymize"],
            )
        )
        added += 1
    if added:
        await db.commit()
    return added


async def x_seed_default_rules__mutmut_14(db: AsyncSession) -> int:
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
                anonymize=rule["anonymize"],
            )
        )
        added += 1
    if added:
        await db.commit()
    return added


async def x_seed_default_rules__mutmut_15(db: AsyncSession) -> int:
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
                )
        )
        added += 1
    if added:
        await db.commit()
    return added


async def x_seed_default_rules__mutmut_16(db: AsyncSession) -> int:
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
                retention_days=rule["XXretention_daysXX"],
                anonymize=rule["anonymize"],
            )
        )
        added += 1
    if added:
        await db.commit()
    return added


async def x_seed_default_rules__mutmut_17(db: AsyncSession) -> int:
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
                retention_days=rule["RETENTION_DAYS"],
                anonymize=rule["anonymize"],
            )
        )
        added += 1
    if added:
        await db.commit()
    return added


async def x_seed_default_rules__mutmut_18(db: AsyncSession) -> int:
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
                anonymize=rule["XXanonymizeXX"],
            )
        )
        added += 1
    if added:
        await db.commit()
    return added


async def x_seed_default_rules__mutmut_19(db: AsyncSession) -> int:
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
                anonymize=rule["ANONYMIZE"],
            )
        )
        added += 1
    if added:
        await db.commit()
    return added


async def x_seed_default_rules__mutmut_20(db: AsyncSession) -> int:
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
        added = 1
    if added:
        await db.commit()
    return added


async def x_seed_default_rules__mutmut_21(db: AsyncSession) -> int:
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
        added -= 1
    if added:
        await db.commit()
    return added


async def x_seed_default_rules__mutmut_22(db: AsyncSession) -> int:
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
        added += 2
    if added:
        await db.commit()
    return added

mutants_x_seed_default_rules__mutmut['_mutmut_orig'] = x_seed_default_rules__mutmut_orig # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_1'] = x_seed_default_rules__mutmut_1 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_2'] = x_seed_default_rules__mutmut_2 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_3'] = x_seed_default_rules__mutmut_3 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_4'] = x_seed_default_rules__mutmut_4 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_5'] = x_seed_default_rules__mutmut_5 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_6'] = x_seed_default_rules__mutmut_6 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_7'] = x_seed_default_rules__mutmut_7 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_8'] = x_seed_default_rules__mutmut_8 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_9'] = x_seed_default_rules__mutmut_9 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_10'] = x_seed_default_rules__mutmut_10 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_11'] = x_seed_default_rules__mutmut_11 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_12'] = x_seed_default_rules__mutmut_12 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_13'] = x_seed_default_rules__mutmut_13 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_14'] = x_seed_default_rules__mutmut_14 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_15'] = x_seed_default_rules__mutmut_15 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_16'] = x_seed_default_rules__mutmut_16 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_17'] = x_seed_default_rules__mutmut_17 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_18'] = x_seed_default_rules__mutmut_18 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_19'] = x_seed_default_rules__mutmut_19 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_20'] = x_seed_default_rules__mutmut_20 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_21'] = x_seed_default_rules__mutmut_21 # type: ignore # mutmut generated
mutants_x_seed_default_rules__mutmut['x_seed_default_rules__mutmut_22'] = x_seed_default_rules__mutmut_22 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_purge_expired__mutmut)
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


async def x_purge_expired__mutmut_orig(db: AsyncSession, dry_run: bool = True) -> dict:
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


async def x_purge_expired__mutmut_1(db: AsyncSession, dry_run: bool = False) -> dict:
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


async def x_purge_expired__mutmut_2(db: AsyncSession, dry_run: bool = True) -> dict:
    """Count (and, unless dry_run, delete) expired rows in prunable tables.

    Returns {table: {"expired": n, "deleted": n}}.
    """
    now = None
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


async def x_purge_expired__mutmut_3(db: AsyncSession, dry_run: bool = True) -> dict:
    """Count (and, unless dry_run, delete) expired rows in prunable tables.

    Returns {table: {"expired": n, "deleted": n}}.
    """
    now = datetime.now(None).replace(tzinfo=None)
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


async def x_purge_expired__mutmut_4(db: AsyncSession, dry_run: bool = True) -> dict:
    """Count (and, unless dry_run, delete) expired rows in prunable tables.

    Returns {table: {"expired": n, "deleted": n}}.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    report: dict[str, dict] = None
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


async def x_purge_expired__mutmut_5(db: AsyncSession, dry_run: bool = True) -> dict:
    """Count (and, unless dry_run, delete) expired rows in prunable tables.

    Returns {table: {"expired": n, "deleted": n}}.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    report: dict[str, dict] = {}
    for table_name, rule in _DEFAULT_RULES.items():
        if rule["prunable"]:
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


async def x_purge_expired__mutmut_6(db: AsyncSession, dry_run: bool = True) -> dict:
    """Count (and, unless dry_run, delete) expired rows in prunable tables.

    Returns {table: {"expired": n, "deleted": n}}.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    report: dict[str, dict] = {}
    for table_name, rule in _DEFAULT_RULES.items():
        if not rule["XXprunableXX"]:
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


async def x_purge_expired__mutmut_7(db: AsyncSession, dry_run: bool = True) -> dict:
    """Count (and, unless dry_run, delete) expired rows in prunable tables.

    Returns {table: {"expired": n, "deleted": n}}.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    report: dict[str, dict] = {}
    for table_name, rule in _DEFAULT_RULES.items():
        if not rule["PRUNABLE"]:
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


async def x_purge_expired__mutmut_8(db: AsyncSession, dry_run: bool = True) -> dict:
    """Count (and, unless dry_run, delete) expired rows in prunable tables.

    Returns {table: {"expired": n, "deleted": n}}.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    report: dict[str, dict] = {}
    for table_name, rule in _DEFAULT_RULES.items():
        if not rule["prunable"]:
            break
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


async def x_purge_expired__mutmut_9(db: AsyncSession, dry_run: bool = True) -> dict:
    """Count (and, unless dry_run, delete) expired rows in prunable tables.

    Returns {table: {"expired": n, "deleted": n}}.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    report: dict[str, dict] = {}
    for table_name, rule in _DEFAULT_RULES.items():
        if not rule["prunable"]:
            continue
        model = None
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


async def x_purge_expired__mutmut_10(db: AsyncSession, dry_run: bool = True) -> dict:
    """Count (and, unless dry_run, delete) expired rows in prunable tables.

    Returns {table: {"expired": n, "deleted": n}}.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    report: dict[str, dict] = {}
    for table_name, rule in _DEFAULT_RULES.items():
        if not rule["prunable"]:
            continue
        model = _model_for(None)
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


async def x_purge_expired__mutmut_11(db: AsyncSession, dry_run: bool = True) -> dict:
    """Count (and, unless dry_run, delete) expired rows in prunable tables.

    Returns {table: {"expired": n, "deleted": n}}.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    report: dict[str, dict] = {}
    for table_name, rule in _DEFAULT_RULES.items():
        if not rule["prunable"]:
            continue
        model = _model_for(table_name)
        if model is not None:
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


async def x_purge_expired__mutmut_12(db: AsyncSession, dry_run: bool = True) -> dict:
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
            break
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


async def x_purge_expired__mutmut_13(db: AsyncSession, dry_run: bool = True) -> dict:
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
        ts_col = None
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


async def x_purge_expired__mutmut_14(db: AsyncSession, dry_run: bool = True) -> dict:
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
        ts_col = getattr(None, rule["ts"], None)
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


async def x_purge_expired__mutmut_15(db: AsyncSession, dry_run: bool = True) -> dict:
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
        ts_col = getattr(model, None, None)
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


async def x_purge_expired__mutmut_16(db: AsyncSession, dry_run: bool = True) -> dict:
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
        ts_col = getattr(rule["ts"], None)
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


async def x_purge_expired__mutmut_17(db: AsyncSession, dry_run: bool = True) -> dict:
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
        ts_col = getattr(model, None)
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


async def x_purge_expired__mutmut_18(db: AsyncSession, dry_run: bool = True) -> dict:
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
        ts_col = getattr(model, rule["ts"], )
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


async def x_purge_expired__mutmut_19(db: AsyncSession, dry_run: bool = True) -> dict:
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
        ts_col = getattr(model, rule["XXtsXX"], None)
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


async def x_purge_expired__mutmut_20(db: AsyncSession, dry_run: bool = True) -> dict:
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
        ts_col = getattr(model, rule["TS"], None)
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


async def x_purge_expired__mutmut_21(db: AsyncSession, dry_run: bool = True) -> dict:
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
        if ts_col is not None:
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


async def x_purge_expired__mutmut_22(db: AsyncSession, dry_run: bool = True) -> dict:
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
            break
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


async def x_purge_expired__mutmut_23(db: AsyncSession, dry_run: bool = True) -> dict:
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
        cutoff = None
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


async def x_purge_expired__mutmut_24(db: AsyncSession, dry_run: bool = True) -> dict:
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
        cutoff = now + timedelta(days=rule["retention_days"])
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


async def x_purge_expired__mutmut_25(db: AsyncSession, dry_run: bool = True) -> dict:
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
        cutoff = now - timedelta(days=None)
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


async def x_purge_expired__mutmut_26(db: AsyncSession, dry_run: bool = True) -> dict:
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
        cutoff = now - timedelta(days=rule["XXretention_daysXX"])
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


async def x_purge_expired__mutmut_27(db: AsyncSession, dry_run: bool = True) -> dict:
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
        cutoff = now - timedelta(days=rule["RETENTION_DAYS"])
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


async def x_purge_expired__mutmut_28(db: AsyncSession, dry_run: bool = True) -> dict:
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
        expired = None
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


async def x_purge_expired__mutmut_29(db: AsyncSession, dry_run: bool = True) -> dict:
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
        expired = (await db.execute(select(func.count()).select_from(model).where(ts_col < cutoff))).scalar() and 0
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


async def x_purge_expired__mutmut_30(db: AsyncSession, dry_run: bool = True) -> dict:
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
        expired = (await db.execute(None)).scalar() or 0
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


async def x_purge_expired__mutmut_31(db: AsyncSession, dry_run: bool = True) -> dict:
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
        expired = (await db.execute(select(func.count()).select_from(model).where(None))).scalar() or 0
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


async def x_purge_expired__mutmut_32(db: AsyncSession, dry_run: bool = True) -> dict:
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
        expired = (await db.execute(select(func.count()).select_from(None).where(ts_col < cutoff))).scalar() or 0
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


async def x_purge_expired__mutmut_33(db: AsyncSession, dry_run: bool = True) -> dict:
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
        expired = (await db.execute(select(None).select_from(model).where(ts_col < cutoff))).scalar() or 0
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


async def x_purge_expired__mutmut_34(db: AsyncSession, dry_run: bool = True) -> dict:
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
        expired = (await db.execute(select(func.count()).select_from(model).where(ts_col <= cutoff))).scalar() or 0
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


async def x_purge_expired__mutmut_35(db: AsyncSession, dry_run: bool = True) -> dict:
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
        expired = (await db.execute(select(func.count()).select_from(model).where(ts_col < cutoff))).scalar() or 1
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


async def x_purge_expired__mutmut_36(db: AsyncSession, dry_run: bool = True) -> dict:
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
        deleted = None
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


async def x_purge_expired__mutmut_37(db: AsyncSession, dry_run: bool = True) -> dict:
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
        deleted = 1
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


async def x_purge_expired__mutmut_38(db: AsyncSession, dry_run: bool = True) -> dict:
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
        if expired or not dry_run:
            rows = (await db.execute(select(model).where(ts_col < cutoff))).scalars().all()
            for r in rows:
                await db.delete(r)
            deleted = len(rows)
        report[table_name] = {"expired": expired, "deleted": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_39(db: AsyncSession, dry_run: bool = True) -> dict:
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
        if expired and dry_run:
            rows = (await db.execute(select(model).where(ts_col < cutoff))).scalars().all()
            for r in rows:
                await db.delete(r)
            deleted = len(rows)
        report[table_name] = {"expired": expired, "deleted": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_40(db: AsyncSession, dry_run: bool = True) -> dict:
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
            rows = None
            for r in rows:
                await db.delete(r)
            deleted = len(rows)
        report[table_name] = {"expired": expired, "deleted": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_41(db: AsyncSession, dry_run: bool = True) -> dict:
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
            rows = (await db.execute(None)).scalars().all()
            for r in rows:
                await db.delete(r)
            deleted = len(rows)
        report[table_name] = {"expired": expired, "deleted": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_42(db: AsyncSession, dry_run: bool = True) -> dict:
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
            rows = (await db.execute(select(model).where(None))).scalars().all()
            for r in rows:
                await db.delete(r)
            deleted = len(rows)
        report[table_name] = {"expired": expired, "deleted": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_43(db: AsyncSession, dry_run: bool = True) -> dict:
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
            rows = (await db.execute(select(None).where(ts_col < cutoff))).scalars().all()
            for r in rows:
                await db.delete(r)
            deleted = len(rows)
        report[table_name] = {"expired": expired, "deleted": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_44(db: AsyncSession, dry_run: bool = True) -> dict:
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
            rows = (await db.execute(select(model).where(ts_col <= cutoff))).scalars().all()
            for r in rows:
                await db.delete(r)
            deleted = len(rows)
        report[table_name] = {"expired": expired, "deleted": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_45(db: AsyncSession, dry_run: bool = True) -> dict:
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
                await db.delete(None)
            deleted = len(rows)
        report[table_name] = {"expired": expired, "deleted": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_46(db: AsyncSession, dry_run: bool = True) -> dict:
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
            deleted = None
        report[table_name] = {"expired": expired, "deleted": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_47(db: AsyncSession, dry_run: bool = True) -> dict:
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
        report[table_name] = None
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_48(db: AsyncSession, dry_run: bool = True) -> dict:
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
        report[table_name] = {"XXexpiredXX": expired, "deleted": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_49(db: AsyncSession, dry_run: bool = True) -> dict:
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
        report[table_name] = {"EXPIRED": expired, "deleted": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_50(db: AsyncSession, dry_run: bool = True) -> dict:
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
        report[table_name] = {"expired": expired, "XXdeletedXX": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_51(db: AsyncSession, dry_run: bool = True) -> dict:
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
        report[table_name] = {"expired": expired, "DELETED": deleted}
    if not dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_52(db: AsyncSession, dry_run: bool = True) -> dict:
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
    if dry_run:
        await db.commit()
    log.info("retention purge (dry_run=%s): %s", dry_run, report)
    return report


async def x_purge_expired__mutmut_53(db: AsyncSession, dry_run: bool = True) -> dict:
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
    log.info(None, dry_run, report)
    return report


async def x_purge_expired__mutmut_54(db: AsyncSession, dry_run: bool = True) -> dict:
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
    log.info("retention purge (dry_run=%s): %s", None, report)
    return report


async def x_purge_expired__mutmut_55(db: AsyncSession, dry_run: bool = True) -> dict:
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
    log.info("retention purge (dry_run=%s): %s", dry_run, None)
    return report


async def x_purge_expired__mutmut_56(db: AsyncSession, dry_run: bool = True) -> dict:
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
    log.info(dry_run, report)
    return report


async def x_purge_expired__mutmut_57(db: AsyncSession, dry_run: bool = True) -> dict:
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
    log.info("retention purge (dry_run=%s): %s", report)
    return report


async def x_purge_expired__mutmut_58(db: AsyncSession, dry_run: bool = True) -> dict:
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
    log.info("retention purge (dry_run=%s): %s", dry_run, )
    return report


async def x_purge_expired__mutmut_59(db: AsyncSession, dry_run: bool = True) -> dict:
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
    log.info("XXretention purge (dry_run=%s): %sXX", dry_run, report)
    return report


async def x_purge_expired__mutmut_60(db: AsyncSession, dry_run: bool = True) -> dict:
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
    log.info("RETENTION PURGE (DRY_RUN=%S): %S", dry_run, report)
    return report

mutants_x_purge_expired__mutmut['_mutmut_orig'] = x_purge_expired__mutmut_orig # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_1'] = x_purge_expired__mutmut_1 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_2'] = x_purge_expired__mutmut_2 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_3'] = x_purge_expired__mutmut_3 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_4'] = x_purge_expired__mutmut_4 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_5'] = x_purge_expired__mutmut_5 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_6'] = x_purge_expired__mutmut_6 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_7'] = x_purge_expired__mutmut_7 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_8'] = x_purge_expired__mutmut_8 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_9'] = x_purge_expired__mutmut_9 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_10'] = x_purge_expired__mutmut_10 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_11'] = x_purge_expired__mutmut_11 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_12'] = x_purge_expired__mutmut_12 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_13'] = x_purge_expired__mutmut_13 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_14'] = x_purge_expired__mutmut_14 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_15'] = x_purge_expired__mutmut_15 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_16'] = x_purge_expired__mutmut_16 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_17'] = x_purge_expired__mutmut_17 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_18'] = x_purge_expired__mutmut_18 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_19'] = x_purge_expired__mutmut_19 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_20'] = x_purge_expired__mutmut_20 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_21'] = x_purge_expired__mutmut_21 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_22'] = x_purge_expired__mutmut_22 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_23'] = x_purge_expired__mutmut_23 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_24'] = x_purge_expired__mutmut_24 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_25'] = x_purge_expired__mutmut_25 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_26'] = x_purge_expired__mutmut_26 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_27'] = x_purge_expired__mutmut_27 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_28'] = x_purge_expired__mutmut_28 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_29'] = x_purge_expired__mutmut_29 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_30'] = x_purge_expired__mutmut_30 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_31'] = x_purge_expired__mutmut_31 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_32'] = x_purge_expired__mutmut_32 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_33'] = x_purge_expired__mutmut_33 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_34'] = x_purge_expired__mutmut_34 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_35'] = x_purge_expired__mutmut_35 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_36'] = x_purge_expired__mutmut_36 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_37'] = x_purge_expired__mutmut_37 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_38'] = x_purge_expired__mutmut_38 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_39'] = x_purge_expired__mutmut_39 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_40'] = x_purge_expired__mutmut_40 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_41'] = x_purge_expired__mutmut_41 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_42'] = x_purge_expired__mutmut_42 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_43'] = x_purge_expired__mutmut_43 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_44'] = x_purge_expired__mutmut_44 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_45'] = x_purge_expired__mutmut_45 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_46'] = x_purge_expired__mutmut_46 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_47'] = x_purge_expired__mutmut_47 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_48'] = x_purge_expired__mutmut_48 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_49'] = x_purge_expired__mutmut_49 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_50'] = x_purge_expired__mutmut_50 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_51'] = x_purge_expired__mutmut_51 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_52'] = x_purge_expired__mutmut_52 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_53'] = x_purge_expired__mutmut_53 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_54'] = x_purge_expired__mutmut_54 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_55'] = x_purge_expired__mutmut_55 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_56'] = x_purge_expired__mutmut_56 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_57'] = x_purge_expired__mutmut_57 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_58'] = x_purge_expired__mutmut_58 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_59'] = x_purge_expired__mutmut_59 # type: ignore # mutmut generated
mutants_x_purge_expired__mutmut['x_purge_expired__mutmut_60'] = x_purge_expired__mutmut_60 # type: ignore # mutmut generated
