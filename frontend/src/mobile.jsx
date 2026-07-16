/* global React */
const { useState, useEffect } = React;

/* ── Accessibility helpers ──────────────────────────────────────────────── */
function onKeyActivate(handler) {
  return (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handler(e);
    }
  };
}

// Human, non-alarming label for why a signal isn't delivered (most are simply
// below the confidence bar). `short` returns a compact uppercase chip.
function deliveryLabel(status, short) {
  const s = (status || "").toLowerCase();
  if (s.includes("mean-reversion setup") || s.includes("oversold")) return short ? "NO MR SETUP" : "No mean-reversion setup";
  if (s.includes("floor") || s.includes("confidence")) return short ? "BELOW THRESHOLD" : "Below confidence threshold";
  if (s.includes("intraday") || s.includes("style")) return short ? "STYLE OFF" : "Intraday style — not delivered";
  if (s.includes("sector")) return short ? "SECTOR PAUSED" : "Sector temporarily paused";
  if (s.includes("regime") || s.includes("long-only")) return short ? "NOT BUY" : "Not a buy signal";
  if (s.includes("blocked") || s.includes("edge")) return short ? "PAUSED" : "Ticker paused — no MR edge";
  return short ? "BELOW THRESHOLD" : "Below delivery threshold";
}

// ── Static mock data (replaced by real API when online) ─────────────────────
const MOBILE_SIGNALS_MOCK = [
  { tk:"NVDA", action:"BUY",  style:"POSITION", conf:87, head:"Breakout above 200-DMA + CUDA license rumor", entry:1245, stop:1188, target:1385, time:"09:31", co:"NVIDIA Corp",            price:1248.40, ch:32.10,  chPct:2.64  },
  { tk:"TSLA", action:"SELL", style:"INTRADAY", conf:72, head:"Breaking below pivot + delivery miss",         entry:165,  stop:172,  target:152,  time:"10:14", co:"Tesla Inc",               price:164.80,  ch:-4.20,  chPct:-2.48 },
  { tk:"AMD",  action:"BUY",  style:"SWING",    conf:69, head:"Volume surge + 50-DMA reclaim",               entry:162,  stop:154,  target:178,  time:"10:42", co:"Advanced Micro Devices",   price:162.50,  ch:3.85,   chPct:2.43  },
  { tk:"META", action:"HOLD", style:"POSITION", conf:54, head:"Mixed signals — earnings beat, guidance soft", entry:null, stop:null, target:null, time:"11:08", co:"Meta Platforms",           price:488.20,  ch:0.40,   chPct:0.08  },
  { tk:"AAPL", action:"BUY",  style:"SWING",    conf:76, head:"Insider cluster buy + analyst upgrade",        entry:178,  stop:172,  target:192,  time:"11:34", co:"Apple Inc",                price:179.20,  ch:2.10,   chPct:1.18  },
];

const POSITIONS_MOCK = [
  { tk:"NVDA", shares:12,  avg:1180,  last:1248.40, pnl:820.80, pct:5.80,  spark:[40,42,45,44,48,52,55,58] },
  { tk:"AAPL", shares:50,  avg:174.50,last:179.20,  pnl:235.00, pct:2.69,  spark:[35,36,34,38,40,39,42,44] },
  { tk:"MSFT", shares:8,   avg:412,   last:428.60,  pnl:132.80, pct:4.03,  spark:[30,32,35,33,36,38,40,41] },
  { tk:"TSLA", shares:-10, avg:172,   last:164.80,  pnl:72.00,  pct:4.19,  spark:[50,48,45,47,43,40,38,36] },
];

const OPTIONS_SUMMARY_MOCK = {
  label:"COT + carry + diversifier pack",
  n:24,
  netSharpe:0.88,
  annReturn:18.7,
  annVol:21.3,
  maxDD:-38.5,
  calmar:0.46,
  since:"2007",
};

// ── Auth helpers (same pattern as app.auth.jsx) ─────────────────────────────
let _accessToken = null;
const getToken   = () => _accessToken;
const saveToken  = t  => { _accessToken = t; };
const clearToken = () => { _accessToken = null; };

let _refreshPromise = null;
async function _tryRefresh() {
  if (_refreshPromise) return _refreshPromise;
  _refreshPromise = fetch("/api/auth/refresh-cookie", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  })
    .then(r => r.ok ? r.json() : null)
    .then(d => {
      if (d?.access_token) { saveToken(d.access_token); return true; }
      return false;
    })
    .catch(() => false)
    .finally(() => { _refreshPromise = null; });
  return _refreshPromise;
}

async function authFetch(path, opts = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(opts.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(path, { ...opts, headers, credentials: "include" });
  if (res.status === 401) {
    const refreshed = await _tryRefresh();
    if (refreshed) {
      const newToken = getToken();
      const retryHeaders = { ...headers, "Authorization": `Bearer ${newToken}` };
      return fetch(path, { ...opts, headers: retryHeaders, credentials: "include" });
    }
    clearToken();
    window.location.replace("/login?next=/mobile");
  }
  return res;
}

async function apiFetch(path, opts = {}) {
  try {
    const res = await authFetch(path, opts);
    if (!res.ok) throw new Error(res.status);
    return res.json();
  } catch { return null; }
}

async function mFetch(path, opts = {}) {
  try {
    const res = await authFetch(path, opts);
    if (!res.ok) return null;
    return res.json();
  } catch { return null; }
}

function Sparkline({ data, color }) {
  if (!data || !data.length) return null;
  const max = Math.max(...data), min = Math.min(...data);
  const range = max - min || 1;
  const w = 60, h = 24;
  const pts = data.map((v, i) => `${(i/(data.length-1))*w},${h-((v-min)/range)*h}`).join(" ");
  return (
    <svg aria-hidden="true" width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ width:60, height:24 }}>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

const MIcon = ({ name, size = 22 }) => {
  const paths = {
    feed:     <><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="14" y2="18"/></>,
    star:     <polygon points="12 2 15 9 22 9.5 17 14 18.5 21 12 17.5 5.5 21 7 14 2 9.5 9 9 12 2"/>,
    chart:    <><line x1="3" y1="20" x2="21" y2="20"/><polyline points="4 16 9 11 13 14 20 6"/></>,
    book:     <><path d="M4 4h12a4 4 0 0 1 4 4v12H8a4 4 0 0 1-4-4V4z"/><line x1="4" y1="18" x2="20" y2="18"/></>,
    user:     <><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></>,
    bell:     <><path d="M18 16v-5a6 6 0 0 0-12 0v5l-2 2h16z"/><path d="M10 20a2 2 0 0 0 4 0"/></>,
    settings: <><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 0 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 0 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 0 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 0 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></>,
    filter:   <polygon points="3 4 21 4 14 13 14 19 10 21 10 13 3 4"/>,
    chev:     <polyline points="9 6 15 12 9 18"/>,
    chevl:    <polyline points="15 6 9 12 15 18"/>,
    send:     <><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></>,
    money:    <><circle cx="12" cy="12" r="10"/><path d="M15 9.5a3 3 0 0 0-3-1.5c-1.7 0-3 1-3 2.5s1.5 2 3 2.5 3 1 3 2.5-1.3 2.5-3 2.5-3-.5-3-1.5"/><line x1="12" y1="6" x2="12" y2="8"/><line x1="12" y1="16" x2="12" y2="18"/></>,
    shield:   <path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-4z"/>,
    plug:     <><path d="M9 2v6"/><path d="M15 2v6"/><path d="M6 8h12v4a6 6 0 0 1-12 0V8z"/><path d="M12 18v4"/></>,
    refresh:  <><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1 2.12-9.36L23 10"/></>,
  };
  return (
    <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      {paths[name]}
    </svg>
  );
};

function MStatusBar({ time }) {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => { const id = setInterval(() => setNow(new Date()), 1000); return () => clearInterval(id); }, []);
  const display = time || now.toLocaleTimeString([], { hour:"2-digit", minute:"2-digit" });
  return (
    <div style={{ display:"flex", justifyContent:"space-between", padding:"6px 22px 0", fontFamily:"var(--mono)", fontSize:13, fontWeight:600 }}>
      <span>{display}</span>
      <span style={{ display:"inline-flex", gap:6, alignItems:"center" }}>
        <svg aria-hidden="true" width="16" height="11" viewBox="0 0 16 11" fill="currentColor"><rect x="0" y="7" width="3" height="4" rx="0.5"/><rect x="4" y="5" width="3" height="6" rx="0.5"/><rect x="8" y="3" width="3" height="8" rx="0.5"/><rect x="12" y="0" width="3" height="11" rx="0.5"/></svg>
        <svg aria-hidden="true" width="16" height="11" viewBox="0 0 16 11" fill="currentColor"><path d="M8 2C5 2 2.5 3 1 5l1.5 1.5C3.5 5 5.5 4 8 4s4.5 1 5.5 2.5L15 5C13.5 3 11 2 8 2zm0 3.5C6.5 5.5 5 6 4 7l1.5 1.5C6 8 7 7.5 8 7.5s2 .5 2.5 1L12 7c-1-1-2.5-1.5-4-1.5zm0 3.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z"/></svg>
        <svg aria-hidden="true" width="24" height="11" viewBox="0 0 24 11" fill="none"><rect x="0.5" y="0.5" width="20" height="10" rx="2" stroke="currentColor"/><rect x="2" y="2" width="17" height="7" rx="1" fill="currentColor"/><rect x="21" y="3.5" width="1.5" height="4" rx="0.5" fill="currentColor"/></svg>
      </span>
    </div>
  );
}

function MTabBar({ active, setTab }) {
  const tabs = [
    { k:"feed",      l:"Signals",   i:"feed"  },
    { k:"watch",     l:"Watchlist", i:"star"  },
    { k:"portfolio", l:"Paper",     i:"chart" },
    { k:"record",    l:"Record",    i:"book"  },
    { k:"account",   l:"Account",   i:"user"  },
  ];
  return (
    <div className="m-tabs">
      {tabs.map(t => (
        <div key={t.k} className={`m-tab ${active===t.k?"on":""}`} onClick={() => setTab(t.k)} role="button" tabIndex={0}>
          <MIcon name={t.i} size={22}/>
          <span>{t.l}</span>
        </div>
      ))}
    </div>
  );
}

// ── Feed screen ──────────────────────────────────────────────────────────────
function FeedScreen({ signals, onSelect, loading, demo, onRefresh }) {
  const [filter, setFilter] = useState("all");
  const [ptrState, setPtrState] = useState("idle"); // idle | pulling | released
  const ptrStartY = useRef(0);
  const ptrRef = useRef(null);

  const items = filter === "all" ? signals
    : filter === "buy" ? signals.filter(s => (s.action||s.act) === "BUY")
    : signals.filter(s => (s.confidence||s.conf||0) >= 70);

  const onTouchStart = e => {
    if (ptrRef.current && ptrRef.current.scrollTop === 0) {
      ptrStartY.current = e.touches[0].clientY;
    }
  };
  const onTouchMove = e => {
    if (ptrStartY.current === 0) return;
    const y = e.touches[0].clientY;
    const diff = y - ptrStartY.current;
    if (diff > 0 && ptrRef.current && ptrRef.current.scrollTop === 0) {
      setPtrState(diff > 80 ? "released" : "pulling");
      if (diff > 120) ptrStartY.current = y - 120;
    }
  };
  const onTouchEnd = () => {
    if (ptrState === "released" && onRefresh) {
      onRefresh();
    }
    setPtrState("idle");
    ptrStartY.current = 0;
  };

  const toCard = s => ({
    tk:     s.ticker || s.tk,
    action: s.action || s.act,
    style:  (s.style||"swing").toUpperCase(),
    conf:   Math.round(s.confidence || s.conf || 0),
    head:   s.headline || s.head,
    entry:  s.entry,
    stop:   s.stop,
    target: s.target,
    time:   (s.ts || s.time || "").slice(0, 5),
    co:     s.company || s.co,
    price:  s.price,
    ch:     s.change || s.ch || 0,
    chPct:  s.changePct || s.chPct || 0,
    deliverable:    s.deliverable !== false,
    deliveryStatus: s.deliveryStatus || null,
    raw:    s,
  });

  return (
    <>
      <MStatusBar/>
      <div className="m-top">
        <span className="brand" style={{ display:"inline-flex", alignItems:"center", gap:8 }}>
          <svg width="22" height="22" viewBox="0 0 32 32" fill="none" stroke="var(--accent)" strokeWidth="3.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ flex:"none" }}>
            <path d="M21.4 11.2c0-3.4-4.1-4.8-7.7-3.5-3.3 1.2-3.5 5-.2 6.4l3.6 1.5c3.3 1.4 3.1 5.2-.2 6.5-3.6 1.3-7.7-.1-7.7-3.6"/>
            <path d="M18.6 13.4 25.3 6.7"/>
            <path d="M20.4 6.4 25.6 6.4 25.6 11.6"/>
          </svg>
          <span style={{ fontFamily:"var(--mono, monospace)", fontWeight:700, fontSize:14, letterSpacing:"0.06em", color:"var(--text, #e6edf7)" }}>SIGNAL<span style={{ color:"var(--accent)" }}>.</span>TRADE</span>
        </span>
        <span className="live">LIVE · {signals.length}</span>
        <span className="ico" onClick={onRefresh} role="button" tabIndex={0} title="Refresh" style={{ opacity: loading ? 0.5 : 1 }}><MIcon name="refresh" size={18}/></span>
      </div>
      {demo && (
        <div style={{ padding:"6px 16px", background:"var(--warn-soft)", borderBottom:"1px solid color-mix(in oklch, var(--warn) 30%, transparent)", fontSize:11, color:"var(--warn)", display:"flex", alignItems:"center", gap:6 }}>
          <span style={{ width:6, height:6, borderRadius:"50%", background:"var(--warn)" }}/>
          Demo data · connect to server for live signals
        </div>
      )}
      <div className="m-style-strip">
        {[["all","ALL"],["buy","BUY ONLY"],["high","≥70% CONF"]].map(([k,l]) => (
          <span key={k} className={`m-pill ${filter===k?"on":""}`} onClick={() => setFilter(k)} onKeyDown={onKeyActivate(() => setFilter(k))} role="button" tabIndex={0}>{l}</span>
        ))}
      </div>
      {ptrState !== "idle" && (
        <div style={{ textAlign:"center", padding:"8px 0", color:"var(--text-faint)", fontSize:11, fontFamily:"var(--mono)" }}>
          {ptrState === "released" ? "Release to refresh…" : "Pull to refresh…"}
        </div>
      )}
      <div className="m-feed" ref={ptrRef}
        onTouchStart={onTouchStart} onTouchMove={onTouchMove} onTouchEnd={onTouchEnd}>
        {loading && items.length === 0 && (
          <div style={{ textAlign:"center", padding:"60px 20px", color:"var(--text-faint)", fontSize:13 }}>Loading signals…</div>
        )}
        {items.map((s, i) => {
          const c = toCard(s);
          const undeliv = c.deliverable === false;
          const showDivider = undeliv && (i === 0 || (items[i - 1] && items[i - 1].deliverable !== false));
          return (
            <React.Fragment key={i}>
            {showDivider && (
              <div style={{ display:"flex", alignItems:"center", gap:8, padding:"10px 16px 4px",
                fontSize:10, fontWeight:700, color:"var(--text-faint)", letterSpacing:"0.1em" }}>
                <span style={{ flex:"none" }}>BELOW DELIVERY THRESHOLD</span>
                <span style={{ flex:1, height:1, background:"var(--line)" }}/>
              </div>
            )}
            <div className={`m-card ${c.action}`} onClick={() => onSelect && onSelect(c)} role="button" tabIndex={0}
              style={undeliv ? { opacity:0.7, borderLeft:"2px solid rgba(120,120,120,0.45)",
                background:"repeating-linear-gradient(135deg, rgba(120,120,120,0.05) 0 8px, transparent 8px 16px)" } : undefined}>
              <div className="m-card-top">
                <span className={`m-verb ${c.action}`}>{c.action}</span>
                <span className="m-tk">{c.tk}</span>
                <span className={`m-style-badge ${c.style.toLowerCase()}`}>{c.style}</span>
                {c.deliverable === false && (
                  <span title={c.deliveryStatus || "Below delivery threshold"}
                    style={{ fontSize:9, fontWeight:700, color:"var(--text-dim)",
                      background:"rgba(120,120,120,0.16)", border:"1px solid rgba(120,120,120,0.3)",
                      borderRadius:3, padding:"1px 4px", letterSpacing:"0.04em" }}>{deliveryLabel(c.deliveryStatus, true)}</span>
                )}
                <span className="m-conf">{c.conf}%</span>
              </div>
              <div className="m-card-head">{c.head}</div>
              <div className="m-card-bot">
                {c.entry ? (
                  <>
                    <span className="m-trade-pill"><span className="l">ENTRY</span>${c.entry}</span>
                    <span className="m-trade-pill s"><span className="l">STOP</span>${c.stop}</span>
                    <span className="m-trade-pill p"><span className="l">TGT</span>${c.target}</span>
                  </>
                ) : (
                  <span className="m-trade-pill" style={{ color:"var(--warn)" }}>No trade plan — wait</span>
                )}
                <span className="m-time">{c.time}</span>
              </div>
            </div>
            </React.Fragment>
          );
        })}
        {items.length === 0 && (
          <div style={{ textAlign:"center", padding:"60px 20px", color:"var(--text-faint)", fontSize:13 }}>
            No signals match this filter.
          </div>
        )}
      </div>
    </>
  );
}

// ── Detail screen ────────────────────────────────────────────────────────────
function DetailScreen({ signal, onBack, onSend, onPaperTrade }) {
  const s = signal;
  const up = (s.ch||0) >= 0;
  const rationale = s.raw?.rationale || [];
  const [sendState, setSendState] = useState("idle");
  const [paperState, setPaperState] = useState("idle");

  const handleSend = async () => {
    if (sendState !== "idle") return;
    setSendState("sending");
    try {
      await onSend?.();
      setSendState("sent");
      setTimeout(() => setSendState("idle"), 2000);
    } catch {
      setSendState("idle");
    }
  };

  const handlePaper = async () => {
    if (paperState !== "idle") return;
    setPaperState("placing");
    try {
      await onPaperTrade?.();
      setPaperState("placed");
      setTimeout(() => setPaperState("idle"), 2000);
    } catch {
      setPaperState("idle");
    }
  };

  return (
    <>
      <MStatusBar/>
      <div className="m-top">
        <span className="ico" onClick={onBack} style={{ cursor:"pointer" }} role="button" tabIndex={0}><MIcon name="chevl" size={18}/></span>
        <span className="brand" style={{ marginLeft:0 }}>{s.tk}</span>
        <span style={{ marginLeft:"auto" }} className="ico"><MIcon name="bell" size={18}/></span>
      </div>
      <div className="m-feed" style={{ padding:0 }}>
        <div className="m-detail-hero">
          <div className="m-detail-row">
            <span className={`m-verb ${s.action}`} style={{ fontSize:11, padding:"4px 8px" }}>{s.action}</span>
            <div style={{ minWidth:0 }}>
              <div className="m-detail-tk">{s.tk}</div>
              <div className="m-detail-co">{s.co}</div>
            </div>
            <div style={{ marginLeft:"auto", textAlign:"right" }}>
              <div className="m-detail-px">${Number(s.price||0).toFixed(2)}</div>
              <div className={`m-detail-ch ${up?"up":"down"}`}>{up?"+":""}{Number(s.ch||0).toFixed(2)} ({up?"+":""}{Number(s.chPct||0).toFixed(2)}%)</div>
            </div>
          </div>
          <div className="m-meta-row">
            <div className="m-meta"><span className="l">CONF</span><span className="v" style={{ color:"var(--accent)" }}>{s.conf}%</span></div>
            <div className="m-meta"><span className="l">R:R</span><span className="v">{s.raw?.rr || "—"}</span></div>
            <div className="m-meta"><span className="l">SENTIMENT</span><span className="v" style={{ color:"var(--up)" }}>{s.raw?.sentiment != null ? `${s.raw.sentiment >= 0 ? "+" : ""}${Number(s.raw.sentiment).toFixed(2)}` : "—"}</span></div>
            <div className="m-meta" style={{ marginLeft:"auto" }}><span className="l">STYLE</span><span className="v">{s.style}</span></div>
          </div>
          {s.deliverable === false && (
            <div style={{ display:"flex", gap:6, alignItems:"baseline", fontSize:12, lineHeight:1.4,
              color:"var(--text-dim)", background:"rgba(120,120,120,0.12)",
              border:"1px solid rgba(120,120,120,0.25)", borderRadius:6, padding:"7px 10px", marginTop:10 }}>
              <strong style={{ whiteSpace:"nowrap" }}>{deliveryLabel(s.deliveryStatus)}</strong>
              <span>{s.deliveryStatus || "below the delivery threshold"} — shown for context; no alert is sent.</span>
            </div>
          )}
        </div>

        <div className="m-plain">
          <span className="ico">i</span>
          <strong>In plain English:</strong> {s.action === "BUY" ? "Price likely to rise" : "Price likely to fall"}. The system is <strong>{s.conf}%</strong> confident.{s.entry ? <> Buy near <strong>${s.entry}</strong>, stop at <strong>${s.stop}</strong>, target <strong>${s.target}</strong>.</> : " No trade plan yet."}
        </div>

        {s.entry && (
          <div className="m-section">
            <div className="m-section-title">Trade plan</div>
            <div className="m-trade-grid">
              <div className="m-trade-card"><div className="l">Buy at</div><div className="v">${s.entry}</div></div>
              <div className="m-trade-card"><div className="l">Cut loss</div><div className="v down">${s.stop}</div></div>
              <div className="m-trade-card"><div className="l">Take profit</div><div className="v up">${s.target}</div></div>
            </div>
          </div>
        )}

        {rationale.length > 0 && (
          <div className="m-section" style={{ paddingBottom:16 }}>
            <div className="m-section-title">Why · {rationale.length} signals agree</div>
            <div className="m-rationale-list">
              {rationale.slice(0, 4).map((r, i) => (
                <div key={i} className="m-rationale-item">
                  <span className="src">{r.src}</span>
                  <h5>{r.head}</h5>
                  <p>{r.body}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      <div className="m-action-row">
        <button className="m-btn primary" onClick={handleSend} disabled={sendState !== "idle"}>
          <MIcon name="send" size={14}/> &nbsp;{sendState === "sending" ? "Sending…" : sendState === "sent" ? "Sent ✓" : "Send to Telegram"}
        </button>
        <button className="m-btn" onClick={handlePaper} disabled={paperState !== "idle"}>
          {paperState === "placing" ? "Placing…" : paperState === "placed" ? "Placed ✓" : "Paper trade"}
        </button>
      </div>
    </>
  );
}

// ── Portfolio tabs ───────────────────────────────────────────────────────────
function PortfolioTabs({ active, onChange }) {
  const tabs = [
    { k:"equity",  l:"Equity" },
    { k:"options", l:"Options" },
    { k:"cot",     l:"COT Engine" },
  ];
  return (
    <div className="m-pf-tabs">
      {tabs.map(t => (
        <button
          key={t.k}
          className={`m-pf-tab ${active === t.k ? "on" : ""}`}
          onClick={() => onChange(t.k)}
        >{t.l}</button>
      ))}
    </div>
  );
}

// ── Portfolio screen ─────────────────────────────────────────────────────────
function PortfolioScreen({ positions, demo, cotAccount, cotPositions, cotDemo = true }) {
  const [pfTab, setPfTab] = useState("equity");
  const equity = positions.reduce((s, p) => s + (p.last || 0) * Math.abs(p.shares || p.qty || 0), 0);
  const totalPnl = positions.reduce((s, p) => s + (p.pnl || 0), 0);
  const cotPos = cotPositions || [];
  const cotEquity = cotAccount ? parseFloat(cotAccount.equity) : null;
  const cotLastEquity = cotAccount ? parseFloat(cotAccount.last_equity) : null;
  const cotDayPl = Number.isFinite(cotEquity) && Number.isFinite(cotLastEquity) ? cotEquity - cotLastEquity : null;
  const cotDayPlPct = cotDayPl != null && cotLastEquity ? (cotDayPl / cotLastEquity) * 100 : null;
  return (
    <>
      <MStatusBar/>
      <div className="m-top">
        <span className="brand"><span className="d"></span>PAPER PORTFOLIO</span>
        <span className="live" style={{ color:"var(--info)" }}>SIM</span>
        <span className="ico"><MIcon name="settings" size={18}/></span>
      </div>
      {((pfTab === "equity" && demo) || (pfTab === "cot" && cotDemo)) && (
        <div style={{ padding:"6px 16px", background:"var(--warn-soft)", borderBottom:"1px solid color-mix(in oklch, var(--warn) 30%, transparent)", fontSize:11, color:"var(--warn)", display:"flex", alignItems:"center", gap:6 }}>
          <span style={{ width:6, height:6, borderRadius:"50%", background:"var(--warn)" }}/>
          {pfTab === "cot" ? "COT Engine not connected · demo positions shown" : "Demo positions · connect to server for real P&L"}
        </div>
      )}
      <div className="m-feed" style={{ padding:0 }}>
        <div className="m-pf-hero">
          <div className="m-pf-eyebrow">Simulated trading account</div>
          <PortfolioTabs active={pfTab} onChange={setPfTab} />
          {pfTab === "equity" && (
            <>
              <div className="m-pf-bal">${equity > 0 ? equity.toLocaleString("en-US", { minimumFractionDigits:2, maximumFractionDigits:2 }) : "—"}</div>
              {totalPnl !== 0 && <div className="m-pf-ch" style={{ color: totalPnl >= 0 ? "var(--up)" : "var(--down)" }}>{totalPnl >= 0 ? "+" : ""}${Math.abs(totalPnl).toFixed(2)} open P&L</div>}
              <div className="m-pf-stats">
                <div className="m-pf-stat"><div className="l">Positions</div><div className="v">{positions.length}</div></div>
                <div className="m-pf-stat"><div className="l">Open P&L</div><div className="v" style={{ color:totalPnl >= 0 ? "var(--up)" : "var(--down)" }}>{totalPnl >= 0 ? "+" : ""}${Math.abs(totalPnl).toFixed(0)}</div></div>
                <div className="m-pf-stat"><div className="l">Status</div><div className="v" style={{ color:"var(--info)" }}>PAPER</div></div>
              </div>
            </>
          )}
          {pfTab === "options" && (
            <>
              <div className="m-pf-bal">$1,000,000.00</div>
              <div className="m-pf-ch">Options overlay backtest</div>
              <div className="m-pf-stats">
                <div className="m-pf-stat"><div className="l">Net Sharpe</div><div className="v" style={{ color:"var(--up)" }}>{OPTIONS_SUMMARY_MOCK.netSharpe}</div></div>
                <div className="m-pf-stat"><div className="l">Ann. return</div><div className="v">{OPTIONS_SUMMARY_MOCK.annReturn}%</div></div>
                <div className="m-pf-stat"><div className="l">Max DD</div><div className="v" style={{ color:"var(--down)" }}>{OPTIONS_SUMMARY_MOCK.maxDD}%</div></div>
              </div>
            </>
          )}
          {pfTab === "cot" && (
            <>
              <div className="m-pf-bal">{cotDemo || cotEquity == null ? "—" : `$${cotEquity.toLocaleString("en-US", { minimumFractionDigits:2, maximumFractionDigits:2 })}`}</div>
              <div className="m-pf-ch" style={cotDayPl != null ? { color: cotDayPl >= 0 ? "var(--up)" : "var(--down)" } : undefined}>
                {cotDemo ? "Connect COT Alpaca keys for live data" : cotDayPl == null ? "—" : `${cotDayPl >= 0 ? "+" : ""}$${cotDayPl.toFixed(2)} (${cotDayPlPct >= 0 ? "+" : ""}${cotDayPlPct.toFixed(2)}%) today`}
              </div>
              <div className="m-pf-stats">
                <div className="m-pf-stat"><div className="l">Positions</div><div className="v">{cotDemo ? "—" : cotPos.length}</div></div>
                <div className="m-pf-stat"><div className="l">Day P&L</div><div className="v" style={cotDayPl != null ? { color: cotDayPl >= 0 ? "var(--up)" : "var(--down)" } : undefined}>{cotDemo || cotDayPl == null ? "—" : `${cotDayPl >= 0 ? "+" : ""}$${cotDayPl.toFixed(0)}`}</div></div>
                <div className="m-pf-stat"><div className="l">Status</div><div className="v" style={{ color:"var(--info)" }}>{cotDemo ? "N/A" : "PAPER"}</div></div>
              </div>
            </>
          )}
        </div>
        {pfTab === "equity" && (
          <>
            <div className="m-list-head">Open positions · {positions.length}</div>
            {positions.map((p, i) => {
              const tk   = p.symbol || p.tk;
              const sh   = p.qty || p.shares || 0;
              const last = p.current_price || p.last || 0;
              const avg  = p.avg_entry_price || p.avg || 0;
              const pnl  = p.unrealized_pl != null ? parseFloat(p.unrealized_pl) : (p.pnl || 0);
              const pct  = p.unrealized_plpc != null ? parseFloat(p.unrealized_plpc) * 100 : (p.pct || 0);
              const spark = p.spark || [40,42,44,43,46,45,48,50];
              return (
                <div key={i} className="m-pos-row">
                  <div className="m-pos-tk">{tk}</div>
                  <div className="m-pos-info">
                    <div className="m-pos-shares">{Math.abs(sh)} sh · avg ${Number(avg).toFixed(2)}</div>
                    <div className="m-pos-px">${Number(last).toFixed(2)}</div>
                  </div>
                  <Sparkline data={spark} color={pnl >= 0 ? "var(--up)" : "var(--down)"}/>
                  <div className={`m-pos-pnl ${pnl >= 0 ? "up" : "down"}`}>
                    <div className="v">{pnl >= 0 ? "+" : "−"}${Math.abs(pnl).toFixed(0)}</div>
                    <div className="pct">{pnl >= 0 ? "+" : "−"}{Math.abs(pct).toFixed(2)}%</div>
                  </div>
                </div>
              );
            })}
            {positions.length === 0 && <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:13 }}>No open positions.</div>}
          </>
        )}
        {pfTab === "options" && (
          <>
            <div className="m-list-head">Strategy · {OPTIONS_SUMMARY_MOCK.label}</div>
            <div style={{ padding:"14px 16px", borderBottom:"1px solid var(--line-soft)" }}>
              <div style={{ fontSize:13, color:"var(--text-dim)", lineHeight:1.5 }}>
                Options overlay backtest on the COT + carry + diversifier pack ({OPTIONS_SUMMARY_MOCK.n} instruments, {OPTIONS_SUMMARY_MOCK.since}–2026).
              </div>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12, marginTop:14 }}>
                <div className="m-trade-card"><div className="l">Ann. vol</div><div className="v">{OPTIONS_SUMMARY_MOCK.annVol}%</div></div>
                <div className="m-trade-card"><div className="l">Calmar</div><div className="v">{OPTIONS_SUMMARY_MOCK.calmar}</div></div>
              </div>
            </div>
          </>
        )}
        {pfTab === "cot" && (
          <>
            {cotDemo ? (
              <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:13 }}>
                COT Engine keys not configured — no live data to show.
              </div>
            ) : (
              <>
                <div className="m-list-head">Open positions · {cotPos.length}</div>
                {cotPos.map((p, i) => {
                  const tk = p.symbol || p.ticker;
                  const side = p.side || (parseFloat(p.qty) < 0 ? "short" : "long");
                  const notional = Math.abs(parseFloat(p.market_value ?? p.qty * (p.current_price || p.avg_entry_price || 0)) || 0);
                  const pnl = parseFloat(p.unrealized_pl || 0);
                  return (
                    <div key={i} className="m-pos-row">
                      <div className="m-pos-tk">{tk}</div>
                      <div className="m-pos-info">
                        <div className="m-pos-shares">{side} · {Math.abs(parseFloat(p.qty) || 0)} units</div>
                        <div className="m-pos-px">${notional.toLocaleString()} notional</div>
                      </div>
                      <Sparkline data={p.spark || [40,42,41,43,44,45,46,47]} color={pnl >= 0 ? "var(--up)" : "var(--down)"}/>
                      <div className={`m-pos-pnl ${pnl >= 0 ? "up" : "down"}`}>
                        <div className="v">{pnl >= 0 ? "+" : "−"}${Math.abs(pnl).toFixed(0)}</div>
                        <div className="pct">{side === "long" ? "Long" : "Short"}</div>
                      </div>
                    </div>
                  );
                })}
                {cotPos.length === 0 && <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:13 }}>No open positions.</div>}
              </>
            )}
          </>
        )}
        <div style={{ padding:16 }}><button className="m-btn" style={{ width:"100%" }}>View closed trades →</button></div>
      </div>
    </>
  );
}

// ── Record screen ────────────────────────────────────────────────────────────
function RecordScreen({ stats }) {
  const o = stats?.overall;
  const fmt = (v, d=2) => v == null ? "—" : Number(v).toFixed(d);
  const pctFmt = v => v == null ? "—" : `${v >= 0 ? "+" : ""}${fmt(v)}%`;
  return (
    <>
      <MStatusBar/>
      <div className="m-top">
        <span className="brand"><span className="d"></span>TRACK RECORD</span>
        <span className="live">{stats?.total_signals || 0} SIG</span>
      </div>
      <div className="m-feed">
        {/* Summary cards */}
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:8, marginBottom:12 }}>
          {[
            ["Win Rate",   o?.win_rate != null ? `${fmt(o.win_rate, 1)}%` : "—", o?.win_rate >= 60 ? "var(--up)" : "var(--warn)"],
            ["Avg Return", pctFmt(o?.avg_return), o?.avg_return >= 0 ? "var(--up)" : "var(--down)"],
            ["Sharpe",     o?.sharpe != null ? fmt(o.sharpe) : "—", o?.sharpe >= 1 ? "var(--up)" : "var(--text)"],
            ["Signals",    stats?.total_signals || "—", "var(--accent)"],
          ].map(([l,v,c]) => (
            <div key={l} style={{ background:"var(--bg-1)", border:"1px solid var(--line)", borderRadius:10, padding:"12px 14px" }}>
              <div style={{ fontFamily:"var(--mono)", fontSize:9, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:4 }}>{l}</div>
              <div style={{ fontFamily:"var(--mono)", fontSize:22, fontWeight:700, color:c }}>{v}</div>
            </div>
          ))}
        </div>

        {/* By ticker */}
        {(stats?.top_tickers||[]).slice(0,8).map((t, i) => (
          <div key={i} style={{ display:"flex", alignItems:"center", gap:10, padding:"11px 14px", background:"var(--bg-1)", border:"1px solid var(--line)", borderRadius:8, marginBottom:6 }}>
            <span style={{ fontFamily:"var(--mono)", fontWeight:700, fontSize:13, minWidth:52 }}>{t.ticker}</span>
            <div style={{ flex:1 }}>
              <div style={{ height:3, background:"var(--line)", borderRadius:2, overflow:"hidden" }}>
                <div style={{ height:"100%", borderRadius:2, width:`${t.win_rate||0}%`, background: t.win_rate >= 60 ? "var(--up)" : "var(--warn)" }}/>
              </div>
            </div>
            <span style={{ fontFamily:"var(--mono)", fontSize:11, color: t.win_rate >= 60 ? "var(--up)" : "var(--warn)", minWidth:36, textAlign:"right" }}>{t.win_rate?.toFixed(0)}%</span>
            <span style={{ fontFamily:"var(--mono)", fontSize:11, color: t.avg_return >= 0 ? "var(--up)" : "var(--down)", minWidth:48, textAlign:"right" }}>{pctFmt(t.avg_return)}</span>
          </div>
        ))}
        {(!stats || !o) && <div style={{ padding:"60px 0", textAlign:"center", color:"var(--text-faint)", fontSize:13 }}>Loading track record…</div>}
      </div>
    </>
  );
}

// ── Account screen ───────────────────────────────────────────────────────────
function AccountScreen({ user }) {
  const tier = user?.subscription_tier || "free";
  const initials = (user?.full_name || user?.email || "?")[0].toUpperCase();
  return (
    <>
      <MStatusBar/>
      <div className="m-top">
        <span className="brand"><span className="d"></span>ACCOUNT</span>
        <span style={{ marginLeft:"auto" }} className="ico"><MIcon name="settings" size={18}/></span>
      </div>
      <div className="m-feed" style={{ padding:0 }}>
        <div className="m-acc-hero">
          <div className="m-acc-row">
            <div className="m-avatar">{initials}</div>
            <div style={{ flex:1 }}>
              <div className="m-acc-name">{user?.full_name || "—"}</div>
              <div className="m-acc-email">{user?.email || "—"}</div>
            </div>
            <span className="m-tier-badge">{tier.toUpperCase()}{user?.is_owner ? " ★" : ""}</span>
          </div>
        </div>
        <div className="m-list">
          <div className="m-list-head">Subscription</div>
          <div className="m-list-item">
            <div className="li-ico"><MIcon name="money" size={16}/></div>
            <div className="li-text">
              <div className="li-title">{tier === "elite" ? "Elite · $99/mo" : tier === "pro" ? "Pro · $49/mo" : tier === "basic" ? "Basic · $19/mo" : "Free"}</div>
              <div className="li-sub">{user?.subscription_status === "active" ? `Renews ${user?.subscription_period_end ? new Date(user.subscription_period_end).toLocaleDateString() : "—"}` : user?.subscription_status || "Inactive"}</div>
            </div>
            <MIcon name="chev" size={16}/>
          </div>
        </div>
        <div className="m-list">
          <div className="m-list-head">Delivery</div>
          <div className="m-list-item">
            <div className="li-ico"><MIcon name="send" size={16}/></div>
            <div className="li-text">
              <div className="li-title">Telegram</div>
              <div className="li-sub">{user?.telegram_linked ? "Connected" : "Not linked — open Account on desktop"}</div>
            </div>
            <span className="li-val" style={{ color: user?.telegram_linked ? "var(--up)" : "var(--text-faint)" }}>{user?.telegram_linked ? "ON" : "OFF"}</span>
          </div>
          <div className="m-list-item">
            <div className="li-ico"><MIcon name="bell" size={16}/></div>
            <div className="li-text">
              <div className="li-title">Push notifications</div>
              <div className="li-sub">Browser push for high-confidence signals</div>
            </div>
            <div className="m-toggle on"></div>
          </div>
        </div>
        <div className="m-list">
          <div className="m-list-head">Legal</div>
          <div className="m-list-item">
            <div className="li-ico"><MIcon name="shield" size={16}/></div>
            <div className="li-text">
              <div className="li-title">Terms of Service</div>
            </div>
            <MIcon name="chev" size={16}/>
          </div>
          <div className="m-list-item">
            <div className="li-ico"><MIcon name="shield" size={16}/></div>
            <div className="li-text">
              <div className="li-title">Privacy Policy</div>
            </div>
            <MIcon name="chev" size={16}/>
          </div>
        </div>
        <div style={{ padding:"20px 16px 30px", textAlign:"center" }}>
          <button className="m-btn" style={{ width:"100%", color:"var(--down)", borderColor:"var(--down-soft)" }}
            onClick={() => { clearToken(); window.location.href = "/login"; }}>
            Sign out
          </button>
          <div style={{ marginTop:14, fontSize:10, color:"var(--text-faint)", lineHeight:1.5 }}>
            <strong style={{ color:"var(--warn)" }}>NOT FINANCIAL ADVICE.</strong> Educational tool only.<br/>Past performance does not predict future results.
          </div>
        </div>
      </div>
    </>
  );
}

// ── Onboard screen ───────────────────────────────────────────────────────────
function OnboardScreen({ onLogin, onSignup }) {
  return (
    <div className="m-app">
      <MStatusBar/>
      <div style={{ flex:1, display:"flex", flexDirection:"column", padding:"60px 28px 24px", textAlign:"center" }}>
        <div style={{ fontFamily:"var(--mono)", fontSize:11, letterSpacing:"0.2em", color:"var(--accent)", marginBottom:14 }}>SIGNAL.TRADE</div>
        <div style={{ fontSize:44, lineHeight:1.05, color:"var(--text)", letterSpacing:"-0.02em", fontWeight:800 }}>
          Quant signals.<br/><span style={{ color:"var(--accent)" }}>Plain English.</span>
        </div>
        <div style={{ marginTop:18, fontSize:14, color:"var(--text-dim)", lineHeight:1.5 }}>
          Dozens of signals across technical, options, institutional, and macro data — fused into one calibrated confidence score and pushed to Telegram.
        </div>
        <div style={{ flex:1 }}/>
        <div style={{ display:"grid", gap:10, marginBottom:14, textAlign:"left" }}>
          {[["📊","Multi-factor market signals"],["🎯","Entry, stop & target on every BUY/SELL"],["📱","Telegram + Web Push, your hours"]].map((f, i) => (
            <div key={i} style={{ display:"flex", gap:12, alignItems:"center", padding:"12px 14px", background:"var(--bg-2)", borderRadius:12, border:"1px solid var(--line)" }}>
              <span style={{ fontSize:18 }}>{f[0]}</span>
              <span style={{ fontSize:13, color:"var(--text)" }}>{f[1]}</span>
            </div>
          ))}
        </div>
        <button className="m-btn primary" style={{ width:"100%", padding:14, fontSize:14, fontWeight:600, marginBottom:8 }} onClick={onSignup}>Create free account</button>
        <button className="m-btn" style={{ width:"100%", padding:12, fontSize:13, border:"none", background:"transparent", color:"var(--text-dim)" }} onClick={onLogin}>I already have an account</button>
        <div style={{ marginTop:14, fontSize:9, color:"var(--text-faint)", lineHeight:1.4 }}>Not financial advice · Educational signals only</div>
      </div>
    </div>
  );
}

// ── Root mobile app ──────────────────────────────────────────────────────────
function MobileApp() {
  const [tab,       setTab]       = useState("feed");
  const [signals,   setSignals]   = useState([]);
  const [positions, setPositions] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [signalsDemo, setSignalsDemo] = useState(false);
  const [positionsDemo, setPositionsDemo] = useState(false);
  const [watchlistDemo, setWatchlistDemo] = useState(false);
  const [cotAccount, setCotAccount] = useState(null);
  const [cotPositions, setCotPositions] = useState([]);
  const [cotDemo, setCotDemo] = useState(true);
  const [dataLoading, setDataLoading] = useState(false);
  const [stats,     setStats]     = useState(null);
  const [user,      setUser]      = useState(null);
  const [authReady, setAuthReady] = useState(false);
  const [selected,  setSelected]  = useState(null);
  const [now,       setNow]       = useState(() => new Date());

  const loadData = async (opts = {}) => {
    if (!user) return;
    const ctrl = opts.signal ? { signal: opts.signal } : {};
    setDataLoading(true);
    try {
      const [sigs, pos, wl] = await Promise.all([
        apiFetch("/api/signals", ctrl),
        apiFetch("/api/paper/positions", ctrl),
        apiFetch("/api/watchlist", ctrl),
      ]);
      if (sigs && Array.isArray(sigs) && sigs.length > 0) {
        setSignals(sigs);
        setSignalsDemo(false);
      } else {
        setSignals(MOBILE_SIGNALS_MOCK);
        setSignalsDemo(true);
      }
      if (pos && Array.isArray(pos) && pos.length > 0) {
        setPositions(pos);
        setPositionsDemo(false);
      } else {
        setPositions(POSITIONS_MOCK);
        setPositionsDemo(true);
      }
      if (wl && Array.isArray(wl) && wl.length > 0) {
        setWatchlist(wl);
        setWatchlistDemo(false);
      } else {
        setWatchlist(WATCH_MOCK);
        setWatchlistDemo(true);
      }
    } catch {
      setSignals(MOBILE_SIGNALS_MOCK);
      setPositions(POSITIONS_MOCK);
      setWatchlist(WATCH_MOCK);
      setSignalsDemo(true);
      setPositionsDemo(true);
      setWatchlistDemo(true);
    } finally {
      setDataLoading(false);
    }
    apiFetch("/api/public/track-record", ctrl).then(d => { if (d && !d.no_data) setStats(d); }).catch(() => {});

    // COT/signal-engine shadow book — separate Alpaca keys, may be unconfigured
    // (403) for a given deployment. Only show real numbers; never fall back to
    // fabricated "live" figures — an empty/unconfigured account renders an
    // honest "not connected" state instead of invented P&L.
    Promise.all([
      apiFetch("/api/paper/cot/account", ctrl),
      apiFetch("/api/paper/cot/positions", ctrl),
    ]).then(([acct, pos]) => {
      if (acct && !acct.detail) {
        setCotAccount(acct);
        setCotPositions(Array.isArray(pos) ? pos : []);
        setCotDemo(false);
      } else {
        setCotAccount(null);
        setCotPositions([]);
        setCotDemo(true);
      }
    }).catch(() => { setCotAccount(null); setCotPositions([]); setCotDemo(true); });
  };

  // Auth
  useEffect(() => {
    const token = getToken();
    if (!token) {
      _tryRefresh().then(ok => {
        if (ok) {
          authFetch("/api/auth/me")
            .then(r => r.ok ? r.json() : null)
            .then(u => { if (u) setUser(u); else clearToken(); })
            .catch(() => {})
            .finally(() => setAuthReady(true));
        } else {
          setAuthReady(true);
        }
      });
      return;
    }
    const ctrl = new AbortController();
    authFetch("/api/auth/me", { signal: ctrl.signal })
      .then(r => r.ok ? r.json() : null)
      .then(u => { if (u) setUser(u); else clearToken(); })
      .catch(() => {})
      .finally(() => setAuthReady(true));
    return () => ctrl.abort();
  }, []);

  // Data
  useEffect(() => {
    if (!user) return;
    const ctrl = new AbortController();
    loadData({ signal: ctrl.signal });
    return () => ctrl.abort();
  }, [user]);

  // Clock
  useEffect(() => { const id = setInterval(() => setNow(new Date()), 60000); return () => clearInterval(id); }, []);

  if (!authReady) return <div style={{ display:"flex", alignItems:"center", justifyContent:"center", height:"100%", background:"var(--bg-0)", color:"var(--text-faint)", fontFamily:"var(--mono)", fontSize:13 }}>Loading…</div>;

  if (!user) return <OnboardScreen onLogin={() => window.location.href="/login?next=/mobile"} onSignup={() => window.location.href="/signup"}/>;

  const refresh = () => loadData();

  const sendSignal = async (s) => {
    if (s.raw?.id) {
      await mFetch(`/api/signals/${s.raw.id}/send`);
    }
  };

  const paperTrade = async (s) => {
    if (!s?.tk) return;
    await authFetch("/api/paper/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        symbol: s.tk,
        qty: 1,
        side: s.action === "BUY" ? "buy" : "sell",
        type: "market",
        time_in_force: "day",
      }),
    });
  };

  const screenContent = () => {
    if (selected && tab === "feed") return <DetailScreen signal={selected} onBack={() => setSelected(null)} onSend={() => sendSignal(selected)} onPaperTrade={() => paperTrade(selected)}/>;
    switch (tab) {
      case "feed":      return <FeedScreen signals={signals} onSelect={s => setSelected(s)} loading={dataLoading} demo={signalsDemo} onRefresh={refresh}/>;
      case "portfolio": return <PortfolioScreen positions={positions} demo={positionsDemo} cotAccount={cotAccount} cotPositions={cotPositions} cotDemo={cotDemo}/>;
      case "record":    return <RecordScreen stats={stats}/>;
      case "account":   return <AccountScreen user={user}/>;
      case "watch":     return <WatchlistScreen tickers={watchlist} demo={watchlistDemo} onRefresh={refresh}/>;
      default:          return (
        <div style={{ flex:1, display:"flex", alignItems:"center", justifyContent:"center", color:"var(--text-faint)", fontSize:13 }}>
          Coming soon
        </div>
      );
    }
  };

  return (
    <div className="m-app">
      <div style={{ flex:1, overflow:"hidden", display:"flex", flexDirection:"column" }}>
        {screenContent()}
      </div>
      {!selected && <MTabBar active={tab} setTab={setTab}/>}
    </div>
  );
}

// ── Watchlist screen ─────────────────────────────────────────────────────────
const WATCH_MOCK = [
  { tk:"NVDA",  co:"NVIDIA",      price:1248.40, ch:2.64,  sigs:3, alert:true  },
  { tk:"AAPL",  co:"Apple",       price:179.20,  ch:1.18,  sigs:1, alert:true  },
  { tk:"MSFT",  co:"Microsoft",   price:428.60,  ch:0.84,  sigs:0, alert:false },
  { tk:"TSLA",  co:"Tesla",       price:164.80,  ch:-2.48, sigs:2, alert:true  },
  { tk:"AMD",   co:"AMD",         price:162.50,  ch:2.43,  sigs:1, alert:true  },
  { tk:"GOOGL", co:"Alphabet",    price:178.90,  ch:0.32,  sigs:0, alert:false },
  { tk:"AMZN",  co:"Amazon",      price:195.20,  ch:-0.76, sigs:0, alert:false },
  { tk:"PLTR",  co:"Palantir",    price:28.40,   ch:4.12,  sigs:2, alert:true  },
];

function WatchlistScreen({ tickers = WATCH_MOCK, demo = false, onRefresh }) {
  const [filter, setFilter] = useState("all");
  const items = filter === "signals" ? tickers.filter(t => (t.sigs||0) > 0)
              : filter === "alerts"  ? tickers.filter(t => t.alert)
              : tickers;
  return (
    <>
      <MStatusBar/>
      <div className="m-top">
        <span style={{ fontFamily:"var(--mono)", fontWeight:700, fontSize:13, color:"var(--text)" }}>Watchlist</span>
        <span style={{ marginLeft:"auto", display:"inline-flex", gap:10, alignItems:"center" }}>
          {onRefresh && <span className="ico" onClick={onRefresh} role="button" tabIndex={0}><MIcon name="refresh" size={18}/></span>}
          <span className="ico"><MIcon name="filter" size={18}/></span>
          <span className="ico" style={{ color:"var(--accent)", fontSize:20 }}>+</span>
        </span>
      </div>
      {demo && (
        <div style={{ padding:"6px 16px", background:"var(--warn-soft)", borderBottom:"1px solid color-mix(in oklch, var(--warn) 30%, transparent)", fontSize:11, color:"var(--warn)", display:"flex", alignItems:"center", gap:6 }}>
          <span style={{ width:6, height:6, borderRadius:"50%", background:"var(--warn)"}}/>
          Demo watchlist · connect to server for live prices
        </div>
      )}
      <div style={{ padding:"0 16px 12px", display:"flex", gap:6, overflowX:"auto" }}>
        {[["all","ALL · "+tickers.length],["signals","SIGNALS"],["alerts","ALERTS"]].map(([k,l]) => (
          <span key={k} className={`m-pill ${filter===k?"on":""}`} onClick={() => setFilter(k)} onKeyDown={onKeyActivate(() => setFilter(k))} role="button" tabIndex={0}>{l}</span>
        ))}
      </div>
      <div style={{ flex:1, overflowY:"auto" }}>
        {items.map((w, i) => (
          <div key={i} style={{ display:"flex", alignItems:"center", gap:12, padding:"14px 16px", borderBottom:"1px solid var(--line)" }}>
            <div style={{ width:40, height:40, borderRadius:10, background:"var(--bg-2)", display:"grid", placeItems:"center", fontFamily:"var(--mono)", fontWeight:700, fontSize:11, color:"var(--text)" }}>
              {w.tk.slice(0,2)}
            </div>
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ display:"flex", alignItems:"center", gap:6 }}>
                <span style={{ fontFamily:"var(--mono)", fontWeight:600, fontSize:14, color:"var(--text)" }}>{w.tk}</span>
                {w.sigs > 0 && <span style={{ fontFamily:"var(--mono)", fontSize:9, padding:"2px 5px", borderRadius:4, background:"color-mix(in oklch,var(--accent) 18%,transparent)", color:"var(--accent)" }}>{w.sigs} live</span>}
                {w.alert && <span style={{ color:"var(--warn)" }}><MIcon name="bell" size={11}/></span>}
              </div>
              <div style={{ fontSize:11, color:"var(--text-dim)", marginTop:2 }}>{w.co}</div>
            </div>
            <div style={{ textAlign:"right" }}>
              <div style={{ fontFamily:"var(--mono)", fontSize:13, color:"var(--text)" }}>{w.price != null ? `$${Number(w.price).toFixed(2)}` : "—"}</div>
              <div style={{ fontFamily:"var(--mono)", fontSize:11, color: (w.change||w.ch) >= 0 ? "var(--up)" : "var(--down)", marginTop:2 }}>{w.change != null || w.ch != null ? `${(w.change||w.ch) >= 0 ? "+" : ""}${Number(w.change||w.ch).toFixed(2)}%` : ""}</div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}


// ── Paywall screen ────────────────────────────────────────────────────────────
function PaywallScreen({ onClose }) {
  const tiers = [
    { name:"Free",   price:"$0",     per:"/forever", fav:false, current:true,  cta:"Current plan",    desc:"3 signals/day, Signal Journal (resolved outcomes), market context" },
    { name:"Basic",  price:"$19",   per:"/month",   fav:true,  current:false, cta:"Start 7-day trial", desc:"Unlimited live signals, Telegram + Web Push, backtest, Excel export" },
    { name:"Pro",    price:"$49",   per:"/month",   fav:false, current:false, cta:"Upgrade to Pro",  desc:"Everything in Basic + volatility targeting, correlation matrix, weekly digest" },
    { name:"Elite",  price:"$99",   per:"/month",   fav:false, current:false, cta:"Upgrade to Elite", desc:"Everything in Pro + early access + priority delivery + API access + dedicated support" },
  ];
  return (
    <>
      <MStatusBar/>
      <div className="m-top">
        {onClose && <span className="ico" onClick={onClose} role="button" tabIndex={0}><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"><polyline points="15 6 9 12 15 18"/></svg></span>}
        <span style={{ fontFamily:"var(--mono)", fontSize:11, letterSpacing:"0.15em", color:"var(--text-dim)", marginLeft: onClose ? 0 : "auto" }}>UPGRADE</span>
      </div>
      <div style={{ flex:1, overflowY:"auto", padding:"16px 16px 20px" }}>
        <div style={{ fontSize:26, fontWeight:800, color:"var(--text)", lineHeight:1.1, letterSpacing:"-0.02em", marginBottom:8 }}>
          Unlock the full feed
        </div>
        <div style={{ fontSize:13, color:"var(--text-dim)", lineHeight:1.5, marginBottom:18 }}>
          Free shows 3 signals/day with the Signal Journal (resolved outcomes, 7-day delay). Upgrade to receive signals live.
        </div>
        <div style={{ display:"grid", gap:10 }}>
          {tiers.map((t, i) => (
            <div key={i} style={{ padding:16, borderRadius:14, background:t.fav ? "color-mix(in oklch,var(--accent) 8%,var(--bg-2))" : "var(--bg-2)", border:t.fav ? "1.5px solid var(--accent)" : "1px solid var(--line)", position:"relative" }}>
              {t.fav && <span style={{ position:"absolute", top:-8, right:12, padding:"3px 8px", borderRadius:4, background:"var(--accent)", color:"#000", fontFamily:"var(--mono)", fontSize:9, fontWeight:700, letterSpacing:"0.1em" }}>POPULAR</span>}
              <div style={{ display:"flex", alignItems:"baseline", gap:6, marginBottom:6 }}>
                <span style={{ fontWeight:600, fontSize:14, color:"var(--text)" }}>{t.name}</span>
                <span style={{ marginLeft:"auto", fontFamily:"var(--mono)", fontSize:20, fontWeight:700, color:"var(--text)" }}>{t.price}</span>
                <span style={{ fontFamily:"var(--mono)", fontSize:10, color:"var(--text-faint)" }}>{t.per}</span>
              </div>
              <div style={{ fontSize:12, color:"var(--text-dim)", lineHeight:1.45, marginBottom:10 }}>{t.desc}</div>
              <button className={t.current ? "m-btn" : "m-btn primary"} style={{ width:"100%", padding:10, fontSize:12, opacity:t.current ? 0.5 : 1 }}
                onClick={() => { if (!t.current) window.location.href = `/signup?plan=${t.name.toLowerCase()}`; }}>
                {t.cta}
              </button>
            </div>
          ))}
        </div>
        <div style={{ marginTop:18, padding:12, borderRadius:10, background:"color-mix(in oklch,var(--warn) 10%,transparent)", border:"1px solid color-mix(in oklch,var(--warn) 30%,transparent)" }}>
          <div style={{ fontSize:11, color:"var(--warn)", fontWeight:600, marginBottom:4 }}>⚠ Risk Disclosure</div>
          <div style={{ fontSize:11, color:"var(--text-dim)", lineHeight:1.45 }}>Educational signals only. Not financial advice. Past performance ≠ future results.</div>
        </div>
      </div>
    </>
  );
}

// ── Static screens for design canvas ─────────────────────────────────────────
function FeedScreen_Static()      { return <FeedScreen signals={MOBILE_SIGNALS_MOCK} onSelect={() => {}}/> }
function DetailScreen_Static()    { return <DetailScreen signal={{ tk:"NVDA", action:"BUY", style:"POSITION", conf:87, head:"Breakout above 200-DMA + CUDA license rumor", entry:1245, stop:1188, target:1385, ch:32.10, chPct:2.64, price:1248.40, co:"NVIDIA Corp", raw:{ rationale:[{ src:"13F FLOW", head:"Berkshire added 2.3M shares", body:"Q1 13F filing showed Berkshire increased NVDA position by 18%." },{ src:"OPTIONS", head:"Unusual call sweep $1300", body:"5,400 contracts at $1300C, 6× open interest." },{ src:"TECHNICAL", head:"Reclaim 200-DMA on 2× volume", body:"Closed above 200-DMA for 3rd consecutive session, RSI 58." }] } }} onBack={() => {}} onSend={() => {}}/> }
function PortfolioScreen_Static() { return <PortfolioScreen positions={POSITIONS_MOCK}/> }
function AccountScreen_Static()   { return <AccountScreen user={{ full_name:"Rohan K.", email:"rohan@gmail.com", subscription_tier:"pro", subscription_status:"active", is_owner:false, telegram_linked:true }}/> }
function OnboardScreen_Static()   { return <OnboardScreen onLogin={() => {}} onSignup={() => {}}/> }
function WatchlistScreen_Static() { return <WatchlistScreen tickers={WATCH_MOCK}/> }
function PaywallScreen_Static()   { return <PaywallScreen onClose={() => {}}/> }

if (typeof window !== 'undefined') {
  Object.assign(window, {
    MobileApp,
    FeedScreen:      FeedScreen_Static,
    DetailScreen:    DetailScreen_Static,
    PortfolioScreen: PortfolioScreen_Static,
    AccountScreen:   AccountScreen_Static,
    OnboardScreen:   OnboardScreen_Static,
    WatchlistScreen: WatchlistScreen_Static,
    PaywallScreen:   PaywallScreen_Static,
  });
}
