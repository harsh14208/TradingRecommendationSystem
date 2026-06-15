/* global React, ReactDOM */
// SIGNAL.TRADE cinematic app shell — production wiring.
// Keeps the reference navigation/layout and fuses the real backend auth,
// signals, market context, settings persistence, WebSocket, and signal actions.

/* ─── App defaults (mirrors legacy tweakState) ─────────────────────────────── */
const DEFAULTS = {
  theme: "dark",
  accent: "#22d3ee",
  density: "comfortable",
  chartStyle: "area",
  aggressiveness: "balanced",
  style: "swing",
  days: ["Mon", "Tue", "Wed", "Thu", "Fri"],
  startTime: "09:30",
  endTime: "16:00",
  customConf: null,
  weight_overrides: {},
};

const DISCLAIMER_KEY = "signal_trade_disclaimer_v1";

/* ─── Helpers ──────────────────────────────────────────────────────────────── */
function fmtPrice(v, dp = 2) {
  if (v == null) return "—";
  return v.toLocaleString("en-US", { minimumFractionDigits: dp, maximumFractionDigits: dp });
}

function fmtPct(v, signed = true) {
  if (v == null) return "—";
  const s = signed ? (v >= 0 ? "+" : "−") : "";
  return s + Math.abs(v).toFixed(2) + "%";
}

function fmtTime(iso) {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false, timeZone: "America/New_York" });
  } catch { return "—"; }
}

function toNum(v, fallback = 0) {
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
}

/* Parse R:R strings from the backend (e.g. "1:2.0", "2.5", "—") into a number. */
function parseRR(v) {
  if (v == null || v === "—" || v === "") return null;
  if (typeof v === "number") return Number.isFinite(v) ? v : null;
  const s = String(v).trim();
  if (s.includes(":")) {
    const [risk, reward] = s.split(":");
    const r = toNum(risk, 0), rw = toNum(reward, 0);
    if (r > 0 && rw > 0) return rw / r;
    return null;
  }
  const n = toNum(s, null);
  return n != null && n > 0 ? n : null;
}

/* Map a backend signal into the cinematic shape. Missing narrative fields fall
   back to the matching mock signal so the UI never looks empty. */
function toCinSignal(s) {
  const mock = (typeof SIGNALS !== "undefined" ? SIGNALS : []).find((m) => m.tk === (s.ticker || s.tk));
  const tk = s.ticker || s.tk || "???";
  const signal = (s.action || s.signal || "HOLD").toUpperCase();
  const px = toNum(s.price ?? s.px, 0);
  const chg = toNum(s.change ?? s.chgPct, 0);
  const entry = s.entry != null ? toNum(s.entry, null) : (mock?.entry ?? null);
  const stop = s.stop != null ? toNum(s.stop, null) : (mock?.stop ?? null);
  const target = s.target != null ? toNum(s.target, null) : (mock?.target ?? null);
  const computedRR = entry != null && stop != null && target != null && Math.abs(entry - stop) > 1e-9
    ? Math.abs((target - entry) / (entry - stop)) : null;
  const rr = parseRR(s.rr) ?? computedRR ?? parseRR(mock?.rr) ?? 0;
  const rationale = (s.rationale || []).map((r) => ({
    src: r.src || r.source || "SRC",
    head: r.head || r.headline || r.title || "",
    body: r.body || r.summary || "",
    meta: r.meta || r.time || "",
    sentiment: r.sentiment || (r.score > 0 ? "pos" : r.score < 0 ? "neg" : "neu"),
  }));
  return {
    id: s.id || tk,
    tk,
    name: s.company || s.name || mock?.name || tk,
    signal,
    conf: toNum(s.confidence ?? s.conf, 50),
    px,
    chgPct: chg,
    rr,
    entry,
    stop,
    target,
    mcap: s.mcap || mock?.mcap || "—",
    vol: s.vol || mock?.vol || "—",
    pe: s.pe || mock?.pe || "—",
    ts: s.ts || fmtTime(s.created_at) || (mock?.ts || "—"),
    style: s.style || mock?.style || "swing",
    win: toNum(s.win, mock?.win ?? 60),
    sources: (s.sources || mock?.sources || []).map((x) => (typeof x === "string" ? x : x.name || x.abbr || "SRC")),
    headline: s.headline || s.reason || s.title || mock?.headline || `${signal} setup on ${tk}`,
    narrative: s.narrative || s.summary || s.explanation || mock?.narrative || "",
    rationale: rationale.length ? rationale : (mock?.rationale || []),
    seed: s.seed || mock?.seed || hashSeed(tk),
    drift: toNum(s.drift, mock?.drift ?? 0),
    volatility: toNum(s.volatility ?? s.vol, mock?.vol ?? 0.02),
  };
}

function hashSeed(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) h = ((h << 5) - h) + str.charCodeAt(i);
  return Math.abs(h) || 1;
}

function toCinTicker(t) {
  return {
    tk: t.ticker || t.t || t.tk,
    verb: (t.action || t.verb || "HOLD").toUpperCase(),
    px: fmtPrice(t.price || t.p || t.px, (t.price || t.p || t.px) > 1000 ? 0 : 2),
    chg: fmtPct(t.change || t.chg || t.changePct || 0),
  };
}

/* Delivery-log timestamp: "Jun 12 · 15:31" (ET) from created_at, else the
   raw preformatted time. Keeps date+time consistent across dashboard + market. */
function fmtLogStamp(l) {
  if (l && l.created_at) {
    try {
      return new Intl.DateTimeFormat("en-US", {
        timeZone: "America/New_York", month: "short", day: "numeric",
        hour: "2-digit", minute: "2-digit", hour12: false,
      }).format(new Date(l.created_at)).replace(", ", " · ");
    } catch {}
  }
  return (l && (l.time || l.t)) || "—";
}

function toCinLog(l) {
  const status = (l.status || l.s || "sent").toLowerCase();
  const msg = l.message || l.m || "";
  const col = status === "sent" ? "var(--bull)" : status === "fail" ? "var(--bear)" : "var(--neutral)";
  return { t: fmtLogStamp(l), s: status, m: msg, col };
}

/* ─── Navigation ───────────────────────────────────────────────────────────── */
const NAV = [
  ["home", "Home"],
  ["dashboard", "Dashboard"],
  ["market", "Market"],
  ["backtest", "Backtest"],
  ["track", "Track Record"],
  ["tools", "Tools"],
  ["settings", "Settings"],
];

const NAV_ICONS = {
  home: <path d="M3 10.5 12 3l9 7.5V21h-6v-6h-6v6H3z" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round"></path>,
  dashboard: <path d="M4 19V9m6 10V5m6 14v-7m-14 9h18" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round"></path>,
  market: <path d="M4 17l5-6 4 3 7-9M4 21h16" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"></path>,
  track: <path d="M5 21V5m14 16V11M12 21V3" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round"></path>,
  backtest: <path d="M4 17l5-6 4 3 7-9M4 21h16" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"></path>,
  settings: <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm8-3a8 8 0 0 1-.2 1.8l2 1.5-2 3.4-2.3-1a8 8 0 0 1-3 1.8L14 22h-4l-.4-2.5a8 8 0 0 1-3-1.8l-2.4 1-2-3.4 2-1.5A8 8 0 0 1 4 12c0-.6.1-1.2.2-1.8l-2-1.5 2-3.4 2.3 1a8 8 0 0 1 3-1.8L10 2h4l.4 2.5a8 8 0 0 1 3 1.8l2.4-1 2 3.4-2 1.5c.1.6.2 1.2.2 1.8z" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"></path>,
  tools: <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.6-3.6a1 1 0 0 0 0-1.4l-1.6-1.6a1 1 0 0 0-1.4 0l-3.6 3.6zM2 17.2V21h3.8l11-11.1L13 6.1 2 17.2z" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round"></path>,
};

function TopNav({ page, go, onBack, currentUser, onLogout, hideBack }) {
  const tier = currentUser?.subscription_tier || "free";
  const isOwner = currentUser?.is_owner;
  // Hide the global page-back while a tool overlay is open — the overlay has
  // its own Back, and two stacked "Back" buttons are confusing.
  const showBack = page !== "home" && !hideBack;
  return (
    <header className="topnav">
      {showBack && (
        <button className="btn ghost" onClick={onBack} aria-label="Back"
          style={{ display: "inline-flex", alignItems: "center", gap: 6, marginRight: 8, padding: "6px 10px" }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5"></path>
            <path d="M12 19l-7-7 7-7"></path>
          </svg>
          <span style={{ fontSize: 12 }}>Back</span>
        </button>
      )}
      <Logo go={go} aria-label="SIGNAL.TRADE home"></Logo>
      <nav className="links" style={{ marginLeft: 8 }} aria-label="Primary">
        {NAV.map(([id, label]) => (
          <button key={id} className={page === id ? "on" : ""} onClick={() => go(id)} aria-current={page === id ? "page" : undefined}>{label}</button>
        ))}
      </nav>
      <div className="nav-right" style={{ marginLeft: "auto", minWidth: 0, display: "flex", alignItems: "center", gap: 14 }}>
        <MarketBadge />
        {currentUser && (
          <span className="kicker" title={currentUser.email || currentUser.name || tier}
            style={{ textTransform: "uppercase", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 170, minWidth: 0 }}>
            {currentUser.email || currentUser.name || tier}
            {isOwner && <span style={{ color: "var(--bull)", marginLeft: 6 }}>OWNER</span>}
          </span>
        )}
        {currentUser && (
          <button className="btn sm" style={{ flexShrink: 0 }} onClick={onLogout}>Log out</button>
        )}
      </div>
    </header>
  );
}

function BottomNav({ page, go }) {
  return (
    <nav className="bottomnav" aria-label="Primary">
      {NAV.map(([id, label]) => (
        <button key={id} className={page === id ? "on" : ""} onClick={() => go(id)} aria-current={page === id ? "page" : undefined}>
          <svg viewBox="0 0 24 24" aria-hidden="true">{NAV_ICONS[id]}</svg>
          {label.replace("Signal ", "").replace(" Lab", "")}
        </button>
      ))}
    </nav>
  );
}

function Footer() {
  return (
    <footer style={{ borderTop: "1px solid var(--line-soft)", padding: "28px 0 36px", marginTop: 8 }}>
      <div className="wrap" style={{ display: "flex", gap: 20, alignItems: "center", flexWrap: "wrap" }}>
        <Logo></Logo>
        <span style={{ fontSize: 11, color: "var(--text-ghost)", lineHeight: 1.5, maxWidth: 640, textWrap: "pretty" }}>
          For educational and informational purposes only. Not financial advice. Past performance does not predict
          future results. Trade at your own risk; consult a licensed advisor.
        </span>
        <span className="kicker" style={{ marginLeft: "auto" }}>© 2026 SIGNAL.TRADE</span>
      </div>
    </footer>
  );
}

function ETClock() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => { const id = setInterval(() => setNow(new Date()), 1000); return () => clearInterval(id); }, []);
  try {
    return <span>{new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }).format(now)} ET</span>;
  } catch { return <span>— ET</span>; }
}

/* Live US-equity session status from the ET wall clock (regular hours only;
   holidays not modelled). Drives the topnav badge + dot colour. */
function marketStatus(d = new Date()) {
  try {
    const parts = new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", weekday: "short", hour: "2-digit", minute: "2-digit", hour12: false }).formatToParts(d);
    const wd = parts.find((p) => p.type === "weekday").value;
    const mins = Number(parts.find((p) => p.type === "hour").value) * 60 + Number(parts.find((p) => p.type === "minute").value);
    const weekday = !["Sat", "Sun"].includes(wd);
    if (weekday && mins >= 570 && mins < 960) return { label: "MARKET OPEN", cls: "" };
    if (weekday && mins >= 240 && mins < 570) return { label: "PRE-MARKET", cls: "amber" };
    if (weekday && mins >= 960 && mins < 1200) return { label: "AFTER HOURS", cls: "amber" };
    return { label: "MARKET CLOSED", cls: "red" };
  } catch { return { label: "MARKET", cls: "" }; }
}

function MarketBadge() {
  const [, tick] = useState(0);
  useEffect(() => { const id = setInterval(() => tick((t) => t + 1), 30000); return () => clearInterval(id); }, []);
  const st = marketStatus();
  return (
    <span className="kicker" style={{ display: "inline-flex", alignItems: "center", gap: 7, flexShrink: 0, whiteSpace: "nowrap" }}>
      <LiveDot color={st.cls}></LiveDot> {st.label} · <ETClock />
    </span>
  );
}

class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { err: null }; }
  static getDerivedStateFromError(err) { return { err }; }
  render() {
    if (this.state.err) {
      return (
        <div style={{ padding: 60, textAlign: "center" }}>
          <div className="kicker" style={{ color: "var(--bear)", marginBottom: 10 }}>SOMETHING BROKE</div>
          <p className="dim" style={{ fontSize: 13 }}>{String(this.state.err)}</p>
          <button className="btn" onClick={() => this.setState({ err: null })}>Try again</button>
        </div>
      );
    }
    return this.props.children;
  }
}

/* ─── Owner kill-switch control ─────────────────────────────────────────────── */
function KillSwitch({ currentUser }) {
  const [paused, setPaused] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!currentUser?.is_owner) return;
    let alive = true;
    apiFetch("/api/admin/execution-kill-switch").then((d) => { if (alive && d) setPaused(d.execution_paused); });
    return () => { alive = false; };
  }, [currentUser]);

  const toggle = async () => {
    setLoading(true);
    const d = await apiFetch("/api/admin/execution-kill-switch", { method: "POST" });
    if (d) setPaused(d.execution_paused);
    setLoading(false);
  };

  if (!currentUser?.is_owner || paused === null) return null;
  const col = paused ? "var(--bull)" : "var(--bear)";
  return (
    <button onClick={toggle} disabled={loading} title={paused ? "Resume auto-execution" : "Immediately pause all auto-execution"}
      style={{ display: "flex", alignItems: "center", gap: 5, padding: "4px 10px", height: 28,
        background: paused ? "var(--bull-soft)" : "var(--bear-soft)",
        border: `1px solid ${col}`, borderRadius: 5, color: col, fontFamily: "var(--font-mono)", fontSize: 10,
        fontWeight: 600, letterSpacing: "0.06em", cursor: "pointer", whiteSpace: "nowrap", opacity: loading ? 0.5 : 1 }}>
      <span style={{ width: 7, height: 7, borderRadius: "50%", background: col, boxShadow: `0 0 6px ${col}` }} />
      <span>{paused ? "RESUME AUTO-EXEC" : "KILL SWITCH"}</span>
    </button>
  );
}

/* ─── Signal actions shared with Dashboard ──────────────────────────────────── */
function useSignalActions({ signals, setSignals, setLog }) {
  const sendToTelegram = useCallback(async (id) => {
    const sig = signals.find((s) => s.id === id);
    if (!sig) return;
    try {
      const raw = await authFetch(`/api/signals/${sig.id}/send`, { method: "POST" });
      const data = await raw.json();
      if (!raw.ok) { alert(data.detail || "Could not send to Telegram."); return; }
      if (data.success) {
        const t = fmtTime(new Date().toISOString());
        setLog((prev) => [{ t, s: "sent", m: `✓ ${sig.action || sig.signal} ${sig.ticker || sig.tk} @ ${fmtPrice(sig.price || sig.px)} (Conf ${Math.round(sig.confidence || sig.conf || 0)}%)`, col: "var(--bull)" }, ...prev]);
      } else {
        alert(data.detail || "Telegram delivery failed.");
      }
    } catch { alert("Network error — could not reach the server."); }
  }, [signals, setLog]);

  const skipSignal = useCallback(async (id) => {
    await apiFetch(`/api/signals/${id}/skip`, { method: "POST" });
    setSignals((prev) => prev.filter((s) => s.id !== id));
  }, [setSignals]);

  const reviewSignal = useCallback(async (id) => {
    await apiFetch(`/api/signals/${id}/review`, { method: "POST" });
    setSignals((prev) => prev.map((s) => s.id === id ? { ...s, reviewed: true } : s));
  }, [setSignals]);

  const saveNote = useCallback(async (id, note) => {
    await apiFetch(`/api/signals/${id}/notes`, { method: "PATCH", body: JSON.stringify({ notes: note }) });
    setSignals((prev) => prev.map((s) => s.id === id ? { ...s, notes: note } : s));
  }, [setSignals]);

  return { sendToTelegram, skipSignal, reviewSignal, saveNote };
}

/* ─── Main App ──────────────────────────────────────────────────────────────── */
function App() {
  /* Auth */
  const [currentUser, setCurrentUser] = useState(null);
  const [authReady, setAuthReady] = useState(false);
  const [disclaimerAck, setDisclaimerAck] = useState(() => !!localStorage.getItem(DISCLAIMER_KEY));

  /* Data */
  const [signals, setSignals] = useState(() => {
    try {
      const c = localStorage.getItem("st_signals_cache");
      if (c) { const p = JSON.parse(c); if (Array.isArray(p)) return p; }
    } catch {}
    return [];
  });
  const [histSignals, setHistSignals] = useState([]);
  const [sources, setSources] = useState([]);
  const [log, setLog] = useState([]);
  const [tickerTape, setTickerTape] = useState([]);
  const [marketCtx, setMarketCtx] = useState(null);
  const [signalQuota, setSignalQuota] = useState(null);
  const [online, setOnline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  /* UI / settings */
  const [page, setPage] = useState(() => { try { return localStorage.getItem("st_cin_page") || "dashboard"; } catch { return "dashboard"; } });
  const pageHistoryRef = useRef([page]);
  useEffect(() => { pageHistoryRef.current = [page]; }, []);

  const [tweakState, setTweakState] = useState(() => {
    try { return { ...DEFAULTS, ...JSON.parse(localStorage.getItem("st_tweaks") || "{}") }; }
    catch { return DEFAULTS; }
  });
  const tweakSaving = useRef(false);
  const pendingTweak = useRef(null);
  const setTweak = useCallback((patch) => {
    const next = { ...tweakState, ...patch };
    setTweakState(next);
    try { localStorage.setItem("st_tweaks", JSON.stringify(next)); } catch {}
    pendingTweak.current = next;
    if (tweakSaving.current) return;
    const run = async () => {
      tweakSaving.current = true;
      while (pendingTweak.current) {
        const payload = pendingTweak.current;
        pendingTweak.current = null;
        try { await apiFetch("/api/settings", { method: "PUT", body: JSON.stringify(payload) }); } catch {}
      }
      tweakSaving.current = false;
    };
    run();
  }, [tweakState]);

  const settingsHydrated = useRef(false);
  useEffect(() => {
    if (!authReady || !currentUser || settingsHydrated.current) return;
    settingsHydrated.current = true;
    apiFetch("/api/settings").then((d) => {
      if (!d) return;
      const merged = { ...DEFAULTS, ...d };
      setTweakState(merged);
      try { localStorage.setItem("st_tweaks", JSON.stringify(merged)); } catch {}
    }).catch(() => {});
  }, [authReady, currentUser]);

  const go = useCallback((p) => {
    setPage(p);
    const last = pageHistoryRef.current[pageHistoryRef.current.length - 1];
    if (last !== p) pageHistoryRef.current = [...pageHistoryRef.current, p];
    try { localStorage.setItem("st_cin_page", p); } catch {}
    try { window.scrollTo({ top: 0 }); } catch {}
  }, []);

  const goBack = useCallback(() => {
    if (pageHistoryRef.current.length <= 1) { go("home"); return; }
    const next = pageHistoryRef.current.slice(0, -1);
    pageHistoryRef.current = next;
    setPage(next[next.length - 1]);
    try { window.scrollTo({ top: 0 }); } catch {}
  }, [go]);

  /* Theme / density */
  useEffect(() => {
    // The cinematic UI is dark-only by design (mesh/glass/glow). Force dark so a
    // stale/legacy "light" preference can't half-apply and hide text.
    document.documentElement.setAttribute("data-theme", "dark");
    document.documentElement.setAttribute("data-density", tweakState.density);
    // Guard against a near-white accent (it would make --bull/--accent text
    // invisible). Fall back to cyan above a high-luminance threshold.
    const hex = (tweakState.accent || "#22d3ee").replace("#", "");
    const n0 = parseInt(hex, 16);
    const lum = (0.2126 * ((n0 >> 16) & 255) + 0.7152 * ((n0 >> 8) & 255) + 0.0722 * (n0 & 255)) / 255;
    const accent = lum > 0.72 ? "#22d3ee" : (tweakState.accent || "#22d3ee");
    document.documentElement.style.setProperty("--accent", accent);
    document.documentElement.style.setProperty("--up", accent);
    document.documentElement.style.setProperty("--bull", accent);
    const n = parseInt(accent.replace("#", ""), 16);
    const rgb = `${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}`;
    document.documentElement.style.setProperty("--up-soft", `rgba(${rgb}, 0.12)`);
    document.documentElement.style.setProperty("--up-glow", `rgba(${rgb}, 0.35)`);
    document.documentElement.style.setProperty("--bull-soft", `rgba(${rgb}, 0.12)`);
    document.documentElement.style.setProperty("--bull-glow", `rgba(${rgb}, 0.35)`);
    document.documentElement.style.setProperty("font-size", tweakState.density === "compact" ? "13px" : tweakState.density === "comfy" ? "15px" : "14px");
  }, [tweakState.theme, tweakState.density, tweakState.accent]);

  /* Auth bootstrap */
  useEffect(() => {
    const ctrl = new AbortController();
    const params = new URLSearchParams(window.location.search);
    const oauthCode = params.get("oauth_code");
    if (oauthCode) {
      window.history.replaceState({}, "", window.location.pathname);
      fetch(`/api/auth/oauth-exchange?code=${oauthCode}`, { signal: ctrl.signal })
        .then((r) => r.ok ? r.json() : null)
        .then((d) => { if (d?.access_token) { saveToken(d.access_token); if (d.user) setCurrentUser(d.user); } })
        .catch(() => {})
        .finally(() => setAuthReady(true));
      return () => ctrl.abort();
    }
    const token = getToken();
    const fetchMe = () =>
      authFetch("/api/auth/me", { signal: ctrl.signal })
        .then((r) => r.ok ? r.json() : null)
        .then((u) => { if (u) setCurrentUser(u); else clearToken(); })
        .catch(() => {})
        .finally(() => setAuthReady(true));
    if (!token) {
      _tryRefresh().then((ok) => { if (ok) fetchMe(); else setAuthReady(true); });
      return () => ctrl.abort();
    }
    fetchMe();
    return () => ctrl.abort();
  }, []);

  /* Data loading */
  const _parseQuotaHeaders = (headers) => {
    const limit = headers.get("X-Signal-Quota-Limit");
    const remaining = headers.get("X-Signal-Quota-Remaining");
    const resetsAt = headers.get("X-Signal-Quota-Resets-At");
    if (!limit || !remaining) return null;
    return { limit: limit === "unlimited" ? null : parseInt(limit, 10), remaining: remaining === "unlimited" ? null : parseInt(remaining, 10), resetsAt: resetsAt || null };
  };

  const loadData = useCallback(async (showSpinner = false, opts = {}) => {
    if (showSpinner) setRefreshing(true);
    const signal = opts.signal;
    try {
      const [sigsRaw, srcs] = await Promise.all([apiFetchRaw("/api/signals", { signal }), apiFetch("/api/sources", { signal })]);
      const sigs = sigsRaw.json;
      if (Array.isArray(sigs)) { setSignals(sigs); try { localStorage.setItem("st_signals_cache", JSON.stringify(sigs)); } catch {} }
      if (sigsRaw.ok) setSignalQuota(_parseQuotaHeaders(sigsRaw.headers));
      if (Array.isArray(srcs)) setSources(srcs);
      setOnline(true);
    } catch { setOnline(false); } finally { setLoading(false); if (showSpinner) setRefreshing(false); }

    Promise.all([
      apiFetch("/api/delivery/log", { signal }),
      apiFetch("/api/quotes", { signal }),
      apiFetch("/api/market/context", { signal }),
      apiFetch("/api/signals/history", { signal }),
    ]).then(([lg, quotes, mkt, hist]) => {
      if (Array.isArray(lg)) setLog(lg);
      if (Array.isArray(quotes)) setTickerTape(quotes);
      if (mkt) setMarketCtx(mkt);
      if (hist) setHistSignals(Array.isArray(hist) ? hist.filter((h) => h.outcomePct != null) : []);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!authReady || !currentUser) return;
    const ctrl = new AbortController();
    loadData(false, { signal: ctrl.signal });
    return () => ctrl.abort();
  }, [authReady, currentUser, loadData]);

  /* Auto-refresh every 30s */
  useEffect(() => {
    if (!authReady || !currentUser) return;
    const id = setInterval(() => loadData(), 30000);
    return () => clearInterval(id);
  }, [authReady, currentUser, loadData]);

  /* WebSocket */
  useEffect(() => {
    if (!authReady || !currentUser) return;
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const token = getToken();
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    let ws = token ? new WebSocket(wsUrl, ["token", token]) : new WebSocket(wsUrl);
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.type === "new_signal") setSignals((prev) => [data.signal, ...prev.filter((s) => s.id !== data.signal.id)]);
        else if (data.type === "price_update") { if (data.quotes) setTickerTape(data.quotes); }
        else if (data.type === "tick") {
          setTickerTape((prev) => {
            const idx = prev.findIndex((t) => (t.t || t.ticker) === data.ticker);
            if (idx === -1) return prev;
            const next = [...prev]; next[idx] = { ...next[idx], p: data.price }; return next;
          });
        } else if (data.type === "market_context") setMarketCtx(data.data);
      } catch {}
    };
    return () => { ws.onmessage = null; ws.onerror = null; ws.onclose = null; ws.close(); };
  }, [authReady, currentUser]);

  const { sendToTelegram, skipSignal, reviewSignal, saveNote } = useSignalActions({ signals, setSignals, setLog });

  const handleLogout = () => {
    authFetch("/api/auth/logout", { method: "POST" }).finally(() => { clearToken(); window.location.replace("/login"); });
  };

  /* Auth gate */
  useEffect(() => { if (authReady && !currentUser) window.location.replace("/login?next=/app"); }, [authReady, currentUser]);

  /* Derived cinematic data */
  const cinSignals = useMemo(() => signals.map(toCinSignal), [signals]);
  const cinTickerTape = useMemo(() => tickerTape.map(toCinTicker), [tickerTape]);
  const cinLog = useMemo(() => log.map(toCinLog), [log]);

  /* Page props bundle */
  const common = { currentUser, setTweak, tweakState, hasTierAccess };

  /* Legacy tool modals */
  const [modals, setModals] = useState({ account: false, watchlist: false, alerts: false, screener: false, paper: false, market: false, sector: false, calendar: false, pricing: false, history: false, rules: false, sources: false, performance: false, tweaks: false, alert: false });
  const openModal = (k) => () => setModals((m) => ({ ...m, [k]: true }));
  const closeModal = (k) => () => setModals((m) => ({ ...m, [k]: false }));

  const [alertSignal, setAlertSignal] = useState(null);
  const openPriceAlert = useCallback((s) => { setAlertSignal(s); setModals((m) => ({ ...m, alert: true })); }, []);
  const closePriceAlert = useCallback(() => { setAlertSignal(null); setModals((m) => ({ ...m, alert: false })); }, []);

  const toggleSource = useCallback(async (id) => {
    const res = await apiFetch(`/api/sources/${id}`, { method: "PATCH" });
    if (res) setSources((prev) => prev.map((s) => (s.id === id ? { ...s, is_on: res.is_on } : s)));
  }, []);

  if (!authReady) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh", background: "var(--bg-0)", color: "var(--text-faint)", fontFamily: "var(--font-mono)", fontSize: 13 }}>Loading…</div>
  );
  if (!currentUser) return null;

  if (!disclaimerAck) return (
    <div style={{ position: "fixed", inset: 0, zIndex: 9999, background: "rgba(0,0,0,0.82)", display: "flex", alignItems: "center", justifyContent: "center", padding: 20 }}>
      <div style={{ background: "var(--bg-1)", border: "1px solid var(--line)", borderRadius: 14, maxWidth: 560, width: "100%", padding: "32px 36px" }}>
        <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>⚠️ Important Disclaimer</div>
        <div style={{ fontSize: 13, lineHeight: 1.75, color: "var(--text-dim)", display: "flex", flexDirection: "column", gap: 10 }}>
          <p style={{ margin: 0 }}><strong style={{ color: "var(--text)" }}>Signal.Trade is not financial advice.</strong> All signals are for informational and educational purposes only.</p>
          <p style={{ margin: 0 }}>Signal.Trade is <strong style={{ color: "var(--text)" }}>not a registered investment adviser</strong>. Nothing here constitutes a solicitation to buy or sell any security.</p>
          <p style={{ margin: 0 }}><strong style={{ color: "var(--warn)" }}>Trading involves substantial risk of loss.</strong> Past performance does not guarantee future results. You are solely responsible for all investment decisions.</p>
        </div>
        <button className="btn primary" style={{ width: "100%", marginTop: 24, padding: "11px 0", fontSize: 13, fontWeight: 700 }}
          onClick={() => { localStorage.setItem(DISCLAIMER_KEY, "1"); setDisclaimerAck(true); }}>
          I understand — this is for personal research only
        </button>
      </div>
    </div>
  );

  return (
    <ErrorBoundary>
      <div data-screen-label={NAV.find(([id]) => id === page)[1]}>
        <TopNav page={page} go={go} onBack={goBack} currentUser={currentUser} onLogout={handleLogout} hideBack={Object.values(modals).some(Boolean)} />
        {/* Kill switch — only on the dashboard, and only while auto-trading is enabled. */}
        {page === "dashboard" && currentUser?.auto_execute && (
          <div style={{ position: "fixed", top: 58, right: 12, zIndex: 60 }}>
            <KillSwitch currentUser={currentUser} />
          </div>
        )}
        {page === "home" && <PageHome key="home" go={go} t={tweakState} {...common} />}
        {page === "dashboard" && <PageDashboard key="dash" signals={cinSignals} tickerTape={cinTickerTape} log={cinLog} loading={loading} onSend={sendToTelegram} onSkip={skipSignal} onReview={reviewSignal} onNote={saveNote} onPriceAlert={openPriceAlert} {...common} />}
        {page === "market" && <PageMarket key="mkt" marketCtx={marketCtx} sources={sources} log={cinLog} {...common} />}
        {page === "backtest" && <PageBacktest key="bt" {...common} />}
        {page === "track" && <PageTrack key="trk" histSignals={histSignals} {...common} />}
        {page === "settings" && <PageSettings key="set" currentUser={currentUser} settings={tweakState} setSettings={setTweak} {...common} />}
        {page === "tools" && <PageTools key="tools" currentUser={currentUser}
          openAccount={openModal("account")} openWatchlist={openModal("watchlist")}
          openAlerts={openModal("alerts")} openScreener={openModal("screener")}
          openPaper={openModal("paper")} openMarket={openModal("market")}
          openSector={openModal("sector")} openCalendar={openModal("calendar")}
          openHistory={openModal("history")} openRules={openModal("rules")}
          openSources={openModal("sources")} openPerformance={openModal("performance")}
          openPricing={openModal("pricing")} openTweaks={openModal("tweaks")} />}
        <Footer />
        <BottomNav page={page} go={go} />

        {/* Legacy feature modals/overlays */}
        <AccountModal open={modals.account} onClose={closeModal("account")} user={currentUser} setUser={setCurrentUser} onUpgrade={openModal("pricing")} />
        <WatchlistView open={modals.watchlist} onClose={closeModal("watchlist")} quotes={tickerTape} histSignals={histSignals} />
        <AlertsView open={modals.alerts} onClose={closeModal("alerts")} />
        <ScreenerView open={modals.screener} onClose={closeModal("screener")} />
        <PaperView open={modals.paper} onClose={closeModal("paper")} online={online} />
        <MarketOverviewView open={modals.market} onClose={closeModal("market")} online={online} />
        <SectorView open={modals.sector} onClose={closeModal("sector")} online={online} />
        <CalendarView open={modals.calendar} onClose={closeModal("calendar")} />
        <PricingView open={modals.pricing} onClose={closeModal("pricing")} user={currentUser} />
        <HistoryView open={modals.history} onClose={closeModal("history")} online={online} />
        <RulesView open={modals.rules} onClose={closeModal("rules")}
          aggr={tweakState.aggressiveness} style={tweakState.style} days={tweakState.days}
          startTime={tweakState.startTime} endTime={tweakState.endTime}
          setTweak={setTweak} customConf={tweakState.customConf} />
        <SourcesView open={modals.sources} onClose={closeModal("sources")} sources={sources} toggle={toggleSource} />
        <MyPerformanceView open={modals.performance} onClose={closeModal("performance")} />
        <TweaksPanel open={modals.tweaks} onClose={closeModal("tweaks")} state={tweakState} set={setTweak} />
        <PriceAlertModal open={modals.alert} onClose={closePriceAlert} ticker={alertSignal?.tk} currentPrice={alertSignal?.px} />
      </div>
    </ErrorBoundary>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
