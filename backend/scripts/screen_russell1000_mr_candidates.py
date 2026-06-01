"""
screen_russell1000_mr_candidates.py — Screen Russell 1000 for MR-quality tickers.

Motivation:
  IS backtest generates ~7 trades/yr on 100 tickers.  Ann.Sharpe = per_trade_Sharpe × √(N/T).
  At SR=0.29 per-trade, scaling from 7→50 trades/yr lifts Ann.Sharpe 0.29→0.77.
  The Russell 1000 (top 1000 by mkt cap) provides a quality-controlled expansion pool.
  ADV ≥ $50M/day ensures institutional liquidity — MR bounces need buyers.

Key differences from screen_sp500_mr_candidates.py:
  1. Source: iShares IWB ETF holdings (≈ Russell 1000)
  2. ADV filter: 30d avg dollar volume ≥ $50M/day (institutional liquidity)
  3. Market cap floor: $3B (Russell 1000 extends to ~$5B lower bound vs S&P 500's $8B+)

Backtest methodology: identical to S&P 500 screener (base discovery pass,
  thresh=35, ATR≥20, sector hold). PASS tickers need §15f+§17f validation.

Usage:
    cd backend
    python scripts/screen_russell1000_mr_candidates.py 2>&1 | tee /tmp/screen_r1000.log
    python scripts/screen_russell1000_mr_candidates.py --fast   # 2006-2016 only
    python scripts/screen_russell1000_mr_candidates.py --adv 75 # raise ADV bar to $75M
"""

from __future__ import annotations

import argparse
import io
import os
import ssl
import sys
import urllib.request
import warnings
from multiprocessing import Pool

import certifi
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

# ── iShares IWB (Russell 1000 ETF) holdings endpoint ─────────────────────────
# Public CSV download — no auth required. skiprows handles the ~9-row metadata
# header that iShares prepends before the actual holdings table.
_ISHARES_IWB_URL = (
    "https://www.ishares.com/us/products/239707/ISHARES-RUSSELL-1000-ETF/"
    "1467271812596.ajax?fileType=csv&fileName=IWB_holdings&dataType=fund"
)

# ── Sector targeting ─────────────────────────────────────────────────────────
# Live-eligible sectors — PASS tickers from these go straight to production candidate list.
_MR_SECTORS = {
    "Technology",
    "Consumer Cyclical",
    "Financial Services",
    "Communication Services",
    "Energy",
}
# Research-only sectors — blocked in live delivery_gates (§10) but included in the IS
# backtest universe for gate calibration. Tickers from these sectors are downloaded and
# backtested; PASS tickers are tagged "(research-only)" and must NOT be added to the live
# engine without first enabling the sector in delivery_gates.
_RESEARCH_ONLY_SECTORS = {
    "Healthcare",  # XLV — §10 hard block; Sharpe −0.17 on full universe; some sub-sectors viable
    "Industrials",  # XLI — §10 hard block; defense/aerospace sub-sector shows MR edge
}
# Hard-blocked: no known MR edge, blocked everywhere.
_BLOCKED_SECTORS = {
    "Real Estate",
    "Utilities",
    "Basic Materials",
    "Consumer Defensive",
}

# Production tickers already in the live engine — skip to avoid duplicates
_SKIP = set(_PRODUCTION_TICKERS) | {
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
    "QCOM",
    "BRK-B",
    "BRK.B",
}

# ── Quality thresholds ────────────────────────────────────────────────────────
MIN_MARKET_CAP_B = 3.0  # $3B — Russell 1000 lower bound; ADV filter does the real work
MIN_BETA = 0.70  # need mean-reversion on fear; low-beta = defensive, not MR
MIN_ADV_M = 50.0  # $50M/day 30d avg dollar volume (institutional MR liquidity)
MIN_WR = 50.0  # win rate floor — let Sharpe be the primary gate
MIN_SHARPE = 0.20  # per-trade Sharpe floor — matches honest forward estimate (IS=0.29)
MIN_TRADES = 5  # minimum trade count
# WATCH tier: surfaces strong tickers where N<10 prevents Sharpe computation
WATCH_MIN_WR = 60.0  # higher WR bar (no Sharpe confirmation)
WATCH_MIN_AVG = 0.5  # minimum avg return %/trade
WATCH_MIN_N = 5  # minimum trade count for WATCH


# ── Constituent loading ───────────────────────────────────────────────────────


def _load_russell1000_ishares() -> list[str]:
    """
    Fetch Russell 1000 tickers from iShares IWB holdings CSV.
    Returns [] immediately if the response is HTML (bot-protection redirect).
    """
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    try:
        req = urllib.request.Request(
            _ISHARES_IWB_URL,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Referer": "https://www.ishares.com",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=20) as resp:
            raw = resp.read(512).decode("utf-8", errors="replace")  # peek first 512 bytes

        # iShares returns Content-Type: text/csv but sends HTML on bot-protection redirect.
        if raw.lstrip().startswith("<!") or "<html" in raw[:100].lower():
            return []  # HTML — not a CSV, give up immediately

        # Need full response for parsing
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")

        lines = raw.splitlines()
        header_row = 0
        for i, line in enumerate(lines):
            if line.startswith("Name") or ",Ticker," in line or line.startswith("Ticker"):
                header_row = i
                break

        df = pd.read_csv(io.StringIO(raw), skiprows=header_row, on_bad_lines="skip")
        if "Ticker" in df.columns:
            ticker_col = df["Ticker"]
        elif len(df.columns) > 1:
            ticker_col = df.iloc[:, 1]
        else:
            return []

        tickers = ticker_col.dropna().astype(str).str.strip().tolist()
        return [
            t.replace(".", "-")
            for t in tickers
            if t and t != "-" and t.lower() != "nan" and 1 <= len(t) <= 6 and t[0].isalpha()
        ]
    except Exception as e:
        print(f"  [warn] iShares IWB fetch failed: {e}")
        return []


def _load_wiki_index(url: str, table_id: str | None = None) -> list[str]:
    """Fetch tickers from a Wikipedia index constituents page."""
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
            html = resp.read()
        kwargs = {"attrs": {"id": table_id}} if table_id else {}
        tables = pd.read_html(html, **kwargs)
        df = tables[0]
        # Handle MultiIndex columns (change history tables)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
        df.columns = df.columns.str.strip()
        sym_col = next((c for c in df.columns if c in ("Symbol", "Ticker")), df.columns[0])
        raw = df[sym_col].dropna().astype(str).tolist()
        return [t.replace(".", "-").strip() for t in raw if t and len(t) <= 6 and t[0].isalpha()]
    except Exception as e:
        print(f"  [warn] Wikipedia fetch failed ({url}): {e}")
        return []


def _load_universe() -> list[str]:
    """
    Load ~900-ticker universe approximating the Russell 1000.

    Strategy (in order):
      1. iShares IWB holdings CSV — detect HTML redirect and skip quickly
      2. Wikipedia S&P 500 + S&P 400 MidCap — covers ~900 tickers, overlaps
         heavily with the Russell 1000 (R1000 ≈ S&P 500 + S&P 400 + ~100 others)
         ADV ≥ $50M filter eliminates the low-quality fringe.

    Returns deduplicated list of normalised ticker strings.
    """
    print("  Trying iShares IWB holdings… ", end="", flush=True)
    tickers = _load_russell1000_ishares()
    if len(tickers) >= 500:
        print(f"ok ({len(tickers)} raw tickers from IWB)")
        return list(dict.fromkeys(tickers))
    print("blocked (HTML response) — using Wikipedia S&P 500 + S&P 400 MidCap")

    sp500 = _load_wiki_index(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        table_id="constituents",
    )
    sp400 = _load_wiki_index(
        "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies",
    )
    combined = list(dict.fromkeys(sp500 + sp400))
    if combined:
        print(f"  S&P 500: {len(sp500)} + S&P 400 MidCap: {len(sp400)} = {len(combined)} unique tickers")
        return combined

    print("  [error] All sources failed. No universe loaded.")
    return []


# ── Metadata fetch ────────────────────────────────────────────────────────────


def _fetch_ticker_meta(ticker: str) -> dict:
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
    if "Healthcare" in sector or "Health" in sector:
        return "Healthcare*"  # * = research-only
    if "Industrials" in sector or "Industrial" in sector:
        return "Industrials*"  # * = research-only
    return "Other"


def _is_research_only(sector_grp: str) -> bool:
    return sector_grp.endswith("*")


# ── ADV computation ───────────────────────────────────────────────────────────


def _compute_adv_30d(df: pd.DataFrame) -> float:
    """30-day average dollar volume = mean(Close × Volume) over last 30 trading days."""
    if df is None or len(df) < 5:
        return 0.0
    tail = df.tail(30)
    adv = (tail["Close"] * tail["Volume"]).mean()
    return float(adv) if pd.notna(adv) else 0.0


# ── Backtest runner ───────────────────────────────────────────────────────────


def _ann_val(sv: dict, period_years: float = 20.0) -> float:
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
    """Base discovery backtest — same methodology as S&P 500 screener."""
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
            buy_thresh_override=35,
            atr_pct_rank_min_override=20.0,
        )
        if tdf.empty:
            return {"n": 0, "wr": 0.0, "avg": 0.0, "sharpe": 0.0, "ann": 0.0, "max_dd": 0.0}
        sv = stats(tdf["net_pct"].tolist())
        sv["ann"] = _ann_val(sv)
        return sv
    except Exception as e:
        print(f"  [warn] {ticker}: backtest error — {e}")
        return {"n": 0, "wr": 0.0, "avg": 0.0, "sharpe": 0.0, "ann": 0.0, "max_dd": 0.0}


# ── Main ──────────────────────────────────────────────────────────────────────


def main(fast: bool = False, adv_m: float = MIN_ADV_M) -> None:
    period_label = "2006–2016 (fast)" if fast else f"2006–{END}"
    min_trades = 3 if fast else MIN_TRADES
    adv_label = f"${adv_m:.0f}M"

    print("# Russell 1000 MR Candidate Screener\n")
    print("> Source: iShares IWB (primary) → Wikipedia S&P 500 + S&P 400 MidCap (~900 tickers)")
    print(f"> Filters: target sectors, mkt cap ≥ ${MIN_MARKET_CAP_B:.0f}B, beta ≥ {MIN_BETA}, ADV ≥ {adv_label}/day")
    print("> Backtest: base discovery (thresh=35, ATR≥20, sector hold). PASS needs §15f+§17f validation.")
    print(f"> Period: {period_label}")
    print(f"> Quality bar: WR ≥ {MIN_WR:.0f}%, per-trade Sharpe ≥ {MIN_SHARPE}, N ≥ {min_trades}\n")

    # ── 1. Universe ───────────────────────────────────────────────────────────
    _section("1. Loading Russell 1000 constituents")
    all_tickers = _load_universe()
    if not all_tickers:
        print("[error] No tickers loaded. Exiting.")
        return

    candidates_raw = [t for t in all_tickers if t not in _SKIP]
    print(f"  {len(all_tickers)} total → {len(candidates_raw)} after removing production/known-bad tickers.\n")

    # ── 2. Sector / beta / mkt cap metadata ──────────────────────────────────
    _section("2. Fetching sector / beta / market cap metadata")
    print(f"  Fetching yfinance info for {len(candidates_raw)} tickers (4-8 min)…\n")

    import concurrent.futures

    meta_list: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(_fetch_ticker_meta, t): t for t in candidates_raw}
        done = 0
        for fut in concurrent.futures.as_completed(futures):
            meta_list.append(fut.result())
            done += 1
            if done % 100 == 0:
                print(f"    {done}/{len(candidates_raw)} metadata fetched…")

    meta_df = pd.DataFrame(meta_list)

    # ── 3. Sector / mkt cap / beta pre-filter ────────────────────────────────
    _section("3. Applying sector / market cap / beta pre-filters")

    in_target = meta_df["sector"].apply(lambda s: any(k in s for k in _MR_SECTORS | _RESEARCH_ONLY_SECTORS))
    in_blocked = meta_df["sector"].apply(lambda s: any(k in s for k in _BLOCKED_SECTORS))
    meta_filtered = meta_df[in_target & ~in_blocked].copy()
    n_research = meta_filtered["sector"].apply(lambda s: any(k in s for k in _RESEARCH_ONLY_SECTORS)).sum()
    print(f"  After sector filter: {len(meta_filtered)} tickers ({n_research} research-only: Healthcare/Industrials)")

    meta_filtered = meta_filtered[meta_filtered["mkt_cap_b"] >= MIN_MARKET_CAP_B]
    print(f"  After mkt cap ≥ ${MIN_MARKET_CAP_B:.0f}B: {len(meta_filtered)} tickers")

    meta_filtered = meta_filtered[meta_filtered["beta"] >= MIN_BETA]
    print(f"  After beta ≥ {MIN_BETA}: {len(meta_filtered)} tickers\n")

    candidates = meta_filtered["ticker"].tolist()
    sector_map = dict(zip(meta_filtered["ticker"], meta_filtered["sector"]))
    beta_map = dict(zip(meta_filtered["ticker"], meta_filtered["beta"].round(2)))
    cap_map = dict(zip(meta_filtered["ticker"], meta_filtered["mkt_cap_b"].round(1)))

    if not candidates:
        print("[error] No candidates passed the pre-filter.")
        return

    # ── 4. Alt data (VIX, SPY, FRED) ─────────────────────────────────────────
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

    # ── 5. Download OHLCV ─────────────────────────────────────────────────────
    _section(f"5. Downloading {len(candidates)} candidate tickers")
    print(f"\nDownloading {len(candidates)} tickers in parallel (8 workers)…\n")

    N_DL = min(8, os.cpu_count() or 4)
    with Pool(N_DL) as p:
        dl_results = p.map(
            process_ticker,
            [(t, vix, spy_trend, stlfsi4, True, None, {}, {}, {}, False, {}, False) for t in candidates],
        )

    all_dfs: dict[str, pd.DataFrame] = {}
    fail_count = 0
    for ticker, _, _, df in dl_results:
        if df is not None and len(df) >= 250:
            all_dfs[ticker] = df
        else:
            fail_count += 1

    print(f"\n  {len(all_dfs)} tickers loaded ({fail_count} failed / insufficient history).")

    # ── 6. ADV filter (computed from OHLCV — more precise than metadata) ──────
    _section(f"6. ADV filter: 30d avg dollar volume ≥ {adv_label}/day")
    adv_map: dict[str, float] = {}
    adv_filtered: dict[str, pd.DataFrame] = {}
    adv_fail = 0
    for ticker, df in all_dfs.items():
        adv = _compute_adv_30d(df)
        adv_map[ticker] = adv
        if adv >= adv_m * 1_000_000:
            adv_filtered[ticker] = df
        else:
            adv_fail += 1

    print(f"  {len(adv_filtered)} tickers pass ADV ≥ {adv_label}/day")
    print(f"  {adv_fail} tickers excluded (insufficient liquidity)\n")

    if not adv_filtered:
        print("[error] No tickers passed the ADV filter.")
        return

    # ── 7. Extra indicators + pre-score ──────────────────────────────────────
    _section("7. Computing extra indicators")
    spy_s = spy_closes if not spy_closes.empty else None
    hyg_s = hyg_closes if not hyg_closes.empty else None
    for df in adv_filtered.values():
        compute_extra_indicators(df, spy_closes=spy_s, hyg_closes=hyg_s)

    pre_dfs = _prescore(adv_filtered, mr_w=0.1)
    print(f"  Pre-scoring done ({len(pre_dfs)} tickers, MR=0.1).")

    # ── 8. Backtest ───────────────────────────────────────────────────────────
    _section("8. Running base discovery backtest on all candidates")
    print("\n  Config: thresh=35, ATR≥20, sector hold. PASS tickers need §15f+§17f validation.\n")

    results = []
    total = len(pre_dfs)
    for i, (ticker, df) in enumerate(pre_dfs.items(), 1):
        sector_raw = sector_map.get(ticker, "")
        sector_grp = _classify_sector(sector_raw)
        sv = _backtest_candidate(ticker, df, sector_grp, vix, spy_trend, stlfsi4)
        adv_val = adv_map.get(ticker, 0.0) / 1_000_000
        sv.update(
            {
                "ticker": ticker,
                "sector_grp": sector_grp,
                "sector_raw": sector_raw,
                "beta": beta_map.get(ticker, 0.0),
                "mkt_cap_b": cap_map.get(ticker, 0.0),
                "adv_30d_m": round(adv_val, 1),
            }
        )
        results.append(sv)
        if i % 10 == 0 or i == total:
            _sh = sv.get("sharpe") or 0.0
            _wr = sv.get("wr") or 0.0
            print(f"  [{i}/{total}] {ticker}: N={sv['n']}, WR={_wr:.0f}%, Sh={_sh:.2f}, ADV=${adv_val:.0f}M")

    results_df = pd.DataFrame(results)
    for _col in ("wr", "avg", "sharpe", "ann", "max_dd", "adv_30d_m"):
        _series = pd.to_numeric(results_df[_col], errors="coerce")
        results_df[_col] = _series.fillna(0.0)
    results_df = results_df.sort_values("ann", ascending=False)

    # ── 9. Full results table ─────────────────────────────────────────────────
    _section("9. Full Candidate Results (ranked by Ann.Sharpe)")
    print(
        f"\n{'Ticker':<8} {'Sector':<12} {'Beta':>5} {'Cap($B)':>8} {'ADV($M)':>8} "
        f"{'N':>4} {'WR':>6} {'Avg%':>7} {'Sharpe':>8} {'Ann.Sh':>8} {'MaxDD':>7}"
    )
    print("-" * 88)
    for _, r in results_df.iterrows():
        n = r.get("n", 0)
        if n < 1:
            continue
        wr_s = f"{(r.get('wr') or 0):.0f}%"
        avg_s = f"{(r.get('avg') or 0):.2f}%"
        sh_s = fmt_sharpe(r.get("sharpe") or 0)
        ann_s = f"{r.get('ann') or 0:.2f}"
        dd_s = f"{(r.get('max_dd') or 0):.1f}%"
        adv_s = f"${r.get('adv_30d_m') or 0:.0f}M"
        flag = (
            " ✓" if ((r.get("wr") or 0) >= MIN_WR and (r.get("sharpe") or 0) >= MIN_SHARPE and n >= min_trades) else ""
        )
        print(
            f"{r['ticker']:<8} {r['sector_grp']:<12} {r['beta']:>5.2f} "
            f"{r['mkt_cap_b']:>7.0f}B {adv_s:>8} "
            f"{n:>4} {wr_s:>6} {avg_s:>7} {sh_s:>8} {ann_s:>8} {dd_s:>7}{flag}"
        )

    # ── 10. PASS / FAIL summary ───────────────────────────────────────────────
    _section("10. Candidates Meeting Quality Bar")
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
        live_pass = pass_df[~pass_df["sector_grp"].apply(_is_research_only)]
        research_pass = pass_df[pass_df["sector_grp"].apply(_is_research_only)]

        print("\n### PASS (live-eligible) — Copy into production TICKERS universe:\n")
        pass_by_sector: dict[str, list[str]] = {}
        for _, r in live_pass.iterrows():
            pass_by_sector.setdefault(r["sector_grp"], []).append(r["ticker"])
        for sector, tickers in sorted(pass_by_sector.items()):
            print(f"  # {sector}")
            print(f"  {','.join(sorted(tickers))}")
            print()
        live_tickers = sorted(live_pass["ticker"].tolist())
        print(f"  # All {len(live_tickers)} live PASS tickers (copy-paste ready):")
        for chunk in [live_tickers[i : i + 10] for i in range(0, len(live_tickers), 10)]:
            print(f"  {', '.join(repr(t) for t in chunk)},")

        if not research_pass.empty:
            print("\n### PASS (research-only — DO NOT add to live engine without enabling sector gate):\n")
            for _, r in research_pass.iterrows():
                print(
                    f"  {r['ticker']:<8} {r['sector_grp']:<14} WR={r['wr']:.0f}%  Avg={r['avg']:.2f}%  Sh={r['sharpe'] or 0:.2f}"
                )

    if not fail_df.empty:
        print("\n### FAIL — Do NOT add (tested, below quality bar):\n")
        fail_tickers = sorted(fail_df["ticker"].tolist())
        for i in range(0, len(fail_tickers), 15):
            print(f"  {', '.join(fail_tickers[i : i + 15])}")

    # WATCH tier: N<10 so Sharpe not computed, but WR and Avg look strong enough
    # to warrant a full 20yr validation run.
    _pass_set = set(pass_df["ticker"].tolist())
    watch_df = (
        results_df[
            (results_df["wr"] >= WATCH_MIN_WR)
            & (results_df["avg"] >= WATCH_MIN_AVG)
            & (results_df["n"] >= WATCH_MIN_N)
            & ~results_df["ticker"].isin(_pass_set)
        ]
        .sort_values("wr", ascending=False)
        .copy()
    )

    if not watch_df.empty:
        print(
            f"\n### WATCH — WR ≥ {WATCH_MIN_WR:.0f}%, Avg ≥ {WATCH_MIN_AVG:.1f}%, N ≥ {WATCH_MIN_N}, no Sharpe (N<10). Validate in 20yr mode:\n"
        )
        print(f"  {'Ticker':<8} {'Sector':<14} {'N':>4} {'WR':>6} {'Avg%':>7} {'ADV($M)':>9} {'Note'}")
        print(f"  {'-' * 62}")
        for _, r in watch_df.iterrows():
            note = "(research-only)" if _is_research_only(r["sector_grp"]) else ""
            print(
                f"  {r['ticker']:<8} {r['sector_grp']:<14} {r['n']:>4} "
                f"{(r.get('wr') or 0):.0f}% {(r.get('avg') or 0):>6.2f}% "
                f"${r.get('adv_30d_m') or 0:>7.0f}M  {note}"
            )
        watch_tickers = sorted(watch_df["ticker"].tolist())
        print(f"\n  # All {len(watch_tickers)} WATCH tickers:")
        for chunk in [watch_tickers[i : i + 10] for i in range(0, len(watch_tickers), 10)]:
            print(f"  {', '.join(chunk)}")

    # ── 11. ADV distribution ──────────────────────────────────────────────────
    _section("11. ADV Distribution of PASS Tickers")
    if not pass_df.empty:
        adv_vals = pass_df["adv_30d_m"].sort_values(ascending=False)
        print(f"\n  Median ADV: ${adv_vals.median():.0f}M/day")
        print(f"  Min ADV (lowest-liquidity PASS): ${adv_vals.min():.0f}M/day")
        print(f"  Max ADV: ${adv_vals.max():.0f}M/day")
        # Liquidity tier breakdown
        tier1 = (adv_vals >= 500).sum()
        tier2 = ((adv_vals >= 100) & (adv_vals < 500)).sum()
        tier3 = ((adv_vals >= 50) & (adv_vals < 100)).sum()
        print("\n  Liquidity tiers:")
        print(f"    ADV ≥ $500M (mega-cap liquidity): {tier1} tickers")
        print(f"    ADV $100–500M (large-cap):        {tier2} tickers")
        print(f"    ADV $50–100M (mid-cap boundary):  {tier3} tickers")

    # ── 12. Sharpe projection ─────────────────────────────────────────────────
    _section("12. Annualised Sharpe Projection")
    n_pass = len(pass_df)
    n_current = 100  # current production universe
    n_total = n_current + n_pass

    # Current: ~7 trades/yr on 100 tickers = 0.07 trades/ticker/yr
    trades_per_ticker_yr = 7.0 / 100.0
    new_trades_est = n_total * trades_per_ticker_yr * 20  # 20yr total
    projected_ann = 0.29 * (new_trades_est / 20) ** 0.5  # IS per-trade Sharpe = 0.29

    print(f"\n  Current:  {n_current} tickers → ~7 trades/yr → IS Ann.Sharpe 0.29 (per-trade)")
    print(f"  New PASS: {n_pass} tickers from Russell 1000 (ADV ≥ {adv_label}/day)")
    print(f"  Combined: {n_total} tickers → ~{n_total * trades_per_ticker_yr:.0f} trades/yr (projected)")
    print(f"  Projected Ann.Sharpe (IS per-trade SR=0.29): {projected_ann:.2f}")
    print(f"  Conservative (forward SR=0.15):              {0.15 * (new_trades_est / 20) ** 0.5:.2f}")
    print()
    print("  Note: Run §15f+§17f backtest on PASS tickers before adding to production.")
    print("  Validate per-ticker Sharpe ≥ 0.35 individually. Then add to TICKERS in")
    print("  backtest_technicals.py and re-run IS + OOS to confirm aggregate metrics hold.")
    print(f"\n*Russell 1000 MR Candidate Screener · ADV ≥ {adv_label} · {period_label}*")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Screen Russell 1000 for MR-quality tickers.")
    ap.add_argument("--fast", action="store_true", help="2006–2016 only (~40min vs ~120min)")
    ap.add_argument(
        "--adv",
        type=float,
        default=MIN_ADV_M,
        metavar="M",
        help=f"Minimum 30d avg dollar volume in $M/day (default: {MIN_ADV_M})",
    )
    args = ap.parse_args()
    main(fast=args.fast, adv_m=args.adv)
