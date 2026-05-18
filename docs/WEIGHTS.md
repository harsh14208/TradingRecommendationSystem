Bug fix (ADX + Supertrend + Keltner were all None): Defined the tr (True Range series) and atr_s (Wilder ATR series) that were referenced but never defined. ADX, Supertrend direction, and Keltner Channels now return real values.
IBS — (close − low) / (high − low), 1-line computation
VWAP extensions — added vwap_pct_prev (for cross detection), vwap_slope_pos (3-bar VWAP trend direction), vwap_band1/2_upper/lower (σ bands using price-around-VWAP std, not Bollinger)
ATR expansion tracking — atr_expand_bars, atr_contract_bars, atr_pct_rank (252-bar percentile)
Volume Profile — vp_poc, vp_vah, vp_val via daily OHLCV volume distribution across 40 price bins over rolling 20 sessions
Market Structure — market_struct (bos_bull/bos_bear/mss_bull/below_resistance) and ms_level using 3-bar pivot highs/lows
signal_engine.py changes:

Signal	Family	Weight
IBS < 0.10 extreme oversold	mean_rev_score	+12
IBS > 0.90 extreme overbought	mean_rev_score	−10
VWAP rising + price above	ma_score	+6
VWAP falling + price below	ma_score	−5
VWAP +2σ band touch	mean_rev_score	−14
VWAP −2σ band touch	mean_rev_score	+14
VWAP cross up + RVOL ≥ 2×	ma_score	+16
VWAP cross down + RVOL ≥ 2×	ma_score	−14
RVOL ≥ 3× (catalyst)	momentum_score	±10
RVOL < 0.5 (no participation)	momentum_score	×0.5
Stealth accumulation (down + RVOL ≥ 2× + RSI < 40)	mean_rev_score	+10
ATR expanding 3+ bars up	trend_score	+12
ATR expanding 3+ bars down	trend_score	−10
ATR contracting 5+ bars	mean_rev_score	+6
ATR rank > 90%	mean_rev_score	×0.5
ATR rank < 10%	mean_rev_score	×1.4
VP: Price above VAH + RVOL ≥ 1.5	ma_score	+16
VP: Price below VAL + RVOL ≥ 1.5	ma_score	−14
VP: Price at POC + ADX < 20	ma_score	+8
BOS bullish	momentum_score	+12
BOS bearish	momentum_score	−12
MSS bullish (liquidity grab + reversal)	momentum_score	+20
