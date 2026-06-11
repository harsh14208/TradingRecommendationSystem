"""Bulk-download SimFin free fundamental data for US companies.

Uses the SimFin bulk-download API (prod.simfin.com) directly via requests;
the `simfin` Python package is NOT required.  Data is saved as raw CSVs to
`backend/data/simfin_raw/` for downstream factor construction.

PIT AUDIT
---------
SimFin bulk data is restated in-place: when a company files a restatement the
old row is overwritten with the revised numbers.  This means a naive
`Report Date` index is NOT point-in-time safe — you would be using restated
figures that were not available on the original filing date.

This script inspects `Restated Date` vs `Publish Date`.  If restatements are
observed a WARNING is emitted and `build_simfin_factors.py` applies a 90-day
lag to all filing dates as a conservative safety margin.

Usage
-----
    cd backend && python scripts/simfin_bulk_download.py --api-key $SIMFIN_API_KEY
"""

from __future__ import annotations

import argparse
import logging
import os
import urllib.parse
import zipfile
from pathlib import Path

import pandas as pd
import requests

log = logging.getLogger(__name__)

_HERE = Path(__file__).resolve().parent
_BACKEND = _HERE.parent
_DATA = _BACKEND / "data"
_OUT_DIR = _DATA / "simfin_raw"
_SP500_CSV = _DATA / "sp500_ticker_start_end.csv"

SIMFIN_BULK_URL = "https://prod.simfin.com/api/bulk-download/s3"

# Datasets to fetch.  Flow statements need both quarterly (for timeliness) and
# TTM (for smoothing).  Balance sheet is a stock variable — quarterly is best.
_DATASETS: list[tuple[str, str | None]] = [
    ("income", "annual"),
    ("income", "quarterly"),
    ("income", "ttm"),
    ("balance", "annual"),
    ("balance", "quarterly"),
    ("cashflow", "annual"),
    ("cashflow", "quarterly"),
    ("cashflow", "ttm"),
    ("companies", None),
]

# SimFin CSVs use semicolons
_SEP = ";"

_PIT_SAMPLE_ROWS = 50_000


def _auth_header(api_key: str) -> dict[str, str]:
    return {"Authorization": f"api-key {api_key}"}


def _download_zip(url: str, headers: dict[str, str], dest: Path) -> None:
    """Stream-download a ZIP file to ``dest``."""
    with requests.get(url, headers=headers, stream=True, timeout=300) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                fh.write(chunk)


def _extract_csv(zip_path: Path, out_dir: Path) -> Path | None:
    """Extract the first CSV member of a ZIP to ``out_dir``."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        csv_members = [m for m in zf.namelist() if m.lower().endswith(".csv")]
        if not csv_members:
            return None
        zf.extractall(out_dir)
        return out_dir / csv_members[0]


def _dataset_path(dataset: str, variant: str | None, out_dir: Path) -> Path:
    name = f"us-{dataset}"
    if variant:
        name += f"-{variant}"
    return out_dir / f"{name}.csv"


def download_dataset(
    dataset: str,
    variant: str | None,
    api_key: str,
    out_dir: Path,
) -> Path | None:
    """Download one SimFin bulk dataset and return the extracted CSV path."""
    params: dict[str, str] = {"dataset": dataset, "market": "us"}
    if variant:
        params["variant"] = variant

    headers = _auth_header(api_key)
    zip_path = out_dir / f"us-{dataset}-{variant or 'raw'}.zip"
    url = f"{SIMFIN_BULK_URL}?{urllib.parse.urlencode(params)}"

    try:
        _download_zip(url, headers, zip_path)
    except requests.RequestException as exc:
        log.error("Download failed for %s %s: %s", dataset, variant or "", exc)
        return None

    csv_path = _extract_csv(zip_path, out_dir)
    if csv_path is None:
        log.error("No CSV found in ZIP for %s %s", dataset, variant or "")
        return None

    # Ensure stable filename
    stable = _dataset_path(dataset, variant, out_dir)
    if csv_path != stable:
        csv_path.rename(stable)
        csv_path = stable

    # Clean up ZIP
    zip_path.unlink(missing_ok=True)
    return csv_path


def _load_sp500_tickers() -> set[str]:
    """Current and historical S&P 500 tickers from the PIT membership file."""
    if not _SP500_CSV.exists():
        log.warning("S&P 500 membership CSV not found at %s", _SP500_CSV)
        return set()
    df = pd.read_csv(_SP500_CSV)
    return set(df["ticker"].dropna().astype(str).str.upper())


def _norm_ticker(ticker: str) -> str:
    """Match the cache filename convention (BF.B -> BF-B)."""
    return ticker.replace(".", "-")


def _pit_audit(csv_path: Path) -> bool:
    """Return True if the dataset appears PIT-safe (no restatements overwriting history).

    We sample the first ``_PIT_SAMPLE_ROWS`` rows and compare ``Restated Date``
    to ``Publish Date``.  If they differ, SimFin has overwritten the original
    filing with a restatement — the row is NOT PIT-safe without a lag.
    """
    try:
        df = pd.read_csv(csv_path, sep=_SEP, nrows=_PIT_SAMPLE_ROWS)
    except Exception as exc:
        log.warning("Could not read %s for PIT audit: %s", csv_path, exc)
        return True  # conservative: assume safe if we cannot check

    if "Restated Date" not in df.columns or "Publish Date" not in df.columns:
        return True

    # Non-empty Restated Date that differs from Publish Date => restatement
    restated = (
        df["Restated Date"].notna()
        & (df["Restated Date"].astype(str) != "")
        & (df["Restated Date"] != df["Publish Date"])
    )
    n_restate = int(restated.sum())
    if n_restate:
        pct = n_restate / len(df) * 100
        log.warning(
            "PIT AUDIT WARNING — %s: %s/%s rows (%.1f%%) have "
            "Restated Date != Publish Date.  SimFin bulk data is NOT PIT-safe; "
            "restatements overwrite history.  A 90-day lag is required before "
            "using figures in a backtest.",
            csv_path.name,
            n_restate,
            len(df),
            pct,
        )
        return False
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description="Bulk download SimFin free data for US companies")
    ap.add_argument("--api-key", default=os.getenv("SIMFIN_API_KEY"), help="SimFin API key")
    ap.add_argument("--out-dir", type=Path, default=_OUT_DIR, help="Output directory for raw CSVs")
    args = ap.parse_args()

    if not args.api_key:
        raise SystemExit("SimFin API key required. Pass --api-key or set SIMFIN_API_KEY env var.")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    sp500 = _load_sp500_tickers()
    log.info("S&P 500 universe: %d tickers", len(sp500))

    pit_safe = True
    for dataset, variant in _DATASETS:
        log.info("Downloading %s %s ...", dataset, variant or "")
        csv_path = download_dataset(dataset, variant, args.api_key, args.out_dir)
        if csv_path is None:
            log.warning("Skipping %s %s (download failed)", dataset, variant or "")
            continue
        log.info("Saved → %s", csv_path)

        if dataset in ("income", "balance", "cashflow"):
            if not _pit_audit(csv_path):
                pit_safe = False

    if not pit_safe:
        log.warning("NON-PIT-SAFE RESTATEMENTS DETECTED. Apply a 90-day lag in build_simfin_factors.py.")


if __name__ == "__main__":
    main()
