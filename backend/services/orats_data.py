"""ORATS historical options data loader and feature panel builder.

Designed for the **Near End-of-Day** files delivered via FTP:
  ORATS_SMV_Strikes_YYYYMMDD.csv inside zip archives.

The module builds a compact daily per-ticker panel (one row per ticker per date)
with options-derived features that can be merged into the backtest alt-data panel
or consumed live by the gate stack.
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger("signal.orats_data")

CONTRACT_MULTIPLIER = 100.0
ORATS_COLUMNS = [
    "ticker",
    "cOpra",
    "pOpra",
    "stkPx",
    "expirDate",
    "yte",
    "strike",
    "cVolu",
    "cOi",
    "pVolu",
    "pOi",
    "cBidPx",
    "cValue",
    "cAskPx",
    "pBidPx",
    "pValue",
    "pAskPx",
    "cBidIv",
    "cMidIv",
    "cAskIv",
    "smoothSmvVol",
    "pBidIv",
    "pMidIv",
    "pAskIv",
    "iRate",
    "divRate",
    "residualRateData",
    "delta",
    "gamma",
    "theta",
    "vega",
    "rho",
    "phi",
    "driftlessTheta",
    "extVol",
    "extCTheo",
    "extPTheo",
    "spot_px",
    "trade_date",
]


def _parse_orats_date(s: pd.Series) -> pd.Series:
    """Parse ORATS' M/D/YYYY date strings."""
    return pd.to_datetime(s, format="%m/%d/%Y").dt.date


def _read_orats_csv(path: Path) -> pd.DataFrame:
    """Read a single ORATS SMV strikes CSV."""
    log.info("Reading ORATS file: %s", path)
    df = pd.read_csv(
        path,
        dtype={"ticker": str, "cOpra": str, "pOpra": str},
        low_memory=False,
    )
    if "trade_date" not in df.columns and "quotedate" in df.columns:
        df = df.rename(columns={"quotedate": "trade_date"})

    df["trade_date"] = _parse_orats_date(df["trade_date"])
    df["expirDate"] = _parse_orats_date(df["expirDate"])
    df["yte_days"] = (df["expirDate"] - df["trade_date"]).dt.days
    return df


def _atm_iv_for_ticker(g: pd.DataFrame) -> float:
    """Approximate 30-day ATM IV from the smoothed vol surface.

    Selects the option with call delta closest to 0.50 among tenors closest to
    30 calendar days. The ORATS `delta` column is call delta; puts are derived.
    """
    target_yte = 30.0
    g = g.copy()
    g["dist_yte"] = (g["yte_days"] - target_yte).abs()
    best_yte = g["yte_days"].iloc[g["dist_yte"].argmin()]
    tenor = g[g["yte_days"] == best_yte]
    if tenor.empty:
        return np.nan
    atm_row = tenor.loc[(tenor["delta"] - 0.50).abs().idxmin()]
    return float(atm_row["smoothSmvVol"])


def _iv_skew_for_ticker(g: pd.DataFrame) -> dict[str, float]:
    """Return 25-delta call/put IV approximations and put-call skew.

    ORATS provides a single `delta` column (call delta). Put delta = call_delta - 1.
    25-delta call ≈ call_delta 0.25; 25-delta put ≈ put_delta -0.25 ≈ call_delta 0.75.
    """
    g = g.copy()
    g["dist_yte"] = (g["yte_days"] - 30.0).abs()
    best_yte = g["yte_days"].iloc[g["dist_yte"].argmin()]
    tenor = g[g["yte_days"] == best_yte]
    if tenor.empty:
        return {"iv_25d_call": np.nan, "iv_25d_put": np.nan, "pc_iv_skew": np.nan}

    iv_25d_call = float(tenor.loc[(tenor["delta"] - 0.25).abs().idxmin(), "smoothSmvVol"])
    iv_25d_put = float(tenor.loc[(tenor["delta"] - 0.75).abs().idxmin(), "smoothSmvVol"])
    pc_iv_skew = iv_25d_put - iv_25d_call if pd.notna(iv_25d_put) and pd.notna(iv_25d_call) else np.nan
    return {"iv_25d_call": iv_25d_call, "iv_25d_put": iv_25d_put, "pc_iv_skew": pc_iv_skew}


def _gex_dex_for_ticker(g: pd.DataFrame) -> dict[str, float]:
    """Gamma/delta exposure in dollars (approximate).

    Each row contains both call and put data. ORATS' `delta` column is the
    call delta; put delta is derived as call_delta - 1. Gamma is the same for
    calls and puts at a given strike.
    """
    stk = g["stkPx"].iloc[0]
    call_gex = (g["gamma"].fillna(0) * g["cOi"].fillna(0) * stk * CONTRACT_MULTIPLIER).sum()
    put_gex = (g["gamma"].fillna(0) * g["pOi"].fillna(0) * stk * CONTRACT_MULTIPLIER).sum()
    gex = float(call_gex + put_gex)

    call_dex = (g["delta"].fillna(0) * g["cOi"].fillna(0) * g["strike"] * CONTRACT_MULTIPLIER).sum()
    put_delta = g["delta"].fillna(0) - 1.0
    put_dex = (put_delta * g["pOi"].fillna(0) * g["strike"] * CONTRACT_MULTIPLIER).sum()
    dex = float(call_dex + put_dex)
    return {"gex": gex, "dex": dex}


def _volume_oi_metrics(g: pd.DataFrame) -> dict[str, float]:
    """Put/call volume and open-interest ratios plus 0-DTE put volume."""
    call_vol = g["cVolu"].fillna(0).sum()
    put_vol = g["pVolu"].fillna(0).sum()
    call_oi = g["cOi"].fillna(0).sum()
    put_oi = g["pOi"].fillna(0).sum()
    zero_dte_puts = g.loc[g["yte_days"] <= 1, "pVolu"].fillna(0).sum()
    return {
        "pc_volume_ratio": float(put_vol / call_vol) if call_vol > 0 else np.nan,
        "pc_oi_ratio": float(put_oi / call_oi) if call_oi > 0 else np.nan,
        "total_opt_volume": float(call_vol + put_vol),
        "total_opt_oi": float(call_oi + put_oi),
        "zero_dte_put_volume": float(zero_dte_puts),
    }


def summarize_orats_day(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse a raw ORATS strikes day into one row per ticker."""
    rows = []
    for ticker, g in df.groupby("ticker"):
        if len(g) < 2:
            continue
        base = {
            "ticker": ticker,
            "date": g["trade_date"].iloc[0],
            "stk_px": float(g["stkPx"].iloc[0]),
        }
        base["atm_iv_30d"] = _atm_iv_for_ticker(g)
        base.update(_iv_skew_for_ticker(g))
        base.update(_gex_dex_for_ticker(g))
        base.update(_volume_oi_metrics(g))
        rows.append(base)
    return pd.DataFrame(rows)


def build_orats_panel(
    raw_dir: Path,
    output_path: Path,
    start_date: date | None = None,
    end_date: date | None = None,
) -> pd.DataFrame:
    """Build and save a per-ticker daily panel from raw ORATS files.

    Files may be either:
      - ORATS_SMV_Strikes_YYYYMMDD.csv
      - ORATS_SMV_Strikes_YYYYMMDD.zip containing the CSV
    """
    raw_dir = Path(raw_dir)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    files: list[Path] = []
    for ext in ("*.csv", "*.zip"):
        files.extend(raw_dir.glob(ext))
    files.sort()

    date_re = re.compile(r"ORATS_SMV_Strikes_(\d{8})")
    daily_frames: list[pd.DataFrame] = []

    for f in files:
        m = date_re.search(f.name)
        if not m:
            continue
        file_date = datetime.strptime(m.group(1), "%Y%m%d").date()
        if start_date and file_date < start_date:
            continue
        if end_date and file_date > end_date:
            continue

        if f.suffix == ".zip":
            import zipfile

            with zipfile.ZipFile(f) as z:
                csv_name = next(n for n in z.namelist() if n.endswith(".csv"))
                with z.open(csv_name) as zf:
                    df = pd.read_csv(zf, dtype={"ticker": str, "cOpra": str, "pOpra": str}, low_memory=False)
                    df["trade_date"] = _parse_orats_date(df["trade_date"])
                    df["expirDate"] = _parse_orats_date(df["expirDate"])
                    df["yte_days"] = (pd.to_datetime(df["expirDate"]) - pd.to_datetime(df["trade_date"])).dt.days
        else:
            df = _read_orats_csv(f)

        summary = summarize_orats_day(df)
        daily_frames.append(summary)
        log.info("%s: %d tickers", file_date, len(summary))

    if not daily_frames:
        raise ValueError(f"No ORATS files found in {raw_dir}")

    panel = pd.concat(daily_frames, ignore_index=True)
    panel = panel.sort_values(["ticker", "date"]).reset_index(drop=True)

    # Add rolling IV rank / percentile using the panel history.
    panel["iv_rank_252"] = panel.groupby("ticker")["atm_iv_30d"].transform(
        lambda s: s.rolling(252, min_periods=60).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False)
    )
    panel["iv_pctile_252"] = panel.groupby("ticker")["atm_iv_30d"].transform(
        lambda s: s.rolling(252, min_periods=60).apply(
            lambda x: (x.iloc[-1] - x.min()) / max(x.max() - x.min(), 1e-9), raw=False
        )
    )

    panel.to_parquet(output_path, index=False)
    log.info("Panel saved: %s (%d rows, %d tickers)", output_path, len(panel), panel["ticker"].nunique())
    return panel


def load_orats_panel(path: Path | str | None = None) -> pd.DataFrame | None:
    """Load a pre-built ORATS panel, or None if missing."""
    if path is None:
        path = Path(__file__).parent.parent / "data" / "cache_orats" / "orats_panel.parquet"
    else:
        path = Path(path)
    if not path.exists():
        return None
    return pd.read_parquet(path)


# ── PostgreSQL persistence (ORATS FTP download expires ~30 days after purchase) ──

_DB_COLUMNS = [
    "ticker",
    "date",
    "stk_px",
    "atm_iv_30d",
    "iv_25d_call",
    "iv_25d_put",
    "pc_iv_skew",
    "gex",
    "dex",
    "pc_volume_ratio",
    "pc_oi_ratio",
    "total_opt_volume",
    "total_opt_oi",
    "zero_dte_put_volume",
    "iv_rank_252",
    "iv_pctile_252",
]


async def save_orats_panel_to_db(panel: pd.DataFrame, batch_size: int = 5000) -> int:
    """Persist an ORATS feature panel to PostgreSQL.

    Uses ``on_conflict_do_nothing`` on (ticker, date) so re-running the builder
    is idempotent.  Returns the number of rows inserted.
    """
    from database import _IS_POSTGRES, AsyncSessionLocal
    from models import OratsDailyFeatures

    if _IS_POSTGRES:
        from sqlalchemy.dialects.postgresql import insert as _insert
    else:
        from sqlalchemy import insert as _insert

    df = panel[_DB_COLUMNS].copy()
    df["date"] = pd.to_datetime(df["date"]).dt.date
    records = df.replace({np.nan: None}).to_dict("records")

    inserted = 0
    async with AsyncSessionLocal() as db:
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            stmt = _insert(OratsDailyFeatures).values(batch)
            if _IS_POSTGRES:
                stmt = stmt.on_conflict_do_nothing(index_elements=["ticker", "date"])
            result = await db.execute(stmt)
            inserted += int(result.rowcount) if result.rowcount is not None else len(batch)
        await db.commit()
    log.info("Persisted %d ORATS rows to orats_daily_features", inserted)
    return inserted


async def load_orats_panel_from_db() -> pd.DataFrame | None:
    """Load the ORATS feature panel from PostgreSQL, or None if empty."""
    from sqlalchemy import select

    from database import AsyncSessionLocal
    from models import OratsDailyFeatures

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(OratsDailyFeatures))
        rows = result.scalars().all()
        if not rows:
            return None
        data = [{col: getattr(r, col) for col in _DB_COLUMNS + ["fetched_at"]} for r in rows]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    return df
