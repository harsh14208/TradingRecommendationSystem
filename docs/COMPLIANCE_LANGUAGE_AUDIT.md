# Compliance Language Audit (TSYS-13a)

**Scope:** product, marketing, email, and in-app copy for regulated-advice risk —
with emphasis on auto-execution, copy-trading-like workflows, and performance claims.

**Method:** grep across `frontend/`, `backend/`, `docs/` for prohibited-claim
patterns (`guarantee[d]`, `risk-free`, `will profit`, `can't lose`, `sure thing`,
`riskless`) and for the presence of required disclaimers (`not financial advice`,
`past performance`, `informational/educational purposes`). Last run: 2026-06-07.

## Findings

| Pattern | Count | Verdict |
|---|---|---|
| `risk-free` | 14 | ✅ All legitimate — "risk-free **rate**/bonds/hurdle" in scoring (`assembler.py`, `signal_engine.py`, `calc_tbd_metrics.py`). No marketing "risk-free returns". |
| `guarantee[d]` | 8 | ✅ All legitimate — disclaimers ("does not **guarantee** future results") + code comments ("guarantees alignment"). No "guaranteed profit". |
| `will profit` / `can't lose` / `riskless` / `sure thing` | 0 | ✅ None present. |
| `not financial advice` | 16 | ✅ Disclaimers present in README, email footer (`email_svc.py`), Discord embeds, Telegram. |
| `past performance` disclaimer | present | ✅ README + email footer. |

**No prohibited performance or suitability claims were found.** Signal.Trade
copy already positions output as "algorithmic, informational/educational" and
states it is "not a registered investment adviser, broker-dealer, or financial
planner" ([docs/README.md](README.md)).

## Required-disclaimer coverage by surface

| Surface | Disclaimer present? |
|---|---|
| README / public site | ✅ |
| Email (digest/alert footer) | ✅ `email_svc.py` |
| Telegram / Discord signal messages | ✅ "NOT FINANCIAL ADVICE" footer |
| **Live broker auto-execution** | ✅ Gated by an explicit risk acknowledgement (TSYS-13b): `POST /api/me/risk-acknowledge` is required before a live broker connection, and the acknowledgement is recorded immutably (TSYS-13c). |

## Recommendations (non-blocking)

1. **Surface the disclosure text in the risk-ack UI** (TSYS-11a): the backend gate
   exists, but the frontend must render the suitability/risk disclosure before the
   user calls `risk-acknowledge` so consent is informed, not just recorded.
2. **Avoid "recommendation" framing in auto-execution copy** — prefer "algorithmic
   signal" to reduce RIA-advice ambiguity when orders are placed automatically.
3. **Re-run this audit before each marketing push** — the grep patterns above are
   the canonical check; add new prohibited terms as marketing copy expands.

> This audit is engineering due diligence, not legal advice. A securities/fintech
> attorney should review before any paid marketing or live-trading GA.
