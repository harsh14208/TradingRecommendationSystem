import os
import sys
import unittest

# Force SQLite for this test run.
# Otherwise SQLAlchemy will attempt to load asyncpg at import-time.
os.environ.setdefault("DATABASE_URL", "")


# Ensure backend/ is on sys.path so absolute imports like `from services...` work.
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


class TestImportsSmoke(unittest.TestCase):
    def test_can_import_core_services(self):
        # Smoke-test: ensures the app can import key modules.
        # If any dependency import breaks, this fails early.
        # Ensure repo root is importable so `import backend.*` works.
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)

        import backend.routers.auth  # noqa: F401
        import backend.services.calibration  # noqa: F401
        import backend.services.scanner  # noqa: F401
        import backend.services.signal_engine  # noqa: F401


if __name__ == "__main__":
    unittest.main()
