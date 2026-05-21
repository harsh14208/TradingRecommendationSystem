"""
backend/scripts/signal_alpha_decomposition.py  (v6 — 26-family)

Progression:
  v1  5 families   MR×1.0 OSC×1.0   Sharpe 0.27  WR 56.7%  avg +1.06%  N=247
  v2 11 families   MR×0.5 OSC×1.0   Sharpe 0.43  WR 66.2%  avg +1.45%  N=77
  v3 17 families   MR×0.7 OSC×1.0   Sharpe 0.17  WR 51.2%  avg +0.64%  N=510
       Weight sweep found: OSC=0.0, MR=0.0 optimal → 34 trades, Sharpe 0.42
  v4 22 families   MR×0.0 OSC×0.0   + 5 new MR-contrarian families → Sharpe 0.23
  v5 26 families   +disagg(BB/IBS/VWAP/RSI_LEVEL) → Sharpe 0.08 ← WORSE
       Lesson: disaggregating MR-gate conditions = double-counting; BB_PURE/IBS_PURE/
       VWAP_DIST corr 0.75-0.79 with existing signals → all 3 CONFIRMED REDUNDANT
  v6 26 families   Remove 3 redundant; add 3 orthogonal: EARN · REDDAY · MOM_DECEL
       RESULT: N=403, WR=50.9%, Sharpe=0.16 · EARN/REDDAY/MOM_DECEL ALL CONFIRMED REDUNDANT
       EARN +0.04, MOM_DECEL +0.03 ΔSharpe when removed = they ADD low-quality trades
       HURST bug fixed (lp undefined → real values); HURST still confirmed redundant (+0.02)
       Incremental peak: +CMF (10 families) → N=10, Sharpe=0.49 = v4-opt reproduced
       OHLCV signal space EXHAUSTED: no new pure price/volume signal improves beyond v4-opt

Confirmed redundant (v1→v6): OSC · MR · MFI · WK52 · RSI_DIV · STREAK · PIVOT ·
  SUPER · HURST · GAP · RSI_LEVEL · EARN · REDDAY · MOM_DECEL ·
  BB_PURE · IBS_PURE · VWAP_DIST (removed in v6, corr 0.75-0.79)

Implemented in signal_engine.py (alpha-comp v3 findings):
  • Keltner lower breach on RSI<42 → mean_rev_score +10 (was score -8)
  • SMA20 streak <= -7 days → mean_rev_score +8 (was momentum_score -8)
  • Donchian new 20-day low on RSI<45 → mean_rev_score +10 (was momentum_score -10)

Original 5  : OSC · TREND · VOL · MA · MR
Added v2    : MFI · CANDLE · ROC · WK52 · RS · RSI_DIV
Added v3    : KELTNER(MR) · STREAK(MR) · CMF · DONCHIAN(MR) · HYG · PIVOT
Added v4    : SUPER(MR) · HURST · ATR_REG · GAP(MR) · PRICESTR(MR)
Added v5    : RSI_LEVEL (kept); BB_PURE · IBS_PURE · VWAP_DIST (removed in v6)
Added v6    : EARN (earnings proximity risk) · REDDAY (consec. red candles) ·
              MOM_DECEL (ROC deceleration = momentum 2nd derivative)
  (all pure OHLCV + HYG ETF, matches signal_engine.py indicators)

Tests:
  10a  Ablation          — remove one family, ΔSharpe vs baseline
  10b  Incremental build — add families one at a time
  10c  Optimal combo     — essential+helpful families only
  10d  Weight sweep      — OSC and MR confirmations
  10e  Regime survival
  10f  Correlation matrix
  10g  MR gate filter
  10h  Monte Carlo       — naive vs optimal
  10i  Three-gate verdict

Run from backend/:
    python scripts/signal_alpha_decomposition.py
"""
from __future__ import annotations
import os, sys, warnings, math, itertools
from datetime import datetime
from multiprocessing import Pool

import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

_HERE   = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _p in [_PARENT, _HERE]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import backtest_technicals as bt
from backtest_technicals import (
    TICKERS, START, END, HOLD_DAYS,
    BUY_THRESH, BUY_THRESH_MAX, SELL_THRESH,
    FRICTION_PCT, POSITION_SIZE, REGIMES,
    MR_RSI_CEIL, MR_BB_CEIL, MR_IBS_CEIL, MR_VWAP_FLOOR,
    simulate_ticker, stats, fmt_sharpe, fmt_pf, print_table,
    _EMPTY_STATS, fetch_spy_trend, fetch_stlfsi4, process_ticker,
)

# ─────────────────────────────────────────────────────────────────────────────
# Family registry  (26 total)
# ─────────────────────────────────────────────────────────────────────────────

SIGNAL_FAMILIES = [
    # ── 12 families: 11 essential + OSC at low weight as signal generator ─────
    # The 11 essential families are quality FILTERS (TREND/VOL/MA/ROC/RS/CMF fire
    # NEGATIVE for oversold stocks — correct, they're in downtrends). Without a
    # positive signal generator, no stock clears BUY_THRESH=40.
    # OSC (RSI/Stoch) was "redundant" only WITH KELTNER (corr=0.70). With KELTNER
    # removed, OSC is needed as the RSI-based generator at reduced weight (0.30).
    "osc",       # RSI/Stoch/WR/CCI — signal generator for oversold stocks, weight=0.50 (v2 proven)
    "trend",     # MACD/EMA/ADX — essential quality filter (ΔSharpe -0.07)
    "vol",       # OBV/Surge/Dry-up — essential quality filter (ΔSharpe -0.06)
    "ma",        # SMA/VWAP/Z-score — most critical filter, ΔSharpe -0.13
    "wk52",      # 52-week range position — v7 essential
    "roc",       # 10-day Rate of Change — essential (ΔSharpe -0.02 to -0.07)
    "rs",        # 1-month return vs SPY — essential (ΔSharpe -0.05)
    "cmf",       # Chaikin Money Flow — essential (ΔSharpe -0.02 to -0.04)
    "donchian",  # 20-day low MR setup — essential MR-contrarian (ΔSharpe -0.01 to -0.04)
    "hyg",       # HYG credit stress — essential (ΔSharpe -0.02)
    "atr_reg",   # ATR pct rank — essential + most orthogonal (avg corr 0.08)
    "pricestr",  # LH/LL price structure — essential MR-contrarian (ΔSharpe -0.04)
]

FAMILY_LABELS = {
    "osc":      "OSC     (RSI/Stoch/WR)          ← generator @0.50 weight",
    "trend":    "TREND   (MACD/EMA/ADX/BOS)",
    "vol":      "VOL     (OBV/Surge/Dry-up)",
    "ma":       "MA      (SMA/VWAP/Z-score)       ← most critical",
    "wk52":     "WK52    (52-Week Range Position)",
    "roc":      "ROC     (10-day Rate of Change)",
    "rs":       "RS      (1-Month Return vs SPY)",
    "cmf":      "CMF     (Chaikin Money Flow)",
    "donchian": "DONCHIAN(near 20-day low = MR)   ← MR-contrarian",
    "hyg":      "HYG     (Credit stress — HYG 1M)",
    "atr_reg":  "ATR_REG (ATR pct rank — coiling) ← most orthogonal",
    "pricestr": "PRICESTR(LH/LL structure = MR)   ← MR-contrarian",
}

# OSC first (signal generator) then quality filters in order of ΔSharpe impact.
INCREMENTAL_ORDER = [
    "osc",      # RSI/Stoch — signal generator for oversold stocks (weight=0.30)
    "ma",       # structure anchor — most critical filter
    "trend",    # momentum direction
    "vol",      # volume confirmation
    "roc",      # 10d momentum
    "rs",       # relative performance vs SPY
    "donchian", # 20d low MR-contrarian
    "pricestr", # LH/LL structure MR-contrarian
    "atr_reg",  # volatility coiling (near-orthogonal)
    "cmf",      # Chaikin flow confirmation
    "wk52",     # 52-week range position
    "hyg",      # credit stress macro filter
]

FAM_COLS = [
    "osc_f",
    "trend_f","vol_f","ma_f","wk52_f","roc_f",
    "rs_f","cmf_f","donchian_f","hyg_f","atr_reg_f","pricestr_f",
]

BASE_WEIGHTS: dict[str, float] = {f: 1.0 for f in SIGNAL_FAMILIES}
BASE_WEIGHTS["osc"] = 0.50  # v2's proven weight — RSI/Stoch generator for oversold stocks


# ─────────────────────────────────────────────────────────────────────────────
# Extra indicator computation  (v2 families + 6 new v3 families)
# ─────────────────────────────────────────────────────────────────────────────

def compute_extra_indicators(
    df: pd.DataFrame,
    spy_closes: pd.Series | None = None,
    hyg_closes: pd.Series | None = None,
) -> pd.DataFrame:
    """Add indicator columns for the 11 essential families. Safe to call after bt.compute_indicators.

    Removed (confirmed redundant v1-v7): MFI, RSI_DIV, CANDLE, KELTNER, STREAK,
    PIVOT, SUPER, HURST, GAP, RSI_LEVEL, EARN, REDDAY, MOM_DECEL, SECTOR_RS.
    Removed Hurst loop (was 90s bottleneck) and Supertrend loop.
    """
    c = df["Close"]; h = df["High"]; l = df["Low"]
    v = df["Volume"]

    # ── ROC(10) — for ROC family ──────────────────────────────────────────────
    df["roc10"] = (c / c.shift(10) - 1) * 100

    # ── WK52 position — for WK52 family ──────────────────────────────────────
    r_max = c.rolling(252, min_periods=30).max()
    r_min = c.rolling(252, min_periods=30).min()
    df["wk52_pos"] = (c - r_min) / (r_max - r_min).replace(0, np.nan)

    # ── 1-Month RS vs SPY — for RS family ────────────────────────────────────
    if spy_closes is not None:
        spy_a = spy_closes.reindex(df.index, method="ffill")
        df["rs_1m"] = ((c / c.shift(21) - 1) - (spy_a / spy_a.shift(21) - 1)) * 100

    # ── CMF(20) — for CMF family ──────────────────────────────────────────────
    mf_mult = ((c - l) - (h - c)) / (h - l).replace(0, np.nan)
    df["cmf"] = (mf_mult * v).rolling(20).sum() / v.rolling(20).sum().replace(0, np.nan)

    # ── DONCHIAN — for DONCHIAN family ───────────────────────────────────────
    dc_hi = h.rolling(20).max(); dc_lo = l.rolling(20).min()
    df["donchian_pos"]      = (c - dc_lo) / (dc_hi - dc_lo).replace(0, np.nan)
    df["donchian_new_high"] = (c >= dc_hi.shift(1)).astype(float)
    df["donchian_new_low"]  = (c <= dc_lo.shift(1)).astype(float)

    # ── HYG 1-month return — for HYG family ──────────────────────────────────
    if hyg_closes is not None:
        hyg_a = hyg_closes.reindex(df.index, method="ffill")
        df["hyg_1m"] = (hyg_a / hyg_a.shift(21) - 1) * 100

    # ── Price Structure HH/HL vs LH/LL — for PRICESTR family ─────────────────
    mid = 10
    rh = h.shift(1); rl = l.shift(1)
    ph = rh.rolling(mid).max().shift(mid); pl = rl.rolling(mid).min().shift(mid)
    rh2 = rh.rolling(mid).max();          rl2 = rl.rolling(mid).min()
    df["ps_hh_hl"] = ((rh2 > ph * 1.005) & (rl2 > pl * 1.005)).astype(float)
    df["ps_lh_ll"] = ((rh2 < ph * 0.995) & (rl2 < pl * 0.995)).astype(float)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Data fetchers
# ─────────────────────────────────────────────────────────────────────────────

def _download_etf_closes(ticker: str, start: str, end: str, label: str) -> pd.Series:
    try:
        raw = yf.download(ticker, start=start, end=end, interval="1d",
                          auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        closes = raw["Close"].ffill()
        closes.index = pd.to_datetime(closes.index).normalize()
        return closes
    except Exception as e:
        print(f"  {label} download failed ({e})")
        return pd.Series(dtype=float)


# ─────────────────────────────────────────────────────────────────────────────
# 11-family vectorised scoring (essential families only)
# ─────────────────────────────────────────────────────────────────────────────

def compute_scores_masked(
    df: pd.DataFrame,
    family_weights: dict | None = None,
    return_families: bool = False,
) -> "pd.Series | pd.DataFrame":
    """
    11-family vectorised scoring (essential families only, v7 ablation consensus).
    family_weights: per-family scalar; missing keys default to BASE_WEIGHTS.
    return_families: if True return per-family DataFrame (for correlation).
    """
    n = len(df)

    def _v(col, fill=0.0):
        return df[col].fillna(fill).values.astype(float) if col in df.columns else np.full(n, fill)

    def _b(col):
        if col not in df.columns: return np.zeros(n, dtype=bool)
        return df[col].notna().values & (df[col].fillna(0).values.astype(float) == 1.0)

    c         = _v("Close")
    rsi       = _v("rsi", 50.0)
    rsi_ok    = df["rsi"].notna().values    if "rsi"    in df.columns else np.zeros(n, bool)
    atr       = _v("atr", 0.0)
    atr_pct   = np.where(c > 0, atr / c, 0.02)
    low_atr   = atr_pct < 0.010
    adx_val   = _v("adx",        0.0)
    rvol      = _v("rvol",        1.0)
    chg_pct   = _v("change_pct",  0.0)
    sma200_v  = _v("sma200",      0.0)
    sma200_ok = df["sma200"].notna().values if "sma200" in df.columns else np.zeros(n, bool)
    sma20_v   = _v("sma20",       0.0)
    sma20_ok  = df["sma20"].notna().values  if "sma20"  in df.columns else np.zeros(n, bool)

    # ── Oscillator (signal generator at reduced weight 0.30) ─────────────────
    # OSC was "redundant" with KELTNER (corr=0.70) in v1-v7 full system.
    # With KELTNER removed, OSC is the primary positive score generator for RSI<35 stocks.
    osc = np.zeros(n)
    osc += np.where(rsi_ok & (rsi < 25),                              28, 0)
    osc += np.where(rsi_ok & (rsi >= 25) & (rsi < 35),               16, 0)
    osc += np.where(rsi_ok & (rsi > 75),                             -18, 0)
    osc += np.where(rsi_ok & (rsi >= 65) & (rsi <= 75),              -10, 0)
    wr  = _v("wr", -50); wr_ok = df["wr"].notna().values if "wr" in df.columns else np.zeros(n, bool)
    osc += np.where(wr_ok & (wr <= -85),  10, 0)
    osc += np.where(wr_ok & (wr >= -15),  -8, 0)
    osc = np.clip(osc, -25, 25)

    # ── Trend ─────────────────────────────────────────────────────────────────
    trend  = np.zeros(n)
    hist   = _v("macd_hist", 0); h_ok = df["macd_hist"].notna().values if "macd_hist" in df.columns else np.zeros(n, bool)
    hist_p = _v("macd_hist_p", 0)
    cu_m = h_ok&(hist>0)&(hist_p<=0); cd_m = h_ok&(hist<0)&(hist_p>=0)
    rise = hist > hist_p; no_x = h_ok & ~cu_m & ~cd_m
    trend += np.select([cu_m&rise, cd_m&~rise, cu_m&~rise, cd_m&rise,
                        no_x&(hist>0)&rise, no_x&(hist<0)&~rise,
                        no_x&(hist>0)&~rise, no_x&(hist<0)&rise],
                       [18, -18, 12, -12, 16, -16, 6, -6], default=0)
    trend += np.where(_b("macd_bull_div"),  20, 0)
    trend += np.where(_b("macd_bear_div"), -20, 0)
    e8   = _v("ema8",    0.0); e21  = _v("ema21",   0.0)
    e8p  = _v("ema8_p",  0.0); e21p = _v("ema21_p", 0.0)
    em_cols = ["ema8","ema21","ema8_p","ema21_p"]
    em_ok = (df[em_cols].notna().all(axis=1).values if all(x in df.columns for x in em_cols) else np.zeros(n, bool))
    vc   = rvol > 1.2; e_cu = em_ok&(e8>e21)&(e8p<=e21p); e_cd = em_ok&(e8<e21)&(e8p>=e21p)
    trend += np.select([e_cu&vc, e_cu&~vc, e_cd&vc, e_cd&~vc,
                        em_ok&~e_cu&~e_cd&(e8>e21), em_ok&~e_cu&~e_cd&(e8<=e21)],
                       [14, 8, -14, -8, 4, -4], default=0)
    pdi = _v("plus_di", 0); mdi = _v("minus_di", 0)
    di_ok = (df["plus_di"].notna().values & df["minus_di"].notna().values
             if "plus_di" in df.columns else np.zeros(n, bool))
    trend += np.select([di_ok&(adx_val>40)&(pdi>mdi), di_ok&(adx_val>40)&(pdi<=mdi),
                        di_ok&(adx_val>25)&(adx_val<=40)&(pdi>mdi),
                        di_ok&(adx_val>25)&(adx_val<=40)&(pdi<=mdi)],
                       [18, -18, 10, -10], default=0)
    atr_exp = _v("atr_expand_bars", 0)
    trend += np.where(atr_exp >= 5, np.where(chg_pct >= 0, 16, -10), 0)
    trend += np.where((atr_exp >= 3) & (atr_exp < 5), np.where(chg_pct >= 0, 10, -10), 0)
    if "market_struct" in df.columns:
        ms = df["market_struct"].values
        trend += np.where(ms=="bos_bull", 12, np.where(ms=="bos_bear", -12, np.where(ms=="mss_bull", 16, 0)))
    trend = np.clip(trend, -28, 28)
    trend = np.where(trend > 0,
                     np.where(rsi > 75, trend*0.30, np.where(rsi > 65, trend*0.55, trend)),
                     np.where(rsi < 25, trend*0.30, np.where(rsi < 35, trend*0.55, trend)))

    # ── Volume ────────────────────────────────────────────────────────────────
    vol    = np.zeros(n)
    obv_ab = _v("obv_above", 0); obv_sl = _v("obv_slope", 0)
    ob_ok  = (df["obv_above"].notna().values & df["obv_slope"].notna().values
              if "obv_above" in df.columns else np.zeros(n, bool))
    vol += np.where(ob_ok&(obv_ab>0)&(obv_sl>0),   12, 0)   # OBV above + rising (osc removed)
    vol += np.where(ob_ok&(obv_ab<=0)&(obv_sl<0), -12, 0)  # OBV below + falling
    vs = _b("vol_surge"); vd = _b("vol_dryup")
    vol += np.where(vs & (obv_sl>0) & sma20_ok & (c>sma20_v),  14, 0)
    vol += np.where(vs & (obv_sl<0) & sma20_ok & (c<sma20_v), -14, 0)
    vol += np.where(vd, -8, 0)
    vol += np.where(_b("obv_bull_div"),  12, 0)
    vol += np.where(_b("obv_bear_div"), -10, 0)
    vol += np.where((rsi < 40) & (rvol >= 2.0) & (chg_pct < 0), 10, 0)
    vol += np.where(rvol >= 3.0, np.where(chg_pct >= 0, 10, -10), 0)
    vol  = np.clip(vol, -20, 20)

    # ── MA ────────────────────────────────────────────────────────────────────
    ma      = np.zeros(n)
    sma50   = _v("sma50",  0.0); s50_ok  = df["sma50"].notna().values  if "sma50"  in df.columns else np.zeros(n, bool)
    sma200  = sma200_v;          s200_ok = sma200_ok
    ema200  = _v("ema200", 0.0); e200_ok = df["ema200"].notna().values if "ema200" in df.columns else np.zeros(n, bool)
    s200_sl = _v("sma200_slope",0); s50_sl=_v("sma50_slope",0); s20_sl=_v("sma20_slope",0)
    zscore  = _v("price_zscore", 0)
    ma += np.select([s200_ok&(c>sma200*1.02)&(s200_sl>0), s200_ok&(c>sma200*1.01),
                     s200_ok&(c<sma200*0.98)&(s200_sl<0), s200_ok&(c<sma200*0.99)],
                    [18, 12, -18, -12], default=0)
    ma += np.select([s50_ok&(c>sma50)&(s50_sl>0), s50_ok&(c>sma50),
                     s50_ok&(c<sma50)&(s50_sl<0), s50_ok&(c<sma50)],
                    [16, 8, -14, -6], default=0)
    ma += np.where(sma20_ok&(c>sma20_v)&(s20_sl>0),  12, 0)
    ma += np.where(sma20_ok&(c<sma20_v)&(s20_sl<0),  -8, 0)
    ma += np.select([zscore<-2.0,(zscore>=-2.0)&(zscore<-1.5),zscore>2.0,(zscore>1.5)&(zscore<=2.0)],
                    [14,7,-12,-6], default=0)
    ma += np.where(s50_ok&s200_ok&(sma50>sma200*1.005),  10, 0)
    ma += np.where(s50_ok&s200_ok&(sma50<sma200*0.995), -10, 0)
    ma += np.where(e200_ok&s200_ok&(c>ema200)&(c>sma200),  3, 0)
    ma += np.where(e200_ok&s200_ok&(c<ema200)&(c<sma200), -3, 0)
    vwap_pct   = _v("vwap_pct", 0)
    vp_ok      = df["vwap_pct"].notna().values if "vwap_pct" in df.columns else np.zeros(n, bool)
    vwap_slope = df["vwap_slope_pos"].fillna(False).astype(bool).values if "vwap_slope_pos" in df.columns else np.zeros(n, bool)
    ma += np.where(vp_ok & vwap_slope & (vwap_pct>0),   6, 0)
    ma += np.where(vp_ok & ~vwap_slope & (vwap_pct<0), -5, 0)
    vwap_20   = _v("vwap_20",0.0); v20_ok = df["vwap_20"].notna().values    if "vwap_20"      in df.columns else np.zeros(n, bool)
    prev_c    = _v("Close_prev",0.0); prev_vwap = _v("vwap_20_prev", 0.0)
    ma += np.where(v20_ok&(rvol>=2.0)&(prev_c<prev_vwap)&(c>=vwap_20),  12, 0)
    ma += np.where(v20_ok&(rvol>=2.0)&(prev_c>prev_vwap)&(c<=vwap_20), -14, 0)
    vp_poc = _v("vp_poc",0); vp_vah=_v("vp_vah",0); vp_val=_v("vp_val",0)
    vp_cols = ["vp_poc","vp_vah","vp_val"]
    vp_ok2  = (df[vp_cols].notna().all(axis=1).values if all(x in df.columns for x in vp_cols) else np.zeros(n, bool))
    ma += np.where(vp_ok2&(rvol>=1.5)&(c>vp_vah),  16, 0)
    ma += np.where(vp_ok2&(rvol>=1.5)&(c<vp_val), -14, 0)
    poc_d = np.where(vp_poc>0, np.abs(c-vp_poc)/vp_poc*100, 99)
    ma += np.where(vp_ok2 & (poc_d<=0.25) & (adx_val<20), 8, 0)
    ma  = np.clip(ma, -28, 28)

    # ── Regime layers — TREND adjustment only (MR/OSC families removed) ───────
    strong    = adx_val > 40
    s200_sl_a = _v("sma200_slope", 0)
    trend = np.where(strong, trend * 1.20, trend)                              # amplify in strong trend
    trend = np.where(sma200_ok & (s200_sl_a < -0.01), trend * 0.30, trend)   # dampen in bear market
    trend = np.where(low_atr, 0.0, trend)   # no trend signal in low-ATR environment
    vol   = np.where(low_atr, 0.0, vol)     # no volume signal in low-ATR environment

    # ── ROC (cap ±10)
    roc10_arr=_v("roc10",0); roc10_ok=df["roc10"].notna().values if "roc10" in df.columns else np.zeros(n,bool)
    roc_sc=np.select([roc10_ok&(roc10_arr>8), roc10_ok&(roc10_arr>4)&(roc10_arr<=8),
                      roc10_ok&(roc10_arr<-8),roc10_ok&(roc10_arr<-4)&(roc10_arr>=-8)],
                     [8,4,-8,-4], default=0)
    roc_sc=np.clip(roc_sc,-10,10)

    # WK52 (cap ±8)
    wk52_pos=_v("wk52_pos",0.5); wk52_ok=df["wk52_pos"].notna().values if "wk52_pos" in df.columns else np.zeros(n,bool)
    wk52_sc=np.select([wk52_ok&(wk52_pos>=0.90),wk52_ok&(wk52_pos>=0.75)&(wk52_pos<0.90),
                       wk52_ok&(wk52_pos<=0.10),wk52_ok&(wk52_pos<=0.25)&(wk52_pos>0.10)],
                      [4,2,-4,-2], default=0)
    wk52_sc=np.clip(wk52_sc,-8,8)

    # RS (cap ±12)
    rs_1m=_v("rs_1m",0); rs_ok=df["rs_1m"].notna().values if "rs_1m" in df.columns else np.zeros(n,bool)
    rs_sc=np.select([rs_ok&(rs_1m>8), rs_ok&(rs_1m>2)&(rs_1m<=8),
                     rs_ok&(rs_1m<-8),rs_ok&(rs_1m<-2)&(rs_1m>=-8)],
                    [12,4,-12,-5], default=0)
    rs_sc=np.clip(rs_sc,-12,12)

    # ── CMF(20) — Chaikin Money Flow (inflow=bullish, outflow=bearish)
    # Rationale: heavy outflow on an oversold stock = still selling, not yet safe to enter
    # Positive CMF on a technically oversold stock = smart money accumulating = high conviction
    cmf_arr=_v("cmf",0); cmf_ok=df["cmf"].notna().values if "cmf" in df.columns else np.zeros(n,bool)
    cmf_sc=np.select([cmf_ok&(cmf_arr>0.25), cmf_ok&(cmf_arr>0.10)&(cmf_arr<=0.25),
                      cmf_ok&(cmf_arr<-0.25),cmf_ok&(cmf_arr<-0.10)&(cmf_arr>=-0.25)],
                     [10, 5, -10, -5], default=0)
    cmf_sc=np.clip(cmf_sc,-10,10)

    # DONCHIAN (cap ±10) — MR-contrarian: near/at 20-day low = 20-day oversold = MR bounce
    # At/near 20-day high = overbought = mild negative (not MR entry)
    dc_pos=_v("donchian_pos",0.5); dc_ok=df["donchian_pos"].notna().values if "donchian_pos" in df.columns else np.zeros(n,bool)
    don_sc=np.zeros(n)
    don_sc += np.where(_b("donchian_new_low"),                               10, 0)  # at 20d low = MR setup
    don_sc += np.where(dc_ok & (dc_pos <= 0.10) & ~_b("donchian_new_low"),   5, 0)  # near 20d low
    don_sc += np.where(_b("donchian_new_high"),                              -6, 0)  # at 20d high = not MR
    don_sc += np.where(dc_ok & (dc_pos >= 0.90) & ~_b("donchian_new_high"), -3, 0)  # near 20d high
    don_sc=np.clip(don_sc,-10,10)

    # HYG — credit stress proxy (cap ±10)
    hyg_1m=_v("hyg_1m",0); hyg_ok=df["hyg_1m"].notna().values if "hyg_1m" in df.columns else np.zeros(n,bool)
    hyg_sc=np.select([hyg_ok&(hyg_1m>2), hyg_ok&(hyg_1m<-5), hyg_ok&(hyg_1m<-3)&(hyg_1m>=-5)],
                     [5, -10, -8], default=0)
    hyg_sc=np.clip(hyg_sc,-10,10)

    # PIVOT, RSI_LEVEL, EARN, REDDAY, MOM_DECEL, SECTOR_RS, SUPER, HURST, GAP — all removed
    # (confirmed redundant v6/v7; ΔSharpe ≥ 0 when removed from baseline)

    # ── ATR_REG (ATR percentile rank — volatility regime, cap ±8) ────────────
    # low rank = vol coiling = MR-friendly; high rank = expanding = momentum-dominant
    atr_rk    = _v("atr_pct_rank", 50)
    ark_ok    = df["atr_pct_rank"].notna().values if "atr_pct_rank" in df.columns else np.zeros(n, bool)
    atrreg_sc = np.select(
        [ark_ok & (atr_rk < 10), ark_ok & (atr_rk >= 10) & (atr_rk < 20),
         ark_ok & (atr_rk > 90), ark_ok & (atr_rk >= 80) & (atr_rk <= 90)],
        [8, 4, -6, -3], default=0)
    atrreg_sc = np.clip(atrreg_sc, -8, 8)

    # ── PRICESTR (LH/LL price structure MR-contrarian, cap ±8) ───────────────
    pstr_sc  = np.zeros(n)
    pstr_sc += np.where(_b("ps_lh_ll"),  8, 0)   # lower highs + lower lows = MR bounce setup
    pstr_sc += np.where(_b("ps_hh_hl"), -4, 0)   # uptrend = not an MR entry
    pstr_sc  = np.clip(pstr_sc, -8, 8)

    # ── Assemble 11 essential families ───────────────────────────────────────
    fw = dict(BASE_WEIGHTS)
    if family_weights:
        fw.update(family_weights)

    osc_f   = np.clip(osc,        -25, 25) * 1.00 * fw.get("osc",      0.50)
    trend_f = np.clip(trend,     -28, 28) * 0.90 * fw.get("trend",    1.0)
    vol_f   = np.clip(vol,       -20, 20) * 0.85 * fw.get("vol",      1.0)
    ma_f    = np.clip(ma,        -28, 28) * 1.00 * fw.get("ma",       1.0)
    wk52_f  = np.clip(wk52_sc,   -8,   8) * 1.00 * fw.get("wk52",    1.0)
    roc_f   = np.clip(roc_sc,   -10, 10) * 1.00 * fw.get("roc",      1.0)
    rs_f    = np.clip(rs_sc,    -12, 12) * 1.00 * fw.get("rs",       1.0)
    cmf_f   = np.clip(cmf_sc,   -10, 10) * 1.00 * fw.get("cmf",      1.0)
    don_f   = np.clip(don_sc,   -10, 10) * 1.00 * fw.get("donchian", 1.0)
    hyg_f   = np.clip(hyg_sc,   -10, 10) * 1.00 * fw.get("hyg",      1.0)
    areg_f  = np.clip(atrreg_sc, -8,  8) * 1.00 * fw.get("atr_reg",  1.0)
    pstr_f  = np.clip(pstr_sc,   -8,  8) * 1.00 * fw.get("pricestr", 1.0)

    score = osc_f + trend_f + vol_f + ma_f + wk52_f + roc_f + rs_f + cmf_f + don_f + hyg_f + areg_f + pstr_f

    stk      = np.stack([osc_f,trend_f,vol_f,ma_f,wk52_f,roc_f,rs_f,cmf_f,don_f,hyg_f,areg_f,pstr_f], axis=1)
    bull_cnt = (stk >  5).sum(axis=1)
    bear_cnt = (stk < -5).sum(axis=1)
    score = np.where((score>0)&(bull_cnt<2), score*0.50, score)
    score = np.where((score<0)&(bear_cnt<2), score*0.50, score)
    score = np.where((score>0)&vd&(rsi>=30),  score*0.70, score)
    score = np.round(score, 2)

    if return_families:
        return pd.DataFrame({
            "osc_f":osc_f,
            "trend_f":trend_f,"vol_f":vol_f,"ma_f":ma_f,"wk52_f":wk52_f,"roc_f":roc_f,
            "rs_f":rs_f,"cmf_f":cmf_f,"donchian_f":don_f,"hyg_f":hyg_f,
            "atr_reg_f":areg_f,"pricestr_f":pstr_f,
            "score":score,
        }, index=df.index)

    return pd.Series(score, index=df.index)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _run(fw_override: dict, all_dfs, vix, spy_trend, stlfsi4) -> tuple[dict, pd.DataFrame]:
    """Run simulation with BASE_WEIGHTS merged with fw_override."""
    fw = dict(BASE_WEIGHTS); fw.update(fw_override)
    trades_list = []
    for ticker, df in all_dfs.items():
        df2 = df.copy()
        df2["score"] = compute_scores_masked(df2, family_weights=fw)
        t = simulate_ticker(ticker, df2, vix, spy_trend, stlfsi4, mr_only=True)
        if not t.empty:
            trades_list.append(t)
    if not trades_list:
        return dict(_EMPTY_STATS), pd.DataFrame()
    tdf = pd.concat(trades_list, ignore_index=True)
    return stats(tdf["net_pct"].tolist()), tdf


def _mask_ablate(fam):  return {fam: 0.0}
def _mask_include(inc): return {f: (1.0 if f in inc else 0.0) for f in SIGNAL_FAMILIES}

def _fmt_row(label, sv, bs):
    sh   = sv.get("sharpe") or 0.0
    d_sh = sh - (bs.get("sharpe") or 0.0)
    d_wr = sv["wr"] - bs["wr"]
    d_av = sv["avg"] - bs["avg"]
    if   d_sh < -0.03: vd = "✓ essential"
    elif d_sh < 0.0:   vd = "~ helpful"
    else:              vd = "✗ redundant"
    return [label, str(sv["n"]),
            f"{sv['wr']:.1f}% ({d_wr:+.1f}pp)",
            f"{sv['avg']:+.2f}% ({d_av:+.2f}pp)",
            f"{fmt_sharpe(sv['sharpe'])} ({d_sh:+.2f})",
            f"-{sv['max_dd']:.2f}%", vd]


def _monte_carlo(rets: list[float], n_sims: int = 8000) -> tuple[float, float]:
    if not rets: return 0.0, 0.0
    arr  = np.array(rets)
    sims = [stats(np.random.choice(arr, size=len(arr), replace=True).tolist()).get("sharpe") or 0.0
            for _ in range(n_sims)]
    return float(np.percentile(sims, 5)), float(np.percentile(sims, 95))


# ─────────────────────────────────────────────────────────────────────────────
# §10 — full decomposition report  (v3)
# ─────────────────────────────────────────────────────────────────────────────

def run_ablation_suite(all_dfs, vix, spy_trend, stlfsi4, baseline_stats, baseline_trades):
    print("\n## 10. Signal Alpha Decomposition — v8 (11 Essential Families)\n")
    print(f"> {len(all_dfs)} tickers  ·  11 essential families (16 redundant removed after v1-v7 testing)")
    print(f"> Removed: osc, mr, mfi, candle, rsi_div, keltner, streak, pivot, super, hurst, gap,")
    print(f">          rsi_level, earn, redday, mom_decel, sector_rs — all ΔSharpe ≥ 0 when removed")
    print(f"> MR-only gate ON  ·  same entry/exit rules\n")

    bs_sh  = baseline_stats.get("sharpe") or 0.0
    bs_wr  = baseline_stats["wr"]
    bs_avg = baseline_stats["avg"]
    bs_dd  = baseline_stats["max_dd"]
    bs_n   = baseline_stats["n"]

    # ── 10a. Ablation ─────────────────────────────────────────────────────────
    print("### 10a. Ablation Test — Remove One Family\n")

    abl_rows = [["**BASELINE** (11 essential families, v8 clean)", str(bs_n),
                 f"{bs_wr:.1f}%", f"{bs_avg:+.2f}%",
                 fmt_sharpe(baseline_stats["sharpe"]), f"-{bs_dd:.2f}%", "—"]]
    ablation_results: dict[str, dict] = {}

    for fam in SIGNAL_FAMILIES:
        print(f"  ablating {fam}…", flush=True)
        sv, _ = _run(_mask_ablate(fam), all_dfs, vix, spy_trend, stlfsi4)
        ablation_results[fam] = sv
        abl_rows.append(_fmt_row(f"−{FAMILY_LABELS[fam]}", sv, baseline_stats))

    print_table(["Family Removed","N","Win Rate (Δ)","Avg Ret (Δ)","Sharpe (Δ)","Max DD","Verdict"], abl_rows)
    print("\n> ✓ essential = ΔSharpe < −0.03  ·  ~ helpful = ΔSharpe < 0  ·  ✗ redundant = ΔSharpe ≥ 0")

    # ── 10b. Incremental Build ────────────────────────────────────────────────
    print("\n### 10b. Incremental Build — Add One Family at a Time\n")
    inc_rows = []; prev_sh = None; included: list[str] = []

    for fam in INCREMENTAL_ORDER:
        included.append(fam)
        print(f"  +{fam}…", flush=True)
        sv, _ = _run({f: (1.0 if f in included else 0.0) for f in SIGNAL_FAMILIES},
                     all_dfs, vix, spy_trend, stlfsi4)
        sh   = sv.get("sharpe") or 0.0
        d_sh = (sh - prev_sh) if prev_sh is not None else sh
        inc_rows.append([f"+{fam.upper()}", str(sv["n"]), f"{sv['wr']:.1f}%",
                         f"{sv['avg']:+.2f}%",
                         f"{fmt_sharpe(sv['sharpe'])} ({'first' if prev_sh is None else f'{d_sh:+.2f}'})",
                         f"-{sv['max_dd']:.2f}%"])
        prev_sh = sh

    inc_rows.append(["**= Baseline**", str(bs_n), f"{bs_wr:.1f}%", f"{bs_avg:+.2f}%",
                     f"{fmt_sharpe(baseline_stats['sharpe'])} (ref)", f"-{bs_dd:.2f}%"])
    print_table(["Added","N","WR","Avg Ret","Sharpe (Δ)","Max DD"], inc_rows)

    # ── 10c. Optimal sub-combination ──────────────────────────────────────────
    print("\n### 10c. Optimal Sub-Combination (essential + helpful families only)\n")

    essential_fams = [f for f in SIGNAL_FAMILIES
                      if (ablation_results[f].get("sharpe") or 0.0) < bs_sh]
    print(f"  Essential families: {essential_fams}", flush=True)
    print(f"  Running optimal subset ({len(essential_fams)} families)…", flush=True)
    sv_opt, tdf_opt = _run(_mask_include(essential_fams), all_dfs, vix, spy_trend, stlfsi4)
    d_sh_opt = (sv_opt.get("sharpe") or 0.0) - bs_sh

    print_table(["Config","N","WR","Avg Ret","Sharpe","Max DD"], [
        ["Full baseline (26 fam)", str(bs_n), f"{bs_wr:.1f}%", f"{bs_avg:+.2f}%",
         fmt_sharpe(baseline_stats["sharpe"]), f"-{bs_dd:.2f}%"],
        [f"Optimal ({len(essential_fams)} fam)", str(sv_opt["n"]), f"{sv_opt['wr']:.1f}%",
         f"{sv_opt['avg']:+.2f}%", f"{fmt_sharpe(sv_opt['sharpe'])} ({d_sh_opt:+.2f})", f"-{sv_opt['max_dd']:.2f}%"],
    ])
    print(f"\n> Optimal families: {', '.join(essential_fams)}")

    # ── 10d. Weight sweep — MR and OSC ────────────────────────────────────────
    print("\n### 10d. Weight Sweep — MR and OSC\n")
    print("> Both confirmed redundant in v1+v2. Sweeping confirms optimal weight.\n")

    for swept_fam in ["mr", "osc"]:
        print(f"**{swept_fam.upper()} weight sweep:**\n")
        sweep_rows = []
        for w in [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]:
            sv, _ = _run({swept_fam: w}, all_dfs, vix, spy_trend, stlfsi4)
            d_sh  = (sv.get("sharpe") or 0.0) - bs_sh
            sweep_rows.append([f"{w:.1f}", str(sv["n"]), f"{sv['wr']:.1f}%",
                                f"{sv['avg']:+.2f}%",
                                f"{fmt_sharpe(sv['sharpe'])} ({d_sh:+.2f})",
                                f"-{sv['max_dd']:.2f}%"])
        print_table([f"{swept_fam.upper()} weight","N","WR","Avg Ret","Sharpe (Δ vs baseline)","Max DD"],
                    sweep_rows)
        print()

    # ── 10e. Regime survival (optimal combo) ──────────────────────────────────
    print("\n### 10e. Regime Survival — Optimal Combination\n")
    if tdf_opt is not None and not tdf_opt.empty:
        reg_rows = []
        for rname, rstart, rend in REGIMES:
            mask = (tdf_opt["date"] >= pd.Timestamp(rstart)) & (tdf_opt["date"] <= pd.Timestamp(rend))
            sv = stats(tdf_opt[mask]["net_pct"].tolist())
            if sv["n"] == 0: continue
            flag = " ✗" if sv["avg"] < 0 else (" ⚠" if sv["wr"] < 45 else "")
            reg_rows.append([rname, str(sv["n"]), f"{sv['wr']:.1f}%{flag}",
                             f"{sv['avg']:+.2f}%{flag}", fmt_sharpe(sv["sharpe"]), f"-{sv['max_dd']:.2f}%"])
        print_table(["Regime","N","WR","Avg Ret","Sharpe","Max DD"], reg_rows)
        print("\n> ⚠ WR < 45%  ·  ✗ negative avg return (edge absent in this regime)")

    # ── 10f. Correlation matrix ───────────────────────────────────────────────
    print("\n### 10f. Signal Correlation Matrix — at BUY Signal Bars\n")
    fam_frames: list[pd.DataFrame] = []
    for ticker, df in all_dfs.items():
        fdf  = compute_scores_masked(df, return_families=True)
        mask = fdf["score"] >= BUY_THRESH
        if mask.sum() > 5:
            fam_frames.append(fdf[mask][FAM_COLS])

    if fam_frames:
        combined = pd.concat(fam_frames, ignore_index=True)

        # Drop zero-variance columns: families with BASE_WEIGHTS=0.0 produce a constant
        # 0.0 score across all rows → zero variance → corr() returns NaN for those columns.
        # This caused all OSC and MR rows/columns to show NaN when those weights were 0.
        active_cols   = [c for c in FAM_COLS if combined[c].std() > 1e-9]
        skipped_cols  = [c for c in FAM_COLS if c not in active_cols]
        active_labels = [c.replace("_f", "").upper() for c in active_cols]
        if skipped_cols:
            print(f"> Skipping zero-weight families (weight=0.0): "
                  f"{', '.join(c.replace('_f','').upper() for c in skipped_cols)}\n")

        if len(active_cols) < 2:
            print("> Not enough active families for correlation analysis.\n")
        else:
            corr = combined[active_cols].corr().round(2)
            print("| | " + " | ".join(active_labels) + " |")
            print("|:---|" + "|".join("---:" for _ in active_labels) + "|")
            for i, lbl in enumerate(active_labels):
                vals = [f"{corr.loc[active_cols[i], active_cols[j]]:.2f}" for j in range(len(active_labels))]
                print(f"| **{lbl}** | " + " | ".join(vals) + " |")
            n_l = len(active_labels)
            off = [abs(corr.iloc[i, j]) for i in range(n_l) for j in range(n_l) if i != j]
            # Filter out any residual NaN from near-zero variance families
            off = [v for v in off if v == v]
            avg_c = float(np.mean(off)) if off else float("nan")
            if avg_c == avg_c:
                print(f"\n> Avg |off-diagonal| = **{avg_c:.2f}**  "
                      f"{'→ good orthogonality' if avg_c<0.25 else '→ moderate overlap' if avg_c<0.40 else '→ high redundancy'}")
                pairs = sorted(
                    [(abs(corr.loc[active_cols[i], active_cols[j]]), active_labels[i], active_labels[j])
                     for i in range(n_l) for j in range(i+1, n_l)
                     if corr.loc[active_cols[i], active_cols[j]] == corr.loc[active_cols[i], active_cols[j]]],
                    reverse=True)
                print("> Most correlated: " + " · ".join(f"{a}↔{b} ({r:.2f})" for r, a, b in pairs[:3]))
            print(f"> {len(combined):,} BUY signal bars sampled across {len(fam_frames)} tickers")

    # ── 10g. MR gate filter ───────────────────────────────────────────────────
    print("\n### 10g. MR Gate Filter Analysis\n")
    total_raw  = 0; cc = {"rsi":0,"bb":0,"ibs":0,"vwap":0,"passes":0}
    for ticker, df in all_dfs.items():
        mask = df["score"] >= BUY_THRESH
        total_raw += int(mask.sum())
        if not mask.sum(): continue
        sub = df[mask]
        rsi_ok  = (sub["rsi"].fillna(50)      < MR_RSI_CEIL)   if "rsi"      in sub.columns else pd.Series(False, index=sub.index)
        bb_ok   = (sub["bb_pct_b"].fillna(1)  < MR_BB_CEIL)    if "bb_pct_b" in sub.columns else pd.Series(False, index=sub.index)
        ibs_ok  = (sub["ibs"].fillna(1)       < MR_IBS_CEIL)   if "ibs"      in sub.columns else pd.Series(False, index=sub.index)
        vwap_ok = (sub["vwap_pct"].fillna(0)  < MR_VWAP_FLOOR) if "vwap_pct" in sub.columns else pd.Series(False, index=sub.index)
        passes  = rsi_ok | bb_ok | ibs_ok | vwap_ok
        cc["rsi"] += int(rsi_ok.sum()); cc["bb"]   += int(bb_ok.sum())
        cc["ibs"] += int(ibs_ok.sum()); cc["vwap"] += int(vwap_ok.sum())
        cc["passes"] += int(passes.sum())
    if total_raw:
        pct_p = cc["passes"] / total_raw * 100
        print(f"Raw BUY signals (score ≥ {BUY_THRESH}): **{total_raw:,}**")
        print(f"Passes MR gate: **{cc['passes']:,}** ({pct_p:.1f}%)  |  Filtered: {total_raw-cc['passes']:,} ({100-pct_p:.1f}%)\n")
        print_table(["MR Condition","Triggers","% of Raw BUY"], [
            [f"RSI < {MR_RSI_CEIL}",      f"{cc['rsi']:,}",  f"{cc['rsi']/total_raw*100:.1f}%"],
            [f"BB%B < {MR_BB_CEIL}",       f"{cc['bb']:,}",   f"{cc['bb']/total_raw*100:.1f}%"],
            [f"IBS < {MR_IBS_CEIL}",       f"{cc['ibs']:,}",  f"{cc['ibs']/total_raw*100:.1f}%"],
            [f"VWAP% < {MR_VWAP_FLOOR}%", f"{cc['vwap']:,}", f"{cc['vwap']/total_raw*100:.1f}%"],
        ])

    # ── 10h. Monte Carlo comparison ───────────────────────────────────────────
    print("\n### 10h. Monte Carlo — Naive Baseline vs Optimal Combo\n")
    print("> 8,000 bootstrap simulations. P5 > 0 = edge is statistically real.\n")

    p5b, p95b = _monte_carlo(baseline_trades["net_pct"].tolist())
    print(f"**Baseline (26 fam):**  Sharpe P5={p5b:.2f}  P95={p95b:.2f}"
          + (" ✓ positive P5" if p5b > 0 else " ⚠ P5 ≤ 0"))
    if tdf_opt is not None and not tdf_opt.empty:
        p5o, p95o = _monte_carlo(tdf_opt["net_pct"].tolist())
        print(f"**Optimal combo:**      Sharpe P5={p5o:.2f}  P95={p95o:.2f}"
              + (" ✓ positive P5" if p5o > 0 else " ⚠ P5 ≤ 0"))

    # ── 10i. Three-gate verdict ───────────────────────────────────────────────
    print("\n### 10i. Three-Gate Verdict\n")
    essential_fams_all = [f for f in SIGNAL_FAMILIES if (ablation_results[f].get("sharpe") or 0.0) < bs_sh]
    rv = stats(baseline_trades[baseline_trades["date"] >= pd.Timestamp("2024-01-01")]["net_pct"].tolist())
    gate1 = len(essential_fams_all) >= 3
    gate2 = rv["n"] > 0 and rv["avg"] > 0
    gate3 = bs_avg > 0
    print("| Gate | Criterion | Result | Detail |")
    print("|:---|:---|:---:|:---|")
    print(f"| **G1** | ≥3 families load-bearing | {'✓ PASS' if gate1 else '✗ FAIL'} | {len(essential_fams_all)}/17 essential |")
    print(f"| **G3** | Net positive after costs | {'✓ PASS' if gate3 else '✗ FAIL'} | avg {bs_avg:+.2f}%  MaxDD -{bs_dd:.2f}%  N={bs_n} |")
    gp = sum([gate1, gate2, gate3])
    verdict = {3:"REAL EDGE",2:"PARTIAL EDGE",1:"FRAGILE",0:"NO EDGE"}[gp]
    print(f"\n**{gp}/3 gates → {verdict}**")
    redund = [f for f in SIGNAL_FAMILIES if f not in essential_fams_all]
    if redund:
        print(f"\n> Redundant (confirmed across v1+v2+v3): {', '.join(redund)}")
    print(f"\n---")
    print(f"*v8 · 11 essential families · {len(all_dfs)} tickers · {len(REGIMES)} regimes · {datetime.today().strftime('%Y-%m-%d')}*")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    years = datetime.today().year - int(START[:4])
    print("# Signal Alpha Decomposition — v8 (11 Essential Families)\n")
    print(f"> All 27 families tested across v1-v7. 16 confirmed redundant (ΔSharpe ≥ 0) removed.")
    print(f"> v8 is the clean essential-only script: faster runs, cleaner ablation signal.")
    print(f"> Tickers: {', '.join(TICKERS)}")
    print(f"> Period:  {START} → {END}  ({years}-yr)")
    print(f"> Best practical config: v2 (Sharpe 0.43, N=77). Technical ceiling: v4-opt (Sharpe 0.49, N=10)\n")

    # ── Fetch alt-data ────────────────────────────────────────────────────────
    print("Fetching VIX…",          end=" ", flush=True)
    try:
        vix_df = yf.download("^VIX", start=START, end=END, interval="1d", auto_adjust=False, progress=False)
        if isinstance(vix_df.columns, pd.MultiIndex): vix_df.columns = vix_df.columns.get_level_values(0)
        vix = {pd.Timestamp(str(k)[:10]): float(v) for k, v in vix_df["Close"].items() if pd.notna(v)}
        print(f"ok ({len(vix)} bars)")
    except Exception as e:
        vix = {}; print(f"failed ({e})")

    print("Fetching SPY trend…",    end=" ", flush=True)
    spy_trend = fetch_spy_trend(START, END)
    print(f"ok ({len(spy_trend)} bars)")

    print("Fetching SPY closes…",   end=" ", flush=True)
    spy_closes = _download_etf_closes("SPY", START, END, "SPY")
    print(f"ok ({len(spy_closes)} bars)" if not spy_closes.empty else "failed")

    print("Fetching HYG closes…",   end=" ", flush=True)
    hyg_closes = _download_etf_closes("HYG", START, END, "HYG")
    print(f"ok ({len(hyg_closes)} bars)" if not hyg_closes.empty else "failed (HYG family disabled)")

    print("Fetching FRED STLFSI4…", end=" ", flush=True)
    _fred_key = os.getenv("FRED_API_KEY", "")
    if not _fred_key:
        try:
            for line in open(os.path.join(_PARENT, ".env")):
                if line.startswith("FRED_API_KEY="): _fred_key = line.strip().split("=",1)[1]
        except Exception: pass
    stlfsi4 = fetch_stlfsi4(START, END, _fred_key)
    print(f"ok ({len(stlfsi4)} obs)" if stlfsi4 else "skipped")

    # ── Parallel download + bt indicators ─────────────────────────────────────
    print(f"\nDownloading {len(TICKERS)} tickers (parallel)…\n")
    with Pool(8) as p:
        results = p.map(process_ticker, [(t, vix, spy_trend, stlfsi4, True) for t in TICKERS])

    all_dfs: dict = {}
    for ticker, _t, _bh, df in results:
        if df is not None: all_dfs[ticker] = df

    if not all_dfs: print("[error] No data."); return

    # ── Apply extra indicators for 11 essential families ─────────────────────
    print("Computing extra indicators (11 essential families: ROC, WK52, RS, CMF, DONCHIAN, HYG, PRICESTR)…", flush=True)
    spy_s = spy_closes if not spy_closes.empty else None
    hyg_s = hyg_closes if not hyg_closes.empty else None
    for ticker, df in all_dfs.items():
        compute_extra_indicators(df, spy_closes=spy_s, hyg_closes=hyg_s)

    # ── Compute 11-family baseline scores ────────────────────────────────────
    print(f"Computing 11-family essential-only scores…", flush=True)
    baseline_trades_list = []
    for ticker, df in all_dfs.items():
        df["score"] = compute_scores_masked(df)
        t = simulate_ticker(ticker, df, vix, spy_trend, stlfsi4, mr_only=True)
        if not t.empty: baseline_trades_list.append(t)

    if not baseline_trades_list: print("[error] No baseline trades."); return
    baseline_trades  = pd.concat(baseline_trades_list, ignore_index=True)
    baseline_stats_d = stats(baseline_trades["net_pct"].tolist())

    # ── Version comparison header ──────────────────────────────────────────────
    print(f"\n{'─'*65}")
    print_table(["Version","Families","Config","N","WR","Avg Ret","Sharpe","MaxDD"], [
        ["v2","11",    "MR×0.5 OSC×1.0 (best practical)",  "77",  "66.2%", "+1.45%", "0.43", "-0.60%"],
        ["v4-opt","11","essential-only (ceiling)",           "10",  "70.0%", "+1.02%", "0.49", "-0.18%"],
        ["**v8**","12",f"11 essential + OSC×0.50 generator",
         str(baseline_stats_d["n"]),
         f"{baseline_stats_d['wr']:.1f}%",
         f"{baseline_stats_d['avg']:+.2f}%",
         fmt_sharpe(baseline_stats_d["sharpe"]),
         f"-{baseline_stats_d['max_dd']:.2f}%"],
    ])
    print(f"{'─'*65}\n")

    run_ablation_suite(
        all_dfs         = all_dfs,
        vix             = vix,
        spy_trend       = spy_trend,
        stlfsi4         = stlfsi4,
        baseline_stats  = baseline_stats_d,
        baseline_trades = baseline_trades,
    )


if __name__ == "__main__":
    main()
