/* global React, apiFetch */
// SIGNAL.TRADE cinematic — Market Context page.
// Wired to /api/market/context, /api/sources, /api/delivery/log,
// /api/market/sectors and /api/market/calendar.

const { useState: mUseState, useEffect: mUseEffect } = React;

function toNum(v, fallback = 0) {
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
}

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
  const ret = toNum(s.ret_1m, 0);
  const flow = toNum(s.flow_1w, 0);
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
      <span className={`mono ${flow >= 0 ? "bull" : "bear"}`} style={{ fontSize: 11, textAlign: "right" }}>{flow >= 0 ? "+" : ""}{flow.toFixed(0)}M</span>
    </div>
  );
}

function CalendarRow({ e }) {
  const col = e.impact === "HIGH" ? "var(--bear)" : e.impact === "MEDIUM" ? "var(--neutral)" : "var(--text-faint)";
  const d = new Date(e.date + "T00:00");
  const ds = d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  const hasFcst = e.forecast != null && e.previous != null;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "62px 1fr auto", gap: 12, alignItems: "center", padding: "10px 0", borderBottom: "1px solid var(--line-soft)" }}>
      <div>
        <div className="mono" style={{ fontSize: 11.5, fontWeight: 600 }}>{ds}</div>
        <div className="mono" style={{ fontSize: 10, color: "var(--text-faint)" }}>{e.time}</div>
      </div>
      <div>
        <div style={{ fontSize: 12.5, fontWeight: 500 }}>{e.name}</div>
        {hasFcst && <div style={{ fontSize: 11, color: "var(--text-faint)", marginTop: 1 }}>Fcst <span className="mono">{e.forecast}</span> · Prev <span className="mono">{e.previous}</span></div>}
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

// Parse a free-text delivery message ("→ BUY NVDA @ 1248.32 (Conf 87%)") into
// its structured pieces so each log entry can render as a signal card.
function _parseDeliveryMsg(m) {
  const s = m || "";
  const vm = s.match(/\b(BUY|SELL|HOLD)\b/);
  const verb = vm ? vm[1] : null;
  const tkm = verb ? s.match(new RegExp(verb + "\\s+([A-Z][A-Z.]{0,6})")) : null;
  const pxm = s.match(/@\s*\$?([\d,]+(?:\.\d+)?)/);
  const cm = s.match(/Conf\s*(\d+)\s*%/i);
  return { verb, tk: tkm ? tkm[1] : null, px: pxm ? pxm[1] : null, conf: cm ? cm[1] : null };
}

function DeliveryRow({ l, last }) {
  const msg = l.m || l.message || "";
  const status = l.s || l.status || "sent";
  const time = l.t || l.time;
  const { verb, tk, px, conf } = _parseDeliveryMsg(msg);
  const col = verb === "SELL" ? "var(--bear)" : verb === "BUY" ? "var(--bull)" : verb === "HOLD" ? "var(--neutral)"
    : status === "fail" ? "var(--bear)" : "var(--text-faint)";
  const frame = { borderLeft: `2px solid ${col}`, borderBottom: last ? "none" : "1px solid var(--line-soft)" };
  if (verb && tk) {
    return (
      <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 10, padding: "11px 14px", ...frame }}>
        <SignalBadge signal={verb}></SignalBadge>
        <div style={{ minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
            <span className="mono" style={{ fontWeight: 700, fontSize: 13, color: "var(--text)" }}>{tk}</span>
            {px && <span className="mono dim" style={{ fontSize: 11.5 }}>${px}</span>}
            <span className="kicker" style={{ marginLeft: "auto", color: "var(--text-ghost)", whiteSpace: "nowrap" }}>{time}</span>
          </div>
          <div className="kicker" style={{ marginTop: 3, color: "var(--text-faint)" }}>{conf ? `${conf}% CONF` : "DELIVERED"}</div>
        </div>
      </div>
    );
  }
  // system / non-trade message (rate limit, scan, suppressed HOLD…)
  return (
    <div style={{ padding: "11px 14px", ...frame }}>
      <div className="mono" style={{ fontSize: 11.5, color: status === "fail" ? "var(--bear)" : "var(--text-dim)", lineHeight: 1.5, textWrap: "pretty" }}>
        {msg.replace(/^[→~✗✓●]\s*/, "")}
      </div>
      <div className="kicker" style={{ marginTop: 3, color: "var(--text-ghost)" }}>{time}</div>
    </div>
  );
}

function DeliveryLog({ log }) {
  const rows = Array.isArray(log) && log.length ? log : M_LOG;
  return (
    <div className="glass" style={{ padding: 0, overflow: "hidden", alignSelf: "start" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "13px 14px", borderBottom: "1px solid var(--line)" }}>
        <span className="kicker">DELIVERY LOG</span>
        <span className="kicker" style={{ marginLeft: "auto", color: "var(--bull)", display: "inline-flex", gap: 6, alignItems: "center" }}><LiveDot></LiveDot> LIVE</span>
      </div>
      <div>{rows.map((l, i) => <DeliveryRow key={i} l={l} last={i === rows.length - 1}></DeliveryRow>)}</div>
    </div>
  );
}

function _first(...vals) {
  for (const v of vals) if (v != null) return v;
  return vals[vals.length - 1];
}

function marketSources(sources) {
  if (!Array.isArray(sources) || !sources.length) return M_SOURCES;
  const abbrFor = (s) => s.abbr || (typeof srcAbbr === "function" ? srcAbbr(s.name) : (s.name || "").slice(0, 4).toUpperCase());
  return sources.map((s) => ({
    id: s.id,
    name: s.name,
    abbr: abbrFor(s),
    desc: s.description || s.desc || "",
    on: s.is_on,
    reqs: _first(s.requests_24h, s.reqs, 0),
    latency: _first(s.latency_ms, s.latency, 0),
    feed: s.feed || (s.is_on ? "Live" : "Disabled"),
  }));
}

const ROTATION_MAP = { early: "early_bull", mid: "early_bull", late: "early_bear", recession: "late_bear" };
function marketRotation(macro) {
  const stage = macro?.sector_rotation?.stage || macro?.sector_rotation || M_MACRO.sector_rotation;
  const mapped = ROTATION_MAP[stage] || stage;
  return M_ROTATION.find((r) => r.id === mapped) || M_ROTATION[0];
}

function marketContextCards(m) {
  if (!m) return M_CONTEXT_SIGNALS;
  const fg = m.fear_greed, macro = m.macro, breadth = m.breadth, pc = m.put_call, aaii = m.aaii, cot = m.cot;
  const cards = [];
  if (fg?.score != null) {
    const sent = fg.score < 25 ? "bullish" : fg.score > 75 ? "bearish" : "neutral";
    cards.push({ src: "F&G", head: `Fear & Greed at ${fg.score.toFixed(1)} — ${fg.label || sent}`, body: `CNN Fear & Greed reads ${fg.score.toFixed(1)}. Extremes are contrarian: fear supports dips, greed warns of complacency.`, sentiment: sent });
  }
  if (macro?.vix != null) {
    const sent = macro.vix < 16 ? "bullish" : macro.vix > 25 ? "bearish" : "neutral";
    cards.push({ src: "VIX", head: `VIX at ${macro.vix.toFixed(2)}`, body: `VIX is ${macro.vix.toFixed(2)}. Low realized vol supports upside; elevated readings flag fear and mean-reversion opportunity.`, sentiment: sent });
  }
  const yc = macro?.yc_spread != null ? macro.yc_spread : (macro?.t10y != null && macro?.t2y != null ? macro.t10y - macro.t2y : (macro?.t10y != null && macro?.t3m != null ? macro.t10y - macro.t3m : null));
  if (yc != null) {
    const sent = yc > 0 ? "bullish" : "bearish";
    cards.push({ src: "Yield", head: `Yield curve ${yc >= 0 ? "+" : ""}${yc.toFixed(2)}%`, body: `10Y minus short-term spread is ${yc >= 0 ? "+" : ""}${yc.toFixed(2)}%. Inversion is a recession warning, but lead times vary.`, sentiment: sent });
  }
  if (breadth?.pct_above_200d != null) {
    const sent = breadth.pct_above_200d >= 60 ? "bullish" : breadth.pct_above_200d <= 40 ? "bearish" : "neutral";
    cards.push({ src: "Breadth", head: `${breadth.pct_above_200d.toFixed(1)}% of S&P 500 > 200d`, body: `Breadth is ${breadth.pct_above_200d.toFixed(1)}% — ${sent === "bullish" ? "broad participation" : sent === "bearish" ? "deterioration" : "mixed"} across the index.`, sentiment: sent });
  }
  if (cot?.net_pct != null) {
    const sent = cot.net_pct < -20 ? "bullish" : cot.net_pct > 20 ? "bearish" : "neutral";
    cards.push({ src: "COT", head: `Leveraged funds net ${cot.net_pct.toFixed(1)}%`, body: `COT positioning is ${cot.net_pct.toFixed(1)}% net. Crowded positioning is contrarian when extreme.`, sentiment: sent });
  }
  if (aaii?.spread != null) {
    const sent = aaii.spread > 20 ? "bearish" : aaii.spread < -10 ? "bullish" : "neutral";
    cards.push({ src: "AAII", head: `AAII bull-bear spread ${aaii.spread > 0 ? "+" : ""}${aaii.spread.toFixed(1)}%`, body: `Active investors are ${aaii.spread > 0 ? "net bullish" : "net bearish"}. Extremes are contrarian reads.`, sentiment: sent });
  }
  if (pc?.ratio != null) {
    const sent = pc.ratio > 1.1 ? "bullish" : pc.ratio < 0.7 ? "bearish" : "neutral";
    cards.push({ src: "P/C", head: `Put/Call ratio ${pc.ratio.toFixed(2)}`, body: `Equity put/call at ${pc.ratio.toFixed(2)} — ${sent === "bullish" ? "fearful" : sent === "bearish" ? "complacent" : "neutral"} options flow.`, sentiment: sent });
  }
  if (macro?.dxy_1m != null) {
    const sent = macro.dxy_1m > 2 ? "bearish" : macro.dxy_1m < -2 ? "bullish" : "neutral";
    cards.push({ src: "DXY", head: `Dollar ${macro.dxy_1m >= 0 ? "+" : ""}${macro.dxy_1m.toFixed(1)}% 1m`, body: `DXY moved ${macro.dxy_1m >= 0 ? "+" : ""}${macro.dxy_1m.toFixed(1)}% over the trailing month. A rising dollar tightens financial conditions.`, sentiment: sent });
  }
  return cards.length ? cards : M_CONTEXT_SIGNALS;
}

function PageMarket({ marketCtx, sources, log }) {
  const [sectors, setSectors] = mUseState(null);
  const [calendar, setCalendar] = mUseState(null);

  mUseEffect(() => {
    apiFetch("/api/market/sectors").then((d) => { if (Array.isArray(d)) setSectors(d); });
    apiFetch("/api/market/calendar").then((d) => { if (Array.isArray(d)) setCalendar(d); });
  }, []);

  const fg = marketCtx?.fear_greed || M_FEAR_GREED;
  const macro = marketCtx?.macro || M_MACRO;
  const breadth = marketCtx?.breadth || M_BREADTH;
  // Regime panel. Use the demo mock ONLY while the page is still loading
  // (marketCtx === null, e.g. the unauthenticated teaser). Once real context
  // has loaded but the HMM degraded (regime "unknown" — no/insufficient data),
  // show an honest "Unavailable" state. Never paint a fabricated BULL 73% over
  // a degraded model on the authed dashboard — every signal is gated by this tape.
  const hmmLive = marketCtx?.hmm_regime;
  const regimeUnavailable = !!marketCtx && (!hmmLive || !hmmLive.regime || hmmLive.regime === "unknown");
  const hmm = regimeUnavailable
    ? { regime: "unknown", bull_prob: 0, bear_prob: 0, transition_risk: 0, vix_z: 0 }
    : (marketCtx ? hmmLive : M_HMM);
  const regimeCol = regimeUnavailable
    ? "var(--text-faint)"
    : hmm.regime === "bear" ? "var(--bear)" : hmm.regime === "transition" ? "var(--neutral)" : "var(--bull)";
  const contextSignals = marketContextCards(marketCtx);
  const srcList = marketSources(sources);
  const rotation = marketRotation(macro);
  const ycSpread = macro?.yc_spread != null ? macro.yc_spread : (macro?.t10y != null && macro?.t2y != null ? macro.t10y - macro.t2y : M_MACRO.yc_spread);
  const ycTone = ycSpread >= 0 ? "up" : "down";
  const vixTone = macro?.vix != null && macro.vix < 20 ? "up" : "neutral";
  const sectorList = sectors && sectors.length ? sectors : M_SECTORS;
  const calendarList = calendar && calendar.length ? calendar : M_CALENDAR;
  const loadingSectors = sectors === null;
  const loadingCalendar = calendar === null;
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
            <Gauge score={fg.score} label={fg.label}></Gauge>
          </Defer>
          <div className="mono" style={{ fontSize: 11, color: "var(--text-faint)", textAlign: "center", marginTop: 6 }}>
            1w ago {fg.prev_1w ?? fg.prev_close ?? "—"} · 1m ago {fg.prev_1m ?? "—"}
          </div>
        </div>

        <div className="glass" style={{ padding: 20 }}>
          <div className="kicker" style={{ marginBottom: 12 }}>REGIME · HIDDEN MARKOV MODEL</div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
            <span className="mono" style={{ fontSize: 22, fontWeight: 700, color: regimeCol, textTransform: "capitalize" }}>{regimeUnavailable ? "Unavailable" : hmm.regime}</span>
            <span className="kicker" style={{ color: regimeCol }}>{regimeUnavailable ? "MODEL DEGRADED — NO DATA" : `${((hmm.bull_prob || 0) * 100).toFixed(0)}% PROBABILITY`}</span>
          </div>
          <div style={{ height: 8, borderRadius: 4, overflow: "hidden", display: "flex", marginBottom: 12 }}>
            <div style={{ width: `${(hmm.bull_prob || 0) * 100}%`, background: "var(--bull)" }}></div>
            <div style={{ width: `${(hmm.bear_prob || 0) * 100}%`, background: "var(--bear)", opacity: 0.6 }}></div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            <MacroStat label="Transition risk" value={`${((hmm.transition_risk || 0) * 100).toFixed(0)}%`} tone="neutral"></MacroStat>
            <MacroStat label="VIX z-score" value={(hmm.vix_z || 0).toFixed(1)} tone="up"></MacroStat>
          </div>
        </div>

        <div className="glass" style={{ padding: 20 }}>
          <div className="kicker" style={{ marginBottom: 12 }}>MACRO DASHBOARD</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            <MacroStat label="VIX" value={macro?.vix != null ? macro.vix.toFixed(2) : M_MACRO.vix} sub="Fear gauge" tone={vixTone}></MacroStat>
            <MacroStat label="10Y − 2Y" value={`${ycSpread >= 0 ? "+" : ""}${ycSpread.toFixed(2)}%`} sub={ycSpread < 0 ? "Inverted" : "Positive"} tone={ycTone}></MacroStat>
            <MacroStat label="Breadth >200d" value={`${breadth?.pct_above_200d != null ? breadth.pct_above_200d.toFixed(1) : M_BREADTH.pct_above_200d}%`} sub={breadth?.pct_above_200d >= 60 ? "Healthy" : "Mixed"} tone={breadth?.pct_above_200d >= 60 ? "up" : "neutral"}></MacroStat>
            <MacroStat label="CPI YoY" value={`${macro?.cpi != null ? macro.cpi.toFixed(1) : M_MACRO.cpi}%`} sub="Headline inflation" tone="neutral"></MacroStat>
          </div>
        </div>
      </div>

      {/* Context narrative */}
      <div className="kicker" style={{ margin: "26px 0 12px" }}>WHAT THE TAPE IS SAYING · {contextSignals.length} SIGNALS</div>
      <div className="mkt-context" style={{ marginBottom: 8 }}>
        {contextSignals.map((c, i) => <ContextCard key={i} c={c}></ContextCard>)}
      </div>

      {/* Sectors + calendar */}
      <div className="mkt-two" style={{ marginTop: 26 }}>
        <div className="glass" style={{ padding: 20, alignSelf: "start" }}>
          <div style={{ display: "flex", alignItems: "center", marginBottom: 6 }}>
            <span className="kicker">SECTOR PERFORMANCE · 1M RETURN + 1W FLOW</span>
            <span className="kicker" style={{ marginLeft: "auto", color: "var(--bull)" }}>{rotation.label.toUpperCase()}</span>
          </div>
          <Defer ms={600} skeleton={<div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 10 }}>{[0, 1, 2, 3, 4, 5].map((i) => <SkelBlock key={i} h={24}></SkelBlock>)}</div>}>
            <div style={{ marginTop: 8 }}>{sectorList.map((s) => <SectorBar key={s.etf} s={s}></SectorBar>)}</div>
          </Defer>
          <div style={{ marginTop: 14, padding: "10px 12px", borderRadius: 8, background: "var(--bull-soft)", border: "1px solid rgba(34,211,238,0.16)", fontSize: 12, color: "var(--text-dim)", lineHeight: 1.5 }}>
            Rotation read: <span className="bull" style={{ fontWeight: 600 }}>{rotation.note}</span> — leaders {rotation.etfs.join(", ")}.
          </div>
        </div>

        <div className="glass" style={{ padding: 20, alignSelf: "start" }}>
          <div className="kicker" style={{ marginBottom: 6 }}>ECONOMIC CALENDAR</div>
          <Defer ms={650} skeleton={<div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 10 }}>{[0, 1, 2, 3, 4].map((i) => <SkelBlock key={i} h={32}></SkelBlock>)}</div>}>
            <div style={{ marginTop: 4 }}>{calendarList.slice(0, 9).map((e, i) => <CalendarRow key={i} e={e}></CalendarRow>)}</div>
          </Defer>
        </div>
      </div>

      {/* Sources */}
      <div style={{ marginTop: 26 }}>
        <div className="kicker" style={{ marginBottom: 12 }}>DATA SOURCES · {srcList.filter((s) => s.on).length}/{srcList.length} ONLINE</div>
        <div className="mkt-sources">{srcList.map((s) => <SourcePill key={s.id} s={s}></SourcePill>)}</div>
      </div>
    </div>
  );
}

Object.assign(window, { PageMarket });
