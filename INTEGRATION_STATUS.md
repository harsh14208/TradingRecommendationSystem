# Integration Status Report

> Last updated: 2026-07-19T02:27:10Z
> Commit: `30caf5b31e665e6c6712da8379e6ff45d971877a`
> Pipeline: **FAILED**

## Summary
| Metric | Value |
|--------|-------|
| Total Tests | 2682 |
| Passed | 2649 |
| Failed | 1 |
| Skipped | 32 |
| Coverage | 75.2% |
| Duration | 180.76s |

## Feature Breakdown
| Feature / Module | Tests | Status | Duration (s) | Errors |
|------------------|-------|--------|--------------|--------|
| Authentication | 82 | ✅ | 0.0 | — |
| Signal Engine | 132 | ✅ | 0.0 | — |
| Scanner | 65 | ✅ | 0.0 | — |
| Telegram / Delivery | 101 | ✅ | 0.0 | — |
| Billing | 25 | ✅ | 0.0 | — |
| Watchlist | 10 | ✅ | 0.0 | — |
| Quotes / Market | 40 | ✅ | 0.0 | — |
| Technicals | 67 | ✅ | 0.0 | — |
| ML / Scoring | 16 | ✅ | 0.0 | — |
| Other | 2144 | ❌ | 0.0 | assert 404 == 200 |

## Coverage Breakdown
| Module | Coverage |
|--------|----------|
| `signal_engine` | 47.4% |
| `broker_svc` | 66.1% |
| `assembler` | 66.5% |
| `market_data` | 74.4% |
| `polygon_client` | 75.6% |
| `signal_ml` | 82.9% |
| `technicals` | 83.9% |
| `macro` | 84.5% |
| `signals` | 84.8% |
| `calibration` | 84.9% |
| `admin` | 87.2% |
| `quotes` | 88.1% |
| `auth` | 96.3% |
| `options` | 96.4% |
| `models` | 100.0% |

## Trend
| Run | Timestamp | Tests | Coverage | Status |
|-----|-----------|-------|----------|--------|
| Current | 2026-07-19T02:27:10Z | 2682 | 75.2% | FAILED |
| Previous | N/A | N/A | N/A | N/A |

### Health Delta
- Tests: first run vs previous
- Coverage: baseline vs previous
- Status: —

---
*Generated automatically by `scripts/generate_status_report.py`*
