"""Build SimFin fundamental factors from raw bulk CSVs.

Reads the SimFin CSVs written by ``simfin_bulk_download.py``,
extracts filing-date-indexed Series for the concepts needed by the
cross-sectional alpha model, and writes ``data/simfin_factors.pkl``
with the same structure as ``data/fundamental_factors.pkl``:
    {ticker: {concept: filing-date Series}}

If the PIT audit in the download step detected non-safe restatements,
a 90-day lag is applied to all filing dates before outputting.

Usage
-----
    cd backend && python scripts/build_simfin_factors.py
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

_HERE = Path(__file__).resolve().parent
_BACKEND = _HERE.parent
_DATA = _BACKEND / "data"
_RAW_DIR = _DATA / "simfin_raw"
_OUT = _DATA / "simfin_factors.pkl"

# SimFin bulk CSVs use semicolons
_SEP = ";"

# Column names in SimFin bulk data
_TICKER = "Ticker"
_REPORT_DATE = "Report Date"
_PUBLISH_DATE = "Publish Date"
_RESTATED_DATE = "Restated Date"
_NET_INCOME = "Net Income"
_GROSS_PROFIT = "Gross Profit"
_OP_CASH_FLOW = "Net Cash from Operating Activities"
_TOTAL_ASSETS = "Total Assets"
_SHARES_BASIC = "Shares (Basic)"

# Concepts to extract and store
_CONCEPTS: dict[str, str] = {
    "net_income": _NET_INCOME,
    "gross_profit": _GROSS_PROFIT,
    "op_cash_flow": _OP_CASH_FLOW,
    "assets": _TOTAL_ASSETS,
    "shares_basic": _SHARES_BASIC,
}


def _norm_ticker(ticker: str) -> str:
    """Match the cache filename convention (BF.B -> BF-B)."""
    return ticker.replace(".", "-")


def _find_csv(dataset: str, variant: str | None = None) -> Path | None:
    """Return the first CSV matching ``us-{dataset}-{variant}.csv``."""
    name = f"us-{dataset}"
    if variant:
        name += f"-{variant}"
    matches = list(_RAW_DIR.glob(f"{name}*.csv"))
    return matches[0] if matches else None


def _read_csv(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame | None:
    """Read a semicolon-delimited SimFin CSV."""
    if not path.exists():
        return None
    try:
        return pd.read_csv(path, sep=_SEP, parse_dates=parse_dates, low_memory=False)
    except Exception as exc:
        log.warning("Failed to read %s: %s", path, exc)
        return None


def _extract_series(df: pd.DataFrame | None, ticker: str, value_col: str) -> pd.Series | None:
    """Extract a ``filing-date -> value`` Series for one ticker."""
    if df is None or value_col not in df.columns:
        return None
    # Normalize SimFin tickers to match our cache convention (BF.B -> BF-B)
    norm = df[_TICKER].astype(str).str.upper().str.replace(".", "-", regex=False)
    sub = df[norm == ticker][[_REPORT_DATE, value_col]].dropna()
    if sub.empty:
        return None
    sub = sub.sort_values(_REPORT_DATE).drop_duplicates(subset=[_REPORT_DATE], keep="last")
    s = sub.set_index(_REPORT_DATE)[value_col]
    s.index = pd.to_datetime(s.index)
    s = s[~s.index.duplicated(keep="last")].sort_index()
    return s


def _apply_lag(series: pd.Series | None, days: int = 90) -> pd.Series | None:
    """Shift filing dates backward by ``days`` as a conservative PIT lag."""
    if series is None or series.empty:
        return series
    series = series.copy()
    series.index = series.index - pd.Timedelta(days=days)
    return series


def _pit_unsafe() -> bool:
    """Inspect raw CSVs for restatements (Restated Date != Publish Date)."""
    for dataset, variant in [
        ("income", "quarterly"),
        ("income", "ttm"),
        ("balance", "quarterly"),
        ("cashflow", "quarterly"),
        ("cashflow", "ttm"),
    ]:
        path = _find_csv(dataset, variant)
        if path is None:
            continue
        df = _read_csv(path, parse_dates=[_PUBLISH_DATE, _RESTATED_DATE])
        if df is None:
            continue
        if _RESTATED_DATE not in df.columns or _PUBLISH_DATE not in df.columns:
            continue
        restated = (
            df[_RESTATED_DATE].notna()
            & (df[_RESTATED_DATE].astype(str) != "")
            & (df[_RESTATED_DATE] != df[_PUBLISH_DATE])
        )
        if restated.any():
            return True
    return False


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # Prefer quarterly/ttm for timeliness; fall back to annual if missing.
    inc_q = _read_csv(_find_csv("income", "quarterly"), parse_dates=[_REPORT_DATE])
    inc_ttm = _read_csv(_find_csv("income", "ttm"), parse_dates=[_REPORT_DATE])
    bal_q = _read_csv(_find_csv("balance", "quarterly"), parse_dates=[_REPORT_DATE])
    cf_q = _read_csv(_find_csv("cashflow", "quarterly"), parse_dates=[_REPORT_DATE])
    cf_ttm = _read_csv(_find_csv("cashflow", "ttm"), parse_dates=[_REPORT_DATE])

    if inc_q is None and inc_ttm is None:
        raise SystemExit("No SimFin income data found. Run simfin_bulk_download.py first.")

    pit_unsafe = _pit_unsafe()
    lag_days = 90 if pit_unsafe else 0
    if lag_days:
        log.warning("PIT audit: restatements detected. Applying %d-day lag to all figures.", lag_days)

    # Build universe from all datasets
    all_tickers: set[str] = set()
    for df in (inc_q, inc_ttm, bal_q, cf_q, cf_ttm):
        if df is not None:
            all_tickers.update(df[_TICKER].dropna().astype(str).str.upper().apply(_norm_ticker))

    log.info("Building SimFin factors for %d tickers ...", len(all_tickers))

    out: dict[str, dict[str, pd.Series]] = {}
    for i, ticker in enumerate(sorted(all_tickers), 1):
        rec: dict[str, pd.Series | None] = {}

        # Flow items: use quarterly so the downstream panel can apply a
        # trailing-4-filing TTM sum (same convention as EDGAR factors).
        # TTM datasets are kept as fallback only.
        for concept, col in _CONCEPTS.items():
            if concept in ("net_income", "gross_profit", "shares_basic"):
                s = _extract_series(inc_q, ticker, col) or _extract_series(inc_ttm, ticker, col)
            elif concept == "op_cash_flow":
                s = _extract_series(cf_q, ticker, col) or _extract_series(cf_ttm, ticker, col)
            elif concept == "assets":
                s = _extract_series(bal_q, ticker, col)
            else:
                s = None
            rec[concept] = s

        # Apply PIT lag if needed
        if lag_days:
            for key in list(rec.keys()):
                rec[key] = _apply_lag(rec[key], lag_days)

        # Only keep tickers with at least one populated concept
        if any(v is not None and len(v) for v in rec.values()):
            out[ticker] = {k: v for k, v in rec.items() if v is not None and len(v)}

        if i % 250 == 0 or i == len(all_tickers):
            log.info("  ...processed %d/%d tickers", i, len(all_tickers))

    with open(_OUT, "wb") as f:
        pickle.dump(out, f)

    # Coverage report
    have = {c: sum(1 for t in out if c in out[t]) for c in _CONCEPTS}
    log.info("Saved %d tickers → %s", len(out), _OUT)
    log.info("Concept coverage: %s", have)


if __name__ == "__main__":
    main()
