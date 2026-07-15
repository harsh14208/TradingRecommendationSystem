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


@pytest.fixture(autouse=True)
def _neutralize_cohort_gate():
    """Make the self-calibrating cohort-EV gate inert by default in tests.

    The gate reads a process-global snapshot (cache → disk). Without this, every
    test of an unrelated gate would be coupled to whatever ``data/cohort_edges.json``
    happens to hold locally. We disable disk loading and clear the cache so the gate
    is in cold-start passthrough (deliver-everything) unless a test explicitly installs
    its own snapshot via ``cache_snapshot(...)`` (see test_cohort_edge_gate.py).
    """
    try:
        from services import cohort_edge_gate as _ceg

        _ceg.set_disk_load_enabled(False)
        _ceg.cache_snapshot(None)
        yield
        _ceg.cache_snapshot(None)
        _ceg.set_disk_load_enabled(True)
    except Exception:
        yield


@pytest.fixture(autouse=True)
def _isolate_signal_ml_persistence(tmp_path, monkeypatch):
    """Redirect ALL signal_ml model/feature persistence paths to tmp_path.

    Root-caused 2026-07-15: tests exercising train_model() mocked _MODEL_FILE
    but not _FEATURE_FILE (and friends), so every full pytest run overwrote
    production data/signal_ml_features.json with fixture metadata (n_total=400,
    champion_auc=0.65). The drift monitor then compared live features against
    zero-variance fixture stats — thousands of bogus "distribution drift"
    warnings per scan — and honest retrain artifacts were silently clobbered
    before being committed. No test may write to the real data/ model files.
    """
    try:
        from services import signal_ml as _sml

        for _attr in (
            "_MODEL_FILE",
            "_FEATURE_FILE",
            "_ENTRY_MODEL_FILE",
            "_ENTRY_FEATURE_FILE",
            "_CHALLENGER_MODEL_FILE",
            "_CHALLENGER_FEATURE_FILE",
            "_META_MODEL_FILE",
            "_META_FEATURE_FILE",
        ):
            if hasattr(_sml, _attr):
                monkeypatch.setattr(_sml, _attr, tmp_path / getattr(_sml, _attr).name)
        yield
    except Exception:
        yield


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
