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
    python scripts/backtest_technicals.py             # IS run (default)
    python scripts/backtest_technicals.py --oos       # OOS v4 validation (18 tickers)
    python scripts/backtest_technicals.py --sweep     # BUY_THRESH / HOLD_DAYS grid search
    python scripts/backtest_technicals.py --gate-sweep  # §59–§82 threshold sensitivity
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

# 100-ticker universe (expanded 2026-05-31: 68→100).
# XLK 25 / XLF 16 / XLY 21 / XLC 7 / XLB 9 / XLV 9 / XLE 6 / XLI 5 / XLP 2.
# XLV/XLE/XLI/XLP tickers are blocked in the live engine (§10 sector filter) —
# they appear here for IS backtest research only (gate calibration, Sharpe decomp).
# Removed systematic underperformers: ABBV, TMO, NKE (OOS), TXN, BAC (re-added §18),
# QCOM (re-added §18), AMZN (re-added §18), MRK (re-added §18), PG (re-added §18),
# COST (re-added §18), PFE, BRK-B, WMT, KO (re-added §18).
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
    # MRVL removed: IS −6.65% avg — infrastructure semi shows continuation, not MR
    # LRCX removed: IS −7.20% avg — semi equipment cycle multi-quarter, not 10-day
    "CSCO",  # Networking; slow but reliable MR
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
    "DIS",  # Walt Disney — sentiment-driven MR on streaming/parks cycles
    "T",  # AT&T — range-bound dividend stock; reliable MR oscillator
    "VZ",  # Verizon — similar cadence to T; telecom range-bound MR
    # ── §40 OOS promotions ────────────────────────────────────────────────────
    # LOW/FDX/MMM/EMR previously lived here but are now in _GRADUATED_TICKERS.
    # Moving OOS-tested tickers into IS contaminates both sets: the IS Sharpe
    # includes OOS-positive-selected names, and the remaining OOS is negatively
    # selected (everything that wasn't good enough to promote). Both biases
    # inflate reported IS and deflate OOS, masking the true curation gap.
    # ── Balance expansion (2026-05-29) ───────────────────────────────────────
    # XLB Materials — was 1 ticker; filling to 6 for sector balance
    "LIN",  # Linde — industrial gases; ultra-low idio-vol, clean compounder MR
    "SHW",  # Sherwin-Williams — wide moat; smooth trend MR on pullbacks
    "APD",  # Air Products — industrial gases peer; similar MR cadence to LIN
    "ECL",  # Ecolab — water/hygiene; very stable, reliable MR bounces
    "NUE",  # Nucor — steel cyclical; high MR amplitude on demand cycles
    # XLF additions — Visa/AXP/SPGI for payment/data MR (no earnings-binary risk)
    "V",  # Visa — payments network; smooth compounder; MR on rate fears
    "AXP",  # American Express — consumer spend proxy; strong MR on pullbacks
    "SPGI",  # S&P Global — data/ratings; predictable earnings, clean MR
    # XLY additions — travel + auto + off-price
    "BKNG",  # Booking Holdings — travel demand cycles; high-beta MR bounces
    "GM",  # General Motors — auto cyclical; oversold bounces well-defined
    "TJX",  # TJX Companies — off-price retail; smooth compounder MR
    # XLK addition — Arista for networking/cloud adjacent
    "ANET",  # Arista Networks — cloud networking; earnings-driven MR cycles
    # ── Universe expansion to 100 tickers (2026-05-31) ──────────────────────────
    # XLK additions — software/services/legacy tech
    "INTU",  # Intuit — financial software; earnings-driven MR on guidance misses
    "WDAY",  # Workday — cloud HCM/ERP; guidance-miss MR; S&P 500 since 2014
    "IBM",  # IBM — range-bound legacy tech; consistent pullback/recovery cycles
    "MSI",  # Motorola Solutions — defense/public safety tech; clean MR
    # XLF additions — exchange operators + insurance + consumer credit
    "ICE",  # Intercontinental Exchange — exchange/data operator; range-bound MR
    "CME",  # CME Group — exchange operator; vol-of-vol driven MR
    "TROW",  # T. Rowe Price — asset manager; AUM-correlated MR pullbacks
    "COF",  # Capital One — consumer credit; delinquency-fear-driven oversold bounces
    "CB",  # Chubb — P&C insurance; CAT-event oversold bounces
    # XLY additions — homebuilders + auto-parts + dining + specialty retail
    "CMG",  # Chipotle — earnings-driven MR; S&P 500 since 2012 (adj prices handle split)
    "PHM",  # PulteGroup — homebuilder; rate-cycle MR parallel to DHI
    "LEN",  # Lennar — homebuilder; permits/rate-cycle MR
    "ORLY",  # O'Reilly Auto Parts — smooth compounder; durable earnings MR
    "DRI",  # Darden Restaurants — dining chains; sentiment + earnings MR
    "ULTA",  # Ulta Beauty — specialty retail; consumer sentiment MR
    # XLC additions — cable/gaming/advertising
    "CMCSA",  # Comcast — cable/streaming; range-bound MR around cord-cutting fears
    "EA",  # Electronic Arts — gaming; earnings-cycle MR
    "IPG",  # Interpublic Group — advertising; stable range-bound MR
    # XLB additions — fertilizer/aggregates/specialty chemicals
    "CF",  # CF Industries — fertilizer; nat-gas/crop-price commodity-cycle MR
    "MLM",  # Martin Marietta Materials — aggregates; construction-cycle MR
    "CE",  # Celanese — specialty chemicals; S&P 500 since 2010; cycle MR
    # XLV Healthcare (§10 removes — blocked in live engine; backtest research only)
    "JNJ",  # Johnson & Johnson — pharma/medtech compounder; classic MR anchor
    "MRK",  # Merck — pharma; patent-cycle MR on pipeline news
    "LLY",  # Eli Lilly — high-growth pharma; MR on sentiment swings
    "UNH",  # UnitedHealth — managed care; steady compounder MR
    "ABT",  # Abbott — medtech/diagnostics; smooth compounder MR
    "BSX",  # Boston Scientific — medtech; earnings-driven MR cycles
    "AMGN",  # Amgen — large biotech; stable enough for MR; S&P 500 since 1994
    "CI",  # Cigna — managed care peer to UNH; earnings-driven MR
    "HCA",  # HCA Healthcare — hospital operator; volume-cycle MR; S&P 500 since 2015
    # XLE Energy (§10 removes — blocked in live engine; backtest research only)
    "XOM",  # ExxonMobil — mega-cap energy; oil-cycle MR
    "CVX",  # Chevron — stable major; cleaner MR than XOM
    "COP",  # ConocoPhillips — E&P; high-beta oil MR
    "SLB",  # SLB (Schlumberger) — oilfield services; oil-activity-cycle MR
    "EOG",  # EOG Resources — E&P; commodity-cycle MR; S&P 500 since 2000
    "MPC",  # Marathon Petroleum — refining; crack-spread-cycle MR
    # XLI additions (§10 removes — blocked in live engine; backtest research only)
    "HON",  # Honeywell — diversified industrial; steady compounder MR
    "RTX",  # RTX Corp (Raytheon) — defense/aerospace; backlog-driven MR
    "CAT",  # Caterpillar — machinery; global construction/mining cycle MR
    "DE",  # Deere — agricultural machinery; seasonal demand-cycle MR
    "LMT",  # Lockheed Martin — defense; backlog-driven smooth MR
    # XLP Consumer Staples (live delivery_gates blocks; §10 does not — research only)
    "PG",  # Procter & Gamble — ultra-stable staples; very tight MR oscillator
    "KO",  # Coca-Cola — range-bound staples compounder; classic MR instrument
    # ── §ETF-EXP Research note (2026-05-29): sector ETFs EXCLUDED from IS universe ──
    # Tested SPY/QQQ/IWM/XLK/XLY/XLB/XLI: all showed WR 33–50%, avg −0.51 to −0.96%.
    # ETFs are too efficiently arbed — BB%B/IBS/VWAP% MR signals calibrated on individual
    # stock volatility do not persist at index level. XLF/XLV/XLE showed positive results
    # (WR 80–100%) but N=1–5 is not significant. ETF MR requires separate signal calibration.
]

# ── Graduated tickers — EXCLUDED from both IS and OOS ────────────────────────
# These tickers were previously in HELD_OUT_TICKERS (OOS), showed positive OOS
# results in §40, and were moved into IS. Placing OOS-selected tickers into IS
# contaminates both sets: IS gains a positive-selection bias and OOS loses those
# tickers, leaving only negatively-selected survivors in the OOS pool. Both
# distort the IS-vs-OOS curation-bias verdict.
# Resolution: quarantine them in a third bucket. Their historical performance is
# known (OOS WR: LOW 62.5%, FDX 66.7%, MMM 100% N=5, EMR 75%) and must not be
# re-used without fresh forward data. Do NOT add these to HELD_OUT_TICKERS.
_GRADUATED_TICKERS: list[str] = ["LOW", "FDX", "MMM", "EMR"]

# ── Curated-out tickers (removed because they dragged IS Sharpe) ─────────────
# Restored below as _CURATED_OUT_TICKERS for the optional full-universe curation
# bias report (run with --full-universe flag). These 14 tickers were dropped from
# TICKERS explicitly because they underperformed in IS — a form of data snooping
# that inflates the reported IS Sharpe. The curation bias = IS(curated) − IS(full).
_CURATED_OUT_TICKERS: list[str] = [
    "ABBV",
    "TMO",
    "NKE",
    "TXN",
    "BAC",
    "V",
    "AMZN",
    "MRK",
    "PG",
    "COST",
    "PFE",
    "WMT",
    "KO",
    # TSLA, SBUX, MCD, GS, C, MA, SCHW, BLK also removed — see TICKERS comments
    "TSLA",
    "SBUX",
]

# ── Held-out OOS validation universe — v5: same-sector, live-block aware ──────
# v1: confounded — 6/10 from XLI/XLV/XLE (blocked sectors in delivery_gates).
# v2: included MS (XLF) — MS is blocked by BLOCKED_TICKERS; biased OOS.
# v3: XLK/XLY/XLC/XLB only — 10 tickers, N=14 (±13pp SE on WR, too noisy).
# v4: +8 tickers (XLK/XLY/XLB/XLF) → 18 total. Result: N=22, Sharpe=−0.08.
#     KLAC/AMAT are in live BLOCKED_TICKERS but fired in OOS, inflating gap.
# v5: +3 tickers (XLK: AVGO/ACN; XLY: MCD) → 21 total.
#     run_oos_validation() now reports two metrics: raw (all) and clean (ex-blocked).
#     Target: N≥30 clean trades → SE ≤ ±9pp on WR.
# All tickers: S&P 500 members since ≥2007, never touched in any IS research.
# BLOCKED_TICKERS (KLAC/AMAT) are kept in list — `run_oos_validation` excludes them
# automatically from the "clean" result and prints a side-by-side comparison.
HELD_OUT_TICKERS = [
    # XLK — Technology (same sector as NVDA/MSFT/AAPL/AMD block)
    "ORCL",  # Oracle — enterprise SaaS/cloud; same cadence as MSFT/CRM
    "AMAT",  # Applied Materials — semi equipment; IN BLOCKED_TICKERS (excluded from clean)
    "KLAC",  # KLA Corp — semi equipment; IN BLOCKED_TICKERS (excluded from clean)
    "NOW",  # ServiceNow — workflow SaaS; same sector as CRM/ADBE
    "ADSK",  # Autodesk — CAD/PLM SaaS; S&P 500 since 2007; design-tool MR cycles
    "SNPS",  # Synopsys — EDA tools; same MR cadence as CDNS (IS); S&P 500 since 2017
    "AVGO",  # Broadcom — chip/infrastructure; S&P 500 since 2013; v5 addition
    "ACN",  # Accenture — IT services; S&P 500 since 2011; CTSH peer (IS); v5 addition
    # XLY — Consumer Discretionary (same sector as HD/TGT/LULU block)
    "NKE",  # Nike — athletic retail; pullbacks on guidance misses → bounce
    "DHI",  # D.R. Horton — homebuilder; rate-driven MR cycles
    "APTV",  # Aptiv — auto tech; cyclical demand-driven MR
    "BWA",  # BorgWarner — auto parts; same cycle as F/GM (IS); long S&P 500 member
    "YUM",  # Yum Brands — restaurants; long S&P 500 member; consumer sentiment MR
    "MCD",  # McDonald's — global restaurants; long S&P 500 history; YUM sector peer; v5 addition
    # XLC — Communication (same sector as GOOG/META/NFLX)
    "CHTR",  # Charter Communications — cable; sentiment-driven MR
    "TTWO",  # Take-Two Interactive — gaming; earnings-driven MR
    # XLB — Materials (same sector as LIN/SHW/NUE block)
    "FCX",  # Freeport-McMoRan — copper/gold miner; commodity-cycle MR; long history
    "PPG",  # PPG Industries — paints/coatings; long S&P 500 history; SHW peer-sector MR
    "IFF",  # Int'l Flavors & Fragrances — specialty chemicals; LIN/ECL sector peer
    # XLF — Financials (not blocked in delivery_gates; same as JPM/WFC/BAC in IS)
    "STT",  # State Street — financial services; custody bank MR on rate cycles
    "MTB",  # M&T Bank — regional bank; same MR cadence as FITB/KEY/RF (IS)
]

# Live-blocked tickers that appear in HELD_OUT_TICKERS — excluded from "clean" OOS metrics.
# Included in full list so their trade count is visible; excluded from the headline Sharpe.
_OOS_BLOCKED_TICKERS: frozenset[str] = frozenset({"AMAT", "KLAC", "STT", "MTB"})

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
    "CSCO": "XLK",
    "CDNS": "XLK",
    "CRM": "XLK",
    "CTSH": "XLK",
    "NTAP": "XLK",
    "FIS": "XLK",
    # OOS v5 additions (XLK)
    "AVGO": "XLK",
    "ACN": "XLK",
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
    "FCX": "XLB",
    # XLF — Financials
    "JPM": "XLF",
    "WFC": "XLF",
    "BAC": "XLF",
    "BX": "XLF",
    "KKR": "XLF",
    "FITB": "XLF",
    "KEY": "XLF",
    "RF": "XLF",
    "V": "XLF",
    "AXP": "XLF",
    "SPGI": "XLF",
    # XLC — Communication Services
    "DIS": "XLC",
    "T": "XLC",
    "VZ": "XLC",
    # XLB — Materials
    "LIN": "XLB",
    "SHW": "XLB",
    "APD": "XLB",
    "ECL": "XLB",
    "NUE": "XLB",
    # XLY — Consumer Discretionary
    "BKNG": "XLY",
    "GM": "XLY",
    "TJX": "XLY",
    # XLK — Technology
    "ANET": "XLK",
    # XLV — Healthcare (blocked in §10)
    "JNJ": "XLV",
    "MRK": "XLV",
    "LLY": "XLV",
    "UNH": "XLV",
    # XLE — Energy (blocked in §10)
    "XOM": "XLE",
    "CVX": "XLE",
    "COP": "XLE",
    # XLI — Industrials additions (blocked in §10)
    "HON": "XLI",
    "RTX": "XLI",
    # XLP — Consumer Staples (live-blocked; §10 does not block — research only)
    "PG": "XLP",
    "KO": "XLP",
    # OOS v4 expansion tickers
    "ADSK": "XLK",
    "SNPS": "XLK",
    "BWA": "XLY",
    "YUM": "XLY",
    "PPG": "XLB",
    "IFF": "XLB",
    "STT": "XLF",
    "MTB": "XLF",
    # OOS v5 additions
    "MCD": "XLY",
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
# Extra slippage applied when a stop is GAPPED THROUGH overnight (open < stop for BUY).
# Models bid-ask spread widening and market-impact on catastrophic gap exits;
# 0.15% is conservative for large-caps but realistic for fast-moving down-gaps.
GAP_STOP_SLIP_PCT = 0.15
# Slippage applied on non-gap stop exits (stop price reached intrabar, not gapped).
# A market order at a breached stop still prints through the stop due to bid-ask
# spread and queue position — 0.10% is conservative for S&P 500 mega-caps and
# realistic for mid-caps (EXPE, TPR, PSKY) during fast-market conditions.
NORMAL_STOP_SLIP_PCT = 0.10
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

# ── §59–§78 research gate parameters ─────────────────────────────────────────
OU_HALFLIFE_MAX = 25.0  # §59: half-life > 25d → reversion too slow for 2.5× hold window
HURST_TREND_CEIL = 0.80  # §60: H > 0.80 → strong trending regime; large-caps median ~0.71
IDIO_VOL_MAX = 55.0  # §61: annualized 63d realized vol > 55% → high noise band
SEP_SCORE_FLOOR = 55  # §78: September worst calendar month — extra conviction required
OCT_SCORE_FLOOR = 53  # §78: October elevated-vol month — slightly higher bar

# ── §67 Historical FOMC announcement dates (2003–2026) ───────────────────────
# Day-0 = hard block: unpredictable rate decision gaps destroy MR stop levels.
# Source: Federal Reserve press release dates.
_FOMC_DATES_HIST: frozenset[str] = frozenset(
    {
        # 2003
        "2003-01-29",
        "2003-03-18",
        "2003-05-06",
        "2003-06-25",
        "2003-08-12",
        "2003-09-16",
        "2003-10-28",
        "2003-12-09",
        # 2004
        "2004-01-28",
        "2004-03-16",
        "2004-05-04",
        "2004-06-30",
        "2004-08-10",
        "2004-09-21",
        "2004-11-10",
        "2004-12-14",
        # 2005
        "2005-02-02",
        "2005-03-22",
        "2005-05-03",
        "2005-06-30",
        "2005-08-09",
        "2005-09-20",
        "2005-11-01",
        "2005-12-13",
        # 2006
        "2006-01-31",
        "2006-03-28",
        "2006-05-10",
        "2006-06-29",
        "2006-08-08",
        "2006-09-20",
        "2006-10-25",
        "2006-12-12",
        # 2007
        "2007-01-31",
        "2007-03-21",
        "2007-05-09",
        "2007-06-28",
        "2007-08-07",
        "2007-09-18",
        "2007-10-31",
        "2007-12-11",
        # 2008 (includes 2 emergency cuts + 1 coordinated inter-meeting)
        "2008-01-22",
        "2008-01-30",
        "2008-03-18",
        "2008-04-30",
        "2008-06-25",
        "2008-08-05",
        "2008-09-16",
        "2008-10-08",
        "2008-10-29",
        "2008-12-16",
        # 2009
        "2009-01-28",
        "2009-03-18",
        "2009-04-29",
        "2009-06-24",
        "2009-08-12",
        "2009-09-23",
        "2009-11-04",
        "2009-12-16",
        # 2010
        "2010-01-27",
        "2010-03-16",
        "2010-04-28",
        "2010-06-23",
        "2010-08-10",
        "2010-09-21",
        "2010-11-03",
        "2010-12-14",
        # 2011
        "2011-01-26",
        "2011-03-15",
        "2011-04-27",
        "2011-06-22",
        "2011-08-09",
        "2011-09-21",
        "2011-11-02",
        "2011-12-13",
        # 2012
        "2012-01-25",
        "2012-03-13",
        "2012-04-25",
        "2012-06-20",
        "2012-08-01",
        "2012-09-13",
        "2012-10-24",
        "2012-12-12",
        # 2013
        "2013-01-30",
        "2013-03-20",
        "2013-05-01",
        "2013-06-19",
        "2013-07-31",
        "2013-09-18",
        "2013-10-30",
        "2013-12-18",
        # 2014
        "2014-01-29",
        "2014-03-19",
        "2014-04-30",
        "2014-06-18",
        "2014-07-30",
        "2014-09-17",
        "2014-10-29",
        "2014-12-17",
        # 2015
        "2015-01-28",
        "2015-03-18",
        "2015-04-29",
        "2015-06-17",
        "2015-07-29",
        "2015-09-17",
        "2015-10-28",
        "2015-12-16",
        # 2016
        "2016-01-27",
        "2016-03-16",
        "2016-04-27",
        "2016-06-15",
        "2016-07-27",
        "2016-09-21",
        "2016-11-02",
        "2016-12-14",
        # 2017
        "2017-02-01",
        "2017-03-15",
        "2017-05-03",
        "2017-06-14",
        "2017-07-26",
        "2017-09-20",
        "2017-11-01",
        "2017-12-13",
        # 2018
        "2018-01-31",
        "2018-03-21",
        "2018-05-02",
        "2018-06-13",
        "2018-08-01",
        "2018-09-26",
        "2018-11-08",
        "2018-12-19",
        # 2019
        "2019-01-30",
        "2019-03-20",
        "2019-05-01",
        "2019-06-19",
        "2019-07-31",
        "2019-09-18",
        "2019-10-30",
        "2019-12-11",
        # 2020 (includes COVID emergency cuts)
        "2020-01-29",
        "2020-03-03",
        "2020-03-15",
        "2020-04-29",
        "2020-06-10",
        "2020-07-29",
        "2020-09-16",
        "2020-11-05",
        "2020-12-16",
        # 2021
        "2021-01-27",
        "2021-03-17",
        "2021-04-28",
        "2021-06-16",
        "2021-07-28",
        "2021-09-22",
        "2021-11-03",
        "2021-12-15",
        # 2022
        "2022-02-02",
        "2022-03-16",
        "2022-05-04",
        "2022-06-15",
        "2022-07-27",
        "2022-09-21",
        "2022-11-02",
        "2022-12-14",
        # 2023
        "2023-02-01",
        "2023-03-22",
        "2023-05-03",
        "2023-06-14",
        "2023-07-26",
        "2023-09-20",
        "2023-11-01",
        "2023-12-13",
        # 2024
        "2024-01-31",
        "2024-03-20",
        "2024-05-01",
        "2024-06-12",
        "2024-07-31",
        "2024-09-18",
        "2024-11-07",
        "2024-12-18",
        # 2025
        "2025-01-29",
        "2025-03-19",
        "2025-05-07",
        "2025-06-18",
        "2025-07-30",
        "2025-09-17",
        "2025-10-29",
        "2025-12-10",
        # 2026
        "2026-01-28",
        "2026-03-18",
        "2026-04-29",
        "2026-06-17",
        "2026-07-29",
        "2026-09-16",
        "2026-10-28",
        "2026-12-16",
    }
)

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

    # ── §59 OU Half-life (63-day rolling) ────────────────────────────────────
    # Vectorized OLS: regress Δlog(p) on log(p[t-1]) over a 63-day rolling window.
    # Half-life λ = −log(2)/θ where θ = slope. Negative slope required (mean-reverting).
    _lp = np.log(np.maximum(c, 1e-10))
    _dlp = _lp.diff()
    _lp_lag = _lp.shift(1)
    _W = 63
    _roll_xy = (_lp_lag * _dlp).rolling(_W).sum()
    _roll_x = _lp_lag.rolling(_W).sum()
    _roll_y = _dlp.rolling(_W).sum()
    _roll_x2 = (_lp_lag**2).rolling(_W).sum()
    _denom = _W * _roll_x2 - _roll_x**2
    _slope = (_W * _roll_xy - _roll_x * _roll_y) / _denom.replace(0, np.nan)
    _ou_hl = -np.log(2) / _slope.where(_slope < -1e-10)
    df.loc[:, "ou_halflife"] = _ou_hl.clip(lower=0, upper=90)  # cap at 90d for display

    # ── §60 Hurst Exponent (63-day rolling R/S) ───────────────────────────────
    # H < 0.5 = anti-persistent (MR-friendly); H > 0.5 = trending.
    _lr_all = np.diff(np.log(np.maximum(c.values.astype(float), 1e-10)))
    _hurst_arr = np.full(len(df), np.nan)
    for _k in range(63, len(df)):
        _seg = _lr_all[_k - 63 : _k]
        _rs_pts = []
        for _lag in (4, 8, 16, 32):
            _n2 = (len(_seg) // _lag) * _lag
            if _n2 < _lag * 2:
                continue
            _sub = _seg[:_n2].reshape(-1, _lag)
            _rs_row = []
            for _row in _sub:
                _mu = _row.mean()
                _cd = np.cumsum(_row - _mu)
                _R = float(_cd.max() - _cd.min())
                _S = float(_row.std(ddof=1)) or 1e-10
                if _R > 0:
                    _rs_row.append(_R / _S)
            if _rs_row:
                _rs_pts.append((np.log(_lag), np.log(float(np.mean(_rs_row)))))
        if len(_rs_pts) >= 3:
            _xh = np.array([v[0] for v in _rs_pts])
            _yh = np.array([v[1] for v in _rs_pts])
            _hurst_arr[_k] = float(np.clip(np.polyfit(_xh, _yh, 1)[0], 0.0, 1.0))
    df.loc[:, "hurst"] = _hurst_arr

    # ── §61 Realized volatility (63-day annualized) ───────────────────────────
    df.loc[:, "realized_vol_63"] = c.pct_change().rolling(63).std(ddof=1) * np.sqrt(252) * 100

    # ── §77 52-week low proximity flag (for tax-loss harvest analysis) ────────
    _low52 = c.rolling(252).min()
    df.loc[:, "near_52wk_low"] = ((c - _low52) / _low52.replace(0, np.nan) < 0.08).astype(float)

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
    # §17 sensitivity (72-ticker IS): 1.5s/2.0t (all cases) → Sharpe 0.29 vs 0.26 baseline,
    #   +5.6pp WR, lower MaxDD. 1.0s/2.0t forced: Sharpe 0.23 (worse). Confirms 1.5s better.
    #   Strong trend (ADX>35): 1.0s / 3.0t  — trend carries; tight stop + extended target
    #   All other cases:       1.5s / 2.0t  — wider stop avoids intraday noise stops
    if adx > 35:
        s, t = 1.0, 3.0
    else:
        s, t = 1.5, 2.0

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
    vix_regime_v2: bool = False,
    cross_asset: dict | None = None,
    adaptive_profit_thresh_override: float | None = None,
    adaptive_rsi_thresh_override: float | None = None,
    fomc_dates: frozenset | None = None,
    t10y_data: dict | None = None,
    trin_data: dict | None = None,
    ad_data: dict | None = None,
) -> pd.DataFrame:
    """
    Generate signals and simulate trades for one ticker.

    NOTE — gates deliberately excluded from this backtest (look-ahead bias):
    • Fundamental value-trap gate (revenue_growth / FCF from yfinance .info): .info
      reflects current-day data only — not the value reported at any historical date.
      Applying it here would filter 2003 signals using 2026 fundamentals. Live signal
      engine applies it correctly; backtest omits it entirely.
    • AR(1) revenue_growth blend: same reason — yfinance .info is not point-in-time.
    • §73 insider clustering, §74 Beneish M-score, §76 Altman Z-score: quarterly
      financials are not point-in-time via yfinance — look-ahead bias risk. Live engine
      applies them correctly using freshly fetched data.

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
      20.  §59 OU half-life — ou_halflife > 25d → reversion too slow (>2.5× hold window)
      21.  §60 Hurst        — H > 0.80 → strong trending regime (large-caps median ~0.71)
      22.  §61 Idio vol     — realized_vol_63 > 55% → fat-tail noise band, skip MR
      10.  Earnings blackout — block within EARNINGS_BLACKOUT_DAYS of report
      11.  Consecutive RSI  — RSI must still be declining into the entry bar
      12.  Deep-bear RSI    — VIX>28 + SPY<SMA200×0.95 requires RSI<35
      13.  Price-SMA20      — price must be ≥2% below SMA20 (waived score≥65)
      14.  Dollar volume    — avg daily $ volume must exceed MIN_AVG_DOLLAR_VOL
      15.  Day-of-week      — no Friday entries (waived score≥65)
      15b. Thursday gate    — Thursday signals require score≥55 (fills Friday open; §57)
      19.  Cross-asset      — 3/3 macro headwinds (TLT+UUP+XLE) suppress BUY confidence (§55)
      23.  §67 FOMC day     — hard block on FOMC announcement day (rate decision gap risk)
      24.  §78 Seasonality  — Sep: score<55 blocked; Oct: score<53 blocked
      25.  §64 Yield curve  — inverted T10Y–IRX (<-0.5%) + XLF: require score+5
      26.  §68 Rising rates — T10Y 30d change >0.5pp + XLK: require score+5
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
    _vix_regime_v2 = vix_regime_v2
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

        # ── §54 VIX-conditional 5-band regime switching (threshold only) ────────
        # Dalio "All Weather": different regimes require different parameters.
        # §20 validated: VIX<15 = zero edge; VIX 15-18 = relaxed; VIX 18-25 =
        # default; VIX 25-35 = elevated fear, lower threshold productive;
        # VIX>35 = panic mode. Threshold adjusted here; VIX<15 suspension and
        # Gate 1 relaxation applied AFTER is_buy_signal is computed.
        if _vix_regime_v2 and vix_today is not None:
            if vix_today < 18.0:
                # Relaxed below Gate 9b (VIX<20 already blocks MR entries).
                _buy_thresh = 45
                _atr_rank_max = None
                _ret_jump_max = None
            elif vix_today < 25.0:
                pass  # default regime
            elif vix_today <= 35.0:
                # Elevated fear: lower threshold + cap extreme ATR.
                _buy_thresh = 45
                _atr_rank_max = 70.0
            else:
                # VIX > 35: extreme panic — strongest MR setups only.
                _buy_thresh = 40
                _atr_rank_max = 70.0

        is_buy_signal = _buy_thresh <= score <= BUY_THRESH_MAX
        is_sell_signal = score <= SELL_THRESH

        if not is_buy_signal and not is_sell_signal:
            continue

        # ── §54 VIX<15 suspension (applied after is_buy_signal is known) ─────────
        # §20: zero MR edge when VIX < 15; suspend BUY entries to preserve capital.
        if _vix_regime_v2 and is_buy_signal and vix_today is not None and vix_today < 15.0:
            continue

        # ── Gate 1: VIX tiers ─────────────────────────────────────────────────
        if is_buy_signal and vix_today is not None:
            if vix_today > 30:
                # §54 panic mode: allow VIX 30-35 entries with high conviction.
                # Standard mode: hard block above 30 (matches live engine).
                if not (_vix_regime_v2 and vix_today <= 35 and score >= 45):
                    continue
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

        # ── Gate 20: §59 OU half-life — reversion speed ───────────────────────
        # Block MR entries where the OU half-life exceeds 2.5× the hold window.
        # A half-life of >25 days means the price is unlikely to substantially
        # complete its mean-reversion before HOLD_DAYS expires.
        # Only fires when the column is populated (requires ≥63 bars of history).
        if is_buy_signal and _is_mr_setup:
            _ou_hl_v = row.get("ou_halflife")
            if _ou_hl_v is not None and pd.notna(_ou_hl_v):
                if float(_ou_hl_v) > OU_HALFLIFE_MAX:
                    continue

        # ── Gate 21: §60 Hurst — trending regime block ────────────────────────
        # Hurst > 0.80 = strongly trending behaviour. Large-cap US equities have
        # a median Hurst of ~0.71 (mild persistence is the norm); only the extreme
        # trending tail (H>0.80) is a genuine MR category-error.
        if is_buy_signal and _is_mr_setup:
            _hurst_v = row.get("hurst")
            if _hurst_v is not None and pd.notna(_hurst_v):
                if float(_hurst_v) > HURST_TREND_CEIL:
                    continue

        # ── Gate 22: §61 Idiosyncratic vol — high noise band ──────────────────
        # Annualized 63d realized vol > 55% = fat tails dominate. In this regime,
        # short-term oversold moves are more likely fundamental than mechanical.
        # Ang, Hodrick, Xing & Zhang (2006): high idio-vol predicts lower returns.
        if is_buy_signal and _is_mr_setup:
            _rvol63_v = row.get("realized_vol_63")
            if _rvol63_v is not None and pd.notna(_rvol63_v):
                if float(_rvol63_v) > IDIO_VOL_MAX:
                    continue

        # ── Gate 10: Earnings blackout ─────────────────────────────────────────
        # Binary earnings events destroy MR setups — an oversold stock that beats
        # will gap up (missing our stop target entirely) or misses and gaps past
        # the stop in one bar. Block entries within the blackout window.
        _earn_blackout = earnings_blackout_days if earnings_blackout_days is not None else EARNINGS_BLACKOUT_DAYS
        _days_to_earn: int = 999
        _days_since_earn: int | None = None
        if earnings_dates:
            _days_to_earn = min(
                ((e - date).days for e in earnings_dates if (e - date).days >= 0),
                default=999,
            )
            _past = [(date - e).days for e in earnings_dates if (date - e).days >= 0]
            if _past:
                _days_since_earn = min(_past)
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

        # ── Gate 15b: Thursday signal stricter threshold (§57) ────────────────
        # Thursday signals fill at Friday open — worse fill quality (pre-weekend
        # de-risking, institutional position squaring). Live data §11a (437 signals):
        # Thursday WR 56.2% vs Tuesday 70.1% — 14pp gap. Require higher conviction
        # to justify the inferior fill-day. Score 55 balances noise rejection vs
        # trade count. Waived at score≥65 (strong conviction).
        if is_buy_signal and date.dayofweek == 3 and score < 55:  # Thursday = 3
            continue

        # ── Gate 16: VIX minimum — skip low-volatility regime entries ─────────
        # In low-VIX environments stocks don't panic-sell deeply enough for
        # meaningful MR bounces. Elevated VIX = fear-driven capitulation =
        # stronger bounce. Only applied when vix_min_override is set.
        if is_buy_signal and _vix_min is not None and vix_today is not None:
            if vix_today < _vix_min:
                continue

        # ── Gate 19: Cross-asset macro headwind (§55) ─────────────────────────
        # When TLT+UUP+XLE all signal macro breakdown simultaneously (3/3),
        # equity MR is unreliable: forced selling is systemic, not stock-specific;
        # the reversal requires macro resolution, not just oversold technicals.
        # 3/3 headwinds → skip entry (macro breakdown, not equity-specific panic).
        # 2/3 → reduce score threshold requirement (less confident setup needed,
        # since the macro headwind is partial; handled implicitly by score gate).
        # Only active when cross_asset dict is provided.
        if is_buy_signal and cross_asset is not None:
            _ca_count = cross_asset.get(pd.Timestamp(str(date)[:10]), 0)
            if _ca_count >= 3:
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

        # ── Gate 23: §67 FOMC day hard block ──────────────────────────────────
        # On FOMC announcement days the rate decision creates an unpredictable
        # intraday gap that can stop out any MR position entered that morning.
        # Lucca & Moench (2015): mean intraday range on FOMC days is 2× normal.
        if is_buy_signal and fomc_dates is not None:
            if str(date)[:10] in fomc_dates:
                continue

        # ── Gate 24: §78 September/October seasonality threshold ──────────────
        # Bouman & Jacobsen (2002): September worst calendar month (avg −1.0% S&P),
        # October most volatile. Only high-conviction setups carry positive EV
        # against the negative seasonal drift. Raise the score floor.
        if is_buy_signal:
            _month_e = date.month
            if _month_e == 9 and score < SEP_SCORE_FLOOR:
                continue
            if _month_e == 10 and score < OCT_SCORE_FLOOR:
                continue

        # ── Gate 25: §64 Yield curve — XLF sector penalty ─────────────────────
        # Inverted yield curve (<-0.5%) compresses bank NIMs → XLF MR entries in
        # this regime have structurally lower WR. Harvey (1988). Require 5 extra
        # score points to pass.
        # ── Gate 26: §68 Rising rates — XLK sector penalty ────────────────────
        # Rapidly rising 10Y yield (>0.5pp/30d) compresses tech DCF valuations.
        # Damodaran (2022): tech duration risk is highest in rate-hike cycles.
        if is_buy_signal and t10y_data is not None:
            _t10y_entry = t10y_data.get(pd.Timestamp(str(date)[:10]))
            if _t10y_entry is not None:
                _t10y2y_sp, _t10y_30d = _t10y_entry
                _ticker_sector = TICKER_TO_SECTOR.get(ticker, "")
                if _t10y2y_sp is not None and _t10y2y_sp < -0.5 and _ticker_sector == "XLF":
                    if score < _buy_thresh + 5:
                        continue
                if _t10y_30d is not None and _t10y_30d > 0.5 and _ticker_sector == "XLK":
                    if score < _buy_thresh + 5:
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
                    # Gap-through: if the bar opened below the stop, fill at the open.
                    # Apply extra slippage (GAP_STOP_SLIP_PCT) only on true gap-downs
                    # (open already below stop) to model widened bid-ask and market impact.
                    _gapped = day_open < stop_price
                    _base_fill = min(stop_price, day_open)
                    if _gapped:
                        # Gap-through: open already below stop — wide spread + impact
                        exit_price = _base_fill * (1 - GAP_STOP_SLIP_PCT / 100)
                    else:
                        # Normal stop hit intrabar: market order still slips bid-ask
                        exit_price = _base_fill * (1 - NORMAL_STOP_SLIP_PCT / 100)
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
                    # Gap-through (short): fill at worst of stop or open if gapped above stop.
                    # Extra slippage on true gap-ups (open already above stop).
                    _gapped_short = day_open > stop_price
                    _base_fill_short = max(stop_price, day_open)
                    if _gapped_short:
                        exit_price = _base_fill_short * (1 + GAP_STOP_SLIP_PCT / 100)
                    else:
                        exit_price = _base_fill_short * (1 + NORMAL_STOP_SLIP_PCT / 100)
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

        # ── §65/§66/§77 context metadata for analysis splits ─────────────────
        _date_key = pd.Timestamp(str(date)[:10])
        _trin_today = (trin_data or {}).get(_date_key)
        _ad_entry = (ad_data or {}).get(_date_key)
        _ad_chg_today = float(_ad_entry[0]) if _ad_entry is not None else None
        _zweig_today = bool(_ad_entry[1]) if _ad_entry is not None else False
        _near_52wk_low_flag = (
            bool(row.get("near_52wk_low", False)) if pd.notna(row.get("near_52wk_low", float("nan"))) else False
        )

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
                "days_since_earnings": _days_since_earn,
                "dow": date.dayofweek,
                "trin": round(_trin_today, 2) if _trin_today is not None else None,
                "ad_ema10_chg": round(_ad_chg_today, 1) if _ad_chg_today is not None else None,
                "zweig_thrust": _zweig_today,
                "near_52wk_low": _near_52wk_low_flag,
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
    """Block bootstrap Monte Carlo for honest Sharpe confidence intervals.

    Consecutive trades on the same ticker share regime — they are NOT IID.
    IID (iid=np.random.choice) resamples break this structure and produce
    confidence intervals that are 30–50% too tight. Block bootstrap (Politis &
    Romano 1994) preserves serial autocorrelation by resampling contiguous
    blocks of trades, producing wider and honest P5/P95 intervals.

    Block size: max(5, round(N^(1/3))). For N=114 → block=5; N=1500 → block=11.
    This matches the mean-reverting cycle length (~5–10 holding days) and is
    consistent with the Politis-Romano optimal block selection rule.
    """
    returns = trades_df["net_pct"].values
    if len(returns) == 0:
        return
    n = len(returns)
    block_size = max(5, int(round(n ** (1 / 3))))
    n_blocks_needed = -(-n // block_size)  # ceiling division

    rng = np.random.default_rng(seed=42)
    sharpe_sims = []
    for _ in range(n_sims):
        starts = rng.integers(0, max(1, n - block_size + 1), size=n_blocks_needed)
        blocks = [returns[s : s + block_size] for s in starts]
        sample = np.concatenate(blocks)[:n]
        s = stats(sample.tolist())
        sharpe_sims.append(s.get("sharpe") or 0.0)

    p5 = np.percentile(sharpe_sims, 5)
    p95 = np.percentile(sharpe_sims, 95)
    print(
        f"- **Monte Carlo Sharpe (block bootstrap N={n_sims}, block={block_size}, 5th/95th pct):** {p5:.2f} / {p95:.2f}"
    )
    print(
        f"  > Block bootstrap (block={block_size}) preserves serial autocorrelation. "
        "IID resampling would overstate CI confidence by ~30–50%."
    )
    if p5 < 0:
        print("  > ⚠ 5th percentile < 0 — edge may not be real; treat Sharpe as upper bound.")


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


def fetch_cross_asset_composite(start: str, end: str) -> dict[pd.Timestamp, int]:
    """Fetch TLT, UUP (DXY proxy), and XLE to build a daily cross-asset headwind score.

    Score 0–3 headwinds per day:
      TLT 5d change > +1.5%   → bond flight-to-quality (macro breakdown signal)
      UUP 5d change > +1.0%   → dollar strength / risk-off demand
      XLE 5d change < −3.0%   → commodity demand collapse (recession signal)

    Score 3/3 → macro breakdown (equity MR unreliable → suppress confidence).
    Score 0/3 → equity-specific panic (cleanest MR setup; no macro headwind).

    Returns dict: date → headwind_count (0, 1, 2, or 3).
    §55: Dalio/Bridgewater cross-asset triangulation — isolates equity panic from
    systemic macro breakdown. Missing data → 0 (no headwind assumed).
    """
    try:
        tlt_raw = yf.download("TLT", start=start, end=end, interval="1d", auto_adjust=True, progress=False)
        uup_raw = yf.download("UUP", start=start, end=end, interval="1d", auto_adjust=True, progress=False)
        xle_raw = yf.download("XLE", start=start, end=end, interval="1d", auto_adjust=True, progress=False)

        def _close(df):
            if df is None or df.empty:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df = df.copy()
                df.columns = df.columns.get_level_values(0)
            s = df["Close"].ffill() if "Close" in df.columns else None
            if s is not None:
                # Normalize index to tz-naive date-only to avoid KeyError on misaligned tz-aware indices
                s = s.copy()
                s.index = pd.to_datetime([str(i)[:10] for i in s.index])
            return s

        tlt = _close(tlt_raw)
        uup = _close(uup_raw)
        xle = _close(xle_raw)
        if tlt is None or uup is None or xle is None:
            return {}

        # Align to common trading days via DataFrame join; forward-fill gaps
        ca = pd.DataFrame({"tlt": tlt, "uup": uup, "xle": xle}).ffill().dropna()

        # 5-day percentage change (vectorized — no per-row get_loc)
        tlt_5d = ca["tlt"].pct_change(5) * 100
        uup_5d = ca["uup"].pct_change(5) * 100
        xle_5d = ca["xle"].pct_change(5) * 100

        count_series = (tlt_5d > 1.5).astype(int) + (uup_5d > 1.0).astype(int) + (xle_5d < -3.0).astype(int)

        return {pd.Timestamp(str(dt)[:10]): int(v) for dt, v in count_series.items() if pd.notna(v)}
    except Exception as e:
        print(f"[cross-asset] failed ({e})")
        return {}


def fetch_t10y(start: str, end: str) -> dict[pd.Timestamp, tuple[float | None, float | None]]:
    """Fetch 10Y Treasury yield (^TNX) and 13-week T-bill (^IRX) to compute:
      - t10y2y_spread: 10Y minus ~2Y rate (^IRX used as short-rate proxy)
      - t10y_30d_chg: 22-trading-day change in 10Y yield

    Returns dict: date → (t10y2y_spread_pct, t10y_30d_chg_pp).
    Both are None if data is unavailable for that date.
    Used for §64 (XLF yield-curve gate) and §68 (XLK rising-rate gate).
    """
    try:
        t10y_raw = yf.download("^TNX", start=start, end=end, interval="1d", auto_adjust=False, progress=False)
        irx_raw = yf.download("^IRX", start=start, end=end, interval="1d", auto_adjust=False, progress=False)
        if isinstance(t10y_raw.columns, pd.MultiIndex):
            t10y_raw.columns = t10y_raw.columns.get_level_values(0)
        if isinstance(irx_raw.columns, pd.MultiIndex):
            irx_raw.columns = irx_raw.columns.get_level_values(0)
        t10y_s = t10y_raw["Close"].ffill() if "Close" in t10y_raw.columns else pd.Series(dtype=float)
        irx_s = irx_raw["Close"].ffill() if "Close" in irx_raw.columns else pd.Series(dtype=float)
        t10y_30d = t10y_s - t10y_s.shift(22)
        out: dict[pd.Timestamp, tuple[float | None, float | None]] = {}
        for dt in t10y_s.index:
            key = pd.Timestamp(str(dt)[:10])
            t10 = float(t10y_s.loc[dt]) if pd.notna(t10y_s.loc[dt]) else None
            irx = float(irx_s.loc[dt]) if dt in irx_s.index and pd.notna(irx_s.loc[dt]) else None
            chg = float(t10y_30d.loc[dt]) if pd.notna(t10y_30d.loc[dt]) else None
            spread = (t10 - irx) if (t10 is not None and irx is not None) else None
            out[key] = (spread, chg)
        return out
    except Exception as e:
        print(f"[t10y] failed ({e})")
        return {}


def fetch_trin(start: str, end: str) -> dict[pd.Timestamp, float]:
    """Fetch NYSE TRIN (Arms Index) from ^TRIN via yfinance.

    TRIN > 2.0 = market-wide capitulation (panic selling — MR setups have higher WR).
    Returns dict: date → trin_value. Falls back to empty if unavailable.
    Used for §65 analysis (split trades by capitulation context).
    """
    try:
        raw = yf.download("^TRIN", start=start, end=end, interval="1d", auto_adjust=False, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        s = raw["Close"].ffill() if "Close" in raw.columns else pd.Series(dtype=float)
        return {pd.Timestamp(str(k)[:10]): float(v) for k, v in s.items() if pd.notna(v)}
    except Exception as e:
        print(f"[trin] failed ({e})")
        return {}


def fetch_ad_breadth(start: str, end: str) -> dict[pd.Timestamp, tuple[float, bool]]:
    """Fetch NYSE cumulative A/D line (^NYAD) to compute Zweig breadth thrust signal.

    Returns dict: date → (ad_10ema_chg, zweig_thrust_today).
      ad_10ema_chg: 10-day EMA of daily A/D changes (negative = breadth deteriorating)
      zweig_thrust_today: True if EMA crossed from negative to > +50 within last 10 bars
    Used for §66 analysis.
    """
    try:
        raw = yf.download("^NYAD", start=start, end=end, interval="1d", auto_adjust=False, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        ad = raw["Close"].ffill() if "Close" in raw.columns else pd.Series(dtype=float)
        ad_chg = ad.diff()
        ad_ema10 = ad_chg.ewm(span=10, adjust=False).mean()
        out: dict[pd.Timestamp, tuple[float, bool]] = {}
        for i, dt in enumerate(ad_ema10.index):
            if pd.isna(ad_ema10.iloc[i]):
                continue
            chg_val = float(ad_ema10.iloc[i])
            thrust = False
            if i >= 10:
                prev_vals = ad_ema10.iloc[i - 10 : i]
                thrust = bool(any(v < 0 for v in prev_vals) and chg_val > 50)
            out[pd.Timestamp(str(dt)[:10])] = (chg_val, thrust)
        return out
    except Exception as e:
        print(f"[ad_breadth] failed ({e})")
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
        n_combos = len(results)
        print("Full sweep results (sorted by Sharpe):\n")
        print(res_df.to_string(index=False))
        best = res_df.iloc[0]
        print(
            f"\n> Best: BUY_THRESH={int(best['buy_lo'])}, MAX={int(best['buy_hi'])}, "
            f"HOLD={int(best['hold'])} → Sharpe {best['sharpe']:.3f}, "
            f"WR {best['wr']:.1f}%, avg {best['avg']:+.3f}%, n={int(best['n'])}"
        )
        # Multiple-comparison inflation warning (Bonferroni adjustment)
        # The best-of-N Sharpe is inflated relative to any single pre-specified
        # threshold. Under the null hypothesis (no edge), the expected best Sharpe
        # across K combinations rises with K. A conservative Bonferroni-adjusted
        # p-value for selecting the top combination from K=n_combos is α_bonf = α/K.
        # At K=45, a Sharpe that would be "significant" at α=0.05 with a single test
        # requires the raw p-value to be ≤0.001 to remain significant after correction.
        print(
            f"\n> ⚠ **Multiple-comparisons inflation ({n_combos} combinations):**"
            f" best-of-{n_combos} Sharpe is inflated vs a pre-specified threshold."
            f" Bonferroni-adjusted significance level: α/{n_combos} = "
            f"{0.05 / n_combos:.4f}. Treat the selected BUY_THRESH as a starting"
            " point, not a proven optimal — validate on OOS data."
        )

    # Restore original globals
    BUY_THRESH = orig_buy
    BUY_THRESH_MAX = orig_buy_max
    SELL_THRESH = orig_sell
    HOLD_DAYS = orig_hold


# ─────────────────────────────────────────────────────────────────────────────
# Full-Universe Curation Bias Report
# ─────────────────────────────────────────────────────────────────────────────


def run_full_universe_curation_bias(
    vix, spy_trend, stlfsi4, fomc_dates=None, t10y_data=None, trin_data=None, ad_data=None
):
    """Quantify IS universe curation bias by including the 14 removed underperformers.

    The main IS universe excluded 14 tickers because they 'dragged avg return by
    -0.30% to -0.67% per trade'. Running the full universe (curated + removed) shows
    what portion of the IS Sharpe 0.24 is genuine alpha vs selection bias from the
    curated universe.

    Curation bias = IS_Sharpe(curated) - IS_Sharpe(full).

    Only run with --full-universe flag because it requires downloading ~14 more tickers
    (slow). Results are printed for transparency; the curated IS remains the primary
    performance report for live-engine alignment.

    Activate by passing --full-universe on the command line.
    """
    print("\n## Full-Universe Curation Bias Report (--full-universe flag)\n")
    print("> Runs the same IS strategy on _CURATED_OUT_TICKERS (removed underperformers)")
    print("> to show what portion of IS Sharpe is curation bias vs genuine alpha.\n")

    args_list = [
        (t, vix, spy_trend, stlfsi4, True, fomc_dates, t10y_data, trin_data, ad_data) for t in _CURATED_OUT_TICKERS
    ]
    with Pool(min(8, len(_CURATED_OUT_TICKERS))) as p:
        results = p.map(process_ticker, args_list)

    removed_trades: list[pd.DataFrame] = []
    for ticker, t_df, _bh, _df in results:
        if t_df is not None and not t_df.empty:
            removed_trades.append(t_df)

    if not removed_trades:
        print("> [warn] No trades generated for removed tickers — check data availability.\n")
        return

    removed = pd.concat(removed_trades, ignore_index=True)
    sr = stats(removed["net_pct"].tolist())
    print("### Curated-out tickers (would-be IS underperformers)\n")
    print_table(
        ["Metric", "Curated-Out Only", "Note"],
        [
            ["Total Trades", str(sr["n"]), ""],
            ["Win Rate", f"{sr['wr']:.1f}%", ""],
            ["Avg Return / Trade", f"{sr['avg']:+.2f}%", ""],
            ["Sharpe", fmt_sharpe(sr["sharpe"]), ""],
        ],
    )

    # Per-ticker breakdown
    rows = []
    for ticker, t_df, _bh, _df in results:
        if t_df is None or t_df.empty:
            rows.append([ticker, "0", "—", "—", "—"])
            continue
        st = stats(t_df["net_pct"].tolist())
        rows.append([ticker, str(st["n"]), f"{st['wr']:.1f}%", f"{st['avg']:+.2f}%", fmt_sharpe(st["sharpe"])])
    print("\n### Per-Ticker (curated-out)\n")
    print_table(["Ticker", "N", "WR", "Avg Ret", "Sharpe"], rows)
    print(
        "\n> Curation bias = IS_Sharpe(curated) − IS_Sharpe(full_universe)."
        " If Sharpe(curated-out) << Sharpe(IS), the curated IS Sharpe is overstated by that gap.\n"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Gate Sensitivity Sweep (§59–§82 threshold analysis)
# ─────────────────────────────────────────────────────────────────────────────


def gate_sensitivity_sweep(
    all_dfs,
    vix,
    spy_trend,
    stlfsi4,
    fomc_dates=None,
    t10y_data=None,
    trin_data=None,
    ad_data=None,
):
    """One-at-a-time IS sensitivity analysis for §59–§82 gate thresholds.

    Each parameter is swept across a calibration grid while all others are held
    at baseline. 999 = gate disabled (upper-bound check). Outputs: N, WR, avg
    return, Sharpe for every setting so the analyst can see the Sharpe cliff.
    """
    global OU_HALFLIFE_MAX, HURST_TREND_CEIL, IDIO_VOL_MAX, SEP_SCORE_FLOOR, OCT_SCORE_FLOOR

    print("\n## Gate Sensitivity Sweep — §59–§82 thresholds (IS universe, MR-only)\n")
    print("> One-at-a-time analysis: each parameter varied, all others held at baseline.")
    print(
        f"> Baseline: OU_HALFLIFE_MAX={OU_HALFLIFE_MAX}, HURST_TREND_CEIL={HURST_TREND_CEIL}, "
        f"IDIO_VOL_MAX={IDIO_VOL_MAX}, SEP_SCORE_FLOOR={SEP_SCORE_FLOOR}, OCT_SCORE_FLOOR={OCT_SCORE_FLOOR}\n"
    )

    def _run_all(label: str) -> dict:
        trades = []
        for ticker, df in all_dfs.items():
            t = simulate_ticker(
                ticker,
                df,
                vix,
                spy_trend,
                stlfsi4,
                mr_only=True,
                fomc_dates=fomc_dates,
                t10y_data=t10y_data,
                trin_data=trin_data,
                ad_data=ad_data,
            )
            if not t.empty:
                trades.append(t)
        if not trades:
            return {"label": label, "n": 0, "wr": 0.0, "avg": 0.0, "sharpe": None}
        sv = stats(pd.concat(trades, ignore_index=True)["net_pct"].tolist())
        return {
            "label": label,
            "n": sv["n"],
            "wr": round(sv.get("wr", 0.0), 1),
            "avg": round(sv.get("avg", 0.0), 3),
            "sharpe": sv.get("sharpe"),
        }

    def _print_rows(header: str, rows: list[dict]) -> None:
        print(f"### {header}\n")
        print_table(
            ["Setting", "N", "WR", "Avg Ret", "Sharpe"],
            [[r["label"], str(r["n"]), f"{r['wr']:.1f}%", f"{r['avg']:+.3f}%", fmt_sharpe(r["sharpe"])] for r in rows],
        )
        best = max(rows, key=lambda r: r["sharpe"] or -99)
        print(
            f"> Optimal: {best['label']} → Sharpe {fmt_sharpe(best['sharpe'])}, WR {best['wr']:.1f}%, N={best['n']}\n"
        )

    # ── §59 OU halflife ───────────────────────────────────────────────────────
    orig_ou = OU_HALFLIFE_MAX
    ou_rows = []
    for val in [10.0, 15.0, 20.0, 25.0, 30.0, 999.0]:
        OU_HALFLIFE_MAX = val
        label = "disabled" if val == 999.0 else f"{val:.0f}d"
        ou_rows.append(_run_all(label))
    OU_HALFLIFE_MAX = orig_ou
    _print_rows("§59 OU Halflife Max (days, MR entries only)", ou_rows)

    # ── §60 Hurst ceiling ─────────────────────────────────────────────────────
    orig_hurst = HURST_TREND_CEIL
    hurst_rows = []
    for val in [0.60, 0.65, 0.70, 0.75, 0.80, 999.0]:
        HURST_TREND_CEIL = val
        label = "disabled" if val == 999.0 else f"{val:.2f}"
        hurst_rows.append(_run_all(label))
    HURST_TREND_CEIL = orig_hurst
    _print_rows("§60 Hurst Trend Ceiling (H >, MR entries only)", hurst_rows)

    # ── §61 Idiosyncratic vol ceiling ─────────────────────────────────────────
    orig_ivol = IDIO_VOL_MAX
    ivol_rows = []
    for val in [35.0, 45.0, 55.0, 65.0, 80.0, 999.0]:
        IDIO_VOL_MAX = val
        label = "disabled" if val == 999.0 else f"{val:.0f}%"
        ivol_rows.append(_run_all(label))
    IDIO_VOL_MAX = orig_ivol
    _print_rows("§61 Idiosyncratic Vol Max (annualized 63d, MR entries only)", ivol_rows)

    # ── §78 September score floor ─────────────────────────────────────────────
    orig_sep = SEP_SCORE_FLOOR
    sep_rows = []
    for val in [50, 53, 55, 58, 62, 999]:
        SEP_SCORE_FLOOR = val
        label = "disabled" if val == 999 else str(val)
        sep_rows.append(_run_all(label))
    SEP_SCORE_FLOOR = orig_sep
    _print_rows("§78 September BUY Score Floor", sep_rows)

    # ── §78 October score floor ───────────────────────────────────────────────
    orig_oct = OCT_SCORE_FLOOR
    oct_rows = []
    for val in [48, 50, 53, 55, 58, 999]:
        OCT_SCORE_FLOOR = val
        label = "disabled" if val == 999 else str(val)
        oct_rows.append(_run_all(label))
    OCT_SCORE_FLOOR = orig_oct
    _print_rows("§78 October BUY Score Floor", oct_rows)


# ─────────────────────────────────────────────────────────────────────────────
# Walk-Forward Temporal Stability
# ─────────────────────────────────────────────────────────────────────────────


def run_walk_forward_temporal(trades_df: pd.DataFrame) -> None:
    """Measure whether the edge is stable across market regimes.

    The IS backtest uses pre-specified gates (BUY_THRESH, §59-§82 parameters)
    derived from the full 23-year IS period.  This function partitions the
    same IS trades by calendar year-range to answer a distinct question:
    is the Sharpe 0.24 driven by one lucky regime (e.g. GFC vol) or does the
    edge persist across bull, bear, recovery and rate-cycle environments?

    This is NOT a true walk-forward (gates are not re-calibrated per epoch —
    that would require re-running parameter_sweep() per window, future work).
    It is a temporal stability check: a signal that only fires in one epoch
    is regime-specific, not systematic.

    Epochs:
      2003-2009  Pre-GFC bull + GFC collapse (high realized vol)
      2010-2016  Post-crisis recovery (steady low-vol bull)
      2017-2021  Late-cycle + COVID collapse + V-shaped recovery
      2022-pres  Rate-hike cycle + normalization (new macro regime)

    A credible systematic edge should show positive Sharpe in ≥3 of 4 epochs.
    """
    print("\n## Walk-Forward Temporal Stability (IS universe, pre-specified gates)\n")
    print("> Not a true walk-forward (gates not re-calibrated per epoch).")
    print("> Measures regime stability: a signal surviving all 4 epochs is")
    print("> more robust than one driven by a single vol regime.\n")

    epochs = [
        ("2003–2009  (Pre-GFC/GFC)", 2003, 2010),
        ("2010–2016  (Post-crisis bull)", 2010, 2017),
        ("2017–2021  (Late-cycle/COVID)", 2017, 2022),
        ("2022–pres  (Rate-hike cycle)", 2022, 2100),
    ]

    rows = []
    positive_epochs = 0
    for label, yr_start, yr_end in epochs:
        sub = trades_df[(trades_df["year"] >= yr_start) & (trades_df["year"] < yr_end)]
        sr = stats(sub["net_pct"].tolist())
        sh = sr.get("sharpe")
        if sh is not None and sh > 0:
            positive_epochs += 1
        rows.append(
            [
                label,
                str(sr["n"]),
                f"{sr['wr']:.1f}%" if sr["n"] else "—",
                f"{sr['avg']:+.2f}%" if sr["n"] else "—",
                fmt_sharpe(sh),
                f"-{sr['max_dd']:.2f}%" if sr["n"] else "—",
            ]
        )

    print_table(["Epoch", "N", "WR", "Avg Ret", "Sharpe", "Max DD"], rows)
    print()

    # Verdict
    print("**Temporal stability verdict:**")
    if positive_epochs == 4:
        print(f"- ✅ {positive_epochs}/4 epochs Sharpe > 0 — edge is regime-agnostic.")
    elif positive_epochs >= 3:
        print(f"- ⚠ {positive_epochs}/4 epochs Sharpe > 0 — mostly stable; one epoch is regime-specific.")
    elif positive_epochs >= 2:
        print(f"- ⚠ {positive_epochs}/4 epochs Sharpe > 0 — partial stability; edge may be regime-dependent.")
    else:
        print(f"- ⛔ Only {positive_epochs}/4 epochs Sharpe > 0 — edge is concentrated in one regime.")

    print(
        "> Note: for true walk-forward validation, run parameter_sweep() on each epoch separately"
        " and re-select BUY_THRESH per period. Epoch-specific Sharpe will be lower than full-period IS Sharpe.\n"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Held-out OOS Validation
# ─────────────────────────────────────────────────────────────────────────────


def run_oos_validation(vix, spy_trend, stlfsi4, fomc_dates=None, t10y_data=None, trin_data=None, ad_data=None):
    """Run the MR-only strategy on HELD_OUT_TICKERS and compare vs main universe.

    These tickers were never touched during research or gate calibration —
    any edge found here is genuinely out-of-sample.

    Reports two result sets:
      ALL  — all HELD_OUT_TICKERS (shows what each ticker contributed)
      CLEAN — excludes _OOS_BLOCKED_TICKERS (AMAT/KLAC/STT/MTB are live-blocked;
              their OOS trades inflate the curation-bias gap artificially)

    Interpretation guide:
      OOS Sharpe ≥ 0.10   → edge generalises; curation bias is small
      OOS Sharpe 0.00-0.10 → modest curation bias; still a real signal
      OOS Sharpe < 0.00    → main-universe results are heavily curated;
                             treat reported Sharpe with scepticism
    """
    blocked_note = " (★ = in live BLOCKED_TICKERS — excluded from clean metrics)"
    print("\n## OOS Validation — Held-Out Universe (never seen during research)\n")
    print(f"> Tickers: {', '.join(HELD_OUT_TICKERS)}")
    print(f"> {blocked_note}")
    print("> Same MR-Only strategy, same gates, same period — zero data-mining benefit.\n")

    args_list = [
        (t, vix, spy_trend, stlfsi4, True, fomc_dates, t10y_data, trin_data, ad_data) for t in HELD_OUT_TICKERS
    ]
    with Pool(min(8, len(HELD_OUT_TICKERS))) as p:
        results = p.map(process_ticker, args_list)

    oos_trades: list[pd.DataFrame] = []
    clean_trades: list[pd.DataFrame] = []
    for ticker, t_df, _bh, _df in results:
        if t_df is not None and not t_df.empty:
            oos_trades.append(t_df)
            if ticker not in _OOS_BLOCKED_TICKERS:
                clean_trades.append(t_df)

    if not oos_trades:
        print("> [warn] No OOS trades generated — check data availability.\n")
        return

    oos = pd.concat(oos_trades, ignore_index=True)
    s = stats(oos["net_pct"].tolist())

    # Clean OOS = excludes live-blocked tickers (KLAC/AMAT) for unbiased read
    if clean_trades:
        oos_clean = pd.concat(clean_trades, ignore_index=True)
        sc = stats(oos_clean["net_pct"].tolist())
    else:
        oos_clean = oos
        sc = s

    _blocked_labels = ", ".join(sorted(_OOS_BLOCKED_TICKERS))
    print_table(
        ["Metric", f"ALL ({len(HELD_OUT_TICKERS)} tickers)", f"CLEAN (ex {_blocked_labels})", "Interpretation"],
        [
            ["Total Trades", str(s["n"]), str(sc["n"]), "clean = live-compatible"],
            ["Win Rate", f"{s['wr']:.1f}%", f"{sc['wr']:.1f}%", "target ≥50%"],
            ["Avg Return / Trade", f"{s['avg']:+.2f}%", f"{sc['avg']:+.2f}%", "net 0.50% friction"],
            ["Profit Factor", fmt_pf(s["pf"]), fmt_pf(sc["pf"]), "≥1.0 required"],
            ["Sharpe Ratio", fmt_sharpe(s["sharpe"]), fmt_sharpe(sc["sharpe"]), "≥0.10 = edge generalises"],
            ["Max Drawdown", f"-{s['max_dd']:.2f}%", f"-{sc['max_dd']:.2f}%", "5% sizing"],
        ],
    )

    # Per-ticker breakdown
    print("\n### OOS Per-Ticker\n")
    rows = []
    for ticker, t_df, _bh, _df in results:
        blocked_flag = " ★" if ticker in _OOS_BLOCKED_TICKERS else ""
        if t_df is None or t_df.empty:
            rows.append([ticker + blocked_flag, "0", "—", "—", "—"])
            continue
        st = stats(t_df["net_pct"].tolist())
        rows.append(
            [
                ticker + blocked_flag,
                str(st["n"]),
                f"{st['wr']:.1f}%" if st["n"] else "—",
                f"{st['avg']:+.2f}%" if st["n"] else "—",
                fmt_sharpe(st["sharpe"]),
            ]
        )
    print_table(["Ticker (★=live-blocked)", "N", "WR", "Avg Ret", "Sharpe"], rows)
    print()

    # ── OOS Score-Band Analysis (clean) ───────────────────────────────────────
    if "score" in oos_clean.columns:
        _oos_sb = oos_clean.copy()
        _oos_sb["score_band"] = pd.cut(
            _oos_sb["score"],
            bins=[BUY_THRESH - 1, 50, 60, 70, 999],
            labels=["40-50", "50-60", "60-70", "70+"],
            right=True,
        )
        print("### OOS Score-Band Analysis (clean — ex live-blocked)\n")
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
    # §59–§82 canonical IS (74-ticker, sector-filtered live-equivalent)
    is_wr = 64.9
    is_avg = 0.90
    is_sh = 0.24
    # Use CLEAN OOS for curation-bias verdict (apples-to-apples vs sector-filtered IS)
    oos_wr = sc["wr"]
    oos_avg = sc["avg"]
    oos_sh = sc["sharpe"] or 0.0
    wr_gap = oos_wr - is_wr
    avg_gap = oos_avg - is_avg
    sh_gap = oos_sh - is_sh

    print("### OOS Verdict — Curation Bias (clean OOS vs sector-filtered IS)\n")
    print_table(
        ["Metric", "IS sector-filtered", "OOS clean", "Gap"],
        [
            ["Win Rate", f"{is_wr:.1f}%", f"{oos_wr:.1f}%", f"{wr_gap:+.1f}pp"],
            ["Avg Return", f"+{is_avg:.2f}%", f"{oos_avg:+.2f}%", f"{avg_gap:+.2f}pp"],
            ["Sharpe", f"{is_sh:.2f}", f"{oos_sh:.2f}", f"{sh_gap:+.2f}"],
            ["Profit Factor", "2.00×", fmt_pf(sc["pf"]), ""],
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
        f"**Sector composition note:** v5 held-out set ({len(HELD_OUT_TICKERS)} tickers: XLK/XLY/XLC/XLB/XLF).",
        f"CLEAN excludes {_blocked_labels} (live BLOCKED_TICKERS — semi equipment, continuation not MR).",
        "IS comparison uses sector-filtered result (XLV/XLI/XLE removed from 74-ticker IS).",
    ]
    for line in _verdict_lines:
        print(line)
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Parallel Processing
# ─────────────────────────────────────────────────────────────────────────────


def process_ticker(args):
    ticker, vix, spy_trend, stlfsi4, mr_only, fomc_dates, t10y_data, trin_data, ad_data = args
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

        # ── Fetch earnings dates: Polygon only (full point-in-time history) ────
        # Polygon vX/reference/financials covers SEC filing dates back to 2003.
        # yfinance.get_earnings_dates() was intentionally REMOVED: it returns
        # the *current* forward-looking calendar (up to ~4yr ahead) which, when
        # used in a historical backtest, constitutes lookahead bias — a signal
        # blocked at 2015-01-20 would have used 2026's version of the earnings
        # calendar, not what was known in January 2015. Polygon SEC filing dates
        # are point-in-time (the actual announcement date is in the past when the
        # record is written) and do not suffer from this problem.
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

        t = simulate_ticker(
            ticker,
            df,
            vix,
            spy_trend,
            stlfsi4,
            mr_only=mr_only,
            earnings_dates=earnings_dates,
            fomc_dates=fomc_dates,
            t10y_data=t10y_data,
            trin_data=trin_data,
            ad_data=ad_data,
        )
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
    print("> **Earnings blackout:** Polygon vX/reference/financials only (point-in-time SEC filing dates).")
    print(">   yfinance supplement REMOVED (lookahead bias — returns forward calendar, not historical dates).")
    print("> ⚠ **Survivorship bias — CRITICAL:** Universe is drawn from *current* S&P 500 survivors.")
    print(">   Companies that delisted, went bankrupt, or were removed 2003–2026 are absent:")
    print(">   Lehman Brothers, Bear Stearns, Washington Mutual, Sears, General Electric (removed")
    print(">   2018), Enron, WorldCom, and ~200 others. MR strategies are *uniquely* exposed because")
    print(">   buying a -15% dip on a company heading to zero produces a -100% loss leg that is")
    print(">   completely invisible in this simulation. Academic literature (e.g., Brown, Goetzmann,")
    print(">   Ross 1992; Kothari, Shanken, Sloan 1995) documents 1–4 pp/yr WR overstatement from")
    print(">   survivorship alone; for MR systems buying distressed names the bias is larger.")
    print(">   Treat reported WR and avg return as upper-bound estimates, not realized performance.")
    print(">   Fix requires point-in-time constituent data (Norgate, Sharadar, or CRSP).\n")

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

    # ── §64/§68 T10Y yield and spread ─────────────────────────────────────────
    print("Fetching T10Y / IRX (yield curve + rate change)…", end=" ", flush=True)
    t10y_data = fetch_t10y(START, END)
    print(f"ok ({len(t10y_data)} bars)" if t10y_data else "skipped (fetch failed)")

    # ── §65 TRIN (Arms Index) ─────────────────────────────────────────────────
    print("Fetching TRIN (NYSE Arms Index)…", end=" ", flush=True)
    trin_data = fetch_trin(START, END)
    print(f"ok ({len(trin_data)} bars)" if trin_data else "skipped (fetch failed)")

    # ── §66 A/D breadth (Zweig thrust) ───────────────────────────────────────
    print("Fetching NYSE A/D breadth (Zweig)…", end=" ", flush=True)
    ad_data = fetch_ad_breadth(START, END)
    print(f"ok ({len(ad_data)} bars)" if ad_data else "skipped (fetch failed)")

    # ── Download price data and compute signals ───────────────────────────────
    all_trades: list[pd.DataFrame] = []
    bh_returns = []
    all_dfs = {}

    mode_label = "MR-Only" if BACKTEST_MR_DEFAULT else "Full-Signal"
    print(f"\nRunning in **{mode_label}** mode (BACKTEST_MR_DEFAULT={BACKTEST_MR_DEFAULT})")
    if BACKTEST_MR_DEFAULT:
        print(f"  MR gate: RSI<{MR_RSI_CEIL} OR BB%B<{MR_BB_CEIL} OR IBS<{MR_IBS_CEIL} OR VWAP%<{MR_VWAP_FLOOR}%\n")

    args_list = [
        (t, vix, spy_trend, stlfsi4, BACKTEST_MR_DEFAULT, _FOMC_DATES_HIST, t10y_data, trin_data, ad_data)
        for t in TICKERS
    ]

    import multiprocessing as _mp

    _mp.set_start_method("fork", force=True)  # macOS Python 3.14 spawn→fork
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
    # §5b. Day-of-Week breakdown (§57 research validation)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n## 5b. Day-of-Week Performance (Signal Date)\n")
    print("> Signal date DOW — Friday blocked by Gate 15. Thursday = fills Friday open.")
    _dow_names = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday"}
    dow_rows = []
    for _d in range(5):
        _sub = trades[trades["dow"] == _d]["net_pct"].tolist() if "dow" in trades.columns else []
        _sr = stats(_sub)
        if _sr["n"] == 0:
            continue
        dow_rows.append(
            [
                _dow_names[_d],
                str(_sr["n"]),
                f"{_sr['wr']:.1f}%",
                f"{_sr['avg']:+.2f}%",
                fmt_pf(_sr["pf"]),
                fmt_sharpe(_sr["sharpe"]),
            ]
        )
    print_table(["Signal Day", "N", "WR", "Avg Ret", "PF", "Sharpe"], dow_rows)
    print("> Gate 15b active: Thursday signals require score ≥ 55 (vs baseline ≥ 50).")

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
    run_walk_forward_temporal(trades)

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

    # ─────────────────────────────────────────────────────────────────────────
    # §11. §54 Research — VIX-Conditional Regime Switching (5-band)
    # ─────────────────────────────────────────────────────────────────────────
    if all_dfs and BACKTEST_MR_DEFAULT:
        print("\n## 11. §54 VIX-Conditional Regime Switching (5-band)\n")
        print("> VIX<15→suspend · VIX 15-18→thresh=45 · VIX 18-25→default ·")
        print("> VIX 25-35→thresh=45+ATRceil=70 · VIX>35→thresh=40+ATRceil=70")
        print("> Gate 1 relaxed: VIX 30-35 allowed at score≥45 (panic mode).\n")

        v2_list = []
        for ticker_k, df_k in all_dfs.items():
            t_v2 = simulate_ticker(
                ticker_k,
                df_k,
                vix,
                spy_trend,
                stlfsi4,
                mr_only=True,
                vix_regime_v2=True,
            )
            if not t_v2.empty:
                v2_list.append(t_v2)

        if not v2_list:
            print("[no §54 trades generated]\n")
        else:
            v2_trades = pd.concat(v2_list, ignore_index=True)
            sv2 = stats(v2_trades["net_pct"].tolist())
            print_table(
                ["Metric", "Baseline (§1-§8)", "§54 VIX Regime", "Δ"],
                [
                    ["N Trades", str(s["n"]), str(sv2["n"]), f"{sv2['n'] - s['n']:+d}"],
                    ["Win Rate", f"{s['wr']:.1f}%", f"{sv2['wr']:.1f}%", f"{sv2['wr'] - s['wr']:+.1f}pp"],
                    ["Avg Return", f"{s['avg']:+.2f}%", f"{sv2['avg']:+.2f}%", f"{sv2['avg'] - s['avg']:+.2f}pp"],
                    [
                        "Sharpe",
                        fmt_sharpe(s["sharpe"]),
                        fmt_sharpe(sv2["sharpe"]),
                        f"{(sv2['sharpe'] or 0) - (s['sharpe'] or 0):+.2f}",
                    ],
                    ["Max DD", f"-{s['max_dd']:.2f}%", f"-{sv2['max_dd']:.2f}%", ""],
                ],
            )
            print("\n> §54 verdict: ΔSharpe > 0 = regime switching adds value over static threshold.\n")
            monte_carlo(v2_trades)

    # ─────────────────────────────────────────────────────────────────────────
    # §12. §55 Research — Cross-Asset Macro Composite (TLT+UUP+XLE)
    # ─────────────────────────────────────────────────────────────────────────
    if all_dfs and BACKTEST_MR_DEFAULT:
        print("\n## 12. §55 Cross-Asset Macro Composite (TLT+UUP+XLE)\n")
        print("> TLT 5d>+1.5% + UUP 5d>+1.0% + XLE 5d<-3.0% = 3/3 macro breakdown → skip entry.")
        print("Fetching TLT/UUP/XLE…", end=" ", flush=True)
        cross_asset_data = fetch_cross_asset_composite(START, END)
        if not cross_asset_data:
            print("failed — §55 skipped.\n")
        else:
            headwind_counts = list(cross_asset_data.values())
            n3 = sum(1 for c in headwind_counts if c >= 3)
            n2 = sum(1 for c in headwind_counts if c == 2)
            print(f"ok ({len(cross_asset_data)} days, {n3} with 3/3 headwinds, {n2} with 2/3)\n")

            ca_list = []
            for ticker_k, df_k in all_dfs.items():
                t_ca = simulate_ticker(
                    ticker_k,
                    df_k,
                    vix,
                    spy_trend,
                    stlfsi4,
                    mr_only=True,
                    cross_asset=cross_asset_data,
                )
                if not t_ca.empty:
                    ca_list.append(t_ca)

            if not ca_list:
                print("[no §55 trades generated]\n")
            else:
                ca_trades = pd.concat(ca_list, ignore_index=True)
                sca = stats(ca_trades["net_pct"].tolist())
                print_table(
                    ["Metric", "Baseline (§1-§8)", "§55 Cross-Asset", "Δ"],
                    [
                        ["N Trades", str(s["n"]), str(sca["n"]), f"{sca['n'] - s['n']:+d}"],
                        ["Win Rate", f"{s['wr']:.1f}%", f"{sca['wr']:.1f}%", f"{sca['wr'] - s['wr']:+.1f}pp"],
                        ["Avg Return", f"{s['avg']:+.2f}%", f"{sca['avg']:+.2f}%", f"{sca['avg'] - s['avg']:+.2f}pp"],
                        [
                            "Sharpe",
                            fmt_sharpe(s["sharpe"]),
                            fmt_sharpe(sca["sharpe"]),
                            f"{(sca['sharpe'] or 0) - (s['sharpe'] or 0):+.2f}",
                        ],
                        ["Max DD", f"-{s['max_dd']:.2f}%", f"-{sca['max_dd']:.2f}%", ""],
                    ],
                )
                blocked_pct = (s["n"] - sca["n"]) / s["n"] * 100 if s["n"] > 0 else 0
                print(f"\n> {s['n'] - sca['n']} trades blocked ({blocked_pct:.1f}%) by 3/3 macro headwind gate.")
                print("> §55 verdict: ΔSharpe > 0 = cross-asset filter removes false positives.\n")
                monte_carlo(ca_trades)

    # §13. §53 Research — Post-Earnings Oversold MR Timing (35–65d window)
    # ─────────────────────────────────────────────────────────────────────────
    # Jegadeesh & Livnat (2006): post-earnings drift exhausts in 30–40d.
    # Days 35–65 after a negative-surprise earnings = structural dislocation,
    # not ongoing repricing → highest-quality MR entry window.
    if "days_since_earnings" in trades.columns and BACKTEST_MR_DEFAULT:
        print("\n## 13. §53 Post-Earnings Oversold MR Timing (35–65d Window)\n")
        _has_dse = trades["days_since_earnings"].notna()
        _in_window = _has_dse & trades["days_since_earnings"].between(35, 65)
        _out_window = ~_in_window

        _t_in = trades[_in_window]["net_pct"].tolist()
        _t_out = trades[_out_window]["net_pct"].tolist()
        _s_in = stats(_t_in) if _t_in else {"n": 0, "wr": 0, "avg": 0, "sharpe": None}
        _s_out = stats(_t_out) if _t_out else {"n": 0, "wr": 0, "avg": 0, "sharpe": None}

        print("> Days since last earnings → 35–65d window (drift exhausted, MR prime).\n")
        print_table(
            ["Metric", "Other (outside 35-65d)", "35–65d Post-Earnings", "Δ"],
            [
                ["N Trades", str(_s_out["n"]), str(_s_in["n"]), f"{_s_in['n'] - _s_out['n']:+d}"],
                ["Win Rate", f"{_s_out['wr']:.1f}%", f"{_s_in['wr']:.1f}%", f"{_s_in['wr'] - _s_out['wr']:+.1f}pp"],
                [
                    "Avg Return",
                    f"{_s_out['avg']:+.2f}%",
                    f"{_s_in['avg']:+.2f}%",
                    f"{_s_in['avg'] - _s_out['avg']:+.2f}pp",
                ],
                [
                    "Sharpe",
                    fmt_sharpe(_s_out["sharpe"]),
                    fmt_sharpe(_s_in["sharpe"]),
                    f"{(_s_in['sharpe'] or 0) - (_s_out['sharpe'] or 0):+.2f}"
                    if _s_in["sharpe"] and _s_out["sharpe"]
                    else "—",
                ],
            ],
        )
        _window_pct = _s_in["n"] / s["n"] * 100 if s["n"] > 0 else 0
        print(f"\n> {_s_in['n']} of {s['n']} trades ({_window_pct:.0f}%) fall in the 35–65d post-earnings window.")
        if _s_in["n"] >= 5 and _s_out["wr"] > 0:
            _delta_wr = _s_in["wr"] - _s_out["wr"]
            if _delta_wr >= 5:
                print(f"> §53 verdict: 35–65d window shows +{_delta_wr:.1f}pp WR — post-earnings timing adds edge.")
            elif _delta_wr <= -5:
                print(
                    f"> §53 verdict: 35–65d window shows {_delta_wr:.1f}pp WR — no post-earnings MR edge in this universe."
                )
            else:
                print(f"> §53 verdict: WR difference {_delta_wr:+.1f}pp — insufficient to confirm post-earnings edge.")
        else:
            print(f"> §53 verdict: N={_s_in['n']} in window (need ≥5 for significance). Inconclusive.")
        print()

    # ─────────────────────────────────────────────────────────────────────────
    # §14. §65 Research — TRIN Capitulation Split
    # ─────────────────────────────────────────────────────────────────────────
    # Arms Index > 2.0 = market-wide panic selling. MR BUY entries during
    # capitulation context should show higher WR (classic MR hypothesis).
    if "trin" in trades.columns and trades["trin"].notna().any():
        print("\n## 14. §65 TRIN Capitulation Split (BUY trades only)\n")
        _buy_t = trades[trades["action"] == "BUY"].copy()
        _trin_cap = _buy_t[_buy_t["trin"] >= 2.0]
        _trin_norm = _buy_t[_buy_t["trin"] < 2.0]
        _trin_na = _buy_t[_buy_t["trin"].isna()]
        _cap_rows = []
        for label, sub in [
            ("TRIN ≥ 2.0 (capitulation)", _trin_cap),
            ("TRIN < 2.0 (normal)", _trin_norm),
            ("TRIN N/A", _trin_na),
        ]:
            st = stats(sub["net_pct"].tolist())
            if st["n"] == 0:
                continue
            _cap_rows.append([label, str(st["n"]), f"{st['wr']:.1f}%", f"{st['avg']:+.2f}%", fmt_sharpe(st["sharpe"])])
        print_table(["Context", "N", "WR", "Avg Ret", "Sharpe"], _cap_rows)
        if len(_trin_cap) >= 5 and len(_trin_norm) >= 5:
            _trin_delta = stats(_trin_cap["net_pct"].tolist())["wr"] - stats(_trin_norm["net_pct"].tolist())["wr"]
            if _trin_delta > 3:
                print(f"> §65 verdict: TRIN≥2 adds +{_trin_delta:.1f}pp WR — capitulation context confirms MR edge.")
            elif _trin_delta > 0:
                print(f"> §65 verdict: TRIN≥2 adds +{_trin_delta:.1f}pp WR — modest capitulation lift.")
            else:
                print(f"> §65 verdict: TRIN≥2 gap {_trin_delta:+.1f}pp — no additional edge in capitulation context.")
        print()

    # ─────────────────────────────────────────────────────────────────────────
    # §15. §66 Research — Zweig Breadth Thrust / A/D Breadth Split
    # ─────────────────────────────────────────────────────────────────────────
    # Zweig thrust (10-day EMA of A/D crosses from negative to >+50) is a rare
    # event. Negative A/D breadth (EMA < −200) should reduce MR WR (market
    # deterioration; MR setups may continue falling).
    if "ad_ema10_chg" in trades.columns and trades["ad_ema10_chg"].notna().any():
        print("\n## 15. §66 A/D Breadth Split (BUY trades only)\n")
        _buy_ad = trades[trades["action"] == "BUY"].copy()
        _zweig_yes = _buy_ad[_buy_ad["zweig_thrust"] == True]
        _ad_neg = _buy_ad[(_buy_ad["zweig_thrust"] == False) & (_buy_ad["ad_ema10_chg"] < -200)]
        _ad_pos = _buy_ad[(_buy_ad["zweig_thrust"] == False) & (_buy_ad["ad_ema10_chg"] >= -200)]
        _ad_rows = []
        for label, sub in [
            ("Zweig Thrust (rare bullish surge)", _zweig_yes),
            ("A/D Breadth normal (EMA ≥ −200)", _ad_pos),
            ("A/D Breadth weak (EMA < −200)", _ad_neg),
        ]:
            st = stats(sub["net_pct"].tolist())
            if st["n"] == 0:
                continue
            _ad_rows.append([label, str(st["n"]), f"{st['wr']:.1f}%", f"{st['avg']:+.2f}%", fmt_sharpe(st["sharpe"])])
        print_table(["Context", "N", "WR", "Avg Ret", "Sharpe"], _ad_rows)
        if len(_ad_neg) >= 5 and len(_ad_pos) >= 5:
            _neg_wr = stats(_ad_neg["net_pct"].tolist())["wr"]
            _pos_wr = stats(_ad_pos["net_pct"].tolist())["wr"]
            _ad_delta = _neg_wr - _pos_wr
            if _ad_delta < -3:
                print(f"> §66 verdict: weak breadth (EMA<−200) shows {_ad_delta:.1f}pp WR gap — confirmed headwind.")
            else:
                print(f"> §66 verdict: breadth gap {_ad_delta:+.1f}pp — no strong breadth-MR interaction found.")
        print()

    # ─────────────────────────────────────────────────────────────────────────
    # §16. §77 Research — Tax-Loss Harvest Window Split
    # ─────────────────────────────────────────────────────────────────────────
    # Nov/Dec near 52-week lows → forced tax-loss selling → artificial dip that
    # reverses in January. Classic January Effect (Reinganum 1983; Keim 1983).
    if "near_52wk_low" in trades.columns:
        print("\n## 16. §77 Tax-Loss Harvest Window (BUY trades near 52-wk low)\n")
        _buy_tlh = trades[trades["action"] == "BUY"].copy()
        _buy_tlh["month"] = _buy_tlh["date"].dt.month
        _tlh_nov_dec = _buy_tlh[(_buy_tlh["month"].isin([11, 12])) & (_buy_tlh["near_52wk_low"] == True)]
        _tlh_jan = _buy_tlh[(_buy_tlh["month"] == 1) & (_buy_tlh["near_52wk_low"] == True)]
        _tlh_other = _buy_tlh[
            ~(
                ((_buy_tlh["month"].isin([11, 12])) & (_buy_tlh["near_52wk_low"] == True))
                | ((_buy_tlh["month"] == 1) & (_buy_tlh["near_52wk_low"] == True))
            )
        ]
        _tlh_rows = []
        for label, sub in [
            ("Nov/Dec near 52-wk low (tax-loss)", _tlh_nov_dec),
            ("January near 52-wk low (rebound)", _tlh_jan),
            ("All other BUY trades", _tlh_other),
        ]:
            st = stats(sub["net_pct"].tolist())
            if st["n"] == 0:
                continue
            _tlh_rows.append([label, str(st["n"]), f"{st['wr']:.1f}%", f"{st['avg']:+.2f}%", fmt_sharpe(st["sharpe"])])
        print_table(["Context", "N", "WR", "Avg Ret", "Sharpe"], _tlh_rows)
        if len(_tlh_nov_dec) >= 5 and len(_tlh_other) >= 5:
            _tlh_wr = stats(_tlh_nov_dec["net_pct"].tolist())["wr"]
            _other_wr = stats(_tlh_other["net_pct"].tolist())["wr"]
            _tlh_delta = _tlh_wr - _other_wr
            if _tlh_delta > 3:
                print(f"> §77 verdict: Nov/Dec near-low adds +{_tlh_delta:.1f}pp WR — tax-loss MR edge confirmed.")
            else:
                print(
                    f"> §77 verdict: Nov/Dec near-low gap {_tlh_delta:+.1f}pp — tax-loss seasonality not significant in this universe."
                )
        print()

    # ─────────────────────────────────────────────────────────────────────────
    # §17. Stop Sensitivity — ATR multiplier comparison (IS universe)
    # Investigates whether widening the stop from baseline (1.0s/2.0t for normal,
    # 1.5s/2.0t for high-vol/ADX) improves Sharpe. Motivation: live WR 42.2%
    # vs IS WR 68.8% — stop-too-tight hypothesis (stops firing at intraday noise
    # level rather than on genuine direction changes).
    # ─────────────────────────────────────────────────────────────────────────
    print("\n## 17. Stop Sensitivity — ATR Multiplier (IS Universe)\n")
    print("> Re-runs IS simulation with fixed stop_mult_override. Earnings dates not re-fetched.")
    print("> Baseline uses adaptive atr_levels() (1.0s/2.0t normal; 1.5s/2.0t high-vol/ADX).")
    print()
    _stop_configs = [
        ("Baseline (adaptive atr_levels)", None, None),
        ("1.0s/2.0t (force normal, no adapt)", 1.0, 2.0),
        ("1.5s/2.0t (wide — all cases)", 1.5, 2.0),
        ("2.0s/2.5t (very wide)", 2.0, 2.5),
    ]
    _stop_rows = []
    for _slabel, _smult, _tmult in _stop_configs:
        _st_trades: list[pd.DataFrame] = []
        for _ticker, _df in all_dfs.items():
            try:
                _t = simulate_ticker(
                    _ticker,
                    _df,
                    vix,
                    spy_trend,
                    stlfsi4,
                    mr_only=True,
                    stop_mult_override=_smult,
                    target_mult_override=_tmult,
                    fomc_dates=_FOMC_DATES_HIST,
                    t10y_data=t10y_data,
                    trin_data=trin_data,
                    ad_data=ad_data,
                )
                if not _t.empty:
                    _st_trades.append(_t)
            except Exception:
                pass
        if not _st_trades:
            continue
        _stdf = pd.concat(_st_trades, ignore_index=True)
        _ss = stats(_stdf["net_pct"].tolist())
        _baseline_sharpe = _stop_rows[0][4] if _stop_rows else "—"
        _stop_rows.append(
            [
                _slabel,
                str(_ss["n"]),
                f"{_ss['wr']:.1f}%",
                f"{_ss['avg']:+.2f}%",
                fmt_sharpe(_ss["sharpe"]),
                f"-{_ss['max_dd']:.2f}%",
            ]
        )
    print_table(["Stop Config", "N", "WR", "Avg Ret", "Sharpe", "Max DD"], _stop_rows)
    if len(_stop_rows) >= 2:
        _bl = _stop_rows[0]
        _best = max(_stop_rows[1:], key=lambda r: float(r[4]) if r[4] != "—" else -999)
        print(f"> Baseline Sharpe: {_bl[4]} | Best alternative: {_best[0]} → {_best[4]}")
        _bl_sh = float(_bl[4]) if _bl[4] != "—" else 0.0
        _best_sh = float(_best[4]) if _best[4] != "—" else 0.0
        if _best_sh > _bl_sh + 0.01:
            print(
                f"> §17 verdict: wider stop improves Sharpe by +{_best_sh - _bl_sh:.2f} — consider tightening live stops."
            )
        else:
            print("> §17 verdict: baseline adaptive stops are optimal — do NOT widen.")
    print()

    if "--oos" in sys.argv or "--sweep" in sys.argv:
        run_oos_validation(
            vix,
            spy_trend,
            stlfsi4,
            fomc_dates=_FOMC_DATES_HIST,
            t10y_data=t10y_data,
            trin_data=trin_data,
            ad_data=ad_data,
        )

    if "--sweep" in sys.argv:
        parameter_sweep(all_dfs, vix, spy_trend, stlfsi4)

    if "--full-universe" in sys.argv:
        run_full_universe_curation_bias(
            vix,
            spy_trend,
            stlfsi4,
            fomc_dates=_FOMC_DATES_HIST,
            t10y_data=t10y_data,
            trin_data=trin_data,
            ad_data=ad_data,
        )

    if "--gate-sweep" in sys.argv:
        gate_sensitivity_sweep(
            all_dfs,
            vix,
            spy_trend,
            stlfsi4,
            fomc_dates=_FOMC_DATES_HIST,
            t10y_data=t10y_data,
            trin_data=trin_data,
            ad_data=ad_data,
        )


if __name__ == "__main__":
    main()
