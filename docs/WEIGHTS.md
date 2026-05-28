# Signal.Trade — Scoring Weights & Signal Gates Reference

> **Version: v6.9+** · Updated: 2026-05-27 (§40 risk gate refinements applied)
> Source of truth: `backend/services/signal_scoring.py` + `backend/services/signal_engine.py`
> **Notable changes in §40:** OSC weight 1.0→0.3, RSI removed from MR gate, VIX<20 global gate added, ATR stops tightened 2.0s/2.5t→1.0s/2.0t

---

## Family Caps & Multipliers

| Family | Cap | Multiplier | Notes |
|:---|--:|--:|:---|
| Oscillator (RSI/Stoch/WR/CCI) | ±25 | ×1.0 | Asymmetric: oversold > overbought |
| Trend (MACD/EMA/ADX) | ±28 | ×0.90 | |
| Volume (OBV/surge/divergence) | ±20 | ×0.85 | |
| MA (SMA200/50/20+slopes/z-score) | ±28 | ×1.0 | |
| Mean-Reversion (BB+RSI/squeeze/IBS) | ±18 | ×1.0 | Cap raised from ±8 after BB+RSI confluence research |

---

## Oscillator Family

| Signal | Weight | Notes |
|:---|--:|:---|
| RSI < 25 (deep oversold) | +28 | Highest-probability bounce |
| RSI < 35 (oversold) | +16 | |
| RSI > 75 (deep overbought) | −18 | Asymmetric: less reliable |
| RSI > 65 (overbought) | −10 | |
| Stochastic cross up (SK<20, SD<20) | +18 | Both in extreme zone |
| Stochastic cross up (SK<20) | +10 | Single extreme |
| Stochastic cross down (SK>80, SD>80) | −14 | Asymmetric |
| Stochastic cross down (SK>80) | −8 | |
| SK < 25 zone | +5 | |
| SK > 75 zone | −4 | |
| Williams %R ≤ −85 | +10 | Only extreme readings |
| Williams %R ≥ −15 | −8 | |
| CCI < −200 | +14 | |
| CCI < −150 | +8 | |
| CCI < −100 | +3 | |
| CCI > 200 | −12 | |
| CCI > 150 | −7 | |
| CCI > 100 | −3 | |

---

## Trend Family (×0.90 after cap)

| Signal | Weight | Notes |
|:---|--:|:---|
| MACD hist cross above zero + rising | +18 | Cross + momentum |
| MACD hist cross below zero + falling | −18 | |
| MACD cross above zero (flat) | +12 | |
| MACD cross below zero (flat) | −12 | |
| MACD positive + accelerating | +16 | Continuation > crossover |
| MACD negative + falling | −16 | |
| MACD positive + decelerating | +6 | |
| MACD negative + rising (weak) | −6 | |
| MACD bullish divergence | +20 | Price lower low, MACD higher low |
| MACD bearish divergence | −20 | |
| EMA 8/21 cross up + RVOL>1.2 | +14 | Volume-confirmed |
| EMA 8/21 cross up (no vol) | +8 | |
| EMA 8/21 cross down + RVOL>1.2 | −14 | |
| EMA 8/21 cross down (no vol) | −8 | |
| EMA 8 > EMA 21 (state) | +4 | |
| EMA 8 < EMA 21 (state) | −4 | |
| ADX > 40 + +DI > −DI | +18 | Strong trend tier |
| ADX > 40 + −DI > +DI | −18 | |
| ADX 25–40 + +DI > −DI | +10 | Moderate tier |
| ADX 25–40 + −DI > +DI | −10 | |
| ADX < 20 | 0 | No contribution — suppress chop |
| ATR expanding 5+ bars (up day) | +16 | Sustained expansion = real trend |
| ATR expanding 5+ bars (down day) | −10 | |
| ATR expanding 3–4 bars (up day) | +10 | |
| ATR expanding 3–4 bars (down day) | −10 | |
| BOS bullish | +12 | Break of structure (vectorized pivot) |
| BOS bearish | −12 | |
| MSS bullish (reversal after downtrend) | +16 | |

**RSI suppression of trend signals (post-cap):**

| Condition | Effect |
|:---|:---|
| Trend>0 + RSI>75 | trend ×0.30 |
| Trend>0 + RSI>65 | trend ×0.55 |
| Trend<0 + RSI<25 | trend ×0.30 |
| Trend<0 + RSI<35 | trend ×0.55 |

---

## Volume Family (×0.85 after cap)

| Signal | Weight | Notes |
|:---|--:|:---|
| OBV above 20-MA + slope > 0 (osc>15) | +16 | Strong confirmation |
| OBV above 20-MA + slope > 0 (osc≤15) | +8 | Weak alignment |
| OBV below 20-MA + slope < 0 (osc<−15) | −16 | |
| OBV below 20-MA + slope < 0 (osc≥−15) | −8 | |
| Volume surge >150% + OBV rising + price>SMA20 | +14 | Breakout confirm |
| Volume surge >150% + OBV falling + price<SMA20 | −14 | |
| Volume dry-up <50% | −8 | Lack of conviction |
| OBV accumulation divergence (price ↓, OBV ↑) | +12 | |
| OBV distribution divergence (price ↑, OBV ↓) | −10 | |
| Stealth accumulation (RSI<40 + RVOL≥2 + down day) | +10 | Institutional dip-buy |
| Extreme RVOL ≥3× (up day) | +10 | Catalyst/breakout |
| Extreme RVOL ≥3× (down day) | −10 | |

---

## MA Family (×1.0)

| Signal | Weight | Notes |
|:---|--:|:---|
| Price > SMA200×1.02 + slope > 0 | +18 | Strong bull + rising 200MA |
| Price > SMA200×1.01 | +12 | |
| Price < SMA200×0.98 + slope < 0 | −18 | |
| Price < SMA200×0.99 | −12 | |
| Price > SMA50 + slope > 0 | +16 | 50-day more actionable than 200-day |
| Price > SMA50 | +8 | |
| Price < SMA50 + slope < 0 | −14 | |
| Price < SMA50 | −6 | |
| Price > SMA20 + slope > 0 | +12 | Short-term trend confirm |
| Price < SMA20 + slope < 0 | −8 | |
| Price z-score < −2.0 | +14 | Statistical mean reversion |
| Price z-score < −1.5 | +7 | |
| Price z-score > 2.0 | −12 | |
| Price z-score > 1.5 | −6 | |
| Golden Cross (SMA50 > SMA200×1.005) | +10 | Reduced — late signal |
| Death Cross (SMA50 < SMA200×0.995) | −10 | |
| Above both EMA200 and SMA200 | +3 | Double confirmation |
| Below both EMA200 and SMA200 | −3 | |
| VWAP rising + price above VWAP | +6 | |
| VWAP falling + price below VWAP | −5 | |
| VWAP cross up + RVOL≥2× | +12 | High-volume VWAP reclaim |
| VWAP cross down + RVOL≥2× | −14 | |
| VP: Price above VAH + RVOL≥1.5 | +16 | Value Area High breakout |
| VP: Price below VAL + RVOL≥1.5 | −14 | |
| VP: Price at POC + ADX<20 | +8 | Magnet in ranging market |

---

## Mean-Reversion Family (×1.0)

| Signal | Weight | Notes |
|:---|--:|:---|
| BB %B < 0.05 + RSI < 35 | +18 | Full confluence — 65%+ WR |
| BB %B < 0.05 + RSI < 45 | +12 | |
| BB %B < 0.05 | +6 | |
| BB %B < 0.15 + RSI < 35 | +10 | Near lower band |
| BB %B < 0.15 + RSI < 45 | +5 | |
| BB %B > 0.95 + RSI > 65 | −14 | Asymmetric (OB less reliable) |
| BB %B > 0.95 + RSI > 55 | −8 | |
| BB %B > 0.95 | −4 | |
| BB %B > 0.85 + RSI > 65 | −8 | |
| BB %B > 0.85 + RSI > 55 | −4 | |
| BB Squeeze breakout up | +16 | Compressed volatility release |
| BB Squeeze breakout down | −16 | |
| Ranging market (ADX<20) + BB %B < 0.15 | +6 | MR favored in chop |
| IBS < 0.05 (close near day's low) | +15 | |
| IBS < 0.10 | +8 | |
| IBS > 0.90 (close near day's high) | −10 | |
| VWAP −2σ band touch | +14 | 2-sigma extension |
| VWAP +2σ band touch | −14 | |
| ATR contracting 5+ bars | +6 | Coiling = MR environment |
| ATR rank > 90th percentile | ×0.5 | High-vol suppresses MR |
| ATR rank < 10th percentile | ×1.4 | Low-vol amplifies MR |

---

## Regime Adjustment Layers (applied in order)

### Layer 1 — ADX Trend Strength

| ADX | Trend effect | MR effect | Oscillator effect |
|:---|:---|:---|:---|
| > 40 (strong) | ×1.20 | ×0.10 | ×0.30 if \|osc\| < 16 |
| 25–40 (moderate) | unchanged | ×0.40 | unchanged |
| < 25 (ranging) | ×0.30 | ×1.20 (+×1.30 if BB%B<0.10) | **×0.30** (§40: global weight, was variable) |

> **§40 note:** Oscillator total weight reduced from 1.0 to 0.3 globally. §12 alpha decomp found OSC redundant with DONCHIAN (corr=0.74); 0.3 weight acts as quality selector not signal generator (per-trade Sharpe 0.33, N=26 in §12 sweep).

### Layer 2 — Price vs SMA200

| Condition | Effect |
|:---|:---|
| Bull market (price > SMA200) + bearish MR | MR ×0.20 |
| SMA200 rising + price < SMA200×0.98 | MR ×1.30 (healthy uptrend dip) |
| SMA200 falling (slope < −0.01%) | Trend ×0.30 |

### Layer 3 — Quality Gate

≥2 signal families must score > 5 (bull) or < −5 (bear). If fewer than 2 agree, `score ×0.50`.

### Layer 4 — Volume Veto

If BUY signal AND volume dry-up (<50% avg) AND RSI ≥ 30: `score ×0.70`.

---

## Risk Gates (signal_engine.py — applied after scoring)

| Gate | Trigger | Action |
|:---|:---|:---|
| Chronic Loser Exclusion | Ticker win rate < 45% | BUY → HOLD |
| Orthogonality | < 3 independent data families AND score < 50 | BUY → HOLD |
| Technical-Only SELL | SELL with no alt-data source | SELL → HOLD |
| RVOL | RVOL < 1.2 AND non-oversold (RSI≥30) | BUY → HOLD |
| **ADX Minimum (v5.10)** | ADX < 18 AND non-oversold AND score < 45 | BUY → HOLD |
| **RSI Overbought + Weak Trend (v5.10)** | RSI>70 AND ADX<28 AND bull mkt AND score<40 | BUY → HOLD |
| ATR Minimum | ATR < 0.7% of price | BUY → HOLD |
| Low-Vol Stock | ATR < 0.8% AND (score<35 OR macro<0) | BUY → HOLD |
| Defensive Ticker Block | ticker in {KO, PEP, T, NEE, PG, USB, PNC, C, AIG, WM, MCO, TT, DE, TJX, ABBV, MRK, PFE, LLY, TMO, TXN, NKE, V, PM, WMT, APH, EOG, SYK, CVX, UPS} — BAC/TGT removed v5.12; APH/EOG/SYK/CVX/UPS added v6.1 (live 0% WR) | BUY → HOLD |
| Dollar Volume | < $5M/day | −4–8pp confidence penalty |
| STLFSI4 + VIX stress | STLFSI4>1.5 AND VIX>30 | BUY → HOLD |
| STLFSI4 + VIX elevated | STLFSI4>1.0 AND VIX>25 AND score<50 | BUY → HOLD |
| SMA200 downtrend | price < SMA200×0.99 AND RSI≥25 AND score<60 | BUY → HOLD |
| SELL uptrend alt-data | price > SMA200×1.01 AND no alt-data AND score>−45 | SELL → HOLD |
| **SPY Neutral Zone (v5.10)** | SPY within ±2% of SMA200 AND score<45 | BUY → HOLD |
| Bear + VIX | sp500_trend==down AND VIX>25 AND score<50 | BUY → HOLD |
| BUY Saturation | 7d BUY:SELL ratio>4:1 AND score<42 | BUY → HOLD |
| Broad Market Breadth | >70% S&P above 200DMA AND score<42 | BUY → HOLD |
| VIX Hard Floor | VIX>30 AND confidence<75% | BUY/SELL → HOLD |
| Mega-Cap Haircut | Mkt cap ≥$500B | −2pp confidence |
| **MR Entry Condition (v5.12 → v6.9+§40)** | score<65 AND no (BB%B<0.22 OR IBS<0.15 OR VWAP%<−0.75) | BUY → HOLD | RSI removed in §40; non-binding constraint |
| **VIX<20 Global Gate (§40)** | VIX < 20 AND _has_mr | BUY → HOLD | Mean-reversion fails when market is too calm; blocks all MR entries in low-volatility regimes |
| **Deep-Bear RSI (v5.12)** | VIX>28 AND SPY<SMA200×0.95 AND RSI≥35 | BUY → HOLD |
| **Price-SMA20 Distance (v5.12)** | score<65 AND price ≥ SMA20×0.98 (less than 2% below 20-DMA) | BUY → HOLD |
| **Day-of-Week (v5.12)** | Friday AND score<65 | BUY → HOLD |
| **Sector MR Block (v6.1 — §16a)** | Sector in {XLV, XLI, XLRE} (buy_thresh=999); calibrated hold_days/vix_min for XLK/XLF/XLY/XLP/XLC/XLE via `_SECTOR_MR_CONFIG` | BUY → HOLD (blocked sectors) |
| **Fundamental Value-Trap (v6.1)** | revenue_growth < −20% YoY AND FCF yield < −5% of market cap (yfinance) | BUY → HOLD |
| **ATR%rank Ceiling (v6.1 — §17b)** | ATR%rank > 70th percentile at MR entry | BUY → HOLD |
| **Single-Day Jump Filter (v6.1 — §17c)** | Single-day return < −6% | BUY → HOLD |
| **VIX Slope Gate (v6.1 — §17)** | VIX 3-day slope > +3pts AND VIX > 16 | BUY → HOLD |
| **IBS + SMA20 Streak (v6.1 — §17e)** | IBS < 0.15 as sole MR trigger requires ≥5 consecutive days below SMA20 (Pagonidis 2013) | BUY → HOLD |
| **Near-Earnings Revision Soft-Gate (v6.1)** | 8-14d pre-earnings AND no positive analyst revision | −4pp confidence haircut |

---

## Stop / Target Levels (`atr_levels()` function)

### Swing style (5-day hold — v5.10 calibrated → §40 refined)

| Condition | Stop mult | Target mult | R:R | Notes |
|:---|--:|--:|--:|---|
| Strong trend (ADX > 35) | 1.0× | 3.0× | 3.0 | Trend carries further, tight stop |
| High vol (ATR > 2.5% of price) | 1.5× | 2.0× | 1.3 | Wider stop for gap risk |
| Normal vol (ATR 1–2.5%) | 1.0× | 2.0× | 2.0 | **§40: tightened from 1.5×/2.0×** |
| Low vol (ATR < 1.0%) | 1.5× | 2.0× | 1.3 | **§40: tightened from 2.0×/2.5×** |

> **§40 change (2026-05-27):** Swing normal vol reduced 1.5s/2.0t → 1.0s/2.0t. §11c decomp (103 tickers, 23yr): tighter stop cuts losing trades faster while maintaining R:R 2.0 (Sharpe 0.50 vs 0.24 at 1.5×/2.0×). High-vol and ADX>35 also tuned accordingly.

### Position style (multi-day hold)

| Condition | Stop mult | Target mult |
|:---|--:|--:|
| High vol | 2.5× | 3.5× |
| Normal vol | 3.0× | 4.5× |
| Low vol | 3.5× | 5.0× |

### Intraday style

| All conditions | Stop mult | Target mult |
|:---|--:|--:|
| — | 1.5× | 2.0× |
