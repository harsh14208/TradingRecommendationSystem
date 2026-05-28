import os
import sys

# 1. Fix ModuleNotFoundError for 'services' and 'routers'
# Add the backend directory to sys.path so pytest can discover modules during collection.
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# 2. Fix ModuleNotFoundError for 'asyncpg'
# Force test runs to use an isolated SQLite database. This bypasses the need
# for asyncpg during test collection and protects your local PostgreSQL dev database.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_db.sqlite"
