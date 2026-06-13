import contextlib
import os
import sys

# Fix ModuleNotFoundError for 'services' and 'routers'
# Add the backend directory to sys.path so pytest can discover modules during collection.
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Set safe test env defaults before any backend module imports (which create Settings).
os.environ["SIGNAL_TRADE_TESTING"] = "1"
os.environ["SITE_PRIVATE_TOKEN"] = ""  # disable private-preview middleware in tests
os.environ["SENTRY_DSN"] = ""  # keep Sentry quiet in tests
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_db.sqlite")
os.environ.setdefault("JWT_SECRET", "x" * 32)
os.environ.setdefault("OWNER_PASSWORD", "y" * 16)

import pytest


@pytest.fixture(autouse=True, scope="session")
def _set_test_database_url():
    """Force test runs to use an isolated SQLite database.

    This bypasses the need for asyncpg during test collection and protects
    your local PostgreSQL dev database.
    """
    mp = pytest.MonkeyPatch()
    mp.setenv("DATABASE_URL", "sqlite+aiosqlite:///./test_db.sqlite")
    yield
    mp.undo()


@contextlib.contextmanager
def override_deps(app, **deps):
    """Temporarily override FastAPI dependencies and restore them on exit.

    Usage:
        with override_deps(app, get_current_user=lambda: mock_user):
            resp = client.get("/api/protected")
    """
    original = dict(app.dependency_overrides)
    app.dependency_overrides.update(deps)
    try:
        yield
    finally:
        app.dependency_overrides = original
