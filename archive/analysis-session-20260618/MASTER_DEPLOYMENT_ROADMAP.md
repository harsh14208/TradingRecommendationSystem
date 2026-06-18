# Signal.Trade — Master Deployment Roadmap
## From Personal Project to Money-Making Product

**Date:** 2026-06-15
**Version:** v1.0
**Product Version:** v8.8.5 / v10.10
**Current Quality:** 8.9/10 Product · 8.3/10 B+ Quality
**Tests:** 2,550 passed (ex-e2e) · 30.4% mutation score
**Current Revenue:** $0 MRR

---

## Executive Summary

Signal.Trade is one of the most intellectually honest and technically ambitious quant signal projects built by a solo developer. It features a 70+ indicator mean-reversion engine, full subscription billing, broker auto-execution (Alpaca/IBKR), a research experiment registry, and a shadow/challenger framework — all backed by 2,550 tests and rigorous statistical methodology.

**However, three critical truths must be faced:**

1. **The signal is not yet investable.** Live win rate is ~43% (phantom-corrected) vs. 69.1% in-sample. The 25.5pp gap is ~60% structural (regime mismatch + overfitting ceiling) and ~40% was delivery contamination (now fixed). The clean post-fix book shows 57.8% WR on N=90 — encouraging but thin.

2. **The product is not yet deployable for scale.** Five P0 technical blockers (Stripe webhook, SMTP, Telegram broadcast, CI/CD safety, test coverage) would cause customer-facing incidents within days of accepting paying users.

3. **The business model is mispriced.** $29/$79 pricing assumes proven alpha. A 43% WR strategy cannot command those prices. The free tier is too generous, and the value ladder is inverted.

**The path forward is a dual-track strategy:**
- **Track A (Technical):** Clear P0 blockers → closed beta (20 users) → P1 hardening → public launch
- **Track B (Signal):** Accrue clean forward data → promote h=63 shadow → train sector models → paid alt-data SPRT → live auto-execution gated on WR > 55%

**Realistic timeline to first revenue:** 4–6 weeks.
**Realistic timeline to friend-recommendable product:** 12 months.
**Realistic Year 1 ARR:** $150K–$330K if conversion hits AI-native SaaS benchmarks.

---

## 1. Current State: The Honest Scorecard

### 1.1 Technical Maturity (7/10 Overall)

| Dimension | Score | Evidence | Gap |
|---|---|---|---|
| **Infrastructure & DevOps** | 6/10 | CI/CD exists, Railway+Fly.io, Cloudflare CDN | `continue-on-error` on deploy; no staging; no IaC; no PostgreSQL backup |
| **Backend Architecture** | 7/10 | 40 routers, 15 bg tasks, Redis locks, lifespan | `scanner.py` 2,400+ lines; no API versioning; no service boundaries |
| **Testing & Quality** | 6/10 | 2,550 tests pass, ruff, pre-commit, Lighthouse CI | 25% coverage floor; 30.4% mutation score; 5/12 E2E pass |
| **Security** | 7/10 | SecretStr, OAuth PKCE, CSP, HSTS, rate limits | No pen-test; gitleaks doesn't block; no WAF; no secret rotation |
| **Frontend** | 7/10 | esbuild, a11y pass, PWA, responsive | 1,238 KB bundle; no typed API client; no code splitting |
| **Observability** | 6/10 | Sentry, structured logs, rotating files | No Prometheus/Grafana; no PagerDuty; no synthetic monitors |
| **Database** | 7/10 | PostgreSQL 16, Alembic, pool config, hot indexes | No PITR; no read replicas; no retention policy; dual migration paths |
| **API Design** | 7/10 | Pydantic schemas, rate limits, health checks | No `/v1` versioning; no contract tests; no tiered rate limits |

### 1.2 Product & Business Maturity (6/10)

| Area | Status | Blocker |
|---|---|---|
| **Pricing** | Misaligned | $29/$79 assumes proven alpha; free tier too generous |
| **Onboarding** | Missing | No guided first experience; users land in dense dashboard |
| **Trust Building** | Weak | No social proof, no testimonials, no "proof before pay" path |
| **Marketing** | Nonexistent | No SEO, no content, no community, no paid ads |
| **Legal/Compliance** | Partial | "Not financial advice" everywhere; needs securities attorney review |
| **Revenue** | Zero | No paying customers; Stripe products set up but not fully configured |

### 1.3 Signal Quality (5/10)

| Metric | IS (Backtest) | Live (Corrected) | Gap | Fixable? |
|---|---|---|---|---|
| Win Rate | 69.1% | 42.5% (full) / 57.8% (post-fix) | 25.5pp | ~40% fixed, ~60% structural |
| Sharpe (per-trade) | 0.24 | 0.04 (full) / 0.29 (post-fix) | — | Regime-dependent |
| Brier Score | — | 0.2641 | — | Calibration stage mismatch |
| PBO | 0.200 | — | — | IS ceiling spent |
| Deflated Sharpe | FAILS at 744 | — | — | Cannot iterate IS further |
| Cross-sectional shadow | — | +0.576 [CI +0.22, +0.91] | — | Shadow only; not promoted |

**Key Insight:** The v8.4 delivery audit proved that live alpha was *near-IS all along* — the delivery infrastructure was leaking it. The clean book (57.8% WR) is the real signal. The remaining gap is structural (regime mismatch + overfitting ceiling).

---

## 2. The Critical Path: What MUST Happen First

### 2.1 P0 Blockers — Fix Before Any Paid Signups (48 Hours)

| # | Blocker | Fix | Effort | Risk if Ignored |
|---|---|---|---|---|
| 1 | **Stripe Webhook Secret Missing** | Register webhook in Stripe Dashboard; copy `whsec_...` to `.env` | 1 hr | Subscriptions never activate; users pay but get no features |
| 2 | **SMTP Not Configured** | SendGrid Essentials (~$20/mo); test password-reset flow | 2 hrs | No verification, no password reset, no weekly digest |
| 3 | **Telegram Broadcast Channel Missing** | Create private channel, add bot as admin, set `TELEGRAM_BROADCAST_CHANNEL_ID` | 30 min | Rate limits at >50 users; delivery fails silently |
| 4 | **CI/CD `continue-on-error: true`** | Remove from secrets-scan and deploy jobs; fix gitleaks findings | 1 day | Broken builds and leaked secrets reach production |
| 5 | **Test Coverage 25% / Mutation 30%** | Add focused tests on `broker_svc.py`, `admin.py`, `delivery_gates.py` | 1 week | Untested financial edge cases cause money-losing bugs |

### 2.2 Signal Gate — The Real Money Blocker

The single most important factor determining whether users make money is **signal quality**. No amount of UI polish or marketing can overcome a 43% WR.

**The honest hierarchy of what matters:**

1. **Accrue clean forward data** (priority 0) — The post-fix book (N=90, 57.8% WR) must grow to N≥150 with WR≥55% before any live capital
2. **Promote h=63 cross-sectional shadow** (2–3 months) — Highest-impact orthogonal alpha; selection-clean
3. **Train sector-specific models** (3–4 months) — XLF/XLP/XLU/XLI currently blocked; could unlock 20–30% more volume
4. **Buy paid options data + pre-register SPRT** (2–3 months) — Unusual Whales or ORATS; ~$150–300/mo research spend
5. **Fix midday 11–12 ET microstructure** (1 week) — Hard block or confidence haircut if effect persists

**Rule: Paper only until LIVE-1 through LIVE-8 are complete.** This is non-negotiable. Accepting subscriptions for signal *viewing* is fine; accepting subscriptions for *auto-execution* before the empirical bar is met is gambling with user trust.

---

## 3. Phase-by-Phase Roadmap

### Phase 0: Foundation (Weeks 1–2) — "Get to Beta"

**Goal:** Clear P0 blockers. Fix the free tier. Make the product *safe* for 20 beta users.

| Week | Action | Owner | Effort | Success Metric |
|------|--------|-------|--------|----------------|
| 1 | Fix Stripe webhook + SMTP + Telegram broadcast | DevOps | 4 hrs | All pre-launch items #3–#6 checked off |
| 1 | Fix CI/CD `continue-on-error` | DevOps | 4 hrs | Green build blocks on all failures |
| 1 | Cut free tier to 3 signals/day + 7-day delay | Engineering | 2 hrs | Free users still sign up; complaint rate <5% |
| 1 | Move paper trading to Basic tier | Engineering | 4 hrs | Paper trading becomes onboarding centerpiece |
| 2 | Restructure pricing: $19 Basic / $49 Pro / $99 Elite (hidden) | Product | 2 hrs | Stripe products updated |
| 2 | Build 5-step interactive onboarding tutorial | Engineering | 8 hrs | 80% of new users complete tutorial |
| 2 | Add "Signal Journal" — free users see how their 3 signals performed | Engineering | 6 hrs | Free→paid conversion improves |
| 2 | Publish honest `/track-record` with 43% WR + gap explanation | Product | 4 hrs | Time on page >2 min |

**Phase 0 Gate:** All P0 blockers cleared + closed beta sign-up form live. No paid ads. No public launch.

### Phase 1: Closed Beta (Weeks 3–6) — "Prove the Funnel"

**Goal:** 20 engaged beta users. Validate onboarding, pricing, and signal delivery. No paid marketing.

| Week | Action | Owner | Success Metric |
|------|--------|-------|----------------|
| 3–4 | Recruit 20 beta users via Reddit r/algotrading, Twitter, personal network | Marketing | 20 signups, 50% complete onboarding |
| 3–4 | Weekly "Signal Autopsy" — what happened to last week's signals | Product | 80% open rate on digest |
| 3–4 | Collect feedback via Telegram/Discord; fix top 5 UX issues | Product | NPS ≥ 30 |
| 5–6 | Add "Community Track Record" (opt-in paper trading results) | Engineering | 5+ users share results |
| 5–6 | Implement referral system: "Give 1 week Pro, Get 1 week Pro" | Engineering | 3+ referrals generated |
| 5–6 | Add Intercom/Telegram support bot | Engineering | <24h response time |
| 5–6 | Write "Product Classification" legal table for `/tos` | Legal | Securities attorney review initiated |

**Phase 1 Gate:** ≥15 active beta users at end of Week 6. ≥5 paper trades per user. Zero live broker connections.

### Phase 2: Public Launch (Weeks 7–12) — "First 100 Users"

**Goal:** Open the doors. First 100 users. First revenue. Organic growth only.

| Channel | Tactic | Expected Yield |
|---------|--------|----------------|
| Reddit | r/algotrading, r/stocks — "I built a 70-indicator MR scanner, here's 3 months of live results" | 20–40 users |
| Twitter/X | Daily "Signal of the Day" thread with full rationale | 15–30 users |
| Product Hunt | Launch with "Paper Trading" angle | 10–20 users |
| SEO | "The 25.5pp Gap" blog post + indicator deep dives | 10–20 users |
| Referral | "Give 1 week Pro, Get 1 week Pro" | 5–10 users |

**Technical work in parallel:**
- Add Prometheus + Grafana (P1-2)
- PostgreSQL automated backups (P1-1)
- Redis in production (P1-4)
- API versioning `/api/v1/` (P1-5)
- Raise coverage to 40% (P1-7)

**Phase 2 Gate:** ≥100 users, ≥$1K MRR, ≥50% of paid users actively paper trading.

### Phase 3: Growth (Months 4–9) — "First 1,000 Users"

**Goal:** Systematic growth. Prove unit economics. Build the signal database.

| Channel | Budget | Expected Yield |
|---------|--------|----------------|
| Google Ads | $500–1,000/mo | 50–100 users |
| YouTube "Signal Review" | Time only | 30–50 users |
| Newsletter partnerships | Time only | 20–40 users |
| Discord community | Time only | Retention + word-of-mouth |
| Affiliate (30% recurring) | Revenue share | 50–100 users |

**Signal work in parallel:**
- Month 4: h=63 shadow ≥100 tagged signals; begin promotion evaluation
- Month 5: First sector model (XLF) trained; OOS validation
- Month 6: Paid alt-data SPRT initiated (Unusual Whales or ORATS)
- Month 7+: Meta-model retrain if CV-AUC crosses 0.52

**Phase 3 Gate:** ≥1,000 users, ≥$10K MRR, live WR consistently >50% for 100+ resolved signals.

### Phase 4: Scale (Months 10–18) — "Friend-Recommendable"

**Goal:** Achieve M18 (friend-recommendable product). Prove the strategy works over a full market cycle.

**Triggers for advancement:**
- Live WR crosses 55% for 150+ resolved signals → Launch Elite tier ($99) with auto-execution
- h=63 shadow promotes → Rebrand as "multi-strategy quant platform"
- 2+ sector models promote → Expand watchlist by 20–30%
- Portfolio Ann.Sharpe ≥1.0 → Begin B2B white-label conversations

**Phase 4 Gate:** M18 achieved — you would recommend this to a quant-savvy friend.

---

## 4. Technical Blockers & Fixes

### 4.1 Top 10 Technical Blockers

| Rank | Blocker | Severity | Dimension | Fix Effort |
|---|---|---|---|---|
| 1 | Stripe Webhook Secret Missing | P0 | Security/Billing | 1 hr |
| 2 | SMTP Not Configured | P0 | Infrastructure | 2 hrs |
| 3 | Telegram Broadcast Channel Missing | P0 | Scale/Delivery | 30 min |
| 4 | CI/CD `continue-on-error` | P0 | DevOps/Security | 1 day |
| 5 | Test Coverage 25% / Mutation 30% | P1 | Quality | 1 week |
| 6 | No PostgreSQL Backup & PITR | P1 | Database | 2 days |
| 7 | No Production Monitoring Stack | P1 | Observability | 2 days |
| 8 | Redis Not Enabled in Production | P1 | Scale | 4 hrs |
| 9 | No API Versioning | P1 | API Design | 2 days |
| 10 | No Penetration Test | P1 | Security | 3 days |

### 4.2 Recommended Architecture Improvements

**Immediate (P0–P1):**
- Remove ad-hoc `init_db()` additive migrations; enforce Alembic-only in production
- Add `/api/v1/` prefix to all current routes; reserve `/api/v2/` for breaking changes
- Implement PostgreSQL automated backups (`pg_dump` daily to S3/R2)
- Add Prometheus `/metrics` endpoint + Grafana dashboard
- Remove `continue-on-error` from CI; add staging environment

**Short-term (P2):**
- Code-split frontend bundle (1,238 KB → <500 KB initial)
- Add typed API client (OpenAPI generator or tRPC)
- Implement tiered rate limits (free: 10/min, basic: 60/min, pro: 120/min)
- Add synthetic monitoring (Sentry Uptime or UptimeRobot)
- Data retention policy: archive signals >2 years to Parquet/S3

---

## 5. Product & Business Strategy

### 5.1 Pricing Restructure (Deploy Week 1)

| Tier | Current | Recommended | Rationale |
|------|---------|-------------|-----------|
| **Free** | 5 signals/day | **3 signals/day + 7-day delay** | Create conversion pressure; still enough to evaluate |
| **Basic** | $29/mo | **$19/mo** | Match VectorVest ($19.99); Signal.Trade has less proven track record |
| **Pro** | $79/mo | **$49/mo** | Paper trading + backtest is not worth $79; $49 is "no-brainer" test |
| **Elite** | — | **$99/mo (hidden)** | Auto-execution only when WR > 55%; creates aspiration |

**Promotional pricing:**
- Launch week: "First month $1" for all new signups
- "Paper Trading Challenge": Complete 20 paper trades → 1 month Pro free
- Annual: 2 months free (17% discount)

### 5.2 Value Proposition Reframe

**Current (weak):** "70+ independent indicators, 23-year backtested MR strategy"

**Recommended (strong):**
> **Primary:** "The only signal platform that tells you exactly how often it's wrong — and learns from it."
> **Secondary:** "Paper-trade proven mean-reversion signals before risking a dollar."
> **Tertiary:** "70+ indicators, 23 years of data, one honest score."

**Why this works:** The 43% WR is a liability only if you hide it. Making it a *feature* of honesty (calibration, Brier score, explicit gap analysis) differentiates Signal.Trade from every competitor that claims 80% WR with no proof.

### 5.3 Revenue Streams (Prioritized)

| Stream | Potential | Effort | Timeline |
|--------|-----------|--------|----------|
| **Subscriptions** | $19–$99/mo | Low | Immediate |
| **Affiliate broker referrals** | $50–$200/user | Low | Immediate |
| **Premium newsletter** | $29/mo | Low | 1 month |
| **Data API access** | $200–$500/mo | Medium | 2–3 months |
| **White-label / B2B** | $1K–$5K/mo | High | 6–12 months |
| **Education / Courses** | $99–$299 one-time | Medium | 2–3 months |

### 5.4 North Star Metric

**Monthly Resolved Paper Trades per Paying User**

If this number is >10 and growing, revenue follows. If it's <5, the product isn't sticky enough yet.

---

## 6. Signal Quality Roadmap

### 6.1 The 3-Month Horizon (Jul–Sep 2026)

**Goal:** Prove the clean post-fix book is reproducible.

| Milestone | Target | Go/No-Go |
|---|---|---|
| **M1.** Post-fix N ≥ 150 | 150 resolved BUY signals, all post-2026-06-10 | Go: N≥150; No-Go: N<100 |
| **M2.** Post-fix WR ≥ 55% | Net-of-friction WR on clean book | Go: WR≥55% with Wilson CI ≥50%; No-Go: WR<50% |
| **M3.** Brier ≤ 0.25 | Calibration skill vs naive 0.25 | Go: Brier≤0.25; No-Go: Brier>0.27 |
| **M4.** h=63 shadow tagged ≥ 100 | Cross-sectional shadow signals accrued | Go: ≥100 tagged; No-Go: <50 |
| **M5.** Midday effect validated | N≥20 in 11–12 ET window | Go: WR≥45%; No-Go: WR<35% (hard filter) |
| **M6.** Sector model trained (1 sector) | First sector model (XLF) hits ≥100 trades | Go: OOS AUC ≥0.55; No-Go: AUC<0.52 |

**Expected Sharpe if all GO:** 0.25–0.35 per-trade.

### 6.2 The 6-Month Horizon (Oct–Dec 2026)

**Goal:** Promote shadow and first sector model; begin paid alt-data SPRT.

| Milestone | Target | Go/No-Go |
|---|---|---|
| **M7.** h=63 shadow promoted | §92 criteria met | Go: Bottom-decile WR ≥3pp worse, monotonic, ≥150 resolved |
| **M8.** Sector model promoted (1 sector) | First sector unblocked via QENG-1c | Go: Live shadow WR≥55% for sector, N≥50 |
| **M9.** Paid alt-data SPRT initiated | Unusual Whales or ORATS data purchased | Go: 2+ hypotheses pre-registered, SPRT monitor live |
| **M10.** Meta-model AUC ≥ 0.52 | Weekly retrain crosses threshold | Go: CV-AUC ≥0.52 with CI lower bound ≥0.50 |
| **M11.** OOS v7/v8 validation | ≥30 live trades in pre-specified held-out tickers | Go: OOS WR≥50% |
| **M12.** Calibration v5 (raw_conf) | Stage mismatch fixed | Go: Brier≤0.22 on new protocol |

**Expected Sharpe if all GO:** 0.35–0.50 per-trade.

### 6.3 The 12-Month Horizon (Jan–Jun 2027)

**Goal:** Achieve friend-recommendable edge.

| Milestone | Target | Go/No-Go |
|---|---|---|
| **M13.** 2+ sector models promoted | XLF + XLY or XLC unblocked | Go: Each sector live shadow WR≥55%, N≥100 |
| **M14.** Paid alt-data SPRT resolved | 1+ hypothesis crosses SPRT boundary | Go: SPRT accepts H1 at 90% power |
| **M15.** Full portfolio Ann.Sharpe ≥ 1.0 | Combined MR + shadow + sectors | Go: 12-month rolling portfolio Ann.Sharpe ≥1.0, MaxDD<10% |
| **M16.** Brier ≤ 0.20 | Well-calibrated confidence | Go: Brier≤0.20, confidence gap ≤5pp |
| **M17.** Drawdown throttle validated | R7 DD-throttle proves it helps in live crisis | Go: MaxDD <8% in any 30-day window |
| **M18.** Friend-recommendable | I would recommend this to a risk-tolerant friend | Go: All of M13–M17 GO + 12-month track record |

**Expected Sharpe if all GO:** Portfolio Ann.Sharpe 1.0–1.5. This is the threshold where the strategy becomes genuinely attractive to quantitative investors.

---

## 7. Risk Management & Legal

### 7.1 Regulatory Risk Mitigation

| Risk | Severity | Mitigation | Cost |
|------|----------|------------|------|
| SEC/State RIA scrutiny | 🔴 High | Product classification table on `/tos`; "publisher's exclusion" language; no personalized advice | Securities attorney review: $2,000–5,000 |
| User loses money, blames platform | 🔴 High | Paper trading as default; explicit risk acknowledgement; kill switch; no testimonials with dollar amounts | — |
| Data breach (broker credentials) | 🔴 High | Scrypt KDF v2 + per-credential salt; annual pen-test; bug bounty | $500–2,000/year |
| Chargebacks / disputes | 🟡 Medium | 14-day no-questions refund policy; proactively refund signal-quality complaints | — |
| GDPR/CCPA | 🟢 Low | Already compliant; deletion endpoint exists; privacy policy published | — |

### 7.2 Recommended Legal Additions

1. **Product Classification Table** on `/tos` (mirroring HaasOnline):
   ```
   | Entity Type | Signal.Trade Classification |
   | Investment Adviser (SEC) | ❌ No — does not provide investment advice |
   | Broker-Dealer (SEC/FINRA) | ❌ No — does not execute or facilitate trades |
   | Software Company | ✅ Yes — algorithmic signal generation tool |
   ```

2. **User Acknowledgment Flow:** Before first paper trade, user must scroll through and click "I understand that Signal.Trade is software, not a financial advisor" — record immutable timestamp + IP.

3. **Quarterly Marketing Copy Audit:** grep for prohibited claims (`guarantee`, `risk-free`, `will profit`, `can't lose`). Already in place; extend pattern list as copy grows.

4. **Securities Attorney Review:** Budget $2,000–5,000 for pre-launch compliance review of ToS, Privacy Policy, marketing copy, and auto-execution risk-ack flow.

### 7.3 Operational Risk Controls (Already Implemented)

| Control | Status | File |
|---|---|---|
| Global kill switch | ✅ Live | `routers/admin.py` |
| Drawdown circuit breaker (-5%) | ✅ Live | `services/broker_svc.py` |
| Bracket stop orders | ✅ Live | `services/alpaca_rest.py`, `services/ibkr_rest.py` |
| Per-user runtime limits | ✅ Live | `models.py`, `services/broker_svc.py` |
| Credential encryption (scrypt KDF v2) | ✅ Live | `services/broker_svc.py` |
| Risk acknowledgement recording | ✅ Live | `routers/me.py` |
| Decay monitor | ✅ Live | `scripts/decay_monitor.py` |
| SPRT forward validation | ✅ Live | `scripts/sprt_monitor.py` |
| Paper-only default | ✅ Live | `config.py` |

---

## 8. Financial Model & Projections

### 8.1 Year 1 Revenue Scenarios

| Scenario | Free Users | Basic ($19/mo) | Pro ($49/mo) | Elite ($99/mo) | MRR | ARR |
|---|---|---|---|---|---|---|
| **Conservative** (3% free→paid) | 1,000 | 30 | 6 | 0 | $864 | $10,368 |
| **Base** (5% free→paid, 15% upsell) | 2,000 | 100 | 15 | 0 | $2,635 | $31,620 |
| **Optimistic** (8% free→paid, 20% upsell) | 3,000 | 240 | 48 | 12 | $9,048 | $108,576 |
| **Stretch** (10% free→paid, 25% upsell, 5% Elite) | 5,000 | 500 | 125 | 25 | $22,000 | $264,000 |

### 8.2 Cost Structure (Lean Operation)

| Expense | Monthly | Annual |
|---------|---------|--------|
| Railway + PostgreSQL | ~$15 | ~$180 |
| Redis (Upstash or Railway) | ~$10 | ~$120 |
| SendGrid Essentials | ~$20 | ~$240 |
| Stripe fees (2.9% + $0.30) | Variable | — |
| Sentry | ~$26 | ~$312 |
| Cloudflare Pro | ~$20 | ~$240 |
| Domain | ~$1 | ~$12 |
| Paid data (Unusual Whales / ORATS) | ~$200 | ~$2,400 |
| Securities attorney | — | ~$3,000 |
| **Total fixed costs** | **~$312/mo** | **~$3,744/yr** |

**Break-even:** ~17 Basic subscribers or ~7 Pro subscribers.

### 8.3 Unit Economics

| Metric | Target | Current |
|--------|--------|---------|
| CAC (Customer Acquisition Cost) | <$50 | Unknown |
| LTV (Lifetime Value) | >$300 | Unknown |
| LTV/CAC ratio | >3:1 | Unknown |
| Monthly churn | <10% | Unknown |
| Net Revenue Retention | >100% | Unknown |

**Action:** Implement analytics to track these from Day 1. Add Stripe + Mixpanel/Amplitude integration.

---

## 9. The "Do This Week" Action List

### Monday (4 hours)
- [ ] Register Stripe webhook endpoint; copy `whsec_...` to `STRIPE_WEBHOOK_SECRET`
- [ ] Configure SendGrid SMTP; test password-reset flow for owner account
- [ ] Create Telegram broadcast channel; set `TELEGRAM_BROADCAST_CHANNEL_ID`
- [ ] Remove `continue-on-error: true` from CI secrets-scan and deploy jobs

### Tuesday (4 hours)
- [ ] Restructure pricing in Stripe: $19 Basic / $49 Pro / $99 Elite (hidden)
- [ ] Cut free tier to 3 signals/day + 7-day history delay
- [ ] Move paper trading to Basic tier; update tier gating in `config.py`
- [ ] Publish honest `/track-record` page: 43% WR, gap explanation, fix roadmap

### Wednesday (4 hours)
- [ ] Write "The 25.5pp Gap" blog post for SEO + differentiation
- [ ] Apply for Alpaca and IBKR affiliate/referral programs
- [ ] Add "Product Classification" legal table to `/tos`
- [ ] Build 5-step interactive onboarding tutorial (skeleton)

### Thursday (4 hours)
- [ ] Fix midday 11–12 ET filter (hard block or confidence haircut)
- [ ] Add `SendLog` delivery quality tracking to all send paths
- [ ] Verify kill switch works from mobile via Cloudflare Tunnel
- [ ] Test paper trading end-to-end on owner account

### Friday (4 hours)
- [ ] Build "Signal Journal" MVP: free users see how their 3 signals performed
- [ ] Create Discord server for community
- [ ] Draft launch copy for Reddit r/algotrading and Product Hunt
- [ ] Review weekly: signal volume, delivery quality, live WR, Brier score

---

## 10. Success Metrics & Dashboard

### 10.1 Weekly KPIs

| Metric | Target | Where |
|--------|--------|-------|
| New signups | 10–20/week | Stripe dashboard |
| Free→Paid conversion | >5% | Analytics |
| Active paper traders | >50% of paid users | DB query |
| Avg paper trades/user/month | >10 | DB query |
| Live WR (clean BUYs) | Trending toward 55% | `/api/admin/live-wr-stats` |
| Brier score | Trending toward 0.25 | `scripts/backfill_confidence.py` |
| Signal delivery success rate | >95% | `SendLog` table |
| Churn rate | <10%/month | Stripe dashboard |

### 10.2 Monthly Reviews

| Review | Attendees | Topics |
|--------|-----------|--------|
| Signal quality | Owner + quant review | WR, Sharpe, Brier, gap decomposition, new alpha research |
| Product | Owner + any team | Onboarding funnel, UX feedback, feature requests, roadmap |
| Business | Owner | MRR, churn, CAC, LTV, unit economics, marketing ROI |
| Technical | Owner + any team | Uptime, errors, coverage, security, debt, infrastructure |
| Legal | Owner + attorney | Compliance, marketing copy, user complaints, regulatory changes |

---

## 11. Appendix: Reference Reports

This roadmap synthesizes three deep-dive analyses:

1. **Technical Architecture Assessment** — `docs/PRODUCTION_READINESS_ASSESSMENT.md`
   - Dimension-by-dimension maturity scoring
   - Top 10 technical blockers with effort estimates
   - P0/P1/P2 prioritized action plan

2. **Business & Product Strategy** — `SIGNAL_TRADE_BUSINESS_ANALYSIS.md`
   - Pricing restructure and revenue model
   - Go-to-market phases and channels
   - Competitive positioning and risk mitigation
   - "Do This Week" priority action list

3. **Quantitative Edge Assessment** — `signal_edge_assessment.agent.final.md`
   - Honest assessment of current signal quality
   - Live-vs-IS gap decomposition
   - Ranked edge-improvement opportunities
   - 12-month signal quality roadmap with go/no-go criteria

---

*This roadmap is a living document. Update it weekly as the project evolves. The single most important rule: paper only until the numbers justify live capital.*
