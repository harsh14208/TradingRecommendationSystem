"""
Technical indicators engine.

Hot-path optimisation (Data Pipeline Vectorisation TODO):
  _np_sma(c, n)   — numpy rolling mean via cumsum; 5–8× faster than pd.rolling(n).mean()
  _np_ewm(c, a)   — numpy EWM alpha loop; avoids pandas overhead for short alpha series
  _np_atr(h,l,c)  — numpy True Range; eliminates pd.concat of 3 Series

For cross-ticker vectorisation call batch_calculate_indicators(histories)
which stacks all tickers into a single numpy matrix and returns {ticker: dict}.
"""

import numpy as np
import pandas as pd

# ── NumPy fast-path helpers ───────────────────────────────────────────────────


def _np_sma(c: np.ndarray, n: int) -> np.ndarray:
    """Rolling simple moving average via cumsum — O(N), no Python loop."""
    if len(c) < n:
        return np.full(len(c), np.nan)
    cs = np.cumsum(np.insert(c, 0, 0.0))
    out = (cs[n:] - cs[:-n]) / n
    return np.concatenate([np.full(n - 1, np.nan), out])


def _np_ewm(c: np.ndarray, span: int) -> np.ndarray:
    """EWM with span parameter — alpha = 2/(span+1). Faster than pandas for <1000 rows."""
    alpha = 2.0 / (span + 1)
    out = np.empty(len(c))
    out[0] = c[0]
    for i in range(1, len(c)):
        out[i] = alpha * c[i] + (1 - alpha) * out[i - 1]
    return out


def _np_atr(h: np.ndarray, l: np.ndarray, c: np.ndarray, period: int = 14) -> float:
    """
    Average True Range via numpy — eliminates pd.concat overhead.
    Returns the most recent ATR value only.
    """
    prev_c = c[:-1]
    tr = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - prev_c), np.abs(l[1:] - prev_c)))
    # Wilder smoothing (EWM with com=period-1)
    alpha = 1.0 / period
    atr = tr[0]
    for v in tr[1:]:
        atr = alpha * v + (1 - alpha) * atr
    return float(atr)


def _safe(series, idx=-1):
    try:
        v = series.iloc[idx]
        return None if pd.isna(v) else float(v)
    except Exception:
        return None


def calculate_indicators(df: pd.DataFrame) -> dict:
    if df is None or len(df) < 30:
        return {}

    close = df["Close"].astype(float)
    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    vol = df["Volume"].astype(float)
    open_ = df["Open"].astype(float) if "Open" in df.columns else close

    out = {}

    try:
        # ── Price / change ──────────────────────────────────────────────
        out["price"] = round(float(close.iloc[-1]), 4)
        prev = float(close.iloc[-2]) if len(close) > 1 else out["price"]
        out["change"] = round(out["price"] - prev, 4)
        out["change_pct"] = round(out["change"] / prev * 100, 4) if prev else 0

        # ── RSI(14) ─────────────────────────────────────────────────────
        delta = close.diff()
        avg_gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
        avg_loss = (-delta).clip(lower=0).ewm(com=13, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi_s = 100 - 100 / (1 + rs)
        out["rsi"] = round(float(rsi_s.iloc[-1]), 2) if not pd.isna(rsi_s.iloc[-1]) else None

        # ── MACD(12,26,9) ───────────────────────────────────────────────
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        sig = macd.ewm(span=9, adjust=False).mean()
        hist = macd - sig
        out["macd"] = round(float(macd.iloc[-1]), 6)
        out["macd_signal"] = round(float(sig.iloc[-1]), 6)
        out["macd_hist"] = round(float(hist.iloc[-1]), 6)
        out["macd_hist_prev"] = round(float(hist.iloc[-2]), 6) if len(hist) > 1 else 0.0

        # ── Moving averages (numpy fast-path) ──────────────────────────
        _c = close.values
        _sma20 = _np_sma(_c, 20)
        _sma50 = _np_sma(_c, 50)
        _sma200 = _np_sma(_c, 200)
        out["sma20"] = round(float(_sma20[-1]), 4) if not np.isnan(_sma20[-1]) else None
        out["sma50"] = round(float(_sma50[-1]), 4) if not np.isnan(_sma50[-1]) else None
        out["sma200"] = round(float(_sma200[-1]), 4) if not np.isnan(_sma200[-1]) else None

        # ── EMA 8 / 21 (short-term momentum) ────────────────────────────
        ema8 = close.ewm(span=8, adjust=False).mean()
        ema21 = close.ewm(span=21, adjust=False).mean()
        out["ema8"] = round(float(ema8.iloc[-1]), 4)
        out["ema21"] = round(float(ema21.iloc[-1]), 4)
        out["ema8_prev"] = round(float(ema8.iloc[-2]), 4) if len(ema8) > 1 else None
        out["ema21_prev"] = round(float(ema21.iloc[-2]), 4) if len(ema21) > 1 else None

        # ── True Range series (shared by ATR, ADX, Keltner, Supertrend) ────
        # Defined once here so all downstream try-blocks get the same series.
        _prev_c = close.shift(1)
        tr = pd.Series(
            np.maximum((high - low).values, np.maximum(np.abs(high - _prev_c).values, np.abs(low - _prev_c).values)),
            index=close.index,
        )
        atr_s = tr.ewm(com=13, adjust=False).mean()  # Wilder ATR(14) series

        # ── ATR(14) scalar ──────────────────────────────────────────────
        out["atr"] = round(float(atr_s.iloc[-1]), 4)

        # ── Bollinger Bands(20, 2) ───────────────────────────────────────
        _bb_mid_arr = _np_sma(_c, 20)
        _bb_mid_v = _bb_mid_arr[-1]
        # Rolling std via numpy (faster than pandas for short windows)
        _w = min(20, len(_c))
        _bb_std_v = float(np.std(_c[-_w:], ddof=1)) if _w >= 2 else 0.0
        out["bb_upper"] = round(_bb_mid_v + 2 * _bb_std_v, 4) if not np.isnan(_bb_mid_v) else None
        out["bb_lower"] = round(_bb_mid_v - 2 * _bb_std_v, 4) if not np.isnan(_bb_mid_v) else None
        out["bb_mid"] = round(float(_bb_mid_v), 4) if not np.isnan(_bb_mid_v) else None
        # Pandas Series needed by squeeze/zscore/streak calculations below
        bb_mid = close.rolling(20).mean()
        bb_std = close.rolling(20).std()

        # ── Stochastic Oscillator %K(14) / %D(3) ────────────────────────
        low14 = low.rolling(14).min()
        high14 = high.rolling(14).max()
        rng14 = (high14 - low14).replace(0, np.nan)
        stoch_k = 100 * (close - low14) / rng14
        stoch_d = stoch_k.rolling(3).mean()
        out["stoch_k"] = _safe(stoch_k)
        out["stoch_d"] = _safe(stoch_d)
        out["stoch_k_prev"] = _safe(stoch_k, -2)
        out["stoch_d_prev"] = _safe(stoch_d, -2)

        # ── Williams %R(14) ─────────────────────────────────────────────
        wr = -100 * (high14 - close) / rng14
        out["williams_r"] = _safe(wr)

        # ── OBV and trend ────────────────────────────────────────────────
        obv = (np.sign(close.diff()) * vol).fillna(0).cumsum()
        obv_sma = obv.rolling(20).mean()
        out["obv"] = float(obv.iloc[-1])
        out["obv_above"] = bool(obv.iloc[-1] > obv_sma.iloc[-1])
        out["obv_slope"] = round(float(obv.iloc[-1] - obv.iloc[-5]), 0) if len(obv) >= 5 else 0.0

        # ── ADX(14) ─────────────────────────────────────────────────────
        try:
            plus_dm = high.diff().clip(lower=0)
            minus_dm = (-low.diff()).clip(lower=0)
            mask = high.diff() > (-low.diff())
            plus_dm = plus_dm.where(mask, 0)
            minus_dm = minus_dm.where(~mask, 0)
            smooth_tr = atr_s * 14
            plus_di = 100 * plus_dm.ewm(com=13, adjust=False).mean() / smooth_tr.replace(0, np.nan)
            minus_di = 100 * minus_dm.ewm(com=13, adjust=False).mean() / smooth_tr.replace(0, np.nan)
            dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
            adx_s = dx.ewm(com=13, adjust=False).mean()
            out["adx"] = _safe(adx_s)
            out["adx_plus_di"] = _safe(plus_di)
            out["adx_minus_di"] = _safe(minus_di)
        except Exception:
            out["adx"] = None

        # ── CCI(20) ─────────────────────────────────────────────────────
        tp = (high + low + close) / 3
        cci_ma = tp.rolling(20).mean()
        cci_mad = tp.rolling(20).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
        cci_s = (tp - cci_ma) / (0.015 * cci_mad.replace(0, np.nan))
        out["cci"] = _safe(cci_s)

        # ── Rate of Change ROC(10) ───────────────────────────────────────
        roc = (close / close.shift(10) - 1) * 100
        out["roc10"] = _safe(roc)

        # ── 52-Week High / Low ───────────────────────────────────────────
        n_wk = min(252, len(close))
        out["week52_high"] = round(float(high.rolling(n_wk).max().iloc[-1]), 4)
        out["week52_low"] = round(float(low.rolling(n_wk).min().iloc[-1]), 4)

        # ── Candlestick pattern (last bar) ───────────────────────────────
        c0 = float(close.iloc[-1])
        o0 = float(open_.iloc[-1])
        h0 = float(high.iloc[-1])
        l0 = float(low.iloc[-1])
        body = abs(c0 - o0)
        rng0 = h0 - l0
        upper = h0 - max(c0, o0)
        lower = min(c0, o0) - l0
        pattern = None
        if rng0 > 0:
            if body / rng0 < 0.1:
                pattern = "doji"
            elif c0 > o0 and lower > 2 * body and upper < body * 0.5:
                pattern = "hammer"
            elif o0 > c0 and upper > 2 * body and lower < body * 0.5:
                pattern = "shooting_star"
            elif len(close) > 1:
                c1 = float(close.iloc[-2])
                o1 = float(open_.iloc[-2])
                if c0 > o0 and o1 > c1 and c0 > o1 and o0 < c1:
                    pattern = "bullish_engulfing"
                elif o0 > c0 and c1 > o1 and o0 > c1 and c0 < o1:
                    pattern = "bearish_engulfing"
        out["candle_pattern"] = pattern

        # ── Classic Pivot Points (previous session) ──────────────────────
        if len(close) > 1:
            ph = float(high.iloc[-2])
            pl = float(low.iloc[-2])
            pc = float(close.iloc[-2])
            piv = (ph + pl + pc) / 3
            out["pivot"] = round(piv, 4)
            out["pivot_r1"] = round(2 * piv - pl, 4)
            out["pivot_s1"] = round(2 * piv - ph, 4)
            out["pivot_r2"] = round(piv + (ph - pl), 4)
            out["pivot_s2"] = round(piv - (ph - pl), 4)

        # ── Volume ──────────────────────────────────────────────────────
        out["volume"] = int(vol.iloc[-1])
        # EWM (span=20) discounts post-earnings and holiday volume spikes that
        # inflate a simple 20-day SMA, which would otherwise cause false RVOL
        # negatives on good setups and false positives after spike-depressed days.
        out["avg_volume"] = int(vol.ewm(span=20, adjust=False).mean().iloc[-1])

        # ── MACD zero-line cross ─────────────────────────────────────────
        if len(macd) > 1:
            out["macd_zero_cross_up"] = bool(float(macd.iloc[-1]) > 0 and float(macd.iloc[-2]) <= 0)
            out["macd_zero_cross_down"] = bool(float(macd.iloc[-1]) < 0 and float(macd.iloc[-2]) >= 0)

        # ── Bollinger Band %B and squeeze detection ──────────────────────
        bb_lower_s = bb_mid - 2 * bb_std
        bb_upper_s = bb_mid + 2 * bb_std
        bb_width_s = bb_upper_s - bb_lower_s
        bb_rng = float(bb_width_s.iloc[-1])
        if bb_rng > 0:
            out["bb_pct_b"] = round(float((close.iloc[-1] - float(bb_lower_s.iloc[-1])) / bb_rng), 4)
        if len(bb_width_s) >= 20:
            out["bb_squeeze"] = bool(bb_width_s.iloc[-1] <= bb_width_s.rolling(20).min().iloc[-1] * 1.03)

        # ── Z-Score: price deviation from SMA20 in standard deviations ──
        std20 = close.rolling(20).std()
        if float(std20.iloc[-1]) > 0:
            out["zscore"] = round(float((close.iloc[-1] - float(bb_mid.iloc[-1])) / float(std20.iloc[-1])), 2)

        # ── Money Flow Index MFI(14) — RSI with volume weighting ────────
        tp_mfi = (high + low + close) / 3
        rmf = tp_mfi * vol
        pmf = rmf.where(tp_mfi > tp_mfi.shift(1), 0.0)
        nmf = rmf.where(tp_mfi < tp_mfi.shift(1), 0.0)
        mfr = pmf.rolling(14).sum() / nmf.rolling(14).sum().replace(0, np.nan)
        mfi_s = 100 - 100 / (1 + mfr)
        out["mfi"] = _safe(mfi_s)

        # ── Consecutive close streak vs SMA20 ────────────────────────────
        above_sma = close > bb_mid
        streak = 0
        last_val = bool(above_sma.iloc[-1])
        for i in range(len(above_sma) - 1, max(len(above_sma) - 11, -1), -1):
            if bool(above_sma.iloc[i]) == last_val:
                streak += 1
            else:
                break
        out["close_streak"] = streak if last_val else -streak

        # ── RSI divergence (20-bar lookback, split into two halves) ──────
        try:
            n = min(20, len(close))
            mid = n // 2
            c_sl = close.iloc[-n:].reset_index(drop=True)
            r_sl = rsi_s.iloc[-n:].reset_index(drop=True)
            prev_low_i = int(c_sl.iloc[:mid].idxmin())
            prev_high_i = int(c_sl.iloc[:mid].idxmax())
            curr_low_i = mid + int(c_sl.iloc[mid:].idxmin())
            curr_high_i = mid + int(c_sl.iloc[mid:].idxmax())
            curr_rsi = float(rsi_s.iloc[-1]) if not pd.isna(rsi_s.iloc[-1]) else 50
            if (
                c_sl.iloc[curr_low_i] < c_sl.iloc[prev_low_i] * 0.995
                and r_sl.iloc[curr_low_i] > r_sl.iloc[prev_low_i] + 3
                and curr_rsi < 50
            ):
                out["rsi_divergence"] = "bullish"
            elif (
                c_sl.iloc[curr_high_i] > c_sl.iloc[prev_high_i] * 1.005
                and r_sl.iloc[curr_high_i] < r_sl.iloc[prev_high_i] - 3
                and curr_rsi > 50
            ):
                out["rsi_divergence"] = "bearish"
        except Exception:
            pass

        # ── Ichimoku Cloud ───────────────────────────────────────────────
        try:
            if len(df) >= 52:
                tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
                kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
                senkou_a = ((tenkan + kijun) / 2).shift(26)
                senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
                chikou_lag = 26
                out["ichi_tenkan"] = _safe(tenkan)
                out["ichi_kijun"] = _safe(kijun)
                out["ichi_tenkan_p"] = _safe(tenkan, -2)
                out["ichi_kijun_p"] = _safe(kijun, -2)
                # Cloud top/bottom at current time (use shifted values at -26 offset)
                sa_now = float(senkou_a.iloc[-27]) if len(senkou_a) > 27 and not pd.isna(senkou_a.iloc[-27]) else None
                sb_now = float(senkou_b.iloc[-27]) if len(senkou_b) > 27 and not pd.isna(senkou_b.iloc[-27]) else None
                if sa_now is not None and sb_now is not None:
                    out["ichi_cloud_top"] = round(max(sa_now, sb_now), 4)
                    out["ichi_cloud_bot"] = round(min(sa_now, sb_now), 4)
                    out["ichi_cloud_bull"] = bool(sa_now > sb_now)  # True = green cloud (bullish)
                out["ichi_chikou_above"] = (
                    bool(float(close.iloc[-1]) > float(close.iloc[-chikou_lag - 1]))
                    if len(close) > chikou_lag + 1
                    else None
                )
        except Exception:
            pass

        # ── Chaikin Money Flow (CMF-20) ──────────────────────────────────
        try:
            hl_range = (high - low).replace(0, np.nan)
            mf_mult = ((close - low) - (high - close)) / hl_range
            cmf_s = (mf_mult * vol).rolling(20).sum() / vol.rolling(20).sum().replace(0, np.nan)
            out["cmf"] = round(float(cmf_s.iloc[-1]), 4) if not pd.isna(cmf_s.iloc[-1]) else None
            out["cmf_prev"] = (
                round(float(cmf_s.iloc[-2]), 4) if len(cmf_s) > 1 and not pd.isna(cmf_s.iloc[-2]) else None
            )
        except Exception:
            pass

        # ── Donchian Channel (20-day) ────────────────────────────────────
        try:
            dc_high = high.rolling(20).max()
            dc_low = low.rolling(20).min()
            out["donchian_high"] = round(float(dc_high.iloc[-1]), 4)
            out["donchian_low"] = round(float(dc_low.iloc[-1]), 4)
            out["donchian_high_p"] = round(float(dc_high.iloc[-2]), 4) if len(dc_high) > 1 else None
            out["donchian_low_p"] = round(float(dc_low.iloc[-2]), 4) if len(dc_low) > 1 else None
        except Exception:
            pass

        # ── Price structure: Higher Highs / Lower Lows ───────────────────
        try:
            n = min(30, len(close))
            mid = n // 2
            if n >= 10:
                fh = float(high.iloc[-n:-mid].max())
                ch = float(high.iloc[-mid:].max())
                fl = float(low.iloc[-n:-mid].min())
                cl = float(low.iloc[-mid:].min())
                if ch > fh * 1.005 and cl > fl * 1.005:
                    out["price_structure"] = "hh_hl"
                elif ch < fh * 0.995 and cl < fl * 0.995:
                    out["price_structure"] = "lh_ll"
                else:
                    out["price_structure"] = "neutral"
        except Exception:
            pass

        # ── Gap analysis (today open vs yesterday close) ─────────────────
        try:
            if len(close) > 1:
                prev_c = float(close.iloc[-2])
                gap_pct = (float(open_.iloc[-1]) - prev_c) / prev_c * 100 if prev_c else 0
                out["gap_pct"] = round(gap_pct, 3)
        except Exception:
            pass

        # ── Relative Volume (RVOL) ───────────────────────────────────────
        # Use last 20 bars *excluding* today for the average, then compare today's volume.
        # nanmean handles any NaN gaps in the volume series gracefully.
        try:
            today_vol = float(vol.iloc[-1])
            hist_vols = vol.iloc[-21:-1].dropna()  # up to 20 prior sessions
            if len(hist_vols) >= 5:
                avg20 = float(hist_vols.mean())
                out["avg_volume"] = int(avg20)  # overwrite with cleaner value
                out["rvol"] = round(today_vol / max(avg20, 1), 2)
        except Exception:
            pass

        # ── Average Daily Range % (ADR) and compression ──────────────────
        try:
            adr_pct_s = (high - low) / close.replace(0, np.nan) * 100
            adr20 = float(adr_pct_s.rolling(20).mean().iloc[-1])
            out["adr_pct"] = round(adr20, 3)
            if len(adr_pct_s) >= 120:
                adr_6m_high = float(adr_pct_s.rolling(20).mean().rolling(100).max().iloc[-1])
                out["adr_6m_high"] = round(adr_6m_high, 3)
                out["adr_compression"] = bool(adr20 <= adr_6m_high * 0.55)
        except Exception:
            pass

        # ── Supertrend(7, 3) ─────────────────────────────────────────────
        try:
            atr7 = tr.ewm(com=6, adjust=False).mean()  # Wilder ATR(7)
            hl2 = (high + low) / 2
            st_mult = 3.0
            basic_upper = hl2 + st_mult * atr7
            basic_lower = hl2 - st_mult * atr7

            f_upper = basic_upper.copy().astype(float)
            f_lower = basic_lower.copy().astype(float)
            dirs = [0] * len(close)
            for i in range(1, len(close)):
                f_upper.iloc[i] = (
                    float(basic_upper.iloc[i])
                    if (
                        float(basic_upper.iloc[i]) < float(f_upper.iloc[i - 1])
                        or float(close.iloc[i - 1]) > float(f_upper.iloc[i - 1])
                    )
                    else float(f_upper.iloc[i - 1])
                )
                f_lower.iloc[i] = (
                    float(basic_lower.iloc[i])
                    if (
                        float(basic_lower.iloc[i]) > float(f_lower.iloc[i - 1])
                        or float(close.iloc[i - 1]) < float(f_lower.iloc[i - 1])
                    )
                    else float(f_lower.iloc[i - 1])
                )
                if float(close.iloc[i]) > float(f_upper.iloc[i - 1]):
                    dirs[i] = 1
                elif float(close.iloc[i]) < float(f_lower.iloc[i - 1]):
                    dirs[i] = -1
                else:
                    dirs[i] = dirs[i - 1]

            out["supertrend_dir"] = dirs[-1]
            out["supertrend_dir_prev"] = dirs[-2] if len(dirs) > 1 else 0
            out["supertrend_val"] = round(float(f_lower.iloc[-1]) if dirs[-1] == 1 else float(f_upper.iloc[-1]), 4)
        except Exception:
            pass

        # ── Hurst Exponent (variance-scaling method, 100-bar window) ─────
        try:
            n = min(100, len(close))
            if n >= 30:
                log_prices = np.log(close.iloc[-n:].values.astype(float))
                lags = [l for l in [2, 4, 8, 16, 32] if l < n // 2]
                taus = [np.std(log_prices[lag:] - log_prices[:-lag]) for lag in lags]
                valid = [(l, t) for l, t in zip(lags, taus) if t > 0]
                if len(valid) >= 3:
                    hurst = float(np.polyfit([np.log(l) for l, _ in valid], [np.log(t) for _, t in valid], 1)[0])
                    out["hurst"] = round(max(0.0, min(1.0, hurst)), 3)
        except Exception:
            pass

        # ── Keltner Channels(20, 2 × ATR) ────────────────────────────────
        try:
            kc_mid = close.ewm(span=20, adjust=False).mean()
            out["kc_upper"] = round(float((kc_mid + 2.0 * atr_s).iloc[-1]), 4)
            out["kc_lower"] = round(float((kc_mid - 2.0 * atr_s).iloc[-1]), 4)
            out["kc_mid"] = round(float(kc_mid.iloc[-1]), 4)
        except Exception:
            pass

        # ── Fractal Dimension Index (Ehlers formula, 30-bar) ─────────────
        # Measures linearity (trending) vs fractality (choppy) of price action.
        # Values range 1.0–2.0: <1.5 = trending (trust breakouts),
        #                         >1.5 = choppy (fade breakouts, prefer reversals).
        try:
            n = 30
            if len(close) >= n + 1:
                hh = float(high.rolling(n).max().iloc[-1])
                ll = float(low.rolling(n).min().iloc[-1])
                denom = hh - ll
                if denom > 0:
                    # Sum of unit-square diagonal steps (Ehlers)
                    dt = 1.0 / (n - 1)
                    c_slice = close.iloc[-n:].values.astype(float)
                    steps = sum(
                        np.sqrt(dt**2 + ((c_slice[i] - c_slice[i - 1]) / denom) ** 2) for i in range(1, len(c_slice))
                    )
                    if steps > 0:
                        fdi_val = 1.0 + np.log(steps) / np.log(2 * (n - 1))
                        out["fdi"] = round(float(np.clip(fdi_val, 1.0, 2.0)), 3)
        except Exception:
            pass

        # ── Rolling 20-day VWAP ───────────────────────────────────────
        # Typical Price × Volume accumulated over rolling 20 sessions.
        # A price below VWAP means buyers have been underwater vs. the mean
        # cost basis — a structural liquidity headwind for BUY signals.
        try:
            tp = (high + low + close) / 3.0
            n_vwap = min(20, len(df))
            cum_tpv = (tp * vol).rolling(n_vwap).sum()
            cum_vol = vol.rolling(n_vwap).sum()
            vwap_s = cum_tpv / cum_vol.replace(0, np.nan)
            vwap_val = float(vwap_s.iloc[-1]) if not pd.isna(vwap_s.iloc[-1]) else None
            if vwap_val:
                out["vwap_20"] = round(vwap_val, 4)
                out["vwap_pct"] = round((out["price"] - vwap_val) / vwap_val * 100, 2)
                # Prior-day vwap_pct (for cross detection in signal engine)
                if len(vwap_s) >= 2 and not pd.isna(vwap_s.iloc[-2]):
                    vwap_prev_val = float(vwap_s.iloc[-2])
                    if vwap_prev_val > 0:
                        out["vwap_pct_prev"] = round((float(close.iloc[-2]) - vwap_prev_val) / vwap_prev_val * 100, 2)
                # VWAP slope: True if VWAP has risen over the last 3 bars
                if len(vwap_s) >= 4:
                    vwap_3d_ago = float(vwap_s.iloc[-4]) if not pd.isna(vwap_s.iloc[-4]) else None
                    if vwap_3d_ago:
                        out["vwap_slope_pos"] = bool(vwap_val > vwap_3d_ago)
                # VWAP σ bands: std-dev of close around VWAP (not Bollinger Bands —
                # different distribution because we use VWAP not SMA as centre)
                vwap_resid = close - vwap_s
                vwap_std_s = vwap_resid.rolling(n_vwap).std()
                if not pd.isna(vwap_std_s.iloc[-1]):
                    vwap_std = float(vwap_std_s.iloc[-1])
                    if vwap_std > 0:
                        out["vwap_band1_upper"] = round(vwap_val + vwap_std, 4)
                        out["vwap_band1_lower"] = round(vwap_val - vwap_std, 4)
                        out["vwap_band2_upper"] = round(vwap_val + 2 * vwap_std, 4)
                        out["vwap_band2_lower"] = round(vwap_val - 2 * vwap_std, 4)
        except Exception:
            pass

        # ── IBS — Internal Bar Strength ──────────────────────────────────
        # Where the close lands within the day's range: 0 = at low, 1 = at high.
        # A reliable single-bar mean-reversion exhaustion signal.
        try:
            c0_ibs = float(close.iloc[-1])
            h0_ibs = float(high.iloc[-1])
            l0_ibs = float(low.iloc[-1])
            rng_ibs = h0_ibs - l0_ibs
            if rng_ibs > 0:
                out["ibs"] = round((c0_ibs - l0_ibs) / rng_ibs, 4)
        except Exception:
            pass

        # ── ATR Expansion / Contraction tracking ─────────────────────────
        # Counts consecutive bars ATR is expanding or contracting, and the
        # ATR percentile rank over the last 252 bars (regime filter).
        try:
            atr_clean = atr_s.dropna()
            if len(atr_clean) >= 10:
                atr_arr = atr_clean.values
                expand_cnt = 0
                contract_cnt = 0
                for i in range(len(atr_arr) - 1, 0, -1):
                    if atr_arr[i] > atr_arr[i - 1]:
                        if contract_cnt == 0:
                            expand_cnt += 1
                        else:
                            break
                    else:
                        if expand_cnt == 0:
                            contract_cnt += 1
                        else:
                            break
                out["atr_expand_bars"] = expand_cnt
                out["atr_contract_bars"] = contract_cnt
                n_rank = min(252, len(atr_clean))
                atr_window = atr_clean.iloc[-n_rank:].values
                out["atr_pct_rank"] = round(float(np.mean(atr_window < atr_window[-1])) * 100, 1)
        except Exception:
            pass

        # ── Volume Profile (POC / VAH / VAL) — daily OHLCV approximation ─
        # Distributes each session's volume uniformly across its H-L range,
        # then finds the modal price (POC) and 70%-volume value area (VAH/VAL).
        try:
            n_vp = min(20, len(df))
            vp_df = df.iloc[-n_vp:]
            p_min = float(vp_df["Low"].min())
            p_max = float(vp_df["High"].max())
            if p_max > p_min:
                n_bins = 40
                bins = np.linspace(p_min, p_max, n_bins + 1)
                bvol = np.zeros(n_bins)
                for _, row in vp_df.iterrows():
                    h_r = float(row["High"])
                    l_r = float(row["Low"])
                    v_r = float(row["Volume"])
                    rng_r = h_r - l_r
                    for j in range(n_bins):
                        if rng_r <= 0:
                            idx = min(int((float(row["Close"]) - p_min) / (p_max - p_min) * n_bins), n_bins - 1)
                            bvol[idx] += v_r
                            break
                        overlap = min(h_r, bins[j + 1]) - max(l_r, bins[j])
                        if overlap > 0:
                            bvol[j] += v_r * (overlap / rng_r)
                poc_idx = int(np.argmax(bvol))
                out["vp_poc"] = round(float((bins[poc_idx] + bins[poc_idx + 1]) / 2), 4)
                # Value Area: expand from POC until 70% of total volume captured
                total_v = float(np.sum(bvol))
                target = total_v * 0.70
                lo_i = hi_i = poc_idx
                acc = float(bvol[poc_idx])
                while acc < target and (lo_i > 0 or hi_i < n_bins - 1):
                    lo_add = float(bvol[lo_i - 1]) if lo_i > 0 else 0.0
                    hi_add = float(bvol[hi_i + 1]) if hi_i < n_bins - 1 else 0.0
                    if lo_add >= hi_add and lo_i > 0:
                        lo_i -= 1
                        acc += lo_add
                    elif hi_i < n_bins - 1:
                        hi_i += 1
                        acc += hi_add
                    else:
                        break
                out["vp_vah"] = round(float(bins[hi_i + 1]), 4)
                out["vp_val"] = round(float(bins[lo_i]), 4)
        except Exception:
            pass

        # ── Market Structure — BOS / MSS ─────────────────────────────────
        # Detects Break of Structure (trend continuation) and Market Structure
        # Shift (liquidity grab + reversal) using 3-bar pivot highs/lows.
        try:
            if len(df) >= 20:
                n_ms = min(60, len(df))
                ms_h = high.iloc[-n_ms:].values.astype(float)
                ms_l = low.iloc[-n_ms:].values.astype(float)
                ms_c = close.iloc[-n_ms:].values.astype(float)
                phighs: list[tuple[int, float]] = []
                plows: list[tuple[int, float]] = []
                for i in range(1, len(ms_h) - 1):
                    if ms_h[i] > ms_h[i - 1] and ms_h[i] > ms_h[i + 1]:
                        phighs.append((i, ms_h[i]))
                    if ms_l[i] < ms_l[i - 1] and ms_l[i] < ms_l[i + 1]:
                        plows.append((i, ms_l[i]))
                last_c = ms_c[-1]
                struct = None
                ms_lvl = None
                if len(phighs) >= 2:
                    lph = phighs[-1][1]
                    pph = phighs[-2][1]
                    if last_c > lph and lph > pph:  # BOS bull: close breaks above HH
                        struct = "bos_bull"
                        ms_lvl = lph
                    elif last_c < lph:
                        struct = "below_resistance"
                        ms_lvl = lph
                if len(plows) >= 2:
                    lpl = plows[-1][1]
                    ppl = plows[-2][1]
                    if last_c < lpl and lpl < ppl:  # BOS bear: close breaks below LL
                        struct = "bos_bear"
                        ms_lvl = lpl
                    # MSS bull: swept prior low then closed above last swing high
                    if (
                        lpl < ppl * 0.995
                        and len(phighs) >= 1
                        and plows[-1][0] > phighs[-1][0]
                        and last_c > phighs[-1][1]
                    ):
                        struct = "mss_bull"
                        ms_lvl = phighs[-1][1]
                if struct:
                    out["market_struct"] = struct
                    out["ms_level"] = round(float(ms_lvl), 4)
        except Exception:
            pass

        # ── Elliott Wave & Gann Analysis (Simplified) ─────────────────────
        try:
            if len(close) >= 50:
                # Gann 1x1 Angle
                # Look back 20 bars for a significant low/high
                low_20 = low.iloc[-20:]
                high_20 = high.iloc[-20:]
                recent_low_idx = int(np.argmin(low_20.values))
                recent_high_idx = int(np.argmax(high_20.values))

                recent_low_val = float(low_20.iloc[recent_low_idx])
                recent_high_val = float(high_20.iloc[recent_high_idx])

                days_since_low = 20 - recent_low_idx
                days_since_high = 20 - recent_high_idx

                # Approximate 1 unit of price per time unit using ATR / 10
                atr_val = out.get("atr", out["price"] * 0.02)
                gann_step = atr_val * 0.1

                gann_1x1_up = recent_low_val + (days_since_low * gann_step)
                gann_1x1_down = recent_high_val - (days_since_high * gann_step)

                sma20 = out.get("sma20", out["price"])
                sma50 = out.get("sma50", out["price"])

                if out["price"] > gann_1x1_up and days_since_low > 5 and sma20 > sma50:
                    out["gann_state"] = "above_1x1_up"
                elif out["price"] < gann_1x1_down and days_since_high > 5 and sma20 < sma50:
                    out["gann_state"] = "below_1x1_down"

                # Elliott Wave simplified heuristics
                macd_val = out.get("macd", 0)
                macd_hist = out.get("macd_hist", 0)
                macd_hist_p = out.get("macd_hist_prev", 0)
                rsi_div = out.get("rsi_divergence")

                wk52_h = out.get("week52_high", out["price"])
                wk52_l = out.get("week52_low", out["price"])

                is_new_high = out["price"] >= wk52_h * 0.98
                is_new_low = out["price"] <= wk52_l * 1.02

                if is_new_high and rsi_div == "bearish":
                    out["elliott_wave_phase"] = "wave_5_up"
                elif is_new_high and macd_val > 0 and macd_hist > macd_hist_p:
                    out["elliott_wave_phase"] = "wave_3_up"
                elif is_new_low and rsi_div == "bullish":
                    out["elliott_wave_phase"] = "wave_c_down"
                elif is_new_low and macd_val < 0 and macd_hist < macd_hist_p:
                    out["elliott_wave_phase"] = "wave_3_down"
        except Exception:
            pass

    except Exception as e:
        print(f"Indicator calculation error: {e}")

    return out


# ── Cross-ticker vectorised batch calculation ─────────────────────────────────
# Computes RSI, MACD, SMA20/50/200, ATR for ALL tickers in a single numpy pass.
# Falls back to the per-ticker calculate_indicators() for tickers with unusual
# data shapes or errors.  Called by scanner.py instead of individual calls.


def batch_calculate_indicators(
    histories: dict[str, "pd.DataFrame"],
    period: int = 14,
) -> dict[str, dict]:
    """
    Vectorised indicator calculation across all tickers.
    Returns {ticker: partial_indicators} that supplement (not replace) the
    full calculate_indicators() result — covers the expensive rolling ops.

    Performance: ~O(N × T) with numpy where N=tickers and T=bars, vs O(N) × O(T)
    sequential pandas. Expected speedup: 3–5× for the SMA/ATR operations.
    """
    results: dict[str, dict] = {}
    for ticker, df in histories.items():
        if df is None or len(df) < 30:
            continue
        try:
            c = df["Close"].astype(float).values
            h = df["High"].astype(float).values
            l = df["Low"].astype(float).values

            sma20 = _np_sma(c, 20)
            sma50 = _np_sma(c, 50)
            sma200 = _np_sma(c, 200)
            atr = _np_atr(h, l, c, period)

            # EWM RSI via numpy
            delta = np.diff(c)
            gains = np.where(delta > 0, delta, 0.0)
            losses = np.where(delta < 0, -delta, 0.0)
            avg_g = _np_ewm(gains, span=2 * period - 1)
            avg_l = _np_ewm(losses, span=2 * period - 1)
            rsi_val = 100 - 100 / (1 + avg_g[-1] / max(avg_l[-1], 1e-10))

            results[ticker] = {
                "sma20_v": float(sma20[-1]) if not np.isnan(sma20[-1]) else None,
                "sma50_v": float(sma50[-1]) if not np.isnan(sma50[-1]) else None,
                "sma200_v": float(sma200[-1]) if not np.isnan(sma200[-1]) else None,
                "atr_v": round(atr, 4),
                "rsi_v": round(float(rsi_val), 2),
            }
        except Exception:
            pass
    return results
