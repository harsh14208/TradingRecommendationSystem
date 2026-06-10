# Quant Engine Review: Signal.Trade

*Reviewer lens: senior quant researcher / execution engineer. Review date: 2026-06-09. Code as of commit 0e5b0f1 + working tree.*

## Executive Summary

**Overall assessment:** This is a far more honest backtest than most retail-grade systems — signal-at-close/fill-at-next-open discipline, stop-before-target intrabar priority, per-trade (non-annualized) Sharpe, block-bootstrap CIs, pre-specified held-out ticker sets, and a documented "honest forward Sharpe 0.13–0.18" that already haircuts the IS number. The core price/indicator pipeline is point-in-time clean: I found **no `.shift(-1)`-style look-ahead in any signal-time feature**.

However, three serious problems undermine specific subsystems:

1. **CRITICAL — Meta-label model train/serve skew.** The live meta-model (`predict_meta_prob`, which scales delivered confidence by 0.60–1.40×) is trained from `data/backtest_trades_is.csv`, which contains **none** of `entry_prob`, `ou_halflife`, `hurst`, `vix` (column is `vix_entry`), `rvol`, `vix_term_ratio`, `sector_momentum`, `vix_9d_ratio`, and no HMM columns. At training time 8 of 14 features are NaN and the two HMM features are the constants 0.5/0.1; at serve time all are real values. The model the assembler trusts live was effectively trained on `(atr_pct, dte_bucket, dow)` plus noise.
2. **HIGH — The survivorship "correction" can silently become a placebo.** `is_index_constituent()` regenerates `sp500_historical_constituents.json` with full-history membership for every curated ticker if the file is missing. And independent of that file, the universe itself contains no delisted names beyond four hand-coded stubs — true survivorship bias remains (the team knows; §84).
3. **HIGH — The deflated-Sharpe defense uses `n_trials=50`, but the research log documents ≳300 effective trials.** At N=205, expected max SR from 300–500 independent searches is 0.24–0.25 — **above** the reported IS Sharpe 0.23. Under an honest trial count, the canonical IS result does not clear its own data-mining bar. The OOS-CLEAN 0.13 (and especially OOS-ALL 0.04) are the numbers to believe.

**Top 3 fixes (this week):**
1. Disable `predict_meta_prob` in the assembler (or set `meta_prob=None`) until the meta-model is retrained on a trades file that actually carries its features.
2. Make `is_index_constituent()` **fail loudly** instead of generating a full-history default map; assert the loaded JSON came from the fja05680 PIT source.
3. Lag all weekly FRED series (STLFSI4, NFCI) by their publication delay (~5–7 days), not observation date — Gate 2 currently sees crisis-week stress readings days before the market did, exactly when MR entries fire.

**Top 3 research priorities:**
1. Re-run `--validate-live-gates` with publication-lagged STLFSI4/NFCI and the strict PIT file to re-establish the canon table.
2. Quantify the real trial count (count every sweep cell, gate ablation, and threshold reselect in docs/Stats.md) and report DSR against it; alternatively adopt White's Reality Check / SPA on the stored experiment registry.
3. Champion/challenger comparison on a **shared frozen test window**, not each model's own OOS window (current Δ-AUC gate compares numbers from different samples).

---

## 1. Signal Generation Findings

### 1.1 Data leakage risks

| Finding | Severity |
|---|---|
| Meta-model train/serve skew (features absent at training, real at serving) | **CRITICAL** (skew, not leakage — but worse in effect) |
| STLFSI4/NFCI keyed to observation date, not publication date (`fetch_fred_series`, backtest_technicals.py:3418-3458) — ~5-7 day look-ahead on weekly stress data, concentrated in crisis weeks | **MEDIUM-HIGH** |
| Earnings blackout uses Polygon `filing_date` (10-Q/K submission), which trails the press-release announcement by days-to-weeks (`fetch_earnings_dates_polygon`, :3355) — backtest "avoids earnings" on the wrong dates, and treats future filing dates as known in advance | MEDIUM |
| HMM regime (live): fit on trailing 252d, only last-observation posterior used — **no leakage live** ✅. But the smoothed-posterior caveat applies if anyone ever decodes historical paths for training features | LOW (live) |
| Technical features: all rolling/trailing windows in `compute_indicators()` (:858-1142) — RSI, BB%B, IBS, VWAP%, ATR rank (rolling 252d quantiles), OU half-life, Hurst all PIT-clean | ✅ clean |
| Sector peer confirmation (`scan_all`, signal_engine.py:5637-5680): contemporaneous same-batch signals only — no future info | ✅ clean |
| §63 cointegration: trailing 252-obs window, ADF-gated — PIT-clean (β fit includes the current bar, standard and acceptable) | ✅ clean |
| Fundamentals: live engine uses fresh fetches (correct PIT live); backtest **excludes** them with an explicit docstring explaining why (simulate_ticker, :2104-2112) — exemplary discipline | ✅ |

### 1.2 Feature engineering issues
- `rvol` comment says "prior 20 sessions excluding today" but `v.rolling(21).mean().shift(1)` is a 21-session mean (:983). Cosmetic, but the live engine must match exactly or the RVOL≥1.2 gate diverges at the margin.
- Dollar-volume gate (:2508-2512) uses **adjusted** close × volume. For long-history dividend payers the adjusted price understates historical dollar volume, over-blocking early-period trades. Use unadjusted price for liquidity gates.
- Live indicators are computed at scan time on intraday data while backtest indicators use completed daily bars — IBS/RSI on a partial bar is a different feature than IBS/RSI at the close. This is a live/backtest distribution gap, not leakage (live is harder), but it plausibly explains part of the live-WR shortfall. *(Question 1 below.)*

### 1.3 Meta-labeling concerns
- **Label construction is good**: triple-barrier, +2.0/−1.5 vol-units, 10d vertical barrier, barriers from entry-time ATR (PIT), GARCH variant fit *strictly before the entry bar* (train_metalabel_model.py:101-126) ✅.
- **Feature matrix is broken** (CRITICAL, above): `extract_meta_features` (:245-280) reads columns the trades CSV does not have. Verified: `data/backtest_trades_is.csv` header has no `entry_prob/ou_halflife/hurst/rvol/sector_etf/vix/vix_term_ratio/sector_momentum/vix_9d_ratio` — and `vix` exists only as `vix_entry`, so even the one available value is missed by name mismatch. The docstring calls `entry_prob` "THE key feature"; in training it is 100% NaN.
- `purged_expanding_cv` (:286-309) applies `embargo_days=20` to **row indices**, not calendar days. With ~200 trades over 23 years, 20 rows ≈ 2 years of embargo — directionally conservative, but mislabeled and will behave very differently on dense live data.
- Additional skew: memory/notes indicate `get_history(period="max")` from scripts has returned ~63 bars; if that recurs, triple-barrier forward windows silently shrink and labels degrade to the `net_pct` fallback. Add an assertion on forward-window length.

### 1.4 Calibration concerns
- The walk-forward protocol is correct in time: isotonic/Platt fit on oldest 80%, Brier validated on newest 20%, applied forward to live signals (calibration.py:231-318) ✅.
- **Stage mismatch (MEDIUM):** calibration is trained on the *final stored* confidence of past signals, but applied mid-pipeline (assembler.py:992-1003) — *before* the ML blend (:1114), overbought haircuts (:1138-1167), and the scan-level peer haircut (signal_engine.py:5666). The mapping `f(final_conf) → P(win)` is being applied to a variable that is not final confidence. Each refit then ingests signals whose confidence already passed through the previous map — an iterative isotonic-on-isotonic feedback loop. Recommendation: store and calibrate on `raw_conf` (pre-calibration), apply calibration as the **last** confidence-mutating step.
- Win label is `outcome_pct > 0` with no friction (calibration.py:214), and mixes `outcome_14d` with ~7d `outcome_pct` (:211) against a 10-day hold. Calibrated probabilities therefore answer "P(gross-positive at an inconsistent horizon)", not "P(profitable trade)".
- Brier vs naive-0.5 is reported ✅; no reliability diagram artifact is persisted — cheap to add.

---

## 2. Backtest Engine Findings

### 2.1 Survivorship bias — **HIGH**
Three layers, in decreasing order of acknowledgment:
1. **Acknowledged:** universe is hand-curated (107 tickers) using full-history research; the curation-gap methodology (IS vs pre-specified OOS tickers) is the right mitigation and is genuinely well done.
2. **Partially mitigated:** PIT constituent filter (§84/v10.6) — but `is_index_constituent()` (backtest_technicals.py:104-166) **auto-generates** a default membership file granting every curated ticker membership for 2003–2026 (with ~18 hand-coded exceptions) whenever the JSON is missing. A deleted/corrupted file silently converts the survivorship correction into a no-op while still printing "PIT Constituents" messaging. The file is also currently *modified* in the working tree — its provenance should be pinned (checksum or generated-by header).
3. **Unmitigated:** no delisted tickers with real price history exist in the universe (LEH/BSC/WM/SHLD stubs have no usable yfinance data). Every 23-year Sharpe in the canon table is conditional on "the company still exists in 2026". For a BUY-the-dip MR strategy this bias is **positive** (the dips that never recovered — the delistings — are exactly the missing sample). The §84 conclusion (paid PIT security master required) is correct; until then, every IS number should carry an explicit survivorship caveat in Stats.md.

### 2.2 Look-ahead bias — **mostly clean**
- Signal at bar-*i* close → fill at *i+1* open (:2611-2616) ✅. Stops/targets anchored to actual fill (:2643-2645) ✅. Same-bar stop checked **before** target for longs (:2668-2690) — pessimistic, correct ✅. Gap-through stops fill at `min(stop, open)` with extra slippage ✅. MR-gate inputs (`rsi/bb/ibs/vwap` at :2352-2363) are bar-*i* close values — known at decision time ✅.
- **Bug (LOW):** the no-exit fallback (:2770-2772) computes the time-exit bar as `(i+1)+(hold-1)`, ignoring `_fill_bar` — wrong by one day when `entry_delay_override=True`. Research-flag-only path, but fix it.
- VIX same-day close used for a decision at the equity close (VIX prints until 16:15 ET) — ~15 min of technical future info, immaterial. STLFSI4/NFCI publication lag is the real issue (§1.1).
- Cooldown `in_trade_until = date + max(exit_day+3, 5)` mixes trading-day `exit_day` with calendar-day arithmetic (:2897) — sloppy but conservative.

### 2.3 Execution realism — **adequate for the stated size, with gaps**
- 0.5% round-trip friction on ≥$50M-ADV large caps at next-open fills is defensible, even conservative for small retail size; a friction sweep exists (`_run_friction`).
- Stop slippage 0.10% normal / 0.15% gap-through is **thin** for true gap-throughs (an 8% overnight gap on an earnings surprise routinely costs >0.15% beyond the open). Since earnings blackout uses the wrong dates (§1.1), some of these gaps are in-sample and under-penalized.
- Shorts are disabled in the canonical backtest (`SELL_THRESH=-100`) so borrow modeling is moot there ✅; the §86 L/S model ran an explicit borrow sweep with a sensible GC assumption ✅.
- No market-impact model. Fine at 5% position size of small capital — but state the capital assumption in Stats.md so nobody scales blindly.
- `positionSizeScale` (L1–L8) is **live-only**; the backtest applies L7/L8 analogues as *reporting* weights (stats_kelly / quality sizing). Acceptable, but the canon table mixes sized and unsized Sharpes — label each row.

### 2.4 Multiple testing / overfitting — **the weakest statistical link**
- The research log itself documents §1–§86 strategies, a 14-config quality sweep, exit-sweep grids, parameter sweeps, hold-period sweeps, walk-forward threshold reselection, and ~30 gate ablations. A conservative count of effective trials is 300–1000, not 50.
- `sharpe_ci_print(..., n_trials=50)` hardcodes the DSR baseline (:3175-3219). At N=205: E[max SR | 50 trials]=0.195 (passes), **300 trials → 0.236, 500 → 0.246 (both fail vs IS 0.23)**. The ✅ printed next to "Deflated Sharpe" is an artifact of the trial count.
- Genuinely good: pre-specified OOS ticker sets (v7/v8 locked before research), OOS evaluated rarely, curation gap tracked, Lo (2002) CI printed with honest ⚠ flags when SR=0 is inside.
- **Selection on outcomes (MEDIUM):** "OOS CLEAN" excludes `_OOS_BLOCKED_TICKERS` — tickers blocked *because they lost* (live or OOS: STT/MTB "OOS v5: 0% WR"; APH on **N=4** live trades). Excluding realized losers from the OOS metric is conditioning on the outcome; the honest generalization number is OOS-ALL (Sharpe 0.04–0.05), which is reported but not headlined. Same concern for ticker-adaptive confidence floors in `check_delivery_gates` (delivery_gates.py:139-151) driven by per-ticker live win rates at unknown (likely tiny) N.
- Challenger promotion rule: Δ-AUC ≥ 0.005 with N≥300 — see §3, the comparison is across non-comparable test sets.

### 2.5 Risk metrics gaps
- `stats()` max-drawdown is computed over `pd.concat(all_trades)` in **per-ticker order, not chronological order** (:4711 → :3109-3113). The headline `max_dd` is the drawdown of an equity curve that never existed. `run_portfolio_simulation` sorts by date and is the only valid DD number; the canon table should use it exclusively.
- Drawdown is trade-close granularity everywhere — intra-trade MTM excursions (a −8% dip that recovers to −1% by exit) are invisible. MFE is tracked; MAE is not. Add MAE and a daily-MTM portfolio curve.
- No skew/kurtosis/tail-loss (CVaR) reporting. For a strategy whose loss mode is "earnings gap through the stop", the left tail is the business — report worst-5 trades and P1/P5 of per-trade returns alongside Sharpe.
- Returns: per-trade averages (arithmetic) for stats; compounding handled only in the portfolio sim — fine, since both are labeled.

---

## 3. ML Pipeline Findings

- **Labels:** live model uses `outcome_pct > 0` (signal_ml.py:444) — no friction, horizon (~7d/14d) ≠ hold (10d). Meta-model uses proper triple-barrier ✅ (but see CRITICAL skew). Entry model trains on backtest trade outcomes with purged expanding CV + embargo per docs ✅.
- **No forward-vol leakage into barrier widths:** GARCH variant fits strictly pre-entry ✅; default is entry ATR ✅.
- **Champion/challenger flaw (MEDIUM-HIGH):** `train_model()` compares the new model's OOS AUC on the *newest 30% window* against the champion's **stored** `oos_auc` from a *different, earlier window* (:535-560). AUC differences across windows at N_test≈170 have SE ≈ 0.04 — a 0.005 promotion threshold across different samples is decided by window noise, not skill. Fix: maintain a frozen rolling comparison set, score both models on it.
- **Feature hygiene:** excluding `confidence`/`raw_score` from the live model to avoid the tautological loop (:118-135) is exactly right and rarely done. ✅
- **Drift monitoring:** `validate_feature_schema` checks vector length only; `compute_rolling_auc` (90d window) monitors outcome-level drift ✅. There is **no feature-distribution monitor** (PSI/KS vs training distribution) — given the meta-model skew found above, this is the monitor that would have caught it. Add per-feature PSI logged at predict time.
- The team's own caveat is correct: 566 resolved signals in one ~7-week regime window ≈ effective N far below 566; the auto-retrain's self-gating behavior (reject at Δ−0.0011) worked as designed.

---

## 4. Live vs Backtest Gap

**Strong points (better than most shops):** phantom-win audit + nightly `validate_predictions.py --fix-phantoms`; `gate_contribution_analysis.py` per-gate live WR attribution; calibration v4 with honest Brier; rolling-AUC drift monitor; §86 deployed **shadow-only** with explicit "must not move a trade" guardrails (cross_sectional_shadow.py docstring); challenger runs as shadow scores; documented honest forward Sharpe (0.13–0.18) below the IS number. The live-WR-42% vs backtest-68% gap was investigated and root-caused rather than ignored.

**Remaining structural gaps:**
1. The live score is the backtest score plus ~50 unvalidated families (news, options, sentiment, 13F…) at different cap weights — the backtest validates a *subsystem*, not the shipped product. The MR-gate hard block at delivery (delivery_gates.py:132) is the right containment: it forces live entries back into the validated region.
2. Live delivery now requires **MR-count ≥ 2** (delivery_gates.py:127-133) while the canon IS table is built with `require_mr_count=1`. The 2-count backtest (N=154, Sh 0.21) exists but is not the headlined baseline — re-canonize on the config actually shipped.
3. Backtest fills at next-day open; live delivers intraday with extended-hours snapshots — fill-price methodology differs. Telemetry comparing assumed vs realized entry prices (signal price vs broker fill) is the missing piece; `calc_tbd_metrics.py` covers friction but per-trade fill-slippage distribution should be tracked explicitly.
4. Confidence floors/blocks adapt to live outcomes at small N (APH at N=4, ticker WR floors) — this is online overfitting to noise. Require N≥30 (the project's own standard elsewhere) before any per-ticker action.

---

## 5. Concrete Code Snippets

### Snippet 1: train_metalabel_model.py:262-277 + data/backtest_trades_is.csv — CRITICAL
```python
row = [
    float(r.get("entry_prob") or float("nan")),   # column absent → NaN, "THE key feature"
    float(r.get("ou_halflife") or float("nan")),  # absent → NaN
    float(r.get("hurst") or float("nan")),        # absent → NaN
    float(r.get("vix") or float("nan")),          # CSV column is `vix_entry` → NaN
    ...
    float(r.get("hmm_bull_prob") or 0.5),         # absent → constant 0.5
    float(r.get("hmm_trans_risk") or 0.1),        # absent → constant 0.1
```
**Risk:** The trades CSV (verified header) carries none of these. The meta-model is trained on NaN/constants for 11 of 14 features, then served real values in `assembler.py:1101-1114`, where its output scales live confidence by 0.60–1.40×. XGBoost's learned NaN-default branches route real serve-time values down paths never trained. Also `or float("nan")` maps legitimate 0.0 values to NaN.
**Recommendation:** Disable `meta_prob` in the blend immediately. Extend `--save-trades` to emit every meta feature at entry time (ou_halflife, hurst, vix, rvol, sector_etf, entry_prob via the entry model, term-structure ratios), rename `vix_entry` consistently, add a hard assertion that <20% of any feature column is NaN before training, and use `pd.isna`-aware coercion instead of `or`.

### Snippet 2: backtest_technicals.py:112-157 — HIGH
```python
if not os.path.exists(path):
    ...
    for t in all_scr_tickers:
        if t not in default_map:
            default_map[t] = [[start_all, end_all]]   # full 2003–2026 membership for everyone
    json.dump(default_map, f, indent=4)
    print(f"\n[PIT Constituents] Generated default index membership database: {path}\n")
```
**Risk:** If the PIT file is missing, the "survivorship correction" silently regenerates itself as a near-no-op (every curated ticker is a member for the whole sample) while logging success-sounding output. v10.6/v10.7 canon numbers depend on which file was on disk at run time; the file is currently modified in the working tree with no provenance check.
**Recommendation:** `raise FileNotFoundError` instead of generating defaults; embed a `"source": "fja05680/sp500@<commit>"` key in the JSON and assert on it at load.

### Snippet 3: backtest_technicals.py:3189-3195 — HIGH
```python
se = math.sqrt((1 + sr**2 / 2) / n)
...
expected_max_sr = math.sqrt(1.0 / n) * math.sqrt(2 * math.log(n_trials))   # n_trials defaults to 50
```
**Risk:** The deflated-Sharpe pass/fail is hardwired to 50 trials. The repo's own docs enumerate ≥86 strategy sections plus multi-cell sweeps — ≥300 effective trials is conservative, at which point E[max SR]≈0.24 exceeds the canonical IS 0.23 and the printed ✅ flips to ⚠.
**Recommendation:** Maintain a persistent experiment counter (each `--validate-live-gates` ablation, sweep cell, and threshold reselect increments it) and pass it as `n_trials`; or implement White's Reality Check over the saved experiment returns.

### Snippet 4: backtest_technicals.py:4711 + 3108-3113 — MEDIUM
```python
trades = pd.concat(all_trades, ignore_index=True)   # per-ticker blocks, NOT date-sorted
...
for r in rets:                                      # stats(): equity curve in this order
    cap += cap * POSITION_SIZE * (r / 100)
    max_dd = max(max_dd, (peak - cap) / peak * 100)
```
**Risk:** Headline `max_dd` is computed over an equity curve ordered AAPL-trades-then-MSFT-trades…, not chronologically. Drawdown is order-dependent; the reported number is fiction. (Sharpe/WR are order-invariant and unaffected.)
**Recommendation:** `trades.sort_values("date", inplace=True)` before `stats()`, or drop `max_dd` from `stats()` and report drawdown only from `run_portfolio_simulation` (which sorts and tracks capital).

### Snippet 5: backtest_technicals.py:3418-3455 (`fetch_fred_series` → Gate 2) — MEDIUM-HIGH
```python
raw[pd.Timestamp(o["date"])] = float(o["value"])     # keyed to OBSERVATION date
...
series = pd.Series(raw).reindex(idx).ffill()         # ffill from observation date
```
**Risk:** STLFSI4's observation date is the Friday of the index week; FRED *publishes* it the following Thursday. NFCI similarly lags. The backtest's stress gates (Gate 2, Gate 2b) therefore act on values ~5–7 days before any live system could — and weekly stress spikes coincide exactly with the crisis weeks where MR entries cluster. The docstring's "no look-ahead" claim conflates observation-dating with publication-dating.
**Recommendation:** Shift weekly series keys forward by the publication lag (FRED's `realtime_start` field gives it exactly), re-run the canon backtest, and report the delta.

### Snippet 6: signal_ml.py:535-560 — MEDIUM-HIGH
```python
if _FEATURE_FILE.exists():
    _champ_meta = json.loads(_FEATURE_FILE.read_text())
    _champion_auc = _champ_meta.get("oos_auc")        # champion's AUC from an OLD window
...
# deploy iff oos_auc > _champion_auc + 0.005          # challenger's AUC from the NEW window
```
**Risk:** The two AUCs come from different test sets/eras. With N_test≈170, the cross-window AUC noise (SE≈0.04) is ~8× the 0.005 promotion threshold; promotions/rejections are regime-window lottery outcomes.
**Recommendation:** Score champion *and* challenger on the same frozen evaluation window (e.g., the newest 30% both models held out), and require the Hanley-McNeil CIs to separate, not just the point delta.

### Snippet 7: backtest_technicals.py:2770-2772 — LOW
```python
if exit_price is None:
    idx = min((i + 1) + (_hold_days - 1), len(df) - 1)   # hardcodes i+1, ignores _fill_bar
    exit_price = float(df.iloc[idx]["Close"])
```
**Risk:** With `entry_delay_override=True` (fill at i+2) the time-exit reads the close one bar early — a subtle mis-measurement in the §17d entry-delay research results.
**Recommendation:** `idx = min(_fill_bar + _hold_days - 1, len(df) - 1)`.

### Snippet 8: services/engines/assembler.py:992-1003 vs 1114 vs signal_engine.py:5666 — MEDIUM
```python
confidence, _bin = apply_calibration(confidence, action, cal_map, regime=_cal_regime)  # step 1
...
confidence = _ml_blend(confidence, _entry_prob, _live_prob, _challenger_prob, _meta_prob)  # step 2 mutates it again
# ... later, scan_all: sig["confidence"] -= 12 (peer haircut)                              # step 3
```
**Risk:** The isotonic map was fit on *final stored* confidence but is applied two mutation steps before final. Each weekly refit then trains on outputs of the previous map — an iterative feedback loop that can drift the calibration away from any fixed target.
**Recommendation:** Persist `raw_confidence` on every signal; train calibration on raw→outcome; apply calibration as the single last step before delivery gates.

---

## 6. Recommended Roadmap

### Immediate (this week)
1. Null out `meta_prob` in `blend_confidence` callers (one-line change in assembler) until Snippet 1 is fixed.
2. Make the PIT constituents file load-or-fail (Snippet 2); pin its provenance.
3. Sort trades by date before `stats()` (Snippet 4); fix the `_fill_bar` time-exit (Snippet 7).
4. Add a feature-NaN-rate assertion to both ML trainers and a per-feature PSI log to `predict_*` paths.

### Short-term (this month)
1. Publication-lag the FRED weekly series and re-run the canon + `--validate-live-gates`; update Stats.md with before/after.
2. Regenerate `backtest_trades_is.csv` with full meta features; retrain meta-model; verify CV-AUC survives.
3. Frozen shared evaluation window for champion/challenger; store both AUCs + CIs per retrain.
4. Re-canonize the IS table on the shipped config (MR-count=2, live-equivalent sector blocks), and label which rows include sizing.
5. Move calibration to the final pipeline step; calibrate on raw confidence; align the win label to net-of-friction at the 10d horizon.

### Medium-term (this quarter)
1. Experiment registry → honest `n_trials` for DSR (or SPA test). Re-state the canon table's significance claims against it.
2. Survivorship: either budget for Norgate/Sharadar PIT data (§84) or quantify the bias bound (e.g., assume one delisting-grade loss per ticker-decade and show Sharpe sensitivity).
3. Fill-quality telemetry: per-trade signal-price vs broker-fill distribution, fed back into the friction constant.
4. Daily-MTM portfolio curve + MAE/CVaR/worst-5 reporting in every backtest summary.
5. Replace per-ticker live blocks/floors with a hierarchical (shrinkage) model or a hard N≥30 rule — stop acting on N=4.

---

## 8. Status Update — 2026-06-10 (Post-§87–§94)

**Meta-model retrain executed:**
- Fresh train on 217 trades with all 15 features (including new `ff_str` from §89).
- CV-AUC: **0.4224 ± 0.0977** — still below `_MIN_META_AUC=0.52` gate.
- Top features by importance: `vix_term_ratio` (0.088), `dow` (0.085), `hmm_trans_risk` (0.082).
- **Constraint is N (sample size), not features.** At ~50 trades/month, need ~4–6 more months to reach N=400–500 for stable AUC.
- Assembler guard removed: `predict_meta_prob()` now returns `None` when meta-model is below threshold; live signals are NOT scaled by meta_prob.
- Auto-activation: model will auto-deploy when CV-AUC crosses 0.52 on a weekly retrain.

**Factor attribution (§89b):**
- Alpha = +0.87%/day (p=0.044) — genuine idiosyncratic alpha confirmed.
- R² = 0.05 — 95% unexplained by standard factors.

**Train/serve skew status:**
- The CRITICAL finding (§1.3) about missing features in the trades CSV has been **partially addressed**:
  - `_extract_meta_features()` now reads all 15 features from the backtest trade records.
  - The backtest CSV is regenerated with `--save-trades` and includes all 15 columns.
  - However, historical trades (pre-2026-06) still lack some features (VIX term structure, sector momentum) because they were not computed at the time.
  - The current retrain uses 217 trades — all post-feature-introduction but N is still too small for stable AUC.

**Recommended next actions (unchanged from §6):**
1. Continue accumulating N until CV-AUC crosses 0.52.
2. Do NOT deploy meta-model before threshold is met.
3. Weekly retrain already live in `_weekly_ml_retrain` — no manual action needed.

---

## 7. Questions for the Team

1. During market hours, do live indicators (IBS, RSI, BB%B) use today's *partial* bar from the Polygon snapshot? If so, the live MR gate fires on a feature the backtest never saw — has the live-vs-backtest WR gap been segmented by time-of-day of signal generation?
2. What exactly is stored in `Signal.confidence` — pre- or post-peer-haircut? (Determines how bad the calibration feedback loop is.)
3. How many effective parameter trials does the team believe have been run since §1? Is anything outside docs/Stats.md (notebooks, deleted branches) unaccounted for?
4. `_OOS_BLOCKED_TICKERS` — were any of these blocked using information from the OOS runs themselves (STT/MTB cite "OOS v5")? If yes, OOS-CLEAN is partially in-sample and should be renamed.
5. Is auto-execution (broker_svc/Alpaca) live with real capital, paper, or disabled? The answer changes the urgency of the meta-model fix from "important" to "stop trading".
6. The trades CSV is regenerated by `--save-trades` — is there any versioning tying a trained model artifact to the exact CSV/commit it was trained from?
