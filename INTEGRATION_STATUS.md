# Integration Status Report

> Last updated: 2026-08-16T01:08:33Z
> Commit: `d7ba896eb497ac696d18298784c027425e4836b3`
> Pipeline: **FAILED**

## Summary
| Metric | Value |
|--------|-------|
| Total Tests | 2700 |
| Passed | 2666 |
| Failed | 2 |
| Skipped | 32 |
| Coverage | 75.4% |
| Duration | 164.05s |

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
| Other | 2162 | ❌ | 0.0 | assert 404 == 200 |

## Coverage Breakdown
| Module | Coverage |
|--------|----------|
| `signal_engine` | 47.5% |
| `assembler` | 66.5% |
| `broker_svc` | 66.9% |
| `market_data` | 74.4% |
| `polygon_client` | 75.6% |
| `signal_ml` | 82.9% |
| `technicals` | 83.9% |
| `signals` | 84.8% |
| `calibration` | 84.9% |
| `macro` | 85.0% |
| `admin` | 87.2% |
| `quotes` | 88.1% |
| `options` | 95.5% |
| `auth` | 96.3% |
| `models` | 100.0% |

## Trend
| Run | Timestamp | Tests | Coverage | Status |
|-----|-----------|-------|----------|--------|
| Current | 2026-08-16T01:08:33Z | 2700 | 75.4% | FAILED |
| Previous | 2026-08-09T01:26:34Z | 2700 | 75.4% | FAILED |

### Health Delta
- Tests: +0 vs previous
- Coverage: +0.0% vs previous
- Status: Stable

---
*Generated automatically by `scripts/generate_status_report.py`*
