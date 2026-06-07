/* global React */
const { useState, useEffect } = React;

/* ── Auth helpers ─────────────────────────────────────────────────────────── */
// Access token in module memory only — the HTTP-only refresh cookie persists sessions.
let _accessToken = null;
const getToken = () => _accessToken;

async function apiPost(path, body, token) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(path, { method: "POST", headers, body: JSON.stringify(body) });
  const data = await res.json();
  return { ok: res.ok, data };
}

/* ── Signal cards for hero phone mockup ──────────────────────────────────── */
const W_SIGNALS = [
  { tk: "NVDA", action: "BUY",  style: "POSITION", conf: 82, head: "Double-confirmed: above EMA200 + weekly SMA13 uptrend ×8/10", entry: 1245, stop: 1188, target: 1385 },
  { tk: "TSLA", action: "SELL", style: "SWING",    conf: 71, head: "Death cross + dark pool distribution $12M net sell",            entry: 165,  stop: 172,  target: 152  },
  { tk: "AMD",  action: "BUY",  style: "SWING",    conf: 68, head: "RSI 28 oversold + weekly RSI 37 — double-confirmed",            entry: 162,  stop: 154,  target: 178  },
];

const W_FEATURES = [
  { ico: "📊", t: "13F Institutional Flow",      d: "Tracks Berkshire, Pershing, Tiger and 12 more — fires when they buy or add. Quarterly + Form 4 insider clusters." },
  { ico: "🐋", t: "Unusual Options Sweeps",      d: "Volume >5× OI, OTM spikes, IV term structure across 3 expiries. GEX computed daily." },
  { ico: "📰", t: "Polygon.io News + Analyst",   d: "Polygon primary news (<5min latency), Finnhub real-time, analyst upgrades, price target changes." },
  { ico: "📄", t: "SEC Form 4 Insider Trades",   d: "Cluster buys flagged within 30 days. EDGAR XBRL parsing for 15 top hedge funds." },
  { ico: "📈", t: "65+ Technical Signal Blocks", d: "RSI weekly/daily, MACD, EMA(200), Bollinger, ADX, Ichimoku, Supertrend, Hurst, FDI, Z-score and more." },
  { ico: "🌐", t: "Macro Regime (HMM)",          d: "2-state Gaussian HMM on VIX, SPY return, yield curve, realised vol — replaces static VIX thresholds." },
  { ico: "🔮", t: "Bayesian Calibration",        d: "Platt scaling blends raw score toward empirical win rate. Max confidence capped at 84% to prevent overconfidence." },
  { ico: "🦈", t: "Dark Pool Block Trades",      d: "Live FINRA TRF prints via Massive WebSocket. Lee-Ready tick rule infers direction. Block threshold: $250K+." },
  { ico: "🏭", t: "Supply Chain Alt Data",       d: "Baltic Dry Index, Brent crude momentum, Cass Freight — sector impact map for 20+ watchlist tickers." },
  { ico: "📱", t: "Telegram + Discord + Push",   d: "Per-subscriber fan-out, Discord webhooks, Web Push (VAPID). Plain-English rationale + full disclaimer." },
  { ico: "⚖️", t: "Polygon Financial Ratios",   d: "FCF yield, gross/net margin, debt/equity from SEC filings via Polygon vX. Dividend Aristocrat streak bonus." },
  { ico: "🔗", t: "Related Company Peer Check", d: "Polygon co-occurrence peers (NVDA→AMD/INTC/TSM) confirm BUY signals. More precise than GICS sector groups." },
];

const W_FAQS = [
  { q: "Is this financial advice?", a: "No. Every signal is published with a full disclaimer — for educational and informational purposes only. Past performance does not predict future results. Trade at your own risk; consult a licensed advisor." },
  { q: "How fresh is the data?", a: "Polygon.io is the primary OHLCV + news source (<5min news latency). Live dark pool prints via Massive WebSocket. Scan cycle runs every 60 seconds. SEC 13F filings cached 6 hours. Free-tier rate limits respected; circuit breaker protects against yfinance 429 bans." },
  { q: "Can I cancel anytime?", a: "Yes. Stripe Billing Portal — one click, no questions. Service runs through end of billing period." },
  { q: "Why Telegram, not email?", a: "Telegram has a free, robust Bot API. Delivers in < 2 seconds. Same instant push, lighter infrastructure, no SMTP headaches." },
  { q: "Do I need to babysit the alerts?", a: "No. Set delivery window (e.g. 09:30–16:00 ET) + active days. Confidence threshold suppresses noise. Quiet hours block off-hours sends." },
  { q: "What about backtesting?", a: "Win rate, Sharpe, max drawdown, Calmar by horizon (1d/3d/7d/14d). Per-ticker track record + auditable simulation with slippage." },
];

/* ── Logo ────────────────────────────────────────────────────────────────── */
function Logo({ size = 13 }) {
  return (
    <span className="brand">
      <span className="dot"/>
      <span style={{ fontSize: size }}>SIGNAL.TRADE</span>
      <span className="v" style={{ fontSize: size - 2 }}>v5.2</span>
    </span>
  );
}

/* ── Nav ─────────────────────────────────────────────────────────────────── */
function Nav({ go, page }) {
  return (
    <nav className="nav">
      <a onClick={() => go("home")} style={{ cursor:"pointer", textDecoration:"none" }} role="button" tabIndex={0}><Logo/></a>
      <div className="nav-links">
        <a onClick={() => go("home")}      className={page==="home"?"on":""} role="button" tabIndex={0}>Features</a>
        <a onClick={() => go("track")}     className={page==="track"?"on":""} role="button" tabIndex={0}>Track record</a>
        <a onClick={() => go("docs")}      className={page==="docs"?"on":""} style={{ cursor:"pointer" }} role="button" tabIndex={0}>Docs</a>
        <a onClick={() => go("telegram")}  className={page==="telegram"?"on":""} role="button" tabIndex={0}>Telegram</a>
        <a style={{ cursor:"pointer" }} onClick={() => { go("home"); setTimeout(() => document.getElementById("pricing")?.scrollIntoView({ behavior:"smooth" }), 80); }} role="button" tabIndex={0}>Pricing</a>
      </div>
      <div className="nav-cta">
        <span className="nav-status">ENGINE LIVE · 164 TICKERS · 60s CYCLE</span>
        <button className="btn ghost" onClick={() => window.location.href = "/login"}>Sign in</button>
        <button className="btn primary" onClick={() => window.location.href = "/signup"}>Start free</button>
      </div>
    </nav>
  );
}

/* ── Hero phone mockup ───────────────────────────────────────────────────── */
function HeroPhone() {
  return (
    <div className="phone">
      <div className="phone-content">
        <div style={{ display:"flex", alignItems:"center", gap:8, padding:"0 4px 8px", borderBottom:"1px solid var(--line)" }}>
          <div style={{ width:6, height:6, borderRadius:"50%", background:"var(--up)" }}/>
          <span style={{ fontFamily:"var(--font-mono)", fontSize:10, color:"var(--text-faint)", letterSpacing:"0.1em" }}>SIGNAL.TRADE</span>
          <span style={{ marginLeft:"auto", fontFamily:"var(--font-mono)", fontSize:9, color:"var(--text-faint)" }}>12:54</span>
        </div>
        {W_SIGNALS.map((s, i) => (
          <div key={i} className={`phone-card signal ${s.action.toLowerCase()}`}>
            <div className="pc-row">
              <span className={`pc-verb ${s.action.toLowerCase()}`}>{s.action}</span>
              <span className="pc-tk">{s.tk}</span>
              <span className="pc-conf">{s.conf}%</span>
            </div>
            <div className="pc-head">{s.head}</div>
            <div className="pc-trade">
              <span className="t">${s.entry}</span>
              <span className="t s">↓${s.stop}</span>
              <span className="t p">↑${s.target}</span>
            </div>
          </div>
        ))}
        <div style={{ marginTop:"auto", textAlign:"center", fontFamily:"var(--font-mono)", fontSize:9, color:"var(--text-faint)", padding:6 }}>
          Sent via Telegram · 09:31 ET
        </div>
      </div>
    </div>
  );
}

/* ── Hero ─────────────────────────────────────────────────────────────────── */
function Hero({ go, stats }) {
  const wr  = stats?.overall?.win_rate;
  const n   = stats?.total_signals;
  return (
    <section className="hero">
      <div className="hero-grid">
        <div>
          <div className="eyebrow"><span className="pulse"/>NEW · POLYGON.IO PRIMARY · MACRO HMM · DARK POOL RECONSTRUCTION</div>
          <h1 className="headline">Your personal <em>quant desk</em>, beamed straight to Telegram.</h1>
          <p className="sub">65+ independent signal blocks, institutional 13F flow, dark pool block prints, options sweeps, and a Markov macro regime model — all fused into one confidence score, capped at 84% to prevent overconfidence.</p>
          <div className="hero-actions">
            <button className="btn primary lg" onClick={() => go("signup")}>Start 7-day free trial</button>
            <button className="btn lg" onClick={() => go("track")}>See live track record →</button>
          </div>
          <div className="hero-meta">
            <span><strong className="b">{n ?? "—"}</strong> signals tracked</span>
            <span><strong className="b">{wr != null ? wr.toFixed(1)+"%" : "—"}</strong> win rate</span>
            <span><strong className="b">65+</strong> signal blocks</span>
            <span><strong className="b">164</strong> watchlist tickers</span>
          </div>
        </div>
        <div className="hero-phone"><HeroPhone/></div>
      </div>
    </section>
  );
}

/* ── Stat strip ──────────────────────────────────────────────────────────── */
function StatStrip({ stats }) {
  const o   = stats?.overall;
  const wr  = o?.win_rate;
  const ar  = o?.avg_return;
  const sh  = o?.sharpe;
  const n   = stats?.total_signals;
  const items = [
    { n: wr  != null ? wr.toFixed(1)+"%" : "—", l:"Win rate",        s:"Resolved signals" },
    { n: sh  != null ? sh.toFixed(2) : "—",      l:"Sharpe ratio",    s:"Annualized" },
    { n: ar  != null ? (ar >= 0 ? "+" : "")+ar.toFixed(2)+"%" : "—", l:"Avg return / signal", s:"Per resolved signal" },
    { n: n   ?? "—",                             l:"Signals tracked", s:"Since launch" },
  ];
  return (
    <div className="stat-strip">
      {items.map((s, i) => (
        <div key={i}>
          <div className="stat-num">{s.n}</div>
          <div className="stat-lbl">{s.l}</div>
          <div className="stat-sub">{s.s}</div>
        </div>
      ))}
    </div>
  );
}

/* ── Features ────────────────────────────────────────────────────────────── */
function Sources() {
  return (
    <section className="section" id="features">
      <div className="section-head">
        <div className="section-eyebrow">02 · The Signal Stack</div>
        <h2 className="section-title">12 data sources, fused into one confidence score.</h2>
        <p className="section-sub">Polygon.io as primary OHLCV + news + financials (free tier). Every signal shows exactly which sources agreed and why.</p>
      </div>
      <div className="sources-grid">
        {W_FEATURES.map((f, i) => (
          <div key={i} className="source-card">
            <div className="sc-top">
              <div className="sc-ico">{f.ico}</div>
              <div>
                <div className="sc-name">{f.t}</div>
                <div className="sc-tag">FREE TIER</div>
              </div>
            </div>
            <div className="sc-desc">{f.d}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ── Flow ─────────────────────────────────────────────────────────────────── */
function Flow() {
  const steps = [
    { n:"01", t:"Sources scan",     d:"Polygon.io (primary OHLCV + indicators + news + financials), Massive WebSocket dark pool, EDGAR 13F + Form 4, Finnhub, FRED, CBOE, Alpaca IEX — all polled or streamed." },
    { n:"02", t:"Score fusion",     d:"65+ signal blocks across 11 scoring families, capped per group, HMM regime-gated, Bayesian-calibrated. Max confidence 84%." },
    { n:"03", t:"Filters apply",    d:"Confidence threshold, R:R floor, ex-dividend blackout, earnings cooldown, low-ATR regime switch, your delivery window + style filter." },
    { n:"04", t:"You get pinged",   d:"Telegram / Discord / Web Push with plain-English rationale, entry/stop/target, R:R, and full legal disclaimer." },
  ];
  return (
    <section className="section" id="how">
      <div className="section-head">
        <div className="section-eyebrow">03 · From signal to phone</div>
        <h2 className="section-title">A four-stage pipeline. Differential scan skips stable tickers every cycle.</h2>
      </div>
      <div className="flow">
        {steps.map((s, i) => (
          <div key={i} className="flow-step">
            <div className="flow-num">{s.n}</div>
            <h4>{s.t}</h4>
            <p>{s.d}</p>
            {i < steps.length - 1 && (
              <svg aria-hidden="true" className="arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6"/></svg>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

/* ── Pricing ─────────────────────────────────────────────────────────────── */
function Pricing({ go }) {
  const tiers = [
    {
      name: "Free", amt: "$0", per: "forever",
      desc: "Read-only access. See signals after they're sent. No notifications.",
      cta: "Get started", btn: "btn",
      feats: [["✓","View live signal feed",true],["✓","Track record + history",true],["✓","Sector heatmap",true],["✗","Telegram delivery",false],["✗","Backtesting",false],["✗","Paper trading",false]]
    },
    {
      name: "Basic", amt: "$29", per: "/month",
      desc: "The full alerting experience. Telegram + Discord + Web Push delivery, backtest engine, Excel export.",
      cta: "Start 7-day trial", btn: "btn primary", featured: true,
      feats: [["✓","Everything in Free",true],["✓","Telegram + Discord + Web Push alerts",true],["✓","Configure days + delivery window",true],["✓","Backtesting engine (1d/3d/7d/14d)",true],["✓","Watchlist + price alerts + Excel export",true],["✗","Paper trading + correlation",false]]
    },
    {
      name: "Pro", amt: "$79", per: "/month",
      desc: "Full institutional quant desk. Paper trading, volatility targeting, correlation matrix, weekly digest.",
      cta: "Start 7-day trial", btn: "btn",
      feats: [["✓","Everything in Basic",true],["✓","Alpaca paper trading",true],["✓","Signal correlation matrix",true],["✓","Bayesian + predictive confidence intervals",true],["✓","Portfolio volatility targeting (15% target)",true],["✓","Simulated backtest with slippage + weekly digest",true]]
    },
  ];
  return (
    <section className="section" id="pricing">
      <div className="section-head">
        <div className="section-eyebrow">04 · Pricing</div>
        <h2 className="section-title">Pick a tier. Cancel anytime in one click.</h2>
        <p className="section-sub">Stripe Billing Portal — no support ticket required. 7-day free trial on Basic ($29/mo) and Pro ($79/mo). Comparable to Unusual Whales, a fraction of Trade Ideas.</p>
      </div>
      <div className="pricing-grid">
        {tiers.map((t, i) => (
          <div key={i} className={`price-card ${t.featured?"featured":""}`}>
            {t.featured && <div className="featured-tag">MOST POPULAR</div>}
            <div className="price-tier">{t.name}</div>
            <div className="price-amt">{t.amt}<small>{t.per}</small></div>
            <div className="price-desc">{t.desc}</div>
            <button className={t.btn} onClick={() => go(t.name === "Free" ? "signup" : "signup")}>{t.cta}</button>
            <div className="feat-list">
              {t.feats.map(([m,lbl,on], j) => (
                <div key={j} className={`feat-item ${on?"":"dim"}`}>
                  <span className={on?"ck":"x"}>{m}</span>
                  <span>{lbl}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ── Track record (home snippet) ─────────────────────────────────────────── */
function TrackRecord({ go, stats }) {
  const o = stats?.overall;
  const tickers = stats?.top_tickers || [];
  const byMonth = stats?.by_month || [];
  const fmtRet = v => v == null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;
  const maxWr = Math.max(...byMonth.map(m => m.win_rate || 0), 1);
  return (
    <section className="section" id="track">
      <div className="section-head">
        <div className="section-eyebrow">05 · Public Track Record</div>
        <h2 className="section-title">No cherry-picking. Every signal, every outcome, on a public page.</h2>
        <p className="section-sub">Updated automatically as 1d/3d/7d/14d horizons resolve. Aggregate-only — no PII.</p>
      </div>
      <div className="tr-grid">
        <div>
          <div className="tr-big">
            <div className="tr-num">{o?.win_rate != null ? o.win_rate.toFixed(1)+"%" : "—"}</div>
            <div className="tr-lbl">Overall win rate · {stats?.total_signals ?? "—"} resolved signals</div>
          </div>
          {byMonth.length > 0 && (
            <div style={{ marginTop:24 }}>
              <div className="mono" style={{ fontSize:11, color:"var(--text-faint)", letterSpacing:"0.1em", textTransform:"uppercase", marginBottom:12 }}>Last {byMonth.length} months · win rate %</div>
              <div className="tr-bars">
                {byMonth.map((m, i) => {
                  const up = (m.avg_return || 0) >= 0;
                  return <div key={i} className={`tr-bar ${up?"":"dn"}`} style={{ height:`${((m.win_rate||0)/maxWr)*90}%` }} title={`${m.month}: ${(m.win_rate||0).toFixed(1)}%`}/>;
                })}
              </div>
              <div className="tr-bar-lbls">
                {byMonth.map((m, i) => <span key={i}>{m.month?.slice(5) || "—"}</span>)}
              </div>
            </div>
          )}
        </div>
        <div>
          <div className="mono" style={{ fontSize:11, color:"var(--text-faint)", letterSpacing:"0.1em", textTransform:"uppercase", marginBottom:14 }}>Top tickers by signal count</div>
          <div className="tr-list">
            {tickers.slice(0, 7).map((t, i) => (
              <div key={i} className="tr-row">
                <span className="tk">{t.ticker}</span>
                <span style={{ color:"var(--text-dim)" }}>{t.win_rate != null ? t.win_rate.toFixed(0)+"% wr" : "—"}</span>
                <span className={`pct ${(t.avg_return||0) >= 0 ? "up":"down"}`}>{fmtRet(t.avg_return)}</span>
              </div>
            ))}
            {tickers.length === 0 && <div style={{ padding:"20px 14px", color:"var(--text-faint)", fontSize:12 }}>No resolved signals yet — data accumulates after 1d.</div>}
          </div>
          <button className="btn" style={{ marginTop:18, width:"100%" }} onClick={() => go("track")}>See full track record →</button>
        </div>
      </div>
    </section>
  );
}

/* ── FAQ ─────────────────────────────────────────────────────────────────── */
function FAQ() {
  return (
    <section className="section" id="faq">
      <div className="section-head">
        <div className="section-eyebrow">06 · Questions</div>
        <h2 className="section-title">Things people ask before signing up.</h2>
      </div>
      <div className="faq">
        {W_FAQS.map((f, i) => (
          <div key={i} className="faq-item">
            <div className="faq-q">{f.q}</div>
            <div className="faq-a">{f.a}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ── CTA band ────────────────────────────────────────────────────────────── */
function CTA({ go }) {
  return (
    <div className="cta-band">
      <h2>Ready to stop missing setups?</h2>
      <p>7-day free trial. No credit card. Cancel in one click.</p>
      <div style={{ display:"flex", gap:12, justifyContent:"center" }}>
        <button className="btn primary lg" onClick={() => go("signup")}>Start free trial</button>
        <button className="btn lg" onClick={() => go("docs")}>Read the docs</button>
      </div>
    </div>
  );
}

/* ── Footer ──────────────────────────────────────────────────────────────── */
function Footer({ go }) {
  return (
    <>
      <footer className="footer">
        <div>
          <Logo size={14}/>
          <p style={{ marginTop:14 }}>A personal quant desk for retail traders. Built solo, run lean, priced fairly. Educational tool — not a registered investment advisor.</p>
        </div>
        <div className="foot-col">
          <h5>Product</h5>
          <a onClick={() => go("home")} role="button" tabIndex={0}>Features</a>
          <a onClick={() => go("home")} role="button" tabIndex={0}>Pricing</a>
          <a onClick={() => go("track")} role="button" tabIndex={0}>Track record</a>
          <a onClick={() => go("changelog")} role="button" tabIndex={0}>Changelog</a>
        </div>
        <div className="foot-col">
          <h5>Resources</h5>
          <a onClick={() => go("docs")} role="button" tabIndex={0}>Documentation</a>
          <a onClick={() => go("telegram")} role="button" tabIndex={0}>Telegram setup</a>
          <a onClick={() => go("status")} role="button" tabIndex={0}>Status page</a>
        </div>
        <div className="foot-col">
          <h5>Legal</h5>
          <a onClick={() => go("terms")} role="button" tabIndex={0}>Terms of service</a>
          <a onClick={() => go("privacy")} role="button" tabIndex={0}>Privacy policy</a>
          <a onClick={() => go("risk")} role="button" tabIndex={0}>Risk disclosure</a>
          <a href="/app">Open dashboard</a>
        </div>
      </footer>
      <div className="disclaimer-bar">
        <strong>NOT FINANCIAL ADVICE</strong> — SIGNAL.TRADE is an educational signal aggregator. Past performance does not predict future results. Trade at your own risk. Consult a licensed advisor.
      </div>
    </>
  );
}

/* ── Auth page ───────────────────────────────────────────────────────────── */
function AuthPage({ kind, go }) {
  const isSignup = kind === "signup";
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [name,     setName]     = useState("");
  const [error,    setError]    = useState("");
  const [loading,  setLoading]  = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    const path = isSignup ? "/api/auth/register" : "/api/auth/login";
    const body = isSignup ? { email, password, full_name: name } : { email, password };
    const { ok, data } = await apiPost(path, body).catch(() => ({ ok: false, data: { detail: "Network error." } }));
    if (!ok) { setError(data.detail || "Something went wrong."); setLoading(false); return; }
    const tok = data.access_token; // in-memory only; refresh cookie persists the session
    // If paid plan selected (set via query param), go to checkout
    const plan = new URLSearchParams(window.location.search).get("plan");
    if (isSignup && plan && plan !== "free") {
      const { ok: cok, data: cd } = await apiPost(`/api/billing/checkout/${plan}`, {}, tok).catch(() => ({ ok: false, data: {} }));
      if (cok && cd.checkout_url) { window.location.href = cd.checkout_url; return; }
    }
    window.location.href = "/app";
  };

  // Already logged in? Silently refresh from the HTTP-only cookie.
  useEffect(() => {
    fetch("/api/auth/refresh-cookie", { method: "POST", credentials: "include" })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.access_token) window.location.replace("/app"); })
      .catch(() => {});
  }, []);

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div style={{ textAlign:"center", marginBottom:24 }}><Logo size={14}/></div>
        <h2>{isSignup ? "Start your free trial" : "Welcome back"}</h2>
        <p>{isSignup ? "7 days. No credit card. Cancel anytime." : "Sign in to your SIGNAL.TRADE account."}</p>
        {error && <div className="auth-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="auth-fields">
            {isSignup && (
              <div className="auth-field">
                <label>Full name</label>
                <input type="text" placeholder="Your name (optional)" value={name} onChange={e => setName(e.target.value)} autoComplete="name"/>
              </div>
            )}
            <div className="auth-field">
              <label>Email</label>
              <input type="email" placeholder="you@email.com" value={email} onChange={e => setEmail(e.target.value)} required autoComplete="email"/>
            </div>
            <div className="auth-field">
              <label>Password</label>
              <input type="password" placeholder={isSignup ? "At least 8 characters" : "Your password"} value={password} onChange={e => setPassword(e.target.value)} required autoComplete={isSignup ? "new-password" : "current-password"}/>
            </div>
          </div>
          <button type="submit" className="btn primary" style={{ width:"100%", justifyContent:"center", padding:"12px 0", fontSize:14 }} disabled={loading}>
            {loading ? "Please wait…" : isSignup ? "Create account" : "Sign in"}
          </button>
        </form>
        <div className="auth-divider"><span>or</span></div>
        <div className="auth-foot">
          {isSignup ? "Already have an account? " : "New here? "}
          <a className="auth-link" onClick={() => go(isSignup ? "login" : "signup")} role="button" tabIndex={0}>{isSignup ? "Sign in" : "Start free"}</a>
        </div>
        {isSignup && (
          <div className="auth-tos">
            By continuing you agree to our <a onClick={() => go("terms")} role="button" tabIndex={0}>Terms</a>, <a onClick={() => go("privacy")} role="button" tabIndex={0}>Privacy</a> and <a onClick={() => go("risk")} role="button" tabIndex={0}>Risk Disclosure</a>.<br/>
            ⚠️ Not financial advice · Educational tool only.
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Sub-page shell ──────────────────────────────────────────────────────── */
function PageShell({ children, eyebrow, title, sub }) {
  return (
    <div className="page-shell">
      <div className="section-head" style={{ paddingTop:80, paddingBottom:30, paddingLeft:40 }}>
        <div className="section-eyebrow">{eyebrow}</div>
        <h1 className="section-title">{title}</h1>
        {sub && <p className="section-sub">{sub}</p>}
      </div>
      <div className="page-body">{children}</div>
    </div>
  );
}

/* ── Track record full page ──────────────────────────────────────────────── */
function TrackPage({ stats }) {
  const o = stats?.overall;
  const fmtRet = v => v == null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;
  const tickers = stats?.top_tickers || [];
  const byMonth = stats?.by_month || [];
  return (
    <PageShell eyebrow="03 · TRACK RECORD" title="Every signal. Audited." sub="Public ledger of every signal fired since launch — wins, losses, and unresolved positions.">
      <div className="stat-strip" style={{ marginBottom:40 }}>
        <div><div className="stat-num">{stats?.total_signals ?? "—"}</div><div className="stat-lbl">Total signals</div></div>
        <div><div className="stat-num">{o?.win_rate != null ? o.win_rate.toFixed(1)+"%" : "—"}</div><div className="stat-lbl">Win rate</div><div className="stat-sub">Resolved positions only</div></div>
        <div><div className="stat-num">{o?.avg_return != null ? fmtRet(o.avg_return) : "—"}</div><div className="stat-lbl">Avg return / signal</div></div>
        <div><div className="stat-num">{o?.sharpe != null ? o.sharpe.toFixed(2) : "—"}</div><div className="stat-lbl">Sharpe ratio</div><div className="stat-sub">Annualized</div></div>
      </div>
      <div className="track-table">
        <h3>Monthly performance</h3>
        <table>
          <thead><tr><th>Month</th><th>Signals</th><th>Win %</th><th>Avg Return</th><th>Sharpe</th></tr></thead>
          <tbody>
            {byMonth.map((m, i) => (
              <tr key={i}><td><strong>{m.month}</strong></td><td>{m.n}</td><td>{m.win_rate != null ? m.win_rate.toFixed(1)+"%" : "—"}</td><td className={(m.avg_return||0) >= 0 ? "up":"down"}>{fmtRet(m.avg_return)}</td><td>{m.sharpe != null ? m.sharpe.toFixed(2) : "—"}</td></tr>
            ))}
            {byMonth.length === 0 && <tr><td colSpan="5" style={{ textAlign:"center", color:"var(--text-faint)", padding:"20px 0" }}>No resolved signals yet — outcomes accumulate after 1 day.</td></tr>}
          </tbody>
        </table>
      </div>
      <div className="track-table">
        <h3>Top tickers by signal count</h3>
        <table>
          <thead><tr><th>Ticker</th><th>Signals</th><th>Win rate</th><th>Avg return</th></tr></thead>
          <tbody>
            {tickers.map((t, i) => (
              <tr key={i}><td><strong>{t.ticker}</strong></td><td>{t.n}</td><td>{t.win_rate != null ? t.win_rate.toFixed(1)+"%" : "—"}</td><td className={(t.avg_return||0) >= 0 ? "up":"down"}>{fmtRet(t.avg_return)}</td></tr>
            ))}
            {tickers.length === 0 && <tr><td colSpan="4" style={{ textAlign:"center", color:"var(--text-faint)", padding:"20px 0" }}>No data yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </PageShell>
  );
}

/* ── Docs page ───────────────────────────────────────────────────────────── */
function DocsPage() {
  const sections = [
    { t:"Getting started", items:["Installation","First signal","Telegram bot setup","Confidence threshold","Owner account"] },
    { t:"Data sources",    items:["Polygon.io (primary OHLCV + news + financials + indicators)","yfinance (fallback)","Massive WebSocket (dark pool)","Finnhub news","SEC EDGAR 13F + Form 4","CBOE P/C ratio","FRED macro","Alpaca IEX WebSocket"] },
    { t:"Signal engine",   items:["65+ signal blocks across 11 scoring families","Options sweep + GEX detection","13F institutional flow + Form 4 clusters","Macro HMM regime (2-state Gaussian)","Platt scaling calibration (84% max confidence)","Dark pool block trade reconstruction","Supply chain alt data (BDI, Brent, Cass Freight)","Ex-dividend & earnings blackouts","Low-ATR regime switch (mean-reversion only)"] },
    { t:"Backtesting",     items:["Win rate analytics","By-horizon breakdown","Outcome backfill","Auditable simulation","Track record"] },
    { t:"Subscription",    items:["Free / Basic / Pro","Stripe checkout","stripe_setup.py","Billing portal","Webhook setup"] },
    { t:"Legal",           items:["Risk disclosure","Terms of service","Privacy policy","Not financial advice"] },
  ];
  return (
    <PageShell eyebrow="04 · DOCUMENTATION" title="Everything, in plain English." sub="How the engine works, how to configure it, how to read the output.">
      <div className="docs-grid">
        {sections.map((s, i) => (
          <div key={i} className="docs-card">
            <h4>{s.t}</h4>
            <ul>{s.items.map((it, j) => <li key={j}>{it}</li>)}</ul>
          </div>
        ))}
      </div>
      <div className="docs-code">
        <div className="docs-code-head">Example · GET /api/signals</div>
        <pre>{`curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  http://localhost:8000/api/signals

[
  {
    "id": 42,
    "ticker": "NVDA",
    "action": "BUY",
    "confidence": 82.4,
    "price": 875.32,
    "entry": 875.00,
    "stop": 848.00,
    "target": 932.00,
    "rr": "2.1",
    "headline": "Breakout above 200-DMA + call sweep detected",
    "sources": ["13F", "Options", "Technical", "News"],
    "ts": "2026-04-26T09:31:22"
  }
]`}</pre>
      </div>
    </PageShell>
  );
}

/* ── Telegram page ───────────────────────────────────────────────────────── */
function TelegramPage() {
  const steps = [
    { n:"01", t:"Create an account at /signup", d:"Sign up for Basic or Pro — free tier does not include Telegram delivery." },
    { n:"02", t:"Get your link code in Account Settings", d:"Go to /app → Account Settings → Telegram section. Copy your unique link code." },
    { n:"03", t:"Open the Signal.Trade bot on Telegram", d:"Search for your bot (configured via TELEGRAM_BOT_TOKEN). Click Start." },
    { n:"04", t:"Send /start YOUR_CODE", d:'Type /start followed by your code (e.g. "/start A1B2C3D4"). The bot confirms immediately.' },
  ];
  return (
    <PageShell eyebrow="05 · TELEGRAM SETUP" title="Connect in 60 seconds." sub="Bot delivery beats email. Free, instant, and works worldwide.">
      <div className="telegram-grid">
        <div>
          {steps.map((s, i) => (
            <div key={i} className="tg-step">
              <span className="n">{s.n}</span>
              <div>
                <h4>{s.t}</h4>
                <p>{s.d}</p>
              </div>
            </div>
          ))}
        </div>
        <div className="tg-qr">
          <div className="qr-box">
            <div style={{ background:"var(--bg-2)", height:"100%", borderRadius:4, display:"flex", alignItems:"center", justifyContent:"center", color:"var(--text-faint)", fontFamily:"var(--font-mono)", fontSize:12 }}>
              QR code after<br/>bot is deployed
            </div>
          </div>
          <div className="tg-handle">@signal_trade_bot</div>
          <div style={{ fontSize:12, color:"var(--text-dim)", lineHeight:1.6 }}>
            Requires Basic or Pro plan · Also supports Discord webhooks + Web Push (VAPID) · Full legal disclaimer included
          </div>
        </div>
      </div>
    </PageShell>
  );
}

/* ── Legal pages ─────────────────────────────────────────────────────────── */
function LegalPage({ kind, go }) {
  const docs = {
    terms:   { title:"Terms of Service",  eyebrow:"06 · LEGAL · TERMS",   date:"Last updated · May 2026",
      sections:[["1. Service","SIGNAL.TRADE is a SaaS signal aggregator that surfaces algorithmic recommendations derived from public data for educational and informational purposes."],["2. Not financial advice","We are not a registered investment advisor, broker-dealer, or financial planner. Nothing here constitutes a solicitation, offer, or recommendation to buy or sell any security."],["3. Subscription","Plans renew monthly until cancelled. Cancel anytime via Stripe Billing Portal. No partial refunds."],["4. No refunds for trading losses","Subscription fees cover platform access only. We expressly do not provide refunds, credits, or chargebacks on the basis of trading losses, missed opportunities, or signal inaccuracy. By subscribing you waive any right to dispute charges on those grounds."],["5. Acceptable use","You may not resell, scrape at scale, or redistribute signals to third parties without a commercial license."],["6. Liability","Total liability limited to fees paid in the trailing 12 months. We are not liable for trading losses."],["7. Governing law","Delaware, USA. Disputes resolved by binding arbitration under AAA rules."]]},
    privacy: { title:"Privacy Policy",    eyebrow:"06 · LEGAL · PRIVACY", date:"Last updated · April 2026",
      sections:[["What we collect","Email, hashed password (bcrypt), Stripe customer ID, Telegram chat ID, signal preferences, usage analytics."],["What we don't collect","Brokerage credentials, trade history outside the app, location, or third-party tracker data. We do not sell your data."],["Storage","Encrypted at rest. Backups retained 30 days."],["Third parties","Stripe (billing), Telegram (delivery), SMTP provider (transactional email). No analytics/ads networks."],["Your rights","Export, correct, or delete your data anytime via Account → Privacy. GDPR / CCPA compliant."]]},
    risk:    { title:"Risk Disclosure",   eyebrow:"06 · LEGAL · RISK",    date:"Last updated · April 2026",
      sections:[["Trading involves substantial risk","You can lose some or all of your invested capital. Past performance is not indicative of future results."],["Our signals are probabilistic","A 70% confidence signal will lose 30% of the time. Even high-conviction signals fail."],["Backtested results have limitations","Historical simulations do not account for slippage, gaps, halts, or adverse selection."],["You are responsible","We do not execute trades. You decide whether and how to act on any signal."],["Use position sizing","Risk no more than 1–2% of capital per trade. Never risk capital you cannot afford to lose."]]},
  };
  const d = docs[kind];
  return (
    <PageShell eyebrow={d.eyebrow} title={d.title} sub={d.date}>
      <div className="legal-doc">
        {d.sections.map((s, i) => (
          <section key={i}>
            <h3>{s[0]}</h3>
            <p>{s[1]}</p>
          </section>
        ))}
        <div style={{ marginTop:32, padding:"16px 20px", background:"rgba(245,158,11,0.1)", border:"1px solid rgba(245,158,11,0.3)", borderRadius:8, fontSize:13, color:"var(--warn)", lineHeight:1.6 }}>
          ⚠️ <strong>NOT FINANCIAL ADVICE</strong> — SIGNAL.TRADE provides educational signals only. Consult a licensed financial professional before making any trading decision.
        </div>
      </div>
    </PageShell>
  );
}

/* ── Status page ─────────────────────────────────────────────────────────── */
function StatusPage() {
  const services = [
    { n:"Signal engine (65+ blocks)",    s:"operational",  up:99.97, last:"60s cycle" },
    { n:"Polygon.io OHLCV + indicators", s:"operational",  up:99.95, last:"primary source" },
    { n:"Polygon.io news (free tier)",   s:"operational",  up:99.92, last:"<5min latency" },
    { n:"yfinance (fallback)",           s:"operational",  up:99.80, last:"circuit breaker active on 429" },
    { n:"Finnhub news feed",             s:"operational",  up:99.99, last:"2s ago" },
    { n:"Massive WebSocket (dark pool)", s:"operational",  up:99.90, last:"live stream" },
    { n:"SEC EDGAR 13F + Form 4",        s:"operational",  up:100,   last:"6h cache" },
    { n:"CBOE put/call ratio",           s:"operational",  up:99.80, last:"1d cache" },
    { n:"FRED macro data",               s:"operational",  up:99.99, last:"daily" },
    { n:"Alpaca IEX WebSocket",          s:"operational",  up:99.97, last:"live" },
    { n:"Telegram / Discord delivery",   s:"operational",  up:99.99, last:"9s ago" },
    { n:"Stripe billing",                s:"operational",  up:100,   last:"—" },
  ];
  const color = s => s === "operational" ? "var(--up)" : s === "degraded" ? "var(--warn)" : "var(--down)";
  const allGreen = services.every(s => s.s === "operational");
  return (
    <PageShell eyebrow="07 · STATUS" title={allGreen ? "All systems operational." : "Service degraded."} sub="Live status of the signal engine and every upstream data source.">
      <div style={{ padding:"20px 24px", background:`color-mix(in oklch, var(--up) 10%, var(--bg-2))`, border:"1px solid color-mix(in oklch, var(--up) 30%, transparent)", borderRadius:12, marginBottom:30, display:"flex", alignItems:"center", gap:14 }}>
        <span style={{ width:10, height:10, borderRadius:"50%", background:"var(--up)", boxShadow:"0 0 0 4px color-mix(in oklch, var(--up) 30%, transparent)" }}/>
        <div>
          <div style={{ fontWeight:600, color:"#fff" }}>All systems operational</div>
          <div style={{ fontSize:13, color:"var(--text-dim)", marginTop:2 }}>Signal engine running · 60s scan cycle</div>
        </div>
      </div>
      <div className="status-list">
        {services.map((s, i) => (
          <div key={i} className="status-row">
            <span className="dot" style={{ background:color(s.s) }}/>
            <span className="n">{s.n}</span>
            <span className="m" style={{ color:color(s.s) }}>{s.s.toUpperCase()}</span>
            <span className="u">{s.up}% uptime · 90d</span>
            <span className="l">{s.last}</span>
          </div>
        ))}
      </div>
    </PageShell>
  );
}

/* ── Changelog ───────────────────────────────────────────────────────────── */
function ChangelogPage() {
  const items = [
    { v:"v5.2", d:"May 2026", t:"Polygon.io Free-Tier Full Exploitation", b:["Pre-computed RSI/MACD/SMA/EMA(200) blended 60/40 with pandas","Weekly RSI + SMA multi-timeframe confirmation (72% win rate)","3-year annual revenue acceleration 'Earnings Torpedo' (+8pts)","Dividend Aristocrat bonus (Achiever/Aristocrat/King tiers)","Accurate TTM dividend yield from Polygon (fixes 40% yfinance None rate)","Macro news sentiment (SPY/QQQ) BUY cap when VIX >20","Market holiday −5pp haircut before 3-day weekends","Polygon related-company peer confirmation replaces GICS sector","Market status from Polygon (NYSE open/close authoritative)"] },
    { v:"v5.1", d:"May 2026", t:"Macro HMM + Dark Pool + Supply Chain", b:["2-state Gaussian HMM (Baum-Welch) replaces static VIX thresholds","Dark pool block trade reconstruction with Lee-Ready direction inference","Supply chain alt data: Baltic Dry, Brent crude, Cass Freight","Float from Polygon reference data (fixes 30% yfinance None rate)","WebSocket heartbeat watchdog (15s timeout, exponential backoff)","Differential scan: skips stable tickers, saves ~80/154 API calls/cycle"] },
    { v:"v5.0", d:"May 2026", t:"Performance + Infrastructure overhaul", b:["Semaphore(5) parallel signal generation — 5× scan speedup","yfinance global circuit breaker (15min backoff on 429)","Polygon OHLCV shared cache (15-min TTL, no redundant downloads)","News batch fetch: 154 tickers → 3 paginated Polygon calls (~5s vs 35s)","Indicator cache warming on startup (1 ticker/23s over 60min)","SQLite → PostgreSQL migration path (DATABASE_URL env var)","5-min analytics cache for /backtest + /correlation endpoints"] },
    { v:"v4.9", d:"May 2026", t:"Signals + Delivery + UI", b:["Monte Carlo Web Worker (500-path simulation off main thread)","Signal history Excel export (openpyxl, styled, action color-coded)","Confidence trend sparkline added to every expanded signal card","Discord webhook delivery (PATCH /api/auth/integrations)","Outbound webhook with HMAC-SHA256 signature","Price alert evaluator wired into scan cycle","DOM feed pagination (30 initial, Show More button)"] },
    { v:"v4.0", d:"May 2026", t:"Signal quality + calibration overhaul", b:["Platt scaling calibration — max confidence ceiling 84%","Style classification overhaul (position/swing/intraday)","Loss-aware duplicate signal cooldown (48h/72h streak penalty)","Recency-weighted per-ticker win rates (60-day halflife decay)","Bear + high-VIX hard BUY gate; macro contradiction confidence cap","Post-earnings cooldown (days 0–2 hard HOLD, days 3–4 ×0.80)","Cointegration pairs trading (14 pre-defined pairs)","Macro regime 4-stage sector rotation model"] },
    { v:"v3.4", d:"Apr 2026", t:"Complete subscription stack", b:["JWT auth (register, login, refresh, me, change-password)","Stripe Checkout + Billing Portal + Webhooks","Free / Basic / Pro tiers with 7-day free trial","Multi-user Telegram fan-out via signal_deliveries table","Admin panel: setup health, MRR, user list, webhook registration"] },
    { v:"v3.3", d:"Apr 2026", t:"13F + enhanced options sweeps", b:["SEC EDGAR XBRL parsing for 15 top hedge funds","Multi-expiry options sweep detection (vol >5× OI)","OTM call/put volume spike analysis","IV term structure spike detection"] },
    { v:"v3.2", d:"Mar 2026", t:"Mobile app + design canvas", b:["Mobile PWA at /mobile with tab bar navigation","iOS 26 Liquid Glass device frames","Figma-style design canvas at /design with 9 artboards","Marketing landing page + signup/login flow"] },
    { v:"v3.1", d:"Feb 2026", t:"Backtest + predictive intervals", b:["Win rate, Sharpe, max drawdown, Calmar by hold period","Outcome backfill from yfinance historical prices","Bayesian predictive confidence intervals","Signal correlation matrix"] },
  ];
  return (
    <PageShell eyebrow="08 · CHANGELOG" title="What's new in SIGNAL.TRADE" sub="Engine releases & feature rollouts.">
      <div className="changelog">
        {items.map((it, i) => (
          <div key={i} className="cl-row">
            <div className="cl-meta">
              <div className="v">{it.v}</div>
              <div className="d">{it.d}</div>
            </div>
            <div className="cl-body">
              <h3>{it.t}</h3>
              <ul>{it.b.map((b, j) => <li key={j}>{b}</li>)}</ul>
            </div>
          </div>
        ))}
      </div>
    </PageShell>
  );
}

/* ── 404 ─────────────────────────────────────────────────────────────────── */
function NotFoundPage({ go }) {
  return (
    <div className="page-404">
      <div style={{ textAlign:"center", padding:"100px 24px" }}>
        <div style={{ fontFamily:"var(--font-mono)", fontSize:11, letterSpacing:"0.2em", color:"var(--accent)", marginBottom:14 }}>404 · SIGNAL NOT FOUND</div>
        <div style={{ fontSize:80, fontWeight:800, color:"#fff", lineHeight:1, letterSpacing:"-0.04em" }}>This trade<br/>got stopped out.</div>
        <p style={{ marginTop:18, fontSize:16, color:"var(--text-dim)", maxWidth:480, margin:"18px auto 0" }}>The page you're looking for doesn't exist. Back to safety.</p>
        <button className="btn primary lg" style={{ marginTop:30 }} onClick={() => go("home")}>← Back to homepage</button>
      </div>
    </div>
  );
}

/* ── Home ─────────────────────────────────────────────────────────────────── */
function Home({ go, stats }) {
  return (
    <>
      <Hero go={go} stats={stats}/>
      <StatStrip stats={stats}/>
      <Sources/>
      <Flow/>
      <Pricing go={go}/>
      <TrackRecord go={go} stats={stats}/>
      <FAQ/>
      <CTA go={go}/>
    </>
  );
}

/* ── Root ─────────────────────────────────────────────────────────────────── */
function Site() {
  const [page, setPage] = useState(() => {
    const hash = window.location.hash.slice(1);
    return hash || "home";
  });
  const [stats, setStats] = useState(null);

  const go = (p) => {
    setPage(p);
    window.scrollTo({ top: 0 });
    history.replaceState(null, "", "#" + p);
  };

  // Load public track record stats once
  useEffect(() => {
    fetch("/api/public/track-record")
      .then(r => r.json())
      .then(d => { if (!d.no_data) setStats(d); })
      .catch(() => {});
  }, []);

  // Handle hash changes (back button)
  useEffect(() => {
    const onHash = () => setPage(window.location.hash.slice(1) || "home");
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  return (
    <div className="site-shell">
      <Nav page={page} go={go}/>
      {page === "home"      && <Home go={go} stats={stats}/>}
      {page === "track"     && <TrackPage stats={stats}/>}
      {page === "docs"      && <DocsPage/>}
      {page === "telegram"  && <TelegramPage/>}
      {page === "login"     && (window.location.replace("/login"),  null)}
      {page === "signup"    && (window.location.replace("/signup"), null)}
      {page === "terms"     && <LegalPage kind="terms"   go={go}/>}
      {page === "privacy"   && <LegalPage kind="privacy" go={go}/>}
      {page === "risk"      && <LegalPage kind="risk"    go={go}/>}
      {page === "status"    && <StatusPage/>}
      {page === "changelog" && <ChangelogPage/>}
      {!["home","track","docs","telegram","login","signup","terms","privacy","risk","status","changelog"].includes(page) && <NotFoundPage go={go}/>}
      <Footer go={go}/>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<Site/>);
