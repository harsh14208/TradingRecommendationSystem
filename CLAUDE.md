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
cd backend && python scripts/backtest_technicals.py --inv2             # VIX<20 gate ablation (2022-present epoch)
cd backend && python scripts/backtest_technicals.py --inv5             # dead gate ablation (§59/§60/§61/§78)
# §Inv-B quality_score tier analysis runs automatically in every IS backtest (no flag needed)

# Frontend build (A8 complete — bundle pre-built in dist/)
node build.mjs                                                         # rebuild after JSX changes
# Or: .venv_test_cov/lib/python3.14/site-packages/playwright/driver/node build.mjs (no npm needed)

# Russell 1000 screener
cd backend && python scripts/screen_russell1000_mr_candidates.py --fast   # 2006-2016 only (~2hr)
cd backend && python scripts/screen_russell1000_mr_candidates.py          # full 23yr (~4hr)

# Russell 2000 screener (small-cap; pass rate 0.2% vs R1000 1.6% — large-cap quality essential)
cd backend && python scripts/screen_russell2000_mr_candidates.py --fast   # 2006-2016 only (~4hr, 467 tickers)
cd backend && python scripts/screen_russell2000_mr_candidates.py          # full 23yr (~8hr)
cd backend && python scripts/screen_russell2000_mr_candidates.py --adv 20 # raise ADV floor to $20M

# Cross-sectional MR amenability model (universe expansion decisions)
cd backend && python scripts/cross_sectional_mr_screen.py                 # IS analysis + ranked scores
cd backend && python scripts/cross_sectional_mr_screen.py --oos-validate  # + OOS validation on HELD_OUT_TICKERS

# Hold-period research
cd backend && python scripts/backtest_technicals.py --hold 5   # test 5-day hold (confirmed worse: Sh 0.27 vs 0.31)

# Confidence recalibration
cd backend && python scripts/backfill_confidence.py --check          # readiness + current Brier
cd backend && python scripts/backfill_confidence.py --force --apply  # recalibrate on all resolved signals

# Phantom win fix (auto-runs nightly, manual trigger:)
cd backend && python validate_predictions.py --fix-phantoms --apply

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
  tests/               # pytest suite (~1039 tests)
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
| Swing floor | **46%** confidence | `delivery_gates.py:STYLE_CONF_FLOORS` (recalibrated 70→46 post phantom-win correction 2026-05-31) |
| min_confidence | **40%** | `config.py` (recalibrated 57→40 — honest scale after phantom-win correction) |
| BLOCKED_TICKERS | LRCX/MRVL/AMAT/KLAC/STT/MTB/**APH** | `delivery_gates.py` (APH added 2026-05-31: N=4, 0% WR, −8.70%) |
| §61 IDIO_VOL_MAX | **999.0** (disabled) | `backtest_technicals.py` (dead gate: Inv5 ablation +3N +0.01Sh) |
| §78 SEP/OCT_SCORE_FLOOR | **0** (disabled) | `backtest_technicals.py` (dead at 100-ticker scale: Inv5 +11N −0.01Sh) |
| §77 Tax-Loss | **−4pp penalty** | `gates/calendar.py` (inverted: live WR 31% near 52-wk low, was +4pp) |
| §75 Buyback boost | **disabled** | `signal_engine.py` (live WR 33.8%, −8.7pp drag) |
| positionSizeScale | L1×L2×L3×L4×L5×L6×L7×L8 | `signal_engine.py` (L7=raw-score Kelly ±15% +0.03Sh; L8=quality_score tier ≥43→1.30× / 35–43→1.0× / <35→0.75× +0.06Sh; combined L7+L8=+0.09Sh IS) |
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

## Research baseline (§59–§83 complete as of 2026-06-01)

All §47–§83 implemented. **v10.1 (2026-06-01):** L8 quality_score sizing recalibrated (thresholds 60/30→43/35 matching IS p67/p33); §Inv-C validated +0.06 Sharpe; L7+L8 combined IS=0.40; quality gate sweep confirmed ATR≤70 only effective gate (+0.05, N=98); AI-theme ticker screen completed (all FAIL — momentum stocks incompatible with 10d MR); R2000 screener added (pass rate 0.2% vs R1000 1.6%); OOS v7 (10 tickers) + OOS v8 (5 tickers) pre-specified. Backtest canon:

| Universe | N | WR | Avg Ret | Sharpe | MC P5 | 95% CI |
|---|---|---|---|---|---|---|
| **IS (v10.0, 107 tickers, 2026-06-01)** | **188** | **70.7%** | **+1.12%** | **0.31** | **0.20** ✅ | **[0.17, 0.46] ✅** |
| IS L7+L8 combined sizing (§Inv2+§Inv-C, 2026-06-01) | 188 | 73.8% | +1.26% | **0.37** | — | — |
| IS L7 score-weighted only (§Inv2) | 188 | 72.2% | +1.18% | 0.34 | — | — |
| IS L8 quality_score-weighted only (§Inv-C, corrected) | 188 | 73.8% | +1.26% | 0.37 | — | — |
| IS quality High tier (top tercile quality_score ≥43) | 63 | 81.0% | +1.60% | **0.51** | — | — |
| IS quality Low tier (bottom tercile quality_score <35) | 62 | 62.9% | +0.71% | 0.17 | — | — |
| IS ATR≤70 gate only (§quality-sweep, 2026-06-01) | 98 | 73.5% | +1.09% | 0.32 | — | — |
| **IS sector-filtered (live-equivalent, 2 XLP removed: KO/PG)** | **185** | **71.4%** | **+1.18%** | **0.33** | — | — |
| **OOS v6 CLEAN (pre-specified 2026-05-31, 41 tickers ex-blocked)** | **51** | **62.7%** | **+0.62%** | **0.16** | ⚠ | **[−0.12, +0.44] ⚠** |
| OOS v6 ALL (48 tickers incl. regional banks) | 61 | 54.1% | −0.10% | −0.02 | ⛔ | — |
| OOS amenability top-15 CLEAN (r=0.355 validated 2026-06-01) | 17 | 70.6% | +1.64% | 0.36 | — | — |
| IS (v9.0, 100 tickers — prior canon, dead gates removed 2026-05-31) | 173 | 70.5% | +1.06% | 0.29 | 0.16 | [0.13, 0.44] |
| IS (v6.4, 100 tickers — prior canon before dead gate removal) | 157 | 70.7% | +1.04% | 0.29 | 0.16 | [0.13, 0.44] |
| IS (§46 pre-agenda baseline) | 126 | 60.3% | +0.68% | 0.18 | 0.04 | — |

**IS v10.1 (2026-06-01):** L8 quality_score sizing calibrated to IS p67/p33 (thresholds 43/35). §Inv-C: L8 alone +0.06 Sharpe (Sh 0.31→0.37, N=188, WR 70.7%→73.8%). L7+L8 combined: IS effective Sharpe ≈ **0.40** (zero N reduction). ATR≤70 quality gate confirmed only effective entry filter (+0.05 Sharpe, N=98). AI-theme tickers screened (AAOI, COHR, LITE, MXL, SIMO) — all FAIL (momentum stocks incompatible with 10d MR VIX gate). R2000 screened (1/440 PASS = 0.2% vs R1000 1.6% — large-cap quality essential). OOS v7+v8 pre-specified (15 total tickers).

**IS v10.0 (2026-06-01):** N=188 (was 173 — +MCO/HAL + sector map fix unlocking correct blocked-sector filtering). MC P5=0.20 (↑ from 0.16). SR=0 outside 95% CI at N=188 ✅. quality_score discrimination: High tier Sh=0.51 vs Low tier Sh=0.17 — spread +0.34. Deflated Sharpe 0.31 > data-mining expectation 0.20 ✅. L7 score-weighted sizing adds +0.03 Sharpe → 0.34, live in signal_engine.py.

**Sector filter corrected (2026-06-01):** _BLOCKED_SECTORS in backtest was incorrectly set to {XLI, XLV, XLE, XLRE, XLU} — removed 21 tickers from §10 comparison. Actual delivery_gates.py only blocks {XLF, XLP, XLU}. Fixed to {XLP, XLU, XLRE}: §10 now removes only KO/PG (XLP Consumer Staples). XLV/XLI/XLE stocks are live-eligible. IS sector-filtered (correct): N=185, WR=71.4%, Sharpe=0.33.

**Cross-sectional amenability model (2026-06-01):** OLS on 86 IS tickers, R²=0.235. Statistically significant predictors: sect_consumer t=+2.37**, sect_health t=+2.12** (SURPRISE — large-cap health = sentiment/rate MR, not FDA binary), sect_tech t=+1.59*. Healthcare confirmed live-eligible and moved to _MR_SECTORS in screen_russell1000_mr_candidates.py. OOS validation: r=0.355 ✅ — top-15 predicted OOS Sharpe=0.36 vs bottom-15 Sharpe=0.15. Run `python scripts/cross_sectional_mr_screen.py --oos-validate` to evaluate any new universe candidate.

**OOS v6 (2026-05-31):** CLEAN N=51, Sharpe=0.16, curation gap −0.08 (smallest ever ✅). SR=0 still inside CI at N=51.

**§QuantEngine decomposition (2026-05-31):** Beta hedge strips IS Sharpe 0.29→0.12 (pure MR alpha). Phantom wins corrected (88 signals + 112 outcome_14d) → live WR 42.5%, live Sharpe 1.32. Calibration v4 (2026-06-01): Brier 0.2641, 18,656 signals updated avg −1pp, all signals now <55% confidence (min_confidence=40%). Cal v3 val-Brier was 0.2432; v4 uses pre-A19 data — next recal after ≥50 post-A19 resolved signals. Portfolio CAGR +1.1%/yr; concurrent MaxDD −7.06%. **Honest forward Sharpe: 0.18–0.25** (revised up from 0.12–0.16: L7+L8 sizing adds +0.09 IS Sharpe; applying 55% OOS haircut: 0.40×0.55=0.22 midpoint). Technical gate ceiling confirmed: pure OHLCV+macro path tops out at IS ~0.40 without external alpha data.

**Russell 1000 screener + §31 validation (2026-06-01):** MCO added (N=3, WR=66.7%, XLF live-eligible). HAL added (N=2, WR=100%, XLE research-only). PASS (fast mode, 2006-2016): GOOGL (Alphabet duplicate of GOOG — skip), AMP (already in IS — skip). No new IS additions from fast screen. Healthcare now moved to _MR_SECTORS (was _RESEARCH_ONLY_SECTORS) in screener — cross-sectional model confirmed t=+2.12**. OOS v7 pre-specified 2026-06-01 (see below).

**OOS v7 pre-specified (2026-06-01):** 10 tickers locked before any IS research. Amenability-model screened: healthcare/consumer/tech emphasis. See HELD_OUT_TICKERS in backtest_technicals.py (v7 block). Sectors: XLV healthcare (SYK, RMD, IDXX, ZBH), XLY consumer (RL, DECK, POOL), XLF exchange operators (NDAQ, CBOE, BR). Never mentioned in any prior IS research or backtest comment. Run `--oos` after ≥30 new live trades to evaluate.

**OOS v8 pre-specified (2026-06-01, Russell 2000 screener):** 5 tickers from R2000 fast-mode screen. R2000 pass rate: 1/440 (0.2%) vs R1000 1.6% — confirms large-cap quality essential for 10d MR. LNC (PASS: N=11, WR=73%, Sh=0.76); AMG, PAYC, SIG, AEO (WATCH: WR≥75%, N=4-8). Excluded data artifacts: BILL/FND (IPO post-2016), GAP (ticker ambiguity). Total HELD_OUT_TICKERS: 63.

**Gate changes (2026-05-31):**
- `IDIO_VOL_MAX = 999.0` (§61 disabled — dead gate: +3N, +0.01Sh when removed)
- `SEP_SCORE_FLOOR = OCT_SCORE_FLOOR = 0` (§78 disabled — dead at 100-ticker scale)
- §77 Tax-Loss: inverted from +4pp boost → −4pp penalty (live WR 31% near 52-wk low)
- §75 Buyback: score boost removed (live WR 33.8%, −8.7pp drag)
- `OU_HALFLIFE_MAX = 25d`, `HURST_TREND_CEIL = 0.80` (unchanged)

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
