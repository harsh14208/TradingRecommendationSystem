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
  v7 26 families   N=477, WR=50.1%, Sharpe=0.15 (full 26-family baseline)
  v8 12 families   Remove 16 redundant → N=4 ← BROKEN: OSC at 0.50 (should be 1.0) + MR absent
       Root cause: quality filters all fire NEGATIVE for oversold stocks; max achievable
       score without MR ≈ 30, can't clear BUY_THRESH=40. N=4 is not signal quality — it's
       a scoring architecture bug. WR=75% Sharpe=0.64 on N=4 has no statistical meaning.
  v9 13 families   Fix: OSC×1.0 (v2-proven) + MR×0.5 (v2-proven) restored as generators
       RESULT: N=33, WR=63.6%, Sharpe=0.30, MaxDD=-0.27% — fix worked but N still low
       Ablation: ROC, RS, ATR_REG all confirmed redundant (ΔSharpe +0.10/+0.08/+0.21)
       These 3 all penalise oversold declining stocks (MR targets) → suppress N while hurting Sharpe
  v10 10 families   Remove ROC, RS, ATR_REG (v9-confirmed redundant) → win-win: more N + better Sharpe
  v11a N=789  Sharpe=0.03 — dual-gate (MOM: RSI 50-68) too loose; random bull-market bars
  v11b N=168  Sharpe=0.19 — tightened MOM gate (8 conditions); still drags Sharpe below v10
       Root cause: 10-day hold + momentum = short-term reversal zone, not continuation
  v11c N=143  Sharpe=0.24 — gap+streak triggers mostly blocked by gate 11 (RSI declining)
       Gate 11 only valid for RSI-triggered entries; gap/streak bypass it
  v11d N=168  Sharpe=0.16 — gate 11 bypass for non-RSI triggers added bad trades; reverted
  v11e 11 fam  50-ticker universe (30 base + 20 diversified large-caps); v11c gate config

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

import math
import os
import sys
import time
import warnings
from contextlib import contextmanager
from datetime import datetime
from multiprocessing import Pool

import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _p in [_PARENT, _HERE]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from backtest_technicals import (
    _EMPTY_STATS,
    BUY_THRESH,
    END,
    MR_BB_CEIL,
    MR_IBS_CEIL,
    MR_RSI_CEIL,
    MR_VWAP_FLOOR,
    REGIMES,
    START,
    fetch_spy_trend,
    fetch_stlfsi4,
    fmt_pf,
    fmt_sharpe,
    print_table,
    process_ticker,
    simulate_ticker,
    stats,
    stats_weighted,
)
from backtest_technicals import (
    TICKERS as _BASE_TICKERS,
)

# ─────────────────────────────────────────────────────────────────────────────
# Curated universe expansion — DECOMP ONLY (main backtest unchanged)
# Criteria: 20-yr+ history, FAANG-profile MR (tech/fintech/quality consumer),
# no binary event risk (pharma FDA, regulatory crises, commodity-only cycles).
# Failed in v11e (excluded): pharma JNJ/PFE/MRK/LLY, heavy industrials HON/BA/CAT,
# pure memory semis MU, consumer staples KO/WMT, media/parks DIS.
# ─────────────────────────────────────────────────────────────────────────────
_DECOMP_EXPANSION = [
    # ── Semiconductor platform / equipment (not memory/commodity) ────────────
    "AVGO",  # Broadcom — chip platform M&A; corrections bounce reliably
    "AMAT",  # Applied Materials — equipment cycle; less volatile than chip makers
    "LRCX",  # Lam Research — equipment
    "KLAC",  # KLA Corp — metrology equipment
    # ── Enterprise software (long history) ───────────────────────────────────
    "ORCL",  # Oracle — DB + cloud; 20-yr correction-and-recovery cycles
    "INTU",  # Intuit — fintech/tax; strong seasonal MR setups
    "ADSK",  # Autodesk — design software; 20-yr history
    "CDNS",  # Cadence Design — EDA; very low idiosyncratic risk
    "SNPS",  # Synopsys — EDA
    "CTSH",  # Cognizant — IT services; sector correction/recovery cycles
    # ── Cloud / security (post-2009 IPOs) ────────────────────────────────────
    "FTNT",  # Fortinet — cybersecurity (2009+)
    "NOW",  # ServiceNow — enterprise workflow (2012+)
    "PANW",  # Palo Alto Networks — cybersecurity (2012+)
    "WDAY",  # Workday — HCM cloud (2012+)
    # ── Consumer internet / travel tech ──────────────────────────────────────
    "BKNG",  # Booking Holdings — travel; 20-40% corrections bounce hard
    "EBAY",  # eBay — marketplace (1998+)
    "PYPL",  # PayPal — fintech (2015+)
    # ── Payment networks (pure toll road, no credit risk) ────────────────────
    "V",  # Visa — pure network (2008+)
    "MA",  # Mastercard — same profile (2006+)
    # ── Financial services non-bank (exchanges, asset managers) ──────────────
    "BLK",  # BlackRock — AUM-driven; not credit-sensitive like banks
    "SCHW",  # Charles Schwab — brokerage; high-beta but not investment-bank
    "CME",  # CME Group — exchange revenue; steady
    "SPGI",  # S&P Global — data/ratings
    "MCO",  # Moody's — ratings
    "ICE",  # Intercontinental Exchange
    "MSCI",  # MSCI — index/data (2007+)
    # ── Consumer / retail (correction-bounce profile) ─────────────────────────
    "LOW",  # Lowe's — home improvement twin to HD (HD already works well)
    "TJX",  # TJX Companies — off-price retail
    "ROST",  # Ross Stores — off-price
    "LULU",  # Lululemon — premium athletic (2007+); high-beta consumer
    # ── Travel / hospitality ─────────────────────────────────────────────────
    "MAR",  # Marriott Hotels — large corrections on travel demand
    "HLT",  # Hilton Hotels (2013+)
    "RCL",  # Royal Caribbean — high-beta travel
    # ── Media / telecom adjacent ─────────────────────────────────────────────
    "CHTR",  # Charter Communications — cable (same profile as CMCSA, which works)
    # ── Auto additional ───────────────────────────────────────────────────────
    "GM",  # General Motors (2010+)
    # ── Technology infrastructure ─────────────────────────────────────────────
    "AKAM",  # Akamai — CDN/edge
    "ACN",  # Accenture — IT consulting; global scale
    # ── Fintech / payment processing ─────────────────────────────────────────
    "FIS",  # Fidelity National Information — payment processing
    "FISV",  # Fiserv — fintech
    # ── Data / analytics platforms ────────────────────────────────────────────
    "VRSK",  # Verisk — data analytics (2009+)
    # ── Homebuilders (rate-driven MR setups) ─────────────────────────────────
    "DHI",  # D.R. Horton — homebuilder; deep MR on rate-rise fears
    "LEN",  # Lennar — homebuilder
    # ── International quality foundry ─────────────────────────────────────────
    "TSM",  # Taiwan Semiconductor — foundry leader; strong MR bounces
    # ── Energy (integrated + services) ──────────────────────────────────────
    "EOG",  # EOG Resources — quality E&P; different cycle from integrated oil
    "XOM",  # ExxonMobil — integrated; 20-yr MR bounces on macro dislocations
    "CVX",  # Chevron — integrated; large corrections during oil downturns
    "COP",  # ConocoPhillips — E&P; high-beta to WTI
    "SLB",  # SLB (Schlumberger) — oilfield services; cycle-driven MR
    # ── Healthcare (large-cap; MR on sector sell-offs, not drug events) ──────
    "JNJ",  # Johnson & Johnson — diversified; MR on legal/sector fear
    "AMGN",  # Amgen — large biotech; MR on sector rotations (1987+)
    "BMY",  # Bristol-Myers — large pharma (1993+)
    "GILD",  # Gilead Sciences — antiviral specialist (1992+)
    "MDT",  # Medtronic — medical devices; steady MR on rate/macro fears
    "ABT",  # Abbott Laboratories — diversified healthcare (1972+)
    "ISRG",  # Intuitive Surgical — robotic surgery (2000+); high-beta healthcare
    # ── Industrials (capital goods / defense / logistics) ────────────────────
    "CAT",  # Caterpillar — construction/mining equipment; commodity MR cycles
    "HON",  # Honeywell — diversified industrial; defensive MR setups
    "GE",  # GE Aerospace — restructured aerospace (historical data 2006+)
    "UNP",  # Union Pacific — railroad; steady earnings MR cycles
    "MMM",  # 3M — diversified manufacturer; rate/demand MR setups
    "BA",  # Boeing — aerospace; large MR bounces on safety/macro fears
    # ── Telecom / media (defensive dividend; MR on rate fears) ──────────────
    "VZ",  # Verizon — defensive telecom; MR on rate-rise fears
    "T",  # AT&T — telecom; post-split high-yield MR (2022+)
    # ── Materials (specialty chemicals; MR on commodity/macro cycles) ────────
    "APD",  # Air Products — industrial gases; steady correction-and-recovery
    "ECL",  # Ecolab — specialty chemicals; quality defensive
    # ── Real Estate (REITs; MR on rate-rise fears) ───────────────────────────
    "AMT",  # American Tower — cell towers; deep MR on rate-rise fears
    "PLD",  # Prologis — industrial REIT; correction bounce cycles
    "SPG",  # Simon Property — mall REIT; high-beta real estate MR
]

TICKERS = list(dict.fromkeys(_BASE_TICKERS + _DECOMP_EXPANSION))  # preserve order, no dupes

# ─────────────────────────────────────────────────────────────────────────────
# Status-tracking helpers
# ─────────────────────────────────────────────────────────────────────────────

_SCRIPT_START: float = time.time()


def _elapsed() -> str:
    s = int(time.time() - _SCRIPT_START)
    return f"{s // 60:02d}:{s % 60:02d}"


def _section(title: str) -> None:
    """Print a timed section header."""
    print(f"\n[{_elapsed()}] ── {title} ──", flush=True)


def _progress(current: int, total: int, label: str = "") -> None:
    """Print inline [current/total] progress with elapsed time."""
    pct = int(current / total * 100)
    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
    suffix = f"  {label}" if label else ""
    print(f"  [{_elapsed()}] [{current:>2}/{total}] {bar} {pct:>3}%{suffix}", flush=True)


# ─────────────────────────────────────────────────────────────────────────────
# Family registry  (26 total)
# ─────────────────────────────────────────────────────────────────────────────

SIGNAL_FAMILIES = [
    # ── 10 families: OSC + MR generators + 8 quality filters ─────────────────
    # v9 ablation confirmed ROC, RS, ATR_REG all redundant (ΔSharpe ≥ 0 when removed).
    # Crucially: they penalise oversold declining stocks — exactly the MR targets —
    # pushing good setups below BUY_THRESH=40 and collapsing N. Removing them gives
    # more trades AND better Sharpe (win-win, no tradeoff).
    #   ROC removed: N 33→54, Sharpe 0.30→0.40
    #   RS removed:  N 33→64, Sharpe 0.30→0.38
    #   ATR_REG:     N 33→34, Sharpe 0.30→0.51
    "osc",  # RSI/Stoch/WR/CCI — signal generator, weight=1.0 (v2 proven)
    "mr",  # BB+RSI+IBS+VWAP-bands — primary MR generator, weight=0.50 (v2 proven)
    "trend",  # MACD/EMA/ADX — essential (v9 ΔSharpe -0.02)
    "vol",  # OBV/Surge/Dry-up — essential (v9 ΔSharpe -0.03)
    "ma",  # SMA/VWAP/Z-score — most critical (v9 ΔSharpe -6.22)
    "wk52",  # 52-week range position — helpful (v9 ΔSharpe -0.03)
    "cmf",  # Chaikin Money Flow — essential (v9 ΔSharpe -0.04)
    "donchian",  # 20-day low MR setup — essential (v9 ΔSharpe -0.07)
    "hyg",  # HYG credit stress — macro filter (borderline, kept for tail risk)
    "pricestr",  # LH/LL price structure — essential (v9 ΔSharpe -0.12)
    "rs_quality",  # 63-day RS rank vs SPY + 52W-high proximity — momentum selector (v11)
]

FAMILY_LABELS = {
    "osc": "OSC     (RSI/Stoch/WR)          ← generator @1.00 weight",
    "mr": "MR      (BB+RSI+IBS+VWAP-bands) ← generator @0.50 weight",
    "trend": "TREND   (MACD/EMA/ADX/BOS)",
    "vol": "VOL     (OBV/Surge/Dry-up)",
    "ma": "MA      (SMA/VWAP/Z-score)       ← most critical",
    "wk52": "WK52    (52-Week Range Position)",
    "cmf": "CMF     (Chaikin Money Flow)",
    "donchian": "DONCHIAN(near 20-day low = MR)   ← MR-contrarian",
    "hyg": "HYG     (Credit stress — HYG 1M)",
    "pricestr": "PRICESTR(LH/LL structure = MR)   ← MR-contrarian",
    "rs_quality": "RS_QUAL (63-day RS rank + 52W-high proximity) ← momentum selector",
}

# OSC + MR first (signal generators) then quality filters in order of ΔSharpe impact.
INCREMENTAL_ORDER = [
    "osc",  # RSI/Stoch — signal generator (weight=1.0)
    "mr",  # BB+RSI+IBS+VWAP-bands — MR generator (weight=0.5)
    "ma",  # structure anchor — most critical filter
    "trend",  # momentum direction
    "vol",  # volume confirmation
    "donchian",  # 20d low MR-contrarian
    "pricestr",  # LH/LL structure MR-contrarian
    "cmf",  # Chaikin flow confirmation
    "wk52",  # 52-week range position
    "hyg",  # credit stress macro filter
    "rs_quality",  # 63d RS rank + 52W-high proximity (v11 momentum selector)
]

FAM_COLS = [
    "osc_f",
    "mr_f",
    "trend_f",
    "vol_f",
    "ma_f",
    "wk52_f",
    "cmf_f",
    "donchian_f",
    "hyg_f",
    "pricestr_f",
    "rs_quality_f",
]

BASE_WEIGHTS: dict[str, float] = {f: 1.0 for f in SIGNAL_FAMILIES}
BASE_WEIGHTS["osc"] = (
    1.00  # §45 OSC sweep: OSC×1.0 is only breakeven setting on 105-ticker universe (Sharpe 0.00 vs -0.24 at 0.3)
)
BASE_WEIGHTS["mr"] = 0.70  # v12 sweep: MR×0.7 optimal (confirmed); re-sweep jointly with OSC×1.0 if N changes
BASE_WEIGHTS["donchian"] = 0.50  # §42: OSC↔DONCHIAN correlation=0.70 (double-counting MR signal); reduce from 1.0
BASE_WEIGHTS["trend"] = 0.00  # §45 ablation: removing TREND = +0.29 Sharpe; MACD/EMA/ADX punish MR-oversold entries
BASE_WEIGHTS["cmf"] = (
    0.00  # §46 ablation: CMF redundant with TREND=0 (ΔSharpe +0.04 if removed); OBV/RVOL carry money-flow info
)

# v11: dual-gate tested but disabled — momentum trades (RSI 50-68) at 10-day hold
# have near-zero edge (short-term reversal effect, Jegadeesh 1990) and dragged
# Sharpe from 0.25 → 0.19 even with 8-condition quality filter.
# v11c fix: extended MR triggers instead — gap-down (≥1.5%) and streak (≤-6 days)
# are orthogonal MR conditions with documented post-gap fill edge (65-70% in large-caps).
DUAL_GATE_ON: bool = False


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
    c = df["Close"]
    h = df["High"]
    l = df["Low"]
    v = df["Volume"]

    # ── ROC(10) — for ROC family ──────────────────────────────────────────────
    df["roc10"] = (c / c.shift(10) - 1) * 100

    # ── WK52 position — for WK52 family ──────────────────────────────────────
    r_max = c.rolling(252, min_periods=30).max()
    r_min = c.rolling(252, min_periods=30).min()
    df["wk52_pos"] = (c - r_min) / (r_max - r_min).replace(0, np.nan)

    # ── 1-Month RS vs SPY — for RS family and MOM gate ───────────────────────
    if spy_closes is not None:
        spy_a = spy_closes.reindex(df.index, method="ffill")
        df["rs_1m"] = ((c / c.shift(21) - 1) - (spy_a / spy_a.shift(21) - 1)) * 100
        # 63-day RS rank — for RS_QUALITY family (v11 momentum selector)
        df["rs_63d"] = ((c / c.shift(63) - 1) - (spy_a / spy_a.shift(63) - 1)) * 100
        # percentile rank over trailing 252 bars: high = outperforming consistently
        df["rs_rank"] = df["rs_63d"].rolling(252, min_periods=63).rank(pct=True) * 100

    # ── CMF(20) — for CMF family ──────────────────────────────────────────────
    mf_mult = ((c - l) - (h - c)) / (h - l).replace(0, np.nan)
    df["cmf"] = (mf_mult * v).rolling(20).sum() / v.rolling(20).sum().replace(0, np.nan)

    # ── DONCHIAN — for DONCHIAN family ───────────────────────────────────────
    dc_hi = h.rolling(20).max()
    dc_lo = l.rolling(20).min()
    df["donchian_pos"] = (c - dc_lo) / (dc_hi - dc_lo).replace(0, np.nan)
    df["donchian_new_high"] = (c >= dc_hi.shift(1)).astype(float)
    df["donchian_new_low"] = (c <= dc_lo.shift(1)).astype(float)

    # ── HYG 1-month return — for HYG family ──────────────────────────────────
    if hyg_closes is not None:
        hyg_a = hyg_closes.reindex(df.index, method="ffill")
        df["hyg_1m"] = (hyg_a / hyg_a.shift(21) - 1) * 100

    # ── Price Structure HH/HL vs LH/LL — for PRICESTR family ─────────────────
    mid = 10
    rh = h.shift(1)
    rl = l.shift(1)
    ph = rh.rolling(mid).max().shift(mid)
    pl = rl.rolling(mid).min().shift(mid)
    rh2 = rh.rolling(mid).max()
    rl2 = rl.rolling(mid).min()
    df["ps_hh_hl"] = ((rh2 > ph * 1.005) & (rl2 > pl * 1.005)).astype(float)
    df["ps_lh_ll"] = ((rh2 < ph * 0.995) & (rl2 < pl * 0.995)).astype(float)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Data fetchers
# ─────────────────────────────────────────────────────────────────────────────


def _download_etf_closes(ticker: str, start: str, end: str, label: str) -> pd.Series:
    try:
        raw = yf.download(ticker, start=start, end=end, interval="1d", auto_adjust=True, progress=False)
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
) -> pd.Series | pd.DataFrame:
    """
    11-family vectorised scoring (essential families only, v7 ablation consensus).
    family_weights: per-family scalar; missing keys default to BASE_WEIGHTS.
    return_families: if True return per-family DataFrame (for correlation).
    """
    n = len(df)

    def _v(col, fill=0.0):
        return df[col].fillna(fill).values.astype(float) if col in df.columns else np.full(n, fill)

    def _b(col):
        if col not in df.columns:
            return np.zeros(n, dtype=bool)
        return df[col].notna().values & (df[col].fillna(0).values.astype(float) == 1.0)

    c = _v("Close")
    rsi = _v("rsi", 50.0)
    rsi_ok = df["rsi"].notna().values if "rsi" in df.columns else np.zeros(n, bool)
    atr = _v("atr", 0.0)
    atr_pct = np.where(c > 0, atr / c, 0.02)
    low_atr = atr_pct < 0.010
    adx_val = _v("adx", 0.0)
    rvol = _v("rvol", 1.0)
    chg_pct = _v("change_pct", 0.0)
    sma200_v = _v("sma200", 0.0)
    sma200_ok = df["sma200"].notna().values if "sma200" in df.columns else np.zeros(n, bool)
    sma20_v = _v("sma20", 0.0)
    sma20_ok = df["sma20"].notna().values if "sma20" in df.columns else np.zeros(n, bool)

    # ── Oscillator (signal generator at reduced weight 0.30) ─────────────────
    # OSC was "redundant" with KELTNER (corr=0.70) in v1-v7 full system.
    # With KELTNER removed, OSC is the primary positive score generator for RSI<35 stocks.
    osc = np.zeros(n)
    osc += np.where(rsi_ok & (rsi < 25), 28, 0)
    osc += np.where(rsi_ok & (rsi >= 25) & (rsi < 35), 16, 0)
    osc += np.where(rsi_ok & (rsi > 75), -18, 0)
    osc += np.where(rsi_ok & (rsi >= 65) & (rsi <= 75), -10, 0)
    wr = _v("wr", -50)
    wr_ok = df["wr"].notna().values if "wr" in df.columns else np.zeros(n, bool)
    osc += np.where(wr_ok & (wr <= -85), 10, 0)
    osc += np.where(wr_ok & (wr >= -15), -8, 0)
    osc = np.clip(osc, -25, 25)

    # ── Trend ─────────────────────────────────────────────────────────────────
    trend = np.zeros(n)
    hist = _v("macd_hist", 0)
    h_ok = df["macd_hist"].notna().values if "macd_hist" in df.columns else np.zeros(n, bool)
    hist_p = _v("macd_hist_p", 0)
    cu_m = h_ok & (hist > 0) & (hist_p <= 0)
    cd_m = h_ok & (hist < 0) & (hist_p >= 0)
    rise = hist > hist_p
    no_x = h_ok & ~cu_m & ~cd_m
    trend += np.select(
        [
            cu_m & rise,
            cd_m & ~rise,
            cu_m & ~rise,
            cd_m & rise,
            no_x & (hist > 0) & rise,
            no_x & (hist < 0) & ~rise,
            no_x & (hist > 0) & ~rise,
            no_x & (hist < 0) & rise,
        ],
        [18, -18, 12, -12, 16, -16, 6, -6],
        default=0,
    )
    trend += np.where(_b("macd_bull_div"), 20, 0)
    trend += np.where(_b("macd_bear_div"), -20, 0)
    e8 = _v("ema8", 0.0)
    e21 = _v("ema21", 0.0)
    e8p = _v("ema8_p", 0.0)
    e21p = _v("ema21_p", 0.0)
    em_cols = ["ema8", "ema21", "ema8_p", "ema21_p"]
    em_ok = df[em_cols].notna().all(axis=1).values if all(x in df.columns for x in em_cols) else np.zeros(n, bool)
    vc = rvol > 1.2
    e_cu = em_ok & (e8 > e21) & (e8p <= e21p)
    e_cd = em_ok & (e8 < e21) & (e8p >= e21p)
    trend += np.select(
        [
            e_cu & vc,
            e_cu & ~vc,
            e_cd & vc,
            e_cd & ~vc,
            em_ok & ~e_cu & ~e_cd & (e8 > e21),
            em_ok & ~e_cu & ~e_cd & (e8 <= e21),
        ],
        [14, 8, -14, -8, 4, -4],
        default=0,
    )
    pdi = _v("plus_di", 0)
    mdi = _v("minus_di", 0)
    di_ok = (
        df["plus_di"].notna().values & df["minus_di"].notna().values if "plus_di" in df.columns else np.zeros(n, bool)
    )
    trend += np.select(
        [
            di_ok & (adx_val > 40) & (pdi > mdi),
            di_ok & (adx_val > 40) & (pdi <= mdi),
            di_ok & (adx_val > 25) & (adx_val <= 40) & (pdi > mdi),
            di_ok & (adx_val > 25) & (adx_val <= 40) & (pdi <= mdi),
        ],
        [18, -18, 10, -10],
        default=0,
    )
    atr_exp = _v("atr_expand_bars", 0)
    trend += np.where(atr_exp >= 5, np.where(chg_pct >= 0, 16, -10), 0)
    trend += np.where((atr_exp >= 3) & (atr_exp < 5), np.where(chg_pct >= 0, 10, -10), 0)
    if "market_struct" in df.columns:
        ms = df["market_struct"].values
        trend += np.where(ms == "bos_bull", 12, np.where(ms == "bos_bear", -12, np.where(ms == "mss_bull", 16, 0)))
    trend = np.clip(trend, -28, 28)
    trend = np.where(
        trend > 0,
        np.where(rsi > 75, trend * 0.30, np.where(rsi > 65, trend * 0.55, trend)),
        np.where(rsi < 25, trend * 0.30, np.where(rsi < 35, trend * 0.55, trend)),
    )

    # ── Volume ────────────────────────────────────────────────────────────────
    vol = np.zeros(n)
    obv_ab = _v("obv_above", 0)
    obv_sl = _v("obv_slope", 0)
    ob_ok = (
        df["obv_above"].notna().values & df["obv_slope"].notna().values
        if "obv_above" in df.columns
        else np.zeros(n, bool)
    )
    vol += np.where(ob_ok & (obv_ab > 0) & (obv_sl > 0), 12, 0)  # OBV above + rising (osc removed)
    vol += np.where(ob_ok & (obv_ab <= 0) & (obv_sl < 0), -12, 0)  # OBV below + falling
    vs = _b("vol_surge")
    vd = _b("vol_dryup")
    vol += np.where(vs & (obv_sl > 0) & sma20_ok & (c > sma20_v), 14, 0)
    vol += np.where(vs & (obv_sl < 0) & sma20_ok & (c < sma20_v), -14, 0)
    vol += np.where(vd, -8, 0)
    vol += np.where(_b("obv_bull_div"), 12, 0)
    vol += np.where(_b("obv_bear_div"), -10, 0)
    vol += np.where((rsi < 40) & (rvol >= 2.0) & (chg_pct < 0), 10, 0)
    vol += np.where(rvol >= 3.0, np.where(chg_pct >= 0, 10, -10), 0)
    vol = np.clip(vol, -20, 20)

    # ── MA ────────────────────────────────────────────────────────────────────
    ma = np.zeros(n)
    sma50 = _v("sma50", 0.0)
    s50_ok = df["sma50"].notna().values if "sma50" in df.columns else np.zeros(n, bool)
    sma200 = sma200_v
    s200_ok = sma200_ok
    ema200 = _v("ema200", 0.0)
    e200_ok = df["ema200"].notna().values if "ema200" in df.columns else np.zeros(n, bool)
    s200_sl = _v("sma200_slope", 0)
    s50_sl = _v("sma50_slope", 0)
    s20_sl = _v("sma20_slope", 0)
    zscore = _v("price_zscore", 0)
    ma += np.select(
        [
            s200_ok & (c > sma200 * 1.02) & (s200_sl > 0),
            s200_ok & (c > sma200 * 1.01),
            s200_ok & (c < sma200 * 0.98) & (s200_sl < 0),
            s200_ok & (c < sma200 * 0.99),
        ],
        [18, 12, -18, -12],
        default=0,
    )
    ma += np.select(
        [
            s50_ok & (c > sma50) & (s50_sl > 0),
            s50_ok & (c > sma50),
            s50_ok & (c < sma50) & (s50_sl < 0),
            s50_ok & (c < sma50),
        ],
        [16, 8, -14, -6],
        default=0,
    )
    ma += np.where(sma20_ok & (c > sma20_v) & (s20_sl > 0), 12, 0)
    ma += np.where(sma20_ok & (c < sma20_v) & (s20_sl < 0), -8, 0)
    ma += np.select(
        [zscore < -2.0, (zscore >= -2.0) & (zscore < -1.5), zscore > 2.0, (zscore > 1.5) & (zscore <= 2.0)],
        [14, 7, -12, -6],
        default=0,
    )
    ma += np.where(s50_ok & s200_ok & (sma50 > sma200 * 1.005), 10, 0)
    ma += np.where(s50_ok & s200_ok & (sma50 < sma200 * 0.995), -10, 0)
    ma += np.where(e200_ok & s200_ok & (c > ema200) & (c > sma200), 3, 0)
    ma += np.where(e200_ok & s200_ok & (c < ema200) & (c < sma200), -3, 0)
    vwap_pct = _v("vwap_pct", 0)
    vp_ok = df["vwap_pct"].notna().values if "vwap_pct" in df.columns else np.zeros(n, bool)
    vwap_slope = (
        df["vwap_slope_pos"].fillna(False).astype(bool).values if "vwap_slope_pos" in df.columns else np.zeros(n, bool)
    )
    ma += np.where(vp_ok & vwap_slope & (vwap_pct > 0), 6, 0)
    ma += np.where(vp_ok & ~vwap_slope & (vwap_pct < 0), -5, 0)
    vwap_20 = _v("vwap_20", 0.0)
    v20_ok = df["vwap_20"].notna().values if "vwap_20" in df.columns else np.zeros(n, bool)
    prev_c = _v("Close_prev", 0.0)
    prev_vwap = _v("vwap_20_prev", 0.0)
    ma += np.where(v20_ok & (rvol >= 2.0) & (prev_c < prev_vwap) & (c >= vwap_20), 12, 0)
    ma += np.where(v20_ok & (rvol >= 2.0) & (prev_c > prev_vwap) & (c <= vwap_20), -14, 0)
    vp_poc = _v("vp_poc", 0)
    vp_vah = _v("vp_vah", 0)
    vp_val = _v("vp_val", 0)
    vp_cols = ["vp_poc", "vp_vah", "vp_val"]
    vp_ok2 = df[vp_cols].notna().all(axis=1).values if all(x in df.columns for x in vp_cols) else np.zeros(n, bool)
    ma += np.where(vp_ok2 & (rvol >= 1.5) & (c > vp_vah), 16, 0)
    ma += np.where(vp_ok2 & (rvol >= 1.5) & (c < vp_val), -14, 0)
    poc_d = np.where(vp_poc > 0, np.abs(c - vp_poc) / vp_poc * 100, 99)
    ma += np.where(vp_ok2 & (poc_d <= 0.25) & (adx_val < 20), 8, 0)
    ma = np.clip(ma, -28, 28)

    # ── Regime layers — TREND adjustment only (MR/OSC families removed) ───────
    strong = adx_val > 40
    s200_sl_a = _v("sma200_slope", 0)
    trend = np.where(strong, trend * 1.20, trend)  # amplify in strong trend
    trend = np.where(sma200_ok & (s200_sl_a < -0.01), trend * 0.30, trend)  # dampen in bear market
    trend = np.where(low_atr, 0.0, trend)  # no trend signal in low-ATR environment
    vol = np.where(low_atr, 0.0, vol)  # no volume signal in low-ATR environment

    # ── ROC (cap ±10)
    roc10_arr = _v("roc10", 0)
    roc10_ok = df["roc10"].notna().values if "roc10" in df.columns else np.zeros(n, bool)
    roc_sc = np.select(
        [
            roc10_ok & (roc10_arr > 8),
            roc10_ok & (roc10_arr > 4) & (roc10_arr <= 8),
            roc10_ok & (roc10_arr < -8),
            roc10_ok & (roc10_arr < -4) & (roc10_arr >= -8),
        ],
        [8, 4, -8, -4],
        default=0,
    )
    roc_sc = np.clip(roc_sc, -10, 10)

    # WK52 (cap ±8)
    wk52_pos = _v("wk52_pos", 0.5)
    wk52_ok = df["wk52_pos"].notna().values if "wk52_pos" in df.columns else np.zeros(n, bool)
    wk52_sc = np.select(
        [
            wk52_ok & (wk52_pos >= 0.90),
            wk52_ok & (wk52_pos >= 0.75) & (wk52_pos < 0.90),
            wk52_ok & (wk52_pos <= 0.10),
            wk52_ok & (wk52_pos <= 0.25) & (wk52_pos > 0.10),
        ],
        [4, 2, -4, -2],
        default=0,
    )
    wk52_sc = np.clip(wk52_sc, -8, 8)

    # RS (cap ±12)
    rs_1m = _v("rs_1m", 0)
    rs_ok = df["rs_1m"].notna().values if "rs_1m" in df.columns else np.zeros(n, bool)
    rs_sc = np.select(
        [
            rs_ok & (rs_1m > 8),
            rs_ok & (rs_1m > 2) & (rs_1m <= 8),
            rs_ok & (rs_1m < -8),
            rs_ok & (rs_1m < -2) & (rs_1m >= -8),
        ],
        [12, 4, -12, -5],
        default=0,
    )
    rs_sc = np.clip(rs_sc, -12, 12)

    # ── CMF(20) — Chaikin Money Flow (inflow=bullish, outflow=bearish)
    # Rationale: heavy outflow on an oversold stock = still selling, not yet safe to enter
    # Positive CMF on a technically oversold stock = smart money accumulating = high conviction
    cmf_arr = _v("cmf", 0)
    cmf_ok = df["cmf"].notna().values if "cmf" in df.columns else np.zeros(n, bool)
    cmf_sc = np.select(
        [
            cmf_ok & (cmf_arr > 0.25),
            cmf_ok & (cmf_arr > 0.10) & (cmf_arr <= 0.25),
            cmf_ok & (cmf_arr < -0.25),
            cmf_ok & (cmf_arr < -0.10) & (cmf_arr >= -0.25),
        ],
        [10, 5, -10, -5],
        default=0,
    )
    cmf_sc = np.clip(cmf_sc, -10, 10)

    # DONCHIAN (cap ±10) — MR-contrarian: near/at 20-day low = 20-day oversold = MR bounce
    # At/near 20-day high = overbought = mild negative (not MR entry)
    dc_pos = _v("donchian_pos", 0.5)
    dc_ok = df["donchian_pos"].notna().values if "donchian_pos" in df.columns else np.zeros(n, bool)
    don_sc = np.zeros(n)
    don_sc += np.where(_b("donchian_new_low"), 10, 0)  # at 20d low = MR setup
    don_sc += np.where(dc_ok & (dc_pos <= 0.10) & ~_b("donchian_new_low"), 5, 0)  # near 20d low
    don_sc += np.where(_b("donchian_new_high"), -6, 0)  # at 20d high = not MR
    don_sc += np.where(dc_ok & (dc_pos >= 0.90) & ~_b("donchian_new_high"), -3, 0)  # near 20d high
    don_sc = np.clip(don_sc, -10, 10)

    # HYG — credit stress proxy (cap ±10)
    hyg_1m = _v("hyg_1m", 0)
    hyg_ok = df["hyg_1m"].notna().values if "hyg_1m" in df.columns else np.zeros(n, bool)
    hyg_sc = np.select(
        [hyg_ok & (hyg_1m > 2), hyg_ok & (hyg_1m < -5), hyg_ok & (hyg_1m < -3) & (hyg_1m >= -5)],
        [5, -10, -8],
        default=0,
    )
    hyg_sc = np.clip(hyg_sc, -10, 10)

    # PIVOT, RSI_LEVEL, EARN, REDDAY, MOM_DECEL, SECTOR_RS, SUPER, HURST, GAP — all removed
    # (confirmed redundant v6/v7; ΔSharpe ≥ 0 when removed from baseline)

    # ── ATR_REG (ATR percentile rank — volatility regime, cap ±8) ────────────
    # low rank = vol coiling = MR-friendly; high rank = expanding = momentum-dominant
    atr_rk = _v("atr_pct_rank", 50)
    ark_ok = df["atr_pct_rank"].notna().values if "atr_pct_rank" in df.columns else np.zeros(n, bool)
    atrreg_sc = np.select(
        [
            ark_ok & (atr_rk < 10),
            ark_ok & (atr_rk >= 10) & (atr_rk < 20),
            ark_ok & (atr_rk > 90),
            ark_ok & (atr_rk >= 80) & (atr_rk <= 90),
        ],
        [8, 4, -6, -3],
        default=0,
    )
    atrreg_sc = np.clip(atrreg_sc, -8, 8)

    # ── PRICESTR (LH/LL price structure MR-contrarian, cap ±8) ───────────────
    pstr_sc = np.zeros(n)
    pstr_sc += np.where(_b("ps_lh_ll"), 8, 0)  # lower highs + lower lows = MR bounce setup
    pstr_sc += np.where(_b("ps_hh_hl"), -4, 0)  # uptrend = not an MR entry
    pstr_sc = np.clip(pstr_sc, -8, 8)

    # ── MR — BB+RSI confluence, IBS, VWAP ±2σ bands, ATR contraction (cap ±18) ──
    # Reintroduced at v2-proven weight (0.50): the 11 quality filters all fire
    # NEGATIVE for oversold declining stocks. Without MR as a positive generator,
    # max achievable score ≈ 30 — insufficient to clear BUY_THRESH=40 (→ N=4).
    # MR is the primary oversold signal in the main backtest; its absence here
    # was the sole cause of N collapsing from 477 (v7) to 4 (v8).
    bb_arr = _v("bb_pct_b", 0.5)
    bb_ok2 = df["bb_pct_b"].notna().values if "bb_pct_b" in df.columns else np.zeros(n, bool)
    ibs_arr = _v("ibs", 0.5)
    ibs_ok2 = df["ibs"].notna().values if "ibs" in df.columns else np.zeros(n, bool)
    mr_raw = np.zeros(n)
    # BB + RSI confluence (same tiers as main backtest compute_scores)
    mr_raw += np.select(
        [
            bb_ok2 & (bb_arr < 0.05) & (rsi < 35),
            bb_ok2 & (bb_arr < 0.05) & (rsi >= 35) & (rsi < 45),
            bb_ok2 & (bb_arr < 0.05),
            bb_ok2 & (bb_arr >= 0.05) & (bb_arr < 0.15) & (rsi < 35),
            bb_ok2 & (bb_arr >= 0.05) & (bb_arr < 0.15) & (rsi >= 35) & (rsi < 45),
        ],
        [18, 12, 6, 10, 5],
        default=0,
    )
    mr_raw += np.select(
        [
            bb_ok2 & (bb_arr > 0.95) & (rsi > 65),
            bb_ok2 & (bb_arr > 0.95) & (rsi > 55) & (rsi <= 65),
            bb_ok2 & (bb_arr > 0.85) & (bb_arr <= 0.95) & (rsi > 65),
            bb_ok2 & (bb_arr > 0.85) & (bb_arr <= 0.95) & (rsi > 55) & (rsi <= 65),
        ],
        [-14, -8, -8, -4],
        default=0,
    )
    mr_raw += np.where(_b("squeeze_breakout_up"), 16, 0)
    mr_raw += np.where(_b("squeeze_breakout_down"), -16, 0)
    mr_raw += np.where(bb_ok2 & (adx_val < 20) & (bb_arr < 0.15), 6, 0)
    # IBS extremes (intrabar close position)
    mr_raw += np.select(
        [ibs_ok2 & (ibs_arr < 0.05), ibs_ok2 & (ibs_arr >= 0.05) & (ibs_arr < 0.10), ibs_ok2 & (ibs_arr > 0.90)],
        [15, 8, -10],
        default=0,
    )
    # VWAP ±2σ band extremes
    b2u = _v("vwap_band2_upper", np.inf)
    b2u_ok = df["vwap_band2_upper"].notna().values if "vwap_band2_upper" in df.columns else np.zeros(n, bool)
    b2l = _v("vwap_band2_lower", -np.inf)
    b2l_ok = df["vwap_band2_lower"].notna().values if "vwap_band2_lower" in df.columns else np.zeros(n, bool)
    mr_raw += np.where(b2u_ok & (c >= b2u), -14, 0)
    mr_raw += np.where(b2l_ok & (c <= b2l), 14, 0)
    # ATR contraction (coiling = MR-friendly)
    atr_con2 = _v("atr_contract_bars", 0)
    mr_raw += np.where(atr_con2 >= 5, 6, 0)
    # ADX regime: suppress in strong trends, amplify in ranging markets
    mod_mr = (adx_val > 25) & ~strong
    rng_mr = ~strong & ~mod_mr
    mr_raw = np.where(strong, mr_raw * 0.10, mr_raw)
    mr_raw = np.where(mod_mr, mr_raw * 0.40, mr_raw)
    mr_raw = np.where(rng_mr, mr_raw * 1.20, mr_raw)
    mr_raw = np.where(rng_mr & bb_ok2 & (bb_arr < 0.10), mr_raw * 1.30, mr_raw)
    # Bear market suppression / healthy-uptrend dip boost
    mr_raw = np.where(sma200_ok & (c > sma200_v) & (mr_raw < 0), mr_raw * 0.20, mr_raw)
    mr_raw = np.where(sma200_ok & (s200_sl_a > 0) & (c < sma200_v * 0.98), mr_raw * 1.30, mr_raw)
    # ATR rank scaling (coiling = MR boost, expanding = MR penalty)
    mr_raw = mr_raw * np.where(ark_ok & (atr_rk < 10), 1.4, np.where(ark_ok & (atr_rk > 90), 0.5, 1.0))
    mr_sc = np.clip(mr_raw, -18, 18)

    # ── RS Quality — 63-day RS rank + 52W-high proximity (v11 momentum selector)
    # Only positive contributions (no penalty for low RS — MR targets can have
    # low RS and should not be penalized). Boosts momentum breakout bars over
    # BUY_THRESH so the dual_gate momentum path generates enough trade candidates.
    rs_rank_v = _v("rs_rank", 50)  # percentile 0-100; 50 = median
    rs_rk_ok = df["rs_rank"].notna().values if "rs_rank" in df.columns else np.zeros(n, bool)
    wk52_pos = _v("wk52_pos", 0.5)
    rq_raw = np.zeros(n)
    rq_raw += np.where(rs_rk_ok & (rs_rank_v >= 80), 12, 0)  # top quintile: outperforming 80% of peers
    rq_raw += np.where(rs_rk_ok & (rs_rank_v >= 60) & (rs_rank_v < 80), 6, 0)
    rq_raw += np.where(wk52_pos >= 0.92, 10, 0)  # within 8% of 52W high — George & Hwang anchoring
    rq_raw += np.where((wk52_pos >= 0.80) & (wk52_pos < 0.92), 4, 0)
    rq_sc = np.clip(rq_raw, 0, 16)  # no negatives: MR bars with low RS get 0 (neutral)

    # ── Assemble 11 families (OSC + MR generators + 8 quality filters + RS_QUALITY)
    # ROC, RS, ATR_REG excluded: confirmed redundant in v9 — they penalise the
    # oversold declining stocks that are the MR targets, reducing N and Sharpe.
    fw = dict(BASE_WEIGHTS)
    if family_weights:
        fw.update(family_weights)

    osc_f = np.clip(osc, -25, 25) * 1.00 * fw.get("osc", 1.00)
    mr_f = np.clip(mr_sc, -18, 18) * 1.00 * fw.get("mr", 0.50)
    trend_f = np.clip(trend, -28, 28) * 0.90 * fw.get("trend", 1.0)
    vol_f = np.clip(vol, -20, 20) * 0.85 * fw.get("vol", 1.0)
    ma_f = np.clip(ma, -28, 28) * 1.00 * fw.get("ma", 1.0)
    wk52_f = np.clip(wk52_sc, -8, 8) * 1.00 * fw.get("wk52", 1.0)
    cmf_f = np.clip(cmf_sc, -10, 10) * 1.00 * fw.get("cmf", 1.0)
    don_f = np.clip(don_sc, -10, 10) * 1.00 * fw.get("donchian", 1.0)
    hyg_f = np.clip(hyg_sc, -10, 10) * 1.00 * fw.get("hyg", 1.0)
    pstr_f = np.clip(pstr_sc, -8, 8) * 1.00 * fw.get("pricestr", 1.0)
    rq_f = np.clip(rq_sc, 0, 16) * 1.00 * fw.get("rs_quality", 1.0)

    score = osc_f + mr_f + trend_f + vol_f + ma_f + wk52_f + cmf_f + don_f + hyg_f + pstr_f + rq_f

    stk = np.stack([osc_f, mr_f, trend_f, vol_f, ma_f, wk52_f, cmf_f, don_f, hyg_f, pstr_f, rq_f], axis=1)
    bull_cnt = (stk > 5).sum(axis=1)
    bear_cnt = (stk < -5).sum(axis=1)
    score = np.where((score > 0) & (bull_cnt < 2), score * 0.50, score)
    score = np.where((score < 0) & (bear_cnt < 2), score * 0.50, score)
    score = np.where((score > 0) & vd & (rsi >= 30), score * 0.70, score)
    score = np.round(score, 2)

    if return_families:
        return pd.DataFrame(
            {
                "osc_f": osc_f,
                "mr_f": mr_f,
                "trend_f": trend_f,
                "vol_f": vol_f,
                "ma_f": ma_f,
                "wk52_f": wk52_f,
                "cmf_f": cmf_f,
                "donchian_f": don_f,
                "hyg_f": hyg_f,
                "pricestr_f": pstr_f,
                "rs_quality_f": rq_f,
                "score": score,
            },
            index=df.index,
        )

    return pd.Series(score, index=df.index)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _run(fw_override: dict, all_dfs, vix, spy_trend, stlfsi4) -> tuple[dict, pd.DataFrame]:
    """Run simulation with BASE_WEIGHTS merged with fw_override."""
    fw = dict(BASE_WEIGHTS)
    fw.update(fw_override)
    trades_list = []
    for ticker, df in all_dfs.items():
        df2 = df.copy()
        df2["score"] = compute_scores_masked(df2, family_weights=fw)
        t = simulate_ticker(ticker, df2, vix, spy_trend, stlfsi4, mr_only=True, dual_gate=DUAL_GATE_ON)
        if not t.empty:
            trades_list.append(t)
    if not trades_list:
        return dict(_EMPTY_STATS), pd.DataFrame()
    tdf = pd.concat(trades_list, ignore_index=True)
    return stats(tdf["net_pct"].tolist()), tdf


def _mask_ablate(fam):
    return {fam: 0.0}


def _mask_include(inc):
    return {f: (1.0 if f in inc else 0.0) for f in SIGNAL_FAMILIES}


def _fmt_row(label, sv, bs):
    sh = sv.get("sharpe") or 0.0
    d_sh = sh - (bs.get("sharpe") or 0.0)
    d_wr = sv["wr"] - bs["wr"]
    d_av = sv["avg"] - bs["avg"]
    if d_sh < -0.03:
        vd = "✓ essential"
    elif d_sh < 0.0:
        vd = "~ helpful"
    else:
        vd = "✗ redundant"
    return [
        label,
        str(sv["n"]),
        f"{sv['wr']:.1f}% ({d_wr:+.1f}pp)",
        f"{sv['avg']:+.2f}% ({d_av:+.2f}pp)",
        f"{fmt_sharpe(sv['sharpe'])} ({d_sh:+.2f})",
        f"-{sv['max_dd']:.2f}%",
        vd,
    ]


def _monte_carlo(rets: list[float], n_sims: int = 8000) -> tuple[float, float]:
    if not rets:
        return 0.0, 0.0
    arr = np.array(rets)
    sims = [
        stats(np.random.choice(arr, size=len(arr), replace=True).tolist()).get("sharpe") or 0.0 for _ in range(n_sims)
    ]
    return float(np.percentile(sims, 5)), float(np.percentile(sims, 95))


# ─────────────────────────────────────────────────────────────────────────────
# §10 — full decomposition report  (v3)
# ─────────────────────────────────────────────────────────────────────────────


def run_ablation_suite(all_dfs, vix, spy_trend, stlfsi4, baseline_stats, baseline_trades):
    print("\n## 10. Signal Alpha Decomposition — v10 (OSC×1.0 + MR×0.5 + 8 Quality Filters)\n")
    print(f"> {len(all_dfs)} tickers  ·  10 families: OSC×1.0 + MR×0.5 generators + 8 quality filters")
    print("> Removed (v1-v10): mfi, candle, rsi_div, keltner, streak, pivot, super, hurst, gap,")
    print(">   rsi_level, earn, redday, mom_decel, sector_rs, roc, rs, atr_reg — all ΔSharpe ≥ 0")
    print("> ROC/RS/ATR_REG removed in v10: penalise MR targets → less N AND worse Sharpe (v9 ablation)")
    print("> MR-only gate ON  ·  same entry/exit rules\n")

    bs_sh = baseline_stats.get("sharpe") or 0.0
    bs_wr = baseline_stats["wr"]
    bs_avg = baseline_stats["avg"]
    bs_dd = baseline_stats["max_dd"]
    bs_n = baseline_stats["n"]

    # ── 10a. Ablation ─────────────────────────────────────────────────────────
    _section("10a. Ablation Test")
    print("### 10a. Ablation Test — Remove One Family\n")

    abl_rows = [
        [
            "**BASELINE** (10 families: OSC×1.0 + MR×0.5 + 8 filters, v10)",
            str(bs_n),
            f"{bs_wr:.1f}%",
            f"{bs_avg:+.2f}%",
            fmt_sharpe(baseline_stats["sharpe"]),
            f"-{bs_dd:.2f}%",
            "—",
        ]
    ]
    ablation_results: dict[str, dict] = {}

    for _i, fam in enumerate(SIGNAL_FAMILIES, 1):
        _progress(_i, len(SIGNAL_FAMILIES), f"ablating {fam}")
        sv, _ = _run(_mask_ablate(fam), all_dfs, vix, spy_trend, stlfsi4)
        ablation_results[fam] = sv
        abl_rows.append(_fmt_row(f"−{FAMILY_LABELS[fam]}", sv, baseline_stats))

    print_table(["Family Removed", "N", "Win Rate (Δ)", "Avg Ret (Δ)", "Sharpe (Δ)", "Max DD", "Verdict"], abl_rows)
    print("\n> ✓ essential = ΔSharpe < −0.03  ·  ~ helpful = ΔSharpe < 0  ·  ✗ redundant = ΔSharpe ≥ 0")

    # ── 10b. Incremental Build ────────────────────────────────────────────────
    _section("10b. Incremental Build")
    print("\n### 10b. Incremental Build — Add One Family at a Time\n")
    inc_rows = []
    prev_sh = None
    included: list[str] = []

    for _i, fam in enumerate(INCREMENTAL_ORDER, 1):
        included.append(fam)
        _progress(_i, len(INCREMENTAL_ORDER), f"+{fam}")
        sv, _ = _run({f: (1.0 if f in included else 0.0) for f in SIGNAL_FAMILIES}, all_dfs, vix, spy_trend, stlfsi4)
        sh = sv.get("sharpe") or 0.0
        d_sh = (sh - prev_sh) if prev_sh is not None else sh
        inc_rows.append(
            [
                f"+{fam.upper()}",
                str(sv["n"]),
                f"{sv['wr']:.1f}%",
                f"{sv['avg']:+.2f}%",
                f"{fmt_sharpe(sv['sharpe'])} ({'first' if prev_sh is None else f'{d_sh:+.2f}'})",
                f"-{sv['max_dd']:.2f}%",
            ]
        )
        prev_sh = sh

    inc_rows.append(
        [
            "**= Baseline**",
            str(bs_n),
            f"{bs_wr:.1f}%",
            f"{bs_avg:+.2f}%",
            f"{fmt_sharpe(baseline_stats['sharpe'])} (ref)",
            f"-{bs_dd:.2f}%",
        ]
    )
    print_table(["Added", "N", "WR", "Avg Ret", "Sharpe (Δ)", "Max DD"], inc_rows)

    # ── 10c. Optimal sub-combination ──────────────────────────────────────────
    print("\n### 10c. Optimal Sub-Combination (essential + helpful families only)\n")

    essential_fams = [f for f in SIGNAL_FAMILIES if (ablation_results[f].get("sharpe") or 0.0) < bs_sh]
    print(f"  Essential families: {essential_fams}", flush=True)
    print(f"  Running optimal subset ({len(essential_fams)} families)…", flush=True)
    sv_opt, tdf_opt = _run(_mask_include(essential_fams), all_dfs, vix, spy_trend, stlfsi4)
    d_sh_opt = (sv_opt.get("sharpe") or 0.0) - bs_sh

    print_table(
        ["Config", "N", "WR", "Avg Ret", "Sharpe", "Max DD"],
        [
            [
                "Full baseline (26 fam)",
                str(bs_n),
                f"{bs_wr:.1f}%",
                f"{bs_avg:+.2f}%",
                fmt_sharpe(baseline_stats["sharpe"]),
                f"-{bs_dd:.2f}%",
            ],
            [
                f"Optimal ({len(essential_fams)} fam)",
                str(sv_opt["n"]),
                f"{sv_opt['wr']:.1f}%",
                f"{sv_opt['avg']:+.2f}%",
                f"{fmt_sharpe(sv_opt['sharpe'])} ({d_sh_opt:+.2f})",
                f"-{sv_opt['max_dd']:.2f}%",
            ],
        ],
    )
    print(f"\n> Optimal families: {', '.join(essential_fams)}")

    # ── 10d. Weight sweep — MR and OSC ────────────────────────────────────────
    _section("10d. Weight Sweep")
    print("\n### 10d. Weight Sweep — MR and OSC\n")
    print("> Both confirmed redundant in v1+v2. Sweeping confirms optimal weight.\n")

    _weights_to_sweep = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
    for swept_fam in ["mr", "osc"]:
        print(f"**{swept_fam.upper()} weight sweep:**\n")
        sweep_rows = []
        for _wi, w in enumerate(_weights_to_sweep, 1):
            _progress(_wi, len(_weights_to_sweep), f"{swept_fam}={w:.1f}")
            sv, _ = _run({swept_fam: w}, all_dfs, vix, spy_trend, stlfsi4)
            d_sh = (sv.get("sharpe") or 0.0) - bs_sh
            sweep_rows.append(
                [
                    f"{w:.1f}",
                    str(sv["n"]),
                    f"{sv['wr']:.1f}%",
                    f"{sv['avg']:+.2f}%",
                    f"{fmt_sharpe(sv['sharpe'])} ({d_sh:+.2f})",
                    f"-{sv['max_dd']:.2f}%",
                ]
            )
        print_table(
            [f"{swept_fam.upper()} weight", "N", "WR", "Avg Ret", "Sharpe (Δ vs baseline)", "Max DD"], sweep_rows
        )
        print()

    # ── 10e. Regime survival (optimal combo) ──────────────────────────────────
    _section("10e. Regime Survival")
    print("\n### 10e. Regime Survival — Optimal Combination\n")
    if tdf_opt is not None and not tdf_opt.empty:
        reg_rows = []
        for rname, rstart, rend in REGIMES:
            mask = (tdf_opt["date"] >= pd.Timestamp(rstart)) & (tdf_opt["date"] <= pd.Timestamp(rend))
            sv = stats(tdf_opt[mask]["net_pct"].tolist())
            if sv["n"] == 0:
                continue
            flag = " ✗" if sv["avg"] < 0 else (" ⚠" if sv["wr"] < 45 else "")
            reg_rows.append(
                [
                    rname,
                    str(sv["n"]),
                    f"{sv['wr']:.1f}%{flag}",
                    f"{sv['avg']:+.2f}%{flag}",
                    fmt_sharpe(sv["sharpe"]),
                    f"-{sv['max_dd']:.2f}%",
                ]
            )
        print_table(["Regime", "N", "WR", "Avg Ret", "Sharpe", "Max DD"], reg_rows)
        print("\n> ⚠ WR < 45%  ·  ✗ negative avg return (edge absent in this regime)")

    # ── 10f. Correlation matrix ───────────────────────────────────────────────
    _section("10f. Correlation Matrix")
    print("\n### 10f. Signal Correlation Matrix — at BUY Signal Bars\n")
    fam_frames: list[pd.DataFrame] = []
    for ticker, df in all_dfs.items():
        fdf = compute_scores_masked(df, return_families=True)
        mask = fdf["score"] >= BUY_THRESH
        if mask.sum() > 5:
            fam_frames.append(fdf[mask][FAM_COLS])

    if fam_frames:
        combined = pd.concat(fam_frames, ignore_index=True)

        # Drop zero-variance columns: families with BASE_WEIGHTS=0.0 produce a constant
        # 0.0 score across all rows → zero variance → corr() returns NaN for those columns.
        # This caused all OSC and MR rows/columns to show NaN when those weights were 0.
        active_cols = [c for c in FAM_COLS if combined[c].std() > 1e-9]
        skipped_cols = [c for c in FAM_COLS if c not in active_cols]
        active_labels = [c.replace("_f", "").upper() for c in active_cols]
        if skipped_cols:
            print(
                f"> Skipping zero-weight families (weight=0.0): "
                f"{', '.join(c.replace('_f', '').upper() for c in skipped_cols)}\n"
            )

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
                print(
                    f"\n> Avg |off-diagonal| = **{avg_c:.2f}**  "
                    f"{'→ good orthogonality' if avg_c < 0.25 else '→ moderate overlap' if avg_c < 0.40 else '→ high redundancy'}"
                )
                pairs = sorted(
                    [
                        (abs(corr.loc[active_cols[i], active_cols[j]]), active_labels[i], active_labels[j])
                        for i in range(n_l)
                        for j in range(i + 1, n_l)
                        if corr.loc[active_cols[i], active_cols[j]] == corr.loc[active_cols[i], active_cols[j]]
                    ],
                    reverse=True,
                )
                print("> Most correlated: " + " · ".join(f"{a}↔{b} ({r:.2f})" for r, a, b in pairs[:3]))
            print(f"> {len(combined):,} BUY signal bars sampled across {len(fam_frames)} tickers")

    # ── 10g. MR gate filter ───────────────────────────────────────────────────
    print("\n### 10g. MR Gate Filter Analysis\n")
    total_raw = 0
    cc = {"rsi": 0, "bb": 0, "ibs": 0, "vwap": 0, "passes": 0}
    for ticker, df in all_dfs.items():
        mask = df["score"] >= BUY_THRESH
        total_raw += int(mask.sum())
        if not mask.sum():
            continue
        sub = df[mask]
        rsi_ok = (sub["rsi"].fillna(50) < MR_RSI_CEIL) if "rsi" in sub.columns else pd.Series(False, index=sub.index)
        bb_ok = (
            (sub["bb_pct_b"].fillna(1) < MR_BB_CEIL) if "bb_pct_b" in sub.columns else pd.Series(False, index=sub.index)
        )
        ibs_ok = (sub["ibs"].fillna(1) < MR_IBS_CEIL) if "ibs" in sub.columns else pd.Series(False, index=sub.index)
        vwap_ok = (
            (sub["vwap_pct"].fillna(0) < MR_VWAP_FLOOR)
            if "vwap_pct" in sub.columns
            else pd.Series(False, index=sub.index)
        )
        passes = rsi_ok | bb_ok | ibs_ok | vwap_ok
        cc["rsi"] += int(rsi_ok.sum())
        cc["bb"] += int(bb_ok.sum())
        cc["ibs"] += int(ibs_ok.sum())
        cc["vwap"] += int(vwap_ok.sum())
        cc["passes"] += int(passes.sum())
    if total_raw:
        pct_p = cc["passes"] / total_raw * 100
        print(f"Raw BUY signals (score ≥ {BUY_THRESH}): **{total_raw:,}**")
        print(
            f"Passes MR gate: **{cc['passes']:,}** ({pct_p:.1f}%)  |  Filtered: {total_raw - cc['passes']:,} ({100 - pct_p:.1f}%)\n"
        )
        print_table(
            ["MR Condition", "Triggers", "% of Raw BUY"],
            [
                [f"RSI < {MR_RSI_CEIL}", f"{cc['rsi']:,}", f"{cc['rsi'] / total_raw * 100:.1f}%"],
                [f"BB%B < {MR_BB_CEIL}", f"{cc['bb']:,}", f"{cc['bb'] / total_raw * 100:.1f}%"],
                [f"IBS < {MR_IBS_CEIL}", f"{cc['ibs']:,}", f"{cc['ibs'] / total_raw * 100:.1f}%"],
                [f"VWAP% < {MR_VWAP_FLOOR}%", f"{cc['vwap']:,}", f"{cc['vwap'] / total_raw * 100:.1f}%"],
            ],
        )

    # ── 10h. Monte Carlo comparison ───────────────────────────────────────────
    _section("10h. Monte Carlo (8000 sims)")
    print("\n### 10h. Monte Carlo — Naive Baseline vs Optimal Combo\n")
    print("> 8,000 bootstrap simulations. P5 > 0 = edge is statistically real.\n")

    p5b, p95b = _monte_carlo(baseline_trades["net_pct"].tolist())
    print(
        f"**Baseline (26 fam):**  Sharpe P5={p5b:.2f}  P95={p95b:.2f}" + (" ✓ positive P5" if p5b > 0 else " ⚠ P5 ≤ 0")
    )
    if tdf_opt is not None and not tdf_opt.empty:
        p5o, p95o = _monte_carlo(tdf_opt["net_pct"].tolist())
        print(
            f"**Optimal combo:**      Sharpe P5={p5o:.2f}  P95={p95o:.2f}"
            + (" ✓ positive P5" if p5o > 0 else " ⚠ P5 ≤ 0")
        )

    # ── 10i. Three-gate verdict ───────────────────────────────────────────────
    print("\n### 10i. Three-Gate Verdict\n")
    essential_fams_all = [f for f in SIGNAL_FAMILIES if (ablation_results[f].get("sharpe") or 0.0) < bs_sh]
    rv = stats(baseline_trades[baseline_trades["date"] >= pd.Timestamp("2024-01-01")]["net_pct"].tolist())
    gate1 = len(essential_fams_all) >= 3
    gate2 = rv["n"] > 0 and rv["avg"] > 0
    gate3 = bs_avg > 0
    print("| Gate | Criterion | Result | Detail |")
    print("|:---|:---|:---:|:---|")
    print(
        f"| **G1** | ≥3 families load-bearing | {'✓ PASS' if gate1 else '✗ FAIL'} | {len(essential_fams_all)}/17 essential |"
    )
    print(
        f"| **G3** | Net positive after costs | {'✓ PASS' if gate3 else '✗ FAIL'} | avg {bs_avg:+.2f}%  MaxDD -{bs_dd:.2f}%  N={bs_n} |"
    )
    gp = sum([gate1, gate2, gate3])
    verdict = {3: "REAL EDGE", 2: "PARTIAL EDGE", 1: "FRAGILE", 0: "NO EDGE"}[gp]
    print(f"\n**{gp}/3 gates → {verdict}**")
    redund = [f for f in SIGNAL_FAMILIES if f not in essential_fams_all]
    if redund:
        print(f"\n> Redundant (confirmed across v1+v2+v3): {', '.join(redund)}")
    print("\n---")
    print(
        f"*v12 · 11 families (OSC×1.0 + MR×0.5 + 8 filters + RS_QUALITY) · {len(all_dfs)}-ticker universe · ext-MR (gap+streak) · {len(REGIMES)} regimes · {datetime.today().strftime('%Y-%m-%d')}*"
    )
    print(f"\n[{_elapsed()}] ── DONE — total elapsed: {_elapsed()} ──")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    years = datetime.today().year - int(START[:4])
    print("# Signal Alpha Decomposition — v10 (OSC×1.0 + MR×0.5 + 8 Quality Filters)\n")
    print("> v9 result: N=33, Sharpe=0.30 — ablation confirmed ROC/RS/ATR_REG all redundant.")
    print("> v10 fix: remove ROC, RS, ATR_REG — they penalise oversold MR targets, reducing N AND Sharpe.")
    print("> 17 confirmed redundant families removed total (mfi, candle, rsi_div, keltner, streak, pivot,")
    print(">   super, hurst, gap, rsi_level, earn, redday, mom_decel, sector_rs, roc, rs, atr_reg).")
    print(f"> Tickers: {', '.join(TICKERS)}")
    print(f"> Period:  {START} → {END}  ({years}-yr)")
    print("> Best practical config: v2 (Sharpe 0.43, N=77). Technical ceiling: v4-opt (Sharpe 0.49, N=10)\n")

    # ── Fetch alt-data ────────────────────────────────────────────────────────
    print("Fetching VIX…", end=" ", flush=True)
    try:
        vix_df = yf.download("^VIX", start=START, end=END, interval="1d", auto_adjust=False, progress=False)
        if isinstance(vix_df.columns, pd.MultiIndex):
            vix_df.columns = vix_df.columns.get_level_values(0)
        vix = {pd.Timestamp(str(k)[:10]): float(v) for k, v in vix_df["Close"].items() if pd.notna(v)}
        print(f"ok ({len(vix)} bars)")
    except Exception as e:
        vix = {}
        print(f"failed ({e})")

    print("Fetching SPY trend…", end=" ", flush=True)
    spy_trend = fetch_spy_trend(START, END)
    print(f"ok ({len(spy_trend)} bars)")

    print("Fetching SPY closes…", end=" ", flush=True)
    spy_closes = _download_etf_closes("SPY", START, END, "SPY")
    print(f"ok ({len(spy_closes)} bars)" if not spy_closes.empty else "failed")

    print("Fetching HYG closes…", end=" ", flush=True)
    hyg_closes = _download_etf_closes("HYG", START, END, "HYG")
    print(f"ok ({len(hyg_closes)} bars)" if not hyg_closes.empty else "failed (HYG family disabled)")

    print("Fetching FRED STLFSI4…", end=" ", flush=True)
    _fred_key = os.getenv("FRED_API_KEY", "")
    if not _fred_key:
        try:
            with open(os.path.join(_PARENT, ".env")) as _ef:
                for line in _ef:
                    if line.startswith("FRED_API_KEY="):
                        _fred_key = line.strip().split("=", 1)[1]
        except Exception:
            pass
    stlfsi4 = fetch_stlfsi4(START, END, _fred_key)
    print(f"ok ({len(stlfsi4)} obs)" if stlfsi4 else "skipped")

    # ── Parallel download + bt indicators ─────────────────────────────────────
    _section(f"Downloading {len(TICKERS)} tickers")
    print(f"\nDownloading {len(TICKERS)} tickers (parallel)…\n")
    import multiprocessing as _mp

    _mp.set_start_method("fork", force=True)  # macOS Python 3.14 spawn→fork
    with Pool(8) as p:
        results = p.map(process_ticker, [(t, vix, spy_trend, stlfsi4, True) for t in TICKERS])

    all_dfs: dict = {}
    for ticker, _t, _bh, df in results:
        if df is not None:
            all_dfs[ticker] = df

    if not all_dfs:
        print("[error] No data.")
        return

    # ── Apply extra indicators for 11 families (v11) ─────────────────────────
    print("Computing extra indicators (WK52, RS, RS_RANK, CMF, DONCHIAN, HYG, PRICESTR)…", flush=True)
    spy_s = spy_closes if not spy_closes.empty else None
    hyg_s = hyg_closes if not hyg_closes.empty else None
    for ticker, df in all_dfs.items():
        compute_extra_indicators(df, spy_closes=spy_s, hyg_closes=hyg_s)

    # ── Compute 11-family baseline scores (v11: dual-gate + RS_QUALITY) ──────
    _section("Baseline simulation")
    print(
        "Computing 11-family scores (OSC×1.0 + MR×0.5 + 8 filters + RS_QUALITY, extended MR gate: gap+streak)…",
        flush=True,
    )
    baseline_trades_list = []
    for _i, (ticker, df) in enumerate(all_dfs.items(), 1):
        if _i % 10 == 0 or _i == len(all_dfs):
            _progress(_i, len(all_dfs), f"scoring {ticker}")
        df["score"] = compute_scores_masked(df)
        t = simulate_ticker(ticker, df, vix, spy_trend, stlfsi4, mr_only=True, dual_gate=DUAL_GATE_ON)
        if not t.empty:
            baseline_trades_list.append(t)

    if not baseline_trades_list:
        print("[error] No baseline trades.")
        return
    baseline_trades = pd.concat(baseline_trades_list, ignore_index=True)
    baseline_stats_d = stats(baseline_trades["net_pct"].tolist())

    # ── Version comparison header ──────────────────────────────────────────────
    print(f"\n{'─' * 65}")
    print_table(
        ["Version", "Families", "Config", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"],
        [
            ["v2", "11", "MR×0.5 OSC×1.0 (best practical)", "77", "66.2%", "+1.45%", "0.43", "-0.60%"],
            ["v9", "13", "13 fam — N=33, Sharpe=0.30", "33", "63.6%", "+1.15%", "0.30", "-0.27%"],
            ["v4-opt", "11", "essential-only (ceiling)", "10", "70.0%", "+1.02%", "0.49", "-0.18%"],
            [
                "**v12**",
                "11",
                f"{len(all_dfs)}-ticker, OSC×1.0+MR×0.5+8f+RS_QUAL",
                str(baseline_stats_d["n"]),
                f"{baseline_stats_d['wr']:.1f}%",
                f"{baseline_stats_d['avg']:+.2f}%",
                fmt_sharpe(baseline_stats_d["sharpe"]),
                f"-{baseline_stats_d['max_dd']:.2f}%",
            ],
        ],
    )
    print(f"{'─' * 65}\n")

    run_ablation_suite(
        all_dfs=all_dfs,
        vix=vix,
        spy_trend=spy_trend,
        stlfsi4=stlfsi4,
        baseline_stats=baseline_stats_d,
        baseline_trades=baseline_trades,
    )

    # ── 10j. Earnings Proximity Gate Test ────────────────────────────────────
    # Validates the live finding (Stats.md §11c): signals fired 3-14d before
    # earnings outperform the "safe" 15+d zone by 14-26pp WR.
    # Tests: EARNINGS_BLACKOUT_DAYS=5 (current) vs =2 (proposed live-engine change).
    _section("10j. Earnings Gate Test")
    print("\n\n## 10j. Earnings Proximity Gate Test\n")
    print("> Live data (529 trades, §11c): 3-14d pre-earnings outperforms safe zone.")
    print("> Testing EARN blackout=5 (current) vs blackout=2 (proposed — hard blackout only).\n")

    print("Fetching earnings dates per ticker (yfinance, best-effort)…", flush=True)
    earnings_map: dict[str, set] = {}
    for ticker in list(all_dfs.keys()):
        try:
            cal = yf.Ticker(ticker).get_earnings_dates(limit=50)
            if cal is not None and not cal.empty:
                earnings_map[ticker] = {pd.Timestamp(str(d)[:10]) for d in cal.index}
            else:
                earnings_map[ticker] = set()
        except Exception:
            earnings_map[ticker] = set()
    n_with = sum(1 for v in earnings_map.values() if v)
    print(f"  Earnings dates fetched for {n_with}/{len(earnings_map)} tickers\n")

    def _run_earn_test(blackout: int) -> tuple[dict, pd.DataFrame]:
        trades_list = []
        for ticker, df in all_dfs.items():
            t = simulate_ticker(
                ticker,
                df,
                vix,
                spy_trend,
                stlfsi4,
                mr_only=True,
                dual_gate=DUAL_GATE_ON,
                earnings_dates=earnings_map.get(ticker) or None,
                earnings_blackout_days=blackout,
            )
            if not t.empty:
                trades_list.append(t)
        if not trades_list:
            return dict(_EMPTY_STATS), pd.DataFrame()
        tdf = pd.concat(trades_list, ignore_index=True)
        return stats(tdf["net_pct"].tolist()), tdf

    print("Running blackout=5 (current)…", flush=True)
    s5, tdf5 = _run_earn_test(5)
    print("Running blackout=2 (proposed)…", flush=True)
    s2, tdf2 = _run_earn_test(2)

    # ── Side-by-side comparison ───────────────────────────────────────────────
    def _d(a, b, key):
        return (a.get(key) or 0.0) - (b.get(key) or 0.0)

    print("\n### Gate Comparison\n")
    print_table(
        ["Config", "N", "Win Rate", "Avg Ret", "Sharpe", "Max DD"],
        [
            [
                "blackout=5 (current, baseline)",
                str(s5["n"]),
                f"{s5['wr']:.1f}%",
                f"{s5['avg']:+.2f}%",
                fmt_sharpe(s5["sharpe"]),
                f"-{s5['max_dd']:.2f}%",
            ],
            [
                "blackout=2 (proposed — hard-only)",
                str(s2["n"]),
                f"{s2['wr']:.1f}%",
                f"{s2['avg']:+.2f}%",
                fmt_sharpe(s2["sharpe"]),
                f"-{s2['max_dd']:.2f}%",
            ],
            [
                "Delta (proposed − current)",
                f"{s2['n'] - s5['n']:+d}",
                f"{_d(s2, s5, 'wr'):+.1f}pp",
                f"{_d(s2, s5, 'avg'):+.2f}pp",
                f"{_d(s2, s5, 'sharpe'):+.2f}",
                f"{_d(s5, s2, 'max_dd'):+.2f}pp",
            ],
        ],
    )

    # ── Earnings proximity bucket breakdown (blackout=2 trades) ───────────────
    if not tdf2.empty and "days_to_earnings" in tdf2.columns:
        print("\n### Earnings Proximity Bucket Breakdown (blackout=2 run)\n")
        print("> Bucket = days_to_next_earnings at signal date. None = no upcoming earnings data.\n")

        def _bucket(d):
            if d is None or (isinstance(d, float) and math.isnan(d)):
                return "No data"
            d = int(d)
            if d <= 2:
                return "0-2d (hard blackout)"
            if d <= 7:
                return "3-7d (pre-earnings)"
            if d <= 14:
                return "8-14d (early caution)"
            return "15+d (safe zone)"

        tdf2["earn_bucket"] = tdf2["days_to_earnings"].apply(_bucket)
        bkt_rows = []
        for bkt in [
            "0-2d (hard blackout)",
            "3-7d (pre-earnings)",
            "8-14d (early caution)",
            "15+d (safe zone)",
            "No data",
        ]:
            sub = tdf2[tdf2["earn_bucket"] == bkt]
            if sub.empty:
                continue
            sv = stats(sub["net_pct"].tolist())
            bkt_rows.append(
                [
                    bkt,
                    str(sv["n"]),
                    f"{sv['wr']:.1f}%",
                    f"{sv['avg']:+.2f}%",
                    fmt_pf(sv["pf"]),
                    fmt_sharpe(sv["sharpe"]),
                ]
            )
        print_table(["Bucket", "N", "Win Rate", "Avg Ret", "PF", "Sharpe"], bkt_rows)
        print("\n> If 3-14d WR and avg ret > 15+d: gate direction confirmed wrong (matches live data).")
        print("> If 3-14d underperforms: gate was correct and live finding was small-sample noise.")

    # ── §11. Sharpe > 1.0 Research ───────────────────────────────────────────
    run_sharpe_research(all_dfs, vix, spy_trend, stlfsi4)

    # ── §12. Advanced Gate Research ──────────────────────────────────────────
    run_advanced_research(all_dfs, vix, spy_trend, stlfsi4)

    # ── §13. ATR Regime & Beta-Hedge Research ────────────────────────────────
    run_atr_research(all_dfs, vix, spy_trend, stlfsi4, spy_closes=spy_s)

    # ── §14. Tech/FAANG Sector Optimization ──────────────────────────────────
    run_tech_optimization(all_dfs, vix, spy_trend, stlfsi4)


# ─────────────────────────────────────────────────────────────────────────────
# §11. Sharpe > 1.0 Research — parameter sweep
# ─────────────────────────────────────────────────────────────────────────────


def run_sharpe_research(all_dfs, vix, spy_trend, stlfsi4):
    """Systematic sweep of hold period, RSI gate depth, stop/target ratio, and
    score threshold to find configurations that approach Sharpe > 1.0.

    Academic baseline:
      Lehmann (1990): weekly reversal on 750-stock universe → Sharpe ~1.5 (daily rebal)
      Jegadeesh (1990): 1-week MR strongest; at 4-week already mean-reverts
      Lo & MacKinlay (1990): reversal profit highest at 1-week horizon
    Key insight: 5-day hold reduces σ_trade by √2 vs 10-day with similar avg ret → Sharpe×√2
    """

    def _run_research(
        hold_days: int = 10,
        mr_rsi_ceil: float = 42.0,
        stop_mult: float | None = None,
        target_mult: float | None = None,
        buy_thresh: int = 40,
    ) -> dict:
        trades_list = []
        for ticker, df in all_dfs.items():
            df2 = df.copy()
            df2["score"] = compute_scores_masked(df2, family_weights=dict(BASE_WEIGHTS))
            t = simulate_ticker(
                ticker,
                df2,
                vix,
                spy_trend,
                stlfsi4,
                mr_only=True,
                dual_gate=False,
                hold_days_override=hold_days,
                mr_rsi_ceil_override=mr_rsi_ceil,
                stop_mult_override=stop_mult,
                target_mult_override=target_mult,
                buy_thresh_override=buy_thresh,
            )
            if not t.empty:
                trades_list.append(t)
        if not trades_list:
            return dict(_EMPTY_STATS)
        tdf = pd.concat(trades_list, ignore_index=True)
        return stats(tdf["net_pct"].tolist())

    _section("11. Sharpe > 1.0 Research")
    print("\n\n## 11. Sharpe > 1.0 Research — Parameter Sweep\n")
    n_tickers = len(all_dfs)
    print(f"> Universe: {n_tickers} tickers ({len(_BASE_TICKERS)} base + {n_tickers - len(_BASE_TICKERS)} expansion)")
    print("> Academic anchors: Jegadeesh (1990) weekly reversal strongest; Lo & MacKinlay (1990)")
    print("> reversal profits highest at 1-week horizon. 5-day hold → σ_trade ÷ √2 vs 10-day.")
    print("> Sweeping: hold period · RSI gate depth · stop/target ratio · score threshold.\n")

    # ── 11a. Hold Period Sweep ────────────────────────────────────────────────
    _section("11a. Hold Period Sweep")
    print("### 11a. Hold Period Sweep\n")
    print("> Baseline: hold=10, MR_RSI<42, thresh=40, stop=1.5×/target=2.0×\n")
    _hold_vals = [3, 5, 7, 10]
    hold_rows = []
    for _i, hd in enumerate(_hold_vals, 1):
        _progress(_i, len(_hold_vals), f"hold={hd}d")
        sv = _run_research(hold_days=hd)
        hold_rows.append(
            [
                f"hold={hd}d",
                str(sv["n"]),
                f"{sv['wr']:.1f}%",
                f"{sv['avg']:+.2f}%",
                fmt_sharpe(sv["sharpe"]),
                f"-{sv['max_dd']:.2f}%",
            ]
        )
    print_table(["Hold", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"], hold_rows)

    # ── 11b. RSI Gate Depth Sweep ────────────────────────────────────────────
    _section("11b. RSI Gate Depth Sweep")
    print("\n### 11b. RSI Gate Depth Sweep (MR gate: RSI < threshold)\n")
    print("> Deeper RSI = more extreme oversold = higher bounce probability.\n")
    _rsi_vals = [30, 35, 38, 42]
    rsi_rows = []
    for _i, r in enumerate(_rsi_vals, 1):
        _progress(_i, len(_rsi_vals), f"RSI<{r}")
        sv = _run_research(mr_rsi_ceil=r)
        rsi_rows.append(
            [
                f"RSI<{r}",
                str(sv["n"]),
                f"{sv['wr']:.1f}%",
                f"{sv['avg']:+.2f}%",
                fmt_sharpe(sv["sharpe"]),
                f"-{sv['max_dd']:.2f}%",
            ]
        )
    print_table(["MR gate", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"], rsi_rows)

    # ── 11c. Stop/Target Ratio Sweep ─────────────────────────────────────────
    _section("11c. Stop/Target Ratio Sweep")
    print("\n### 11c. Stop/Target Ratio Sweep\n")
    print("> Current ATR-based: 1.5s/2.0t (R:R 1:1.33). Testing tighter stop or wider target.\n")
    st_rows = []
    combos = [(None, None), (1.0, 2.0), (1.0, 2.5), (1.5, 2.5), (1.5, 3.0), (1.0, 3.0)]
    st_labels = ["1.5s/2.0t (ATR adaptive)", "1.0s/2.0t", "1.0s/2.5t", "1.5s/2.5t", "1.5s/3.0t", "1.0s/3.0t"]
    for _i, ((sm, tm), lbl) in enumerate(zip(combos, st_labels), 1):
        _progress(_i, len(combos), lbl)
        sv = _run_research(stop_mult=sm, target_mult=tm)
        st_rows.append(
            [
                lbl,
                str(sv["n"]),
                f"{sv['wr']:.1f}%",
                f"{sv['avg']:+.2f}%",
                fmt_sharpe(sv["sharpe"]),
                f"-{sv['max_dd']:.2f}%",
            ]
        )
    print_table(["Config", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"], st_rows)

    # ── 11d. Score Threshold Sweep ────────────────────────────────────────────
    _section("11d. Score Threshold Sweep")
    print("\n### 11d. Score Threshold Sweep\n")
    print("> Higher threshold = higher conviction = fewer but better-quality trades.\n")
    # Extended downward: OSC×0.3 reduced N from ~350 to ~11 by raising the effective
    # bar. Testing sub-40 thresholds to recover N while preserving quality gains.
    _thresh_vals = [30, 32, 34, 36, 38, 40, 44, 48, 52, 56]
    thresh_rows = []
    for _i, bt in enumerate(_thresh_vals, 1):
        _progress(_i, len(_thresh_vals), f"thresh≥{bt}")
        sv = _run_research(buy_thresh=bt)
        thresh_rows.append(
            [
                f"thresh≥{bt}",
                str(sv["n"]),
                f"{sv['wr']:.1f}%",
                f"{sv['avg']:+.2f}%",
                fmt_sharpe(sv["sharpe"]),
                f"-{sv['max_dd']:.2f}%",
            ]
        )
    print_table(["Threshold", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"], thresh_rows)

    # ── 11e. Best-Dimension Combinations ─────────────────────────────────────
    _section("11e. Cross-Dimension Combinations")
    print("\n### 11e. Cross-Dimension Combinations\n")
    print("> Combining best values from each 1D sweep.\n")

    combos_2d = [
        {"label": "hold=5 + RSI<35", "hold_days": 5, "mr_rsi_ceil": 35},
        {"label": "hold=5 + RSI<38", "hold_days": 5, "mr_rsi_ceil": 38},
        {"label": "hold=5 + thresh≥44", "hold_days": 5, "buy_thresh": 44},
        {"label": "hold=5 + thresh≥48", "hold_days": 5, "buy_thresh": 48},
        {"label": "hold=7 + RSI<35", "hold_days": 7, "mr_rsi_ceil": 35},
        {"label": "hold=5 + RSI<35 + thresh≥44", "hold_days": 5, "mr_rsi_ceil": 35, "buy_thresh": 44},
        {"label": "hold=5 + RSI<35 + thresh≥48", "hold_days": 5, "mr_rsi_ceil": 35, "buy_thresh": 48},
        {"label": "hold=5 + RSI<38 + thresh≥44", "hold_days": 5, "mr_rsi_ceil": 38, "buy_thresh": 44},
        {"label": "hold=3 + RSI<35 + thresh≥44", "hold_days": 3, "mr_rsi_ceil": 35, "buy_thresh": 44},
        {
            "label": "hold=5 + RSI<35 + 1.0s/2.5t",
            "hold_days": 5,
            "mr_rsi_ceil": 35,
            "stop_mult": 1.0,
            "target_mult": 2.5,
        },
        {
            "label": "hold=5 + RSI<38 + 1.0s/2.5t",
            "hold_days": 5,
            "mr_rsi_ceil": 38,
            "stop_mult": 1.0,
            "target_mult": 2.5,
        },
        {
            "label": "hold=5 + RSI<35 + thresh≥44 + 1.0s/2.5t",
            "hold_days": 5,
            "mr_rsi_ceil": 35,
            "buy_thresh": 44,
            "stop_mult": 1.0,
            "target_mult": 2.5,
        },
    ]

    comb_rows = []
    for _i, cfg in enumerate(combos_2d, 1):
        lbl = cfg.pop("label")
        _progress(_i, len(combos_2d), lbl)
        sv = _run_research(**cfg)
        flag = (
            " ← **Sharpe>1**"
            if (sv.get("sharpe") or 0) >= 1.0
            else (" ← Sharpe>0.7" if (sv.get("sharpe") or 0) >= 0.7 else "")
        )
        comb_rows.append(
            [
                lbl + flag,
                str(sv["n"]),
                f"{sv['wr']:.1f}%",
                f"{sv['avg']:+.2f}%",
                fmt_sharpe(sv["sharpe"]),
                f"-{sv['max_dd']:.2f}%",
            ]
        )
    print_table(["Config", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"], comb_rows)
    print("\n> Note: N < 30 over 20 years requires cautious interpretation (Harvey et al. 2016).")
    print("> Minimum for statistical significance at 95%: N ≥ 130 (low-corr signals).")
    print("> Practical minimum for live deployment: N ≥ 50 (≈3 trades/yr/30 tickers).")


# ─────────────────────────────────────────────────────────────────────────────
# §12. Advanced Gate Research — paths beyond Sharpe 0.92
# ─────────────────────────────────────────────────────────────────────────────


def run_advanced_research(all_dfs, vix, spy_trend, stlfsi4):
    """Five targeted experiments using the MR=0.1 base config (best so far: ann. 0.92).

    Research rationale:
      §12a  Score-weighted Sharpe   — Kelly-style sizing: bet bigger on higher-score trades.
      §12b  VIX minimum gate        — MR bounces strongest in elevated-fear regimes (VIX ≥ 15-20).
      §12c  Multi-condition MR gate — require 2+ simultaneous oversold signals (vs current 1).
      §12d  Persistent oversold     — require previous bar also above BUY_THRESH (Day-2 rule).
      §12e  ATR rank minimum        — only enter when stock volatility is elevated vs its own history.
      §12f  Best combination        — stack the winning gates from §12b-12e.
    """
    _section("12. Advanced Gate Research")
    print("\n\n## 12. Advanced Gate Research — Beyond Annualized Sharpe 0.92\n")
    print("> Base config: MR weight=0.1, 74-ticker universe (best prior result: N=166, Sharpe=0.32, ann≈0.92)")
    print("> Research: VIX minimum · MR multi-condition · persistent oversold · ATR rank filter\n")

    MR_OPT_WEIGHT = 0.1  # best weight from §10d

    def _run12(
        vix_min=None,
        require_mr_count=None,
        require_consec=None,
        atr_rank_min=None,
        mr_w=MR_OPT_WEIGHT,
        buy_thresh=40,
        hold_days=10,
    ) -> tuple[dict, pd.DataFrame]:
        trades_list = []
        fw = dict(BASE_WEIGHTS)
        fw["mr"] = mr_w
        for ticker, df in all_dfs.items():
            df2 = df.copy()
            df2["score"] = compute_scores_masked(df2, family_weights=fw)
            t = simulate_ticker(
                ticker,
                df2,
                vix,
                spy_trend,
                stlfsi4,
                mr_only=True,
                dual_gate=False,
                buy_thresh_override=buy_thresh,
                hold_days_override=hold_days,
                vix_min_override=vix_min,
                require_mr_count_override=require_mr_count,
                require_consec_score_override=require_consec,
                atr_pct_rank_min_override=atr_rank_min,
            )
            if not t.empty:
                trades_list.append(t)
        if not trades_list:
            return dict(_EMPTY_STATS), pd.DataFrame()
        tdf = pd.concat(trades_list, ignore_index=True)
        return stats(tdf["net_pct"].tolist()), tdf

    def _ann(sv: dict) -> str:
        sh = sv.get("sharpe") or 0.0
        n = sv.get("n") or 0
        if n < 5 or sh == 0:
            return "—"
        ann = sh * math.sqrt(n / 20)
        return f"{ann:.2f}"

    def _fmt12(label, sv, base_sh=0.32) -> list:
        sh = sv.get("sharpe") or 0.0
        d_sh = sh - base_sh
        flag = " ← **ANN>1**" if _ann(sv) != "—" and float(_ann(sv)) >= 1.0 else ""
        return [
            label + flag,
            str(sv["n"]),
            f"{sv['wr']:.1f}%",
            f"{sv['avg']:+.2f}%",
            f"{fmt_sharpe(sv['sharpe'])} ({d_sh:+.2f})",
            f"-{sv['max_dd']:.2f}%",
            _ann(sv),
        ]

    # ── Run MR=0.1 base once for reference ───────────────────────────────────
    base12, base12_tdf = _run12()
    base_sh12 = base12.get("sharpe") or 0.0
    print(
        f"Base (MR=0.1): N={base12['n']}, WR={base12['wr']:.1f}%, "
        f"Sharpe={fmt_sharpe(base12['sharpe'])}, Ann={_ann(base12)}\n"
    )

    # ── §12a. Score-weighted Sharpe ───────────────────────────────────────────
    _section("12a. Score-Weighted Sharpe")
    print("### 12a. Score-Weighted Position Sizing\n")
    print("> Equal-weight baseline vs score-proportional sizing (Kelly-style).")
    print("> Higher-score trades get larger positions (floor: 0.5× avg, mean: 1.0×).\n")

    if not base12_tdf.empty and "score" in base12_tdf.columns:
        sw = stats_weighted(base12_tdf["net_pct"].tolist(), base12_tdf["score"].tolist())
        print_table(
            ["Config", "N", "WR", "Avg Ret", "Sharpe", "MaxDD", "Ann. Sharpe"],
            [
                [
                    "Equal-weight (baseline)",
                    str(base12["n"]),
                    f"{base12['wr']:.1f}%",
                    f"{base12['avg']:+.2f}%",
                    fmt_sharpe(base12["sharpe"]),
                    f"-{base12['max_dd']:.2f}%",
                    _ann(base12),
                ],
                [
                    "Score-weighted (Kelly-style)",
                    str(sw["n"]),
                    f"{sw['wr']:.1f}%",
                    f"{sw['avg']:+.2f}%",
                    fmt_sharpe(sw["sharpe"]),
                    f"-{sw['max_dd']:.2f}%",
                    f"{(sw['sharpe'] or 0) * math.sqrt(sw['n'] / 20):.2f}" if sw.get("sharpe") else "—",
                ],
            ],
        )
        print(f"\n> Score range in sample: {base12_tdf['score'].min():.0f} – {base12_tdf['score'].max():.0f}")
        if sw.get("sharpe") and base12.get("sharpe"):
            lift = (sw["sharpe"] - base12["sharpe"]) / base12["sharpe"] * 100
            print(f"> Sharpe lift from score-weighting: {lift:+.1f}%")

    # ── §12b. VIX minimum sweep ───────────────────────────────────────────────
    _section("12b. VIX Minimum Sweep")
    print("\n### 12b. VIX Minimum Filter\n")
    print("> Skip entries when VIX < threshold. Low-VIX = calm market = shallow panic = weak bounce.")
    print("> Academic: Lo & MacKinlay (1990) reversal profits highest in high-volatility regimes.\n")

    vix_vals = [None, 13.0, 15.0, 18.0, 19.0, 20.0]
    vix_rows = [_fmt12("No VIX min (baseline)", base12, base_sh12)]
    best_vix = None
    best_vix_sh = base_sh12
    for _i, vm in enumerate(vix_vals[1:], 1):
        _progress(_i, len(vix_vals) - 1, f"VIX≥{vm:.0f}")
        sv, _ = _run12(vix_min=vm)
        vix_rows.append(_fmt12(f"VIX ≥ {vm:.0f}", sv, base_sh12))
        if (sv.get("sharpe") or 0) > best_vix_sh and sv["n"] >= 50:
            best_vix = vm
            best_vix_sh = sv.get("sharpe") or 0.0
    print_table(["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann. Sharpe"], vix_rows)
    print(f"\n> Best VIX min (N≥50): {best_vix} → Sharpe {best_vix_sh:.2f}")

    # ── §12c. Multi-condition MR gate ─────────────────────────────────────────
    _section("12c. MR Multi-Condition Gate")
    print("\n### 12c. MR Gate — Count Requirement\n")
    print("> Currently 1 condition (IBS<0.15 alone is enough). Require 2 simultaneous signals.")
    print("> IBS+RSI or IBS+BB confluence = higher conviction than IBS-only.\n")

    mr_count_rows = [_fmt12("Count ≥ 1 (baseline OR logic)", base12, base_sh12)]
    best_count = 1
    best_count_sh = base_sh12
    for _i, cnt in enumerate([2, 3], 1):
        _progress(_i, 2, f"count≥{cnt}")
        sv, _ = _run12(require_mr_count=cnt)
        mr_count_rows.append(_fmt12(f"Count ≥ {cnt} conditions simultaneous", sv, base_sh12))
        if (sv.get("sharpe") or 0) > best_count_sh and sv["n"] >= 30:
            best_count = cnt
            best_count_sh = sv.get("sharpe") or 0.0
    print_table(["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann. Sharpe"], mr_count_rows)
    print(f"\n> Best MR count (N≥30): {best_count} → Sharpe {best_count_sh:.2f}")

    # ── §12d. Persistent oversold gate ────────────────────────────────────────
    _section("12d. Persistent Oversold (Consecutive Score)")
    print("\n### 12d. Persistent Oversold — Consecutive Score Requirement\n")
    print("> Require previous bar also had score ≥ BUY_THRESH.")
    print("> Day-1 panic often whipsaws; Day-2+ persistent oversold = near exhaustion.\n")

    _progress(1, 1, "consec=True")
    sv_consec, _ = _run12(require_consec=True)
    consec_rows = [
        _fmt12("Single day (baseline)", base12, base_sh12),
        _fmt12("2+ consecutive days above thresh", sv_consec, base_sh12),
    ]
    print_table(["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann. Sharpe"], consec_rows)
    best_consec_sh = max(base_sh12, sv_consec.get("sharpe") or 0.0)
    use_consec = (sv_consec.get("sharpe") or 0) > base_sh12 and sv_consec["n"] >= 30

    # ── §12e. ATR rank minimum ────────────────────────────────────────────────
    _section("12e. ATR Percentile Rank Minimum")
    print("\n### 12e. ATR Rank Filter — Minimum Volatility Percentile\n")
    print("> Only enter when stock ATR is above X% of its 252-day ATR distribution.")
    print("> Low ATR%rank = quiet period = MR bounces are shallow. High rank = panic = strong bounces.\n")

    atr_vals = [None, 20.0, 30.0, 40.0, 50.0]
    atr_rows = [_fmt12("No ATR filter (baseline)", base12, base_sh12)]
    best_atr = None
    best_atr_sh = base_sh12
    for _i, ar in enumerate(atr_vals[1:], 1):
        _progress(_i, len(atr_vals) - 1, f"ATR%rank≥{ar:.0f}")
        sv, _ = _run12(atr_rank_min=ar)
        atr_rows.append(_fmt12(f"ATR%rank ≥ {ar:.0f}", sv, base_sh12))
        if (sv.get("sharpe") or 0) > best_atr_sh and sv["n"] >= 30:
            best_atr = ar
            best_atr_sh = sv.get("sharpe") or 0.0
    print_table(["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann. Sharpe"], atr_rows)
    print(f"\n> Best ATR min (N≥30): {best_atr} → Sharpe {best_atr_sh:.2f}")

    # ── §12f. Best combination ────────────────────────────────────────────────
    _section("12f. Best Combination")
    print("\n### 12f. Best Gate Combination\n")
    print("> Stack the winning gates from §12b-12e on MR=0.1 base.\n")

    combos_12 = [
        {
            "label": "MR=0.1 base",
        },
        {"label": f"+ VIX≥{best_vix or 15:.0f}", "vix_min": best_vix or 15.0},
        {"label": f"+ ATR%rank≥{best_atr or 20:.0f}", "atr_rank_min": best_atr or 20.0},
        {
            "label": f"+ VIX≥{best_vix or 15:.0f} + ATR%rank≥{best_atr or 20:.0f}",
            "vix_min": best_vix or 15.0,
            "atr_rank_min": best_atr or 20.0,
        },
        {"label": "+ consec score", "require_consec": True},
        {"label": f"+ VIX≥{best_vix or 15:.0f} + consec", "vix_min": best_vix or 15.0, "require_consec": True},
        {
            "label": f"+ VIX≥{best_vix or 15:.0f} + ATR%rank≥{best_atr or 20:.0f} + consec",
            "vix_min": best_vix or 15.0,
            "atr_rank_min": best_atr or 20.0,
            "require_consec": True,
        },
        {"label": "+ MR count≥2", "require_mr_count": 2},
        {"label": f"+ VIX≥{best_vix or 15:.0f} + MR≥2", "vix_min": best_vix or 15.0, "require_mr_count": 2},
    ]

    combo_rows = []
    for _i, cfg in enumerate(combos_12, 1):
        lbl = cfg.pop("label")
        _progress(_i, len(combos_12), lbl)
        if not cfg:
            sv, tdf_ = base12, base12_tdf
        else:
            sv, tdf_ = _run12(**cfg)
        combo_rows.append(_fmt12(lbl, sv, base_sh12))
    print_table(["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann. Sharpe"], combo_rows)

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n### §12 Conclusions\n")
    print("> All experiments on MR=0.1 base (74 tickers), the current best config.")
    print("> Ann. Sharpe = per_trade_Sharpe × √(N/20). Target: ≥ 1.0")
    ann_base = _ann(base12)
    print(f"> MR=0.1 baseline: Sharpe={fmt_sharpe(base12['sharpe'])}, N={base12['n']}, Ann={ann_base}")
    print(f"\n*v12-adv · 74-ticker · MR=0.1 · 5 gate experiments · {END}*")


# ─────────────────────────────────────────────────────────────────────────────
# Parallel simulation infrastructure — module-level for picklability
# Workers are initialised once with shared data; each task receives only small args.
# ─────────────────────────────────────────────────────────────────────────────

_pool_g_dfs: dict = {}
_pool_g_vix: dict = {}
_pool_g_spy: dict = {}
_pool_g_fsi: dict = {}


def _pool_init(dfs: dict, vix: dict, spy: dict, fsi: dict) -> None:
    global _pool_g_dfs, _pool_g_vix, _pool_g_spy, _pool_g_fsi
    _pool_g_dfs = dfs
    _pool_g_vix = vix
    _pool_g_spy = spy
    _pool_g_fsi = fsi


def _pool_sim_ticker(args: tuple) -> pd.DataFrame:
    """Per-ticker worker. Args: (ticker, atr_min, vix_min, hold_days, thresh, atr_max, ret_jump, entry_delay, ibs_streak)."""
    ticker, atr_min, vix_min, hold_days, thresh = args[:5]
    atr_max = args[5] if len(args) > 5 else None
    ret_jump = args[6] if len(args) > 6 else None
    entry_delay = args[7] if len(args) > 7 else False
    ibs_streak = args[8] if len(args) > 8 else None
    df = _pool_g_dfs.get(ticker)
    if df is None:
        return pd.DataFrame()
    return simulate_ticker(
        ticker,
        df,
        _pool_g_vix,
        _pool_g_spy,
        _pool_g_fsi,
        mr_only=True,
        dual_gate=False,
        atr_pct_rank_min_override=atr_min,
        vix_min_override=vix_min,
        hold_days_override=hold_days,
        buy_thresh_override=thresh,
        atr_pct_rank_max_override=atr_max,
        ret_jump_filter_override=ret_jump,
        entry_delay_override=entry_delay,
        ibs_sma20_streak_override=ibs_streak,
    )


def _prescore(all_dfs: dict, mr_w: float = 0.1) -> dict:
    """Score all tickers once with given MR weight. Returns new dict of scored DFs."""
    fw = dict(BASE_WEIGHTS)
    fw["mr"] = mr_w
    out = {}
    for ticker, df in all_dfs.items():
        df2 = df.copy()
        df2["score"] = compute_scores_masked(df2, family_weights=fw)
        out[ticker] = df2
    return out


def _run_par(
    pool,
    ticker_list: list,
    atr_min: float | None = None,
    vix_min: float | None = None,
    hold_days: int | None = None,
    thresh: int | None = None,
    atr_max: float | None = None,
    ret_jump: float | None = None,
    entry_delay: bool = False,
    ibs_streak: int | None = None,
) -> tuple[dict, pd.DataFrame]:
    """Parallel simulate_ticker over ticker_list. Pool must be initialised with _pool_init."""
    args = [(t, atr_min, vix_min, hold_days, thresh, atr_max, ret_jump, entry_delay, ibs_streak) for t in ticker_list]
    results = pool.map(_pool_sim_ticker, args)
    trades = [r for r in results if not r.empty]
    if not trades:
        return dict(_EMPTY_STATS), pd.DataFrame()
    tdf = pd.concat(trades, ignore_index=True)
    return stats(tdf["net_pct"].tolist()), tdf


@contextmanager
def _managed_pool(pool, n_workers, init, initargs):
    """Yield `pool` unchanged if provided; otherwise create and manage a fresh Pool."""
    if pool is not None:
        yield pool
    else:
        with Pool(n_workers, initializer=init, initargs=initargs) as p:
            yield p


# ─────────────────────────────────────────────────────────────────────────────
# §13 — ATR regime fine-tuning, sector analysis, VIX stack, beta-hedge sim
# ─────────────────────────────────────────────────────────────────────────────


def run_atr_research(
    all_dfs, vix, spy_trend, stlfsi4, spy_closes: pd.Series | None = None, pool=None, pre_dfs: dict | None = None
):
    """§13: Narrow ATR sweep, sector-level ATR floors, VIX stacking, and beta-hedge sim.
    Parallel: tickers split across Pool workers; scores pre-computed once at MR=0.1.
    Pass pool+pre_dfs from caller to avoid creating a second Pool (macOS spawn deadlock).
    """
    _section("13. ATR Regime & Beta-Hedge Research")
    print("\n\n## 13. ATR Regime & Beta-Hedge Research (§13)\n")
    print("> Starting point: MR=0.1 + ATR%rank≥20 (N=137, Sharpe=0.38, Ann=1.00 — first to reach target).")
    print("> Research: fine ATR sweep · per-sector ATR floors · VIX stack · beta-hedge sim\n")

    MR_W = 0.1
    N_WORKERS = min(8, os.cpu_count() or 4)

    def _ann(sv):
        sh = sv.get("sharpe") or 0.0
        n = sv.get("n") or 0
        if n < 5 or sh == 0:
            return "—"
        return f"{sh * math.sqrt(n / 20):.2f}"

    def _fmt13(label, sv, base_sh=0.38):
        sh = sv.get("sharpe") or 0.0
        d = sh - base_sh
        flag = " ← **ANN≥1**" if _ann(sv) != "—" and float(_ann(sv)) >= 1.0 else ""
        return [
            label + flag,
            str(sv["n"]),
            f"{sv['wr']:.1f}%",
            f"{sv['avg']:+.2f}%",
            f"{fmt_sharpe(sv['sharpe'])} ({d:+.2f})",
            f"-{sv['max_dd']:.2f}%",
            _ann(sv),
        ]

    def _sa(sv):
        sh = sv.get("sharpe") or 0.0
        n = sv.get("n") or 0
        return f"{sh * math.sqrt(n / 20):.2f}" if n >= 5 else "—"

    # ── Pre-score all tickers once with MR=0.1 (skip if caller provides pre_dfs) ─
    if pre_dfs is None:
        print("Pre-scoring tickers (MR=0.1)…", end=" ", flush=True)
        pre_dfs = _prescore(all_dfs, MR_W)
        print(f"done ({len(pre_dfs)} tickers).")
    ticker_list = list(pre_dfs.keys())

    SECTOR_MAP = {
        "Tech/FAANG": {
            "NVDA",
            "MSFT",
            "AAPL",
            "GOOGL",
            "GOOG",
            "META",
            "AMZN",
            "NFLX",
            "ADBE",
            "TSLA",
            "BKNG",
            "EBAY",
            "INTU",
        },
        "Semis": {"INTC", "AMD", "AVGO", "AMAT", "LRCX", "KLAC", "TSM", "QCOM", "TXN", "MRVL"},
        "Software/IT": {"CSCO", "ORCL", "ADSK", "CDNS", "SNPS", "CTSH", "FTNT", "NOW", "PANW", "WDAY", "ACN", "AKAM"},
        "Financials": {
            "JPM",
            "WFC",
            "BAC",
            "GS",
            "V",
            "MA",
            "BLK",
            "SCHW",
            "CME",
            "SPGI",
            "MCO",
            "ICE",
            "MSCI",
            "FIS",
            "FISV",
        },
        "Consumer": {
            "HD",
            "F",
            "LOW",
            "TJX",
            "ROST",
            "LULU",
            "MAR",
            "HLT",
            "RCL",
            "CHTR",
            "GM",
            "COST",
            "SBUX",
            "TGT",
            "PYPL",
        },
        "Other": {"EOG", "VRSK", "DHI", "LEN"},
    }

    with _managed_pool(pool, N_WORKERS, _pool_init, (pre_dfs, vix, spy_trend, stlfsi4)) as _p:

        def _sim(tickers=None, **kw):
            return _run_par(_p, tickers if tickers is not None else ticker_list, **kw)

        # ── §13 reference ─────────────────────────────────────────────────────
        print("Computing §13 reference (MR=0.1 + ATR≥20)…", end=" ", flush=True)
        base13, base13_tdf = _sim(atr_min=20.0)
        base_sh13 = base13.get("sharpe") or 0.0
        print(f"N={base13['n']}, WR={base13['wr']:.1f}%, Sharpe={fmt_sharpe(base13['sharpe'])}, Ann={_ann(base13)}\n")

        # ── §13a. Fine-grained ATR sweep ──────────────────────────────────────
        _section("13a. Fine-Grained ATR Sweep")
        print("### 13a. Fine-Grained ATR Percentile Sweep\n")
        print("> §12e tested 20/30/40/50. Adding 10 and 15 to find the true sweet spot.\n")
        print("  Running ATR sweep configs in parallel…", flush=True)

        sv_nofilter, _ = _sim()
        sv_atr10, _ = _sim(atr_min=10.0)
        sv_atr15, _ = _sim(atr_min=15.0)

        print_table(
            ["Config", "N", "WR", "Avg Ret", "Sharpe (Δ vs ATR≥20)", "MaxDD", "Ann. Sharpe"],
            [
                _fmt13("No ATR filter (MR=0.1 only)", sv_nofilter, base_sh13),
                _fmt13("ATR%rank ≥ 10", sv_atr10, base_sh13),
                _fmt13("ATR%rank ≥ 15", sv_atr15, base_sh13),
                _fmt13("ATR%rank ≥ 20 (reference §12e)", base13, base_sh13),
            ],
        )
        print("\n> §12e reference (for context): ATR≥30→Ann=0.96, ATR≥40→0.94, ATR≥50→0.92")

        # ── §13b. Sector-level ATR floor ──────────────────────────────────────
        _section("13b. Sector ATR Floor Analysis")
        print("\n### 13b. Per-Sector ATR Percentile Floor\n")
        print("> Does ATR≥20 benefit all sector groups equally, or hurt some?\n")
        print("  Running 18 sector×ATR configs in parallel…", flush=True)

        sect_rows = []
        for sector, tset in SECTOR_MAP.items():
            stickers = [t for t in tset if t in pre_dfs]
            if not stickers:
                continue
            sv_n, _ = _sim(tickers=stickers)
            sv_20, _ = _sim(tickers=stickers, atr_min=20.0)
            sv_30, _ = _sim(tickers=stickers, atr_min=30.0)
            sect_rows.append(
                [
                    sector,
                    f"{sv_n['n']} / {sv_20['n']} / {sv_30['n']}",
                    f"{sv_n.get('sharpe') or 0:.2f} / {sv_20.get('sharpe') or 0:.2f} / {sv_30.get('sharpe') or 0:.2f}",
                    f"{_sa(sv_n)} / {_sa(sv_20)} / {_sa(sv_30)}",
                ]
            )

        print_table(
            ["Sector", "N (no/≥20/≥30 filter)", "Sharpe (no/≥20/≥30)", "Ann. Sharpe (no/≥20/≥30)"],
            sect_rows,
        )
        print("\n> Sectors where ATR≥20 shrinks Ann.: use no filter or sector-specific floor.")
        print("> Sectors where ATR≥20 lifts Ann.: highest ATR-filter benefit — concentrate here.")

        # ── §13c. ATR≥20 + VIX stack ──────────────────────────────────────────
        _section("13c. ATR≥20 + VIX Combination")
        print("\n### 13c. ATR≥20 Baseline + VIX Layer\n")
        print("> §12b: VIX≥15 alone → Ann=0.90 (N drop too costly). Stacking on ATR≥20?")
        print("> If N stays ≥ 110 and Ann ≥ 1.0, the combination is deployable.\n")
        print("  Running VIX combo configs in parallel…", flush=True)

        combo_rows = [_fmt13("ATR≥20 only (reference)", base13, base_sh13)]
        for vm in [13.0, 15.0, 18.0]:
            sv, _ = _sim(atr_min=20.0, vix_min=vm)
            combo_rows.append(_fmt13(f"ATR≥20 + VIX≥{vm:.0f}", sv, base_sh13))
        print_table(["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann. Sharpe"], combo_rows)
        print("\n> If VIX stack preserves Ann ≥ 1.0: update best config to ATR≥20 + VIX≥N.")
        print("> If Ann drops: ATR≥20 alone is the Pareto-optimal single filter.")

    # ── §13d. Beta-hedge simulation (sequential — needs base13_tdf) ───────────
    _section("13d. Beta-Hedge Simulation")
    print("\n### 13d. Beta-Hedge Simulation — Long Stock + Short SPY×β\n")
    print("> Hypothesis: removing market beta cuts irreducible trade std, lifting per-trade Sharpe above 0.50.")
    print("> Method: adjusted_return = trade_net_pct − β × SPY_return_over_same_hold_days")
    print("> β = 252-day rolling OLS beta at entry date. SPY return: entry close → exit-day close.\n")

    if spy_closes is None or spy_closes.empty:
        print("> Skipped — SPY close data unavailable.\n")
        return
    if base13_tdf.empty:
        print("> Skipped — no trades in reference config.\n")
        return

    spy_c = spy_closes.sort_index()
    spy_daily_rets = spy_c.pct_change().dropna()

    print("Computing rolling 252-day beta for each ticker…", flush=True)
    beta_cache: dict = {}
    for ticker, df in all_dfs.items():
        if "Close" not in df.columns:
            continue
        s_rets = df["Close"].pct_change().dropna()
        m_rets = spy_daily_rets.reindex(s_rets.index)
        aligned = pd.concat([s_rets.rename("s"), m_rets.rename("m")], axis=1).dropna()
        if len(aligned) < 63:
            continue
        roll_cov = aligned["s"].rolling(252, min_periods=63).cov(aligned["m"])
        roll_var = aligned["m"].rolling(252, min_periods=63).var()
        with np.errstate(divide="ignore", invalid="ignore"):
            beta_s = (roll_cov / roll_var).clip(-3.0, 3.0).dropna()
        beta_cache[ticker] = beta_s
    print(f"  Beta computed for {len(beta_cache)} tickers.\n")

    spy_idx = spy_c.index
    adj_rets: list[float] = []
    betas_used: list[float] = []

    for _, row in base13_tdf.iterrows():
        ticker = row["ticker"]
        entry_dt = pd.Timestamp(row["date"])
        exit_day = int(row.get("exit_day", 10))
        trade_ret = float(row["net_pct"])

        beta_val = 1.0
        if ticker in beta_cache:
            bs = beta_cache[ticker]
            prior = bs[bs.index <= entry_dt]
            if not prior.empty:
                beta_val = float(prior.iloc[-1])

        e_loc = spy_idx.searchsorted(entry_dt)
        x_loc = min(e_loc + exit_day, len(spy_idx) - 1)
        if e_loc < len(spy_idx) and x_loc > e_loc:
            s_e = float(spy_c.iloc[e_loc])
            s_x = float(spy_c.iloc[x_loc])
            spy_ret = (s_x - s_e) / s_e * 100 if s_e > 0 else 0.0
        else:
            spy_ret = 0.0

        adj_rets.append(trade_ret - beta_val * spy_ret)
        betas_used.append(beta_val)

    sv_beta = stats(adj_rets)
    avg_beta = float(np.mean(betas_used))
    sh_beta = sv_beta.get("sharpe") or 0.0
    ann_ref = base_sh13 * math.sqrt(base13["n"] / 20)
    ann_beta = sh_beta * math.sqrt(sv_beta["n"] / 20) if sv_beta["n"] >= 5 else 0.0

    def _fmt13_plain(label, sv, base_sh=0.0):
        sh = sv.get("sharpe") or 0.0
        d = sh - base_sh
        return [
            label,
            str(sv["n"]),
            f"{sv['wr']:.1f}%",
            f"{sv['avg']:+.2f}%",
            f"{fmt_sharpe(sv['sharpe'])} ({d:+.2f})",
            f"-{sv['max_dd']:.2f}%",
            _ann(sv),
        ]

    print_table(
        ["Config", "N", "WR", "Avg Ret", "Sharpe", "MaxDD", "Ann. Sharpe"],
        [
            _fmt13_plain("Unhedged (ATR≥20 baseline)", base13, base_sh13),
            _fmt13_plain("Beta-hedged (long + short SPY×β)", sv_beta, base_sh13),
        ],
    )
    print(f"\n> Avg β: {avg_beta:.2f}  |  range [{min(betas_used):.2f}, {max(betas_used):.2f}]")
    print(f"> Ann. Sharpe: unhedged {ann_ref:.2f}  →  beta-hedged {ann_beta:.2f}")
    if sh_beta > base_sh13 + 0.01:
        print(
            f"> Per-trade Sharpe lift: {sh_beta - base_sh13:+.2f}  — "
            f"{'breaks 0.50 ceiling' if sh_beta >= 0.50 else 'still below 0.50 ceiling — alt-data or options needed'}"
        )
    else:
        print(
            f"> Beta-hedge negligible or negative ({sh_beta:.2f} vs {base_sh13:.2f}). "
            "Market beta is already partially removed by the panic-regime ATR filter "
            "(high ATR%rank entries tend to occur in elevated-VIX environments)."
        )

    print(f"\n*§13 ATR regime + beta-hedge research · MR=0.1 + ATR≥20 base · {END}*")


# ─────────────────────────────────────────────────────────────────────────────
# §14 — Tech/FAANG Sector Optimization
# ─────────────────────────────────────────────────────────────────────────────


def run_tech_optimization(all_dfs, vix, spy_trend, stlfsi4, pool=None, pre_dfs: dict | None = None):
    """§14: Tech/FAANG sector optimisation — hold period, threshold, sector-specific ATR.
    Parallel: scores pre-computed once; tech and non-tech simulate in parallel per config.
    Pass pool+pre_dfs from caller to avoid creating a second Pool (macOS spawn deadlock).
    """
    _section("14. Tech/FAANG Sector Optimization")
    print("\n\n## 14. Tech/FAANG Sector Optimization (§14)\n")
    print("> Objective: Increase N and Sharpe for the highest-performing sector.")
    print("> Hypothesis 1: 5-day hold period better matches V-bottom fast recoveries.")
    print("> Hypothesis 2: Lowering BUY_THRESH to 38 unlocks more valid MR entries without sacrificing quality.\n")

    # Established large-cap tech only (post-2019 growth names removed after §14 validation)
    TECH_FAANG = {
        "NVDA",
        "MSFT",
        "AAPL",
        "GOOGL",
        "GOOG",
        "META",
        "AMZN",
        "NFLX",
        "ADBE",
        "TSLA",
        "BKNG",
        "EBAY",
        "INTU",
    }

    N_WORKERS = min(8, os.cpu_count() or 4)

    def _ann(sv):
        sh = sv.get("sharpe") or 0.0
        n = sv.get("n") or 0
        if n < 5 or sh == 0:
            return "—"
        return f"{sh * math.sqrt(n / 20):.2f}"

    def _fmt14(label, sv, base_sh=0.0):
        sh = sv.get("sharpe") or 0.0
        d = sh - base_sh
        flag = " ← **ANN≥1**" if _ann(sv) != "—" and float(_ann(sv)) >= 1.0 else ""
        return [
            label + flag,
            str(sv["n"]),
            f"{sv['wr']:.1f}%",
            f"{sv['avg']:+.2f}%",
            f"{fmt_sharpe(sv['sharpe'])} ({d:+.2f})",
            f"-{sv['max_dd']:.2f}%",
            _ann(sv),
        ]

    if pre_dfs is None:
        print("Pre-scoring tickers (MR=0.1)…", end=" ", flush=True)
        pre_dfs = _prescore(all_dfs, mr_w=0.1)
        print("done.", end=" ")
    tech_list = [t for t in pre_dfs if t in TECH_FAANG]
    other_list = [t for t in pre_dfs if t not in TECH_FAANG]
    all_list = list(pre_dfs.keys())
    print(f"Tech={len(tech_list)}, Other={len(other_list)}.")

    with _managed_pool(pool, N_WORKERS, _pool_init, (pre_dfs, vix, spy_trend, stlfsi4)) as _p:

        def _run14(tech_hold=10, tech_thresh=40, atr_min=20.0):
            """Run tech and non-tech in parallel, merge results."""
            sv_t, tdf_t = _run_par(_p, tech_list, atr_min=atr_min, hold_days=tech_hold, thresh=tech_thresh)
            sv_o, tdf_o = _run_par(_p, other_list, atr_min=atr_min)
            both = [t for t in [tdf_t, tdf_o] if not t.empty]
            if not both:
                return dict(_EMPTY_STATS), pd.DataFrame()
            tdf = pd.concat(both, ignore_index=True)
            return stats(tdf["net_pct"].tolist()), tdf

        print("Evaluating tech-specific overrides (parallel per config)…", flush=True)
        base14, _ = _run14(tech_hold=10, tech_thresh=40)
        sv_hold5, _ = _run14(tech_hold=5, tech_thresh=40)
        sv_thresh38, _ = _run14(tech_hold=10, tech_thresh=38)
        sv_combo, _ = _run14(tech_hold=5, tech_thresh=38)

    base_sh14 = base14.get("sharpe") or 0.0
    print_table(
        ["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann. Sharpe"],
        [
            _fmt14("Baseline (MR=0.1 + ATR≥20)", base14, base_sh14),
            _fmt14("Tech 5-day hold", sv_hold5, base_sh14),
            _fmt14("Tech BUY_THRESH=38", sv_thresh38, base_sh14),
            _fmt14("Tech 5d hold + Thresh=38", sv_combo, base_sh14),
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# §15 — Sector-Specific Filter Research
# ─────────────────────────────────────────────────────────────────────────────


def run_sector_research(all_dfs, vix, spy_trend, stlfsi4, pool=None, pre_dfs: dict | None = None):
    """§15: Per-sector filter sweep — universe pruning, hold, VIX, threshold, best combo.

    Strong sectors (§13b): Tech/FAANG Sh=0.43, Financials Sh=0.56, Consumer Sh=0.68
    Weak sectors:          Semis 0.13, Software/IT 0.14, Other 0.13

    §15a  Universe pruning  — strong-only (42 tickers) vs full 68
    §15b  Hold sweep        — 5 / 7 / 10 / 15 per strong sector
    §15c  VIX floor sweep   — None / ≥13 / ≥15 per strong sector
    §15d  BUY_THRESH sweep  — 36 / 38 / 40 / 42 per strong sector
    §15e  ATR floor         — Financials ATR≥30 validation + aggregate impact
    §15f  Best combined     — programmatic winner per dimension, applied together
    """
    _section("15. Sector-Specific Filter Research")
    print("\n\n## 15. Sector-Specific Filter Research (§15)\n")
    print("> §13b baseline: Tech/FAANG Sh=0.43 Ann=0.60 | Financials Sh=0.56 Ann=0.62 | Consumer Sh=0.68 Ann=0.63")
    print("> §13b weak:     Semis 0.13 | Software/IT 0.14 | Other 0.13")
    print("> Research: §15a pruning · §15b hold · §15c VIX · §15d thresh · §15e ATR · §15f best combo\n")

    SECTOR_MAP = {
        "Tech/FAANG": {
            "NVDA",
            "MSFT",
            "AAPL",
            "GOOGL",
            "GOOG",
            "META",
            "AMZN",
            "NFLX",
            "ADBE",
            "TSLA",
            "BKNG",
            "EBAY",
            "INTU",
        },
        "Financials": {
            "JPM",
            "WFC",
            "BAC",
            "GS",
            "V",
            "MA",
            "BLK",
            "SCHW",
            "CME",
            "SPGI",
            "MCO",
            "ICE",
            "MSCI",
            "FIS",
            "FISV",
        },
        "Consumer": {
            "HD",
            "F",
            "LOW",
            "TJX",
            "ROST",
            "LULU",
            "MAR",
            "HLT",
            "RCL",
            "CHTR",
            "GM",
            "COST",
            "SBUX",
            "TGT",
            "PYPL",
        },
        "Semis": {"INTC", "AMD", "AVGO", "AMAT", "LRCX", "KLAC", "TSM", "QCOM", "TXN", "MRVL"},
        "Software/IT": {"CSCO", "ORCL", "ADSK", "CDNS", "SNPS", "CTSH", "FTNT", "NOW", "PANW", "WDAY", "ACN", "AKAM"},
        "Other": {"EOG", "VRSK", "DHI", "LEN"},
    }
    STRONG = ["Tech/FAANG", "Financials", "Consumer"]
    MR_W = 0.1
    N_WORKERS = min(8, os.cpu_count() or 4)
    HDR = ["Config", "N", "WR", "Avg Ret", "Sharpe", "MaxDD", "Ann.Sharpe"]
    HDR_D = ["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann.Sharpe"]

    if pre_dfs is None:
        print("Pre-scoring tickers (MR=0.1)…", end=" ", flush=True)
        pre_dfs = _prescore(all_dfs, mr_w=MR_W)
        print("done.", end=" ")

    sector_lists: dict[str, list] = {name: [t for t in tset if t in pre_dfs] for name, tset in SECTOR_MAP.items()}
    all_tickers = list(pre_dfs.keys())
    strong_tickers = [t for s in STRONG for t in sector_lists[s]]
    weak_set = set(all_tickers) - set(strong_tickers)

    print(
        f"Strong sectors: Tech={len(sector_lists['Tech/FAANG'])}, "
        f"Fin={len(sector_lists['Financials'])}, Con={len(sector_lists['Consumer'])} "
        f"(total {len(strong_tickers)}) | "
        f"Weak: {len(weak_set)} tickers\n"
    )

    # ── Formatters ────────────────────────────────────────────────────────────
    def _ann_val(sv) -> float:
        sh = sv.get("sharpe") or 0.0
        n = sv.get("n") or 0
        return sh * math.sqrt(n / 20) if n >= 5 else 0.0

    def _ann_fmt(sv) -> str:
        v = _ann_val(sv)
        return f"{v:.2f}" if v > 0 else "—"

    def _row(label, sv):
        return [
            label,
            str(sv["n"]),
            f"{sv['wr']:.1f}%",
            f"{sv['avg']:+.2f}%",
            fmt_sharpe(sv.get("sharpe") or 0),
            f"-{sv['max_dd']:.2f}%",
            _ann_fmt(sv),
        ]

    def _row_d(label, sv, base_sh=0.0):
        sh = sv.get("sharpe") or 0.0
        flag = " ← **ANN≥1**" if _ann_val(sv) >= 1.0 else ""
        return [
            label + flag,
            str(sv["n"]),
            f"{sv['wr']:.1f}%",
            f"{sv['avg']:+.2f}%",
            f"{fmt_sharpe(sh)} ({sh - base_sh:+.2f})",
            f"-{sv['max_dd']:.2f}%",
            _ann_fmt(sv),
        ]

    with _managed_pool(pool, N_WORKERS, _pool_init, (pre_dfs, vix, spy_trend, stlfsi4)) as _p:

        def _r(tickers, **kw):
            return _run_par(_p, tickers, **kw)

        # ── §15a. Universe pruning ────────────────────────────────────────────
        _section("15a. Universe Pruning")
        print("\n### 15a. Universe Pruning — Remove Weak Sectors\n")
        print("> Semis (Sh=0.13), Software/IT (0.14), Other (0.13) — all far below threshold.")
        print("> Removing 26 weak tickers: does aggregate Ann.Sharpe improve?\n")
        print("  Running full vs strong-only in parallel…", flush=True)

        sv_full, _ = _r(all_tickers)
        sv_strong, _ = _r(strong_tickers)

        base_sh15 = sv_full.get("sharpe") or 0.0
        print_table(
            HDR_D,
            [
                _row_d("Full 68 tickers (baseline)", sv_full, base_sh15),
                _row_d("Strong only — 42 tickers", sv_strong, base_sh15),
            ],
        )
        print("\n> Verdict: if strong-only Ann > full → remove weak sectors from universe.")
        print("> If strong-only Ann < full → weak sectors offset each other; leave intact.\n")

        # ── §15b. Hold period sweep ───────────────────────────────────────────
        _section("15b. Hold Period Sweep — Per Strong Sector")
        print("\n### 15b. Hold Period per Strong Sector (isolated)\n")
        print("> Hypothesis: Tech V-bottoms resolve in 5d; Financials/Consumer need 7-10d.")
        print("> Hold = 5 / 7 / 10 (baseline) / 15. Each sector tested in isolation.\n")

        HOLD_VALS = [5, 7, 10, 15]
        best_hold: dict[str, int] = {}

        for sector in STRONG:
            sl = sector_lists[sector]
            if not sl:
                best_hold[sector] = 10
                continue
            print(f"\n**{sector}** ({len(sl)} tickers):\n")
            rows = []
            best_ann = -1.0
            best_h = 10
            for h in HOLD_VALS:
                sv, _ = _r(sl, hold_days=h if h != 10 else None)
                base_flag = " (baseline)" if h == 10 else ""
                rows.append(_row(f"Hold = {h}d{base_flag}", sv))
                a = _ann_val(sv)
                if a > best_ann:
                    best_ann = a
                    best_h = h
            best_hold[sector] = best_h
            print_table(HDR, rows)
            print(f"> Winner: hold={best_h}d  Ann={best_ann:.2f}\n")

        print("\n**§15b Summary — optimal hold per sector:**")
        for s in STRONG:
            print(f"  {s}: {best_hold[s]}d")

        # ── §15c. VIX floor sweep ─────────────────────────────────────────────
        _section("15c. VIX Floor Sweep — Per Strong Sector")
        print("\n### 15c. VIX Floor per Strong Sector (isolated)\n")
        print("> VIX≥13 = 'mild fear' filter. May help Tech/Fin (panic bounces), hurt Consumer (staples-adjacent).")
        print("> VIX = None (baseline) / ≥13 / ≥15. Each sector tested in isolation.\n")

        VIX_VALS: list = [None, 13.0, 15.0]
        best_vix: dict[str, float | None] = {}

        for sector in STRONG:
            sl = sector_lists[sector]
            if not sl:
                best_vix[sector] = None
                continue
            print(f"\n**{sector}** ({len(sl)} tickers):\n")
            rows = []
            best_ann = -1.0
            best_vm: float | None = None
            for vm in VIX_VALS:
                sv, _ = _r(sl, vix_min=vm)
                lbl = "No VIX floor (baseline)" if vm is None else f"VIX ≥ {vm:.0f}"
                rows.append(_row(lbl, sv))
                a = _ann_val(sv)
                if a > best_ann:
                    best_ann = a
                    best_vm = vm
            best_vix[sector] = best_vm
            print_table(HDR, rows)
            vl = f"≥{best_vm:.0f}" if best_vm is not None else "none"
            print(f"> Winner: VIX {vl}  Ann={best_ann:.2f}\n")

        print("\n**§15c Summary — optimal VIX floor per sector:**")
        for s in STRONG:
            vl = f"≥{best_vix[s]:.0f}" if best_vix[s] is not None else "none"
            print(f"  {s}: VIX {vl}")

        # ── §15d. BUY_THRESH sweep ────────────────────────────────────────────
        _section("15d. BUY_THRESH Sweep — Per Strong Sector")
        print("\n### 15d. BUY_THRESH per Strong Sector (isolated)\n")
        print("> Lower thresh → more entries (↑N, ↓avg quality). Higher → fewer but cleaner.")
        print("> Base: thresh=40. Test 36 / 38 / 40 / 42 per sector.\n")

        THRESH_VALS = [36, 38, 40, 42]
        best_thresh: dict[str, int] = {}

        for sector in STRONG:
            sl = sector_lists[sector]
            if not sl:
                best_thresh[sector] = 40
                continue
            print(f"\n**{sector}** ({len(sl)} tickers):\n")
            rows = []
            best_ann = -1.0
            best_th = 40
            for th in THRESH_VALS:
                sv, _ = _r(sl, thresh=th)
                base_flag = " (baseline)" if th == 40 else ""
                rows.append(_row(f"THRESH = {th}{base_flag}", sv))
                a = _ann_val(sv)
                if a > best_ann:
                    best_ann = a
                    best_th = th
            best_thresh[sector] = best_th
            print_table(HDR, rows)
            print(f"> Winner: thresh={best_th}  Ann={best_ann:.2f}\n")

        print("\n**§15d Summary — optimal BUY_THRESH per sector:**")
        for s in STRONG:
            print(f"  {s}: thresh={best_thresh[s]}")

        # ── §15e. ATR floor per sector ────────────────────────────────────────
        _section("15e. Sector ATR Floor — Financials ATR≥30 Validation")
        print("\n### 15e. Sector-Specific ATR Floor\n")
        print("> §13b finding: Financials ATR≥30 → Sh 0.56→0.60, Ann 0.62→0.66.")
        print("> Confirming on isolated Financials list; then measuring aggregate impact.\n")

        fin_list = sector_lists["Financials"]
        non_fin = [t for t in strong_tickers if t not in set(fin_list)]

        sv_fin20, _ = _r(fin_list, atr_min=20.0)
        sv_fin30, _ = _r(fin_list, atr_min=30.0)

        print("**Financials isolated (ATR≥20 vs ATR≥30):**\n")
        print_table(
            HDR,
            [
                _row("Financials  ATR ≥ 20 (baseline)", sv_fin20),
                _row("Financials  ATR ≥ 30", sv_fin30),
            ],
        )

        fin_atr_best: float = 30.0 if _ann_val(sv_fin30) >= _ann_val(sv_fin20) else 20.0
        print(f"\n> Financials optimal ATR floor: ≥{fin_atr_best:.0f}\n")

        # Aggregate: Fin at best ATR, other strong sectors at default, weak excluded
        sv_fin_opt, tdf_fin = _r(fin_list, atr_min=fin_atr_best)
        sv_other, tdf_oth = _r(non_fin)
        both = [t for t in [tdf_fin, tdf_oth] if not t.empty]
        if both:
            agg_tdf = pd.concat(both, ignore_index=True)
            sv_agg_fin = stats(agg_tdf["net_pct"].tolist())
        else:
            sv_agg_fin = dict(_EMPTY_STATS)

        print("**Aggregate (strong sectors: Fin at best ATR, others at default):**\n")
        print_table(
            HDR_D,
            [
                _row_d("Full 68 baseline", sv_full, base_sh15),
                _row_d("Strong only, all ATR≥20", sv_strong, base_sh15),
                _row_d(f"Strong + Fin ATR≥{fin_atr_best:.0f}", sv_agg_fin, base_sh15),
            ],
        )

        # ── §15f. Best combined per-sector config ─────────────────────────────
        _section("15f. Best Combined Per-Sector Configuration")
        print("\n### 15f. Best Combined Per-Sector Configuration\n")
        print("> Apply optimal hold, VIX, thresh (from §15b/c/d) + Fin ATR≥30 (§15e).")
        print("> Weak sectors excluded (§15a verdict).\n")
        print("  Per-sector optimal config:")
        for s in STRONG:
            bh = best_hold[s]
            bv = best_vix[s]
            bt = best_thresh[s]
            atr_note = f"  ATR≥{fin_atr_best:.0f}" if s == "Financials" else ""
            vl = f"  VIX≥{bv:.0f}" if bv is not None else ""
            print(f"    {s}: hold={bh}d  thresh={bt}{vl}{atr_note}")
        print()

        print("  Running sector-optimized configs…", flush=True)
        all_tdfs: list = []
        for sector in STRONG:
            sl = sector_lists[sector]
            if not sl:
                continue
            kw: dict = {}
            h = best_hold[sector]
            if h != 10:
                kw["hold_days"] = h
            vm = best_vix[sector]
            if vm is not None:
                kw["vix_min"] = vm
            th = best_thresh[sector]
            if th != 40:
                kw["thresh"] = th
            if sector == "Financials" and fin_atr_best == 30.0:
                kw["atr_min"] = 30.0
            _, tdf = _r(sl, **kw)
            if not tdf.empty:
                all_tdfs.append(tdf)

        if all_tdfs:
            combined_tdf = pd.concat(all_tdfs, ignore_index=True)
            sv_combined = stats(combined_tdf["net_pct"].tolist())
        else:
            sv_combined = dict(_EMPTY_STATS)

        print_table(
            HDR_D,
            [
                _row_d("Full 68 tickers, uniform ATR≥20 (baseline)", sv_full, base_sh15),
                _row_d("Strong only, uniform ATR≥20", sv_strong, base_sh15),
                _row_d("Strong + sector-optimized filters", sv_combined, base_sh15),
            ],
        )

        print(f"\n*§15 Sector-Specific Filter Research · MR=0.1 · {END}*")


# ─────────────────────────────────────────────────────────────────────────────
# §16 — Full-universe sector sweep (all 11 sectors, all dimensions)
# ─────────────────────────────────────────────────────────────────────────────


def run_full_sector_research(all_dfs, vix, spy_trend, stlfsi4, pool=None, pre_dfs: dict | None = None):
    """§16: Comprehensive per-sector sweep across all sectors in the expanded universe.

    Sectors: Tech/FAANG · Semis · Software/IT · Financials · Consumer · Healthcare
             Energy · Industrials · Telecom · Materials · Real Estate

    §16a  Sector baselines        — each sector at default + ATR≥20/30
    §16b  Hold sweep              — 5 / 7 / 10 per sector
    §16c  VIX floor sweep         — None / ≥13 / ≥15 per sector
    §16d  BUY_THRESH sweep        — 38 / 40 / 42 per sector
    §16e  Best combined           — auto-selected winners applied per sector
    §16f  Sector ranking          — rank all sectors by optimal Ann.Sharpe
    """
    _section("16. Full-Universe Sector Research")
    print("\n\n## 16. Full-Universe Sector Research (§16)\n")
    print("> Expanded universe: 11 sectors including Healthcare, Energy, Industrials, Telecom, Materials, Real Estate")
    print("> §15 validated: Tech hold=5d · Fin VIX≥15 + ATR≥30 + hold=7d · Consumer VIX≥13 + hold=10d")
    print("> §16 extends to all sectors; each dimension swept independently then combined.\n")

    SECTOR_MAP: dict[str, set] = {
        "Tech/FAANG": {
            "NVDA",
            "MSFT",
            "AAPL",
            "GOOGL",
            "GOOG",
            "META",
            "AMZN",
            "NFLX",
            "ADBE",
            "TSLA",
            "BKNG",
            "EBAY",
            "INTU",
        },
        "Semis": {"INTC", "AMD", "AVGO", "AMAT", "LRCX", "KLAC", "TSM", "QCOM", "TXN", "MRVL"},
        "Software/IT": {
            "CSCO",
            "ORCL",
            "ADSK",
            "CDNS",
            "SNPS",
            "CTSH",
            "FTNT",
            "NOW",
            "PANW",
            "WDAY",
            "ACN",
            "AKAM",
            "VRSK",
        },
        "Financials": {
            "JPM",
            "WFC",
            "BAC",
            "GS",
            "V",
            "MA",
            "BLK",
            "SCHW",
            "CME",
            "SPGI",
            "MCO",
            "ICE",
            "MSCI",
            "FIS",
            "FISV",
        },
        "Consumer": {
            "HD",
            "F",
            "LOW",
            "TJX",
            "ROST",
            "LULU",
            "MAR",
            "HLT",
            "RCL",
            "CHTR",
            "GM",
            "COST",
            "SBUX",
            "TGT",
            "PYPL",
            "DHI",
            "LEN",
        },
        "Healthcare": {"JNJ", "AMGN", "BMY", "GILD", "MDT", "ABT", "ISRG"},
        "Energy": {"XOM", "CVX", "COP", "SLB", "EOG"},
        "Industrials": {"CAT", "HON", "GE", "UNP", "MMM", "BA"},
        "Telecom": {"VZ", "T"},
        "Materials": {"APD", "ECL"},
        "Real Estate": {"AMT", "PLD", "SPG"},
    }
    ALL_SECTORS = list(SECTOR_MAP.keys())
    MR_W = 0.1
    N_WORKERS = min(8, os.cpu_count() or 4)
    HDR = ["Sector", "N", "WR", "Avg Ret", "Sharpe", "MaxDD", "Ann.Sharpe"]
    HDR_SW = ["Config", "N", "WR", "Avg Ret", "Sharpe", "MaxDD", "Ann.Sharpe"]

    if pre_dfs is None:
        print("Pre-scoring tickers (MR=0.1)…", end=" ", flush=True)
        pre_dfs = _prescore(all_dfs, mr_w=MR_W)
        print("done.", end=" ")

    sector_lists: dict[str, list] = {name: [t for t in tset if t in pre_dfs] for name, tset in SECTOR_MAP.items()}
    all_tickers = list(pre_dfs.keys())
    total = sum(len(v) for v in sector_lists.values())
    print(f"{total} tickers across {len(ALL_SECTORS)} sectors.\n")
    for s, sl in sector_lists.items():
        print(f"  {s}: {len(sl)} tickers")
    print()

    def _ann_val(sv) -> float:
        sh = sv.get("sharpe") or 0.0
        n = sv.get("n") or 0
        return sh * math.sqrt(n / 20) if n >= 5 else 0.0

    def _ann_fmt(sv) -> str:
        v = _ann_val(sv)
        return f"{v:.2f}" if v > 0 else "—"

    def _row(sector, sv):
        return [
            sector,
            str(sv["n"]),
            f"{sv['wr']:.1f}%",
            f"{sv['avg']:+.2f}%",
            fmt_sharpe(sv.get("sharpe") or 0),
            f"-{sv['max_dd']:.2f}%",
            _ann_fmt(sv),
        ]

    def _rowc(label, sv):
        return [
            label,
            str(sv["n"]),
            f"{sv['wr']:.1f}%",
            f"{sv['avg']:+.2f}%",
            fmt_sharpe(sv.get("sharpe") or 0),
            f"-{sv['max_dd']:.2f}%",
            _ann_fmt(sv),
        ]

    with _managed_pool(pool, N_WORKERS, _pool_init, (pre_dfs, vix, spy_trend, stlfsi4)) as _p:

        def _r(tickers, **kw):
            return _run_par(_p, tickers, **kw)

        # ── §16a. Sector baselines ────────────────────────────────────────────
        _section("16a. Sector Baselines")
        print("\n### 16a. Sector Baselines (default MR=0.1 + ATR≥20)\n")

        base_sv: dict[str, dict] = {}
        base_rows = []
        for sect in ALL_SECTORS:
            sl = sector_lists[sect]
            if not sl:
                continue
            sv, _ = _r(sl)
            base_sv[sect] = sv
            base_rows.append(_row(sect, sv))

        # Sort by Ann.Sharpe desc
        base_rows.sort(key=lambda r: float(r[6]) if r[6] != "—" else -1, reverse=True)
        print_table(HDR, base_rows)

        # Classify
        strong = [s for s in ALL_SECTORS if _ann_val(base_sv.get(s, {})) >= 0.50]
        moderate = [s for s in ALL_SECTORS if 0.20 <= _ann_val(base_sv.get(s, {})) < 0.50]
        weak = [s for s in ALL_SECTORS if _ann_val(base_sv.get(s, {})) < 0.20]
        print(f"\n> Strong (Ann ≥ 0.50):   {', '.join(strong) or 'none'}")
        print(f"> Moderate (0.20–0.50): {', '.join(moderate) or 'none'}")
        print(f"> Weak (Ann < 0.20):    {', '.join(weak) or 'none'}")
        print()

        # ── §16b. Hold sweep ─────────────────────────────────────────────────
        _section("16b. Hold Period Sweep — All Sectors")
        print("\n### 16b. Hold Period per Sector\n")
        print("> Test hold = 5 / 7 / 10 (baseline). Each sector in isolation.\n")

        HOLD_VALS = [5, 7, 10]
        best_hold: dict[str, int] = {}

        for sect in ALL_SECTORS:
            sl = sector_lists[sect]
            if not sl:
                best_hold[sect] = 10
                continue
            rows = []
            best_ann = -1.0
            best_h = 10
            for h in HOLD_VALS:
                sv, _ = _r(sl, hold_days=h if h != 10 else None)
                flag = " (base)" if h == 10 else ""
                rows.append(_rowc(f"Hold={h}d{flag}", sv))
                a = _ann_val(sv)
                if a > best_ann:
                    best_ann = a
                    best_h = h
            best_hold[sect] = best_h
            print(f"\n**{sect}** ({len(sl)} tickers):\n")
            print_table(HDR_SW, rows)
            print(f"> Winner: {best_h}d  Ann={best_ann:.2f}")

        print("\n**§16b — Hold winners:**")
        for s in ALL_SECTORS:
            print(f"  {s}: {best_hold.get(s, 10)}d")

        # ── §16c. VIX floor sweep ─────────────────────────────────────────────
        _section("16c. VIX Floor Sweep — All Sectors")
        print("\n### 16c. VIX Floor per Sector\n")
        print("> Test VIX = None (base) / ≥13 / ≥15. Each sector in isolation.\n")

        VIX_VALS: list = [None, 13.0, 15.0]
        best_vix: dict[str, float | None] = {}

        for sect in ALL_SECTORS:
            sl = sector_lists[sect]
            if not sl:
                best_vix[sect] = None
                continue
            rows = []
            best_ann = -1.0
            best_vm: float | None = None
            for vm in VIX_VALS:
                sv, _ = _r(sl, vix_min=vm)
                lbl = "No VIX floor (base)" if vm is None else f"VIX ≥ {vm:.0f}"
                rows.append(_rowc(lbl, sv))
                a = _ann_val(sv)
                if a > best_ann:
                    best_ann = a
                    best_vm = vm
            best_vix[sect] = best_vm
            print(f"\n**{sect}** ({len(sl)} tickers):\n")
            print_table(HDR_SW, rows)
            vl = f"≥{best_vm:.0f}" if best_vm is not None else "none"
            print(f"> Winner: VIX {vl}  Ann={best_ann:.2f}")

        print("\n**§16c — VIX floor winners:**")
        for s in ALL_SECTORS:
            vl = f"≥{best_vix.get(s):.0f}" if best_vix.get(s) is not None else "none"
            print(f"  {s}: VIX {vl}")

        # ── §16d. BUY_THRESH sweep ────────────────────────────────────────────
        _section("16d. BUY_THRESH Sweep — All Sectors")
        print("\n### 16d. BUY_THRESH per Sector\n")
        print("> Test thresh = 38 / 40 (base) / 42. Each sector in isolation.\n")

        THRESH_VALS = [38, 40, 42]
        best_thresh: dict[str, int] = {}

        for sect in ALL_SECTORS:
            sl = sector_lists[sect]
            if not sl:
                best_thresh[sect] = 40
                continue
            rows = []
            best_ann = -1.0
            best_th = 40
            for th in THRESH_VALS:
                sv, _ = _r(sl, thresh=th)
                flag = " (base)" if th == 40 else ""
                rows.append(_rowc(f"THRESH={th}{flag}", sv))
                a = _ann_val(sv)
                if a > best_ann:
                    best_ann = a
                    best_th = th
            best_thresh[sect] = best_th
            print(f"\n**{sect}** ({len(sl)} tickers):\n")
            print_table(HDR_SW, rows)
            print(f"> Winner: thresh={best_th}  Ann={best_ann:.2f}")

        print("\n**§16d — Thresh winners:**")
        for s in ALL_SECTORS:
            print(f"  {s}: thresh={best_thresh.get(s, 40)}")

        # ── §16e. ATR floor sweep — all sectors ───────────────────────────────
        _section("16e. ATR Floor Sweep — All Sectors")
        print("\n### 16e. ATR%rank Floor per Sector\n")
        print("> §15e confirmed Financials ATR≥30 (+0.04 Sh). Test all sectors: ATR≥20/30.\n")

        ATR_VALS = [20.0, 30.0]
        best_atr: dict[str, float] = {}

        atr_rows_agg = []
        for sect in ALL_SECTORS:
            sl = sector_lists[sect]
            if not sl:
                best_atr[sect] = 20.0
                continue
            best_ann = -1.0
            best_at = 20.0
            row_parts = [sect]
            for at in ATR_VALS:
                sv, _ = _r(sl, atr_min=at)
                a = _ann_val(sv)
                row_parts.append(f"N={sv['n']} Sh={fmt_sharpe(sv.get('sharpe') or 0)} Ann={_ann_fmt(sv)}")
                if a > best_ann:
                    best_ann = a
                    best_at = at
            best_atr[sect] = best_at
            row_parts.append(f"≥{best_at:.0f}")
            atr_rows_agg.append(row_parts)

        print_table(["Sector", "ATR≥20", "ATR≥30", "Best ATR"], atr_rows_agg)

        print("\n**§16e — ATR floor winners:**")
        for s in ALL_SECTORS:
            print(f"  {s}: ATR≥{best_atr.get(s, 20.0):.0f}")

        # ── §16f. Best combined per sector ────────────────────────────────────
        _section("16f. Best Combined Per-Sector Config")
        print("\n### 16f. Best Combined Per-Sector Configuration\n")
        print("> Apply optimal hold, VIX, thresh, ATR from §16b/c/d/e to each sector.\n")
        print("  Per-sector optimal config:")
        for s in ALL_SECTORS:
            bh = best_hold.get(s, 10)
            bv = best_vix.get(s)
            bt = best_thresh.get(s, 40)
            ba = best_atr.get(s, 20.0)
            vl = f"VIX≥{bv:.0f}" if bv is not None else "VIX=any"
            print(f"    {s}: hold={bh}d  {vl}  thresh={bt}  ATR≥{ba:.0f}")
        print()

        sv_full_baseline, _ = _r(all_tickers)
        base_sh16 = sv_full_baseline.get("sharpe") or 0.0

        print("  Running sector-optimized simulation…", flush=True)
        all_tdfs: list = []
        for sect in ALL_SECTORS:
            sl = sector_lists[sect]
            if not sl:
                continue
            kw: dict = {}
            h = best_hold.get(sect, 10)
            if h != 10:
                kw["hold_days"] = h
            vm = best_vix.get(sect)
            if vm is not None:
                kw["vix_min"] = vm
            th = best_thresh.get(sect, 40)
            if th != 40:
                kw["thresh"] = th
            ba = best_atr.get(sect, 20.0)
            if ba != 20.0:
                kw["atr_min"] = ba
            _, tdf = _r(sl, **kw)
            if not tdf.empty:
                all_tdfs.append(tdf)

        if all_tdfs:
            combined_tdf = pd.concat(all_tdfs, ignore_index=True)
            sv_combined = stats(combined_tdf["net_pct"].tolist())
        else:
            sv_combined = dict(_EMPTY_STATS)

        def _row_d16(label, sv):
            sh = sv.get("sharpe") or 0.0
            d = sh - base_sh16
            flag = " ← **ANN≥1**" if _ann_val(sv) >= 1.0 else ""
            return [
                label + flag,
                str(sv["n"]),
                f"{sv['wr']:.1f}%",
                f"{sv['avg']:+.2f}%",
                f"{fmt_sharpe(sh)} ({d:+.2f})",
                f"-{sv['max_dd']:.2f}%",
                _ann_fmt(sv),
            ]

        print_table(
            ["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann.Sharpe"],
            [
                _row_d16("Full universe, uniform ATR≥20 (baseline)", sv_full_baseline),
                _row_d16("All sectors, sector-optimized filters", sv_combined),
            ],
        )

        # §16 sector ranking by best Ann.Sharpe
        _section("16g. Sector Ranking")
        print("\n### 16g. Sector Ranking — Optimal Ann.Sharpe\n")

        ranking_rows = []
        for sect in ALL_SECTORS:
            sl = sector_lists[sect]
            if not sl:
                continue
            kw = {}
            h = best_hold.get(sect, 10)
            if h != 10:
                kw["hold_days"] = h
            vm = best_vix.get(sect)
            if vm is not None:
                kw["vix_min"] = vm
            th = best_thresh.get(sect, 40)
            if th != 40:
                kw["thresh"] = th
            ba = best_atr.get(sect, 20.0)
            if ba != 20.0:
                kw["atr_min"] = ba
            sv, _ = _r(sl, **kw)
            ranking_rows.append((sect, sv, _ann_val(sv)))

        ranking_rows.sort(key=lambda x: x[2], reverse=True)
        print_table(
            ["Rank", "Sector", "N", "WR", "Avg Ret", "Sharpe", "MaxDD", "Ann.Sharpe"],
            [[str(i + 1)] + _row(r[0], r[1]) for i, r in enumerate(ranking_rows)],
        )
        print(f"\n*§16 Full-Universe Sector Research · MR=0.1 · {END}*")


# ── §17 — Entry Quality Gate Research ────────────────────────────────────────
# Tests four new gate ideas sourced from academic research (2026-05-25):
#   §17a  ATR ceiling (≤70th pct)    — trending-panic filter (Quantpedia P70 finding)
#   §17b  Return jump filter          — block single-day drops < −6% (Alpha Architect)
#   §17c  Entry delay (T+2)           — skip "continuation morning" before reversal
#   §17d  Combined best               — all three applied together
# Base: MR=0.1 + ATR≥20, strong 42-ticker universe, §15f sector-optimized params.


def run_gate_research_v17(all_dfs, vix, spy_trend, stlfsi4, pool=None, pre_dfs: dict | None = None) -> None:
    """§17: Entry quality gate research — ATR ceiling, return jump filter, entry delay."""
    import os as _os

    print("\n\n## 17. Entry Quality Gate Research (§17)\n")
    print("> Base: §15f sector-optimized config (Tech/Fin/Consumer, MR=0.1 + ATR≥20).")
    print("> Academic sources: Quantpedia ATR P70, Alpha Architect return-jump filter.")
    print(f"> Period: {START} → {END}\n")

    STRONG_TICKERS = [
        "NVDA",
        "MSFT",
        "AAPL",
        "GOOGL",
        "GOOG",
        "META",
        "AMZN",
        "NFLX",
        "ADBE",
        "TSLA",
        "BKNG",
        "EBAY",
        "INTU",
        "JPM",
        "WFC",
        "BAC",
        "GS",
        "V",
        "MA",
        "BLK",
        "SCHW",
        "CME",
        "SPGI",
        "MCO",
        "ICE",
        "MSCI",
        "FIS",
        "FISV",
        "HD",
        "F",
        "LOW",
        "TJX",
        "ROST",
        "LULU",
        "MAR",
        "HLT",
        "RCL",
        "CHTR",
        "GM",
        "COST",
        "SBUX",
        "TGT",
        "PYPL",
    ]
    STRONG = [t for t in STRONG_TICKERS if t in (pre_dfs or all_dfs)]

    N_WORKERS = min(8, _os.cpu_count() or 4)
    with _managed_pool(pool, N_WORKERS, _pool_init, (pre_dfs or {}, vix, spy_trend, stlfsi4)) as _p:

        def _r(tickers, atr_min=20.0, **kw):
            return _run_par(_p, tickers, atr_min=atr_min, **kw)

        def _ann_val(sv) -> float:
            sh = sv.get("sharpe") or 0.0
            n = sv.get("n") or 0
            return sh * math.sqrt(n / 20) if n >= 5 else 0.0

        def _ann_fmt(sv) -> str:
            v = _ann_val(sv)
            return f"{v:.2f}" if v > 0 else "—"

        def _row(label, sv, ann=None, base_sv=None):
            sh = sv.get("sharpe") or 0.0
            flag = " ← **ANN≥1**" if (ann or _ann_val(sv)) >= 1.0 else ""
            base_sh = (base_sv.get("sharpe") or 0.0) if base_sv is not None else sh
            return [
                label + flag,
                str(sv["n"]),
                f"{sv['wr']:.1f}%",
                f"{sv['avg']:+.2f}%",
                f"{fmt_sharpe(sh)} ({sh - base_sh:+.2f})",
                f"-{sv['max_dd']:.2f}%",
                _ann_fmt(sv),
            ]

        # ── §15f baseline (sector-optimized, reproduced for reference) ─────────
        _section("17. Baseline — §15f Reproduced")
        print("\n### §17 Baseline — §15f Best Combined\n")

        TECH = [
            t
            for t in [
                "NVDA",
                "MSFT",
                "AAPL",
                "GOOGL",
                "GOOG",
                "META",
                "AMZN",
                "NFLX",
                "ADBE",
                "TSLA",
                "BKNG",
                "EBAY",
                "INTU",
            ]
            if t in (pre_dfs or all_dfs)
        ]
        FIN = [
            t
            for t in [
                "JPM",
                "WFC",
                "BAC",
                "GS",
                "V",
                "MA",
                "BLK",
                "SCHW",
                "CME",
                "SPGI",
                "MCO",
                "ICE",
                "MSCI",
                "FIS",
                "FISV",
            ]
            if t in (pre_dfs or all_dfs)
        ]
        CONS = [
            t
            for t in [
                "HD",
                "F",
                "LOW",
                "TJX",
                "ROST",
                "LULU",
                "MAR",
                "HLT",
                "RCL",
                "CHTR",
                "GM",
                "COST",
                "SBUX",
                "TGT",
                "PYPL",
            ]
            if t in (pre_dfs or all_dfs)
        ]

        sv_tech, tdf_tech = _r(TECH, hold_days=5, vix_min=13.0, thresh=40)
        sv_fin, tdf_fin = _r(FIN, hold_days=7, vix_min=15.0, thresh=42, atr_min=30.0)
        sv_cons, tdf_cons = _r(CONS, hold_days=10, vix_min=13.0, thresh=38)
        base_trades = [df for df in [tdf_tech, tdf_fin, tdf_cons] if not df.empty]
        if base_trades:
            tdf_base = pd.concat(base_trades, ignore_index=True)
            sv_base = stats(tdf_base["net_pct"].tolist())
        else:
            sv_base = dict(_EMPTY_STATS)
        ann_base = _ann_val(sv_base)

        print_table(
            ["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann.Sharpe"],
            [_row("§15f baseline (sector-opt)", sv_base, ann_base)],
        )

        # ── §17a. ATR ceiling sweep ────────────────────────────────────────────
        _section("17a. ATR Ceiling Sweep")
        print("\n### §17a. ATR Percentile Rank Ceiling Sweep\n")
        print("> Quantpedia: P70 is optimal MR ceiling. Testing None / 90 / 80 / 70.\n")

        atrc_rows = [_row("no ceiling (baseline)", sv_base, ann_base, sv_base)]
        for ceil_v in [90, 80, 70]:
            _sv_t, _ = _r(TECH, hold_days=5, vix_min=13.0, thresh=40, atr_max=float(ceil_v))
            _sv_f, _ = _r(FIN, hold_days=7, vix_min=15.0, thresh=42, atr_min=30.0, atr_max=float(ceil_v))
            _sv_c, _ = _r(CONS, hold_days=10, vix_min=13.0, thresh=38, atr_max=float(ceil_v))
            trades_c = []
            for _sv, _tl, _kw in [
                (_sv_t, TECH, {"hold_days": 5, "vix_min": 13.0, "thresh": 40, "atr_max": float(ceil_v)}),
                (
                    _sv_f,
                    FIN,
                    {"hold_days": 7, "vix_min": 15.0, "thresh": 42, "atr_min": 30.0, "atr_max": float(ceil_v)},
                ),
                (_sv_c, CONS, {"hold_days": 10, "vix_min": 13.0, "thresh": 38, "atr_max": float(ceil_v)}),
            ]:
                _, _tdf = _r(_tl, **_kw)
                if not _tdf.empty:
                    trades_c.append(_tdf)
            if trades_c:
                _tdf_c = pd.concat(trades_c, ignore_index=True)
                _sv_c2 = stats(_tdf_c["net_pct"].tolist())
            else:
                _sv_c2 = dict(_EMPTY_STATS)
            atrc_rows.append(_row(f"ATR ceiling ≤ {ceil_v}", _sv_c2, _ann_val(_sv_c2), sv_base))
        print_table(["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann.Sharpe"], atrc_rows)
        best_ceil = min(
            [90, 80, 70],
            key=lambda v: (
                -_ann_val(
                    stats(
                        pd.concat(
                            [
                                r
                                for _, r in [
                                    _r(TECH, hold_days=5, vix_min=13.0, thresh=40, atr_max=float(v)),
                                    _r(FIN, hold_days=7, vix_min=15.0, thresh=42, atr_min=30.0, atr_max=float(v)),
                                    _r(CONS, hold_days=10, vix_min=13.0, thresh=38, atr_max=float(v)),
                                ]
                                if not r.empty
                            ],
                            ignore_index=True,
                        )["net_pct"].tolist()
                    )
                    if True
                    else 0
                )
            ),
        )

        # ── §17b. Return jump filter sweep ────────────────────────────────────
        _section("17b. Return Jump Filter")
        print("\n### §17b. Single-Day Return Jump Filter\n")
        print("> Block entries where 1-day return < threshold (fundamental repricing guard).\n")
        print("> Alpha Architect: filtering return jumps tripled cumulative returns.\n")

        jump_rows = [_row("no filter (baseline)", sv_base, ann_base, sv_base)]
        for thresh_j in [-8.0, -6.0, -5.0]:
            trades_j = []
            for _tl, _kw in [
                (TECH, {"hold_days": 5, "vix_min": 13.0, "thresh": 40, "ret_jump": thresh_j}),
                (FIN, {"hold_days": 7, "vix_min": 15.0, "thresh": 42, "atr_min": 30.0, "ret_jump": thresh_j}),
                (CONS, {"hold_days": 10, "vix_min": 13.0, "thresh": 38, "ret_jump": thresh_j}),
            ]:
                _, _tdf = _r(_tl, **_kw)
                if not _tdf.empty:
                    trades_j.append(_tdf)
            if trades_j:
                _tdf_j = pd.concat(trades_j, ignore_index=True)
                _sv_j = stats(_tdf_j["net_pct"].tolist())
            else:
                _sv_j = dict(_EMPTY_STATS)
            jump_rows.append(_row(f"ret jump < {thresh_j:.0f}%", _sv_j, _ann_val(_sv_j), sv_base))
        print_table(["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann.Sharpe"], jump_rows)

        # ── §17c. Entry delay (T+2) ────────────────────────────────────────────
        _section("17c. Entry Delay T+2")
        print("\n### §17c. Entry Delay — Fill at T+2 Open vs T+1 Open\n")
        print("> Alpha Architect: skipping the 'continuation morning' before reversal begins.\n")

        delay_rows = [_row("T+1 fill (baseline)", sv_base, ann_base, sv_base)]
        trades_d = []
        for _tl, _kw in [
            (TECH, {"hold_days": 5, "vix_min": 13.0, "thresh": 40, "entry_delay": True}),
            (FIN, {"hold_days": 7, "vix_min": 15.0, "thresh": 42, "atr_min": 30.0, "entry_delay": True}),
            (CONS, {"hold_days": 10, "vix_min": 13.0, "thresh": 38, "entry_delay": True}),
        ]:
            _, _tdf = _r(_tl, **_kw)
            if not _tdf.empty:
                trades_d.append(_tdf)
        if trades_d:
            _tdf_d = pd.concat(trades_d, ignore_index=True)
            _sv_d = stats(_tdf_d["net_pct"].tolist())
        else:
            _sv_d = dict(_EMPTY_STATS)
        delay_rows.append(_row("T+2 fill (1-day skip)", _sv_d, _ann_val(_sv_d), sv_base))
        print_table(["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann.Sharpe"], delay_rows)

        # ── §17d. Best combined ────────────────────────────────────────────────
        _section("17d. Best Combined")
        print("\n### §17d. Best Combined — §15f + All §17 Winners\n")
        print("> Apply whichever §17 gates improved quality, stacked onto §15f base.\n")

        trades_all = []
        for _tl, _kw in [
            (TECH, {"hold_days": 5, "vix_min": 13.0, "thresh": 40, "atr_max": 70.0, "ret_jump": -6.0}),
            (FIN, {"hold_days": 7, "vix_min": 15.0, "thresh": 42, "atr_min": 30.0, "atr_max": 70.0, "ret_jump": -6.0}),
            (CONS, {"hold_days": 10, "vix_min": 13.0, "thresh": 38, "atr_max": 70.0, "ret_jump": -6.0}),
        ]:
            _, _tdf = _r(_tl, **_kw)
            if not _tdf.empty:
                trades_all.append(_tdf)
        if trades_all:
            _tdf_all = pd.concat(trades_all, ignore_index=True)
            _sv_all = stats(_tdf_all["net_pct"].tolist())
        else:
            _sv_all = dict(_EMPTY_STATS)

        print_table(
            ["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann.Sharpe"],
            [
                _row("§15f baseline", sv_base, ann_base, sv_base),
                _row("§15f + ATR≤70 + jump<-6%", _sv_all, _ann_val(_sv_all), sv_base),
            ],
        )
        # ── §17e. IBS + multi-day SMA20 confluence (Pagonidis) ───────────────
        _section("17e. IBS + SMA20 Streak Confluence")
        print("\n### §17e. IBS + Multi-Day SMA20 Confluence Gate\n")
        print("> Pagonidis (2013): IBS<0.15 as the sole MR trigger requires ≥N days below SMA20.")
        print("> When IBS fires on a single bad day without sustained selling, the bounce is weaker.\n")

        ibs_rows = [_row("no IBS streak gate (baseline)", sv_base, ann_base, sv_base)]
        for streak_n in [3, 5, 7]:
            trades_ibs = []
            for _tl, _kw in [
                (TECH, {"hold_days": 5, "vix_min": 13.0, "thresh": 40, "ibs_streak": streak_n}),
                (FIN, {"hold_days": 7, "vix_min": 15.0, "thresh": 42, "atr_min": 30.0, "ibs_streak": streak_n}),
                (CONS, {"hold_days": 10, "vix_min": 13.0, "thresh": 38, "ibs_streak": streak_n}),
            ]:
                _, _tdf = _r(_tl, **_kw)
                if not _tdf.empty:
                    trades_ibs.append(_tdf)
            if trades_ibs:
                _tdf_ibs = pd.concat(trades_ibs, ignore_index=True)
                _sv_ibs = stats(_tdf_ibs["net_pct"].tolist())
            else:
                _sv_ibs = dict(_EMPTY_STATS)
            ibs_rows.append(
                _row(f"IBS sole-trigger needs ≥{streak_n}d below SMA20", _sv_ibs, _ann_val(_sv_ibs), sv_base)
            )
        print_table(["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann.Sharpe"], ibs_rows)

        # ── §17f. All gates combined ───────────────────────────────────────────
        _section("17f. All Gates Combined")
        print("\n### §17f. Full Stack — §15f + ATR≤70 + Jump<−6% + IBS Streak≥5\n")
        print("> Best of all §17 gates stacked onto §15f base.\n")

        trades_full = []
        for _tl, _kw in [
            (TECH, {"hold_days": 5, "vix_min": 13.0, "thresh": 40, "atr_max": 70.0, "ret_jump": -6.0, "ibs_streak": 5}),
            (
                FIN,
                {
                    "hold_days": 7,
                    "vix_min": 15.0,
                    "thresh": 42,
                    "atr_min": 30.0,
                    "atr_max": 70.0,
                    "ret_jump": -6.0,
                    "ibs_streak": 5,
                },
            ),
            (
                CONS,
                {"hold_days": 10, "vix_min": 13.0, "thresh": 38, "atr_max": 70.0, "ret_jump": -6.0, "ibs_streak": 5},
            ),
        ]:
            _, _tdf = _r(_tl, **_kw)
            if not _tdf.empty:
                trades_full.append(_tdf)
        if trades_full:
            _tdf_full = pd.concat(trades_full, ignore_index=True)
            _sv_full = stats(_tdf_full["net_pct"].tolist())
        else:
            _sv_full = dict(_EMPTY_STATS)

        print_table(
            ["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD", "Ann.Sharpe"],
            [
                _row("§15f baseline", sv_base, ann_base, sv_base),
                _row("§15f + ATR≤70 + jump<−6%", _sv_all, _ann_val(_sv_all), sv_base),
                _row("§15f + ATR≤70 + jump<−6% + IBS≥5d", _sv_full, _ann_val(_sv_full), sv_base),
            ],
        )
        print(f"\n*§17 Entry Quality Gate Research · MR=0.1 · §15f base · {END}*")


if __name__ == "__main__":
    main()
