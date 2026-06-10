"""Extract a cross-sectional FUNDAMENTAL factor zoo from SEC EDGAR companyfacts.

Reuses the EDGAR fetch/parse helpers in backtest_edgar.py to pull the raw XBRL
line items needed for the academic orthogonal-to-price factor set:
  • value (book/market)         — StockholdersEquity ÷ market cap
  • gross profitability         — GrossProfit ÷ Assets            (Novy-Marx)
  • accruals                    — (NetIncome − OperatingCashFlow) ÷ Assets (Sloan; low=good)
  • asset growth                — ΔAssets YoY                     (investment factor; low=good)
  • net share issuance          — Δshares-out YoY                 (buyback=good)
  • piotroski F-score change    — quality momentum (from existing pickle)

Output: data/fundamental_factors.pkl = {ticker: {concept: filing-date Series}}.
Concepts stored raw (PIT, filing-date indexed); ratios needing price are formed
cross-sectionally in scripts/research/exp7_factor_zoo_ic.py.

CIKs are reused from data/edgar_fundamentals.pkl (no CIK-map fetch needed).

    cd backend && source venv/bin/activate && python scripts/build_fundamental_factors.py
"""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND))

from scripts.backtest_edgar import _entries_to_series, _get_concept, fetch_edgar_facts  # noqa: E402

_DATA = _BACKEND / "data"
_EDGAR_PKL = _DATA / "edgar_fundamentals.pkl"
_OUT = _DATA / "fundamental_factors.pkl"

# us-gaap concept → (synonym keys to try, in order). _get_concept returns the
# first that exists, USD or shares units, 10-K/10-Q only.
CONCEPTS = {
    "book_equity": ("StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"),
    "assets": ("Assets",),
    "revenue": ("Revenues", "SalesRevenueNet", "RevenueFromContractWithCustomerExcludingAssessedTax"),
    "gross_profit": ("GrossProfit",),
    "cost_of_revenue": ("CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"),
    "net_income": ("NetIncomeLoss", "ProfitLoss"),
    "op_cash_flow": ("NetCashProvidedByUsedInOperatingActivities", "CashGeneratedFromOperations"),
    "shares_out": (
        "CommonStockSharesOutstanding",
        "WeightedAverageNumberOfDilutedSharesOutstanding",
        "WeightedAverageNumberOfSharesOutstandingBasic",
    ),
}


def main() -> None:
    with open(_EDGAR_PKL, "rb") as f:
        edgar = pickle.load(f)
    ciks = {t: edgar[t]["cik"] for t in edgar if edgar[t].get("cik")}
    print(f"Extracting fundamental factor zoo for {len(ciks)} tickers (CIKs reused from edgar pickle)…")

    out: dict[str, dict] = {}
    for i, (ticker, cik) in enumerate(sorted(ciks.items()), 1):
        try:
            facts = fetch_edgar_facts(cik)
        except Exception as exc:
            print(f"  [{i:>3}/{len(ciks)}] {ticker}: fetch failed ({exc})")
            continue
        usgaap = facts.get("facts", {}).get("us-gaap", {})
        if not usgaap:
            print(f"  [{i:>3}/{len(ciks)}] {ticker}: no us-gaap facts")
            continue
        rec: dict = {"cik": cik, "piotroski": edgar[ticker].get("piotroski")}
        n_ok = 0
        for name, keys in CONCEPTS.items():
            s = _entries_to_series(_get_concept(usgaap, *keys))
            rec[name] = s
            if len(s):
                n_ok += 1
        out[ticker] = rec
        if i % 25 == 0 or i == len(ciks):
            print(f"  [{i:>3}/{len(ciks)}] {ticker}: {n_ok}/{len(CONCEPTS)} concepts")

    with open(_OUT, "wb") as f:
        pickle.dump(out, f)
    have = {c: sum(1 for t in out if len(out[t].get(c, []))) for c in CONCEPTS}
    print(f"\nSaved {len(out)} tickers → {_OUT}")
    print("Concept coverage:", {c: f"{n}/{len(out)}" for c, n in have.items()})


if __name__ == "__main__":
    main()
