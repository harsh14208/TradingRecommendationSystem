"""Run backend unit tests.


Used by local dev / CI to quickly catch regressions before restarting.

Usage:
  python3 -m backend.tests.run_all_tests
  python3 backend/tests/run_all_tests.py
"""

import os
import subprocess
import sys


def main() -> int:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    cmd = [sys.executable, "-m", "unittest", "discover", "-q", "-s", "backend/tests"]

    env = os.environ.copy()
    # Ensure backend/ is importable so tests can import `services.*`.
    backend_dir = os.path.join(root, "backend")
    env["PYTHONPATH"] = backend_dir + os.pathsep + env.get("PYTHONPATH", "")

    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=root, env=env)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
