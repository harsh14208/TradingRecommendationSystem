/* global React */
const { useState, useEffect } = React;

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
  };
  return (
    <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      {paths[name]}
    </svg>
  );
};

function MStatusBar({ time = "9:41" }) {
  return (
    <div style={{ display:"flex", justifyContent:"space-between", padding:"6px 22px 0", fontFamily:"var(--mono)", fontSize:13, fontWeight:600 }}>
      <span>{time}</span>
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
function FeedScreen({ signals, onSelect }) {
  const [filter, setFilter] = useState("all");
  const items = filter === "all" ? signals
    : filter === "buy" ? signals.filter(s => (s.action||s.act) === "BUY")
    : signals.filter(s => (s.confidence||s.conf||0) >= 70);

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
    raw:    s,
  });

  return (
    <>
      <MStatusBar/>
      <div className="m-top">
        <span className="brand"><img src="/logo-full.png" alt="Signal.Trade" style={{ height: 65, width: "auto" }}/></span>
        <span className="live">LIVE · {signals.length}</span>
        <span className="ico"><MIcon name="filter" size={18}/></span>
      </div>
      <div className="m-style-strip">
        {[["all","ALL"],["buy","BUY ONLY"],["high","≥70% CONF"]].map(([k,l]) => (
          <span key={k} className={`m-pill ${filter===k?"on":""}`} onClick={() => setFilter(k)} role="button" tabIndex={0}>{l}</span>
        ))}
      </div>
      <div className="m-feed">
        {items.map((s, i) => {
          const c = toCard(s);
          return (
            <div key={i} className={`m-card ${c.action}`} onClick={() => onSelect && onSelect(c)} role="button" tabIndex={0}>
              <div className="m-card-top">
                <span className={`m-verb ${c.action}`}>{c.action}</span>
                <span className="m-tk">{c.tk}</span>
                <span className={`m-style-badge ${c.style.toLowerCase()}`}>{c.style}</span>
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
function DetailScreen({ signal, onBack, onSend }) {
  const s = signal;
  const up = (s.ch||0) >= 0;
  const rationale = s.raw?.rationale || [];
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
        <button className="m-btn primary" onClick={onSend}><MIcon name="send" size={14}/> &nbsp;Send to Telegram</button>
        <button className="m-btn">Paper trade</button>
      </div>
    </>
  );
}

// ── Portfolio screen ─────────────────────────────────────────────────────────
function PortfolioScreen({ positions }) {
  const equity = positions.reduce((s, p) => s + (p.last || 0) * Math.abs(p.shares || p.qty || 0), 0);
  const totalPnl = positions.reduce((s, p) => s + (p.pnl || 0), 0);
  return (
    <>
      <MStatusBar/>
      <div className="m-top">
        <span className="brand"><span className="d"></span>PAPER PORTFOLIO</span>
        <span className="live" style={{ color:"var(--info)" }}>SIM</span>
        <span className="ico"><MIcon name="settings" size={18}/></span>
      </div>
      <div className="m-feed" style={{ padding:0 }}>
        <div className="m-pf-hero">
          <div className="m-pf-eyebrow">Equity · Sim account</div>
          <div className="m-pf-bal">${equity > 0 ? equity.toLocaleString("en-US", { minimumFractionDigits:2, maximumFractionDigits:2 }) : "—"}</div>
          {totalPnl !== 0 && <div className="m-pf-ch" style={{ color: totalPnl >= 0 ? "var(--up)" : "var(--down)" }}>{totalPnl >= 0 ? "+" : ""}${Math.abs(totalPnl).toFixed(2)} open P&L</div>}
          <div className="m-pf-stats">
            <div className="m-pf-stat"><div className="l">Positions</div><div className="v">{positions.length}</div></div>
            <div className="m-pf-stat"><div className="l">Open P&L</div><div className="v" style={{ color:totalPnl >= 0 ? "var(--up)" : "var(--down)" }}>{totalPnl >= 0 ? "+" : ""}${Math.abs(totalPnl).toFixed(0)}</div></div>
            <div className="m-pf-stat"><div className="l">Status</div><div className="v" style={{ color:"var(--info)" }}>PAPER</div></div>
          </div>
        </div>
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
              <Sparkline data={spark} color={pnl >= 0 ? "#10b981" : "#ef4444"}/>
              <div className={`m-pos-pnl ${pnl >= 0 ? "up" : "down"}`}>
                <div className="v">{pnl >= 0 ? "+" : "−"}${Math.abs(pnl).toFixed(0)}</div>
                <div className="pct">{pnl >= 0 ? "+" : "−"}{Math.abs(pct).toFixed(2)}%</div>
              </div>
            </div>
          );
        })}
        {positions.length === 0 && <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:13 }}>No open positions.</div>}
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
              <div className="li-title">{tier === "pro" ? "Pro · $79/mo" : tier === "basic" ? "Basic · $29/mo" : "Free"}</div>
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
          <button className="m-btn" style={{ width:"100%", color:"var(--down)", borderColor:"rgba(239,68,68,0.3)" }}
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
        <div style={{ fontSize:44, lineHeight:1.05, color:"#fff", letterSpacing:"-0.02em", fontWeight:800 }}>
          Quant signals.<br/><span style={{ color:"var(--accent)" }}>Plain English.</span>
        </div>
        <div style={{ marginTop:18, fontSize:14, color:"var(--text-dim)", lineHeight:1.5 }}>
          65+ signal blocks — Polygon.io primary data, dark pool prints, 13F institutional flow, Macro HMM — fused into one confidence score (max 84%) and pushed to Telegram.
        </div>
        <div style={{ flex:1 }}/>
        <div style={{ display:"grid", gap:10, marginBottom:14, textAlign:"left" }}>
          {[["📊","65+ signal blocks, Polygon.io primary"],["🎯","Entry, stop & target on every BUY/SELL"],["📱","Telegram + Discord + Web Push, your hours"]].map((f, i) => (
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
  const [signals,   setSignals]   = useState(MOBILE_SIGNALS_MOCK);
  const [positions, setPositions] = useState(POSITIONS_MOCK);
  const [stats,     setStats]     = useState(null);
  const [user,      setUser]      = useState(null);
  const [authReady, setAuthReady] = useState(false);
  const [selected,  setSelected]  = useState(null);
  const [now,       setNow]       = useState(() => new Date());

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
    const opts = { signal: ctrl.signal };
    apiFetch("/api/signals", opts).then(d => { if (d && Array.isArray(d) && d.length > 0) setSignals(d); });
    apiFetch("/api/paper/positions", opts).then(d => { if (d && Array.isArray(d) && d.length > 0) setPositions(d); });
    apiFetch("/api/public/track-record", opts).then(d => { if (d && !d.no_data) setStats(d); });
    return () => ctrl.abort();
  }, [user]);

  // Clock
  useEffect(() => { const id = setInterval(() => setNow(new Date()), 60000); return () => clearInterval(id); }, []);

  if (!authReady) return <div style={{ display:"flex", alignItems:"center", justifyContent:"center", height:"100%", background:"var(--bg-0)", color:"var(--text-faint)", fontFamily:"var(--mono)", fontSize:13 }}>Loading…</div>;

  if (!user) return <OnboardScreen onLogin={() => window.location.href="/login?next=/mobile"} onSignup={() => window.location.href="/signup"}/>;

  const sendSignal = async (s) => {
    if (s.raw?.id) {
      await mFetch(`/api/signals/${s.raw.id}/send`);
      alert(`✓ ${s.action} ${s.tk} sent to Telegram`);
    }
  };

  const screenContent = () => {
    if (selected && tab === "feed") return <DetailScreen signal={selected} onBack={() => setSelected(null)} onSend={() => sendSignal(selected)}/>;
    switch (tab) {
      case "feed":      return <FeedScreen signals={signals} onSelect={s => setSelected(s)}/>;
      case "portfolio": return <PortfolioScreen positions={positions}/>;
      case "record":    return <RecordScreen stats={stats}/>;
      case "account":   return <AccountScreen user={user}/>;
      default:          return (
        <div style={{ flex:1, display:"flex", alignItems:"center", justifyContent:"center", color:"var(--text-faint)", fontSize:13 }}>
          Watchlist coming soon
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

function WatchlistScreen({ tickers = WATCH_MOCK }) {
  const [filter, setFilter] = useState("all");
  const items = filter === "signals" ? tickers.filter(t => t.sigs > 0)
              : filter === "alerts"  ? tickers.filter(t => t.alert)
              : tickers;
  return (
    <>
      <MStatusBar/>
      <div className="m-top">
        <span style={{ fontFamily:"var(--mono)", fontWeight:700, fontSize:13, color:"#fff" }}>Watchlist</span>
        <span style={{ marginLeft:"auto", display:"inline-flex", gap:10, alignItems:"center" }}>
          <span className="ico"><MIcon name="filter" size={18}/></span>
          <span className="ico" style={{ color:"var(--accent)", fontSize:20 }}>+</span>
        </span>
      </div>
      <div style={{ padding:"0 16px 12px", display:"flex", gap:6, overflowX:"auto" }}>
        {[["all","ALL · "+tickers.length],["signals","SIGNALS"],["alerts","ALERTS"]].map(([k,l]) => (
          <span key={k} className={`m-pill ${filter===k?"on":""}`} onClick={() => setFilter(k)} role="button" tabIndex={0}>{l}</span>
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
                <span style={{ fontFamily:"var(--mono)", fontWeight:600, fontSize:14, color:"#fff" }}>{w.tk}</span>
                {w.sigs > 0 && <span style={{ fontFamily:"var(--mono)", fontSize:9, padding:"2px 5px", borderRadius:4, background:"color-mix(in oklch,var(--accent) 18%,transparent)", color:"var(--accent)" }}>{w.sigs} live</span>}
                {w.alert && <span style={{ color:"var(--warn)" }}><MIcon name="bell" size={11}/></span>}
              </div>
              <div style={{ fontSize:11, color:"var(--text-dim)", marginTop:2 }}>{w.co}</div>
            </div>
            <div style={{ textAlign:"right" }}>
              <div style={{ fontFamily:"var(--mono)", fontSize:13, color:"#fff" }}>${w.price.toFixed(2)}</div>
              <div style={{ fontFamily:"var(--mono)", fontSize:11, color: w.ch >= 0 ? "var(--up)" : "var(--down)", marginTop:2 }}>{w.ch >= 0 ? "+" : ""}{w.ch}%</div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

// ── Notifications / activity screen ──────────────────────────────────────────
const NOTIFS_MOCK = [
  { type:"BUY",   tk:"NVDA", text:"Confidence raised to 87% — entry $1,245",       ago:"2m"  },
  { type:"FILL",  tk:"AAPL", text:"Paper portfolio: BUY 50 @ $178.20 filled",       ago:"14m" },
  { type:"SELL",  tk:"TSLA", text:"Pivot break confirmed — entry $165, stop $172",  ago:"32m" },
  { type:"ALERT", tk:"PLTR", text:"Volume spike 4.2× — added to watchlist",         ago:"1h"  },
  { type:"BUY",   tk:"AMD",  text:"50-DMA reclaim + flow surge — 69% conf",         ago:"2h"  },
  { type:"SYS",   tk:null,   text:"Daily recap: 12 fired, 8 W / 3 L / 1 open",      ago:"9h"  },
  { type:"HOLD",  tk:"META", text:"Mixed signals — suppressed below 60%",           ago:"1d"  },
];

function NotifScreen({ notifs = NOTIFS_MOCK }) {
  const [filter, setFilter] = useState("all");
  const items = filter === "all" ? notifs
    : notifs.filter(n => n.type.toLowerCase() === filter || (filter === "fills" && n.type === "FILL"));
  return (
    <>
      <MStatusBar/>
      <div className="m-top">
        <span style={{ fontFamily:"var(--mono)", fontWeight:700, fontSize:13, color:"#fff" }}>Activity</span>
        <span style={{ marginLeft:"auto", fontFamily:"var(--mono)", fontSize:10, color:"var(--text-faint)" }}>Mark all read</span>
      </div>
      <div style={{ padding:"0 16px 12px", display:"flex", gap:6, overflowX:"auto" }}>
        {[["all","ALL · "+notifs.length],["buy","SIGNALS"],["fill","FILLS"],["alert","ALERTS"]].map(([k,l]) => (
          <span key={k} className={`m-pill ${filter===k?"on":""}`} onClick={() => setFilter(k)} role="button" tabIndex={0}>{l}</span>
        ))}
      </div>
      <div style={{ flex:1, overflowY:"auto" }}>
        {items.map((n, i) => {
          const c = n.type==="BUY" ? "var(--up)" : n.type==="SELL" ? "var(--down)" : n.type==="HOLD" ? "var(--warn)" : n.type==="FILL" ? "var(--accent)" : "var(--text-faint)";
          return (
            <div key={i} style={{ display:"flex", gap:12, padding:"14px 16px", borderBottom:"1px solid var(--line)" }}>
              <div style={{ width:36, height:36, borderRadius:10, background:`color-mix(in oklch,${c} 14%,transparent)`, color:c, display:"grid", placeItems:"center", fontFamily:"var(--mono)", fontSize:9, fontWeight:700, flex:"none" }}>
                {n.type}
              </div>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ display:"flex", alignItems:"baseline", gap:8 }}>
                  {n.tk && <span style={{ fontFamily:"var(--mono)", fontWeight:600, fontSize:13, color:"#fff" }}>{n.tk}</span>}
                  <span style={{ fontFamily:"var(--mono)", fontSize:10, color:"var(--text-faint)", marginLeft:"auto" }}>{n.ago} ago</span>
                </div>
                <div style={{ fontSize:12, color:"var(--text-dim)", marginTop:3, lineHeight:1.4 }}>{n.text}</div>
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}

// ── Paywall screen ────────────────────────────────────────────────────────────
function PaywallScreen({ onClose }) {
  const tiers = [
    { name:"Free",   price:"$0",     per:"/forever", fav:false, current:true,  cta:"Current plan",    desc:"5 signals/day, 1h delay, top tickers only" },
    { name:"Basic",  price:"$29",   per:"/month",   fav:true,  current:false, cta:"Start 7-day trial", desc:"Unlimited live signals, Telegram + Discord + Web Push, backtest, Excel export" },
    { name:"Pro",    price:"$79",   per:"/month",   fav:false, current:false, cta:"Upgrade to Pro",  desc:"Everything in Basic + paper trading, volatility targeting, correlation matrix, weekly digest" },
  ];
  return (
    <>
      <MStatusBar/>
      <div className="m-top">
        {onClose && <span className="ico" onClick={onClose} role="button" tabIndex={0}><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"><polyline points="15 6 9 12 15 18"/></svg></span>}
        <span style={{ fontFamily:"var(--mono)", fontSize:11, letterSpacing:"0.15em", color:"var(--text-dim)", marginLeft: onClose ? 0 : "auto" }}>UPGRADE</span>
      </div>
      <div style={{ flex:1, overflowY:"auto", padding:"16px 16px 20px" }}>
        <div style={{ fontSize:26, fontWeight:800, color:"#fff", lineHeight:1.1, letterSpacing:"-0.02em", marginBottom:8 }}>
          Unlock the full feed
        </div>
        <div style={{ fontSize:13, color:"var(--text-dim)", lineHeight:1.5, marginBottom:18 }}>
          Free shows 5 signals/day with 1h delay. Upgrade to receive signals live.
        </div>
        <div style={{ display:"grid", gap:10 }}>
          {tiers.map((t, i) => (
            <div key={i} style={{ padding:16, borderRadius:14, background:t.fav ? "color-mix(in oklch,var(--accent) 8%,var(--bg-2))" : "var(--bg-2)", border:t.fav ? "1.5px solid var(--accent)" : "1px solid var(--line)", position:"relative" }}>
              {t.fav && <span style={{ position:"absolute", top:-8, right:12, padding:"3px 8px", borderRadius:4, background:"var(--accent)", color:"#000", fontFamily:"var(--mono)", fontSize:9, fontWeight:700, letterSpacing:"0.1em" }}>POPULAR</span>}
              <div style={{ display:"flex", alignItems:"baseline", gap:6, marginBottom:6 }}>
                <span style={{ fontWeight:600, fontSize:14, color:"#fff" }}>{t.name}</span>
                <span style={{ marginLeft:"auto", fontFamily:"var(--mono)", fontSize:20, fontWeight:700, color:"#fff" }}>{t.price}</span>
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
function NotifScreen_Static()     { return <NotifScreen notifs={NOTIFS_MOCK}/> }
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
    NotifScreen:     NotifScreen_Static,
    PaywallScreen:   PaywallScreen_Static,
  });
}
