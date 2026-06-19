"""Massive (Polygon) options flat-file loader → ORATS-compatible feature panel.

Builds the SAME per-ticker daily panel as `orats_data.py` (one row per ticker per
date: stk_px / atm_iv_30d / pc_iv_skew / volumes / …) but from the **Massive options
day-aggregate flat files** you already pay for (Options Starter, 2y history incl. the
Aug-2024 vol spike) instead of the paid ORATS FTP. IV is computed locally by inverting
Black–Scholes on each contract's EOD close — so no pre-computed-IV subscription needed.

Pipeline:
  1. download day-agg flat files (options + underlying stocks) from S3  [download_day_aggs]
  2. per (underlying, date): pick ~30d tenor, invert BS for ATM IV + 25Δ skew  [build_massive_panel]
  3. persist via orats_data.save_orats_panel_to_db (same `orats_daily_features` table)

The output is consumed unchanged by `scripts/orats_opportunity_model.get_vol_view`.

S3 access (separate from the REST API key — get keys at massive.com/dashboard/flat-files):
  endpoint https://files.polygon.io  bucket flatfiles
  options    us_options_opra/day_aggs_v1/YYYY/MM/YYYY-MM-DD.csv.gz
  stocks     us_stocks_sip/day_aggs_v1/YYYY/MM/YYYY-MM-DD.csv.gz
"""

from __future__ import annotations

import gzip
import logging
import math
import os
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm

log = logging.getLogger("signal.massive_options_data")

_S3_ENDPOINT = os.getenv("MASSIVE_S3_ENDPOINT", "https://files.polygon.io")
_S3_BUCKET = os.getenv("MASSIVE_S3_BUCKET", "flatfiles")
_OPT_PREFIX = "us_options_opra/day_aggs_v1"
_STK_PREFIX = "us_stocks_sip/day_aggs_v1"

_RISK_FREE = 0.04  # flat r; ATM 30d IV is insensitive to small r changes
_TARGET_DTE = 30.0


# ──────────────────────────────────────────────────────────────────────────
# S3 download
# ──────────────────────────────────────────────────────────────────────────
def download_day_aggs(start: date, end: date, dest_root: Path, kind: str = "options") -> list[Path]:
    """Download day-agg flat files for [start, end] into dest_root/<kind>/.

    Needs S3 keys in env: MASSIVE_S3_KEY / MASSIVE_S3_SECRET (the Flat-Files keys,
    NOT the REST API key). Falls back to a clear error if boto3 is missing — the
    `aws s3 cp` CLI works identically with --endpoint-url https://files.polygon.io."""
    try:
        import boto3
        from botocore.config import Config
    except ImportError as e:
        raise SystemExit(
            "boto3 not installed. Either `pip install boto3`, or download with the aws CLI:\n"
            "  aws s3 sync s3://flatfiles/us_options_opra/day_aggs_v1/2024/ "
            "./data/cache_massive/options/2024/ --endpoint-url https://files.polygon.io --profile massive"
        ) from e

    key = os.getenv("MASSIVE_S3_KEY")
    secret = os.getenv("MASSIVE_S3_SECRET")
    if not key or not secret:
        raise SystemExit("Set MASSIVE_S3_KEY and MASSIVE_S3_SECRET (Flat-Files keys from the dashboard).")

    prefix = _OPT_PREFIX if kind == "options" else _STK_PREFIX
    s3 = boto3.client(
        "s3",
        endpoint_url=_S3_ENDPOINT,
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        config=Config(signature_version="s3v4"),
    )
    dest_dir = Path(dest_root) / kind
    dest_dir.mkdir(parents=True, exist_ok=True)

    out: list[Path] = []
    for d in pd.bdate_range(start, end):
        rel = f"{prefix}/{d.year}/{d.month:02d}/{d.strftime('%Y-%m-%d')}.csv.gz"
        local = dest_dir / f"{d.strftime('%Y-%m-%d')}.csv.gz"
        if local.exists():
            out.append(local)
            continue
        try:
            s3.download_file(_S3_BUCKET, rel, str(local))
            out.append(local)
            log.info("downloaded %s", rel)
        except Exception as e:  # missing day (holiday) or transient
            log.debug("skip %s: %s", rel, e)
    return out


# ──────────────────────────────────────────────────────────────────────────
# Black–Scholes inversion
# ──────────────────────────────────────────────────────────────────────────
def _bs_price(S: float, K: float, T: float, sigma: float, cp: str, r: float = _RISK_FREE) -> float:
    if T <= 0 or sigma <= 0:
        return max(0.0, (S - K) if cp == "C" else (K - S))
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if cp == "C":
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def _implied_vol(price: float, S: float, K: float, T: float, cp: str, r: float = _RISK_FREE) -> float:
    """Invert BS for IV; NaN if price is below intrinsic or solver fails."""
    if price <= 0 or S <= 0 or K <= 0 or T <= 0:
        return float("nan")
    intrinsic = max(0.0, (S - K) if cp == "C" else (K - S)) * math.exp(-r * T)
    if price < intrinsic - 1e-6:
        return float("nan")
    try:
        return float(brentq(lambda s: _bs_price(S, K, T, s, cp, r) - price, 1e-3, 5.0, maxiter=80, xtol=1e-4))
    except (ValueError, RuntimeError):
        return float("nan")


def _call_delta(S: float, K: float, T: float, sigma: float, r: float = _RISK_FREE) -> float:
    if T <= 0 or sigma <= 0:
        return float("nan")
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    return float(norm.cdf(d1))


# ──────────────────────────────────────────────────────────────────────────
# Parsing & summarisation
# ──────────────────────────────────────────────────────────────────────────
def _parse_opra(t: str) -> tuple[str, date, str, float] | None:
    """O:AAPL260116C00150000 → ('AAPL', 2026-01-16, 'C', 150.0). Last 15 chars are
    YYMMDD(6)+CP(1)+strike×1000(8); everything between 'O:' and that is the root."""
    if not t.startswith("O:") or len(t) < 18:
        return None
    body = t[2:]
    try:
        root = body[:-15]
        exp = datetime.strptime(body[-15:-9], "%y%m%d").date()
        cp = body[-9]
        strike = int(body[-8:]) / 1000.0
        if not root or cp not in ("C", "P"):
            return None
        return root, exp, cp, strike
    except (ValueError, IndexError):
        return None


def _summarize_underlying(g: pd.DataFrame, spot: float, trade_date: date) -> dict | None:
    """Collapse one underlying's option chain (a single day) to the panel row."""
    g = g[g["volume"] > 0].copy()
    if len(g) < 4 or spot <= 0:
        return None
    g["yte_days"] = (pd.to_datetime(g["expiry"]) - pd.Timestamp(trade_date)).dt.days
    g = g[g["yte_days"] > 0]
    if g.empty:
        return None

    # Nearest tenor to 30d, solve IV for its contracts.
    best_yte = g.loc[(g["yte_days"] - _TARGET_DTE).abs().idxmin(), "yte_days"]
    tenor = g[g["yte_days"] == best_yte].copy()
    T = best_yte / 365.0
    tenor["iv"] = [
        _implied_vol(px, spot, k, T, cp)
        for px, k, cp in zip(tenor["close"], tenor["strike"], tenor["cp"], strict=False)
    ]
    tenor = tenor.dropna(subset=["iv"])
    if tenor.empty:
        return None
    tenor["delta"] = [_call_delta(spot, k, T, iv) for k, iv in zip(tenor["strike"], tenor["iv"], strict=False)]

    atm = tenor.loc[(tenor["strike"] - spot).abs().idxmin()]
    atm_iv = float(atm["iv"])
    # 25Δ skew: IV at call-delta≈0.25 (OTM call) vs ≈0.75 (≈ −0.25 put delta).
    iv_25c = float(tenor.loc[(tenor["delta"] - 0.25).abs().idxmin(), "iv"])
    iv_25p = float(tenor.loc[(tenor["delta"] - 0.75).abs().idxmin(), "iv"])
    skew = iv_25p - iv_25c

    call_vol = float(g.loc[g["cp"] == "C", "volume"].sum())
    put_vol = float(g.loc[g["cp"] == "P", "volume"].sum())
    zero_dte_put = float(g.loc[(g["yte_days"] <= 1) & (g["cp"] == "P"), "volume"].sum())

    return {
        "ticker": g["root"].iloc[0],
        "date": trade_date,
        "stk_px": float(spot),
        "atm_iv_30d": atm_iv,
        "iv_25d_call": iv_25c,
        "iv_25d_put": iv_25p,
        "pc_iv_skew": skew,
        "gex": np.nan,  # not needed by the VRP/vol model; left for parity
        "dex": np.nan,
        "pc_volume_ratio": (put_vol / call_vol) if call_vol > 0 else np.nan,
        "pc_oi_ratio": np.nan,  # OI not in day-aggs (separate OI file/endpoint)
        "total_opt_volume": call_vol + put_vol,
        "total_opt_oi": np.nan,
        "zero_dte_put_volume": zero_dte_put,
    }


def _load_stock_closes(stock_file: Path) -> dict[str, float]:
    df = pd.read_csv(stock_file)
    return dict(zip(df["ticker"].astype(str), df["close"].astype(float), strict=False))


def build_massive_panel(
    options_dir: Path,
    stocks_dir: Path,
    output_path: Path,
    universe: set[str] | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> pd.DataFrame:
    """Build the per-ticker daily IV panel from downloaded day-agg flat files.

    options_dir / stocks_dir hold YYYY-MM-DD.csv.gz files. `universe` (optional) limits
    to the underlyings you care about — strongly recommended, the raw files are whole-market.
    `start_date` / `end_date` restrict the build to a date window (inclusive); use this for
    incremental daily updates.
    """
    options_dir, stocks_dir = Path(options_dir), Path(stocks_dir)
    rows: list[dict] = []

    for opt_file in sorted(options_dir.glob("*.csv.gz")):
        trade_date = datetime.strptime(opt_file.name.split(".")[0], "%Y-%m-%d").date()
        if start_date is not None and trade_date < start_date:
            continue
        if end_date is not None and trade_date > end_date:
            continue
        stock_file = stocks_dir / opt_file.name
        if not stock_file.exists():
            log.warning("no stock file for %s — skipping", trade_date)
            continue
        closes = _load_stock_closes(stock_file)

        with gzip.open(opt_file, "rt") as fh:
            df = pd.read_csv(fh, usecols=["ticker", "close", "volume"])
        parsed = df["ticker"].map(_parse_opra)
        df = df[parsed.notna()].copy()
        df[["root", "expiry", "cp", "strike"]] = pd.DataFrame(parsed[parsed.notna()].tolist(), index=df.index)
        if universe:
            df = df[df["root"].isin(universe)]

        added = 0
        for root, g in df.groupby("root"):
            spot = closes.get(root)
            if spot is None:
                continue
            row = _summarize_underlying(g, spot, trade_date)
            if row:
                rows.append(row)
                added += 1
        log.info("%s: %d underlyings", trade_date, added)

    if not rows:
        raise ValueError(f"No panel rows built from {options_dir}")
    panel = pd.DataFrame(rows).sort_values(["ticker", "date"]).reset_index(drop=True)

    # Rolling IV rank/percentile (parity with orats_data; mostly NaN until 60d accrue).
    panel["iv_rank_252"] = panel.groupby("ticker")["atm_iv_30d"].transform(
        lambda s: s.rolling(252, min_periods=60).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False)
    )
    panel["iv_pctile_252"] = panel.groupby("ticker")["atm_iv_30d"].transform(
        lambda s: s.rolling(252, min_periods=60).apply(
            lambda x: (x.iloc[-1] - x.min()) / max(x.max() - x.min(), 1e-9), raw=False
        )
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(output_path, index=False)
    log.info("Massive panel saved: %s (%d rows, %d tickers)", output_path, len(panel), panel["ticker"].nunique())
    return panel


def append_to_massive_panel(
    options_dir: Path,
    stocks_dir: Path,
    output_path: Path,
    universe: set[str] | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> pd.DataFrame:
    """Build new dates and merge them into an existing parquet panel.

    Drops any existing rows for the rebuilt date range before concatenating, so the
    operation is idempotent. Useful for the daily EOD update: build just yesterday,
    then merge into the 2-year cached panel.
    """
    output_path = Path(output_path)
    new_panel = build_massive_panel(
        options_dir, stocks_dir, output_path, universe=universe, start_date=start_date, end_date=end_date
    )
    if not output_path.exists():
        return new_panel
    old_panel = pd.read_parquet(output_path)
    min_date = new_panel["date"].min()
    max_date = new_panel["date"].max()
    old_panel = old_panel[
        (old_panel["date"] < pd.Timestamp(min_date)) | (old_panel["date"] > pd.Timestamp(max_date))
    ].copy()
    merged = pd.concat([old_panel, new_panel], ignore_index=True)
    merged = merged.sort_values(["ticker", "date"]).reset_index(drop=True)
    merged.to_parquet(output_path, index=False)
    log.info(
        "Incremental merge: %d old rows + %d new rows = %d rows, %d tickers",
        len(old_panel),
        len(new_panel),
        len(merged),
        merged["ticker"].nunique(),
    )
    return merged
