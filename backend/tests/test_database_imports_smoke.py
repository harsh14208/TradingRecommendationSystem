import importlib
import sys


def test_database_imports_without_asyncpg(monkeypatch):
    """Smoke: importing backend.database should not fail when asyncpg isn't installed.

    The repo's test environment may run with SQLite (default), so the module must
    gracefully avoid importing/using asyncpg at import-time.
    """

    # Ensure we use SQLite even if CI has DATABASE_URL configured.
    monkeypatch.setenv("DATABASE_URL", "")

    # Use monkeypatch.setitem so pytest restores original module after the test,
    # preventing get_db function-identity contamination in other tests.
    original = sys.modules.get("database")
    if original is not None:
        monkeypatch.setitem(sys.modules, "database", original)
    monkeypatch.delitem(sys.modules, "database", raising=False)
    monkeypatch.delitem(sys.modules, "backend.database", raising=False)

    # The project uses absolute imports like `from database import ...`
    # when PYTHONPATH includes backend/.
    db = importlib.import_module("database")

    assert hasattr(db, "DATABASE_URL")
    assert db.DATABASE_URL.startswith("sqlite+")
