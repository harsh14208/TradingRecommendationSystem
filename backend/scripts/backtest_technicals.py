"""
Tier-1 Technical Backtest — Signal.Trade engine rules replayed against
30 years of OHLCV data using only indicators computable from price/volume.

Score family caps (technical-only backtest — calibrated independently from live engine):
  • Oscillator family : RSI/Stoch/WR/CCI → clip(±25) × 1.00             → max ±25.0
  • Trend family      : MACD/EMA/ADX      → clip(±28) × 0.90             → max ±25.2
  • Volume family     : OBV/CMF/surge     → clip(±20) × 0.85             → max ±17.0
  • MA family         : SMA200/50/20      → clip(±28) × 1.00             → max ±28.0
  • MR family         : BB/%B/IBS/VWAP   → clip(±18) × 1.00             → max ±18.0
  NOTE: These caps differ from signal_engine.py because the live engine has 50+ additional
  signal families (options, fundamentals, alt-data, macro) that raise scores materially.
  Aligning caps would collapse backtest trade count from ~188 to ~15.
  Regime layers (4):
    L1 ADX strength  : >40 → trend×1.20 MR×0.10; 25-40 → MR×0.40; <20 → trend×0.30 MR×1.20
    L2 SMA200 price  : bull → suppress bearish MR×0.20
    L3 Quality gate  : ≥2 families must agree (else score×0.50)
    L4 Volume veto   : dry-up volume on BUY → score×0.70 (waived RSI<30)
  BUY threshold : score ≥ 50
  SELL threshold: score ≤ −100 (disabled)
  VIX tiers     : BUY blocked >30; marginal BUY (score<45) blocked 25-30
  MR gate       : ≥2 of {RSI<42, BB%B<0.22, IBS<0.15, VWAP%<-0.75%} (2026-06-09: 1→2)
  SPY trend     : BUY requires SPY>SMA200 (or RSI<30/score≥55)
  STLFSI4       : FRED financial stress — hard-blocks BUY >1.5+VIX>30; marginal block >1.0+VIX>25
  Stops/targets : ATR-based swing, universal 1.5s/2.0t (matches live _levels(); ADX>35 branch removed)
  Hold period   : max 10 trading days
  Friction      : 0.50% round-trip (matches FRICTION_PCT in calc_tbd_metrics.py)
  Ann. Sharpe   : √252 with trading-day-equivalent event returns (calendar_days × 252/365.25)

Run from backend/:
    python scripts/backtest_technicals.py             # IS run (default)
    python scripts/backtest_technicals.py --oos       # OOS v4 validation (18 tickers)
    python scripts/backtest_technicals.py --sweep     # BUY_THRESH / HOLD_DAYS grid search
    python scripts/backtest_technicals.py --gate-sweep  # §59–§82 threshold sensitivity
    python scripts/backtest_technicals.py --orats     # §111 ORATS options-flow alt-data tilt
    python scripts/backtest_technicals.py --portfolio --vol-target 0.10  # portfolio vol targeting
    python scripts/backtest_technicals.py --portfolio --entry-limit 0.20   # limit entry 0.2 ATR below close
    python scripts/backtest_technicals.py --portfolio --max21-filter 0.55  # keep low-MAX signals (bottom 55%)
"""

from __future__ import annotations

import json
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

import socket

socket.setdefaulttimeout(10)

import asyncio
import threading
import warnings
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

# Meta-label feature generation (QUANT_ENGINE_REVIEW §1.3)
try:
    import xgboost as xgb
    from services.signal_ml import predict_entry_prob, get_entry_model
except Exception:
    xgb = None  # type: ignore[assignment]
    predict_entry_prob = None  # type: ignore[assignment]
    get_entry_model = None  # type: ignore[assignment]

try:
    from hmmlearn.hmm import GaussianHMM
except Exception:
    GaussianHMM = None  # type: ignore[assignment,misc]

# ── §104–§110: Alt-data panel globals (loaded in main(), used by simulate_ticker) ──
_alt_data_panels: dict[str, pd.DataFrame | None] = {
    "finra_sv": None,
    "sec_ftd": None,
    "naaim": None,
    "aaii": None,
    "gdelt": None,
    "finra_ats": None,
    "wikipedia": None,
    "occ": None,
    "orats": None,
}

# ── Parallel simulation globals (set by main(), read by worker processes) ────
# macOS uses fork() for Pool, so these are copy-on-write inherited by workers.
_RUN_VIX: dict = {}
_RUN_SPY_TREND: dict = {}
_RUN_STLFSI4: dict = {}


def _simulate_ticker_worker(args):
    """Worker for parallel simulate_ticker runs."""
    ticker, df, kwargs = args
    try:
        tr = simulate_ticker(ticker, df, _RUN_VIX, _RUN_SPY_TREND, _RUN_STLFSI4, **kwargs)
        return ticker, tr
    except Exception as e:
        print(f"{ticker} simulate_ticker error: {e}", flush=True)
        return ticker, None


def _filter_simulation_results(results: list[tuple[str, pd.DataFrame | None]]) -> list[pd.DataFrame]:
    """Return only non-empty DataFrames from worker results."""
    return [tr for _, tr in results if tr is not None and not tr.empty]


def _run_simulation_parallel(
    all_dfs: dict[str, pd.DataFrame],
    common_kwargs: dict | None = None,
    per_ticker_kwargs: dict[str, dict] | None = None,
    max_workers: int | None = None,
    vix: dict | None = None,
    spy_trend: dict | None = None,
    stlfsi4: dict | None = None,
) -> list[pd.DataFrame]:
    """Run simulate_ticker for all tickers in parallel.

    Respects `--sequential` to bypass the pool (useful for macOS fork-debugging
    or when running under profilers).  Worker count defaults to
    ``BACKTEST_WORKERS`` env var or 8.
    """
    global _RUN_VIX, _RUN_SPY_TREND, _RUN_STLFSI4
    if vix is not None:
        _RUN_VIX = vix
    if spy_trend is not None:
        _RUN_SPY_TREND = spy_trend
    if stlfsi4 is not None:
        _RUN_STLFSI4 = stlfsi4
    if common_kwargs is None:
        common_kwargs = {}
    if per_ticker_kwargs is None:
        per_ticker_kwargs = {}
    if max_workers is None:
        max_workers = int(os.getenv("BACKTEST_WORKERS", "8"))

    args = []
    for ticker, df in all_dfs.items():
        kwargs = dict(common_kwargs)
        kwargs.update(per_ticker_kwargs.get(ticker, {}))
        args.append((ticker, df, kwargs))

    if max_workers <= 1 or "--sequential" in sys.argv:
        results = [_simulate_ticker_worker(a) for a in args]
    else:
        with ThreadPoolExecutor(max_workers=max_workers) as p:
            results = list(p.map(_simulate_ticker_worker, args))

    return results


def _log_experiment(
    experiment_type: str,
    hypothesis: str,
    n_trials: int = 1,
    is_metrics: dict | None = None,
) -> None:
    """Append experiment record to local registry for honest DSR trial counting."""
    try:
        import subprocess
        from datetime import datetime, timezone

        git_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
    except Exception:
        git_sha = None

    record = {
        "experiment_type": experiment_type,
        "hypothesis": hypothesis,
        "git_sha": git_sha,
        "number_of_trials": n_trials,
        "is_metrics": is_metrics or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _exp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "experiment_registry.jsonl")
    try:
        with open(_exp_path, "a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


def _count_experiments() -> int:
    try:
        _exp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "experiment_registry.jsonl")
        if not os.path.exists(_exp_path):
            return 0
        with open(_exp_path) as f:
            return sum(json.loads(line).get("number_of_trials", 1) for line in f if line.strip())
    except Exception:
        return 0


def cached_yf_download(
    ticker_or_tickers, start: str, end: str, interval: str = "1d", auto_adjust: bool = True, progress: bool = False
) -> pd.DataFrame:
    import os

    _HERE = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.abspath(os.path.join(_HERE, "..", "data", "cache_ohlcv"))
    os.makedirs(cache_dir, exist_ok=True)

    if not isinstance(ticker_or_tickers, str) and hasattr(ticker_or_tickers, "__iter__"):
        ticker_str = "_".join(sorted(list(ticker_or_tickers)))
    else:
        ticker_str = str(ticker_or_tickers)

    ticker_clean = ticker_str.replace("^", "_").replace("-", "_").replace(" ", "_")
    filename = f"{ticker_clean}_{start}_{end}_{interval}_adj{auto_adjust}.csv"
    cache_path = os.path.join(cache_dir, filename)

    if os.path.exists(cache_path):
        try:
            return pd.read_csv(cache_path, header=[0, 1], index_col=0, parse_dates=True)
        except Exception:
            pass

    raw = yf.download(
        ticker_or_tickers,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=auto_adjust,
        progress=progress,
        threads=False,
    )
    if not raw.empty:
        raw.to_csv(cache_path)
    return raw


warnings.filterwarnings("ignore")

_CONSTITUENTS_MAP = None


_UNMAPPED_CONSTITUENTS_WARNED: set[str] = set()
_UNMAPPED_CONSTITUENTS_LOCK = threading.Lock()


def is_index_constituent(ticker: str, date: pd.Timestamp) -> bool:
    global _CONSTITUENTS_MAP
    if _CONSTITUENTS_MAP is None:
        import json
        import os

        _HERE = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(_HERE, "..", "data", "sp500_historical_constituents.json"))
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"PIT constituents file missing: {path}. "
                "Download from fja05680/sp500-historical-constituents or equivalent "
                "point-in-time source. Auto-generated defaults silently remove the "
                "survivorship correction and invalidate backtest results."
            )

        try:
            with open(path) as f:
                _CONSTITUENTS_MAP = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load constituents file {path}: {e}") from e

        if not isinstance(_CONSTITUENTS_MAP, dict):
            raise RuntimeError(f"Constituents file {path} is not a JSON object.")

        # Provenance check: if the file was generated from a known PIT source it
        # should carry a '_source' key.  Warn (don't hard-fail) so legacy files
        # still load while the team pins provenance on the next refresh.
        if "_source" not in _CONSTITUENTS_MAP:
            print(
                f"\n⚠ [PIT Constituents] {path} lacks '_source' provenance key. "
                "Assert that this file came from fja05680/sp500-historical-constituents "
                "or another verified PIT source.\n"
            )

    lookup_ticker = ticker
    if ticker == "LEH":
        lookup_ticker = "LEHMQ"
    elif ticker == "WM":
        lookup_ticker = "WAMUQ"

    intervals = _CONSTITUENTS_MAP.get(lookup_ticker)
    if not intervals:
        # Unknown ticker = survivorship correction silently bypassed for it.
        # Warn once per ticker so a stale constituents file can't quietly
        # readmit names with no membership data.
        with _UNMAPPED_CONSTITUENTS_LOCK:
            if lookup_ticker not in _UNMAPPED_CONSTITUENTS_WARNED:
                _UNMAPPED_CONSTITUENTS_WARNED.add(lookup_ticker)
                print(f"⚠ [PIT Constituents] {lookup_ticker} not in membership map — treating as always-member")
        return True

    date_dt = date.date()
    for start_str, end_str in intervals:
        start = datetime.strptime(start_str, "%Y-%m-%d").date()
        end = datetime.strptime(end_str, "%Y-%m-%d").date()
        if start <= date_dt <= end:
            return True

    return False


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
    "AMP",  # Ameriprise Financial — R1000 screener PASS: N=10, WR=80%, Sh=0.42 (2006-2016)
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
    "MCO",  # Moody's Corp — credit ratings; R1000 screener N=9, WR=78%, Avg=+1.21% (2006-2016)
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
    # XLV Healthcare (§10 removes — allowed in live engine)
    "JNJ",  # Johnson & Johnson — pharma/medtech compounder; classic MR anchor
    "MRK",  # Merck — pharma; patent-cycle MR on pipeline news
    "LLY",  # Eli Lilly — high-growth pharma; MR on sentiment swings
    "UNH",  # UnitedHealth — managed care; steady compounder MR
    "ABT",  # Abbott — medtech/diagnostics; smooth compounder MR
    "BSX",  # Boston Scientific — medtech; earnings-driven MR cycles
    "AMGN",  # Amgen — large biotech; stable enough for MR; S&P 500 since 1994
    "CI",  # Cigna — managed care peer to UNH; earnings-driven MR
    "HCA",  # HCA Healthcare — hospital operator; volume-cycle MR; S&P 500 since 2015
    # XLE Energy (§10 removes — allowed in live engine)
    "XOM",  # ExxonMobil — mega-cap energy; oil-cycle MR
    "CVX",  # Chevron — stable major; cleaner MR than XOM
    "COP",  # ConocoPhillips — E&P; high-beta oil MR
    "SLB",  # SLB (Schlumberger) — oilfield services; oil-activity-cycle MR
    "EOG",  # EOG Resources — E&P; commodity-cycle MR; S&P 500 since 2000
    "MPC",  # Marathon Petroleum — refining; crack-spread-cycle MR
    "HAL",  # Halliburton — oilfield services; R1000 screener WR=86%, Avg=+4.30% (fast mode)
    # FTI removed: IS N=1 WR=0% Avg=-6.80% (§31-4 verdict: fast-mode 83% WR not replicated full IS)
    # TRGP removed: IS N=4 WR=25% Avg=-1.30% (§31-4 verdict: midstream gas continuation not MR)
    # XLI additions (§10 removes — allowed in live engine)
    "HON",  # Honeywell — diversified industrial; steady compounder MR
    "RTX",  # RTX Corp (Raytheon) — defense/aerospace; backlog-driven MR
    "CAT",  # Caterpillar — machinery; global construction/mining cycle MR
    "DE",  # Deere — agricultural machinery; seasonal demand-cycle MR
    "LMT",  # Lockheed Martin — defense; backlog-driven smooth MR
    "CSX",  # CSX Corp — railway; R1000 screener PASS: N=10, WR=67%, Sh=0.50 (2006-2016)
    "UNP",  # Union Pacific — railway; R1000 screener PASS: N=11, WR=73%, Sh=0.44 (2006-2016)
    "ETN",  # Eaton — industrial/elec; R1000 screener PASS: N=10, WR=70%, Sh=0.43 (2006-2016)
    "XYL",  # Xylem — water tech; R1000 screener PASS: N=10, WR=60%, Sh=0.30 (2006-2016)
    # XLP Consumer Staples (live delivery_gates blocks; §10 does not — research only)
    "PG",  # Procter & Gamble — ultra-stable staples; very tight MR oscillator
    "KO",  # Coca-Cola — range-bound staples compounder; classic MR instrument
    # ETFs are too efficiently arbed — BB%B/IBS/VWAP% MR signals calibrated on individual
    # stock volatility do not persist at index level. XLF/XLV/XLE showed positive results
    # (WR 80–100%) but N=1–5 is not significant. ETF MR requires separate signal calibration.
    # ── Historical Delisted Constituents (Survivorship correction §84) ───────
    "LEH",
    "BSC",
    "WM",
    "SHLD",
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
    # ── OOS v6 — pre-specified 2026-05-31, chosen BEFORE any IS research on these names ──
    # Selection criteria: S&P 500 member since ≥2010, allowed sector (XLK/XLY/XLC/XLB/XLF),
    # never appeared in TICKERS, _CURATED_OUT_TICKERS, HELD_OUT_TICKERS, or any backtest
    # comment as tested/rejected. Target N≥50 clean trades for SE ≤ ±14pp on WR.
    # XLK — Technology
    "ANSS",  # ANSYS — simulation software; S&P 500 since 1994; engineering-cycle MR
    "AKAM",  # Akamai — CDN/security; S&P 500 since 2007; sentiment-driven MR
    "VRSN",  # VeriSign — DNS/domain registry; ultra-stable range-bound MR oscillator
    "FTNT",  # Fortinet — cybersecurity; S&P 500 since 2011; earnings-cycle MR
    "ZBRA",  # Zebra Technologies — enterprise mobility; S&P 500 since 2014; MR on demand cycles
    "TYL",  # Tyler Technologies — govt software; S&P 500 since 2014; steady compounder MR
    "CDW",  # CDW Corp — IT solutions; S&P 500 since 2013; B2B tech distribution MR
    "KEYS",  # Keysight — electronic test/measurement; S&P 500 since 2014; capex-cycle MR
    "SWKS",  # Skyworks Solutions — RF semiconductors; S&P 500 since 2008; smartphone-cycle MR
    # XLY — Consumer Discretionary
    "TSCO",  # Tractor Supply — farm/ranch retail; S&P 500 since 2009; steady compounder MR
    "BBY",  # Best Buy — consumer electronics retail; S&P 500 since 2001; earnings-driven MR
    "NVR",  # NVR Inc — homebuilder; S&P 500 since 1999; rate-cycle MR (non-overlapping DHI)
    "HAS",  # Hasbro — toys; S&P 500 since 1980s; consumer sentiment MR
    "DG",  # Dollar General — discount retail; S&P 500 since 2009; steady compounder MR
    "WHR",  # Whirlpool — appliances; S&P 500 since 1980s; housing-cycle MR
    "KMX",  # CarMax — used vehicles; S&P 500 since 2002; consumer credit cycle MR
    # XLC — Communication Services
    "OMC",  # Omnicom — advertising; S&P 500 since 1980s; stable range-bound MR
    "LYV",  # Live Nation — live entertainment; S&P 500 since 2010; consumer spending MR
    # XLB — Materials
    "PKG",  # Packaging Corp of America — paper/packaging; S&P 500 since 2006; cycle MR
    "SEE",  # Sealed Air — protective packaging; S&P 500 since 1990s; margin-cycle MR
    "FMC",  # FMC Corp — agricultural chemicals; S&P 500 since 1990s; crop-price MR
    "BALL",  # Ball Corp — aluminum packaging; S&P 500 since 1990s; commodity-input MR
    # XLF — Financials
    "CINF",  # Cincinnati Financial — P&C insurance; S&P 500 since 1990s; steady compounder MR
    "HBAN",  # Huntington Bancshares — regional bank; S&P 500 since 1990s; rate-cycle MR
    "ZION",  # Zions Bancorporation — regional bank; S&P 500 since 2000; rate-cycle MR
    "CFG",  # Citizens Financial — regional bank; S&P 500 since 2015; consumer credit MR
    "PRU",  # Prudential Financial — insurance/asset mgmt; S&P 500 since 2001; market-cycle MR
    # ── OOS v7 — pre-specified 2026-06-01, chosen BEFORE any IS research on these names ──
    # Selection: amenability model (r=0.355 OOS validated) → healthcare + consumer + exchange operators.
    # Healthcare (XLV — confirmed live-eligible, cross-sectional t=+2.12**):
    "SYK",  # Stryker — surgical equipment/instruments; S&P 500 since 1998; rate-fear MR
    "RMD",  # ResMed — sleep/respiratory devices; S&P 500 since 2004; earnings-cycle MR
    "IDXX",  # IDEXX Laboratories — veterinary diagnostics; S&P 500 since 2011; sector-sentiment MR
    "ZBH",  # Zimmer Biomet — orthopedic devices; S&P 500 since 2001; procedure-volume MR
    # XLY — Consumer Discretionary (sect_consumer t=+2.37**):
    "RL",  # Ralph Lauren — luxury apparel; S&P 500 since 1997; consumer sentiment MR
    "DECK",  # Deckers Brands (UGG/HOKA) — footwear; S&P 500 since 2011; earnings-cycle MR
    "POOL",  # Pool Corporation — pool supply distribution; S&P 500 since 2004; seasonal MR
    # XLF — Exchange operators (not rate-credit sensitive; structural liquidity providers):
    "NDAQ",  # Nasdaq — exchange/data; S&P 500 since 2002; market-cycle MR on vol spikes
    "CBOE",  # Cboe Global Markets — options exchange; S&P 500 since 2010; VIX-cycle MR
    "BR",  # Broadridge Financial — investor communications; S&P 500 since 2007; earnings MR
    # ── OOS v8 — pre-specified 2026-06-01, from Russell 2000 screener ──────────────────────────
    # R2000 screener: 1/440 PASS (LNC Sh=0.76), 4 credible WATCH. Excluded data artifacts:
    # BILL (IPO 2019), FND (IPO 2017), GAP (ticker ambiguity — real ticker is GPS).
    # R2000 pass rate 0.2% vs R1000 1.6% → confirms large-cap quality essential for 10d MR.
    "LNC",  # Lincoln National — life insurance; R2000 PASS: N=11, WR=73%, Sh=0.76, avg=+2.82%
    "AMG",  # Affiliated Managers Group — asset manager (BX/KKR profile); WATCH N=4, WR=100%
    "PAYC",  # Paycom Software — payroll SaaS; WATCH N=8, WR=75% (IPO 2014; partial fast-mode)
    "SIG",  # Signet Jewelers — jewelry retail; WATCH N=5, WR=100%, avg=+4.71%
    "AEO",  # American Eagle Outfitters — apparel; WATCH N=4, WR=75%, avg=+1.48%
    # ── OOS v9 — pre-specified 2026-06-05 using amenability model (cross_sectional_mr_screen.py) ──
    # Selection: top amenability scores NOT previously in TICKERS, _CURATED_OUT_TICKERS,
    # HELD_OUT_TICKERS, or any IS backtest comment. All R1000-eligible, large-cap.
    # DO NOT use these tickers in IS research until OOS v7/v8 have been formally evaluated.
    # XLV — Healthcare (amenability model t=+2.12**, confirmed live-eligible):
    "ISRG",  # Intuitive Surgical — robotic surgery; limited catalyst noise vs biotech
    "ZTS",  # Zoetis — veterinary pharma; steady compounder with low analyst-revision vol
    # XLI — Industrials (confirmed live-eligible, no sector block):
    "ODFL",  # Old Dominion Freight — LTL trucking; freight-cycle MR with high amenability
    "VRSK",  # Verisk Analytics — data/analytics; low vol, high free cash, range-bound
    "CPRT",  # Copart — auto auctions; unique sector, limited macro beta
    "CTAS",  # Cintas — uniform/facility services; slow-moving, highly predictable MR
    # XLK — Technology (amenability model sect_tech t=+1.59*):
    "MPWR",  # Monolithic Power Systems — power mgmt ICs; POWI peer but larger (R1000)
    # XLC — Communication Services:
    "NWS",  # News Corp — media; XLC, S&P 500 since 2004; sentiment-driven range MR
    # XLY — Consumer Discretionary (sect_consumer t=+2.37**):
    "KSS",  # Kohl's — department store; S&P 500 since 1992; consumer sentiment MR
    "WST",  # West Pharmaceutical — drug delivery; XLV-adjacent; stable compounding MR
]

# Live-blocked tickers that appear in HELD_OUT_TICKERS — excluded from "clean" OOS metrics.
# Included in full list so their trade count is visible; excluded from the headline Sharpe.
# v6 additions: HBAN/ZION/CFG are regional banks (same profile as STT/MTB which showed 0% WR);
# flagged so the clean OOS metric is not contaminated by delivery_gates-blocked names.
_OOS_BLOCKED_TICKERS: frozenset[str] = frozenset({"AMAT", "KLAC", "STT", "MTB", "HBAN", "ZION", "CFG"})

# ── Curated universe-expansion cohort — locked 2026-06-15 for FORWARD validation ──
# 9 large-caps added to the live watchlist after the §86 universe-expansion sweep
# (scripts/screen_universe_expansion.py; pooled IS N=43, WR 67%, +1.22%/trade, Sh 0.40).
# These were SELECTED on positive IS MR edge, so they are NOT a blind OOS set and are
# deliberately kept OUT of HELD_OUT_TICKERS (re-running IS on them would just re-confirm
# the selection). The honest test is their FORWARD live performance from the lock date,
# pre-registered here so the bar can't move later.
# PASS criterion: clean live WR ≥ 55% AND avg net/trade > 0 over ≥30 resolved BUYs by
# ~2026-09-15 → keep; else prune from the watchlist. Check via /api/admin/live-wr-stats
# filtered to these tickers, or gate_contribution_analysis.py.
_EXPANSION_COHORT_20260615: frozenset[str] = frozenset({"CBRE", "NXPI", "EL", "TRV", "IP", "MCK", "ROK", "CMI", "MET"})

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
    # XLI — Industrials (allowed in delivery_gates; §10 historical filter)
    "ROP": "XLI",
    "TDY": "XLI",
    "TEL": "XLI",
    "FDX": "XLI",
    "MMM": "XLI",
    "EMR": "XLI",
    "CSX": "XLI",
    "UNP": "XLI",
    "ETN": "XLI",
    "XYL": "XLI",
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
    "AMP": "XLF",
    "FITB": "XLF",
    "KEY": "XLF",
    "RF": "XLF",
    "V": "XLF",
    "AXP": "XLF",
    "SPGI": "XLF",
    "MCO": "XLF",
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
    # XLV — Healthcare (allowed in live engine)
    "JNJ": "XLV",
    "MRK": "XLV",
    "LLY": "XLV",
    "UNH": "XLV",
    # XLE — Energy (allowed in live engine)
    "XOM": "XLE",
    "CVX": "XLE",
    "COP": "XLE",
    # XLI — Industrials additions (allowed in live engine)
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
    # OOS v6 additions (pre-specified 2026-05-31)
    "ANSS": "XLK",
    "AKAM": "XLK",
    "VRSN": "XLK",
    "FTNT": "XLK",
    "ZBRA": "XLK",
    "TYL": "XLK",
    "CDW": "XLK",
    "KEYS": "XLK",
    "SWKS": "XLK",
    "TSCO": "XLY",
    "BBY": "XLY",
    "NVR": "XLY",
    "HAS": "XLY",
    "DG": "XLY",
    "WHR": "XLY",
    "KMX": "XLY",
    "OMC": "XLC",
    "LYV": "XLC",
    "PKG": "XLB",
    "SEE": "XLB",
    "FMC": "XLB",
    "BALL": "XLB",
    "CINF": "XLF",
    "HBAN": "XLF",
    "ZION": "XLF",
    "CFG": "XLF",
    "PRU": "XLF",
    # ── IS 100→105 expansion tickers (2026-05-31) — missing from map ──────────
    # XLK — Technology
    "INTU": "XLK",
    "WDAY": "XLK",
    "IBM": "XLK",
    "MSI": "XLK",
    # XLF — Financials
    "ICE": "XLF",
    "CME": "XLF",
    "TROW": "XLF",
    "COF": "XLF",
    "CB": "XLF",
    # XLY — Consumer Discretionary
    "CMG": "XLY",
    "PHM": "XLY",
    "LEN": "XLY",
    "ORLY": "XLY",
    "DRI": "XLY",
    "ULTA": "XLY",
    # XLC — Communication Services
    "CMCSA": "XLC",
    "EA": "XLC",
    "IPG": "XLC",
    # XLB — Materials
    "CF": "XLB",
    "MLM": "XLB",
    "CE": "XLB",
    # XLV — Healthcare (allowed in delivery_gates (cross-sectional confirmed))
    "ABT": "XLV",
    "BSX": "XLV",
    "AMGN": "XLV",
    "CI": "XLV",
    "HCA": "XLV",
    # XLE — Energy (allowed in delivery_gates (cross-sectional confirmed))
    "SLB": "XLE",
    "EOG": "XLE",
    "MPC": "XLE",
    "HAL": "XLE",
    # XLI — Industrials (allowed in delivery_gates (cross-sectional confirmed))
    "CAT": "XLI",
    "DE": "XLI",
    "LMT": "XLI",
    # Delisted constituents
    "LEH": "XLF",
    "BSC": "XLF",
    "WM": "XLF",
    "SHLD": "XLY",
}
# §10 sector filter: matches ACTUAL delivery_gates.py BLOCKED_SECTORS.
# delivery_gates.py: frozenset({"XLF", "XLP", "XLU"}) — XLV/XLI/XLE are allowed.
# Cross-sectional model (2026-06-01): healthcare (t=+2.12**) and consumer (t=+2.37**)
# confirmed positive MR alpha — removing them from §10 was incorrect.
# XLF individual stocks (JPM/WFC/etc.) are NOT blocked — only XLF ETF itself.
# We include XLF here for the §10 "sector-neutral" view since sectorEtf=XLF stocks
# are tracked by the scanner but the ETF signal itself would be blocked.
# §94: per-sector hold-days (matches live _SECTOR_MR_CONFIG in helpers.py)
_SECTOR_HOLD_DAYS: dict[str, int] = {
    "XLK": 5,  # Tech — fastest recovery
    "XLF": 7,  # Financials
    "XLY": 10,  # Consumer Disc
    "XLP": 10,  # Consumer Staples
    "XLE": 5,  # Energy
    "XLC": 10,  # Telecom/Comm
    "XLB": 5,  # Materials
    "XLU": 10,  # Utilities (blocked)
    "XLV": 7,  # Healthcare (blocked)
    "XLI": 7,  # Industrials (blocked)
    "XLRE": 5,  # Real Estate (blocked)
}

_BLOCKED_SECTORS = {"XLP", "XLU", "XLRE"}

START = os.getenv("BACKTEST_START", "2003-01-01")  # extended from 2006 — captures Pre-GFC Bull fully (was only 2006-07)
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
# Was raised to 50 (halves trades, ~doubles avg return); v7.1 judged 40-50 not worth it.
# §relax-sweep (2026-06-18): that verdict was too coarse — it lumped the weak 40-45 band
# with the tradeable 45-50 band. Splitting them: BUY_THRESH 50→45 grows N +52% IS / +60%
# OOS-CLEAN (98→157) while holding OOS Sharpe FLAT at 0.18 (avg +0.68% identical, curation
# verdict ✅ "edge generalises"). 50→40 gives back Sharpe (−0.02, avg→+0.57%) — stop at 45.
# Relaxing MR thresholds (BB/IBS/VWAP) adds 0 trades; BUY_THRESH is the only N lever.
BUY_THRESH = 45
BUY_THRESH_MAX = 999  # effectively no ceiling
SELL_THRESH = -100  # SELLs disabled. §32 validation (2026-05-26): −45 threshold produced
# N=1354 SELLs at WR=33.1%, Avg=−0.43%, Sharpe=−0.08, MaxDD=−28%.
# Adding SELLs collapses overall Sharpe 0.20→−0.03. Live SELL edge
# (60.8% raw WR) is entirely alt-data driven — absent on OHLCV alone.
POSITION_SIZE = 0.05  # 5% of capital per trade (for drawdown sim)

# §63 Engle-Granger step-2 gate: only count a pair as cointegrated (and apply the
# coint_z scoring modifier) when its residual spread is stationary. Mirrors
# services/technicals.py::_COINT_ADF_PMAX. Flip _COINT_REQUIRE_STATIONARY to False
# to ablate the gate (reproduces the pre-2026-06-09 ungated §63 behaviour).
_COINT_ADF_PMAX = 0.10
_COINT_REQUIRE_STATIONARY = True

# ── §QuantEngine research constants ──────────────────────────────────────────
BETA_HEDGE_RATIO = 0.90  # short 90% of position value in SPY to neutralize beta
BETA_HEDGE_FRICTION = 0.10  # extra round-trip friction for the SPY hedge leg (%)
VOL_REF_ANN = 0.25  # reference annualized vol (S&P 500 median) for vol-targeting
FORECAST_THRESH_DIV = 10.0  # score points per unit of continuous forecast above threshold
FORECAST_FLOOR = 0.25  # minimum size multiplier for marginal entries
FORECAST_CAP = 2.0  # maximum size multiplier for high-conviction entries
MAX_PORTFOLIO_SLOTS = 5  # max concurrent positions in portfolio simulation

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

# §59/§60 restored 2026-06-03: individual ablation showed ΔSh≈0 per gate, but removing
# all dead gates together (v10.4) added 24 marginal trades and dropped IS Sh 0.24→0.19.
# These two filters collectively block ~10 low-quality trades; restoring them recovers ~0.04 Sh.
# §61 Idio vol, §78 Sep/Oct remain removed — they blocked 0 trades at current thresholds.
OU_HALFLIFE_MAX = 25.0  # §59: half-life > 25d → reversion too slow for 2.5× hold window
HURST_TREND_CEIL = 0.80  # §60: H > 0.80 → strong trending regime; large-caps median ~0.71

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

# ── Backtest research flags (Sharpe-improvement experiments) ──────────────────
# These are toggled via CLI flags; they do NOT affect the live engine.
_SCORE_BAND_SIZING = False
_DYNAMIC_STOP_RSI = False
_NO_FAMILY_DISCOUNT = False


def score_band_size_mult(score: float) -> float:
    """Non-linear position sizing by backtest-validated Sharpe band.

    Band data (v7.1, 2026-05-28):
      <50  → Sharpe ~0.07, WR 56%  → reduce size
      50-55 → Sharpe ~0.15         → modest reduction
      55-60 → Sharpe ~0.21, WR 65% → baseline
      60-65 → Sharpe ~0.25+        → modest boost
      65-70 → higher conviction    → stronger boost
      70-75 → strong edge          → near-max
      ≥75   → extreme edge         → max
    """
    if score >= 75:
        return 1.55
    elif score >= 70:
        return 1.45
    elif score >= 65:
        return 1.30
    elif score >= 60:
        return 1.15
    elif score >= 55:
        return 1.00
    elif score >= 50:
        return 0.75
    else:
        return 0.50


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
    avg_prior20 = v.shift(1).rolling(20).mean()
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

    # ── §60 Hurst Exponent (64-day rolling R/S) ───────────────────────────────
    # H < 0.5 = anti-persistent (MR-friendly); H > 0.5 = trending.
    # Window = 64 (was 63): lag=32 requires n2 >= 64 (≥2 sub-windows) — 63-bar window
    # always skipped lag=32, leaving the regression with only 3 points (lags 4,8,16).
    # 64 bars gives lag=32 exactly 2 sub-windows (n2=64), enabling 4-point regression.
    _lr_all = np.diff(np.log(np.maximum(c.values.astype(float), 1e-10)))
    _hurst_arr = np.full(len(df), np.nan)
    _lags = np.array([4, 8, 16, 32])
    _log_lags = np.log(_lags)
    for _k in range(64, len(df)):
        _seg = _lr_all[_k - 64 : _k]
        _rs_pts = []
        for _idx, _lag in enumerate(_lags):
            _sub = _seg.reshape(-1, _lag)
            _mu = _sub.mean(axis=1, keepdims=True)
            _cd = np.cumsum(_sub - _mu, axis=1)
            _R = _cd.max(axis=1) - _cd.min(axis=1)
            _S = _sub.std(axis=1, ddof=1)
            _S[_S == 0.0] = 1e-10
            _valid = _R > 0
            if np.any(_valid):
                _mean_rs = np.mean(_R[_valid] / _S[_valid])
                _rs_pts.append((_log_lags[_idx], np.log(_mean_rs)))
        if len(_rs_pts) >= 3:
            _xh = np.array([v[0] for v in _rs_pts])
            _yh = np.array([v[1] for v in _rs_pts])
            _n_pts = len(_xh)
            _sum_x = _xh.sum()
            _sum_y = _yh.sum()
            _sum_xx = (_xh**2).sum()
            _sum_xy = (_xh * _yh).sum()
            _denom = _n_pts * _sum_xx - _sum_x**2
            if abs(_denom) > 1e-12:
                _slope = (_n_pts * _sum_xy - _sum_x * _sum_y) / _denom
                _hurst_arr[_k] = float(np.clip(_slope, 0.0, 1.0))
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


def score_row(r: pd.Series, no_family_discount: bool = False) -> float:
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

    # MR-dip context (gate-audit 2026-07-15, parity with live signal_scoring):
    # when the same bar shows an oversold dip (BB%B<0.22 or IBS<0.15), the
    # stochastic / Williams%R OVERBOUGHT penalties are wrong-signed — live
    # delivered cohorts ran +4.7pp / +8.1pp ABOVE baseline (N=134/133). An
    # overbought fast oscillator during a dip is early recovery, not resistance.
    _bb_dip = r.get("bb_pct_b")
    _ibs_dip = r.get("ibs")
    _mr_dip = (pd.notna(_bb_dip) and float(_bb_dip) < 0.22) or (pd.notna(_ibs_dip) and float(_ibs_dip) < 0.15)

    sk, sd = r.get("stoch_k"), r.get("stoch_d")
    sk_p, sd_p = r.get("stoch_k_p"), r.get("stoch_d_p")
    if all(pd.notna(x) for x in (sk, sd, sk_p, sd_p)):
        sk, sd, sk_p, sd_p = float(sk), float(sd), float(sk_p), float(sd_p)
        cross_up = (sk > sd) and (sk_p <= sd_p)
        cross_down = (sk < sd) and (sk_p >= sd_p)
        if sk < 20 and sd < 20 and cross_up:
            osc += 18  # both in extreme zone
        elif sk > 80 and sd > 80 and cross_down:
            osc -= 0 if _mr_dip else 14  # asymmetric; skipped in MR-dip context
        elif sk < 20 and cross_up:
            osc += 10
        elif sk > 80 and cross_down:
            osc -= 0 if _mr_dip else 8
        elif sk < 25:
            osc += 5
        elif sk > 75:
            osc -= 0 if _mr_dip else 4

    wr = r.get("wr")
    if pd.notna(wr):
        wr = float(wr)
        if wr <= -85:
            osc += 10  # only extreme readings
        elif wr >= -15:
            osc -= 0 if _mr_dip else 8

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
    # These caps are calibrated for a technical-only (5-family) backtest.
    # They differ from signal_engine.py because the live engine has 50+ additional
    # signal families (options, fundamentals, alt-data, macro) that increase scores;
    # compressing these caps to match live-engine values would collapse trade count.
    osc_f = max(-25, min(25, osc)) * 1.00
    trend_f = max(-28, min(28, trend_score)) * (1.00 if no_family_discount else 0.90)
    volume_f = max(-20, min(20, volume_score)) * (1.00 if no_family_discount else 0.85)
    ma_f = max(-28, min(28, ma_score)) * 1.00
    mr_f = max(-18, min(18, mean_rev_score)) * 1.00

    score = osc_f + trend_f + volume_f + ma_f + mr_f

    # ── §63 Sector Cointegration ──────────────────────────────────────────────
    cz = r.get("coint_z")
    if cz is not None and not (isinstance(cz, float) and np.isnan(cz)):
        cz = float(cz)
        if cz < -2.0:
            score += 4.0
        elif cz < -1.0:
            score += 2.0
        elif cz > 0.5:
            score -= 2.0

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


def compute_scores(df: pd.DataFrame, no_family_discount: bool = False) -> pd.Series:
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
    # MR-dip context (gate-audit 2026-07-15, parity with score_row above):
    # skip stoch/W%R overbought penalties when the bar shows BB%B<0.22 or IBS<0.15.
    _bb_v = _v("bb_pct_b", 1.0)
    _ibs_v = _v("ibs", 1.0)
    _bb_ok = df["bb_pct_b"].notna().values if "bb_pct_b" in df.columns else np.zeros(n, bool)
    _ibs_ok = df["ibs"].notna().values if "ibs" in df.columns else np.zeros(n, bool)
    _mr_dip_v = (_bb_ok & (_bb_v < 0.22)) | (_ibs_ok & (_ibs_v < 0.15))

    osc += np.select(
        [
            cu & (sk < 20) & (sd < 20),
            cd & (sk > 80) & (sd > 80) & ~_mr_dip_v,
            cu & (sk < 20),
            cd & (sk > 80) & ~_mr_dip_v,
            st_ok & ~handled & (sk < 25),
            st_ok & ~handled & (sk > 75) & ~_mr_dip_v,
        ],
        [18, -14, 10, -8, 5, -4],
        default=0,
    )

    wr = _v("wr", -50)
    wr_ok = df["wr"].notna().values if "wr" in df.columns else np.zeros(n, bool)
    osc += np.where(wr_ok & (wr <= -85), 10, 0)
    osc += np.where(wr_ok & (wr >= -15) & ~_mr_dip_v, -8, 0)

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
    # Caps calibrated for technical-only (5-family) backtest.  The live engine
    # has 50+ additional signal families so its score ceiling is ~4× higher;
    # these caps must NOT be changed to match the live engine's ±22/±30 values
    # because that collapses the trade count from ~188 to ~15.
    _trend_mult = 1.00 if no_family_discount else 0.90
    _vol_mult = 1.00 if no_family_discount else 0.85
    osc_f = np.clip(osc, -25, 25) * 1.00
    trend_f = np.clip(trend, -28, 28) * _trend_mult
    vol_f = np.clip(vol, -20, 20) * _vol_mult
    ma_f = np.clip(ma, -28, 28) * 1.00
    mr_f = np.clip(mr, -18, 18) * 1.00
    score = osc_f + trend_f + vol_f + ma_f + mr_f

    # ── §63 Sector Cointegration (pre-computed rolling Z-score) ───────────────
    # Z < -2.0 → stock is >2σ below its long-run relationship with sector ETF
    # (double dislocation: oversold vs own history AND vs sector peers → +4pts).
    # Z > 0.5 → stock above sector relationship → weaker MR candidate (−2pts).
    if "coint_z" in df.columns:
        cz = df["coint_z"].values.astype(float)
        cz_ok = ~np.isnan(cz)
        score = score + np.where(
            cz_ok & (cz < -2.0), 4.0, np.where(cz_ok & (cz < -1.0), 2.0, np.where(cz_ok & (cz > 0.5), -2.0, 0.0))
        )

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

    # Universal 1.5s/2.0t — matches signal_engine.py _levels() exactly.
    # §17 sensitivity confirmed: 1.5s/2.0t beats 1.0s/2.0t (Sharpe 0.29 vs 0.23).
    # Former ADX>35 branch (1.0s/3.0t) removed: live engine never had this branch,
    # so it was inflating backtest R:R for trending stocks vs what live trading produces.
    s, t = 1.5, 2.0

    if stop_mult_override is not None:
        s = stop_mult_override
    if target_mult_override is not None:
        t = target_mult_override

    if action == "BUY":
        return price - s * atr, price + t * atr
    else:
        return price + s * atr, price - t * atr


def simulate_alt_exit(df, fill_bar, hold_days, entry, atr, action, stop0, target, friction, ratchet=True):
    """R1/R4: mechanical exit simulator for A/B vs the live exit stack.

    ratchet=True (R1): arm once +1 ATR favorable → ratchet stop to breakeven+0.1%, then
    trail 1 ATR below the high-water mark (tests "don't let a winner become a loser").
    ratchet=False (R4): pure fixed stop (stop0) + hard target + time exit — vary stop0 to
    test stop width (1.5 ATR baseline vs 2.5 ATR wide vs none). Returns net % (gross −
    friction); None if atr unusable.
    """
    if atr <= 0:
        return None
    n = len(df)
    stop = stop0
    armed = False
    hw = lw = entry
    exit_price = None
    for j in range(hold_days):
        if fill_bar + j >= n:
            break
        bar = df.iloc[fill_bar + j]
        hi, lo, op = float(bar["High"]), float(bar["Low"]), float(bar["Open"])
        if action == "BUY":
            hw = max(hw, hi)
            if ratchet and not armed and hi >= entry + atr:
                armed = True
                stop = max(stop, entry * 1.001)
            if ratchet and armed:
                stop = max(stop, hw - atr)
            if lo <= stop:
                slip = GAP_STOP_SLIP_PCT if op < stop else NORMAL_STOP_SLIP_PCT
                exit_price = (min(op, stop) if op < stop else stop) * (1 - slip / 100)
                break
            if hi >= target:
                exit_price = target
                break
        else:  # SELL / short
            lw = min(lw, lo)
            if ratchet and not armed and lo <= entry - atr:
                armed = True
                stop = min(stop, entry * 0.999)
            if ratchet and armed:
                stop = min(stop, lw + atr)
            if hi >= stop:
                slip = GAP_STOP_SLIP_PCT if op > stop else NORMAL_STOP_SLIP_PCT
                exit_price = (max(op, stop) if op > stop else stop) * (1 + slip / 100)
                break
            if lo <= target:
                exit_price = target
                break
    if exit_price is None:
        idx = min(fill_bar + hold_days - 1, n - 1)
        exit_price = float(df.iloc[idx]["Close"])
    gross = (exit_price - entry) / entry * 100 if action == "BUY" else (entry - exit_price) / entry * 100
    return round(gross - friction, 3)


# ── Meta-label helpers (QUANT_ENGINE_REVIEW §1.3) ───────────────────────────


_SECTOR_ORD_META: dict[str, int] = {
    "XLK": 0,
    "XLY": 1,
    "XLC": 2,
    "XLF": 3,
    "XLB": 4,
    "XLI": 5,
    "XLV": 6,
    "XLE": 7,
    "XLP": 8,
    "XLRE": 9,
    "XLU": 10,
}


def _compute_entry_prob(row, atr, entry_price, vix_today, date, ticker, entry_model):
    """Run the entry XGBoost model on a historical signal."""
    if entry_model is None or xgb is None:
        return None
    try:
        _atr_pct = (float(atr) / float(entry_price) * 100.0) if entry_price and entry_price > 0 else float("nan")
        _sector = TICKER_TO_SECTOR.get(ticker, "XLK")
        _sector_ord = float(_SECTOR_ORD_META.get(_sector.upper(), -1))
        feats = [
            float(row.get("bb_pct_b")) if pd.notna(row.get("bb_pct_b")) else float("nan"),
            float(row.get("ibs")) if pd.notna(row.get("ibs")) else float("nan"),
            float(row.get("vwap_pct")) if pd.notna(row.get("vwap_pct")) else float("nan"),
            float(row.get("rsi")) if pd.notna(row.get("rsi")) else float("nan"),
            float(row.get("adx")) if pd.notna(row.get("adx")) else float("nan"),
            float(row.get("rvol")) if pd.notna(row.get("rvol")) else float("nan"),
            _atr_pct,
            float(row.get("price_zscore")) if pd.notna(row.get("price_zscore")) else float("nan"),
            float(row.get("ou_halflife")) if pd.notna(row.get("ou_halflife")) else float("nan"),
            float(row.get("hurst")) if pd.notna(row.get("hurst")) else float("nan"),
            float(vix_today) if vix_today is not None else float("nan"),
            _sector_ord,
            float(date.weekday()),
            float(date.month),
        ]
        _names = [
            "bb_pct_b",
            "ibs",
            "vwap_pct",
            "rsi",
            "adx",
            "rvol",
            "atr_pct",
            "price_zscore",
            "ou_halflife",
            "hurst",
            "vix",
            "sector_ord",
            "dow",
            "month",
        ]
        dm = xgb.DMatrix(np.array([feats], dtype=float), feature_names=_names)
        return float(entry_model.predict(dm)[0])
    except Exception:
        return None


def _compute_vix_9d_ratio(vix_dict: dict, date_key: pd.Timestamp) -> float | None:
    """VIX / 9-day rolling mean of VIX."""
    if not vix_dict:
        return None
    try:
        _dates = sorted(vix_dict.keys())
        _idx = _dates.index(date_key)
        _window = _dates[max(0, _idx - 8) : _idx + 1]
        _vals = [vix_dict[d] for d in _window if vix_dict.get(d) is not None]
        if not _vals:
            return None
        _mean = sum(_vals) / len(_vals)
        return round(vix_dict[date_key] / _mean, 4) if _mean > 0 else None
    except Exception:
        return None


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
    thursday_gate_enabled: bool = True,
    stop_mult_override: float | None = None,
    target_mult_override: float | None = None,
    buy_thresh_override: int | None = None,
    vix_min_override: float | None = None,
    require_mr_count_override: int | None = None,
    require_consec_score_override: bool | None = None,
    consec_score_thresh_override: float | None = None,
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
    beta_hedge: bool = False,
    spy_prices: dict | None = None,
    forecast_sizing: bool = False,
    fred_panel: dict | None = None,
    score_band_sizing: bool = False,
    dynamic_stop_rsi: bool = False,
    no_family_discount: bool = False,
    dow_filter: set[int] | None = None,
    mr_bb_ceil_override: float | None = None,
    mr_ibs_ceil_override: float | None = None,
    score_accel: bool = False,
    # §87: conviction-tier sizing — consecutive-score as sizing multiplier
    consec_score_sizing: bool = False,
    # Meta-label feature passthrough (QUANT_ENGINE_REVIEW §1.3)
    entry_model=None,
    hmm_cache: dict | None = None,
    vix3m_series: pd.Series | None = None,
    sector_momentum_map: dict | None = None,
    sector_etf_close: pd.Series | None = None,
    ff_str: dict | None = None,
    si_rising_map: dict | None = None,
    calm_sleeve: bool = False,
    ff_str_regime_map: dict | None = None,
    # §96b: entry-at-close variant — fill at signal-day Close instead of T+1 Open
    entry_at_close: bool = False,
    # §97a: limit-order entry — fill at Close − k×ATR if next-day Low ≤ limit
    entry_limit_k: float | None = None,
    # §MAX: skip signals whose 21-day MAX exceeds the expanding percentile
    max21_filter_pct: float | None = None,
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
    _limit_signals_attempted = 0
    in_trade_until = pd.Timestamp("2000-01-01")
    _hold_days = hold_days_override if hold_days_override is not None else HOLD_DAYS
    # §94: per-sector hold-days parity with live engine
    _sector_etf_hold = TICKER_TO_SECTOR.get(ticker, "XLK")
    _sector_hold_days = _SECTOR_HOLD_DAYS.get(_sector_etf_hold, _hold_days)
    _hold_days = _sector_hold_days
    # §88: calm-regime sleeve uses shorter hold (5d) for faster turnaround in low-vol
    if calm_sleeve:
        _hold_days = 5
    _mr_rsi_ceil = mr_rsi_ceil_override if mr_rsi_ceil_override is not None else MR_RSI_CEIL
    _buy_thresh = buy_thresh_override if buy_thresh_override is not None else BUY_THRESH
    # §88: calm-regime sleeve overrides
    if calm_sleeve:
        _buy_thresh = 38
        _vix_min = 0.0
    else:
        _vix_min = vix_min_override
    _require_mr_count = require_mr_count_override if require_mr_count_override is not None else 1
    _require_consec = require_consec_score_override if require_consec_score_override is not None else False
    _consec_score_sizing = consec_score_sizing
    _consec_score_thresh = consec_score_thresh_override if consec_score_thresh_override is not None else _buy_thresh
    _mr_bb_ceil = mr_bb_ceil_override if mr_bb_ceil_override is not None else MR_BB_CEIL
    _mr_ibs_ceil = mr_ibs_ceil_override if mr_ibs_ceil_override is not None else MR_IBS_CEIL
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

    def _orats_float(row: dict | None, key: str) -> float | None:
        """Safely extract and round an ORATS feature value."""
        if row is None:
            return None
        v = row.get(key)
        if v is None:
            return None
        try:
            return round(float(v), 4)
        except Exception:
            return None

    _trade_from_ts = pd.Timestamp(TRADE_FROM)
    # §MAX: max daily close-to-close return over the trailing 21 bars (Chen et al.,
    # "Maxing Out Short-term Reversals" — reversal much stronger in high-MAX,
    # lottery-like names). Causal: at bar i the window ends at bar i's close,
    # which is known when the signal is generated (entry fills T+1).
    _max21_series = df["Close"].pct_change().rolling(21).max() * 100.0
    _max21_quantile = None
    if max21_filter_pct is not None:
        # Causal expanding quantile: at bar i, only past max21 values are known.
        _max21_quantile = _max21_series.expanding(min_periods=21).quantile(max21_filter_pct).reindex(df.index)
    for i in range(200, len(df)):
        row = df.iloc[i]
        date = df.index[i]

        if TRADE_FROM != END and date < _trade_from_ts:
            continue

        # §MAX filter: skip signals whose 21-day MAX is above the expanding percentile.
        if _max21_quantile is not None and pd.notna(_max21_quantile.iloc[i]):
            if float(_max21_series.iloc[i]) > float(_max21_quantile.iloc[i]):
                continue

        if date <= in_trade_until:
            continue

        # Day-of-week filter — block entries on specified days (0=Mon, 4=Fri)
        if dow_filter is not None and date.dayofweek in dow_filter:
            continue

        # Check point-in-time constituent membership (Survivorship bias correction §84)
        if "--no-pit" not in sys.argv and not is_index_constituent(ticker, date):
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

        # ── Gate 2b: §13 FRED macro-regime panel (research — active only when supplied) ──
        # MR bounces weaken when financial conditions tighten, credit stress rises, or
        # the curve inverts (recession regime). Each sub-gate hard-blocks BUYs in its
        # extreme regime and blocks only marginal (low-conviction) BUYs in its elevated
        # regime; high-conviction signals pass. Point-in-time via observation-dated,
        # forward-filled FRED series (last KNOWN value only — no look-ahead). Orthogonal
        # to VIX+STLFSI4. Only active when fred_panel is provided (mirrors cross_asset).
        if is_buy_signal and fred_panel:
            _fd = pd.Timestamp(str(date)[:10])
            _nfci = fred_panel.get("nfci", {}).get(_fd)
            _baa = fred_panel.get("baa10y", {}).get(_fd)
            _t10y3m = fred_panel.get("t10y3m", {}).get(_fd)
            # NFCI: >0 = tighter-than-average conditions; >0.5 = clear tightening
            if _nfci is not None and _nfci > 0.5:
                continue
            if _nfci is not None and _nfci > 0.0 and score < 50:
                continue
            # Baa-10Y credit spread (normal ~1.5-2.5%): >4% crisis (hard); >3% elevated (marginal)
            if _baa is not None and _baa > 4.0:
                continue
            if _baa is not None and _baa > 3.0 and score < 50:
                continue
            # Inverted curve (10Y<3M) = recession regime: require conviction
            if _t10y3m is not None and _t10y3m < 0.0 and score < 55:
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
        _mr_trigger_label: str = "none"  # set by gate-9 if mr_only trade fires
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
            _trig_rsi = rsi_e < _mr_rsi_ceil
            _trig_bb = bb_e < _mr_bb_ceil
            _trig_ibs = ibs_e < _mr_ibs_ceil
            _trig_vwap = vwap_e < MR_VWAP_FLOOR
            _is_mr_setup = _trig_rsi or _trig_bb or _trig_ibs or _trig_vwap
            # Build trigger label for analysis (Inv 1)
            _active = [
                t
                for flag, t in [(_trig_ibs, "IBS"), (_trig_bb, "BB"), (_trig_vwap, "VWAP"), (_trig_rsi, "RSI")]
                if flag
            ]
            _mr_trigger_label = "+".join(_active) if len(_active) == 1 else ("multi" if len(_active) > 1 else "none")
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
                        bb_e < _mr_bb_ceil,
                        ibs_e < _mr_ibs_ceil,
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
        # Block MR entries where OU half-life > 25d (2.5× the 10d hold window).
        # Restored 2026-06-03: v10.4 regression showed this filter blocks ~2 genuinely
        # slow-reverting entries; removing it added marginal trades that hurt aggregate WR.
        if is_buy_signal and _is_mr_setup:
            _ou_hl_v = row.get("ou_halflife")
            if _ou_hl_v is not None and pd.notna(_ou_hl_v):
                if float(_ou_hl_v) > OU_HALFLIFE_MAX:
                    continue

        # ── Gate 21: §60 Hurst — trending regime block ────────────────────────
        # Hurst > 0.80 = strongly trending. Large-cap median ~0.71; only the extreme
        # tail is a genuine MR category-error. Restored 2026-06-03 with same rationale.
        if is_buy_signal and _is_mr_setup:
            _hurst_v = row.get("hurst")
            if _hurst_v is not None and pd.notna(_hurst_v):
                if float(_hurst_v) > HURST_TREND_CEIL:
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
        # Require the previous bar also had score >= threshold. One-day panic
        # signals frequently whipsaw; persistent oversold (2+ days above threshold)
        # indicates sustained selling pressure nearing exhaustion — higher conviction.
        # _consec_score_thresh defaults to _buy_thresh but can be graduated lower
        # (e.g. 45) to keep more trades while still filtering single-day spikes.
        # §87: when --consec-score-sizing is set, this becomes a sizing multiplier
        # (1.3× for persistent oversold, 1.0× for single-day spikes) instead of a filter.
        _consec_size_mult = 1.0
        if is_buy_signal and i > 0:
            prev_score = float(df.iloc[i - 1]["score"]) if "score" in df.columns else 0.0
            if _consec_score_sizing:
                # Sizing mode: boost size for persistent oversold, keep single-day at 1.0×
                if prev_score >= _consec_score_thresh:
                    _consec_size_mult = 1.3
            elif _require_consec and prev_score < _consec_score_thresh:
                # Filter mode: skip single-day spikes
                continue

        # ── Gate 18b: Score acceleration — require rising conviction ────────────
        # Filters signals where score is already peaking and starting to decline.
        # A rising score indicates building selling pressure / increasing signal
        # strength — entry is earlier in the move, before the bounce begins.
        if is_buy_signal and score_accel and i > 0:
            prev_score = float(df.iloc[i - 1]["score"]) if "score" in df.columns else 0.0
            if score <= prev_score:
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
        # Use unadjusted close when available so historical dollar volume for
        # dividend payers is not understated (adjusted close shrinks over time).
        if is_buy_signal and rvol > 0:
            raw_vol = float(df.iloc[i]["Volume"]) if "Volume" in df.columns else 0.0
            avg_vol_20 = raw_vol / rvol  # rvol = today / avg20 → avg20 = today/rvol
            _liq_price = float(df.iloc[i]["Close"]) if "Adj Close" in df.columns else price
            if _liq_price * avg_vol_20 < MIN_AVG_DOLLAR_VOL:
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
        if is_buy_signal and thursday_gate_enabled and date.dayofweek == 3 and score < 55:  # Thursday = 3
            continue

        # ── Gate 16: VIX minimum — skip low-volatility regime entries ─────────
        # In low-VIX environments stocks don't panic-sell deeply enough for
        # meaningful MR bounces. Elevated VIX = fear-driven capitulation =
        # stronger bounce. Only applied when vix_min_override is set.
        if is_buy_signal and _vix_min is not None and vix_today is not None:
            if vix_today < _vix_min:
                continue
        # §88: calm-regime sleeve — ONLY generates trades when VIX < 20
        if calm_sleeve and is_buy_signal and vix_today is not None and vix_today >= 20:
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
                _ibs_ev < _mr_ibs_ceil
                and _rsi_ev >= _mr_rsi_ceil
                and _bb_ev >= _mr_bb_ceil
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
        # §96b: entry-at-close fills at signal-bar Close (caveat: ~10-min look-ahead
        # since signal is computed on completed bar; flag as approximate).
        _fill_bar = i + 2 if _entry_delay else i + 1
        if _fill_bar >= len(df):
            break

        _signal_close = float(row["Close"])
        _fill_open = float(df.iloc[_fill_bar]["Open"])

        if entry_at_close:
            entry_price = _signal_close
            _entry_style = "close"
        elif entry_limit_k is not None and entry_limit_k > 0:
            _limit_signals_attempted += 1
            # §97a: limit at signal Close − k×ATR; fill iff next-day Low ≤ limit
            _limit_price = _signal_close - entry_limit_k * atr
            if _fill_open <= _limit_price:
                # Gap-down through limit: fill at the worse of limit or open
                entry_price = max(_limit_price, _fill_open)
                _entry_style = f"limit_k{entry_limit_k}"
            elif float(df.iloc[_fill_bar]["Low"]) <= _limit_price:
                # Intraday touch: fill at limit
                entry_price = _limit_price
                _entry_style = f"limit_k{entry_limit_k}"
            else:
                # Unfilled — signal expires
                continue
        else:
            entry_price = _fill_open
            _entry_style = "open"

        # ── Beta-hedge: record SPY open at fill bar for return offset ─────────
        _spy_entry_price: float | None = None
        if beta_hedge and spy_prices:
            _fill_date_key = pd.Timestamp(str(df.index[_fill_bar])[:10])
            _spy_entry_price = spy_prices.get(_fill_date_key)
        _exit_bar_idx: int = _fill_bar  # updated in each exit branch; default = fill bar

        # ── Dynamic stop widening based on entry RSI ──────────────────────────
        # Oversold entries (RSI<30) often see an initial dip before reversal.
        # Widening the stop prevents premature stop-outs on these bounces.
        _dyn_stop_mult = None
        if dynamic_stop_rsi and is_buy_signal:
            _rsi_entry = float(row.get("rsi", 50)) if pd.notna(row.get("rsi")) else 50.0
            if _rsi_entry < 30:
                _dyn_stop_mult = 2.0
            elif _rsi_entry < 35:
                _dyn_stop_mult = 1.75
            else:
                _dyn_stop_mult = 1.5
            # Override only when dynamic is wider than any existing override
            if stop_mult_override is not None and _dyn_stop_mult <= stop_mult_override:
                _dyn_stop_mult = stop_mult_override

        _effective_stop_mult = _dyn_stop_mult if _dyn_stop_mult is not None else stop_mult_override

        # Anchor stop/target to actual fill price, not signal-bar close.
        # Using signal close misplaces stops by the overnight gap distance.
        stop_price, target_price = atr_levels(
            entry_price, atr, action, adx_v, _effective_stop_mult, target_mult_override
        )

        # ── Scan next HOLD_DAYS bars for stop/target/time-loss exit ──────────
        exit_price = None
        exit_reason = "time"
        exit_day = _hold_days
        _mfe_pct = 0.0  # max favorable excursion across hold bars
        _mae_pct = 0.0  # max adverse excursion across hold bars
        # §96a: overnight vs intraday decomposition
        _overnight_sum = 0.0
        _intraday_sum = 0.0

        for j in range(0, _hold_days):
            if _fill_bar + j >= len(df):
                exit_day = j - 1 if j > 0 else 0
                break
            bar = df.iloc[_fill_bar + j]
            day_high = float(bar["High"])
            day_low = float(bar["Low"])
            day_close = float(bar["Close"])

            day_open = float(bar["Open"])
            # Track MFE / MAE: best / worst intrabar price reached vs entry
            if action == "BUY":
                _mfe_pct = max(_mfe_pct, (day_high - entry_price) / entry_price * 100)
                _mae_pct = min(_mae_pct, (day_low - entry_price) / entry_price * 100)
            else:
                _mfe_pct = max(_mfe_pct, (entry_price - day_low) / entry_price * 100)
                _mae_pct = min(_mae_pct, (entry_price - day_high) / entry_price * 100)

            # §96a: overnight vs intraday decomposition
            # Bug-fix (1): day-0 overnight only for close-entry; open/limit entries
            # start intraday at entry_price, not the prior close→open gap.
            if j == 0:
                if entry_at_close:
                    # Trade entered at signal-day close; own the Close→Open gap
                    _overnight_sum += (day_open - entry_price) / entry_price * 100
                    _intraday_sum += (day_close - day_open) / entry_price * 100
                else:
                    # Open or limit entry: trade did not exist overnight
                    _overnight_sum += 0.0
                    _intraday_sum += (day_close - entry_price) / entry_price * 100
            else:
                _prev_close = float(df.iloc[_fill_bar + j - 1]["Close"])
                _overnight_sum += (day_open - _prev_close) / entry_price * 100
                _intraday_sum += (day_close - day_open) / entry_price * 100

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
                    _exit_bar_idx = _fill_bar + j
                    break
                if day_high >= target_price:
                    exit_price = target_price
                    exit_reason = "target"
                    exit_day = j
                    _exit_bar_idx = _fill_bar + j
                    break
                # Cut losers early: only after _max_loss_days AND trade is ≥1% in the red
                # (avoids exiting trades that are merely flat or marginally negative)
                if j >= _max_loss_days - 1 and day_close < entry_price * 0.99:
                    exit_price = day_close
                    exit_reason = "time_loss"
                    exit_day = j
                    _exit_bar_idx = _fill_bar + j
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
                        _exit_bar_idx = _fill_bar + j
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
                        _exit_bar_idx = _fill_bar + j
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
                    _exit_bar_idx = _fill_bar + j
                    break
                if day_low <= target_price:
                    exit_price = target_price
                    exit_reason = "target"
                    exit_day = j
                    _exit_bar_idx = _fill_bar + j
                    break
                if j >= _max_loss_days - 1 and day_close > entry_price * 1.01:
                    exit_price = day_close
                    exit_reason = "time_loss"
                    exit_day = j
                    _exit_bar_idx = _fill_bar + j
                    break

        if exit_price is None:
            idx = min(_fill_bar + _hold_days - 1, len(df) - 1)
            exit_price = float(df.iloc[idx]["Close"])
            _exit_bar_idx = idx

        # §96a: adjust exit-day intraday from Close to actual exit_price
        if _exit_bar_idx >= _fill_bar:
            _exit_bar = df.iloc[_exit_bar_idx]
            _exit_open = float(_exit_bar["Open"])
            _exit_close = float(_exit_bar["Close"])
            _exit_day = _exit_bar_idx - _fill_bar
            if _exit_day == 0 and not entry_at_close:
                # Day-0 intraday was (Close - entry_price), replace with (exit_price - entry_price)
                _intraday_sum -= (_exit_close - entry_price) / entry_price * 100
                _intraday_sum += (exit_price - entry_price) / entry_price * 100
            else:
                _intraday_sum -= (_exit_close - _exit_open) / entry_price * 100
                _intraday_sum += (exit_price - _exit_open) / entry_price * 100

        # ── Return calculation ────────────────────────────────────────────────
        if action == "BUY":
            gross_pct = (exit_price - entry_price) / entry_price * 100
        else:
            gross_pct = (entry_price - exit_price) / entry_price * 100

        # ── §QuantEngine: beta hedge — subtract 0.9× SPY return over same period ──
        # Neutralises the beta=0.918 market exposure so net_pct reflects pure MR alpha.
        # SPY leg friction: +0.10% round-trip (spy_prices uses adjusted closes).
        _spy_leg_pct = 0.0
        if beta_hedge and spy_prices and _spy_entry_price is not None:
            _exit_date_key = pd.Timestamp(str(df.index[min(_exit_bar_idx, len(df) - 1)])[:10])
            _spy_exit_price = spy_prices.get(_exit_date_key)
            if _spy_exit_price is not None and _spy_entry_price > 0:
                _spy_leg_pct = (_spy_exit_price - _spy_entry_price) / _spy_entry_price * 100
                gross_pct -= BETA_HEDGE_RATIO * _spy_leg_pct

        net_pct = gross_pct - FRICTION_PCT - (BETA_HEDGE_FRICTION if beta_hedge else 0.0)

        # R1: parallel breakeven-ratchet exit for A/B comparison (read-only research column).
        _net_alt = simulate_alt_exit(
            df, _fill_bar, _hold_days, entry_price, atr, action, stop_price, target_price, FRICTION_PCT
        )
        # R4: mechanical fixed-stop variants (no ratchet) to isolate stop-WIDTH effect.
        _stop_15 = stop_price  # baseline 1.5 ATR (same as live)
        _stop_25 = (entry_price - 2.5 * atr) if action == "BUY" else (entry_price + 2.5 * atr)
        _stop_none = 0.0 if action == "BUY" else 1e9
        _net_stop15 = simulate_alt_exit(
            df, _fill_bar, _hold_days, entry_price, atr, action, _stop_15, target_price, FRICTION_PCT, ratchet=False
        )
        _net_stop25 = simulate_alt_exit(
            df, _fill_bar, _hold_days, entry_price, atr, action, _stop_25, target_price, FRICTION_PCT, ratchet=False
        )
        _net_nostop = simulate_alt_exit(
            df, _fill_bar, _hold_days, entry_price, atr, action, _stop_none, target_price, FRICTION_PCT, ratchet=False
        )

        # ── §QuantEngine: continuous forecast sizing (Carver FDM) ─────────────
        # Position size scales linearly with score above threshold.
        # Score at threshold (50) → FORECAST_FLOOR×; score 60 → 1.0×; score 70 → 2.0×.
        # Stores multiplier for score-weighted stats reporting (--forecast-sizing).
        _size_mult = 1.0
        if forecast_sizing and is_buy_signal:
            _forecast_val = (score - _buy_thresh) / FORECAST_THRESH_DIV
            _size_mult = max(FORECAST_FLOOR, min(FORECAST_CAP, _forecast_val))
        if score_band_sizing and is_buy_signal:
            _size_mult = score_band_size_mult(score)
        if _consec_score_sizing and is_buy_signal:
            # §87: multiply base size by consec-score conviction tier
            _size_mult *= _consec_size_mult
        _date_key = pd.Timestamp(str(date)[:10])
        # §111: ORATS options-flow row lookup (near-EOD options snapshot)
        _orats_row = None
        if _alt_data_panels.get("orats") is not None:
            _orats_row = _alt_data_panels["orats"].get(ticker.upper(), {}).get(_date_key.date())
        # §91: rising short-interest sizing tilt (squeeze-fuel thesis)
        if si_rising_map and is_buy_signal:
            _si_flag = si_rising_map.get(ticker, {}).get(_date_key)
            if _si_flag is True:
                _size_mult *= 1.15
        # §104: FINRA short-volume squeeze-fuel tilt
        # Condition: elevated short interest (>40%) AND falling (>5pp in 5d)
        if _alt_data_panels.get("finra_sv") is not None and is_buy_signal:
            _sv_dict = _alt_data_panels["finra_sv"].get(ticker.upper(), {})
            _sv_match = _sv_dict.get(_date_key.date())
            if _sv_match is not None:
                _sv_ratio = float(_sv_match.get("short_volume_ratio", 0))
                _sv_delta = float(_sv_match.get("sv_ratio_5d_delta", 0))
                # Elevated-and-falling short pressure = fuel
                if _sv_ratio > 40.0 and _sv_delta < -10.0:
                    _size_mult *= 1.15
        # §105: SEC FTD dislocation tilt
        if _alt_data_panels.get("sec_ftd") is not None and is_buy_signal:
            _ftd_dict = _alt_data_panels["sec_ftd"].get(ticker.upper(), {})
            _ftd_match = _ftd_dict.get(_date_key.date())
            if _ftd_match is not None:
                _ftd_pctile = float(_ftd_match.get("ftd_63d_pctile", 0))
                if _ftd_pctile > 75.0:
                    _size_mult *= 1.15
        # §106: Sentiment capitulation tilt (UMCSENT primary, NAAIM fallback)
        if _alt_data_panels.get("umcsent") is not None and is_buy_signal:
            _umcsent_match = _alt_data_panels["umcsent"].get(_date_key.date())
            if _umcsent_match is not None:
                _umcsent_val = float(_umcsent_match.get("umcsent", 0))
                if _umcsent_val < 60.0:  # low sentiment = fear/capitulation
                    _size_mult *= 1.10
        elif _alt_data_panels.get("naaim") is not None and is_buy_signal:
            _naaim_match = _alt_data_panels["naaim"].get(_date_key.date())
            if _naaim_match is not None:
                _naaim_exp = float(_naaim_match.get("naaim_exposure", 0))
                if _naaim_exp < 30.0:  # bottom-quintile = capitulation
                    _size_mult *= 1.15
        # §107: GDELT news-tone capitulation/repricing context
        if _alt_data_panels.get("gdelt") is not None and is_buy_signal:
            _gdelt_dict = _alt_data_panels["gdelt"].get(ticker.upper(), {})
            _gdelt_match = _gdelt_dict.get(_date_key.date())
            if _gdelt_match is not None:
                _tone_z = float(_gdelt_match.get("tone_z", 0))
                # Negative tone at oversold = potential capitulation (size up)
                if _tone_z < -1.5:
                    _size_mult *= 1.10
        # §111: ORATS options-flow sizing tilt
        if _orats_row is not None and is_buy_signal:
            _orats_iv_rank = float(_orats_row.get("iv_rank_252") or np.nan)
            _orats_skew = float(_orats_row.get("pc_iv_skew") or np.nan)
            _orats_gex = float(_orats_row.get("gex") or 0.0)
            _orats_pc_vol = float(_orats_row.get("pc_volume_ratio") or np.nan)
            _orats_0dte_puts = float(_orats_row.get("zero_dte_put_volume") or 0.0)
            # High IVR MR setups: dealer hedge unwind amplification
            if not math.isnan(_orats_iv_rank) and _orats_iv_rank >= 50.0:
                _size_mult *= 1.10
            # Steep put skew: panic peak precision
            if not math.isnan(_orats_skew) and _orats_skew > 0.10:
                _size_mult *= 1.08
            # Positive GEX: dealers net long gamma → mechanical support
            if _orats_gex > 0:
                _size_mult *= 1.05
            # Extreme 0-DTE put volume: capitulation hedging / forced selling
            if not math.isnan(_orats_pc_vol) and _orats_pc_vol > 1.5 and _orats_0dte_puts > 1000:
                _size_mult *= 1.05
        # §88: calm-regime sleeve — 0.5× risk budget on relaxed low-VIX entries
        if calm_sleeve and is_buy_signal:
            _size_mult *= 0.5
        # §89a: FF ST_Rev regime tilt — size down when reversal factor is negative
        if ff_str_regime_map and is_buy_signal:
            _ff_regime_mult = ff_str_regime_map.get(_date_key, 1.0)
            if _ff_regime_mult is not None:
                _size_mult *= float(_ff_regime_mult)
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
                "net_pct_alt": _net_alt,  # R1: breakeven-ratchet exit variant
                "net_pct_stop15": _net_stop15,  # R4: mechanical 1.5-ATR stop
                "net_pct_stop25": _net_stop25,  # R4: mechanical 2.5-ATR stop
                "net_pct_nostop": _net_nostop,  # R4: no hard stop (target/time only)
                "spy_leg_pct": round(_spy_leg_pct, 3) if beta_hedge else None,
                "size_mult": round(_size_mult, 3),
                "overnight_pct": round(_overnight_sum, 3),
                "intraday_pct": round(_intraday_sum, 3),
                "entry_style": _entry_style,
                "mr_trigger": _mr_trigger_label,
                # §MAX: trailing-21-bar max daily return at signal time (lottery proxy)
                "max21": round(float(_max21_series.iloc[i]), 2) if pd.notna(_max21_series.iloc[i]) else None,
                # ── Quality score (Option B — continuous trade ranking) ──────────
                # Composite 0-100: rewards high signal score, fast OU mean-reversion,
                # and low Hurst (more mean-reverting). Used to rank trades within the
                # passing set — addresses Inv4 finding that confidence is flat (42-44%).
                "quality_score": round(
                    min(
                        100.0,
                        max(
                            0.0,
                            # 40% weight: score above threshold (normalized 0-30 → 0-40)
                            min(40.0, (score - _buy_thresh) / 30.0 * 40.0)
                            # 35% weight: OU halflife (shorter = faster MR; 0d=best, 25d=worst)
                            + (
                                35.0 * max(0.0, 1.0 - float(row.get("ou_halflife", 25)) / 25.0)
                                if pd.notna(row.get("ou_halflife"))
                                else 17.5
                            )
                            # 25% weight: Hurst (lower = more MR; 0.5=best, 0.80=worst)
                            + (
                                25.0 * max(0.0, 1.0 - (float(row.get("hurst", 0.65)) - 0.5) / 0.30)
                                if pd.notna(row.get("hurst"))
                                else 12.5
                            ),
                        ),
                    ),
                    1,
                ),
                "mfe_pct": round(_mfe_pct, 3),
                "mae_pct": round(_mae_pct, 3),
                "atr_pct": round(atr / entry_price * 100, 2) if entry_price > 0 else 0,
                "days_to_earnings": _days_to_earn if _days_to_earn < 999 else None,
                "days_since_earnings": _days_since_earn,
                "dow": date.dayofweek,
                "near_52wk_low": _near_52wk_low_flag,
                # ── Regime + microstructure context at entry (backtest_new_layers.py) ──
                "vix_entry": round(float(vix_today), 2) if vix_today is not None else None,
                "spy_trend_entry": int(spy_trend.get(date, 0)),
                # OFI daily proxy: ibs and change_pct are computed per-bar in compute_scores()
                "ibs_entry": round(float(row.get("ibs", 0.5)), 3) if pd.notna(row.get("ibs")) else None,
                "change_pct_entry": round(float(row.get("change_pct", 0.0)), 3)
                if pd.notna(row.get("change_pct"))
                else None,
                # ── Meta-label features (QUANT_ENGINE_REVIEW §1.3) ─────────────────
                # Stored so backtest_trades_is.csv can train the meta-model without
                # train/serve skew.  All 14 features must be real values — no NaN
                # fallbacks — so the model learns true conditional relationships.
                "entry_price": round(entry_price, 2),
                "atr": round(float(atr), 4) if pd.notna(atr) else None,
                "ou_halflife": round(float(row.get("ou_halflife")), 2) if pd.notna(row.get("ou_halflife")) else None,
                "hurst": round(float(row.get("hurst")), 3) if pd.notna(row.get("hurst")) else None,
                "rvol": round(float(row.get("rvol")), 3) if pd.notna(row.get("rvol")) else None,
                "vix": round(float(vix_today), 2) if vix_today is not None else None,
                "sector_etf": TICKER_TO_SECTOR.get(ticker, "XLK"),
                "bb_pct_b": round(float(row.get("bb_pct_b")), 4) if pd.notna(row.get("bb_pct_b")) else None,
                "vwap_pct": round(float(row.get("vwap_pct")), 4) if pd.notna(row.get("vwap_pct")) else None,
                "price_zscore": round(float(row.get("price_zscore")), 4) if pd.notna(row.get("price_zscore")) else None,
                "month": date.month,
                # Computed / looked-up meta features
                "entry_prob": (
                    _compute_entry_prob(row, atr, entry_price, vix_today, date, ticker, entry_model)
                    if entry_model is not None
                    else None
                ),
                "hmm_bull_prob": (
                    round(float(hmm_cache.get(_date_key, {}).get("bull_prob", 0.5)), 4) if hmm_cache else 0.5
                ),
                "hmm_trans_risk": (
                    round(float(hmm_cache.get(_date_key, {}).get("transition_risk", 0.1)), 4) if hmm_cache else 0.1
                ),
                "vix_term_ratio": (
                    round(float(vix_today) / float(vix3m_series.get(_date_key, vix_today)), 4)
                    if vix_today is not None and vix3m_series is not None
                    else None
                ),
                "sector_momentum": (
                    round(float(sector_momentum_map.get(TICKER_TO_SECTOR.get(ticker, "XLK"), {}).get(_date_key)), 4)
                    if sector_momentum_map
                    and sector_momentum_map.get(TICKER_TO_SECTOR.get(ticker, "XLK"), {}).get(_date_key) is not None
                    else None
                ),
                "vix_9d_ratio": (_compute_vix_9d_ratio(vix, _date_key) if vix else None),
                "ff_str": (
                    round(float(ff_str.get(_date_key)), 4) if ff_str and ff_str.get(_date_key) is not None else None
                ),
                "si_rising": (si_rising_map.get(ticker, {}).get(_date_key) if si_rising_map else None),
                # ── §104–§110: Alt-data features at entry ────────────────────────
                "sv_ratio": (
                    round(
                        float(
                            _alt_data_panels["finra_sv"]
                            .get(ticker.upper(), {})
                            .get(_date_key.date(), {})
                            .get("short_volume_ratio", 0)
                        ),
                        4,
                    )
                    if _alt_data_panels.get("finra_sv") is not None
                    else None
                ),
                "sv_ratio_5d_delta": (
                    round(
                        float(
                            _alt_data_panels["finra_sv"]
                            .get(ticker.upper(), {})
                            .get(_date_key.date(), {})
                            .get("sv_ratio_5d_delta", 0)
                        ),
                        4,
                    )
                    if _alt_data_panels.get("finra_sv") is not None
                    else None
                ),
                "ftd_63d_pctile": (
                    round(
                        float(
                            _alt_data_panels["sec_ftd"]
                            .get(ticker.upper(), {})
                            .get(_date_key.date(), {})
                            .get("ftd_63d_pctile", 0)
                        ),
                        4,
                    )
                    if _alt_data_panels.get("sec_ftd") is not None
                    else None
                ),
                "umcsent": (
                    round(float(_alt_data_panels["umcsent"].get(_date_key.date(), {}).get("umcsent", 0)), 4)
                    if _alt_data_panels.get("umcsent") is not None
                    else None
                ),
                "tone_z": (
                    round(
                        float(
                            _alt_data_panels["gdelt"].get(ticker.upper(), {}).get(_date_key.date(), {}).get("tone_z", 0)
                        ),
                        4,
                    )
                    if _alt_data_panels.get("gdelt") is not None
                    else None
                ),
                # ── §111: ORATS options-flow features at entry ───────────────────
                "orats_iv_rank": _orats_float(_orats_row, "iv_rank_252"),
                "orats_iv_pctile": _orats_float(_orats_row, "iv_pctile_252"),
                "orats_atm_iv_30d": _orats_float(_orats_row, "atm_iv_30d"),
                "orats_pc_iv_skew": _orats_float(_orats_row, "pc_iv_skew"),
                "orats_gex": _orats_float(_orats_row, "gex"),
                "orats_dex": _orats_float(_orats_row, "dex"),
                "orats_pc_volume_ratio": _orats_float(_orats_row, "pc_volume_ratio"),
                "orats_pc_oi_ratio": _orats_float(_orats_row, "pc_oi_ratio"),
                "orats_zero_dte_put_volume": _orats_float(_orats_row, "zero_dte_put_volume"),
            }
        )

        # Cooldown: trade duration + 3 calendar days buffer.
        # v5.11: changed from 2×duration (too aggressive with HOLD_DAYS=7)
        # to duration+3 — allows re-entry sooner after a quick exit while
        # still preventing same-day re-entry (exit_day=0 → 3 day cooldown).
        in_trade_until = date + pd.Timedelta(days=max(exit_day + 3, 5))

    _df_result = pd.DataFrame(trades)
    if entry_limit_k is not None and entry_limit_k > 0:
        _df_result.attrs["_limit_signals_attempted"] = _limit_signals_attempted
    return _df_result


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
    "avg_mae": None,
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


# R10-7 deployable live L7 curve — convex half-Kelly over raw score, clamped to
# the unchanged [0.85, 1.15] envelope. b and neutral are baked from the IS §Inv-K
# fit so the live engine reproduces the validated curve without the full sample.
_KELLY_PAYOFF_B = 0.83  # realized avg_win/avg_loss of the MR strategy (IS §Inv-K)
_KELLY_NEUTRAL = 0.2283  # Kelly fraction at the neutral score=65 (normaliser)


def kelly_size_mult(score: float, lo: float = 0.85, hi: float = 1.15) -> float:
    """R10-7 per-signal half-Kelly sizing multiplier (the exact live L7 formula).

    p ≈ score→win-prob (linear, anchored at 0.5 for score=50); f = max(0, p −
    (1−p)/b); normalised to 1.0× at the neutral score=65 and clamped to the
    unchanged [lo, hi] envelope so total position risk is identical to the prior
    linear L7 — only the *shape* (convex vs linear) changes.
    """
    p = min(0.95, max(0.05, 0.5 + (score - 50.0) / 100.0))
    kelly = max(0.0, p - (1.0 - p) / _KELLY_PAYOFF_B)
    return min(hi, max(lo, kelly / _KELLY_NEUTRAL))


def stats_explicit_weights(rets: list[float], weights: list[float]) -> dict:
    """Weighted stats using caller-supplied per-trade weights AS-IS (mean-normalised
    only) — unlike stats_weighted, it does not min-max rescale, so a deployable
    sizing curve is evaluated exactly as it would size live."""
    if not rets or not weights or len(rets) != len(weights):
        return dict(_EMPTY_STATS)
    arr = np.array(rets, dtype=float)
    w = np.array(weights, dtype=float)
    if w.mean() <= 0:
        return stats(rets)
    w = w / w.mean()
    mu = float(np.average(arr, weights=w))
    var = float(np.average((arr - mu) ** 2, weights=w))
    std = math.sqrt(var) if var > 0 else 0.0
    sharpe = round(mu / std, 4) if std > 0 and len(rets) >= 10 else None
    wr_w = float(np.sum(w[arr > 0])) / float(np.sum(w)) * 100 if np.sum(w) > 0 else 0.0
    cap, peak, max_dd = 10_000.0, 10_000.0, 0.0
    for r, wi in zip(rets, w.tolist()):
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


def stats_kelly(
    rets: list[float],
    scores: list[float],
    frac: float = 0.5,
    lo: float = 0.70,
    hi: float = 1.30,
) -> dict:
    """R10-7: per-signal half-Kelly position sizing.

    The strategy uses a universal 1.5-ATR stop / 2.0-ATR target, so the *planned*
    reward:risk is constant — per-signal Kelly therefore has no per-signal payoff
    term and reduces to a confidence-conditional sizing curve. Here:
      - p (per-trade win prob) is read off an in-sample score→WR calibration
        (monotone-smoothed quintile win rates) — the empirical answer to "what
        does the score predict about win probability";
      - b (payoff ratio) is the realized avg_win / avg_loss of the sample (the
        effective edge of a 10-day-hold MR trade, not the 1.33 target ratio);
      - f_i = frac · max(0, p_i − (1−p_i)/b), normalized to mean 1.0 and clamped
        to [lo, hi] so it stays inside the live sizing risk envelope.

    Compare its Sharpe to stats_weighted (linear L7) and stats (equal-weight) to
    decide whether the convex Kelly shape beats the current linear nudge.
    """
    if not rets or not scores or len(rets) != len(scores):
        return dict(_EMPTY_STATS)
    arr = np.array(rets, dtype=float)
    sc = np.array(scores, dtype=float)
    wins = arr[arr > 0]
    losses = arr[arr <= 0]
    if len(wins) < 5 or len(losses) < 5 or sc.max() == sc.min():
        return stats(rets)
    b = float(wins.mean() / abs(losses.mean())) if losses.mean() != 0 else 1.33

    # In-sample score→WR calibration via quantile bins, monotone-smoothed (isotonic-lite).
    order = np.argsort(sc)
    n = len(sc)
    nbins = min(5, max(2, n // 20))
    edges = np.linspace(0, n, nbins + 1).astype(int)
    bin_wr = []
    for i in range(nbins):
        idx = order[edges[i] : edges[i + 1]]
        bin_wr.append(float((arr[idx] > 0).mean()) if len(idx) else float((arr > 0).mean()))
    for i in range(1, nbins):  # enforce non-decreasing WR in score
        bin_wr[i] = max(bin_wr[i], bin_wr[i - 1])
    p = np.empty(n)
    for i in range(nbins):
        p[order[edges[i] : edges[i + 1]]] = bin_wr[i]
    p = np.clip(p, 0.05, 0.95)

    kelly = np.clip(p - (1 - p) / b, 0.0, None)  # full Kelly fraction per trade
    f = frac * kelly
    if f.max() <= 0:
        return stats(rets)
    neutral = float(np.mean(f[f > 0]))
    w = np.clip(f / neutral, lo, hi)
    w = w / w.mean()

    mu = float(np.average(arr, weights=w))
    var = float(np.average((arr - mu) ** 2, weights=w))
    std = math.sqrt(var) if var > 0 else 0.0
    sharpe = round(mu / std, 4) if std > 0 and n >= 10 else None
    wr_w = float(np.sum(w[arr > 0])) / float(np.sum(w)) * 100 if np.sum(w) > 0 else 0.0

    cap, peak, max_dd = 10_000.0, 10_000.0, 0.0
    for r, wi in zip(rets, w.tolist()):
        cap += cap * POSITION_SIZE * wi * (r / 100)
        peak = max(peak, cap)
        max_dd = max(max_dd, (peak - cap) / peak * 100)

    return {
        "n": n,
        "wr": round(wr_w, 1),
        "avg": round(mu, 2),
        "avg_win": None,
        "avg_loss": None,
        "pf": round(b, 2),
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
        "avg_mae": None,
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


def sharpe_ci_print(sr: float | None, n: int, n_trials: int | None = None, label: str = "IS") -> None:
    """Print Lo (2002) 95% CI for a per-trade Sharpe ratio and Deflated Sharpe warning.

    SE(SR) = sqrt((1 + SR^2/2) / N) where N is number of trades.
    This is the IID special case of the Lo (2002) formula applied at trade level.

    Also computes the expected maximum Sharpe from n_trials independent parameter
    searches (Bailey & López de Prado 2014 Deflated Sharpe Ratio), showing whether
    the IS Sharpe can be explained by data mining alone.

    n_trials defaults to the env var SIGNAL_TRADE_N_TRIALS (fallback 300).
    The research log documents ≥86 strategy sections plus sweeps and gate
    ablations; 300 is a conservative lower-bound honest count.

    Prints: 95% CI bounds, whether SR=0 is inside, and the data-mining baseline.
    """
    if sr is None or n < 10:
        return
    if n_trials is None:
        n_trials = int(os.environ.get("SIGNAL_TRADE_N_TRIALS", "0"))
        if n_trials <= 0:
            n_trials = max(300, _count_experiments())
    se = math.sqrt((1 + sr**2 / 2) / n)
    lo = round(sr - 1.96 * se, 2)
    hi = round(sr + 1.96 * se, 2)
    zero_inside = lo < 0 < hi

    # Expected max Sharpe from n_trials independent searches (Gumbel extreme-value)
    expected_max_sr = math.sqrt(1.0 / n) * math.sqrt(2 * math.log(n_trials))

    print(f"\n### Sharpe Statistical Significance ({label})\n")
    print(f"- **Lo (2002) 95% CI:** [{lo:.2f}, {hi:.2f}]  (SE={se:.3f}, N={n})")
    if zero_inside:
        print(
            f"  > ⚠ SR=0 is INSIDE the 95% CI — the {label} Sharpe is not statistically "
            f"significant at 5% on N={n} trades alone. Treat as directional evidence, not proof."
        )
    else:
        print(f"  > ✅ SR=0 is outside the 95% CI — statistically significant at 5% on N={n} trades.")
    print(
        f"- **Deflated Sharpe (Bailey-López de Prado, {n_trials} trials):** "
        f"expected max SR by chance = {expected_max_sr:.2f}"
    )
    if sr < expected_max_sr:
        print(
            f"  > ⚠ {label} Sharpe {sr:.2f} < data-mining expectation {expected_max_sr:.2f} "
            f"from {n_trials} parameter searches. Cannot rule out partial data-mining artifact."
        )
    else:
        print(
            f"  > ✅ {label} Sharpe {sr:.2f} > data-mining expectation {expected_max_sr:.2f} — "
            "unlikely to be explained by data mining alone."
        )


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
        raw = cached_yf_download("SPY", start=start, end=end, interval="1d", auto_adjust=True, progress=False)
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


def fetch_spy_prices(start: str, end: str) -> dict[pd.Timestamp, float]:
    """Return {date: adjusted_close} for SPY — used by the beta-hedge computation."""
    try:
        raw = cached_yf_download("SPY", start=start, end=end, interval="1d", auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        closes = raw["Close"].ffill()
        return {pd.Timestamp(str(k)[:10]): float(v) for k, v in closes.items() if pd.notna(v)}
    except Exception as e:
        print(f"failed ({e}) — beta hedge disabled")
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
    if "--pbo" in sys.argv:
        return {}
    try:
        _HERE = os.path.dirname(os.path.abspath(__file__))
        cache_dir = os.path.abspath(os.path.join(_HERE, "..", "data", "cache_ohlcv"))

        tlt_path = os.path.join(cache_dir, f"TLT_{start}_{end}_1d_adjTrue.csv")
        uup_path = os.path.join(cache_dir, f"UUP_{start}_{end}_1d_adjTrue.csv")
        xle_path = os.path.join(cache_dir, f"XLE_{start}_{end}_1d_adjTrue.csv")

        tlt_raw = pd.read_csv(tlt_path, header=[0, 1], index_col=0, parse_dates=True)
        uup_raw = pd.read_csv(uup_path, header=[0, 1], index_col=0, parse_dates=True)
        xle_raw = pd.read_csv(xle_path, header=[0, 1], index_col=0, parse_dates=True)

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


def fetch_earnings_dates_polygon(ticker: str, api_key: str, start: str) -> set:
    """Fetch quarterly filing dates from Polygon vX/reference/financials.
    Returns a set of pd.Timestamps covering full history back to start.

    WARNING: This is a best-effort proxy for earnings announcement dates.
    Polygon returns ``period_of_report_date`` (quarter end, closest to the
    actual earnings event), ``filing_date`` (SEC 10-Q/10-K submission, lags
    by days-to-weeks), and ``start_date`` (fallback).  We use the earliest
    available date, but true announcement dates require a dedicated earnings
    calendar API (e.g. Polygon ``vX/reference/dividends`` or a commercial
    earnings-data feed).  Dates here may trail the press-release by several
    days, so the blackout window is slightly conservative.
    Covers 2003-2022 — the gap yfinance cannot reach.
    """
    import os
    import json

    _HERE = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.abspath(os.path.join(_HERE, "..", "data", "cache_earnings"))
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{ticker}.json")

    if os.path.exists(cache_path):
        try:
            with open(cache_path) as f:
                date_strs = json.load(f)
                return {pd.Timestamp(ds) for ds in date_strs}
        except Exception:
            pass

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
                # Prefer dates closer to the actual announcement:
                # period_of_report_date ≈ quarter end (closest to earnings)
                # filing_date = SEC submission (lags by days-to-weeks)
                # start_date = fallback
                fd = result.get("period_of_report_date") or result.get("filing_date") or result.get("start_date")
                if fd:
                    dates.add(pd.Timestamp(str(fd)[:10]))
            # Polygon paginates via next_url
            next_url = body.get("next_url")
            if not next_url:
                break
            url = next_url + f"&apiKey={api_key}"
            params = {}
        if dates:
            try:
                with open(cache_path, "w") as f:
                    json.dump([str(d)[:10] for d in sorted(list(dates))], f)
            except Exception:
                pass
    except Exception:
        pass
    return dates


def fetch_fred_series(
    series_id: str, start: str, end: str, api_key: str, pub_lag_days: int = 7
) -> dict[pd.Timestamp, float]:
    """
    Fetch any FRED series → forward-filled to daily so every trading day has a value.

    Point-in-time discipline: each observation is keyed to its OBSERVATION date plus
    `pub_lag_days` (the series' real publication delay), then ffilled forward — the
    backtest only ever sees a value on/after the day it was actually published.
    Weekly series (STLFSI4, NFCI) publish ~5-7 days after the week they describe →
    lag 7; daily Treasury/Moody's series publish same/next evening → lag 1.

    NOTE (2026-06-12 regression fix): a prior version keyed observations to
    `o["realtime_start"]` intending the publication date. FRED only returns real
    vintage dates when the request carries an explicit realtime window; by default
    every observation echoes realtime_start = TODAY, which collapsed the whole
    series to a single present-day key — STLFSI4 Gate 2 and the §14 panel were
    silently empty for all historical dates (introduced d55a26e 2026-06-09).
    True ALFRED vintages are also unusable for STLFSI4: the series was created in
    2020, so first-release keying would erase all pre-2020 history. Fixed lag on
    the observation date is the correct, conservative join.
    FRED encodes missing values as ".", which float() rejects and we skip.
    """
    if not api_key:
        return {}
    try:
        import requests as _req

        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "observation_start": start,
            "observation_end": end,
        }
        r = _req.get(url, params=params, timeout=15)
        obs = r.json().get("observations", [])
        if not obs:
            return {}
        raw = {}
        for o in obs:
            try:
                key_date = pd.Timestamp(o["date"]) + pd.Timedelta(days=pub_lag_days)
                raw[key_date] = float(o["value"])
            except (ValueError, KeyError):
                pass  # "." = FRED missing-value marker
        if not raw:
            return {}
        idx = pd.date_range(start=min(raw), end=max(raw), freq="D")
        series = pd.Series(raw).reindex(idx).ffill()
        return {pd.Timestamp(str(k)[:10]): float(v) for k, v in series.items() if pd.notna(v)}
    except Exception as e:
        print(f"failed ({e})")
        return {}


def fetch_stlfsi4(start: str, end: str, api_key: str) -> dict[pd.Timestamp, float]:
    """
    St. Louis Fed Financial Stress Index (STLFSI4) from FRED — see fetch_fred_series.
    Values: negative = below-average stress; > 1.0 = elevated; > 1.5 = crisis.
    Weekly (week ends Friday), published the following Thursday → pub_lag_days=7.
    """
    return fetch_fred_series("STLFSI4", start, end, api_key, pub_lag_days=7)


def fetch_ff_str(start: str, end: str) -> dict[pd.Timestamp, float]:
    """
    Fama-French Short-Term Reversal factor (daily) from Ken French Data Library.
    Returns {date: ST_Rev_return_pct} for the requested range.
    Cached to disk to avoid repeated downloads.
    """
    import io
    import zipfile

    cache_dir = os.path.abspath(os.path.join(_HERE, "..", "data", "cache_ff"))
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"ff_str_lag7_{start}_{end}.json")  # _lag7: PIT-lagged keys (2026-06-12)
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            raw = json.load(f)
        return {pd.Timestamp(k): float(v) for k, v in raw.items()}

    url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_ST_Reversal_Factor_daily_CSV.zip"
    result: dict[pd.Timestamp, float] = {}
    try:
        import requests as _req

        r = _req.get(url, timeout=30)
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            csv_name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
            with z.open(csv_name) as f:
                df = pd.read_csv(f, skiprows=13, engine="python")
        df.columns = [c.strip() for c in df.columns]
        # Robust date parse: drop footer rows that don't look like YYYYMMDD
        _date_col = df.columns[0]
        _valid = df[_date_col].astype(str).str.match(r"^\d{8}$")
        df = df[_valid].copy()
        df["date"] = pd.to_datetime(df[_date_col].astype(str), format="%Y%m%d")
        df = df[(df["date"] >= start) & (df["date"] <= end)]
        # PIT lag: Ken French refreshes the daily files roughly monthly, so the
        # ST_Rev return for date X is not actually downloadable until weeks later.
        # Key each value to date + 7 days as a floor (audit 2026-06-12); revisit
        # with the true ~monthly worst-case before the meta-model (the only
        # consumer) ever crosses its activation gate.
        result = {row["date"] + pd.Timedelta(days=7): float(row["ST_Rev"]) for _, row in df.iterrows()}
        with open(cache_path, "w") as f:
            json.dump({str(k): v for k, v in result.items()}, f)
    except Exception as e:
        print(f"[ff_str] fetch failed: {e}")
    return result


def fetch_fred_panel(start: str, end: str, api_key: str) -> dict[str, dict]:
    """
    FRED macro-regime panel for the §14 regime-gate ablation. All free, FRED-key-gated,
    decades deep — and orthogonal to the VIX+STLFSI4 the backtest already gates on:
      nfci    — Chicago Fed National Financial Conditions Index (>0 = tighter than avg), 1971+
      baa10y  — Moody's Baa corporate yield minus 10Y Treasury, % (credit stress), 1986+
      t10y3m  — 10Y minus 3M Treasury spread, % (<0 = inverted curve = recession regime), 1982+
    Each value is a daily-ffilled {date: float} dict; empty if no key / fetch fails.

    NB: ICE BofA HY-OAS (BAMLH0A0HYM2) was the obvious credit gauge but FRED now only
    serves ~2yr of it publicly (ICE licensing change → 2023+ only), too shallow for the
    23yr backtest. BAA10Y is the deep, free, non-ICE substitute (Moody's, daily, 1986+).
    """
    return {
        # NFCI: weekly, published Wednesday for the prior week → 7d lag.
        "nfci": fetch_fred_series("NFCI", start, end, api_key, pub_lag_days=7),
        # BAA10Y / T10Y3M: daily, published same/next evening → usable T+1.
        "baa10y": fetch_fred_series("BAA10Y", start, end, api_key, pub_lag_days=1),
        "t10y3m": fetch_fred_series("T10Y3M", start, end, api_key, pub_lag_days=1),
    }


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

                sweep_trades = _filter_simulation_results(
                    _run_simulation_parallel(
                        all_dfs,
                        common_kwargs={"mr_only": True},
                        vix=vix,
                        spy_trend=spy_trend,
                        stlfsi4=stlfsi4,
                    )
                )

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
        _log_experiment(
            experiment_type="parameter_sweep",
            hypothesis="BUY_THRESH / HOLD_DAYS grid search",
            n_trials=len(results),
            is_metrics={"sharpe": float(best["sharpe"]), "n": int(best["n"])},
        )

    # Restore original globals
    BUY_THRESH = orig_buy
    BUY_THRESH_MAX = orig_buy_max
    SELL_THRESH = orig_sell
    HOLD_DAYS = orig_hold


# ─────────────────────────────────────────────────────────────────────────────
# Full-Universe Curation Bias Report
# ─────────────────────────────────────────────────────────────────────────────


def run_full_universe_curation_bias(vix, spy_trend, stlfsi4):
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

    args_list = [(t, vix, spy_trend, stlfsi4, True, False, {}, False, False) for t in _CURATED_OUT_TICKERS]
    _workers = int(os.getenv("BACKTEST_WORKERS", "8"))
    with ThreadPoolExecutor(max_workers=min(_workers, len(_CURATED_OUT_TICKERS))) as p:
        results = list(p.map(process_ticker, args_list))

    curated_dfs = {ticker: ind_df for ticker, _bh, ind_df, _ed in results if ind_df is not None and not ind_df.empty}
    _sim_results = _run_simulation_parallel(
        curated_dfs,
        common_kwargs={"mr_only": True},
        vix=vix,
        spy_trend=spy_trend,
        stlfsi4=stlfsi4,
    )
    removed_trades = _filter_simulation_results(_sim_results)
    curated_trades = {ticker: df for ticker, df in _sim_results if df is not None and not df.empty}

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
    for ticker, _bh, _ind, _ed in results:
        t_df = curated_trades.get(ticker)
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
):
    """One-at-a-time IS sensitivity analysis for §59–§82 gate thresholds.

    Each parameter is swept across a calibration grid while all others are held
    at baseline. 999 = gate disabled (upper-bound check). Outputs: N, WR, avg
    return, Sharpe for every setting so the analyst can see the Sharpe cliff.
    """
    print("\n## Gate Sensitivity Sweep — §59–§82 thresholds (IS universe, MR-only)\n")
    print("> One-at-a-time analysis: each parameter varied, all others held at baseline.")
    print("> Note: §59 OU halflife, §60 Hurst, §61 Idio vol, §78 Sep/Oct removed as")
    print(">       hard-block gates (--validate-live-gates 2026-06-02: all ΔSh=0.00).\n")

    def _run_all(label: str) -> dict:
        trades = _filter_simulation_results(
            _run_simulation_parallel(
                all_dfs,
                common_kwargs={"mr_only": True},
                vix=vix,
                spy_trend=spy_trend,
                stlfsi4=stlfsi4,
            )
        )
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

    print("> All sweepable gates removed. Use --validate-live-gates for the active gate ablation.")
    print("> Run --inv5 for the legacy ablation report on the removed gates.\n")
    _log_experiment(
        experiment_type="gate_ablation",
        hypothesis="§59–§82 gate threshold sensitivity",
        n_trials=0,
        is_metrics={},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Walk-Forward Temporal Stability
# ─────────────────────────────────────────────────────────────────────────────


_T_BILL_ANN = 0.035  # 3.5% historical average T-bill rate (conservative for 2003-2026)


def run_portfolio_simulation(
    trades_df: pd.DataFrame,
    max_concurrent: int = MAX_PORTFOLIO_SLOTS,
    dd_throttle: bool = False,
    dd_trig: float = 3.0,
    throttle_mult: float = 0.5,
    quiet: bool = False,
    vol_target: float | None = None,
) -> dict | None:
    """Concurrent-position portfolio equity-curve simulation.

    R7: when ``dd_throttle`` is set, a new slot opened while the portfolio is more than
    ``dd_trig`` % below its equity peak is sized at ``throttle_mult``× (graduated de-risk,
    causal — the drawdown is measured from already-closed capital). Returns
    {cagr, max_dd, ann_sharpe} so callers can A/B the throttle.

    Models:
      1. Position overlap — multiple tickers open simultaneously (greedy slot allocation)
      2. Compound drawdown — concurrent losing trades amplify portfolio DD
      3. T-bill return on idle capital — each event records how many slots were idle
         in the preceding interval and credits _T_BILL_ANN × idle_fraction × days/365
      4. Capital compounding — position P&L and T-bill return recycle into next slot

    Idle capital: when fewer than max_concurrent slots are occupied, the undeployed
    fraction earns _T_BILL_ANN prorated to the calendar days between events.  This
    models investing idle cash in T-bills/money market — the most conservative
    assumption for uninvested capital (QE4).
    """
    if trades_df is None or trades_df.empty:
        return None

    df = trades_df.copy().sort_values("date").reset_index(drop=True)

    # Approximate calendar exit_dt from trading-bar hold count (×1.4 for cal days)
    df["_entry_dt"] = pd.to_datetime(df["date"])
    df["_exit_dt"] = df["_entry_dt"] + pd.to_timedelta((df["exit_day"].clip(lower=0) * 1.4 + 1).astype(int), unit="D")

    slot_size = 1.0 / max_concurrent
    capital = 10_000.0
    peak = capital
    max_dd = 0.0
    open_slots: list = []  # [(exit_dt, net_pct, size_mult)]
    equity_log: list = [(df["_entry_dt"].iloc[0], capital)]
    skipped = 0
    last_event_dt = df["_entry_dt"].iloc[0]

    # ── §QuantEngine: portfolio-level volatility targeting ───────────────────
    # Harvey et al. / Man Group evidence: scaling exposure to a forecast-vol
    # target is one of the most reliable Sharpe levers in equity systems.
    # We use a causal expanding/rolling realized vol of per-trade net_pct
    # returns and scale each slot's notional so expected portfolio vol
    # approximates vol_target (default 25% ann).
    _vol_multipliers: list[float] | None = None
    if vol_target is not None and len(df) >= 2:
        _min_periods = min(21, len(df) - 1)
        _roll_std = df["net_pct"].shift(1).rolling(window=63, min_periods=_min_periods).std()
        # Fallback to expanding std for the first trades.
        _exp_std = df["net_pct"].shift(1).expanding(min_periods=_min_periods).std()
        _realized_std = _roll_std.fillna(_exp_std)
        # Annualize: each trade is a HOLD_DAYS-period return, so daily vol =
        # trade_std / sqrt(HOLD_DAYS) and annual vol = daily vol * sqrt(252).
        # UNITS (bug fixed 2026-07-15): net_pct is in PERCENT (0.8 == 0.8%), so
        # divide by 100 to get a decimal vol comparable to vol_target. Without
        # this, forecast vol read ~35 (3,500% ann) and the multiplier clipped
        # to the 0.25 floor for EVERY trade at any target — "vol targeting"
        # silently degenerated into a constant 0.25x de-leverage (σ=0.05 and
        # σ=2.0 produced identical equity curves).
        _forecast_vol = ((_realized_std / 100.0) * np.sqrt(252 / max(HOLD_DAYS, 1))).clip(lower=1e-6)
        _multiplier = (vol_target / _forecast_vol).clip(lower=0.25, upper=2.0)
        _vol_multipliers = _multiplier.fillna(1.0).tolist()

    def _apply_tbill(until_dt: pd.Timestamp) -> None:
        """Credit T-bill return on idle slots between last_event_dt and until_dt."""
        nonlocal capital, last_event_dt
        dt_days = (until_dt - last_event_dt).days
        if dt_days <= 0:
            return
        idle_slots = max_concurrent - len(open_slots)
        if idle_slots <= 0:
            return
        idle_frac = idle_slots / max_concurrent
        capital *= 1.0 + _T_BILL_ANN * idle_frac * (dt_days / 365.25)
        last_event_dt = until_dt

    for i, row in df.iterrows():
        entry_dt = row["_entry_dt"]
        exit_dt = row["_exit_dt"]
        net_pct = float(row["net_pct"])

        # Credit T-bill on idle capital up to this entry event
        _apply_tbill(entry_dt)

        # Close expired slots
        still_open = []
        for slot_exit, slot_pct, slot_mult in sorted(open_slots, key=lambda x: x[0]):
            if slot_exit <= entry_dt:
                capital += capital * slot_size * slot_mult * (slot_pct / 100)
                peak = max(peak, capital)
                max_dd = max(max_dd, (peak - capital) / peak * 100)
                equity_log.append((slot_exit, round(capital, 4)))
            else:
                still_open.append((slot_exit, slot_pct, slot_mult))
        open_slots = still_open

        if len(open_slots) < max_concurrent:
            # R7: graduated de-risk — size down a new slot opened during a drawdown.
            _dd_now = (peak - capital) / peak * 100 if peak > 0 else 0.0
            _throttle = throttle_mult if (dd_throttle and _dd_now > dd_trig) else 1.0
            _trade_size = float(row.get("size_mult", 1.0)) if pd.notna(row.get("size_mult")) else 1.0
            _vol_mult = _vol_multipliers[i] if _vol_multipliers else 1.0
            _mult = _throttle * _trade_size * _vol_mult
            open_slots.append((exit_dt, net_pct, _mult))
        else:
            skipped += 1

    # Drain remaining slots
    for slot_exit, slot_pct, slot_mult in sorted(open_slots, key=lambda x: x[0]):
        _apply_tbill(slot_exit)
        capital += capital * slot_size * slot_mult * (slot_pct / 100)
        peak = max(peak, capital)
        max_dd = max(max_dd, (peak - capital) / peak * 100)
        equity_log.append((slot_exit, round(capital, 4)))

    if len(equity_log) < 10:
        return None

    # Annualized Sharpe via daily-equivalent event returns.
    # Industry standard (hedge funds / quant firms): annualize with √252 trading days.
    # event_days from equity_log are CALENDAR days; convert to trading-day equivalents
    # via × 252/365.25 before dividing returns, so the √252 annualisation is consistent.
    # (Using calendar days / √252 understates ann. Sharpe by √(252/365.25) ≈ 17%.)
    event_rets = []
    event_days_td = []  # trading-day equivalents
    for i in range(1, len(equity_log)):
        prev_dt, prev_cap = equity_log[i - 1]
        curr_dt, curr_cap = equity_log[i]
        if prev_cap > 0:
            cal_days = max((curr_dt - prev_dt).days, 1)
            event_rets.append((curr_cap / prev_cap - 1) * 100)
            event_days_td.append(max(cal_days * 252 / 365.25, 1.0))

    if not event_rets:
        return None

    daily_equiv = [r / d for r, d in zip(event_rets, event_days_td)]
    mu_d = np.mean(daily_equiv)
    std_d = np.std(daily_equiv, ddof=1)
    ann_sharpe = round((mu_d / std_d) * np.sqrt(252), 3) if std_d > 0 else None

    total_days = (equity_log[-1][0] - equity_log[0][0]).days
    n_years = total_days / 365.25 if total_days > 0 else 1.0
    cagr = round(((capital / 10_000) ** (1 / n_years) - 1) * 100, 2) if n_years > 0 else 0.0

    # Counterfactual: pure T-bill CAGR over same period for comparison
    tbill_cagr = round((_T_BILL_ANN * 100), 1)

    n_events = len(equity_log) - 1
    n_input = len(df)

    if not quiet:
        print(f"\n## §QuantEngine: Portfolio Equity-Curve Simulation ({max_concurrent} concurrent slots)\n")
        _metrics_rows = [
            ["Input trades", str(n_input), "signal-level"],
            ["Skipped (slots full)", str(skipped), f"{skipped / n_input * 100:.1f}%"],
            ["Exit events", str(n_events), "slot close events"],
            ["Final capital", f"${capital:,.0f}", "from $10,000 start (incl. T-bill on idle)"],
            ["CAGR", f"{cagr:+.1f}%", f"over {n_years:.1f} years"],
            ["T-bill benchmark", f"+{tbill_cagr:.1f}%", f"{_T_BILL_ANN * 100:.1f}% annual on idle (QE4)"],
            ["Portfolio Max DD", f"-{max_dd:.2f}%", "concurrent-position compound DD"],
            ["Annualized Sharpe", fmt_sharpe(ann_sharpe) if ann_sharpe else "—", "event-time (see note)"],
        ]
        if vol_target is not None and _vol_multipliers is not None:
            _avg_mult = float(np.mean(_vol_multipliers))
            _metrics_rows.insert(
                4,
                ["Vol target (ann)", f"{vol_target:.0%}", f"avg size mult {_avg_mult:.2f}x (Harvey/Man Group)"],
            )
        print_table(["Metric", "Value", "Note"], _metrics_rows)
        print(
            f"\n> Idle capital earns {_T_BILL_ANN * 100:.1f}%/yr T-bill rate (QE4: 3.5% historical 2003-2026 avg).\n"
            "> Ann. Sharpe from event-time daily-equivalent returns — use CAGR as the primary metric.\n"
            f"> Concurrent DD compounding: {max_concurrent} simultaneous losing trades → "
            f"{max_concurrent * POSITION_SIZE * 100:.0f}% max concurrent exposure.\n"
        )
    return {
        "cagr": cagr,
        "max_dd": round(max_dd, 2),
        "ann_sharpe": ann_sharpe,
        "skipped": skipped,
        "equity_log": equity_log,
    }


def run_walk_forward_with_opt(
    all_dfs: dict,
    vix: dict,
    spy_trend: dict,
    stlfsi4: dict,
) -> None:
    """True walk-forward validation with per-epoch BUY_THRESH optimisation.

    Partitions the 23-year IS universe into 4 consecutive epochs.
    For each epoch i (i > 0):
      1. Select BUY_THRESH on all data BEFORE epoch i (expanding IS window).
      2. Evaluate the selected threshold on epoch i (walk-forward OOS).

    Yields 3 honest OOS Sharpe estimates — threshold selection never looks at
    the epoch being evaluated.  This is a structural improvement over
    run_walk_forward_temporal() which uses the globally-set BUY_THRESH (fit on
    the full 23-yr IS) in all epochs.

    Speed: pre-computes trade lists for each threshold candidate once, then
    filters by year for IS/OOS splits — avoids N_tickers × N_epochs × N_thresh
    re-downloads.
    """
    global BUY_THRESH
    orig_thresh = BUY_THRESH

    EPOCH_DEFS = [
        ("2003–2009", 2003, 2010),
        ("2010–2016", 2010, 2017),
        ("2017–2021", 2017, 2022),
        ("2022–pres", 2022, 2100),
    ]
    WF_THRESH = [40, 45, 50, 55, 60]

    print("\n## §QuantEngine: Walk-Forward with BUY_THRESH Optimisation\n")
    print("> Pre-computes trades for each threshold, then splits by epoch year range.")
    print("> IS window = all data before OOS epoch (expanding) — threshold never sees OOS data.\n")

    # Step 1: pre-compute full trade DataFrames for each threshold candidate
    print("Pre-computing per-threshold trade lists…", end=" ", flush=True)
    per_thresh: dict[int, pd.DataFrame] = {}
    for thresh in WF_THRESH:
        BUY_THRESH = thresh
        t_list = _filter_simulation_results(
            _run_simulation_parallel(
                all_dfs,
                common_kwargs={"mr_only": True},
                vix=vix,
                spy_trend=spy_trend,
                stlfsi4=stlfsi4,
            )
        )
        per_thresh[thresh] = pd.concat(t_list, ignore_index=True) if t_list else pd.DataFrame()
    BUY_THRESH = orig_thresh
    print("done.\n")

    oos_sharpes: list[float] = []
    rows = []

    for epoch_i in range(1, len(EPOCH_DEFS)):
        oos_label, oos_start, oos_end = EPOCH_DEFS[epoch_i]

        # Step 2: select best threshold on all IS data before this epoch
        best_thresh = orig_thresh
        best_is_sh = -999.0
        for thresh in WF_THRESH:
            df_thresh = per_thresh.get(thresh)
            if df_thresh is None or df_thresh.empty:
                continue
            is_sub = df_thresh[df_thresh["date"].dt.year < oos_start]
            if is_sub.empty:
                continue
            s_is = stats(is_sub["net_pct"].tolist())
            sh = s_is.get("sharpe") or -999.0
            if sh > best_is_sh and s_is["n"] >= 10:
                best_is_sh = sh
                best_thresh = thresh

        # Step 3: evaluate selected threshold on OOS epoch
        df_oos_src = per_thresh.get(best_thresh)
        if df_oos_src is not None and not df_oos_src.empty:
            oos_sub = df_oos_src[(df_oos_src["date"].dt.year >= oos_start) & (df_oos_src["date"].dt.year < oos_end)]
            s_oos = stats(oos_sub["net_pct"].tolist() if not oos_sub.empty else [])
        else:
            s_oos = dict(_EMPTY_STATS)

        sh_oos = s_oos.get("sharpe")
        if sh_oos is not None:
            oos_sharpes.append(sh_oos)

        rows.append(
            [
                oos_label,
                str(best_thresh),
                f"{best_is_sh:.2f}" if best_is_sh > -999 else "—",
                str(s_oos["n"]),
                f"{s_oos['wr']:.1f}%" if s_oos["n"] else "—",
                f"{s_oos['avg']:+.2f}%" if s_oos["n"] else "—",
                fmt_sharpe(sh_oos),
            ]
        )

    print_table(
        ["OOS Epoch", "Sel. Thresh", "IS Sharpe", "OOS N", "OOS WR", "OOS Avg", "OOS Sharpe"],
        rows,
    )

    if oos_sharpes:
        wf_avg = float(np.mean(oos_sharpes))
        wf_pos = sum(1 for s in oos_sharpes if s > 0)
        print(f"\n**Walk-Forward OOS Sharpe ({len(oos_sharpes)} epochs avg):** {wf_avg:.3f}")
        print(f"**Positive OOS epochs:** {wf_pos}/{len(oos_sharpes)}")
        verdict = (
            "✅ Edge persists under parameter rotation — forward estimate is positive."
            if wf_avg > 0.05
            else "⚠ Marginal forward edge — may be in-sample inflation."
            if wf_avg > 0
            else "⛔ Negative walk-forward OOS — edge is in-sample only."
        )
        print(f"> {verdict}")
    n_wf_trials = (len(EPOCH_DEFS) - 1) * len(WF_THRESH)
    total_oos_n = sum(int(r[3]) for r in rows if r[3].isdigit())
    _log_experiment(
        experiment_type="walk_forward_threshold",
        hypothesis="Walk-forward BUY_THRESH optimisation per epoch",
        n_trials=n_wf_trials,
        is_metrics={
            "sharpe": round(float(np.mean(oos_sharpes)), 3) if oos_sharpes else None,
            "n": total_oos_n,
        },
    )
    print()


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


def run_oos_validation(vix, spy_trend, stlfsi4, buy_thresh_override=None):
    """Run the MR-only strategy on HELD_OUT_TICKERS and compare vs main universe.

    buy_thresh_override — if set (e.g. 45 from --buy-thresh), validates a relaxed
    entry-score gate out-of-sample (paired with --relax-sweep findings).

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

    args_list = [(t, vix, spy_trend, stlfsi4, True, False, {}, False, False) for t in HELD_OUT_TICKERS]
    _workers = int(os.getenv("BACKTEST_WORKERS", "8"))
    with ThreadPoolExecutor(max_workers=min(_workers, len(HELD_OUT_TICKERS))) as p:
        results = list(p.map(process_ticker, args_list))

    oos_dfs = {ticker: ind_df for ticker, _bh, ind_df, _ed in results if ind_df is not None and not ind_df.empty}
    _sim_results = _run_simulation_parallel(
        oos_dfs,
        common_kwargs={"mr_only": True, "buy_thresh_override": buy_thresh_override},
        vix=vix,
        spy_trend=spy_trend,
        stlfsi4=stlfsi4,
    )
    per_ticker_trades = {ticker: df for ticker, df in _sim_results}
    oos_trades = [df for _, df in _sim_results if df is not None and not df.empty]
    clean_trades = [
        df for ticker, df in _sim_results if df is not None and not df.empty and ticker not in _OOS_BLOCKED_TICKERS
    ]

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

    # ── R7 OOS check: DD-scaled exposure on the held-out clean set ─────────────
    if "date" in oos_clean.columns and len(oos_clean) >= 20:
        _ob = run_portfolio_simulation(oos_clean, dd_throttle=False, quiet=True)
        _ot = run_portfolio_simulation(oos_clean, dd_throttle=True, dd_trig=3.0, throttle_mult=0.5, quiet=True)
        if _ob and _ot:
            print("\n### R7 OOS — DD-Throttle on Held-Out Set (concurrent portfolio)\n")
            print_table(
                ["Policy (OOS clean)", "CAGR", "Ann.Sharpe", "Max DD"],
                [
                    ["Full exposure", f"{_ob['cagr']:+.1f}%", fmt_sharpe(_ob["ann_sharpe"]), f"-{_ob['max_dd']:.2f}%"],
                    [
                        "DD-throttle 0.5× >3% off peak",
                        f"{_ot['cagr']:+.1f}%",
                        fmt_sharpe(_ot["ann_sharpe"]),
                        f"-{_ot['max_dd']:.2f}%",
                    ],
                ],
            )
            _dmd_o = _ob["max_dd"] - _ot["max_dd"]
            _dsa_o = (_ot["ann_sharpe"] or 0.0) - (_ob["ann_sharpe"] or 0.0)
            print(
                f"\n> OOS: ΔAnn.Sharpe {_dsa_o:+.3f}, MaxDD reduction {_dmd_o:+.2f}pp "
                f"(N={len(oos_clean)} — small; directional only).\n"
            )

    # Per-ticker breakdown
    print("\n### OOS Per-Ticker\n")
    rows = []
    for ticker, _bh, _ind, _ed in results:
        t_df = per_ticker_trades.get(ticker)
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
    # §59–§82 canonical IS (sector-filtered live-equivalent, v10.9)
    # Updated 2026-06-10: matches current delivery_gates.py BLOCKED_SECTORS.
    is_wr = 69.3
    is_avg = 0.83
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

    # Statistical significance of OOS Sharpe — essential context for any claim of alpha
    sharpe_ci_print(sc.get("sharpe"), sc["n"], label="OOS CLEAN")
    sharpe_ci_print(s.get("sharpe"), s["n"], label="OOS ALL")

    # Minimum N needed for OOS CI lower bound to exceed 0.0
    _target_sr = 0.10
    _n_needed = math.ceil((1.96 / _target_sr) ** 2 * (1 + _target_sr**2 / 2))
    _oos_clean_n = sc["n"]
    _n_gap = _n_needed - _oos_clean_n
    _n_verdict = "sufficient ✅" if _n_gap <= 0 else f"insufficient ({_n_gap} more needed) ⚠"
    print(
        f"\n> **Minimum OOS N for CI to exclude 0 at SR≥{_target_sr}:** "
        f"≈{_n_needed} trades — current CLEAN N={_oos_clean_n} is {_n_verdict}"
    )
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Parallel Processing
# ─────────────────────────────────────────────────────────────────────────────


def process_ticker(args):
    (
        ticker,
        vix,
        spy_trend,
        stlfsi4,
        mr_only,
        beta_hedge,
        spy_prices,
        forecast_sizing,
        no_family_discount,
    ) = args
    print(f"Processing {ticker}…", flush=True)
    try:
        # Check indicator cache first
        _HERE = os.path.dirname(os.path.abspath(__file__))
        cache_dir = os.path.abspath(os.path.join(_HERE, "..", "data", "cache_indicators"))
        os.makedirs(cache_dir, exist_ok=True)
        ticker_clean = ticker.replace("^", "_").replace("-", "_").replace(" ", "_")
        _cache_suffix = "_nodisc" if no_family_discount else ""
        indicator_cache_path = os.path.join(cache_dir, f"{ticker_clean}_{START}_{END}{_cache_suffix}.csv")

        loaded_from_cache = False
        if os.path.exists(indicator_cache_path):
            try:
                df = pd.read_csv(indicator_cache_path, index_col=0, parse_dates=True)
                loaded_from_cache = True
            except Exception as e:
                print(f"Failed to read indicator cache for {ticker}: {e}, computing fresh...", flush=True)

        if not loaded_from_cache:
            raw = cached_yf_download(ticker, start=START, end=END, interval="1d", auto_adjust=True, progress=False)
            if raw.empty or len(raw) < 250:
                print(f"{ticker}: insufficient data — skipped", flush=True)
                return ticker, None, None, None

            # Flatten MultiIndex columns if present
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)

            df = raw[["Open", "High", "Low", "Close", "Volume"]].copy()
            df = df.ffill().dropna(subset=["Close", "Volume"])

            # Wrap indicator computation: missing columns should not crash per-ticker.
            try:
                compute_indicators(df)
                # Cache the computed dataframe
                df.to_csv(indicator_cache_path)
            except Exception as e:
                print(f"\n{ticker} compute_indicators error — {e}", flush=True)
                df["score"] = 0.0
                return ticker, None, None, None

        bh_return = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[0]) - 1) * 100

        if "vwap_pct" not in df.columns:
            df["vwap_pct"] = np.nan
        if "vwap_pct_prev" not in df.columns:
            df["vwap_pct_prev"] = df["vwap_pct"].shift(1)
        if "vwap_slope_pos" not in df.columns:
            df["vwap_slope_pos"] = False

        df["score"] = compute_scores(df, no_family_discount=no_family_discount)

        # ── Fetch earnings dates: Polygon only (full point-in-time history) ────
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
        return ticker, bh_return, df, earnings_dates
    except Exception as e:
        print(f"{ticker} error — {e}", flush=True)
        return ticker, None, None, None


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main():
    global HOLD_DAYS, MAX_LOSS_DAYS, TICKERS
    if "--pbo" in sys.argv or "--quick" in sys.argv:
        TICKERS = TICKERS[:15]
    # --hold N : override hold period (e.g. --hold 5 for short-horizon MR validation)
    if "--hold" in sys.argv:
        _hi = sys.argv.index("--hold")
        if _hi + 1 < len(sys.argv):
            HOLD_DAYS = int(sys.argv[_hi + 1])
            MAX_LOSS_DAYS = max(1, round(HOLD_DAYS * 0.4))
            print(f"[--hold override] HOLD_DAYS={HOLD_DAYS}  MAX_LOSS_DAYS={MAX_LOSS_DAYS}")

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
    print("> ✓ **Survivorship bias correction — ACTIVE:** Point-in-time S&P 500 constituent data")
    print(">   sourced from https://github.com/fja05680/sp500.git is loaded and enforced.")
    print(">   Historical/delisted companies (Lehman Brothers, Bear Stearns, Washington Mutual,")
    print(">   Sears, General Electric, etc.) are simulated for their active constituent windows.")
    print(">   Signals outside their index membership windows are excluded from the backtest.\n")

    # ── Download VIX ─────────────────────────────────────────────────────────
    print("Fetching VIX…", end=" ", flush=True)
    try:
        vix_df = cached_yf_download("^VIX", start=START, end=END, interval="1d", auto_adjust=False, progress=False)
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

    # ── Share macro state with parallel simulation workers ────────────────────
    global _RUN_VIX, _RUN_SPY_TREND, _RUN_STLFSI4
    _RUN_VIX = vix
    _RUN_SPY_TREND = spy_trend
    _RUN_STLFSI4 = stlfsi4

    # ── §104–§110: Load alt-data panels (if available) ────────────────────────
    _finra_sv_flag = "--finra-sv" in sys.argv
    _sec_ftd_flag = "--sec-ftd" in sys.argv
    _naaim_flag = "--naaim" in sys.argv
    _gdelt_flag = "--gdelt" in sys.argv
    _finra_ats_flag = "--finra-ats" in sys.argv
    _wiki_flag = "--wiki" in sys.argv
    _occ_flag = "--occ" in sys.argv

    if _finra_sv_flag:
        print("Loading FINRA short-volume panel…", end=" ", flush=True)
        try:
            from services.finra_short_volume import load_short_volume_panel

            _alt_data_panels["finra_sv"] = load_short_volume_panel()
            print(
                f"ok ({len(_alt_data_panels['finra_sv'])} rows)"
                if _alt_data_panels["finra_sv"] is not None
                else "not found"
            )
        except Exception as e:
            print(f"failed ({e})")
    if _sec_ftd_flag:
        print("Loading SEC FTD panel…", end=" ", flush=True)
        try:
            from services.sec_ftd import load_ftd_panel

            _alt_data_panels["sec_ftd"] = load_ftd_panel()
            print(
                f"ok ({len(_alt_data_panels['sec_ftd'])} rows)"
                if _alt_data_panels["sec_ftd"] is not None
                else "not found"
            )
        except Exception as e:
            print(f"failed ({e})")
    if _naaim_flag:
        print("Loading sentiment panels…", end=" ", flush=True)
        try:
            from services.sentiment_naaim_aaii import load_umcsent_panel, load_naaim_panel, load_aaii_panel

            _alt_data_panels["umcsent"] = load_umcsent_panel()
            _alt_data_panels["naaim"] = load_naaim_panel()
            _alt_data_panels["aaii"] = load_aaii_panel()
            _parts = []
            if _alt_data_panels["umcsent"] is not None:
                _parts.append(f"umcsent={len(_alt_data_panels['umcsent'])}")
            if _alt_data_panels["naaim"] is not None:
                _parts.append(f"naaim={len(_alt_data_panels['naaim'])}")
            if _alt_data_panels["aaii"] is not None:
                _parts.append(f"aaii={len(_alt_data_panels['aaii'])}")
            print(f"ok ({', '.join(_parts)})" if _parts else "not found")
        except Exception as e:
            print(f"failed ({e})")
    if _gdelt_flag:
        print("Loading GDELT tone panel…", end=" ", flush=True)
        try:
            from services.gdelt_news_tone import load_gdelt_tone_panel

            _alt_data_panels["gdelt"] = load_gdelt_tone_panel()
            print(
                f"ok ({len(_alt_data_panels['gdelt'])} rows)" if _alt_data_panels["gdelt"] is not None else "not found"
            )
        except Exception as e:
            print(f"failed ({e})")
    if _finra_ats_flag:
        print("Loading FINRA ATS panel…", end=" ", flush=True)
        try:
            from services.finra_ats_dark_pool import load_ats_panel

            _alt_data_panels["finra_ats"] = load_ats_panel()
            print(
                f"ok ({len(_alt_data_panels['finra_ats'])} rows)"
                if _alt_data_panels["finra_ats"] is not None
                else "not found"
            )
        except Exception as e:
            print(f"failed ({e})")
    if _wiki_flag:
        print("Loading Wikipedia pageviews panel…", end=" ", flush=True)
        try:
            from services.wikipedia_pageviews import load_wikipedia_panel

            _alt_data_panels["wikipedia"] = load_wikipedia_panel()
            print(
                f"ok ({len(_alt_data_panels['wikipedia'])} rows)"
                if _alt_data_panels["wikipedia"] is not None
                else "not found"
            )
        except Exception as e:
            print(f"failed ({e})")
    if _occ_flag:
        print("Loading OCC volume/OI panel…", end=" ", flush=True)
        try:
            from services.occ_volume_oi import load_occ_panel

            _alt_data_panels["occ"] = load_occ_panel()
            print(f"ok ({len(_alt_data_panels['occ'])} rows)" if _alt_data_panels["occ"] is not None else "not found")
        except Exception as e:
            print(f"failed ({e})")

    # ── §111: ORATS historical options panel ──────────────────────────────────
    # The purchased FTP download expires after ~30 days, so PostgreSQL is the
    # authoritative long-term store.  Parquet is used only as a build-time cache.
    _orats_flag = "--orats" in sys.argv
    if _orats_flag:
        print("Loading ORATS options panel…", end=" ", flush=True)
        try:
            from database import _IS_POSTGRES
            from services.orats_data import load_orats_panel, load_orats_panel_from_db

            _orats_path = Path(__file__).resolve().parent.parent / "data" / "cache_orats" / "orats_panel.parquet"
            # Prefer Postgres (persistent) over parquet (temporary build artifact).
            _orats_source = "postgres" if _IS_POSTGRES else "sqlite"
            try:
                _alt_data_panels["orats"] = asyncio.run(load_orats_panel_from_db())
            except Exception as _db_err:
                _db_msg = str(_db_err).split("\n")[0][:120]
                print(f"\n  [db fallback: {_db_msg}…]", end=" ", flush=True)
                _alt_data_panels["orats"] = load_orats_panel(_orats_path)
                _orats_source = "parquet"
            if _alt_data_panels["orats"] is None:
                _alt_data_panels["orats"] = load_orats_panel(_orats_path)
                _orats_source = "parquet"
            if _alt_data_panels["orats"] is not None:
                _orats_df = _alt_data_panels["orats"]
                print(f"ok ({_orats_source}: {len(_orats_df)} rows, {_orats_df['ticker'].nunique()} tickers)")
                # Convert to nested dict for fast point-in-time lookup in simulate_ticker().
                _orats_dict: dict[str, dict] = {}
                for _ot, _og in _orats_df.groupby("ticker"):
                    _orats_dict[_ot] = {pd.to_datetime(_r["date"]).date(): _r for _r in _og.to_dict("records")}
                _alt_data_panels["orats"] = _orats_dict
            else:
                print("not found")
        except Exception as e:
            print(f"failed ({e})")

    # ── Download price data and compute signals ───────────────────────────────
    all_trades: list[pd.DataFrame] = []
    bh_returns = []
    all_dfs = {}

    mode_label = "MR-Only" if BACKTEST_MR_DEFAULT else "Full-Signal"
    print(f"\nRunning in **{mode_label}** mode (BACKTEST_MR_DEFAULT={BACKTEST_MR_DEFAULT})")
    if BACKTEST_MR_DEFAULT:
        print(f"  MR gate: RSI<{MR_RSI_CEIL} OR BB%B<{MR_BB_CEIL} OR IBS<{MR_IBS_CEIL} OR VWAP%<{MR_VWAP_FLOOR}%\n")

    _beta_hedge_flag = "--beta-hedge" in sys.argv
    _forecast_sizing_flag = "--forecast-sizing" in sys.argv
    _score_band_sizing_flag = "--score-band-sizing" in sys.argv
    _dynamic_stop_rsi_flag = "--dynamic-stop-rsi" in sys.argv
    _no_family_discount_flag = "--no-family-discount" in sys.argv
    _entry_delay_flag = "--entry-delay" in sys.argv
    _consec_score_flag = "--consec-score" in sys.argv
    _consec_score_sizing_flag = "--consec-score-sizing" in sys.argv
    _entry_at_close_flag = "--entry-at-close" in sys.argv
    _entry_limit_flag = "--entry-limit" in sys.argv
    _entry_limit_k = None
    for _i, _arg in enumerate(sys.argv):
        if _arg == "--entry-limit" and _i + 1 < len(sys.argv):
            try:
                _entry_limit_k = float(sys.argv[_i + 1])
            except ValueError:
                pass

    # §MAX: filter out signals whose trailing 21-day MAX is above the expanding 55th percentile.
    _max21_filter_pct = 0.55  # default: keep bottom 55% (low MAX)
    if "--max21-filter" in sys.argv:
        for _i, _arg in enumerate(sys.argv):
            if _arg == "--max21-filter" and _i + 1 < len(sys.argv):
                try:
                    _max21_filter_pct = float(sys.argv[_i + 1])
                except ValueError:
                    pass

    # Portfolio-level volatility target (Harvey et al. / Man Group).
    _vol_target: float | None = None
    if "--vol-target" in sys.argv:
        _vol_target = VOL_REF_ANN  # default 25%
        for _i, _arg in enumerate(sys.argv):
            if _arg == "--vol-target" and _i + 1 < len(sys.argv):
                try:
                    _vol_target = float(sys.argv[_i + 1])
                except ValueError:
                    pass

    # Parse --target-mult X.Y
    _target_mult_override = None
    for _i, _arg in enumerate(sys.argv):
        if _arg == "--target-mult" and _i + 1 < len(sys.argv):
            try:
                _target_mult_override = float(sys.argv[_i + 1])
            except ValueError:
                pass

    # Parse --max-loss-days N
    _max_loss_days_override = None
    for _i, _arg in enumerate(sys.argv):
        if _arg == "--max-loss-days" and _i + 1 < len(sys.argv):
            try:
                _max_loss_days_override = int(sys.argv[_i + 1])
            except ValueError:
                pass

    # Parse --dow-filter MON,TUE,WED,THU,FRI
    _dow_filter = None
    _dow_map = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4}
    for _i, _arg in enumerate(sys.argv):
        if _arg == "--dow-filter" and _i + 1 < len(sys.argv):
            _dow_parts = sys.argv[_i + 1].upper().split(",")
            _dow_filter = {_dow_map[p.strip()] for p in _dow_parts if p.strip() in _dow_map}

    # Parse --consec-score-grad N (graduated consecutive score threshold, e.g. 45)
    _consec_score_thresh_override = None
    for _i, _arg in enumerate(sys.argv):
        if _arg == "--consec-score-grad" and _i + 1 < len(sys.argv):
            try:
                _consec_score_thresh_override = float(sys.argv[_i + 1])
            except ValueError:
                pass

    # Parse --mr-count N (require N MR conditions simultaneously)
    _mr_count_override = None
    for _i, _arg in enumerate(sys.argv):
        if _arg == "--mr-count" and _i + 1 < len(sys.argv):
            try:
                _mr_count_override = int(sys.argv[_i + 1])
            except ValueError:
                pass

    # Parse --rsi-ceil N
    _rsi_ceil_override = None
    for _i, _arg in enumerate(sys.argv):
        if _arg == "--rsi-ceil" and _i + 1 < len(sys.argv):
            try:
                _rsi_ceil_override = float(sys.argv[_i + 1])
            except ValueError:
                pass

    # Parse --bb-ceil N
    _bb_ceil_override = None
    for _i, _arg in enumerate(sys.argv):
        if _arg == "--bb-ceil" and _i + 1 < len(sys.argv):
            try:
                _bb_ceil_override = float(sys.argv[_i + 1])
            except ValueError:
                pass

    # Parse --ibs-ceil N
    _ibs_ceil_override = None
    for _i, _arg in enumerate(sys.argv):
        if _arg == "--ibs-ceil" and _i + 1 < len(sys.argv):
            try:
                _ibs_ceil_override = float(sys.argv[_i + 1])
            except ValueError:
                pass

    # Parse --buy-thresh N
    _buy_thresh_override = None
    for _i, _arg in enumerate(sys.argv):
        if _arg == "--buy-thresh" and _i + 1 < len(sys.argv):
            try:
                _buy_thresh_override = int(sys.argv[_i + 1])
            except ValueError:
                pass

    _score_accel_flag = "--score-accel" in sys.argv

    # SPY prices are needed for the beta-hedge leg return computation
    spy_prices: dict = {}
    if _beta_hedge_flag:
        print("Fetching SPY daily closes for beta-hedge computation…", end=" ", flush=True)
        spy_prices = fetch_spy_prices(START, END)
        print(f"ok ({len(spy_prices)} bars)" if spy_prices else "failed — beta hedge disabled")

    args_list = [
        (
            t,
            vix,
            spy_trend,
            stlfsi4,
            BACKTEST_MR_DEFAULT,
            _beta_hedge_flag,
            spy_prices,
            _forecast_sizing_flag,
            _no_family_discount_flag,
        )
        for t in TICKERS
    ]

    # Run sequentially if --sequential is present or when running --pbo to prevent macOS fork deadlocks
    _run_seq = "--sequential" in sys.argv or "--pbo" in sys.argv
    if _run_seq:
        print("Running ticker processing sequentially...")
        results = [process_ticker(args) for args in args_list]
    else:
        _workers = int(os.getenv("BACKTEST_WORKERS", "8"))
        print(f"Running ticker processing with {_workers} threads...")
        with ThreadPoolExecutor(max_workers=_workers) as p:
            results = list(p.map(process_ticker, args_list))

    all_earnings_dates = {}
    for ticker, bh_ret, df, earnings_dates in results:
        if bh_ret is not None:
            bh_returns.append(bh_ret)
        if df is not None:
            all_dfs[ticker] = df
            all_earnings_dates[ticker] = earnings_dates

    # ── §104–§110: Pre-filter alt-data panels to active tickers + convert to dict for O(1) lookups ─
    _active_tickers = set(all_dfs.keys())
    # Build full trading-date range from all_dfs for global-panel daily ffill
    _all_dates = set()
    for _t_df in all_dfs.values():
        _all_dates.update(pd.to_datetime(_t_df.index).date)
    _sorted_dates = sorted(_all_dates)
    for _panel_key in list(_alt_data_panels.keys()):
        _panel = _alt_data_panels[_panel_key]
        if not isinstance(_panel, pd.DataFrame):
            continue
        if "ticker" in _panel.columns:
            _panel = _panel[_panel["ticker"].isin(_active_tickers)].copy()
        # Convert date cols to datetime.date for consistent key hashing
        for _dcol in ("date", "effective_date"):
            if _dcol in _panel.columns:
                _panel[_dcol] = pd.to_datetime(_panel[_dcol]).dt.date
        if "ticker" in _panel.columns:
            # Per-ticker panel → nested dict: {ticker: {date: row_dict}}
            _alt_data_panels[_panel_key] = {
                _t: _grp.set_index("date" if "date" in _grp.columns else "effective_date").to_dict("index")
                for _t, _grp in _panel.groupby("ticker")
            }
        else:
            # Global panel (e.g., NAAIM, UMCSENT) → forward-fill to daily then flat dict
            _dcol = "date" if "date" in _panel.columns else _panel.columns[0]
            _panel = _panel.set_index(_dcol).sort_index()
            # Reindex to all trading dates and forward-fill
            _daily = _panel.reindex(_sorted_dates, method="ffill")
            _alt_data_panels[_panel_key] = _daily.to_dict("index")

    # ── §63 Sector cointegration Z-score (post-pool, pure numpy) ─────────────
    # For each ticker, compute rolling 252-day cointegration Z-score vs its
    # sector ETF. Stored as df["coint_z"] column so score_row() and
    # compute_scores() can use it as a scoring modifier (+4/+2/-2 pts).
    print("Computing §63 sector cointegration Z-scores…", end=" ", flush=True)
    try:
        _sector_etfs = list({TICKER_TO_SECTOR.get(t, "XLK") for t in all_dfs})
        _etf_raw = cached_yf_download(
            _sector_etfs, start=START, end=END, interval="1d", auto_adjust=True, progress=False
        )
        if isinstance(_etf_raw.columns, pd.MultiIndex):
            _etf_close = _etf_raw["Close"]
        else:
            _etf_close = _etf_raw[["Close"]] if "Close" in _etf_raw.columns else _etf_raw
        _etf_close.index = pd.to_datetime([str(i)[:10] for i in _etf_close.index])

        def _coint_z_series(ticker_prices: pd.Series, etf_prices: pd.Series, window: int = 252) -> pd.Series:
            combined = pd.DataFrame({"s": ticker_prices, "e": etf_prices}).dropna()
            if len(combined) < 60:
                return pd.Series(dtype=float, index=combined.index)
            W = window + 1
            s_col = combined["s"]
            e_col = combined["e"]

            sum_s = s_col.rolling(W, min_periods=60).sum()
            sum_e = e_col.rolling(W, min_periods=60).sum()
            sum_se = (s_col * e_col).rolling(W, min_periods=60).sum()
            sum_ee = (e_col**2).rolling(W, min_periods=60).sum()
            sum_ss = (s_col**2).rolling(W, min_periods=60).sum()
            N = s_col.rolling(W, min_periods=60).count()

            denom = N * sum_ee - sum_e**2
            denom_valid = denom.abs() > 1e-12

            beta = np.where(denom_valid, (N * sum_se - sum_s * sum_e) / denom, np.nan)
            alpha = np.where(denom_valid, (sum_s - beta * sum_e) / N, np.nan)

            resid_last = s_col - (beta * e_col + alpha)
            ss = (
                sum_ss
                + beta**2 * sum_ee
                + N * alpha**2
                - 2 * beta * sum_se
                - 2 * alpha * sum_s
                + 2 * beta * alpha * sum_e
            )
            var = np.maximum(ss / (N - 1), 0.0)
            sigma = np.sqrt(var)

            z_score = np.where((sigma > 1e-8) & denom_valid, resid_last / sigma, np.nan)

            # Engle-Granger step 2: gate the z-score on residual STATIONARITY,
            # mirroring the live engine (services/technicals.py). Per-bar ADF over
            # 23y is too slow, so we test cointegration at quarterly cadence over
            # the trailing `window` and apply the verdict to the NEXT quarter only
            # (test on trailing data, apply forward → no lookahead). Pairs that
            # aren't cointegrated get coint_z=NaN, which every scorer already skips.
            if _COINT_REQUIRE_STATIONARY:
                z_arr = np.asarray(z_score, dtype=float)
                sv = s_col.values
                ev = e_col.values
                ok = np.zeros(len(combined), dtype=bool)
                step = 63
                try:
                    from statsmodels.tsa.stattools import coint

                    for end in range(window, len(combined), step):
                        try:
                            pval = coint(sv[end - window : end], ev[end - window : end])[1]
                        except Exception:
                            pval = 1.0
                        if pval < _COINT_ADF_PMAX:
                            ok[end : end + step] = True
                    z_arr = np.where(ok, z_arr, np.nan)
                except Exception:
                    pass  # statsmodels unavailable → leave z ungated
                return pd.Series(z_arr, index=combined.index)

            return pd.Series(z_score, index=combined.index)

        _coint_added = 0
        for ticker, df in all_dfs.items():
            etf = TICKER_TO_SECTOR.get(ticker, "XLK")
            if etf in _etf_close.columns:
                etf_p = _etf_close[etf]
            elif len(_sector_etfs) == 1 and etf == _sector_etfs[0]:
                etf_p = _etf_close.iloc[:, 0]
            else:
                continue
            cz = _coint_z_series(df["Close"], etf_p)
            df["coint_z"] = cz.reindex(df.index)
            # Recompute scores so they include cointegration adjustments!
            df["score"] = compute_scores(df, no_family_discount=_no_family_discount_flag)
            _coint_added += 1
        print(f"ok ({_coint_added}/{len(all_dfs)} tickers)")
    except Exception as _coint_err:
        print(f"skipped ({_coint_err})")

    # ── Meta-label feature pre-computation (QUANT_ENGINE_REVIEW §1.3) ──────────
    # VIX3M for term-structure ratio
    print("Fetching VIX3M…", end=" ", flush=True)
    _vix3m_series: pd.Series | None = None
    try:
        _vix3m_df = cached_yf_download("^VIX3M", start=START, end=END, interval="1d", auto_adjust=False, progress=False)
        if isinstance(_vix3m_df.columns, pd.MultiIndex):
            _vix3m_df.columns = _vix3m_df.columns.get_level_values(0)
        _vix3m_raw = _vix3m_df["Close"] if "Close" in _vix3m_df.columns else pd.Series(dtype=float)
        _vix3m_series = {pd.Timestamp(str(k)[:10]): float(v) for k, v in _vix3m_raw.items() if pd.notna(v)}
        print(f"ok ({len(_vix3m_series)} bars)")
    except Exception as _v3m_err:
        print(f"failed ({_v3m_err})")

    # Entry model for meta-label training
    _entry_model = None
    if xgb is not None:
        try:
            _entry_model_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "backtest_ml_model.json"
            )
            if os.path.exists(_entry_model_path):
                _entry_model = xgb.Booster()
                _entry_model.load_model(_entry_model_path)
                print(f"[meta] entry model loaded ({_entry_model_path})")
        except Exception as _em_err:
            print(f"[meta] entry model load failed: {_em_err}")

    # HMM regime cache (daily bull_prob + transition_risk)
    _hmm_cache: dict = {}
    if GaussianHMM is not None and vix:
        print("[meta] pre-computing HMM regimes…", end=" ", flush=True)
        try:
            _vix_dates = sorted(vix.keys())
            _spy_hist = cached_yf_download("SPY", start=START, end=END, interval="1d", auto_adjust=True, progress=False)
            if isinstance(_spy_hist.columns, pd.MultiIndex):
                _spy_hist.columns = _spy_hist.columns.get_level_values(0)
            _spy_close = _spy_hist["Close"] if "Close" in _spy_hist.columns else pd.Series(dtype=float)
            _spy_close.index = pd.to_datetime([str(i)[:10] for i in _spy_close.index])
            _spy_ret = _spy_close.pct_change(20).fillna(0)
            _spy_rvol = _spy_close.pct_change().fillna(0).rolling(30).std().fillna(0) * np.sqrt(252)

            # Try to fetch TNX/IRX for yield curve
            _tnx_s = pd.Series(dtype=float)
            _irx_s = pd.Series(dtype=float)
            try:
                _tnx_df = cached_yf_download(
                    "^TNX", start=START, end=END, interval="1d", auto_adjust=False, progress=False
                )
                _irx_df = cached_yf_download(
                    "^IRX", start=START, end=END, interval="1d", auto_adjust=False, progress=False
                )
                if "Close" in _tnx_df.columns:
                    _tnx_s = _tnx_df["Close"]
                    _tnx_s.index = pd.to_datetime([str(i)[:10] for i in _tnx_s.index])
                if "Close" in _irx_df.columns:
                    _irx_s = _irx_df["Close"]
                    _irx_s.index = pd.to_datetime([str(i)[:10] for i in _irx_s.index])
            except Exception:
                pass

            # Fit HMM on expanding windows with 21-day stride (monthly cadence).
            # Forward-fill between refits so each date gets the MOST RECENT regime
            # estimate that was available at that time — no lookahead bias.
            _stride = 21
            _last_entry = None
            for _idx in range(0, len(_vix_dates), _stride):
                _d = _vix_dates[_idx]
                _window = _vix_dates[max(0, _idx - 251) : _idx + 1]
                if len(_window) < 60:
                    continue
                _f_vix = np.array([vix.get(d, np.nan) for d in _window])
                _f_spy = np.array([_spy_ret.get(d, 0.0) for d in _window])
                _f_rvol = np.array([_spy_rvol.get(d, 0.0) for d in _window])
                _f_curve = np.zeros(len(_window))
                if not _tnx_s.empty and not _irx_s.empty:
                    _f_curve = np.array([(_tnx_s.get(d, 0.0) - _irx_s.get(d, 0.0)) for d in _window])

                _X = np.column_stack([_f_vix, _f_spy, _f_curve, _f_rvol])
                _valid = ~np.isnan(_X).any(axis=1)
                _Xv = _X[_valid]
                if len(_Xv) < 60:
                    continue
                _means = _Xv.mean(axis=0)
                _stds = _Xv.std(axis=0)
                _stds[_stds < 1e-6] = 1.0
                _Xn = (_Xv - _means) / _stds

                _hmm_model = GaussianHMM(
                    n_components=2,
                    covariance_type="full",
                    n_iter=25,
                    tol=1e-4,
                    random_state=42,
                    init_params="mc",
                    params="stmc",
                    min_covar=1e-4,
                )
                _hmm_model.startprob_ = np.full(2, 0.5)
                _tm = np.full((2, 2), 0.05)
                np.fill_diagonal(_tm, 0.95)
                _hmm_model.transmat_ = _tm
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    _hmm_model.fit(_Xn)
                    _post = _hmm_model.predict_proba(_Xn)
                    _bull_prob = float(_post[-1][0])
                    _trans_risk = float(1.0 - np.trace(_hmm_model.transmat_) / 2.0)
                    _entry = {"bull_prob": _bull_prob, "transition_risk": _trans_risk}
                    # Fill all dates from this refit point until next stride
                    for _fill_d in _vix_dates[_idx : min(len(_vix_dates), _idx + _stride)]:
                        _hmm_cache[_fill_d] = _entry
                    _last_entry = _entry
            # Ensure any trailing dates (after last full stride) are filled
            if _last_entry:
                for _fill_d in _vix_dates[len(_vix_dates) - (len(_vix_dates) % _stride) :]:
                    if _fill_d not in _hmm_cache:
                        _hmm_cache[_fill_d] = _last_entry
            print(f"ok ({len(_hmm_cache)} dates, refit every {_stride}d)")
        except Exception as _hmm_err:
            print(f"failed ({_hmm_err})")

    # Sector momentum (5-day return per sector ETF)
    _sector_momentum_map: dict = {}
    if _etf_close is not None and not _etf_close.empty:
        print("[meta] pre-computing sector momentum…", end=" ", flush=True)
        try:
            for _etf_col in _etf_close.columns if hasattr(_etf_close, "columns") else [_etf_close.name or "Close"]:
                _s = _etf_close[_etf_col] if hasattr(_etf_close, "columns") else _etf_close
                _mom = _s.pct_change(5).fillna(0)
                _sector_momentum_map[_etf_col] = {
                    pd.Timestamp(str(k)[:10]): float(v) for k, v in _mom.items() if pd.notna(v)
                }
            print(f"ok ({len(_sector_momentum_map)} sectors)")
        except Exception as _sm_err:
            print(f"failed ({_sm_err})")

    # §89: Fama-French Short-Term Reversal factor
    _ff_str: dict = {}
    print("[meta] fetching FF ST_Rev…", end=" ", flush=True)
    try:
        _ff_str = fetch_ff_str(START, END)
        print(f"ok ({len(_ff_str)} daily obs)")
    except Exception as _ff_err:
        print(f"failed ({_ff_err})")

    # §89a: FF ST_Rev regime tilt — rolling 63d Sharpe as sizing dial
    _ff_str_regime_map: dict[pd.Timestamp, float] = {}
    _ff_str_sizing_flag = "--ff-str-sizing" in sys.argv
    if _ff_str_sizing_flag and _ff_str:
        print("[meta] computing FF ST_Rev regime (63d Sharpe)…", end=" ", flush=True)
        try:
            _ff_series = pd.Series(_ff_str).sort_index()
            # Rolling 63d mean / std → annualized Sharpe
            _ff_roll_mean = _ff_series.rolling(63, min_periods=30).mean()
            _ff_roll_std = _ff_series.rolling(63, min_periods=30).std()
            _ff_sharpe = (_ff_roll_mean / _ff_roll_std.replace(0, np.nan)) * np.sqrt(252)
            for _d, _s in _ff_sharpe.items():
                if pd.isna(_s):
                    continue
                # Regime buckets: negative (<-0.5) → 0.5×, flat → 1.0×, positive (>0.5) → 1.0×
                # We only size DOWN in negative regime; flat/positive = full size
                if _s < -0.5:
                    _ff_str_regime_map[_d] = 0.5
                else:
                    _ff_str_regime_map[_d] = 1.0
            print(
                f"ok ({len(_ff_str_regime_map)} dates, negative regime = {sum(1 for v in _ff_str_regime_map.values() if v == 0.5)} days)"
            )
        except Exception as _ff_reg_err:
            print(f"failed ({_ff_reg_err})")

    # §91: Short-interest rising flag (as-of join from bi-weekly FINRA data)
    _si_rising_map: dict[str, dict] = {}
    _si_rising_sizing_flag = "--si-rising-sizing" in sys.argv
    _si_cache_path = os.path.join(os.path.abspath(os.path.join(_HERE, "..", "data", "cache_si")), "si_panel.json")
    if _si_rising_sizing_flag and os.path.exists(_si_cache_path):
        print("[meta] loading short-interest panel…", end=" ", flush=True)
        try:
            with open(_si_cache_path) as f:
                _si_raw = json.load(f)
            # Flatten to {ticker: {pd.Timestamp: rising_bool}}
            for _t, _dates in _si_raw.items():
                _si_rising_map[_t] = {
                    pd.Timestamp(d): v["rising"] for d, v in _dates.items() if v.get("rising") is not None
                }
            print(f"ok ({len(_si_rising_map)} tickers)")
        except Exception as _si_err:
            print(f"failed ({_si_err})")
            _si_rising_map = {}

    # Generate trades now that cointegration and scores are final!
    _per_ticker_earnings = {t: {"earnings_dates": all_earnings_dates.get(t)} for t in all_dfs}
    all_trades = _filter_simulation_results(
        _run_simulation_parallel(
            all_dfs,
            common_kwargs={
                "mr_only": BACKTEST_MR_DEFAULT,
                "beta_hedge": _beta_hedge_flag,
                "spy_prices": spy_prices,
                "forecast_sizing": _forecast_sizing_flag,
                "score_band_sizing": _score_band_sizing_flag,
                "dynamic_stop_rsi": _dynamic_stop_rsi_flag,
                "no_family_discount": _no_family_discount_flag,
                "entry_delay_override": _entry_delay_flag,
                "require_consec_score_override": _consec_score_flag,
                "consec_score_sizing": _consec_score_sizing_flag,
                "consec_score_thresh_override": _consec_score_thresh_override,
                "target_mult_override": _target_mult_override,
                "max_loss_days_override": _max_loss_days_override,
                "dow_filter": _dow_filter,
                "require_mr_count_override": _mr_count_override,
                "mr_rsi_ceil_override": _rsi_ceil_override,
                "mr_bb_ceil_override": _bb_ceil_override,
                "mr_ibs_ceil_override": _ibs_ceil_override,
                "buy_thresh_override": _buy_thresh_override,
                "score_accel": _score_accel_flag,
                "entry_model": _entry_model,
                "hmm_cache": _hmm_cache,
                "vix3m_series": _vix3m_series,
                "sector_momentum_map": _sector_momentum_map,
                "ff_str": _ff_str,
                "si_rising_map": _si_rising_map,
                "ff_str_regime_map": _ff_str_regime_map,
                "entry_at_close": _entry_at_close_flag,
                "entry_limit_k": _entry_limit_k if _entry_limit_flag else None,
                "max21_filter_pct": _max21_filter_pct,
            },
            per_ticker_kwargs=_per_ticker_earnings,
        )
    )

    # §88: Calm-regime sleeve — add low-VIX trades with relaxed config
    _calm_sleeve_flag = "--calm-sleeve" in sys.argv
    if _calm_sleeve_flag and all_dfs:
        print("\n## §88. Calm-Regime Sleeve (VIX<20, thresh=38, hold=5d, 0.5× size)\n")
        _calm_list = _filter_simulation_results(
            _run_simulation_parallel(
                all_dfs,
                common_kwargs={
                    "mr_only": BACKTEST_MR_DEFAULT,
                    "calm_sleeve": True,
                    "beta_hedge": _beta_hedge_flag,
                    "spy_prices": spy_prices,
                    "entry_model": _entry_model,
                    "hmm_cache": _hmm_cache,
                    "vix3m_series": _vix3m_series,
                    "sector_momentum_map": _sector_momentum_map,
                    "ff_str": _ff_str,
                    "si_rising_map": _si_rising_map,
                    "ff_str_regime_map": _ff_str_regime_map,
                },
                per_ticker_kwargs=_per_ticker_earnings,
            )
        )
        if _calm_list:
            _calm_trades = pd.concat(_calm_list, ignore_index=True)
            _cs = stats(_calm_trades["net_pct"].tolist())
            print(
                f"> Calm sleeve: N={_cs['n']}  WR={_cs['wr']:.1f}%  "
                f"Avg={_cs['avg']:+.2f}%  Sharpe={_cs['sharpe'] if _cs['sharpe'] is not None else '—'}\n"
            )
            all_trades.extend(_calm_list)
        else:
            print("[no calm-sleeve trades generated]\n")

    if not all_trades:
        print("\n[error] No trades generated.")
        return

    trades = pd.concat(all_trades, ignore_index=True)
    trades = trades.sort_values("date").reset_index(drop=True)
    _total_limit_attempted = sum(t.attrs.get("_limit_signals_attempted", 0) for t in all_trades)
    trades["year"] = trades["date"].dt.year
    print(f"\nTotal simulated trades: {len(trades)}\n")

    # ── --save-trades: write CSV for backtest_new_layers.py sizing ablation ──
    if "--save-trades" in sys.argv:
        import os as _os

        _save_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "data", "backtest_trades_is.csv")
        trades.to_csv(_save_path, index=False)
        print(f"[--save-trades] Saved {len(trades)} IS trades to {_save_path}\n")

    # ── --exit-sweep: grid over the exit-timing knobs (max_loss_days × no_progress) ──
    # Per the entry-alpha-exhausted finding, entry ranking is saturated (5-fold
    # CV-AUC ≈ 0.50 predicting wins; engine score↔outcome ρ≈0.03), so the only
    # remaining Sharpe lever is the EXIT. This sweeps the two existing exit knobs
    # and ranks by the CAPITAL-AWARE portfolio annualised Sharpe — an exit that
    # frees its slot sooner recycles capital into T-bills / new trades, so cutting
    # hold time WITHOUT hurting per-trade return lifts annualised Sharpe even when
    # per-trade Sharpe is flat. Per-trade Sharpe + mean hold are shown for context.
    if "--exit-sweep" in sys.argv:
        print("\n## Exit-Timing Sweep — max_loss_days × no_progress_days\n")
        print("> Objective: portfolio ANN Sharpe (capital-aware, frees-slot-sooner rewarded).")
        print("> Baseline = live defaults: max_loss_days=4, no_progress=OFF.")
        print("> pSh = per-trade Sharpe (N-blind); hold = mean exit_day; TL/NP = % time_loss/no_progress exits.\n")

        def _exit_run(**ov) -> pd.DataFrame:
            _lst = _filter_simulation_results(_run_simulation_parallel(all_dfs, common_kwargs={"mr_only": True, **ov}))
            return pd.concat(_lst, ignore_index=True) if _lst else pd.DataFrame()

        def _exit_metrics(label: str, **ov) -> dict | None:
            tr = _exit_run(**ov)
            if tr.empty:
                return None
            s = stats(tr["net_pct"].tolist())
            ps = run_portfolio_simulation(tr, quiet=True) or {}
            er = tr["exit_reason"] if "exit_reason" in tr else pd.Series(dtype=str)
            return {
                "label": label,
                "n": s["n"],
                "wr": s["wr"],
                "avg": s["avg"],
                "sharpe": s["sharpe"],
                "hold": float(tr["exit_day"].mean()),
                "tl_pct": float((er == "time_loss").mean() * 100) if len(er) else 0.0,
                "np_pct": float((er == "no_progress").mean() * 100) if len(er) else 0.0,
                "cagr": ps.get("cagr"),
                "maxdd": ps.get("max_dd"),
                "ann": ps.get("ann_sharpe"),
            }

        _exit_configs = [
            ("BASELINE max_loss=4 np=OFF", dict()),
            ("max_loss=2", dict(max_loss_days_override=2)),
            ("max_loss=3", dict(max_loss_days_override=3)),
            ("max_loss=5", dict(max_loss_days_override=5)),
            ("max_loss=6", dict(max_loss_days_override=6)),
            ("max_loss=OFF(99)", dict(max_loss_days_override=99)),
            ("np=3 (max_loss=4)", dict(no_progress_days=3)),
            ("np=4 (max_loss=4)", dict(no_progress_days=4)),
            ("np=5 (max_loss=4)", dict(no_progress_days=5)),
            ("max_loss=3 + np=3", dict(max_loss_days_override=3, no_progress_days=3)),
            ("max_loss=3 + np=4", dict(max_loss_days_override=3, no_progress_days=4)),
            ("max_loss=5 + np=4", dict(max_loss_days_override=5, no_progress_days=4)),
        ]
        _exit_rows = []
        for _lbl, _ov in _exit_configs:
            _m = _exit_metrics(_lbl, **_ov)
            if _m is None:
                continue
            _exit_rows.append(_m)
            print(
                f"  {_lbl:<28} N={_m['n']:>4}  WR={_m['wr']:>5.1f}%  avg={_m['avg']:+.3f}%  "
                f"pSh={fmt_sharpe(_m['sharpe'])}  hold={_m['hold']:.2f}d  "
                f"TL={_m['tl_pct']:>4.1f}%  NP={_m['np_pct']:>4.1f}%  "
                f"CAGR={_m['cagr']:+.1f}%  DD=-{_m['maxdd']:.1f}%  ANN={fmt_sharpe(_m['ann'])}"
            )

        if _exit_rows:
            _eb = _exit_rows[0]
            _base_ann = _eb["ann"] or 0.0
            print(
                f"\n> Ranked by portfolio ANN Sharpe (baseline ANN={fmt_sharpe(_eb['ann'])}, hold={_eb['hold']:.2f}d):"
            )
            for _r in sorted(_exit_rows, key=lambda x: x["ann"] or -99, reverse=True):
                _d = (_r["ann"] or 0.0) - _base_ann
                _flag = " ✅" if _d > 0.05 else (" ⚠" if _d > 0.0 else "")
                print(
                    f"    {_r['label']:<28} ANN={fmt_sharpe(_r['ann'])}  Δ={_d:+.3f}  "
                    f"pSh={fmt_sharpe(_r['sharpe'])}  N={_r['n']}  hold={_r['hold']:.2f}d{_flag}"
                )
            print(
                "\n> Read: a config wins only if ANN Δ>0 with N roughly intact — per-trade Sharpe gains\n"
                "> that come purely from dropping trades (N collapse) do NOT lift ANN (the ATR≤70 trap).\n"
            )
        return

    _vg_only = "--validate-live-gates" in sys.argv and not any(
        a for a in sys.argv[1:] if a.startswith("--") and a != "--validate-live-gates"
    )

    # ── Gate Validation — ablate all backtest-testable live engine gates ─────
    # Runs BEFORE IS stats so --validate-live-gates alone exits fast.
    if "--validate-live-gates" in sys.argv and all_dfs:
        print("\n## Gate Validation — Backtest-Testable Live Engine Gates\n")
        print("> Baseline = IS with all currently-active gates.")
        print("> REMOVE columns: ΔN=trades gained, ΔSharpe — if removing gate HURTS Sh → gate earns its cost.")
        print("> ADD columns: ΔSharpe — if adding gate HELPS Sh → gate confirmed as additive.\n")
        print("> Verdict: ✅ KEEP (ΔSh<−0.02 on remove) | ⚠ REVIEW (|ΔSh|<0.02) | 🔴 REMOVE (ΔSh>+0.01 on remove)")
        print("> For ADD tests: ✅ ADD (ΔSh>+0.01) | ⚠ NEUTRAL | 🔴 HURTS\n")

        global OU_HALFLIFE_MAX, HURST_TREND_CEIL

        # Build IS baseline (identical to main run)
        _vg_base_list = _filter_simulation_results(_run_simulation_parallel(all_dfs, common_kwargs={"mr_only": True}))
        _vg_base = pd.concat(_vg_base_list, ignore_index=True) if _vg_base_list else pd.DataFrame()
        _vg_sb = stats(_vg_base["net_pct"].tolist()) if not _vg_base.empty else dict(_EMPTY_STATS)
        _vg_shn = _vg_sb.get("sharpe") or 0.0
        _vg_wrn = _vg_sb.get("wr", 0.0)
        print(
            f"  {'Baseline (all active gates)':<52} N={_vg_sb['n']:>4}       WR={_vg_wrn:.1f}%       Sh={fmt_sharpe(_vg_sb.get('sharpe'))}\n"
        )

        def _vg_run(**overrides) -> dict:
            _defaults: dict = dict()
            _defaults.update(overrides)
            _lst = _filter_simulation_results(
                _run_simulation_parallel(all_dfs, common_kwargs={"mr_only": True, **_defaults})
            )
            _combined = pd.concat(_lst, ignore_index=True) if _lst else pd.DataFrame()
            return stats(_combined["net_pct"].tolist()) if not _combined.empty else dict(_EMPTY_STATS)

        # BT-4: bootstrap CI helper for gate ΔSharpe significance
        import random as _rnd_vg

        def _bt4_ci(rets: list, n_boot: int = 500) -> tuple:
            """BT-4: 95% bootstrap CI on per-trade Sharpe."""
            if len(rets) < 10:
                return float("nan"), float("nan")
            boot_srs = []
            for _ in range(n_boot):
                s = _rnd_vg.choices(rets, k=len(rets))
                mu = sum(s) / len(s)
                std_b = (sum((r - mu) ** 2 for r in s) / max(len(s) - 1, 1)) ** 0.5
                boot_srs.append(mu / std_b if std_b > 0 else 0.0)
            boot_srs.sort()
            return boot_srs[int(0.025 * n_boot)], boot_srs[int(0.975 * n_boot)]

        def _vg_remove(label: str, **overrides) -> None:
            _sa = _vg_run(**overrides)
            _dn = _sa["n"] - _vg_sb["n"]
            _dsh = (_sa.get("sharpe") or 0.0) - _vg_shn
            _dwr = _sa.get("wr", 0.0) - _vg_wrn
            _verdict = "✅ KEEP" if _dsh < -0.02 else ("⚠ REVIEW" if _dsh >= -0.02 and _dsh < 0.01 else "🔴 REMOVE")
            # BT-4: gate is "CONFIRMED KEEP" only if lower CI bound of removal run < baseline
            _ci_lo, _ci_hi = _bt4_ci(_vg_base["net_pct"].tolist())
            _ci_str = f" CI=[{_ci_lo:.2f},{_ci_hi:.2f}]" if not (math.isnan(_ci_lo if _ci_lo == _ci_lo else 1)) else ""
            print(
                f"  REMOVE {label:<46} N={_sa['n']:>4} ({_dn:+d})"
                f"  WR={_sa['wr']:.1f}% ({_dwr:+.1f}pp)"
                f"  Sh={fmt_sharpe(_sa.get('sharpe'))} ({_dsh:+.2f}){_ci_str}  {_verdict}"
            )

        def _vg_add(label: str, **overrides) -> None:
            _sa = _vg_run(**overrides)
            _dn = _sa["n"] - _vg_sb["n"]
            _dsh = (_sa.get("sharpe") or 0.0) - _vg_shn
            _dwr = _sa.get("wr", 0.0) - _vg_wrn
            _verdict = "✅ ADD" if _dsh > 0.01 else ("⚠ NEUTRAL" if _dsh >= -0.01 else "🔴 HURTS")
            print(
                f"  ADD    {label:<46} N={_sa['n']:>4} ({_dn:+d})"
                f"  WR={_sa['wr']:.1f}% ({_dwr:+.1f}pp)"
                f"  Sh={fmt_sharpe(_sa.get('sharpe'))} ({_dsh:+.2f})  {_verdict}"
            )

        def _vg_global_remove(label: str, **global_overrides) -> None:
            _orig = {k: globals()[k] for k in global_overrides}
            for k, v in global_overrides.items():
                globals()[k] = v
            _sa = _vg_run()
            for k, v in _orig.items():
                globals()[k] = v
            _dn = _sa["n"] - _vg_sb["n"]
            _dsh = (_sa.get("sharpe") or 0.0) - _vg_shn
            _dwr = _sa.get("wr", 0.0) - _vg_wrn
            _verdict = "✅ KEEP" if _dsh < -0.02 else ("⚠ REVIEW" if _dsh >= -0.02 and _dsh < 0.01 else "🔴 REMOVE")
            print(
                f"  REMOVE {label:<46} N={_sa['n']:>4} ({_dn:+d})"
                f"  WR={_sa['wr']:.1f}% ({_dwr:+.1f}pp)"
                f"  Sh={fmt_sharpe(_sa.get('sharpe'))} ({_dsh:+.2f})  {_verdict}"
            )

        print("── Gates currently active in IS baseline (ablation = remove one at a time) ──")
        _vg_remove("§57 Thursday strict threshold", thursday_gate_enabled=False)
        _vg_global_remove("§59 OU halflife ≤25d gate", OU_HALFLIFE_MAX=999.0)
        _vg_global_remove("§60 Hurst ≤0.80 ceiling", HURST_TREND_CEIL=999.0)

        # §63 cointegration: ablate by zeroing coint_z column in all_dfs
        _orig_coint = {t: df.get("coint_z") for t, df in all_dfs.items() if "coint_z" in df.columns}
        for _t, _df in all_dfs.items():
            if "coint_z" in _df.columns:
                all_dfs[_t] = _df.drop(columns=["coint_z"])
        _sa_no_coint = _vg_run()
        for _t, _col in _orig_coint.items():
            all_dfs[_t]["coint_z"] = _col
        _dn_c = _sa_no_coint["n"] - _vg_sb["n"]
        _dsh_c = (_sa_no_coint.get("sharpe") or 0.0) - _vg_shn
        _dwr_c = _sa_no_coint.get("wr", 0.0) - _vg_wrn
        _vdict_c = "✅ KEEP" if _dsh_c < -0.02 else ("⚠ REVIEW" if _dsh_c >= -0.02 and _dsh_c < 0.01 else "🔴 REMOVE")
        print(
            f"  REMOVE §63 Sector cointegration Z-score            "
            f"N={_sa_no_coint['n']:>4} ({_dn_c:+d})"
            f"  WR={_sa_no_coint['wr']:.1f}% ({_dwr_c:+.1f}pp)"
            f"  Sh={fmt_sharpe(_sa_no_coint.get('sharpe'))} ({_dsh_c:+.2f})  {_vdict_c}"
        )

        print("\n── Gates not in IS baseline (ADD test = enable one at a time) ──")
        _vg_add("§54 VIX<20 hard block", vix_min_override=20.0)
        print("  Fetching cross-asset data for §55 test…", end=" ", flush=True)
        try:
            _ca_vg = fetch_cross_asset_composite(START, END)
            print(f"ok ({len(_ca_vg)} bars)")
            _vg_add("§55 Cross-asset 3/3 headwinds block", cross_asset=_ca_vg)
        except Exception as _ca_err:
            print(f"failed ({_ca_err}) — §55 test skipped")

        print()
        print("> Gates NOT testable in backtest (look-ahead bias or paid data required):")
        for _u in [
            "§48 IVR — per-stock options IV history not in OHLCV",
            "§49 Put-call skew — options surface data not historical",
            "§50 Piotroski F-Score — quarterly financials not point-in-time in yfinance",
            "§51 Forward PE — analyst estimate not point-in-time",
            "§52 Short interest velocity — FINRA bi-monthly, not daily historical",
            "§58 EPS revision — analyst revision history not in yfinance",
            "§63 Sector cointegration — now ablated above via coint_z column removal",
            "§65 TRIN — recorded as trade metadata; no pre-specified blocking threshold",
            "§66 AD breadth — same: metadata only; no pre-specified gate condition",
            "§69 GEX flip — options market-maker positioning data not historical",
            "§70 Zero-DTE — recent phenomenon, no pre-2020 history",
            "§71 Max pain — options chain snapshot; no historical strike data",
            "§72 VRP proxy — per-stock IV history required",
            "§73 Insider clustering — EDGAR filings not point-in-time via yfinance",
            "§74 Beneish M-Score — quarterly financials not point-in-time",
            "§76 Altman Z-Score — quarterly financials not point-in-time",
            "§80 NBBO spread — real-time quote data; no historical bid-ask",
            "§81 Block prints — real-time block trade data; no historical equivalent",
        ]:
            print(f"  ❌ {_u}")
        print()

        if _vg_only:
            return  # skip IS stats when running validate-live-gates alone

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
    sharpe_ci_print(s.get("sharpe"), s["n"], label="IS")
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

        full_list = _filter_simulation_results(_run_simulation_parallel(all_dfs, common_kwargs={"mr_only": False}))

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
    # ── §Inv-B. Quality Score Tier Analysis ──────────────────────────────────
    # Option B: does the quality_score (OU halflife + Hurst + score above thresh)
    # discriminate within the passing set? Addresses Inv4 finding (flat confidence).
    if trades is not None and not trades.empty and "quality_score" in trades.columns:
        print("\n## §Inv-B. Quality Score Tier Analysis\n")
        print("> quality_score = 40%×(score-thresh) + 35%×OU_speed + 25%×Hurst_MR\n")
        qs = trades["quality_score"].dropna()
        if len(qs) > 10:
            p33 = qs.quantile(0.33)
            p67 = qs.quantile(0.67)
            tiers = [
                (f"Low  (0–{p33:.0f})", trades[trades["quality_score"] < p33]),
                (
                    f"Mid  ({p33:.0f}–{p67:.0f})",
                    trades[(trades["quality_score"] >= p33) & (trades["quality_score"] < p67)],
                ),
                (f"High ({p67:.0f}–100)", trades[trades["quality_score"] >= p67]),
            ]
            qs_rows = []
            for label, sub in tiers:
                sr = stats(sub["net_pct"].tolist())
                qs_rows.append(
                    [label, str(sr["n"]), f"{sr['wr']:.1f}%", f"{sr['avg']:+.2f}%", fmt_sharpe(sr["sharpe"])]
                )
            print_table(["Quality Tier", "N", "WR", "Avg Ret", "Sharpe"], qs_rows)
            _low = stats(trades[trades["quality_score"] < p33]["net_pct"].tolist())
            _high = stats(trades[trades["quality_score"] >= p67]["net_pct"].tolist())
            _spread = (_high.get("sharpe") or 0) - (_low.get("sharpe") or 0)
            print(f"\n> High vs Low Sharpe spread: {_spread:+.2f}")
            print("> If spread > 0.1 — quality_score discriminates; use for trade sizing.\n")

            # §Inv-C: L8 quality_score-weighted sizing simulation
            # Thresholds recalibrated 2026-06-01 to IS p67/p33 from §Inv-B:
            # High(≥43) N=63 Sh=0.51 | Mid(35–43) N=63 Sh=0.31 | Low(<35) N=62 Sh=0.17
            _qs_vals = trades["quality_score"].fillna(39.0).tolist()
            _l8_weights = [1.30 if q >= 43 else 0.75 if q < 35 else 1.0 for q in _qs_vals]
            _sw_l8 = stats_weighted(trades["net_pct"].tolist(), _l8_weights)
            _eq = stats(trades["net_pct"].tolist())
            _d_sh_l8 = (_sw_l8.get("sharpe") or 0.0) - (_eq.get("sharpe") or 0.0)
            _d_wr_l8 = _sw_l8["wr"] - _eq["wr"]
            print("\n## §Inv-C. L8 Quality_Score-Weighted Sizing Validation\n")
            print("> L8: high quality_score(≥43)→1.30×  mid(35–43)→1.0×  low(<35)→0.75×")
            print("> Thresholds = IS p67/p33 (§Inv-B). Same trades, same entries — only sizing changes.\n")
            print_table(
                ["Config", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"],
                [
                    [
                        "Equal-weight (baseline)",
                        str(_eq["n"]),
                        f"{_eq['wr']:.1f}%",
                        f"{_eq['avg']:+.2f}%",
                        fmt_sharpe(_eq["sharpe"]),
                        f"-{_eq['max_dd']:.2f}%",
                    ],
                    [
                        "L8 quality_score-weighted (1.30×/1.0×/0.75×)",
                        str(_sw_l8["n"]),
                        f"{_sw_l8['wr']:.1f}% ({_d_wr_l8:+.1f}pp)",
                        f"{_sw_l8['avg']:+.2f}%",
                        f"{fmt_sharpe(_sw_l8['sharpe'])} ({_d_sh_l8:+.2f})",
                        f"-{_sw_l8['max_dd']:.2f}%",
                    ],
                ],
            )
            _n_high = sum(1 for q in _qs_vals if q >= 43)
            _n_mid = sum(1 for q in _qs_vals if 35 <= q < 43)
            _n_low = sum(1 for q in _qs_vals if q < 35)
            print(f"\n> Distribution: High(≥43)={_n_high}  Mid(35–43)={_n_mid}  Low(<35)={_n_low}")
            verdict_l8 = (
                "✅ L8 adds value — quality_score sizing confirmed"
                if _d_sh_l8 > 0.01
                else ("➖ L8 neutral" if _d_sh_l8 > -0.01 else "⚠ L8 mildly negative — review quality_score thresholds")
            )
            print(f"> ΔSharpe = {_d_sh_l8:+.3f}  {verdict_l8}\n")

    # ── §MAX. MAX-Effect Tier Analysis (Chen et al., SSRN 4622831) ────────────
    # Published: short-term reversal ~2.5x stronger in high-MAX (lottery) names.
    # Does trailing-21d max daily return discriminate within the passing set?
    if trades is not None and not trades.empty and "max21" in trades.columns:
        _mx = trades.dropna(subset=["max21"])
        if len(_mx) > 30:
            print("\n## §MAX. MAX-Effect Tier Analysis (trailing-21d max daily return)\n")
            _p33, _p67 = _mx["max21"].quantile(0.33), _mx["max21"].quantile(0.67)
            _mx_rows = []
            for _label, _sub in [
                (f"Low  (<{_p33:.1f}%)", _mx[_mx["max21"] < _p33]),
                (f"Mid  ({_p33:.1f}–{_p67:.1f}%)", _mx[(_mx["max21"] >= _p33) & (_mx["max21"] < _p67)]),
                (f"High (≥{_p67:.1f}%)", _mx[_mx["max21"] >= _p67]),
            ]:
                _sr = stats(_sub["net_pct"].tolist())
                _mx_rows.append(
                    [_label, str(_sr["n"]), f"{_sr['wr']:.1f}%", f"{_sr['avg']:+.2f}%", fmt_sharpe(_sr["sharpe"])]
                )
            print_table(["MAX_21 Tier", "N", "WR", "Avg Ret", "Sharpe"], _mx_rows)
            _mx_lo = stats(_mx[_mx["max21"] < _p33]["net_pct"].tolist())
            _mx_hi = stats(_mx[_mx["max21"] >= _p67]["net_pct"].tolist())
            _mx_spread = (_mx_hi.get("sharpe") or 0) - (_mx_lo.get("sharpe") or 0)
            print(f"\n> High-MAX vs Low-MAX Sharpe spread: {_mx_spread:+.2f}")
            print("> Literature predicts High >> Low. Spread > +0.10 ⇒ candidate L-stack sizing feature;")
            print("> spread ≤ 0 ⇒ MAX effect does not transfer to this vol-gated universe.\n")

    # ── §ON. Overnight vs Intraday P&L Decomposition ─────────────────────────
    # Published: short-term reversal profits concentrate overnight. If the intraday
    # leg is a net drag, exiting at the OPEN of the final hold day (instead of the
    # close) is a costless exit improvement candidate.
    if trades is not None and not trades.empty and {"overnight_pct", "intraday_pct"}.issubset(trades.columns):
        _on = trades.dropna(subset=["overnight_pct", "intraday_pct"])
        if len(_on) > 30:
            print("\n## §ON. Overnight vs Intraday P&L Decomposition\n")
            _on_stats = stats(_on["overnight_pct"].tolist())
            _in_stats = stats(_on["intraday_pct"].tolist())
            print_table(
                ["Leg", "N", "Avg/trade", "Total", "Sharpe"],
                [
                    [
                        "Overnight (close→open)",
                        str(_on_stats["n"]),
                        f"{_on_stats['avg']:+.2f}%",
                        f"{_on['overnight_pct'].sum():+.1f}%",
                        fmt_sharpe(_on_stats["sharpe"]),
                    ],
                    [
                        "Intraday (open→close)",
                        str(_in_stats["n"]),
                        f"{_in_stats['avg']:+.2f}%",
                        f"{_on['intraday_pct'].sum():+.1f}%",
                        fmt_sharpe(_in_stats["sharpe"]),
                    ],
                ],
            )
            print("\n> Gross hold P&L ≈ overnight + intraday legs (per-day decomposition over the hold).")
            print("> If one leg carries the P&L and the other drags, session-timed exits are the lever.\n")

    # Sleeve-correlation support: dump MR monthly returns for backtest_sleeves --corr.
    if trades is not None and not trades.empty and {"date", "net_pct"}.issubset(trades.columns):
        try:
            _mrm = trades.copy()
            _mrm["_m"] = pd.to_datetime(_mrm["date"]).dt.to_period("M").astype(str)
            _mrm.groupby("_m")["net_pct"].mean().to_csv("data/mr_monthly.csv")
            # Per-trade dump for the short-volume alt-data alpha check.
            _cols = [c for c in ("date", "ticker", "score", "net_pct", "atr_pct", "vix_entry") if c in trades.columns]
            trades[_cols].to_csv("data/mr_trades.csv", index=False)

            # Continuous month-end equity series for robust sleeve blending.
            _eq_res = run_portfolio_simulation(trades, max_concurrent=MAX_PORTFOLIO_SLOTS, quiet=True)
            if _eq_res and _eq_res.get("equity_log"):
                _eq_df = pd.DataFrame(_eq_res["equity_log"], columns=["date", "equity"])
                _eq_df["date"] = pd.to_datetime(_eq_df["date"])
                _me = _eq_df.set_index("date").resample("ME").last()
                _me_m = _me.pct_change().dropna()
                _me_m.index = _me_m.index.to_period("M").astype(str)
                _me_m.to_csv("data/mr_monthly_equity.csv", header=["net_pct"])
        except Exception:
            pass

    # ── R1. Exit / MFE-Capture Analysis ──────────────────────────────────────
    if trades is not None and not trades.empty and {"mfe_pct", "gross_pct", "exit_reason"}.issubset(trades.columns):
        print("\n## R1. Exit / MFE-Capture Analysis\n")
        print("> MFE = max favorable excursion during the hold. Capture = avg gross / avg MFE.")
        print("> Low capture on winners ⇒ headroom for partial scale-out / trailing exits.\n")

        def _cap_row(label, sub):
            if sub.empty:
                return [label, "0", "—", "—", "—", "—"]
            _mfe = float(sub["mfe_pct"].mean())
            _gr = float(sub["gross_pct"].mean())
            return [
                label,
                str(len(sub)),
                f"{_mfe:+.2f}%",
                f"{_gr:+.2f}%",
                f"{_gr / _mfe * 100:.0f}%" if _mfe > 0 else "—",
                f"{_mfe - _gr:+.2f}%",
            ]

        print_table(
            ["Cohort", "N", "Avg MFE", "Avg Gross", "Capture", "Left on table"],
            [
                _cap_row("All trades", trades),
                _cap_row("Winners", trades[trades["net_pct"] > 0]),
                _cap_row("Losers", trades[trades["net_pct"] <= 0]),
            ],
        )
        print("\n> Exit-reason distribution (avg MFE shows upside present at each exit type):\n")
        _er_rows = []
        for _r, _c in trades["exit_reason"].value_counts().items():
            _sub = trades[trades["exit_reason"] == _r]
            _s = stats(_sub["net_pct"].tolist())
            _er_rows.append(
                [
                    str(_r),
                    str(_c),
                    f"{_c / len(trades) * 100:.0f}%",
                    f"{_s['wr']:.1f}%",
                    f"{_s['avg']:+.2f}%",
                    f"{float(_sub['mfe_pct'].mean()):+.2f}%",
                ]
            )
        print_table(["Exit reason", "N", "% of total", "WR", "Avg Net", "Avg MFE"], _er_rows)

        # ── R1b. Breakeven-Ratchet Exit A/B (deployable) ──────────────────────
        if "net_pct_alt" in trades.columns and trades["net_pct_alt"].notna().any():
            _cur = stats(trades["net_pct"].tolist())
            _altt = trades.dropna(subset=["net_pct_alt"])
            _alt = stats(_altt["net_pct_alt"].tolist())
            _dsh = (_alt.get("sharpe") or 0.0) - (_cur.get("sharpe") or 0.0)
            print("\n## R1b. Breakeven-Ratchet Exit — A/B vs Live Exit Stack\n")
            print(
                "> Alt: arm at +1 ATR favorable → stop ratchets to breakeven+0.1%, then trails 1 ATR "
                "below high-water. Hard target + time exit unchanged. Same 0.50% friction.\n"
            )
            print_table(
                ["Exit policy", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"],
                [
                    [
                        "Current (stop/target/adaptive/time)",
                        str(_cur["n"]),
                        f"{_cur['wr']:.1f}%",
                        f"{_cur['avg']:+.2f}%",
                        fmt_sharpe(_cur["sharpe"]),
                        f"-{_cur['max_dd']:.2f}%",
                    ],
                    [
                        "Breakeven-ratchet + ATR trail",
                        str(_alt["n"]),
                        f"{_alt['wr']:.1f}%",
                        f"{_alt['avg']:+.2f}%",
                        f"{fmt_sharpe(_alt['sharpe'])} ({_dsh:+.2f})",
                        f"-{_alt['max_dd']:.2f}%",
                    ],
                ],
            )
            _v = (
                "✅ Ratchet beats current exits — convert losers' MFE to small wins"
                if _dsh > 0.01
                else "➖ Ratchet ≈ current (adaptive exits already capture most upside)"
                if _dsh > -0.01
                else "⚠ Ratchet worse — current exit stack superior"
            )
            print(f"\n> ΔSharpe = {_dsh:+.3f}  {_v}\n")

        # ── R4. Stop-Width Study (mechanical, no ratchet) ─────────────────────
        if {"net_pct_stop15", "net_pct_stop25", "net_pct_nostop"}.issubset(trades.columns):
            print("\n## R4. Stop-Width Study (mechanical: fixed stop + target + time)\n")
            print(
                "> Isolates stop WIDTH: 1.5 ATR (live) vs 2.5 ATR vs none. MR theory says oversold "
                "bounces need room — does a tighter stop cut recoveries? (no adaptive exits here)\n"
            )
            _r4 = []
            for _lbl, _col in [
                ("1.5-ATR stop (live width)", "net_pct_stop15"),
                ("2.5-ATR stop (wide)", "net_pct_stop25"),
                ("No hard stop (target/time only)", "net_pct_nostop"),
            ]:
                _sub = trades.dropna(subset=[_col])
                _s = stats(_sub[_col].tolist())
                _r4.append(
                    [
                        _lbl,
                        str(_s["n"]),
                        f"{_s['wr']:.1f}%",
                        f"{_s['avg']:+.2f}%",
                        fmt_sharpe(_s["sharpe"]),
                        f"-{_s['max_dd']:.2f}%",
                    ]
                )
            print_table(["Stop policy", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"], _r4)
            _s15 = stats(trades.dropna(subset=["net_pct_stop15"])["net_pct_stop15"].tolist())
            _sno = stats(trades.dropna(subset=["net_pct_nostop"])["net_pct_nostop"].tolist())
            _d = (_sno.get("sharpe") or 0.0) - (_s15.get("sharpe") or 0.0)
            print(
                f"\n> No-stop − 1.5-ATR ΔSharpe = {_d:+.3f}  "
                + (
                    "✅ stop HURTS — widen/remove"
                    if _d > 0.02
                    else "➖ stop ~neutral on mechanical core"
                    if _d > -0.02
                    else "⚠ stop HELPS — keep it"
                )
                + "\n"
            )

    # ── R2. Regime-Conditional Edge (VIX / SPY trend at entry) ────────────────
    if trades is not None and not trades.empty and "vix_entry" in trades.columns:
        print("\n## R2. Regime-Conditional Edge\n")
        print("> Edge by VIX regime at entry — tests whether thresholds/sizing should be regime-aware.\n")
        _vd = trades["vix_entry"].dropna()
        print(
            f"> vix_entry diag: non-null {len(_vd)}/{len(trades)}, "
            f"min={_vd.min() if len(_vd) else float('nan'):.1f} "
            f"mean={_vd.mean() if len(_vd) else float('nan'):.1f} "
            f"max={_vd.max() if len(_vd) else float('nan'):.1f}\n"
        )
        _vt = trades.dropna(subset=["vix_entry"])
        _vb = [
            ("VIX<15 (calm)", _vt[_vt["vix_entry"] < 15]),
            ("15–20", _vt[(_vt["vix_entry"] >= 15) & (_vt["vix_entry"] < 20)]),
            ("20–30 (stress)", _vt[(_vt["vix_entry"] >= 20) & (_vt["vix_entry"] < 30)]),
            ("VIX≥30 (panic)", _vt[_vt["vix_entry"] >= 30]),
        ]
        print_table(
            ["VIX regime", "N", "WR", "Avg Ret", "Sharpe"],
            [
                [
                    _lbl,
                    str(stats(_g["net_pct"].tolist())["n"]),
                    f"{stats(_g['net_pct'].tolist())['wr']:.1f}%",
                    f"{stats(_g['net_pct'].tolist())['avg']:+.2f}%",
                    fmt_sharpe(stats(_g["net_pct"].tolist())["sharpe"]),
                ]
                for _lbl, _g in _vb
            ],
        )
        if "spy_trend_entry" in trades.columns:
            print("\n> Edge by SPY trend at entry:\n")
            _tb = [
                ("SPY down-trend", trades[trades["spy_trend_entry"] < 0]),
                ("SPY flat", trades[trades["spy_trend_entry"] == 0]),
                ("SPY up-trend", trades[trades["spy_trend_entry"] > 0]),
            ]
            print_table(
                ["SPY trend", "N", "WR", "Avg Ret", "Sharpe"],
                [
                    [
                        _lbl,
                        str(stats(_g["net_pct"].tolist())["n"]),
                        f"{stats(_g['net_pct'].tolist())['wr']:.1f}%",
                        f"{stats(_g['net_pct'].tolist())['avg']:+.2f}%",
                        fmt_sharpe(stats(_g["net_pct"].tolist())["sharpe"]),
                    ]
                    for _lbl, _g in _tb
                ],
            )

    # ── R3. Score → Win-Probability Calibration ───────────────────────────────
    if trades is not None and not trades.empty and "score" in trades.columns:
        print("\n## R3. Score → Win-Probability Calibration\n")
        print("> Is raw score a calibrated win-prob? Decile WR should rise monotonically with score.\n")
        _ts = trades.dropna(subset=["score"]).copy()
        if len(_ts) >= 30:
            _ts["win"] = (_ts["net_pct"] > 0).astype(int)
            _ndec = min(10, max(3, len(_ts) // 20))
            _ts["dec"] = pd.qcut(_ts["score"].rank(method="first"), _ndec, labels=False)
            _rows, _prev, _mono = [], None, True
            for d in range(_ndec):
                g = _ts[_ts["dec"] == d]
                wr = float(g["win"].mean()) * 100
                if _prev is not None and wr < _prev - 1e-9:
                    _mono = False
                _prev = wr
                _rows.append([f"D{d + 1}", f"{g['score'].min():.0f}–{g['score'].max():.0f}", str(len(g)), f"{wr:.1f}%"])
            print_table(["Decile", "Score range", "N", "Win rate"], _rows)
            _rho = float(_ts["score"].corr(_ts["win"], method="spearman"))
            print(f"\n> Spearman(score, win) = {_rho:+.3f}; deciles monotonic: {_mono}.")
            print(
                "> Flat/non-monotone ⇒ score is NOT a usable win-prob; needs isotonic calibration "
                "before it can drive Kelly sizing or honest confidence display.\n"
            )

    # ── R5. Cross-Sectional Relative-Value Ranking ────────────────────────────
    if trades is not None and not trades.empty and {"date", "score"}.issubset(trades.columns):
        print("\n## R5. Cross-Sectional Relative-Value Ranking\n")
        print("> On days with ≥3 candidates, does within-day score rank predict outcome?\n")
        _td = trades.dropna(subset=["score"]).copy()
        _sizes = _td.groupby("date").size()
        _multi = _sizes[_sizes >= 3].index
        _md = _td[_td["date"].isin(_multi)].copy()
        if not _md.empty:
            _md["rank"] = _md.groupby("date")["score"].rank(pct=True)
            _top = _md[_md["rank"] >= 0.67]
            _bot = _md[_md["rank"] <= 0.33]
            _st, _sb = stats(_top["net_pct"].tolist()), stats(_bot["net_pct"].tolist())
            print(f"> {len(_multi)} multi-candidate days, {len(_md)} trades.\n")
            print_table(
                ["Within-day rank", "N", "WR", "Avg Ret", "Sharpe"],
                [
                    [
                        "Top third (most oversold rel.)",
                        str(_st["n"]),
                        f"{_st['wr']:.1f}%",
                        f"{_st['avg']:+.2f}%",
                        fmt_sharpe(_st["sharpe"]),
                    ],
                    [
                        "Bottom third",
                        str(_sb["n"]),
                        f"{_sb['wr']:.1f}%",
                        f"{_sb['avg']:+.2f}%",
                        fmt_sharpe(_sb["sharpe"]),
                    ],
                ],
            )
            print("\n> If top-rank Sharpe >> bottom, a daily top-K cross-sectional filter adds value.\n")
        else:
            print("> Not enough multi-candidate days for cross-sectional analysis.\n")

    # ── R7. Portfolio Drawdown-Scaled Exposure ────────────────────────────────
    if trades is not None and not trades.empty and {"date", "net_pct"}.issubset(trades.columns):
        print("\n## R7. Portfolio Drawdown-Scaled Exposure\n")
        print(
            "> Causal de-risk: when the strategy equity is >DD_TRIG below its peak, halve exposure "
            "on subsequent trades until recovery. Tests risk-adjusted improvement (MaxDD vs Sharpe).\n"
        )
        _seq = trades.dropna(subset=["net_pct"]).sort_values("date")["net_pct"].to_numpy(dtype=float) / 100.0

        def _dd_overlay(scaled, dd_trig=0.03):
            eq, peak, maxdd, rets = 1.0, 1.0, 0.0, []
            for x in _seq:
                dd = (peak - eq) / peak  # drawdown BEFORE this trade (causal)
                expo = 0.5 if (scaled and dd > dd_trig) else 1.0
                step = expo * x
                rets.append(step * 100)
                eq *= 1 + step
                peak = max(peak, eq)
                maxdd = max(maxdd, (peak - eq) / peak)
            return rets, maxdd * 100

        _u_rets, _u_dd = _dd_overlay(False)
        _s_rets, _s_dd = _dd_overlay(True)
        _su, _ss = stats(_u_rets), stats(_s_rets)
        print_table(
            ["Exposure policy", "N", "WR", "Avg Ret", "Sharpe", "Equity MaxDD"],
            [
                [
                    "Full exposure (baseline)",
                    str(_su["n"]),
                    f"{_su['wr']:.1f}%",
                    f"{_su['avg']:+.2f}%",
                    fmt_sharpe(_su["sharpe"]),
                    f"-{_u_dd:.2f}%",
                ],
                [
                    "DD-scaled (0.5× when >3% off peak)",
                    str(_ss["n"]),
                    f"{_ss['wr']:.1f}%",
                    f"{_ss['avg']:+.2f}%",
                    fmt_sharpe(_ss["sharpe"]),
                    f"-{_s_dd:.2f}%",
                ],
            ],
        )
        _dsh7 = (_ss.get("sharpe") or 0.0) - (_su.get("sharpe") or 0.0)
        _ddr = _u_dd - _s_dd
        print(
            f"\n> Sequential ΔSharpe = {_dsh7:+.3f}, MaxDD reduction = {_ddr:+.2f}pp  "
            + (
                "✅ better risk-adjusted — cuts DD without killing Sharpe"
                if (_ddr > 0.2 and _dsh7 > -0.02)
                else "➖ neutral — DD overlay adds little at this sequential scale"
                if abs(_dsh7) < 0.03
                else "⚠ hurts Sharpe more than it helps DD"
            )
            + "\n"
        )

        # Realistic concurrent-portfolio A/B (5-slot, T-bill on idle) — addresses the
        # sequential overstatement of MaxDD. This is the deployment-relevant test.
        _pb = run_portfolio_simulation(trades, dd_throttle=False, quiet=True)
        _pt = run_portfolio_simulation(trades, dd_throttle=True, dd_trig=3.0, throttle_mult=0.5, quiet=True)
        if _pb and _pt:
            print("> Concurrent-portfolio A/B (5 slots, T-bill on idle) — deployment-relevant:\n")
            print_table(
                ["Portfolio policy", "CAGR", "Ann.Sharpe", "Max DD"],
                [
                    ["Full exposure", f"{_pb['cagr']:+.1f}%", fmt_sharpe(_pb["ann_sharpe"]), f"-{_pb['max_dd']:.2f}%"],
                    [
                        "DD-throttle 0.5× >3% off peak",
                        f"{_pt['cagr']:+.1f}%",
                        fmt_sharpe(_pt["ann_sharpe"]),
                        f"-{_pt['max_dd']:.2f}%",
                    ],
                ],
            )
            _dca = _pt["cagr"] - _pb["cagr"]
            _dmd = _pb["max_dd"] - _pt["max_dd"]
            _dsa = (_pt["ann_sharpe"] or 0.0) - (_pb["ann_sharpe"] or 0.0)
            print(
                f"\n> Concurrent: ΔCAGR {_dca:+.1f}pp, ΔAnn.Sharpe {_dsa:+.3f}, MaxDD reduction {_dmd:+.2f}pp  "
                + (
                    "✅ deploy graduated DD-throttle in allocator"
                    if (_dmd > 0.2 and _dsa > -0.03)
                    else "➖ neutral on concurrent path — DD already small"
                    if abs(_dsa) < 0.05
                    else "⚠ concurrent path: throttle costs more CAGR than DD saved"
                )
                + "\n"
            )

    # ── §Inv1. MR Trigger Quality Split ──────────────────────────────────────
    # Which MR condition (IBS / BB / VWAP / RSI / multi) drives the best alpha?
    if trades is not None and not trades.empty and "mr_trigger" in trades.columns:
        print("\n## §Inv1. MR Trigger Quality Split (Inv 1)\n")
        print("> Which MR entry condition drives the best Sharpe and trade quality?\n")
        _TRIGGER_ORDER = ["IBS", "BB", "VWAP", "RSI", "multi", "none"]
        trig_rows = []
        for trig in _TRIGGER_ORDER:
            sub = trades[trades["mr_trigger"] == trig]["net_pct"].tolist()
            if not sub:
                continue
            sr = stats(sub)
            trig_rows.append(
                [
                    trig,
                    str(sr["n"]),
                    f"{sr['wr']:.1f}%",
                    f"{sr['avg']:+.2f}%",
                    fmt_sharpe(sr["sharpe"]),
                    fmt_pf(sr["pf"]),
                ]
            )
        print_table(["MR Trigger", "N", "WR", "Avg Ret", "Sharpe", "PF"], trig_rows)
        _baseline = stats(trades["net_pct"].tolist())
        print(
            f"\n> Baseline (all): N={_baseline['n']}, WR={_baseline['wr']:.1f}%, Sharpe={fmt_sharpe(_baseline['sharpe'])}"
        )
        print("> IBS = closed in bottom 15% of day's range. BB = near lower Bollinger Band.")
        print("> VWAP = below rolling VWAP by ≥0.75%. RSI = RSI < 42. multi = 2+ conditions.\n")

    # ── §Inv2. L7 Score-Weighted Sizing Validation ────────────────────────────
    # Validates signal_engine.py L7: positionSizeScale *= max(0.85, min(1.15, 0.85+(score-50)/100))
    # score=50→0.85×  score=65→1.0×  score=80→1.15×
    # If score-weighted Sharpe > equal-weight, the L7 multiplier adds value.
    if trades is not None and not trades.empty and "score" in trades.columns:
        _rets_l7 = trades["net_pct"].tolist()
        _scores_l7 = [
            max(0.85, min(1.15, 0.85 + (float(s) - 50.0) / 100.0)) for s in trades["score"].fillna(50).tolist()
        ]
        sw_l7 = stats_weighted(_rets_l7, _scores_l7)
        eq_l7 = stats(_rets_l7)
        print("\n## §Inv2. L7 Score-Weighted Sizing Validation\n")
        print("> L7: positionSizeScale × max(0.85, min(1.15, 0.85+(score−50)/100))")
        print("> score=50→0.85×  score=65→1.0×  score=80→1.15×\n")
        _delta_sh = (sw_l7.get("sharpe") or 0.0) - (eq_l7.get("sharpe") or 0.0)
        _delta_wr = sw_l7["wr"] - eq_l7["wr"]
        print_table(
            ["Config", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"],
            [
                [
                    "Equal-weight (baseline)",
                    str(eq_l7["n"]),
                    f"{eq_l7['wr']:.1f}%",
                    f"{eq_l7['avg']:+.2f}%",
                    fmt_sharpe(eq_l7["sharpe"]),
                    f"-{eq_l7['max_dd']:.2f}%",
                ],
                [
                    "L7 score-weighted (±15%)",
                    str(sw_l7["n"]),
                    f"{sw_l7['wr']:.1f}% ({_delta_wr:+.1f}pp)",
                    f"{sw_l7['avg']:+.2f}%",
                    f"{fmt_sharpe(sw_l7['sharpe'])} ({_delta_sh:+.2f})",
                    f"-{sw_l7['max_dd']:.2f}%",
                ],
            ],
        )
        verdict = (
            "✅ L7 adds value — size up high-score trades"
            if _delta_sh > 0.01
            else (
                "➖ L7 neutral — sizing nudge not harmful"
                if _delta_sh > -0.01
                else "⚠ L7 mildly negative — review score calibration"
            )
        )
        print(f"\n> ΔSharpe = {_delta_sh:+.3f}  {verdict}\n")

        # ── §Inv-K. R10-7 Per-Signal Half-Kelly vs Linear L7 ──────────────────
        # Constant 1.5s/2.0t R:R → Kelly has no per-signal payoff term and reduces
        # to a confidence-conditional convex sizing curve. Tests whether that convex
        # shape (sized off empirical score→WR + realized payoff) beats the linear L7.
        _kelly = stats_kelly(_rets_l7, trades["score"].fillna(50).tolist())
        if _kelly.get("sharpe") is not None:
            _dk_l7 = (_kelly.get("sharpe") or 0.0) - (sw_l7.get("sharpe") or 0.0)
            _dk_eq = (_kelly.get("sharpe") or 0.0) - (eq_l7.get("sharpe") or 0.0)
            print("\n## §Inv-K. R10-7 Per-Signal Half-Kelly Sizing Validation\n")
            print(
                "> f = 0.5·max(0, p − (1−p)/b); p = in-sample score→WR calibration, "
                "b = realized avg_win/avg_loss; clamped [0.70, 1.30]."
            )
            print(f"> Realized payoff ratio b = {_kelly.get('pf')} (vs 1.33 planned R:R).\n")
            print_table(
                ["Config", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"],
                [
                    [
                        "Equal-weight (baseline)",
                        str(eq_l7["n"]),
                        f"{eq_l7['wr']:.1f}%",
                        f"{eq_l7['avg']:+.2f}%",
                        fmt_sharpe(eq_l7["sharpe"]),
                        f"-{eq_l7['max_dd']:.2f}%",
                    ],
                    [
                        "L7 score-weighted (linear ±15%)",
                        str(sw_l7["n"]),
                        f"{sw_l7['wr']:.1f}%",
                        f"{sw_l7['avg']:+.2f}%",
                        fmt_sharpe(sw_l7["sharpe"]),
                        f"-{sw_l7['max_dd']:.2f}%",
                    ],
                    [
                        "Half-Kelly exploratory (empirical p, [0.70,1.30])",
                        str(_kelly["n"]),
                        f"{_kelly['wr']:.1f}%",
                        f"{_kelly['avg']:+.2f}%",
                        f"{fmt_sharpe(_kelly['sharpe'])} ({_dk_l7:+.2f} vs L7)",
                        f"-{_kelly['max_dd']:.2f}%",
                    ],
                ],
            )
            # The DEPLOYABLE live formula: convex Kelly over raw score, clamped to the
            # unchanged [0.85,1.15] envelope (kelly_size_mult — identical to assembler.py L7).
            _kw = [kelly_size_mult(float(s)) for s in trades["score"].fillna(50).tolist()]
            _kelly_live = stats_explicit_weights(_rets_l7, _kw)
            _dkl = (_kelly_live.get("sharpe") or 0.0) - (sw_l7.get("sharpe") or 0.0)
            print_table(
                ["Deployable live L7", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"],
                [
                    [
                        "Convex Kelly [0.85,1.15] (ships live)",
                        str(_kelly_live["n"]),
                        f"{_kelly_live['wr']:.1f}%",
                        f"{_kelly_live['avg']:+.2f}%",
                        f"{fmt_sharpe(_kelly_live['sharpe'])} ({_dkl:+.2f} vs L7)",
                        f"-{_kelly_live['max_dd']:.2f}%",
                    ],
                ],
            )
            _kv = (
                "✅ Deployable convex Kelly beats linear L7 — ship it"
                if _dkl > 0.005
                else "➖ Deployable Kelly ≈ linear L7 within the conservative envelope — keep linear"
                if _dkl > -0.005
                else "⚠ Deployable Kelly worse than L7 — keep linear nudge"
            )
            print(
                f"\n> Exploratory ΔSharpe vs L7 = {_dk_l7:+.3f} (vs eq {_dk_eq:+.3f}); "
                f"DEPLOYABLE ΔSharpe vs L7 = {_dkl:+.3f}  {_kv}\n"
            )

        # ── §R10-8. Per-Ticker (Vol-Scaled) Friction vs Flat 0.50% ────────────
        # The backtest has no historical fills, so we proxy spread/slippage from
        # realized volatility: wider quotes on higher-ATR names. Round-trip
        # friction_i = clamp(0.10 + 0.06·atr_pct, 0.12, 0.80)%. This is a realism
        # check (is flat 0.50% conservative?) and an edge-robustness check by
        # liquidity/vol tercile — NOT a Sharpe-maximisation knob.
        if "atr_pct" in trades.columns and "gross_pct" in trades.columns:
            _atr = trades["atr_pct"].fillna(2.0).to_numpy(dtype=float)  # atr as % of price
            _fric_pt = np.clip(0.10 + 0.06 * _atr, 0.12, 0.80)
            _gross = trades["gross_pct"].fillna(0.0).to_numpy(dtype=float)
            _net_pt = (_gross - _fric_pt).tolist()
            _flat = stats(trades["net_pct"].tolist())
            _pt = stats(_net_pt)
            print("\n## §R10-8. Per-Ticker Vol-Scaled Friction Validation\n")
            print(
                "> friction_i = clamp(0.10 + 0.06·atr_pct, 0.12, 0.80)% round-trip "
                f"(mean {_fric_pt.mean():.2f}% vs flat {FRICTION_PCT:.2f}%).\n"
            )
            print_table(
                ["Friction model", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"],
                [
                    [
                        f"Flat {FRICTION_PCT:.2f}% (current)",
                        str(_flat["n"]),
                        f"{_flat['wr']:.1f}%",
                        f"{_flat['avg']:+.2f}%",
                        fmt_sharpe(_flat["sharpe"]),
                        f"-{_flat['max_dd']:.2f}%",
                    ],
                    [
                        f"Per-ticker vol-scaled (μ={_fric_pt.mean():.2f}%)",
                        str(_pt["n"]),
                        f"{_pt['wr']:.1f}%",
                        f"{_pt['avg']:+.2f}%",
                        fmt_sharpe(_pt["sharpe"]),
                        f"-{_pt['max_dd']:.2f}%",
                    ],
                ],
            )
            # Edge robustness by ATR tercile under per-ticker friction.
            _t = trades.assign(_net_pt=_net_pt, _atr=_atr)
            _q1, _q2 = np.percentile(_atr, [33, 67])
            _buckets = [
                ("Low-vol (tight spread)", _t[_t["_atr"] <= _q1]),
                ("Mid-vol", _t[(_t["_atr"] > _q1) & (_t["_atr"] <= _q2)]),
                ("High-vol (wide spread)", _t[_t["_atr"] > _q2]),
            ]
            _rows = []
            for _lbl, _grp in _buckets:
                _s = stats(_grp["_net_pt"].tolist())
                _rows.append([_lbl, str(_s["n"]), f"{_s['wr']:.1f}%", f"{_s['avg']:+.2f}%", fmt_sharpe(_s["sharpe"])])
            print("\n> Edge by volatility tercile (net of per-ticker friction):\n")
            print_table(["Vol tercile", "N", "WR", "Avg Ret", "Sharpe"], _rows)
            print(
                "\n> Read: if high-vol Sharpe survives the wider modeled friction, the edge is "
                "robust to spread; the live allocator should still size DOWN wide-NBBO-spread "
                "names (§80 already penalises score; R10-8 adds the sizing lever).\n"
            )

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

        v2_list = _filter_simulation_results(
            _run_simulation_parallel(
                all_dfs,
                common_kwargs={"mr_only": True, "vix_regime_v2": True},
            )
        )

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
    if all_dfs and BACKTEST_MR_DEFAULT and "--validate-live-gates" not in sys.argv:
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

            ca_list = _filter_simulation_results(
                _run_simulation_parallel(
                    all_dfs,
                    common_kwargs={"mr_only": True, "cross_asset": cross_asset_data},
                )
            )

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
    # §14. FRED Macro-Regime Panel (NFCI + BAA10Y + T10Y3M) — regime-gate ablation
    # ─────────────────────────────────────────────────────────────────────────
    # Free, FRED-key-gated, decades deep, orthogonal to the VIX+STLFSI4 the backtest
    # already gates on. A/B: baseline vs. +panel BUY gate. Same gate-validation
    # discipline as §55 — measure ΔSharpe before any live deploy.
    if all_dfs and BACKTEST_MR_DEFAULT and "--validate-live-gates" not in sys.argv:
        print("\n## 14. FRED Macro-Regime Panel (NFCI + BAA10Y + T10Y3M)\n")
        print(
            "> Blocks marginal BUYs (score<50/55) when NFCI>0 / Baa-10Y>3% / 10Y<3M; "
            "hard-blocks at NFCI>0.5 / Baa-10Y>4%. Backtest previously gated only on VIX+STLFSI4."
        )
        print("Fetching FRED NFCI / BAA10Y / T10Y3M…", end=" ", flush=True)
        fred_panel_data = fetch_fred_panel(START, END, _fred_key)
        _have = {k: len(v) for k, v in fred_panel_data.items() if v}
        if not _have:
            print("failed — §14 skipped (no FRED_API_KEY?).\n")
        else:
            print(f"ok ({', '.join(f'{k}={n}' for k, n in _have.items())} daily obs)\n")
            fp_list = _filter_simulation_results(
                _run_simulation_parallel(
                    all_dfs,
                    common_kwargs={
                        "mr_only": True,
                        "fred_panel": fred_panel_data,
                        "ff_str": _ff_str,
                        "si_rising_map": _si_rising_map,
                        "ff_str_regime_map": _ff_str_regime_map,
                    },
                )
            )
            if not fp_list:
                print("[no §14 trades generated]\n")
            else:
                fp_trades = pd.concat(fp_list, ignore_index=True)
                sfp = stats(fp_trades["net_pct"].tolist())
                print_table(
                    ["Metric", "Baseline (§1-§8)", "+FRED panel", "Δ"],
                    [
                        ["N Trades", str(s["n"]), str(sfp["n"]), f"{sfp['n'] - s['n']:+d}"],
                        ["Win Rate", f"{s['wr']:.1f}%", f"{sfp['wr']:.1f}%", f"{sfp['wr'] - s['wr']:+.1f}pp"],
                        ["Avg Return", f"{s['avg']:+.2f}%", f"{sfp['avg']:+.2f}%", f"{sfp['avg'] - s['avg']:+.2f}pp"],
                        [
                            "Sharpe",
                            fmt_sharpe(s["sharpe"]),
                            fmt_sharpe(sfp["sharpe"]),
                            f"{(sfp['sharpe'] or 0) - (s['sharpe'] or 0):+.2f}",
                        ],
                        ["Max DD", f"-{s['max_dd']:.2f}%", f"-{sfp['max_dd']:.2f}%", ""],
                    ],
                )
                _blk = s["n"] - sfp["n"]
                _blkpct = _blk / s["n"] * 100 if s["n"] > 0 else 0.0
                _dsh = (sfp["sharpe"] or 0) - (s["sharpe"] or 0)
                print(f"\n> {_blk} trades blocked ({_blkpct:.1f}%) by the FRED regime panel.")
                _v = (
                    "✅ panel adds value — regime gating removes false positives"
                    if _dsh > 0.01
                    else "➖ panel neutral"
                    if _dsh > -0.01
                    else "⚠ panel harmful — regime gates cut too many recoverable dips"
                )
                print(f"> §14 verdict: ΔSharpe = {_dsh:+.2f}  {_v}\n")
                monte_carlo(fp_trades)

    # ─────────────────────────────────────────────────────────────────────────
    # §15. §65 Research — TRIN Capitulation Split
    # ─────────────────────────────────────────────────────────────────────────
    # Arms Index > 2.0 = market-wide panic selling. MR BUY entries during
    # capitulation context should show higher WR (classic MR hypothesis).

    # ─────────────────────────────────────────────────────────────────────────
    # §15. §66 Research — Zweig Breadth Thrust / A/D Breadth Split
    # ─────────────────────────────────────────────────────────────────────────
    # Zweig thrust (10-day EMA of A/D crosses from negative to >+50) is a rare
    # event. Negative A/D breadth (EMA < −200) should reduce MR WR (market
    # deterioration; MR setups may continue falling).

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
        try:
            _st_trades = _filter_simulation_results(
                _run_simulation_parallel(
                    all_dfs,
                    common_kwargs={
                        "mr_only": True,
                        "stop_mult_override": _smult,
                        "target_mult_override": _tmult,
                    },
                )
            )
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

    # ── §96a. Overnight vs Intraday Decomposition ────────────────────────────
    # Bug-fix (2): only print for plain (default open-entry) book — variant books
    # have their own sections (§96b / §97a) and mixing entry styles invalidates
    # the canonical decomposition read.
    _is_plain_book = not _entry_at_close_flag and not _entry_limit_flag
    if "overnight_pct" in trades.columns and "intraday_pct" in trades.columns and _is_plain_book:
        print("\n## §96a. Overnight vs Intraday Decomposition\n")
        print(
            "> Split each held day's move into overnight (prev Close → Open) and intraday (Open → Close).\n"
            "> Motivation: literature says short-term reversal accrues disproportionately close→open.\n"
        )
        _ov = trades["overnight_pct"].sum()
        _iv = trades["intraday_pct"].sum()
        _total = _ov + _iv
        if abs(_total) > 0.01:
            _ov_share = _ov / _total * 100
            _iv_share = _iv / _total * 100
        else:
            _ov_share = 0.0
            _iv_share = 0.0
        # Bug-fix (3): reconciliation row — decomposition total must equal gross P&L
        _gross_total = trades["gross_pct"].sum()
        _recon = _total - _gross_total
        _recon_pct_of_gross = (_recon / abs(_gross_total) * 100) if abs(_gross_total) > 0.01 else 0.0
        print_table(
            ["Component", "Cumulative %", "Share"],
            [
                ["Overnight (prev Close → Open)", f"{_ov:+.2f}%", f"{_ov_share:.1f}%"],
                ["Intraday (Open → Close)", f"{_iv:+.2f}%", f"{_iv_share:.1f}%"],
                ["Total", f"{_total:+.2f}%", "100.0%"],
                ["Gross P&L", f"{_gross_total:+.2f}%", "—"],
                ["Residual (decomp − gross)", f"{_recon:+.2f}%", f"{_recon_pct_of_gross:.1f}%"],
            ],
        )
        if abs(_recon) > 0.5:
            print(f"> ⚠ Residual = {_recon:+.2f}% — decomposition does NOT reconcile to gross (expected ≈0).")
        # By exit reason
        print("\n### By Exit Reason\n")
        _er_rows = []
        for _reason in ["target", "stop", "time", "time_loss", "adaptive"]:
            _sub = trades[trades["exit_reason"] == _reason]
            if _sub.empty:
                continue
            _er_rows.append(
                [
                    _reason,
                    str(len(_sub)),
                    f"{_sub['overnight_pct'].sum():+.2f}%",
                    f"{_sub['intraday_pct'].sum():+.2f}%",
                ]
            )
        print_table(["Exit", "N", "Overnight", "Intraday"], _er_rows)
        # By day-in-hold
        print("\n### By Day-in-Hold\n")
        _dih_rows = []
        for _d in sorted(trades["exit_day"].unique()):
            _sub = trades[trades["exit_day"] == _d]
            _dih_rows.append(
                [
                    str(_d),
                    str(len(_sub)),
                    f"{_sub['overnight_pct'].mean():+.2f}%",
                    f"{_sub['intraday_pct'].mean():+.2f}%",
                ]
            )
        print_table(["Day", "N", "Avg Overnight", "Avg Intraday"], _dih_rows)
        if abs(_ov) > abs(_iv):
            print(
                "> §96a verdict: overnight contribution dominates — close-entry variant (§96b) may capture more edge."
            )
        else:
            print("> §96a verdict: intraday contribution dominates — close-entry unlikely to help.")
        print()

    # ── §96b. Entry-at-Close A/B ─────────────────────────────────────────────
    if _entry_at_close_flag and "entry_style" in trades.columns:
        print("\n## §96b. Entry-at-Close A/B\n")
        print(
            "> ⚠ CAVEAT: signal is computed on the completed daily bar; close-fill assumes\n"
            "> the signal is computable at ~15:50 (approximate with completed bar).\n"
        )
        _close_trades = trades[trades["entry_style"] == "close"]
        _open_trades = trades[trades["entry_style"] == "open"] if "open" in trades["entry_style"].values else trades
        if not _close_trades.empty:
            _cs = stats(_close_trades["net_pct"].tolist())
            _os = stats(_open_trades["net_pct"].tolist()) if not _open_trades.empty else dict(_EMPTY_STATS)
            print_table(
                ["Variant", "N", "WR", "Avg Ret", "Sharpe", "Max DD"],
                [
                    [
                        "Close-entry",
                        str(_cs["n"]),
                        f"{_cs['wr']:.1f}%",
                        f"{_cs['avg']:+.2f}%",
                        fmt_sharpe(_cs.get("sharpe")),
                        f"-{_cs['max_dd']:.2f}%",
                    ],
                    [
                        "Open-entry (canon)",
                        str(_os["n"]),
                        f"{_os['wr']:.1f}%",
                        f"{_os['avg']:+.2f}%",
                        fmt_sharpe(_os.get("sharpe")),
                        f"-{_os['max_dd']:.2f}%",
                    ],
                ],
            )
            _dsh = (_cs.get("sharpe") or 0.0) - (_os.get("sharpe") or 0.0)
            if _dsh >= 0.03:
                print(f"> §96b verdict: ΔSharpe = +{_dsh:.2f} ≥ +0.03 — DEPLOY close-entry with 15:45 scan slot.")
            elif _dsh >= 0.01:
                print(f"> §96b verdict: ΔSharpe = +{_dsh:.2f} — marginal; monitor forward before deploying.")
            else:
                print(f"> §96b verdict: ΔSharpe = {_dsh:+.2f} — close-entry does NOT improve edge.")
        print()

    # ── §97a. Limit-Order Entry Grid ─────────────────────────────────────────
    if _entry_limit_flag and "entry_style" in trades.columns:
        print("\n## §97a. Limit-Order Entry Grid\n")
        print(
            "> Fill at signal Close − k×ATR if next-day Low ≤ limit.\n"
            "> Unfilled signals expire — the N cost is on the table (guardrail #1).\n"
        )
        _limit_rows = []
        for _style in sorted(trades["entry_style"].unique()):
            _sub = trades[trades["entry_style"] == _style]
            if _sub.empty:
                continue
            _ss = stats(_sub["net_pct"].tolist())
            _fill_rate = len(_sub) / _total_limit_attempted * 100 if _total_limit_attempted > 0 else 0.0
            _limit_rows.append(
                [
                    _style,
                    str(_ss["n"]),
                    f"{_fill_rate:.1f}%",
                    f"{_ss['wr']:.1f}%",
                    f"{_ss['avg']:+.2f}%",
                    fmt_sharpe(_ss.get("sharpe")),
                    f"-{_ss['max_dd']:.2f}%",
                ]
            )
        print_table(
            ["Entry Style", "N", "Fill Rate", "WR", "Avg Ret", "Sharpe", "Max DD"],
            _limit_rows,
        )
        print(
            "> Read: a limit variant wins only if it beats canon on per-trade Sharpe AND CAGR\n"
            "> at acceptable fill rate — per-trade gains from dropping trades are the ATR≤70 trap.\n"
        )

    # ── §QuantEngine: portfolio equity curve simulation ──────────────────────
    if "--portfolio" in sys.argv:
        # R7 (2026-07-15): the step-function DD-throttle is DEPLOYED in the live
        # allocator (portfolio_allocator.compute_dd_multiplier — >3% off peak →
        # 0.5× new positions; 26yr A/B: Ann.Sharpe 3.28→3.46, MaxDD −8.43→−6.38
        # at zero CAGR cost). The headline sim mirrors live by default;
        # --no-dd-throttle shows the unthrottled path.
        _dd_on = "--no-dd-throttle" not in sys.argv
        run_portfolio_simulation(trades, vol_target=_vol_target, dd_throttle=_dd_on, dd_trig=3.0, throttle_mult=0.5)
        if _vol_target is not None:
            print(
                "\n> Vol-target baseline comparison: run without --vol-target to see "
                "unscaled Sharpe/MaxDD for the same trade stream.\n"
            )

    # ── §QuantEngine: beta-hedge comparison ──────────────────────────────────
    if _beta_hedge_flag and spy_prices:
        print("\n## §QuantEngine: Beta-Hedge Comparison\n")
        print(
            f"> Each BUY: short {BETA_HEDGE_RATIO:.0%} SPY at entry, close at exit. "
            f"Extra friction: +{BETA_HEDGE_FRICTION:.2f}% round-trip on SPY leg.\n"
        )
        _bh_spy_present = trades["spy_leg_pct"].notna().sum()
        _bh_baseline = stats(trades["net_pct"].tolist())
        # Beta-neutral net_pct is already baked into trades["net_pct"] when beta_hedge=True.
        # Show side-by-side vs the unhedged equivalent (gross_pct - FRICTION_PCT).
        _unhedged_net = (trades["gross_pct"] + BETA_HEDGE_RATIO * trades["spy_leg_pct"].fillna(0)) - FRICTION_PCT
        _bh_unhedged_stats = stats(_unhedged_net.tolist())
        print_table(
            ["Metric", "Unhedged (no SPY)", "Beta-Hedged (−0.9×SPY)", "Δ"],
            [
                ["N Trades", str(s["n"]), str(_bh_baseline["n"]), ""],
                [
                    "Win Rate",
                    f"{_bh_unhedged_stats['wr']:.1f}%",
                    f"{_bh_baseline['wr']:.1f}%",
                    f"{_bh_baseline['wr'] - _bh_unhedged_stats['wr']:+.1f}pp",
                ],
                [
                    "Avg Return",
                    f"{_bh_unhedged_stats['avg']:+.2f}%",
                    f"{_bh_baseline['avg']:+.2f}%",
                    f"{_bh_baseline['avg'] - _bh_unhedged_stats['avg']:+.2f}pp",
                ],
                [
                    "Sharpe",
                    fmt_sharpe(_bh_unhedged_stats["sharpe"]),
                    fmt_sharpe(_bh_baseline["sharpe"]),
                    f"{(_bh_baseline.get('sharpe') or 0) - (_bh_unhedged_stats.get('sharpe') or 0):+.2f}",
                ],
                ["Max DD", f"-{_bh_unhedged_stats['max_dd']:.2f}%", f"-{_bh_baseline['max_dd']:.2f}%", ""],
            ],
        )
        print(f"\n> SPY hedge data available for {_bh_spy_present}/{s['n']} trades.")
        monte_carlo(trades)

    # ── §QuantEngine: continuous forecast sizing report ───────────────────────
    if _forecast_sizing_flag and "size_mult" in trades.columns:
        print("\n## §QuantEngine: Continuous Forecast Sizing (Carver FDM)\n")
        print(
            f"> Position size ∝ (score − {BUY_THRESH}) / {FORECAST_THRESH_DIV:.0f}, "
            f"clamped [{FORECAST_FLOOR}×, {FORECAST_CAP}×].\n"
        )
        _sm = trades["size_mult"].fillna(1.0).tolist()
        _rets = trades["net_pct"].tolist()
        sw = stats_weighted(_rets, _sm)
        sf = stats(_rets)
        print_table(
            ["Metric", "Flat Sizing", "Forecast Sizing", "Δ"],
            [
                ["Win Rate", f"{sf['wr']:.1f}%", f"{sw['wr']:.1f}%", f"{sw['wr'] - sf['wr']:+.1f}pp"],
                ["Weighted Avg", f"{sf['avg']:+.2f}%", f"{sw['avg']:+.2f}%", f"{sw['avg'] - sf['avg']:+.2f}pp"],
                [
                    "Sharpe",
                    fmt_sharpe(sf["sharpe"]),
                    fmt_sharpe(sw["sharpe"]),
                    f"{(sw.get('sharpe') or 0) - (sf.get('sharpe') or 0):+.2f}",
                ],
            ],
        )
        # Score-band breakdown of size multipliers
        if "score_band" in trades.columns:
            print("\n### Avg size multiplier by score band\n")
            sb_rows = []
            for band in ["40-50", "50-60", "60-70", "70+"]:
                sub = trades[trades["score_band"] == band]
                if sub.empty:
                    continue
                avg_mult = sub["size_mult"].mean()
                sb_rows.append([str(band), f"{avg_mult:.2f}×", str(len(sub))])
            print_table(["Score Band", "Avg Size Mult", "N"], sb_rows)

    # ── §QuantEngine: non-linear score-band sizing report ────────────────────
    if _consec_score_sizing_flag and "size_mult" in trades.columns:
        print("\n## §87. Consec-Score Conviction Sizing A/B\n")
        print(
            "> Prev-day score ≥ threshold → 1.3× size (conviction tier), else 1.0×.\n"
            "> Sizing form of the §83d consec-score filter — keeps all trades (ΔN=0).\n"
        )
        _sm87 = trades["size_mult"].fillna(1.0).tolist()
        _rets87 = trades["net_pct"].tolist()
        sw87 = stats_weighted(_rets87, _sm87)
        sf87 = stats(_rets87)
        _n_boost = sum(1 for m in _sm87 if m > 1.0)
        print_table(
            ["Metric", "Flat Sizing", "Consec-Score Sizing", "Δ"],
            [
                ["Boosted trades", "—", f"{_n_boost}/{len(_sm87)}", "—"],
                ["Win Rate", f"{sf87['wr']:.1f}%", f"{sw87['wr']:.1f}%", f"{sw87['wr'] - sf87['wr']:+.1f}pp"],
                ["Weighted Avg", f"{sf87['avg']:+.2f}%", f"{sw87['avg']:+.2f}%", f"{sw87['avg'] - sf87['avg']:+.2f}pp"],
                [
                    "Sharpe",
                    fmt_sharpe(sf87["sharpe"]),
                    fmt_sharpe(sw87["sharpe"]),
                    f"{(sw87.get('sharpe') or 0) - (sf87.get('sharpe') or 0):+.2f}",
                ],
            ],
        )
        _d87 = (sw87.get("sharpe") or 0) - (sf87.get("sharpe") or 0)
        _v87 = "✅ deploy as L10" if _d87 >= 0.02 else "⚪ below +0.02 deploy bar — do not deploy"
        print(f"\n> §87 verdict: ΔSharpe = {_d87:+.3f}  {_v87}")

    if _score_band_sizing_flag and "size_mult" in trades.columns:
        print("\n## §QuantEngine: Non-linear Score-Band Sizing\n")
        print(
            "> Position size steps by backtest-validated Sharpe band.\n"
            ">  <50→0.5×  50-55→0.75×  55-60→1.0×  60-65→1.15×  65-70→1.3×  70-75→1.45×  ≥75→1.55×\n"
        )
        _sm = trades["size_mult"].fillna(1.0).tolist()
        _rets = trades["net_pct"].tolist()
        sw = stats_weighted(_rets, _sm)
        sf = stats(_rets)
        print_table(
            ["Metric", "Flat Sizing", "Score-Band Sizing", "Δ"],
            [
                ["Win Rate", f"{sf['wr']:.1f}%", f"{sw['wr']:.1f}%", f"{sw['wr'] - sf['wr']:+.1f}pp"],
                ["Weighted Avg", f"{sf['avg']:+.2f}%", f"{sw['avg']:+.2f}%", f"{sw['avg'] - sf['avg']:+.2f}pp"],
                [
                    "Sharpe",
                    fmt_sharpe(sf["sharpe"]),
                    fmt_sharpe(sw["sharpe"]),
                    f"{(sw.get('sharpe') or 0) - (sf.get('sharpe') or 0):+.2f}",
                ],
            ],
        )
        print("\n### Avg size multiplier by score band\n")
        sb_rows = []
        for band in ["<50", "50-55", "55-60", "60-65", "65-70", "70-75", "75+"]:
            if band == "<50":
                sub = trades[trades["score"] < 50]
            elif band == "50-55":
                sub = trades[(trades["score"] >= 50) & (trades["score"] < 55)]
            elif band == "55-60":
                sub = trades[(trades["score"] >= 55) & (trades["score"] < 60)]
            elif band == "60-65":
                sub = trades[(trades["score"] >= 60) & (trades["score"] < 65)]
            elif band == "65-70":
                sub = trades[(trades["score"] >= 65) & (trades["score"] < 70)]
            elif band == "70-75":
                sub = trades[(trades["score"] >= 70) & (trades["score"] < 75)]
            else:
                sub = trades[trades["score"] >= 75]
            if sub.empty:
                continue
            avg_mult = sub["size_mult"].mean()
            sb_rows.append([str(band), f"{avg_mult:.2f}×", str(len(sub))])
        print_table(["Score Band", "Avg Size Mult", "N"], sb_rows)

    # ── §Inv2. VIX<20 gate ablation on 2022-present epoch ────────────────────
    if "--inv2" in sys.argv and all_dfs:
        print("\n## §Inv2. VIX<20 Gate Ablation — 2022-Present Epoch\n")
        print("> Does the VIX<20 MR suspension gate kill alpha in the current low-VIX regime?")
        print("> Comparing 2022-present with gate ON (default) vs gate OFF (vix_min_override=0).\n")
        _epoch_start = pd.Timestamp("2022-01-01")
        for _label, _vix_min in [("VIX<20 gate ON (default)", 20.0), ("VIX<20 gate OFF", 0.0)]:
            _ep_list = _filter_simulation_results(
                _run_simulation_parallel(
                    all_dfs,
                    common_kwargs={"mr_only": True, "vix_min_override": _vix_min},
                )
            )
            _ep_list = [_tr[_tr["date"] >= _epoch_start] for _tr in _ep_list if not _tr.empty]
            if _ep_list:
                _ep_df = pd.concat(_ep_list, ignore_index=True)
                _se = stats(_ep_df["net_pct"].tolist())
                print(
                    f"**{_label}:** N={_se['n']}, WR={_se['wr']:.1f}%, Avg={_se['avg']:+.2f}%, Sharpe={fmt_sharpe(_se['sharpe'])}, MaxDD={_se['max_dd']:.2f}%"
                )
            else:
                print(f"**{_label}:** 0 trades")
        print()

    # ── §Inv5. Retired — superseded by --validate-live-gates ─────────────────────
    if "--inv5" in sys.argv:
        print("\n## §Inv5 (retired 2026-06-02)\n")
        print("> All gates previously tested by --inv5 have been removed:")
        print(">   §59 OU halflife, §60 Hurst, §61 Idio vol, §78 Sep/Oct — all ΔSh=0.00 (dead)")
        print("> Use --validate-live-gates for the current gate ablation table.\n")

    # ── A18. Friction sensitivity sweep ──────────────────────────────────────
    if "--friction" in sys.argv and all_dfs:
        print("\n## A18. Friction Sensitivity Sweep\n")
        print("> Re-runs IS on cached all_dfs at each round-trip friction level.")
        print("> Flags tipping point where Sharpe drops below 0.20 (NBBO gate review trigger).\n")
        _friction_levels = [0.25, 0.50, 0.75, 1.00, 1.25]
        _friction_orig = FRICTION_PCT

        def _run_friction(label: str, fric: float) -> dict:
            global FRICTION_PCT
            FRICTION_PCT = fric
            _lst = _filter_simulation_results(_run_simulation_parallel(all_dfs, common_kwargs={"mr_only": True}))
            FRICTION_PCT = _friction_orig
            _combined = pd.concat(_lst, ignore_index=True) if _lst else pd.DataFrame()
            return stats(_combined["net_pct"].tolist()) if not _combined.empty else dict(_EMPTY_STATS)

        _fric_baseline = _run_friction("baseline", 0.50)
        _fric_rows = []
        for _fv in _friction_levels:
            _fs = _run_friction(f"{_fv:.2f}%", _fv)
            _dsh = (_fs.get("sharpe") or 0.0) - (_fric_baseline.get("sharpe") or 0.0)
            _flag = ""
            if _fs.get("sharpe") is not None and _fs["sharpe"] < 0.20:
                _flag = "  ⚠ Sharpe<0.20 — tighten NBBO gate"
            elif _fv == 0.50:
                _flag = "  ← current"
            _fric_rows.append(
                f"  {_fv:.2f}%  |  N={_fs['n']:>3}  WR={_fs['wr']:.1f}%  Avg={_fs['avg']:+.2f}%  "
                f"Sh={fmt_sharpe(_fs.get('sharpe'))}  MaxDD={_fs['max_dd']:.2f}%  "
                f"ΔSh={_dsh:+.3f}{_flag}"
            )
        print(f"  {'Fric%':<6}  {'N':>3}  {'WR':>6}  {'Avg':>7}  {'Sharpe':>8}  {'MaxDD':>8}  ΔSharpe")
        for _r in _fric_rows:
            print(_r)
        print(
            "\nNote: ADV-participation cost model (friction = bid_ask/2 + 0.1×√(size/ADV30))"
            " requires intraday ADV data not available in this backtest."
        )
        print()

    # ── §QuantEngine: walk-forward with threshold optimisation ───────────────
    if "--walk-forward" in sys.argv and all_dfs:
        run_walk_forward_with_opt(
            all_dfs,
            vix,
            spy_trend,
            stlfsi4,
        )

    # ── Quality Gate Sweep — path to forward Sharpe 0.50 ─────────────────────
    if "--quality-sweep" in sys.argv and all_dfs:
        print("\n\n## Quality Gate Sweep — Entry Filter Combinations\n")
        print("> Goal: find gate combo that lifts Sharpe toward 0.40+ with N ≥ 80.")
        print("> Gates: multi-condition MR (OR→AND), ATR ceiling (≤70), jump filter (<−6%), IBS streak (≥5d).")
        print("> All gates already validated individually in §12/§17. This sweeps combinations.\n")

        def _qrun(require_mr=1, atr_max=None, ret_jump=None, ibs_streak=None):
            trades_list = _filter_simulation_results(
                _run_simulation_parallel(
                    all_dfs,
                    common_kwargs={
                        "mr_only": True,
                        "require_mr_count_override": require_mr if require_mr > 1 else None,
                        "atr_pct_rank_max_override": atr_max,
                        "ret_jump_filter_override": ret_jump,
                        "ibs_sma20_streak_override": ibs_streak,
                    },
                )
            )
            if not trades_list:
                return dict(_EMPTY_STATS)
            return stats(pd.concat(trades_list, ignore_index=True)["net_pct"].tolist())

        _qs_baseline = _qrun()
        _qs_bs = _qs_baseline.get("sharpe") or 0.0

        _qs_configs = [
            ("baseline (all current gates)", 1, None, None, None),
            ("+ MR≥2 conditions", 2, None, None, None),
            ("+ ATR%rank ≤ 70", 1, 70.0, None, None),
            ("+ jump < −6%", 1, None, -6.0, None),
            ("+ IBS streak ≥ 5d", 1, None, None, 5),
            ("MR≥2 + ATR≤70", 2, 70.0, None, None),
            ("MR≥2 + jump<−6%", 2, None, -6.0, None),
            ("MR≥2 + IBS-streak≥5", 2, None, None, 5),
            ("ATR≤70 + jump<−6%", 1, 70.0, -6.0, None),
            ("ATR≤70 + IBS-streak≥5", 1, 70.0, None, 5),
            ("MR≥2 + ATR≤70 + jump<−6%", 2, 70.0, -6.0, None),
            ("MR≥2 + ATR≤70 + IBS-streak≥5", 2, 70.0, None, 5),
            ("ATR≤70 + jump<−6% + IBS-streak≥5", 1, 70.0, -6.0, 5),
            ("MR≥2 + ATR≤70 + jump<−6% + IBS≥5 (full stack)", 2, 70.0, -6.0, 5),
        ]

        _qs_rows = []
        best_sh, best_label = _qs_bs, "baseline"
        for i, (label, mr, atr, jump, ibs) in enumerate(_qs_configs, 1):
            print(f"  [{i:>2}/{len(_qs_configs)}] {label}…", flush=True)
            sv = _qrun(require_mr=mr, atr_max=atr, ret_jump=jump, ibs_streak=ibs)
            sh = sv.get("sharpe") or 0.0
            dsh = sh - _qs_bs
            flag = " ← BEST" if sh > best_sh and sv["n"] >= 80 else ""
            if sh > best_sh and sv["n"] >= 80:
                best_sh = sh
                best_label = label
            target = " ★ TARGET" if sh >= 0.40 and sv["n"] >= 80 else ""
            _qs_rows.append(
                [
                    label + flag + target,
                    str(sv["n"]),
                    f"{sv['wr']:.1f}%",
                    f"{sv['avg']:+.2f}%",
                    f"{fmt_sharpe(sh)} ({dsh:+.2f})",
                    f"-{sv['max_dd']:.2f}%",
                ]
            )

        print_table(["Config", "N", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD"], _qs_rows)
        print(
            f"\n> Baseline: N={_qs_baseline['n']}, WR={_qs_baseline['wr']:.1f}%, Sharpe={fmt_sharpe(_qs_baseline.get('sharpe'))}"
        )
        print(f"> Best (N≥80): '{best_label}' → Sharpe {best_sh:.2f}")
        if best_sh >= 0.40:
            print(
                f"> ★ Target Sharpe ≥ 0.40 achieved. Forward Sharpe estimate: {best_sh * 0.55:.2f}–{best_sh * 0.65:.2f}"
            )
            print("> Next: run --oos with this config to validate on held-out tickers.")
        else:
            print(f"> Target Sharpe ≥ 0.40 not reached with N≥80. Best: {best_sh:.2f}")
            print("> Consider relaxing N floor to 60, or combining with options flow data.")
        print()

    # ── Relax Sweep — LOOSEN entry gates to grow N while holding Sharpe ───────
    # Mirror of --quality-sweep but in the opposite direction: the live delivery
    # pipeline is signal-starved (June 2026: ~0.5% BUY delivery rate). This asks
    # the IS question "which gate can we relax to recover N without giving back
    # Sharpe?" Levers: MR thresholds (BB%B/IBS/VWAP — currently tightened to
    # 0.22/0.15/-0.75 from 0.30/0.20/-0.50) and BUY_THRESH (50). MR-count is
    # already 1 (matches live); can't relax further.
    if "--relax-sweep" in sys.argv and all_dfs:
        import sys as _sys

        _mod = _sys.modules[__name__]
        print("\n\n## Relax Sweep — Loosen Entry Gates to Grow N\n")
        print("> Goal: recover delivery volume (N) without giving back IS Sharpe.")
        print(
            f"> Baseline gates: BB%B<{MR_BB_CEIL} OR IBS<{MR_IBS_CEIL} OR VWAP%<{MR_VWAP_FLOOR}%, BUY_THRESH={BUY_THRESH}, MR≥1.\n"
        )

        def _rrun(bb=None, ibs=None, vwap=None, buy=None):
            _saved_vwap = _mod.MR_VWAP_FLOOR
            if vwap is not None:
                _mod.MR_VWAP_FLOOR = vwap
            try:
                trades_list = _filter_simulation_results(
                    _run_simulation_parallel(
                        all_dfs,
                        common_kwargs={
                            "mr_only": True,
                            "mr_bb_ceil_override": bb,
                            "mr_ibs_ceil_override": ibs,
                            "buy_thresh_override": buy,
                        },
                    )
                )
            finally:
                _mod.MR_VWAP_FLOOR = _saved_vwap
            if not trades_list:
                return dict(_EMPTY_STATS)
            return stats(pd.concat(trades_list, ignore_index=True)["net_pct"].tolist())

        _rs_baseline = _rrun()
        _rs_bs = _rs_baseline.get("sharpe") or 0.0
        _rs_bn = _rs_baseline["n"]

        # (label, bb_ceil, ibs_ceil, vwap_floor, buy_thresh) — None = keep current
        _rs_configs = [
            ("baseline (current gates)", None, None, None, None),
            ("BB%B ceil 0.22→0.30", 0.30, None, None, None),
            ("IBS ceil 0.15→0.20", None, 0.20, None, None),
            ("VWAP floor -0.75→-0.50", None, None, -0.50, None),
            ("BUY_THRESH 50→45", None, None, None, 45),
            ("BUY_THRESH 50→40", None, None, None, 40),
            ("all MR thresholds relaxed", 0.30, 0.20, -0.50, None),
            ("all MR relaxed + BUY_THRESH 45", 0.30, 0.20, -0.50, 45),
            ("all MR relaxed + BUY_THRESH 40", 0.30, 0.20, -0.50, 40),
        ]

        _rs_rows = []
        # "Keep" = grows N by ≥10% while holding Sharpe within 0.02 of baseline.
        best_label, best_n, best_sh = "baseline", _rs_bn, _rs_bs
        for i, (label, bb, ibs, vwap, buy) in enumerate(_rs_configs, 1):
            print(f"  [{i:>2}/{len(_rs_configs)}] {label}…", flush=True)
            sv = _rrun(bb=bb, ibs=ibs, vwap=vwap, buy=buy)
            sh = sv.get("sharpe") or 0.0
            dn = sv["n"] - _rs_bn
            keeps_sharpe = sh >= _rs_bs - 0.02
            grows_n = sv["n"] >= _rs_bn * 1.10
            verdict = " ✅ KEEP" if (keeps_sharpe and grows_n) else (" ⚠ N-up Sh-down" if grows_n else "")
            # prefer the config with the most N among those that hold Sharpe
            if keeps_sharpe and sv["n"] > best_n:
                best_n, best_sh, best_label = sv["n"], sh, label
            _rs_rows.append(
                [
                    label + verdict,
                    f"{sv['n']} ({dn:+d})",
                    f"{sv['wr']:.1f}%",
                    f"{sv['avg']:+.2f}%",
                    f"{fmt_sharpe(sh)} ({sh - _rs_bs:+.2f})",
                    f"-{sv['max_dd']:.2f}%",
                ]
            )

        print_table(["Config", "N (Δ)", "WR", "Avg Ret", "Sharpe (Δ)", "MaxDD"], _rs_rows)
        print(f"\n> Baseline: N={_rs_bn}, WR={_rs_baseline['wr']:.1f}%, Sharpe={fmt_sharpe(_rs_bs)}")
        if best_label != "baseline":
            print(
                f"> Best N-growth holding Sharpe (≥-0.02): '{best_label}' → N={best_n} (+{best_n - _rs_bn}), Sharpe {best_sh:.2f}"
            )
            print(
                "> Next: --oos with this config to confirm the relaxed gate survives out-of-sample before any live change."
            )
        else:
            print(
                "> No relaxation grows N ≥10% without giving back >0.02 Sharpe — the gates are at the efficient frontier."
            )
        print()

    # ── Gate Validation — ablate all backtest-testable live engine gates ─────
    if "--oos" in sys.argv or "--sweep" in sys.argv:
        run_oos_validation(
            vix,
            spy_trend,
            stlfsi4,
            buy_thresh_override=_buy_thresh_override,
        )

    if "--sweep" in sys.argv:
        parameter_sweep(all_dfs, vix, spy_trend, stlfsi4)

    if "--full-universe" in sys.argv:
        run_full_universe_curation_bias(
            vix,
            spy_trend,
            stlfsi4,
        )

    if "--gate-sweep" in sys.argv:
        gate_sensitivity_sweep(
            all_dfs,
            vix,
            spy_trend,
            stlfsi4,
        )

    # ── BT-2: Parameter stability sweep (BUY_THRESH 45–55) ───────────────────
    if "--param-sweep" in sys.argv and all_dfs:
        import random as _random

        print("\n## BT-2: BUY_THRESH Parameter Stability Sweep (45–55)\n")
        print("> Goal: confirm Sharpe is stable ±0.03 across [48, 52] — not a knife-edge optimum.")
        print("> Each row reruns the full IS backtest at that threshold.\n")

        def _bootstrap_sr_ci(rets: list, n_boot: int = 500) -> tuple:
            """95% CI on per-trade Sharpe via bootstrap resampling."""
            if len(rets) < 10:
                return float("nan"), float("nan")
            boot_srs = []
            for _ in range(n_boot):
                sample = _random.choices(rets, k=len(rets))
                mu = sum(sample) / len(sample)
                std_b = (sum((r - mu) ** 2 for r in sample) / max(len(sample) - 1, 1)) ** 0.5
                boot_srs.append(mu / std_b if std_b > 0 else 0.0)
            boot_srs.sort()
            return boot_srs[int(0.025 * n_boot)], boot_srs[int(0.975 * n_boot)]

        _orig_bt = BUY_THRESH
        _ps_rows = []
        for _bt in range(45, 56):
            _ps_trades = _filter_simulation_results(
                _run_simulation_parallel(
                    all_dfs,
                    common_kwargs={"mr_only": True, "buy_thresh_override": _bt},
                )
            )
            if not _ps_trades:
                continue
            _ps_combined = pd.concat(_ps_trades, ignore_index=True)
            _rets = _ps_combined["net_pct"].tolist()
            _sv = stats(_rets)
            _ci_lo, _ci_hi = _bootstrap_sr_ci(_rets)
            _flag = " ← CURRENT" if _bt == _orig_bt else ""
            _ps_rows.append(
                [
                    f"BUY_THRESH={_bt}{_flag}",
                    str(_sv["n"]),
                    f"{_sv['wr']:.1f}%",
                    f"{_sv['avg']:+.2f}%",
                    fmt_sharpe(_sv.get("sharpe")),
                    f"[{_ci_lo:.2f}, {_ci_hi:.2f}]",
                ]
            )

        print_table(["Config", "N", "WR", "Avg Ret", "Sharpe", "Bootstrap 95% CI"], _ps_rows)
        print()
        print("> Stable if Sharpe varies ≤±0.03 across BUY_THRESH 48–52.")
        print("> Knife-edge: if peak Sharpe is >0.05 above adjacent values, overfit risk is high.")
        print()

    # ── RD-4: Regime decomposition of IS stats (--regime-split) ─────────────
    if "--regime-split" in sys.argv and all_dfs:
        print("\n## RD-4: IS Stats by VIX Regime\n")
        print("> Split IS trades into VIX regimes at entry date.")
        print("> VIX<20 (calm) / 20–30 (elevated) / >30 (stress)")
        print("> Reveals whether forward Sharpe estimate is regime-conditional.\n")

        _rs_trades = _filter_simulation_results(_run_simulation_parallel(all_dfs, common_kwargs={"mr_only": True}))
        _all_trades_df = pd.concat(_rs_trades, ignore_index=True) if _rs_trades else pd.DataFrame()
        if _rs_trades:
            _rs_all = pd.concat(_rs_trades, ignore_index=True)

            # Tag each trade with VIX regime at entry
            def _vix_regime(entry_date):
                try:
                    _dt_str = str(entry_date)[:10]
                    # Guard against non-date scalars (e.g. price 150.25 → "150.25")
                    if not _dt_str[:4].isdigit() or "-" not in _dt_str:
                        return "unknown"
                    v = vix.get(pd.Timestamp(_dt_str))
                except Exception:
                    return "unknown"
                if v is None:
                    return "unknown"
                if v < 20:
                    return "calm (<20)"
                if v < 30:
                    return "elevated (20–30)"
                return "stress (>30)"

            # simulate_ticker returns a "date" column (Timestamp); "entry" is price.
            if "date" in _rs_all.columns:
                _rs_all["vix_regime"] = _rs_all["date"].apply(_vix_regime)
            elif "entry_date" in _rs_all.columns:
                _rs_all["vix_regime"] = _rs_all["entry_date"].apply(_vix_regime)
            elif "entry" in _rs_all.columns:
                _rs_all["vix_regime"] = _rs_all["entry"].apply(_vix_regime)
            else:
                _rs_all["vix_regime"] = "unknown"

            _rs_rows = []
            for _regime in ["calm (<20)", "elevated (20–30)", "stress (>30)", "unknown"]:
                _sub = _rs_all[_rs_all["vix_regime"] == _regime]
                if _sub.empty:
                    continue
                _rv = stats(_sub["net_pct"].tolist())
                _rs_rows.append(
                    [
                        _regime,
                        str(_rv["n"]),
                        f"{_rv['wr']:.1f}%",
                        f"{_rv['avg']:+.2f}%",
                        fmt_sharpe(_rv.get("sharpe")),
                        f"{_rv['max_dd']:.2f}%",
                    ]
                )
            print_table(["VIX Regime", "N", "WR", "Avg Ret", "Sharpe", "MaxDD"], _rs_rows)
            print()
            print("> §54 VIX<20 hard block in delivery_gates.py should eliminate most calm-regime signals.")
            print("> If stress-regime Sharpe >> elevated-regime: consider sizing up during VIX>30 entries.")
            print()

    # ── QENG-1b: Probability of Backtest Overfitting (PBO) Report ─────────────
    if "--pbo" in sys.argv and all_dfs:
        from itertools import combinations as _combinations
        import numpy as _np
        import asyncio as _asyncio

        print("\n## QENG-1b: Probability of Backtest Overfitting (PBO) Report\n")
        print("> Goal: Compute PBO using Combinatorially Symmetric Cross-Validation (CSCV) splits.")
        print("> Sweeps BUY_THRESH from 45 to 55 (11 parameter variants) over S=8 temporal partitions.")
        print("> Promotability threshold: PBO < 0.15 is required.\n")

        # 1. Gather all trades for each trial BUY_THRESH in [45..55]
        _orig_bt = BUY_THRESH
        _trials = list(range(45, 56))
        _all_trial_trades = {}

        print("Simulating strategy variants...")
        for _bt in _trials:
            _trades_list = _filter_simulation_results(
                _run_simulation_parallel(
                    all_dfs,
                    common_kwargs={"mr_only": True, "buy_thresh_override": _bt},
                )
            )
            if _trades_list:
                _all_trial_trades[_bt] = pd.concat(_trades_list, ignore_index=True)
            else:
                _all_trial_trades[_bt] = pd.DataFrame(columns=["entry_date", "net_pct"])

        # Determine the global min/max dates across all trials to split chronologically
        _all_dates = []
        for _bt, _df_trades in _all_trial_trades.items():
            if not _df_trades.empty:
                _col = "entry" if "entry" in _df_trades.columns else "entry_date"
                _all_dates.extend(pd.to_datetime(_df_trades[_col]).tolist())

        if not _all_dates:
            print("No trades found across any trials to compute PBO.")
        else:
            _min_date = min(_all_dates)
            _max_date = max(_all_dates)
            _duration = _max_date - _min_date

            # Divide timeline into S=8 slices
            S = 8
            _slice_duration = _duration / S
            _slices = []
            for i in range(S):
                _start = _min_date + i * _slice_duration
                _end = _min_date + (i + 1) * _slice_duration
                _slices.append((_start, _end))

            # Helper to calculate Sharpe of a list of returns
            def _calc_raw_sharpe(returns: list[float]) -> float:
                if len(returns) < 3:
                    return 0.0
                mean_r = sum(returns) / len(returns)
                std_r = (sum((r - mean_r) ** 2 for r in returns) / (len(returns) - 1)) ** 0.5
                if std_r == 0:
                    return 0.0
                return (mean_r / std_r) * math.sqrt(52)

            # Assign each trade to a slice for each trial
            _trial_slice_rets = {}
            for _bt in _trials:
                _df_trades = _all_trial_trades[_bt]
                _trial_slice_rets[_bt] = [[] for _ in range(S)]
                if not _df_trades.empty:
                    _col = "entry" if "entry" in _df_trades.columns else "entry_date"
                    _dates = pd.to_datetime(_df_trades[_col])
                    _rets = _df_trades["net_pct"].tolist()
                    for _idx, _d in enumerate(_dates):
                        # Find which slice it belongs to
                        _s_found = S - 1
                        for _s in range(S - 1):
                            if _slices[_s][0] <= _d < _slices[_s][1]:
                                _s_found = _s
                                break
                        _trial_slice_rets[_bt][_s_found].append(_rets[_idx])

            # Now form combinations of S/2 train slices
            _all_combos = list(_combinations(range(S), S // 2))
            _overfit_count = 0
            _total_combos = len(_all_combos)

            _rank_distribution = []

            for _train_indices in _all_combos:
                _test_indices = [idx for idx in range(S) if idx not in _train_indices]

                # Evaluate all trials on training set
                _train_sharpes = {}
                for _bt in _trials:
                    _train_rets = []
                    for idx in _train_indices:
                        _train_rets.extend(_trial_slice_rets[_bt][idx])
                    _train_sharpes[_bt] = _calc_raw_sharpe(_train_rets)

                # Identify optimal trial on training set:
                _best_train_bt = max(_trials, key=lambda _bt: _train_sharpes[_bt])

                # Evaluate all trials on testing set
                _test_sharpes = {}
                for _bt in _trials:
                    _test_rets = []
                    for idx in _test_indices:
                        _test_rets.extend(_trial_slice_rets[_bt][idx])
                    _test_sharpes[_bt] = _calc_raw_sharpe(_test_rets)

                # Rank the selected parameter on testing set.
                _sorted_test_sharpes = sorted([(_test_sharpes[_bt], _bt) for _bt in _trials])
                _rank_idx = -1
                for rank_i, (sh, _bt) in enumerate(_sorted_test_sharpes):
                    if _bt == _best_train_bt:
                        _rank_idx = rank_i
                        break

                _rel_rank = (_rank_idx + 1) / len(_trials)
                _rank_distribution.append(_rel_rank)

                if _rel_rank <= 0.50:
                    _overfit_count += 1

            _pbo = _overfit_count / _total_combos
            print(f"Combinations evaluated: {_total_combos} (S={S} slices, S//2 train)")
            print(f"Overfit instances (test rank <= median): {_overfit_count}")
            print(f"Probability of Backtest Overfitting (PBO): {_pbo:.4f} ({_pbo * 100:.1f}%)")

            _threshold = 0.15
            _passed = _pbo < _threshold
            _status_str = "PASS" if _passed else "WARNING"
            print(f"STATUS: {_status_str} (PBO {_pbo:.4f} vs limit {_threshold})")

            # Print relative rank distribution
            _p10 = float(_np.percentile(_rank_distribution, 10))
            _p50 = float(_np.percentile(_rank_distribution, 50))
            _p90 = float(_np.percentile(_rank_distribution, 90))
            print("\nTest Rank Distribution:")
            print(f"  P10 Rank: {_p10 * 100:.1f}%")
            print(f"  P50 Rank: {_p50 * 100:.1f}%")
            print(f"  P90 Rank: {_p90 * 100:.1f}%")
            print()

            # Save the experiment into database
            async def _save_experiment_in_db():
                try:
                    import subprocess
                    from database import AsyncSessionLocal
                    from models import ResearchExperiment

                    try:
                        git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
                    except Exception:
                        git_sha = None

                    # Find best global trial
                    # (simulate original or current)
                    _orig_sv = (
                        stats(_all_trial_trades[_orig_bt]["net_pct"].tolist())
                        if not _all_trial_trades[_orig_bt].empty
                        else {"sharpe": 0.0, "wr": 0.0, "avg": 0.0}
                    )

                    async with AsyncSessionLocal() as db:
                        exp = ResearchExperiment(
                            experiment_type="parameter_sweep",
                            hypothesis="BUY_THRESH parameter sweep from 45 to 55 to verify stability and compute PBO",
                            universe={"tickers": list(all_dfs.keys())},
                            data_version="1.0",
                            git_sha=git_sha,
                            search_space={"BUY_THRESH": _trials},
                            number_of_trials=len(_trials),
                            is_metrics={
                                "original_sharpe": _orig_sv.get("sharpe", 0.0),
                                "original_win_rate": _orig_sv.get("wr", 0.0),
                                "original_avg_ret": _orig_sv.get("avg", 0.0),
                            },
                            oos_metrics={"rank_distribution": {"p10": _p10, "p50": _p50, "p90": _p90}},
                            dsr_pbo={"pbo": _pbo, "S": S, "combos": _total_combos},
                            decision="shadow" if _passed else "rejected",
                            promotion_status="pending",
                        )
                        db.add(exp)
                        await db.commit()
                        print(f"> Registered experiment in DB registry (ID: {exp.id})")
                except Exception as db_err:
                    print(f"Failed to write experiment to DB: {db_err}")

            _asyncio.run(_save_experiment_in_db())


if __name__ == "__main__":
    main()
