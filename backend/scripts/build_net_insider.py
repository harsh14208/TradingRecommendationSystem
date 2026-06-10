"""Extract a NET insider-buying signal from SEC Form 4 XML (buys − sells).

EXP6 showed the raw Form 4 *count* proxy has strong but contrarian IC (count is
selling-dominated). The clean, correctly-signed signal is NET open-market buying:
sum of nonDerivative transactionShares with code P (purchase, Acquired) minus
code S (sale, Disposed). This parses the actual Form 4 ownershipDocument XML.

SCOPE: full-history Form 4 parsing across the universe is a multi-hour scrape, so
this bounds to the most-recent `--max-filings` Form 4s per ticker (recent years —
where a live signal matters; EXP6's count proxy was already only 2015+/50% cov).
Resumable: caches per-ticker to data/net_insider.pkl and skips finished tickers.

Output: data/net_insider.pkl = {ticker: Series(date → trailing-90d net shares bought / shares_out)}.

    cd backend && source venv/bin/activate && python scripts/build_net_insider.py --max-filings 120
"""

from __future__ import annotations

import argparse
import pickle
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests

_BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND))
from scripts.backtest_edgar import EDGAR_BASE, HEADERS, RATE_DELAY  # noqa: E402

_DATA = _BACKEND / "data"
_EDGAR_PKL = _DATA / "edgar_fundamentals.pkl"
_OUT = _DATA / "net_insider.pkl"

_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"
# Form 4 nonDerivative transaction blocks: pull code (P/S/A...), shares, A/D flag.
_TXN_RE = re.compile(
    r"<nonDerivativeTransaction>.*?<transactionCode>(?P<code>[A-Z])</transactionCode>"
    r".*?<transactionShares>\s*<value>(?P<shares>[\d.]+)</value>"
    r".*?<transactionAcquiredDisposedCode>\s*<value>(?P<ad>[AD])</value>",
    re.DOTALL,
)


def _form4_recent(cik: str, max_filings: int) -> list[tuple[pd.Timestamp, str]]:
    """(filed_date, accession) for the most-recent Form 4s from the submissions API."""
    url = f"{EDGAR_BASE}/submissions/CIK{cik}.json"
    time.sleep(RATE_DELAY)
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        return []
    rec = r.json().get("filings", {}).get("recent", {})
    out = [
        (pd.Timestamp(d), a)
        for f, d, a in zip(rec.get("form", []), rec.get("filingDate", []), rec.get("accessionNumber", []))
        if f == "4"
    ]
    return out[:max_filings]


def _net_shares(cik: str, accn: str) -> float | None:
    """Net open-market shares (P purchases − S sales) from one Form 4's .txt submission."""
    url = f"{_ARCHIVES}/{int(cik)}/{accn.replace('-', '')}/{accn}.txt"
    time.sleep(RATE_DELAY)
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return None
    except Exception:
        return None
    net = 0.0
    found = False
    for m in _TXN_RE.finditer(r.text):
        code, shares, ad = m.group("code"), float(m.group("shares")), m.group("ad")
        if code not in ("P", "S"):  # only open-market purchases/sales (exclude grants/exercises)
            continue
        found = True
        net += shares if ad == "A" else -shares
    return net if found else 0.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-filings", type=int, default=120, help="most-recent Form 4s per ticker to parse")
    args = ap.parse_args()

    with open(_EDGAR_PKL, "rb") as f:
        edgar = pickle.load(f)
    ciks = {t: edgar[t]["cik"] for t in edgar if edgar[t].get("cik")}
    done = {}
    if _OUT.exists():
        with open(_OUT, "rb") as f:
            done = pickle.load(f)
    todo = [t for t in sorted(ciks) if t not in done]
    print(f"net-insider: {len(done)} cached, {len(todo)} to fetch (max {args.max_filings} Form 4s/ticker)")

    for i, ticker in enumerate(todo, 1):
        cik = ciks[ticker]
        filings = _form4_recent(cik, args.max_filings)
        rows: dict[pd.Timestamp, float] = {}
        for filed, accn in filings:
            ns = _net_shares(cik, accn)
            if ns is not None:
                rows[filed] = rows.get(filed, 0.0) + ns
        if rows:
            s = pd.Series(rows).sort_index()
            s = s[~s.index.duplicated(keep="last")]
            # trailing-90d net buying (in shares); normalized to shares_out at screen time
            daily = s.resample("D").sum().fillna(0.0)
            done[ticker] = daily.rolling(90, min_periods=1).sum()
        else:
            done[ticker] = pd.Series(dtype=float)
        if i % 10 == 0 or i == len(todo):
            with open(_OUT, "wb") as f:  # checkpoint (resumable)
                pickle.dump(done, f)
            print(f"  [{i:>3}/{len(todo)}] {ticker}: {len(filings)} Form 4s → {len(done[ticker])}d net series")

    with open(_OUT, "wb") as f:
        pickle.dump(done, f)
    nonempty = sum(1 for t in done if len(done[t]))
    print(f"\nSaved {len(done)} tickers ({nonempty} non-empty) → {_OUT}")


if __name__ == "__main__":
    main()
