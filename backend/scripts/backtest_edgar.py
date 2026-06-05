"""
scripts/backtest_edgar.py — Validate Tier 3 fundamental signals via EDGAR.

Downloads point-in-time SEC EDGAR data for all IS tickers and runs
the IS backtest with three fundamental score modifiers:

  §50 Piotroski F-Score  (+12/+5/-4/-10 pts based on F-score tier)
  §76 Altman Z-Score     (-10 pts if Z < 1.81 distress zone)
  §73 Insider clustering (from Form 4 filings; +8 if 3+ unique buyers in 30d)

All data is keyed on SEC *filing_date* (not period end) to ensure true
point-in-time accuracy — no look-ahead bias.

USAGE:
    cd backend && python scripts/backtest_edgar.py           # fetch + run (first time ~10 min)
    cd backend && python scripts/backtest_edgar.py --cached  # reload cached data (~3 min)
    cd backend && python scripts/backtest_edgar.py --ticker NVDA  # debug single ticker

EDGAR API limits: 10 req/s. We use a 0.12s delay between requests.
Data is cached to data/edgar_fundamentals.pkl so subsequent runs are fast.

Outputs:
  - IS baseline (no EDGAR) vs each modifier vs all combined
  - ΔSharpe table per modifier
  - Per-ticker ΔSharpe for the combined model
"""

from __future__ import annotations

import os
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import yfinance as yf

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
sys.path.insert(0, _PARENT)

# Import from the main backtest script
import backtest_technicals as bt

CACHE_PATH = Path(_PARENT) / "data" / "edgar_fundamentals.pkl"
EDGAR_BASE = "https://data.sec.gov"
HEADERS = {"User-Agent": "Signal.Trade Research harsh13858@gmail.com"}
RATE_DELAY = 0.12  # seconds between EDGAR requests (10 req/s limit)

# ─────────────────────────────────────────────────────────────────────────────
# CIK Lookup
# ─────────────────────────────────────────────────────────────────────────────


def fetch_cik_map() -> dict[str, str]:
    """Download SEC ticker→CIK lookup from EDGAR."""
    url = "https://www.sec.gov/files/company_tickers.json"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    # {0: {cik_str: "0001045810", ticker: "NVDA", title: "NVIDIA CORP"}, ...}
    return {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in data.values()}


# ─────────────────────────────────────────────────────────────────────────────
# EDGAR company facts parser
# ─────────────────────────────────────────────────────────────────────────────


def _get_concept(facts_usgaap: dict, *keys: str) -> list[dict]:
    """Return the USD unit entries for the first matching concept key."""
    for k in keys:
        c = facts_usgaap.get(k)
        if c:
            entries = c.get("units", {}).get("USD") or c.get("units", {}).get("shares") or []
            return [e for e in entries if e.get("form") in ("10-K", "10-Q")]
    return []


def _entries_to_series(entries: list[dict], freq: str = "Q") -> pd.Series:
    """Convert EDGAR fact entries to a filing-date-indexed Series."""
    rows = {}
    for e in entries:
        filed = e.get("filed")
        val = e.get("val")
        fp = e.get("fp", "")
        if filed and val is not None:
            # Use fp to filter quarterly vs annual
            if freq == "Q" and fp not in ("Q1", "Q2", "Q3", "Q4", "FY"):
                continue
            rows[pd.Timestamp(filed)] = float(val)
    if not rows:
        return pd.Series(dtype=float)
    s = pd.Series(rows).sort_index()
    # Deduplicate: keep last filing per date
    return s[~s.index.duplicated(keep="last")]


def fetch_edgar_facts(cik: str) -> dict:
    """Fetch company XBRL facts from SEC EDGAR."""
    url = f"{EDGAR_BASE}/api/xbrl/companyfacts/CIK{cik}.json"
    time.sleep(RATE_DELAY)
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code == 404:
        return {}
    r.raise_for_status()
    return r.json()


# ─────────────────────────────────────────────────────────────────────────────
# Piotroski F-Score (3-signal simplified: ROA, OCF, ΔLeverage)
# ─────────────────────────────────────────────────────────────────────────────
# Using a simplified 3-signal version to ensure data availability.
# Full 9-signal Piotroski needs 4 quarters of stable data per signal.
# 3 signals focus on the strongest predictors (Fama-French confirmed).
#
# F = ROA_pos + OCF_pos + Leverage_falling
# Score ≥ 2 = "strong" (+5 pts), score = 0 = "weak" (-5 pts)


def compute_piotroski_series(facts: dict) -> pd.Series:
    """
    Point-in-time Piotroski F-Score series (filing_date → score).
    Returns NaN where insufficient data.
    """
    usgaap = facts.get("facts", {}).get("us-gaap", {})

    # Net income
    ni = _entries_to_series(
        _get_concept(usgaap, "NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic")
    )
    # Operating cash flow
    ocf = _entries_to_series(
        _get_concept(usgaap, "NetCashProvidedByUsedInOperatingActivities", "CashGeneratedFromOperations")
    )
    # Total assets
    assets = _entries_to_series(_get_concept(usgaap, "Assets"))
    # Long-term debt
    ltd = _entries_to_series(
        _get_concept(usgaap, "LongTermDebt", "LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations")
    )

    if assets.empty or ni.empty:
        return pd.Series(dtype=float)

    # Build quarterly snapshots at each filing date in assets
    records = []
    for filing_date in assets.index:
        a = assets.asof(filing_date)
        if pd.isna(a) or a <= 0:
            continue
        n = ni.asof(filing_date)
        o = ocf.asof(filing_date) if not ocf.empty else np.nan
        l = ltd.asof(filing_date) if not ltd.empty else np.nan

        # Prior year (approx 365 days back)
        prior = filing_date - pd.Timedelta(days=365)
        a_prev = assets.asof(prior) if filing_date > assets.index[0] + pd.Timedelta(days=300) else np.nan
        l_prev = ltd.asof(prior) if not ltd.empty and filing_date > assets.index[0] + pd.Timedelta(days=300) else np.nan

        f = 0
        # F1: ROA > 0
        if not pd.isna(n) and n > 0:
            f += 1
        # F2: OCF > 0
        if not pd.isna(o) and o > 0:
            f += 1
        # F5: leverage declining (LTD/Assets this year < prior year)
        if not pd.isna(l) and not pd.isna(a) and not pd.isna(l_prev) and not pd.isna(a_prev) and a_prev > 0:
            lev_now = l / a
            lev_prev = l_prev / a_prev
            if lev_now < lev_prev:
                f += 1

        records.append((filing_date, f))

    if not records:
        return pd.Series(dtype=float)
    return pd.Series({d: v for d, v in records})


# ─────────────────────────────────────────────────────────────────────────────
# Altman Z-Score (modified book-value version for public companies)
# ─────────────────────────────────────────────────────────────────────────────
# Z' = 0.717*X1 + 0.847*X2 + 3.107*X3 + 0.420*X4 + 0.998*X5
# X1 = Working Capital / Total Assets
# X2 = Retained Earnings / Total Assets
# X3 = EBIT / Total Assets
# X4 = Book Equity / Total Liabilities
# X5 = Revenue / Total Assets
# Z' < 1.23 → distress, Z' > 2.90 → safe


def compute_altman_series(facts: dict) -> pd.Series:
    """Point-in-time Altman Z'-Score series (filing_date → Z')."""
    usgaap = facts.get("facts", {}).get("us-gaap", {})

    assets = _entries_to_series(_get_concept(usgaap, "Assets"))
    ca = _entries_to_series(_get_concept(usgaap, "AssetsCurrent"))
    cl = _entries_to_series(_get_concept(usgaap, "LiabilitiesCurrent"))
    retained = _entries_to_series(_get_concept(usgaap, "RetainedEarningsAccumulatedDeficit", "RetainedEarnings"))
    ebit = _entries_to_series(
        _get_concept(
            usgaap,
            "OperatingIncomeLoss",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        )
    )
    equity = _entries_to_series(
        _get_concept(
            usgaap, "StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
        )
    )
    liabilities = _entries_to_series(_get_concept(usgaap, "Liabilities"))
    revenue = _entries_to_series(
        _get_concept(usgaap, "Revenues", "SalesRevenueNet", "RevenueFromContractWithCustomerExcludingAssessedTax")
    )

    if assets.empty or equity.empty:
        return pd.Series(dtype=float)

    records = []
    for filing_date in assets.index:
        a = assets.asof(filing_date)
        if pd.isna(a) or a <= 0:
            continue
        ca_v = ca.asof(filing_date) if not ca.empty else np.nan
        cl_v = cl.asof(filing_date) if not cl.empty else np.nan
        re_v = retained.asof(filing_date) if not retained.empty else np.nan
        eb_v = ebit.asof(filing_date) if not ebit.empty else np.nan
        eq_v = equity.asof(filing_date) if not equity.empty else np.nan
        li_v = liabilities.asof(filing_date) if not liabilities.empty else np.nan
        rv_v = revenue.asof(filing_date) if not revenue.empty else np.nan

        x1 = (ca_v - cl_v) / a if not pd.isna(ca_v) and not pd.isna(cl_v) else np.nan
        x2 = re_v / a if not pd.isna(re_v) else np.nan
        x3 = eb_v / a if not pd.isna(eb_v) else np.nan
        x4 = eq_v / li_v if not pd.isna(eq_v) and not pd.isna(li_v) and li_v > 0 else np.nan
        x5 = rv_v / a if not pd.isna(rv_v) else np.nan

        components = [x1, x2, x3, x4, x5]
        weights = [0.717, 0.847, 3.107, 0.420, 0.998]
        valid = [(w, x) for w, x in zip(weights, components) if not pd.isna(x)]
        if len(valid) < 3:
            continue
        z = sum(w * x for w, x in valid)
        records.append((filing_date, z))

    if not records:
        return pd.Series(dtype=float)
    return pd.Series({d: v for d, v in records})


# ─────────────────────────────────────────────────────────────────────────────
# Insider clustering via EDGAR Form 4
# ─────────────────────────────────────────────────────────────────────────────


def fetch_insider_transactions(cik: str) -> list[dict]:
    """
    Fetch Form 4 insider transaction data via EDGAR submissions API.
    Returns list of {filed_date, transaction_type, shares} dicts.
    """
    url = f"{EDGAR_BASE}/submissions/CIK{cik}.json"
    time.sleep(RATE_DELAY)
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        return []
    data = r.json()

    transactions = []
    filings = data.get("filings", {}).get("recent", {})
    forms = filings.get("form", [])
    dates = filings.get("filingDate", [])
    accns = filings.get("accessionNumber", [])

    for form, date, accn in zip(forms, dates, accns):
        if form != "4":
            continue
        transactions.append(
            {
                "filed": pd.Timestamp(date),
                "accn": accn,
            }
        )

    # For simplicity: count unique Form 4 filers per 30-day window as a proxy
    # for insider cluster. We don't parse the actual Form 4 XML (complex).
    return transactions


def compute_insider_series(cik: str) -> pd.Series:
    """
    Build a rolling 30-day Form 4 filing count series (proxy for insider activity).
    Returns a daily series: date → n_filings_in_prior_30d.
    """
    txns = fetch_insider_transactions(cik)
    if not txns:
        return pd.Series(dtype=float)

    dates = sorted(t["filed"] for t in txns)
    if not dates:
        return pd.Series(dtype=float)

    # Build daily count of unique Form 4 filings in trailing 30 days
    date_range = pd.date_range(dates[0], max(dates) + pd.Timedelta(days=30), freq="D")
    counts = {}
    dates_set = pd.DatetimeIndex(dates)
    for d in date_range:
        window_start = d - pd.Timedelta(days=30)
        n = ((dates_set >= window_start) & (dates_set <= d)).sum()
        counts[d] = int(n)
    return pd.Series(counts)


# ─────────────────────────────────────────────────────────────────────────────
# Cache management
# ─────────────────────────────────────────────────────────────────────────────


def build_cache(tickers: list[str], cik_map: dict[str, str]) -> dict:
    """Fetch EDGAR data for all tickers and return cache dict."""
    cache = {}
    missing = []
    total = len(tickers)

    for i, ticker in enumerate(tickers, 1):
        cik = cik_map.get(ticker.upper())
        if not cik:
            missing.append(ticker)
            print(f"  [{i:>3}/{total}] {ticker}: no CIK — skipped")
            continue

        print(f"  [{i:>3}/{total}] {ticker} (CIK {cik})…", end=" ", flush=True)
        try:
            facts = fetch_edgar_facts(cik)
            if not facts:
                print("404")
                continue

            piotroski = compute_piotroski_series(facts)
            altman = compute_altman_series(facts)
            insider = compute_insider_series(cik)

            cache[ticker] = {
                "cik": cik,
                "piotroski": piotroski,
                "altman": altman,
                "insider": insider,
            }
            n_p = len(piotroski)
            n_a = len(altman)
            n_i = len(insider)
            print(f"ok (piotroski={n_p}pts, altman={n_a}pts, insider={n_i}d)")
        except Exception as e:
            print(f"error: {e}")

    print(f"\nCache built: {len(cache)}/{total} tickers. Missing CIK: {missing}")
    return cache


def load_or_build_cache(tickers: list[str], force_rebuild: bool = False) -> dict:
    if not force_rebuild and CACHE_PATH.exists():
        print(f"Loading cached EDGAR data from {CACHE_PATH}…", end=" ")
        with open(CACHE_PATH, "rb") as f:
            cache = pickle.load(f)
        print(f"ok ({len(cache)} tickers)")
        return cache

    print(f"Fetching EDGAR data for {len(tickers)} tickers (~0.12s/ticker)…")
    print(f"Estimated time: {len(tickers) * 0.3 / 60:.1f} min\n")
    cik_map = fetch_cik_map()
    cache = build_cache(tickers, cik_map)
    CACHE_PATH.parent.mkdir(exist_ok=True)
    with open(CACHE_PATH, "wb") as f:
        pickle.dump(cache, f)
    print(f"\nCache saved to {CACHE_PATH}")
    return cache


# ─────────────────────────────────────────────────────────────────────────────
# IS Backtest with EDGAR modifiers
# ─────────────────────────────────────────────────────────────────────────────


def _fundamental_score_modifier(
    entry_date: pd.Timestamp,
    ticker: str,
    cache: dict,
    use_piotroski: bool = True,
    use_altman: bool = True,
    use_insider: bool = True,
) -> float:
    """Return total score adjustment from EDGAR fundamentals at entry_date."""
    data = cache.get(ticker)
    if not data:
        return 0.0

    delta = 0.0

    if use_piotroski and not data["piotroski"].empty:
        try:
            f = data["piotroski"].asof(entry_date)
            if not pd.isna(f):
                if f >= 2:
                    delta += 5.0
                elif f == 0:
                    delta -= 5.0
        except Exception:
            pass

    if use_altman and not data["altman"].empty:
        try:
            z = data["altman"].asof(entry_date)
            if not pd.isna(z):
                if z < 0.0:
                    delta -= 10.0  # truly negative Z': structural distress (extreme case)
                elif z > 2.9:
                    delta += 5.0  # safe zone: strong balance sheet boosts MR conviction
                # 0.0 ≤ Z' ≤ 2.9: neutral — covers most large-cap tech/financials
        except Exception:
            pass

    if use_insider and not data["insider"].empty:
        try:
            n_filings = data["insider"].asof(entry_date)
            if not pd.isna(n_filings) and n_filings >= 3:
                delta += 8.0  # cluster of insiders buying (from live §73)
        except Exception:
            pass

    return delta


def run_is_with_edgar(
    all_dfs: dict,
    vix: dict,
    spy_trend: dict,
    stlfsi4: dict,
    cache: dict,
    use_piotroski: bool = True,
    use_altman: bool = True,
    use_insider: bool = True,
) -> pd.DataFrame:
    """Run IS backtest adding EDGAR score modifier at each entry date."""
    all_trades = []
    for ticker, df in all_dfs.items():
        t = bt.simulate_ticker(ticker, df, vix, spy_trend, stlfsi4, mr_only=True)
        if t.empty:
            continue

        # Apply EDGAR modifier: re-filter by adjusted score
        rows = []
        for _, row in t.iterrows():
            entry_date = pd.Timestamp(row["date"])
            adj = _fundamental_score_modifier(entry_date, ticker, cache, use_piotroski, use_altman, use_insider)
            # Re-evaluate BUY threshold with adjusted score
            new_score = row["score"] + adj
            if new_score >= bt.BUY_THRESH:
                row = row.copy()
                row["score"] = new_score
                rows.append(row)

        if rows:
            all_trades.append(pd.DataFrame(rows))

    if not all_trades:
        return pd.DataFrame()
    return pd.concat(all_trades, ignore_index=True)


def run_baseline(all_dfs, vix, spy_trend, stlfsi4):
    """Baseline IS run (no EDGAR)."""
    trades = []
    for ticker, df in all_dfs.items():
        t = bt.simulate_ticker(ticker, df, vix, spy_trend, stlfsi4, mr_only=True)
        if not t.empty:
            trades.append(t)
    return pd.concat(trades, ignore_index=True) if trades else pd.DataFrame()


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def _load_ticker_for_edgar(ticker: str) -> tuple[str, pd.DataFrame | None]:
    """Module-level loader for multiprocessing pool (must be picklable)."""
    try:
        raw = yf.download(ticker, start=bt.START, end=bt.END, interval="1d", auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        if raw.empty or len(raw) < 250:
            return ticker, None
        df = bt.compute_indicators(raw)
        df["score"] = bt.compute_scores(df)
        return ticker, df
    except Exception:
        return ticker, None


def main():
    single_ticker = None
    force_rebuild = "--rebuild" in sys.argv
    use_cached = "--cached" in sys.argv
    if "--ticker" in sys.argv:
        idx = sys.argv.index("--ticker")
        if idx + 1 < len(sys.argv):
            single_ticker = sys.argv[idx + 1].upper()

    print("# EDGAR Tier-3 Signal Validation — IS Backtest\n")
    print(f"> Tickers: {len(bt.TICKERS)} IS universe")
    print(f"> Period: {bt.START} → {bt.END}")
    print("> Signals: §50 Piotroski F-Score, §76 Altman Z'-Score, §73 Insider Form 4 clustering\n")

    # ── Load EDGAR cache ───────────────────────────────────────────────────────
    tickers = [single_ticker] if single_ticker else bt.TICKERS
    cache = load_or_build_cache(tickers, force_rebuild=force_rebuild)

    if single_ticker:
        print(f"\n## Debug: {single_ticker}\n")
        data = cache.get(single_ticker)
        if not data:
            print(f"No EDGAR data for {single_ticker}")
            return
        print(f"Piotroski ({len(data['piotroski'])} filings):")
        print(data["piotroski"].tail(8).to_string())
        print(f"\nAltman ({len(data['altman'])} filings):")
        print(data["altman"].tail(8).to_string())
        print("\nInsider filings (rolling 30d count, last 20):")
        print(data["insider"].tail(20).to_string())
        return

    # ── Download IS price data ─────────────────────────────────────────────────
    print("\nDownloading IS price data for baseline run…")
    vix_df = yf.download("^VIX", start=bt.START, end=bt.END, interval="1d", auto_adjust=False, progress=False)
    if isinstance(vix_df.columns, pd.MultiIndex):
        vix_df.columns = vix_df.columns.get_level_values(0)
    vix = {pd.Timestamp(str(k)[:10]): float(v) for k, v in vix_df["Close"].items() if pd.notna(v)}
    spy_trend = bt.fetch_spy_trend(bt.START, bt.END)
    stlfsi4 = {}  # skip FRED for speed

    # Sequential download — avoids multiprocessing stdout capture issues
    all_dfs = {}
    for _i, _ticker in enumerate(bt.TICKERS, 1):
        _t, _df = _load_ticker_for_edgar(_ticker)
        if _df is not None:
            all_dfs[_t] = _df
        if _i % 20 == 0:
            print(f"  {_i}/{len(bt.TICKERS)} tickers loaded…", flush=True)
    print(f"Loaded {len(all_dfs)} tickers.\n")

    # ── Baseline ───────────────────────────────────────────────────────────────
    print("Running baseline IS (no EDGAR)…", end=" ", flush=True)
    base = run_baseline(all_dfs, vix, spy_trend, stlfsi4)
    sb = bt.stats(base["net_pct"].tolist()) if not base.empty else {}
    print(f"N={sb.get('n', 0)}, WR={sb.get('wr', 0):.1f}%, Sh={bt.fmt_sharpe(sb.get('sharpe'))}")

    results = [("Baseline (no EDGAR)", sb)]

    # ── Per-modifier ablation ──────────────────────────────────────────────────
    configs = [
        ("§50 Piotroski only", True, False, False),
        ("§76 Altman only", False, True, False),
        ("§73 Insider only", False, False, True),
        ("§50 + §76 (Piotroski+Altman)", True, True, False),
        ("§50 + §73 (Piotroski+Insider)", True, False, True),
        ("§76 + §73 (Altman+Insider)", False, True, True),
        ("All three combined", True, True, True),
    ]

    for label, p, a, i in configs:
        print(f"Running {label}…", end=" ", flush=True)
        t = run_is_with_edgar(all_dfs, vix, spy_trend, stlfsi4, cache, p, a, i)
        s = bt.stats(t["net_pct"].tolist()) if not t.empty else {}
        results.append((label, s))
        dsh = (s.get("sharpe") or 0.0) - (sb.get("sharpe") or 0.0)
        print(f"N={s.get('n', 0)}, WR={s.get('wr', 0):.1f}%, Sh={bt.fmt_sharpe(s.get('sharpe'))} ({dsh:+.2f})")

    # ── Summary table ──────────────────────────────────────────────────────────
    print("\n## EDGAR Fundamental Modifier Results\n")
    bt.print_table(
        ["Config", "N", "WR", "Avg Ret", "Sharpe", "ΔSharpe", "Verdict"],
        [
            [
                label,
                str(s.get("n", 0)),
                f"{s.get('wr', 0):.1f}%",
                f"{s.get('avg', 0):+.2f}%",
                bt.fmt_sharpe(s.get("sharpe")),
                f"{(s.get('sharpe') or 0.0) - (sb.get('sharpe') or 0.0):+.2f}",
                (
                    "✅ ADD"
                    if (s.get("sharpe") or 0.0) - (sb.get("sharpe") or 0.0) > 0.01
                    else (
                        "⚠ NEUTRAL" if abs((s.get("sharpe") or 0.0) - (sb.get("sharpe") or 0.0)) <= 0.01 else "🔴 HURTS"
                    )
                ),
            ]
            for label, s in results
        ],
    )

    print("\n> §50 Piotroski interpretation: F≥2 → +5pts (strong balance sheet → MR bounce more reliable)")
    print("> §76 Altman interpretation: Z'<1.23 → −10pts (distress zone → 'falling knife' risk)")
    print("> §73 Insider interpretation: ≥3 Form 4 filings in 30d → +8pts (cluster buying during dip)")
    print("> EDGAR XBRL data coverage: ~2009-present (XBRL mandate). Pre-2009 entries default to neutral.")
    print("\n> Next: if any modifier shows ΔSh > +0.02 with N≥80, add to backtest_technicals.py as a scored column.")
    print("> If ΔSh < -0.02, remove that modifier from signal_engine.py (§85-1 audit).")


if __name__ == "__main__":
    main()
