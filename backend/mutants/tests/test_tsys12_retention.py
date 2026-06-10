"""TSYS-12b/12c: retention rules, purge pass, and hot-path index audit."""

from unittest.mock import AsyncMock, MagicMock

import pytest

import models
from services import retention_svc


def test_default_rules_cover_core_and_prunable_tables():
    rules = retention_svc.default_rules()
    assert "provider_response_samples" in rules and rules["provider_response_samples"]["prunable"] is True
    # Core regulated tables are present but NOT auto-pruned.
    assert rules["signals"]["prunable"] is False
    assert rules["users"]["prunable"] is False


@pytest.mark.asyncio
async def test_purge_dry_run_reports_without_deleting():
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar=MagicMock(return_value=5)))
    db.delete = AsyncMock()
    report = await retention_svc.purge_expired(db, dry_run=True)
    # Every prunable table reports expired counts but deletes nothing in dry-run.
    assert report["provider_response_samples"]["expired"] == 5
    assert all(v["deleted"] == 0 for v in report.values())
    db.delete.assert_not_called()


@pytest.mark.asyncio
async def test_seed_default_rules_adds_missing():
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalars=lambda: MagicMock(all=lambda: [])))
    db.add = MagicMock()
    db.commit = AsyncMock()
    added = await retention_svc.seed_default_rules(db)
    assert added == len(retention_svc.default_rules())
    assert db.add.call_count == added


def test_hotpath_indexes_present():
    """TSYS-12c regression guard: required hot-path columns stay indexed."""
    required = [
        ("signals", "created_at"),
        ("signals", "is_sent"),
        ("signal_deliveries", "user_id"),
        ("signal_deliveries", "signal_id"),
        ("broker_orders", "user_id"),
        ("broker_orders", "status"),
        ("broker_orders", "created_at"),
        ("action_audit_logs", "user_id"),
        ("provider_response_samples", "created_at"),
    ]
    tables = {m.__tablename__: m.__table__ for m in models.Base.__subclasses__() if hasattr(m, "__tablename__")}
    missing = []
    for table_name, column in required:
        tbl = tables.get(table_name)
        col = tbl.columns.get(column) if tbl is not None else None
        indexed = bool(col is not None and col.index) or (
            tbl is not None and any(column in idx.columns for idx in tbl.indexes)
        )
        if not indexed:
            missing.append(f"{table_name}.{column}")
    assert not missing, f"hot-path columns missing an index: {missing}"
