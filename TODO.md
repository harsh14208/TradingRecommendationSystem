# TODO - Add tests for all uncovered backend modules

## Plan (approved)
1. Scan repo to map Python modules under `backend/` (services + routers + root backend/*.py) to existing tests under `backend/tests/test_*.py`.
2. Identify uncovered modules and categorize them:
   - Pure/unit-testable helpers (string parsing, scoring math, feature extraction, etc.)
   - Async/network/DB/integration-heavy modules to be tested with mocks (pytest + AsyncMock/patch).
3. For each uncovered module, add a focused `backend/tests/test_<module>.py` test file with:
   - Happy-path + edge-case(s)
   - Mocking for external services (HTTP, DB, Redis, SDKs like stripe/polygon/qdrant/playwright)
4. Add/extend an import-smoke test to ensure key modules import without side effects.
5. Run test suite (`pytest` if configured, otherwise `python -m unittest discover`) and iterate on any failures.

