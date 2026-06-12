"""Root pytest configuration.

The Playwright plugin's synchronous browser engine leaves a running event loop
in the test process.  That conflicts with pytest-asyncio when E2E and backend
unit tests are executed in the same pytest invocation.  We therefore:

  1. Skip E2E tests by default.
  2. Block the pytest-playwright plugin unless ``--run-e2e`` is passed.

Run unit tests:      pytest tests/ -q --timeout=30
Run E2E tests:       pytest tests/e2e --run-e2e -q --timeout=60
"""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="Run the Playwright E2E test suite",
    )


def pytest_load_initial_conftests(early_config, parser, args) -> None:
    if "--run-e2e" not in args:
        early_config.pluginmanager.set_blocked("pytest_playwright")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-e2e"):
        return
    skip_e2e = pytest.mark.skip(reason="E2E tests skipped unless --run-e2e")
    for item in items:
        if "tests/e2e" in str(item.path):
            item.add_marker(skip_e2e)
