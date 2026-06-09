"""Shared data loader for the awesome-quant Tier-1 experiments.

Reads the engine's own OHLCV cache (data/cache_ohlcv/*.csv) so every test runs
on the *same* adjusted price history the live backtest uses — no new data.

These scripts depend on skfolio / alphalens / arch, which require numpy>=2.0 and
conflict with the pinned numpy==1.26.4 in backend/venv. Run them in an ISOLATED
env — see backend/scripts/research/README.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

# research/ -> scripts/ -> backend/
_BACKEND = Path(__file__).resolve().parents[2]
CACHE = _BACKEND / "data" / "cache_ohlcv"
TRADES = _BACKEND / "data" / "backtest_trades_is.csv"

_FN = re.compile(r"^(?P<tkr>[A-Z\.\-]+)_(?P<start>\d{4}-\d{2}-\d{2})_(?P<end>\d{4}-\d{2}-\d{2})_")


def _latest_files() -> dict[str, Path]:
    """One file per ticker — keep the one with the latest end-date."""
    best: dict[str, tuple[str, Path]] = {}
    for f in CACHE.glob("*.csv"):
        m = _FN.match(f.name)
        if not m:
            continue
        tkr, end = m.group("tkr"), m.group("end")
        if tkr not in best or end > best[tkr][0]:
            best[tkr] = (end, f)
    return {t: p for t, (_, p) in best.items()}


def load_close(tkr: str, path: Path) -> pd.Series | None:
    try:
        df = pd.read_csv(path, skiprows=[1, 2], index_col=0, parse_dates=True)
        s = pd.to_numeric(df["Close"], errors="coerce").dropna()
        s.name = tkr
        return s if len(s) > 252 else None
    except Exception:
        return None


def load_ohlc(tkr: str, path: Path) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(path, skiprows=[1, 2], index_col=0, parse_dates=True)
        for c in ("Close", "High", "Low", "Open"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.dropna(subset=["Close", "High", "Low"])
        return df if len(df) > 252 else None
    except Exception:
        return None


def close_panel(tickers: list[str] | None = None, start: str = "2006-01-01") -> pd.DataFrame:
    """Wide close-price panel (index=date, cols=ticker)."""
    files = _latest_files()
    if tickers is not None:
        files = {t: p for t, p in files.items() if t in tickers}
    series = []
    for t, p in files.items():
        s = load_close(t, p)
        if s is not None:
            series.append(s)
    panel = pd.concat(series, axis=1).sort_index()
    panel = panel[panel.index >= start]
    return panel


def ohlcv_panels(
    tickers: list[str] | None = None,
    start: str = "2008-01-01",
    min_coverage: float = 0.6,
) -> dict[str, pd.DataFrame]:
    """Wide OHLCV panels for the WorldQuant-101 screen.

    Returns {"open","high","low","close","volume"} → each a (date × ticker)
    DataFrame on a common date index, restricted to tickers with at least
    `min_coverage` of rows present over the window (dense cross-section).
    """
    files = _latest_files()
    if tickers is not None:
        files = {t: p for t, p in files.items() if t in tickers}
    cols = ("Open", "High", "Low", "Close", "Volume")
    frames: dict[str, list[pd.Series]] = {c: [] for c in cols}
    for t, p in files.items():
        df = load_ohlc(t, p)
        if df is None or "Volume" not in df.columns:
            continue
        df = df[df.index >= start]
        if df.empty:
            continue
        for c in cols:
            s = pd.to_numeric(df[c], errors="coerce")
            s.name = t
            frames[c].append(s)
    out = {c.lower(): pd.concat(frames[c], axis=1).sort_index() for c in cols}
    # Keep only tickers dense enough over the window (avoid sparse-column noise)
    close = out["close"]
    keep = close.columns[close.notna().mean() >= min_coverage]
    return {k: v[keep] for k, v in out.items()}


def traded_tickers() -> list[str]:
    df = pd.read_csv(TRADES)
    return sorted(df["ticker"].unique().tolist())


if __name__ == "__main__":
    files = _latest_files()
    print(f"unique tickers in cache: {len(files)}")
    tt = traded_tickers()
    print(f"traded tickers: {len(tt)}")
    have = [t for t in tt if t in files]
    print(f"traded tickers with cache: {len(have)}")
    panel = close_panel(have)
    print(f"panel shape: {panel.shape}  range {panel.index.min().date()}..{panel.index.max().date()}")
