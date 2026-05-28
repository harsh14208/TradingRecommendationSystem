"""
Tier-1 Technical Backtest — Signal.Trade engine rules replayed against
30 years of OHLCV data using only indicators computable from price/volume.

Optimised weight structure (research-driven, 2025 update):
  • Oscillator family  : RSI asymmetric (+28/-18), Stoch extreme-zone, WR, CCI → cap ±25 ×1.0
  • Trend family       : MACD cross+continuation+divergence, EMA8/21+vol, ADX 3-tier → cap ±28 ×0.90
  • Volume family      : OBV align/diverge, surge(>150%), dry-up(<50%)  → cap ±20 ×0.85
  • MA family          : SMA200/50/20+slopes, price z-score, Golden/Death Cross → cap ±28 ×1.0
  • Mean-rev family    : BB+RSI confluence, %B, squeeze breakout          → cap ±18 ×1.0
  Regime layers (4):
    L1 ADX strength  : >40 → trend×1.20 MR×0.10; 25-40 → MR×0.40; <20 → trend×0.30 MR×1.20
    L2 SMA200 price  : bull → suppress bearish MR×0.20
    L3 Quality gate  : ≥2 families must agree (else score×0.50)
    L4 Volume veto   : dry-up volume on BUY → score×0.70 (waived RSI<30)
  BUY threshold : score ≥ 35
  SELL threshold: score ≤ −40
  RVOL gate     : BUY blocked if RVOL < 1.2 (waived when RSI < 30)
  VIX tiers     : BUY blocked >30; marginal BUY (score<45) blocked 25-30; SELL suppressed <15
  SPY trend     : BUY requires SPY>SMA200 (or RSI<30/score≥55); SELL requires SPY<SMA200 or score≤-50
  STLFSI4       : FRED financial stress — hard-blocks BUY >1.5+VIX>30; marginal block >1.0+VIX>25
  Stops/targets : ATR-based, swing style (2×/3× ATR, normal vol)
  Hold period   : max 7 trading days (matches live engine primary horizon)
  Friction      : 0.50% round-trip (matches FRICTION_PCT in calc_tbd_metrics.py)

Run from backend/:
    python scripts/backtest_technicals.py
"""

from __future__ import annotations

import math
import os
import sys
import warnings
from datetime import datetime
from multiprocessing import Pool

import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

# Technical-friendly universe: high-beta trending names.
# Removed 15 systematic underperformers (event-driven pharma, consumer staples,
# range-bound banks, legacy cyclicals) — those sectors respond to fundamentals,
# not technicals, and drag avg return by -0.30% to -0.67% per trade.
# Removed: ABBV, TMO, NKE, TXN, BAC, V, QCOM, AMZN, MRK, PG, COST, PFE, BRK-B, WMT, KO
TICKERS = [
    # ── Mega-cap tech (strong MR on genuine pullbacks) ────────────────────────
    "NVDA",  # AI leader; bounces hard from oversold (Sharpe 0.30 in v5.12)
    "MSFT",  # Enterprise cloud; clean MR (Sharpe 0.35)
    "AAPL",  # Consumer tech; mean-reverts around SMA50
    # GOOGL removed: same underlying as GOOG (Class A vs C) — double-counts Alphabet
    "GOOG",  # Alphabet class C — §18 validated: N=5, WR=80%, Sh=0.81, Ann=0.41
    "META",  # Social; big pullbacks recover within 10 days
    "AMZN",  # Retail/AWS; deep pullbacks → strong bounces (Sharpe 0.44)
    "NFLX",  # Streaming; high-beta with reliable MR bounces (added v5.12)
    "ADBE",  # Creative SaaS; systematic pullbacks after earnings misses (added)
    # ── Semiconductors ───────────────────────────────────────────────────────
    "INTC",  # Legacy semi; highly cyclical MR (Sharpe 0.67, best ticker v5.12)
    "AMD",  # GPU/CPU; re-added — consecutive RSI gate filters the chasing (Sharpe 0.77)
    # MU removed: 30% WR, -1.41% — DRAM cycles too long for 10-day MR hold
    "QCOM",  # Established mobile semi
    # TXN removed: live defensive block (20yr backtest -1.36% avg, 25% WR; analog semi earnings-driven)
    "MRVL",  # Infrastructure semi
    "CSCO",  # Networking; slow but reliable MR
    "LRCX",  # Lam Research — §18 screener PASS: WR 75%, Sh 0.48, N=4
    "CDNS",  # Cadence Design — §18 screener PASS: EDA, very low idiosyncratic risk
    "CRM",  # Salesforce — §18 screener PASS: enterprise SaaS MR
    "CTSH",  # Cognizant — §18 screener PASS: IT services sector MR
    # PANW removed: live defensive block (20yr backtest -2.15% avg; earnings-binary cybersec)
    "NTAP",  # NetApp — §18 screener PASS: storage infrastructure MR
    # GEN removed: live defensive block (20yr backtest -1.76% avg, 0% WR; low liquidity)
    # CPAY removed: live defensive block (20yr backtest -2.01% avg, 0% WR; payments/financial)
    "ROP",  # Roper Technologies — §18 screener PASS: diversified tech
    "TDY",  # Teledyne — §18 screener PASS: defense/industrial tech
    "TEL",  # TE Connectivity — §18 screener PASS: electronic components
    "FIS",  # Fidelity National Info — §18 screener PASS: payment processing
    # ── Financials ───────────────────────────────────────────────────────────
    "JPM",  # Largest US bank; MR around rate expectations
    "WFC",  # Regional/diversified; MR in rate cycle (Sharpe 0.20)
    "BAC",  # Similar MR profile to JPM/WFC (added)
    # GS removed: live defensive block (20yr backtest -1.33% avg; investment bank macro-driven)
    # BLK removed: live defensive block (20yr backtest -0.99% avg; AUM correlated with drawdowns)
    "BX",  # Blackstone — §18 screener PASS: alt-asset manager MR
    # C removed: live defensive block + worst 20yr ticker (-2.53% avg); 2011 reverse split distorts OBV/RVOL
    # MA removed: live defensive block (20yr backtest -1.20% avg; same dynamics as V/already blocked)
    # SCHW removed: live defensive block (20yr backtest -0.98% avg; rate-sensitive MR traps)
    "KKR",  # KKR — §18 screener PASS: alt-asset manager
    "FITB",  # Fifth Third Bancorp — §18 screener PASS: regional bank MR
    "KEY",  # KeyCorp — §18 screener PASS: regional bank MR
    "RF",  # Regions Financial — §18 screener PASS: regional bank MR
    # ── Consumer (staples + discretionary) ───────────────────────────────────
    "HD",  # Home improvement; systematic pullbacks recover (Sharpe 0.37)
    "F",  # Ford; automotive cyclical, high-volume, strong MR bounces (added)
    "COST",  # Warehouse retail; smooth compounder MR
    # SBUX removed: live defensive block (20yr backtest -1.05% avg; operating turnaround cycles)
    # MCD removed: 33.3% WR, -0.36% — too slow for 10-day MR holds
    "TGT",  # Target retail; systematic earnings-driven pullbacks + MR (added)
    # TSLA removed: live defensive block (20yr backtest -1.08% avg, 28.6% WR; narrative/momentum driven)
    "EBAY",  # eBay — §18 screener PASS: marketplace MR on sentiment swings
    "EXPE",  # Expedia — §18 screener PASS: travel recovery MR
    "HLT",  # Hilton — §18 screener PASS: hospitality MR
    "MAR",  # Marriott — §18 screener PASS: hospitality MR
    "LULU",  # Lululemon — §18 screener PASS: premium athletic MR
    "ROST",  # Ross Stores — §18 screener PASS: off-price retail MR
    "TPR",  # Tapestry — §18 screener PASS: luxury goods MR
    "DPZ",  # Domino's Pizza — §18 screener PASS: consumer MR
    "AVY",  # Avery Dennison — §18 screener PASS: materials/consumer MR
    # ── Communication ────────────────────────────────────────────────────────
    "PSKY",  # Paramount Skydance (fmr PARA) — §18 screener PASS: media MR
    # ── §40 OOS promotions ────────────────────────────────────────────────────
    # Promoted from HELD_OUT_TICKERS after positive OOS avg return:
    "LOW",  # Lowe's — OOS WR 62.5%, avg +0.33%; XLY home improvement MR
    "FDX",  # FedEx — OOS WR 66.7%, avg +0.71%; logistics MR on demand cycles
    "MMM",  # 3M — OOS WR 100%, avg +2.12%; industrial compounder (N=5, treat with caution)
    "EMR",  # Emerson Electric — OOS WR 75%, avg +0.47%; automation demand cycles
]

# ── Held-out OOS validation universe — v2: same-sector (§40 redesign) ─────────
# v1 held-out set (LMT, CAT, XOM, UNH, ORLY, NSC + promoted LOW/FDX/MMM/EMR)
# was confounded: 6/10 tickers from XLI/XLV/XLE (blocked sectors in delivery_gates).
# Negative OOS verdict was partly sector-mismatch, not pure curation bias.
#
# v2: draw from the SAME sectors as the main universe (XLK/XLY/XLC/XLB/XLF)
# so the OOS test isolates curation bias from sector effects.
# All tickers: S&P 500 members since ≥2010, never touched in any research.
HELD_OUT_TICKERS = [
    # XLK — Technology (same sector as NVDA/MSFT/AAPL/AMD block)
    "ORCL",  # Oracle — enterprise SaaS/cloud; same cadence as MSFT/CRM
    "AMAT",  # Applied Materials — semi equipment; same cycle as LRCX/KLAC
    "KLAC",  # KLA Corp — semi equipment; peer group to LRCX/AMAT
    "NOW",  # ServiceNow — workflow SaaS; same sector as CRM/ADBE
    # XLY — Consumer Discretionary (same sector as HD/TGT/LULU block)
    "NKE",  # Nike — athletic retail; pullbacks on guidance misses → bounce
    "DHI",  # D.R. Horton — homebuilder; rate-driven MR cycles
    "APTV",  # Aptiv — auto tech; cyclical demand-driven MR
    # XLC — Communication (same sector as GOOG/META/NFLX)
    "CHTR",  # Charter Communications — cable; sentiment-driven MR
    "TTWO",  # Take-Two Interactive — gaming; earnings-driven MR
    # XLF — Financials (same sector as JPM/BAC/BX block)
    "MS",  # Morgan Stanley — investment bank; rate-cycle MR
]

# ── Sector map: ticker → GICS sector ETF ─────────────────────────────────────
# Used for delivery-gates-aligned sector filter (§10).
# Blocked sectors in live engine: XLI, XLV, XLE, XLRE, XLU.
TICKER_TO_SECTOR: dict[str, str] = {
    # XLK — Technology
    "NVDA": "XLK",
    "MSFT": "XLK",
    "AAPL": "XLK",
    "ADBE": "XLK",
    "INTC": "XLK",
    "AMD": "XLK",
    "QCOM": "XLK",
    "MRVL": "XLK",
    "CSCO": "XLK",
    "LRCX": "XLK",
    "CDNS": "XLK",
    "CRM": "XLK",
    "CTSH": "XLK",
    "NTAP": "XLK",
    "FIS": "XLK",
    # XLI — Industrials (blocked in delivery_gates)
    "ROP": "XLI",
    "TDY": "XLI",
    "TEL": "XLI",
    "FDX": "XLI",
    "MMM": "XLI",
    "EMR": "XLI",
    # XLC — Communication Services
    "GOOG": "XLC",
    "META": "XLC",
    "NFLX": "XLC",
    "EXPE": "XLC",
    "PSKY": "XLC",
    # XLY — Consumer Discretionary
    "AMZN": "XLY",
    "HD": "XLY",
    "F": "XLY",
    "COST": "XLY",
    "TGT": "XLY",
    "EBAY": "XLY",
    "HLT": "XLY",
    "MAR": "XLY",
    "LULU": "XLY",
    "ROST": "XLY",
    "TPR": "XLY",
    "DPZ": "XLY",
    "LOW": "XLY",
    # XLB — Materials
    "AVY": "XLB",
    # XLF — Financials
    "JPM": "XLF",
    "WFC": "XLF",
    "BAC": "XLF",
    "BX": "XLF",
    "KKR": "XLF",
    "FITB": "XLF",
    "KEY": "XLF",
    "RF": "XLF",
}
_BLOCKED_SECTORS = {"XLI", "XLV", "XLE", "XLRE", "XLU"}

START = "2003-01-01"  # extended from 2006 — captures Pre-GFC Bull fully (was only 2006-07)
END = datetime.today().strftime("%Y-%m-%d")
TRADE_FROM = END  # no filter by default — override for short-window runs
HOLD_DAYS = 10  # v5.12 sweep-optimal: HOLD=10 with all quality gates.
# MR bounces on high-quality oversold setups take 7-10
# days to fully play out; 10-day hold captures the full move.
MAX_LOSS_DAYS = 4  # Scaled with HOLD_DAYS: cut losers on bar 4 (40% through hold).
FRICTION_PCT = 0.50  # 0.25% entry + 0.25% exit — matches calc_tbd_metrics.py live friction.
# Audit finding: was 0.20% (mismatch), overstating per-trade EV by ~32%.
# v5.12 sweep-optimal (45-combination grid, all 7 gates active, 2026-05-18):
# Best: BUY_THRESH=40, MAX=∞, HOLD=10 → Sharpe 0.165, WR 51.9%, avg +0.61%
# v7.1 score-band analysis (2026-05-28): band 40-50 → WR 56.2%, avg +0.26%, Sharpe 0.07
#                                         band 50-60 → WR 64.7%, avg +0.87%, Sharpe 0.21
# Raised to 50: halves trade count, ~doubles avg return. 40-50 band not worth the risk.
BUY_THRESH = 50
BUY_THRESH_MAX = 999  # effectively no ceiling
SELL_THRESH = -100  # SELLs disabled. §32 validation (2026-05-26): −45 threshold produced
# N=1354 SELLs at WR=33.1%, Avg=−0.43%, Sharpe=−0.08, MaxDD=−28%.
# Adding SELLs collapses overall Sharpe 0.20→−0.03. Live SELL edge
# (60.8% raw WR) is entirely alt-data driven — absent on OHLCV alone.
POSITION_SIZE = 0.05  # 5% of capital per trade (for drawdown sim)

# ── Mean-Reversion-Only mode — default for primary run ───────────────────────
# §9 analysis showed MR-only is strictly better on every metric:
#   WR +1.3pp, avg return +75% (+0.12%→+0.21%), Sharpe +0.03, MaxDD −47%.
#   Monte Carlo p5 flipped positive — edge becomes statistically robust.
# Main run (§1-§8) uses MR gate. §9 shows full-signal comparison.
BACKTEST_MR_DEFAULT = True

# ── New gate parameters ───────────────────────────────────────────────────────
EARNINGS_BLACKOUT_DAYS = 5  # Block entries within 5 cal days of earnings
MIN_AVG_DOLLAR_VOL = 50_000_000  # $50M avg daily dollar volume minimum
DEEP_BEAR_VIX = 28  # VIX threshold for stricter bear-market RSI gate
DEEP_BEAR_SMA200_RATIO = 0.95  # SPY must be <95% of SMA200 to trigger deep-bear gate
DEEP_BEAR_RSI_MAX = 35  # In deep bear, only accept RSI < 35 (extreme oversold)

# MR thresholds — tightened from original §9 values for higher-quality entries.
# §9 showed the 40-50 score band with ANY MR condition hit Sharpe 0.10.
# Tighter thresholds concentrate on the high-conviction oversold setups that
# drove the GFC Bear Sharpe of 0.41 and NVDA's swing from −0.42% to +0.60%.
MR_RSI_CEIL = 42  # was 48 — stock must be clearly approaching oversold
MR_BB_CEIL = 0.22  # was 0.30 — near lower Bollinger Band (not just below midpoint)
MR_IBS_CEIL = 0.15  # was 0.20 — closed within 15% of the day's low (weak close)
MR_VWAP_FLOOR = -0.75  # was −0.5 — must be meaningfully below rolling VWAP
# Extended MR triggers — orthogonal to RSI/BB/IBS/VWAP, add new entry classes:
MR_GAP_FLOOR = -1.5  # gap down ≥1.5% = panic sell overshoots, post-gap MR bounce (65-70% fill rate)
MR_STREAK_CEIL = -6  # 6+ consecutive closes below SMA20 = sustained weakness exhaustion

# Momentum gate parameters (dual_gate mode — parallel to MR gate)
# When dual_gate=True, entries are allowed if MR gate OR momentum gate passes.
# Momentum gate targets trending breakout setups: RSI in healthy trend zone,
# MACD accelerating, OBV positive (accumulation), above SMA50, outperforming SPY.
MOM_RSI_FLOOR = 50  # RSI above neutral (trending, not mean-reverting)
MOM_RSI_CEIL = 68  # RSI below overbought (room left to run)

REGIMES = [
    ("Dot-com Bull", "1996-01-01", "2000-03-10"),
    ("Dot-com Crash", "2000-03-11", "2002-10-09"),
    ("Pre-GFC Bull", "2002-10-10", "2007-10-08"),
    ("GFC Bear", "2007-10-09", "2009-03-09"),
    ("Post-GFC Bull", "2009-03-10", "2019-12-31"),
    ("COVID Crash", "2020-02-19", "2020-03-23"),
    ("COVID Recovery", "2020-03-24", "2021-12-31"),
    ("Rate-Hike Bear", "2022-01-01", "2022-12-31"),
    ("AI Rally", "2023-01-01", "2024-12-31"),
    ("Current (2025+)", "2025-01-01", END),
]


# ─────────────────────────────────────────────────────────────────────────────
# Indicator computation (pure pandas / numpy — no external TA library)
# ─────────────────────────────────────────────────────────────────────────────


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add all indicator columns to df in-place. Returns df.

    Must align with backend/services/technicals.py field names used by
    signal_engine.py's technical scoring rules.
    """
    c, h, l, v = df["Close"], df["High"], df["Low"], df["Volume"]

    # ── RSI(14) ──────────────────────────────────────────────────────────────
    delta = c.diff()
    gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
    df.loc[:, "rsi"] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))

    # ── Stochastic %K/%D (14, 3) ─────────────────────────────────────────────
    lo14 = l.rolling(14).min()
    hi14 = h.rolling(14).max()
    stoch_k = 100 * (c - lo14) / (hi14 - lo14).replace(0, np.nan)
    df.loc[:, "stoch_k"] = stoch_k
    df.loc[:, "stoch_d"] = stoch_k.rolling(3).mean()
    df.loc[:, "stoch_k_p"] = stoch_k.shift(1)
    df.loc[:, "stoch_d_p"] = df["stoch_d"].shift(1)

    # ── Williams %R(14) ──────────────────────────────────────────────────────
    df.loc[:, "wr"] = -100 * (hi14 - c) / (hi14 - lo14).replace(0, np.nan)

    # ── CCI(20) ──────────────────────────────────────────────────────────────
    tp = (h + l + c) / 3
    cci_ma = tp.rolling(20).mean()
    cci_mad = tp.rolling(20).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    df.loc[:, "cci"] = (tp - cci_ma) / (0.015 * cci_mad.replace(0, np.nan))

    # ── MACD(12, 26, 9) ──────────────────────────────────────────────────────
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    sig_line = macd_line.ewm(span=9, adjust=False).mean()
    df.loc[:, "macd_hist"] = macd_line - sig_line
    df.loc[:, "macd_hist_p"] = df["macd_hist"].shift(1)

    # ── MACD Divergence (5-bar lookback) ─────────────────────────────────────
    # Bullish: price declining over 5 bars but MACD hist rising (momentum diverging up)
    # Bearish: price rising over 5 bars but MACD hist falling (momentum diverging down)
    c_5ago = c.shift(5)
    hist_5ago = df["macd_hist"].shift(5)
    df.loc[:, "macd_bull_div"] = (
        (c < c_5ago) & (df["macd_hist"] > hist_5ago) & (df["macd_hist"] < 0) & (c <= c.rolling(10).min() * 1.02)
    ).astype(float)
    df.loc[:, "macd_bear_div"] = (
        (c > c_5ago) & (df["macd_hist"] < hist_5ago) & (df["macd_hist"] > 0) & (c >= c.rolling(10).max() * 0.98)
    ).astype(float)

    # ── EMA(8) / EMA(21) ─────────────────────────────────────────────────────
    df.loc[:, "ema8"] = c.ewm(span=8, adjust=False).mean()
    df.loc[:, "ema21"] = c.ewm(span=21, adjust=False).mean()
    df.loc[:, "ema8_p"] = df["ema8"].shift(1)
    df.loc[:, "ema21_p"] = df["ema21"].shift(1)

    # ── OBV (On-Balance Volume) + divergence ─────────────────────────────────
    direction = np.sign(c.diff()).fillna(0)
    obv = (v * direction).cumsum()
    df.loc[:, "obv"] = obv
    df.loc[:, "obv_ma20"] = obv.rolling(20).mean()
    df.loc[:, "obv_above"] = (obv > df["obv_ma20"]).astype(float)
    df.loc[:, "obv_slope"] = obv.diff()
    # Accumulation: price down 5-bar but OBV up; Distribution: price up but OBV down
    df.loc[:, "obv_bull_div"] = ((c < c.shift(5)) & (obv > obv.shift(5))).astype(float)
    df.loc[:, "obv_bear_div"] = ((c > c.shift(5)) & (obv < obv.shift(5))).astype(float)

    # ── ATR(14) ───────────────────────────────────────────────────────────────
    tr = pd.concat(
        [
            h - l,
            (h - c.shift()).abs(),
            (l - c.shift()).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df.loc[:, "atr"] = tr.ewm(com=13, adjust=False).mean()

    # ── ADX(14) with +DI / -DI ───────────────────────────────────────────────
    up_move = h - h.shift(1)
    dn_move = l.shift(1) - l
    plus_dm = np.where((up_move > dn_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((dn_move > up_move) & (dn_move > 0), dn_move, 0.0)
    atr14 = df["atr"]
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(com=13, adjust=False).mean() / atr14.replace(0, np.nan)
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(com=13, adjust=False).mean() / atr14.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    df.loc[:, "adx"] = dx.ewm(com=13, adjust=False).mean()
    df.loc[:, "plus_di"] = plus_di
    df.loc[:, "minus_di"] = minus_di

    # ── SMA(20), SMA(50), SMA(200), EMA(200) + 5-bar slopes ──────────────────
    df.loc[:, "sma20"] = c.rolling(20).mean()
    df.loc[:, "sma50"] = c.rolling(50).mean()
    df.loc[:, "sma200"] = c.rolling(200).mean()
    df.loc[:, "ema200"] = c.ewm(span=200, adjust=False).mean()
    df.loc[:, "sma20_slope"] = (df["sma20"] - df["sma20"].shift(5)) / df["sma20"].shift(5).replace(0, np.nan)
    df.loc[:, "sma50_slope"] = (df["sma50"] - df["sma50"].shift(5)) / df["sma50"].shift(5).replace(0, np.nan)
    df.loc[:, "sma200_slope"] = (df["sma200"] - df["sma200"].shift(5)) / df["sma200"].shift(5).replace(0, np.nan)

    # ── Bollinger Bands(20, 2) + %B + Squeeze ────────────────────────────────
    bb_mid = c.rolling(20).mean()
    bb_std = c.rolling(20).std(ddof=1) * 2
    df.loc[:, "bb_upper"] = bb_mid + bb_std
    df.loc[:, "bb_lower"] = bb_mid - bb_std
    bb_range = (df["bb_upper"] - df["bb_lower"]).replace(0, np.nan)
    df.loc[:, "bb_pct_b"] = (c - df["bb_lower"]) / bb_range  # 0=lower, 1=upper
    # BB Squeeze: BB inside Keltner Channel (EMA20 ± 1.5×ATR)
    ema20 = c.ewm(span=20, adjust=False).mean()
    kc_upper = ema20 + 1.5 * df["atr"]
    kc_lower = ema20 - 1.5 * df["atr"]
    df.loc[:, "bb_squeeze"] = ((df["bb_upper"] < kc_upper) & (df["bb_lower"] > kc_lower)).astype(float)
    squeeze_p = df["bb_squeeze"].shift(1)
    df.loc[:, "squeeze_breakout_up"] = ((squeeze_p == 1) & (df["bb_squeeze"] == 0) & (c > bb_mid)).astype(float)
    df.loc[:, "squeeze_breakout_down"] = ((squeeze_p == 1) & (df["bb_squeeze"] == 0) & (c < bb_mid)).astype(float)

    # ── Price Z-score (20-day rolling) ───────────────────────────────────────
    roll_mean = c.rolling(20).mean()
    roll_std = c.rolling(20).std(ddof=1)
    df.loc[:, "price_zscore"] = (c - roll_mean) / roll_std.replace(0, np.nan)

    # ── RVOL + surge/dry-up flags ─────────────────────────────────────────────
    # Align with signal_engine: RVOL uses today's volume vs mean of prior 20 sessions (excluding today).
    avg_prior20 = v.rolling(21).mean().shift(1)
    df.loc[:, "rvol"] = v / avg_prior20.replace(0, np.nan)
    df.loc[:, "vol_surge"] = (df["rvol"] > 1.5).astype(float)  # >150% avg volume
    df.loc[:, "vol_dryup"] = (df["rvol"] < 0.5).astype(float)  # <50% avg volume

    # ── Price change helpers for direction-aware buckets ────────────────
    # Used by:
    #   • ATR expansion bullish/bearish direction scoring
    #   • Stealth accumulation (down day detection)
    # Track both absolute and percent change.
    c_prev = c.shift(1)
    df.loc[:, "change"] = c - c_prev
    df.loc[:, "change_pct"] = c.pct_change() * 100.0

    # ── VWAP cross helpers (prev close vs prev VWAP) ─────────────────────
    # Used to avoid meaningless comparisons between different VWAP anchors.
    df.loc[:, "Close_prev"] = c_prev

    # vwap_20_prev will be created after vwap_20 is computed.

    # ── IBS — (close − low) / (high − low) ────────────────────────────────────

    rng_ibs = (h - l).replace(0, np.nan)
    df.loc[:, "ibs"] = (c - l) / rng_ibs

    # ── Rolling 20-day VWAP + σ bands around price-around-VWAP std ─────────
    # NOTE: In signal scoring, VWAP-cross logic should compare:
    #   prev close vs prev VWAP (not prev VWAP value vs today close).
    # We therefore compute vwap_pct for the same day anchor and shift it.
    tp = (h + l + c) / 3.0
    n_vwap = min(20, len(df))
    cum_tpv = (tp * v).rolling(n_vwap).sum()
    cum_vol = v.rolling(n_vwap).sum()
    vwap_s = cum_tpv / cum_vol.replace(0, np.nan)

    df.loc[:, "vwap_20"] = vwap_s
    df.loc[:, "vwap_pct"] = (c - vwap_s) / vwap_s.replace(0, np.nan) * 100.0
    # Correct meaning: prev day's (prev close - prev VWAP)/prev VWAP.
    df.loc[:, "vwap_pct_prev"] = df["vwap_pct"].shift(1)
    df.loc[:, "vwap_slope_pos"] = (vwap_s > vwap_s.shift(3)).astype("boolean")

    # Keep backward compatibility: some older scoring paths expect this name.
    # Only if vwap_20 exists (it should, but guard to avoid KeyError).
    if "vwap_20" in df.columns:
        df.loc[:, "vwap_20_prev"] = df["vwap_20"].shift(1)
    else:
        df.loc[:, "vwap_20_prev"] = np.nan

    vwap_resid = c - vwap_s

    vwap_std_s = vwap_resid.rolling(n_vwap).std(ddof=1)
    df.loc[:, "vwap_band1_upper"] = vwap_s + vwap_std_s
    df.loc[:, "vwap_band1_lower"] = vwap_s - vwap_std_s
    df.loc[:, "vwap_band2_upper"] = vwap_s + 2.0 * vwap_std_s
    df.loc[:, "vwap_band2_lower"] = vwap_s - 2.0 * vwap_std_s

    # ── ATR expansion / contraction + pct_rank (vectorized) ─────────────────
    atr_s = df["atr"]
    atr_up = atr_s > atr_s.shift(1)
    atr_dn = atr_s < atr_s.shift(1)
    df.loc[:, "atr_expand_bars"] = (atr_up.groupby((~atr_up).cumsum()).cumcount() + 1).where(atr_up, 0).astype(float)
    df.loc[:, "atr_contract_bars"] = (atr_dn.groupby((~atr_dn).cumsum()).cumcount() + 1).where(atr_dn, 0).astype(float)
    # Fast percentile rank via rolling quantile interpolation (no look-ahead)
    atr_90 = atr_s.rolling(252, min_periods=30).quantile(0.90)
    atr_10 = atr_s.rolling(252, min_periods=30).quantile(0.10)
    df.loc[:, "atr_pct_rank"] = ((atr_s - atr_10) / (atr_90 - atr_10).replace(0, np.nan) * 80 + 10).clip(0, 100)

    # ── Volume Profile (vectorized): POC≈VWAP, VAH/VAL≈rolling high/low ────────
    n_vp = 20
    df.loc[:, "vp_poc"] = df["vwap_20"]
    df.loc[:, "vp_vah"] = df["High"].rolling(n_vp).max()
    df.loc[:, "vp_val"] = df["Low"].rolling(n_vp).min()

    # ── Market Structure (vectorized): break-of-structure / MSS ──────────────
    roll_high = df["High"].shift(1).rolling(20).max()
    roll_low = df["Low"].shift(1).rolling(20).min()
    ms = pd.Series(None, index=df.index, dtype=object)
    ms.loc[df["Close"] < roll_low] = "bos_bear"
    ms.loc[df["Close"] > roll_high] = "bos_bull"
    below_50 = df["Close"].shift(5) < df["sma50"].shift(5)
    ms.loc[(df["Close"] > roll_high) & below_50] = "mss_bull"
    df.loc[:, "market_struct"] = ms
    df.loc[:, "ms_level"] = np.where(ms == "bos_bull", roll_high, np.where(ms == "bos_bear", roll_low, np.nan))

    # ── Gap percentage (overnight gap vs prior close) ─────────────────────────
    # Audit fix: gap_pct was referenced in simulate_ticker MR gate (MR_GAP_FLOOR=-1.5%)
    # but never computed — the trigger was silently dead. Gap-down MR setups (panic
    # overshoot fills) are a valid orthogonal entry class; now properly computed.
    df.loc[:, "gap_pct"] = (df["Open"] - c.shift(1)) / c.shift(1).replace(0, np.nan) * 100

    # ── Consecutive closes below SMA20 (streak counter, negative = below) ────
    # Audit fix: close_streak was referenced in simulate_ticker MR gate (MR_STREAK_CEIL=-6)
    # and IBS+streak confluence gate but never computed — both triggers were silently dead.
    # Negative value = number of consecutive closes below SMA20 (e.g. -7 = 7 days below).
    _below_sma20 = c < df["sma20"]
    _grp = (~_below_sma20).cumsum()
    _run = _below_sma20.groupby(_grp).cumcount() + 1
    df.loc[:, "close_streak"] = -_run.where(_below_sma20, other=0).astype(float)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Scoring — exact replication of signal_scoring.py + signal_engine.py
# ─────────────────────────────────────────────────────────────────────────────


def score_row(r: pd.Series) -> float:
    """
    Compute the technical score using the optimised research weight structure.
    All 5 families + 4 regime layers. Technical-only (no news/options/fundamentals).
    """
    price = float(r["Close"])
    rsi_val = float(r["rsi"]) if pd.notna(r.get("rsi")) else 50.0
    atr = float(r["atr"]) if pd.notna(r.get("atr")) else 0.0
    atr_pct = atr / price if price > 0 else 0.02
    is_low_atr = atr_pct < 0.010

    adx_val = float(r.get("adx")) if pd.notna(r.get("adx")) else 0.0
    sma200_v = float(r.get("sma200")) if pd.notna(r.get("sma200")) else None
    rvol_now = float(r.get("rvol")) if pd.notna(r.get("rvol")) else 1.0
    change_pct = float(r.get("change_pct", 0.0)) if pd.notna(r.get("change_pct")) else 0.0

    # ── Oscillator family (cap ±25, ×1.0) ─────────────────────────────────────
    # Asymmetric: oversold bounces more reliable than overbought reversions
    osc = 0.0

    if pd.notna(r.get("rsi")):
        if rsi_val < 25:
            osc += 28  # deep oversold — highest-probability bounce
        elif rsi_val < 35:
            osc += 16
        elif rsi_val > 75:
            osc -= 18  # asymmetric penalty
        elif rsi_val > 65:
            osc -= 10

    sk, sd = r.get("stoch_k"), r.get("stoch_d")
    sk_p, sd_p = r.get("stoch_k_p"), r.get("stoch_d_p")
    if all(pd.notna(x) for x in (sk, sd, sk_p, sd_p)):
        sk, sd, sk_p, sd_p = float(sk), float(sd), float(sk_p), float(sd_p)
        cross_up = (sk > sd) and (sk_p <= sd_p)
        cross_down = (sk < sd) and (sk_p >= sd_p)
        if sk < 20 and sd < 20 and cross_up:
            osc += 18  # both in extreme zone
        elif sk > 80 and sd > 80 and cross_down:
            osc -= 14  # asymmetric
        elif sk < 20 and cross_up:
            osc += 10
        elif sk > 80 and cross_down:
            osc -= 8
        elif sk < 25:
            osc += 5
        elif sk > 75:
            osc -= 4

    wr = r.get("wr")
    if pd.notna(wr):
        wr = float(wr)
        if wr <= -85:
            osc += 10  # only extreme readings
        elif wr >= -15:
            osc -= 8

    cci = r.get("cci")
    if pd.notna(cci):
        cci = float(cci)
        if cci < -200:
            osc += 14
        elif cci < -150:
            osc += 8
        elif cci < -100:
            osc += 3
        elif cci > 200:
            osc -= 12
        elif cci > 150:
            osc -= 7
        elif cci > 100:
            osc -= 3

    osc = max(-25, min(25, osc))

    # ── Trend family (cap ±28, ×0.90) ─────────────────────────────────────────
    # Continuation > crossover; divergence is highest-probability signal
    trend_score = 0.0

    hist = r.get("macd_hist")
    hist_p = r.get("macd_hist_p")
    if pd.notna(hist) and pd.notna(hist_p):
        hist, hist_p = float(hist), float(hist_p)
        cross_up = (hist > 0) and (hist_p <= 0)
        cross_down = (hist < 0) and (hist_p >= 0)
        hist_rising = hist > hist_p
        if cross_up and hist_rising:
            trend_score += 18
        elif cross_down and not hist_rising:
            trend_score -= 18
        elif cross_up:
            trend_score += 12
        elif cross_down:
            trend_score -= 12
        elif hist > 0 and hist_rising:
            trend_score += 16  # positive accel > cross
        elif hist < 0 and not hist_rising:
            trend_score -= 16
        elif hist > 0:
            trend_score += 6
        elif hist < 0:
            trend_score -= 6

    if pd.notna(r.get("macd_bull_div")) and float(r.get("macd_bull_div")) == 1.0:
        trend_score += 20
    if pd.notna(r.get("macd_bear_div")) and float(r.get("macd_bear_div")) == 1.0:
        trend_score -= 20

    e8, e21, e8p, e21p = r.get("ema8"), r.get("ema21"), r.get("ema8_p"), r.get("ema21_p")
    if all(pd.notna(x) for x in (e8, e21, e8p, e21p)):
        e8, e21, e8p, e21p = float(e8), float(e21), float(e8p), float(e21p)
        vol_confirm = rvol_now > 1.2
        if (e8 > e21) and (e8p <= e21p):
            trend_score += 14 if vol_confirm else 8
        elif (e8 < e21) and (e8p >= e21p):
            trend_score -= 14 if vol_confirm else 8
        elif e8 > e21:
            trend_score += 4
        else:
            trend_score -= 4

    # ADX 3-tier: eliminate weak trend signals, amplify strong ones
    pdi, mdi = r.get("plus_di"), r.get("minus_di")
    if pd.notna(pdi) and pd.notna(mdi):
        pdi, mdi = float(pdi), float(mdi)
        if adx_val > 40:
            trend_score += 18 if pdi > mdi else -18
        elif adx_val > 25:
            trend_score += 10 if pdi > mdi else -10
        # ADX < 20: no contribution — crossovers whipsaw in chop

    # ATR expansion: sustained expansion signals real trend strength
    atr_expand = r.get("atr_expand_bars")
    if atr_expand is not None and pd.notna(atr_expand):
        exp = float(atr_expand)
        if exp >= 5:
            trend_score += 16 if change_pct >= 0 else -10
        elif exp >= 3:
            trend_score += 10 if change_pct >= 0 else -10

    # Market structure BOS/MSS
    ms_struct = r.get("market_struct")
    if ms_struct is not None and pd.notna(ms_struct):
        if ms_struct == "bos_bull":
            trend_score += 12
        elif ms_struct == "bos_bear":
            trend_score -= 12
        elif ms_struct == "mss_bull":
            trend_score += 16

    trend_score = max(-28, min(28, trend_score))

    # RSI suppression of trend signals (strengthened vs old 0.50 flat)
    if trend_score > 0 and rsi_val > 75:
        trend_score *= 0.30
    elif trend_score > 0 and rsi_val > 65:
        trend_score *= 0.55
    elif trend_score < 0 and rsi_val < 25:
        trend_score *= 0.30
    elif trend_score < 0 and rsi_val < 35:
        trend_score *= 0.55

    # ── Volume family (cap ±20, ×0.85) ────────────────────────────────────────
    volume_score = 0.0
    obv_above = r.get("obv_above")
    obv_slope = r.get("obv_slope")
    sma20_v = float(r.get("sma20")) if pd.notna(r.get("sma20")) else None
    vol_surge_f = pd.notna(r.get("vol_surge")) and float(r.get("vol_surge")) == 1.0
    vol_dryup_f = pd.notna(r.get("vol_dryup")) and float(r.get("vol_dryup")) == 1.0
    obv_bull_div = pd.notna(r.get("obv_bull_div")) and float(r.get("obv_bull_div")) == 1.0
    obv_bear_div = pd.notna(r.get("obv_bear_div")) and float(r.get("obv_bear_div")) == 1.0

    if pd.notna(obv_above) and pd.notna(obv_slope):
        obv_sl = float(obv_slope)
        if float(obv_above) and obv_sl > 0:
            volume_score += 16 if osc > 15 else 8
        elif not float(obv_above) and obv_sl < 0:
            volume_score += -16 if osc < -15 else -8

    if vol_surge_f and pd.notna(obv_slope):
        obv_sl = float(obv_slope)
        if obv_sl > 0 and sma20_v is not None and price > sma20_v:
            volume_score += 14
        elif obv_sl < 0 and sma20_v is not None and price < sma20_v:
            volume_score -= 14

    if vol_dryup_f:
        volume_score -= 8
    if obv_bull_div:
        volume_score += 12  # accumulation
    if obv_bear_div:
        volume_score -= 10  # distribution

    # Stealth accumulation: institutional buying the dip (RSI<40, RVOL≥2, down day)
    if rsi_val < 40 and rvol_now >= 2.0 and change_pct < 0:
        volume_score += 10

    # Direction-aware surge: extreme RVOL confirms breakout/breakdown
    if rvol_now >= 3.0:
        volume_score += 10 if change_pct >= 0 else -10

    volume_score = max(-20, min(20, volume_score))

    # ── MA family (cap ±28, ×1.0) ──────────────────────────────────────────────
    # 50-day more actionable than 200-day; slopes add conviction
    ma_score = 0.0
    sma50 = r.get("sma50")
    sma200 = r.get("sma200")
    ema200 = r.get("ema200")
    sma200_sl = float(r.get("sma200_slope")) if pd.notna(r.get("sma200_slope")) else 0.0
    sma50_sl = float(r.get("sma50_slope")) if pd.notna(r.get("sma50_slope")) else 0.0
    sma20_sl = float(r.get("sma20_slope")) if pd.notna(r.get("sma20_slope")) else 0.0
    zscore = float(r.get("price_zscore")) if pd.notna(r.get("price_zscore")) else 0.0

    if pd.notna(sma200):
        s200 = float(sma200)
        if price > s200 * 1.02 and sma200_sl > 0:
            ma_score += 18
        elif price > s200 * 1.01:
            ma_score += 12
        elif price < s200 * 0.98 and sma200_sl < 0:
            ma_score -= 18
        elif price < s200 * 0.99:
            ma_score -= 12

    if pd.notna(sma50):
        s50 = float(sma50)
        if price > s50 and sma50_sl > 0:
            ma_score += 16
        elif price > s50:
            ma_score += 8
        elif price < s50 and sma50_sl < 0:
            ma_score -= 14
        else:
            ma_score -= 6

    if sma20_v is not None:
        if price > sma20_v and sma20_sl > 0:
            ma_score += 12
        elif price < sma20_v and sma20_sl < 0:
            ma_score -= 8

    # Price z-score: statistical mean reversion from extended moves
    if zscore < -2.0:
        ma_score += 14
    elif zscore < -1.5:
        ma_score += 7
    elif zscore > 2.0:
        ma_score -= 12
    elif zscore > 1.5:
        ma_score -= 6

    # Golden / Death Cross — weight reduced (late signal)
    if pd.notna(sma50) and pd.notna(sma200):
        s50, s200 = float(sma50), float(sma200)
        if s50 > s200 * 1.005:
            ma_score += 10
        elif s50 < s200 * 0.995:
            ma_score -= 10

    if pd.notna(ema200) and pd.notna(sma200):
        e200, s200 = float(ema200), float(sma200)
        if price > e200 and price > s200:
            ma_score += 3
        elif price < e200 and price < s200:
            ma_score -= 3

    # VWAP: price position relative to rolling VWAP + slope
    vwap_pct = r.get("vwap_pct")
    vwap_slope_pos = r.get("vwap_slope_pos")
    if pd.notna(vwap_pct):
        if pd.notna(vwap_slope_pos):
            if bool(vwap_slope_pos) and float(vwap_pct) > 0:
                ma_score += 6
            elif (not bool(vwap_slope_pos)) and float(vwap_pct) < 0:
                ma_score -= 5
        vwap_20 = r.get("vwap_20")
        prev_close = float(r.get("Close_prev")) if pd.notna(r.get("Close_prev")) else price
        prev_vwap = float(r.get("vwap_20_prev")) if pd.notna(r.get("vwap_20_prev")) else price
        if pd.notna(vwap_20) and rvol_now >= 2.0:
            if prev_close < prev_vwap and price >= float(vwap_20):
                ma_score += 12
            elif prev_close > prev_vwap and price <= float(vwap_20):
                ma_score -= 14

    # Volume Profile: price vs VAH/VAL
    vp_poc = r.get("vp_poc")
    vp_vah = r.get("vp_vah")
    vp_val = r.get("vp_val")
    if all(pd.notna(x) for x in (vp_poc, vp_vah, vp_val)):
        if rvol_now >= 1.5:
            if price > float(vp_vah):
                ma_score += 16
            elif price < float(vp_val):
                ma_score -= 14
        poc_dist = abs(price - float(vp_poc)) / float(vp_poc) * 100 if float(vp_poc) > 0 else 99
        if poc_dist <= 0.25 and adx_val < 20:
            ma_score += 8

    ma_score = max(-28, min(28, ma_score))

    # ── Mean-Reversion family (cap ±18, ×1.0) ─────────────────────────────────
    # BB+RSI confluence achieves 65%+ WR vs 50% alone; cap raised ±8→±18
    mean_rev_score = 0.0
    bb_pct_b = float(r.get("bb_pct_b", 0.5)) if pd.notna(r.get("bb_pct_b")) else 0.5
    squeeze_up = pd.notna(r.get("squeeze_breakout_up")) and float(r.get("squeeze_breakout_up")) == 1.0
    squeeze_down = pd.notna(r.get("squeeze_breakout_down")) and float(r.get("squeeze_breakout_down")) == 1.0

    # BB + RSI confluence
    if bb_pct_b < 0.05:
        if rsi_val < 35:
            mean_rev_score += 18
        elif rsi_val < 45:
            mean_rev_score += 12
        else:
            mean_rev_score += 6
    elif bb_pct_b < 0.15:
        if rsi_val < 35:
            mean_rev_score += 10
        elif rsi_val < 45:
            mean_rev_score += 5

    if bb_pct_b > 0.95:
        if rsi_val > 65:
            mean_rev_score -= 14
        elif rsi_val > 55:
            mean_rev_score -= 8
        else:
            mean_rev_score -= 4
    elif bb_pct_b > 0.85:
        if rsi_val > 65:
            mean_rev_score -= 8
        elif rsi_val > 55:
            mean_rev_score -= 4

    if squeeze_up:
        mean_rev_score += 16
    if squeeze_down:
        mean_rev_score -= 16

    if adx_val < 20 and bb_pct_b < 0.15:
        mean_rev_score += 6  # ranging market bonus

    # IBS extremes (intrabar positioning)
    ibs = r.get("ibs")
    if pd.notna(ibs):
        ibs = float(ibs)
        if ibs < 0.05:
            mean_rev_score += 15
        elif ibs < 0.10:
            mean_rev_score += 8
        elif ibs > 0.90:
            mean_rev_score -= 10

    # VWAP band extremes
    b2u = r.get("vwap_band2_upper")
    b2l = r.get("vwap_band2_lower")
    if pd.notna(b2u) and price >= float(b2u):
        mean_rev_score -= 14
    if pd.notna(b2l) and price <= float(b2l):
        mean_rev_score += 14

    # ATR contraction: coiling environment favours mean reversion
    atr_contract = r.get("atr_contract_bars")
    if pd.notna(atr_contract) and float(atr_contract) >= 5:
        mean_rev_score += 6
    atr_pct_rank = r.get("atr_pct_rank")
    if pd.notna(atr_pct_rank):
        if float(atr_pct_rank) > 90:
            mean_rev_score *= 0.5
        elif float(atr_pct_rank) < 10:
            mean_rev_score *= 1.4

    mean_rev_score = max(-18, min(18, mean_rev_score))

    # ── Layer 1: ADX trend-strength regime ────────────────────────────────────
    if adx_val > 40:
        trend_score *= 1.20
        mean_rev_score *= 0.10  # almost eliminate MR in strong trend
        if abs(osc) < 16:
            osc *= 0.30  # only extreme oscillators survive
    elif adx_val > 25:
        mean_rev_score *= 0.40
    else:  # ranging
        trend_score *= 0.30
        mean_rev_score *= 1.20
        if bb_pct_b < 0.10:
            mean_rev_score *= 1.30  # BB bonus in ranging market

    # ── Layer 2: Price vs SMA200 ──────────────────────────────────────────────
    sma200_sl = float(r.get("sma200_slope")) if pd.notna(r.get("sma200_slope")) else 0.0
    if sma200_v is not None:
        if price > sma200_v and mean_rev_score < 0:
            mean_rev_score *= 0.20  # suppress bearish MR in bull trend
        if sma200_sl > 0 and price < sma200_v * 0.98:
            mean_rev_score *= 1.30  # boost MR in healthy-uptrend dip
        if sma200_sl < -0.01:
            trend_score *= 0.30  # suppress trend in downtrend

    # ── Suppress momentum/trend when ATR too low ──────────────────────────────
    if is_low_atr:
        trend_score = 0.0
        volume_score = 0.0

    # ── Apply family multipliers and assemble final score ─────────────────────
    osc_f = max(-25, min(25, osc)) * 1.00
    trend_f = max(-28, min(28, trend_score)) * 0.90
    volume_f = max(-20, min(20, volume_score)) * 0.85
    ma_f = max(-28, min(28, ma_score)) * 1.00
    mr_f = max(-18, min(18, mean_rev_score)) * 1.00

    score = osc_f + trend_f + volume_f + ma_f + mr_f

    # ── Layer 3: Quality gate — ≥2 families must agree ────────────────────────
    fams = [osc_f, trend_f, volume_f, ma_f, mr_f]
    families_bull = sum(1 for f in fams if f > 5)
    families_bear = sum(1 for f in fams if f < -5)
    if score > 0 and families_bull < 2 or score < 0 and families_bear < 2:
        score *= 0.50

    # ── Layer 4: Volume veto — dry volume on BUY kills conviction ─────────────
    if score > 0 and vol_dryup_f and rsi_val >= 30:
        score *= 0.70

    return round(float(score), 2)


# ─────────────────────────────────────────────────────────────────────────────
# Vectorized scoring — replaces df.apply(score_row, axis=1), ~20-50x faster
# ─────────────────────────────────────────────────────────────────────────────


def compute_scores(df: pd.DataFrame) -> pd.Series:
    """
    Fully vectorised replacement for df.apply(score_row, axis=1).
    Operates on the entire DataFrame in one numpy pass (~20-50x faster).
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

    # ── Oscillator (cap ±25) ──────────────────────────────────────────────────
    osc = np.zeros(n)
    osc += np.where(rsi_ok & (rsi < 25), 28, 0)
    osc += np.where(rsi_ok & (rsi >= 25) & (rsi < 35), 16, 0)
    osc += np.where(rsi_ok & (rsi > 75), -18, 0)
    osc += np.where(rsi_ok & (rsi >= 65) & (rsi <= 75), -10, 0)

    sk = _v("stoch_k", 50)
    sd = _v("stoch_d", 50)
    sk_p = _v("stoch_k_p", 50)
    sd_p = _v("stoch_d_p", 50)
    st_cols = ["stoch_k", "stoch_d", "stoch_k_p", "stoch_d_p"]
    st_ok = df[st_cols].notna().all(axis=1).values if all(x in df.columns for x in st_cols) else np.zeros(n, bool)
    cu = st_ok & (sk > sd) & (sk_p <= sd_p)
    cd = st_ok & (sk < sd) & (sk_p >= sd_p)
    # Zone conditions use the same elif-fallthrough logic as score_row:
    # they fire whenever the higher-priority cross conditions didn't match.
    handled = (cu & (sk < 20) & (sd < 20)) | (cd & (sk > 80) & (sd > 80)) | (cu & (sk < 20)) | (cd & (sk > 80))
    osc += np.select(
        [
            cu & (sk < 20) & (sd < 20),
            cd & (sk > 80) & (sd > 80),
            cu & (sk < 20),
            cd & (sk > 80),
            st_ok & ~handled & (sk < 25),
            st_ok & ~handled & (sk > 75),
        ],
        [18, -14, 10, -8, 5, -4],
        default=0,
    )

    wr = _v("wr", -50)
    wr_ok = df["wr"].notna().values if "wr" in df.columns else np.zeros(n, bool)
    osc += np.where(wr_ok & (wr <= -85), 10, 0)
    osc += np.where(wr_ok & (wr >= -15), -8, 0)

    cci = _v("cci", 0)
    cci_ok = df["cci"].notna().values if "cci" in df.columns else np.zeros(n, bool)
    osc += np.select(
        [
            cci_ok & (cci < -200),
            cci_ok & (cci >= -200) & (cci < -150),
            cci_ok & (cci >= -150) & (cci < -100),
            cci_ok & (cci > 200),
            cci_ok & (cci <= 200) & (cci > 150),
            cci_ok & (cci <= 150) & (cci > 100),
        ],
        [14, 8, 3, -12, -7, -3],
        default=0,
    )
    osc = np.clip(osc, -25, 25)

    # ── Trend (cap ±28) ───────────────────────────────────────────────────────
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

    # ── Volume (cap ±20) ──────────────────────────────────────────────────────
    vol = np.zeros(n)
    obv_ab = _v("obv_above", 0)
    obv_sl = _v("obv_slope", 0)
    ob_ok = (
        df["obv_above"].notna().values & df["obv_slope"].notna().values
        if "obv_above" in df.columns
        else np.zeros(n, bool)
    )
    vol += np.where(ob_ok & (obv_ab > 0) & (obv_sl > 0) & (osc > 15), 16, 0)
    vol += np.where(ob_ok & (obv_ab > 0) & (obv_sl > 0) & (osc <= 15), 8, 0)
    vol += np.where(ob_ok & (obv_ab <= 0) & (obv_sl < 0) & (osc < -15), -16, 0)
    vol += np.where(ob_ok & (obv_ab <= 0) & (obv_sl < 0) & (osc >= -15), -8, 0)

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

    # ── MA (cap ±28) ──────────────────────────────────────────────────────────
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
    if "vwap_slope_pos" in df.columns:
        vwap_slope = df["vwap_slope_pos"].fillna(False).astype(bool).values
    else:
        vwap_slope = np.zeros(n, dtype=bool)
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

    # ── Mean-Reversion (cap ±18) ──────────────────────────────────────────────
    mr = np.zeros(n)
    bb = _v("bb_pct_b", 0.5)
    bb_ok = df["bb_pct_b"].notna().values if "bb_pct_b" in df.columns else np.zeros(n, bool)
    mr += np.select(
        [
            bb_ok & (bb < 0.05) & (rsi < 35),
            bb_ok & (bb < 0.05) & (rsi >= 35) & (rsi < 45),
            bb_ok & (bb < 0.05),
            bb_ok & (bb >= 0.05) & (bb < 0.15) & (rsi < 35),
            bb_ok & (bb >= 0.05) & (bb < 0.15) & (rsi >= 35) & (rsi < 45),
        ],
        [18, 12, 6, 10, 5],
        default=0,
    )
    mr += np.select(
        [
            bb_ok & (bb > 0.95) & (rsi > 65),
            bb_ok & (bb > 0.95) & (rsi > 55) & (rsi <= 65),
            bb_ok & (bb > 0.95),
            bb_ok & (bb > 0.85) & (bb <= 0.95) & (rsi > 65),
            bb_ok & (bb > 0.85) & (bb <= 0.95) & (rsi > 55) & (rsi <= 65),
        ],
        [-14, -8, -4, -8, -4],
        default=0,
    )
    mr += np.where(_b("squeeze_breakout_up"), 16, 0)
    mr += np.where(_b("squeeze_breakout_down"), -16, 0)
    mr += np.where(bb_ok & (adx_val < 20) & (bb < 0.15), 6, 0)

    ibs = _v("ibs", 0.5)
    ibs_ok = df["ibs"].notna().values if "ibs" in df.columns else np.zeros(n, bool)
    mr += np.select(
        [ibs_ok & (ibs < 0.05), ibs_ok & (ibs >= 0.05) & (ibs < 0.10), ibs_ok & (ibs > 0.90)], [15, 8, -10], default=0
    )

    b2u = _v("vwap_band2_upper", np.inf)
    b2u_ok = df["vwap_band2_upper"].notna().values if "vwap_band2_upper" in df.columns else np.zeros(n, bool)
    b2l = _v("vwap_band2_lower", -np.inf)
    b2l_ok = df["vwap_band2_lower"].notna().values if "vwap_band2_lower" in df.columns else np.zeros(n, bool)
    mr += np.where(b2u_ok & (c >= b2u), -14, 0)
    mr += np.where(b2l_ok & (c <= b2l), 14, 0)

    atr_con = _v("atr_contract_bars", 0)
    atr_rank = _v("atr_pct_rank", 50)
    ar_ok = df["atr_pct_rank"].notna().values if "atr_pct_rank" in df.columns else np.zeros(n, bool)
    mr += np.where(atr_con >= 5, 6, 0)
    mr = mr * np.where(ar_ok & (atr_rank > 90), 0.5, np.where(ar_ok & (atr_rank < 10), 1.4, 1.0))
    mr = np.clip(mr, -18, 18)

    # ── Regime Layers ─────────────────────────────────────────────────────────
    strong = adx_val > 40
    mod = (adx_val > 25) & ~strong
    rng = ~strong & ~mod
    trend = np.where(strong, trend * 1.20, trend)
    mr = np.where(strong, mr * 0.10, mr)
    osc = np.where(strong & (np.abs(osc) < 16), osc * 0.30, osc)
    mr = np.where(mod, mr * 0.40, mr)
    trend = np.where(rng, trend * 0.30, trend)
    mr = np.where(rng, mr * 1.20, mr)
    mr = np.where(rng & bb_ok & (bb < 0.10), mr * 1.30, mr)

    s200_sl_a = _v("sma200_slope", 0)
    bull_mkt = sma200_ok & (c > sma200_v)
    mr = np.where(bull_mkt & (mr < 0), mr * 0.20, mr)
    mr = np.where(sma200_ok & (s200_sl_a > 0) & (c < sma200_v * 0.98), mr * 1.30, mr)
    trend = np.where(sma200_ok & (s200_sl_a < -0.01), trend * 0.30, trend)

    trend = np.where(low_atr, 0.0, trend)
    vol = np.where(low_atr, 0.0, vol)

    # ── Assemble + quality gate + volume veto ────────────────────────────────
    osc_f = np.clip(osc, -25, 25) * 1.00
    trend_f = np.clip(trend, -28, 28) * 0.90
    vol_f = np.clip(vol, -20, 20) * 0.85
    ma_f = np.clip(ma, -28, 28) * 1.00
    mr_f = np.clip(mr, -18, 18) * 1.00
    score = osc_f + trend_f + vol_f + ma_f + mr_f

    stk = np.stack([osc_f, trend_f, vol_f, ma_f, mr_f], axis=1)
    bull_cnt = (stk > 5).sum(axis=1)
    bear_cnt = (stk < -5).sum(axis=1)
    score = np.where((score > 0) & (bull_cnt < 2), score * 0.50, score)
    score = np.where((score < 0) & (bear_cnt < 2), score * 0.50, score)
    score = np.where((score > 0) & vd & (rsi >= 30), score * 0.70, score)

    return pd.Series(np.round(score, 2), index=df.index)


def atr_levels(
    price: float,
    atr: float,
    action: str,
    adx: float = 25.0,
    stop_mult_override: float | None = None,
    target_mult_override: float | None = None,
) -> tuple[float, float]:
    """Return (stop_price, target_price) for swing style.

    Three Fixes:
      - Tighter Stops: ATR/ADX-aware stop (cut the bleeding)
      - Extend Targets in Strong Trends: ADX>35 widens targets
    """
    if atr == 0:
        return (price * 0.96, price * 1.04) if action == "BUY" else (price * 1.04, price * 0.96)

    atr_pct = atr / price

    # Targets calibrated so they're achievable within HOLD_DAYS bars.
    # §11c decomp (103-ticker 23yr): 1.0s/2.0t → Sharpe 0.50 vs 0.24 at 2.0s/2.5t.
    # Tighter stop cuts losses faster while keeping the same target (R:R 2.0 vs 1.25).
    #   Strong trend (ADX>35): 1.0s / 3.0t  — trend carries further, tight stop
    #   High vol (ATR>2.5%):   1.5s / 2.0t  — gaps require slightly wider stop
    #   Low vol  (ATR<1.0%):   1.5s / 2.0t  — same, modest target
    #   Normal:                1.0s / 2.0t  — R:R 2.0 (§11c optimal)
    if adx > 35:
        s, t = 1.0, 3.0
    elif atr_pct > 0.025 or atr_pct < 0.010:
        s, t = 1.5, 2.0
    else:
        s, t = 1.0, 2.0

    if stop_mult_override is not None:
        s = stop_mult_override
    if target_mult_override is not None:
        t = target_mult_override

    if action == "BUY":
        return price - s * atr, price + t * atr
    else:
        return price + s * atr, price - t * atr


# ─────────────────────────────────────────────────────────────────────────────
# Trade simulation
# ─────────────────────────────────────────────────────────────────────────────


def simulate_ticker(
    ticker: str,
    df: pd.DataFrame,
    vix: dict,
    spy_trend: dict,
    stlfsi4: dict,
    mr_only: bool = False,
    dual_gate: bool = False,
    earnings_dates: set | None = None,
    earnings_blackout_days: int | None = None,
    hold_days_override: int | None = None,
    mr_rsi_ceil_override: float | None = None,
    stop_mult_override: float | None = None,
    target_mult_override: float | None = None,
    buy_thresh_override: int | None = None,
    vix_min_override: float | None = None,
    require_mr_count_override: int | None = None,
    require_consec_score_override: bool | None = None,
    atr_pct_rank_min_override: float | None = None,
    atr_pct_rank_max_override: float | None = None,
    ret_jump_filter_override: float | None = None,
    entry_delay_override: bool = False,
    ibs_sma20_streak_override: int | None = None,
    max_loss_days_override: int | None = None,
    no_progress_days: int | None = None,
    vix_regime_switch: bool = False,
    adaptive_profit_thresh_override: float | None = None,
    adaptive_rsi_thresh_override: float | None = None,
) -> pd.DataFrame:
    """
    Generate signals and simulate trades for one ticker.

    Gates applied (in order):
      1.   VIX tiers        — hard block >30; marginal BUY (score<45) blocked 25-30
      2.   STLFSI4 stress   — hard block >1.5+VIX>30; marginal >1.0+VIX>25+score<50
      3.   SPY macro trend  — BUY requires bull/RSI<30/score≥55; bear blocks score<60
      4.   RVOL gate        — BUY blocked if RVOL < 1.2 (waived RSI<30)
      5.   SELL SMA200 gate — technical-only SELL needs score ≤ -50
      5b.  BUY SMA200 gate  — BUY blocked below SMA200×0.99 unless RSI<25 or score≥60
      6–8. ADX (< 18 + score<45) / RSI / ATR gates
      9.   MR/Dual gate     — MR: RSI<42 OR BB%B<0.22 OR IBS<0.15 OR VWAP%<-0.75
                              MOM (dual_gate): RSI 50-68 + MACD accel + OBV+ + >SMA50 + RS+
      9b.  Global VIX min   — MR BUY blocked when VIX < 20 (§12b engine gate)
      10.  Earnings blackout — block within EARNINGS_BLACKOUT_DAYS of report
      11.  Consecutive RSI  — RSI must still be declining into the entry bar
      12.  Deep-bear RSI    — VIX>28 + SPY<SMA200×0.95 requires RSI<35
      13.  Price-SMA20      — price must be ≥2% below SMA20 (waived score≥65)
      14.  Dollar volume    — avg daily $ volume must exceed MIN_AVG_DOLLAR_VOL
      15.  Day-of-week      — no Friday entries (waived score≥65)
    """
    trades = []
    in_trade_until = pd.Timestamp("2000-01-01")
    _hold_days = hold_days_override if hold_days_override is not None else HOLD_DAYS
    _mr_rsi_ceil = mr_rsi_ceil_override if mr_rsi_ceil_override is not None else MR_RSI_CEIL
    _buy_thresh = buy_thresh_override if buy_thresh_override is not None else BUY_THRESH
    _vix_min = vix_min_override
    _require_mr_count = require_mr_count_override if require_mr_count_override is not None else 1
    _require_consec = require_consec_score_override if require_consec_score_override is not None else False
    # Default to 20 in MR-only mode — matches live engine gate (§12e validated:
    # Ann. Sharpe 0.92 → 1.00, removes only 17% of trades, WR +3.4pp).
    _atr_rank_min = atr_pct_rank_min_override if atr_pct_rank_min_override is not None else (20.0 if mr_only else None)
    _atr_rank_max = atr_pct_rank_max_override  # None = no ceiling
    _ret_jump_max = ret_jump_filter_override  # e.g. -6.0 blocks if 1-day chg < -6%
    _entry_delay = entry_delay_override  # True = fill at T+2 open, not T+1
    _ibs_sma20_streak = ibs_sma20_streak_override  # e.g. 5 = require ≥5 days below SMA20 for IBS-only MR
    _max_loss_days = max_loss_days_override if max_loss_days_override is not None else MAX_LOSS_DAYS
    _no_progress_days = no_progress_days
    _vix_regime_switch = vix_regime_switch
    _adaptive_profit_thresh = adaptive_profit_thresh_override if adaptive_profit_thresh_override is not None else 1.005
    _adaptive_rsi_thresh = adaptive_rsi_thresh_override if adaptive_rsi_thresh_override is not None else 45.0

    _trade_from_ts = pd.Timestamp(TRADE_FROM)
    for i in range(200, len(df)):
        row = df.iloc[i]
        date = df.index[i]

        if TRADE_FROM != END and date < _trade_from_ts:
            continue

        if date <= in_trade_until:
            continue

        score = float(row["score"])
        price = float(row["Close"])
        atr = float(row["atr"]) if pd.notna(row["atr"]) else 0.0
        rvol = float(row["rvol"]) if pd.notna(row["rvol"]) else 1.0
        rsi_v = float(row["rsi"]) if pd.notna(row["rsi"]) else 50.0
        is_oversold = rsi_v < 30
        sma200_v = float(row["sma200"]) if pd.notna(row["sma200"]) else None

        vix_today = vix.get(date)
        stress_today = stlfsi4.get(date)
        spy_dir = spy_trend.get(date)  # +1 = bull, -1 = bear, None = unknown

        # ── §21 VIX-regime switching ──────────────────────────────────────────
        # high-VIX (≥18): strict mode — thresh=38, ATR ceil=70, jump<-6%
        # low-VIX  (<18): relaxed mode — thresh=35, no ATR ceil, no jump filter
        if _vix_regime_switch and vix_today is not None:
            if vix_today >= 18.0:
                _buy_thresh, _atr_rank_max, _ret_jump_max = 38, 70.0, -6.0
            else:
                _buy_thresh, _atr_rank_max, _ret_jump_max = 35, None, None

        is_buy_signal = _buy_thresh <= score <= BUY_THRESH_MAX
        is_sell_signal = score <= SELL_THRESH

        if not is_buy_signal and not is_sell_signal:
            continue

        # ── Gate 1: VIX tiers ─────────────────────────────────────────────────
        if is_buy_signal and vix_today is not None:
            if vix_today > 30:
                continue  # hard block (matches live engine + docstring)
            if vix_today > 25 and score < 45:
                continue  # elevated fear — need conviction
        if is_sell_signal and vix_today is not None and vix_today < 15 and score > -45:
            continue  # complacency — market trending up
        if is_sell_signal and vix_today is not None and vix_today > 35:
            continue  # panic spike — reversal risk too high to short

        # ── Gate 2: STLFSI4 financial stress ──────────────────────────────────
        if is_buy_signal and stress_today is not None and vix_today is not None:
            if stress_today > 1.5 and vix_today > 30:
                continue
            if stress_today > 1.0 and vix_today > 25 and score < 50:
                continue

        # ── Gate 3: SPY macro trend ───────────────────────────────────────────
        # Bull (+1): block all shorts
        if spy_dir == 1 and is_sell_signal:
            continue

        # Bear (-1): no oversold exception — oversold stocks keep falling in
        # systemic downtrends (dead-cat-bounce trap). Only exceptional conviction.
        if spy_dir == -1 and is_buy_signal and score < 60:
            continue

        # Neutral (0 / transition zone ±2% of SMA200): require elevated conviction.
        # Prevents whipsaw entries during regime transitions (Aug-2022 bear bounce,
        # late-2018 Q4 breakdown). Marginal signals fail here; strong ones pass.
        if spy_dir == 0 and is_buy_signal and score < 45:
            continue

        # ── Gate 4: RVOL gate ─────────────────────────────────────────────────
        if is_buy_signal and rvol < 1.2 and not is_oversold:
            continue

        # ── Gate 6: ADX minimum — no entries in completely directionless markets ──
        # Deep oversold (RSI<30) is excepted: oversold bounces work even in chop.
        # score<45 waiver matches signal engine (high-conviction signals pass).
        adx_entry = float(row["adx"]) if pd.notna(row.get("adx")) else 0.0
        if is_buy_signal and adx_entry < 18 and not is_oversold and score < 45:
            continue

        # ── Gate 5: per-stock SMA200 SELL gate ───────────────────────────────
        # Only allow SELLs above SMA200 when signal is extremely strong (score ≤ -50)
        if is_sell_signal and sma200_v is not None and price > sma200_v * 1.01 and score > -50:
            continue

        # ── Gate 5b: SMA200 downtrend BUY gate (matches signal engine) ──────────
        # Signal engine: price < SMA200*0.99 in downtrend → HOLD unless RSI<25 or score≥60.
        # RSI waiver tightened from 30→25 (engine finding: RSI 25-30 entries in downtrends
        # are dead-cat bounces). High-conviction entries (score≥60) bypass.
        if is_buy_signal and sma200_v is not None and price < sma200_v * 0.99 and rsi_v >= 25 and score < 60:
            continue

        # ── Gate 7: RSI overbought in weak-trend bull market ─────────────────
        # Block overbought entries (RSI > 70) only when the trend is weak
        # (ADX < 28) — catches "topping market" false breakouts where a stock
        # is extended but momentum is fading (2018 pattern).
        # When ADX ≥ 28 (genuinely strong trend), RSI > 70 stocks can keep going
        # and blocking them hurts momentum-rich years like 2013/2017.
        if is_buy_signal and spy_dir == 1 and rsi_v > 70 and score < 40 and adx_entry < 28:
            continue

        # ── Gate 8: Minimum ATR — skip near-flat stocks ───────────────────────
        # Stocks moving < 0.7%/day on average can't produce 5-day swing returns
        # above friction. Filters slow consumer staples / mega-caps in low-vol.
        atr_pct_entry = atr / price if price > 0 else 0.0
        if is_buy_signal and atr_pct_entry < 0.007:
            continue

        # ── Gate 9: MR-only / Dual-Gate filter ────────────────────────────────
        # mr_only=True: entry requires at least one genuine MR condition.
        # dual_gate=True: entry allowed if MR gate passes OR momentum gate passes.
        # MR gate: RSI<42 OR BB%B<0.22 OR IBS<0.15 OR VWAP%<-0.75 (oversold setup)
        # MOM gate: RSI in [50,68], MACD accelerating, OBV positive, above SMA50,
        #           outperforming SPY (trending breakout setup — orthogonal to MR)
        _is_mr_setup = False
        _is_mom_setup = False
        if (mr_only or dual_gate) and is_buy_signal:
            rsi_e = float(row.get("rsi", 50)) if pd.notna(row.get("rsi")) else 50.0
            bb_e = float(row.get("bb_pct_b", 0.5)) if pd.notna(row.get("bb_pct_b")) else 0.5
            ibs_e = float(row.get("ibs", 0.5)) if pd.notna(row.get("ibs")) else 0.5
            vwap_e = float(row.get("vwap_pct", 0)) if pd.notna(row.get("vwap_pct")) else 0.0
            # gap_pct and close_streak are no longer MR-gate triggers — matches
            # signal engine's _has_mr (RSI/BB/IBS/VWAP only). They still
            # contribute to the signal score via compute_scores().
            _is_mr_setup = rsi_e < _mr_rsi_ceil or bb_e < MR_BB_CEIL or ibs_e < MR_IBS_CEIL or vwap_e < MR_VWAP_FLOOR
            if dual_gate and not _is_mr_setup:
                _mh = float(row.get("macd_hist", 0)) if pd.notna(row.get("macd_hist")) else 0.0
                _mhp = float(row.get("macd_hist_p", 0)) if pd.notna(row.get("macd_hist_p")) else 0.0
                _obva = bool(row.get("obv_above", 0))
                _s50 = float(row.get("sma50", price)) if pd.notna(row.get("sma50")) else price
                _s20 = float(row.get("sma20", price)) if pd.notna(row.get("sma20")) else price
                _rs1m = float(row.get("rs_1m", 0)) if pd.notna(row.get("rs_1m")) else 0.0
                _wk52 = float(row.get("wk52_pos", 0.5)) if pd.notna(row.get("wk52_pos")) else 0.5
                _is_mom_setup = (
                    54 <= rsi_e <= 63  # tight trend zone: not barely neutral, not near overbought
                    and _mh > 0
                    and _mh > _mhp  # MACD positive AND accelerating (both required)
                    and _obva  # OBV accumulation confirmed
                    and price > _s50  # above SMA50 (medium-term uptrend)
                    and price > _s20  # above SMA20 (short-term momentum intact)
                    and _rs1m > 2.0  # meaningfully outperforming SPY (not marginal)
                    and _wk52 > 0.88  # within 12% of 52W high (George & Hwang 2004)
                    and adx_entry > 22  # genuine trend strength (not chop)
                    and score >= 50  # high-conviction signal required for momentum
                )
            if not (_is_mr_setup or _is_mom_setup):
                continue

            # ── Gate 9a: MR multi-condition confluence ─────────────────────────
            # By default one MR condition suffices (OR logic). When
            # require_mr_count_override > 1, demand simultaneous signals —
            # e.g. IBS<0.15 AND RSI<42 — filtering single-condition IBS-only
            # entries that are the weakest class of MR setups.
            if _is_mr_setup and _require_mr_count > 1:
                _mr_count = sum(
                    [
                        rsi_e < _mr_rsi_ceil,
                        bb_e < MR_BB_CEIL,
                        ibs_e < MR_IBS_CEIL,
                        vwap_e < MR_VWAP_FLOOR,
                    ]
                )
                if _mr_count < _require_mr_count:
                    continue

            # ── Gate 9b: Global VIX minimum for MR entries ────────────────────
            # Signal engine: vix < 20 → HOLD for MR setups (§12b: 103-ticker 23yr).
            # Low-VIX = shallow panic = weak MR bounces. MR edge requires fear premium.
            # §12b: VIX≥20 → Sharpe 0.23 vs 0.13 baseline, WR 64.1%, MaxDD -0.87%.
            if _is_mr_setup and vix_today is not None and vix_today < 20:
                continue

        # ── Gate 10: Earnings blackout ─────────────────────────────────────────
        # Binary earnings events destroy MR setups — an oversold stock that beats
        # will gap up (missing our stop target entirely) or misses and gaps past
        # the stop in one bar. Block entries within the blackout window.
        _earn_blackout = earnings_blackout_days if earnings_blackout_days is not None else EARNINGS_BLACKOUT_DAYS
        _days_to_earn: int = 999
        if earnings_dates:
            _days_to_earn = min(
                ((e - date).days for e in earnings_dates if (e - date).days >= 0),
                default=999,
            )
            if is_buy_signal and _days_to_earn <= _earn_blackout:
                continue

        # ── Gate 11: Consecutive RSI decline (all MR setups) ─────────────────
        # Require RSI still falling into the signal bar (selling still active).
        # Applies to all MR entries including gap/streak triggers — if RSI is rising
        # on a gap-down or streak bar, the bounce may already be underway and entry
        # is late. Tested RSI-only bypass in v11d: added bad trades, Sharpe 0.16.
        if is_buy_signal and i > 0 and _is_mr_setup and not _is_mom_setup:
            prev_rsi = float(df.iloc[i - 1]["rsi"]) if pd.notna(df.iloc[i - 1].get("rsi")) else rsi_v + 1
            if rsi_v >= prev_rsi:  # RSI rising or flat — bounce may already be underway
                continue

        # ── Gate 18: Persistent oversold — consecutive score requirement ───────
        # Require the previous bar also had score >= BUY_THRESH. One-day panic
        # signals frequently whipsaw; persistent oversold (2+ days above threshold)
        # indicates sustained selling pressure nearing exhaustion — higher conviction.
        if is_buy_signal and _require_consec and i > 0:
            prev_score = float(df.iloc[i - 1]["score"]) if "score" in df.columns else 0.0
            if prev_score < _buy_thresh:
                continue

        # ── Gate 12: Deep-bear stricter RSI ───────────────────────────────────
        # In systemic downturns (VIX > DEEP_BEAR_VIX and SPY well below SMA200),
        # "oversold" at RSI 42 is a falling knife, not a bounce. Only the most
        # extreme capitulation (RSI < 35) has MR edge in those regimes —
        # responsible for the 2022 rate-hike bear's −2.17% avg on 13 trades.
        if is_buy_signal and vix_today is not None and sma200_v is not None:
            deep_bear = vix_today > DEEP_BEAR_VIX and price < sma200_v * DEEP_BEAR_SMA200_RATIO
            if deep_bear and rsi_v >= DEEP_BEAR_RSI_MAX:
                continue

        # ── Gate 13: Price-SMA20 distance (MR setups only) ────────────────────
        # Require price ≥2% below 20-day SMA — matches signal engine (0.98 threshold).
        # Waived when score≥65 (strong independent confirmation), also matching engine.
        # Skipped for momentum setups — those entries require price ABOVE SMA20.
        if is_buy_signal and _is_mr_setup and not _is_mom_setup:
            sma20_e = float(row.get("sma20", 0)) if pd.notna(row.get("sma20")) else 0.0
            if sma20_e > 0 and price >= sma20_e * 0.98 and score < 65:
                continue

        # ── Gate 14: Dollar-volume minimum ────────────────────────────────────
        # Skip entries where average daily dollar volume < MIN_AVG_DOLLAR_VOL.
        # Illiquid sessions inflate our 0.20% friction assumption; wide bid-ask
        # spreads on thin tape can easily absorb the entire expected edge.
        if is_buy_signal and rvol > 0:
            raw_vol = float(df.iloc[i]["Volume"]) if "Volume" in df.columns else 0.0
            avg_vol_20 = raw_vol / rvol  # rvol = today / avg20 → avg20 = today/rvol
            if price * avg_vol_20 < MIN_AVG_DOLLAR_VOL:
                continue

        # ── Gate 15: Day-of-week — no Friday entries ──────────────────────────
        # Friday BUY entries carry 2-day weekend gap risk with no intraday
        # management possible. MR setups that fire Friday tend to resolve
        # Monday morning on the gap open, often adversely.
        # Waived at score≥65 (strong conviction) — matches signal engine.
        if is_buy_signal and date.dayofweek == 4 and score < 65:  # Friday = 4
            continue

        # ── Gate 16: VIX minimum — skip low-volatility regime entries ─────────
        # In low-VIX environments stocks don't panic-sell deeply enough for
        # meaningful MR bounces. Elevated VIX = fear-driven capitulation =
        # stronger bounce. Only applied when vix_min_override is set.
        if is_buy_signal and _vix_min is not None and vix_today is not None:
            if vix_today < _vix_min:
                continue

        # ── Gate 17: ATR percentile rank minimum ──────────────────────────────
        # Only enter when this stock's ATR is elevated relative to its own
        # history. Low ATR%rank = dormant period = weak bounces. High ATR%rank
        # = panic-level volatility = MR bounces are strongest.
        atr_rank_e = float(row.get("atr_pct_rank", 50)) if pd.notna(row.get("atr_pct_rank")) else 50.0
        if is_buy_signal and _atr_rank_min is not None:
            if atr_rank_e < _atr_rank_min:
                continue

        # ── Gate 17b: ATR percentile rank ceiling (§17a research) ─────────────
        # ATR > 70th pct = trending panic / structural breakdown. At this extreme,
        # forced selling may not have peaked — the stock is in a trending move, not
        # a recoverable dip. MR setups in very-high-ATR regimes often continue lower
        # before reversing (Quantpedia ATR regime research, P50/P70 threshold finding).
        if is_buy_signal and _atr_rank_max is not None:
            if atr_rank_e > _atr_rank_max:
                continue

        # ── Gate 17c: Single-day return jump filter (§17b research) ───────────
        # Large single-day drops (< −6%) often signal fundamental repricing
        # (earnings miss, guidance cut, fraud, regulatory action) rather than
        # a recoverable panic. The stock may gap down and stay down.
        # Alpha Architect finding: filtering "return jumps" tripled cumulative returns.
        # IBS-only entries on −8%+ days are especially suspect — closing near the low
        # of an 8% down day is often the beginning of multi-day continuation.
        if is_buy_signal and _ret_jump_max is not None:
            chg_e = float(row.get("change_pct", 0)) if pd.notna(row.get("change_pct")) else 0.0
            if chg_e < _ret_jump_max:
                continue

        # ── Gate 17e: IBS + multi-day SMA20 confluence (§17e research, Pagonidis) ──
        # Pagonidis (2013): IBS<0.15 triggered by a single bad day without sustained
        # selling pressure produces weaker MR bounces. Combining IBS<0.15 with
        # ≥N consecutive days below SMA20 confirms the stock is genuinely oversold,
        # not just experiencing a one-day intrabar weakness event.
        # Gate: when IBS<0.15 is the SOLE MR trigger (RSI≥42, BB≥0.22, VWAP≥-0.75,
        # no gap, no streak), require close_streak ≤ -N (N = _ibs_sma20_streak).
        if is_buy_signal and _ibs_sma20_streak is not None and _is_mr_setup:
            _ibs_ev = float(row.get("ibs", 0.5)) if pd.notna(row.get("ibs")) else 0.5
            _rsi_ev = float(row.get("rsi", 50)) if pd.notna(row.get("rsi")) else 50.0
            _bb_ev = float(row.get("bb_pct_b", 0.5)) if pd.notna(row.get("bb_pct_b")) else 0.5
            _vwap_ev = float(row.get("vwap_pct", 0)) if pd.notna(row.get("vwap_pct")) else 0.0
            _gap_ev = float(row.get("gap_pct", 0)) if pd.notna(row.get("gap_pct")) else 0.0
            _ibs_is_sole = (
                _ibs_ev < MR_IBS_CEIL
                and _rsi_ev >= _mr_rsi_ceil
                and _bb_ev >= MR_BB_CEIL
                and _vwap_ev >= MR_VWAP_FLOOR
                and _gap_ev >= MR_GAP_FLOOR
            )
            if _ibs_is_sole:
                _streak_ev = float(row.get("close_streak", 0)) if pd.notna(row.get("close_streak")) else 0.0
                if _streak_ev > -_ibs_sma20_streak:
                    continue

        action = "BUY" if is_buy_signal else "SELL"

        adx_v = float(row["adx"]) if pd.notna(row.get("adx")) else 25.0

        # Signal is generated at bar-i close; fill at T+1 open (default) or T+2 open
        # when entry_delay_override=True (§17d: skip the continuation morning).
        _fill_bar = i + 2 if _entry_delay else i + 1
        if _fill_bar >= len(df):
            break
        entry_price = float(df.iloc[_fill_bar]["Open"])

        # Anchor stop/target to actual fill price, not signal-bar close.
        # Using signal close misplaces stops by the overnight gap distance.
        stop_price, target_price = atr_levels(entry_price, atr, action, adx_v, stop_mult_override, target_mult_override)

        # ── Scan next HOLD_DAYS bars for stop/target/time-loss exit ──────────
        exit_price = None
        exit_reason = "time"
        exit_day = _hold_days
        _mfe_pct = 0.0  # max favorable excursion across hold bars

        for j in range(0, _hold_days):
            if _fill_bar + j >= len(df):
                exit_day = j - 1 if j > 0 else 0
                break
            bar = df.iloc[_fill_bar + j]
            day_high = float(bar["High"])
            day_low = float(bar["Low"])
            day_close = float(bar["Close"])

            day_open = float(bar["Open"])
            # Track MFE: best intrabar price reached vs entry
            if action == "BUY":
                _mfe_pct = max(_mfe_pct, (day_high - entry_price) / entry_price * 100)
            else:
                _mfe_pct = max(_mfe_pct, (entry_price - day_low) / entry_price * 100)
            if action == "BUY":
                if day_low <= stop_price:
                    # Gap-through: if the bar opened below the stop, fill at the open
                    # (stock already past stop before market could execute at stop_price).
                    exit_price = min(stop_price, day_open)
                    exit_reason = "stop"
                    exit_day = j
                    break
                if day_high >= target_price:
                    exit_price = target_price
                    exit_reason = "target"
                    exit_day = j
                    break
                # Cut losers early: only after _max_loss_days AND trade is ≥1% in the red
                # (avoids exiting trades that are merely flat or marginally negative)
                if j >= _max_loss_days - 1 and day_close < entry_price * 0.99:
                    exit_price = day_close
                    exit_reason = "time_loss"
                    exit_day = j
                    break
                # ── No-progress exit: thesis failed, RSI not recovering ──────────
                # Fires when the trade hasn't gained ≥0.3% by day N AND RSI hasn't
                # bounced above 50 — signals the MR bounce simply isn't materializing.
                if _no_progress_days is not None and j >= _no_progress_days - 1:
                    _rsi_np = float(bar.get("rsi", 50)) if pd.notna(bar.get("rsi")) else 50.0
                    if day_close < entry_price * 1.003 and _rsi_np <= 50:
                        exit_price = day_close
                        exit_reason = "no_progress"
                        exit_day = j
                        break
                # ── Adaptive exit: MR bounce completion (profit-lock mechanism) ──
                # Exit when indicators confirm the bounce is done AND we're profitable.
                # No look-ahead bias: all indicators use the same bar's close; exit
                # is booked at that same day_close.
                # Requires: profitable > _adaptive_profit_thresh (0.5%) AND ≥ 2 days.
                # §35b: RSI threshold lowered 55→45 — RSI>55 was never reached in
                # many completed bounces; 45 captures 47% of trades vs 29% at WR 100%.
                #
                # NOTE — 100% WR on adaptive exits is DEFINITIONAL, not predictive:
                # the gate only fires when day_close > entry * 1.005 (profit threshold).
                # Since exit_price = day_close, the net return is always > 0.5% - friction.
                # The adaptive indicator conditions (RSI>45, MACD+accel, VWAP+, SMA20+)
                # determine WHEN to capture the profit, not WHETHER the trade will profit.
                # The meaningful metric is: what fraction of all entries reach this gate
                # vs. hitting stop or time_loss instead.
                if j >= 2 and day_close > entry_price * _adaptive_profit_thresh:
                    _rsi_now = float(bar.get("rsi", 50)) if pd.notna(bar.get("rsi")) else 50.0
                    _macd_h = float(bar.get("macd_hist", 0)) if pd.notna(bar.get("macd_hist")) else 0.0
                    _macd_hp = float(bar.get("macd_hist_p", 0)) if pd.notna(bar.get("macd_hist_p")) else 0.0
                    _vwap_p = float(bar.get("vwap_pct", -1)) if pd.notna(bar.get("vwap_pct")) else -1.0
                    _sma20_x = float(bar.get("sma20", 0)) if pd.notna(bar.get("sma20")) else 0.0
                    _bounce_done = (
                        _rsi_now > _adaptive_rsi_thresh  # RSI above threshold
                        or (_macd_h > 0 and _macd_h > _macd_hp)  # MACD positive + accelerating
                        or _vwap_p > 0  # price recaptured VWAP
                        or (_sma20_x > 0 and day_close > _sma20_x)  # price back above SMA20
                    )
                    if _bounce_done:
                        exit_price = day_close
                        exit_reason = "adaptive"
                        exit_day = j
                        break
            else:  # SELL / short
                if day_high >= stop_price:
                    # Gap-through (short): fill at worst of stop or open if gapped above stop
                    exit_price = max(stop_price, day_open)
                    exit_reason = "stop"
                    exit_day = j
                    break
                if day_low <= target_price:
                    exit_price = target_price
                    exit_reason = "target"
                    exit_day = j
                    break
                if j >= _max_loss_days - 1 and day_close > entry_price * 1.01:
                    exit_price = day_close
                    exit_reason = "time_loss"
                    exit_day = j
                    break

        if exit_price is None:
            idx = min((i + 1) + (_hold_days - 1), len(df) - 1)
            exit_price = float(df.iloc[idx]["Close"])

        # ── Return calculation ────────────────────────────────────────────────
        if action == "BUY":
            gross_pct = (exit_price - entry_price) / entry_price * 100
        else:
            gross_pct = (entry_price - exit_price) / entry_price * 100

        net_pct = gross_pct - FRICTION_PCT

        trades.append(
            {
                "date": date,
                "ticker": ticker,
                "action": action,
                "score": score,
                "entry": round(entry_price, 2),
                "stop": round(stop_price, 2),
                "target": round(target_price, 2),
                "exit_price": round(exit_price, 2),
                "exit_reason": exit_reason,
                "exit_day": exit_day,
                "gross_pct": round(gross_pct, 3),
                "net_pct": round(net_pct, 3),
                "mfe_pct": round(_mfe_pct, 3),
                "atr_pct": round(atr / entry_price * 100, 2) if entry_price > 0 else 0,
                "days_to_earnings": _days_to_earn if _days_to_earn < 999 else None,
            }
        )

        # Cooldown: trade duration + 3 calendar days buffer.
        # v5.11: changed from 2×duration (too aggressive with HOLD_DAYS=7)
        # to duration+3 — allows re-entry sooner after a quick exit while
        # still preventing same-day re-entry (exit_day=0 → 3 day cooldown).
        in_trade_until = date + pd.Timedelta(days=max(exit_day + 3, 5))

    return pd.DataFrame(trades)


# ─────────────────────────────────────────────────────────────────────────────
# Stats helpers
# ─────────────────────────────────────────────────────────────────────────────

_EMPTY_STATS = {
    "n": 0,
    "wr": 0.0,
    "avg": 0.0,
    "avg_win": None,
    "avg_loss": None,
    "pf": None,
    "sharpe": None,
    "max_dd": 0.0,
}


def stats_weighted(rets: list[float], scores: list[float]) -> dict:
    """Score-proportional position sizing Sharpe.

    Each trade is weighted by its conviction score (normalized, mean=1.0).
    Models a portfolio where position size scales with signal confidence.
    Scores are min-max normalised then floored at 0.5× so no trade is zeroed out.
    """
    if not rets or not scores or len(rets) != len(scores):
        return dict(_EMPTY_STATS)
    arr = np.array(rets, dtype=float)
    w = np.array(scores, dtype=float)
    if w.max() == w.min():
        return stats(rets)
    w = (w - w.min()) / (w.max() - w.min())  # 0→1
    w = w + 0.5  # floor at 0.5× (still participate)
    w = w / w.mean()  # mean-normalize to 1.0

    mu = float(np.average(arr, weights=w))
    var = float(np.average((arr - mu) ** 2, weights=w))
    std = math.sqrt(var) if var > 0 else 0.0
    sharpe = round(mu / std, 4) if std > 0 and len(rets) >= 10 else None

    wins_w = float(np.sum(w[arr > 0]))
    total_w = float(np.sum(w))
    wr_w = wins_w / total_w * 100 if total_w > 0 else 0.0

    cap, peak, max_dd = 10_000.0, 10_000.0, 0.0
    for r, wi in zip(rets, (w / w.mean()).tolist()):
        cap += cap * POSITION_SIZE * wi * (r / 100)
        peak = max(peak, cap)
        max_dd = max(max_dd, (peak - cap) / peak * 100)

    return {
        "n": len(rets),
        "wr": round(wr_w, 1),
        "avg": round(mu, 2),
        "avg_win": None,
        "avg_loss": None,
        "pf": None,
        "sharpe": sharpe,
        "max_dd": round(max_dd, 2),
    }


def stats(rets: list[float]) -> dict:
    if not rets:
        return dict(_EMPTY_STATS)
    n = len(rets)
    wins = [r for r in rets if r > 0]
    loss = [r for r in rets if r <= 0]
    mu = sum(rets) / n
    std = math.sqrt(sum((r - mu) ** 2 for r in rets) / max(n - 1, 1)) if n > 1 else 0
    gp = sum(wins)
    gl = abs(sum(loss))
    pf = gp / gl if gl > 0 else float("inf")

    # Max drawdown on equity curve (5% position size)
    cap, peak, max_dd = 10_000.0, 10_000.0, 0.0
    for r in rets:
        cap += cap * POSITION_SIZE * (r / 100)
        peak = max(peak, cap)
        max_dd = max(max_dd, (peak - cap) / peak * 100)

    # Per-trade Sharpe (not annualized). Backtest returns are trade-level,
    # so applying sqrt(252) as if returns were daily is misleading.
    # Require N≥10: smaller samples produce extreme/meaningless Sharpe values
    # (e.g. GEN with N=2 produced Sharpe -54.17 from near-zero std deviation).
    sharpe = round((mu / std), 4) if std > 0 and n >= 10 else None

    return {
        "n": n,
        "wr": round(len(wins) / n * 100, 1),
        "avg": round(mu, 2),
        "avg_win": round(sum(wins) / len(wins), 2) if wins else None,
        "avg_loss": round(sum(loss) / len(loss), 2) if loss else None,
        "pf": round(pf, 2) if pf != float("inf") else None,
        "sharpe": sharpe,
        "max_dd": round(max_dd, 2),
    }


def monte_carlo(trades_df, n_sims=10000):
    returns = trades_df["net_pct"].values
    if len(returns) == 0:
        return
    sharpe_sims = []
    for _ in range(n_sims):
        sample = np.random.choice(returns, size=len(returns), replace=True)
        s = stats(sample.tolist())
        sharpe_sims.append(s.get("sharpe") or 0.0)

    p5 = np.percentile(sharpe_sims, 5)
    p95 = np.percentile(sharpe_sims, 95)
    print(f"- **Monte Carlo Sharpe (5th/95th percentile):** {p5:.2f} / {p95:.2f}")
    if p5 < 0:
        print("  > ⚠ 5th percentile < 0. Your edge might not be real.")


def fmt_pf(v):
    if v is None:
        return "∞"
    return f"{v:.2f}×"


def fmt_sharpe(v):
    return "—" if v is None else f"{v:.2f}"


def print_table(header, rows):
    print("| " + " | ".join(header) + " |")
    print("|" + "|".join("---:" if i > 0 else ":---" for i in range(len(header))) + "|")
    for row in rows:
        print("| " + " | ".join(str(x) for x in row) + " |")


# ─────────────────────────────────────────────────────────────────────────────
# Alt-data fetch helpers
# ─────────────────────────────────────────────────────────────────────────────


def fetch_spy_trend(start: str, end: str) -> dict[pd.Timestamp, int]:
    """
    Download SPY daily closes and compute a rolling SMA(200).
    Returns a regime code for each date (zero look-ahead):
      +1  confirmed bull : SPY > SMA200 × 1.02  (2%+ above)
      -1  confirmed bear : SPY < SMA200 × 0.98  (2%+ below)
       0  neutral / transition : SPY within ±2% of SMA200
    The ±2% buffer eliminates whipsaw at regime turning points —
    August-2022 bear-bounce and late-2018 collapse both live in the neutral zone.
    """
    try:
        raw = yf.download("SPY", start=start, end=end, interval="1d", auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        closes = raw["Close"].ffill()
        sma200 = closes.rolling(200).mean()
        trend = {}
        for dt, c, s in zip(closes.index, closes.values, sma200.values):
            if np.isnan(s):
                continue
            ratio = float(c) / float(s)
            if ratio > 1.02:
                regime = 1  # confirmed bull
            elif ratio < 0.98:
                regime = -1  # confirmed bear
            else:
                regime = 0  # transition zone
            trend[pd.Timestamp(str(dt)[:10])] = regime
        return trend
    except Exception as e:
        print(f"failed ({e})")
        return {}


def fetch_earnings_dates_polygon(ticker: str, api_key: str, start: str) -> set:
    """Fetch quarterly filing dates from Polygon vX/reference/financials.
    Returns a set of pd.Timestamps covering full history back to start.
    Uses filing_date as the earnings-event proxy (SEC 10-Q/10-K submission).
    Covers 2003-2022 — the gap yfinance cannot reach.
    """
    dates: set = set()
    if not api_key:
        return dates
    try:
        import requests as _req

        url = "https://api.polygon.io/vX/reference/financials"
        params = {
            "ticker": ticker,
            "timeframe": "quarterly",
            "filing_date.gte": start,
            "limit": 100,
            "order": "asc",
            "apiKey": api_key,
        }
        while True:
            r = _req.get(url, params=params, timeout=15)
            if r.status_code != 200:
                break
            body = r.json()
            for result in body.get("results") or []:
                fd = result.get("filing_date") or result.get("start_date")
                if fd:
                    dates.add(pd.Timestamp(str(fd)[:10]))
            # Polygon paginates via next_url
            next_url = body.get("next_url")
            if not next_url:
                break
            url = next_url + f"&apiKey={api_key}"
            params = {}
    except Exception:
        pass
    return dates


def fetch_stlfsi4(start: str, end: str, api_key: str) -> dict[pd.Timestamp, float]:
    """
    Fetch the St. Louis Fed Financial Stress Index (STLFSI4) from FRED.
    Weekly series → forward-filled to daily so every trading day has a value.
    Values: negative = below-average stress; > 1.0 = elevated; > 1.5 = crisis.
    """
    if not api_key:
        return {}
    try:
        import requests as _req

        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": "STLFSI4",
            "api_key": api_key,
            "file_type": "json",
            "observation_start": start,
            "observation_end": end,
        }
        r = _req.get(url, params=params, timeout=15)
        obs = r.json().get("observations", [])
        if not obs:
            return {}
        # Build weekly series
        weekly = {}
        for o in obs:
            try:
                weekly[pd.Timestamp(o["date"])] = float(o["value"])
            except (ValueError, KeyError):
                pass
        if not weekly:
            return {}
        # Forward-fill weekly → daily using a date range
        idx = pd.date_range(start=min(weekly), end=max(weekly), freq="D")
        series = pd.Series(weekly).reindex(idx).ffill()
        return {pd.Timestamp(str(k)[:10]): float(v) for k, v in series.items() if pd.notna(v)}
    except Exception as e:
        print(f"failed ({e})")
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# Parameter Sweep (Grid Search)
# ─────────────────────────────────────────────────────────────────────────────


def parameter_sweep(all_dfs, vix, spy_trend, stlfsi4):
    print("\n## Parameter Sweep (Grid Search — MR-Only mode)\n")
    results = []
    global BUY_THRESH, BUY_THRESH_MAX, SELL_THRESH, HOLD_DAYS

    orig_buy = BUY_THRESH
    orig_buy_max = BUY_THRESH_MAX
    orig_sell = SELL_THRESH
    orig_hold = HOLD_DAYS

    for buy_t in [35, 40, 45]:
        for buy_max in [55, 60, 65, 999]:
            for hold in [5, 7, 10]:
                BUY_THRESH = buy_t
                BUY_THRESH_MAX = buy_max
                HOLD_DAYS = hold

                sweep_trades = []
                for ticker, df in all_dfs.items():
                    t = simulate_ticker(ticker, df, vix, spy_trend, stlfsi4, mr_only=True)
                    if not t.empty:
                        sweep_trades.append(t)

                if sweep_trades:
                    trades_df = pd.concat(sweep_trades, ignore_index=True)
                    sv = stats(trades_df["net_pct"].tolist())
                    results.append(
                        {
                            "buy_lo": buy_t,
                            "buy_hi": buy_max,
                            "hold": hold,
                            "sharpe": round(sv.get("sharpe") or 0, 3),
                            "wr": round(sv.get("wr", 0), 1),
                            "avg": round(sv.get("avg", 0), 3),
                            "n": sv.get("n", 0),
                        }
                    )

    if results:
        res_df = pd.DataFrame(results).sort_values("sharpe", ascending=False)
        print("Full sweep results (sorted by Sharpe):\n")
        print(res_df.to_string(index=False))
        best = res_df.iloc[0]
        print(
            f"\n> Best: BUY_THRESH={int(best['buy_lo'])}, MAX={int(best['buy_hi'])}, "
            f"HOLD={int(best['hold'])} → Sharpe {best['sharpe']:.3f}, "
            f"WR {best['wr']:.1f}%, avg {best['avg']:+.3f}%, n={int(best['n'])}"
        )

    # Restore original globals
    BUY_THRESH = orig_buy
    BUY_THRESH_MAX = orig_buy_max
    SELL_THRESH = orig_sell
    HOLD_DAYS = orig_hold


# ─────────────────────────────────────────────────────────────────────────────
# Held-out OOS Validation
# ─────────────────────────────────────────────────────────────────────────────


def run_oos_validation(vix, spy_trend, stlfsi4):
    """Run the MR-only strategy on HELD_OUT_TICKERS and compare vs main universe.

    These tickers were never touched during research or gate calibration —
    any edge found here is genuinely out-of-sample.

    Interpretation guide:
      OOS Sharpe ≥ 0.10   → edge generalises; curation bias is small
      OOS Sharpe 0.00-0.10 → modest curation bias; still a real signal
      OOS Sharpe < 0.00    → main-universe results are heavily curated;
                             treat reported Sharpe with scepticism
    """
    print("\n## OOS Validation — Held-Out Universe (never seen during research)\n")
    print(f"> Tickers: {', '.join(HELD_OUT_TICKERS)}")
    print("> Same MR-Only strategy, same gates, same period — zero data-mining benefit.\n")

    args_list = [(t, vix, spy_trend, stlfsi4, True) for t in HELD_OUT_TICKERS]
    with Pool(min(8, len(HELD_OUT_TICKERS))) as p:
        results = p.map(process_ticker, args_list)

    oos_trades: list[pd.DataFrame] = []
    for ticker, t_df, _bh, _df in results:
        if t_df is not None and not t_df.empty:
            oos_trades.append(t_df)

    if not oos_trades:
        print("> [warn] No OOS trades generated — check data availability.\n")
        return

    oos = pd.concat(oos_trades, ignore_index=True)
    s = stats(oos["net_pct"].tolist())
    print_table(
        ["Metric", "OOS Value", "Interpretation"],
        [
            ["Total Trades", str(s["n"]), "held-out tickers only"],
            ["Win Rate", f"{s['wr']:.1f}%", "target ≥50% for real edge"],
            ["Avg Return / Trade", f"{s['avg']:+.2f}%", "net of 0.50% friction"],
            ["Profit Factor", fmt_pf(s["pf"]), "≥1.0 required"],
            ["Sharpe Ratio", fmt_sharpe(s["sharpe"]), "≥0.10 = edge generalises"],
            ["Max Drawdown", f"-{s['max_dd']:.2f}%", "5% position sizing"],
        ],
    )

    # Per-ticker breakdown
    print("\n### OOS Per-Ticker\n")
    rows = []
    for ticker, t_df, _bh, _df in results:
        if t_df is None or t_df.empty:
            rows.append([ticker, "0", "—", "—", "—"])
            continue
        st = stats(t_df["net_pct"].tolist())
        rows.append(
            [
                ticker,
                str(st["n"]),
                f"{st['wr']:.1f}%" if st["n"] else "—",
                f"{st['avg']:+.2f}%" if st["n"] else "—",
                fmt_sharpe(st["sharpe"]),
            ]
        )
    print_table(["Ticker", "N", "WR", "Avg Ret", "Sharpe"], rows)
    print()

    # ── OOS Score-Band Analysis ────────────────────────────────────────────────
    if "score" in oos.columns:
        _oos_sb = oos.copy()
        _oos_sb["score_band"] = pd.cut(
            _oos_sb["score"],
            bins=[BUY_THRESH - 1, 50, 60, 70, 999],
            labels=["40-50", "50-60", "60-70", "70+"],
            right=True,
        )
        print("### OOS Score-Band Analysis\n")
        sb_rows = []
        for band in ["40-50", "50-60", "60-70", "70+"]:
            sub = _oos_sb[_oos_sb["score_band"] == band]["net_pct"].tolist()
            sr = stats(sub)
            if sr["n"] == 0:
                continue
            sb_rows.append(
                [
                    str(band),
                    str(sr["n"]),
                    f"{sr['wr']:.1f}%",
                    f"{sr['avg']:+.2f}%",
                    fmt_sharpe(sr["sharpe"]),
                ]
            )
        print_table(["Score Band", "N", "WR", "Avg Ret", "Sharpe"], sb_rows)
        print()

    # ── In-Sample vs OOS verdict ───────────────────────────────────────────────
    # Compute in-sample metrics on main TICKERS (re-uses cached data from the
    # parallel run that already completed before run_oos_validation() was called).
    # We use _global_insample if available, else derive from already-run results.
    is_wr = 60.5  # §41 23yr run with 48 tickers (constant — this function is called after main run)
    is_avg = 0.57
    is_sh = 0.14
    oos_wr = s["wr"]
    oos_avg = s["avg"]
    oos_sh = s["sharpe"] or 0.0
    wr_gap = oos_wr - is_wr
    avg_gap = oos_avg - is_avg
    sh_gap = oos_sh - is_sh

    print("### OOS Verdict — Curation Bias Quantification\n")
    print_table(
        ["Metric", "In-Sample (main)", "OOS (held-out)", "Gap"],
        [
            ["Win Rate", f"{is_wr:.1f}%", f"{oos_wr:.1f}%", f"{wr_gap:+.1f}pp"],
            ["Avg Return", f"+{is_avg:.2f}%", f"{oos_avg:+.2f}%", f"{avg_gap:+.2f}pp"],
            ["Sharpe", f"{is_sh:.2f}", f"{oos_sh:.2f}", f"{sh_gap:+.2f}"],
            ["Profit Factor", "1.35×", fmt_pf(s["pf"]), ""],
        ],
    )

    _verdict_lines = [
        "",
        "**Interpretation:**",
        f"- WR gap: {wr_gap:+.1f}pp | Avg return gap: {avg_gap:+.2f}pp | Sharpe gap: {sh_gap:+.2f}",
    ]
    if oos_sh >= 0.10:
        _verdict_lines.append("- ✅ OOS Sharpe ≥ 0.10 — edge generalises; curation bias is small.")
    elif oos_sh >= 0.0:
        _verdict_lines.append("- ⚠ OOS Sharpe 0.00–0.10 — modest curation bias; signal is real but overstated.")
    else:
        _verdict_lines.append("- ⛔ OOS Sharpe < 0 — main-universe Sharpe is curated; treat with scepticism.")
    _verdict_lines += [
        "",
        "**Sector composition note:** HELD_OUT_TICKERS overlap XLI (CAT, NSC, LMT, EMR),",
        "XLV (UNH), and XLE (XOM) — sectors BLOCKED in the live delivery_gates (no MR edge",
        "confirmed in §15-§16 research). A fairer OOS test would draw from the same sectors",
        "(XLK/XLY/XLC/XLB) as the main universe — this OOS result is partially explained by",
        "sector composition rather than pure curation bias.",
    ]
    for line in _verdict_lines:
        print(line)
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Parallel Processing
# ─────────────────────────────────────────────────────────────────────────────


def process_ticker(args):
    ticker, vix, spy_trend, stlfsi4, mr_only = args
    print(f"Processing {ticker}…", flush=True)
    try:
        raw = yf.download(ticker, start=START, end=END, interval="1d", auto_adjust=True, progress=False)
        if raw.empty or len(raw) < 250:
            print(f"{ticker}: insufficient data — skipped", flush=True)
            return ticker, None, None, None

        # Flatten MultiIndex columns if present
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)

        df = raw[["Open", "High", "Low", "Close", "Volume"]].copy()
        df = df.ffill().dropna(subset=["Close", "Volume"])

        bh_return = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[0]) - 1) * 100

        # Wrap indicator computation: missing columns should not crash per-ticker.
        try:
            compute_indicators(df)
        except Exception as e:
            print(f"\n{ticker} compute_indicators error — {e}", flush=True)
            df["score"] = 0.0
            return ticker, None, None, None

        if "vwap_pct" not in df.columns:
            df["vwap_pct"] = np.nan
        if "vwap_pct_prev" not in df.columns:
            df["vwap_pct_prev"] = df["vwap_pct"].shift(1)
        if "vwap_slope_pos" not in df.columns:
            df["vwap_slope_pos"] = False

        df["score"] = compute_scores(df)

        # ── Fetch earnings dates: Polygon (full history) + yfinance (recent) ────
        # Polygon vX/reference/financials covers SEC filing dates back to 2003.
        # yfinance supplements with the most-recent ~4yr (forward earnings calendar).
        _poly_key = os.getenv("MASSIVE_API_KEY", "")
        if not _poly_key:
            _env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
            try:
                with open(_env_path) as _ef:
                    for line in _ef:
                        if line.startswith("MASSIVE_API_KEY="):
                            _poly_key = line.strip().split("=", 1)[1]
            except Exception:
                pass
        earnings_dates: set = fetch_earnings_dates_polygon(ticker, _poly_key, START)
        try:
            tkr_obj = yf.Ticker(ticker)
            cal = tkr_obj.get_earnings_dates(limit=100)
            if cal is not None and not cal.empty:
                for d in cal.index:
                    try:
                        earnings_dates.add(pd.Timestamp(str(d)[:10]))
                    except Exception:
                        pass
        except Exception:
            pass

        t = simulate_ticker(ticker, df, vix, spy_trend, stlfsi4, mr_only=mr_only, earnings_dates=earnings_dates)
        if not t.empty:
            print(f"{ticker}: {len(t)} trades", flush=True)
            return ticker, t, bh_return, df
        else:
            print(f"{ticker}: 0 trades", flush=True)
            return ticker, None, bh_return, df
    except Exception as e:
        print(f"{ticker} error — {e}", flush=True)
        return ticker, None, None, None


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main():
    years = datetime.today().year - int(START[:4])
    print("# Tier-1 Technical Backtest — Signal.Trade Engine Rules\n")
    print(f"> **Tickers:** {', '.join(TICKERS)}")
    print(f"> **Period:** {START} → {END} ({years}-year)  |  **Hold:** ≤{HOLD_DAYS} trading days")
    print(
        f"> **Entry:** BUY score ≥{BUY_THRESH} · SELL score ≤{SELL_THRESH}  |  **Friction:** {FRICTION_PCT}% round-trip"
    )
    print("> **Stops/targets:** ATR-based swing style (tighter stops; extended targets in strong ADX trends)")
    print("> _Technical + macro alt-data (SPY trend, STLFSI4, VIX tiers). No news/options/fundamentals._")
    print("> **Earnings blackout:** Polygon vX/reference/financials (full history) + yfinance (recent ~4yr).")
    print(">   SEC filing dates used as earnings-event proxy. Pre-2003 data unavailable.")
    print("> ⚠ **Survivorship bias:** Universe is drawn from *current* S&P 500 survivors.")
    print(">   Companies that delisted, went bankrupt, or were removed 2003–2026 (Lehman, Sears,")
    print(">   Bear Stearns, etc.) are absent. Reported WR and avg return are therefore overstated")
    print(">   vs. a point-in-time historical constituent list. Fix requires Norgate/Sharadar data.\n")

    # ── Download VIX ─────────────────────────────────────────────────────────
    print("Fetching VIX…", end=" ", flush=True)
    try:
        vix_df = yf.download("^VIX", start=START, end=END, interval="1d", auto_adjust=False, progress=False)
        if isinstance(vix_df.columns, pd.MultiIndex):
            vix_df.columns = vix_df.columns.get_level_values(0)
        vix_series = vix_df["Close"] if "Close" in vix_df.columns else pd.Series(dtype=float)
        vix = {pd.Timestamp(str(k)[:10]): float(v) for k, v in vix_series.items() if pd.notna(v)}
        print(f"ok ({len(vix)} bars)")
    except Exception as e:
        vix = {}
        print(f"failed ({e}) — VIX gate disabled")

    # ── SPY macro trend ───────────────────────────────────────────────────────
    print("Fetching SPY macro trend…", end=" ", flush=True)
    spy_trend = fetch_spy_trend(START, END)
    bull_days = sum(1 for v in spy_trend.values() if v == 1)
    bear_days = sum(1 for v in spy_trend.values() if v == -1)
    neut_days = sum(1 for v in spy_trend.values() if v == 0)
    print(f"ok ({len(spy_trend)} bars — bull {bull_days}d / neutral {neut_days}d / bear {bear_days}d)")

    # ── FRED STLFSI4 financial stress index ───────────────────────────────────
    print("Fetching FRED STLFSI4…", end=" ", flush=True)
    _fred_key = os.getenv("FRED_API_KEY", "")
    if not _fred_key:
        # Try loading from backend/.env directly
        _env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        try:
            with open(_env_path) as _ef:
                for line in _ef:
                    if line.startswith("FRED_API_KEY="):
                        _fred_key = line.strip().split("=", 1)[1]
        except Exception:
            pass
    stlfsi4 = fetch_stlfsi4(START, END, _fred_key)
    print(f"ok ({len(stlfsi4)} daily obs)" if stlfsi4 else "skipped (no FRED_API_KEY)")

    # ── Download price data and compute signals ───────────────────────────────
    all_trades: list[pd.DataFrame] = []
    bh_returns = []
    all_dfs = {}

    mode_label = "MR-Only" if BACKTEST_MR_DEFAULT else "Full-Signal"
    print(f"\nRunning in **{mode_label}** mode (BACKTEST_MR_DEFAULT={BACKTEST_MR_DEFAULT})")
    if BACKTEST_MR_DEFAULT:
        print(f"  MR gate: RSI<{MR_RSI_CEIL} OR BB%B<{MR_BB_CEIL} OR IBS<{MR_IBS_CEIL} OR VWAP%<{MR_VWAP_FLOOR}%\n")

    args_list = [(t, vix, spy_trend, stlfsi4, BACKTEST_MR_DEFAULT) for t in TICKERS]

    with Pool(8) as p:
        results = p.map(process_ticker, args_list)

    for ticker, t_df, bh_ret, df in results:
        if bh_ret is not None:
            bh_returns.append(bh_ret)
        if df is not None:
            all_dfs[ticker] = df
        if t_df is not None and not t_df.empty:
            all_trades.append(t_df)

    if not all_trades:
        print("\n[error] No trades generated.")
        return

    trades = pd.concat(all_trades, ignore_index=True)
    trades["year"] = trades["date"].dt.year
    print(f"\nTotal simulated trades: {len(trades)}\n")

    # ─────────────────────────────────────────────────────────────────────────
    # §1. Overall summary
    # ─────────────────────────────────────────────────────────────────────────
    print(f"## 1. Overall Performance ({years}-year, Technical-Only)\n")
    s = stats(trades["net_pct"].tolist())
    print_table(
        ["Metric", "Value", "Note"],
        [
            ["Total Trades", str(s["n"]), "across all tickers, non-overlapping per ticker"],
            ["Win Rate", f"{s['wr']:.1f}%", "net of 0.50% friction"],
            ["Avg Return / Trade", f"{s['avg']:+.2f}%", "net"],
            ["Avg Win", f"{s['avg_win']:+.2f}%" if s["avg_win"] else "—", ""],
            ["Avg Loss", f"{s['avg_loss']:+.2f}%" if s["avg_loss"] else "—", ""],
            ["Profit Factor", fmt_pf(s["pf"]), "gross profit / gross loss"],
            ["Sharpe Ratio", fmt_sharpe(s["sharpe"]), "per-trade Sharpe (not annualized)"],
            ["Max Drawdown", f"-{s['max_dd']:.2f}%", "5% position sizing"],
        ],
    )

    # ─────────────────────────────────────────────────────────────────────────
    # §2. BUY vs SELL
    # ─────────────────────────────────────────────────────────────────────────
    print("\n## 2. BUY vs SELL\n")
    rows = []
    for action in ["BUY", "SELL"]:
        sub = trades[trades["action"] == action]["net_pct"].tolist()
        s2 = stats(sub)
        rows.append(
            [
                f"**{action}**",
                str(s2["n"]),
                f"{s2['wr']:.1f}%",
                f"{s2['avg']:+.2f}%",
                fmt_pf(s2["pf"]),
                fmt_sharpe(s2["sharpe"]),
                f"-{s2['max_dd']:.2f}%",
            ]
        )
    print_table(["Action", "N", "Win Rate", "Avg Ret", "PF", "Sharpe", "Max DD"], rows)

    # ─────────────────────────────────────────────────────────────────────────
    # §3. Exit-type breakdown
    # ─────────────────────────────────────────────────────────────────────────
    print("\n## 3. Exit-Type Breakdown\n")
    rows = []
    for reason in ["target", "stop", "time", "time_loss", "adaptive"]:
        sub_df = trades[trades["exit_reason"] == reason]
        sub = sub_df["net_pct"].tolist()
        s3 = stats(sub)
        pct_of_total = len(sub) / len(trades) * 100
        # Capture rate: what fraction of the MFE (max favorable excursion) the
        # exit actually captured. 100% WR on adaptive is definitional (profit
        # threshold filter). Capture rate is the honest signal — did the exit
        # lock in most of the available move?
        capture_str = "—"
        if reason == "adaptive" and s3["n"] > 0 and "mfe_pct" in sub_df.columns:
            _mfe_arr = sub_df["mfe_pct"].values
            _ret_arr = sub_df["gross_pct"].values
            _valid = _mfe_arr > 0
            if _valid.sum() > 0:
                _cr = float((_ret_arr[_valid] / _mfe_arr[_valid]).mean()) * 100
                capture_str = f"{_cr:.0f}%"
        rows.append(
            [
                f"**{reason.capitalize()}**",
                str(s3["n"]),
                f"{pct_of_total:.1f}%",
                f"{s3['wr']:.1f}%" if s3["n"] else "—",
                f"{s3['avg']:+.2f}%" if s3["n"] else "—",
                capture_str,
            ]
        )
    print_table(["Exit", "N", "% of Total", "Win Rate", "Avg Ret", "MFE Capture"], rows)
    print("> _MFE Capture (adaptive only): avg fraction of maximum favorable excursion captured._")
    print("> _100% WR on adaptive exits is definitional — profit threshold is a prerequisite to fire._")

    # ─────────────────────────────────────────────────────────────────────────
    # §4. Regime breakdown — the key insight
    # ─────────────────────────────────────────────────────────────────────────
    print("\n## 4. Regime Breakdown — Does the Edge Survive Market Cycles?\n")
    rows = []
    for name, start, end in REGIMES:
        mask = (trades["date"] >= pd.Timestamp(start)) & (trades["date"] <= pd.Timestamp(end))
        sub = trades[mask]["net_pct"].tolist()
        s4 = stats(sub)
        if s4["n"] == 0:
            rows.append([name, "0", "—", "—", "—", "—", "—"])
        else:
            sharpe_str = fmt_sharpe(s4["sharpe"])
            # Flag regimes where edge collapses
            flag = ""
            if s4["wr"] < 45:
                flag = " ⚠"
            if s4["avg"] < 0:
                flag = " ✗"
            rows.append(
                [
                    name,
                    str(s4["n"]),
                    f"{s4['wr']:.1f}%{flag}",
                    f"{s4['avg']:+.2f}%{flag}",
                    fmt_pf(s4["pf"]),
                    sharpe_str,
                    f"-{s4['max_dd']:.2f}%",
                ]
            )
    print_table(
        ["Regime", "N", "Win Rate", "Avg Ret", "PF", "Sharpe", "Max DD"],
        rows,
    )
    print("\n> ⚠ = WR < 45% (marginal) · ✗ = negative avg return (edge absent)")

    # ─────────────────────────────────────────────────────────────────────────
    # §5. Annual summary (last 5 years detail)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n## 5. Annual Performance\n")
    rows = []
    for yr in sorted(trades["year"].unique()):
        sub = trades[trades["year"] == yr]["net_pct"].tolist()
        s5 = stats(sub)
        flag = " ⚠" if s5["wr"] < 45 else ""
        flag = " ✗" if s5["avg"] < 0 else flag
        rows.append(
            [
                str(yr),
                str(s5["n"]),
                f"{s5['wr']:.1f}%{flag}",
                f"{s5['avg']:+.2f}%",
                fmt_sharpe(s5["sharpe"]),
                f"-{s5['max_dd']:.2f}%",
            ]
        )
    print_table(["Year", "N", "Win Rate", "Avg Ret", "Sharpe", "Max DD"], rows)

    # ─────────────────────────────────────────────────────────────────────────
    # §6. Per-ticker breakdown
    # ─────────────────────────────────────────────────────────────────────────
    print("\n## 6. Per-Ticker Performance\n")
    rows = []
    for ticker in sorted(trades["ticker"].unique()):
        sub = trades[trades["ticker"] == ticker]["net_pct"].tolist()
        s6 = stats(sub)
        rows.append(
            [
                ticker,
                str(s6["n"]),
                f"{s6['wr']:.1f}%",
                f"{s6['avg']:+.2f}%",
                fmt_sharpe(s6["sharpe"]),
                f"-{s6['max_dd']:.2f}%",
            ]
        )
    rows.sort(key=lambda x: float(x[3].replace("+", "").replace("%", "")), reverse=True)
    print_table(["Ticker", "N", "Win Rate", "Avg Ret", "Sharpe", "Max DD"], rows)

    # ─────────────────────────────────────────────────────────────────────────
    # §7. Live vs backtest gap
    # ─────────────────────────────────────────────────────────────────────────
    print("\n## 7. Live Engine vs Technical-Only Backtest\n")
    print_table(
        ["Metric", "Live Engine (3-wk)", f"Tech + Macro Backtest ({years}y)", "Gap"],
        [
            ["Trades", "529", str(s["n"]), "—"],
            ["Win Rate", "42.2%", f"{s['wr']:.1f}%", f"{s['wr'] - 42.2:+.1f}pp"],
            ["Avg Return", "  +0.45%", f"{s['avg']:+.2f}%", f"{s['avg'] - 0.45:+.2f}pp"],
            ["Sharpe", "5.67", fmt_sharpe(s["sharpe"]), "—"],
        ],
    )
    print("\n> Gap = value of news, options, fundamentals, and alt-data stack on top of pure technical rules.")

    # ─────────────────────────────────────────────────────────────────────────
    # §8. Key findings
    # ─────────────────────────────────────────────────────────────────────────
    gfc_mask = (trades["date"] >= pd.Timestamp("2007-10-09")) & (trades["date"] <= pd.Timestamp("2009-03-09"))
    gfc = stats(trades[gfc_mask]["net_pct"].tolist())
    rh_mask = (trades["date"] >= pd.Timestamp("2022-01-01")) & (trades["date"] <= pd.Timestamp("2022-12-31"))
    rh = stats(trades[rh_mask]["net_pct"].tolist())
    ai_mask = (trades["date"] >= pd.Timestamp("2023-01-01")) & (trades["date"] <= pd.Timestamp("2024-12-31"))
    ai = stats(trades[ai_mask]["net_pct"].tolist())

    print("\n## 8. Key Findings\n")
    print(
        f"- **20-year win rate:** {s['wr']:.1f}% (net after friction) — "
        + (
            "edge is present across full cycle."
            if s["wr"] >= 50
            else "marginal — technical rules alone are below coin-flip."
        )
    )
    if gfc["n"] > 0:
        print(
            f"- **GFC Bear (2007-09):** {gfc['wr']:.1f}% WR, avg {gfc['avg']:+.2f}% — "
            + (
                "edge collapsed in crisis. VIX gate blocks the worst entries."
                if gfc["avg"] < 0
                else "rules held surprisingly well."
            )
        )
    if rh["n"] > 0:
        print(
            f"- **Rate-Hike Bear (2022):** {rh['wr']:.1f}% WR, avg {rh['avg']:+.2f}% — "
            + (
                "long-biased rules suffered in 2022 bear. A macro-trend filter (SMA200 gate) would help."
                if rh["avg"] < 0
                else "rules survived 2022."
            )
        )
    if ai["n"] > 0:
        print(
            f"- **AI Rally (2023-24):** {ai['wr']:.1f}% WR, avg {ai['avg']:+.2f}% — "
            + ("strong performance in trend-following regime." if ai["avg"] > 1 else "moderate performance.")
        )
    print(
        f"- **Sharpe {fmt_sharpe(s['sharpe'])} (technical-only) vs 5.67 live** — "
        "difference quantifies alt-data contribution."
    )
    print(f"- **Max Drawdown:** -{s['max_dd']:.2f}% (5% sizing) across 20 years.")
    monte_carlo(trades)

    if bh_returns:
        print(f"\nBuy-and-Hold avg: {np.mean(bh_returns):+.1f}%")
        print(f"Strategy total: {sum(trades['net_pct']):+.1f}%")

    # ─────────────────────────────────────────────────────────────────────────
    # §9. Full-Signal comparison — reuses all_dfs, no re-download.
    # The main run (§1-§8) ran in MR-only mode. §9 reruns with mr_only=False
    # to quantify the contribution of the MR gate.
    # ─────────────────────────────────────────────────────────────────────────
    if all_dfs and BACKTEST_MR_DEFAULT:
        print("\n## 9. Full-Signal Comparison (no MR filter)\n")
        print("> Reuses downloaded price data — no extra network calls.")
        print(f"> Same gates as main run except MR gate is OFF. BUY_THRESH={BUY_THRESH}, HOLD_DAYS={HOLD_DAYS}.\n")

        full_list = []
        for ticker_k, df_k in all_dfs.items():
            t_full = simulate_ticker(ticker_k, df_k, vix, spy_trend, stlfsi4, mr_only=False)
            if not t_full.empty:
                full_list.append(t_full)

        if not full_list:
            print("[no full-mode trades generated]\n")
        else:
            full = pd.concat(full_list, ignore_index=True)
            full["year"] = full["date"].dt.year
            s_full = stats(full["net_pct"].tolist())

            # ── 9a. Head-to-head ──────────────────────────────────────────────
            print("### 9a. MR-Only (main) vs Full-Signal — Overall\n")
            print_table(
                ["Metric", "MR-Only (§1-§8)", "Full-Signal", "MR Edge"],
                [
                    ["N Trades", str(s["n"]), str(s_full["n"]), "—"],
                    ["Win Rate", f"{s['wr']:.1f}%", f"{s_full['wr']:.1f}%", f"{s['wr'] - s_full['wr']:+.1f}pp"],
                    ["Avg Return", f"{s['avg']:+.2f}%", f"{s_full['avg']:+.2f}%", f"{s['avg'] - s_full['avg']:+.2f}pp"],
                    [
                        "Avg Win",
                        f"{s['avg_win']:+.2f}%" if s["avg_win"] else "—",
                        f"{s_full['avg_win']:+.2f}%" if s_full["avg_win"] else "—",
                        "",
                    ],
                    [
                        "Avg Loss",
                        f"{s['avg_loss']:+.2f}%" if s["avg_loss"] else "—",
                        f"{s_full['avg_loss']:+.2f}%" if s_full["avg_loss"] else "—",
                        "",
                    ],
                    ["Profit Factor", fmt_pf(s["pf"]), fmt_pf(s_full["pf"]), ""],
                    [
                        "Sharpe",
                        fmt_sharpe(s["sharpe"]),
                        fmt_sharpe(s_full["sharpe"]),
                        f"{(s.get('sharpe') or 0) - (s_full.get('sharpe') or 0):+.2f}",
                    ],
                    ["Max DD", f"-{s['max_dd']:.2f}%", f"-{s_full['max_dd']:.2f}%", ""],
                ],
            )

            # ── 9b. Regime comparison ─────────────────────────────────────────
            print("\n### 9b. Regime Comparison: MR-Only vs Full-Signal\n")
            reg_rows = []
            for rname, rstart, rend in REGIMES:
                mask = (trades["date"] >= pd.Timestamp(rstart)) & (trades["date"] <= pd.Timestamp(rend))
                mask_f = (full["date"] >= pd.Timestamp(rstart)) & (full["date"] <= pd.Timestamp(rend))
                sr_mr = stats(trades[mask]["net_pct"].tolist())
                sr_full = stats(full[mask_f]["net_pct"].tolist())
                if sr_mr["n"] == 0 and sr_full["n"] == 0:
                    continue
                reg_rows.append(
                    [
                        rname,
                        f"{sr_mr['n']} / {sr_full['n']}",
                        f"{sr_mr['wr']:.1f}% / {sr_full['wr']:.1f}%",
                        f"{sr_mr['avg']:+.2f}% / {sr_full['avg']:+.2f}%",
                        f"{fmt_sharpe(sr_mr['sharpe'])} / {fmt_sharpe(sr_full['sharpe'])}",
                    ]
                )
            print_table(["Regime", "N (MR/Full)", "WR (MR/Full)", "Avg (MR/Full)", "Sharpe (MR/Full)"], reg_rows)

            # ── 9c. Score-band analysis (MR-only) ────────────────────────────
            print("\n### 9c. Score-Band Analysis — MR-Only\n")
            trades["score_band"] = pd.cut(
                trades["score"],
                bins=[BUY_THRESH - 1, 50, 60, 70, 999],
                labels=["40-50", "50-60", "60-70", "70+"],
                right=True,
            )
            band_rows = []
            for band in ["40-50", "50-60", "60-70", "70+"]:
                sub = trades[trades["score_band"] == band]["net_pct"].tolist()
                sr = stats(sub)
                if sr["n"] == 0:
                    continue
                band_rows.append(
                    [
                        str(band),
                        str(sr["n"]),
                        f"{sr['wr']:.1f}%",
                        f"{sr['avg']:+.2f}%",
                        fmt_sharpe(sr["sharpe"]),
                        fmt_pf(sr["pf"]),
                    ]
                )
            print_table(["Score Band", "N", "Win Rate", "Avg Ret", "Sharpe", "PF"], band_rows)

            print("\n> **Full-Signal Monte Carlo:**")
            monte_carlo(full)

    # ── §10. Delivery-Gates-Aligned Sector Filter ─────────────────────────────
    # Show results filtered to only the sectors the live delivery_gates allows.
    # Blocked live sectors: XLI, XLV, XLE, XLRE, XLU.
    # Tickers in the main universe that fall in blocked sectors (ROP/TDY/TEL/
    # FDX/MMM/EMR) are excluded here to reveal what the live engine actually sees.
    if all_dfs and trades is not None and not trades.empty:
        _allowed = [t for t in trades["ticker"].unique() if TICKER_TO_SECTOR.get(t, "XLK") not in _BLOCKED_SECTORS]
        _blocked_tkrs = [t for t in trades["ticker"].unique() if TICKER_TO_SECTOR.get(t, "XLK") in _BLOCKED_SECTORS]
        trades_sf = trades[trades["ticker"].isin(_allowed)]
        if not trades_sf.empty:
            sf = stats(trades_sf["net_pct"].tolist())
            sa = stats(trades["net_pct"].tolist())
            print("\n## 10. Delivery-Gates-Aligned Results (Sector Filter)\n")
            print(
                f"> Removed {len(_blocked_tkrs)} ticker(s) from blocked sectors "
                f"(XLI/XLV/XLE): {', '.join(sorted(_blocked_tkrs)) or 'none'}\n"
            )
            print_table(
                ["Metric", "All Tickers (§1)", "Sector-Filtered", "Δ"],
                [
                    ["N Trades", str(sa["n"]), str(sf["n"]), ""],
                    ["Win Rate", f"{sa['wr']:.1f}%", f"{sf['wr']:.1f}%", f"{sf['wr'] - sa['wr']:+.1f}pp"],
                    ["Avg Return", f"{sa['avg']:+.2f}%", f"{sf['avg']:+.2f}%", f"{sf['avg'] - sa['avg']:+.2f}pp"],
                    [
                        "Sharpe",
                        fmt_sharpe(sa["sharpe"]),
                        fmt_sharpe(sf["sharpe"]),
                        f"{(sf['sharpe'] or 0) - (sa['sharpe'] or 0):+.2f}",
                    ],
                    ["Max DD", f"-{sa['max_dd']:.2f}%", f"-{sf['max_dd']:.2f}%", ""],
                    ["Prof Factor", fmt_pf(sa["pf"]), fmt_pf(sf["pf"]), ""],
                ],
            )
            # Score-band breakdown for sector-filtered trades
            trades_sf = trades_sf.copy()
            trades_sf["score_band"] = pd.cut(
                trades_sf["score"],
                bins=[BUY_THRESH - 1, 50, 60, 70, 999],
                labels=["40-50", "50-60", "60-70", "70+"],
                right=True,
            )
            print("\n### 10a. Score-Band (Sector-Filtered Only)\n")
            sf_band_rows = []
            for band in ["40-50", "50-60", "60-70", "70+"]:
                sub = trades_sf[trades_sf["score_band"] == band]["net_pct"].tolist()
                sr = stats(sub)
                if sr["n"] == 0:
                    continue
                sf_band_rows.append(
                    [
                        str(band),
                        str(sr["n"]),
                        f"{sr['wr']:.1f}%",
                        f"{sr['avg']:+.2f}%",
                        fmt_sharpe(sr["sharpe"]),
                        fmt_pf(sr["pf"]),
                    ]
                )
            print_table(["Score Band", "N", "Win Rate", "Avg Ret", "Sharpe", "PF"], sf_band_rows)

    if "--oos" in sys.argv or "--sweep" in sys.argv:
        run_oos_validation(vix, spy_trend, stlfsi4)

    if "--sweep" in sys.argv:
        parameter_sweep(all_dfs, vix, spy_trend, stlfsi4)


if __name__ == "__main__":
    main()
