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

# §QuantEngine research flags (combinable, each adds ~1 min)
cd backend && python scripts/backtest_technicals.py --beta-hedge      # strip beta: IS 0.29→0.12 pure alpha
cd backend && python scripts/backtest_technicals.py --forecast-sizing # Carver FDM: +0.04 Sharpe
cd backend && python scripts/backtest_technicals.py --portfolio        # concurrent portfolio CAGR+MaxDD
cd backend && python scripts/backtest_technicals.py --walk-forward     # BUY_THRESH OOS re-select (WF avg 0.455)

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
  tests/               # pytest suite (~916 tests)
  scripts/
    backtest_technicals.py  # 23-year MR backtest + OOS validation
    train_backtest_ml.py    # Train entry model on IS backtest outcomes
    eval_ml.py              # Evaluate both models (§1-§8)
```

## Key constants

| Constant | Value | File |
|---|---|---|
| `BUY_THRESH` | 50 | `backtest_technicals.py` |
| `HOLD_DAYS` | 10 | `backtest_technicals.py` |
| `FRICTION` | 0.5% round-trip | `backtest_technicals.py` |
| MR gate | BB%B<0.22 OR IBS<0.15 OR VWAP%<−0.75% | `signal_engine.py` (RSI removed §40) |
| Stop swing (ATR) | 1.5s/2.0t universal | `atr_levels()` / `_levels()` (§17: +0.03 Sharpe, +5.6pp WR vs 1.0s) |
| Stop ADX>35 (ATR) | 1.0s/3.0t | `backtest_technicals.py:atr_levels()` (trend — tight stop, wide target) |
| OSC weight | 1.0 | `signal_engine.py:3777` (was 0.3 §40; restored §45 — 0.3 only valid on 24-ticker subset) |
| MR weight | 0.7 | `signal_alpha_decomposition.py:314` (was 0.5, §40) |
| Sector HARD_LIMIT | 30% | `signal_engine.py` (was 50%, tightened §43) |
| Sector SOFT_LIMIT | 20% | `signal_engine.py` (was 30%, tightened §43) |
| Scanner semaphore | 8 per worker | `signal_engine.py:scan_all()` (was 15, §43 DB pool fix) |
| Swing floor | 70% confidence | `delivery_gates.py:STYLE_CONF_FLOORS` (was 62→65→70; alpha −1.028%/trade) |
| BLOCKED_TICKERS | LRCX/MRVL/AMAT/KLAC/STT/MTB | `delivery_gates.py` (semi equipment + XLF regional banks — no 10-day MR) |
| Entry model OOS AUC | 0.6399 (champion) | `data/backtest_ml_features.json` (14 tech features, 23yr IS) |
| Entry model CV-AUC | 0.6188 ± 0.1261 | purged expanding-window CV (K=5, embargo=20d) |
| Min N for live model deploy | 300 | `signal_ml.py:_MIN_LIVE_N_FOR_DEPLOYMENT` (Hanley-McNeil CI justification) |
| Min AUC delta to deploy | 0.005 | `signal_ml.py:_MIN_AUC_DELTA_TO_DEPLOY` |
| Dual model blend | 50% entry + 50% live → ×[0.75, 1.25] | `signal_ml.py:blend_confidence()` |

## CI

File: `.github/workflows/ci.yml`
Steps: install deps → syntax check → import smoke → pytest → accuracy gate → pip-audit → ruff

**CI Python is 3.11.** Local Python is 3.14. Never use syntax that requires 3.12+:
- ❌ Backslashes inside f-string `{}` expressions
- ❌ `match` statements without `# type: ignore` if targeting 3.10

`ruff.toml` sets `target-version = "py311"` — run `ruff check` locally to catch these before push.

## Research baseline (§59–§83 complete as of 2026-05-31)

All §47–§83 implemented. v6.4 (2026-05-31): Lo(2002) Sharpe CI + Deflated Sharpe output; ML deployment N-gate + AUC CI + min-delta; universe expanded 74→100 tickers; 6 new methodology integrity tests. IS CI [0.13, 0.44] — SR=0 outside 95% CI for first time ✅. Backtest canon:

| Universe | N | WR | Avg Ret | Sharpe | MC P5 | 95% CI |
|---|---|---|---|---|---|---|
| **IS (§59–§82 gates, 100 tickers)** | **157** | **70.7%** | **+1.04%** | **0.29** | **0.16** ✅ | **[0.13, 0.44] ✅** |
| IS sector-filtered (live-equivalent, 9 XLV/XLE/XLI removed) | 136 | 69.9% | +1.02% | 0.24 | — | — |
| **OOS v6 CLEAN (pre-specified 2026-05-31, 41 tickers ex-blocked)** | **51** | **62.7%** | **+0.62%** | **0.16** | ⚠ | **[−0.12, +0.44] ⚠** |
| OOS v6 ALL (48 tickers incl. regional banks) | 61 | 54.1% | −0.10% | −0.02 | ⛔ | — |
| OOS v5 CLEAN (19 tickers: ex AMAT/KLAC) | 27 | 55.6% | +0.18% | 0.05 | ⚠ | [−0.36, +0.46] ⚠ |
| OOS v3 (10 tickers) | 14 | 50.0% | +0.27% | 0.06 | ⚠ | — |
| IS (§59–§82 gates, 74 tickers — prior canon) | 114 | 67.5% | +0.98% | 0.28 | 0.13 | — |
| IS (§46 pre-agenda baseline) | 126 | 60.3% | +0.68% | 0.18 | 0.04 | — |

**IS v6.4 result (2026-05-31):** N=157, WR=70.7%, Sharpe=0.29. CI [0.13, 0.44] — SR=0 outside CI ✅. Deflated Sharpe 0.29 > 0.22 — unlikely pure data mining ✅. Temporal stability: 3/4 epochs positive.

**OOS v6 result (2026-05-31):** CLEAN (41 tickers, pre-specified before IS research): N=51, WR=62.7%, Avg=+0.62%, Sharpe=0.16. Curation bias gap: WR −2.2pp, Sharpe −0.08 vs IS sector-filtered — **smallest gap ever ✅**. OOS Sharpe ≥ 0.10 → edge generalises verdict ✅. CI [−0.12, +0.44] — SR=0 still inside ⚠ (N=51; need ≈387 for exclusion). Score-band 50–60: N=43, WR=60.5%, Sharpe=0.15 confirms edge in the dominant band.

**§QuantEngine decomposition (2026-05-31):** Beta hedge strips IS Sharpe 0.29→0.12 (pure MR alpha). Phantom wins corrected (88 signals) → live WR 42.5%, live Sharpe 1.32 (honest). Calibration recorrected: Brier 0.2432, all signals at ~42% confidence (min_confidence lowered to 40%). Portfolio CAGR +1.1%/yr (7 trades/yr, 65% idle); concurrent MaxDD −7.06%. **Honest forward Sharpe estimate: 0.12–0.16** (beta-hedged IS to OOS v6 range).

**Universe:** 100 individual stocks for IS backtest (no ETFs — ETF MR doesn't work with stock-level signal calibration). XLV/XLI/XLE/XLP tickers are research-only (blocked in live engine by §10 sector filter). 9 tickers removed for sector-filtered live-equivalent view.

**Gate calibration notes:**
- `OU_HALFLIFE_MAX = 25d` (was 12d — at 12d, threshold sat at the median, blocking 50% of signals)
- `HURST_TREND_CEIL = 0.80` (was 0.60 — large-cap equities have median Hurst ~0.71; 0.60 blocked 88–95% of signals)

**§47–§58 implementation summary:**
- §47: VIX term structure backwardation — already in `macro.py` (VIX/VIX3M ratio, +7/-4)
- §48: IVR gate — MR BUY + IVR≥50 → +5pp; IVR<20 → −3pp (`signal_engine.py`)
- §49: Put-call skew — 25d skew >0.10 → +4pp in MR BUY (`signal_engine.py`)
- §50: Piotroski F-Score — already fully implemented in `fundamentals.py` (9-point, lines 6320–6350)
- §51: Forward PE value trap — PE>30 → −5pp; PE<15 → +3pp (`signal_engine.py`)
- §52: Short interest velocity — SI down >15% → +4pp; SI up >20% → −5pp (`signal_engine.py`, data from `market_data.py`)
- §53: Post-earnings timing — REJECTED (−17.4pp WR in 35–65d window vs outside)
- §54: VIX<15 MR suspension — hard block in `delivery_gates.py`
- §55: Cross-asset macro 3/3 headwinds — hard block in `delivery_gates.py`
- §56: Kelly position sizing — VIX-conditional `positionSizeScale` in `_assemble_signal()`
- §57: Thursday DOW gate — −3pp haircut / score≥55 gate in `delivery_gates.py`
- §58: EPS revision momentum — proxied by existing Finnhub `revision_pts` in `signal_engine.py`

See `docs/Stats.md` §47–§52 for full per-strategy results. Monte Carlo MR-Only P5=0.13 → edge statistically confirmed.

## §59–§84 research agenda — implementation status (2026-05-29)

26 strategies across 7 groups. ✅ = fully wired in live engine; ⏳ = deferred/needs paid data.

| Status | Group | Sections | Notes |
|---|---|---|---|
| ✅ | Statistical/Quant | §59 OU halflife, §60 Hurst, §61 idio vol | `technicals.py` compute; `signal_engine.py` gate |
| ⏳ | Statistical/Quant | §62 VRP | Needs options per-stock IV |
| ✅ | Statistical/Quant | §63 sector cointegration | `compute_cointegration_zscore()` in `technicals.py`; Z<−2.0→+4pp; ETF histories injected from watchlist prefetch |
| ✅ | Macro extensions | §64 yield curve, §65 TRIN, §66 AD breadth, §67 FOMC, §68 T10Y rate | `macro.py` fetch; `_assemble_signal()` / `delivery_gates.py` gate |
| ✅ | Options pack | §69 GEX flip, §70 zero-DTE, §71 max pain, §72 VRP proxy | `options.py` compute + `score_options()` |
| ✅ | Fundamental quality | §73 insider clustering, §74 Beneish, §76 Altman | `edgar.py` / `fundamentals.py` compute; `signal_engine.py` gate |
| ⏳ | Fundamental quality | §75 buyback window | EDGAR 8-K parsing complexity |
| ✅ | Calendar/seasonal | §77 tax-loss window, §78 Sep/Oct seasonality | `_assemble_signal()` / `delivery_gates.py` |
| ⏳ | Calendar/seasonal | §79 Q1 rebalancing | Needs prior-year sector return |
| ✅ | Execution quality | §80 NBBO spread | `spread_pct` from `_snapshot_cache.lastQuote`; >1.0%→−10pp, >0.5%→−5pp |
| ✅ | Execution quality | §81 block prints | `get_recent_block_prints()` in `polygon_client.py`; ≥3 block buys→+5pp |
| ✅ | Portfolio construction | §82 trailingStopPct | Added to `_assemble_signal()` return dict |
| ✅ | Portfolio construction | §83 cross-signal correlation | avg pairwise corr in `scan_all()`; avg_corr>0.75→positionSizeScale cut |
| ⏳ | Portfolio construction | §84 survivorship bias | Paid Norgate/Sharadar point-in-time constituent data |

## MCP servers (when Node.js is available)

```bash
# GitHub — lets Claude read PRs, CI logs, issues directly
claude mcp add github -- npx -y @modelcontextprotocol/server-github
# Set: export GITHUB_PERSONAL_ACCESS_TOKEN=<your-pat>

# SQLite — lets Claude query trading.db directly
claude mcp add sqlite -- npx -y @modelcontextprotocol/server-sqlite backend/trading.db
```
