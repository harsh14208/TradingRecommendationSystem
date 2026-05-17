# Integration Status Report

> Last updated: 2026-05-17T00:35:59Z
> Commit: `local`
> Pipeline: **PASSED**

## Summary
| Metric | Value |
|--------|-------|
| Total Tests | 599 |
| Passed | 596 |
| Failed | 0 |
| Skipped | 3 |
| Coverage | 49.5% |
| Duration | 36.86s |

## Feature Breakdown
| Feature / Module | Tests | Status | Duration (s) | Errors |
|------------------|-------|--------|--------------|--------|
| Authentication | 58 | ✅ | 0.0 | — |
| Signal Engine | 111 | ✅ | 0.0 | — |
| Scanner | 54 | ✅ | 0.0 | — |
| Telegram / Delivery | 39 | ✅ | 0.0 | — |
| Billing | 5 | ✅ | 0.0 | — |
| Watchlist | 10 | ✅ | 0.0 | — |
| Quotes / Market | 4 | ✅ | 0.0 | — |
| Technicals | 45 | ✅ | 0.0 | — |
| ML / Scoring | 7 | ✅ | 0.0 | — |
| Other | 266 | ✅ | 0.0 | — |

## Coverage Breakdown
| Module | Coverage |
|--------|----------|
| `main` | 0.0% |
| `local_llm` | 0.0% |
| `vector_store` | 0.0% |
| `macro` | 5.8% |
| `signals` | 15.5% |
| `quotes` | 18.2% |
| `scanner` | 21.2% |
| `edgar` | 26.6% |
| `signal_ml` | 38.6% |
| `signal_engine` | 40.6% |
| `options` | 46.6% |
| `auth` | 51.9% |
| `technicals` | 82.7% |
| `test_signal_workers` | 98.7% |
| `test_scanner_extended` | 100.0% |

## Trend
| Run | Timestamp | Tests | Coverage | Status |
|-----|-----------|-------|----------|--------|
| Current | 2026-05-17T00:35:59Z | 599 | 49.5% | PASSED |
| Previous | N/A | N/A | N/A | N/A |

### Health Delta
- Tests: N/A vs previous
- Coverage: N/A vs previous
- Status: —

---

## Architectural Assessment

| Category | Score | Justification |
|----------|-------|---------------|
| **Testability & Code Decoupling** | 5/10 | Core business logic (scanner, signal engine) is tightly coupled to DB sessions and external HTTP calls, making true unit tests require deep mocking scaffolding. Pure functions like `_market_hours_ok`, `_pct`, and indicator math are cleanly isolated. The router layer uses FastAPI's `Depends()` for DB injection, which is good. Main bottleneck: `run_scan` is a 300-line monolith that does data fetch, scoring, persistence, and delivery in one function. Splitting these into injected services would dramatically improve testability. |
| **Robustness & Error Resilience** | 6/10 | Most external API calls are individually try/except'd and fail gracefully (market data, Telegram, Alpaca). The scanner's `_periodic_scan` loop now catches `BaseException` and has a watchdog that restarts it if it dies. Key weaknesses remain: `scan_all` failures return silently without incrementing the fail streak; the differential scan can starve all tickers if market data APIs are consistently slow; SQLite under concurrent load from two uvicorn workers causes locking. |
| **CI/CD Pipeline Efficiency** | 6/10 | The push/PR workflow runs syntax check, smoke tests, unit tests, and pip-audit. pip caching on `requirements.txt` eliminates install overhead. The new weekend workflow runs the full suite and auto-commits the status report. Weaknesses: tests run sequentially (no `-n auto` parallelism via pytest-xdist); the 37-second suite would benefit from splitting into fast unit and slow integration jobs; no matrix across Python versions; no Docker layer caching for the heavier dependency install. |
| **Maintainability & Documentation** | 6/10 | HOWTO.md and inline comments explain the non-obvious parts (differential scan, cooldown logic, SLA tracking). Module separation across `routers/`, `services/`, and `models.py` is clean. The signal engine at 3700+ lines is the main readability debt — it mixes scoring, data enrichment, and ML calibration with no sub-module boundary. The `run_scan` function similarly needs decomposition. Pydantic v2 deprecation warnings (class-based Config) indicate minor technical debt in router schemas. |

### Summary
The system is **production-viable** for a single-operator deployment. The main engineering investments needed for scale are: decomposing `run_scan` and `signal_engine` into injectable services, migrating from SQLite to PostgreSQL for concurrent access, adding pytest-xdist for parallel test execution, and enforcing the owner-gate on all mutation endpoints (done in this session for the most critical ones).

---
*Generated automatically by `scripts/generate_status_report.py`*
