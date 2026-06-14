/* global React */
// SIGNAL.TRADE cinematic — Home page.
const { useState: hUseState } = React;

function TickerTape() {
  const items = [...TICKER_TAPE, ...TICKER_TAPE]; // doubled for seamless loop
  return (
    <div className="marquee">
      <div className="marquee-track">
        {items.map((t, i) => (
          <span className="tick" key={i}>
            <span className={`verb ${t.verb.toLowerCase()}`}>{t.verb}</span>
            <span className="tk">{t.tk}</span>
            <span>{t.px}</span>
            <span className={t.chg.startsWith("+") ? "bull" : t.chg.startsWith("-") ? "bear" : "dim"}>{t.chg}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

function FeatureChart({ f }) {
  if (f.chart === "spark") return <Spark data={genSeries(f.seed, 40, 100, 0.004, 0.02)} w={260} h={56} color={f.color}></Spark>;
  if (f.chart === "bars") return <MiniBars seed={f.seed} n={26} w={260} h={56} color={f.color}></MiniBars>;
  if (f.chart === "equity") return <Spark data={genSeries(f.seed, 60, 100, 0.005, 0.013)} w={260} h={56} color={f.color}></Spark>;
  // regime: stepped line
  const rnd = mulberry32(f.seed);
  const data = []; let lvl = 0.5;
  for (let i = 0; i < 40; i++) { if (rnd() > 0.86) lvl = 0.2 + rnd() * 0.6; data.push(lvl); }
  return <Spark data={data} w={260} h={56} color={f.color} sw={1.5}></Spark>;
}

function HomeHero({ go, t }) {
  return (
    <section style={{ position: "relative", padding: "92px 0 64px", overflow: "hidden" }}>
      <div className={`mesh ${t.meshMotion ? "animated" : ""}`}>
        <div className="blob b1"></div>
        <div className="blob b2"></div>
        <div className="blob b3"></div>
        <div className="grid-lines"></div>
      </div>
      <div className="wrap" style={{ position: "relative", textAlign: "center", maxWidth: 880 }}>
        <div className="kicker" style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 14px", border: "1px solid var(--line)", borderRadius: 999, background: "rgba(10,14,23,0.5)" }}>
          <LiveDot></LiveDot> ENGINE LIVE · 52 SIGNALS TODAY · 680 TICKERS SCANNED
        </div>
        <h1 style={{ fontSize: "clamp(38px, 6vw, 68px)", fontWeight: 700, letterSpacing: "-0.035em", lineHeight: 1.04, margin: "28px 0 18px", textWrap: "balance" }}>
          The market never sleeps.<br></br>
          <span style={{ background: "linear-gradient(90deg, var(--bull), #7dd3fc)", WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" }}>Neither does your edge.</span>
        </h1>
        <p style={{ fontSize: 17, color: "var(--text-dim)", maxWidth: 580, margin: "0 auto 34px", lineHeight: 1.6, textWrap: "pretty" }}>
          Institutional flow, options sweeps, 25+ technicals and macro regime — fused into one
          confidence score and pushed to your phone the second a signal fires.
        </p>
        <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
          <button className="btn primary lg" onClick={() => go("dashboard")}>Open the dashboard</button>
          <button className="btn lg" onClick={() => go("backtest")}>Run a backtest →</button>
        </div>
        <div className="mono" style={{ display: "flex", gap: 30, justifyContent: "center", marginTop: 44, fontSize: 12.5, color: "var(--text-faint)", flexWrap: "wrap", fontVariantNumeric: "tabular-nums" }}>
          <span><strong className="bull"><Num value={61.4} dp={1}></Num>%</strong> 7-day win rate</span>
          <span><strong style={{ color: "var(--text)" }}><Num value={52} dp={0}></Num></strong> signals today</span>
          <span><strong style={{ color: "var(--text)" }}><Num value={2.3} dp={1}></Num>s</strong> avg latency</span>
          <span><strong style={{ color: "var(--text)" }}><Num value={20} dp={0}></Num>y</strong> of backtests</span>
        </div>
      </div>
    </section>
  );
}

function StatStrip() {
  return (
    <section className="wrap" style={{ padding: "8px 28px 0" }}>
      <div className="home-stats glass" style={{ padding: "4px 0" }}>
        {HOME_STATS.map((s, i) => (
          <div key={i} style={{ padding: "20px 24px", borderRight: i < HOME_STATS.length - 1 ? "1px solid var(--line-soft)" : "none" }}>
            <div style={{ fontSize: 28, fontWeight: 700, letterSpacing: "-0.02em" }}>
              <Num value={s.n} dp={s.dp} prefix={s.prefix || ""} suffix={s.suffix}></Num>
            </div>
            <div style={{ fontSize: 12.5, fontWeight: 600, marginTop: 4 }}>{s.l}</div>
            <div style={{ fontSize: 11.5, color: "var(--text-faint)", marginTop: 2 }}>{s.s}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function Pricing({ go }) {
  return (
    <section className="wrap" style={{ padding: "72px 28px 40px" }}>
      <div className="kicker" style={{ marginBottom: 10 }}>PRICING</div>
      <h2 style={{ fontSize: 30, fontWeight: 650, letterSpacing: "-0.025em", margin: "0 0 32px", maxWidth: 560, textWrap: "balance" }}>
        Pick a tier. Cancel anytime in one click.
      </h2>
      <div className="pricing-grid">
        {M_PRICING.map((t, i) => (
          <div key={i} className="glass glass-hover" style={{ padding: "24px 22px", display: "flex", flexDirection: "column", gap: 4, position: "relative", borderColor: t.featured ? "rgba(34,211,238,0.3)" : undefined, background: t.featured ? "linear-gradient(160deg, rgba(34,211,238,0.06), rgba(255,255,255,0.02))" : undefined }}>
            {t.featured && <span className="kicker" style={{ position: "absolute", top: 18, right: 18, color: "var(--bull)" }}>MOST POPULAR</span>}
            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-dim)" }}>{t.name}</div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 4, margin: "2px 0 6px" }}>
              <span className="mono" style={{ fontSize: 30, fontWeight: 700 }}>{t.amt}</span>
              <span className="mono dim" style={{ fontSize: 13 }}>{t.per}</span>
            </div>
            <p style={{ fontSize: 12.5, color: "var(--text-dim)", lineHeight: 1.5, margin: "0 0 16px", minHeight: 54, textWrap: "pretty" }}>{t.desc}</p>
            <button className={`btn ${t.featured ? "primary" : ""}`} style={{ width: "100%", marginBottom: 16 }} onClick={() => go("dashboard")}>{t.name === "Free" ? "Get started" : "Start 7-day trial"}</button>
            <div style={{ display: "flex", flexDirection: "column", gap: 9 }}>
              {t.feats.map(([lbl, on], j) => (
                <div key={j} style={{ display: "flex", alignItems: "center", gap: 9, fontSize: 12.5, color: on ? "var(--text)" : "var(--text-ghost)" }}>
                  <span style={{ color: on ? "var(--bull)" : "var(--text-ghost)", fontWeight: 700, fontFamily: "var(--font-mono)", fontSize: 12 }}>{on ? "\u2713" : "\u2715"}</span>
                  {lbl}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function FeatureCards() {
  return (
    <section className="wrap" style={{ padding: "72px 28px 40px" }}>
      <div className="kicker" style={{ marginBottom: 10 }}>WHAT THE ENGINE WATCHES</div>
      <h2 style={{ fontSize: 30, fontWeight: 650, letterSpacing: "-0.025em", margin: "0 0 32px", maxWidth: 560, textWrap: "balance" }}>
        Four streams of evidence. One honest score.
      </h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(270px, 1fr))", gap: 14 }}>
        {FEATURES.map((f, i) => (
          <div key={i} className="glass glass-hover" style={{ padding: "22px 22px 16px", display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <div style={{ fontSize: 15.5, fontWeight: 600, marginBottom: 6 }}>{f.t}</div>
              <div style={{ fontSize: 13, color: "var(--text-dim)", lineHeight: 1.55, textWrap: "pretty" }}>{f.d}</div>
            </div>
            <div style={{ marginTop: "auto" }}>
              <FeatureChart f={f}></FeatureChart>
              <div className="kicker" style={{ marginTop: 10, color: f.color === "neutral" ? "var(--neutral)" : "var(--bull)" }}>{f.stat}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function StoryStrip({ go }) {
  return (
    <section className="wrap" style={{ padding: "48px 28px 88px" }}>
      <div className="glass story-grid" style={{ padding: "44px 44px", background: "linear-gradient(135deg, rgba(34,211,238,0.05), rgba(255,255,255,0.015) 55%)" }}>
        <div>
          <div className="kicker" style={{ marginBottom: 12 }}>DATA STORYTELLING, NOT DATA DUMPS</div>
          <h3 style={{ fontSize: 24, fontWeight: 650, letterSpacing: "-0.02em", margin: "0 0 14px", textWrap: "balance" }}>
            Every signal arrives with its track record attached.
          </h3>
          <p style={{ fontSize: 14, color: "var(--text-dim)", lineHeight: 1.65, margin: "0 0 24px", textWrap: "pretty" }}>
            Not "Signal: BUY, Sharpe 1.4." Instead: <em style={{ color: "var(--text)", fontStyle: "normal", fontWeight: 600 }}>"this pattern
            has a 78% win rate over 20 years with max drawdown under 3%"</em> — plus the equity curve to prove it,
            and a plain-English explanation of why it fired.
          </p>
          <button className="btn primary" onClick={() => go("dashboard")}>See it live</button>
        </div>
        <div className="glass" style={{ padding: 20, background: "rgba(10,14,23,0.5)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
            <SignalBadge signal="BUY"></SignalBadge>
            <span className="mono" style={{ fontWeight: 700, fontSize: 14 }}>NVDA</span>
            <span className="mono dim" style={{ fontSize: 12, marginLeft: "auto" }}>conf 87%</span>
          </div>
          <Spark data={genSeries(11 * 97 + 5, 60, 100, 0.0022, 0.024)} w={300} h={72} color="bull"></Spark>
          <div style={{ fontSize: 12.5, color: "var(--text-dim)", lineHeight: 1.55, marginTop: 14, textWrap: "pretty" }}>
            NVDA signals have closed <span className="bull" style={{ fontWeight: 600 }}>71% green over the 14-day horizon</span> historically — 84 signals on the public ledger, +18.2% cumulative.
          </div>
        </div>
      </div>
    </section>
  );
}

function PageHome({ go, t, currentUser }) {
  // Paid members don't need the upsell — only show pricing to free / signed-out visitors.
  const tier = currentUser?.subscription_tier || "free";
  const showPricing = tier === "free";
  return (
    <div className="page">
      <HomeHero go={go} t={t}></HomeHero>
      <TickerTape></TickerTape>
      <StatStrip></StatStrip>
      <FeatureCards></FeatureCards>
      <StoryStrip go={go}></StoryStrip>
      {showPricing && <Pricing go={go}></Pricing>}
    </div>
  );
}

Object.assign(window, { PageHome, TickerTape });
