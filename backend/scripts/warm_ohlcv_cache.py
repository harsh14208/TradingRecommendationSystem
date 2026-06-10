"""One-off: pre-warm data/cache_ohlcv so backtest_technicals.py runs offline.

Each yfinance download runs in a daemon thread with a hard timeout, so a single
hung socket (flaky yfinance) is abandoned instead of wedging the whole run.
Re-runnable: already-cached symbols are skipped instantly.
"""

import sys
import threading

sys.path.insert(0, ".")

import scripts.backtest_technicals as bt  # noqa: E402
from scripts.backtest_technicals import cached_yf_download  # noqa: E402

START, END = "2003-01-01", "2026-06-08"
TIMEOUT = 25  # seconds per symbol before abandoning


def _symbols() -> list[str]:
    syms = set(bt.TICKERS)
    for name in ("HELD_OUT_TICKERS", "ETF_TICKERS", "SECTOR_ETFS", "_SECTOR_ETFS", "OOS_TICKERS"):
        v = getattr(bt, name, None)
        if v:
            try:
                syms |= set(v)
            except TypeError:
                pass
    syms |= {
        "SPY",
        "^VIX",
        "^VIX3M",
        "^IRX",
        "TLT",
        "UUP",
        "XLE",
        "XLK",
        "XLF",
        "XLY",
        "XLC",
        "XLB",
        "XLV",
        "XLI",
        "XLP",
        "XLU",
        "XLRE",
    }
    return sorted(syms)


def _fetch(sym: str, out: dict) -> None:
    try:
        df = cached_yf_download(sym, START, END)
        out["ok"] = df is not None and not df.empty
    except Exception as e:  # noqa: BLE001
        out["err"] = repr(e)


def warm(syms: list[str]) -> list[str]:
    ok, fail = [], []
    for i, sym in enumerate(syms, 1):
        out: dict = {}
        t = threading.Thread(target=_fetch, args=(sym, out), daemon=True)
        t.start()
        t.join(timeout=TIMEOUT)
        if t.is_alive():
            fail.append(sym)
            status = "HANG"
        elif out.get("ok"):
            ok.append(sym)
            status = "ok"
        else:
            fail.append(sym)
            status = f"empty/{out.get('err', 'no-data')[:40]}"
        print(f"[{i}/{len(syms)}] {sym}: {status}  (ok={len(ok)} fail={len(fail)})", flush=True)
    return fail


if __name__ == "__main__":
    syms = _symbols()
    print(f"Warming {len(syms)} symbols (timeout {TIMEOUT}s each)…", flush=True)
    failed = warm(syms)
    if failed:
        print(f"\nRetry pass for {len(failed)} failed symbols…", flush=True)
        failed = warm(failed)
    print(f"\nDONE. Persistently failed ({len(failed)}): {', '.join(failed) or 'none'}", flush=True)
