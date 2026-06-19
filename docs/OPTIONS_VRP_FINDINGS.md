# Options / ORATS / Massive — Session Findings (2026-06-18)

Context doc for the options-volatility research done this session. Pairs with
`docs/TODO.md` §120–§125 and the memory files `orats-opportunity-model.md` /
`orats-live-engine-integration.md`. **Nothing here is wired into the live engine** —
it is all standalone research.

---

## 0. TL;DR

- The $100 of ORATS options data **cannot predict direction**, but it **reliably predicts
  the *size* of moves** — and stocks systematically move **less** than options imply
  (the variance risk premium). That short-premium edge is real and validated, but it is
  a **low reward/risk, fat-tailed** strategy whose tail is barely tested.
- We built a full standalone stack: a vol/VRP model, a fusion recommendation engine
  (direction × options-value × earnings → concrete option trades), per-trade win/size/PnL,
  and a risk-capped portfolio book.
- **You do NOT need to keep paying ORATS.** Your existing **Massive** plans (Stocks +
  Options Starter, ~$58/mo total) can rebuild the same panel for free from flat files,
  and add intraday data ORATS doesn't. The one thing Massive lacks is **deep history**
  (2-year cap; ORATS has 2007+) needed for robust multi-regime tail testing.

---

## 1. The core finding — direction vs volatility

| Question tested | Verdict |
|---|---|
| Predict **direction** (sign of forward return)? | **NO edge.** Headline L/S Sharpe 1.4–1.9 is a pure **volatility/beta tilt** — `corr(pred, IV)≈+0.5`, **within-IV-tercile IC ≈ 0** (t<1), top-decile hit rate ≈ 50%. Dead end — do not re-run. |
| Predict **move size** (magnitude)? | **YES, strongly.** `atm_iv_30d` vs next-day \|move\|: **IC +0.38, t=+67**. Walk-forward move-size forecast IC **+0.36 companies / +0.55 ETF**. |
| Is there a tradeable edge? | **YES — the variance risk premium.** Realized 2-day move ≈ **0.72× implied** (median 0.57×); **74–78% of names move LESS than implied.** |

Note: free trailing realized vol forecasts move-size *slightly better* than IV (IC 0.50 vs
0.42). So the paid data's value is **the implied move itself** (for rich-vs-cheap), not vol
forecasting.

---

## 2. The VRP edge — validated numbers (ORATS 2026 panel, purged walk-forward, h=2d)

Tail-capped short-straddle backtest on the **rich (sell-premium) cohort**
(premium ≈ 0.8× implied, stop −3× premium, 5% cost):

| Universe | Net / 2d-trade | Win | Sharpe | Worst trade | Hit tail-cap |
|---|---|---|---|---|---|
| Companies ≥$10B | **+0.82%** | 69% | +3.0 | **−32%** | **0%** |
| ETF ≥$1B | **+1.19%** | 93% | +14 | **−12%** | **0%** |
| Companies, ex-earnings proxy | +0.48% | 67% | +2.4 | **−15%** | — |

**Critical caveat: `hit-tail-cap = 0%` and uncapped ≈ capped ⇒ the 2026 sample has NO vol
spike, so the short-vol tail is UNTESTED.** Sharpe 3–14 is regime-specific/optimistic.
The earnings filter ~halves the worst case (−32% → −15%).

### 2a. The first REAL tail test — Massive 2-year backtest incl. Aug-2024 spike (companies, h=2d)
Built from Massive flat files (`scripts/massive_spike_backtest.py`), ~470 test days
2024-08 → 2026-06:

| Slice | N | Net / 2d-trade | Win | Worst | Hit-cap |
|---|---|---|---|---|---|
| **Full 2y** | — | **+0.53%** | 71% | **−16.4%** | 1% |
| **Aug-2024 spike (07-29→08-16)** | 22 | **+1.06%** | **82%** | **−5.9%** | 5% |
| Calm month (2025-05) | 231 | +0.54% | 65% | −7.5% | 0% |

**Surprising but explainable:** the short-premium book **made money *through* the Aug-2024
market-wide spike** (+1.06%/trade, 82% win, worst only −5.9%). The Aug-5 event was a **fast,
V-shaped one-day spike that mean-reverted in ~3 days** — so selling the *elevated post-spike
premium* paid off as IV collapsed. A 2-day-horizon book recovers fast from a one-day shock.

**The real tail is idiosyncratic, not market-wide.** Full-2y worst trade was **WDAY −15.4%**
(IV 62%, implied 5.6%, **realized 20.9%** — an earnings/news jump). Single-name gap risk, not
the index spike, is what hurts → reinforces the **mandatory earnings filter + leveraged-name
exclusion + diversified book**.

**Caveat that remains:** Aug-2024 was a *fast-reverting* spike. A 2-day book is most
vulnerable to a **sustained / escalating** vol regime (2008 GFC ran months; March-2020 was
weeks) — which is still **not in the downloadable 2-year window** (those are 403-gated). So
the tail is **better tested than before, but not fully**. Net 2y edge (+0.53%, Sharpe 3.0) is
lower than the 2026-only +0.82% — i.e. more honest once harder periods are included.

**Reward/risk is the honest lens:** premium-selling has terrible per-trade RR (**0.03–0.19** —
risk $300–500 to make $20–40) despite high win rates (classic short-vol). **Directional
confluence trades** (engine BUY + options signal) have far better RR (MRVL 2.0, SPY 1.33)
and dominate expected $.

---

## 3. The recommendation engine & portfolio book

`scripts/orats_recommendation_engine.py` fuses three views into one action per name:
**direction** (live `signals` table) × **VRP** (`get_vol_view`) × **earnings**
(`days_to_earnings`).

Action vocabulary:
- `SELL_CASH_SEC_PUT` — engine BUY + rich options → get paid to enter
- `BUY_STOCK` — engine BUY, options fair/cheap
- `SELL_STRANGLE` — no direction + rich + no earnings → VRP harvest (single names)
- `SELL_DEFINED_RISK` — index mode: iron condor / put spread (never naked)
- `LONG_STRADDLE` — genuinely cheap (richness < 1) + a catalyst
- `AVOID_EARNINGS` — rich IV that is an imminent earnings event
- `NO_ACTION`

Three universes: `companies` (CS/ADRC ≥$10B), `etf` (≥$1B AUM), `index` (broad-market/
sector ETFs — the VIX-analog, defined-risk only).

**Per-trade plan** (added): `win%` (empirical CDF of realized/forecast move at breakeven),
`size_$`/`contracts`/`shares` (risk-budgeted with hard concentration caps), `exp_gain_$`,
`max_loss_$`. Flags: `--capital`, `--risk-per-trade`, `--max-book-risk`, `--max-positions`,
`--max-iv-sell`.

**Portfolio book** (`build_book`): ranks by reward/risk, excludes ATM IV > 80% from sells
(kills leveraged ETFs), greedily fills to a total premium-at-risk cap → **bounds the
correlated worst case**. On $100k / 10% book risk:

| Book | Expected / 2d | Worst case (all stop) | Avg win |
|---|---|---|---|
| Companies (20 pos) | +$2,249 (2.25%) | −$6,435 (6.4%) | 66% |
| ETF (20 pos) | +$488 (0.49%) | −$4,083 (4.1%) | 63% |
| Index (7 pos) | +$311 (0.31%) | −$1,426 (1.4%) | 61% |

> Running ALL 124 company recs (no cap) = $619k notional / −$55k worst case on $100k =
> 6× over-levered. The book cap is mandatory, not optional.

**Known gotcha:** the directional leg can be **stale** — always sanity-check engine
entry/stop/target vs spot. (MRVL on 2026-06-17 had stop $298 *above* spot $295 → untradeable;
TRV and SPY were coherent.)

---

## 4. How to trade the actionable ones (the confluence trades)

- **Bullish + options RICH → sell a cash-secured put** (TRV): sell a ~30Δ put below spot,
  expiry **before earnings**, collect premium; assigned = buy the stock you wanted at a
  discount. Take profit at ~50% of premium.
- **Bullish + options FAIR/CHEAP → buy stock or a slightly-ITM call** (SPY, MRVL). Swing
  trade on the engine's hold, not 2 days.
- **No direction + RICH + no earnings → strangle** (single names) or **defined-risk
  condor/put-spread** (index). Never naked on an index.
- Requires options approval (Level 1–2). Skip leveraged ETFs and earnings names on the
  sell side.

---

## 5. VIX (§124) — the worst expression of this edge

Trading VIX is the same short-VRP bet, concentrated and stripped of diversification.
Your data argues against it: market-level VRP is thinner & tail-heavier (SPY realized/implied
**mean 0.93** vs 0.72 cross-sectional; QQQ 1.02 = no edge). It deletes diversification,
concentrates 100% into the untested tail (XIV went −96% in a day, Feb-2018), needs VIX-futures
term-structure data we don't have, and VIX ETPs (VXX/UVXY/SVXY) add decay/leverage. **Sane
market-level expression = defined-risk SPY/SPX premium via `--universe index`**, gated on the
VIX/VIX3M term structure (`macro.py` §47), never VIX ETPs.

---

## 6. Data sources — Massive vs ORATS

| Dimension | ORATS ($99/mo API, or one-time bulk) | Massive (already own, ~$58/mo) |
|---|---|---|
| IV method | smoothed vol **surface**, dividend-adj, robust thin strikes | **BS inversion on last-trade close** — noisier, no div adj, staleness |
| Downloadable history | **2007+ (all vol regimes)** | **rolling 2y** (only Aug-2024 spike) |
| Pre-computed fields | 100+ (IV rank, skew, kurtosis, GEX, term structure) | OHLCV only → compute IV/skew; **no OI/GEX/term-structure** |
| Intraday | not in $99 tier | **minute bars → HF realized vol** (ORATS doesn't give cheaply) |
| Cost | +$99/mo | $0 extra |

**Verdict / decision:** Massive is the **going-forward data source** for options IV + live
scoring. ORATS is no longer relied on for the live feed; keep it only as a **one-time
deep-history purchase** if/when you need 2018/2020 in the tail sample.

**IV-agreement sanity check — DONE (25 liquid names, 2026 overlap, 2,645 rows, 115 days):**
- **ATM IV: corr 0.996, mean\|diff\| 0.012 (1.2 vol pts)** — Massive BS-from-close IV is
  essentially identical to ORATS's smoothed surface (per-name corr 0.94–0.995: SPY 0.956,
  NVDA 0.984, AAPL 0.936, SLV 0.995). **Confirms Massive is a clean substitute for the ATM-IV
  feed that drives the VRP edge.**
- **stk_px: corr 1.000.**
- **Skew (`pc_iv_skew`): corr only 0.398, mean\|diff\| 0.045 — WEAK.** BS-on-close skew is
  noisy at the wing strikes where last-trade prices are stale; ORATS smooths them. Skew is a
  minor feature in the vol model (ATM IV dominates), so the VRP edge is unaffected — **but do
  NOT trust Massive skew for any skew-based signal** (§49 put-call gate, etc.); use ORATS or a
  smoothed fit there.

### Massive flat-file access (TESTED)
- Endpoint `https://files.massive.com`, bucket `flatfiles`. **Flat-file S3 keys are
  separate from the REST API key** — get them at `massive.com/dashboard/flat-files`,
  set `MASSIVE_S3_KEY` / `MASSIVE_S3_SECRET` (+ optional `MASSIVE_S3_ENDPOINT`).
- Paths: `us_options_opra/day_aggs_v1/YYYY/MM/YYYY-MM-DD.csv.gz`,
  `us_stocks_sip/day_aggs_v1/...` (underlying closes).
- **Downloadable on your plans (4 datasets):** options + stocks **day** aggs (using) and
  **minute** aggs (the free upgrade). Files are small: day ~3MB, minute ~23–30MB.
- **403 / not accessible:** `us_indices` (VIX/VIX3M/VVIX), options & stock `quotes`/`trades`
  (no bid-ask → IV stuck on last-trade), all futures/crypto/forex, **and anything > 2 years
  old** (2014+ options are *listed* but GetObject 403s).

---

## 7. The Massive loader (built + tested this session)

- `services/massive_options_data.py` — S3 downloader + OPRA parser
  (`O:AAPL260116C00150000` → AAPL/2026-01-16/C/150) + **BS inversion** (`scipy.brentq`) for
  ATM 30d IV + 25Δ skew + volumes → **same `orats_daily_features` schema** → consumed
  unchanged by `get_vol_view`.
- `scripts/build_massive_options_panel.py` — CLI: `--download --build --save-to-db
  --universe-from-watchlist --start --end`.
- `tests/test_massive_options_data.py` — 5 tests, green.
- **Validated on real data:** SPY ATM IV **14% → 29% → 18%** across the Aug 5 2024 spike;
  synthetic flat-vol chain recovers 20% IV / ~0 skew; BS round-trip recovers 0.2500.
- **Caveats baked in:** no OI (day-aggs), IV from last-trade close (vs ORATS smoothed),
  GEX/DEX left NaN (not needed for VRP).

### HF realized vol (§125) — the free model upgrade
`us_stocks_sip/minute_aggs_v1` → realized vol from 1-min returns. **Close-to-close
systematically understates vol on choppy days** → false "rich" sells into turbulence.
Aug-5-2024 (HF 1-min realized vol vs close move): SPY 31% vs 1.5%, AAPL 73% vs 5.3%, JPM 35%
vs 0.8% (whipsawed flat). On Aug 5 SPY IV≈29% ≈ HF-realized 31% → options were **fairly
priced**, but the close-to-close model would flag them RICH and sell into the spike.
**Action:** add `rvol_hf` to `_VOL_FEATURES` + a turbulence sell-gate. Options minute is
sparse (~12 ATM bars/day) → use "last bar ≤ 15:55" for time-consistency, liquid names only.

---

## 8. Open items / next steps

1. ✅ **DONE — Massive-vs-ORATS IV agreement:** 16,065 overlapping (ticker,date) pairs,
   140 tickers. **Per-ticker median ATM IV corr = 0.786**, mean = 0.766; top liquid names
   (AMZN, NFLX, META, NVDA, MSFT) > 0.98. **Overall (naive) ATM IV corr = 0.50** — the
   disagreement is cross-sectional/level, not within-name. **Skew corr = 0.04** — Massive
   skew is noisy; do not use it for skew signals. Live-feed decision remains **Massive**.
   ✅ **DONE — full 2-year Massive VRP straddle backtest** with Aug-2024 spike week isolated;
   see §10 for results.
2. **Wire `rvol_hf`** (HF realized vol from minute bars) into the vol model + as a sell-gate;
   re-test forecast IC and the Aug-2024 worst-trade.
3. **Add a stale-signal filter** to the recommender (drop BUY_STOCK / SELL_CSP whose
   entry/stop/target are inconsistent with spot).
4. **Live shadow** (§122): add `optionsStrategy`/`vrpRichness` to the live signal dict
   (`assembler.py`) as a logged-only field; promote after a real vol regime. VRP only, never
   the §121 direction model.
5. **§123 preconditions before any live capital:** untested tail, leveraged-ETF exclusion,
   mandatory earnings filter, P&L realism vs real chains, options routing/margin approval.
6. **Decision:** keep Massive (free) as the data source; buy ORATS bulk history *only* if a
   multi-regime tail sample is needed.

---

## 10. Session-end results (2026-06-18)

### Massive 2-year VRP straddle backtest — companies universe, h=2d
First real out-of-sample tail test, built from Massive flat files
(`data/cache_massive/massive_panel_2y.parquet`).

| Sample | N | Net / trade | Win | Sharpe | Worst | Hit-cap |
|---|---:|---:|---:|---:|---:|---:|
| Full 2y | — | **+0.53%** | **71%** | **+3.0** | **−16.4%** | **1%** |
| Aug-2024 spike (07-29 → 08-16) | — | **+1.06%** | **82%** | — | **−5.9%** | — |
| Calm month (2025-05) | — | **+0.54%** | **65%** | — | **−7.5%** | — |

- **Worst single trade:** WDAY −15.4% (IV 62%, implied 2d move 5.6%, realized 20.9%) — an
  earnings jump. This is exactly the risk the earnings filter is meant to cut.
- **Worst 8 premium-sell trades (the tail):**

  | date | ticker | IV | implied% | realized% | loss% |
  |---|---:|---:|---:|---:|---:|
  | 2025-08-11 | PSKY | 43% | 3.8% | 48.2% | −44.4% |
  | 2026-02-25 | PSKY | 72% | 6.4% | 33.0% | −26.5% |
  | 2025-08-12 | PSKY | 53% | 4.7% | 31.1% | −26.4% |
  | 2026-04-22 | INTC | 76% | 6.7% | 26.5% | −19.7% |
  | 2025-01-23 | ANET | 50% | 4.5% | 22.3% | −17.9% |
  | 2025-05-12 | UNH | 35% | 3.1% | 18.7% | −15.6% |
  | 2025-01-22 | EA | 30% | 2.7% | 18.1% | −15.4% |
  | 2026-05-28 | WDAY | 62% | 5.6% | 20.9% | −15.4% |

- **Interpretation:** the short-premium edge survives a real vol spike, but the tail is not
  benign — 1% hit the stop-cap and a single earnings event can cost −15%+. The earnings
  filter is mandatory; the book risk cap is mandatory. PSKY stands out as a repeated tail
  name (thin/spready options likely), so liquid-name filtering is also warranted.

### Massive-vs-ORATS IV agreement (2026 overlap)
- Overlap: 16,065 (ticker,date) pairs, 140 tickers.
- ATM IV 30d: overall Pearson r = **0.50**, per-ticker median r = **0.79**, top names > 0.98.
- Put-call IV skew: overall r = **0.04** — Massive skew from last-trade day-aggs is too noisy
  for skew signals.
- IV level errors: mean abs error 2.91 vol points, median 1.49 vol points; mean pct error
  8.7%, median 5.2%.
- **Conclusion:** Massive is good enough for ATM IV / VRP scoring. Do not use Massive for
  skew-sensitive strategies without smoothing or intraday refinement.

---

## 9. File & data locations

**Scripts:** `backend/scripts/{orats_opportunity_model,orats_recommendation_engine,
build_orats_panel,build_massive_options_panel,massive_spike_backtest}.py`
**Services:** `backend/services/{orats_data,massive_options_data}.py`
**Tests:** `backend/tests/test_massive_options_data.py`
**Data:** Postgres `orats_daily_features` (ORATS 2026 panel, 115d); `backend/data/cache_massive/`
(1.6GB flat files, 2024-06→2026-06 + minute samples); `data/orats_ticker_meta.json`
(Polygon shares/type cache); outputs `data/orats_{recommendations,book,vol}_<universe>_<date>.csv`.
**Docs/memory:** `docs/TODO.md` §120–§125; memory `orats-opportunity-model.md`,
`orats-live-engine-integration.md`.

**Run examples:**
```bash
cd backend
python scripts/orats_opportunity_model.py --mode vol --horizon 2 --universe etf
python scripts/orats_recommendation_engine.py --universe companies --capital 100000
# Massive flat files (set MASSIVE_S3_KEY/SECRET, endpoint https://files.massive.com):
python scripts/build_massive_options_panel.py --download --build --save-to-db \
    --start 2024-06-18 --end 2026-06-17 --universe-from-watchlist
```
