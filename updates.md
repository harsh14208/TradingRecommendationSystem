# Signal.Trade — Session Updates

## 2026-05-16 — v5.5: Validation-Driven Fixes, Quant Features & Leveraged ETF Tracker

### Context
All changes in this session were driven by a live signal validation run (`validate_predictions.py`) against 529 resolved signals (2026-04-28 → 2026-05-14). Key findings that drove the fixes:

| Metric | Value |
|--------|-------|
| Win rate (7d) | 57.7% |
| Win rate (14d) | 63.2% |
| Avg return (7d) | +2.32% |
| Avg return (14d) | +4.90% |
| Brier score | 0.2899 (0.25 = random) |
| Confidence gap | +16pp **OVERCONFIDENT** |
| Intraday win rate | 30.4% |
| Swing win rate | 38.2% |
| Position win rate | 61.4% |
| Tickers with 0% BUY win rate | BAC, KO, PEP, T, NEE, PG, USB, PNC, C, TGT, AIG, WM, MCO, TT, DE, TJX |
| Best signals | SMCI +32%, MU +28%, AMD +25% |
| 75-84% confidence band actual win rate | 48-50% |

---

### Validation & Calibration Fixes

**`backend/validate_predictions.py`**
- `_best_outcome()` now prefers `outcome_14d` over `outcome_pct` (7d) — 14d shows +4.90% avg vs +2.32%
- Horizon labels in WORST/BEST signal tables now correctly show "14d" when applicable

**`backend/services/calibration.py`**
- `_MAX_BLEND` raised 0.80 → 0.90 (more aggressive correction toward empirical win rates)
- `_N_FULL` lowered 30 → 20 (full blend activates sooner)
- Calibration query now reads `outcome_14d` when available, falls back to `outcome_pct`
- Clamp updated from [35, 84] → [35, 72]

**`backend/services/signal_engine.py`** — confidence ceiling
- Hard ceiling lowered from 84% → 72% at all 6 cap/clamp sites:
  - `_score_to_action()` initial ceiling
  - Historical win rate adjustment
  - Risk-free rate yield dampener boost
  - Final hard ceiling in `_assemble_signal()`
  - Peer confirmation post-processing
  - Supply chain propagation post-processing
- Basis: 75-84% confidence bands empirically win at only 48-50%

**`backend/services/signal_engine.py`** — signal style
- Intraday style retirement (2026-05-10) reverted; three-way `intraday / swing / position` routing restored

**`backend/services/signal_engine.py`** — defensive-ticker BUY gate
- 16 tickers with validated 0% BUY win rate (≥3 signals each) now gate BUY → HOLD with a Risk Gate rationale card: BAC, KO, PEP, T, NEE, PG, USB, PNC, C, TGT, AIG, WM, MCO, TT, DE, TJX
- Complements existing ATR<0.8% gate (which catches low-vol defensives) — this gate catches higher-ATR names like banks and retail

---

### Quant Features (free-data only, zero new API costs)

**`backend/services/macro.py`** — FRED credit spreads
- Added `BAMLH0A0HYM2` (ICE BofA US HY OAS spread) and `BAMLC0A0CM` (IG OAS spread) to the existing FRED `asyncio.gather()` call — both free, FRED key already configured
- HY scoring: >600bps → −10 (crisis), >450bps → −5 (stress), <300bps → +4 (risk-on)
- IG scoring: >200bps → −4 (broad caution)
- Replaces the indirect HYG ETF price proxy with the actual underlying spread series

**`backend/services/news.py`** — analyst revision momentum
- `_fetch_analyst_recs()` already called Finnhub `recommendation_trends` returning 4 months of data but only read `raw[0]`
- Now also reads `raw[1]` (prior month), computes `revision_pts = bull_delta − bear_delta` (capped ±8)
- `bull_delta = (strongBuy×2 + buy)[current] − (strongBuy×2 + buy)[prior]`
- Zero additional API calls

**`backend/services/signal_engine.py`** — analyst revision scoring block
- New block after the static consensus block: fires when `|rev_pts| ≥ 2`
- +rev_pts → "Analyst Upgrade Momentum" rationale card; −rev_pts → "Analyst Downgrade Momentum"
- One of the most documented equity alpha factors (SUE effect / earnings revision momentum)

**`backend/services/signal_engine.py`** — cross-sectional universe ranking
- Added to tail of `scan_all()`, after sector peer confirmation and supply chain propagation
- Requires ≥10 directional signals in the scan batch to be meaningful
- Sorted by confidence, percentile rank computed: top decile +3pp, top quartile +1.5pp; bottom quartile −1.5pp, bottom decile −3pp
- Capped at [35, 72]; each adjusted signal gets a "Cross-Sectional" rationale card with universe rank percentile
- Converts the engine from absolute scoring (each ticker in isolation) to relative scoring (how does this ticker compare to the full universe right now) — the approach used in all production quant fund models

**`backend/services/signal_engine.py`** — beta in signal dict
- `info["beta"]` was already fetched from yfinance but not returned in the signal dict
- Added `"beta": info.get("beta")` to the `_assemble_signal()` return dict
- Exposes SPY beta for beta-adjusted position sizing in PositionCalc

**`backend/routers/signals.py`** — alpha decay by source endpoint
- New `GET /api/signals/alpha-decay` endpoint
- Queries all resolved signals, unpacks each signal's `sources` JSON array (no schema change needed), and computes per-source win rate + avg return at each of the four horizons: 1d, 3d, 7d, 14d
- Parameters: `min_n` (default 3) — minimum resolved signals per source to include
- 5-minute in-memory cache (same pattern as `/backtest`)
- Use case: reveals which scoring families have real edge at which horizons. E.g. "RSI Oversold h1d=44%, h14d=71%" means the entry signal is short-lived noise but the underlying setup has long-horizon edge — should generate position signals, not intraday

---

### Leveraged & Inverse-Leveraged ETF Tracker

**`backend/services/signal_engine.py`** — `_LEVERAGED_ETFS` frozenset
- 52 tickers: 3× bull (TQQQ, UPRO, SPXL, SOXL, TECL, FAS, TNA, LABU, WEBL, FNGU, NAIL, DPST, YINN, DRN, TMF, HIBL, MIDU, GUSH, NUGT, JNUG + 2× UCO/SSO/QLD/ROM/UWM), 3× bear (SQQQ, SPXS, SPXU, SOXS, TECS, FAZ, TZA, LABD, FNGD, YANG, DRV, TMV, HIBS, SRTY, DRIP, DUST, JDST + 2× SCO/SDS/QID/REW/TWM)
- Module-level frozenset, single source of truth used by all three ETF guards below

**`backend/services/signal_engine.py`** — fundamentals bypass
- Immediately after `_fetched` is unpacked in `generate_signal()`, if `ticker in _LEVERAGED_ETFS`:
  - `fundamentals = {}`, `earnings_cal = {}`, `earnings_surp = {}`, `insider = {}`, `analyst_recs = {}`, `congress = {}`
  - All downstream scoring blocks already guard on `if fundamentals:` / `if insider:` etc. — clean bypass, no wasted API calls
  - Workers still launch (they're async fire-and-forget) but their results are silently ignored

**`backend/services/signal_engine.py`** — style cap + disclosure card
- If style derivation assigns "position" for a leveraged ETF → forced back to "swing"
  - Basis: daily-rebalancing products lose 2–8% NAV per round-trip to volatility decay; position-style hold times make target prices meaningless
- Every leveraged ETF signal gets a "Risk Gate" rationale card disclosing: multiplier (2× or 3×), direction (Bull/Bear), decay risk, fundamentals bypass, ≤5 day hold recommendation, ⅓ position size recommendation

**`backend/main.py`** — watchlist seed
- 45 new leveraged ETF tickers added to `DEFAULT_TICKERS` under clearly labelled comment blocks
- Seed now covers ~210 tickers total (up from 164)
- Seed only fires on first startup or when <20 active tickers exist — existing DB is unaffected

**`backend/services/market_data.py`** — company names
- All 52 leveraged ETFs added to `COMPANY_NAMES` with full display name and `(3×)` / `(−3×)` / `(2×)` suffix
- Suffix is visible in the signal feed header, making leverage immediately clear to users

**`backend/services/sector.py`** — sector mappings
- All 52 leveraged ETFs mapped to their underlying's sector ETF:
  - SOXL/SOXS, TECL/TECS, QLD/QID, ROM/REW, UPRO/SPXL/SPXS/SPXU, SSO/SDS, HIBL/HIBS, WEBL/FNGU/FNGD → `XLK`
  - FAS/FAZ, DPST → `XLF`
  - TNA/TZA, UWM/TWM, SRTY, MIDU → `XLI`
  - GUSH/DRIP, UCO/SCO → `XLE`
  - LABU/LABD → `XLV`
  - NUGT/DUST, JNUG/JDST → `XLB`
  - DRN/DRV → `XLRE`
  - TMF/TMV → `XLU`
  - YINN/YANG → `XLC`
  - NAIL → `XLI`
- Enables sector peer confirmation and sector RS scoring to work correctly for leveraged ETFs

---

### Git

```
114ecc4 feat: quant improvements, leveraged ETF tracker, validation fixes
```

9 files changed, 490 insertions(+), 38 deletions(-)
