# §85-2 MD&A Sentiment Audit — Results (2026-06-09)

## Summary

**Finding: MD&A sentiment modifier has NEVER fired historically due to a bug in `_fetch_filing_text()`.**

- Total resolved signals in database: **566**
- Signals with MD&A (`mda_delta`) in rationale: **0**
- Signals with any SEC EDGAR source in rationale: **0**
- Signals with buyback rationale: **77** (buyback gate works)
- Signals with insider rationale: **0** (separate gate, may also be under-reported)

## Root Cause

The `_fetch_filing_text()` function in `services/edgar.py` used an outdated EDGAR URL pattern:

```
https://www.sec.gov/Archives/edgar/data/{cik}/{acc_clean}/{acc}-index.json
```

This returns **404**. SEC EDGAR filing index pages are now served as **HTML** (`.htm`), not JSON.
The code then tried to parse the non-existent JSON response, failed silently, and returned an
empty list of filing texts → `get_mda_delta()` always returned `{}` → `abs(_mda_score) >= 2.0`
was never satisfied → no signal ever received an MD&A score adjustment.

## Fix Applied (v8.2, 2026-06-09)

Replaced the broken index-page fetch with direct `primaryDocument` usage from the
submissions API (which already returns `primaryDocument` in the JSON response):

```python
# Before: fetched index.json (404), parsed directory listing
# After: use primaryDocument directly from submissions API
pri_docs = filings.get("primaryDocument", [])
targets = [
    (acc, dt, doc)
    for form, acc, dt, doc in zip(forms, accs, dates, pri_docs)
    if form == form_type and doc
][:2]
```

This eliminates one HTTP round-trip per filing and correctly fetches the primary
HTML document.

## Verification

Post-fix test on AAPL (CIK 0000320193):
- `_fetch_filing_text('0000320193', '10-Q')` → returns **2** filing texts (50000 chars each)
- `get_mda_delta('AAPL')` → returns `{'score': 0.0, 'reason': 'No significant language change', 'form_type': '10-Q'}`

The function now works. AAPL's MD&A delta is 0.0 (no significant QoQ language change),
which is expected for a stable large-cap.

## Recommendation

1. **No modifier to disable** — the bug prevented MD&A from ever firing, so there is no
   historical ΔWR data to analyze.
2. **Monitor going forward** — now that the fix is live, track signals that receive
   `mda_delta != 0` and compute their win rate vs. baseline after N≥50 such signals.
3. **Expected impact is small** — MD&A delta is capped at ±8 points and only fires when
   `abs(score) >= 2.0`. For stable large-caps, most deltas will be near zero.
4. **Consider CIK coverage** — `_KNOWN_CIKS` only covers ~60 tickers. Unknown tickers
   silently return `{}`. Expand the map or add a live CIK lookup fallback.

## Files Changed

- `backend/services/edgar.py` — `_fetch_filing_text()` fixed to use `primaryDocument`
- `backend/services/supply_chain.py` — removed dead `^BDI` fetch
- `backend/services/signal_engine.py` — updated supply-chain rationale to not reference BDI
