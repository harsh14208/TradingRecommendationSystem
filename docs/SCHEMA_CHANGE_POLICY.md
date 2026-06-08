# Schema Change Policy (TSYS-12a)

**Production schema changes are Alembic-only.** Every table/column/index change
that must reach production goes through a reviewed Alembic migration in
`backend/alembic/versions/`, applied with `alembic upgrade head`.

## Rules

1. **No production DDL outside Alembic.** Do not rely on `Base.metadata.create_all`
   / `init_db` column additions to mutate a production database. Those paths exist
   only for **dev/test convenience** (fast SQLite spin-up) and must never be the
   mechanism by which a prod column appears.
2. **One linear head.** Before opening a PR, run `alembic heads` — it must print a
   single head. Forked heads (a real hazard with concurrent sessions) are blocked
   by the migration smoke test (`test_tsys12_migrations.py`). If you forked, rebase
   your `down_revision` onto the current head.
3. **Every upgrade needs a real downgrade.** A migration whose `upgrade()` calls
   `op.*` must have a non-empty `downgrade()`. Enforced by the smoke test.
4. **New hot-path columns ship with an index.** Columns that appear in `WHERE` /
   `ORDER BY` on a hot path must be indexed in the same migration. The index audit
   (`GET /api/admin/index-audit` + `test_tsys12_retention.py::test_hotpath_indexes_present`)
   guards the known set.
5. **Retention is policy-driven.** Per-table retention/anonymization lives in
   `services/retention_svc.py` (`DataRetentionRule`). Core/regulated tables
   (`users`, `signals`, `signal_deliveries`, `broker_orders`) are **never**
   auto-pruned — they require the explicit, audited deletion flow (TSYS-13d).

## CI / pre-merge checklist

- `alembic heads` → exactly one head
- `pytest tests/test_tsys12_migrations.py` → green (single head, linear chain, real downgrades)
- `pytest tests/test_tsys12_retention.py::test_hotpath_indexes_present` → green
- New migration applies cleanly on a fresh DB (`alembic upgrade head`) and reverses (`alembic downgrade -1`)
