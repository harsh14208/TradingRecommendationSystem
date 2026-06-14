/* global React */
// SIGNAL.TRADE cinematic — Market Context page.
const { useState: mUseState } = React;

function Gauge({ score, label }) {
  // semicircle 0..100 → 180°..0°
  const r = 80, cx = 100, cy = 100, sw = 14;
  const ang = Math.PI * (1 - score / 100);
  const x = cx + r * Math.cos(ang), y = cy - r * Math.sin(ang);
  const zoneCol = score < 25 ? "var(--bear)" : score < 45 ? "#fb8d4d" : score < 55 ? "var(--neutral)" : score < 75 ? "#7ddf9e" : "var(--bull)";
  const arc = (a0, a1) => {
    const p0 = [cx + r * Math.cos(a0), cy - r * Math.sin(a0)];
    const p1 = [cx + r * Math.cos(a1), cy - r * Math.sin(a1)];
    return `M${p0[0].toFixed(1)},${p0[1].toFixed(1)} A${r},${r} 0 0 1 ${p1[0].toFixed(1)},${p1[1].toFixed(1)}`;
  };
  const segs = [
    [Math.PI, Math.PI * 0.75, "var(--bear)"],
    [Math.PI * 0.75, Math.PI * 0.55, "#fb8d4d"],
    [Math.PI * 0.55, Math.PI * 0.45, "var(--neutral)"],
    [Math.PI * 0.45, Math.PI * 0.25, "#7ddf9e"],
    [Math.PI * 0.25, 0, "var(--bull)"],
  ];
  return (
    <svg viewBox="0 0 200 120" style={{ width: "100%", maxWidth: 240, display: "block", margin: "0 auto" }}>
      {segs.map((sg, i) => <path key={i} d={arc(sg[0], sg[1])} fill="none" stroke={sg[2]} strokeWidth={sw} strokeLinecap="butt" opacity="0.85"></path>)}
      <line x1={cx} y1={cy} x2={x} y2={y} stroke="var(--text)" strokeWidth="2.5" strokeLinecap="round"></line>
      <circle cx={cx} cy={cy} r="5" fill="var(--text)"></circle>
      <text x={cx} y={cy - 26} textAnchor="middle" fontSize="26" fontWeight="700" fill={zoneCol} fontFamily="var(--font-mono)">{score.toFixed(0)}</text>
      <text x={cx} y={cy - 10} textAnchor="middle" fontSize="10" fill="var(--text-faint)" fontFamily="var(--font-mono)" letterSpacing="0.12em">{label.toUpperCase()}</text>
    </svg>
  );
}

function MacroStat({ label, value, sub, tone }) {
  const col = tone === "up" ? "var(--bull)" : tone === "down" ? "var(--bear)" : "var(--text)";
  return (
    <div style={{ padding: "12px 14px", borderRadius: 8, background: "rgba(255,255,255,0.02)", border: "1px solid var(--line-soft)" }}>
      <div className="kicker" style={{ marginBottom: 6 }}>{label}</div>
      <div className="mono" style={{ fontSize: 17, fontWeight: 700, color: col }}>{value}</div>
      {sub && <div style={{ fontSize: 10.5, color: "var(--text-faint)", marginTop: 2 }}>{sub}</div>}
    </div>
  );
}

function ContextCard({ c }) {
  const col = c.sentiment === "bullish" ? "var(--bull)" : c.sentiment === "bearish" ? "var(--bear)" : "var(--neutral)";
  return (
    <div className="glass glass-hover" style={{ padding: 16, borderLeft: `2px solid ${col}` }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span className="mono" style={{ fontSize: 9.5, fontWeight: 700, letterSpacing: "0.06em", color: col, border: `1px solid ${col}`, borderRadius: 4, padding: "2px 6px" }}>{c.src}</span>
        <span style={{ fontSize: 13, fontWeight: 600 }}>{c.head}</span>
        <span className="kicker" style={{ marginLeft: "auto", color: col }}>{c.sentiment.toUpperCase()}</span>
      </div>
      <p style={{ margin: 0, fontSize: 12, color: "var(--text-dim)", lineHeight: 1.55, textWrap: "pretty" }}>{c.body}</p>
    </div>
  );
}

function SectorBar({ s }) {
  const ret = s.ret_1m;
  const col = ret >= 0 ? "var(--bull)" : "var(--bear)";
  const w = Math.min(100, Math.abs(ret) * 8);
  return (
    <div style={{ display: "grid", gridTemplateColumns: "120px 1fr 64px 64px", gap: 12, alignItems: "center", padding: "8px 0", borderBottom: "1px solid var(--line-soft)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span className="mono" style={{ fontSize: 11, fontWeight: 700, color: "var(--text)" }}>{s.etf}</span>
        <span style={{ fontSize: 11.5, color: "var(--text-dim)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{s.name}</span>
      </div>
      <div style={{ display: "flex", justifyContent: ret >= 0 ? "flex-start" : "flex-end", height: 6 }}>
        <div style={{ width: `${w}%`, borderRadius: 2, background: col, opacity: 0.7 }}></div>
      </div>
      <span className={`mono ${ret >= 0 ? "bull" : "bear"}`} style={{ fontSize: 11.5, textAlign: "right" }}>{ret >= 0 ? "+" : ""}{ret.toFixed(1)}%</span>
      <span className={`mono ${s.flow_1w >= 0 ? "bull" : "bear"}`} style={{ fontSize: 11, textAlign: "right" }}>{s.flow_1w >= 0 ? "+" : ""}{s.flow_1w.toFixed(0)}M</span>
    </div>
  );
}

function CalendarRow({ e }) {
  const col = e.impact === "HIGH" ? "var(--bear)" : e.impact === "MEDIUM" ? "var(--neutral)" : "var(--text-faint)";
  const d = new Date(e.date + "T00:00");
  const ds = d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  return (
    <div style={{ display: "grid", gridTemplateColumns: "62px 1fr auto", gap: 12, alignItems: "center", padding: "10px 0", borderBottom: "1px solid var(--line-soft)" }}>
      <div>
        <div className="mono" style={{ fontSize: 11.5, fontWeight: 600 }}>{ds}</div>
        <div className="mono" style={{ fontSize: 10, color: "var(--text-faint)" }}>{e.time}</div>
      </div>
      <div>
        <div style={{ fontSize: 12.5, fontWeight: 500 }}>{e.name}</div>
        <div style={{ fontSize: 11, color: "var(--text-faint)", marginTop: 1 }}>Fcst <span className="mono">{e.forecast}</span> · Prev <span className="mono">{e.previous}</span></div>
      </div>
      <span className="mono" style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.06em", color: col, border: `1px solid ${col}`, borderRadius: 4, padding: "2px 6px" }}>{e.impact}</span>
    </div>
  );
}

function SourcePill({ s }) {
  return (
    <div className="glass" style={{ padding: "12px 14px", opacity: s.on ? 1 : 0.5 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <span className={`live-dot ${s.on ? "" : "red"}`} style={{ background: s.on ? "var(--bull)" : "var(--text-faint)" }}></span>
        <span style={{ fontSize: 12.5, fontWeight: 600 }}>{s.name}</span>
        <span className="kicker" style={{ marginLeft: "auto" }}>{s.abbr}</span>
      </div>
      <div style={{ fontSize: 11, color: "var(--text-dim)", marginBottom: 8 }}>{s.desc}</div>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <span className="mono" style={{ fontSize: 10.5, color: "var(--text-faint)" }}>{s.on ? `${s.reqs} req · ${s.latency}ms` : "Disabled"}</span>
        <span className="kicker" style={{ color: s.on ? "var(--bull)" : "var(--text-ghost)" }}>{s.feed}</span>
      </div>
    </div>
  );
}

function DeliveryLog() {
  return (
    <div className="glass" style={{ padding: 16, alignSelf: "start" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <span className="kicker">DELIVERY LOG</span>
        <span className="kicker" style={{ marginLeft: "auto", color: "var(--bull)", display: "inline-flex", gap: 6, alignItems: "center" }}><LiveDot></LiveDot> LIVE</span>
      </div>
      <div className="mono" style={{ fontSize: 11, display: "flex", flexDirection: "column", gap: 7 }}>
        {M_LOG.map((l, i) => {
          const col = l.s === "sent" ? "var(--bull)" : l.s === "fail" ? "var(--bear)" : "var(--neutral)";
          return (
            <div key={i} style={{ display: "flex", gap: 10 }}>
              <span style={{ color: "var(--text-ghost)" }}>{l.t}</span>
              <span style={{ color: col, flex: 1, textWrap: "pretty" }}>{l.m}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function PageMarket() {
  return (
    <div className="page wrap" style={{ paddingTop: 24, paddingBottom: 56 }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 18, flexWrap: "wrap" }}>
        <h2 style={{ fontSize: 24, fontWeight: 650, letterSpacing: "-0.02em", margin: 0 }}>Market Context</h2>
        <span className="kicker" style={{ display: "inline-flex", gap: 7, alignItems: "center" }}><LiveDot></LiveDot> EVERY SIGNAL IS GATED BY THE TAPE BELOW</span>
      </div>

      {/* Top: gauge + regime + macro */}
      <div className="mkt-top" style={{ marginBottom: 14 }}>
        <div className="glass" style={{ padding: 20 }}>
          <div className="kicker" style={{ marginBottom: 10 }}>FEAR & GREED</div>
          <Defer ms={500} skeleton={<SkelBlock h={120}></SkelBlock>}>
            <Gauge score={M_FEAR_GREED.score} label={M_FEAR_GREED.label}></Gauge>
          </Defer>
          <div className="mono" style={{ fontSize: 11, color: "var(--text-faint)", textAlign: "center", marginTop: 6 }}>
            1w ago {M_FEAR_GREED.prev_1w} · 1m ago {M_FEAR_GREED.prev_1m}
          </div>
        </div>

        <div className="glass" style={{ padding: 20 }}>
          <div className="kicker" style={{ marginBottom: 12 }}>REGIME · HIDDEN MARKOV MODEL</div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
            <span className="mono" style={{ fontSize: 22, fontWeight: 700, color: "var(--bull)", textTransform: "capitalize" }}>{M_HMM.regime}</span>
            <span className="kicker" style={{ color: "var(--bull)" }}>{(M_HMM.bull_prob * 100).toFixed(0)}% PROBABILITY</span>
          </div>
          <div style={{ height: 8, borderRadius: 4, overflow: "hidden", display: "flex", marginBottom: 12 }}>
            <div style={{ width: `${M_HMM.bull_prob * 100}%`, background: "var(--bull)" }}></div>
            <div style={{ width: `${M_HMM.bear_prob * 100}%`, background: "var(--bear)", opacity: 0.6 }}></div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            <MacroStat label="Transition risk" value={`${(M_HMM.transition_risk * 100).toFixed(0)}%`} tone="neutral"></MacroStat>
            <MacroStat label="VIX z-score" value={M_HMM.vix_z.toFixed(1)} tone="up"></MacroStat>
          </div>
        </div>

        <div className="glass" style={{ padding: 20 }}>
          <div className="kicker" style={{ marginBottom: 12 }}>MACRO DASHBOARD</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            <MacroStat label="VIX" value={M_MACRO.vix} sub="Below 1-yr mean" tone="up"></MacroStat>
            <MacroStat label="10Y − 2Y" value={`${M_MACRO.yc_spread}%`} sub="Inverted" tone="down"></MacroStat>
            <MacroStat label="Breadth >200d" value={`${M_BREADTH.pct_above_200d}%`} sub="Healthy" tone="up"></MacroStat>
            <MacroStat label="CPI YoY" value={`${M_MACRO.cpi}%`} sub="Cooling" tone="neutral"></MacroStat>
          </div>
        </div>
      </div>

      {/* Context narrative */}
      <div className="kicker" style={{ margin: "26px 0 12px" }}>WHAT THE TAPE IS SAYING · {M_CONTEXT_SIGNALS.length} SIGNALS</div>
      <div className="mkt-context" style={{ marginBottom: 8 }}>
        {M_CONTEXT_SIGNALS.map((c, i) => <ContextCard key={i} c={c}></ContextCard>)}
      </div>

      {/* Sectors + calendar */}
      <div className="mkt-two" style={{ marginTop: 26 }}>
        <div className="glass" style={{ padding: 20, alignSelf: "start" }}>
          <div style={{ display: "flex", alignItems: "center", marginBottom: 6 }}>
            <span className="kicker">SECTOR PERFORMANCE · 1M RETURN + 1W FLOW</span>
            <span className="kicker" style={{ marginLeft: "auto", color: "var(--bull)" }}>{M_ROTATION.find((r) => r.id === M_MACRO.sector_rotation).label.toUpperCase()}</span>
          </div>
          <Defer ms={600} skeleton={<div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 10 }}>{[0, 1, 2, 3, 4, 5].map((i) => <SkelBlock key={i} h={24}></SkelBlock>)}</div>}>
            <div style={{ marginTop: 8 }}>{M_SECTORS.map((s) => <SectorBar key={s.etf} s={s}></SectorBar>)}</div>
          </Defer>
          <div style={{ marginTop: 14, padding: "10px 12px", borderRadius: 8, background: "var(--bull-soft)", border: "1px solid rgba(34,211,238,0.16)", fontSize: 12, color: "var(--text-dim)", lineHeight: 1.5 }}>
            Rotation read: <span className="bull" style={{ fontWeight: 600 }}>{M_ROTATION.find((r) => r.id === M_MACRO.sector_rotation).note}</span> — leaders {M_ROTATION.find((r) => r.id === M_MACRO.sector_rotation).etfs.join(", ")}.
          </div>
        </div>

        <div className="glass" style={{ padding: 20, alignSelf: "start" }}>
          <div className="kicker" style={{ marginBottom: 6 }}>ECONOMIC CALENDAR</div>
          <Defer ms={650} skeleton={<div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 10 }}>{[0, 1, 2, 3, 4].map((i) => <SkelBlock key={i} h={32}></SkelBlock>)}</div>}>
            <div style={{ marginTop: 4 }}>{M_CALENDAR.slice(0, 9).map((e, i) => <CalendarRow key={i} e={e}></CalendarRow>)}</div>
          </Defer>
        </div>
      </div>

      {/* Sources + log */}
      <div className="mkt-two" style={{ marginTop: 26 }}>
        <div>
          <div className="kicker" style={{ marginBottom: 12 }}>DATA SOURCES · {M_SOURCES.filter((s) => s.on).length}/{M_SOURCES.length} ONLINE</div>
          <div className="mkt-sources">{M_SOURCES.map((s) => <SourcePill key={s.id} s={s}></SourcePill>)}</div>
        </div>
        <DeliveryLog></DeliveryLog>
      </div>
    </div>
  );
}

Object.assign(window, { PageMarket });
