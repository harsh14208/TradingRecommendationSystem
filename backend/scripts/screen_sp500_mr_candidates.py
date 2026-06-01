"""
screen_sp500_mr_candidates.py — Screen S&P 500 for MR-quality tickers.

Mathematical case: Ann.Sharpe = per_trade_Sharpe × √(N/20).
  Current (42 tickers, N≈66): 0.70 × √(66/20) = 1.27
  Target  (150 tickers, N≈235): 0.60 × √(235/20) = 2.05

Screening criteria:
  1. S&P 500 constituent (stable, liquid, institutional grade)
  2. GICS sector: Technology, Consumer Discretionary, Financials
     (confirmed positive MR edge in §15a/§15b/§15c/§16a research)
  3. Exclude confirmed-negative sectors: Healthcare, Industrials,
     Real Estate, Energy, Utilities, Materials (§16a confirmed)
  4. Market cap ≥ $10B (institutional liquidity — MR bounces need buyers)
  5. Beta > 0.7 (mean-reverts on fear; low-beta stocks are defensive, not MR)
  6. Exclude tickers already in the production TICKERS universe

Backtest gate (§17f config — our current best):
  MR-only, ATR%rank [20, 70], return jump < −6% blocked,
  IBS-sole-trigger requires ≥5 days below SMA20.
  Hold days: Tech=5d, Financials=7d, Consumer=10d.

Quality threshold for inclusion:
  WR ≥ 55%, per-trade Sharpe ≥ 0.35, N ≥ 5 trades over 20yr.

Output:
  - Full ranked table (all candidates)
  - PASS list (meeting threshold) — copy into _STRONG universe

Usage:
    cd backend
    python scripts/screen_sp500_mr_candidates.py 2>&1 | tee /tmp/screen_sp500.log
    # Fast mode (2006–2016 only, ~30min): --fast
    python scripts/screen_sp500_mr_candidates.py --fast
"""

from __future__ import annotations

import argparse
import os
import sys
import warnings
from multiprocessing import Pool

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _p in [_PARENT, _HERE]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from backtest_technicals import (
    END,
    fetch_spy_trend,
    fetch_stlfsi4,
    fmt_sharpe,
    process_ticker,
    simulate_ticker,
    stats,
)
from backtest_technicals import (
    TICKERS as _PRODUCTION_TICKERS,
)
from signal_alpha_decomposition import (
    _download_etf_closes,
    _prescore,
    _section,
    compute_extra_indicators,
)

# ── Target sectors (GICS names as returned by yfinance info["sector"]) ────────
_MR_SECTORS = {
    "Technology",
    "Consumer Cyclical",  # yfinance name for Consumer Discretionary
    "Financial Services",  # yfinance name for Financials
    "Communication Services",  # partial overlap — will backtest-gate individually
    "Energy",  # §16g: Ann=0.44, WR=75% with VIX≥15+thresh=40+hold=5d
}

# Confirmed-negative sectors from §16g — exclude regardless
_BLOCKED_SECTORS = {
    "Healthcare",
    "Industrials",
    "Real Estate",
    "Utilities",
    "Basic Materials",
    "Consumer Defensive",  # XLP — low-beta, macro-driven
}

# Current production tickers — skip (already included or known bad)
_SKIP = set(_PRODUCTION_TICKERS) | {
    # Known bad: confirmed weak in §15a pruning or bad-ticker list
    "MU",
    "MCD",
    "KO",
    "WMT",
    "PG",
    "PFE",
    "MRK",
    "ABBV",
    "TMO",
    "NKE",
    "TXN",
    "QCOM",  # removed from TICKERS for documented reasons
    "BRK-B",
    "BRK.B",  # Berkshire — no options, no MR edge
}

MIN_MARKET_CAP_B = 10.0  # $10B minimum
MIN_BETA = 0.70  # beta floor — need mean-reversion on fear
MIN_WR = 55.0  # win rate floor — stats() returns percent (0–100), not decimal
MIN_SHARPE = 0.35  # per-trade Sharpe floor for inclusion
MIN_TRADES = 5  # minimum trade count (statistical significance)


def _load_sp500_wiki() -> pd.DataFrame:
    """Fetch S&P 500 constituents from Wikipedia."""
    import ssl
    import urllib.request

    import certifi

    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
            html = resp.read()
        tables = pd.read_html(html, attrs={"id": "constituents"})
        df = tables[0]
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"  [warn] Wikipedia fetch failed: {e}")
        return pd.DataFrame()


def _fetch_ticker_meta(ticker: str) -> dict:
    """Fetch market cap, beta, sector from yfinance info (cached per run)."""
    try:
        info = yf.Ticker(ticker).info
        sector = info.get("sector") or info.get("sectorDisp", "")
        mkt_cap_b = (info.get("marketCap") or 0) / 1e9
        beta = info.get("beta") or 0.0
        name = info.get("shortName") or ticker
        return {"ticker": ticker, "sector": sector, "mkt_cap_b": mkt_cap_b, "beta": beta, "name": name}
    except Exception:
        return {"ticker": ticker, "sector": "", "mkt_cap_b": 0.0, "beta": 0.0, "name": ticker}


def _classify_sector(sector: str) -> str:
    """Map yfinance sector to our MR sector groups."""
    if "Technology" in sector:
        return "Tech"
    if "Consumer Cyclical" in sector:
        return "Consumer"
    if "Financial" in sector:
        return "Financial"
    if "Communication" in sector:
        return "Communication"
    if "Energy" in sector:
        return "Energy"
    return "Other"


def _ann_val(sv: dict, period_years: float = 20.0) -> float:
    """Annualised Sharpe: per_trade_Sharpe × √(N / years)."""
    sh = sv.get("sharpe", 0.0) or 0.0
    n = sv.get("n", 0) or 0
    if n < 2:
        return 0.0
    return round(sh * (n / period_years) ** 0.5, 3)


def _backtest_candidate(
    ticker: str,
    df: pd.DataFrame,
    sector_group: str,
    vix: dict,
    spy_trend: dict,
    stlfsi4: dict,
) -> dict:
    """
    Run baseline discovery backtest on a single candidate. Returns stats dict.

    Uses base config (MR=0.1, thresh=35, ATR≥20, no VIX floor, hold=10d) for discovery.
    Sector-specific thresholds (40-42) + VIX floors collapse N to 0-2 trades in 20yr
    for new candidates — insufficient for statistical screening.
    The base config generates 3-8 trades per ticker, enough for the MIN_TRADES=5 bar.
    Top candidates (WR≥55%, Sh≥0.35, N≥5) should be validated with §15f+§17f gates.
    """
    # Base discovery config: low thresh + no VIX floor generates enough N
    # Sector hold days preserved (doesn't affect N, only which endpoint is measured)
    if sector_group == "Tech":
        hold_days = 5
    elif sector_group == "Financial":
        hold_days = 7
    elif sector_group == "Energy":
        hold_days = 5
    else:
        hold_days = 10

    try:
        tdf = simulate_ticker(
            ticker,
            df,
            vix,
            spy_trend,
            stlfsi4,
            mr_only=True,
            hold_days_override=hold_days,
            buy_thresh_override=35,  # global base threshold for max N discovery
            atr_pct_rank_min_override=20.0,  # ATR≥20 quality gate (always on)
            # No VIX floor, no ATR ceiling, no jump filter — discovery pass
        )
        if tdf.empty:
            return {"n": 0, "wr": 0.0, "avg": 0.0, "sharpe": 0.0, "ann": 0.0, "max_dd": 0.0}
        sv = stats(tdf["net_pct"].tolist())
        sv["ann"] = _ann_val(sv)
        return sv
    except Exception as e:
        print(f"  [warn] {ticker}: backtest error — {e}")
        return {"n": 0, "wr": 0.0, "avg": 0.0, "sharpe": 0.0, "ann": 0.0, "maxdd": 0.0}


def main(fast: bool = False) -> None:
    period_label = "2006–2016 (fast)" if fast else f"2006–{END}"
    # §17f gates generate ~1.5 trades/ticker/20yr on strong sectors.
    # Fast mode (10yr) = ~0.75 trades/ticker → use N≥3 to surface candidates.
    # Full mode (20yr) uses the standard N≥5 bar for statistical significance.
    min_trades = 3 if fast else MIN_TRADES
    print("# S&P 500 MR Candidate Screener\n")
    print("> Target: Tech + Consumer Disc + Financials + Energy + Comm, mktcap ≥ $10B, beta ≥ 0.7")
    print(
        "> Backtest: base discovery (thresh=35, ATR≥20, sector hold, no VIX/ceiling/jump). PASS needs §15f+§17f validation."
    )
    print(f"> Period: {period_label}")
    print(f"> Quality bar: WR ≥ {MIN_WR:.0f}%, per-trade Sharpe ≥ {MIN_SHARPE}, N ≥ {min_trades}\n")

    # ── 1. Get S&P 500 constituent list ───────────────────────────────────────
    _section("1. Loading S&P 500 constituents from Wikipedia")
    sp500_df = _load_sp500_wiki()
    if sp500_df.empty:
        print("[error] Could not load S&P 500 list. Check internet connection.")
        return

    sym_col = "Symbol" if "Symbol" in sp500_df.columns else sp500_df.columns[0]
    all_sp500 = [t.replace(".", "-") for t in sp500_df[sym_col].tolist()]
    print(f"  {len(all_sp500)} S&P 500 constituents loaded.")

    # Candidates = S&P 500 minus skip list
    candidates_raw = [t for t in all_sp500 if t not in _SKIP]
    print(f"  {len(candidates_raw)} after removing production tickers and known-bad.\n")

    # ── 2. Fetch metadata (sector, beta, mkt cap) in parallel ─────────────────
    _section("2. Fetching sector/beta/market cap metadata")
    print(f"  Fetching yfinance info for {len(candidates_raw)} tickers (may take 3-5 min)…\n")

    import concurrent.futures

    meta_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(_fetch_ticker_meta, t): t for t in candidates_raw}
        done = 0
        for fut in concurrent.futures.as_completed(futures):
            meta_list.append(fut.result())
            done += 1
            if done % 50 == 0:
                print(f"    {done}/{len(candidates_raw)} metadata fetched…")

    meta_df = pd.DataFrame(meta_list)

    # ── 3. Apply sector + mkt cap + beta filters ──────────────────────────────
    _section("3. Applying sector / market cap / beta filters")

    # Keep only target sectors
    in_target = meta_df["sector"].apply(lambda s: any(k in s for k in _MR_SECTORS))
    in_blocked = meta_df["sector"].apply(lambda s: any(k in s for k in _BLOCKED_SECTORS))
    meta_filtered = meta_df[in_target & ~in_blocked].copy()
    print(f"  After sector filter: {len(meta_filtered)} tickers")

    meta_filtered = meta_filtered[meta_filtered["mkt_cap_b"] >= MIN_MARKET_CAP_B]
    print(f"  After mkt cap ≥ ${MIN_MARKET_CAP_B:.0f}B filter: {len(meta_filtered)} tickers")

    meta_filtered = meta_filtered[meta_filtered["beta"] >= MIN_BETA]
    print(f"  After beta ≥ {MIN_BETA} filter: {len(meta_filtered)} tickers\n")

    candidates = meta_filtered["ticker"].tolist()
    sector_map = dict(zip(meta_filtered["ticker"], meta_filtered["sector"]))
    beta_map = dict(zip(meta_filtered["ticker"], meta_filtered["beta"].round(2)))
    cap_map = dict(zip(meta_filtered["ticker"], meta_filtered["mkt_cap_b"].round(1)))

    if not candidates:
        print("[error] No candidates passed the filter.")
        return

    # ── 4. Fetch alt-data (VIX, SPY, FRED) ───────────────────────────────────
    _section("4. Fetching VIX / SPY / STLFSI4")
    bt_start = "2006-01-01"
    bt_end = "2016-12-31" if fast else END

    print("Fetching VIX…", end=" ", flush=True)
    try:
        vix_df = yf.download("^VIX", start=bt_start, end=bt_end, interval="1d", auto_adjust=False, progress=False)
        if isinstance(vix_df.columns, pd.MultiIndex):
            vix_df.columns = vix_df.columns.get_level_values(0)
        vix = {pd.Timestamp(str(k)[:10]): float(v) for k, v in vix_df["Close"].items() if pd.notna(v)}
        print(f"ok ({len(vix)} bars)")
    except Exception as e:
        vix = {}
        print(f"failed ({e})")

    print("Fetching SPY trend…", end=" ", flush=True)
    spy_trend = fetch_spy_trend(bt_start, bt_end)
    print(f"ok ({len(spy_trend)} bars)")

    print("Fetching FRED STLFSI4…", end=" ", flush=True)
    _fred_key = os.getenv("FRED_API_KEY", "")
    if not _fred_key:
        try:
            with open(os.path.join(_PARENT, ".env")) as ef:
                for line in ef:
                    if line.startswith("FRED_API_KEY="):
                        _fred_key = line.strip().split("=", 1)[1]
        except Exception:
            pass
    stlfsi4 = fetch_stlfsi4(bt_start, bt_end, _fred_key)
    print(f"ok ({len(stlfsi4)} obs)" if stlfsi4 else "skipped")

    spy_closes = _download_etf_closes("SPY", bt_start, bt_end, "SPY")
    hyg_closes = _download_etf_closes("HYG", bt_start, bt_end, "HYG")

    # ── 5. Download and process OHLCV for all candidates ──────────────────────
    _section(f"5. Downloading {len(candidates)} candidate tickers")
    print(f"\nDownloading {len(candidates)} tickers in parallel (8 workers)…\n")

    N_DL = min(8, os.cpu_count() or 4)
    with Pool(N_DL) as p:
        dl_results = p.map(
            process_ticker,
            [(t, vix, spy_trend, stlfsi4, True) for t in candidates],
        )

    all_dfs: dict = {}
    fail_count = 0
    for ticker, _t, _bh, df in dl_results:
        if df is not None and len(df) >= 250:
            all_dfs[ticker] = df
        else:
            fail_count += 1

    print(f"\n  {len(all_dfs)} tickers loaded ({fail_count} failed / insufficient history).")

    # ── 6. Compute extra indicators + pre-score ───────────────────────────────
    _section("6. Computing extra indicators")
    spy_s = spy_closes if not spy_closes.empty else None
    hyg_s = hyg_closes if not hyg_closes.empty else None
    for df in all_dfs.values():
        compute_extra_indicators(df, spy_closes=spy_s, hyg_closes=hyg_s)

    pre_dfs = _prescore(all_dfs, mr_w=0.1)
    print(f"  Pre-scoring done ({len(pre_dfs)} tickers, MR=0.1).")

    # ── 7. Run §17f backtest on each candidate ─────────────────────────────────
    _section("7. Running §17f backtest on all candidates")
    print("\n  Config: base discovery — thresh=35, ATR≥20, sector hold. PASS tickers need §15f+§17f validation.\n")

    results = []
    total = len(pre_dfs)
    for i, (ticker, df) in enumerate(pre_dfs.items(), 1):
        sector_raw = sector_map.get(ticker, "")
        sector_grp = _classify_sector(sector_raw)
        sv = _backtest_candidate(ticker, df, sector_grp, vix, spy_trend, stlfsi4)
        sv.update(
            {
                "ticker": ticker,
                "sector_grp": sector_grp,
                "sector_raw": sector_raw,
                "beta": beta_map.get(ticker, 0.0),
                "mkt_cap_b": cap_map.get(ticker, 0.0),
            }
        )
        results.append(sv)
        if i % 10 == 0 or i == total:
            _sh = sv.get("sharpe") or 0.0
            _wr = sv.get("wr") or 0.0
            print(f"  [{i}/{total}] {ticker}: N={sv['n']}, WR={_wr:.0f}%, Sh={_sh:.2f}")

    results_df = pd.DataFrame(results)
    for _col in ("wr", "avg", "sharpe", "ann", "max_dd"):
        _series = pd.to_numeric(results_df[_col], errors="coerce")
        results_df[_col] = _series.fillna(0.0)
    results_df = results_df.sort_values("ann", ascending=False)

    # ── 8. Print full results table ────────────────────────────────────────────
    _section("8. Full Candidate Results (ranked by Ann.Sharpe)")
    print(
        f"\n{'Ticker':<8} {'Sector':<12} {'Beta':>5} {'Cap($B)':>8} {'N':>4} {'WR':>6} {'Avg%':>7} {'Sharpe':>8} {'Ann.Sh':>8} {'MaxDD':>7}"
    )
    print("-" * 75)
    for _, r in results_df.iterrows():
        n = r.get("n", 0)
        if n < 1:
            continue
        wr_s = f"{(r.get('wr') or 0):.0f}%"
        avg_s = f"{(r.get('avg') or 0):.2f}%"
        sh_s = fmt_sharpe(r.get("sharpe") or 0)
        ann_s = f"{r.get('ann') or 0:.2f}"
        dd_s = f"{(r.get('max_dd') or 0):.1f}%"
        flag = (
            " ✓" if ((r.get("wr") or 0) >= MIN_WR and (r.get("sharpe") or 0) >= MIN_SHARPE and n >= min_trades) else ""
        )
        print(
            f"{r['ticker']:<8} {r['sector_grp']:<12} {r['beta']:>5.2f} {r['mkt_cap_b']:>7.0f}B {n:>4} {wr_s:>6} {avg_s:>7} {sh_s:>8} {ann_s:>8} {dd_s:>7}{flag}"
        )

    # ── 9. PASS / FAIL summary ─────────────────────────────────────────────────
    _section("9. Candidates Meeting Quality Bar")
    pass_df = results_df[
        (results_df["wr"] >= MIN_WR) & (results_df["sharpe"] >= MIN_SHARPE) & (results_df["n"] >= min_trades)
    ].copy()

    fail_df = results_df[
        (results_df["n"] >= min_trades) & ~((results_df["wr"] >= MIN_WR) & (results_df["sharpe"] >= MIN_SHARPE))
    ].copy()

    insufficient_df = results_df[results_df["n"] < min_trades].copy()

    print(f"\n  PASS: {len(pass_df)} tickers (WR ≥ {MIN_WR:.0f}%, Sharpe ≥ {MIN_SHARPE}, N ≥ {min_trades})")
    print(f"  FAIL: {len(fail_df)} tickers (tested but below quality bar)")
    print(f"  SKIP: {len(insufficient_df)} tickers (N < {min_trades} — insufficient signal history)")

    if not pass_df.empty:
        print("\n### PASS — Copy into _STRONG universe:\n")
        pass_by_sector = {}
        for _, r in pass_df.iterrows():
            pass_by_sector.setdefault(r["sector_grp"], []).append(r["ticker"])
        for sector, tickers in sorted(pass_by_sector.items()):
            print(f"  # {sector}")
            print(f"  {','.join(sorted(tickers))}")
            print()

        # Print as Python list for direct copy-paste
        all_pass_tickers = sorted(pass_df["ticker"].tolist())
        print(f"  # All {len(all_pass_tickers)} PASS tickers (sorted):")
        chunks = [all_pass_tickers[i : i + 10] for i in range(0, len(all_pass_tickers), 10)]
        for chunk in chunks:
            quoted = ", ".join(f'"{t}"' for t in chunk)
            print(f"  {quoted},")

    if not fail_df.empty:
        print("\n### FAIL — Do NOT add (tested, below quality bar):\n")
        fail_tickers = sorted(fail_df["ticker"].tolist())
        for i in range(0, len(fail_tickers), 15):
            print(f"  {', '.join(fail_tickers[i : i + 15])}")

    # ── 10. Projection ─────────────────────────────────────────────────────────
    _section("10. Annualised Sharpe Projection")
    n_pass = len(pass_df)
    n_current = 42  # strong universe size
    n_total = n_current + n_pass

    current_per_trade_sh = 0.70
    new_trades_est = n_total * (66 / n_current)  # linear trade count scale
    projected_ann = current_per_trade_sh * (new_trades_est / 20) ** 0.5

    print(f"\n  Current:  {n_current} tickers → N≈66 trades/yr → Ann.Sharpe ≈ 1.27")
    print(f"  New PASS: {n_pass} tickers passing quality bar")
    print(f"  Combined: {n_total} tickers → N≈{new_trades_est:.0f} trades/yr (projected)")
    print(f"  Projected Ann.Sharpe: {projected_ann:.2f} (at 0.70 per-trade Sharpe)")
    print(f"  Conservative (0.60 per-trade):  {0.60 * (new_trades_est / 20) ** 0.5:.2f}")
    print("\n  Note: Run §17f backtest on PASS tickers against full 20yr period before")
    print("  adding to production. Validate per-ticker Sharpe ≥ 0.35 individually.")
    print(f"\n*S&P 500 MR Candidate Screener · base discovery (thresh=35, ATR≥20) · {period_label}*")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="2006–2016 only (~30min vs ~90min)")
    args = ap.parse_args()
    main(fast=args.fast)
