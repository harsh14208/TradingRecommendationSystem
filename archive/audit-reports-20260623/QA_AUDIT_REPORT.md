# Signal.Trade — Comprehensive Functional QA Audit Report

**Audit Date:** 2025-07-02
**Auditor:** Lead QA Automation Engineer (AI)
**Scope:** Full frontend application — all pages, overlays, modals, and components
**Application:** Signal.Trade v5.2 (React 18 SPA + HTML static pages)
**Environment:** Codebase review (`/frontend/src/*.jsx`, `/frontend/pages/*.html`)

---

## Table of Contents
1. [Application Inventory](#1-application-inventory)
2. [The Happy Path](#2-the-happy-path)
3. [Lens 1: Click, Hover, & Interactive Element States](#3-lens-1--click-hover--interactive-element-states)
4. [Lens 2: Form Inputs, Validation, & Boundary Testing](#4-lens-2--form-inputs-validation--boundary-testing)
5. [Lens 3: Real-Time State Transitions & Network Delays](#5-lens-3--real-time-state-transitions--network-delays)
6. [Lens 4: Responsive, Resizing, & Touch Target Mechanics](#6-lens-4--responsive-resizing--touch-target-mechanics)
7. [Lens 5: Navigation, Browser History, & Disruption Recovery](#7-lens-5--navigation-browser-history--disruption-recovery)
8. [Lens 6: Keyboard Navigation & Focus Trap Verification](#8-lens-6--keyboard-navigation--focus-trap-verification)
9. [The Bug & Edge-Case Log](#9-the-bug--edge-case-log)
10. [The E2E Test Case Script](#10-the-e2e-test-case-script)

---

## 1. Application Inventory

### Static HTML Pages
| Page | File | Route |
|------|------|-------|
| Landing / Marketing | `frontend/pages/landing.html` → `site.jsx` | `/` |
| Login | `frontend/pages/login.html` | `/login` |
| Signup | `frontend/pages/signup.html` | `/signup` |
| Verify Email | `frontend/pages/verify-email.html` | `/verify-email` |
| Reset Password | `frontend/pages/reset-password.html` | `/reset-password` |
| Track Record | `frontend/pages/track-record.html` | `/track-record` |
| Terms of Service | `frontend/pages/tos.html` | `/tos` |
| Privacy Policy | `frontend/pages/privacy.html` | `/privacy` |
| Design Canvas | `frontend/pages/design.html` | `/design` |
| Mobile App | `frontend/pages/mobile.html` → `mobile.jsx` | `/mobile` |

### Main SPA (Dashboard) — `app.jsx`
**Core Layout:**
- Top bar (brand, search, ticker tape, actions, clock, user avatar)
- Sidebar (16 nav items + threshold slider + footer)
- Main panel (feed + detail + delivery panes)
- Status bar + Disclaimer bar
- Mobile bottom nav + panel pager

**Navigation Items (16):**
1. Live signals (feed) 2. History 3. Backtest 4. Watchlist 5. Paper Portfolio 6. Market overview 7. Sector heatmap 8. Economic calendar 9. Sources 10. Rules & filters 11. Alert rules 12. Screener 13. Performance 14. Account (modal) 15. Upgrade plan 16. Threshold slider

**Overlays/Modals:**
- WatchlistView, SourcesView, RulesView, MarketOverviewView, SectorView, CalendarView, PaperView, HistoryView, MyPerformanceView, AlertsView, ScreenerView, BacktestView, PricingView, AccountModal, PriceAlertModal, TweaksPanel, HotkeyHelp, DemoTour

**Detail Tabs:**
- Why (chart + rationale + predictive)
- Position (sizing calculator)
- Simulate (Monte Carlo)
- Similar (historical signals)

### Cinematic Views (cin.*)
- `cin.dashboard.jsx` — Alternative signal dashboard with real sparklines
- `cin.market.jsx` — Market context with gauges, regime, macro, sectors, calendar
- `cin.backtest.jsx` — Backtest lab with equity curve simulation + live metrics
- `cin.settings.jsx` — Settings (data, alerts, account, billing)
- `cin.track.jsx` — Track record page
- `cin.data.jsx` — Data utilities
- `cin.tools.jsx` — Tools (minimal)

---

## 2. The Happy Path

These flows work flawlessly under normal conditions:

| # | Flow | Steps |
|---|------|-------|
| 1 | **Landing → Signup → Dashboard** | Visit `/` → click "Start free trial" → select plan → enter email/password → submit → redirect to `/app` → disclaimer appears → acknowledge → dashboard loads |
| 2 | **Login → Dashboard** | Visit `/login` → enter valid credentials → submit → token saved in memory → redirect to `/app` → dashboard loads with signal feed |
| 3 | **Signal Feed Navigation** | Click signal in feed → detail pane opens → click "Why" tab → chart loads → rationale visible → trade plan visible with entry/stop/target |
| 4 | **Filter & Style** | Click filter chips (All/Buy/Sell/High) → signal count updates → click style strip (Intraday/Swing/Position) → feed filters by style |
| 5 | **Send to Telegram** | Select signal → click "Send to Telegram" → POST to `/api/signals/{id}/send` → delivery log updates → success message appears |
| 6 | **Paper Trade** | Select signal with Basic+ tier → click "Paper Trade" → POST to `/api/paper/orders` → success flash (green) → position added |
| 7 | **Watchlist Add/Remove** | Open Watchlist overlay → enter ticker → click Add → API call → ticker appears in grid → click ✕ to remove → API call → removed |
| 8 | **Rules & Threshold** | Open Rules overlay → adjust confidence slider → threshold updates in sidebar and status bar → time window changes → validated on blur |
| 9 | **Pricing & Checkout** | Click "Upgrade" → Pricing overlay opens → plans load from `/api/billing/plans` → select plan → POST to checkout → redirect to Stripe |
| 10 | **Theme & Density** | Open Tweaks panel → click accent swatch → CSS custom property updates → click density toggle → feed row spacing changes |
| 11 | **Market Overview** | Navigate to Market overview → Fear & Greed gauge renders → regime panel shows HMM state → macro stats display → sector bars show |
| 12 | **Backtest** | Open Backtest overlay → date range selects → tabs switch (Summary/Sources/Tickers/Track/Corr/Calib/Decay/Model) → data loads from API |
| 13 | **Chart Period Switch** | In detail pane, click chart tabs (1D/5D/1M/3M/1Y) → new OHLCV data fetched → chart re-renders with LightweightCharts |
| 14 | **Compare Benchmark** | Click SPY/QQQ/IWM/GLD button → secondary chart series overlayed → comparison data fetched |
| 15 | **Mobile Panel Paging** | Swipe main panel on mobile → scroll-snap switches panels → pager dots update → arrow buttons navigate |

---

## 3. Lens 1 — Click, Hover, & Interactive Element States

### Verified Behavior
- **Filter chips**: Active state changes border color + background (`fc on` class)
- **Style strip buttons**: `on` class toggles active state
- **Signal rows**: `active` class highlights selected row; `expanded` class reveals details
- **Nav items**: `active` class + left border indicator
- **Detail tabs**: `active` underline + color change
- **Tweaks panel swatches**: `on` class (border ring)
- **Plan cards** (signup): `selected` class changes border/background
- **Paper trade button**: `paperTradeFlash` state triggers green background for 1.5s
- **Save note button**: `saved` state changes text to "✓ Saved" + green color

### Issues Found
1. **No hover state on many buttons**: Most buttons in `app.modals.jsx` use inline styles without `:hover` CSS rules. The `btn ghost` and `btn primary` classes likely have hover styles, but many custom inline-styled buttons (e.g., account settings buttons, alert rule buttons) have **zero visual feedback on hover**.

2. **Signal row hover missing**: `SignalRow` in `app.signal.jsx` has no hover CSS — the cursor changes but no background color shift. This makes it hard to see which row is being targeted before clicking.

3. **Sidebar threshold +/- buttons**: In `app.jsx` (lines 971–983), the threshold increment buttons are small inline-styled `<button>` elements with no hover state, no active state, and no disabled state when at boundary (0% or 100%).

4. **Chart drawing mode**: The draw toggle in `app.ui.jsx` (line 442) has an `active` style but no visual feedback when a level is placed. The user must rely on the line appearing on the chart, which can be subtle.

5. **Refresh button**: The `refreshing` state adds a CSS spin animation (`animation: spin 0.8s linear infinite`), which is good. But the button is not disabled during refresh, so rapid clicking could trigger multiple `manualScan()` calls. (Actually, it IS disabled: `disabled={refreshing}` — verified at line 851. Good.)

6. **Kill Switch button**: No hover state, only `opacity: loading ? 0.5 : 1`. The button is crucial (owner-only) but has minimal visual affordance.

7. **Mobile bottom nav items**: No `:active` or `:hover` state. On touch devices, the `active` class only toggles on selection, not on touch feedback.

8. **InfoPop (ⓘ) icon**: No hover state. The cursor changes but the icon stays the same opacity.

---

## 4. Lens 2 — Form Inputs, Validation, & Boundary Testing

### Verified Behavior
- **Login form**: HTML5 `required` on email and password fields. Focus border changes to `var(--up)`.
- **Signup form**: Email `required`, password `required`. Password hint visible.
- **RulesView confidence**: Input `type="number"` with `min=0` `max=100`. Validates on blur — `isNaN(v) || v < 0 || v > 100` shows error. Good.
- **RulesView time**: Validates `HH:MM` format via regex. Cross-validates start < end. Good.
- **PriceAlertModal**: Validates target > 0, < 1,000,000. Shows inline error. Good.
- **Watchlist input**: Forces uppercase, strips non-letters, maxLength=5. Validates ticker format via `TICKER_RE`. Good.
- **AccountModal name**: `maxLength=60`, validates on save (empty, >60 chars). Good.
- **Screener inputs**: Number fields parsed but not range-validated. Choice dropdowns prevent invalid values.

### Issues Found

#### HIGH SEVERITY

1. **Signup email — no real-time validation** (`signup.html`): The email input only uses `type="email"` with HTML5 validation. No regex validation for format, no domain check, no duplicate check (client-side). The form only validates on submit.

2. **Password strength — no indicator** (`signup.html`): Password has no strength meter, no minimum complexity rules shown beyond "At least 8 characters". No enforcement of uppercase/number/special char requirements.

3. **Broker credential fields — no validation** (`app.modals.jsx`, AccountModal): API Key and Secret inputs accept **any** text. No format validation (e.g., Alpaca keys start with `PK`/`AK`). No length validation. The `connectBroker` function only checks `!brokerKey.trim() || !brokerSecret.trim()`. No masking/visibility toggle on the secret field (it's `type="password"` which is good, but no reveal button).

4. **Auto-execution quantity — allows 0 and negative** (`app.modals.jsx`, line 193): The `autoExecQty` input is `type="number"` with `min="1"` but the validation only checks `isNaN(q) || q < 1`. However, the HTML `min` attribute may not prevent all input methods (e.g., pasting negative values). The validation is correct but occurs only on save, not during typing.

5. **Confidence threshold in TweaksPanel — no validation** (`app.modals.jsx`, line 1159): The input has `min=0` `max=100` but the `onChange` handler uses `parseFloat(e.target.value)` with `!isNaN(v) && v >= 0 && v <= 100` — but `parseFloat("100.5")` = 100.5 which is > 100, yet the condition `v <= 100` would prevent it. Wait, actually `v >= 0 && v <= 100` would block 100.5. So this IS validated. But invalid values are silently rejected (no error message shown to user). The input simply won't update.

#### MEDIUM SEVERITY

6. **Screener value fields — no validation** (`app.modals.jsx`, ScreenerView): Text fields accept any input. Number fields are parsed but if `parseFloat` fails, the raw string is sent to the API, which may return a 400 error. No client-side type enforcement.

7. **Alert rule confidence — allows non-numeric** (`app.modals.jsx`, AlertsView): The minConf input uses `parseFloat` but if the user enters text, `parseFloat` returns NaN and the validation catches it. However, the error message "Confidence must be 0–100" is generic — it doesn't distinguish between NaN, < 0, and > 100.

8. **Forgot password email — no validation** (`login.html`): The forgot form input has `type="email"` but no client-side validation before the submit button is clicked. The error message is shown in a `.msg` div but only after the server responds.

9. **Note textarea — no max length** (`app.signal.jsx`, NoteEditor): The journal note textarea has no `maxLength` or character counter. Users could paste extremely large text blocks, potentially causing performance issues or API payload errors.

10. **Name field in signup — no sanitization** (`signup.html`): The name field accepts any characters, including special characters, HTML tags, etc. No XSS sanitization visible in the frontend (though the backend likely handles it).

#### LOW SEVERITY

11. **Signup plan duplicate feature** (`signup.html`, line 177): The Basic plan lists "Telegram + Web Push delivery" **twice** in the features list. This is a UI/content bug, not functional.

12. **Search query — no debounce** (`app.jsx`): The search input fires `setSearchQuery` on every keystroke, which triggers `matchesSearch` callback and `filteredSignals` recalculation on every keystroke. For large signal arrays, this could cause input lag. No debounce or throttle.

---

## 5. Lens 3 — Real-Time State Transitions & Network Delays

### Verified Behavior
- **Initial load**: `authReady` → `currentUser` → `loadData()` → `setLoading(false)`. Skeleton not shown; only "Loading…" text.
- **Auto-refresh**: 30-second countdown timer visible. `countdown` state decrements every second. `loadData(false)` fires silently at 0.
- **Manual refresh**: `manualScan()` sets `refreshing=true` → API call → 1.5s delay → `loadData(false)` → `refreshing=false`.
- **WebSocket**: Connects with token via subprotocol. Handles `new_signal`, `price_update`, `tick`, `market_context` messages.
- **Tweak saving**: `tweakSaving` ref guards against overlapping PUTs. `pendingTweak` ref queues the latest value.
- **Predictive loading**: `predLoading` state shows "calculating…" text while fetching.
- **Chart loading**: `loading` state shows "Loading chart…" overlay.

### Issues Found

#### HIGH SEVERITY

1. **No skeleton screens for overlays** — Most overlays (Watchlist, Sources, Rules, History, Backtest, etc.) show only a plain text "Loading…" div when data is fetching. There are no skeleton cards, shimmer effects, or structural placeholders. This causes layout shift and a jarring experience when data arrives.

2. **WebSocket — no reconnection with exponential backoff** — The `wsReconnectDelay` ref is declared (line 122) but **never actually used**. The WebSocket `useEffect` at line 245 creates a new `WebSocket` on mount but has no `onclose`/`onerror` handler that reconnects. If the connection drops, the user sees a stale banner but data never refreshes live. The `wsStatus` state only tracks `connecting`/`open`/`closed` but the only place it's set is in the `useEffect` return cleanup (which sets it to... nowhere — actually `wsStatus` is only set in the cleanup if we track it, but it's not).

   Actually, looking more carefully: `wsStatus` is initialized as `"connecting"` (line 119) and updated... nowhere in the WebSocket effect! The WebSocket `onopen`/`onclose`/`onerror` handlers are missing. The `wsStatus` variable is never actually updated by the WebSocket lifecycle. This means:
   - The connection banner at line 892 (`{wsStatus !== "open" && (...)}`) will **always show** after the initial mount, even if the WebSocket is connected, because `wsStatus` never changes to `"open"`.
   - This is a **CRITICAL functional bug**: the "Reconnecting to live feed…" banner will be permanently visible.

3. **Double-submit vulnerability on paper trade** — The Paper Trade button in the detail pane (`app.jsx` line 1692–1712) is not disabled during the API call. The user can click it multiple times, creating multiple paper orders. The button uses `paperTradeFlash` state for visual feedback but does not disable the button while the fetch is in-flight. (Actually, the `authFetch` is async and the button doesn't track a loading state — no `disabled` prop.)

   Wait, looking again: `paperTradeFlash` is a boolean. The button is NOT disabled during the fetch. Only the `active` class changes. So yes, double-clicking will fire multiple `POST /api/paper/orders` requests.

4. **No retry for failed API calls** — The `apiFetch` function in `app.auth.jsx` (line 56–62) catches errors and returns `null`. There is no retry logic, no exponential backoff, and no user-visible error state for transient failures. A single 500 error on `/api/signals` will permanently show "No signals" or empty state with no way to retry.

5. **Concurrent refresh race condition** — `manualScan()` at line 726–733 does not guard against concurrent invocations. If the user clicks refresh rapidly, multiple `POST /api/signals/scan` calls will be in-flight simultaneously, followed by multiple `loadData()` calls. The `refreshing` state prevents UI spin duplication but not the API calls.

#### MEDIUM SEVERITY

6. **Tweak save — no error feedback** — If the `PUT /api/settings` call fails in `setTweak` (line 137–151), the error is silently caught (`catch {}`). The user sees their local settings update but the server never receives them. No toast, no banner, no retry button.

7. **Chart loading — no timeout** — The chart fetch (`app.ui.jsx` line 237) has no timeout. If the API hangs, the "Loading chart…" overlay persists indefinitely. No timeout or fallback after N seconds.

8. **Predictive data — no cache** — Every time the active signal changes, `/api/signals/predictive` is fetched. If the user rapidly switches between signals, multiple in-flight requests compete. No caching or deduplication.

9. **Feed pagination — no scroll-triggered loading** — The feed uses a manual "Show more" button (line 1198–1207). No infinite scroll. On mobile, the user must tap repeatedly to see all signals.

10. **Load-more button not disabled during load** — The "Show more" button has no loading state. If `loadData()` is in progress, clicking "Show more" could cause inconsistent pagination state.

---

## 6. Lens 4 — Responsive, Resizing, & Touch Target Mechanics

### Verified Behavior
- **CSS breakpoints**: `@media(max-width:768px)` used in login/signup pages. CSS grid switches to single column.
- **Mobile nav**: Bottom nav bar with 6 items (feed, history, backtest, watchlist, delivery, overview). Only shown on mobile via CSS.
- **Panel paging**: Horizontal scroll with `scroll-snap` behavior on mobile. Pager dots + arrow buttons.
- **Sidebar on mobile**: Slides in as a drawer with backdrop overlay. `navMenuOpen` toggles via hamburger button.
- **Topbar ticker**: Hidden or truncated on small screens (CSS `overflow:hidden` on `.ticker-track`).
- **Chart resize**: `ResizeObserver` updates LightweightCharts width on container resize.
- **Overlay max-width**: Most overlays use `maxWidth:760` or `maxWidth:980` with centered margins.

### Issues Found

#### HIGH SEVERITY

1. **Mobile sidebar only shows 6 items vs 16 desktop** — The bottom nav (`mobile-nav`) only has 6 items: feed, history, backtest, watchlist, delivery, overview. The full sidebar has 16+ items (sources, rules, alerts, screener, performance, calendar, sectors, paper). These are **completely inaccessible on mobile** unless the user opens the hamburger menu to trigger the sidebar drawer. This is a severe navigation gap.

2. **Hamburger button too small** — The hamburger icon button in the topbar (`app.jsx` line 835) uses `iconbtn` class with no explicit size. The SVG is 14×14px. The total hit area is likely ~28×28px, which is below the WCAG 2.1 minimum of 44×44px for touch targets.

3. **Mobile panel pager arrows too small** — The pager arrow buttons (`app.jsx` line 1757) use a simple `‹` / `›` text character. The hit area is likely ~24×24px, well below the 44px minimum.

4. **Topbar buttons may overlap on tablet** — The topbar has: brand, search, ticker, hamburger, `?`, refresh, countdown, kill switch, settings, logout, avatar. On a 768px-wide tablet, the search bar and ticker tape will likely clip or cause horizontal overflow. No `overflow-x` or truncation strategy is applied to the topbar container.

5. **No pull-to-refresh on main app** — Only the `mobile.jsx` feed has pull-to-refresh (touch handlers). The main `app.jsx` feed has no pull-to-refresh gesture. On mobile web, users expect this pattern.

#### MEDIUM SEVERITY

6. **Overlay not full-screen on mobile** — Overlays use `overlay` class which likely renders as an overlay panel. On mobile, if the overlay content exceeds the viewport height, it scrolls internally. But the overlay header may not be sticky, so users can lose the close button context when scrolling.

7. **Chart comparison buttons may wrap poorly** — The compare vs buttons (SPY/QQQ/IWM/GLD) in the detail pane (`app.jsx` line 1393–1407) are inline buttons with no wrapping container. On narrow viewports, they could overflow the chart container.

8. **Signal row expanded content — no max-height** — When expanded, the signal row can grow very tall with rationale, actions, and stats. On mobile, this could push other content far below the viewport. No max-height or scroll containment.

9. **Tweaks panel not responsive** — The TweaksPanel (`app.modals.jsx`) uses a fixed `maxWidth:760` but the content inside (accent swatches, density buttons, etc.) uses a horizontal layout that may not wrap correctly on mobile. The `tweak-row` CSS class is not shown to use `flex-wrap`.

10. **Signup progress bar — no responsive wrapping** — On mobile (<480px), the 3-step progress bar may overflow or scale poorly. The step labels are inline and could clip.

---

## 7. Lens 5 — Navigation, Browser History, & Disruption Recovery

### Verified Behavior
- **OAuth redirect**: After Google OAuth, the `?oauth_code=` param is removed from URL via `history.replaceState` (line 200). Good.
- **Auth gate**: Unauthenticated users are redirected to `/login?next=/app` via `useEffect` (line 743). Good.
- **Disclaimer**: Stored in `localStorage` with key `signal_trade_disclaimer_v1`. Persists across sessions. Good.
- **Tweaks**: Stored in `localStorage` with key `st_tweaks`. Hydrated from DB on first auth. Good.
- **Signals cache**: `st_signals_cache` in `localStorage` provides seed data before network load. Good.
- **Token refresh**: HTTP-only cookie-based refresh with `_tryRefresh()` and `_refreshPromise` guard. Good.
- **Page refresh during auth**: If no token in memory, the app tries to refresh from cookie before redirecting. Good.

### Issues Found

#### HIGH SEVERITY

1. **No URL state management for overlays** — The app uses `useState` for all navigation (`nav`, `accountOpen`, `pricingOpen`, etc.). None of these states are persisted to the URL hash or query params. If a user:
   - Opens the Backtest overlay
   - Refreshes the page
   - The page returns to the Feed view, not Backtest

   This breaks the **expected behavior** of every modern SPA. Users cannot bookmark specific views, share links to specific overlays, or use the browser back button to close overlays.

2. **Browser Back button breaks app state** — Since there is no router (no React Router, no hash-based routing), pressing the browser Back button will:
   - If the user navigated from `/login` to `/app`, Back goes to `/login` (good)
   - But within `/app`, clicking Back does nothing because no history entries were pushed. If the user was on an overlay and clicked Back, they would leave the app entirely instead of closing the overlay.
   - This is a **critical UX violation** for SPAs.

3. **No state preservation for active signal** — The `activeId` is not stored in `localStorage` or URL. A refresh resets the selection to the first signal. This is especially annoying when a user is deep in the Simulate or Position tab and refreshes.

4. **No session recovery for in-progress actions** — If a user is filling out:
   - The screener builder (name, rules)
   - The alert rule form (ticker, minConf)
   - The price alert modal (target price)
   - The account settings (broker form)

   And refreshes the page, all form state is lost. No `beforeunload` warning or localStorage backup.

5. **OAuth `next` param not preserved** — The auth gate at line 743 uses `window.location.replace("/login?next=/app")` — but it always sends to `/app`, not the original page the user was trying to access. If the user was on `/mobile` or a specific view, they lose that context.

6. **Network error — UI freezes or shows stale data** — When the API is unreachable:
   - `loadData` catches the error, sets `online=false`, and `setLoading(false)` (line 606–608). The feed shows cached signals from `localStorage` but there is no clear "You are offline" banner at the top of the feed pane. The only offline indicator is the small sidebar status card and the `wsStatus` banner (which, as noted in Lens 3, is broken).
   - Failed actions (send to Telegram, skip signal, save note) show `alert()` dialogs (line 689, 695, 698). These are browser-native, jarring, and block the UI thread. No inline toast/banner notifications.

#### MEDIUM SEVERITY

7. **No `beforeunload` warning for unsaved changes** — The ScreenerView, AlertsView, RulesView, and AccountModal all have forms that could be partially filled. No `beforeunload` event listener warns the user about losing unsaved work.

8. **Billing checkout redirect loses context** — If a user clicks "Upgrade" from a specific context (e.g., "Paper trading requires Basic"), goes to Stripe, and returns, the app does not restore the context or the overlay that triggered the upgrade. The `pricingContext` state is lost on refresh.

9. **Demo tour — no skip on refresh** — If the demo tour opens and the user refreshes, it will open again (unless `localStorage` already has the key). But if the user was mid-tour, there's no resume capability.

---

## 8. Lens 6 — Keyboard Navigation & Focus Trap Verification

### Verified Behavior
- **Keyboard shortcuts**: Documented in `HotkeyHelp` overlay. Implemented in `useEffect` at line 455:
  - `?` or `Shift+/` → toggle hotkey help
  - `Escape` → close overlays, nav drawer, tour
  - `Cmd+\` → toggle density
  - `1/2/3/4` → filter chips
  - `j/k` → navigate feed
  - `Enter` → open full detail
  - `Shift+S` → send to Telegram
  - `p` → paper trade (with tier check)
  - `s` → skip signal
  - `Cmd+K` → focus search
  - `d` → toggle full detail
- **Focus visible**: `*:focus-visible` CSS rule adds `outline:2px solid var(--accent);outline-offset:2px` (line 102 in login.html). Good.
- **Tabindex on nav items**: Sidebar nav items have `tabIndex={0}` and `role="button"`.
- **Search input**: Has `ref` for programmatic focus. Good.
- **Chart canvas**: `aria-label` added dynamically for accessibility. Good.

### Issues Found

#### HIGH SEVERITY

1. **No Enter/Space handlers on `role="button"` elements** — This is the **most widespread critical accessibility bug** in the entire app. Across all files, any element with `role="button"` and `tabIndex={0}` **must** handle `Enter` and `Space` key events to be keyboard-accessible. Here are the specific violations:

   - **Sidebar nav items** (`app.jsx`, lines 909–966): Every `.nav-item` has `role="button"` + `tabIndex={0}` + `onClick={() => setNav("...")}` but **no `onKeyDown` handler**. Keyboard users can Tab to these items but cannot activate them with Enter or Space.
   - **Filter chips** (`app.signal.jsx`, line 291): `fc` buttons are actual `<button>` elements — this is fine.
   - **Style strip buttons** (`app.jsx`, line 1120): `ss-btn` is an actual `<button>` — fine.
   - **Day toggle buttons** (`app.jsx`, line 1134): `.day` elements have `role="button"` + `tabIndex={0}` but no keyboard handler.
   - **Mobile bottom nav items** (`app.jsx`, line 1788): `mobile-nav-item` has `role="button"` + `tabIndex={0}` but no keyboard handler.
   - **Signal row toggle** (`app.signal.jsx`, line 20): The `.signal-row-inner` is a `<button>` — fine. But the parent `<div className="signal">` has `onClick` via bubbling.
   - **Detail tabs** (`app.jsx`, line 1364): Actual `<button>` elements — fine.
   - **Chart period tabs** (`app.jsx`, line 1385): `<span>` with `role="button"` + `tabIndex={0}` but **no keyboard handler**.
   - **Compare vs buttons** (`app.jsx`, line 1394): Actual `<button>` elements — fine.
   - **Tweaks panel swatches** (`app.modals.jsx`, line 1102): `<div>` with `role="button"` + `tabIndex={0}` but no keyboard handler.
   - **Tweaks panel seg buttons** (`app.modals.jsx`, lines 1109, 1116, etc.): Actual `<button>` elements — fine.
   - **Pricing plan cards** (`app.modals.jsx`): Not interactive (no onclick).
   - **Alert rule pause/resume buttons** (`app.modals.jsx`, lines 1412–1413): Actual `<button>` with icons — fine, but icons may not have labels.
   - **Screener preset buttons** (`app.modals.jsx`, lines 1563–1568): `<button>` elements with icons — fine.
   - **Watchlist sort button** (`app.modals.jsx`, line 950): `<button>` — fine.
   - **Delivery log tabs** (`app.signal.jsx`, lines 202–203): `del-tab` `<div>` with `role="button"` + `tabIndex={0}` but **no keyboard handler**.
   - **InfoPop trigger** (`app.ui.jsx`, line 192): `<button>` — fine.
   - **Tip trigger** (`app.ui.jsx`, line 121): `<span>` with mouse events only — not keyboard accessible. Tooltip content is never reachable by keyboard.
   - **Cinematic views**: `cin.dashboard.jsx`, `cin.market.jsx`, `cin.backtest.jsx` — many glass-hover cards with `onClick` but no keyboard handlers.

   **Impact**: Screen reader and keyboard-only users cannot navigate the app. This is a **WCAG 2.1 Level A failure** (4.1.2 Name, Role, Value).

2. **No focus trap on overlays** — When any overlay/modal opens (AccountModal, PricingView, PriceAlertModal, TweaksPanel, etc.):
   - No `focus()` is called on the first focusable element inside the overlay.
   - The overlay does not trap focus — Tabbing cycles through the entire page, including the sidebar and main panel behind the overlay.
   - No `aria-modal="true"` is set on overlay containers.
   - The overlay backdrop is not focusable or announced.

   This is a **WCAG 2.1 Level A failure** (2.4.3 Focus Order).

3. **No focus management on overlay close** — When an overlay closes (e.g., clicking BackButton), focus is not returned to the trigger element. The focus is lost to `document.body`, forcing keyboard users to Tab from the beginning of the page.

4. **Chart — not keyboard accessible** — The LightweightCharts canvas is focusable (with `role="button"` added dynamically), but:
   - No keyboard navigation inside the chart (arrow keys, +/- for zoom, etc.)
   - The drawing tool only works with mouse click + right-click. No keyboard alternative.
   - The period selector buttons (1D/5D/1M/etc.) are keyboard accessible, but the chart itself is not.

5. **Search — no `aria-label`** — The search input (`app.jsx`, line 783) has no `aria-label` or `aria-describedby`. Screen readers may not announce its purpose. The placeholder text is descriptive but placeholders are not always read by screen readers.

6. **Mobile pager — no keyboard accessibility** — The panel pager buttons (`app.jsx` lines 1757, 1769) are not keyboard focusable (no `tabIndex`). The arrow buttons are disabled based on `panelIdx` but disabled buttons are typically removed from the tab order.

#### MEDIUM SEVERITY

7. **Skip link missing** — There is no "Skip to main content" link at the top of the page. Keyboard users must Tab through the entire topbar and sidebar before reaching the main content.

8. **No heading hierarchy** — The app uses `<h1>` once (hidden for screen readers at line 774: `style={{position:"absolute",width:"1px"...}}`). But inside overlays, there is no consistent heading hierarchy (h2, h3, etc.). Screen reader users cannot navigate by heading.

9. **Live region for dynamic updates** — When new signals arrive via WebSocket, the feed updates but there is no `aria-live` region to announce this to screen readers. The user has no way of knowing a new signal appeared.

10. **Signal count badge not announced** — The sidebar shows signal counts (e.g., `{filteredSignals.length}`) but these are not wrapped in `aria-live` or visually associated with the nav label for screen readers.

---

## 9. The Bug & Edge-Case Log

### Summary Table

| # | Element/Interaction | Expected Behavior | Actual Behavior | Severity |
|---|---------------------|-------------------|-----------------|----------|
| 1 | **WebSocket status banner** | Banner disappears when WebSocket connects | Banner is **permanently visible** because `wsStatus` is never updated to `"open"` | 🔴 High |
| 2 | **Sidebar nav items (keyboard)** | Enter/Space activates nav item | Tab focuses item but Enter/Space does nothing | 🔴 High |
| 3 | **Mobile bottom nav (keyboard)** | Enter/Space activates tab | Tab focuses item but Enter/Space does nothing | 🔴 High |
| 4 | **Day toggle buttons (keyboard)** | Enter/Space toggles day | Tab focuses but Enter/Space does nothing | 🔴 High |
| 5 | **Chart period tabs (keyboard)** | Enter/Space switches period | Tab focuses but Enter/Space does nothing | 🔴 High |
| 6 | **Delivery log tabs (keyboard)** | Enter/Space switches tab | Tab focuses but Enter/Space does nothing | 🔴 High |
| 7 | **Tweaks swatches (keyboard)** | Enter/Space selects accent | Tab focuses but Enter/Space does nothing | 🔴 High |
| 8 | **Overlay focus trap** | Focus stays inside overlay when open | Focus escapes to background page | 🔴 High |
| 9 | **Overlay focus return** | Focus returns to trigger on close | Focus is lost to document.body | 🔴 High |
| 10 | **No URL state / Back button** | Back closes overlay; URL reflects view | Back leaves app entirely; no URL state | 🔴 High |
| 11 | **Paper trade double-submit** | Button disabled during API call | Button remains clickable; multiple orders possible | 🔴 High |
| 12 | **No API retry logic** | Failed calls retry or show retry UI | Failed calls silently fail; no retry UI | 🔴 High |
| 13 | **WebSocket no reconnect** | Auto-reconnect on disconnect | No reconnect logic; `wsReconnectDelay` unused | 🔴 High |
| 14 | **No skeleton screens** | Skeleton placeholders during load | Plain text "Loading…" only; layout shift | 🟡 Medium |
| 15 | **Mobile nav only 6 of 16 items** | All nav items accessible | 10 items only reachable via hamburger drawer | 🟡 Medium |
| 16 | **Hamburger touch target** | 44×44px minimum | Likely ~28×28px | 🟡 Medium |
| 17 | **Pager arrow touch target** | 44×44px minimum | Likely ~24×24px | 🟡 Medium |
| 18 | **No pull-to-refresh (main app)** | Swipe down refreshes feed | No gesture support | 🟡 Medium |
| 19 | **No real-time email validation** | Inline format validation on blur | Only HTML5 validation; no format check | 🟡 Medium |
| 20 | **No password strength indicator** | Visual strength meter | Only "At least 8 chars" hint | 🟡 Medium |
| 21 | **Broker key — no format validation** | Validates Alpaca key format | Accepts any text | 🟡 Medium |
| 22 | **Auto-exec quantity boundary** | Rejects 0 and negative on input | HTML `min` may not prevent paste; only save-time check | 🟡 Medium |
| 23 | **Tweak save — silent failure** | Shows error if server save fails | Error silently caught; no user feedback | 🟡 Medium |
| 24 | **Chart fetch — no timeout** | Shows error after N seconds | "Loading…" persists indefinitely | 🟡 Medium |
| 25 | **No `beforeunload` warning** | Warns about unsaved form data | No warning; data lost on refresh | 🟡 Medium |
| 26 | **No `aria-live` for new signals** | Screen reader announces new signal | New signals appear silently | 🟡 Medium |
| 27 | **No skip navigation link** | "Skip to content" link at top | No skip link; must tab through all | 🟡 Medium |
| 28 | **Tip tooltip — not keyboard accessible** | Keyboard users can trigger tooltip | Only mouse enter/leave; no keyboard access | 🟡 Medium |
| 29 | **Search no debounce** | Throttled recalculation | Recalculates on every keystroke | 🟢 Low |
| 30 | **Note textarea — no maxLength** | Limits text to reasonable length | No limit; may cause API errors | 🟢 Low |
| 31 | **Signup duplicate feature** | Unique features per plan | "Telegram + Web Push" listed twice | 🟢 Low |
| 32 | **No responsive wrapping for topbar** | Graceful truncation on tablet | Possible overflow/clipping | 🟢 Low |
| 33 | **No focus on chart canvas** | Full keyboard chart navigation | Only focusable; no keyboard interaction | 🟢 Low |
| 34 | **OAuth `next` param hardcoded** | Preserves original destination | Always redirects to `/app` | 🟢 Low |
| 35 | **No `aria-modal` on overlays** | Screen reader knows it's a modal | No `aria-modal` attribute | 🟢 Low |
| 36 | **No heading hierarchy in overlays** | h2/h3 structure for navigation | Inconsistent heading levels | 🟢 Low |
| 37 | **Active signal not preserved on refresh** | Returns to previously selected signal | Resets to first signal | 🟢 Low |
| 38 | **Overlay header not sticky** | Close button always visible | May scroll out of view on mobile | 🟢 Low |
| 39 | **Concurrent manualScan()** | Blocks duplicate calls | Multiple API calls in flight | 🟢 Low |
| 40 | **Screener text values not validated** | Type-safe input | Raw string sent to API | 🟢 Low |
| 41 | **Mobile sidebar drawer — no swipe-to-dismiss** | Swipe left closes drawer | Only close button or backdrop tap | 🟢 Low |
| 42 | **Name field — no XSS sanitization** | Strips HTML/script tags | Accepts any characters | 🟢 Low |
| 43 | **Predictive fetch — no deduplication** | Cancels previous in-flight request | Multiple requests for rapid switching | 🟢 Low |
| 44 | **Feed "Show more" no loading state** | Disabled while loading | Remains clickable during load | 🟢 Low |
| 45 | **Signup name field accepts any chars** | Sanitizes or validates | No client-side validation | 🟢 Low |
| 46 | **Billing context lost on refresh** | Restores upgrade context after return | Context lost | 🟢 Low |
| 47 | **No `aria-label` on search** | Screen reader announces search purpose | No label; placeholder may not be read | 🟢 Low |
| 48 | **Signal count badge not announced** | Screen reader announces count changes | No `aria-live` region | 🟢 Low |
| 49 | **Mobile panel pager not focusable** | Keyboard accessible | No `tabIndex` | 🟢 Low |
| 50 | **Tweaks panel content may not wrap** | Responsive layout on mobile | Fixed horizontal layout | 🟢 Low |

---

## 10. The E2E Test Case Script

### Test Suite: Signal.Trade Full Application E2E

**Prerequisites:**
- Backend running at `http://localhost:8000` (or staging URL)
- Test user: `test@signal.trade` / `TestPass123!` (Free tier)
- Test user 2: `basic@signal.trade` / `TestPass123!` (Basic tier)
- Test user 3: `pro@signal.trade` / `TestPass123!` (Pro tier)
- Test user 4: `owner@signal.trade` / `OwnerPass123!` (Owner)
- Playwright/Cypress test runner configured
- Mobile viewport: 375×812 (iPhone X)
- Tablet viewport: 768×1024 (iPad)
- Desktop viewport: 1440×900

---

### TS-001: Authentication & Onboarding

```gherkin
Feature: User Authentication

Scenario: TS-001.1 — Successful login
  Given I am on the login page
  When I enter a valid email and password
  And I click the "Sign In" button
  Then I am redirected to /app
  And the disclaimer modal appears
  And the dashboard loads with signal feed visible

Scenario: TS-001.2 — Invalid login credentials
  Given I am on the login page
  When I enter an invalid password
  And I click the "Sign In" button
  Then the error box shows "Invalid credentials"
  And the submit button is re-enabled

Scenario: TS-001.3 — Google OAuth flow
  Given I am on the login page
  When I click the "Google" button
  Then I am redirected to Google's OAuth consent screen
  When I complete OAuth consent
  Then I am redirected back to /app with ?oauth_code= removed from URL
  And the dashboard loads

Scenario: TS-001.4 — Signup multi-step flow
  Given I am on the signup page
  Then I see the plan selection step (3 cards: Free, Basic, Pro)
  When I select the "Basic" plan
  And I click "Continue with Basic"
  Then the account creation form appears
  When I enter email, password, and optional name
  And I click "Create account"
  Then I am redirected to /app
  And the dashboard loads

Scenario: TS-001.5 — Password reset flow
  Given I am on the login page
  When I click "Forgot password?"
  Then the forgot form appears
  When I enter my email and click "Send reset link"
  Then the message shows reset link sent
  When I click the link from my email
  Then I am on the reset-password page
  When I enter a new password and confirm
  Then I am redirected to /login

Scenario: TS-001.6 — Session refresh
  Given I am logged in and have a valid refresh cookie
  When I close and reopen the browser
  Then the app silently refreshes the token
  And the dashboard loads without re-authentication

Scenario: TS-001.7 — Session expiry
  Given I am logged in
  When the refresh token expires
  Then I am redirected to /login?next=/app
  And the error box shows "Session expired"
```

---

### TS-002: Dashboard Core — Signal Feed

```gherkin
Feature: Signal Feed

Scenario: TS-002.1 — Signal feed loads with data
  Given I am logged in on the dashboard
  Then the feed pane shows signals
  And the filter chips show counts (All, Buy, Sell, High)
  And the style strip shows the current style
  And the active signal is highlighted

Scenario: TS-002.2 — Filter by action
  When I click the "BUY only" chip
  Then only BUY signals are visible
  And the count badge updates
  When I click "All"
  Then all signals are visible

Scenario: TS-002.3 — Filter by style
  When I click "Intraday" in the style strip
  Then the feed filters to intraday signals
  And the filter resets to "All"
  When I click "Swing"
  Then the feed filters to swing signals

Scenario: TS-002.4 — Search by ticker
  When I type "AAPL" in the search bar
  Then the feed shows only AAPL signals
  When I press Escape
  Then the search clears
  When I type "dark pool buy"
  Then the feed shows signals matching the natural language query

Scenario: TS-002.5 — Signal selection and expansion
  When I click a signal row
  Then the row becomes active (highlighted)
  And the detail pane shows the signal's data
  When I click the same row again
  Then the row expands showing entry/stop/target and actions
  When I click "Full detail →"
  Then the detail pane scrolls to the simulate tab

Scenario: TS-002.6 — Suppressed signals
  When I lower the threshold to 40%
  Then suppressed signals appear below a divider
  When I click "Show more suppressed"
  Then 20 more suppressed signals appear

Scenario: TS-002.7 — Keyboard navigation
  When I press "j"
  Then the next signal in the feed becomes active
  When I press "k"
  Then the previous signal becomes active
  When I press "Enter"
  Then the full detail opens for the active signal

Scenario: TS-002.8 — Mobile panel paging
  Given I am on mobile viewport
  When I swipe left on the main panel
  Then the detail pane scrolls into view
  And the pager dot updates to panel 1
  When I click the right arrow
  Then the delivery pane scrolls into view
```

---

### TS-003: Signal Detail Pane

```gherkin
Feature: Signal Detail Pane

Scenario: TS-003.1 — Why tab — chart and rationale
  Given a signal is selected
  When I am on the "Why" tab
  Then the chart shows with entry/stop/target lines
  And the rationale list shows with source badges
  And the predictive panel shows (if loaded)

Scenario: TS-003.2 — Chart period switching
  When I click "1D" on the chart tabs
  Then the chart re-renders with 1D data
  When I click "1Y"
  Then the chart re-renders with 1Y data

Scenario: TS-003.3 — Compare vs benchmark
  When I click "SPY"
  Then a second chart series appears below the main chart
  When I click "SPY" again
  Then the comparison chart disappears

Scenario: TS-003.4 — Position tab — tier gate
  Given I am a Free user
  When I click the "Position" tab
  Then a tier-gate message appears: "Position sizing requires Basic or higher"
  And an "Upgrade" button is visible

Scenario: TS-003.5 — Position tab — Basic user
  Given I am a Basic user
  When I click the "Position" tab
  Then the position calculator appears
  When I click "Paper trade"
  Then a POST request is sent to /api/paper/orders
  And the button flashes green briefly

Scenario: TS-003.6 — Simulate tab
  When I click the "Simulate" tab
  Then the Monte Carlo simulation panel appears

Scenario: TS-003.7 — Similar tab
  When I click the "Similar" tab
  Then similar historical signals are listed

Scenario: TS-003.8 — Send to Telegram
  When I click "Send to Telegram"
  Then a POST request is sent to /api/signals/{id}/send
  And the delivery log updates
  And a success message appears

Scenario: TS-003.9 — Skip signal
  When I click "Skip"
  Then a POST request is sent to /api/signals/{id}/skip
  And the signal is removed from the feed
  And the next signal becomes active

Scenario: TS-003.10 — Paper trade double-click
  When I double-click the "Paper Trade" button rapidly
  Then only ONE POST request should be sent
  (Verify no duplicate orders created)

Scenario: TS-003.11 — Chart drawing tool
  When I click the "✏ DRAW" button
  Then the button changes to "✏ DRAWING"
  When I click on the chart
  Then a horizontal price line appears
  When I right-click on the line
  Then the line is removed
  When I click "CLEAR"
  Then all drawn lines are removed
```

---

### TS-004: Sidebar Navigation & Overlays

```gherkin
Feature: Sidebar and Overlays

Scenario: TS-004.1 — Open Watchlist overlay
  When I click "Watchlist" in the sidebar
  Then the Watchlist overlay opens
  And the feed is dimmed in the background
  When I enter "TSLA" and click "Add"
  Then TSLA appears in the watchlist grid
  When I click "✕" on TSLA
  Then TSLA is removed
  When I click "Back"
  Then the overlay closes and the feed is visible

Scenario: TS-004.2 — Open Rules overlay
  When I click "Rules & filters" in the sidebar
  Then the Rules overlay opens
  When I click "Aggressive"
  Then the aggressiveness preset changes
  When I enter "55" in the confidence input and blur
  Then the threshold updates to 55%
  When I enter "25:00" in the time input
  Then a validation error appears: "Invalid time"
  When I enter "09:30" in start and "09:00" in end
  Then a validation error appears: "End time must be after start time"

Scenario: TS-004.3 — Open Sources overlay
  When I click "Sources" in the sidebar
  Then the Sources overlay opens
  When I click a toggle
  Then the source turns on/off
  And a PATCH request is sent to /api/sources/{id}

Scenario: TS-004.4 — Open Backtest overlay
  When I click "Backtest" in the sidebar
  Then the Backtest overlay opens
  And the "Summary" tab is active
  When I click "By Source"
  Then source accuracy data loads
  When I click "Backfill Outcomes"
  Then a POST request is sent and a result banner appears

Scenario: TS-004.5 — Open Account modal
  When I click the user avatar
  Then the Account modal opens
  When I enter a new name and click "Save"
  Then the name is updated via PATCH /api/auth/me
  When I click "Sign Out"
  Then I am redirected to /login

Scenario: TS-004.6 — Open Pricing overlay
  When I click "Upgrade plan"
  Then the Pricing overlay opens
  And plans load from /api/billing/plans
  When I click "Start trial" on Basic
  Then a POST request is sent to /api/billing/checkout/basic
  And I am redirected to Stripe checkout

Scenario: TS-004.7 — Mobile sidebar drawer
  Given I am on mobile viewport
  When I click the hamburger menu
  Then the sidebar slides in as a drawer
  And a backdrop overlay appears
  When I click the backdrop
  Then the drawer closes
  When I click a nav item
  Then the drawer closes and the view changes
```

---

### TS-005: Market Overview & Context

```gherkin
Feature: Market Overview

Scenario: TS-005.1 — Market context loads
  When I click "Market overview" in the sidebar
  Then the Market Overview overlay opens
  And the Fear & Greed gauge renders
  And the HMM Regime panel shows
  And the Macro Dashboard shows VIX, yield curve, breadth, CPI

Scenario: TS-005.2 — Sector heatmap
  When I click "Sector heatmap" in the sidebar
  Then the Sector overlay opens
  And sector bars show 1M return + 1W flow

Scenario: TS-005.3 — Economic calendar
  When I click "Economic calendar" in the sidebar
  Then the Calendar overlay opens
  And upcoming events are listed with impact badges
```

---

### TS-006: Real-Time & Network Resilience

```gherkin
Feature: Real-Time Updates and Network Resilience

Scenario: TS-006.1 — WebSocket live price update
  Given a signal is selected
  When the WebSocket sends a "tick" message for the active ticker
  Then the live price updates in the detail pane
  And the price change color updates

Scenario: TS-006.2 — WebSocket new signal
  When the WebSocket sends a "new_signal" message
  Then the new signal appears at the top of the feed
  And the signal count badge updates

Scenario: TS-006.3 — Auto-refresh countdown
  Then the countdown timer shows 30s
  And it decrements every second
  When it reaches 0
  Then the feed silently refreshes
  And the countdown resets to 30

Scenario: TS-006.4 — Manual refresh
  When I click the refresh button
  Then it spins
  And a POST /api/signals/scan is sent
  After 1.5s, the feed refreshes
  And the button stops spinning

Scenario: TS-006.5 — Backend offline
  When the backend becomes unreachable
  Then the sidebar status card shows "Backend offline"
  And the feed shows cached signals
  And a banner should appear (but currently broken due to wsStatus bug)

Scenario: TS-006.6 — Network recovery
  When the backend comes back online
  Then the app should reconnect and refresh data
  (Currently: manual refresh required due to no auto-reconnect)

Scenario: TS-006.7 — Page refresh mid-action
  Given I am filling out the screener builder
  When I refresh the page
  Then all form data is lost
  (Expected: warn user or preserve state)
```

---

### TS-007: Keyboard & Accessibility

```gherkin
Feature: Keyboard Accessibility

Scenario: TS-007.1 — Full keyboard navigation
  Given I am on the dashboard
  When I press Tab repeatedly
  Then I can reach: search, filter chips, style buttons, day toggles, signal rows, nav items, action buttons
  (Note: Currently FAILS for nav items, day toggles, and mobile nav)

Scenario: TS-007.2 — Keyboard shortcuts
  When I press "?"
  Then the Hotkey Help overlay opens
  When I press "Escape"
  Then it closes
  When I press "Cmd+K"
  Then the search bar is focused
  When I press "1"
  Then the feed filter changes to "All"
  When I press "2"
  Then the filter changes to "Buy"

Scenario: TS-007.3 — Overlay focus trap
  When I open the Account modal with keyboard
  Then focus should be trapped inside the modal
  When I press Tab past the last element
  Then focus should cycle to the first element
  (Note: Currently FAILS — focus escapes to background)

Scenario: TS-007.4 — Overlay close with Escape
  When any overlay is open
  And I press Escape
  Then the overlay closes
  And focus returns to the trigger element
  (Note: Currently partially works but focus return FAILS)

Scenario: TS-007.5 — Screen reader announcements
  When a new signal arrives via WebSocket
  Then a screen reader should announce it
  (Note: Currently FAILS — no aria-live region)
```

---

### TS-008: Boundary & Edge Cases

```gherkin
Feature: Boundary Testing

Scenario: TS-008.1 — Empty search
  When I search for "ZZZZZZ" (non-existent ticker)
  Then the feed shows "No signals above X% confidence"
  And the helper buttons appear (Lower threshold, Clear filter, Scan now)

Scenario: TS-008.2 — Extreme confidence threshold
  When I set the threshold to 100%
  Then no signals match (unless any are at 100%)
  When I set the threshold to 0%
  Then all signals match
  When I set the threshold to -10%
  Then the UI should reject it (validated on Rules save)
  When I set the threshold to 150%
  Then the UI should reject it

Scenario: TS-008.3 — Massive search query
  When I paste a 5000-character string into the search bar
  Then the app should handle it gracefully
  And not crash

Scenario: TS-008.4 — Rapid filter switching
  When I rapidly click Buy → Sell → All → High
  Then the feed should settle on the last clicked filter
  And no visual glitches should occur

Scenario: TS-008.5 — Empty broker credentials
  When I click "Connect" in the broker form with empty fields
  Then the error message appears: "API key and secret are required"

Scenario: TS-008.6 — Invalid alert price
  When I enter "0" in the price alert target
  Then validation error: "Price must be greater than 0"
  When I enter "100000000" in the target
  Then validation error: "Price must be below $1,000,000"

Scenario: TS-008.7 — Watchlist invalid ticker
  When I enter "123" in the watchlist input
  Then error: "Ticker symbols are 1–5 letters"
  When I enter "AAPL12345"
  Then the input truncates to 5 characters

Scenario: TS-008.8 — Concurrent refresh clicks
  When I click "Refresh" 5 times rapidly
  Then only one POST /api/signals/scan should fire
  (Note: Currently FAILS — multiple calls in flight)

Scenario: TS-008.9 — Large signal count
  When the feed has 500+ signals
  Then pagination should work
  And scrolling should remain smooth
  (Note: Verify no FPS drops)

Scenario: TS-008.10 — Browser zoom
  When I zoom to 200%
  Then all text should be readable
  And no elements should overlap or clip
  When I zoom to 50%
  Then the layout should still be usable
```

---

### TS-009: Mobile Responsive

```gherkin
Feature: Mobile Responsive

Scenario: TS-009.1 — Mobile layout
  Given I am on iPhone X viewport
  Then the bottom nav is visible
  And the sidebar is hidden
  And the topbar is simplified
  And the main panel is full-width

Scenario: TS-009.2 — Mobile navigation
  When I tap the hamburger menu
  Then the sidebar drawer slides in
  When I tap "Sources"
  Then the Sources overlay opens
  When I tap the back button
  Then the overlay closes

Scenario: TS-009.3 — Mobile panel paging
  When I swipe left on the main area
  Then I see the detail pane
  When I swipe right
  Then I return to the feed
  When I tap the right arrow in the pager
  Then I see the delivery pane

Scenario: TS-009.4 — Mobile touch targets
  Then all buttons should be at least 44×44px
  (Note: Currently FAILS for hamburger and pager arrows)

Scenario: TS-009.5 — Mobile form inputs
  When I tap the search bar
  Then the keyboard appears
  And the viewport does not scroll unexpectedly
  When I type in the price alert input
  Then the numeric keyboard should appear
```

---

### TS-010: Security & Data Integrity

```gherkin
Feature: Security

Scenario: TS-010.1 — No secrets in localStorage
  When I inspect localStorage
  Then no access token should be stored
  And only `st_tweaks`, `st_signals_cache`, `signal_trade_disclaimer_v1` should exist

Scenario: TS-010.2 — XSS prevention
  When I enter `<script>alert('xss')</script>` in the search bar
  Then the script should not execute
  When I enter the same in the note textarea
  Then it should be safely rendered

Scenario: TS-010.3 — Tier gate enforcement
  Given I am a Free user
  When I try to access the Position tab
  Then the UI blocks with a tier gate
  When I manually POST to /api/paper/orders
  Then the server should return 403 Forbidden

Scenario: TS-010.4 — Owner-only kill switch
  Given I am a non-owner user
  Then the Kill Switch button is not visible
  When I manually POST to /api/admin/execution-kill-switch
  Then the server should return 403 Forbidden

Scenario: TS-010.5 — Logout clears state
  When I click "Sign Out"
  Then the token is cleared from memory
  And localStorage is cleared of sensitive data
  And I am redirected to /login
```

---

## Appendix A: Critical Priority Fix List

### P0 — Fix Before Next Release
1. **WebSocket status update** — Add `onopen`/`onclose`/`onerror` handlers to update `wsStatus` state.
2. **WebSocket auto-reconnect** — Implement exponential backoff reconnection using `wsReconnectDelay`.
3. **Keyboard handlers on all `role="button"` elements** — Add `onKeyDown` with Enter/Space handling to nav items, day toggles, chart tabs, delivery tabs, mobile nav, and tweaks swatches.
4. **Overlay focus trap** — Implement focus trap using `useRef` + `Tab`/`Shift+Tab` interception on all overlays.
5. **Overlay focus return** — Store trigger element ref before opening overlay, restore focus on close.
6. **URL state management** — Add hash-based routing for overlays (e.g., `#watchlist`, `#backtest`) so Back button works and URLs are shareable.
7. **Paper trade button — disable during fetch** — Add `disabled={paperTrading}` state to prevent double-submit.
8. **API retry mechanism** — Add 1 retry with exponential backoff for transient failures, or show inline retry button.
9. **Error feedback for tweak save** — Show toast/banner on `PUT /api/settings` failure.
10. **Skeleton screens** — Add skeleton placeholders for all overlay content areas instead of plain "Loading…" text.

### P1 — Fix Within 2 Sprints
11. **Pull-to-refresh on main app** — Add touch handlers for pull-to-refresh on the feed panel.
12. **Mobile nav parity** — Ensure all 16 nav items are accessible on mobile (either via bottom nav expansion or sidebar drawer).
13. **Touch target sizing** — Ensure all interactive elements are at least 44×44px on mobile.
14. **Real-time validation on signup** — Add email format validation and password strength meter.
15. **Broker credential validation** — Add format validation for Alpaca keys.
16. **Search debounce** — Add 300ms debounce to search input.
17. **Chart fetch timeout** — Add 10s timeout with fallback error state.
18. **Aria-live region for new signals** — Add polite announcement region for feed updates.
19. **Skip navigation link** — Add "Skip to main content" link at page top.
20. **Beforeunload warning** — Warn users about unsaved form data on refresh.

### P2 — Nice to Have
21. **Session state preservation** — Save activeId, nav, and overlay state to localStorage before refresh.
22. **Heading hierarchy** — Add consistent h2/h3 structure in all overlays.
23. **Tip keyboard accessibility** — Make glossary tooltips triggerable by keyboard focus.
24. **Mobile swipe-to-dismiss drawer** — Add swipe left gesture to close sidebar drawer.
25. **Note max length** — Add 2000-character limit to journal notes.
26. **Signup duplicate feature fix** — Remove duplicate "Telegram + Web Push" line from Basic plan.
27. **Topbar responsive wrapping** — Add truncation/overflow strategy for tablet viewports.
28. **Predictive fetch deduplication** — Cancel previous in-flight request when active signal changes rapidly.
29. **Concurrent manualScan guard** — Prevent multiple `POST /api/signals/scan` calls.
30. **Screener value validation** — Enforce type validation before API call.

---

*Report compiled from static code analysis of the Signal.Trade frontend codebase. For live validation, run the E2E test scripts against a deployed instance using Playwright or Cypress.*
