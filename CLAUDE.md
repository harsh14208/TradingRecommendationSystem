# CLAUDE.md — TradingRecommendationSystem

## Environment

- **Python version:** 3.11 (matches CI — `actions/setup-python@v5` with `python-version: "3.11"`)
- **Virtual env:** `backend/venv/` — always activate before running Python commands
- **Working directory for all backend commands:** `backend/`

## Commands

```bash
# Tests
cd backend && pytest tests/ -x -q --timeout=30

# Lint (must pass before commit)
ruff check backend/ --config ruff.toml
ruff format backend/ --config ruff.toml --check

# Security audit
pip-audit -r backend/requirements.txt --ignore-vuln PYSEC-2022-42969

# Backtest (takes ~3 min)
cd backend && python scripts/backtest_technicals.py
cd backend && python scripts/backtest_technicals.py --oos

# Alembic migrations
cd backend && alembic upgrade head
```

## Architecture

```
backend/
  main.py              # FastAPI app, router mounts, lifespan
  database.py          # SQLAlchemy async engine, session factory
  config.py            # Pydantic settings (loads .env)
  routers/             # HTTP endpoints (signals, quotes, auth, billing, …)
  services/
    signal_engine.py   # Core scoring — _assemble_signal()
    signal_ml.py       # XGBoost champion/challenger gate
    scanner.py         # Async market scanner loop
    market_data.py     # OHLCV cache (Redis → in-memory fallback)
    polygon_client.py  # Polygon REST + extended-hours snapshot
    delivery_gates.py  # Sector/session/volatility filters
    macro.py           # VIX, STLFSI4, SPY trend
  tests/               # pytest suite (~762 tests)
  scripts/
    backtest_technicals.py  # 23-year MR backtest + OOS validation
```

## Key constants

| Constant | Value | File |
|---|---|---|
| `BUY_THRESH` | 50 | `backtest_technicals.py` |
| `HOLD_DAYS` | 10 | `backtest_technicals.py` |
| `FRICTION` | 0.5% round-trip | `backtest_technicals.py` |
| MR gate | RSI<42 OR BB%B<0.22 OR IBS<0.15 OR VWAP%<−0.75% | `signal_engine.py` |

## CI

File: `.github/workflows/ci.yml`
Steps: install deps → syntax check → import smoke → pytest → accuracy gate → pip-audit → ruff

**CI Python is 3.11.** Local Python is 3.14. Never use syntax that requires 3.12+:
- ❌ Backslashes inside f-string `{}` expressions
- ❌ `match` statements without `# type: ignore` if targeting 3.10

`ruff.toml` sets `target-version = "py311"` — run `ruff check` locally to catch these before push.

## Research baseline (§42 — v7.1, BUY_THRESH=50)

| Universe | WR | Avg Ret | Sharpe |
|---|---|---|---|
| Main (48 tickers, MR-only) | 60.3% | +0.63% | 0.17 |
| Sector-filtered (live-equivalent) | 59.0% | +0.64% | 0.17 |
| OOS v3 (same-sector held-out, thresh=50) | 50.0% | +0.00% | 0.00 |

See `docs/Stats.md` §42 for full analysis. Prior §41 (thresh=40): IS 60.5%/+0.57%/0.14, OOS −0.30.

## MCP servers (when Node.js is available)

```bash
# GitHub — lets Claude read PRs, CI logs, issues directly
claude mcp add github -- npx -y @modelcontextprotocol/server-github
# Set: export GITHUB_PERSONAL_ACCESS_TOKEN=<your-pat>

# SQLite — lets Claude query trading.db directly
claude mcp add sqlite -- npx -y @modelcontextprotocol/server-sqlite backend/trading.db
```
