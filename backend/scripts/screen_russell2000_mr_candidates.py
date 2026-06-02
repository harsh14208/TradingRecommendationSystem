"""
screen_russell2000_mr_candidates.py — Screen Russell 2000 for MR-quality tickers.

Motivation:
  Russell 2000 (small-cap $300M–$2B) extends the MR universe beyond large-caps.
  Small-caps have higher idiosyncratic risk but also faster mean-reversion cycles
  driven by sentiment overshoots. Quality screen focuses on highest-liquidity R2000
  names to ensure 0.5% friction stays reasonable.

Key differences from screen_russell1000_mr_candidates.py:
  1. Source: iShares IWM ETF holdings (≈ Russell 2000)
  2. ADV filter: 30d avg dollar volume ≥ $10M/day (R2000 is lower-liquidity)
  3. Market cap floor: $300M (R2000 extends to ~$300M lower bound)
  4. Healthcare: research-only (small-cap health has binary FDA/trial event risk,
     unlike large-cap health which is confirmed live-eligible via cross-sectional model)
  5. Quality bar: WR ≥ 60% (tighter than R1000's 55% — more noise at small-cap)
  6. Minimum Sharpe: 0.35 (same as R1000 — no relaxation for noisier signals)

Backtest methodology: identical to R1000 screener (base discovery pass,
  thresh=35, ATR≥20, sector hold). PASS tickers need §15f+§17f validation.

Usage:
    cd backend
    python scripts/screen_russell2000_mr_candidates.py 2>&1 | tee /tmp/screen_r2000.log
    python scripts/screen_russell2000_mr_candidates.py --fast   # 2006-2016 only
    python scripts/screen_russell2000_mr_candidates.py --adv 20 # raise ADV bar to $20M
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
from backtest_technicals import (
    HELD_OUT_TICKERS as _OOS_TICKERS,
)
from signal_alpha_decomposition import (
    _download_etf_closes,
    _prescore,
    _section,
    compute_extra_indicators,
)

# ── iShares IWM (Russell 2000 ETF) holdings endpoint ────────────────────────
_ISHARES_IWM_URL = (
    "https://www.ishares.com/us/products/239710/ISHARES-RUSSELL-2000-ETF/"
    "1467271812596.ajax?fileType=csv&fileName=IWM_holdings&dataType=fund"
)

# ── Sector targeting ─────────────────────────────────────────────────────────
# Live-eligible sectors (same as R1000, but Healthcare is research-only for small-caps).
_MR_SECTORS = {
    "Technology",
    "Consumer Cyclical",
    "Financial Services",
    "Communication Services",
    "Energy",
}
# Research-only: have MR edge at large-cap but risky at small-cap.
# Healthcare: binary FDA/clinical trial events dominate at small-cap.
# Industrials: capex cycle still marginal (t=+0.48 in cross-sectional model).
_RESEARCH_ONLY_SECTORS = {
    "Healthcare",  # small-cap health = pharma/biotech binary risk; unlike confirmed large-cap XLV
    "Industrials",  # marginal cross-sectional evidence; valid sub-sector: defense electronics
}
# Hard-blocked: no MR edge.
_BLOCKED_SECTORS = {
    "Real Estate",
    "Utilities",
    "Basic Materials",
    "Consumer Defensive",
}

# Skip tickers already in production IS or OOS universes
_SKIP = (
    set(_PRODUCTION_TICKERS)
    | set(_OOS_TICKERS)
    | {
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
)

# ── Quality thresholds ────────────────────────────────────────────────────────
MIN_MARKET_CAP_B = 0.3  # $300M — Russell 2000 lower bound
MAX_MARKET_CAP_B = 10.0  # $10B — above this it's really mid/large-cap
MIN_BETA = 0.65  # slightly lower than R1000 (small-caps have higher idiosync vol)
MIN_ADV_M = 10.0  # $10M/day (R2000 lower liquidity)
MIN_WR = 60.0  # tighter than R1000's 55% — more noise at small-cap
MIN_SHARPE = 0.35  # same as R1000
MIN_TRADES = 5
WATCH_MIN_WR = 65.0
WATCH_MIN_AVG = 0.6
WATCH_MIN_N = 4


# ── Constituent loading ───────────────────────────────────────────────────────


def _load_russell2000_ishares() -> list[str]:
    """Fetch Russell 2000 tickers from iShares IWM holdings CSV."""
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    try:
        req = urllib.request.Request(
            _ISHARES_IWM_URL,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Referer": "https://www.ishares.com",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=20) as resp:
            raw = resp.read(512).decode("utf-8", errors="replace")

        if raw.lstrip().startswith("<!") or "<html" in raw[:100].lower():
            return []

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
        print(f"  [warn] iShares IWM fetch failed: {e}")
        return []


def _load_wiki_index(url: str, table_id: str | None = None) -> list[str]:
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
            html = resp.read()
        kwargs = {"attrs": {"id": table_id}} if table_id else {}
        tables = pd.read_html(html, **kwargs)
        df = tables[0]
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
    """Load ~2000-ticker universe approximating the Russell 2000.

    Strategy:
      1. iShares IWM holdings CSV (primary)
      2. Wikipedia S&P 600 SmallCap + S&P 400 MidCap (fallback — ~1500 names)
    """
    print("  Trying iShares IWM holdings… ", end="", flush=True)
    tickers = _load_russell2000_ishares()
    if len(tickers) >= 500:
        print(f"ok ({len(tickers)} raw tickers from IWM)")
        return list(dict.fromkeys(tickers))
    print("blocked (HTML response) — using Wikipedia S&P 600 SmallCap + S&P 400 MidCap")

    sp600 = _load_wiki_index("https://en.wikipedia.org/wiki/List_of_S%26P_600_companies")
    sp400 = _load_wiki_index("https://en.wikipedia.org/wiki/List_of_S%26P_400_companies")
    combined = list(dict.fromkeys(sp600 + sp400))
    if combined:
        print(f"  S&P 600 SmallCap: {len(sp600)} + S&P 400 MidCap: {len(sp400)} = {len(combined)} unique tickers")
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
        return "Healthcare*"  # research-only at small-cap (binary FDA risk)
    if "Industrials" in sector or "Industrial" in sector:
        return "Industrials*"  # research-only (marginal cross-sectional evidence)
    return "Other"


def _is_research_only(sector_grp: str) -> bool:
    return sector_grp.endswith("*")


# ── ADV computation ───────────────────────────────────────────────────────────


def _compute_adv_30d(df: pd.DataFrame) -> float:
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
    """Base discovery backtest — identical methodology to R1000 screener."""
    # Small-caps: use sector-specific hold but cap at 10d (enough for small-cap bounce)
    if sector_group == "Tech":
        hold_days = 5
    elif sector_group == "Financial":
        hold_days = 7
    elif sector_group == "Energy":
        hold_days = 5
    elif sector_group in ("Healthcare*", "Industrials*"):
        hold_days = 10
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

    print("# Russell 2000 MR Candidate Screener\n")
    print("> Source: iShares IWM (primary) → Wikipedia S&P 600 SmallCap + S&P 400 MidCap (~1500 tickers)")
    print(
        f"> Filters: target sectors, mkt cap ${MIN_MARKET_CAP_B:.1f}B–${MAX_MARKET_CAP_B:.0f}B, "
        f"beta ≥ {MIN_BETA}, ADV ≥ {adv_label}/day"
    )
    print("> Healthcare: research-only at small-cap (binary FDA risk; large-cap XLV confirmed live-eligible)")
    print("> Backtest: base discovery (thresh=35, ATR≥20, sector hold). PASS needs §15f+§17f validation.")
    print(f"> Period: {period_label}")
    print(f"> Quality bar: WR ≥ {MIN_WR:.0f}%, per-trade Sharpe ≥ {MIN_SHARPE}, N ≥ {min_trades}\n")

    # ── 1. Universe ───────────────────────────────────────────────────────────
    _section("1. Loading Russell 2000 constituents")
    all_tickers = _load_universe()
    if not all_tickers:
        print("[error] No tickers loaded. Exiting.")
        return

    candidates_raw = [t for t in all_tickers if t not in _SKIP]
    print(f"  {len(all_tickers)} total → {len(candidates_raw)} after removing production/known-bad/OOS tickers.\n")

    # ── 2. Sector / beta / mkt cap metadata ──────────────────────────────────
    _section("2. Fetching sector / beta / market cap metadata")
    print(f"  Fetching yfinance info for {len(candidates_raw)} tickers (parallel)…\n")

    import concurrent.futures

    meta_list: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(_fetch_ticker_meta, t): t for t in candidates_raw}
        done = 0
        for fut in concurrent.futures.as_completed(futures):
            meta_list.append(fut.result())
            done += 1
            if done % 200 == 0:
                print(f"    {done}/{len(candidates_raw)} metadata fetched…")

    meta_df = pd.DataFrame(meta_list)

    # ── 3. Pre-filters ────────────────────────────────────────────────────────
    _section("3. Applying sector / market cap / beta pre-filters")

    in_target = meta_df["sector"].apply(lambda s: any(k in s for k in _MR_SECTORS | _RESEARCH_ONLY_SECTORS))
    in_blocked = meta_df["sector"].apply(lambda s: any(k in s for k in _BLOCKED_SECTORS))
    meta_filtered = meta_df[in_target & ~in_blocked].copy()
    n_research = meta_filtered["sector"].apply(lambda s: any(k in s for k in _RESEARCH_ONLY_SECTORS)).sum()
    print(f"  After sector filter: {len(meta_filtered)} tickers ({n_research} research-only)")

    # Market cap band: $300M–$10B (true small-cap to lower mid-cap boundary)
    meta_filtered = meta_filtered[
        (meta_filtered["mkt_cap_b"] >= MIN_MARKET_CAP_B) & (meta_filtered["mkt_cap_b"] <= MAX_MARKET_CAP_B)
    ]
    print(f"  After mkt cap ${MIN_MARKET_CAP_B:.1f}B–${MAX_MARKET_CAP_B:.0f}B: {len(meta_filtered)} tickers")

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

    import multiprocessing as _mp

    _mp.set_start_method("fork", force=True)

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

    print(f"\n  {len(all_dfs)} tickers loaded ({fail_count} failed/insufficient history).")

    # ── 6. ADV filter ─────────────────────────────────────────────────────────
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
        results_df[_col] = pd.to_numeric(results_df[_col], errors="coerce").fillna(0.0)
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
        ann_s = f"{(r.get('ann') or 0):.2f}"
        dd_s = f"{(r.get('max_dd') or 0):.1f}%"
        research_tag = "*" if _is_research_only(str(r.get("sector_grp", ""))) else " "
        print(
            f"{r['ticker']:<8} {str(r.get('sector_grp', '')):<12}{research_tag}"
            f"{r.get('beta', 0):>5.2f} {r.get('mkt_cap_b', 0):>7.0f}B "
            f"{r.get('adv_30d_m', 0):>7.0f}M "
            f"{n:>4} {wr_s:>6} {avg_s:>7} {sh_s:>8} {ann_s:>8} {dd_s:>7}"
        )

    # ── 10. PASS / FAIL / WATCH classification ────────────────────────────────
    _section("10. Candidates Meeting Quality Bar")

    mask_pass = (
        (results_df["wr"] >= MIN_WR)
        & (results_df["sharpe"] >= MIN_SHARPE)
        & (results_df["n"] >= min_trades)
        & (~results_df["sector_grp"].apply(_is_research_only))
    )
    mask_watch = (
        (results_df["wr"] >= WATCH_MIN_WR)
        & (results_df["avg"] >= WATCH_MIN_AVG)
        & (results_df["n"] >= WATCH_MIN_N)
        & (~results_df["sector_grp"].apply(_is_research_only))
        & ~mask_pass
    )
    mask_research_pass = (
        (results_df["wr"] >= MIN_WR)
        & (results_df["sharpe"] >= MIN_SHARPE)
        & (results_df["n"] >= min_trades)
        & results_df["sector_grp"].apply(_is_research_only)
    )

    pass_df = results_df[mask_pass].copy()
    watch_df = results_df[mask_watch].copy()
    research_df = results_df[mask_research_pass].copy()
    fail_df = results_df[~mask_pass & ~mask_watch & ~mask_research_pass].copy()

    n_pass = len(pass_df)
    n_watch = len(watch_df)
    n_res = len(research_df)

    print(f"\n  PASS: {n_pass} tickers (WR ≥ {MIN_WR:.0f}%, Sharpe ≥ {MIN_SHARPE}, N ≥ {min_trades})")
    print(f"  WATCH: {n_watch} tickers (WR ≥ {WATCH_MIN_WR:.0f}%, Avg ≥ {WATCH_MIN_AVG}%, N ≥ {WATCH_MIN_N})")
    print(f"  RESEARCH-ONLY PASS: {n_res} tickers (Healthcare*/Industrials* — not live-eligible without §10 review)")
    print(f"  FAIL: {len(fail_df)} tickers (tested but below quality bar)")
    print(f"  SKIP: {sum(1 for r in results if r.get('n', 0) < 1)} tickers (N < 1 — insufficient signal history)\n")

    # ── PASS block ────────────────────────────────────────────────────────────
    def _fmt_ticker_block(label: str, df: pd.DataFrame, research_note: str = "") -> None:
        if df.empty:
            print(f"### {label}\n  (none)\n")
            return
        print(f"### {label}\n")
        if research_note:
            print(f"  > {research_note}\n")
        sectors_seen: set[str] = set()
        for _, r in df.sort_values("ann", ascending=False).iterrows():
            sg = str(r.get("sector_grp", "")).rstrip("*")
            if sg not in sectors_seen:
                print(f"  # {sg}")
                sectors_seen.add(sg)
            sh = r.get("sharpe") or 0.0
            n = r.get("n") or 0
            wr = r.get("wr") or 0.0
            avg = r.get("avg") or 0.0
            print(f"  {r['ticker']}  # N={n}, WR={wr:.0f}%, avg={avg:+.2f}%, Sh={sh:.2f}")
        print()
        ready = [f'"{r["ticker"]}"' for _, r in df.iterrows()]
        print(f"  # All {len(ready)} tickers (copy-paste ready):")
        print(f"  {', '.join(ready)}\n")

    _fmt_ticker_block("PASS — Copy into production TICKERS universe:", pass_df)

    if not watch_df.empty:
        _fmt_ticker_block("WATCH — Validate individually before adding:", watch_df)

    if not research_df.empty:
        _fmt_ticker_block(
            "RESEARCH-ONLY PASS — Positive MR edge but sector needs §10 review:",
            research_df,
            "Healthcare*: small-cap binary event risk. Industrials*: marginal cross-sectional evidence. "
            "Run §15f+§17f before live deployment.",
        )

    if not fail_df.empty:
        fail_names = fail_df[fail_df["n"] >= 1]["ticker"].tolist()
        print("### FAIL — Do NOT add (tested, below quality bar):\n")
        # Print in rows of 15
        for i in range(0, len(fail_names), 15):
            print("  " + ", ".join(fail_names[i : i + 15]))
        print()

    # ── 11. ADV distribution ──────────────────────────────────────────────────
    _section("11. ADV Distribution of PASS Tickers")
    if not pass_df.empty:
        adv_vals = pass_df["adv_30d_m"].tolist()
        print(f"  Median ADV: ${sorted(adv_vals)[len(adv_vals) // 2]:.0f}M/day")
        print(f"  Min ADV (lowest-liquidity PASS): ${min(adv_vals):.0f}M/day")
        print(f"  Max ADV: ${max(adv_vals):.0f}M/day\n")
        print("  Liquidity tiers:")
        print(f"    ADV ≥ $100M (crossing large-cap boundary): {sum(1 for a in adv_vals if a >= 100)} tickers")
        print(f"    ADV $20–100M (solid small-cap):            {sum(1 for a in adv_vals if 20 <= a < 100)} tickers")
        print(f"    ADV $10–20M  (minimum threshold):          {sum(1 for a in adv_vals if 10 <= a < 20)} tickers")
    else:
        print("  No PASS tickers — no ADV distribution to report.")

    # ── 12. Annualised Sharpe projection ──────────────────────────────────────
    _section("12. Annualised Sharpe Projection")
    current_n = len(_PRODUCTION_TICKERS)
    new_n = len(pass_df)
    combined_n = current_n + new_n
    sr_is = 0.31
    sr_fwd = 0.16
    yrs = 20.0

    def _ann_sharpe(sr: float, n_tickers: int) -> float:
        trades_per_yr = max(1, int(188 / 107 * n_tickers))
        return round(sr * (trades_per_yr / yrs) ** 0.5, 2)

    print(
        f"\n  Current:  {current_n} tickers → IS Ann.Sharpe {_ann_sharpe(sr_is, current_n)} (IS per-trade SR={sr_is})"
    )
    print(f"  New PASS: {new_n} R2000 tickers")
    print(
        f"  Combined: {combined_n} tickers → {_ann_sharpe(sr_is, combined_n)} IS  / {_ann_sharpe(sr_fwd, combined_n)} fwd"
    )
    print("\n  Note: R2000 tickers have higher idiosyncratic vol → forward SR likely 0.10–0.14 (below R1000's 0.16).")
    print(f"  Conservative (R2000-adjusted forward SR=0.12): {_ann_sharpe(0.12, combined_n)}")
    print("\n  Note: Run §15f+§17f backtest on PASS tickers before adding to production.")
    print("  Validate per-ticker Sharpe ≥ 0.35 individually. R2000 adds diversification but more noise.")

    print(f"\n*Russell 2000 MR Candidate Screener · ADV ≥ {adv_label} · {period_label}*")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Russell 2000 MR Candidate Screener")
    parser.add_argument("--fast", action="store_true", help="2006-2016 only (~2hr)")
    parser.add_argument("--adv", type=float, default=MIN_ADV_M, help="Min ADV $M/day")
    args = parser.parse_args()
    main(fast=args.fast, adv_m=args.adv)
